# Pre-registration: a reading past the wall

Epic `WALL-READ-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `MERGE-BURST-20261119-001#1`. Goal
G17. Framed by A110: these are samples of an unlimited structure, read where possible.

## The question

MERGE-BURST left 14 explosive starts unread: at every stage two maximal blocks shared two points, the case the cluster reading of
DOUBLE-IDENT excludes, and the program's engine ran out of memory by round 5 to 8. Is there a reading past that wall that predicts a
start's next round, or a proof that none of the cluster kind can?

## What the exploration found (disclosed; it shaped this design)

- **The growth is an operator on the live roster.** By REDUCE-BLOCKS' Lemma R, a state is the live points, their open counts and
  the maximal blocks; one round lists the maximal cliques of the candidate graph that no block holds. A compact engine on that
  state (`rosterlib.py`) reproduced start-03's counts 10, 16, 27, 40, 61, 110 and 386 and listed its round-8 groups: 28,064, the
  largest of 109 parents, plus one offshoot (28,065 junctions). The program's engine had stopped there.
- **Start-03's stages.** All its junctions lie over 17 points (round-0 knots and offshoots); one 11-point support carries 126
  distinct round-7 junctions, so junctions are not set by their supports. No two points ever have the same maximal blocks. Its
  stage-8 candidate graph has density 0.85, with 365 blocks, the largest of 17,207 points. In stage 7 (density 0.36) every point
  misses at least 117 others; the advisor question misstated this as "117 to 148".
- **A first look at partnered sets.** A greedy search (4 restarts) found partnered sets of order 14 in start-03's stage 8 (so round
  9 has at least 2^14 − 365 = 16,019 groups) and of order at most 4 in stages 0–7. The largest found with no outside common
  candidate had order 1.
- **Partnered starts** (proof ticket A): the start of order 3 grew 8, 10, 24 in rounds 1–3 by both engines, as Theorem 1 says, and
  its open counts gave round 4 = 4,086. The smoke test of A's machine check also ran n = 4 and the controls.
- **The flag complex of the round-0 candidate graph** is acyclic for 16 of EXPLOSIVE's 21 explosive starts and has one
  two-dimensional hollow for 5; round-0 topology does not single out the kind.

## Prior work in the program

- `DOUBLE-IDENT-20261119-001`: the cluster reading inside the class; `DEAD-CAP-20261119-001`: its branch system.
- `REDUCE-BLOCKS-20261119-001` (Lemma R, refereed in part): the live roster is all the growth reads.
- `MERGE-BURST-20261119-001`: the 16 starts followed here, the two read ones, and the wall.
- `EXPLOSIVE-20261119-001` (refereed): the sample the 16 come from, and the label's meaning (a jump seen before a stop).
- `BREAK-EDDIES-20261119-001` (refereed): the stage identity.

## Prior work outside

- Neumann-Lara (1978): the clique graph of the cocktail-party graph O_n is O_{2^(n−1)}, the first clique-divergent graph. Proof
  ticket A adapts it.
- Deciding clique-divergence of finite graphs is open; it is undecidable for automatic graphs (Cedillo and Pizaña, 2021).
- The injection of an induced subgraph's maximal cliques into the graph's is folklore.

## Design

Two tickets. A is a proof with a machine check (its table M1–M4 is frozen in its `proof.md`). B is this experiment, run with
`experiments/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/job.py` through the shared runner.

- **B1, the engines agree.** The roster engine against the program's engine, per-round multisets of (parents, open count) and
  stall and close verdicts:
  - every touch-census arrangement, rounds 1–6;
  - 1,000 random starts of 6 to 13 knots within seven places (REDUCE-BLOCKS' sampler, seed `wall-read-B-<case>`), rounds 1–6, each
    in a child of 3 GB and 120 s;
  - MERGE-BURST's two read starts, start-00 to round 14 and start-04 to round 7, in a child of 7 GB and 900 s.
- **Following the 16.** Each of MERGE-BURST's 16 starts is grown by the roster engine in a child of 7 GB and 20 minutes. At each
  built stage the job records the counts, the largest group and block, whether one block holds every live point, the best
  partnered sets (greedy, two modes, three seeded restarts), and the sub-count bound of Lemma 2 (the procedure in `job.py`'s
  docstring: seeded random W of 16 to 128 points, maximal cliques counted until a 120 s cap per W or 240 s per stage).

## Predictions (frozen)

| # | Prediction | Held when |
| --- | --- | --- |
| B1 | The roster engine equals the program's engine wherever both finish | no comparison differs (comparisons stopped by a limit counted apart) |
| B2 | Start-03: the open counts of round 7 sum to the parent counts of round 8 (offshoots included); fastlib's separate enumeration lists 28,064 round-8 groups, the largest of 109 parents (values disclosed) | all three equal |
| B3 | Lemma 2 in the wild: at every stage of the 16 whose next round is listed, both bounds are at most the listed groups | no exception |
| B4 | (risky) Start-03, stage 8: the sub-count bound proves at least 10^6 groups in round 9 | bound ≥ 1,000,000 |
| B5 | For at least 10 of the 13 other unread starts (01, 02, 05–15), the better bound at the last stage built exceeds that stage's count: the reading proves the next round larger than any built | ≥ 10 of 13 |
| B6 | No unread start reaches a stage where one block holds every live point (no merge) within the roster engine's reach | none of 14 |

Not predicted, recorded: the order of the largest partnered sets with no outside common candidate (Lemma 3's two-round bound
needs order ≥ 3 and 2^(k−1) above the block count), densities, and where each start stops.

## Stop rule

One run of each job. A failed B1 or B3 is a bug or a counterexample to Lemma 2, reported as such. The epic stops at the result:
partnered starts as an exact reading past the wall, the cluster-reading obstruction, and what the bounds read of the 14.

## Advisor

Fable 5.2 was consulted before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)). It confirmed
the partnered proof and named four gaps (distinct blocks, monotonicity, round 1, the closing clause), all closed. It narrowed the
obstruction to regular covers and a size function s(t), proposed the partnered bound (Lemma 2's special case) ahead of a
retraction lemma or sampling, proposed the words "partnered" and "runaway growth", and tightened the predictions (B2's double count,
fresh n = 4 and 5 values and controls in A). Its reading of the stage-7 density as an inconsistency came from my misstatement.
