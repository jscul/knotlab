# Where the top binds every depth directly, and whether it is truly bounded

Epic `DIRECT-REACH-20261115-001` (`LEVEL-REACH-20261114-001#2` with `ADDR-KNOTS-20261113-001#2`, at the coordinator's go-ahead,
2026-11-15 00:29 UTC; G17, with G1), 2026-11-15 to 16. Proof note:
[proof.md](../../proofs/DIRECT-REACH-20261115-001B/DIRECT-REACH-20261115-001B-P001_every_depth/proof.md). Computations:
`experiments/DIRECT-REACH-20261115-001A/` (built by Codex on 2026-11-15 and gated; populations run by the thread). The canonical K1–K3
test is unchanged. **Referee pending.**

## The question

`LEVEL-REACH-20261114-001` read, at depth 9, the least bond from level 3 to level 3 + s for s = 1..4 in addressed patterns. In 5 to 11%
of the alive weight it was **direct**: constant over the four levels, two or three members. The referee narrowed this to "constant
over four levels, not proved bounded", since the least bond is not monotone in depth. Is direct reach truly bounded at every depth and
every s, where does it occur, and what do the direct patterns share? Population D: the 146 descriptions with a constant profile, 2
(34) or 3 (66), or the half-rate profile [3, 3, 4, 4] (46). Population U: 88 bounded-activity descriptions with an undecided cell.

## Answer

**Direct reach is truly bounded at every depth for 54 of the 100 constant descriptions, proved; for the rest it is read to depth 9
only, and two leave their constant at s = 5.** Two new every-depth arguments do it.

1. **Blocks of orbits (Theorem W, proved).** The maps' orbits split each level, and every knot placed at an orbit lies in its
   **block**, the orbit with its children. Blocks meet only parent to child, so the pattern is solved exactly block by block, and when
   the orbits stay small there are finitely many kinds of block: life, ties and three-member bonds inside two orbits are then decided
   at every depth and every s by a finite computation. 85 of the 146 have orbits of at most four addresses. All 10 constant-2 ones
   have L = 2 and all 32 constant-3 ones have L = 3 exactly, at every depth N ≥ 3 + s and every s ≥ 1. This was the earlier session's
   lead: in the simplest case the tie lives in a block of six addresses (an orbit of two with its four children).
2. **A block's descent (Theorem D, proved).** When the orbits grow (whole levels up to level 8 in the other 61), a few addresses followed
   down one letter each, the letters eventually periodic, still form a sub-pattern whose blocks meet in a row, and its state is
   eventually periodic. With a finite-reader state for life (a finite machine reading the address gives the value; 139 of 146 have
   one), a tie carried by the descent gives L = 2 at every depth, and a carried three-member set with its one-sided pair shown free
   gives L ≤ 3. This adds 5 constant-2 and 7 constant-3 descriptions with growing orbits.

| Profile (s = 1..4 at depth 9) | Descriptions | Bounded at every depth and every s, from level 3 | How |
| --- | ---: | --- | --- |
| constant 2 | 34 | 15: L = 2 | W 10, D 5 (growing orbits) |
| constant 3 | 66 | 39: L ≤ 3, of which 32 L = 3 exactly | W 32, D 7 (growing orbits) |
| [3, 3, 4, 4] | 46 | none bounded; 43 have no tie at any depth (L ≥ 3) | W |

**Read deeper, at depth 9 (certified).** Reading two levels further (top level 2, s = 5 and 6) separates direct from half-rate where
the top-2 control agrees with the census (31 of 34, 60 of 66, 42 of 46): 30 of 31 constant-2 stay at 2, 58 of 60 constant-3 stay at 3,
and all 42 half-rate ones exceed 4 by s = 5. From top level 3 at s = 5, two constant descriptions leave their constant: d50c90fa37ed…
(2 → 3, the one constant-2 without a tie class through levels 3 to 8) and 5b906d33a1e9… (3 → more than 3, bounded activity, growing
orbits). So "constant over four levels" is not "constant": 2 of 100 change at the fifth.

**What the direct ones share.** Not small orbits: 43 of the 46 half-rate descriptions have orbits of at most four addresses, against
42 of the 100 direct ones. Among small orbits the difference is how far a fixed relation survives between two orbits: for the direct
ones a tie, or a three-member bond inside two orbits, holds at every distance s; for the half-rate ones a three-member bond inside two
orbits exists only at s = 1, and longer bonds must take in more orbits. Activity sorts them partly: the half-rate profile is
exponential activity with small orbits (43 of 46), while all 12 finitary descriptions and 31 of the 32 bounded-activity ones in D are
direct. The descents found hold two addresses in 38 of 41: the all-0 and all-1 addresses (19), or two addresses that differ only in
their first letter, given the same letters (15). Level-shifting maps of the whole pattern, which the advisor expected to be the common cause, exist for 11 constant-3 descriptions and
for none of the others.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Theorem W: blocks of orbits meet only parent to child; with finitely many kinds, ties, two-orbit three-member bonds and life are decided at every depth | proved |
| 2 | Corollary W: 10 constant-2 (L = 2) and 32 constant-3 (L = 3) descriptions at every depth and every s; 43 half-rate with no tie at any depth | computed by a finite check; agrees with SAT on 1,020 joint relations at depths 6 and 10 and on life at depths 2 to 12, and with the certified depth-9 results on 935 cells |
| 3 | Theorem D: a descent carrying a tie, or a three-member set with its one-sided pair free, bounds the reach at every depth | proved |
| 4 | Corollary D: 13 constant-2 (5 with growing orbits) with L = 2, 28 constant-3 (7 with growing orbits) with L ≤ 3, at every depth | computed; all 41 descents' blocks equal the explicit ones, 521 of 521 claims hold at depth 9, the finite-reader states hold at depth 12 |
| 5 | Life at every depth for 139 of 146 by finite-reader states (85 also by W) | computed (a product-automaton check) |
| 6 | Deeper at depth 9: direct and half-rate separate (58 of 60 at 3, 42 of 42 above 4 by s = 5); 2 of 100 constant ones change at s = 5 | computed, certified (SAT with checked refutations) |
| 7 | What the direct ones share: a relation between two orbits kept at every distance; not small orbits; activity sorts partly | computed, exploratory |
| 8 | Undecided bounded descriptions: not cheaply decidable (1 of 6 decided in the pilot, 3 of 13 cells, all at L = 4); the other 82 not run | computed, certified |

## Undecided bounded descriptions (population U)

**Not cheaply decidable; the remaining 82 were not run.** The pilot (`readout_U_pilot.json`; LONG_RUNNING `DIRECT-REACH-A2`, 5
descriptions run by the thread on 2026-11-16 from 19:21 to 20:21 UTC, the sixth from the Codex smoke) gave the first 6 descriptions of
U by case id 900 s for each census-undecided cell, after their tie classes (none had a tie). One of the 6 had every undecided cell
decided (needed: 2), and 3 of the 13 cells were decided, each at L = 4 within 59 s; every cell at s ≥ 3 that the census left open
stayed open, except one at s = 4. All 88 have orbits that grow, so Theorem W does not reach them, and the decided cells (L = 4) are
above what a descent of Theorem D can show. The three decided cells took at most 59 s, in a leaner search than the census's (no
per-target searches sharing its deadline), so the extra time decided nothing beyond the first minute, as the advisor expected from the
census's solve times.

## Predictions

Frozen in [predictions.md](predictions.md) (written after the population D run had finished but before its read-out; 5 rows had been
seen).

- **P1 holds.** 33 of the 34 constant-2 descriptions have one tie class meeting every level 3 to 8 at depth 9 (needed: 17).
- **P2 holds.** Where the top-2 control agrees (60 of 66 constant-3, 42 of 46 half-rate), 58 of 60 constant-3 stay at L ≤ 3 at s = 5
  and 6 (97%, needed 70%), and all 42 half-rate ones have L ≥ 5 at s = 6 (and already at s = 5).
- **P3 fails.** 1 of the 6 pilot descriptions had every undecided cell decided at 900 s (needed: 2), so U is recorded as not
  cheaply decidable and the other 82 were not run.

## Lessons

- A finite family of finite-reader states cannot show that no deeper address is tied to a top address when their joint values at that
  address recur deeper, and in the cases tried they always did. Lower bounds at every depth came only from the exact block
  computation; with growing orbits the program has upper bounds only.
- Ties persist with depth only while the pattern lives, so every every-depth claim needs life at every depth, here from a
  finite-reader state or the blocks.
- The top level matters: from level 2, 3 of 34 constant-2 and 6 of 66 constant-3 descriptions read differently over the same four s.

## Advisor

Used three times: the design and predictions (2026-11-14, `advisor_design_answer.md`); the soundness of the three every-depth
arguments before they were implemented (2026-11-16, `advisor/proof_answer.md`: sound, with four bookkeeping points, all met by the code
or the statements; it missed that finite-reader states cannot separate, found by the computation); and the new words (block, descent,
finite-reader state; `advisor/words_answer.md`), which replaced "window", "chain of windows" and "automatic state".

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — direct reach at every depth | **Status:** Successful | Bounded at every depth for 54 of 100, proved; 2 of 100 change at s = 5 |
| Local direction — blocks of orbits and descents | Continue | Blocks cover 399 of the census's 457 rulers too |
| Broader exploration — G17 nested line | Known alternatives | Joins the ruler theorem and the census; rigid growing patterns open |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Every-depth verdicts replace depth-9 readings for small orbits |

The attempt leaves open the 19 constant-2 and 27 constant-3 descriptions with growing orbits that no descent of at most four addresses
carries, exact lower bounds wherever orbits grow, and the growth of the half-rate profile beyond depth 9. The bridge to G1 is the
ruler: a reach that grows by one per level is the program's bond distance, and blocks may now prove it at every depth for cyclic
patterns, which the hypertree theorem could not.

**Corrections:** none. **Goals:** a G17 checkpoint (with G1), capability gained. **Assumptions:** A83 added (the top binds every
depth when a bond of fixed size reaches every level of every finite pattern); A82 and A76 used.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Exact reach at every depth from blocks | 2/3 — Substantial | 2/3 — Testable | Compute least bonds of any size across blocks for the 43 small-orbit half-rate descriptions and check against depth 9 → a finite procedure that proves their rate at every depth, or bonds that spread over unboundedly many orbits | Selected · awaiting go-ahead |
| 2 | Ties in nearly rigid patterns with growing orbits | 1/3 — Incremental | 2/3 — Testable | Test forcing of each level by a bounded number of levels below it, as a finite-reader check, on the 19 open constant-2 descriptions → a forcing depth that holds at every level, or the cases where it grows | Alternative · deferred |
| 3 | Lower bounds when orbits grow | 2/3 — Substantial | 1/3 — Stated | Look for infinite families of states (finite-reader states moved by the maps, or sets whose flip keeps every knot) that make each top address free with every deeper one → one family for one constant-3 description, or an obstruction | Alternative · deferred |
| 4 | Undecided bounded descriptions by a lower-bound certificate | 1/3 — Incremental | 1/3 — Stated | Certify L ≥ 4 or 5 at s = 3, 4 by a bounded-size refutation family on the 6 pilot descriptions → one certified lower bound, or none within an hour | Alternative · deferred |

1. Payoff 2: blocks would turn the census's rulers (399 of 457 have orbits of at most four addresses, including most of the 158 with
   cycles, `B180`) and its half-rate profiles into every-depth results, settling whether cycles change the rate. Concreteness 2: the
   block computation already decides ties and three-member bonds exactly and is checked against SAT; the open step is a finite
   description of bonds of growing size across blocks, the main uncertainty. Resource bound: one study, with any run over ten minutes
   registered.
2. Payoff 1: would complete the constant-2 class, and connect to the rigidity obstruction of `RIGID-LEVEL-20261114-001`.
   Concreteness 2: the forcing data at depth 9 is in hand, but forcing came from below or within the level in every case tried.
3. Payoff 2: exact "direct" verdicts where orbits grow, and a general tool for lower bounds at every depth. Concreteness 1: finite
   families provably fail when their values recur, and no infinite family is in sight.
4. Payoff 1: would settle part of `LEVEL-REACH-20261114-001`'s bounded-activity question (29 of 45 decided were direct; the rest
   undecided). Concreteness 1: the pilot shows that more search time does not decide them, and no lower-bound method for growing orbits
   is known (the lesson above).

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead.

## Hand-off to the referee

Folder: this one (note, predictions, advisor answers, read-out, `chain_ties.py`, `chain_bounded3.py`, `gate_chain.py`,
`crosscheck_window_tree.py`, `exploratory/`); the proof family `proofs/DIRECT-REACH-20261115-001B/` (`proof.md`, `check.py`,
`result.json`); the Codex-built computations `experiments/DIRECT-REACH-20261115-001A/…/codex/` (`REPORT.md`, gates, certified case
results; their slim records and every cited refutation's hashes in `artifacts/DIRECT-REACH-20261115-001A/`, the 30 GB of
certificates themselves kept on disk only, repacked on 2026-11-16 at John's choice into 135 zstd archives (8.99 GB, every member
checked against its hash; index and extraction in `codex/certificate_archives/INDEX.md`, for example
`zstd -dc --long=27 codex/certificate_archives/<case>.tar.zst | tar -x -C out`); 5 certifications timed out at their query deadlines and are kept as incomplete attempts, leaving those cells undecided, none behind a reported
verdict) and the thread's U pilot `…/thread/`. Proved: Theorems W and D and Lemma 0. Computed: Corollaries W and D, life, the depth-9
read-out. Least sure: (a) the block computation's every-depth bookkeeping (feasible sets by remaining depth, the r < r₀ cases) in
`exploratory/window_tree.py`, checked against SAT only at depths up to 12; (b) the composite words m_j · m_i⁻¹ and the inverse automaton
in `chain_ties.py`, checked against explicit addresses only to level 8; (c) the finite-reader check `exploratory/automatic_life.py`
(a product-automaton safety check), checked only against depth 12.
