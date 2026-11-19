# Do reached arrangements whose junctions meet once ever share a table with other states?

Epic `MEET-ONCE-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for sub-goal B205
(`GROWN-PAIR-20261119-001#2`, `THREE-WAY-20261119-001#1`). Assumptions A97, A108; goal G1. **Referee pending.**

**Record.** Pre-registration, frozen before the run (commit `3d91d3eab`), and Amendment 1 (commit `50d7cc494`, after the frozen
pairing ran an hour without output, before any pair was read): [preregistration.md](preregistration.md). Code:
[the experiment family](../../experiments/MEET-ONCE-20261119-001A/MEET-ONCE-20261119-001A-E001_meet/) (`job.py`, `pairs_meet2.py`;
the frozen `pairs_meet.py`, stopped; the control `check_full.py`). Results:
[meet_pairs2.json](../../artifacts/MEET-ONCE-20261119-001A/MEET-ONCE-20261119-001A-E001_meet/meet_pairs2.json),
[check_full.json](../../artifacts/MEET-ONCE-20261119-001A/MEET-ONCE-20261119-001A-E001_meet/check_full.json), and the run's
stage records (`results_meet-once.jsonl.gz`).

## The answer

**In the owner's terms.**
- **No, not up to 40 junctions.** Among the census stages of 15 to 40 junctions that the cheapest growth reaches in complete
  rounds and in which no two junctions share two distinctions (2,698 stages), no two different arrangements have the same
  bond-distance table and other allowed states. GROWN-PAIR's finding at up to 14 junctions is not a size effect.
- **Distances up to 8 already settle it here.** 102 groups of different arrangements agree on their tables read up to distance 8,
  and in every one of them the allowed states are the same up to renaming. So among these stages the short distances alone fix
  the allowed states, and the full tables of the 102 groups agree as well.
- **What the 102 are.** Same states, other junctions, in 103 tested pairs of three kinds:
  - 83 pair a closed stage (every distinction shared) with an open stage of one junction fewer. They have the same equations,
    since the closed stage's extra junction holds the sum of the others' equations. In the junction graph, that junction plays the
    outside's part.
  - 5 have the same junction graph, with the outside and a junction exchanged.
  - 15 have different junction graphs with the same equations (a Whitney-type rearrangement).
- **What this says with the earlier studies.** Reached collisions with other states need knots that share two distinctions:
  152 groups at up to 14 junctions (GROWN-PAIR), and 22 more at 15 and 16 found by THREE-WAY's referee. Where junctions meet once,
  none appears among reached stages to 40 junctions. This holds for what the law reaches, not for every arrangement. All six of
  UNIQUE-TABLE's static pairs meet once and have other states, and none of them is reachable.

| Meet-once grown stages, 15 to 40 junctions | Count |
| --- | ---: |
| Stages (rounds 1 to 8) | 2,698 |
| Non-isomorphic arrangements | 2,692 |
| Groups with one table read up to distance 8 (candidates) | 102 (101 of two, 1 of three) |
| … same states up to renaming | **102** |
| … other states (a candidate for M1) | **0** |
| Pairs tested within the 102 groups: closed and open of one junction fewer / outside exchanged / other junction graph | 83 / 5 / 15 |
| Undecided (cap or time) | 0 |

## Predictions and verdicts

| # | Prediction | Verdict |
| --- | --- | --- |
| M1 | No pair of non-isomorphic meet-once grown stages with isomorphic full tables and other states | **held** (0; no candidate group had other states) |
| M2 | At least one such pair with the same states | **held** (102 groups, all between non-isomorphic arrangements) |

## How it was done

- **The stages.** `job.py` regrew every census start in complete rounds under the cheapest counts. It kept each stage of rounds 1 to
  8 with 15 to 40 junctions in which no two junctions share two distinctions. For each it computed the table read up to distance
  8, exactly, and pooled beyond. It also took a Weisfeiler–Leman hash of that table and of the arrangement (265 shards on the
  shared runner, 8 workers, 16 GB cap; a few minutes).
- **Candidates.** Arrangements were deduplicated by exact isomorphism, then grouped by exact isomorphism of their pooled tables.
  This used VF2 with Weisfeiler–Leman node colours. Pooled tables are a function of the full table, so every full-table collision
  lies inside a candidate group.
- **States first (Amendment 1).** Every bijection that carries one equation space onto the other keeps the full table, and so the
  pooled one. So the states were decided on the pooled tables:
  - by an isomorphism of the junction graphs, with the outside vertex a plain vertex;
  - otherwise by enumerating pooled-table isomorphisms on twin classes, tested by rank. Twin classes are distinctions held by the
    same junctions. Any carrier maps them onto each other, and permutations inside one keep the equation space.

  Classes with the same states have isomorphic full tables, so no full table was needed. Only classes with other states would
  have been escalated to the full table, and there were none.
- **Why the amendment.** The frozen pairing escalated every candidate to the full table first. At 50 to 90 distinctions a full
  table takes hours (at 52 distinctions: 1.6 s read to 12, 238 s read to 20), and its time limit never fired. It was stopped after
  an hour, before any pair was read. The verdicts are the same in either order.

## Controls

- **The referee's count one size past.** The groups wholly at 15 and 16 junctions number 8, as GROWN-PAIR's referee found
  independently. All 8 have the same states there too.
- **Full tables, directly.** For the 23 pairs of at most 34 distinctions, both full tables were computed and compared by VF2. All
  23 are isomorphic, as the same-states argument requires (`check_full.json`).
- **Carriers.** Every same-states verdict rests on an explicit carrier. It is either a junction-graph isomorphism, or a renaming
  whose image of the stars has the same span as the other arrangement's stars, checked by rank. The 15 found by enumeration were
  each found on the first renaming tried.

## Known results, and what this adds

Known: `GROWN-PAIR-20261119-001` found 80 meet-once reached collisions at up to 14 junctions, all with the same states, and its
referee 8 more at 15 and 16. `UNIQUE-TABLE-20261119-001` found six static meet-once pairs with other states, unreachable by the law.
`THREE-WAY-20261119-001` showed that three-way readings separate every known other-states collision. In the classical terms, the
equations are the cut space of the junction graph. Two arrangements have the same states exactly when the graphs' cycle matroids
are isomorphic (Whitney's 2-isomorphism theorem), and the three kinds above are its familiar cases.

What this adds: among reached meet-once stages, the absence of other-states collisions holds to 40 junctions (2,698 stages, 102
collision groups, every one with the same states). It already holds at distance 8. So among these stages the short distances fix
the allowed states, and the only ambiguity left is which junction holds what.

## Limitations

- The census starts, complete rounds, the cheapest counts, and 15 to 40 junctions; Codex's serial mixed law was not run.
- "States" are equation spaces (no signs), as in the predecessors.
- This is a property of what the law reaches. Statically it fails at 7 and 8 junctions (UNIQUE-TABLE's six). Why the law avoids
  such pairs is not explained here.
- The 83 closed and open pairs depend on counting a closed stage as its own arrangement. Without them, 19 groups remain, and M2
  still holds.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)). It checked that the
escalation is sound if the key is invariant (it is), and that a capped search must count as undecided (taken). It bet on M1 at
about 70%, and it held. It expected any failure where three junctions meet pairwise in three distinctions; none appeared. It
proposed testing states by an orbit search under the table's automorphisms to avoid the cap. Amendment 1's twin-class enumeration
does that job: every test was decided by a junction-graph isomorphism or by the first renaming tried, and no cap was reached.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: reached meet-once collisions with other states, 15 to 40 junctions | **Status:** Successful | None among 2,698 stages; all 102 collision groups keep the states, already at distance 8 |
| Local direction: what reading of a base is complete | Continue | Where junctions meet once, reached stages lose nothing of the states to their distances; statically they do |
| Broader exploration: what distances carry (A97) | Known alternatives | Whitney's theorem names the same-states kinds; the reached and static difference is not known |
| Long-term goal: G1 with A97 | Capability gained | A scope, meeting once and reached, in which pair distances carry the allowed states, to 40 junctions |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why does the law avoid the static pairs? Compare reached meet-once stages with UNIQUE-TABLE's six static pairs: three-connection of the junction graph, cut pairs, what growth requires | 3/3: a reason, and a candidate theorem that distances carry the states of what the law reaches | 2/3: the six pairs and 2,698 stages exist; the property to test is open | test three-connection (and 2-cuts) on every reached meet-once stage and on the six → stop at a property that holds on all reached and fails on the rivals, or none | Selected · proposed next |
| 2 | Codex's serial mixed law: does it reach stages where two junctions share two? | 2/3: decides whether its collisions can have other states | 2/3: the referee's serial census to width 31 | count two-sharing stages in that census → stop at the count | Alternative · deferred |
| 3 | Pair plus three-way readings beyond the found collisions (THREE-WAY #2) | 2/3 | 2/3 | static rivals agreeing on triples, up to 10 junctions | Alternative · deferred |
| 4 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none from this study. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 gains this study (status
unchanged; a scope in which pair distances carry the states of reached stages); A108 gains it (102 groups with the same states and
other junctions). **Basket:** B205 done; B203, B204 remain.

## Final report as sent (2026-11-19 10:07 UTC)

**Outcome:** no, not up to 40 junctions. Among 2,698 reached stages of 15 to 40 junctions where junctions meet at most once, no two different arrangements share a bond-distance table with other allowed states. Closed, referee pending.

- **All 102 collisions keep the states.** That already holds for tables read only to distance 8. They differ only in which junction holds what. In 83, a closed stage pairs with an open one of one junction fewer; in 5 the outside and a junction swap; in 15 the junction graph differs.
- **This is about what the law reaches.** UNIQUE-TABLE's six static pairs also meet once and do have other states, but the law never builds them. Other-states collisions need knots sharing two.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: meet-once reached collisions, 15 to 40 junctions | **Status:** Successful | 0 with other states; all 102 keep the states |
| Local direction: what reading of a base is complete | Continue | Reached meet-once stages lose nothing to their distances; static ones do |
| Broader exploration: what distances carry (A97) | Known alternatives | Whitney's theorem names the same-states kinds |
| Long-term goal: G1 with A97 | Capability gained | A scope where pair distances carry the states, to 40 junctions |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why the law avoids the static pairs | 3/3 | 2/3 | three-connection and cut pairs on all 2,698 reached stages and the six → a property splitting them, or none | Selected · proposed next |
| 2 | Does the serial mixed law reach junctions sharing two? | 2/3 | 2/3 | count them in the referee's serial census | Alternative · deferred |
| 3 | Pair plus three-way readings beyond the found collisions | 2/3 | 2/3 | static rivals agreeing on triples, to 10 junctions | Alternative · deferred |
| 4 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** two since my last report, both from referees and both Not a block. GROWN-PAIR's meet-once headline now carries its size, up to 14 junctions. THREE-WAY's count of stages left alike is 77, not 74. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 and A108 gain this study, status unchanged. **Advisor:** Fable 5.2, before the freeze. It bet on M1 at about 70%, and M1 held. **Amendment:** the frozen pairing needed full tables of hours each, so I amended it before any pair was read: states are now tested first. The verdicts are the same.

Referee hand-off: the decision note is `research/MEET-ONCE-20261119-001/meet_once.md`. Check most closely the states test in `pairs_meet2.py` (twin classes, rank) and the claim that a same-states pair needs no full table.
