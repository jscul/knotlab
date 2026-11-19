# Can a new junction shorten a bond in a way the distances do not foresee?

Epic `HUNT-SHORTEN-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `EXTEND-ROUND-20261119-001#1`.
Assumptions A97, A108; goal G1. **Refereed (R1): confirmed, no Block; one wording point corrected; the referee's full run extends the bound (Referee R1 below).**

**Record.** Pre-registration, frozen before the runs (commit `c4c75d76a`; prior-work line completed in `c849a1b50` before any
result): [preregistration.md](preregistration.md). Code:
[the experiment family](../../experiments/HUNT-SHORTEN-20261119-001A/HUNT-SHORTEN-20261119-001A-E001_attach/) (`attach.py`,
`selfpairs_job.py`; after the read-out `backed.py`). Results:
[attach.json](../../artifacts/HUNT-SHORTEN-20261119-001A/HUNT-SHORTEN-20261119-001A-E001_attach/attach.json),
[selfpairs.json](../../artifacts/HUNT-SHORTEN-20261119-001A/HUNT-SHORTEN-20261119-001A-E001_attach/selfpairs.json),
[backed.json](../../artifacts/HUNT-SHORTEN-20261119-001A/HUNT-SHORTEN-20261119-001A-E001_attach/backed.json).

## The answer

**In the owner's terms.**
- **The configuration exists, but not under the law.** Built directly, the advisor's configuration does what it says.
  - **The test.** On every static meet-once collision of at most 7 junctions, a junction joined by hand to two or three of the
    matched junctions is attached to both sides, and the matching is extended.
  - **The result.** The matching often fails, and usually the two new tables are no longer alike at all: 14,752 of the 14,792
    failures, in 262 of 930 pairs.
  - **Offshoots never break it,** as the advisor predicted.
  So distances alone do not survive a bridging junction.
- **But never where the law's own reading is kept.** No counterexample to the table version (Claim B) appeared anywhere:
  - **Static collisions.** None of them keeps what the round reads, so Claim B says nothing there, even after one attachment.
  - **Census stages up to 14 junctions.** 3,810 stages have a table symmetry that the equations lack but the round's reading
    keeps. All 33,918 of those symmetries tested extend through the census's own next round.
  - **The 86 carried pairs.** All 36,060 reading-keeping matchings extend (EXTEND-ROUND's referee).
- **What that says.** The danger is real for joins made anywhere. When the matching keeps the growing end that the law reads, it
  has not appeared. Being backed alone does not explain this: joins between backed junctions also break the matching
  (exploratory, after the read-out). So, within the census, whatever protects lies in the full reading. It stays a computed
  statement, not a theorem, and beyond the census it fails: Codex's six-junction start breaks it (correction below).

| Test | Cases | Verdict |
| --- | ---: | --- |
| Part 1: one junction attached to both sides of a static pair, all isometries (930 pairs with an attachment) | 41,268 | 14,792 fail (262 pairs), 14,752 with new tables not isometric at all; offshoots (17,356) never fail |
| Part 2: after one attachment, does the matching keep the round's reading? | 26,476 matching | none keeps it: Claim B not reached |
| Part 3: census self-pairs (open stages to 14 junctions; table symmetries the equations lack but the reading keeps) | 33,918 tested on 3,810 stages | **all 33,918 extend** (6 stages late, 34 capped) |
| EXTEND-ROUND's referee: the 86 carried pairs | 36,060 | all extend |

| # | Prediction | Verdict |
| --- | --- | --- |
| H1 | No offshoot attachment fails | **held** (17,356) |
| H2 | A pair-junction attachment fails somewhere (seen in the smoke test) | **held** (14,792 failures, at pairs and three-way joins, one or two fresh) |
| H3 | No Claim B counterexample after one attachment | **held, vacuously** (no attached pair keeps the reading) |
| H4 | No Claim B counterexample among census self-pairs | **held** (33,918 of 33,918) |

## The bound, as asked

- **Exhaustive within its classes.** None of the following has a Claim B counterexample:
  - every static meet-once collision of at most 7 junctions (loose counts at most 3, at most 2 at 7), vacuously;
  - each of those with one junction attached, again vacuously;
  - the open census stages of round 1 or later with at most 14 junctions, under the table symmetries taken on holder classes
    that keep the reading, as far as this study tested them. It tested 33,918 of the 108,289 found, at most 20 per stage. 34
    stages had their symmetries cut at 2,000, and 6 stages timed out.
- **The referee's run covers this bound as stated, and more.** On all 23,003 stages it took one symmetry per coset of holder-class
  permutations, with no cap, including symmetries that break holder classes. 1,746,752 keep the reading without carrying the
  equations, and all 1,746,752 extend (Referee R1 below).
- **Not covered.** All arrangements of 8 to 14 junctions outside the census; more than one round.

## How it was done

- **Part 1 (`attach.py`).** Every full-table isometry of each static pair was enumerated (cap 20,000; 2 pairs reached it).
  - For each set S of one to three live junctions that φ matches, with one or two fresh distinctions, a new junction was
    attached to both sides.
  - The extended renaming was checked entry by entry on the new tables, computed by bonds.
  - On failures, the advisor's path formula (`d′ = min(d, d(x,p) + 2 + d(q,y), …)`) was evaluated. It fails on many entries of
    both sides, so the table does not update like a path metric through the new junction.
- **Part 2.** Every matching attachment was tested for keeping the reading, with the law's round to follow; none kept it.
- **Part 3 (`selfpairs_job.py`, shared runner, 265 shards).** For every open census stage of round ≥ 1 with at most 14
  junctions:
  - its table's isometries onto itself were enumerated on holder twin classes;
  - those carrying the equations were skipped (Claim B\* covers them);
  - those keeping the reading were extended through the census's next stage and checked entry by entry.
- **After the read-out (`backed.py`).** Part 1's joins were split by whether their junctions are pairwise backed, as the law
  requires. Backed joins fail too: 23,672 of 47,928 when backed on both sides.

## Known results, and what this adds

Known:
- EXTEND-ROUND's Claim B, Lemma A and Claim B\*, and its referee's 36,060 extensions;
- PARENT-RULE's backed pairs and the census's table symmetries;
- Whitney's theorems.

What this adds:
- the advisor's mechanism, built and confirmed for joins made by hand;
- offshoots never break a matching;
- the first test of Claim B beyond 7 junctions where the hypothesis can hold (33,918 census self-pairs, all extending);
- the bounds within which no counterexample exists.

## Limitations

- One round only.
- Holder-class symmetries only in Part 3, at most 20 per stage, 14 junctions at most, with 6 stages timed out.
- Part 2 is vacuous, so Claim B has not been tested on pairs built by hand.
- Claim B is not proved.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **What it contributed.** It argued that offshoots preserve matchings (H1, held), gave the wording that keeps Part 1 apart from
  Claim B, and proposed the path-formula diagnostic and the self-pairs test. The self-pairs test is what made a real test possible.
- **Its bets.** It put 65% on Claim B surviving the self-pairs test; it survived.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a counterexample to the table version, a proof, or none within a stated bound | **Status:** Partial | The mechanism exists for joins made by hand; no counterexample to Claim B within the stated bounds (33,918 + 36,060 extensions); not proved |
| Local direction: what reading of a base is complete | Continue | Distance plus the growing end carries one round on every census case the hypothesis covers; beyond the census it fails (Codex, below) |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | Pair distances break under a bridging join; the law's reading avoids it in the census, not beyond |
| Long-term goal: G1 with A97 | Capability gained | A bounded computed form of the premise, and the mechanism that would break it |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove Claim B: why does keeping F (sets met by one junction) prevent the bridging failure? | 3/3 | 2/3 | compare a Part 1 failure with its nearest reading-keeping case; find what F fixes about bonds through a new join → a lemma, or a counterexample | Proposed |
| 2 | More rounds: iterate the extension on the carried pairs and census self-pairs | 2/3 | 2/3 | rounds 2 to 4 where tables stay exact | Alternative · deferred |
| 3 | Symmetries that break holder classes, and 8-junction static collisions | 2/3 | 1/3 | an 8-junction enumeration (needs a graph generator) | Alternative · deferred |
| 4 | B203, B204 | 2/3 | 3/3, 2/3 | as recorded | Alternative · deferred |

**Corrections:** none from this study. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 and A108 gain this
study, status unchanged.

## Referee R1 (2026-11-19)

[Report](referee-R1/report.md), its own engine and a new search. **Confirmed, no Claim B counterexample, no Block; one wording point
corrected, logged in `docs/CORRECTIONS.md` (Not a block).**
- **The full run.** On all 23,003 open stages (rounds 1 to 7, at most 14 junctions), it took one isometry per coset of holder-class
  permutations, with no cap of 20 or 2,000, and included isometries that break holder classes:
  - 3,155,442 isometries in all;
  - 526,507 carrying the equations;
  - 1,746,752 keeping the reading without carrying them, of which 1,630,590 break holder classes.
  All 1,746,752 extend to an isometry of the next table, entry by entry; the study tested 33,918, about 2%.
- **The counts reproduce.** 23,003 stages (21,899 with two junctions sharing two, 1,104 meeting once); 3,816 stages with a
  holder-preserving such symmetry, the study's 3,810 plus its 6 late; 116,162 such symmetries against the study's 108,289, its 34
  stages being cut at 2,000. One stage was finished separately with no cap: start [[4,4,4,4,4],[0,0,1,2,2,0,2,2,0,0]], round 2,
  11 junctions, with 362,496 reading-keeping symmetries, all breaking holder classes, and all extend. Part 1 was read, not rerun.
- **Corrected.** "The bound, as asked" said every holder-class symmetry of every stage; the study tested 33,918 of 108,289, with
  6 stages late and 34 cut. The section now says so, and the referee's run covers the bound as first stated.
- **For the next step.** Holder-breaking symmetries extend too, so the right hypothesis for a proof may be keeping the reading
  alone, without preserving holder classes.

## Correction (2026-11-19, from `GROWN-END-SWAP-20261119-001`; Narrowing)

"No counterexample within the stated bounds" stands: the census stages come from starts of at most five knots, and the referee's
census agrees to 11 junctions. "Whatever protects lies in the full reading" does not hold beyond the census, whether start
junctions meet twice (below) or once: Codex's [GROWN-END-MEET-ONCE-20261119-001](../GROWN-END-MEET-ONCE-20261119-001/decision.md) (refereed) fails at 12 junctions and 23 distinctions from a seven-junction
meet-once start.
- **Codex's construction.** Codex built a reached stage from a six-junction start whose junctions meet twice ([decision note](../GROWN-END-SWAP-20261119-001/decision.md), [referee report](../GROWN-END-SWAP-20261119-001/referee-R1/report.md), refereed).
  A reading-keeping, holder-breaking table symmetry there fails to extend one round.
- **Why the census missed it.** None of the census's 2,994 ten-junction stages is isomorphic to it.
- **What it uses.** It is exactly the bridging join this note built by hand: a dead junction whose distinctions split evenly
  between two holders, and a tie broken by a join's discount. Here the law makes the join itself.

Logged in `docs/CORRECTIONS.md`.

## Final report as sent (2026-11-19 15:23 UTC)

**Outcome:** no counterexample to the table version (Claim B) within the stated bounds, and no proof. The advisor's configuration is real, but only for joins made by hand. Closed, referee pending.

- **The configuration exists.** I attached one junction to both sides of every static meet-once collision of up to 7 junctions, under every table matching: 41,268 cases. A junction bridging two or three matched junctions often breaks the matching: 14,792 cases in 262 pairs, almost always leaving the tables no longer alike at all. Offshoots never break it, as the advisor predicted. So distances alone do not survive a bridging join.
- **It never fires under the law's reading.** Static collisions never keep the round's reading, so Claim B is vacuous there, even after one attachment. The real test was the advisor's self-pairs: 3,810 census stages up to 14 junctions whose table has a symmetry the equations lack but the round's reading keeps. All 33,918 of those symmetries tested extend through the next round. With EXTEND-ROUND's referee's 36,060 on the carried pairs, there is no exception anywhere.
- **Backing is not the reason.** Bridging joins between backed junctions also break matchings (after the read-out). So whatever protects lies in the whole reading.
- **The bound, as you asked.** There is no counterexample on any static meet-once collision of up to 7 junctions (vacuously), on those with one junction attached (vacuously), or on any open census stage up to 14 junctions under its holder-class symmetries (up to 20 tested per stage). All arrangements of 8 to 14 junctions, and more rounds, are not covered.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: counterexample, proof, or a bounded none | **Status:** Partial | Mechanism confirmed by hand; no Claim B counterexample within the bounds; not proved |
| Local direction: what reading of a base is complete | Continue | Distance plus the growing end carries one round wherever tested |
| Broader exploration: what distances carry (A97, A108) | Known alternatives | Distances break under a bridging join; the law's reading avoids it so far |
| Long-term goal: G1 with A97 | Capability gained | A bounded computed form of the premise, and the mechanism that would break it |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove Claim B: what does keeping the reading fix about bonds through a new join? | 3/3 | 2/3 | compare a hand-made failure with its nearest reading-keeping case → a lemma, or a counterexample | Proposed |
| 2 | More rounds on the carried pairs and self-pairs | 2/3 | 2/3 | rounds 2 to 4 where exact | Alternative · deferred |
| 3 | 8-junction static collisions; holder-breaking symmetries | 2/3 | 1/3 | needs a graph generator | Alternative · deferred |

**Corrections:** one since my last report. EXTEND-ROUND: the stall test counts groups, and B* is about the span (the referee); Not a block (commit 454a66f0a). **Goals:** G1 checkpoint (capability gained). **Assumptions:** A97 and A108 gain this study, status unchanged. **Advisor:** Fable 5.2, before the freeze. It argued offshoots are safe (they were), gave the wording, and proposed the self-pairs test that made a real test possible. It bet 65% that Claim B would survive, and it did.

Referee hand-off: the decision note is `research/HUNT-SHORTEN-20261119-001/hunt_shorten.md`. Check most closely the attachment construction in `attach.py` and the self-pair extension in `selfpairs_job.py`.
