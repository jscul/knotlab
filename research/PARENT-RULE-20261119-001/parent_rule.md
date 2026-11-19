# Why does the growth never reach the static pairs?

Epic `PARENT-RULE-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `MEET-ONCE-20261119-001#1`.
Assumption A97; goal G1. **Refereed (R1): confirmed, no Block; one count corrected (178 to 181) and wording, folded in (Referee
R1 below).** The census check's last shard (starts 26,100 to 26,199) was covered by the referee's own run (252 stages, 0
violations) and closed on that evidence; the census numbers below are from the other 264 shards (26,341 starts).

**Record.** Pre-registration, frozen before the runs (commit `88303496e`): [preregistration.md](preregistration.md). Proof:
[proof.md](../../proofs/PARENT-RULE-20261119-001A/PARENT-RULE-20261119-001A-P001_backed/proof.md). Code:
[the experiment family](../../experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/) (`plib.py`,
`census_job.py`, `static_job.py`, `static_pairs.py`; after the read-out `self_grown.py`, `self_grown_all.py`). Results:
[census.json](../../artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/census.json),
[static_pairs.json](../../artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/static_pairs.json),
[self_grown_all.json](../../artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/self_grown_all.json).

## The answer

**In the owner's terms.**
- **Why the law never builds the rivals, at every size (proved).** When the law adds a junction to two older junctions, those two
  already meet a third junction, since the rule joins only junctions with a common neighbour. So in every stage the law reaches,
  any two junctions met by a junction with a loose distinction also meet a third one. The third one holds no loose distinction.
  Call these **backed pairs**. Every one of UNIQUE-TABLE's 11 rivals has a junction with a loose distinction whose partners have
  no third junction in common, so the law can never build them in any round from a connected start, at any size. The same proof shows three more things:
  - junctions with a loose distinction never meet each other;
  - removing them gives back the previous stage exactly;
  - no distance between older distinctions ever grows from one stage to the next.
- **But backed pairs do not keep the states.** Among all 503,039 legal arrangements of at most 7 junctions that meet once, 472
  groups share a table with other states. In 242 of their pairs both sides have backed pairs, and in 38 both survive one
  removal. So backed pairs alone cannot turn MEET-ONCE's "to 40 junctions" into every size.
- **What does separate them, so far.** No pair with other states has both sides surviving two removals. No pair has both sides
  that one round of the law rebuilds from their own previous stage, a test made after the frozen ones failed. These are thin: only
  77 and 85 of the 503,039 arrangements qualify. So the protection comes from the rule's exact choice of joins and counts, not
  from backed pairs alone, and at these sizes that has hardly any room to show.
- **The table's own symmetries.** A reached table can be symmetric in a way the allowed states are not. About one in six of the open
  meet-once reached stages of up to 14 junctions have such a symmetry (181 of 1,099). The renamed copy has the same table and other
  states but is the same arrangement, so it is not a collision. The advisor's suggested cleaner theorem, that every table symmetry
  keeps the states, is false.

| Test | Prediction | Verdict |
| --- | --- | --- |
| C1 | Census stages of round ≥ 1 to 40 junctions: backed by a closed junction, live junctions apart, peel gives the previous stage, depth ≥ round | **held** (0 violations in 70,228 stages; 264 of 265 shards, the last pending) |
| C2 | No previous-stage pair farther in the next open stage (Theorem 3), on open stages ≤ 14 junctions | **held** (22,921 stages: 2,503,142 pairs equal, 162,940 shorter, 0 farther) |
| R1 | Open meet-once reached stages ≤ 14 junctions rigid | **failed** (181 of 1,099 have a table symmetry that does not keep the states) |
| S0 | Other-states collisions among the 503,039, pop-0308's pair among them | **held** (472 groups, 1,034 pairs; the pair found, truth and rival in different state groups) |
| S1a | No other-states pair with both sides backed, in the backed stratum | **failed** (242 pairs; the smallest at 6 junctions) |
| S1b | No other-states pair with both sides of peel depth ≥ 1 | **failed** (38 pairs, all at 7 junctions) |
| S1c | No other-states pair with both sides of peel depth ≥ 2 | **held**, with little power (77 arrangements of depth ≥ 2; 4 pairs with one side) |

## The numbers

| Legal meet-once arrangements of 2 to 7 junctions | Count |
| --- | ---: |
| Arrangements (one per orbit; loose counts ≤ 3, ≤ 2 at 7 junctions) | 503,039 |
| … backed (P1) / peel depth ≥ 1 / ≥ 2 / control Q | 58,972 / 4,671 / 77 / 200,002 |
| … self-grown: one round of the law from its own peel gives it back | 85 |
| Table groups of two or more | 38,301 |
| … same states only | 37,829 |
| … other states | 472 (1,034 pairs; none undecided) |
| Other-states pairs with both sides backed / depth ≥ 1 / depth ≥ 2 / Q / self-grown | 242 / 38 / 0 / 30 / 0 |
| Collision groups among the 85 self-grown | 9, all same states |

| Census, rounds 1 to 8, to 40 junctions (264 of 265 shards) | Count |
| --- | ---: |
| Stages of round ≥ 1 (meet once) | 70,228 (3,889) |
| … violations: backed by a closed junction / live apart / peel gives the previous stage / depth ≥ round | 0 / 0 / 0 / 0 |
| Open stages ≤ 14 junctions: previous-stage pairs equal / shorter / farther | 2,503,142 / 162,940 / 0 |
| Full tables ≤ 14 junctions with a symmetry the states lack: open meet-once / open with two shared / closed | 181 of 1,099 (178 found by symmetries that keep the holder classes) / 4,476 of 21,822 (11 capped; holder classes only) / 615 of 2,714 |
| Tables read to 8, open meet-once stages of 15 to 40: a symmetry not keeping the states (not decisive) | 313 of 2,600 (31 capped) |
| Starts with backed pairs / with backing by a closed junction and live apart | 6,309 / 3,404 of 26,341 |

The control Q requires backed pairs of the closed junctions instead of the live ones. Compare each property's share of the
population with its share of the 2,068 sides of other-states pairs:
- backed pairs: 12% of the population (58,972), but 38% of the sides;
- Q: 40% of the population (200,002), but 9% of the sides.

So at these sizes backed pairs do not protect. If anything, they go with collisions.

## How it was done

- **Ticket A (proof).** Theorems 1 to 3, read off the joining rule.
  - Before a round, the joining junctions are exactly the last round's junctions with a loose distinction. Each gives all of
    them away.
  - A new junction meets only its parents, once each, and new junctions share nothing.
  - Parents were candidates, so a third, older junction meets both. It holds no loose distinction once the round is over.
  - In an open stage every new junction has a fresh distinction (a junction without one holds every loose distinction and closes
    the stage). So removing the live junctions gives the previous stage, and every bond of the previous stage is still a bond.
- **Part C (census).**
  - Every census start was regrown to 40 junctions, and the theorems checked on every stage.
  - Rigidity: every isomorphism of a stage's table onto itself, taken on twin classes, was tested by rank for whether it keeps
    the equation space. This used full tables up to 14 junctions, and tables read to 8 for meet-once stages of 15 to 40.
  - Theorem 3's comparison was run on every open stage of up to 14 junctions.
- **Part S (static).**
  - Every connected simple graph of the networkx atlas on 2 to 7 vertices was taken as the junctions, with every loose count
    per junction up to the graph's automorphisms, keeping the legal ones.
  - Exact tables were computed by bonds, then grouped by isomorphism.
  - States were compared by a junction-graph isomorphism, or else by every table isomorphism on twin classes checked by rank.
- **After the read-out (exploratory, not frozen).** I tested whether each member of an other-states pair is **self-grown**:
  whether one round of the census's law, applied to the arrangement left after removing its live junctions, gives it back. Every
  open reached stage is self-grown, since the law's round reads only the arrangement before it. This was checked on 405 census
  stages.

## Known results, and what this adds

Known:
- the joining rule (`FRESH-COUNT-20261118-001`, `FIRST-KNOT-20261118-001`);
- UNIQUE-TABLE's six static pairs and MEET-ONCE's reached collisions;
- Codex's reachable collisions under the serial law, related by a table symmetry;
- CENSUS-READ's 1,480 stages with a table symmetry that moves a junction, which R1's prediction should have weighed;
- Whitney's 2-isomorphism theorem, and his edge-isomorphism theorem with its small exceptions (the four junctions that pairwise
  meet are one).

What this adds:
- a proved, size-free reason the law never builds UNIQUE-TABLE's rivals (backed pairs);
- exact peeling, and the fact that distances between older distinctions never grow;
- the finding that backed pairs, or one peel, do not keep the states statically at 6 and 7 junctions;
- the finding that the census's open meet-once tables are often symmetric in ways the states are not.

## Limitations

- The static test stops at 7 junctions. There the arrangements that peel twice or are self-grown are too few to test the
  stronger forms. The advisor expects the first informative collisions at 8 to 10.
- "States" are equation spaces (no signs).
- Self-grown was tested after the frozen ladder failed, so it is a lead, not a result.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **What it got right.** It corrected the lemma's statement and proposed the strata, the ladder, the power counts, the control
  and the rigidity test. All were taken. It warned that 7 junctions is too few for the stronger forms, which is what happened.
- **Its bets.** It put about 85% on the backed stratum, which failed (242 pairs). It put about 85% on the peeled form; S1c held,
  but with little power.
- **Rigidity.** Its suggested cleaner theorem, rigidity, is false on the census.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a property splitting reached stages from the rivals, kept at every size | **Status:** Partial | Backed pairs split them and are proved kept at every size; but they do not keep the states (242 static pairs), so they do not give MEET-ONCE at every size |
| Local direction: what reading of a base is complete | Continue | The protection lies in the rule's exact joins and counts; self-grown arrangements are the population to test |
| Broader exploration: what distances carry (A97) | Known alternatives | Whitney's theorems; table symmetries that the states lack are common |
| Long-term goal: G1 with A97 | Obstruction learned | A local property of what the law builds is not enough for distances to carry the states |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One and two rounds of the law from every legal small arrangement: do self-grown meet-once arrangements ever collide with other states? | 3/3: the law's own population far beyond the census's starts | 3/3: the 503,039 arrangements, the law and the states-first pairing exist | grow each one and two rounds, keep meet-once, pool at 8, pair → stop at an other-states pair, or none | Selected · proposed next |
| 2 | Why backed pairs fail: the 24 pairs at 6 junctions | 2/3 | 3/3 | compare the 24 with what one round of the law makes | Alternative · deferred |
| 3 | When Theorem 3 is strict: which older pairs get shorter | 2/3 | 3/3 | the 162,940 shorter pairs against the junction that takes them | Alternative · deferred |
| 4 | B203, B204, THREE-WAY #2 | 2/3 | 2/3 to 3/3 | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G1 checkpoint (obstruction learned). **Assumptions:** A97 gains this study, status unchanged.
**Basket:** #1 taken next if the coordinator agrees; #2 and #3 recorded.

## Referee R1 (2026-11-19)

[Report](referee-R1/report.md), the proofs read; its own growth, enumeration, tables and states. **Confirmed, no Block; one count
corrected and wording, folded in above and logged in `docs/CORRECTIONS.md` (Not a block).**
- **Confirmed.**
  - Theorems 1 to 3 are correct as proved. Lemma 2 needs the start connected, and all 26,441 census starts are.
  - On every census start, the pending shard included: 70,480 stages, 0 violations. On 17,934 open stages of at most 12 junctions,
    Theorem 3 holds with none farther.
  - The static count 503,039 (by Burnside's lemma) and every collision figure reproduce: 472 groups, 1,034 pairs, 242 both backed,
    38 both of depth ≥ 1, 0 both of depth ≥ 2.
  - `plib.states` is sound.
- **Corrected: 178 to 181.** The rigidity test enumerated only table symmetries that map distinctions with the same holders onto
  each other. Those are the only ones that can keep the states, so the test is exact for "keeps". But a symmetry that breaks such
  a class also counts as one the states lack, and 3 more stages have only those. Over every table symmetry, 181 of 1,099 open
  meet-once reached stages have one the states lack.
- **Wording.** "The law can never build them, at any size" now says "in any round from a connected start": Theorem 1 covers
  rounds 1 and later, not the start itself.
- **The pending shard.** It was folded in on the referee's evidence (252 stages, 17 meet once, no violation). The coordinator
  signed off the LONG_RUNNING row. My own run of that shard was stopped.

## Final report as sent (2026-11-19 12:38 UTC)

**Outcome:** half yes. One property explains why the law never builds the static rivals, and it is proved for every size. It does not carry the allowed states by itself, so MEET-ONCE's "to 40 junctions" stays a computed result. Closed, referee pending; the census check's last shard is still running.

- **Why the rivals are never built (proved).** The law joins two junctions only when some third junction meets both. So in every stage it reaches, any two junctions met by a junction with a loose distinction also meet an older junction. Call these backed pairs. All 11 rivals lack them. The same proof shows that removing the newest junctions gives back the previous stage exactly, and that older distances never grow. The census confirms all of this: 70,228 stages, no exception.
- **Backed pairs do not keep the states.** Among all 503,039 legal arrangements of up to 7 junctions that meet once, 242 pairs share a table, have other states, and are backed on both sides. So the protection comes from the law's exact joins and counts. Pairs that peel twice, or that one round of the law rebuilds, never collide with other states, but only 77 and 85 arrangements qualify.
- **Tables are often more symmetric than the states.** 178 of 1,099 open meet-once reached tables have a symmetry the states lack. It only yields a renamed copy, not a collision. The advisor's cleaner theorem, that every table symmetry keeps the states, is therefore false.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a property that splits reached stages from the rivals, kept at every size | **Status:** Partial | Backed pairs split them and are proved kept; they do not keep the states |
| Local direction: what reading of a base is complete | Continue | The law's exact rounds, not a local property, are what to test |
| Broader exploration: what distances carry (A97) | Known alternatives | Whitney's theorems; table symmetries the states lack are common |
| Long-term goal: G1 with A97 | Obstruction learned | A local property of what the law builds is not enough |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Grow every legal small arrangement by one and two rounds of the law; do the meet-once results ever collide with other states? | 3/3 | 3/3 | 503,039 starts, states-first pairing → stop at an other-states pair, or none | Selected · proposed next |
| 2 | Why backed pairs fail: the 24 pairs at 6 junctions | 2/3 | 3/3 | compare with one round of the law | Alternative · deferred |
| 3 | When distances shorten (Theorem 3 strict, 162,940 pairs) | 2/3 | 3/3 | the shorter pairs against the junction that takes them | Alternative · deferred |
| 4 | B203, B204, THREE-WAY #2 | 2/3 | 2/3 to 3/3 | as recorded | Alternative · deferred |

**Corrections:** one since my last report. MEET-ONCE: without the closed stages, 20 groups remain, not 19, and its law-like sentences now give their computed size; Not a block. **Goals:** G1 checkpoint (obstruction learned). **Assumptions:** A97 gains this study, status unchanged. **Advisor:** Fable 5.2, before the freeze. It shaped the strata, the ladder, the controls and the rigidity test. Its 85% bet on backed pairs failed. **Stress test pending:** one census shard (100 starts) is still running and registered; I'll fold it in when it ends.

Referee hand-off: the decision note is `research/PARENT-RULE-20261119-001/parent_rule.md`. Check most closely Theorems 1 to 3 in ticket A's proof, the static enumeration's legality and orbit reduction in `static_job.py`, and the states test in `plib.py`.
