# Does the law, grown from every small arrangement, ever make a meet-once collision with other states?

Epic `GROW-SMALL-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `PARENT-RULE-20261119-001#1`.
Assumption A97; goal G1. **Referee pending.**

**Record.**
- **Pre-registration** ([preregistration.md](preregistration.md)): frozen before the runs (commit `39c8a96cf`). Amendment 1
  (commit `6bdefbc96`) came after the first launch stalled, before any stage of the run was read.
- **Code** ([the experiment family](../../experiments/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/)):
  - `job.py`, `pairs_grow.py` and `targeted.py`;
  - the outside checks `verify_t.py` and `verify_main.py`, and `origin.py`.
- **Results:**
  - [grow_pairs.json](../../artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/grow_pairs.json),
    [targeted.json](../../artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/targeted.json);
  - [verify_t.json](../../artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/verify_t.json),
    [verify_main.json](../../artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/verify_main.json);
  - [origin.json](../../artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/origin.json).

## The answer

**In the owner's terms.**
- **Yes.** Started from small arrangements beyond the census's, the law does build pairs of arrangements that meet once, share
  every bond distance, and have other allowed states. Among the 336,933 stages grown one and two rounds from all 503,039 legal
  meet-once arrangements of at most 7 junctions, 67 groups do so, holding 87 pairs. Every one was regrown from relabelled starts,
  and the 64 small enough were checked again outside the pipeline by bonds. So MEET-ONCE's finding belongs to the census's
  starts, not to the law.
- **Mostly carried, once created.**
  - **Carried: 86 of the 87 pairs.** The two starts already shared a table with other states, and the law grows both sides in
    step. All 86 still share a table read to 8 with other states one round further, and the targeted test follows some to round 3.
  - **Created: 1 pair.** Two 7-junction starts with different tables, and even different knot sizes, each grow in one round into
    12 junctions. The two results have the same table and other states; their weight counts differ, for example 122 against 125
    words of weight 9. One round further their tables differ, so the law separates what it created.
- **Why the census never showed it.** Its starts have at most five knots, and the smallest static collision with other states has
  6 junctions (PARENT-RULE). And creation is very rare: one pair in 336,933 stages.
- **What it means.** Where junctions meet once, the law keeps the states visible in the distances only as far as computed, from
  the census's starts. In general it does not: distances alone do not carry the allowed states of what the law builds.

| Test | Prediction | Verdict |
| --- | --- | --- |
| G1 | No collision with other states among the stages of rounds 1 and 2, none undecided | **failed** (67 groups, 87 pairs; none undecided; all split nowhere on escalation) |
| G2 | Power: at least 100 same-states collision groups | **held** (19,419) |
| C0 | The 472 static other-states groups recovered by the pairing | **held** (472 of 472, none undecided) |
| K | Every stage meets once; every open stage of round r has self-grown depth ≥ r; relabelled copies grow isomorphically | **held** (336,933 meet once; 324,341 open, none below its round; 950 relabelled, none different) |

| Stages grown from the 503,039 starts | Count |
| --- | ---: |
| Starts reaching round 2 / only round 1 / stalling at once | 165,026 / 6,881 / 331,132 |
| Stages (round 1 / round 2) | 336,933 (171,907 / 165,026) |
| Arrangement classes | 334,165 |
| Candidate groups (tables read to 8 isomorphic) | 19,474 |
| … same states only | 19,407 |
| … with other states (all survive to the full table) | 67 (55 of two classes, 8 of three, 4 of four) |
| Pairs in different state groups, by self-grown depth: (1, 1) / (≥ 2, ≥ 2) | 44 / 43 |
| … carried (the starts already collide) / created | 86 / 1 |
| Stages with a pair read beyond 8 (the escalation was needed) | 289,614 |

## The created pair

Start A (7 junctions, sizes 3, 3, 4, 4, 4, 4, 4) and start B (7 junctions, sizes 3, 4, 4, 4, 4, 4, 4) have different tables. Under
the law's round, A gets a join of four junctions, a join of three and three offshoots; B gets a join of four, a pair and three
offshoots. The two stages of 12 junctions and 28 distinctions are:
- not isomorphic, by two encodings;
- isometric: an explicit renaming was checked on all 378 entries of the full tables computed by bonds;
- different in their allowed states: the weight counts of the two equation spaces differ.

Both have backed pairs and live junctions apart (PARENT-RULE's properties), and each has self-grown depth 1. A stage peels back
uniquely, so each can be reached only as round 1 from its own start, or from an isomorphic one. Neither start is itself
self-grown, so no census growth reaches them.

## How it was done

- **The run (`job.py`, shared runner, 8 workers, 16 GB cap; about 12 minutes after Amendment 1).**
  - Every start was grown in complete rounds under the census's law, and each stage recorded with its table read to 8 (hashed),
    its arrangement hash, its self-grown depth, and whether it meets once.
  - Every 500th start was regrown from a relabelled copy.
- **The pairing (`pairs_grow.py`).** It used one global pool and MEET-ONCE's amended pairing, unchanged:
  - exact classes and candidate groups;
  - states first, on the tables read to 8;
  - classes with other states escalated to the full table under an alarm.
  None was undecided, and none split.
- **The control and the targeted test (`targeted.py`, run before Amendment 1).**
  - The 472 static groups were all recovered as collisions with other states.
  - Their members, grown, stay together: 43 pairs at round 1, 20 at round 2 and 6 at round 3 still share a full table with other
    states. Those were checked outside the pipeline (`verify_t.py`).
- **The outside check of the main finds (`verify_main.py`), as frozen for a failure.**
  - Full tables by bonds (PARENT-RULE's `plib`), with the renaming checked entry by entry.
  - Non-isomorphism by a second encoding.
  - Other states by weight counts, or else every table isomorphism checked by rank.
  - Relabelled starts.
  - The next round, on tables read to 8.
  The 64 pairs of at most 15 vertices were all confirmed: the renaming holds entry by entry, the pair is not isomorphic, and the
  states differ (52 already by weight counts). All 87 regrow alike from relabelled starts. One round on, the 86 carried pairs
  still share a table read to 8 with other states, while the created pair's tables differ. The 23 larger pairs (round 2) rest on
  the pipeline's full tables (exact_table_v2), and were not checked again by bonds.
- **Origin (`origin.py`).** For each pair, the two starts' full tables were compared: isomorphic with other states means carried,
  different means created.

## Known results, and what this adds

Known:
- MEET-ONCE: no such pair from the census's starts, to 40 junctions, and 50 by its referee;
- GROWN-PAIR: reached pairs with other states, all with knots sharing two;
- PARENT-RULE: 472 static meet-once groups, backed pairs, and self-grown arrangements;
- Whitney's theorems;
- weight enumerators as an invariant of a binary code (the classical one).

What this adds:
- reached meet-once collisions with other states exist: 87 pairs from small starts;
- the law carries static collisions forward for at least three rounds;
- in one case the law creates one from starts that do not collide;
- so MEET-ONCE's result is a property of the census's starts.

## Limitations

- Starts of at most 7 junctions with at most 3 (at 7: 2) loose distinctions each, and two rounds only. The cheapest counts and
  complete rounds only.
- "Created" means the starts' full tables differ. It does not say whether some third start, isomorphic to neither, reaches the same
  pair.
- Persistence of the main finds past their round is checked on tables read to 8, not full tables.
- Equation spaces without signs.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **What it added.** The targeted test and the positive control. These found the result first and proved the pipeline could see
  it.
- **Its prediction.** It expected any failure to sit among round-1 stages whose starts were already such a pair. That is where 86
  of the 87 pairs sit.
- **Its bet.** It bet 80% that G1 would hold, and G1 failed. Its worry about renamings that are not table isomorphisms was
  answered (every carrier keeps the table).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: reached meet-once collisions with other states from every small start | **Status:** Successful | 67 groups (87 pairs), all verified; 86 carried, 1 created |
| Local direction: what reading of a base is complete | Pivot within the direction | Pair distances do not carry the states of what the law builds; three-way readings (THREE-WAY) are the reading to test on these 87 |
| Broader exploration: what distances carry (A97) | Known alternatives | The census result was a property of small starts |
| Long-term goal: G1 with A97 | Obstruction learned | Distances alone lose the allowed states of reached arrangements that meet once |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Do three-way readings separate the 87 pairs (and the 472 static groups)? | 3/3: whether pair plus three-way readings stay complete up to the states where the law builds collisions | 3/3: THREE-WAY's readings and the pairs exist | three-way readings on every pair → stop at one that agrees on both, or none | Selected · proposed next |
| 2 | How the created pair arises: what the round reads of the two starts | 2/3 | 3/3 | the two starts' joins and counts side by side | Alternative · deferred |
| 3 | Larger starts and more rounds: how often creation happens | 2/3 | 2/3 | starts of 8 junctions, three rounds, sampled | Alternative · deferred |
| 4 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** one, Narrowing. MEET-ONCE's "a property of what the law reaches" holds for the census's starts, not for the law.
PARENT-RULE's inference that the protection lies in the law's exact joins and counts is narrowed the same way. **Goals:** G1
checkpoint (obstruction learned). **Assumptions:** A97 gains this study, status unchanged.

## Final report as sent (2026-11-19 14:29 UTC)

**Outcome:** yes. Grown from slightly larger starts, the law does build meet-once pairs that share every bond distance but have other allowed states. MEET-ONCE's clean result belonged to the census's small starts, not to the law. Closed, referee pending.

- **What I found.** I grew every one of the 503,039 legal meet-once arrangements of up to 7 junctions by one and two rounds. Among the 336,933 resulting stages, all of which meet once, 67 groups (87 pairs) share a full table and have other states. None was undecided, and the 64 small enough were confirmed again by an independent method.
- **Carried, and once created.** In 86 of the 87 pairs, the two starts already collided, and the law grows them in step. One round further they still share a table with other states. In one pair, two 7-junction starts with different tables each grow in one round into 12-junction stages with the same table and other states. That pair separates one round later.
- **Why the census missed it.** Its starts have at most five knots, while the smallest static collision has 6 junctions. Creation is rare: one pair in 336,933 stages.
- **Controls held.** The pipeline recovered all 472 known static collisions. Relabelled starts grow alike. Every open stage peels back as Theorem 2 says.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: reached meet-once collisions with other states from every small start | **Status:** Successful | 87 pairs, all verified; 86 carried, 1 created |
| Local direction: what reading of a base is complete | Pivot within the direction | Pair distances do not carry the states of what the law builds; three-way readings are the test |
| Broader exploration: what distances carry (A97) | Known alternatives | The census result was a property of small starts |
| Long-term goal: G1 with A97 | Obstruction learned | Distances alone lose the states of reached meet-once arrangements |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Do three-way readings separate the 87 pairs (and the 472 static groups)? | 3/3 | 3/3 | THREE-WAY's readings on every pair → stop at one agreeing on both, or none | Selected · proposed next |
| 2 | How the created pair arises | 2/3 | 3/3 | the two starts' joins and counts side by side | Alternative · deferred |
| 3 | Larger starts, more rounds: how often creation happens | 2/3 | 2/3 | 8-junction starts, three rounds, sampled | Alternative · deferred |
| 4 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** two since my last report.
- PARENT-RULE: 181 of 1,099 tables, not 178 (referee); Not a block.
- New, from this study: MEET-ONCE's "a property of what the law reaches" and PARENT-RULE's "the protection lies in the law's exact joins and counts" hold only for the census's starts; Narrowing.

**Goals:** G1 checkpoint (obstruction learned). **Assumptions:** A97 gains this study, status unchanged. **Advisor:** Fable 5.2, before the freeze. Its targeted test and positive control found the result first. It bet 80% against it and was wrong, though it named where the pairs would be.

Referee hand-off: the decision note is `research/GROW-SMALL-20261119-001/grow_small.md`. Check most closely the created pair, the 23 round-2 pairs resting only on the pipeline's full tables, and Amendment 1.
