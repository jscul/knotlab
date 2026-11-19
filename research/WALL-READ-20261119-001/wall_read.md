# A reading past the wall

Epic `WALL-READ-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `MERGE-BURST-20261119-001#1`. Goal
G17. Framed by A110: these are samples of an unlimited structure, read where possible. **Referee pending.**

**Record.**
- **The proof:** [proof.md](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/proof.md), frozen as
  Partial in commit `4e1b62bbd`, then completed.
  - **Its machine check:**
    [rosterlib.py, job.py, merge.py](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/), through the
    shared runner (`WALL-READ-A1`, `runs/wall-read-a`, 32 cases, all ok).
- **The experiment:** [preregistration.md](preregistration.md), frozen in the same commit.
  - **The code:** [job.py, merge.py](../../experiments/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/), through the
    shared runner (`WALL-READ-B1`, `runs/wall-read-b`, 42 cases, all ok).
  - **Results:** [results.json](../../artifacts/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/results.json).
  - **One post hoc check:** [double_count.py](posthoc/double_count.py) and its [output](posthoc/double_count.json).
- **The advisor** checked the design before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **A blow-up without end, read exactly (proved).** Take knots in partner pairs, each able to join every knot but its partner,
  with as many open distinctions as that needs. Every round keeps that form.
  - **The counts.** From six knots they run 8, 10, 24, 4,086, then 2^2043 − 24. Each count is about two to the power of half the
    one before, which the guide will call **runaway growth**.
  - **It never stalls and never ends,** and every round of it is read exactly. Eddies and polynomial growth also never end; this
    is the first start of the explosive kind shown never to end, and the first growth shown faster than every exponential.
  - **It is a known mechanism.** It is Neumann-Lara's octahedra (1978), the first graphs whose iterated clique graphs grow without
    bound, under the growth's rule. That rule drops the joins a block holds, which subtracts the round before last.
  - **Its knots need eight places,** one more than EXPLOSIVE's sample allowed.
- **Past the wall, the old kind of reading cannot work (proved).** A reading by clusters of the unrolled map counts at most
  exponentially many junctions in their size. Runaway growth outruns that, so the clusters would have to be as large as the
  previous round. The wall is a real limit of that kind of reading, not a gap in a proof.
- **The growth is a clique operator.** Each round keeps the largest sets of mutually joinable knots that no single knot meets
  (Lemma R restated). A compact engine built on that alone agrees with the program's engine on every comparison: all 26,441 census
  arrangements, 995 random starts (5 stopped by limits) and the two read explosive starts.
- **A part of a stage bounds its next round (proved).** Any set of live knots, read exactly, gives a lower bound on the next round.
  Its own largest joinable sets each extend to a join of the whole, less one per block and one per knot that can join nothing. A partnered part of k pairs gives 2^k less
  the blocks. This reads one growth from a sample of itself, which A110 asks for. The bound never failed on 6,033 stages plus 140
  in the explosive follow.
- **On the smallest unread start (start-03) the reading is weak.** The compact engine takes it one round further: round 8 has
  28,065 junctions, against the 386 of round 7.
  - **Round 8.** 28,008 of its groups have three or more parents, the largest 109, and its largest block holds 17,207 junctions.
  - **The bound on round 9.** The best partnered part has 14 pairs, so round 9 holds at least 16,019 groups. I had predicted a
    million.
  - **Lemma 3 gives nothing here.** Its two-round bound needs a partnered part with no outside common candidate, and the largest
    such part had one pair.
- **The other 13 unread starts** were each followed one or two rounds further than before, with last jumps of ×10 to ×650 before
  memory or time ran out. Examples:
  - start-02, -05 and -08 (three starts with identical counts) reach 102,871 in round 9, with one block holding 102,475 of them;
  - start-14 reaches 162,336 in round 8;
  - start-01 reaches 21,516 in round 10.

  In none of them do the bounds read past the last round built, and none merges into one block.
- **Start-04's merge reading is now checked one round by growth.** Its round 9 has 304,590 junctions, every one a pair, as the
  block of 781 says (C(781, 2)).
- **What a sample of the explosive kind shows, so far.** In the three starts checked post hoc (start-03, -06 and -07), the last
  jump is made of groups of three or more (99% or more of each round), not of pairs inside one block. Yet small random parts of
  their stages hold few such groups, and their partnered parts are small, so the bounds read them weakly: the structure that makes
  tens of thousands of large groups is neither random-like nor partnered. Whether they end, repeat or run away is still unread.

## Predictions and verdicts

**The proof (ticket A).** 4 of 4 machine checks held ([machine_check.json](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/machine_check.json)).

| # | Check | Verdict | Reading |
| --- | --- | --- | --- |
| M1 | partnered starts n = 3, 4, 5 by both engines | **held** | every round reachable and the next count from the open counts: 4,086, 248 and 65,526 |
| M2 | controls | **held** | one open distinction short stalls; one extra gives 2n offshoots; the ring of four stays at 4 for 10 rounds |
| M3 | Lemma 2 on stages of random and explosive starts | **held** | 6,033 stages, no exception |
| M4 | Lemma 3 on the same | **held** | 1,963 stages, 61 giving a non-empty partnered part next round |

**The experiment (ticket B).** 4 of 6 held as scored, and 2 failed: the bounds read the natural starts weakly.

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| B1 | the roster engine equals the program's engine | **held** | 26,441 census, 995 random (5 stopped by limits), 2 read starts; none differs |
| B2 | start-03's double count; fastlib lists 28,064 round-8 groups, largest 109 | **held** (double count post hoc) | fastlib: 28,064 and 109. The frozen job writes a round's parent sum only after the next round is listed, and round 9 ran out of memory; rebuilt post hoc, 993,164 = 993,164 |
| B3 | Lemma 2's bounds never exceed a listed next round | **held** | 140 stages of the 16 starts |
| B4 | (risky) start-03's round 9 proved ≥ 10^6 | **failed** | partnered bound 16,019; the sub-count 63 (random parts of 128 junctions hold only 428 largest cliques) |
| B5 | for ≥ 10 of 13 other unread starts, the bound exceeds the last count built | **failed** | 0 of 13. Four stages exceed 60,000 junctions, beyond the search's cap; on the rest the best bound is at most 7,899 (start-06, 12,004 junctions) |
| B6 | no unread start merges into one block | **held** | none of 14; start-02's round 9 comes closest, one block holding 102,475 of 102,871 |

## Assumptions

- **A110** gets a history line. A blow-up that provably never ends exists and is read exactly (the partnered start). A part of one
  growth, read exactly, bounds its next round, which is a first sampling inside one growth; on the explosive sample those bounds
  are weak. Status unchanged.
- **A109** gets a history line. The explosive kind now holds a member read completely, partnered runaway growth. The 14 sampled
  ones stay unread. Status unchanged, Under challenge.
- **No new entry.** The default choices here, the greedy search and the sub-count procedure, are methods that give lower bounds.
  Nothing rests on them beyond the bounds they give.

## Prior work in the program (searched at close)

The objects-index search was not run before the freeze; the pre-registration named its prior work by hand. Run at close
(disclosed), with `--until 2026-11-19 --exclude WALL-READ-20261119-001`:
- `track.py objects "explosive starts maximal blocks share two points"` and `"maximal cliques lower bound next round"`: the top rows
  are `MERGE-BURST-20261119-001` (the 16 starts followed here), `REDUCE-BLOCKS-20261119-001` (Lemma R) and
  `EXPLOSIVE-20261119-001` (the sample), all named in the pre-registration, and `ADDR-KNOTS-20261113-001`, which matched on
  "clique" and studies an unrelated object.
- `"cocktail-party graph octahedron clique graph divergent"`: `ADDR-KNOTS-20261113-001`, `PICK-TWO-20261118-001` and
  `OVERLAP-READ-20261111-001`, matched on "clique" or "graph"; unrelated objects.
- `"iterated exponential growth never ends"`: `RANDOM-FATES-20261112-001` (newest-four growth never ends, proved: a relative, a
  different growth law that never ends), `WEIGHTINGS-20261119-001` (the sample's weightings: unrelated
  object) and `LIMIT-STATE-20261112-001` (unrelated).

No earlier study found measures partnered starts or bounds a round from a part of a stage.

## Known results, and what this adds

- **Known.**
  - **Neumann-Lara (1978).** The literature's clique graph of the cocktail-party graph O_n is O_{2^(n−1)}, so iterating it diverges:
    the first clique-divergent graph.
  - **Open in general.** Whether a finite graph's iterated clique graphs diverge is not known to be decidable. Cedillo and Pizaña
    (2021) prove it undecidable for automatic graphs.
  - **Folklore.** Distinct maximal cliques of an induced subgraph extend to distinct maximal cliques of the graph.
- **What this adds.**
  - **The growth is a clique operator.** Each round of the cheapest growth keeps the maximal cliques that no block holds. That
    drop is the "− N(t−1)" of Theorem 1, and it is why partnered starts behave like Neumann-Lara's octahedra.
  - **The first explosive start shown never to end, and the first growth shown faster than every exponential,** with every
    round read exactly.
  - **No cluster reading can follow it.** That is a proof that the wall is real for readings of the tree-of-blocks kind.
  - **Two bounds on the next round from part of a stage.** They are proved and checked, but weak on the sampled starts.

## Limitations

- **The bounds are lower bounds.** A weak bound says nothing against a large next round. Start-03's round 9 may well be far above
  16,019.
- **The search is greedy.** Larger partnered parts may exist in every stage tried.
- **The limits.** 7 GB and 20 minutes per start. Stages over 60,000 junctions were not searched. The 14 unread starts may end,
  repeat or run away; nothing here decides which.
- **Partnered starts lie outside the sample.** Their knots need eight places; EXPLOSIVE sampled seven. Whether a start within
  seven places reaches a partnered stage, or one that retracts onto one, is open.
- **Corollary 4** covers partnered starts and any start with faster-than-exponential counts. It is not proved for every start past
  the wall.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze.
- **It confirmed** the partnered proof and named four gaps, all closed: distinct blocks, monotonicity, round 1 apart, and the
  closing clause.
- **It narrowed the obstruction** to regular covers and a size function s(t). The scope line in Corollary 4 is its.
- **It proposed** the partnered bound ahead of a retraction lemma or sampling. It also proposed the words "partnered" and "runaway
  growth", and tightened the predictions: B2's double count, fresh values for n = 4 and 5, and the controls.
- **Its one wrong point** came from my question. I wrote that in stage 7 each point misses "117 to 148" others, but 117 is the
  fewest; it read that as an inconsistency with the density 0.36.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a reading past the wall | **Status:** Partially successful (proof 4 of 4 checks; experiment 4 of 6, B4 and B5 failed) | Partnered starts are read exactly past the wall and run away without end, and no cluster reading can follow them; on the 14 sampled starts the new bounds read weakly |
| Local direction: the explosive kind (A109) | Research directions | One member read completely (runaway); the sampled ones jump through large groups that neither bound captures |
| Broader exploration: what the cheapest growth builds | Capability gained | The growth is a clique operator dropping the joins a block holds; its fate links to clique-divergence, open in general |
| Long-term goal: G17 | Capability gained | A blow-up that never ends, read exactly, and a way to bound one growth's next round from a part of it |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A retraction lemma: a stage whose blocks map onto a partnered stage (blocks into blocks) runs away at least as fast | 3/3 — it would read any start that retracts, with a lower bound for every later round | 2/3 — Neumann-Lara's retraction theorem is the template; offshoots and held cliques are the work | prove it for maps that send blocks into blocks → stop at a proof, or a start where it fails | Alternative · proposed |
| 2 | Does any start within seven places reach a partnered stage, or one that retracts onto it? | 3/3 — runaway growth inside the sample, not only by construction | 2/3 — the compact engine and the search exist | search the census and EXPLOSIVE's population for partnered stages of order ≥ 3 with no outside common candidate → stop at one, or a sampled bound | Alternative · proposed |
| 3 | What the sampled jumps are made of: which structure makes start-03's 28,008 large groups | 2/3 — a reading of the natural kind | 1/3 — the bounds missed it; no candidate yet | list round 8's groups by the blocks they cross → stop at a structure that bounds round 9 above 28,065, or a reason none can | Alternative · proposed |
| 4 | A sampling estimate of the next round (random descent through the clique search, A110's sampling) | 2/3 | 2/3 | estimate start-03's round 9 with spread → stop at an estimate whose spread is under a factor of 10, or a reason the spread cannot shrink | Alternative · proposed |
| 5 | Prove the 2.3830 ceiling within five places | 2/3 | 2/3 | bound every branch system by the theta's → stop at a proof, or a start that beats it | Alternative · in the basket |

## Final report as sent (2026-11-19 21:08 UTC)

**Outcome:** Past the wall there is now one start read exactly, and it never ends. Its knots come in partner pairs, each able to join every knot but its partner. Every round keeps that form, and the counts run 6, 8, 10, 24, 4,086, then 2^2043 − 24, each about two to the power of half the one before. I'm calling that runaway growth. It's proved, and the machine check passed 4 of 4. It's also the proof that the wall is real: no reading by clusters of the unrolled map can keep up with it. On the smallest unread start itself the new reading is weak. That start, and the other 13, are still unread. Closed, referee pending.

- **What the growth is, past the wall.** Each round keeps the largest sets of knots that can all join one another and that no single knot meets. That makes it a clique operator, and the partnered start is the literature's octahedron case (Neumann-Lara, 1978), adapted to our rule. Our rule drops the joins a block holds, which is why each count subtracts the one from two rounds back.
- **Why no cluster reading can follow it.** Clusters of an unrolled map number at most exponentially many in their size. Runaway growth outruns any exponential, so the clusters would have to be as large as the previous round's whole count.
- **A part bounds the next round (proved).** Read any set of live knots exactly, and you get a lower bound on the next round. That's a first sampling inside one growth, as A110 asks. It never failed, on 6,033 stages in the proof check and 140 in the run.
- **But it reads the real starts weakly.** Two predictions failed.
  - **Start-03.** A compact engine took it one round further, to 28,065 junctions in round 8. The best bound on round 9 is 16,019; I'd predicted a million.
  - **The other 13 unread starts.** Each went one or two rounds further, jumping ×10 to ×650, up to 162,336 junctions. None merged, and the bound passed the last count built for 0 of them.
  - **What that shows.** Their jumps are made of large groups, but those groups aren't partnered or random-like. The structure making them is still unnamed.
- **Also checked.** Start-04's round 9 is 304,590 junctions, all pairs, as its block of 781 predicted. The compact engine matched the program's engine everywhere: 26,441 census starts, 995 random starts and both read starts.
- **One caveat.** The partnered start needs knots of eight places, one more than the explosive sample allowed.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a reading past the wall | **Status:** Partially successful (proof 4 of 4; run 4 of 6, B4 and B5 failed) | Partnered starts are read exactly past the wall and run away without end, and no cluster reading can follow them; on the 14 sampled starts the new bounds read weakly |
| Local direction: the explosive kind (A109) | Research directions | One member is read completely (runaway); the sampled ones jump through large groups that neither bound captures |
| Broader exploration: what the cheapest growth builds | Capability gained | The growth is a clique operator; whether it ends links to clique-divergence, which is open in general |
| Long-term goal: G17 | Capability gained | A blow-up that never ends, read exactly, and a way to bound one growth's next round from a part of it |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A retraction lemma: a stage whose blocks map onto a partnered stage runs away at least as fast | 3/3 | 2/3 | prove it for maps that send blocks into blocks → stop at a proof, or a start where it fails | Alternative · proposed |
| 2 | Does any start within seven places reach a partnered stage, or one that retracts onto it? | 3/3 | 2/3 | search the census and the explosive sample for partnered stages of order ≥ 3 with no outside common candidate → stop at one, or a sampled bound | Alternative · proposed |
| 3 | What makes start-03's 28,008 large groups | 2/3 | 1/3 | list round 8's groups by the blocks they cross → stop at a structure that bounds round 9 above 28,065, or a reason none can | Alternative · proposed |
| 4 | A sampling estimate of the next round (A110's sampling) | 2/3 | 2/3 | estimate start-03's round 9 with spread → stop at a spread under a factor of 10, or a reason it can't shrink | Alternative · proposed |
| 5 | Prove the 2.3830 ceiling within five places | 2/3 | 2/3 | bound every branch system by the theta's → stop at a proof, or a start that beats it | Alternative · in the basket |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained). **Assumptions:** A110 and A109 get history lines, both status unchanged; no new entry. **Basket:** `MERGE-BURST-20261119-001#1` taken and marked done; directions 1–4 added; the 2.3830 ceiling stays in the basket. **Advisor:** Fable 5.2, before the freeze, staying within its text. It confirmed the partnered proof and named four gaps, all closed. It narrowed the cluster obstruction to regular covers. It proposed the partnered bound and the words "partnered" and "runaway growth", and it tightened the predictions. One point of its came from my own misstatement of a density. Separately, the smoke test before the freeze caught a gap in the bound lemma (a knot that can join nothing), fixed before freezing. **Disclosed:** the objects-index search ran at close, not before the freeze; it found no earlier study of partnered starts or of part-of-a-stage bounds.

**Referee hand-off.** The decision note is `research/WALL-READ-20261119-001/wall_read.md`, the proof is `proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/proof.md`, and the run is `experiments/WALL-READ-20261119-001B/WALL-READ-20261119-001B-E001_past/`. The prior-work searches, run at close, are in the note's "Prior work in the program" section. Please check:
- Theorem 1's induction, the (F4) monotonicity and the round-1 base, and the eight-place minimum;
- Corollary 4's counting (regular covers, at most (eΔ)^(k−1) connected k-sets through a member);
- Lemma 2's lone-point term, and Lemma 3's disjointness of complementary groups;
- that `rosterlib` is the program's rule, including the implied clause;
- B2's post hoc double count, and the start-04 round-9 check.
