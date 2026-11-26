# The late views of a growth from its start alone

Epic `LATE-VIEWS-20261126-001`, at the coordinator's go-ahead on the selected direction of
[`LAST-MERGE-20261126-001`](../LAST-MERGE-20261126-001/decision.md). A check by the thread, not registered; open.

## Where it starts

The look-alike study found that a local reader's view of a grown start, each local type of birth (kind, parents,
fresh distinctions, places) counted per round, becomes polynomial in the round, and that these late views decide which
starts look alike; the last-merge study found that the view settles three rounds after the last fall in births. Both
read the view off the grown counts. This study asks for the late view from the start alone.

**Exploration (not a test).** On every census start of up to five knots of dimension two, the late view is two-parent
joins with two fresh distinctions growing at a fixed slope (1, 2, 3, or 2^k in hub families), plus constant counts:
one-parent offshoots (2, 3 or 4 a round) and sometimes a group of three with a two-parent join of three fresh
distinctions, or block-type joins. Neither the offshoot constant nor the slope is a function of the number of leftover
distinctions after round 1 (for example, starts with two leftovers show (offshoots, slope) = (2, 1) in 211 cases and
(4, 2) in 26).

## The route (advisor consulted)

The advisor ([question](advisor_question.md), [answer](advisor_answer.md)) proposes a typed transfer matrix on the
map of joins: by the proved identification, round t's births are the connected clusters of t + 1 members of the
unrolled map, and a birth's type is read from its cluster (parents: members whose removal keeps it connected; fresh
distinctions: its demand). Counting clusters by type per size, as a generating function computed on the finite map,
would give the late view exactly, with the slope and the constants as its poles.

**One premise to check before building.** The advisor assumes that dimension two means one cycle in the map with
finite pieces hanging off it. In the record, dimension two also arises with no cycle at all, from two endless chains in
one connected part (lesson 8.2: two touching three-place knots), so the enumeration must handle endless chains, not
only a ring. The first step is to write the typed cluster count for the acyclic case with endless chains (the class of
CHAIN-IDENT and RELAY-IDENT), check it against the grown counts of every dimension-two census start of up to five knots,
and only then freeze it.

## Next bounded step

1. Build each start's map of joins from round 1 (members, groups through a common knot, leftover members), and its
   unrolled map to depth 30.
2. Enumerate connected clusters by size and type (parents, demand) directly on the unrolled map; compare with the grown
   late views of the census of up to five knots, type by type, round by round.
3. If they agree, replace the direct enumeration by its generating function, freeze it with the advisor, and test on a
   seeded held-out sample of six-knot starts, scored as exact matches past the predicted settling round (the
   advisor's stop rule).
