# Referee report ROW-NEST-R1 (light, as asked)

**Verdict: Confirmed with fixes: one Narrowing, one Not a block.**

**The null result reproduces exactly.** My own triangle builder reproduces all 1,024 rules at every depth from 1 to 40, both life and
the first-row relation.

**The class is too narrow to count, on two counts.**
1. **No fresh distinctions.** Window knots alone cannot express a parity, and a parity needs fresh distinctions (NEST-COUNT's P3b).
2. **Dropped end knots.** These leave every row's ends free.

**A slightly larger rule counts.** Take one NAE bit per site, allow fresh distinctions inside the rule, and read the row ends against
one reference distinction. Then the additive rules 60, 90 and 150 give a life that switches on in windows such as depths 11 to 14
and 27 to 30. That is depth read in binary, unexplained by the census's own classifier. Each of the two widenings alone counts
nothing.

**The note's stated reason is wrong.** "No room to carry a signal" fails inside the class itself: three knots make each new site the
complement of the majority of the three above it.

Referee: the background referee thread, 2026-11-12.
- **Code.** `ref_row.py`, my own builder and classifier.
- **Advisor.** The advisor model was not consulted.

## 1. What reproduces

| Item | Census | Referee |
| --- | --- | --- |
| Rules; alive(t) and T_t equal at every depth 1..40 | 1,024 | 1,024 of 1,024 |
| Last change of life: never / at 2 / 3 / 4 | 910 / 81 / 25 / 8 | the same |
| Last change of T_t: never / at 2 / 3 / 4 | 787 / 186 / 43 / 8 (reported as depths 1, 2, 3) | the same |

**The construction matches the pre-registration.**
- **The window.** It is new i − 1 and new i with old i − 1, i, i + 1.
- **Row ends.** A knot touching a missing end position is dropped.
- **The closing row.** It puts knots on consecutive triples of the bottom row.

**One small indexing note.** The census's "last change at depth 1, 2, 3" counts the change between depths t and t + 1 by t. Read
as "T_t differs from T_{t−1}", the last changes fall at depths 2, 3 and 4.

**The classifier is right as frozen.** It tests constant first, then the smallest period p ≤ 10 holding from some depth a ≤ 20 to
depth 40. Within 40 it cannot see a counter whose changes are sparse and stop before depth 20, but none of the rules changes after
depth 4.

**The closing row is a fair analogue of the depth-1 knot.** But in the 512 rules that contain the knot on old i − 1, i, i + 1, every
row already carries consecutive-triple knots, so the depth-t triangle contains the depth-(t − 1) one. Life there can only fall, by
construction. All 512 are monotone, as the advisor anticipated for the unclosed version.

## 2. Is the class too narrow?

**Signals do travel inside the class.** The rule with the three knots (old i − 1, old i, new i), (old i − 1, old i + 1, new i) and
(old i, old i + 1, new i), mask 148, forces every interior new site to be the complement of the majority of the three above it. I
checked this by enumeration. That is a deterministic row map, so "a knot forces a value only when two of its distinctions already
agree" does not stop a signal. What stops counting is what such maps compute. Threshold rules of this kind settle to fixed points or
period two (Goles and Olivos 1980), and mask 148's first-row relation is constant.

**Two widenings, tested separately and together.**

| Variant | Rules | Result to depth 40 |
| --- | --- | --- |
| The class as frozen | 1,024 | nothing counts; last change by depth 4 |
| Ends read against one reference distinction (instead of dropping the knot) | 1,024 | nothing counts; 550 constant, 474 eventually constant; last change by depth 12 |
| A 4-place even parity per site (fresh distinctions), ends dropped | 15 parity rules, with or without a knot | alive at every depth, first row constant |
| A parity per site, ends read against the reference | rules 150, 90, 60 (and 102) | **150, 90 and 60 count**; 102 dies at depth 3 |

**What the counting rules do.**
- **Rule 60** (each new site is the parity of the two above it and the reference) lives at depths 1 to 6, 11 to 14 and 27 to 30, and
  is dead otherwise up to 40. The windows sit just below 16 and 32.
- **Rules 90 and 150** are similar. Their alive strings are in `result_boundary.json`.
- **The classification.** All three are "unexplained within 40" by the census's own classifier.

**Why this is legitimate.**
- **The parity.** A 4-place even parity is complement-closed, so by NEST-COUNT's P3b it is a pattern of NAE knots on fresh
  distinctions. Reading against a reference keeps everything closed under complement.
- **Locality.** The reference can be a per-site copy tied to its neighbours by equality, as in NEST-COUNT's P3c, which keeps the
  rule local.
- **The mechanism is known.** The space-time diagrams of additive rules are Sierpinski-like, so their rows depend on the binary
  digits of the depth (Martin, Odlyzko and Wolfram 1984). Lucas's theorem is the standard proof.

**So the null result is settled by the class's definition.** Window knots without fresh distinctions cannot express the additive
rules that are the known counters. Dropped end knots let each row absorb any signal at its free ends.

## Fixes for the thread

1. **The Answer and the Reading.**
   - Keep "no rule of this class counts within 40", which is exact.
   - Replace "with one bit per site the law has no room to carry a signal down the rows" with what holds. Signals do travel (mask
     148 is a deterministic anti-majority rule), but threshold maps settle (Goles and Olivos).
   - Say that counting appears with one NAE bit per site once the rule may use fresh distinctions, an additive rule read against a
     reference, and the row ends are read against it too. Rules 60, 90 and 150 count in binary windows, the known Sierpinski
     mechanism.
   - Re-aim direction #1, "two distinctions per site", or add this as the cheaper step. The fewest NAE knots, with fresh
     distinctions, that build an additive rule and a closed boundary, and the weight of that description.

   **Narrowing** (the null is by the class's definition, and its stated reason is refuted inside the class).
2. **Monotone by construction.** Note that the 512 rules containing the knot on old i − 1, i, i + 1 cannot count, since each depth
   contains the one before. **Not a block.**

## Files

| Command | Output | What it does |
| --- | --- | --- |
| `ref_row.py census W 6` | `result_census_*.jsonl` | the 1,024 rules rebuilt and compared |
| `ref_row.py parity` | `result_parity.json` | parity rules with dropped ends |
| `ref_row.py boundary` | `result_boundary.json` | additive rules against a reference |
| `ref_row.py kboundary W 6` | `result_kboundary_*.jsonl` | the 1,024 rules with ends against the reference |
| `ref_row.py summary` | `result_summary.json` | the counts |
