# One birth at a time from what is built: definitions

Epic `LOCAL-ROUND-20261123-001` (sub-goal B323; goals G5 with G18). Frozen on 2026-11-24 with the pre-registration of
ticket A, before any of the study's code is written. It extends [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md)
of `RING-IN-BALANCE-20261123-001` and changes nothing in them. "The definitions" below means that file, cited by line. Words
are the glossary's and the definitions'.

- **Member, met set, common knot, joinable, part, short, waits, retires, live, dead, usable, barred, start** keep exactly
  their meaning there.
- **Member, short, waits and retires** are also used of the start roster, of a brood's roster at birth and of the waiters'
  roster, each with holdings h₀. They mean there what the definitions mean of the live roster with holdings h. A **part** of
  any of these rosters is a connected component of its joinable relation (definitions line 27).
- A roster is always named by its kind: the start roster, a brood's roster at birth, the waiters' roster, the present roster
  (the definitions' live roster as it now is), the reference's roster.
- "Jams" keeps only the definitions' sense (lines 84–85, 125).
- New here, each defined where it first appears: **weaned**, **brood**, **all-weaned**, **all-short**, **status**, a member's
  **acting roster**, **waiters' roster**, a **barring**, **allows**, **cutoff**, **matches through round r**,
  **underbuilds**, the **extent** of a brood from a knot, **x-last order**, **untouched**.

The text was drafted by the helper agent that surveyed the record and wrote a scratch prototype of these laws. The prototype
is not the study's engine. What it showed is disclosed in the pre-registration, under "Known before the freeze".

## 1. What is read from the structure

### 1.1 Parents, children, places, holder-step distance

- **Parents.** Every birth writes, with the new knot, the set of knots it took a distinction from: its **parents**
  (definitions steps 4–5: a join's parents are its group, an offshoot's its one member). The **children** of a knot are the
  knots that have it among their parents. A start knot has no parents and is the child of none.
  - The parent relation is not a reading of the holders: a shared distinction has two holders and no order (definitions
    lines 11–13, 76). It is written by the birth, as the record's birth-by-birth law already reads it (definitions line 111).
    See section 5.
- **Places, loose, usable, barred, h(u), k(u), member, live, dead**: as the definitions, lines 11–24.
- **Holdings at birth.** For a knot x with parents, **h₀(x)** is its number of places less its number of parents. Each
  parent gave one distinction; the others x received at birth, whatever they are now: loose, barred, or shared with a child.
  For a start knot, h₀(x) is its number of places not shared with another start knot.
- **Holder-step distance.** One holder step crosses a shared distinction from one holder to the other
  ([SERIAL-REPAIRS](../SERIAL-REPAIRS-20261120-001/local_rule.md) line 7). The **holder-step distance** between two knots is
  the least number of holder steps between them.
- A rule **reads to holder-step distance d** from a knot when its decision is the same for any two structures that agree on
  every knot within holder-step distance d of it. Agreeing means: their places, which of those are loose, usable or
  barred, and their parent sets and children, together with the closing bit of section 2.4.

### 1.2 The start roster (what plays the part of parents for start knots)

The **start roster** has as members the start knots with h₀ ≥ 1, each with holding h₀. Its met sets are, for each start
knot, the set of start members it meets, when it has at least two. Any start knot may be a common knot here, a member
included, as in definitions step 1. It is the roster the first complete round reads; it never changes.

### 1.3 Weaned

A knot is **weaned** when none of its parents is a member of the present roster: its parents have finished giving. Every
start knot is weaned.

### 1.4 The brood

- The **brood** of a knot x with parents is the smallest set B containing x such that, for every knot in B and every parent
  of it, all children of that parent are in B. The **parents of the brood** are the parents of its knots. Knots of B that
  have since made births, retired or died stay in B.
- **A brood's roster at birth** has as members the knots of B with h₀ ≥ 1, each with holding h₀. Its met sets are, for each
  parent p of the brood, the members that are children of p, when there are at least two.
- A brood is **all-weaned** when every knot in it is weaned.
- **Why this set** (an argument for the referee, not a definition).
  - Under RELEASE a member that makes any birth spends every usable distinction in the one roster in which it acts. So all
    children of a parent are born in one complete round.
  - Past the start, a knot meets only its parents and its children, and a waiter meets only its parents. So a waiter is
    joinable only with brood-mates that still wait.
  - Hence an all-weaned brood's roster at birth is exactly the part the complete rounds read in the round after its births, with
    the holdings it had then. Its waiters' rosters (section 2.1, step 5) are the parts the complete rounds read in the
    rounds after that.

## 2. Plans, and how a birth is made

### 2.1 The plan of a roster

A **roster** here is a set of members, a holding for each, and a family of met sets. Its **plan** is read as follows.

1. **Groups and owing.** As definitions steps 1–2 (lines 36–40), with the roster's holdings.
2. **Treatment.**
   - STALL: if a member is short, the plan **stalls** and has no births.
   - CANCEL-OFFSHOOT: a short member's births are one offshoot from each of its holdings.
   - CANCEL-RETIRE: a short member **retires** in this plan.
   - CANCEL-WAIT: a short member **waits** in this plan.
3. **Births of the plan.** Every group containing a short member is cancelled. Each kept group is one planned join. Each
   member that is not short has as many planned offshoots as its holding less its kept groups (RELEASE).
4. **Fresh count of a planned birth with p parents.**
   - FLOOR1 and RATION-3: as definitions step 7, line 62.
   - ORD: f = max(D, 3 − p, 1). D is the number of groups containing the birth in a roster whose members are the plan's
     births, each with holding 1, and whose met sets are, for each member of the plan's roster, the births it is a parent
     of, when there are at least two. Under STALL no member keeps anything, so no old member enters this roster, and D is
     the birth's owing in the next roster.
   - The closing exception is not applied here (section 2.4).
5. **Waiters' recursion** (CANCEL-WAIT only).
   - The **waiters' roster** of a roster has as members its waiters, with holdings unchanged. Its met sets are the roster's
     met sets intersected with the waiters, kept when they have at least two.
   - Each part of the waiters' roster is read a second time by steps 1 to 5, and its own waiters' roster after that.
   - A part of any roster all of whose members are short is **all-short**: its members wait for ever and make no births. The
     recursion stops there.
   - A member's **acting roster** is the first roster of this sequence in which it is not short.
   - A waiter reads a second time against the waiters of its roster only, never against new knots. Past the start this is
     what the complete rounds read, by section 1.4.
6. **Status.** A member's **planned births** are the births of its acting roster that have it among their parents, with
   multiplicity. Its **status** is one of:
   - "acts", with those births;
   - "retires";
   - "its plan stalls";
   - "is in an all-short part".

### 2.2 Which roster a member reads

- **Start clause.** A start knot reads the start roster (section 1.2), at every moment. The start clause is exact only when
  no start knot that acts meets a start knot that waits.
  - On the start-clause counterexample of the pre-registration two readings are wrong. The waiter (knot 0) reads a waiters' roster of
    itself alone. And the brood's roster at birth of the children of knots 1–3 omits knot 0, which the complete rounds put
    in their part in round 2.
  - Ring(5, 3) satisfies the condition: no start knot is short there.
- Every other member reads its brood's roster at birth (section 1.4).

### 2.3 Births already made

- A planned join with parents G is **made** when some knot has exactly the parents G.
- A member's planned offshoots are made, up to their number, by its children that have it as their only parent.
- The **remaining births** of a plan are, for each planned join and for each member's planned offshoots, those planned less
  those made. When more births of one kind have been made than the plan now gives, none of that kind remains. Where the plan
  read is the complete rounds' own (R2 and R3, and T(d) for d at least the brood's extent), this happens only after a
  mismatch (section 4).

### 2.4 Making a birth, retiring, stalling, the closing bit

1. A law **allows** a birth: a parent set B, each of whose knots holds a usable loose distinction, with the fresh count f of
   the plan it is read from.
2. The new knot takes one usable loose distinction from each knot of B; which one makes no difference up to renaming
   (definitions lines 76–77). It receives f fresh distinctions, all usable (FILLERS is not used here). Its parents are B.
3. **The closing bit** (parity, every ration). If, after taking, no loose distinction is left in the structure (usable or
   barred), the new knot receives none.
   - It is read on the present structure. This is a reading: the definitions' exception (lines 63–66) concerns a round's
     only birth.
   - That the two agree on these laws is argued, not proved here. Every non-closing birth receives at least one fresh
     distinction, and a barred distinction stays loose, so a part never runs out of loose distinctions except at a closing
     birth.
   - Every run counts each firing and whether the reference knot matched to that birth received none.
4. **Retiring.** When a member's status is "retires" and the law allows it (with the same guard as its births), all its usable
   loose distinctions are barred.
   - This is a **barring**. It is not a birth and not a move, since it adds no knot (glossary, "Move").
   - It is made as soon as it is allowed, before the next birth.
5. **Stall.** Under STALL the stall is read from the start roster only: if the start roster's plan stalls, no birth is
   allowed anywhere, and the growth has stalled.
   - This is enough under (ORD, STALL). There a new knot receives f ≥ D, its owing in the next roster (step 4 of section
     2.1). So no member of any later roster is short.
   - A brood's roster at birth whose plan stalls would allow nothing; under ORD this cannot occur. The pre-registration's
     P12 is a check of this, true by construction.

**Orders.** An order of a law is a sequence of allowed births, each allowed at its moment, with every allowed barring
made before the next birth. No fairness, priority or weighting is assumed. The kinds of order the study searches are in
section 4.

## 3. The laws

**R0 · the record's birth-by-birth law.** As the definitions, lines 108–126: common knots ANY, order UNIFORM, and
BY-GENERATION as recorded. It is defined there only for RATION-3 or PRESENT-ORD, with WAIT or FIRST-COME. **Added here**, for
this study only:
- FLOOR1 gives f by p, as RATION-3 does in step 4.
- Under CANCEL-RETIRE a member read short retires at once (a barring).
- Under CANCEL-OFFSHOOT a member read short has an offshoot move from each usable loose distinction and no join move.
- Under ORD the law is PRESENT-ORD with FIRST-COME, as the record ran ROUND-FREE's law
  ([ticket C's readings](../../experiments/RING-IN-BALANCE-20261123-001C/RING-IN-BALANCE-20261123-001C-E001_no_round/deviations.md),
  item 18).

It reads the present roster: its parts, the open test and each member's present holdings.

**R1 · the birth's parents are weaned.**
1. Each member reads its status by sections 2.1–2.2 from the structure as it stands. A brood that is not all-weaned is read with
   the children its parents have so far.
2. A remaining birth B is allowed when every knot of B is weaned.
3. A barring of x is allowed when x is weaned.

The guard reads to holder-step distance 1. How far the reading of a status must go is what T(d) measures.

**R2 · the parents' brood-mates are weaned too.** As R1, but a remaining birth B, or a barring of x, is allowed when
every knot of B (or x) is weaned, and so is every knot sharing a parent with it, that is, every child of each of its parents.
The guard reads to holder-step distance 3.

**R3 · the brood is all-weaned.** As R1, but a remaining birth B, or a barring, is allowed when the brood containing the
knots of B (or the knot barred) is all-weaned. All knots of a remaining birth lie in one brood, since joinable knots share a parent. A birth of start
knots is always allowed, since the start roster has no parents. R3 reads all of the brood. On D2(n, 3) the brood of the
start's births has 2n knots, and its extent from any of them is about n holder steps.

**T(d) · R3's reading within holder-step distance d** (d = 2 to 10). For a proposed birth with parent set B, let W be the
knots within holder-step distance d of some knot of B. Only knots of W are read. A knot of W whose parents or children lie
outside W is read without them: they give it no met set, no member and no guard. The one exception is h₀, which a knot of W
carries itself (its places and the number of its parents), so h₀ is read exactly even at the boundary.
1. **The brood within d** of B is the smallest set containing B such that, for every knot in it and every parent p of it
   that lies in W, every child of p in W is in the set.
2. **Its roster at birth** has as members the knots of the brood within d with h₀ ≥ 1, holdings h₀. Its met sets are, for
   each parent p in W of a knot of the brood within d, the members that are children of p, when there are at least two.
   - If every knot of B is a start knot, read instead the start roster within W: its members in W, and, for each start knot
     in W, the start members in W that it meets, when at least two.
   - A B that mixes start knots and other knots is never allowed.
3. **The plan** of that roster is read by section 2.1, with the waiters' recursion. Made births are subtracted by section
   2.3; the children of B's knots are one holder step from B, so they lie in W.
4. **Allowing.** B is allowed when it is a remaining birth of that plan, with the plan's fresh count, and every knot of the
   brood within d is weaned as read in W (none of its parents in W is a member).
   - A barring of x is allowed when x's status in the reading around x alone is "retires", under the same guard.
5. **Candidates.** The candidates are every member alone, and every remaining join of the reading around one of its
   members. Each candidate is tested in the reading around its own parent set.

The **extent** of a brood from a knot of it is the greatest holder-step distance from that knot to a knot of the brood or a
parent of the brood. When W contains a brood and all its parents, as it does when d is at least the brood's extent from
every knot of B, T(d) reads that brood as R3 does.

**R3L · the present part** (the working idea as literally stated). Read the present roster (definitions step 1, ANY) and its
parts.
1. A part in which no member has a child and every member is weaned is **untouched**. Its plan is the plan of the part
   with present holdings h(u) and present met sets. Its remaining births and barrings are allowed.
2. In a part in which some member has a child, each member reads its status by section 2.2 (the start roster, or its brood's
   roster at birth). Its remaining births and barrings are allowed with no guard.
3. Any other part allows nothing.

R3L reads the whole present part.

**Control · the depth guard, originals supplied.** This is the record's guard, with this study's round in place of the
ordinary operator: [SERIAL-REPAIRS](../SERIAL-REPAIRS-20261120-001/present_proof.md) lines 41–43;
[cohort.py](../../experiments/SERIAL-REPAIRS-20261120-001A/SERIAL-REPAIRS-20261120-001A-E001_repairs/cohort.py) lines 28–81.
The originals are supplied as in
[the clock study's replay.py](../../experiments/TICK-BIRTHS-AND-SCARCITY-20261121-001B/TICK-BIRTHS-AND-SCARCITY-20261121-001B-E001_serial/replay.py)
lines 66–116.
1. The originals are the start knots. The **depth** of a knot is its holder-step distance to the nearest start knot.
2. Let k be the least depth of a member. The **layer** is every knot of depth k, members or not.
3. Holdings: at k = 0, the start holdings; otherwise each layer knot's places not shared with a knot of depth k − 1.
4. The layer's roster has as members the layer knots with holding at least 1. Its met sets are the start roster's at
   k = 0; otherwise, for each knot of depth k − 1, the layer's members it meets, when at least two.
5. The plan is section 2.1, steps 1–4, **without** the waiters' recursion: a waiter is given nothing to do.
6. The layer's children are the knots of depth k + 1, each with its neighbours of depth k as parents. Subtract them (section
   2.3), allow the remaining births, and make barrings as section 2.4.

The control reads the whole structure.

## 4. The comparison

- **Reference.** The reference is ticket A's engine of the earlier study
  ([engine.py](../../experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py),
  `round_step`). It is run on the same start under the same law through a last round R. Each reference knot has a round of
  birth.
- **Gate.** Before any search, the new engine's own complete rounds are checked against the reference structure by
  structure. The test is exact isomorphism of the incidence structure of knots and distinctions after each round, rounds 1
  to R, knots coloured by round of birth and distinctions by barred or not, for every start and law. A failure stops the
  searches until it is resolved and recorded.
- **The last round R** is the least round such that every knot born by round r (the cutoff below), in the reference's roster
  after round R, is either no member or a member of a part all of whose members are short. Under CANCEL-WAIT such a part
  makes no birth in any later round. The reference's growth may also have stopped, stalled or jammed by then.
- **Match.** A run keeps a map m from its knots to reference knots, the identity on start knots.
  - A birth c with parents B and f fresh distinctions **matches** when the reference has a knot c′, not yet an image of m,
    whose parent set is m(B) and whose fresh count (places less parents) is f. Then m(c) is the least-numbered such c′.
  - A barring of x matches when m(x) holds barred distinctions in the reference and has no children there.
  - Anything else is a **mismatch**.
- **Cutoff.** A birth is **within round r** when the image of each of its parents was born by round r. In the comparison only
  births within round r are allowed.
  - For R1, R2, R3 and T(d) the cutoff removes no interleaving that matters. A birth within round r is read from a brood of
    knots born by round r and from their parents, and no birth outside the cutoff enters such a brood.
  - For R0 and R3L, which read the present roster, births outside the cutoff could change what they read. So the cutoff
    removes interleavings, and their least differing orders and any match through round r are relative to the cutoff.
  - A mismatch at a birth whose parent was born after round r is not tested.
- **Outcomes of a run.**
  - A run **matches through round r** when it has no mismatch, allows no birth within round r, every reference knot whose
    parents are all images of m and born by round r is itself an image, and every image of m born by round r that retires
    in the reference is barred in the run.
  - A run **underbuilds** when it allows no birth within round r while one of those reference knots is not an image, or one
    of those retirements is not made.
- A law **builds what the complete rounds build through round r** on a start when every maximal order of it within round r
  matches through round r. When births are made is not compared, only what is built.
- **Memo key.** The set of images of m, together with the set of images of barred knots.
  - It is valid while every birth and barring so far has matched. Then two states with equal keys are the same structure up
    to renaming of distinctions: each image fixes a knot's parents, its fresh count and whether it is barred, and which loose
    distinction of a parent a child took is exchangeable. Every law here is invariant under renaming, so it allows the same
    births in both states.
  - Equal structures can have unequal keys (which of two exchangeable offshoots has the matched children); that only
    enlarges the search.
  - A state's number of births is the size of its key less the start knots. So a breadth-first search over keys finds the
    least number of births to a mismatch exactly. A depth-first search stopped after a set time does not: on the
    start-clause counterexample it reported 9 where the least is 2.
- **Orders searched.** Three kinds, none of them a weighting:
  - **every order**: breadth-first over memo keys, up to a cap on keys, reported as finished or not, with the number of births
    to which every order was searched;
  - **sampled**: at each step a uniform choice among the allowed births within the cutoff, seeds 0 to 199;
  - **x-last**: for each knot x that exists by round 1 of the reference, an order that never makes a birth with x (through
    m) among its parents while any other birth within the cutoff is allowed. Among the others it chooses uniformly, seed 0.
  - Shares are reported under the uniform choice only.
- **Reported in every run:** each firing of the closing bit and whether the matched reference knot received none, and
  whether any roster read has a group of three or more.

## 5. What is supplied by hand (scaffolds)

- **The parent relation.** Which holder of a shared distinction is the parent is written by the birth, not read from the
  holders. Holdings at birth, weaned, brood and every made-birth test depend on it.
  - Recovering it instead from depth to supplied or recognised originals reads the whole structure.
  - Depth orients every parent–child meeting here, but it is not the round under waiting. In the scratch runs 196 of 544
    knots of D2(4, 3) through round 7 have depth unequal to their round.
- **The start clause.** Start knots read the start roster for ever, and start waiters read a second time against start knots
  only. It is exact only when no start knot that acts meets a start knot that waits; on the start-clause counterexample it is wrong
  twice (section 2.2).
- **The waiters' recursion** (section 2.1, step 5): how a waiter reads a second time, against which roster, and the
  all-short test.
- **The barring** under CANCEL-RETIRE: an act that is not a birth, made as soon as allowed.
- **The closing bit**, read on the present structure, and under STALL the read of the start roster only.
- **The guards**: weaned; brood-mates weaned; the brood all-weaned; T(d)'s reading within d and its rule at the boundary; R3L's untouched test.
- **R0's extension** to FLOOR1, CANCEL-RETIRE, CANCEL-OFFSHOOT and ORD.
- **The control's supplied originals.**
- **The comparison**: ticket A's engine as the reference, the cutoff r, the last round R, the rule for a match and its
  least-numbered choice, and the three kinds of order (none a weighting; shares under the uniform choice only).
- **The starts, cutoffs and caps**, and the scratch prototype that produced the disclosed results, which is unreviewed and is not
  the study's engine.
