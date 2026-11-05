---
name: research-radar
description: Scan, rank, and turn new quantitative-finance and agent-engineering research into an actionable research radar. Use for recurring literature monitoring, topic discovery, or research briefings.
---

# Research Radar

## Workflow
1. Confirm scope, time window, and evidence threshold; default to the last 14 days and primary sources.
2. Search broadly, then deduplicate by title, DOI/arXiv ID, and core contribution.
3. For each candidate record source, date, claim, evidence, limitation, and relevance.
4. Rank by novelty, evidence quality, practical impact, and fit (1-5 each). Never rank from title alone.
5. Produce a short radar: **Act now**, **Watch**, **Archive**, with one concrete next step per item.
6. Mark inaccessible or unverified sources explicitly; never invent citations.

## Example
Request: "Weekly radar for market microstructure and LLM agents."

Output item:
- **Watch — Adaptive execution agents** (score 15/20)
- Evidence: arXiv preprint, posted 2026-10-30; simulation only.
- Why: combines online impact estimation with tool-using policy updates.
- Limitation: no live-market evaluation.
- Next step: reproduce the cost model on one month of local order-book data.

## Automation handoff
Use `python -m automations.run research-radar --dry-run` to preview. Review evidence before acting on generated recommendations.
