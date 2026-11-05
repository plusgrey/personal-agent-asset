---
name: backtest-auditor
description: Audit quantitative backtests for leakage, selection bias, unrealistic execution, weak statistics, and reproducibility gaps. Use before trusting, comparing, or deploying a strategy result.
---

# Backtest Auditor

## Workflow
1. Establish data vintages, universe construction, signal timestamp, order timestamp, and fill model.
2. Trace one observation end to end to detect look-ahead, target leakage, survivorship, and revised-data use.
3. Recompute returns after fees, spread, slippage, borrow, latency, capacity, and failed fills.
4. Inspect train/validation/test separation, tuning count, multiple testing, and regime coverage.
5. Stress assumptions and report sensitivity, drawdown, turnover, exposure, and uncertainty—not Sharpe alone.
6. Verify deterministic inputs, code version, parameters, random seeds, and reproducible outputs.
7. Classify findings as blocker, major, minor, or observation; attach a test and remediation to each.

## Example
Finding: **Blocker — close-price leakage**
- Evidence: signal uses today's official close and fills at the same close.
- Impact: information and execution timestamps coincide unrealistically.
- Test: delay fills to next open and add spread/slippage.
- Remediation: align features to data availability and rerun all held-out metrics.

Use `python -m automations.run backtest-auditor --dry-run` for a checklist; an automated checklist does not replace code/data inspection.
