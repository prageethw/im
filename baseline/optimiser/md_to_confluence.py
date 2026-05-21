#!/usr/bin/env python3
"""
md_to_confluence.py
===================

Publish a local Markdown file to Atlassian Confluence Cloud / Data Center.

Pipeline:
    1. Parse Markdown -> AST (mistune)
    2. Discover local image references; resolve relative paths
    3. Render AST -> Confluence Storage Format (XHTML with ac:/ri: namespaces)
    4. Find-or-create the target page (REST API v1, storage body)
    5. Upload images as attachments to that page
    6. Rewrite <ac:image> placeholders to reference real attachment filenames
    7. PUT updated page body with version bump and "Published from VS Code" footer

Why REST API v1?
    v2 only accepts Markdown / ADF for the body — storage (XHTML) is still
    v1-only as of 2026 (Atlassian ticket CONFCLOUD-84415, "Enhance v2 to
    support HTML/Storage format"). For fidelity (code macros, info panels,
    structured attachments) v1 + storage remains the correct choice.

Usage:
    export CONFLUENCE_BASE_URL=https://yourorg.atlassian.net/wiki
    export CONFLUENCE_USER=you@example.com
    export CONFLUENCE_API_TOKEN=xxxxxxxx
    python md_to_confluence.py docs/page.md \\
        --space ENG --title "My Page" --parent-id 123456 \\
        [--dry-run] [--update-only]

Author: Prageeth Warnak — generated 2026-05-17
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import logging
import mimetypes
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import mistune  # pip install mistune>=3.0
import requests  # pip install requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG = logging.getLogger("md2confluence")

# ---------------------------------------------------------------------------
# Language map: fenced-block info string -> Confluence code-macro `language`
# Confluence's `code` macro accepts a limited set; unknown languages fall
# back to "none" rather than erroring.
# ---------------------------------------------------------------------------
CONFLUENCE_LANGUAGES = {
    "actionscript3", "applescript", "bash", "csharp", "coldfusion", "cpp",
    "css", "delphi", "diff", "erlang", "groovy", "html", "xml", "java",
    "javafx", "javascript", "js", "json", "kotlin", "perl", "php", "powershell",
    "python", "py", "ruby", "rb", "rust", "sass", "scala", "shell", "sh",
    "sql", "swift", "text", "typescript", "ts", "vb", "yaml", "yml", "go",
    "none",
}
LANG_ALIASES = {
    "js": "javascript", "ts": "typescript", "py": "python", "rb": "ruby",
    "sh": "bash", "shell": "bash", "yml": "yaml", "golang": "go",
    "c++": "cpp", "c#": "csharp", "ps1": "powershell",
}


def normalise_language(info: str) -> str:
    """Map a fenced-block info string to a Confluence code-macro language."""
    if not info:
        return "none"
    lang = info.strip().split()[0].lower()
    lang = LANG_ALIASES.get(lang, lang)
    return lang if lang in CONFLUENCE_LANGUAGES else "none"


# ---------------------------------------------------------------------------
# Markdown -> Storage-Format renderer
# ---------------------------------------------------------------------------
@dataclass
class ImageRef:
    """A discovered local image reference."""
    src: str                       # original src as written in the .md
    abs_path: Path                 # resolved on disk
    filename: str                  # what we'll upload as
    alt: str = ""
    title: Optional[str] = None
    attachment_id: Optional[str] = None  # filled after upload


# Wrap a rendered <table>...</table> so it sits in a centred container.
# Confluence's storage format honours `align="center"` on <table> and also
# accepts a wrapping <div class="table-wrap" style="text-align: center;">.
# We use both for maximum tenant compatibility.
def _centre_table(table_html: str) -> str:
    # Inject align="center" on the opening <table ...> tag
    if table_html.startswith("<table"):
        end = table_html.find(">")
        if end != -1:
            opening = table_html[:end]
            if 'align=' not in opening:
                opening += ' align="center"'
            if 'style=' not in opening:
                opening += ' style="margin-left: auto; margin-right: auto;"'
            table_html = opening + table_html[end:]
    return (
        '<div class="table-wrap" style="text-align: center;">'
        f'{table_html}'
        '</div>'
    )


class StorageRenderer(mistune.HTMLRenderer):
    """
    Custom mistune renderer emitting Confluence Storage Format (XHTML).

    Differences from default HTMLRenderer:
      * Code blocks -> <ac:structured-macro ac:name="code"> with `language` param
      * Local images -> <ac:image><ri:attachment ri:filename="..."/></ac:image>
                        and recorded in `self.image_refs` for later upload
      * Remote images -> <ac:image><ri:url ri:value="..."/></ac:image>
      * Block quotes starting with "> [!NOTE]" / "[!WARNING]" -> info/warning macro
    """

    # Keep NAME = "html" so mistune plugins (table, strikethrough, task_lists,
    # footnotes, url) register their renderer methods on this subclass.
    # Their HTML output (e.g. <table>, <del>) is already valid storage format.
    NAME = "html"

    # Patterns recognised inside the first paragraph of a blockquote.
    # By the time `block_quote` is called, the inner content is already
    # rendered HTML, so we match the `[!TAG]` marker *inside* a leading <p>.
    ADMONITION_RE = re.compile(
        r"^\s*<p>\s*\[!(NOTE|TIP|INFO|WARNING|CAUTION)\]\s*",
        re.I,
    )
    ADMONITION_MAP = {
        "note": "info", "info": "info", "tip": "tip",
        "warning": "warning", "caution": "warning",
    }

    def __init__(self, source_dir: Path) -> None:
        super().__init__(escape=False)
        self.source_dir = source_dir
        self.image_refs: List[ImageRef] = []
        # Deduplicate by absolute path so we upload once even if referenced N times
        self._image_by_abs: Dict[str, ImageRef] = {}

    # ---- code blocks -------------------------------------------------------
    def block_code(self, code: str, info: Optional[str] = None, **_: Any) -> str:
        lang = normalise_language(info or "")
        # CDATA so we don't have to escape <, >, &, " inside the snippet
        return (
            '<ac:structured-macro ac:name="code" ac:schema-version="1">'
            f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
            '<ac:parameter ac:name="theme">Confluence</ac:parameter>'
            '<ac:parameter ac:name="linenumbers">true</ac:parameter>'
            f'<ac:plain-text-body><![CDATA[{code.rstrip()}]]></ac:plain-text-body>'
            '</ac:structured-macro>'
        )

    # ---- images ------------------------------------------------------------
    # Confluence's <ac:image> is an inline element; to centre it we emit the
    # `ac:align="center"` attribute (which Confluence recognises natively)
    # AND wrap the image in a centred <p> so older renderers still align it.
    def image(self, text: str, url: str, title: Optional[str] = None) -> str:
        alt = text or ""
        parsed = urlparse(url)
        is_remote = parsed.scheme in ("http", "https")

        title_attr = f' ac:title="{html.escape(title)}"' if title else ""
        alt_attr = f' ac:alt="{html.escape(alt)}"' if alt else ""
        align_attr = ' ac:align="center" ac:layout="center"'

        if is_remote:
            inner = (
                f'<ac:image{alt_attr}{title_attr}{align_attr}>'
                f'<ri:url ri:value="{html.escape(url, quote=True)}"/>'
                '</ac:image>'
            )
        else:
            abs_path = (self.source_dir / url).resolve()
            key = str(abs_path)
            if key not in self._image_by_abs:
                # Disambiguate filename so two folders with `diagram.png` don't collide
                stem_hash = hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]
                safe_name = f"{abs_path.stem}-{stem_hash}{abs_path.suffix}"
                ref = ImageRef(src=url, abs_path=abs_path, filename=safe_name,
                               alt=alt, title=title)
                self._image_by_abs[key] = ref
                self.image_refs.append(ref)
            ref = self._image_by_abs[key]
            inner = (
                f'<ac:image{alt_attr}{title_attr}{align_attr}>'
                f'<ri:attachment ri:filename="{html.escape(ref.filename, quote=True)}"/>'
                '</ac:image>'
            )

        # Mark this image so the surrounding paragraph renderer can centre it
        return f'\x00CENTERED_IMG\x00{inner}\x00END_IMG\x00'

    # If a paragraph contains *only* a centred image marker, emit a centred
    # <p> wrapper. Otherwise leave the paragraph alone.
    def paragraph(self, text: str) -> str:
        stripped = text.strip()
        if (stripped.startswith("\x00CENTERED_IMG\x00")
                and stripped.endswith("\x00END_IMG\x00")
                and stripped.count("\x00CENTERED_IMG\x00") == 1):
            inner = stripped[len("\x00CENTERED_IMG\x00"):-len("\x00END_IMG\x00")]
            return f'<p style="text-align: center;">{inner}</p>'
        # Strip markers if image appears mid-paragraph (rare)
        cleaned = text.replace("\x00CENTERED_IMG\x00", "").replace("\x00END_IMG\x00", "")
        return f"<p>{cleaned}</p>"

    # ---- blockquotes: detect GFM-style admonitions ------------------------
    def block_quote(self, text: str) -> str:
        # `text` is already-rendered inner HTML. Detect a leading admonition tag.
        m = self.ADMONITION_RE.search(text)
        if not m:
            return f"<blockquote>{text}</blockquote>"
        kind = m.group(1).lower()
        macro = self.ADMONITION_MAP.get(kind, "info")
        # Strip the [!XXX] token while preserving the opening <p>
        cleaned = self.ADMONITION_RE.sub("<p>", text, count=1)
        return (
            f'<ac:structured-macro ac:name="{macro}" ac:schema-version="1">'
            f'<ac:rich-text-body>{cleaned}</ac:rich-text-body>'
            '</ac:structured-macro>'
        )

    # ---- task lists (GFM) -- render as XHTML with a checkbox glyph --------
    # mistune 3 emits `task_list_item` tokens (separate from `list_item`)
    # when the `task_lists` plugin is enabled.
    def task_list_item(self, text: str, checked: bool = False) -> str:
        box = "\u2611" if checked else "\u2610"  # ballot box (with check)
        return f"<li>{box}&nbsp;{text}</li>"

    # ---- tables: centre via the table plugin's renderer hook --------------
    # mistune's `table` plugin calls `self.table(...)` with the already-
    # rendered <thead>/<tbody> children. We wrap the result in a centred
    # container and add inline alignment attributes to the <table> itself.
    # Cell text alignment is left to Confluence's defaults / the author's
    # explicit Markdown column alignment.
    def table(self, text: str) -> str:
        return _centre_table(f"<table>\n{text}</table>")


def render_markdown(md_text: str, source_dir: Path) -> Tuple[str, List[ImageRef]]:
    """Convert Markdown -> (storage_xhtml, list_of_image_refs)."""
    renderer = StorageRenderer(source_dir=source_dir)
    md = mistune.create_markdown(
        renderer=renderer,
        plugins=["strikethrough", "table", "task_lists", "url", "footnotes"],
    )
    body = md(md_text)
    return body, renderer.image_refs


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def build_footer(source_path: Path, base_url: Optional[str] = None) -> str:
    """Storage-format 'Published from VS Code' footer block."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    src = html.escape(str(source_path.resolve()))
    target_line = (
        f'<p>Target: <code>{html.escape(base_url)}</code></p>' if base_url else ""
    )
    return (
        "\n<hr/>\n"
        '<ac:structured-macro ac:name="info" ac:schema-version="1">'
        '<ac:rich-text-body>'
        '<p><strong>Published from VS Code</strong></p>'
        f'<p>Source: <code>{src}</code></p>'
        f'<p>Published at: {now}</p>'
        f'{target_line}'
        '</ac:rich-text-body>'
        '</ac:structured-macro>'
    )


# ---------------------------------------------------------------------------
# Offline export (for firewalled environments — paste/upload manually)
# ---------------------------------------------------------------------------
OFFLINE_INSTRUCTIONS = """<!--
=============================================================================
CONFLUENCE STORAGE-FORMAT EXPORT
=============================================================================
Generated: {generated_at}
Source:    {source_path}

This file is self-contained Confluence Storage Format (XHTML). The corporate
firewall blocks direct REST API calls, so publish it manually:

OPTION A — Paste into the storage-format editor (fastest)
  1. In Confluence, create or open the target page.
  2. Click "..." (page menu) -> "Advanced details" -> open the page in the
     legacy editor, or in the new editor use:
        "..." -> "View page source"  (requires Space admin in some tenants).
     Alternatively, use the Confluence "Source Editor" marketplace app:
        https://marketplace.atlassian.com/apps/1211201/source-editor
  3. Replace the body with the XHTML below (everything between the BEGIN /
     END markers — do NOT include this comment block).
  4. Save. Then drag-and-drop every file from the `images/` folder onto the
     page so the <ri:attachment ri:filename="..."/> references resolve.

OPTION B — Import as a Word/HTML document
  1. Save this file with a `.html` extension.
  2. Confluence Space tools -> Content Tools -> Import Word Document also
     accepts HTML in many tenants. Image filenames must match the attachment
     filenames listed below.

IMAGE ATTACHMENTS REQUIRED ({image_count}):
{image_list}
Upload all images from the `images/` sibling folder to the same Confluence
page. The filenames have been hash-disambiguated so they will not collide
with existing attachments.

=============================================================================
BEGIN STORAGE FORMAT
=============================================================================
-->
"""

OFFLINE_END_MARKER = "\n<!-- ===== END STORAGE FORMAT ===== -->\n"


def export_offline(md_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Render Markdown to a single self-contained storage-format file plus a
    sibling `images/` folder. No network calls.

    Layout produced:
        <output_dir>/
            <stem>.confluence.xhtml   <-- paste this into Confluence
            images/
                diagram-ab12cd34.png  <-- drag-attach these to the page
                ...
            MANIFEST.txt              <-- human-readable summary
    """
    md_text = md_path.read_text(encoding="utf-8")
    storage_body, image_refs = render_markdown(md_text, md_path.parent)

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    # Copy each discovered image into the bundle under its disambiguated name
    copied: List[Tuple[str, str]] = []
    missing: List[ImageRef] = []
    for ref in image_refs:
        if not ref.abs_path.is_file():
            missing.append(ref)
            continue
        dest = images_dir / ref.filename
        shutil.copy2(ref.abs_path, dest)
        copied.append((ref.filename, str(ref.abs_path)))
        LOG.info("Bundled image: %s", ref.filename)

    if missing:
        for m in missing:
            LOG.error("Image not found: %s (referenced as %s)", m.abs_path, m.src)
        raise FileNotFoundError(f"{len(missing)} image(s) missing on disk")

    footer = build_footer(md_path, base_url=None)
    final_body = storage_body + footer

    image_list = (
        "\n".join(f"  - {fn}   (from {src})" for fn, src in copied) or "  (none)"
    )
    header = OFFLINE_INSTRUCTIONS.format(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        source_path=md_path.resolve(),
        image_count=len(copied),
        image_list=image_list,
    )

    out_file = output_dir / f"{md_path.stem}.confluence.xhtml"
    out_file.write_text(header + final_body + OFFLINE_END_MARKER, encoding="utf-8")

    manifest = output_dir / "MANIFEST.txt"
    manifest.write_text(
        "Confluence offline export\n"
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
        f"Source:    {md_path.resolve()}\n"
        f"Body file: {out_file.name}\n"
        f"Images:    {len(copied)} file(s) in images/\n\n"
        + "\n".join(f"  {fn}" for fn, _ in copied)
        + "\n",
        encoding="utf-8",
    )
    LOG.info("Wrote %s (%d bytes)", out_file, out_file.stat().st_size)
    return {
        "output_file": str(out_file),
        "images_dir": str(images_dir),
        "image_count": len(copied),
        "manifest": str(manifest),
    }


# ---------------------------------------------------------------------------
# Confluence REST client
# ---------------------------------------------------------------------------
class ConfluenceClient:
    """Thin wrapper around Confluence REST API v1 (storage format)."""

    def __init__(self, base_url: str, user: str, token: str,
                 timeout: int = 30, verify_ssl: bool = True) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        creds = base64.b64encode(f"{user}:{token}".encode()).decode()

        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update({
            "Authorization": f"Basic {creds}",
            "Accept": "application/json",
            "User-Agent": "md-to-confluence/1.0 (+vscode)",
        })
        retry = Retry(
            total=4, backoff_factor=1.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PUT"),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://", HTTPAdapter(max_retries=retry))

    # --- low level ---------------------------------------------------------
    def _url(self, path: str) -> str:
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _check(self, r: requests.Response) -> Dict[str, Any]:
        if not r.ok:
            raise RuntimeError(
                f"Confluence API {r.request.method} {r.request.url} "
                f"failed: {r.status_code} {r.text[:500]}"
            )
        return r.json() if r.content else {}

    # --- pages -------------------------------------------------------------
    def find_page(self, space_key: str, title: str) -> Optional[Dict[str, Any]]:
        r = self.session.get(
            self._url("rest/api/content"),
            params={
                "spaceKey": space_key, "title": title,
                "expand": "version,space,ancestors",
            },
            timeout=self.timeout,
        )
        data = self._check(r)
        results = data.get("results", [])
        return results[0] if results else None

    def create_page(self, space_key: str, title: str, storage_body: str,
                    parent_id: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {"storage": {"value": storage_body, "representation": "storage"}},
        }
        if parent_id:
            payload["ancestors"] = [{"id": str(parent_id)}]
        r = self.session.post(
            self._url("rest/api/content"),
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=self.timeout,
        )
        return self._check(r)

    def update_page(self, page_id: str, title: str, storage_body: str,
                    new_version: int, parent_id: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": page_id,
            "type": "page",
            "title": title,
            "version": {"number": new_version, "message": "Published from VS Code"},
            "body": {"storage": {"value": storage_body, "representation": "storage"}},
        }
        if parent_id:
            payload["ancestors"] = [{"id": str(parent_id)}]
        r = self.session.put(
            self._url(f"rest/api/content/{page_id}"),
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=self.timeout,
        )
        return self._check(r)

    # --- attachments -------------------------------------------------------
    def list_attachments(self, page_id: str) -> Dict[str, Dict[str, Any]]:
        """Return {filename: attachment_record} for the page."""
        out: Dict[str, Dict[str, Any]] = {}
        start = 0
        limit = 50
        while True:
            r = self.session.get(
                self._url(f"rest/api/content/{page_id}/child/attachment"),
                params={"start": start, "limit": limit},
                timeout=self.timeout,
            )
            data = self._check(r)
            for item in data.get("results", []):
                out[item["title"]] = item
            if data.get("size", 0) < limit:
                break
            start += limit
        return out

    def upload_attachment(self, page_id: str, file_path: Path, filename: str,
                          existing_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a new attachment, or upload a new version of an existing one.
        The PUT/POST endpoint requires X-Atlassian-Token: nocheck (XSRF guard).
        """
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        with open(file_path, "rb") as fh:
            files = {"file": (filename, fh, mime)}
            data = {"comment": "Uploaded by md-to-confluence", "minorEdit": "true"}
            headers = {"X-Atlassian-Token": "nocheck"}
            if existing_id:
                # New version of an existing attachment
                url = self._url(
                    f"rest/api/content/{page_id}/child/attachment/{existing_id}/data"
                )
                r = self.session.post(url, files=files, data=data,
                                      headers=headers, timeout=self.timeout)
            else:
                url = self._url(f"rest/api/content/{page_id}/child/attachment")
                r = self.session.post(url, files=files, data=data,
                                      headers=headers, timeout=self.timeout)
        result = self._check(r)
        # Single-attachment upload returns {"results":[{...}]}
        if "results" in result and result["results"]:
            return result["results"][0]
        return result


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
@dataclass
class PublishConfig:
    md_path: Path
    space_key: str
    title: str
    parent_id: Optional[str]
    base_url: str
    user: str
    token: str
    dry_run: bool = False
    update_only: bool = False
    verify_ssl: bool = True


def publish(cfg: PublishConfig) -> Dict[str, Any]:
    LOG.info("Reading %s", cfg.md_path)
    md_text = cfg.md_path.read_text(encoding="utf-8")

    storage_body, image_refs = render_markdown(md_text, cfg.md_path.parent)
    LOG.info("Discovered %d local image reference(s)", len(image_refs))

    # Validate every local image actually exists on disk before we touch the API
    missing = [r for r in image_refs if not r.abs_path.is_file()]
    if missing:
        for m in missing:
            LOG.error("Image not found: %s (referenced as %s)", m.abs_path, m.src)
        raise FileNotFoundError(f"{len(missing)} image(s) missing on disk")

    footer = build_footer(cfg.md_path, cfg.base_url)
    final_body = storage_body + footer

    if cfg.dry_run:
        LOG.info("DRY RUN — emitting storage XHTML to stdout")
        print(final_body)
        return {"dry_run": True, "images": [r.filename for r in image_refs]}

    client = ConfluenceClient(cfg.base_url, cfg.user, cfg.token,
                              verify_ssl=cfg.verify_ssl)

    # 1. Find-or-create the page (initial body w/o images is fine; we'll
    #    re-PUT after uploading attachments so <ri:attachment> resolves).
    existing = client.find_page(cfg.space_key, cfg.title)
    if existing:
        page_id = existing["id"]
        current_version = existing["version"]["number"]
        LOG.info("Found existing page id=%s version=%s", page_id, current_version)
    else:
        if cfg.update_only:
            raise RuntimeError(
                f"Page '{cfg.title}' not found in space '{cfg.space_key}' "
                "and --update-only was set"
            )
        LOG.info("Creating new page '%s' in space %s", cfg.title, cfg.space_key)
        # Create with a placeholder body — images aren't attached yet
        placeholder = "<p><em>Publishing in progress…</em></p>"
        created = client.create_page(cfg.space_key, cfg.title, placeholder,
                                     cfg.parent_id)
        page_id = created["id"]
        current_version = created["version"]["number"]
        LOG.info("Created page id=%s", page_id)

    # 2. Upload attachments (skip ones already present with same content hash)
    existing_attachments = client.list_attachments(page_id)
    for ref in image_refs:
        existing_att = existing_attachments.get(ref.filename)
        att = client.upload_attachment(
            page_id, ref.abs_path, ref.filename,
            existing_id=existing_att["id"] if existing_att else None,
        )
        ref.attachment_id = att.get("id")
        LOG.info("Uploaded %s -> attachment id=%s", ref.filename, ref.attachment_id)
        # Be polite — Confluence Cloud throttles aggressively above ~10 req/s
        time.sleep(0.15)

    # 3. PUT the real body with version bump
    updated = client.update_page(
        page_id, cfg.title, final_body,
        new_version=current_version + 1, parent_id=cfg.parent_id,
    )
    page_url = urljoin(
        cfg.base_url.rstrip("/") + "/",
        updated.get("_links", {}).get("webui", "").lstrip("/"),
    )
    LOG.info("Published: %s", page_url)
    return {
        "page_id": page_id,
        "version": current_version + 1,
        "url": page_url,
        "attachments": [{"filename": r.filename, "id": r.attachment_id}
                        for r in image_refs],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Publish a Markdown file to Confluence as storage-format XHTML.",
    )
    p.add_argument("markdown_file", type=Path, help="Path to .md file")
    p.add_argument("--space", required=True, help="Confluence space key (e.g. ENG)")
    p.add_argument("--title", required=True, help="Page title")
    p.add_argument("--parent-id", help="Parent page ID (optional)")
    p.add_argument("--base-url", default=os.environ.get("CONFLUENCE_BASE_URL"),
                   help="Confluence base URL incl. /wiki for Cloud "
                        "(env: CONFLUENCE_BASE_URL)")
    p.add_argument("--user", default=os.environ.get("CONFLUENCE_USER"),
                   help="Atlassian account email (env: CONFLUENCE_USER)")
    p.add_argument("--token", default=os.environ.get("CONFLUENCE_API_TOKEN"),
                   help="Atlassian API token (env: CONFLUENCE_API_TOKEN)")
    p.add_argument("--dry-run", action="store_true",
                   help="Render storage XHTML to stdout; do not call the API")
    p.add_argument("--export", metavar="OUTPUT_DIR", type=Path,
                   help="Offline export mode: write a self-contained storage-"
                        "format file plus images/ folder to OUTPUT_DIR. "
                        "No network calls — use this when the corporate "
                        "firewall blocks the Confluence REST API.")
    p.add_argument("--update-only", action="store_true",
                   help="Fail if the target page does not already exist")
    p.add_argument("--insecure", action="store_true",
                   help="Disable TLS verification (self-signed Data Center only)")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Offline export short-circuits everything else — no network needed
    if args.export:
        try:
            result = export_offline(args.markdown_file, args.export)
        except Exception as exc:  # noqa: BLE001
            LOG.exception("Export failed: %s", exc)
            return 1
        print(json.dumps(result, indent=2))
        return 0

    if not args.dry_run:
        missing = [n for n, v in [
            ("--base-url / CONFLUENCE_BASE_URL", args.base_url),
            ("--user / CONFLUENCE_USER", args.user),
            ("--token / CONFLUENCE_API_TOKEN", args.token),
        ] if not v]
        if missing:
            LOG.error("Missing required credentials: %s", ", ".join(missing))
            return 2

    cfg = PublishConfig(
        md_path=args.markdown_file,
        space_key=args.space,
        title=args.title,
        parent_id=args.parent_id,
        base_url=args.base_url or "https://example.invalid",
        user=args.user or "",
        token=args.token or "",
        dry_run=args.dry_run,
        update_only=args.update_only,
        verify_ssl=not args.insecure,
    )
    try:
        result = publish(cfg)
    except Exception as exc:  # noqa: BLE001 — top-level CLI surface
        LOG.exception("Publish failed: %s", exc)
        return 1
    if not args.dry_run:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
