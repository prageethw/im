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
import subprocess
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

# ---------------------------------------------------------------------------
# Optional system-trust-store integration
# ---------------------------------------------------------------------------
# Corporate networks (Zscaler, Netskope, etc.) terminate TLS with an internal
# CA. Python's `requests` library uses `certifi` by default, which doesn't
# include corporate CAs — leading to CERTIFICATE_VERIFY_FAILED errors.
#
# `truststore` (PEP 543) delegates verification to the operating system, which
# already trusts the corp CA (because IT installed it system-wide). It also
# tolerates legacy CAs without a `keyUsage` extension that OpenSSL 3.x rejects.
#
# We call inject_into_ssl() if it's available; the call is a no-op if the
# library is missing. Set CONFLUENCE_USE_SYSTEM_TRUST=0 to opt out.
def _enable_system_trust() -> bool:
    if os.environ.get("CONFLUENCE_USE_SYSTEM_TRUST", "1") == "0":
        return False
    try:
        import truststore  # type: ignore
        truststore.inject_into_ssl()
        return True
    except ImportError:
        return False

_SYSTEM_TRUST_ACTIVE = _enable_system_trust()

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


def render_markdown(md_text: str, source_dir: Path,
                    insert_header: bool = True,
                    status_text: str = "draft",
                    status_colour: str = "Green") -> Tuple[str, List[ImageRef]]:
    """
    Convert Markdown -> (storage_xhtml, list_of_image_refs).

    When `insert_header` is True (the default), the function:
      1. Strips any `[TOC]` / `[[_TOC_]]` markers from the raw Markdown.
      2. Renders the Markdown to storage format.
      3. Removes any pre-existing `status` / `toc` storage macros.
      4. Prepends a fresh standard header block (status badge + TOC).
    """
    if insert_header:
        md_text, removed = strip_existing_status_and_toc(md_text)
        if removed:
            LOG.info("Removed %d existing status/toc marker(s) from Markdown",
                     removed)

    renderer = StorageRenderer(source_dir=source_dir)
    md = mistune.create_markdown(
        renderer=renderer,
        plugins=["strikethrough", "table", "task_lists", "url", "footnotes"],
    )
    body = md(md_text)

    # Sweep the rendered output too, in case any macro slipped through (e.g.
    # an admonition-wrapped raw HTML block that mistune handled differently).
    if insert_header:
        body = _EMPTY_P_RE.sub("", body)
        body = build_header(status_text, status_colour) + body

    return body, renderer.image_refs


# ---------------------------------------------------------------------------
# Standard header block (status badge + table of contents)
# ---------------------------------------------------------------------------
# Inserted at the top of every page so the whole space has a consistent look.
# - `status` macro renders as a coloured pill (Green/Yellow/Red/Blue/Grey)
# - `toc` macro auto-generates a hyperlinked outline from page headings
#
# The `ac:local-id` / `ac:macro-id` values are fresh UUIDs per render so two
# rendered pages never collide if pasted into the same parent. (Confluence
# regenerates these on save anyway, but emitting unique IDs avoids editor
# warnings about duplicate macro IDs during import.)
import uuid as _uuid  # noqa: E402 — kept local to header section for readability


def build_header(status_text: str = "draft",
                 status_colour: str = "Green") -> str:
    """
    Emit the standard status-pill + TOC header block in Confluence storage
    format. New UUIDs are generated on every call so each render is unique.
    """
    status_macro_id = _uuid.uuid4()
    toc_macro_id = _uuid.uuid4()
    toc_local_id = _uuid.uuid4()
    para1_id = _uuid.uuid4().hex[:12]
    para2_id = _uuid.uuid4().hex[:12]
    return (
        f'<p local-id="{para1_id}">'
        f'<ac:structured-macro ac:name="status" ac:schema-version="1" '
        f'ac:macro-id="{status_macro_id}">'
        f'<ac:parameter ac:name="title">{html.escape(status_text)}</ac:parameter>'
        f'<ac:parameter ac:name="colour">{html.escape(status_colour)}</ac:parameter>'
        f'</ac:structured-macro> </p>'
        f'<ac:structured-macro ac:name="toc" ac:schema-version="1" '
        f'data-layout="default" ac:local-id="{toc_local_id}" '
        f'ac:macro-id="{toc_macro_id}">'
        f'<ac:parameter ac:name="style">none</ac:parameter>'
        f'<ac:parameter ac:name="exclude">(?i)document\\s+status.*|status</ac:parameter>'
        f'</ac:structured-macro>'
        f'<p local-id="{para2_id}" />\n'
    )


# ---------------------------------------------------------------------------
# Strip author-written status / TOC so we never duplicate the header
# ---------------------------------------------------------------------------
# Authors sometimes paste their own status badge or `[TOC]` / `[[_TOC_]]`
# marker into the Markdown source. After Markdown -> storage rendering we
# also need to remove any pre-existing <ac:structured-macro ac:name="toc"|
# "status"> blocks (e.g. if someone copy-pasted raw storage XHTML in).
#
# We do this BEFORE prepending our own header so the final page has exactly
# one status pill and exactly one TOC.

# Patterns removed from the RAW MARKDOWN before rendering. We do it here
# (not after rendering) because mistune wraps raw HTML in containers that
# make post-render regex matching unreliable. Cleaning the Markdown source
# is simpler and more robust.

# Markdown-level TOC markers commonly used by Pandoc / GitLab / mkdocs:
_MD_TOC_MARKERS = (
    re.compile(r"^[ \t]*\[TOC\][ \t]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[ \t]*\[\[_TOC_\]\][ \t]*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^[ \t]*<!--\s*toc\s*-->[ \t]*$", re.IGNORECASE | re.MULTILINE),
)

# Manually-authored TOC blocks: a heading whose text looks like "Table of
# Contents" / "Contents" / "Index", followed by a bullet list of in-page
# anchor links. We match the heading line, then consume every following line
# that is part of the bullet list (blank lines inside the list are allowed),
# stopping at the next heading or the first non-list / non-blank line.
#
# The list-detection part uses a fairly conservative definition of "bullet
# list item": leading whitespace, then `-`, `*`, `+`, or `N.`, then content
# that includes at least one in-page link `](#...)`. This avoids accidentally
# eating prose lists that happen to follow a Contents heading.
_MANUAL_TOC_HEADING_RE = re.compile(
    r"^(?P<hashes>\#{1,6})[ \t]+"
    r"(?:table\s+of\s+contents|contents|index|toc)"
    r"[ \t:.]*$",
    re.IGNORECASE | re.MULTILINE,
)
# A manually-written "## Document status" (or "## Status") heading. The
# auto-injected status pill replaces it, so we strip the heading and any
# content (table or paragraph) that follows until the next heading.
_MANUAL_STATUS_HEADING_RE = re.compile(
    r"^(?P<hashes>\#{1,6})[ \t]+"
    r"(?:document[ \t]+status|status)"
    r"[ \t:.]*$",
    re.IGNORECASE | re.MULTILINE,
)
_ANCHOR_LIST_ITEM_RE = re.compile(
    r"^[ \t]*(?:[-*+]|\d+\.)[ \t]+.*\]\(#[^)]+\)",
)
_NEXT_HEADING_RE = re.compile(r"^\#{1,6}[ \t]+")

# H1 headings to strip from the Markdown source. The Confluence page title
# already serves as the document's top-level heading, so an in-body H1 is
# redundant (and would appear as a duplicate H1 in the TOC macro).
# Matches both ATX-style (`# Heading`) and Setext-style (`Heading\n=====`).
_ATX_H1_RE = re.compile(r"^[ \t]*\#[ \t]+[^\n]*\n?", re.MULTILINE)
_SETEXT_H1_RE = re.compile(r"^[^\n]+\n=+[ \t]*\n?", re.MULTILINE)

# Raw `<ac:structured-macro ac:name="toc|status">...</ac:structured-macro>`
# blocks that an author pasted into the Markdown source. The regex is
# permissive about attribute order, whitespace, and multi-line content.
# Matches either a self-closing `<.../>` form or a paired open/close form.
_MD_MACRO_RE = re.compile(
    r'<ac:structured-macro\b[^>]*?\bac:name="(?:toc|status)"[^>]*?'
    r'(?:/>|>.*?</ac:structured-macro>)',
    re.DOTALL | re.IGNORECASE,
)

# After stripping a macro, a wrapping <p>...</p> may be left holding only
# whitespace. Drop those so we don't accumulate blank paragraphs.
_EMPTY_P_RE = re.compile(r"<p\b[^>]*>\s*</p>", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Title / Git / Pretty-format helpers
# ---------------------------------------------------------------------------
# First ATX H1 (`# Title text`) in the source. Used to default --title from
# the document's own top-level heading when the caller omits --title.
_FIRST_H1_RE = re.compile(
    r"^[ \t]*\#[ \t]+(?P<title>[^\n]+?)[ \t]*$",
    re.MULTILINE,
)


def _strip_inline_markdown(text: str) -> str:
    """
    Render a piece of inline-Markdown to plain text so it can be used as a
    Confluence page title. Strips backticks, bold/italic markers, and link
    syntax (keeps the link label, drops the URL).
    """
    # [label](url) -> label
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # `code` -> code
    text = re.sub(r"`+([^`]+)`+", r"\1", text)
    # **bold** / __bold__ -> bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    # *italic* / _italic_ -> italic
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?<!_)_([^_\n]+)_(?!_)", r"\1", text)
    return text.strip()


def extract_h1_title(md_text: str) -> Optional[str]:
    """
    Return the cleaned text of the first ATX `# H1` heading in the source
    Markdown, ignoring H1s inside fenced code blocks. Returns None when no
    H1 is present.
    """
    # Mask fenced code blocks so we don't pick up `# comments` in code.
    masked_parts: List[str] = []
    in_fence = False
    for line in md_text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            masked_parts.append("\n")
            continue
        masked_parts.append("\n" if in_fence else line)
    masked = "".join(masked_parts)

    m = _FIRST_H1_RE.search(masked)
    if not m:
        return None
    raw = m.group("title")
    cleaned = _strip_inline_markdown(raw)
    return cleaned or None


def _run_git(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    """Run `git <args>` in cwd and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        raise RuntimeError(
            "git executable not found on PATH; install git or rerun with "
            "--no-git-check to bypass the dirty-tree guard"
        ) from exc


def assert_committed_to_local_git(md_path: Path) -> None:
    """
    Verify that md_path lives inside a Git repository AND is fully committed
    locally (no uncommitted edits, no untracked status). Raises RuntimeError
    with a clear, actionable message otherwise.

    NOTE: This checks the *local* working tree only — there is no requirement
    to push. "Commit to local git first" is exactly what is enforced.
    """
    md_path = md_path.resolve()
    if not md_path.is_file():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    # 1. Are we inside a Git work tree?
    rc, out, _ = _run_git(
        ["rev-parse", "--is-inside-work-tree"], cwd=md_path.parent
    )
    if rc != 0 or out.strip() != "true":
        raise RuntimeError(
            f"{md_path} is not inside a Git repository. "
            "Initialise one (`git init`) and commit the file before publishing, "
            "or rerun with --no-git-check to bypass this guard."
        )

    # 2. Resolve repo root so we can ask for the file's status via a path that
    #    Git will recognise regardless of where the script was invoked from.
    rc, root_out, _ = _run_git(["rev-parse", "--show-toplevel"], cwd=md_path.parent)
    if rc != 0:
        raise RuntimeError("Could not determine Git repository root.")
    repo_root = Path(root_out.strip())
    rel_path = md_path.relative_to(repo_root)

    # 3. Status of THIS file specifically (porcelain v1 is stable + parseable).
    rc, status_out, status_err = _run_git(
        ["status", "--porcelain", "--", str(rel_path)],
        cwd=repo_root,
    )
    if rc != 0:
        raise RuntimeError(
            f"git status failed for {rel_path}: {status_err.strip()}"
        )

    status_out = status_out.rstrip("\n")
    if not status_out:
        # Empty -> file is tracked AND clean.
        return

    # Non-empty: parse the first 2 chars per line for diagnostics.
    problems: List[str] = []
    for line in status_out.splitlines():
        code = line[:2]
        path = line[3:]
        if code == "??":
            problems.append(f"untracked: {path}")
        elif code.strip() == "":
            continue
        else:
            problems.append(f"{code.strip()}: {path}")

    raise RuntimeError(
        "Refusing to publish: the Markdown file has uncommitted changes "
        "in your local Git repository. Commit (or stash) the file first.\n"
        f"  File: {rel_path}\n"
        f"  Status: {', '.join(problems) or status_out}\n"
        "  Fix:    git add " + str(rel_path) + " && git commit -m '...'\n"
        "  Bypass: rerun with --no-git-check (not recommended)"
    )


# Packages auto-installed by _ensure_mdformat() on first prettify pass.
# Kept here so the policy is in one obvious place and so the GFM plugin can
# evolve without touching call sites.
_MDFORMAT_REQUIREMENTS = ("mdformat", "mdformat-gfm", "mdformat-tables")


def _pip_install(packages: Tuple[str, ...]) -> bool:
    """
    Install `packages` into the currently active Python environment using
    `python -m pip install --quiet`. Returns True on success, False otherwise.

    We deliberately use the same interpreter that's running the script
    (`sys.executable`) so a venv-installed Python still installs into its
    own site-packages, not the system Python.
    """
    cmd = [sys.executable, "-m", "pip", "install", "--quiet",
           "--disable-pip-version-check", *packages]
    LOG.info("Installing %s via pip ...", " ".join(packages))
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, check=False,
            timeout=180,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        LOG.warning("pip install failed (%s); falling back to built-in "
                    "normaliser", exc)
        return False
    if proc.returncode != 0:
        # Common cause behind corporate proxies: pip cannot reach PyPI.
        # Surface the last bit of stderr so the user knows why.
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-3:]
        LOG.warning("pip install failed (exit %d). Last output:\n  %s\n"
                    "Falling back to built-in normaliser. To skip this "
                    "step entirely, pass --no-prettify.",
                    proc.returncode, "\n  ".join(tail))
        return False
    LOG.info("pip install succeeded for %s", ", ".join(packages))
    return True


def _ensure_mdformat(auto_install: bool = True):  # noqa: ANN202
    """
    Return an imported `mdformat` module, installing it (and the GFM +
    tables plugins) on first call if necessary. Returns None if the import
    cannot be satisfied (e.g. offline behind a corp proxy).
    """
    try:
        import mdformat  # type: ignore
        return mdformat
    except ImportError:
        pass

    if not auto_install:
        return None

    # Try to install. If pip can't reach PyPI we just return None and the
    # caller falls back to the built-in normaliser.
    if not _pip_install(_MDFORMAT_REQUIREMENTS):
        return None

    try:
        import mdformat  # type: ignore
        return mdformat
    except ImportError as exc:
        LOG.warning("mdformat installed but cannot be imported: %s", exc)
        return None


def prettify_markdown(md_text: str, auto_install: bool = True) -> str:
    """
    Return a pretty-formatted copy of `md_text` for upload to Confluence.
    Never writes to disk; the local file is untouched.

    Strategy:
      1. Prefer `mdformat` (auto-installed on first run via pip if missing).
         It's the de-facto Python Markdown formatter and is conservative
         (CommonMark compliant, doesn't reflow paragraphs). We also pull in
         `mdformat-gfm` and `mdformat-tables` so GitHub-flavoured tables and
         admonitions are preserved.
      2. If pip cannot install (no internet, corp proxy block, offline),
         fall back to a built-in normaliser that:
           - normalises line endings to LF
           - strips trailing whitespace on every line
           - collapses 3+ blank lines down to 2
           - ensures exactly one trailing newline at EOF
    """
    mdformat = _ensure_mdformat(auto_install=auto_install)

    if mdformat is not None:
        try:
            formatted = mdformat.text(md_text)
            LOG.info("Pretty-formatted Markdown via mdformat (in-memory only)")
            return formatted
        except Exception as exc:  # noqa: BLE001
            LOG.warning(
                "mdformat available but failed (%s); using built-in normaliser",
                exc,
            )

    # Built-in fallback — purely whitespace/newline cleanup, no structural
    # changes. Won't break code blocks, tables, or any Markdown construct.
    text = md_text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not text.endswith("\n"):
        text += "\n"
    LOG.info("Pretty-formatted Markdown via built-in normaliser (in-memory only)")
    return text


def _strip_manual_status_blocks(md_text: str) -> Tuple[str, int]:
    """
    Remove hand-written "## Document status" (or "## Status") sections,
    including any Markdown table or paragraph that follows the heading,
    up to (but not including) the next heading. Returns (cleaned, count).

    Algorithm:
      1. Find each heading line that looks like a status heading.
      2. Consume the heading + every subsequent line that is blank, a
         Markdown table row (starts with `|`), or non-heading paragraph
         text. Stop at the first heading line encountered.
      3. Delete the heading and all consumed lines.
    """
    lines = md_text.splitlines(keepends=True)
    keep: List[str] = []
    i = 0
    removed_blocks = 0
    n_lines = len(lines)

    while i < n_lines:
        line = lines[i]
        if _MANUAL_STATUS_HEADING_RE.match(line):
            # Consume the heading + the whole block beneath it. We accept
            # blank lines, table rows (lines beginning with `|`), and
            # paragraph lines. We stop at the next Markdown heading.
            j = i + 1
            while j < n_lines:
                s = lines[j]
                if _NEXT_HEADING_RE.match(s):
                    break
                j += 1
            removed_blocks += 1
            i = j
            continue

        keep.append(line)
        i += 1

    return "".join(keep), removed_blocks


def _strip_manual_toc_blocks(md_text: str) -> Tuple[str, int]:
    """
    Remove hand-written "## Table of contents" sections followed by a bullet
    list of in-page anchor links. Returns (cleaned, count_removed_blocks).

    Algorithm:
      1. Find each heading line that looks like a Contents heading.
      2. Walk forward line-by-line. A line is part of the TOC block if it's
         blank, indented continuation, or a bullet/numbered item that links
         to an in-page anchor (`](#...)`). Stop at the first line that is
         neither of those and isn't blank — in particular, stop at the next
         heading.
      3. Delete the heading and all consumed lines.
    """
    lines = md_text.splitlines(keepends=True)
    keep: List[str] = []
    i = 0
    removed_blocks = 0
    n_lines = len(lines)

    while i < n_lines:
        line = lines[i]
        if _MANUAL_TOC_HEADING_RE.match(line):
            # Look ahead: do we have at least one anchor-list item before the
            # next heading? If not, leave this heading alone (it might just
            # be a section called "Contents" with prose underneath).
            j = i + 1
            saw_anchor_item = False
            scan = j
            while scan < n_lines:
                s = lines[scan]
                if _NEXT_HEADING_RE.match(s):
                    break
                if _ANCHOR_LIST_ITEM_RE.match(s):
                    saw_anchor_item = True
                    break
                if s.strip() == "":
                    scan += 1
                    continue
                # Some other content — not a TOC block
                break

            if not saw_anchor_item:
                keep.append(line)
                i += 1
                continue

            # Consume the heading + the whole TOC block. We accept blank
            # lines and indented continuation lines as part of the list.
            j = i + 1
            while j < n_lines:
                s = lines[j]
                if _NEXT_HEADING_RE.match(s):
                    break
                if s.strip() == "":
                    j += 1
                    continue
                if _ANCHOR_LIST_ITEM_RE.match(s):
                    j += 1
                    continue
                # Indented continuation of a previous bullet (nested list)
                if s.startswith(("  ", "\t")) and s.strip():
                    j += 1
                    continue
                break
            removed_blocks += 1
            i = j
            continue

        keep.append(line)
        i += 1

    return "".join(keep), removed_blocks


def strip_existing_status_and_toc(md_text: str) -> Tuple[str, int]:
    """
    Remove `[TOC]`-style markers, raw status/toc storage macros, AND any
    manually-authored "Table of contents" sections that appear in the
    Markdown source. Returns (cleaned_md, count_removed).
    """
    removed = 0

    def _drop(_m: re.Match) -> str:
        nonlocal removed
        removed += 1
        return ""

    # 1. Raw storage macros (status / toc)
    out = _MD_MACRO_RE.sub(_drop, md_text)

    # 2. Inline TOC markers ([TOC], [[_TOC_]], <!-- toc -->)
    for pat in _MD_TOC_MARKERS:
        out, n = pat.subn("", out)
        removed += n

    # 3. Hand-written "## Table of contents" + bullet-anchor list blocks
    out, n = _strip_manual_toc_blocks(out)
    removed += n

    # 4. H1 headings (ATX `# ...` and Setext `...\n===`). The page title
    #    already serves this role.
    out, n = _strip_h1_headings(out)
    removed += n

    # Collapse blank-line runs created by deletions
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out, removed


def _strip_h1_headings(md_text: str) -> Tuple[str, int]:
    """
    Remove all top-level (H1) headings from the Markdown source.

    Handles two cases:
      * ATX style:    `# Heading`
      * Setext style: `Heading\n=======`

    Care is taken NOT to strip inside fenced code blocks — a line like
    `# hello world` inside a ```python block is a comment, not a heading.
    """
    # Split on fenced code blocks so we only process Markdown prose regions.
    # A simple state machine is more robust than a single regex here.
    parts = re.split(r"(```[^\n]*\n.*?\n```)", md_text, flags=re.DOTALL)
    removed = 0
    for idx, part in enumerate(parts):
        if part.startswith("```"):
            continue  # leave fenced blocks untouched
        # ATX `# Heading` — but not `##`, `###`, etc.
        part_new, n1 = _ATX_H1_RE.subn("", part)
        # Setext `Heading\n=====`
        part_new, n2 = _SETEXT_H1_RE.subn("", part_new)
        removed += n1 + n2
        parts[idx] = part_new
    return "".join(parts), removed


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


def export_offline(md_path: Path, output_dir: Path,
                   status_text: str = "draft",
                   status_colour: str = "Green",
                   prettify: bool = True,
                   auto_install_mdformat: bool = True) -> Dict[str, Any]:
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

    The on-disk Markdown file is never modified, even when `prettify=True`;
    the formatter runs purely in memory against the loaded text.
    """
    md_text = md_path.read_text(encoding="utf-8")
    if prettify:
        md_text = prettify_markdown(md_text, auto_install=auto_install_mdformat)
    storage_body, image_refs = render_markdown(
        md_text, md_path.parent,
        status_text=status_text, status_colour=status_colour,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)
    # Note: footer + comment header are intentionally omitted from offline
    # exports — the output should be a clean Confluence page body, ready
    # to paste with no manual cleanup.

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

    out_file = output_dir / f"{md_path.stem}.confluence.xhtml"
    out_file.write_text(storage_body, encoding="utf-8")

    # The MANIFEST.txt remains as a sidecar so users know which images to
    # drag-attach — it lives alongside the XHTML file, not inside it.
    manifest = output_dir / "MANIFEST.txt"
    manifest.write_text(
        "Confluence offline export\n"
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
        f"Source:    {md_path.resolve()}\n"
        f"Body file: {out_file.name}\n"
        f"Images:    {len(copied)} file(s) in images/\n\n"
        "To publish:\n"
        f"  1. Paste the contents of {out_file.name} into Confluence's\n"
        "     source / storage-format editor.\n"
        "  2. Drag-attach every file from images/ to the same page.\n\n"
        "Images to attach:\n"
        + ("\n".join(f"  {fn}" for fn, _ in copied) or "  (none)")
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
# Pre-publish integrity check
# ---------------------------------------------------------------------------
# Sentinels that StorageRenderer injects around centred images while it's
# stitching paragraphs together. They MUST be stripped by paragraph() before
# the body leaves the renderer; if any survive into the final body the
# rendering pipeline is broken and the page would render as garbage in
# Confluence. We treat their presence as a hard fail.
_RENDER_SENTINELS = ("\x00CENTERED_IMG\x00", "\x00END_IMG\x00")

# Unresolved Markdown link/image syntax that should have been consumed by
# mistune. If any of these survive, the parser likely choked on the source.
_UNRESOLVED_MD_PATTERNS = (
    re.compile(r"^!\[[^\]]*\]\([^)]+\)\s*$", re.MULTILINE),  # raw image
)


def validate_publish_payload(
    storage_body: str,
    image_refs: List[ImageRef],
    md_path: Path,
) -> None:
    """
    Pre-flight integrity check run BEFORE any Confluence API call.

    Aborts with RuntimeError when any of the following are detected:
      * A local image referenced in the Markdown is missing on disk.
      * A local image exists but isn't readable (perm error / dangling
        symlink). Catching this here means we never half-create a page
        and then fail mid-upload.
      * The rendered storage body still contains internal renderer
        sentinels — that's a hard sign the renderer broke and the output
        would look corrupt in Confluence.
      * The rendered body is empty or below a sanity-check size.
      * Confluence storage-macro tags appear unbalanced (open without
        matching close).

    Returns None on success. The caller continues to the network step.
    """
    problems: List[str] = []

    # --- 1. Image existence + readability ----------------------------------
    missing: List[ImageRef] = []
    unreadable: List[Tuple[ImageRef, str]] = []
    for ref in image_refs:
        if not ref.abs_path.is_file():
            missing.append(ref)
            continue
        try:
            # Open + read 1 byte to catch permission errors and dangling
            # symlinks. Cheap and short-circuits early.
            with open(ref.abs_path, "rb") as fh:
                _ = fh.read(1)
        except OSError as exc:
            unreadable.append((ref, str(exc)))

    if missing:
        for m in missing:
            LOG.error("Image not found: %s (referenced as %s)", m.abs_path, m.src)
        problems.append(
            f"{len(missing)} image(s) referenced by the Markdown do not "
            f"exist on disk: " + ", ".join(m.src for m in missing)
        )
    if unreadable:
        for ref, err in unreadable:
            LOG.error("Image unreadable: %s (%s)", ref.abs_path, err)
        problems.append(
            f"{len(unreadable)} image file(s) exist but cannot be read: "
            + ", ".join(f"{r.src} ({e})" for r, e in unreadable)
        )

    # --- 2. Renderer sentinel leakage --------------------------------------
    for sentinel in _RENDER_SENTINELS:
        if sentinel in storage_body:
            problems.append(
                f"Internal renderer sentinel {sentinel!r} leaked into the "
                "final storage body — this is a script bug and the page "
                "would render as garbage in Confluence."
            )
            break  # one is enough; don't spam the same diagnosis twice

    # --- 3. Sanity check on body size --------------------------------------
    stripped = storage_body.strip()
    if not stripped:
        problems.append(
            "Rendered Confluence storage body is empty. The Markdown "
            "source produced no content after stripping headers/TOC blocks."
        )
    elif len(stripped) < 32:
        # 32 bytes is well below any plausible real page — even an empty
        # status pill + TOC macro is ~200 bytes. This catches degenerate
        # renders where every paragraph was eaten by an over-broad stripper.
        problems.append(
            f"Rendered storage body is suspiciously small ({len(stripped)} "
            f"bytes). Source: {md_path.name}. Likely cause: an over-broad "
            "strip rule consumed real content."
        )

    # --- 4. Unresolved Markdown leakage ------------------------------------
    # The renderer should consume all `![alt](src)` image syntax. If raw
    # Markdown image syntax survives at start-of-line in the storage body,
    # mistune likely couldn't parse it (e.g. malformed alt-text with stray
    # backticks). Confluence would display it as literal text.
    for pat in _UNRESOLVED_MD_PATTERNS:
        match = pat.search(storage_body)
        if match:
            problems.append(
                f"Unresolved Markdown syntax in rendered body: "
                f"{match.group(0)!r}. The Markdown parser could not "
                "consume this construct — fix the source and re-run."
            )
            break

    # --- 5. Confluence macro tag balance -----------------------------------
    # Self-closing forms (<ac:foo .../>) are fine, but for the open/close
    # paired form the counts must match.
    open_macros = len(re.findall(
        r"<ac:structured-macro\b(?![^>]*\/>)", storage_body
    ))
    close_macros = storage_body.count("</ac:structured-macro>")
    if open_macros != close_macros:
        problems.append(
            f"Unbalanced Confluence storage macros: {open_macros} open vs "
            f"{close_macros} close. The page body would be malformed."
        )

    if problems:
        formatted = "\n  - ".join(problems)
        raise RuntimeError(
            "Pre-publish integrity check FAILED — refusing to write to "
            "Confluence:\n  - " + formatted + "\n"
            "\nNo API calls were made; your Confluence space is untouched. "
            "Fix the issues above and re-run, or pass --dry-run / --export "
            "to inspect the output without publishing."
        )

    LOG.info(
        "Pre-publish integrity check passed (%d image(s), %d byte body)",
        len(image_refs), len(stripped),
    )


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
# Connectivity check (read-only — safe to run from a firewalled corporate box)
# ---------------------------------------------------------------------------
def check_connectivity(base_url: str, user: str, token: str,
                       space_key: Optional[str] = None,
                       verify_ssl: bool = True) -> int:
    """
    Run a sequence of read-only probes against Confluence and print a
    diagnosis. Returns a process exit code (0 = all good, non-zero = fail).

    Probes, in order:
      1. DNS / TCP / TLS reachability of the base URL
      2. /rest/api/user/current  -> validates the API token + identifies you
      3. /rest/api/space         -> validates that we can list spaces
      4. /rest/api/space/{KEY}   -> if --space provided, confirms write target
      5. HEAD on a known content endpoint -> sanity-check rate limit headers

    Every probe is a GET. Nothing is created, modified, or deleted.
    """
    print("=" * 70)
    print("Confluence connectivity check")
    print("=" * 70)
    print(f"Base URL : {base_url}")
    print(f"User     : {user}")
    print(f"Token    : {'*' * 4}{token[-4:] if len(token) >= 4 else '****'} "
          f"({len(token)} chars)")
    print(f"Space    : {space_key or '(not specified)'}")
    print(f"TLS verify: {verify_ssl}")
    print(f"System trust store: {'ACTIVE (truststore)' if _SYSTEM_TRUST_ACTIVE else 'inactive (using certifi)'}")
    print("-" * 70)

    failures: List[str] = []
    warnings: List[str] = []

    # --- Probe 0: basic URL sanity ------------------------------------------
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https"):
        print("✗ Base URL must start with http:// or https://")
        return 2
    if not parsed.netloc:
        print("✗ Base URL is missing a hostname")
        return 2
    # Cloud tenants must include /wiki — easy thing to get wrong
    if "atlassian.net" in parsed.netloc and not parsed.path.rstrip("/").endswith("/wiki"):
        warnings.append(
            "Cloud base URL should end with /wiki "
            f"(e.g. https://{parsed.netloc}/wiki). Current path: {parsed.path!r}"
        )

    try:
        client = ConfluenceClient(base_url, user, token, verify_ssl=verify_ssl)
    except Exception as exc:  # noqa: BLE001
        print(f"✗ Could not initialise HTTP client: {exc}")
        return 1

    # --- Probe 1: TCP / TLS reachability ------------------------------------
    print("[1/5] Reachability ...", end=" ", flush=True)
    try:
        # No auth, no API call — just see if we can open the socket.
        # Using HEAD on the base URL is the lightest possible request.
        r = client.session.head(base_url, timeout=10, allow_redirects=True)
        print(f"OK (HTTP {r.status_code})")
    except requests.exceptions.SSLError as exc:
        print("FAIL")
        failures.append(
            f"TLS handshake failed: {exc}. "
            "If this is Data Center with a self-signed cert, retry with --insecure."
        )
    except requests.exceptions.ConnectTimeout:
        print("FAIL")
        failures.append(
            "Connection timed out. The corporate firewall or proxy is likely "
            "blocking outbound traffic to this host. Check HTTPS_PROXY env var."
        )
    except requests.exceptions.ConnectionError as exc:
        print("FAIL")
        msg = str(exc)
        if "NameResolutionError" in msg or "getaddrinfo" in msg:
            failures.append(f"DNS lookup failed for {parsed.netloc}: {exc}")
        elif "ProxyError" in msg:
            failures.append(f"Proxy error: {exc}. Check HTTPS_PROXY / NO_PROXY.")
        else:
            failures.append(f"Cannot connect: {exc}")
    except Exception as exc:  # noqa: BLE001
        print("FAIL")
        failures.append(f"Unexpected error: {exc}")

    if failures:
        _print_diagnosis(failures, warnings)
        return 1

    # --- Probe 2: authentication -- /rest/api/user/current ------------------
    print("[2/5] Authentication ...", end=" ", flush=True)
    try:
        r = client.session.get(client._url("rest/api/user/current"), timeout=15)
        if r.status_code == 200:
            me = r.json()
            display = me.get("displayName") or me.get("username") or me.get("accountId")
            account_type = me.get("accountType", "unknown")
            print(f"OK — authenticated as '{display}' ({account_type})")
        elif r.status_code == 401:
            print("FAIL")
            failures.append(
                "401 Unauthorized. The API token is invalid, expired, or "
                "the email/username doesn't match the token owner. For "
                "Atlassian Cloud, the username MUST be the account email "
                "and the token must come from id.atlassian.com/manage-profile"
                "/security/api-tokens."
            )
        elif r.status_code == 403:
            print("FAIL")
            failures.append(
                "403 Forbidden. Token is valid but lacks permission to read "
                "the current user. Token scopes may be restricted, or your "
                "account has been disabled."
            )
        else:
            print(f"FAIL (HTTP {r.status_code})")
            failures.append(f"Unexpected status {r.status_code}: {r.text[:300]}")
    except Exception as exc:  # noqa: BLE001
        print("FAIL")
        failures.append(f"Auth probe error: {exc}")

    if failures:
        _print_diagnosis(failures, warnings)
        return 1

    # --- Probe 3: list spaces (read scope) ----------------------------------
    print("[3/5] Read scope (list spaces) ...", end=" ", flush=True)
    try:
        r = client.session.get(
            client._url("rest/api/space"),
            params={"limit": 1}, timeout=15,
        )
        if r.status_code == 200:
            total = r.json().get("size", 0)
            print(f"OK ({total} space visible in first page)")
        else:
            print(f"FAIL (HTTP {r.status_code})")
            failures.append(
                f"Cannot list spaces (HTTP {r.status_code}). Token likely "
                "lacks `read:confluence-space.summary` scope."
            )
    except Exception as exc:  # noqa: BLE001
        print("FAIL")
        failures.append(f"Space-list probe error: {exc}")

    # --- Probe 4: target space exists & is writable -------------------------
    if space_key:
        print(f"[4/5] Target space '{space_key}' ...", end=" ", flush=True)
        try:
            r = client.session.get(
                client._url(f"rest/api/space/{space_key}"),
                params={"expand": "permissions"}, timeout=15,
            )
            if r.status_code == 200:
                space = r.json()
                name = space.get("name", space_key)
                stype = space.get("type", "unknown")
                print(f"OK — '{name}' (type={stype})")
                # Probe write permission by trying to read recent content.
                # (A true write probe would require creating a page, which
                # we deliberately don't do here.)
            elif r.status_code == 404:
                print("FAIL")
                failures.append(
                    f"Space '{space_key}' not found, or your account cannot "
                    "see it. Double-check the space KEY (not the name) in "
                    "the URL: .../wiki/spaces/<KEY>/..."
                )
            elif r.status_code == 403:
                print("FAIL")
                failures.append(
                    f"Forbidden on space '{space_key}'. Token authenticated "
                    "but the account lacks View permission on this space."
                )
            else:
                print(f"FAIL (HTTP {r.status_code})")
                failures.append(f"Space probe returned {r.status_code}")
        except Exception as exc:  # noqa: BLE001
            print("FAIL")
            failures.append(f"Space probe error: {exc}")
    else:
        print("[4/5] Target space ... SKIPPED (no --space provided)")
        warnings.append(
            "Pass --space <KEY> to verify the target space is reachable "
            "before publishing."
        )

    # --- Probe 5: rate-limit / quota headers --------------------------------
    print("[5/5] Rate-limit headers ...", end=" ", flush=True)
    try:
        r = client.session.get(
            client._url("rest/api/content"),
            params={"limit": 1}, timeout=15,
        )
        remaining = r.headers.get("X-RateLimit-Remaining")
        limit = r.headers.get("X-RateLimit-Limit")
        if remaining is not None:
            print(f"OK (remaining={remaining}/{limit})")
        else:
            print("OK (no rate-limit headers exposed)")
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: {exc}")
        warnings.append(f"Rate-limit probe non-fatal error: {exc}")

    _print_diagnosis(failures, warnings)
    return 0 if not failures else 1


def _print_diagnosis(failures: List[str], warnings: List[str]) -> None:
    print("-" * 70)
    if failures:
        print(f"RESULT: ✗ {len(failures)} failure(s) — publishing will NOT work")
        for i, f in enumerate(failures, 1):
            print(f"  {i}. {f}")
    else:
        print("RESULT: ✓ All probes passed — safe to publish")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for i, w in enumerate(warnings, 1):
            print(f"  {i}. {w}")
    print("=" * 70)


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
    status_text: str = "draft"
    status_colour: str = "Green"
    prettify: bool = True
    auto_install_mdformat: bool = True


def publish(cfg: PublishConfig) -> Dict[str, Any]:
    LOG.info("Reading %s", cfg.md_path)
    md_text = cfg.md_path.read_text(encoding="utf-8")

    # Pretty-format the Markdown in memory before rendering. The on-disk
    # file is NEVER modified; only the upload pipeline sees the formatted
    # version. The guard above already enforced a clean Git working tree
    # so the local copy stays authoritative.
    if cfg.prettify:
        md_text = prettify_markdown(
            md_text, auto_install=cfg.auto_install_mdformat
        )

    # Render Markdown. If rendering itself throws (mistune parser bombs out,
    # unbalanced fences, broken plugin, etc.) we abort BEFORE any network
    # call so a half-baked page is never created on Confluence.
    try:
        storage_body, image_refs = render_markdown(
            md_text, cfg.md_path.parent,
            status_text=cfg.status_text, status_colour=cfg.status_colour,
        )
    except Exception as exc:  # noqa: BLE001 — render is third-party
        raise RuntimeError(
            f"Markdown rendering failed for {cfg.md_path.name}: {exc}. "
            "Refusing to publish a partial page to Confluence. "
            "Fix the Markdown source and re-run."
        ) from exc
    LOG.info("Discovered %d local image reference(s)", len(image_refs))

    # Run the full pre-flight integrity check (images, payload sanity).
    # Any failure here raises RuntimeError BEFORE the API client is
    # constructed, so Confluence never sees a partial publish.
    validate_publish_payload(storage_body, image_refs, cfg.md_path)

    final_body = storage_body

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
    p.add_argument("markdown_file", type=Path, nargs="?",
                   help="Path to .md file (omit when using --check)")
    p.add_argument("--space", help="Confluence space key (e.g. ENG). "
                                    "Required for publish; optional for --check.")
    p.add_argument("--title", help="Page title. If omitted, the first "
                                    "`# H1` heading in the Markdown file is "
                                    "used as the title.")
    p.add_argument("--no-git-check", action="store_true",
                   help="Bypass the local-Git committed-state check. By "
                        "default the script refuses to publish when the "
                        "Markdown file has uncommitted edits or is untracked.")
    p.add_argument("--no-prettify", action="store_true",
                   help="Skip the in-memory Markdown pretty-format pass "
                        "that runs before rendering. The local file is "
                        "never modified either way; this flag only turns "
                        "the normalisation off.")
    p.add_argument("--no-auto-install", action="store_true",
                   help="Do NOT auto-pip-install mdformat on first run. "
                        "If mdformat is missing the script will use its "
                        "built-in whitespace normaliser instead. Useful "
                        "behind corporate proxies that block PyPI.")
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
    p.add_argument("--check", action="store_true",
                   help="Validate connectivity, auth, and (optionally) space "
                        "access using read-only API calls. Nothing is created "
                        "or modified. Run this BEFORE attempting a publish.")
    p.add_argument("--status", default="draft",
                   help="Status pill text inserted at top of page "
                        "(default: 'draft')")
    p.add_argument("--status-colour", "--status-color", default="Green",
                   choices=["Grey", "Red", "Yellow", "Green", "Blue"],
                   help="Status pill colour (default: Green)")
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

    # --check short-circuits everything — read-only probes only
    if args.check:
        missing = [n for n, v in [
            ("--base-url / CONFLUENCE_BASE_URL", args.base_url),
            ("--user / CONFLUENCE_USER", args.user),
            ("--token / CONFLUENCE_API_TOKEN", args.token),
        ] if not v]
        if missing:
            LOG.error("Missing required credentials: %s", ", ".join(missing))
            return 2
        return check_connectivity(
            base_url=args.base_url, user=args.user, token=args.token,
            space_key=args.space, verify_ssl=not args.insecure,
        )

    # Offline export short-circuits everything else — no network needed
    if args.export:
        if not args.markdown_file:
            LOG.error("--export requires a markdown_file argument")
            return 2

        # Git-clean guard (same policy as publish mode).
        if not args.no_git_check:
            try:
                assert_committed_to_local_git(args.markdown_file)
            except (RuntimeError, FileNotFoundError) as exc:
                LOG.error("%s", exc)
                return 2

        # Default the page title from the first H1 if the caller didn't pass
        # one. Export still needs a title because the auto-injected status
        # pill block prefers a known page title for log output.
        if not args.title:
            try:
                src = args.markdown_file.read_text(encoding="utf-8")
            except Exception as exc:  # noqa: BLE001
                LOG.error("Could not read %s: %s", args.markdown_file, exc)
                return 2
            inferred = extract_h1_title(src)
            if inferred:
                LOG.info("--title not supplied; using first H1 as title: %r",
                         inferred)
                args.title = inferred
            else:
                LOG.warning("No --title and no `# H1` heading found; export "
                            "will proceed without a title.")

        try:
            result = export_offline(
                args.markdown_file, args.export,
                status_text=args.status, status_colour=args.status_colour,
                prettify=not args.no_prettify,
                auto_install_mdformat=not args.no_auto_install,
            )
        except Exception as exc:  # noqa: BLE001
            LOG.exception("Export failed: %s", exc)
            return 1
        print(json.dumps(result, indent=2))
        return 0

    # Publish mode: markdown_file and --space are required; --title is
    # inferred from the first H1 when omitted.
    if not args.markdown_file:
        LOG.error("markdown_file argument is required for publish mode")
        return 2
    if not args.space:
        LOG.error("--space is required for publish mode")
        return 2

    # Default --title from the first H1 in the source.
    if not args.title:
        try:
            src = args.markdown_file.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            LOG.error("Could not read %s: %s", args.markdown_file, exc)
            return 2
        inferred = extract_h1_title(src)
        if not inferred:
            LOG.error(
                "--title not supplied and no `# H1` heading found in %s. "
                "Either add a top-level heading or pass --title explicitly.",
                args.markdown_file,
            )
            return 2
        LOG.info("--title not supplied; using first H1 as title: %r", inferred)
        args.title = inferred

    # Refuse to publish a file that has uncommitted local edits. This guard
    # runs BEFORE any rendering or network call so the user fails fast.
    if not args.no_git_check:
        try:
            assert_committed_to_local_git(args.markdown_file)
        except (RuntimeError, FileNotFoundError) as exc:
            LOG.error("%s", exc)
            return 2

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
        status_text=args.status,
        status_colour=args.status_colour,
        prettify=not args.no_prettify,
        auto_install_mdformat=not args.no_auto_install,
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
