# The loose frontiers with a third three-fresh join

The exceptional join has three parents and three outputs. Its birth
can precede either of two shrinking joins, or occur between them.
It cannot follow both. A completed history has at least five loose
distinctions and at most two shrinking joins in total. At five loose
distinctions, the triple menu is empty, and all three outputs of the
exceptional site have been consumed.

## Why this is an all-depth check

Start after the first two unary three-fresh additions. There are two
initial incidences, depending on whether the second addition uses
the seed or the first child. Both have seven loose distinctions.
A binary two-output join and a three-output triple leave that
count unchanged. A two-output triple decreases it by one.

A record has the loose count of every still available holder,
ordinary adjacencies among these holders, and the set of subsets
having an exhausted common neighbor. For the latter, the record
stores each exhausted site's full projected neighborhood of size
at least two. Multiplicities of equal neighborhoods do not affect
the presence of a pair witness or a witness common to three.
At a join, take one bit per parent and add the new holder next
to its parents. Preserve the projected neighborhoods of newly
exhausted sites. Further projection suffices for all old exhausted
sites, since they can never acquire another neighbor. The record
therefore determines both legality and its successor exactly.
[Predecessor construction and fixed point](../../VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/family.md#all-histories-have-at-most-two-shrinking-joins)

The record also includes the count of shrinks before the exceptional
birth, or a flag that the birth is still available. When it has
occurred and some output of that site is loose, the record
distinguishes its holder. This last mark determines which legal
triples can use one of those outputs. The mark can be forgotten once
the holder exhausts its outputs. All records are quotiented by
holder renamings that preserve their stored information.

There are at most seven live holders, a finite set of possible
neighborhoods, and at most seven prior shrinks, so the possible
records form a finite set independently of depth. The algorithm
closes the transitions starting from both initials. It checks
every permitted parent group and every actual transition against
a literal history using the inherited parent law. Nonempty loose
groups at a holder use all available names interchangeably for
this law. It can therefore replay one literal choice to verify
each transition, and count all choices by multiplying their
holder counts.

The closed set has 5,722 records and 25,345 edges with the
exceptional holder marked where it is still live. Forgetting
this mark gives 3,581 records and 16,393 edges. The predecessor's
1,118 records and 4,997 edges before the exceptional birth
reproduce the archived full fixed-point digest. The two archived
width-19 prefixes that can take the minimum shrinking triple
also replay with three outputs and appear in this fixed point
at width 22.

## Shrink order and live triples

The counts in the table retain the number of prior shrinking
joins and omit the mark on the exceptional holder. The last
column uses that additional mark to verify the first legal
triple containing a loose output from it.

| Shrinks before the exceptional join | Shrinks after it | Loose bits | Records | With a legal triple | First source width | First width of a legal triple using its output |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 7 | 1,866 | 314 | 22 | 26 |
| 0 | 1 | 6 | 304 | 26 | 28 | 36 |
| 0 | 2 | 5 | 27 | 0 | 38 | — |
| 1 | 0 | 6 | 239 | 26 | 28 | 40 |
| 1 | 1 | 5 | 27 | 0 | 42 | — |

Before the exceptional birth the 20 records with two shrinks
all have five loose distinctions. None admits a triple. Thus
an exceptional birth after two is impossible even after a
binary continuation. At six loose distinctions after the
exceptional birth, some records permit a triple and a second
shrink. At five all subsequent legal source moves are binary.
The records giving minimum widths are found by breadth-first
traversal, and their named histories are saved with the counts.

## Complementary choices from the same frontier

For a source parent group \(P\), let \(\ell_i\) be the current
number of loose bits at holder \(i\). The complement can be
consumed by a single rival move exactly when
\(\ell_i-\mathbf 1_{i\in P}\) is zero or one for every holder,
and the set \(Q\) with value one is an allowed parent group.
This includes rival unary choices. After a literal selection
for \(P\), the names for \(Q\) are the remaining loose bits.

The comparison tests 320 exceptional births and 11,076
post-birth source moves on the unmarked records. At seven
loose bits no two legal input counts can exhaust the frontier.
At five bits such a cover would require a triple, and the
closure has none. At six the only possible cover uses two
triples. There is no such cover at the exceptional birth.
After that birth there are exactly two records with a cover,
one for each order of the exceptional birth and the first
shrink. Both records have three holders of two loose bits
each, with a separate witness for every pair and none for
all three. Each cover uses the same three holders for its
two groups, choosing opposite bits at each. There are eight
literal source choices per record.

The two saved prefixes have widths 36 and 40. Completing either
complementary input set with the same two fresh bits gives
different actual last junctions and an empty triple menu on
both sides. The two proposed last equations differ by the sum
of all prefix equations, which is the six-bit loose boundary.
This establishes equality of their full allowed-state spaces
and full pair tables. The equality uses the literal parity
equations. The frontier closure establishes permissions and
their complementary choices.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001K/VARIABLE-OUTPUT-READER-20261118-001K-P001_third_three_fresh/closure.py
~~~

[Replay checker](closure.py) · [Fixed-point counts and literal histories](closure.json)

## Menus immediately after the exceptional birth

On each old predecessor record, give the same three fresh names to
every lawful literal triple of input bits. Compare the resulting
menus on the same name set. The quotient suffices for this comparison
at arbitrary depth. Every future input is one of the old loose bits
or a new fresh bit. A bijection of holders and their loose names
preserving the old record preserves every parent's witnesses before
and after each possible birth. The two completions then have their
menus transported by this same bijection.

At six old loose bits, 25 of 238 records permit the exceptional
birth. There are 61 literal input sets and 79 pairs of input sets
within single records. Every new menu is empty. At seven old loose
bits the 199 eligible records have 508 literal input sets. Forty-one
produce a live menu. Among 735 within-record comparisons, 128 give
different named triple menus. The first disagreement has a
width-23 prefix and a width-26 completion. The named histories
and differing marks are recorded for pair-distance comparison.
[Replay checker](birth_menus.py) · [Menu counts and adverse choices](birth_menus.json)

## Alternate third three-fresh births

A third three-fresh binary addition raises the loose count by one.
A unary one raises it by two. Using the same frontier recurrence,
breadth-first search finds a positive triple after two shrinks in
the binary branch at width 26, and after three shrinks in the unary
branch at width 30. The named marks are \(\{13,21,23\}\) and
\(\{21,23,28\}\), respectively. These are the shortest qualifying
witnesses across both initial shapes. The search stops at the first
positive state in each branch.

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001K/VARIABLE-OUTPUT-READER-20261118-001K-P001_third_three_fresh/alternate.py --shortest
~~~

[Replay checker](alternate.py) · [Literal histories](alternate.json)
