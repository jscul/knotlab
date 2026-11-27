# Reading a growth straight off its start: what stands

> **Referee report R2, 27 November 2026: confirmed with fixes — Block on the unconditional reduction and on the rank
> checker as a certificate; the conditional core theorem proved** ([the report](referee-R2/report.md)). Before reading the
> twin explanation, the referee drew 192 starts of its own weightings (all agree through round 8 under both laws) and
> built two new failing starts, of 10 and 16 knots, which fail under both laws at round 5: in both, two core births of one
> round share two parents and a common parent of those carries a chain base (chained twins), and removing one loose
> distinction that removes the twins restores agreement. It rebuilt all 834 completed start-and-law scores (830 agree).
> - **Block: the reduction holds only without chained twins.** "So the core's births are the round rule iterated on the
>   core alone" is false in general; the referee proved it on starts without chained twins (two induction properties of
>   the actual growth), and showed that at the first chained twins the parent roster always changes. The chain counting
>   and the fresh counts of mixed births remain unproved.
> - **Block: the rank checker certified nothing at the ends.** It compared ranks 1 to top − 1 only and returned success
>   on both obstructions after checking no transition. Repaired (rank 1 and the top now checked); the 127 and 112 starts
>   without a flag still hold, and both obstructions now fail.
> - **Narrowings.** Round 1 also has offshoots; the twin mechanism is a group {A, B, C′, D′} seen a round earlier on the
>   twins' own counts; the relay alternative failed on 33 starts, not 29; denominators are 417 completed rows (416
>   distinct, of 418); the reduction to the identification holds on accepted pieces without a cycle meeting all its
>   hypotheses. **Not a block:** two replay labels swapped; "every frozen prediction held" dates to the first test (H1
>   later failed at seven knots).

> **Referee report R1, 27 November 2026: refuted in part — Block on the statement to prove and on the order lemma as
> worded; every frozen prediction reproduced** ([the report](referee-R1/report.md)). The referee rebuilt all 358
> comparisons and both samples (175 distinct starts; the hash merged none) and blind-tested 55 eight-knot starts of its
> own weighting, where the flags classed every start correctly. Read this record with these changes.
> - **Block: the absence of both flags does not suffice.** An accepted 36-knot start (seven four-knot cells, one on each
>   triple of the literature's Fano plane, inside one block) has neither flag and fails at round 1 under both laws: the
>   reading's size counts a set's points less two for each whole cell it holds, which gives the whole set size 0 though
>   it contains seven sets of size 2, so the order is not graded by size. A 14-knot start fails the same way. The
>   statement to prove is withdrawn as written: a theorem must first justify the computed size on every cover.
> - **Block: the order lemma as worded is false.** Its second clause must use families maximal among all pairwise
>   parent-sharing families (on one block of four, 123, 124 and 134 share parents pairwise, yet the growth's birth 1234
>   also has parent 234); the first clause needs rank two at least. The obligation is to compare the whole parent roster
>   at each rank.
> - **Narrowings.** A split pair keeps two parents out of one join; how many joins they enter depends on the roster.
>   The cell clause describes one overlap (other overlaps lose the cells differently). Denominators: 352 fresh law
>   comparisons in all, 40 starts with a split pair in the first weighting, closings in rounds 3 to 13; the hand-built
>   start's small knots have four places.

Epic `GRADED-ORDER-20261126-001` (G17 with G1; at the coordinator's pick, the advisor's direction 2 and the late-views
study's direction 2; register entry A301), closed 27 November 2026. Computed, frozen with the advisor's review before
any fresh start was grown; referee pending. [The note](README.md)

## What stands

1. **The exception is a split pair (computed, frozen).** The late-views study's graded-order reading (a start's valid
   sets ordered by inclusion; a birth's parents the sets it covers, its fresh distinctions the sets covering it) reads
   every round of every fresh seven-knot start in which no valid set has two parents that share no parent and no two
   group cells share two knots: 127 starts of two weightings, 254 start-and-law cases, both knot laws, both readings.
   It fails on every start with either (49 fresh starts and three replays), first at round 1 or 2. Both flags are read
   off the start without growing.
2. **The first form of the exception was a special case.** "Two blocks meeting a cell in two common knots" (the route
   cycle, found by hand on the eight-knot miss) misses the six fresh starts and the eight-knot replay with two cells
   sharing one knot, on which the split pair alone predicts the failure; all seven fail. *(Labels corrected after
   referee R2: the hand-built start with four mutually meeting knots has the route-cycle flag.)*
3. **A statement to prove** (written, not proved): in the predictor's class, with no split pair and no two cells
   sharing two knots, the births are exactly the valid sets of the graded order. A proof needs Lemma R (proved) and an
   order lemma: any two parents of a valid set share a parent, and every set of births that pairwise share a parent and
   lies in no one parent's children is the parent set of exactly one valid set.

4. **The node reading (added after the referee, held-out test frozen).** Build the start's core births by Lemma R's round
   rule from the round-1 groups, each birth a node, then count chains and the relay as before. It reads every round of
   238 of 239 held-out starts of a new seed under both laws (all 116 eight-knot ones, one size past) and seven of the
   referee's eight constructed starts (one a graded-order agreement control; the 30-knot one timed out and is
   unresolved); its two misses in 417 completed sample rows (416 distinct, of 418 attempted; a separate eight-knot
   replay passed the 200,000-birth cap) are exactly the starts where two core births share two parents with a chain at a
   common grandparent (post hoc; referee R2 then built two more such starts, both failing).
5. **Proved and computed.** Lemma R gives the round rule (proved); births along chains never change a core group except
   at such twins (proved by referee R2's repaired induction, which replaces the first argument), and at the first such
   twins the parent roster always changes (R2); the chain counting, the fresh counts of mixed births and the relay on
   node cores with chains are computed (R2 proved the relay's birth for finished pieces without chains). On the
   accepted pieces without a cycle that meet all the identification's hypotheses the node reading is the refereed
   identification (`DOUBLE-IDENT`; `NAE-GROWTH-20261119-001Z` for a lone finished piece under not-all-equal).

**Not shown.** The chain counting on node cores as a theorem; a fresh test of the twin exception; pieces with a cycle.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the graded order on fresh starts | **Status:** Successful | Every frozen prediction of the first test held; the exception is stated and read off the start (the later held-out H1 failed at seven knots) |
| Local direction — a reading of the growth from the start alone | Continue | The statement to prove is written; the split-pair starts need births counted per pairwise-sharing set |
| Broader exploration — what a local reader keeps of a start | Capability gained | Which starts the reading covers is now decided before growing |
| Long-term goal — G17 with G1 | Capability gained | The late view of every start without a split pair is read without growing, on the samples |

**Next step:** Continue — #1 proposed; the choice is the coordinator's

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the order lemma for the class without split pairs | 3/3 — turns 705 of 706 into a theorem | 2/3 — Lemma R in hand, the lemma stated | Write the induction on rank with Lemma R item 3 → a proof, or the case where the lemma fails | Proposed |
| 2 | Read split-pair starts: one birth per set of births that pairwise share a parent | 2/3 — removes the exception | 3/3 — the 52 failing cases are listed | Count the cliques of the covering relation at each rank instead of the valid sets; test on the 52 → every round, or the next exception | Proposed |
| 3 | Pieces with a cycle | 2/3 — completes coverage | 2/3 — `RING-IDENT`'s orbits | The late-views study's direction 3 | Proposed |

**Corrections:** two entries in `docs/CORRECTIONS.md` after the referees: R1 (two Blocks: the statement to prove and the order lemma as worded) and R2 (two Blocks: the unconditional reduction and the rank checker as a certificate; five narrowings; one Not a block).
**Goals:** checkpoint row added (G17 with G1; capability gained).
**Assumptions:** A301 entered (the two weightings, the buckets up to renaming, the horizon).
**Scaffolds:** two weightings (`tree+` and `grow`), the seed and buckets, the horizon, repeats removed by a hash; the
result holds under both weightings and both laws, so it is about the reading, with the hash's merging the only
unchecked choice.
**Advisor:** consulted before the freeze: its split pair, the cell clause, its eight-knot start and the warning about
repeats were taken; all were confirmed by the run.
