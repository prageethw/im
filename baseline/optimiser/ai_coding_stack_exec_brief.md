# Proposal: High‑Leverage Coding Assistance for the Optimisation Platform

## Table of Contents

- [1. Purpose and recommendation](#1-purpose-and-recommendation)
- [2. Context: why we need more than Copilot](#2-context-why-we-need-more-than-copilot)
- [3. Options and costs (incremental)](#3-options-and-costs-incremental)
  - [3.1 Baseline: GitHub Copilot Enterprise (already funded)](#31-baseline-github-copilot-enterprise-already-funded)
  - [3.2 Option A (preferred): GitHub Copilot + Claude Code](#32-option-a-preferred-github-copilot--claude-code)
  - [3.3 Option B: GitHub Copilot + OpenAI Codex CLI](#33-option-b-github-copilot--openai-codex-cli)
- [4. ROI and value](#4-roi-and-value)
  - [4.0 Agents vs headcount (conservative view)](#40-agents-vs-headcount-conservative-view)
  - [4.1 Where the value comes from](#41-where-the-value-comes-from)
  - [4.2 Quantitative ROI framing](#42-quantitative-roi-framing)
- [5. Comparison: Copilot vs Claude Code vs Codex CLI](#5-comparison-copilot-vs-claude-code-vs-codex-cli)
- [6. Recommendation](#6-recommendation)
- [7. Recommended viewing](#7-recommended-viewing)
- [8. Sources](#8-sources)

## 1. Purpose and recommendation

This paper recommends that the optimisation platform team standardise on **GitHub Copilot Enterprise plus a single repo‑aware coding agent**: **Claude Code (preferred)** or **OpenAI Codex CLI**. GitHub Copilot is already funded and in use; the incremental decision is which higher‑order coding agent to add so that a small team of engineers can deliver a strategic optimisation platform at acceptable speed and quality.

The preferred option is to run a **6‑seat Claude Max 20x burst for the first 6 months**, giving the team very high Claude capacity during platform bootstrapping, and then deliberately scale down to cheaper Claude plans (Team/Standard or a smaller number of Max seats) once architecture and patterns stabilise.

Codex CLI is included as a credible alternative and benchmark, but not as a primary funding request in this phase.

## 2. Context: why we need more than Copilot

The optimisation platform team is a small platform team relative to the scope: multi‑service event‑driven architecture, optimisation modelling, TMF‑aligned APIs, and extensive technical documentation. Existing AI tooling already includes GitHub Copilot Enterprise, which accelerates line‑by‑line coding, but most of our bottlenecks occur at **project level**: understanding large repos, planning cross‑cutting changes, and implementing multi‑file features from detailed specs.

GitHub Copilot Enterprise works best as an **inline IDE assistant**. It is not designed to: read a whole repository, create a change plan, execute edits across many files, and run commands as an autonomous agent. Claude Code and OpenAI Codex CLI are designed for exactly that style of work.

## 3. Options and costs (incremental)

### 3.1 Baseline: GitHub Copilot Enterprise (already funded)

- **Role**: Inline autocompletion, small refactors, and PR support inside VS Code/JetBrains.  
- **Pricing**: Around 39 USD/user/month, billed monthly (organisation/enterprise plans).  
- **Impact**: Improves throughput when engineers already know the change they want and are typing it themselves. It does not remove the need for manual multi‑file planning and execution.

This paper assumes Copilot remains as our default in‑IDE assistant and does **not** seek additional Copilot funding.

### 3.2 Option A (preferred): GitHub Copilot + Claude Code

Claude Code is Anthropic’s repo‑ and shell‑aware coding agent, available on Claude Max and business plans. It can inspect repositories, propose plans, edit files, and run commands, with strong long‑context reasoning.

For the initial build‑out, we propose using **individual Claude Max 20x plans** to give the team very high usage headroom, then stepping down to cheaper plans once architecture and patterns stabilise.

**Seat and pricing model (Max, public 2026 pricing)**

- Max 20x: 200 USD/user/month (monthly billing), approximately 20× Pro‑level usage per session.
- Plans can be started and stopped monthly, so a 6‑month “burst” is straightforward.

**Proposed configuration**

- 6 × Claude **Max 20x individual seats** for the first 6 months (build‑out phase).
- After 6 months, cancel some or all Max 20x seats and move to cheaper business/Team tiers (for example, Team Standard or a smaller number of high‑capacity seats for power users).

**Incremental cost (example, 6 seats, USD)**

- Phase 1 (0–6 months) – 6 × Max 20x: 6 × 200 = **1,200 USD/month** (monthly pricing).
- Over 6 months, Phase 1 Max spend is **≈7,200 USD**.

After month 6, a typical steady‑state configuration might be:

- Either:
  - 1–2 Max 20x seats retained for heavy users (200–400 USD/month), and the rest cancelled.
- Or:
  - All Max 20x seats cancelled, and
  - 5–6 Team Standard seats at ~20 USD/user/month (≈100–120 USD/month total) for ongoing access to Claude and Claude Code at lower capacity.

This keeps the “high‑power” phase explicitly time‑boxed while giving us a clear path to a much lower steady‑state spend.

Over an 18‑month horizon (example):

- Max 20x Phase 1 spend ≈ 6 × 1,200 = **7,200 USD** total for the first 6 months.
- Phase 2 could then move to cheaper Team/Standard seats (for example, 5 × Standard at ~20 USD/month ≈ 100 USD/month), keeping total 18‑month spend in the **low tens‑of‑thousands USD range** depending on how many high‑capacity seats we retain.

This is still materially less than hiring additional senior headcount, while giving us a very aggressive 6‑month window of “20x‑class” Claude capacity to bootstrap the optimisation platform.

### 3.3 Option B: GitHub Copilot + OpenAI Codex CLI

OpenAI’s Codex CLI (their current coding agent) offers a similar repo‑ and shell‑aware experience but built on GPT‑class models and aligned to the OpenAI ecosystem.

- **Role**: Reads your repo, proposes change plans, applies patches, and runs commands, analogous to Claude Code.  
- **Pricing**: Sold as part of OpenAI’s business/enterprise offerings; typical guidance is on the order of ~50–60 USD/user/month for Enterprise‑grade ChatGPT access, with additional cost for higher‑usage coding agents depending on tokens and features.  
- **Licensing**: Often requires broader OpenAI business agreements; less transparent, more variable with usage than Claude Team’s simple seat‑based structure.

For simplicity, we can assume a similar envelope to Claude Max 20x (order‑of‑magnitude 100–150 USD/user/month for a heavy‑usage agent seat), leading to **similar or slightly higher cost** than Option A for equivalent capacity.

**Note**: This paper recommends we prioritise Claude Code because our heaviest work is repo‑ and architecture‑centric, and published comparisons generally find Claude Code ahead on large refactors and explanation quality, while Codex CLI is competitive but more attractive when an organisation is standardising on OpenAI across the board.

## 4. ROI and value

### 4.0 Agents vs headcount (conservative view)

We assume a benchmark fully loaded cost of approximately 100k per year for a senior engineer and a realistic 1,600–1,800 productive hours per year once meetings, context switching, and leave are taken into account. Modern studies on AI coding tools and agentic workflows suggest that, for suitable tasks, developers can see throughput improvements on the order of 20–50%, particularly for boilerplate and well‑scoped changes, but gains are smaller or even negative on complex, ambiguous work.

For this proposal, we therefore treat coding agents as providing a **fractional productivity lift**, not as replacements for human engineers:

- A reasonable planning assumption is that agents add roughly **0.2–0.5 of an additional engineer’s worth of capacity** per human engineer, concentrated in repetitive multi‑file edits, scaffolding, and translation from detailed specs into code.  
- Agents are *available* 24×7, which lets us run long mechanical tasks or test cycles outside of core hours, but human engineers still define the work and review changes; we do not count “24×7” as 3× the output, only as additional flexibility.

Under these assumptions, investing a few thousand USD per year in agent licences (Claude Code, Codex CLI) is justified if it sustainably delivers even a 20% effective uplift on the 100k/year human’s output. The ROI framing in the rest of this section uses that conservative 0.2–0.5 uplift range rather than any aggressive claims about replacing headcount.

### 4.1 Where the value comes from

For a small optimisation platform team, the AI coding stack cannot just save seconds per function; it must remove whole classes of work from human critical path:

- **Multi‑file changes and migrations**: schema updates, shared library introductions, cross‑cutting concerns (logging, tracing, auth) applied across services.  
- **Spec‑to‑code translation**: turning detailed optimisation and TMF‑style specs into working microservice implementations, tests, and documentation.  
- **Understanding and refactoring existing code**: explaining modules, suggesting restructuring, and safely editing with tests.

Claude Code (and, to a lesser extent, Codex CLI) is designed exactly for these tasks: it reads many files, proposes a plan, and executes, while Copilot focuses on inline assistance.

### 4.2 Quantitative ROI framing

Using conservative assumptions:

- Assume a fully‑loaded senior engineer cost of **≈1,000–1,500 AUD per day** (≈650–1,000 USD).  
- If Claude Code reduces multi‑file and migration work by just **0.5 day per week**, that’s ~250–500 USD of labour value per week, or ~1,000–2,000 USD/month.  
- In Phase 1, six Max 20x seats cost ~1,200 USD/month; in Phase 2, a typical Team/Standard configuration could be ~100–400 USD/month depending on how many high‑capacity seats we keep.

Even with modest productivity gains, the **value generated significantly exceeds the licence cost**, especially during the build‑out phase where we are designing, implementing, and documenting the entire optimisation platform.

In addition, avoiding a single month of delay in delivering the platform, or preventing one major rework cycle due to improved design feedback, likely outweighs the full 18‑month licensing cost.

## 5. Comparison: Copilot vs Claude Code vs Codex CLI

| Aspect | GitHub Copilot Enterprise | Claude Code (Claude/Max) | OpenAI Codex CLI |
| --- | --- | --- | --- |
| Primary role | Inline IDE completions, refactors, PR assistance. | Repo‑ and shell‑aware coding agent; multi‑file plans and edits. | Repo‑ and shell‑aware coding agent using GPT‑class models. |
| Typical usage | “Help me write the next function,” “refactor this file,” quick fixes in editor. | “Implement this feature across these services,” “migrate this pattern across the repo,” “run tests and iterate.” | Similar agentic tasks: implement features, patch multiple files, run commands, but with OpenAI tooling. |
| Context window | Mostly current file + some project context in chat. | Long‑context; reads many files and keeps more design context in a session. | Long‑context via GPT; good on complex tasks, though some reviews find Claude better on repo‑scale reasoning. |
| Integration | Deep integration with GitHub repos, PRs, IDEs. | CLI + Anthropic ecosystem; integrates well with terminals and repo workflows. | CLI + OpenAI ecosystem; natural fit if we standardise on OpenAI more broadly. |
| Strengths | Frictionless daily productivity; excellent for experienced devs who already know desired changes. | High leverage on architecture‑driven, multi‑file work and refactors; strong explanations. | Strong coding ability; benefits if we already have large OpenAI enterprise footprint. |
| Weaknesses | Not agentic; limited at reading whole repos and executing plans end‑to‑end. | Requires good review discipline and process; slightly less convenient for tiny edits than Copilot. | Pricing and limits less transparent; comparisons often rate it slightly behind Claude Code on large refactors. |

## 6. Recommendation

Given that GitHub Copilot Enterprise is already in place and working well as an inline coding assistant, the incremental decision should be about **which repo‑aware coding agent to add, not whether to add one**. For a small optimisation platform team with heavy architecture and multi‑service work, Claude Code delivered via Claude Max 20x for an initial 6‑month burst offers the best alignment of capabilities, pricing clarity, and long‑context reasoning.

**Recommended action**

- Approve funding for **6 Claude Max 20x seats for 6 months**, then deliberately scale down to cheaper Claude plans (Team/Standard, or a smaller number of Max seats) based on observed usage and value.  
- Continue using GitHub Copilot Enterprise as the primary inline IDE assistant.  
- Treat OpenAI Codex CLI as a secondary option for future evaluation if the organisation pursues a broader OpenAI enterprise strategy.

This configuration keeps incremental spend modest relative to headcount (≈1,200 USD/month for 6 months, then potentially ≈100–400 USD/month), while materially increasing the team’s ability to deliver a complex optimisation platform with limited headcount.

## 7. Recommended viewing

For a concrete feel of what modern coding agents can do in practice, this short video is a good reference:

- [How AI coding agents actually work in real projects](https://www.youtube.com/watch?v=6eBSHbLKuN0)

## 8. Sources

- Anthropic – Claude Max and Team pricing and plan descriptions  
- Anthropic – Claude Code and business plans overview  
- GitHub – Copilot Enterprise pricing and billing docs  
- OpenAI – ChatGPT / Codex business and enterprise pricing  
- Independent 2026 guides comparing Claude Code, Codex CLI and Copilot for coding agents  
- Industry and academic studies on AI coding tools and agentic workflows (developer productivity and ROI)