# The grown ring's bond: what stands


> **Referee R1: refuted, one Block** ([report](referee-R1/report.md)). Every ring count, the symmetry results, the
> knot checks, the collapse check and the census tallies reproduce. **Block:** bonds do bind again one layer up. On a
> closed start of twelve three-place knots (every distinction held twice, no growth), six agreements on disjoint
> carriers of three, A0, A1, B0, B1, C0 and C1, are bound by eight lower bonds: no choice of one A, one B and one C
> agrees on all three. The three upper readings [A0 = A1], [B0 = B1] and [C0 = C1] then take seven of eight words,
> missing "all three disagree". Every pair is free, removing any lower bond or any one of the twelve knots restores the
> word, and no lower bond reads an upper reading. On the grown ring at round 3 an eight-bond example exists with
> overlapping lower carriers, and removing either round-3 birth's law restores the word. At least eight lower bonds are
> needed, so clusters of at most three could not have found one. Replayed by the thread (`post/upper_replay.py`:
> 7,570 states, seven upper words, every source law essential). **Narrowings:** the exact joint image holds on 24 of 24
> disjoint clusters but 0 of 70 overlapping ones. Bonds recur under the stated carrier and local-holder tests. Strict
> controls (each carrier meeting each knot at most once, or each reading open after every single-knot fixing) leave 2
> and 0 sampled bonds. Disconnected holders raise the starts with a bond before growth from 408 to 606. Padding:
> 811 of 9,524 source bonds lose a place keeping an admissible bond. The four-place swap is 636 bonds, 225 with a
> carrier of four. The parity holder check kept only the first shortest holder, giving 126 more bonds under the
> existential definition, and 811 of 1,000 starts have a bond. Within the three-valued scheme the reference is
> selected: one of 105 choices of reference and pairing works, and it is the stage's only loose distinction. Credit:
> the four-law witness and its three choices are the earlier referee's.
`RING-BOND-20261127-001`. Frozen in commit 8df7206b94. Results are in `out/`, tallied in `out/tally.json`. Post-hoc
checks, marked as such, are in `post/`. Referee pending.

A **bond** is three agreement readings on disjoint carriers of two or three distinctions (`README.md`, "Definitions").
No knot reads any of them, every two take all four pairs of values, and the three together miss at least one triple.
"Held by the whole" means every law of its holders is essential.

## Answers in parts

**(1) Chosen or selected: the choice is ours, a scaffold.** All six renamings of the ring's three knots map every
stage onto itself through round 5 (P1.1, held). Bonds map to bonds, and the three round-1 bonds with every law
essential are one orbit of three (P1.2, held). Relabelled starts grow isomorphic stages through round 5 (P1.3, held).
No later birth holds a start distinction, so this holds at every round. Nothing read off the growth can single out one
of the three: proved for this ring.

P1.2's last clause failed. At round 3, 16 bonds are fixed by the six renamings. They lie on the born part, a chain of
three knots that the renamings leave alone. Under the stage's own symmetry (48 renamings at round 3, post hoc) no bond
of rounds 1 to 3 is fixed, and the smallest orbit has three. So every bond read here is one of several equivalent
choices.

What the growth does hold without a choice is a three-valued relation (P1.4, held: the advisor's prediction, and mine).
Read each opposite pair (1,5), (2,3), (0,4) as apart, agreeing with 6, or agreeing against 6:
- the triples take 16 of 27 values, and 19 with the birth's law removed;
- removing any one of the four laws adds triples (20, 20, 20, 19), so every law is essential;
- every two of the three readings take all nine pairs;
- every renaming leaves the relation unchanged.

So it passes K1 to K3 as a three-valued relation. Each of the three bonds is a two-valued reading of it, for example
[0 = 4 = 6] is "the pair (0,4) agrees with 6". The model is expected to replace the scaffold (the choice of one bond)
by such a relation. The reading scheme is our choice; within it the reference is selected [R1: 1 of 105 choices of reference and pairing works, and it is the stage's only loose distinction, 6].

**(2) The knot test: passed, and no reading is read at a knot.** The knot checker passes each round-1 bond's clause in
every contact role (9 of 9, P2.1). The birth's law is essential in all nine round-1 bonds; the start alone has none
(P2.2). The collapse rule (merge agreeing carriers, separate disagreeing pairs, add a not-all-equal law on disagreeing
triples, ask a solver) agrees with the search on every bond checked (P2.3):
- the ring, 9,541 bonds;
- census starts 0 to 199 under not-all-equal, 17,059 bonds;
- under parity, 9,384 bonds on census starts 0 to 5. The run was stopped there to close the study; starts 6 to 199 are
  not run.

So each bond is the laws read through agreements, a case split. Readings read at a single knot are excluded by
definition. [R1: the search prefilters readings read at a knot; 53 of 210 disjoint carrier triples on the round-1 ring pass the image test but fail it.]

Post hoc: **bonds need no ring and no growth.** A chain of three three-place knots, (0,1,2), (2,3,4), (4,5,6), holds
16 bonds with all three laws essential, for example [0 = 3], [1 = 5], [2 = 4 = 6] missing 001. On 40.8% of the sampled
census starts there is a bond before any growth (below). On the ring, growth matters because its six distinctions hold
none; the birth supplies a seventh distinction and a fourth law.

**(3) Iteration: the bonds repeat; binding one layer up was not found.**

| Ring, round | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- | --- |
| bonds (full search) | 0 | 9 | 411 | 9,121 | 44,483 | not run (27 distinctions) |
| with every law of the stage essential | 0 | 3 | 144 | 234 | 0 | not run |
| with a newest birth essential | | 9 | 330 | 5,974 | 17,444 | |
| bonds held by ≤ 4 knots (local search) | | 9 | | | 473 (306 with a newest birth) | 803 (330) |
| readings in two or more bonds | 0 | 6 | 91 | 330 | 1,060 | |

Results against the predictions:
- P3.1 held (the advisor's): the 234 every-law bonds of round 3 all have three carriers of three and miss 111. None at
  round 4, as Seymour's count (laws at least as many as merged distinctions) requires.
- P3.2 failed narrowly. All bonds of rounds 1 and 2 are kept, but 14 of round 3's 9,121 are lost at round 4. Each holds
  the pair [9 = 11], and the round-4 join birth (9, 11, 13, 14) holds both, so that knot reads it. The relation itself
  persists.
- P3.3 held, and so did P3.4 (the advisor's).
- Every bond on the ring misses exactly one triple, and so does every bond under the swaps:
  - all readings unchanged by a global flip: 9 bonds at round 1 and 5,556 at round 2;
  - carriers up to four, round 2: [R1: 636 bonds, 225 with a carrier of four, all missing one word; the archived swap read only three places of each four-place carrier.]

The layer above found no bond in what it could read (P3.5, held):
- with disjoint carriers, round 1 has no cluster, and round 2 has 24 (6 of them of three bonds), none holding a bond of
  the layer above;
- with overlap allowed, round 1 has 70 clusters and none holds one; round 2 was cut at its 30-minute stop: not run.

This "none" could hardly have failed, given so few clusters. On 18 of the 24 round-2 clusters, the readings' joint image
is smaller than their bonds allow (P3.6). Post hoc, every one of those is explained by other bonds on the same readings.
[R1: all bonds on the same readings give the exact image on 24 of 24 disjoint round-2 clusters and 0 of 70 overlapping round-1 clusters.] So on the disjoint clusters read, the bonds together present the readings' joint image exactly, like the laws of a system of
their own, but they bind nothing further.

Census, 1,000 held-out starts, not-all-equal, holders ≤ 4 (P3.7):
- (a) held: 408 have a bond at round 0, 9,524 bonds in all.
- (b) held: 433 of the 730 funded starts have a round-1 bond with a birth among its holders (23,760 such bonds); 480
  have readings shared by two bonds.
- (c) held: the count bound holds on every bond.
- (d) failed: census start 477 is four three-place knots holding every distinction twice. Two of its bonds, on three
  pairs, miss two triples each: "if the first pair disagrees, the other two agree or disagree together".

The holder-cap swap (five holders, every tenth sampled start, 100 starts) found 6,153 bonds against 4,867. One stage of
175 gains its first bond at five. The existence result is not about the cap.

**(4) Parity: bonds are sums of laws read through agreements.** The capped run read 179 of the 1,000 starts; 821 are
not run.
- P4.1 held (the advisor's): every bond has a sum of its holders' laws holding exactly two distinctions of each carrier.
- P4.2 held: 111 is never missing.
- P4.3 failed: 24 bonds of shape 223 miss four triples, where two was predicted, and 188 of shape 233 miss two, where one
  or three was predicted. The advisor's shape rule had already failed on the pilot.
- P4.4 held: the ring under parity grows one round and has no bond.

Proved (`README.md`): under parity, which triples occur is fixed by the linear dependences among the carriers' pair
sums, and those dependences are sums of the laws. [R1: the complete set of dependences among the carrier differences determines the image; a dependence using one pair from each carrier is necessary within the carrier cap, but one such sum need not determine the image, and the laws may include births.]
Bonds are common under parity: 125 of 179 starts have one at round 0.

## On the owner's rungs

- **Repetition: met, in a new form** [R1: under the stated carrier and local-holder tests; 177 of the 9,524 sampled bonds before growth need every stage law; strict carrier controls leave 2 and 0]. A relation held by the whole and by no part (every holder's law essential, no knot
  reading any of its readings) recurs: at every round of the ring; on 40.8% of sampled starts before growth; on 59% of
  funded starts after one round, with a birth among the holders. The readings are not facts the whole keeps: a single
  change flips them (the earlier referee).
- **The tower's next step** (bonds binding again one layer up): [R1, Block: reached, on a chosen closed twelve-knot start with disjoint carriers and on the grown ring at round 3 with overlapping carriers, where a birth's law is essential; with six disjoint carriers after growth, and selection by growth, open.] ~~not shown.~~ On every cluster read, the bonds present
  their readings' joint image like laws, but no cluster holds a bond of its own. The clusters are few.
- **Recursion:** not shown.

## Intuitions (links, not evidence)

- **Not-all-equal read against a reference is "or".** The bond is a clause on agreements, and the three-valued relation
  reads each pair against the fresh distinction 6. That is the textbook equivalence of not-all-equal problems with
  ordinary clause problems: adding one shared distinction z turns a clause into a not-all-equal law, and reading
  everything relative to z turns it back (Schaefer 1978). Here growth supplies the z. Cheapest test: on sampled starts,
  check whether every bond is a reading, against some one distinction, of a choice-free many-valued relation.
- **Why the every-law bonds stop.** A not-all-equal system with no state in which every law is needed has at least as
  many laws as distinctions (Seymour 1974). Merging carriers can reduce the distinctions by at most six, so when
  distinctions minus knots passes six, no bond can need every law of the stage. The ring passes six at round 4.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the grown ring's bond | **Status:** STOP on its four questions (P1.1, P1.3, P1.4, P2.1 to P2.3, P3.1, P3.3 to P3.5 [R1: P3.3 and P3.4 at the tested rounds; P3.5 only for the strict search and round-1 overlap], P3.7 a to c, P4.1, P4.2 and P4.4 held; P1.2's last clause, P3.2, P3.7 d and P4.3 failed) | The choice is ours, a three-valued relation needs none; bonds pass the knot test and repeat everywhere, including before growth; nothing binds one layer up on the clusters read; under parity bonds are sums of laws |
| Local direction: a second layer of facts | Open | [R1, Block: eight full-stage agreement bonds bind again on a closed twelve-knot start with disjoint carriers and on the grown ring with overlap; the ring search admitted at most three lower bonds.] ~~Under not-all-equal, bonds are a first-layer phenomenon of agreement readings; the layer above needs clusters on disjoint carriers, which the ring barely has~~ |
| Long-term goal: G17 with G18 | Narrowed | Facts held by the whole exist under both laws (sums of laws under parity, case splits under not-all-equal); a second binding is not shown under either |

**Next step:** Continue with direction 1 (the coordinator's call; the law between parity and not-all-equal waits for the
owner).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The layer above at a scale where it can fail: starts built or sampled with many bonds on disjoint carriers (long chains, several rings), clusters of up to six bonds, bonds as laws | 3/3 | 2/3 | Time a chain of nine knots grown two rounds; search clusters of four to six → a bond of the layer above, or none on a stated class | Proposed |
| 2 | Choice-free relations: is every bond a two-valued reading of a many-valued relation against one reference distinction, on sampled starts? | 2/3 | 2/3 | The 408 census starts with round-0 bonds: group bonds into orbits of readings against each distinction → all, or a counterexample | Proposed |
| 3 | What growth un-makes: join births that make a carrier read at a knot (the 14 lost at round 4) as growth's only selection among bonds | 2/3 | 3/3 | Count lost bonds by birth kind on the census at round 2 → a rule, or none | Proposed |

**Corrections:** none. Two published sentences need wording after the referee: lesson 12.3's not-all-equal paragraph and
its table row frame the bond as grown, and they should add that bonds occur before growth on 40.8% of sampled starts.
**Goals:** checkpoint row added (G17, G18).
**Assumptions:** A308 (scaffold: the reading class, the two holder notions, bonds as laws, the census sample) added.
**Scaffolds:** the reading class (swapped: same answers on the ring), the carrier cap (swapped: same), the holder cap
(swapped: one stage of 175 differs), bonds as laws with disjoint carriers (swapped for overlap at round 1: same; round 2
not run). Each result above is about the model, except the choice of one bond, which is ours.
**Advisor:** consulted before the freeze (hivemind 2026-11-27). Its (1) held, and so did its Seymour bound, its 333/111
round-3 shape and its parity six-sum and 111 rules. Its parity shape rule failed. Its census 21 prediction (a
disconnected essential set) was not tested.
