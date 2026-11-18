# Where not-all-equal bond distance is a distance

Epic `NAE-METRIC-20261118-001`, 18 November 2026, by Claude. The coordinator's go-ahead on `BOND-METRIC-20261118-001`'s direction 2:
under not-all-equal, the owner's case, find a condition on how the knots meet that makes bond distance a true distance, prove it if
possible, and say whether tonight's grown bases (lines, two-order grids) satisfy it. Goals G1 and G16; tests A97 and A39; sub-goal
B200. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `13d727a38` at 10:34 UTC; the census ran from 10:34 to
  10:45 UTC through the shared runner (`NAE-METRIC-B1`, 269 cases, none failed). Two prior-work lines the gate flagged at the freeze
  were added afterwards, labelled.
- Proofs: [proof.md](../../proofs/NAE-METRIC-20261118-001A/NAE-METRIC-20261118-001A-P001_blocks/proof.md).
- Code: [naelib.py, job.py, merge.py, checks.py](../../experiments/NAE-METRIC-20261118-001B/NAE-METRIC-20261118-001B-E001_blocks/).
- Results: [results.json](../../artifacts/NAE-METRIC-20261118-001B/NAE-METRIC-20261118-001B-E001_blocks/results.json).

## The answer

**In the owner's terms.**
- **The question splits along the knots' blocks** (proved). Call a distinction a joint when removing it splits the knots into two
  groups that meet nowhere else. Across a joint, bond distance adds: the distance from one side to the other, minus one, is the
  distance to the joint plus the distance from the joint, each minus one. And two distinctions on one side see only their side. So
  bond distance is a true distance on a not-all-equal base exactly when it is one inside every block, the pieces that no single
  distinction splits. This holds for every base of not-all-equal and betweenness knots, of any arity, and for parity bases too.
- **Which blocks are fine.**
  - A single knot, and a ring of knots each meeting the next once, plain or twisted: bond distance is steps apart plus one on every
    pair (proved). So **every base whose knots form a tree of single knots and rings is a true distance, with bond distance one more
    than the steps apart** (proved). Knot trees are the special case of FREE-READ.
  - Knots meeting at most once, each distinction in at most two knots, and the knots' pattern of meetings with no K4 inside it (the
    literature's series-parallel graphs): no failure among 354 such bases, plain or twisted (computed; a conjecture). With a K4 inside,
    3 of 6 fail; the eight-distinction failure of `BOND-METRIC-20261118-001` is a K4 with one meeting stretched.
  - The woven tori checked in `BOND-METRIC-20261118-001`, and the endless weave (`RULER-20261111-001`).
- **Which blocks fail.** On at most seven distinctions and six knots, every failing pure not-all-equal block has two knots that meet
  twice (325,395 of 1,327,830 blocks at seven and six; none of the failures has knots meeting at most once). A double meeting is not
  always fatal (the weave is full of them), but a lone one is. With betweenness knots mixed in, the twisted four-knot meeting pattern
  on six distinctions also fails with every pair of knots meeting once.
- **Tonight's grown bases.** At 7,140 steps of 244 growth runs (eight PICK-TWO rules from lines of five to eight and the 2 × 2 grid,
  and KF3, NN, NN2 and SEEDK from bracketings), every pair lies in a knot of three except one pair at one step: bond distance is at most
  two there, and the exception is still a true distance (post hoc). So the grown lines and grids satisfy it, but trivially: bond
  distance gives them no spacing (diameter two), as FREE-READ found on split grids. Their spacing lives in the disagreement count.

| Block | True distance? | Evidence |
| --- | --- | --- |
| Single knot | yes (b = 2) | proved |
| Ring of knots meeting once, plain or twisted | yes, b = steps apart + 1 | proved; computed to 9 knots |
| Tree of knots and rings | yes, b − 1 = steps apart | proved; 200 random cacti |
| Meeting once, each distinction in two knots, no K4 | yes in all 354 checked | computed (conjecture) |
| Two knots meeting twice, alone | no | proved (BOND-METRIC T2) |
| Small blocks with a double meeting | often not (325,395 of 1,327,830 at 7 and 6) | computed |
| Twisted four-knot pattern on six (betweenness mixed in) | no | computed |
| Woven tori 3 × 3 to 4 × 5; the endless weave | yes | computed; proved (RULER) |
| Grown split bases (lines, grids, steps between) | yes, diameter at most 2 (one pair at 3) | computed |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 7 gates | held | all pass |
| P1 | b − 1 adds across every separating distinction (1,000 glued bases) | held | 16,719 separated triples, none fails (parity 3,802, not-all-equal 7,439, four-place 5,478) |
| P1b | (advisor) the bond count at a separating distinction | held | exact on 858 bases |
| P2 | the block formula; metric exactly when every block is; no violation spans two blocks | held | no mismatch on 1,000 glued and 1,000 sparse bases |
| P3 | rings of 3 to 9, plain and twisted: b = steps + 1, m(m − 1) runs, other bonds ≥ m + 1, largest b = ⌊m/2⌋ + 2 | held | all 14 |
| P4 | 200 cacti: b − 1 = steps apart | held | no pair differs |
| P5 | failing pure not-all-equal blocks to 7 distinctions and 6 knots have a double meeting | held | 420,202 failing blocks of 1,589,656, all with one |
| P6 | (conjecture) graph-like, series-parallel: metric | held | 0 of 354 fail |
| P7 | grown bases: b ≤ 2 at every step | **failed** | one pair at b = 3 at one step (a three-order state reached from a line of seven by NEWCROSS and by CAP(3) with the same seed); the triangle inequality still holds there (post hoc); the triple criterion matched brute force at all 1,728 steps checked |

7 of 8 held; P7 failed narrowly.

## What it means for A97, A39 and B200

For not-all-equal, the owner's case, the program's distance is a true distance wherever the knots meet in a tree-like way: trees of
knots and rings (proved), and in every series-parallel pattern of single meetings checked. What breaks it is a block where two knots
meet twice in isolation, or a dense small cluster (a K4 among the meetings). A39 (space is spaced by knots that compose) gains the
block form: a base is spaced by bond distance as soon as each of its blocks is, and joints add. For A97 this gives a law-specific
domain where distance reads the base, and a precise boundary.

## Known results, and what this adds

Known, cited once: the bond structure at a separating distinction is, for parity bases, the parallel connection of matroids
(Brylawski 1971; Oxley, ch. 7); the join over it is the lossless join of an acyclic scheme (Beeri, Fagin, Maier and Yannakakis 1983);
block-cut trees and series-parallel graphs (no K4 minor) are classical. What this adds: the same bond structure for every
complement-closed base (not-all-equal and betweenness of any arity), hence additivity of bond distance across joints and the block
reduction of the triangle inequality; rings and cacti proved; the census of small blocks; the series-parallel conjecture. The advisor
knew no published statement of the non-matroid additivity; no literature search was run.

## Limitations

- The series-parallel condition is a conjecture, computed on 354 bases of at most 14 distinctions; the census of blocks stops at seven
  distinctions and six knots.
- Weaves (two-fold surfaces) are covered only by earlier results (the endless weave proved, small tori computed).
- P7's exception was examined post hoc at its one step only.

## Reproduce

```sh
d=experiments/NAE-METRIC-20261118-001B/NAE-METRIC-20261118-001B-E001_blocks
.venv/bin/python -B $d/checks.py
.venv/bin/python -B scripts/longrun.py launch $d/job.py --out runs/nae-metric --workers 8 --case-mem 1500M
.venv/bin/python -B $d/merge.py runs/nae-metric
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage`
names claude-fable-5-2), asked before the freeze. It checked Lemmas 1 and 2 and the gluing, gave the exact bond structure at a joint
and the weaker hypothesis covering parity, corrected blocks to the primal graph, gave the ring lower bound for every pair, and
suggested P1b, P3's counts and P2's "no violation spans two blocks". Its H1 (every graph-like block metric) was already false; P6 is the
thread's variant of its H2 and was not put to it.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: where not-all-equal bond distance is a distance | **Status:** Successful (referee pending) | Proved: joints add and the question is block by block; rings and cacti are true distances. Computed: small failures need a double meeting; series-parallel single meetings pass; grown bases pass trivially. 7 of 8 held |
| Local direction: one distance for both laws (B200) | Promising | Under not-all-equal bond distance is a true distance on tree-like meeting patterns, proved for cacti |
| Broader exploration: decompositions of bases | Known alternatives | Parallel connection and acyclic joins are classical; the complement-closed version is the program's |
| Long-term goal: G1 and G16 | G1 capability gained; G16 capability gained | G1: a proved class of not-all-equal bases where the program's distance is a true distance. G16: blocks and joints as the structure that decides it |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the series-parallel conjecture: decompose at two-distinction separations (the advisor's H2), so b is a minimum over two routes as on a ring | 2/3 | 2/3 | state and check the two-joint formula on rings with one knot replaced by a small block → stop at a proof or a counterexample | Alternative |
| 2 | Double meetings: which blocks with knots meeting twice are true distances (weave rhombi are, lone pairs are not)? | 2/3 | 2/3 | classify the 7-distinction failing blocks by how their double meetings are covered by other knots → stop at a rule that predicts every failure | Alternative |
| 3 | Weaves as blocks: is every two-fold weave of not-all-equal knots a true distance, beyond the cutoff RULER-FLAT found? | 2/3 | 1/3 | tori 5 × 5 to 6 × 6 with a bounded bond search → stop at a failing torus or a proof route | Alternative |

**Corrections:** none for this study.

**Goals:** G1 checkpoint (capability gained: under not-all-equal bond distance is a true distance exactly when it is one in every
block; trees of knots and rings proved) and G16 checkpoint (capability gained: joints and blocks as the structure that decides it); no
goal changed.

**Assumptions:** A39 gains the block form; A97 gains this study; no status changed, no new entry.
