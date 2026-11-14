# Referee brief WEIGHTS-R1 (from the coordinator, 2026-11-14, Codex-assisted)

**The epic.** `WEIGHTS-20261112-001`, closed in d87ec4742, with docs in d104d08ba. The note is `two_shifts.md`; the
pre-registration is 9d760a7dc.

**Claims.**
- **W1 passes under all three weightings.** Travelling new-kind bases with two certified unlengthened shifts are 39/40 at β = 0,
  35/40 at β = 1 and 38/41 at β = 2, after a completion pass.
- **Travelling is rarer with big knots.** 13.5%, 27% and 34%.
- **The old box at β = 2.** 46/54.
- **W2** has no data at β = 0.
- **W3** is undecided: the enlarged arm was infeasible, and the calibration reached 4 of 23.

**The owner's hand-off.**
1. **The summary.** Rerun `summary.py` and confirm the prefix stopping indices (101, 55, 89) and the counts. Is the prefix rule a
   fair reading of the frozen stop, given that the parallel workers ran samples past it?
2. **The certificates.** Independently certify the four completion certificates, and spot-check about 10 of the main arm's
   two-certified bases.
3. **The deviations.** Does the ±42 window patch change any main-arm result? The enlarged arm was disabled, and bases with one
   certified direction are counted as unresolved.
4. **The wording.** "Big knots travel less", and the shared kinds and seeding.

**Constraint.** A long reach run holds most of the cores, so keep the Codex job modest.
