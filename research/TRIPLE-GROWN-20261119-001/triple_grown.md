# Do three-way readings separate the reached and static meet-once collisions?

Epic `TRIPLE-GROWN-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `GROW-SMALL-20261119-001#1`.
Assumption A97; goal G1. **Referee pending.**

**Record.** Pre-registration, frozen before the run (commit `03c06ceb9`): [preregistration.md](preregistration.md). Code:
[triples.py](../../experiments/TRIPLE-GROWN-20261119-001A/TRIPLE-GROWN-20261119-001A-E001_triples/triples.py). Result:
[triples.json](../../artifacts/TRIPLE-GROWN-20261119-001A/TRIPLE-GROWN-20261119-001A-E001_triples/triples.json).

## The answer

**In the owner's terms.**
- **Yes, every one.** Add the three-way readings (the smallest bond holding three given distinctions, less one) to the pair
  distances, and every meet-once collision with other states found so far comes apart:
  - all 1,034 static pairs of 6 and 7 junctions;
  - all 87 reached pairs, the created one included.
  So the picture of THREE-WAY holds on the new collisions: pair distances miss some allowed states, pair plus three-way readings
  miss none found, and the states themselves miss which junction holds what.
- **Not automatic.** If the junctions were all three-place, the three-way readings would find them directly. Here they are not:
  the three-distinction bonds never span the equations (ranks 2 to 6 against 6 to 9). So the separation is a finding, not a
  restatement.
- **Mostly by counting.** In 1,000 of the 1,034 static pairs and 73 of the 87 reached ones, simply counting how many triples have
  each reading already tells the two apart. The rest need the full matching.

| Pairs with one table and other states | Pairs | Separated by three-way readings | … by counts of readings alone | Exact readings |
| --- | ---: | ---: | ---: | ---: |
| Static (PARENT-RULE, 6 and 7 junctions) | 1,034 | **1,034** | 1,000 | 1,034 |
| Reached (GROW-SMALL, 9 to 17 junctions) | 87 | **87** (the created pair included) | 73 | 64 (23 read to 8; separation there is exact) |

| # | Prediction | Verdict |
| --- | --- | --- |
| T1 | All 1,034 static pairs separated | **held** |
| T2 | All 87 reached pairs separated, none undecided | **held** |

## How it was done

- **Readings from bonds.** When both members of a pair have at most 15 vertices, every bond was enumerated (PARENT-RULE's `plib`).
  Otherwise every bond of at most 9 distinctions was enumerated, with exact_table_v2's search returning the bonds, and readings
  above 8 were pooled with "none". The pooled pair readings equal exact_table_v2's on a checked case.
- **The test.** THREE-WAY's test was used: the pair table as a coloured complete graph, with every read triple attached as a
  labelled vertex, and VF2 on the two graphs.

## Known results, and what this adds

Known:
- THREE-WAY's separation of 11 static rivals and 152 reached groups (knots sharing two);
- its referee's 22 further groups at 15 and 16 junctions;
- weight counts as a states invariant (GROW-SMALL).

What this adds: the same holds where junctions meet once, on every static collision of at most 7 junctions and every reached one
GROW-SMALL found. It is also shown not to be automatic here.

## Limitations

- These are the collisions found: static ones up to 7 junctions, and reached ones from those starts in two rounds. That pair plus
  three-way readings suffice in general is not shown; four-way differences were not looked for.
- States are equation spaces.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)). It suspected a tautology,
true if all junctions were three-place, and proposed the rank check. The check shows the tautology does not apply. Its fixes were
taken: one reading regime per pair, pooling "none" with "above 8", and running every pair. Its bets were 97% and 95%, and both
held.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: three-way readings on the new collisions | **Status:** Successful | All 1,034 static and 87 reached pairs separated |
| Local direction: what reading of a base is complete | Continue | Pair plus three-way readings are complete up to the allowed states on everything found, now including meet-once collisions |
| Broader exploration: what distances carry (A97) | Known alternatives | THREE-WAY's pattern, now on meet-once collisions |
| Long-term goal: G1 with A97 | Capability gained | The reading that recovers the states where pair distances fail, on every collision found |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | How the created pair arises (GROW-SMALL #2) | 2/3: the one case where the law makes the ambiguity itself | 3/3: the two starts and their rounds exist | the two starts' joins and counts side by side; why the tables agree, why the states differ, why they part a round later → stop at an explanation, or a precise open question | Selected · started next in this thread (the coordinator's go-ahead) |
| 2 | Search for a pair agreeing on pair and three-way readings with other states (static, 8 junctions) | 2/3 | 2/3 | an 8-junction static enumeration, sampled | Alternative · deferred |
| 3 | Larger starts, more rounds (GROW-SMALL #3) | 2/3 | 2/3 | as recorded | Alternative · deferred |
| 4 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 gains this study, status unchanged.

## Final report as sent (2026-11-19 14:35 UTC)

**Outcome:** yes. Pair plus three-way readings separate every meet-once collision with other states found so far. Closed, referee pending. As you asked, I'm now going straight on to how the created pair arises.

- **All separate.** That covers all 1,034 static pairs of 6 and 7 junctions and all 87 reached pairs, the created one included. In 1,000 and 73 of them, just counting how many triples have each reading already tells the two apart.
- **Not automatic.** The advisor suspected the readings might find every junction directly. They don't: the three-distinction bonds never span the equations (rank 2 to 6 against 6 to 9). So THREE-WAY's picture extends to meet-once collisions, as a finding.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: three-way readings on the new collisions | **Status:** Successful | 1,034 + 87 separated |
| Local direction: what reading of a base is complete | Continue | Pair plus three-way readings complete up to the states on everything found |
| Broader exploration: what distances carry (A97) | Known alternatives | THREE-WAY's pattern, now where junctions meet once |
| Long-term goal: G1 with A97 | Capability gained | The reading that recovers the states where pair distances fail |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | How the created pair arises | 2/3 | 3/3 | the two starts' joins and counts side by side → an explanation, or a precise open question | Selected · started next in this thread |
| 2 | A pair agreeing on pair and three-way readings with other states (static, 8 junctions) | 2/3 | 2/3 | an 8-junction static enumeration, sampled | Alternative · deferred |
| 3 | Larger starts, more rounds | 2/3 | 2/3 | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 gains this study, status unchanged. **Advisor:** Fable 5.2, before the freeze. It suspected a tautology, and the rank check rules it out. It bet 97% and 95%, and both held.

Referee hand-off: the decision note is `research/TRIPLE-GROWN-20261119-001/triple_grown.md`. Check most closely the per-pair reading regime and the 23 pairs read to 8 in `triples.py`.
