# Referee hand-off: BUILT-BINDING-20261126-001

The study note is [README.md](README.md) (frozen section committed at `233d6f3087` before the frozen runs); the
decision is [decision.md](decision.md); the scores are [score.json](score.json), written by [score.py](score.py).

| # | Claim | Evidence class | Code | Data |
| --- | --- | --- | --- | --- |
| 1 | (a) On the 32 built ring families (R = 3, 4 rings of n = 4 to 7 knots, two attachments, two links), after ordinary parity growth the per-ring new carriers obey one parity rule at every round read, each a class fact read by no single knot under both readings of a small change | computed, frozen (P1) | `families.py built`, `repro.py` (`rings_start`, `run_rings`, `analyse`) | `frozen_built.jsonl` |
| 2 | (a) The referee's 30-knot and two 21-knot preparations, and its sampled ten-knot path witness (under the shortest changes only; two of its three carriers are not class facts under changes of at most five distinctions), reproduce with the canonical engine | computed, before the freeze | `repro.py`, `repro_paths.py` | `repro_explore.jsonl`, `repro_paths.json` |
| 3 | (b) Every carrier of every binding read has a start representative, the representatives obey the same relation on the start's allowed states, and its sum is a sum of start laws | computed (P1c; before the freeze on claim 2's witnesses) | `repro.analyse` (`old_representative`) | as above |
| 4 | (c) Before growth the representatives are read by no single knot on every row; under the shortest changes they are class facts on the double-link families and not on the detour families; under changes of at most five distinctions on none; after growth every new carrier is a class fact under both readings | computed, frozen (read in P1) | `repro.analyse` (`facts` at the start and on the stage) | `frozen_built.jsonl`, `score.json` |
| 5 | The argument: premises 1 to 3 hold on every birth record, and the pairs and loops of four span the changes that keep the start's values, on every stage read (census, 900 held-out, 32 built, 400 sampled starts of 9 to 12 knots; rounds 1 to 6) | computed, frozen (P2); proof sketch by the advisor, unverified | `premises.py`, `origin_scan.py` | `frozen_premises_*.jsonl`, `origin_*.jsonl` |
| 6 | The origin test can say no: a birth's first fresh distinction, its other fresh distinctions and its inputs obey one rule, and the first is not a function of the start's values | computed, frozen (P2) | `families.py built` | `frozen_built.jsonl` (part "origin control") |
| 7 | Controls: one loose distinction at a detour's middle knot dissolves the relation at every round; links made loose, or a loose distinction at a connecting knot of a double link, dissolve it or stall | computed, frozen (P3) | `families.py controls` | `frozen_controls.jsonl` |
| 8 | (d) Under both cuts, on the R = 3 detour families with the middle knots joined, one birth of the three middle knots gets no fresh distinction at round 1 and makes the relation (8 tuples at the start, 4 after); ordinary growth leaves it free; the cut runs stall at round 2 [R1: all one-fewer and six of eight arity-floor runs; two stall at round 4] | computed, frozen (P4) | `families.py cuts`, `repro_cuts.py` | `frozen_cuts.jsonl`, `repro_cuts.jsonl` |
| 9 | Under not-all-equal the same carriers take every tuple (read only, no claim) | computed (P5) | `families.py nae` | `frozen_nae.jsonl` |
| 10 | The advisor's 14-knot start binds three ring facts from round 0 by its own laws; the canonical checker passes the relation for every choice of contact | computed, before the freeze | `built.py`, `checker.py` | `built_explore.jsonl`, `checker.json` |
| 11 | Closing: a parity birth's law is implied exactly when its inputs are every loose distinction of its connected structure (the proved law of `ERASURE-AND-CLOSING-SIGNS-20261121-001B`), on every census and held-out birth; under not-all-equal never | computed, before the freeze | `closing.py` | `closing_*.jsonl` |

**Points to press.**
- Claim 4, the heart of (c): the "before" status depends on the reading and on the representative; check both, and
  whether "held only by whole carriers" says anything the lineage rule does not build in.
- Claim 5: the proof sketch in README ("The argument") and `advisor/answer.md` section 2; the premises under capped
  group rules and the cuts (premise 3 fails under both cuts on 136 to 192 census rounds, while the span still holds).
- Claim 1: rounds not read at the 500-distinction cap are not negatives.
- Scaffolds: the built families, the lineage carriers and the origin test (register entry for this study).
