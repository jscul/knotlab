# Referee brief TOP-INFO-R1 (from the coordinator, 2026-11-14, Codex-assisted)

**The epic.** `TOP-INFO-20261114-001`, commit a79e774be, closed preliminary. Its brute-force gate (TOP-INFO-brute30) is still
running; do not wait for it.

**Claims.**
- **The rule fails.** "Bounded exactly when a carried value is read outside R's exception, linear otherwise" is false both ways.
- **Theorem P′ (bond-pinning)**, proved.
- **The two-block window bound**, proved.
- **Localisation**, proved: every bounded case has a bond local to the top and the target. Decidability is open.
- **The census split.** Of the 5,074 bounded: 4,484 R, 523 bond-pinned, 65 "middle members". Plain pinning equals bond-pinning in
  the census.
- **The predictions.** T1 held; T2 failed (15 of 93); T3 failed (9 of 83, plus 2 by R, leaving 72).

**The coordinator's points.**
- Attack P′ and localisation hardest.
- Check 4,484 + 523 + 65 = 5,072 against CARRY-BOUND's 5,072 / 5,074 / 5,076, and whether the two R-bounded families change
  CARRY-BOUND's totals.
- Give "local" an exact meaning.
- Check that the two-block window is exact.
