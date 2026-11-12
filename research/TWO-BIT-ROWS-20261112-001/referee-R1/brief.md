# Referee brief TWO-BIT-ROWS-R1 (from the coordinator, 2026-11-12, lean)

**The epic.** `TWO-BIT-ROWS-20261112-001`, closed referee pending: pre-registration 902871068, epic 32bd76956, goals and notebook
feb22ae4a.

**Files.** The code is `experiments/TWO-BIT-ROWS-20261112-001A/.../census.py`. The data is `artifacts/.../{all,sample}_{flat,hop}_*.jsonl`
and `summary.json`.

**Claims.**
- **P1 held: harmonies exist.**
  - **Hop** (old i, old ⌊i/2⌋, new i − 1 and new i, two distinctions each): 2 knots suffice, in 2 of the 1,596 exhaustive rules with
    one or two knots.
  - **Flat**: 10 knots, in 2 of 4,000 drawn rules (none of the 7,260 rules with one or two knots).
  - **Weight shares:** 0.12% for hop and 0.011% for flat.
- **P2 failed as frozen.** Five hop rules are unexplained within 40. Inspected after the run, they show late changes followed by
  constant or period 2.

**Points to check.**
- The halving reach, including collisions at small i.
- The closing generation, and the inspection after the run.
- Whether the 2-knot hop harmony is forced by the halving reach itself.
- Whether the flat against hop comparison is fair.

**Report.** Send the verdict.
