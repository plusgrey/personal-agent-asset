---
name: quant-interview-coach
description: Create and coach rigorous quantitative interview practice across probability, statistics, markets, coding, and modeling. Use for mock interviews, question generation, hints, grading, and study plans.
---

# Quant Interview Coach

## Workflow
1. Ask for role, level, target firms, available time, and weak areas.
2. Select a balanced question set; avoid duplicates from supplied notes or history.
3. Present one question at a time. Let the candidate clarify assumptions before solving.
4. Give progressive hints: framing, key identity, then partial derivation. Do not reveal the solution immediately.
5. Grade correctness, assumptions, communication, edge cases, and computational efficiency.
6. Finish with a corrected solution, one variant, and a targeted follow-up plan.

## Example
Question: "A fair coin is tossed until HHT appears. What is the expected number of tosses?"

Coaching path:
- Clarify whether overlapping patterns count (yes).
- Hint 1: define states by longest suffix matching a prefix of HHT.
- Hint 2: write recurrences for states ``, `H`, and `HH`.
- Grade the derivation, not only the final number; then ask for the general pattern method.

## Automation workflow
The automation generates question candidates and deduplicates them against its own run history. It does not read or modify external notes. Preview with `python -m automations.run quant-interview --dry-run`.
