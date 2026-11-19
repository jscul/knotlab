# Exact loose frontiers for the binary third three-fresh join

A completed history can shrink at most four times. Four is attained
only when the special binary three-fresh join precedes every shrink.
Exactly one frontier record at five loose distinctions has a legal
triple, and its shortest history has width 30. At four loose
distinctions there is one record, with only a binary continuation.
The width-30 history has a five-bit bond on the whole ordinary shore
while a triple is legal. A width-42 history has the same coexistence
with a proper shore.

## The finite state and its coverage

After the first two unary three-fresh births, the second can have
used the seed or the first child. Both possibilities have seven
loose bits. The special binary three-fresh addition increases the
count by one. Each other binary addition preserves it, and a
three-parent two-fresh addition reduces it by one. Thus the loose
count is \(7-t\) before the special join and \(8-t\) after it,
where \(t\) is the number of shrinks so far.

Use the predecessor's exact state. Store each live holder's loose
count, their ordinary adjacencies, and the set of distinct
projected neighborhoods of exhausted sites with at least two
live neighbors. A pair has a witness precisely if some live
adjacency row or some retained exhausted neighborhood contains
the pair. A triple is allowed if it passes that test on all three
pairs and no row or neighborhood contains all three. This is
independent of which loose name is taken from a holder.

To advance, attach the new holder to the chosen parents, decrement
their loose counts, and record the complete neighborhood of each
newly exhausted holder before projecting to the new live set.
Older exhausted holders cannot gain a neighbor. Hence remembering
their projected subsets suffices indefinitely. Keep an additional
record of the number of shrinks before the special join, or the
flag that it remains unused. A fixed-width bound of eight live
holders and the finite set of projected neighborhoods make this
quotient finite. None of its transitions places a bound on future
depth. [Predecessor quotient proof](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#all-histories-have-at-most-two-shrinking-joins)

The check closes both starts under every admissible holder choice
and fresh count. At every reached record it rebuilds a literal
representative and compares the complete parent roster with the
inherited literal rule. Each newly reached representative is
created by a legal literal join. The entire pre-special fixed
point agrees with the archived J digest. The full closure has
28,108 records and 181,530 transitions.

## Shrinks and positive menus

Before the special birth, the 1,118 records from J have at most
two shrinks. After the special birth the counts are as follows.
Earliest widths are determined by breadth-first search, since
every completed history with the same number of junctions has
the same width.

| Shrinks before special join | Total shrinks | Loose bits | Records | With a legal triple | Earliest width | First positive width |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 8 | 19,356 | 7,062 | 12 | 20 |
| 0 | 1 | 7 | 4,528 | 1,506 | 22 | 24 |
| 0 | 2 | 6 | 455 | 96 | 26 | 26 |
| 0 | 3 | 5 | 34 | 1 | 28 | 30 |
| 0 | 4 | 4 | 1 | 0 | 32 | — |
| 1 | 1 | 7 | 2,025 | 321 | 24 | 26 |
| 1 | 2 | 6 | 289 | 26 | 28 | 38 |
| 1 | 3 | 5 | 27 | 0 | 40 | — |
| 2 | 2 | 6 | 248 | 26 | 30 | 42 |
| 2 | 3 | 5 | 27 | 0 | 44 | — |

The unique positive five-loose record has four holders with
multiplicities \(1,1,1,2\). The three single loose names are
17, 25 and 27 in the width-30 representative, and the last holder
has 28 and 29. Its only three-parent group gives the two choices
\(\{17,25,28\}\) and \(\{17,25,29\}\). In either case the other
two loose bits have adjacent holders, so they cannot be a legal
binary choice. None of the legal binary successors can return to
the positive record along binary continuations. A shrinking successor
has four loose bits and no legal triple. Thus every strict continuation
from the positive five-loose record has an empty triple menu.

The reverse binary graph reaching that positive record is also
a singleton with no transitions. A last binary addition would
have made the unique two-loose holder. That holder has one live
neighbor, so only one of its two parents could have exhausted
its loose bits at that birth. Yet there are two distinct
recorded exhausted neighborhoods containing the holder. Each
would have needed to gain the new holder at that birth, since
already exhausted sites cannot gain neighbors.

The four-loose record has holder multiplicities \(1,1,2\) and
one legal binary holder group. Its successor is the same record.

## Complementary parent choices

For each possible special birth and each allowed source move
after that birth, subtract one from the loose counts of its parents.
The resulting counts describe a legal complementary move exactly
when they are all zero or one and the positive holders form a
legal group of size one, two or three. This tests all literal
choices by multiplicities, including the use of different loose
bits at the same holder on the two sides.

There are exactly three source move records with a complement.
All start at six loose bits and use complementary triples on the same
three holders of two bits apiece. There is one such record for each
possible shrink count before the special join. Their first widths
are 30, 38 and 42, respectively. Each has eight distinct literal
source choices. There is no complementary move at the special birth
or at either of the four- or five-loose frontiers.

## Named five-bit bonds at positive sources

For the width-30 source, use the whole ordinary shore. Its five
boundary bits are \(\{17,25,27,28,29\}\), with the two legal
triples above.

In the width-42 source the special join follows two shrinks
and the initial twelve junctions retain their boundary
\(\{22,23,24,25,26\}\) as a proper shore. The final source
admits four triples, including \(\{35,38,40\}\).

The checker reconstructs each cut in the complete literal wired
graph and verifies connectivity of both shores, which makes it
a bond. The two examples and the frontier results concern the
presence of actual cuts and legal triples in the same source.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001L/VARIABLE-OUTPUT-READER-20261118-001L-P001_binary_third/frontier.py
~~~

[Replay checker](frontier.py) · [Fixed-point counts and named histories](frontier.json)
