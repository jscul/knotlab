# Referee report LATE-HOP-R1 (cheap, as asked)

**Verdict: Confirmed, with two wording fixes (both Not a block).**
- **The records reproduce.**
  - My own builder (TWO-BIT-ROWS-R1's `ref_two.py`) reproduces three more rules exactly: rule 28 to depth 80, and one hop and one
    flat harmony to depth 120.
  - My earlier depth-80 reading of 12 of the selected rules agrees with the records over the same depths. That covers the five late
    rules and seven harmonies.
- **The L2 failure is reported honestly.** It is failed as frozen, and the reason (period-2 harmonies change at every depth) is
  given.
- **Two descriptions need a small fix.**
  - Rule 28's "settling at 47" is a death at 47. Its first-generation relation changes at 41, 42, 44 and 45 before that, so the
    claim that the only changes after 40 are two is too few.
  - Rule 9 alternates at depths 35 to 40, not 35 to 37.

Referee: the background referee thread, 2026-11-12. `ref_late.py` is mine. The advisor model was not consulted.

| Rule | Depths | Referee against the records |
| --- | --- | --- |
| 28 (hop, late, 5 knots) | 1..80 | equal. The first-generation relation changes in pairs every three depths from 17 (17, 18, 20, 21, …, 41, 42, 44, 45), then the rule dies at 47 and stays dead |
| 0 (hop harmony) | 1..120 | equal; period 2 throughout |
| 29 (flat harmony) | 1..120 | equal; period 2 throughout |
| 3, 9, 24, 25, 26 (the five) and 0, 1, 6, 13, 16, 21, 23 | 1..80 | every change agrees with my TWO-BIT-ROWS-R1 reading |

**What the late changes look like.** Rule 28's relation changes in pairs every three depths for about thirty depths, close to a
period-3 harmony, and stops with a death at 47. So, apart from the period-2 alternations, the changes after depth 40 are:
- rule 9's death at 41, after alternating at 35 to 40;
- rule 28's changes at 41, 42, 44 and 45 and its death at 47.

None sits near a power-of-two length (2 + t = 32 or 64), so the frozen L2 would fail even without the harmonies.

## Fixes for the thread

1. **Conclusion 3.** Write: "apart from the alternations, the changes after 40 are rule 9's death at 41 and rule 28's
   first-generation changes at 41, 42, 44 and 45 and its death at 47". Rule 28 runs a period-3 pattern of changes from depth 17
   until it dies at 47. **Not a block.**
2. **Conclusion 1.** Rule 9's first-generation relation alternates at depths 35 to 40, not 35 to 37. **Not a block.**

## Files

`ref_late.py` → `result_late.json`.
