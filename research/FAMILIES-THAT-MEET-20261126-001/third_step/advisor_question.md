You are reviewing, cold, a short research note before it is committed. Be adversarial: find holes in the argument,
claims stated one step beyond what was checked, and wording that says more than the evidence. Answer in at most
700 words, as a numbered list of concrete findings, each with the change you would make. Do not praise.

## The growth law (a program; I quote its round exactly)

Knots hold distinctions. A distinction held by one knot only is that knot's *loose* distinction. A *member* is a
knot with at least one loose distinction. One round:

1. For every knot w, the met set of w is the set of members that share a distinction with w. Two members are
   joinable when some met set holds both. Groups: the cliques of three or more joinable members that are not
   inside one maximal met set, and every joinable pair not covered by such a clique.
2. owe(u) = number of groups holding u; h(u) = number of loose distinctions of u. u is *short* when owe(u) > h(u).
3. A group with a short member is cancelled; the others are kept. Each kept group makes one new knot (a join) whose
   parents are the group's members. A member that is not short gives one loose distinction to each of its joins
   and makes one offshoot (a new knot with that one parent) for each loose distinction left over; so it gives away
   every loose distinction it has. A short member, by the treatment in force: retires (its loose distinctions are
   barred for good), or makes only offshoots (one per loose distinction), or waits (keeps them, stays a member).
4. A new knot holds the distinctions its parents gave it and f fresh ones of its own. f = min(max(D, 3 - p, 1), c)
   where p is the number given, c is the cap of the law (no cap: the "ordinary count"), and D is the number of
   groups it would be in among this round's new knots and the waiting members (computed by rule 1 on them).
Nothing else changes a holding (no birth ever takes a distinction none of its parents gave it).

## The study

Start: 9 original knots v, r1, r2, r3, s, t, b0, b1, b2 with 12 pairs (v-r1, r1-r2, r2-r3, r3-v, v-s, t-v, s-b0,
t-b0, s-b1, b1-t, t-b2, b2-s), each pair met through a spent start knot, each original holding as many loose
distinctions as its pairs. To b2 a tail is added: b2 - q1 - ... - qd, and at qd m rings of four (qd-x-y-z-qd), so
qd has 1 + 2m pairs. For one d the starts m = 1, 2, 3 are the same out to d - 1 steps beyond b2.
Sides, by original ancestors: *second* = has b2 or a tail original among its ancestors; *first* = has b1 and none
of those; *rest* = neither. "Outside" = first or rest.
Read: for each d in 1, 2, 3, cap in none, 4, 5, 6, 7, 8, 9, 10, 12, treatment in retire, offshoots, wait, and each
pair of m: the first round in which the first side's births (as the sorted list of (kind, number of parents,
number of places, f)) differ. 243 starts, each read as many rounds as fit in 8 GB (7 to 14 rounds), 243 pairs.
Also recorded each round: the number of groups holding both an outside member and a second-side member ("groups
joining the sides"), and a digest of every outside birth by name (a knot's name = how it was made: kind, parents'
names, index among equal births of the round) with its f.

## Results

- No cap: never a short member; the first side is the same for the three m at every d through 8 or 9 rounds
  (27 pairs); groups joining the sides never reach zero.
- d = 1: differs at cap 9 from round 5 (9 of 9 pairs), cap 10 from round 6 (9 of 9), cap 12 from round 7 or 8
  (8 of 9), and with waiting only at cap 6 (2 of 3 pairs, round 7) and cap 8 (3 of 3, rounds 7-8). 31 of 81 pairs.
- d = 2 and d = 3: no pair differs (0 of 162) in the 7 to 14 rounds read.
- Retire and offshoots: in every start read that far, the groups joining the sides fall to zero in round c - 1
  (caps 4 to 9: 106 of 106 starts read to that round). With waiting: round 7 at cap 4, round 6 at cap 5, not
  within the rounds read at caps 6 and up. 763 rounds were read after a start's count reached zero; it is zero in
  all of them.
- Round-by-round comparison by name at cap 9, retire, m = 1 against 2. d = 1: second-side knots made from b2 and
  not the tail first differ in round 4; in round 5, 32 groups hold a first-side member together with a
  second-side member that is short in one start only (or is in one start only); in 28 of them no other member is
  short, and the first side has exactly 28 births in m = 2 that m = 1 lacks (all offshoots). d = 2: such
  second-side knots first differ in round 6 (16), 192 differ in round 8, 1,440 in round 9; no group holds one of
  them with a first-side member in any round through 9, and in rounds 8 and 9 no group joins the sides at all.

## The argument I want to state (marked as an argument, not refereed)

C1. From round 2 on, a member that has not yet acted shares distinctions only with its parents (it holds what
    they gave it and its own fresh ones, and nobody takes). A member acts in at most one round (it then gives
    away or bars everything), so all children of one parent are born in one round. Hence two members are joinable
    only if they are children of one parent, born in the same round.
C2. So a group joining the sides (outside member L, second-side member K) consists of children of a parent w; w is
    outside (it is L's ancestor), and K has a second-side parent too, so K is the join of a KEPT group that joined
    the sides in the round w acted. Hence: if in some round (2 or later) no group joins the sides, none does in
    any later round. (For members born before that round and still waiting: they were joinable in that round too,
    and any two joinable members are together in at least one group.)
C3. Once no group joins the sides, every met set is all outside or all second-side, so the outside's groups,
    owing, shortness, births and fresh counts are functions of the outside alone. So two starts whose outside is
    the same knot for knot (by name and f) up to such a round, in both, have the same outside in every later
    round.
I would then write for a pair: "same for good" when both starts were read to a round with no group joining the
sides and their outside digests agree in every round read (118 of the 162 pairs at d = 2, 3 and 36 at d = 1);
"same to round n" otherwise (the sides still joined: not seen within those rounds, and no more).
C1 to C3 restate, for sides, a statement an earlier study of mine recorded for "parts" (components of joinable):
"parts act alone past the start; the descendants of two parts are never joinable" under laws that take nothing.

## Headline I propose

"On this start, with laws that take nothing: without a cap nothing is ever short and nothing is felt, though the
two families stay joined; with a cap, short knots let one side change the other, but the same cap parts the
families for good in round c - 1 (retire, offshoots). A change one step beyond b2 arrives in time at caps of 9,
10 and 12; a change two or three steps beyond does not arrive at any cap from 4 to 9, and at caps of 10 and 12
it was not seen in the 8 rounds read."

## Questions

1. Is C1-C3 sound as stated for all three treatments (especially waiting), given the round as quoted? Name any
   gap (rule 1's cliques, rule 4's D, the round-1 originals, anything).
2. Does "same for good" follow from what is recorded (digests of outside births by name with f, equal in every
   round read; zero groups joining the sides in some round read, in both starts)? What else must be equal?
3. Where does the headline say more than the results? In particular "does not arrive at any cap from 4 to 9" for
   d = 2, 3, and "the same cap parts the families for good in round c - 1".
4. One cheapest further check you would run before committing (each start costs seconds to a minute).
