# Does a table isometry that keeps what the round reads extend one round?

Epic `EXTEND-ROUND-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `CREATED-PAIR-20261119-001#1`.
Assumptions A97, A108; goal G1. **Referee pending.**

**Record.** Pre-registration, frozen before the run (commit `eb910b08e`), with the statement of what the round reads:
[preregistration.md](preregistration.md). Code:
[extend.py](../../experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend/extend.py). Result:
[extend.json](../../artifacts/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend/extend.json).

## The answer

**In the owner's terms.**
- **What one round reads.** In a connected arrangement, one round reads only three things: which junctions hold a loose
  distinction (the live ones), how many each holds, and which sets of live junctions some one junction meets. Nothing else about
  the arrangement enters. **This is proved (Lemma A).**
- **Distance plus that reading: computed for one round, not proved.** Take any of the 57 reached carried pairs that have a table
  renaming keeping this reading. Every such renaming tried, 2,198 in all, extends to a renaming that matches the next round's
  tables. None failed. So on everything tested, distance plus the growing end carries what grows one round further.
- **Why it is not a theorem yet.** The advisor's argument: after a round, a new junction with one fresh distinction can sit inside
  a bond and make it shorter. Which bonds shorten depends on more than the pair distances, on three-way readings among other
  things. So nothing forces the next table from the old table and the reading, and it could fail elsewhere. The version that is
  proved uses the equations in place of the table: same equations plus the same reading carry everything that grows, every round
  (Claim B\*). But these pairs have other equations by construction, so that version says nothing about them.
- **The six, and persistence without the reading.** Six carried pairs have no renaming keeping the reading. They are the smallest
  (9 junctions, from 7-junction starts gaining two junctions in round 1), and in each, one of the junctions the renaming does not
  match is live. They persist anyway, through a different renaming of the next tables that still carries old distinctions onto
  old ones. Among the static pairs, 43 of the 96 that grow on both sides also persist with no renaming keeping the reading, and
  53 part. So keeping the reading is enough (as computed), but not needed.

| Pairs (both members at most 15 vertices) | Pairs | Both grow a round | A renaming keeps the reading | Its extensions tested / isometries of the next tables | Next tables isometric |
| --- | ---: | ---: | ---: | ---: | ---: |
| Reached, carried | 63 | 63 | 57 | 2,198 / **2,198** | 63 (57 with the reading kept, 6 without; all carry old onto old) |
| Reached, created | 1 | 1 | 0 | none | 0 (parts) |
| Static (starts) | 1,034 | 96 | 0 | none | 43 (all without the reading), 53 part |

| # | Prediction | Verdict |
| --- | --- | --- |
| X1 | Every tested extension of a reading-keeping renaming is an isometry of the next tables | **held** (2,198 of 2,198) |
| X1′ | Every pair with a reading-keeping renaming has one that extends | **held** (57 of 57) |
| X2 | Lemma A: every reading-keeping renaming gives corresponding rounds | **held** (the extension was always defined) |

## Lemma A and Claim B\* (proved)

**Lemma A.** Let a be connected. The round's new junctions are determined, up to relabelling, by R(a): the live junctions L,
their loose counts, and the family F of sets of live junctions met by one junction. So are their parent sets and fresh counts.

*Proof.*
- Two live junctions are candidates exactly when they lie in a common member of F.
- The sets are the maximal cliques of candidates, of three or more, contained in no member of F. The pairs are the candidate
  pairs in no set.
- The leftovers become offshoots. The stall test compares each junction's number of sets with its loose count.
- After the round, the live junctions are the new ones, and each new junction meets only its parents (PARENT-RULE Lemma 1).
  So the next round's candidates and sets among them, and hence the demands and the fresh counts, read only the parent sets.
- The implied test reads only whether a junction takes every loose distinction, since a is connected (PARENT-RULE Lemma 2). ∎

**Claim B\*** (the advisor's). Suppose a renaming φ carries a's equations onto b's and keeps R. Then its extension carries the next
equations, and so the next tables.

*Proof.* Old junctions keep their distinction sets, so the next equations are the old ones plus the new junctions'. φ carries the
first by hypothesis and the second by Lemma A; re-pairing twins inside a live junction is harmless, since they are parallel. The
extension again keeps the next reading, which reads only parent sets. So the pair stays together at every later round. ∎

**Claim B** (the table in place of the equations) is the question computed above. It held on every instance, and it is not proved.

## How it was done

`extend.py` enumerated every full-table isometry of each pair, with no twin quotient (cap 20,000; 2 static pairs reached it). For
each isometry it tested whether the reading R is kept. For up to 50 that keep it, it built the extension and checked it entry by
entry against the next round's full tables, computed by bonds, or by exact_table_v2 with no bound. Separately it recorded whether
the next tables are isometric at all, and whether some next isometry carries old distinctions onto old ones.

## Known results, and what this adds

Known:
- PARENT-RULE's Lemmas 1 and 2;
- CREATED-PAIR's growing end, and its 6 of 63;
- GROW-SMALL's persistence and its referee's full-table check of it;
- MEET-TWIST's coupling of two presentations under another law.

What this adds:
- the round's exact reading, proved;
- the equations-plus-reading persistence, proved;
- the table-plus-reading extension, on 2,198 of 2,198 instances;
- what the six are, and that persistence without the reading is common among static pairs.

## Limitations

- One round, on pairs of at most 15 vertices, and only the extensions of isometries that keep the reading (up to 50 per pair).
- Claim B is not proved, and the advisor expects it to fail somewhere (its 25%). The configuration it expects is a new
  pair-junction with one fresh distinction whose parents' three-way readings differ between the two sides. No such case occurred
  here.
- The static pairs are near-vacuous for X1: none has an isometry keeping the reading.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **What it contributed.** It confirmed Lemma A, with connectedness as the condition, and gave Claim B\* with its proof. It argued
  that Claim B has no general reason to hold, and named the configuration where it would fail. It split the pairs into classes and
  proposed the age check, both taken.
- **Its bets.** 80% that some extension works and 60% that every one does. Both held here. It put 25% on Claim B in general,
  which stays open.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: does a reading-keeping isometry extend one round | **Status:** Partial | Lemma A and the equations version proved; the table version held on all 2,198 extensions, but is not proved |
| Local direction: what reading of a base is complete | Continue | Distance plus the growing end carries one round on every tested case; a proof or the advisor's counterexample is the next step |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | The equations version is the routine one; the table version is the owner's premise in its clean form |
| Long-term goal: G1 with A97 | Capability gained | The round's exact reading, and a computed extension rule for distance plus the growing end |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Hunt the advisor's counterexample, or prove Claim B for reached meet-once stages | 3/3: the clean premise as a theorem, or its exact limit | 2/3: the configuration is named; build pairs with a one-fresh pair-junction and differing three-way readings at its parents | construct or search such pairs, test the extension → stop at a counterexample, or a proof using what reached stages have (backed pairs, live junctions apart) | Proposed |
| 2 | Iterate the extension: do the 57 keep the reading and extend at rounds 3 and 4? | 2/3 | 3/3 | grow and re-test → stop at a failure or 4 rounds | Alternative · deferred |
| 3 | Why persistence without the reading (the 6, the 43 static) | 2/3 | 2/3 | the weakest reading that still extends | Alternative · deferred |
| 4 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none from this study. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 and A108 gain this
study, status unchanged.

## Final report as sent (2026-11-19 14:55 UTC)

**Outcome:** partly. What one round of the law reads is now proved exactly. The clean form of your premise, that distance plus the growing end carries what grows, held one round on every case tested, but it is not proved. Closed, referee pending.

- **Proved: what the round reads.** In a connected arrangement it reads only three things: which junctions hold a loose distinction, how many each holds, and which sets of them some one junction meets (Lemma A). With the equations themselves in place of the distances, the advisor's three-line proof (Claim B*) shows that a matching renaming carries everything that grows, every round. These pairs have other equations, though, so that version says nothing about them.
- **Computed: distance plus that reading, one round.** In 57 of the 63 small reached carried pairs, a table renaming keeps the reading. All 2,198 such renamings tried extend to a matching of the next round's tables. None failed.
- **Why it is not a theorem.** The advisor's argument is that a new junction with one fresh distinction can sit inside a bond and shorten it, and that depends on more than pair distances. It named the configuration to hunt; none occurred here.
- **The six.** They are the smallest carried pairs (9 junctions), in which one unmatched junction is live. They persist through a different renaming. Persistence without the reading is common: 43 of 96 grown static pairs do it too.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: does a reading-keeping isometry extend one round | **Status:** Partial | Lemma A and the equations version proved; the table version held on 2,198 of 2,198, unproved |
| Local direction: what reading of a base is complete | Continue | A proof, or the advisor's counterexample, is next |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | The equations version is routine; the table version is the premise |
| Long-term goal: G1 with A97 | Capability gained | The round's exact reading; a computed extension rule |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Hunt the advisor's counterexample, or prove Claim B for reached meet-once stages | 3/3 | 2/3 | build pairs with a one-fresh pair-junction and differing three-way readings at its parents → a counterexample, or a proof | Proposed |
| 2 | Iterate the extension on the 57 to rounds 3 and 4 | 2/3 | 3/3 | grow and re-test | Alternative · deferred |
| 3 | Why persistence without the reading | 2/3 | 2/3 | the weakest reading that still extends | Alternative · deferred |

**Corrections:** one since my last report. CREATED-PAIR: the carried pairs' differences are not always two junctions from the growing end (the referee); Not a block (commit c0422d944). **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 and A108 gain this study, status unchanged. **Advisor:** Fable 5.2, before the freeze. It confirmed Lemma A, gave Claim B* with its proof, argued Claim B could fail, and named where. Its bets of 80% and 60% held here.

Referee hand-off: the decision note is `research/EXTEND-ROUND-20261119-001/extend_round.md`. Check most closely the proofs of Lemma A and Claim B*, and the extension built in `extend.py`.
