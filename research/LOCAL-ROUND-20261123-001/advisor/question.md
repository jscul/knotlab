You are asked to review, cold, the design of a study before it is frozen. You have no tools; answer from this text alone. Be a critical colleague: find what is wrong, ambiguous, untestable, trivially true or confounded. Do not praise. Work small cases by hand where a claim depends on them and say where you disagree.

Context. A research program grows structures of "knots" (parity or not-all-equal constraints on binary "distinctions", each held by one or two knots) in complete synchronous rounds. Earlier today two studies closed whose shared definitions are reproduced first below (frozen, unchanged). They found that the round for the whole growth can be replaced by rounds taken part by part, and that a "birth-by-birth" law in which every knot reads again after each birth jams. An older record has a "depth guard" that reproduces ordinary growth one birth at a time by finishing the least unfinished depth first, reading the whole structure. The new study asks whether births can be made one at a time with each knot reading only a bounded distance, and registers five laws (R0, R1, R2, R3, R3L) and a control. Its definitions and pre-registration follow. A helper wrote a scratch prototype and ran it; those runs are disclosed in the pre-registration and you should treat them as unverified.

Please answer, numbered:
1. Definitions (second file). Are "weaned", "brood", "roster of the brood at birth", the plan with the waiters' recursion, "births already made", the barring write and the closing bit each well defined and mutually consistent? Is the argument in section 1.4 ("the roster of a complete brood at birth is exactly the part the complete rounds read in the round after its births") correct under RELEASE, including for a brood containing knots that then wait? Find a counterexample if there is one. Is the start clause consistent with the complete rounds on a start whose members meet members (for example the ring of five knots, each sharing one distinction with the next and holding three loose)?
2. Laws R1, R2, R3. For the cycle of four through dead knots, D2(4, 3), under (RATION-3, CANCEL-WAIT): do you agree that R1 can differ from the rounds (the disclosed least order of 7 births) and that R2's wider guard prevents exactly that? Is there an order under R2 that you expect to differ, in round 1 or later (for example when the waiting joins of the returned ring wait a second time, or when a waiter's role is read while part of its brood has not been born)? Is R2's guard ("every child of each of its parents is weaned") enough to make a member's role final, or can the role still change as more of the brood is born?
3. The comparison (section 4 of the definitions): is the matching rule sound (least-numbered unmatched reference knot with the same parent images and fresh count)? Can it report "no mismatch" for a run that builds a different structure, or a mismatch for a run that builds the same one? Is the memo key valid as claimed? Is "complete through round r" the right notion, and can the bound hide a difference?
4. Predictions: which are trivially true, which unfalsifiable as worded, which do you expect to fail? P11 claims a role can be read within 5 holder steps (7 after one wait): estimate the true distance by hand on D2(4, 3).
5. The honest scope. The laws read the parent relation (who was made from whom), written by each birth. Is a positive result then a statement about locality at all, or does the parent relation smuggle in the round? What would be the cleanest statement of what R2, if it passes, does and does not show?
6. Known under other names; and words: are "weaned" and "brood" acceptable for these two meanings (the alternatives are "clear" and "kin"), given the rule of one word per meaning and no clash with standard technical senses? Flag other words used in two senses.

=== FILE 1: shared definitions of the earlier studies (frozen, unchanged) ===
# A ring in balance: definitions shared by the three studies

Epic `RING-IN-BALANCE-20261123-001`, 2026-11-23. Frozen with the three pre-registrations, before any of the study's code is
written. Tickets A, B and C cite this file and add only what is their own. The canonical K1–K3 test is unchanged. Words are the
glossary's (Intuitions guide). The growth records' "junction" is a knot and their "growing end" is the live roster. Their
"witness" is here a **common knot**, their "witnessed set" a **met set** and their "adjacent" **joinable**, because the glossary
keeps witness for a helper variable and graph theory uses adjacent for what the program calls meeting.

## Structure

- A **structure** is a finite set of knots, each holding a set of distinctions, its **places**. A distinction has one or two
  **holders**. It is **loose** with one holder and **shared** with two. Every knot of a start has at least three places, and so
  has every new knot except one that receives no fresh distinction (below).
- Two knots **meet** when they share a distinction. A knot is **live** while it holds a loose distinction and **dead** otherwise.
- A **start** is a structure given before any birth, written as its list of knots, each a list of distinction numbers (the
  records' stars).
- A loose distinction is **usable** unless the law has **barred** it: a barred distinction stays loose and is never taken by any
  birth. (The Intuitions guide and the site call a barred distinction "never used".)

## The live roster

- The **members** of the live roster are the knots holding at least one usable loose distinction. Write h(u) for the number of
  usable loose distinctions member u holds and k(u) for the number of barred ones. A knot holding only barred distinctions is
  live and is not a member.
- A **met set** is the set of members that one knot of the structure meets, when it has at least two members. That knot is a
  **common knot** of those members; it may be dead or itself a member. Two knots with the same met set count once.
- Two members are **joinable** when some met set contains both. A **part** of the live roster is a connected component of the
  relation joinable. The roster is **past its start** when no member meets a member (the records' positive age).
- Two rosters, or two parts, are **the same** when a one-to-one renaming of members carries h, k and the family of
  inclusion-maximal met sets of one onto the other.

## One complete round

A **law** is a knot law (parity or not-all-equal), a ration, a treatment and optional extras. One round, on real knots:

1. **Groups.** First take every inclusion-maximal set of at least three pairwise joinable members that is contained in no
   single met set. Then take every joinable pair that is contained in none of the sets just taken. These are the groups
   ([ORDINARY-DYNAMICS-20261120-001](../ORDINARY-DYNAMICS-20261120-001/end_operator.md), "The operator on the present end", step 1).
2. **Owing.** Member u owes one usable loose distinction to each group containing it. It is **short** when it owes more than
   h(u). Shortness is read once, here, for the whole round.
3. **Treatment of a short member.**
   - STALL: if any member is short, no birth is made and the growth has stalled.
   - CANCEL-OFFSHOOT: every group containing a short member is cancelled; the short member makes an offshoot from each of its
     usable loose distinctions.
   - CANCEL-WAIT: every group containing a short member is cancelled; the short member **waits**: it makes nothing and keeps
     everything it holds.
   - CANCEL-RETIRE: every group containing a short member is cancelled; the short member **retires**: it makes nothing now or
     later, and its loose distinctions are barred.
4. **Joins.** Each group that is kept makes one new knot, a **join**, whose parents are its members; it takes one usable loose
   distinction from each.
5. **Offshoots and the release rule.** A member that is not short, after paying its kept groups, makes one new knot of one
   parent, an **offshoot**, from each usable loose distinction it has left. RELEASE (the default): this includes the
   distinctions that its cancelled groups would have taken. HOLD: it keeps those and makes offshoots only from the rest. With
   the extra NO-OFFSHOOT it makes no offshoot, and the distinctions an offshoot would have taken are barred.
6. **Demand.** Count every new knot as a member holding one usable loose distinction, whatever it will receive, and keep every
   old member that still holds a usable loose distinction after steps 3 to 5 (one that waits; under HOLD, one that keeps what
   its cancelled groups would have taken) with what it holds. Form the groups of that roster as in step 1. The **demand** D of
   a new knot is the number of those groups that contain it.
7. **Fresh distinctions (the ration).** A new knot with p parents and demand D receives f fresh distinctions, each loose and held
   by it alone. With q = max(D, 3 − p, 1), the ordinary count:
   - ORD: f = q. CAP-k: f = min(q, k). RATION-k: f = max(k, 3 − p).
   - ONE-FEWER: f = min(q, max(3 − p, 0, q − 1)). FLOOR0: f = max(3 − p, 0). FLOOR1: f = max(3 − p, 1).
   - **Closing exception** (parity only, every ration): a new knot that takes every loose distinction of the structure receives
     none; it may then have fewer than three places. It is then the round's only birth, nothing is barred and no old member
     keeps anything. Under not-all-equal there is no exception
     ([NAE-GROWTH-20261119-001](../NAE-GROWTH-20261119-001/nae_growth.md): the growth reads the knot law in this one place).
8. **Extra FILLERS.** Of a new knot's f fresh distinctions, min(f, D) are usable and the rest are barred.

The records' ordinary growth, the cheapest growth of lesson 8.1, is the law (ORD, STALL). **The two added rules** are the law
(CAP-3, CANCEL-WAIT with RELEASE). **The three added rules** are (CAP-3, CANCEL-WAIT with RELEASE, FILLERS). They were added by
hand (assumption A224, a scaffold); RELEASE is part of what was added. The pilot's program counted a short member by all its
loose distinctions; the two readings agree, because a member holding a barred distinction owes exactly its usable count in
the one round it acts. One barred distinction anywhere switches the closing exception off everywhere, since the exception needs
a birth that takes every loose distinction there is.

A distinction taken by a new knot becomes shared between its old holder and the new knot. Which of a member's usable loose
distinctions goes to which birth makes no difference up to renaming.

## Kinds of outcome under complete rounds

A run is one start grown under one law through a stated number of rounds, or until a stated number of knots. After each round:

- The growth has **stopped** when the roster has no member, **stalled** (STALL only) when a member is short, and **jammed** when
  the roster has members and the round makes no birth.
- A part Y of the roster after round s, past its start, **returns** at round t > s when the members after round t that descend
  from Y (through parents; a waiting member descends from itself) include a part that is the same as Y. The other parts those
  descendants form have **come apart** from Y, and Y **gives parts off** when there is at least one. Returns are searched with
  the least s first and then the least t, and t − s is the period.
- The roster is **in balance** from round s with period T when at least one birth is made in every round and the whole roster
  after round t + T is the same as the whole roster after round t for every t ≥ s in the run. The structure still grows.
- A part has **ended** when none of the knots descending from it is a member. It may still hold barred distinctions.
- For a census a run is given one kind, the first that applies: stalled; jammed; stopped; a part returns giving parts off; a
  part returns giving none off; grows to the bound with no return found.

## One part at a time, and one birth at a time

- **Part-round law.** A move is one complete round of one part: steps 1 to 8 applied to the members of that part alone, the
  other parts left as they are (the closing exception as stated: only for a birth that takes every loose distinction of the
  whole structure). The **own time** of a start knot is 0; a new knot's is one more than its parents'; and a member that
  waits through a move of its part gains one. So a member's own time is the number of moves its line of descent has taken
  part in. A **priority** chooses the part that moves next among the parts that would make a birth:
  - ALL-IN-TURN: every part once, then again; this is the complete round.
  - UNIFORM: each part with equal chance.
  - BY-MEMBERS: each part with chance in proportion to its number of members.
  - LARGEST: a part with the most members; SMALLEST: one with the fewest; ties uniform.
  - MOST-LOOSE: a part whose members hold the most usable loose distinctions in all; ties uniform.
  - LEAST-TIME: a part whose members have the least own time; ties uniform. This priority reads the history, not the structure.
- **Birth-by-birth law** (the present-state reading of [ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md), with
  waiting). A move is one birth, and everything is read again after every move.
  1. Form the groups of the present roster as in step 1, with every knot allowed as a common knot (ANY) or only dead knots
     (DEAD). A group is **open** when no knot already made has all of its members among its parents.
  2. A member is short when it is in more open groups than h(u); a short member makes nothing. Under FIRST-COME, used only to
     check the engine against the record, no member counts as short.
  3. Every open group with no short member is a join move. A member that is not short and holds more usable loose distinctions
     than the number of open groups without a short member that contain it has an offshoot move. (Under FIRST-COME: every open
     group is a join move, and a member has an offshoot move when h(u) exceeds the number of open groups containing it.)
  4. The new knot receives max(3, 3 − p) fresh distinctions (RATION-3), or max(d, 3 − p, 1) (PRESENT-ORD), where d is the number
     of open groups containing it immediately after its birth, the new knot counted as a member before it receives anything.
     Closing exception, parity only: a move that takes every loose distinction of the structure, with d = 0 where d is read,
     receives none.
  5. Start knots have **generation** 0 and a new knot has generation one more than the greatest generation of its parents; a
     move's generation is the greatest generation of its parents. The next move is chosen uniformly among all moves (UNIFORM)
     or among the moves of least generation (BY-GENERATION), with joins first, offshoots first, or uniformly among those. The
     generation is the simulator's record of who was made from whom; it is not read from the structure.
  - A birth-by-birth run has **jammed at generation g** when no move of generation g or less is available and some member of
    generation g or less is short.

## The knot test

- **Parity.** Each knot is the rule that its places have even parity. A knot with place set S passes K1–K3 in the whole
  structure when the allowed states of the structure, restricted to S, are exactly the even assignments of S. Two methods are
  run and must agree on every knot. Ranks: with H the matrix over the field of two elements with one row for each knot, the
  rank of H less the rank of H with the columns of S removed is one (the records' test, ORDINARY-DYNAMICS, `rulers.py`). Cut:
  in the graph with one vertex for each knot and one for the outside, an edge between the two holders of each shared
  distinction and an edge to the outside for each loose one, deleting the knot leaves the rest connected (the knot is not a cut
  vertex; the allowed states are the graph's cycle space).
- **Not-all-equal.** Each knot is the rule that its places are not all equal. A knot passes when the assignments of S that
  extend to an allowed state of the whole structure are exactly the assignments that are not constant, decided by a SAT solver
  for each of the 2^|S| assignments (the records' test, ORDINARY-DYNAMICS, `source_cert.py`).
- **Extension.** A round, or a move, extends when every allowed state of the structure before it is the restriction of an
  allowed state after it.

## Named starts

- **Ring(n, a).** Knots 0 to n − 1. Knot i shares one distinction with knot i + 1 (mod n) and holds a loose distinctions.
  Ring(5, 3) is the start of the golden-ratio eddy.
- **Cycle through dead knots, doubled, D2(n, a).** Members 0 to n − 1, each holding a loose distinctions, and dead knots
  w_0 to w_{n−1}; w_i shares two distinctions with member i and two with member i + 1 (mod n), so w_i has four places and its
  met set is {i, i + 1}.
- **Cycle through dead knots that meet one another, DW(n, a).** As D2 with single meetings: w_i shares one distinction with
  member i, one with member i + 1, one with w_{i−1} and one with w_{i+1}.
- **The seven-knot generator.** Stars [0,1,2,9,10,11], [0,1,3], [4,5,12,13,14], [6,7,15,16,17], [2,3,4,6,18,19,20], [7,8,21,22],
  [5,8,23,24] ([GENERATORS-20261120-001](../GENERATORS-20261120-001/source.md)).

## What is supplied by hand

The complete round (assumption A104); every ration other than ORD, every treatment other than STALL, the release rule and both
extras (A224); the part-round law, the birth-by-birth laws and every priority; the starts; the reading of a part as a thing (as
in A125); the bounds on rounds, moves and knots; and each weighting named where a share is given. Each study says which of
these it swaps.

=== FILE 2: definitions of the new study (to be frozen) ===
# One birth at a time from what is built: definitions

Epic `LOCAL-ROUND-20261123-001` (sub-goal B323; goals G5 with G18), 2026-11-23. Frozen with the pre-registration of ticket A, before any of the
study's code is written. It extends [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) of
`RING-IN-BALANCE-20261123-001` and changes nothing in them; "the definitions" below means that file, cited by line. Words are
the glossary's and the definitions'. **Member, met set, common knot, joinable, part, short, waits, retires, live, dead, usable,
barred, start** keep exactly their meaning there. Two words are new here: **weaned** and **brood** (sections 1.3 and 1.4). The
text was drafted by the helper agent that surveyed the record and wrote a scratch prototype of these laws; the prototype is
not the study's engine, and what it showed is disclosed in the pre-registration.

## 1. What is read from the structure

### 1.1 Parents, children, places

- **Parents.** Every birth writes, with the new knot, the set of knots it took a distinction from: its **parents**
  (definitions step 4–5: a join's parents are its group, an offshoot's its one member). The **children** of a knot are the
  knots that have it among their parents. A start knot has no parents and is the child of none. The parent relation is not
  a reading of the holders: a shared distinction has two holders and no order (definitions lines 11–13, 76). It is written
  by the birth, as the record's birth-by-birth law already reads it (definitions line 111). See section 7.
- **Places, loose, usable, barred, h(u), k(u), member, live, dead**: as the definitions, lines 11–24.
- **Holdings at birth.** For a knot x with parents, **h₀(x)** is its number of places less its number of parents (each
  parent gave one distinction; the others x received at birth, whatever they are now: loose, barred, or shared with a child).
  For a start knot, h₀(x) is its number of places not shared with another start knot.
- **Holder step.** One holder step crosses a shared distinction from one holder to the other
  ([SERIAL-REPAIRS](../SERIAL-REPAIRS-20261120-001/local_rule.md) line 7). The **distance** between two knots is the least
  number of holder steps between them. A rule **reads to distance d** from a knot when its decision is the same for any two
  structures that agree on every knot within d holder steps of it: their places, which of those are loose, usable or
  barred, their parent sets and their children, together with the one global bit of §2.4.

### 1.2 The start roster (what plays the part of parents for start knots)

The **start roster** has as members the start knots with h₀ ≥ 1, each with holding h₀, and as met sets, for each start
knot, the set of start members it meets, when it has at least two. Any start knot may be a common knot here, a member
included, as in definitions step 1. It is the roster the first complete round reads; it never changes.

### 1.3 Weaned

A knot is **weaned** when none of its parents is a member. Every start knot is weaned.

### 1.4 The brood

- The **brood** of a knot x with parents is the smallest set B containing x such that, for every knot in B and every parent
  of it, all children of that parent are in B. The **parents of the brood** are the parents of its knots. Knots of B that
  have since made births, retired or died stay in B.
- The **roster of the brood at birth** has as members the knots of B with h₀ ≥ 1, each with holding h₀, and as met sets,
  for each parent p of the brood, the members that are children of p, when there are at least two.
- A brood is **complete** when every knot in it is weaned.
- Why this set (an argument for the referee, not a definition). Under RELEASE a member that makes any birth spends every
  usable distinction in the one roster in which it acts, so all children of a parent are born in one complete round. Past
  the start, a knot meets only its parents and its children. So the roster of a complete brood at birth is exactly the
  part the complete rounds read in the round after its births, with the holdings it had then.

## 2. Plans, and how a birth is made (common to R1, R2, R3, R3L)

### 2.1 The plan of a roster

A **roster** is a set of members, a holding for each, and a family of met sets. Its **plan** is read as follows.

1. **Groups and owing** as definitions steps 1–2 (lines 36–40), with the roster's holdings.
2. **Treatment.** STALL: if a member is short, the plan **stalls** and has no births. CANCEL-OFFSHOOT: a short member's
   births are one offshoot from each of its holdings. CANCEL-RETIRE: a short member **retires** in this plan. CANCEL-WAIT: a
   short member **waits** in this plan.
3. **Births of the plan.** Every group containing a short member is cancelled. Each kept group is one planned join. Each
   member that is not short has as many planned offshoots as its holding less its kept groups (RELEASE).
4. **Fresh count of a planned birth with p parents.** FLOOR1 and RATION-3 as definitions step 7, line 62. ORD:
   f = max(D, 3 − p, 1), where D is the number of groups containing it in the roster whose members are the plan's births,
   each with holding 1, and whose met sets are, for each member of the plan's roster, the births it is a parent of, when
   there are at least two. Under STALL no member keeps anything, so no old member enters this roster. The closing exception
   is not applied here (§2.4).
5. **Waiters' recursion** (CANCEL-WAIT). The **roster of the waiters** has as members the waiters, with unchanged
   holdings, and as met sets the roster's met sets intersected with the waiters, kept when they have at least two. Each part
   of it is read again by steps 1 to 5. A member's **acting roster** is the first roster of this sequence in which it is not
   short. A part with the same members and met sets as the roster it came from **jams**: its members have no acting roster
   and no births. (A waiter reads again against the waiters of its roster only, never against new knots. Past the start this
   is what the complete rounds read, by §1.4.)
6. A member's **planned births** are the births of its acting roster that have it among their parents, with multiplicity.
   Its **role** is "acts" (with those births), "retires", "stalls" or "jams".

### 2.2 Which roster a member reads

- **Start clause.** A start knot reads the start roster (§1.2), at every moment.
- Every other member reads the roster of its brood at birth (§1.4).

### 2.3 Births already made

A planned join with parents G is **made** when some knot has exactly the parents G. A member's planned offshoots are made,
up to their number, by its children that have it as their only parent. The **remaining births** of a plan are its births
less those made. A join remains only if it remains for each of its parents.

### 2.4 Making a birth, retiring, the closing bit

1. A law **admits** a birth: a parent set B, each of whose knots holds a usable loose distinction, with a fresh count f
   (the plan's count).
2. The new knot takes one usable loose distinction from each knot of B; which one makes no difference up to renaming
   (definitions lines 76–77). It receives f fresh distinctions, all usable (FILLERS is not used here). Its parents are B.
3. **Closing exception** (parity, every ration). If after taking there is no loose distinction left in the structure,
   usable or barred, the new knot receives none. This is the **one global bit** every law here reads.
4. **Retiring.** When a member's role is "retires" and the law admits it (with the same guard as its births), all its
   usable loose distinctions are barred. This is a **barring write**. It is not a birth and not a move, since it adds no knot
   (glossary, "Move"). It is made as soon as it is admitted, before the next birth.
5. **Stall.** Under STALL, if the start roster's plan stalls, no birth is admitted anywhere: the growth has stalled. A brood
   whose plan stalls admits nothing (this is part-local; under ORD it does not arise past the start, §5 P12).

An **order** of a law is a sequence of admitted births, each admitted at its moment, with every admitted barring write made
before the next birth. No fairness, priority or weighting is assumed; the study searches every order.

## 3. The laws

**R0 · the record's birth-by-birth law.** As the definitions, lines 108–126, common knots ANY, order UNIFORM (and
BY-GENERATION as recorded). It is defined there only for RATION-3 or PRESENT-ORD with WAIT or FIRST-COME. **Added here**,
for this study only:
- FLOOR1 gives f by p as RATION-3 does in step 4.
- Under CANCEL-RETIRE a member read short retires at once (a barring write).
- Under CANCEL-OFFSHOOT a member read short has an offshoot move from each usable loose distinction and no join move.
- Under ORD the law is PRESENT-ORD with FIRST-COME, as the record ran ROUND-FREE's law
  ([ticket C's readings](../../experiments/RING-IN-BALANCE-20261123-001C/RING-IN-BALANCE-20261123-001C-E001_no_round/deviations.md), item 18).

Reads to distance: not measured; I guess about 5.

**R1 · the birth's parents are weaned.**
1. Each member reads its role by §2.1–2.2 from the structure as it stands. A brood that is not complete is read with the
   children its parents have so far.
2. A remaining birth B is admitted when every knot of B is weaned.
3. A barring write on x is admitted when x is weaned.

Reads: the guard reads to distance 1. A member's role reads to distance 5 if it has not waited (its groups need 3, the
shortness of each partner 5), and about 5 + 2w after w waits. **Guess, not measured.** An implementation may compute the
whole brood; the distance is a claim about which part of it decides.

**R2 · the parents' brood-mates are weaned too.** As R1, but a remaining birth B (or a barring write on x) is admitted
when every knot of B (or x) is weaned and so is every knot sharing a parent with it, that is, every child of each of its
parents. Reads: the guard reads to distance 3; the role as R1 (guess).

**R3 · the whole brood is weaned** (the working idea, read through broods). As R1, but a remaining birth B (or a barring
write) is admitted when every brood containing a knot of B is complete. Start knots are always admitted, since the start
roster has no parents. Reads: the whole brood. On D2(n, 3) the brood of the start's births has 2n knots and reaches about
n holder steps.

**R3L · the present part** (the working idea as literally stated). Read the present live roster (definitions step 1, ANY)
and its parts.
1. A part in which no member has a child and every member is weaned is **fresh**: its plan is the plan of the part with
   present holdings h(u) and present met sets. Its remaining births and barring writes are admitted.
2. A part in which some member has a child: each member reads its role by §2.2 (start roster or brood at birth), and its
   remaining births and barring writes are admitted with no guard.
3. Any other part admits nothing.

Reads: the whole part.

**Control · the depth guard, originals supplied** (the record's guard with this study's round in place of the ordinary
operator: [SERIAL-REPAIRS](../SERIAL-REPAIRS-20261120-001/present_proof.md) lines 41–43;
[cohort.py](../../experiments/SERIAL-REPAIRS-20261120-001A/SERIAL-REPAIRS-20261120-001A-E001_repairs/cohort.py) lines
28–81; originals supplied as in
[the clock study's replay.py](../../experiments/TICK-BIRTHS-AND-SCARCITY-20261121-001B/TICK-BIRTHS-AND-SCARCITY-20261121-001B-E001_serial/replay.py)
lines 66–116).
1. The originals are the start knots. The **depth** of a knot is its distance to the nearest start knot.
2. Let k be the least depth of a member. The **layer** is every knot of depth k, members or not.
3. Holdings: the start holdings at k = 0; otherwise each layer knot's places not shared with a knot of depth k − 1.
4. Roster: the layer knots with holding at least 1. Met sets: the start roster's at k = 0; otherwise, for each knot of
   depth k − 1, the roster's knots it meets, when at least two.
5. The plan is §2.1 steps 1–4, **without** the waiters' recursion: a waiter has no role.
6. Births are made by the layer knots' children: the knots of depth k + 1, by their neighbours of depth k. Subtract them
   (§2.3), admit the rest, and make barring writes as §2.4.

Reads: the whole structure.

## 4. The comparison

- **Reference.** Ref is the complete rounds from the same start under the same law, through a last round R. R must be such
  that every knot born by round r (the bound below) is no member of Ref's last roster, or Ref's growth has stopped; this is
  checked. Each Ref knot has a round of birth.
- **Match.** A run keeps a map m from its knots to Ref's knots, the identity on start knots.
  - A birth c with parents B and f fresh distinctions **matches** when Ref has a knot c′, not yet an image of m, whose
    parent set is m(B) and whose fresh count (places less parents) is f. Then m(c) is the least-numbered such c′.
  - A barring write on x **matches** when m(x) holds barred distinctions in Ref and has no children there.
  - Anything else is a **mismatch**.
- **Bound.** A birth is **within round r** when the image of each of its parents was born by round r. In the comparison
  only births within round r are admitted. (The glossary's "horizon" is a number of moves, so it is not used here.)
- **Outcomes of a run.** A run is **complete through round r** when it has no mismatch, admits no birth within round r,
  and every Ref knot whose parents are all images of m and born by round r is itself an image. A run **stops short** when
  it admits no birth within round r while some such Ref knot is not an image.
- A law **builds what the complete rounds build through round r** on a start when every maximal order of it within round r
  is complete through round r. When births are made is not compared, only what is built.
- **Memo key.** The set of images of m, together with the set of images of barred knots.
  - It is valid while every birth and write so far has matched. Then two states with equal keys are the same structure up
    to renaming of distinctions: each image fixes a knot's parents, its fresh count and whether it is barred, and which
    loose distinction of a parent a child took is exchangeable. Every law here is invariant under renaming, so it admits
    the same births in both states.
  - Equal structures can have unequal keys (which of two exchangeable offshoots has the matched children); that only
    enlarges the search.
  - A state's number of births is the size of its key less the start knots. So a breadth-first search over keys finds the
    least number of births to a mismatch exactly. A depth-first search stopped by a time limit does not: on the seven-knot
    start it reported 9 where the least is 2.

## 7. What is supplied by hand (scaffolds)

- **The parent relation.** Which holder of a shared distinction is the parent is written by the birth, not read from the
  holders. Holdings at birth, weaned, brood and every made-birth test depend on it. Recovering it instead from depth to
  supplied or recognised originals reads the whole structure. Depth orients every parent–child meeting here, but it is not
  the round under waiting: in the scratch runs 196 of 544 knots of D2(4,3) through round 7 have depth unequal to their
  round.
- **The start clause.** Start knots read the start roster forever, and start waiters read again against start knots only.
  It is wrong on the seven-knot start.
- **The waiters' recursion** (§2.1 step 5): the reading of how a waiter reads again, and against which roster.
- **The barring write** under CANCEL-RETIRE: a write that is not a birth, made as soon as admitted.
- **The global bit** for the closing exception, and under STALL the read of the whole start roster.
- **The guards** themselves (weaned; brood-mates weaned; brood complete) and R3L's freshness test.
- **R0's extension** to FLOOR1, CANCEL-RETIRE, CANCEL-OFFSHOOT and ORD.
- **The control's supplied originals.**
- **The comparison:** the reference rounds, the bound r, the matching rule and its least-numbered choice, and the order
  space (every order, no fairness, no priority, no weighting); sampled shares are under the uniform choice of §5 only.
- **The starts and bounds**, and the scratch prototype that produced §5, which is unreviewed and must not be the study's
  engine.

=== FILE 3: pre-registration of the new study (to be frozen) ===
# Can births be made one at a time, each knot reading a few steps, and still build what the rounds build? Pre-registration

Ticket `LOCAL-ROUND-20261123-001A` of epic `LOCAL-ROUND-20261123-001` (sub-goal B323; goals G5 with G18), 2026-11-23. Frozen before the study's code is written. Code by a
helper agent that has not seen the drafter's prototype, from this text and [the definitions](../LOCAL-ROUND-20261123-001/definitions.md), which
extend the [shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) of `RING-IN-BALANCE-20261123-001`. The
canonical K1–K3 test is unchanged.

## The question

The owner asked on 23 November 2026 whether time is "a device or pattern just like the other ones", and then whether it is
"not really like a sequencer, but more like a priority system". The study of the ring that returns found that the round for
the whole growth can be replaced by rounds taken part by part, and that a law in which every knot reads again after each birth
jams. The record's serial-repairs study had already shown, for ordinary growth, a rule that makes one birth at a time and
builds what the rounds build in every order, by finishing the least unfinished depth first; it reads the whole structure and
needs the first knots to be recognisable, and under waiting it stops short. This study asks what is left: is there a law that
makes one birth at a time, in which each knot reads only a bounded distance and only what is built, that builds in every order
what the complete rounds build, for the laws with a ration fixed at birth, for the ring that returns, which needs waiting,
and for ordinary growth? It registers five laws that differ in how far a knot reads and when it may read, and the record's
depth guard as a control.

## In standard terms

Confluence of an asynchronous graph-rewriting system against its synchronous reference: whether every maximal sequence of
single rule applications, each guarded by a local readiness condition, reaches the structure the parallel steps build. The
guards are of the kind used by a synchronizer in distributed computing (a node acts when its predecessors have finished);
the question of the least radius of the guard is the question of the locality of the synchronizer.

## Prior work in the program

Searches, each with `--until 2026-11-23 --exclude LOCAL-ROUND-20261123-001`:

`python3 -B scripts/track.py objects "one birth at a time from what is built, every order builds what the rounds build" --until 2026-11-23 --exclude LOCAL-ROUND-20261123-001`
`python3 -B scripts/track.py objects "guarded serial rule, depth cohort, reads the whole structure" --until 2026-11-23 --exclude LOCAL-ROUND-20261123-001`
`python3 -B scripts/track.py objects "a knot reads a bounded number of steps to decide its birth" --until 2026-11-23 --exclude LOCAL-ROUND-20261123-001`

- `RING-IN-BALANCE-20261123-001` — the same object: its ticket C showed that parts taking their rounds one at a time build
  what the complete rounds build, and that the birth-by-birth law, here R0, jams. This study starts from its definitions.
- `SETTING-AS-REREAD-20261123-001` — unrelated (a measurement setting read as a re-read birth, another thread's study of the
  same day).
- `SERIAL-REPAIRS-20261120-001` — the same object for ordinary growth: its guarded rule finishes the least unfinished depth
  first and reproduces the complete rounds in every order of its own moves, reading the whole structure, on starts whose
  original knots can be recognised (proved in that scope, referee pending); it also argues, without running it, that a read
  of four to five holder steps suffices once parent direction is available. This study's control is that guard with the
  originals supplied; its laws R1 to R3 are bounded-read relatives of that argument, extended to waiting.
- `TICK-BIRTHS-AND-SCARCITY-20261121-001` — a relative: the same guard on an eight-knot clock, with the originals supplied.
- `GENERATORS-20261120-001` — a relative: its fixed-map replay delivers births in other parent-respecting orders with the
  whole layer's plan supplied.
- `MEET-ORDERS-20261118-001`, `COPY-CLASS-20261118-001`, `MEET-TWIST-20261118-001` — unrelated (orders of meeting in
  betweenness structures).
- `ROUND-FREE-20261119-001` and `FRESH-DEMAND-20261120-001` — relatives: present-state laws are order-dependent; with the
  first layer's plan supplied every order agrees; demand follows from the parents' child lists alone.
- `COPYING-PARTS-20261123-001` — a relative: the laws with a ration fixed at birth, FLOOR1 among them, used here.

## Prior work outside the program

Synchronizers (Awerbuch 1985) run a synchronous algorithm on an asynchronous network by local waiting; Lamport's logical
clocks (1978) order events without a global clock; confluence by critical pairs in graph transformation (Ehrig; Plump) and
abelian networks (Bond and Levine 2016) are the standard settings for order-independence. Not searched beyond ticket C's
note of the earlier study. What this would add is the least reading distance for these growth laws, and a case with waiting.

## Known before the freeze (disclosed)

The drafter of the definitions wrote a scratch prototype of every law here and ran it on every start below before this
freeze. The prototype is unreviewed, is not the study's engine, and its author does not write the study's code. Its complete
rounds agree with ticket A's engine of the earlier study round by round on all twelve start and law pairs. What it showed:

All from my scratch prototype (not record evidence, unreviewed): one core, each search under 50 s. The prototype's complete
rounds agree with ticket A's engine on births and fresh totals per round, rounds 1 to 5, for all twelve start and law
pairs below. "Every order" means the exhaustive search over memo keys finished. "Sampled" means at each step a uniform
choice among the admitted births, seeds 0 to N − 1. Knots are numbered as in growth.py's `from_stars`, births from the first
free number.

Starts. D2(4, 3), D2(5, 3), Ring(5, 3) as the definitions, lines 145–151. Two-knot: `[[0,1,2],[0,3,4]]`. Three-knot:
`[[0,1,2,3],[0,1,4,5],[2,3,6,7]]` (a dead knot with two members). Lone four-place: `[[0,1,2,3]]`. Seven-knot counterexample:
`[[1,2,3,7,8],[1,4,9,10],[2,5,11,12],[3,6,13,14],[4,15,16],[5,17,18],[6,19,20]]`. In it, knot 0 meets knots 1–3 once each
and holds two loose; knot i (1–3) meets 0 and i + 3 and holds two; knots 4–6 hold two.

| Start · law | Bound | R1 | R2 | R3 | R3L | R0 | Control |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D2(4,3) · RATION-3, CANCEL-WAIT | round 1 (28 births) | differs: 67,353 states, 1,332 mismatches; least 7 | every order (65,803 states, 24.5 s) | every order (65,791, 19.3 s) | differs: 32 mismatches; least 12 | every order ends in a mismatch or stops short; least 3 | every order stops short after 20 births |
| D2(5,3) · same | round 1 | least 7 (exact); 30 of 60 sampled differ | 60 of 60 sampled | 60 of 60 sampled | least 14 (exact); 60 of 60 sampled complete | least 3 | 60 of 60 stop short |
| Ring(5,3) · same (members meet members) | round 1 exact least; round 2 sampled | least 7; 15 of 40 differ | 40 of 40 | 40 of 40 | least 3; 39 of 40 differ | least 2 | 40 of 40 stop short |
| Two-knot · FLOOR1, CANCEL-RETIRE | round 2 / 3 every order; round 4 sampled 40 | every order (517 / 17,403 states, 3.2 s); 40 of 40 | every order (357 / 16,435); 40 of 40 | same as R2 | differs: least 3; 26 of 40 differ | least 2 | every order (152 / 4,247); 40 of 40 |
| Two-knot · FLOOR1, CANCEL-OFFSHOOT | round 2 every order; round 3 unfinished; round 4 sampled 40 | every order to round 2 (841); round 3: no mismatch in 95,621 states, unfinished at 35 s; 40 of 40 | every order to round 2 (729); round 3: none in 90,554, unfinished; 40 of 40 | as R2 (92,858 unfinished) | least 3; 31 of 40 differ | least 2 | every order to round 3 (37,258, 6.3 s); 40 of 40 |
| Three-knot · FLOOR1, CANCEL-RETIRE | round 2 / 3 every order; round 4 sampled 40 | every order (128 / 528); 40 of 40 | every order (124 / 364); 40 of 40 | same as R2 | every order to round 2 (124); 40 of 40 | least 2 (a wrong retirement) | every order (79 / 159); 40 of 40 |
| Three-knot · FLOOR1, CANCEL-OFFSHOOT | round 2 / 3 every order; round 4 sampled 40 | every order (409 / 9,260, 1.7 s); 40 of 40 | every order (407 / 8,026); 40 of 40 | same as R2 | differs: least 6; 13 of 40 differ | least 3 | every order (216 / 2,807); 40 of 40 |
| Two three-place knots · ORD, STALL | round 3 every order | every order (4,624) | every order (3,364) | every order (3,136) | not run | least 2 | every order (1,350) |
| Lone four-place · ORD, STALL | round 4 (through the closing birth) every order | every order (84) | every order (84) | every order (84) | not run | least 1 | every order (84) |
| D2(4,3) · ORD, STALL | round 2 sampled 30 | 30 of 30 | 30 of 30 | 30 of 30 | not run | 30 of 30 differ; least 1 | 30 of 30 |
| Ring(5,3) · ORD, STALL | round 2 sampled 30 | 30 of 30 | 30 of 30 | 30 of 30 | not run | 30 of 30 differ; least 1 | 30 of 30 |
| Seven-knot · RATION-3, CANCEL-WAIT (registered counterexample) | round 1 exact least | least 2 | least 2 | least 2 | least 2 | least 2 | stops short (216 states) |

"Least n" is the least number of births of an order ending in a mismatch, found breadth-first, so exact.

The least differing orders:
- **R1 on D2(4,3):** `(0,) (0,1) (0,3) (1,) (1,2)`, then two offshoots of knot 9 (the join of 0 and 1). Its partners'
  waits are not yet visible, because 2 and 3 are still members, so it makes two offshoots where the rounds give one. The
  same on D2(5,3) and Ring(5,3).
- **R3L on D2(n,3):** the start's 2n births, three offshoots of one start offshoot, then a join of a waiting join with
  another start offshoot. With that offshoot dead, the present part of the waiting joins and the other offshoots looks
  fresh, and two of the joins no longer read as short.
- **R3L on the two-knot start:** knot 1's two offshoots, then knot 0 joins one of them through the dead knot 1.
- **R3L on the three-knot start, CANCEL-OFFSHOOT:** `(2,) (1,2) (1,)`, the two offshoots of knot 5, then `(3,4)`. Under
  CANCEL-RETIRE the short join is barred when its brood is first read, so no later present part can contain it.
- **Every brood law on the seven-knot start:** two offshoots of knot 0. In round 1 it waits (three groups, two holdings).
  In round 2 of the complete rounds the dead knots 1–3 meet it and their joins, and it makes one four-parent join and one
  offshoot. The start clause reads it alone and gives two offshoots.

Not searched exhaustively: D2(5, 3) and Ring(5, 3) through round 1 (I estimate about 10⁶ keys), and anything past round 1
on D2 or Ring under CANCEL-WAIT.

## Settled by construction (stated, not tested)

- Under RELEASE a member that makes any birth spends every usable distinction in the one roster in which it acts, so all
  children of a parent are born in one complete round; past the start a knot meets only its parents and its children. Hence
  the roster of a complete brood at birth is the part the complete rounds read in the round after its births (definitions,
  section 1.4). This is an argument for the referee.
- The comparison's memo key is valid while every birth and write has matched (definitions, section 4).

## What is supplied

Listed in the definitions, section 7: the parent relation written by each birth, the start clause, the waiters' recursion,
the barring write, the global bit for closing, the guards, the control's supplied originals, the comparison and its bound,
the starts. This ticket swaps the guard (five laws and a control), the ration and treatment (three families), and the start.
It does not swap the parent relation: a law that reads only holders, with no record of who was made from whom, is outside it.

## Runs (frozen)

Every start, law and bound of the table above, with every law R0, R1, R2, R3, R3L and the control: a breadth-first search
over memo keys for every order where the table says "every order" or gives an exact least; 200 sampled orders (uniform choice
among the admitted births at each step, seeds 0 to 199) where it says sampled, and in addition wherever a search does not
finish within its limit. Beyond the table: the exhaustive search for R2 and R3 on D2(5, 3) and Ring(5, 3) through round 1 is
attempted with a limit of ten million keys; R1, R2 and R3 on D2(4, 3) under (RATION-3, CANCEL-WAIT) through round 3, where
the waiting joins of the returned ring wait a second time, by 200 sampled orders; R1 under (FLOOR1, CANCEL-RETIRE) and
(FLOOR1, CANCEL-OFFSHOOT) on Ring(5, 3) and on the seven-knot generator of the earlier definitions through round 3, by 200
sampled orders (for P13); and for P11, at every state visited in the searches of P1 and P5, the least distance d from 1 to 9
at which a member's role read from the knots within d holder steps equals its role read from the whole brood.

## Predictions (frozen)

Marked (a) already seen in the drafter's scratch runs, (b) a hand prediction that was not run, (c) open: reported without a
prediction.

(a) already seen in the scratch runs above (to be disclosed before the freeze); (b) my hand prediction, not run; (c) open.

- **P1 (a)** R2 and R3 build what the complete rounds build through round 1 on D2(4,3) under (RATION-3, CANCEL-WAIT).
  *Fails when* any order has a mismatch or stops short.
- **P2 (a sampled; b every order)** The same on D2(5,3) through round 1, and on Ring(5,3) through round 1.
  *Fails when* an order differs.
- **P3 (a)** R1 differs on D2(4,3), D2(5,3) and Ring(5,3), with least differing order 7 births, by the mechanism of §5.
  *Fails when* the least is not 7, or the first mismatch is not a waiter's surplus offshoot.
- **P4 (a for n = 4, 5; b for n = 6)** R3L differs on D2(n,3), with least differing order 2n + 4 births (16 at n = 6).
  *Fails when* a shorter or longer least order is found.
- **P5 (a)** R1, R2, R3 build what the rounds build:
  - through round 3 on the two-knot and three-knot starts under (FLOOR1, CANCEL-RETIRE), and on the three-knot start under
    (FLOOR1, CANCEL-OFFSHOOT);
  - through round 2 on the two-knot start under (FLOOR1, CANCEL-OFFSHOOT); (b) through round 3 there.
  *Fails when* an order differs.
- **P6 (a)** R3L differs at the least orders of §5:
  - 3 births on the two-knot start under both treatments;
  - 3 births on Ring(5,3);
  - 6 births on the three-knot start under CANCEL-OFFSHOOT;
  - but not on the three-knot start under CANCEL-RETIRE through round 2.
  *Fails when* any of these differs.
- **P7 (b)** Under (ORD, STALL), R1, R2 and R3 build what the rounds build in every order on D2(4,3) and Ring(5,3) through
  round 2. (a) through round 3 and 4 on the two small starts.
  *Fails when* an order differs.
- **P8 (a)** Every law here differs on the seven-knot start, at 2 births. It is the counterexample of the start clause.
  *Fails when* some law matches there.
- **P9 (a)** The control stops short under CANCEL-WAIT on every registered start with a waiter. It builds what the rounds
  build under CANCEL-RETIRE, CANCEL-OFFSHOOT and ORD at every bound searched. *Fails when* either part fails.
- **P10 (a)** R0 differs on every registered start, at 1 to 3 births. *Fails when* some start matches.
- **P11 (b)** Under R2, a member's role computed from the knots within 5 holder steps (7 after one wait) equals its role
  computed from the whole brood, at every state visited in P1 and P5. The study should measure the least such distance for
  d = 1 to 9. *Fails when* the least distance is above 5 (7).
- **P12 (b)** Under (ORD, STALL) no knot past the start is short (each new knot receives at least its demand;
  [SERIAL-REPAIRS](../SERIAL-REPAIRS-20261120-001/outside_class.md) line 51). So R1's guard suffices and the stall is
  decided by the start roster alone. *Fails when* a brood plan under ORD has a short member.
- **P13 (c)** Whether R1 is exact under CANCEL-RETIRE or CANCEL-OFFSHOOT on starts whose broods have groups of three or
  more. There, owing can fall as a brood fills in (a group of three absorbs pairs), so R1 could read a partner as short too
  early and release an offshoot owed to a join.
- **P14 (c)** Whether R2 stays exact for knots that wait twice, or needs its guard widened by two holder steps per wait.
- **P15 (c)** Whether a start clause exists that passes the seven-knot start and stays within a bounded distance. The
  candidate: a dead start knot's met set includes the start waiters it meets.

A result that fails is reported as it is. A law that builds what the rounds build in every order searched has done so to the
stated round only; no statement about every round is made without an argument, which the result note would mark as such.

## Runs and stop rule

One engine written for this study from the frozen text, with its complete rounds checked against ticket A's engine of the
earlier study (births and fresh totals per round) before any search. Each search is expected to take under ten minutes and
8 GB on one process; anything longer goes through the shared runner with a row in the long-running index. The study stops
when every row of the table and every prediction has a verdict. Deviations are recorded in `deviations.md` in the experiment
family before the affected run. That meets the epic's stop in one of its two forms: a law that matches the complete rounds
in every order searched, with a statement of what it reads, or a mismatch for each law of the family.

=== FILE 4: the drafter's note on the two new words ===
# Words proposed by the drafter (for the advisor)

### 1.5 Words proposed for §1.3 and §1.4

| Meaning | Preferred | Second | Why the preference; words ruled out |
| --- | --- | --- | --- |
| A knot none of whose parents is a member | **weaned** | **clear** | "Weaned" says the parents have stopped giving, has one sense and no use in the record. "Clear" is plainer, but prose uses it constantly ("it is clear"), against one meaning per word. Ruled out: "settled" (the guide uses it for a distinction whose value is fixed, INTUITIONS.md line 4111), "ready" (SERIAL-REPAIRS' ready births), "ripe" (my survey's word, suggests the knot is due to act, false for a waiter), "fresh". |
| The closure under taking all children of each parent | **brood** | **kin** | "Brood" is the young of a set of parents, exactly this set. "Kin" suggests parents and ancestors too. Ruled out: "cohort" (a depth layer in SERIAL-REPAIRS), "family" (the definitions' "family of inclusion-maximal met sets", line 30), "generation" (definitions line 121), "level". |

