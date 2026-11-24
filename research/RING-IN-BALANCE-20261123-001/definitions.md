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
