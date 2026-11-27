# Referee hand-off: UPPER-GROWN-20261127-001

Design and predictions were frozen in commit b35af0be04 (`README.md`, `frozen.sha256`); results are in `out/`, the reading
in `decision.md`, a replay in `post/`.

| Claim | Class | Where |
| --- | --- | --- |
| The seeded draws reach every simple connected cubic graph with 4 to 12 points (1, 2, 5, 19, 85) | computed, against the known counts | `cubic.py`, `out/cubic_*.jsonl` |
| No closed system with 10 or fewer knots has a box; 49 of the 85 with 12 do (801 boxes) | computed (full search) | `out/cubic_*.jsonl` |
| Every box read misses one upper word with all twelve knots needed (681 read) | computed; one box per graph replayed by enumeration | `post/replay_box.py`, `post/replay_box.json` |
| No box on 2,416 stages of 1,000 held-out census starts through round 2 (2,065 full search, 351 local) | computed | `census_boxes.py`, `out/census_*.jsonl` |
| Growth never changes what earlier distinctions allow, so a box needing a birth reads born distinctions | proved (the earlier referee's argument) | `README.md` |

## Points to press

1. **The box form.** It asks for eight single-triple bonds with a product missing pattern. Is there a step one layer up
   with disjoint carriers that is not a box (other upper readings, other lower relations, missing words of more than one
   triple)? Is "at least eight lower clauses" (the previous referee's lemma) needed for every form?
2. **The local search** on the 351 large grown stages misses bonds with disconnected holders, which the witness's lower
   bonds have. Could boxes be hiding there?
3. **Closedness.** The decision's intuition says a needed knot's private distinctions must be read. Test it, and test
   open systems (one link cut from the 49 graphs).
4. **Multigraphs and four-place knots** were not read.
5. **Earlier work:** search the record for edge colourings of cubic graphs with no monochromatic point and for closed
   not-all-equal systems (`python3 -B scripts/track.py objects`).
