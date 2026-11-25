# The order in a knot's own places: definitions ("DH")

Epic `DESCENT-HELD-20261125-001`, 25 November 2026. Builds on the shared definitions ("SD",
[research/RING-IN-BALANCE-20261123-001/definitions.md](../RING-IN-BALANCE-20261123-001/definitions.md), cited by line), the
parents-from-holders pre-registration ("PH",
[research/PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md](../PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md)),
the least-record pre-registration ("LQ",
[research/LEAST-RECORD-20261124-001A/preregistration.md](../LEAST-RECORD-20261124-001A/preregistration.md)) and the fold
study's knot test ("FD 7",
[research/PARTS-MEET-AGAIN-20261124-001/definitions.md](../PARTS-MEET-AGAIN-20261124-001/definitions.md) lines 265-289).
Nothing in them is changed. The canonical K1-K3 test is unchanged. Every term is decided by a program from a run's
structures and its record. The note: [note.md](note.md).

## 0. Words

0.1 SD's words (lines 9-77): structure, place, holder, loose, shared, usable, barred, start, start knot, member, met set,
common knot, joinable, part, group, owing, short, join, offshoot, demand D, ration, treatment, release rule, extras, closing
exception, round. **New knot** is SD's word for a knot a birth makes. Two holders per distinction; no taking rule.

0.2 PH's and LQ's words: look within d, alike, confusable pair, parent place, not a parent place (a child place, or a place
between two start knots), holder step, holder-step distance, stamp, half-built structure, the condition (LQ lines 170-172).
"Mark": loose and usable, loose and barred, or shared.

0.3 **Parent steps** of a knot: 0 for a start knot; one more than the greatest of its parents' for a new knot. It is the
least-record study's "generation" (SD line 121; LQ line 37), quoted here once, computed from the record of parents.

0.4 **Count in threes**: a number's remainder on division by 3; "one more, counted in threes" means a difference of 1 modulo
3. "Mod" appears only inside formulas.

0.5 **Value** is kept for the stamp of A247 (a number written on a knot by whoever runs the growth). What this study puts in
a knot's places is its **count** (DH 2.1).

0.6 Words not used: "held" for this study's result; "hold" in any sense but a knot holding a distinction and HOLD;
"generation" outside the quotation of 0.3; "reads" in any sense but the owner's (a rule or a ration **uses** a count); a
"made" knot ("new knot"); "most" or "many" without a number.

## 1. Runs, starts and their record

1.1 **A run** is one start grown under one law and one knot law in complete rounds (SD steps 1-8), through R rounds or until
the first round after which the structure has more than N knots, or until a round changes nothing (no birth and no new barred
distinction) or stalls. This is the least-record study's reading (its `pfh_pop.py`, function `p3_lineage`: a run ends "at the
first round that changes nothing"); under retiring a round can make no birth and still bar distinctions. **Every run names
its knot law** (parity or not-all-equal); the knot law decides the closing exception (SD lines 63-66) and the knot test.

1.2 **An allowed start**: a finite structure of knots, each of at least three places, each distinction with one or two
holders, no distinction barred. Census starts are also connected, with at least one live knot. A structure **is an allowed
start up to renaming** when some renaming of its knots and distinctions, marks kept, makes it one. This statement is supplied
(DH 10); SD lines 11-18 imply it ("a loose distinction is usable unless the law has barred it") without stating it.

1.3 **The record of parents** is written by each birth (A242), with its round. It is the answer checked against; no law here
has it as an input, and no look shows it.

1.4 **The order of new knots** is the engine's (SD steps 4 and 5: groups in sorted order, then offshoots by member), which is
the order of `lr_core.own_round`. It names knots for the record only. A verdict that depends on it (such as the first
failing birth of a round) is reported as the round and the multiset of the births in question.

## 2. A knot's counts

2.1 Fixed at a knot's birth (for a start knot, at the start): its number of places n; for a new knot its number of parents p,
its demand D, its fresh distinctions f, so n = p + f; its number of places barred at birth z (FILLERS, and DH 3.2's barred
added distinctions; 0 for a start knot).

2.2 **Changing later**: the number of barred places b, which is z at birth and grows only when the knot retires
(CANCEL-RETIRE bars its usable loose places, SD lines 47-48), for start knots and new knots alike; and its numbers of loose and
shared places, which change with later births.

2.3 **Shown within d**: a function of a knot's look within d holder steps (PH lines 37-42) that is unchanged by every renaming
of knots and distinctions. n and b are shown within 0; the other holder's n and b within 1. p, f, D and parent steps are not
shown in general; written on a knot they are stamps. "Shown within d" is always written with its d, and a claim that a
function names the parents always names its population, the function being one function for the whole population.

## 3. The laws

3.1 **Arm R, the recorded laws**: [laws.json](../DESCENT-HELD-20261125-001A/laws.json), "recorded" (ten laws with RELEASE) and
"holding" (four with HOLD), each with what it adds by hand (A104, A224). Every ration there is a function of (p, D) alone (SD
lines 59-62). NO-OFFSHOOT is not used.

3.2 **Arm W, the laws that write the count.** For a base law B and a count form, B with SD step 7 changed as follows and
nothing else. For a new knot x with parents y_1..y_p:
  1. **The base count** F = F_B(p, D).
  2. **The parents' counts** κ(y_i), taken at the moment of the birth: for NEXT3-PLACES the number of places n(y_i); for
     NEXT3-BARRED the number of barred places b(y_i); counted in threes.
  3. **The target.** If every κ(y_i) is one count c, the target is c + 1 (mod 3). Otherwise x is **a birth whose parents
     differ**, counted. Registered rule: no target, s = 0. Swap: when exactly two different counts occur, there is exactly
     one c for which they are c and c + 1 (mod 3) (the order is cyclic, so "the greater" means c + 1 in this sense), and the
     target is c + 2; when three occur, no target.
  4. **The added count** s: the least of 0, 1, 2 that makes x's count the target: p + F + s for NEXT3-PLACES; z_F + s for
     NEXT3-BARRED, z_F being the number of F's distinctions FILLERS bars (0 without FILLERS).
  5. **A closing birth** (parity; SD lines 63-66: a new knot that takes every loose distinction of the structure): it
     receives nothing (F = 0, s = 0), as under B, and is counted; the place rule is not claimed at its places. Swap: it
     receives F_B(p, D) computed as if no closing exception applied, and s recomputed on that F; the structure then does not
     close. The swap keeps every new knot's count right and makes the closing birth fail the parity knot test (its taken
     places are forced even by the other knots, so its fresh places are forced too); it is reported, not claimed. Under
     not-all-equal there is no closing exception and step 5 does not act.
  6. **Usable or barred.** NEXT3-PLACES (usable): x receives F + s fresh distinctions, FILLERS (if in B) applying to all F + s
     (min(F + s, D) usable, the rest barred). NEXT3-PLACES (barred) and NEXT3-BARRED: x receives F as B gives them (FILLERS
     applying to these F) and s more, barred at birth.
  What each adds by hand: the parents' counts as inputs of the ration, the counting in threes, the target, the added
  distinctions and where they go. **Shortness is counted on usable places** (SD steps 2-3 with h(u) the usable loose count);
  an engine that imports a round must be checked on members holding barred places (SD lines 71-73 say the pilot's count of
  all loose places agrees only where barred holders act once, which fails here).

3.3 **NEXT5-BARRED** (a stated variant, not a registered law): counts in fives; the target is one more than the parent count c
for which every other parent count w has c − w in {0, 1, 2} (mod 5), and no target if there is none; the place rule says
"one or two less, counted in fives". It is the least-record study's counting in fives (its results, lines 71-75), moved here;
a greatest difference of d parent steps needs counting in 2d + 1.

3.4 **The brief's literal wording** (the fresh count one more, counted in threes, than the parent's) is not a law of this study:
the place rule would compare n while the law writes f, and n(x) − n(y) ≡ p(x) − p(y) + 1, so it is wrong at the place of every
offshoot of a start knot to its parent, from the offshoot's side.

## 4. The place rule, and the two meanings of "recovers"

4.1 **The place rule** for a count form: at a shared place a of knot x whose other holder is y, the prediction is "a parent
place" exactly when κ(y) is one less than κ(x), counted in threes; otherwise "not a parent place". It uses κ(x) and κ(y):
shown within 1.

4.2 **"The place rule is right on"** a structure: at every shared place the prediction is the place's kind. On a run: on the
structure after every round.

4.3 **"Recovers the parents"**, kept in LQ's sense only (arm R): a population has no confusable pair at distance d (PH lines
45-49). A renaming of a whole structure onto itself that exchanges a parent place with one that is not is a confusable pair
at every d. Where a structure has no such renaming, this text says so in those words ("has no renaming exchanging a parent
place with one that is not") and never that its order is recovered.

4.4 **A parent-closed part** of a run's structure after round t: a set of its knots that contains every start knot and, with
each knot, its parents. It is a construction: each knot with all its places as at the end of round t; a distinction with one
holder in the part loose there; barred marks as at the end of round t. It is not a half-built structure of a run made one
birth at a time (under ORD such a structure does not have D yet); LQ's half-built structures are such parts, up to renaming of
distinctions, wherever the one-birth-at-a-time run matched the rounds. The place rule's verdict at a place uses only the two
holders' counts, so it is the same on every part that contains both, where (c) holds.

4.5 **The conditions on a run**, each decided from the run's own record:
  - (a) **The start's counts agree**: every two start knots that meet have the same count in threes. For NEXT3-BARRED it holds
    by 1.2 (no start knot has a barred place).
  - (b′) **Parent steps agree in threes**: every birth's parents have numbers of parent steps that agree counted in threes.
    Reported beside it: (b) every birth's parents have equal parent steps; and LQ's condition (a start knot waits in a round
    in which a start knot it meets is a parent of a birth).
  - (c) **Fixed counts**: no knot's count changes after its birth (a start knot's, after the start) by a number not divisible
    by 3.
  - (d) **No closing birth that needs a count**: under parity, no closing birth at which s would be more than 0.

4.6 **The greatest difference** of a run: the greatest, over births and their parents, of the new knot's parent steps less the
parent's (1 where (b) holds). Reported by start and by round.

## 5. Arm R

5.1 **The lone-knot structure** of a ration F and a number a ≥ 3 with F(1, a − 1) = a − 1: the start of one knot of a places,
and the structure after its first offshoot in DH 1.4's order. The ten cases are in `laws.json`, "lone_knot_rations".

5.2 **The renaming that exchanges them**: a one-to-one renaming of the knots and distinctions of that structure, keeping every
mark and which places are one distinction, that exchanges the two knots and their loose distinctions and fixes the shared
distinction; the offshoot's place to its parent and the start knot's place to its child are exchanged. Found by search over
every renaming and checked place by place.

5.3 **The census verdict on places** (M2): grown round by round, "fails at round r" (with the multiset of the failing births'
kinds) at the first round with a birth whose n is not one more, counted in threes, than some parent's; "holds through R",
"holds on a finished structure" or "holds, cut at N knots" otherwise. **Reaches three parent steps**: some knot of the run
has parent steps 3 or more (a threshold chosen after the scratch run).

5.4 **The restart control**: the structure after round t of a run, handed in as a start (its record dropped; its stars in
its own order of knots and names of distinctions), grown under the same law for k more rounds, and compared with the run's
structure after round t + k in three stages: (1) equal names (the two lists of knots' places identical); (2) where (1) fails,
an exact test of isomorphism of knots and distinctions with marks, on structures of at most 300 knots; (3) where neither
applies, the signature of DH 8.2, labelled as a signature.

5.5 **The census's own restarts**: a census start C (kept under parity) is **reached within round 1** under a law when, for
some census start S of at most four knots (any of the 223, the kept and the set aside), the structure made of S and a prefix,
in DH 1.4's order, of S's round-1 new knots, with its marks, is an allowed start isomorphic to C (knots and distinctions, marks
kept). It is **reached after a complete round 1** when the prefix is all of round 1's new knots. Reported beside it: the same
with any subset of round 1's new knots in place of a prefix (every such subset is parent-closed, all parents being start knots).

## 6. Growth compared

6.1 Births by round, knots, how the run ended (SD lines 81-93).

6.2 **Same births**: for every round through the last both runs reached, the list of each new knot's parents in DH 1.4's
order is the same under B and under B with a count form.

6.3 **The cost**: the share of new knots with s > 0, and the mean of s.

6.4 **Returns with barred marks**: SD lines 85-88, sameness as SD line 29 with k counting every barred loose distinction. For
the first return found (least s, then least t): its period T; the renaming found that makes the returned part the same as
the part; and **q**, the number of parent steps by which that renaming moves each member (u to u′, q = parent steps of u′ less
those of u), defined when it is the same for every member, else reported "not common". **The period formula**, under the
hypotheses that q is common and that the part's members agree in parent steps counted in threes: under a barred count form
the least period with barred marks is T · 3 / gcd(3, q); without the hypotheses that number is an upper bound only.

## 7. The knot test

Every start knot and every new knot of the run's last structure, under the run's knot law: parity by FD 7's ranks and kernel
methods, which must agree; not-all-equal by FD 7's decomposed method (`nae_decomposed` of the fold study's `knots.py`, exact,
with no hypothesis on fresh distinctions). The knot test is made on every structure the runs make (at most 3,000 knots after
the last round; one more round can pass that bound once, and such a structure is tested as it is). The direct not-all-equal
method is used only as a check of the code, on knots of at most 7 places in structures of at most 150 knots. A census start
with a start knot that fails under parity is set aside under parity (32 of 3,380 starts of up to five knots, 284 of 82,656 at
six knots, scratch); under not-all-equal no start knot fails at up to five knots, so the population is all 3,380.

## 8. Numberings

8.1 A numbering of a start: an order of its knots and of its distinctions. Every numbering when the start has at most six
distinctions; else the 4n (the n shifts of the order of distinctions, each as given or reversed, knots as given or reversed)
and the registered 200 of [numberings_registered.json](../DESCENT-HELD-20261125-001A/numberings_registered.json).

8.2 The test: an exact isomorphism test (knots and distinctions with marks) between the run's last structure under a numbering
and under the numbering as given, on the starts of at most six distinctions; elsewhere the signature (births by round; the
multiset of (round of birth, parent steps, p, n, z, s, number of children, b) over knots; the place rule's counts by kind),
labelled as a signature. "Argued for every numbering; no difference found in N runs" is the only sentence a result may say.

## 9. The census and its weightings

9.1 The census of `COPYING-PARTS-20261123-001A` (its `cpcensus.py`, imported without change): connected graphs of networkx's
atlas on 1 to 5 vertices (and 6 for condition (a) and the sample of 9.3), a loose count 0 to 3 on each knot with degree plus
loose count at least 3 and at least one live knot, each kept once up to the graph's automorphisms; one shared distinction per
edge. 3,380 starts on 1 to 5 knots; 82,656 on 6.

9.2 **The census weighting**: each start counted once. **The labelled weighting** (the swap): each start weighted n!/|Aut|,
|Aut| the number of the graph's automorphisms that keep every loose count, that is, each numbering of the knots counted once.
The strata are unchanged by renaming, so the labelled shares are a reweighting of the same runs.

9.3 **The six-knot sample** for (b′): 3,000 starts of the 82,372 kept under parity, taken in the order of
`random.Random('DESCENT-HELD-20261125-001|six|v2')`'s shuffle of the list `0 .. 82,655` of census indices, skipping starts set
aside; a prefix of that order is itself a sample.

## 10. Supplied statements and scaffolds, with their swaps

- **Allowed start** (DH 1.2), swapped for: a start may carry barred places.
- The count form (places or barred places), swapped between the two.
- Where the added distinctions go (usable or barred), swapped between the two for NEXT3-PLACES.
- Counting in threes; fives as the stated variant of 3.3.
- The rule for a birth whose parents differ (none; one more than the cyclically greater of two).
- The closing reading (3.2 step 5; its swap, which fails the parity knot test).
- The stopping reading (1.1; the swap: end at the first round with no birth).
- The base laws; the starts; the two weightings; the bounds R and N; complete rounds (one birth at a time is not run).
