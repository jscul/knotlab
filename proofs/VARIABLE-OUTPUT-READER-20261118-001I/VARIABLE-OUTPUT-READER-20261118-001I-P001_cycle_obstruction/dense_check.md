# Short equations in a six-site four-place block

The ordinary graph on these six four-place sites has parts
\(\{t,w,b\}\) and \(\{p,q,c\}\), with every meeting across the parts
except \(bc\). Its six stars cover eight internal distinctions and eight
external slots. This maximal two-connected block can lie in a larger
component of the graph on four-place sites.

Under the short-shore and common-equation hypotheses, this block cannot
support a shortest extra equation of size six. The check covers arbitrary
outside incidences consistent with ordinary simplicity and bipartiteness,
and every placement of the unique ternary seed.

## From a competing presentation to the finite check

Suppose the source has no bond of size at most six with three or more
sites on its ordinary shore. Assume all source equations also hold in
the rival, the seed gives the only ternary equation of the rival, and
every source site contains at most two bits of any shortest extra word
of size six. The latter bound follows from minimum weight if every
source site has at most five places. Each weight-six translate of an
extra word by common source equations is a rival bond. Its pairs must
all have \(K\le6\) in the source if the tables agree through six.

Delete the possible single seed bit from a shortest extra word \(W\).
The remaining set \(Q\) has at least five bits. A pair of seed-free
bits with \(K\le6\) must share a holder or have adjacent four-place
holders. A bond of that size either has one site or is the sum of two
adjacent stars. The degree possibilities for the sum are two four-place
stars, or the seed with a four- or five-place star. In the latter case
both seed-free bits would share the nonseed holder. A bit of \(Q\)
without a four-place holder could meet at most two other bits of \(Q\),
one per holder. Hence every bit in \(Q\) has a four-place holder.

Across distinct four-place components a pair can match only through
a shared non-four-place holder. Each bit has at most one such holder,
and therefore can have at most one partner across components. With
five or more bits this places all of \(Q\) in one component.

The block confinement lemma places every bit of \(Q\) at a vertex of
one maximal two-connected block. If it is the six-site block above,
its sixteen slots include all bits of \(Q\). A bit of \(W\) outside
these slots can only be at the seed. The checker adds one slot for
that possible bit. Its other holder, if any, is ignored and all pair
tests involving a seed bit are allowed. These relaxations only add
possibilities. When all three seed slots are at the block, the extra
slot is unavailable. [Block confinement](blocks.md)

The exterior coincidences between nonseed slots are given by a
partition on each color. At any exterior holder, bipartiteness
restricts its incident slots to one color and simplicity permits at
most one from a corner. A private or loose bit can be treated as a
singleton. The universe of partitions allows groups of three at
distinct corners and enforces the cap of two selected bits for every
such holder. It can also include coincidences that lack a lawful
serial history. The seed can occupy any one group of up to three
ports from distinct corners of one color, or occupy no local port.

The checker forms all 64 sums of the six local stars and translates
each six-subset by every sum. A shorter translate excludes the word.
Every translate still of size six must have at most one seed bit,
obey the nonseed holder bound, and pass every seed-free pair test.
Two such bits are compatible precisely if their holders in the block
coincide or are adjacent, or if they share an exterior holder. The
sum of two adjacent four-place stars is a six-bit bond, since otherwise
it would need two disjoint ternary bonds. Any immediate exterior
four-place neighbor meets just one corner of the block. A route
between distinct corners through one or two exterior four-place
vertices would enlarge the two-connected block, so such vertices add
no other compatible pairs. Simplicity then makes every actual exterior
four-place holder a singleton class on the local slots.

## Counts

There are 12,376 six-subsets of the sixteen slots and the seed proxy.
Exactly 1,684 pass the minimum-weight test under all 64 translations,
including 80 that use only component slots. The arbitrary exterior
comparison gives the following counts. Every word passing the initial
tests fails a seed-free pair test in some tied translate.

| Seed ports at the component | Seed placements | Exterior models | Initial passes | Final survivors |
|---:|---:|---:|---:|---:|
| 0 | 1 | 100 | 7,524 | 0 |
| 1 | 8 | 320 | 20,688 | 0 |
| 2 | 10 | 180 | 7,752 | 0 |
| 3 | 4 | 40 | 96 | 0 |
| **Total** | **23** | **640** | **36,060** | **0** |

For the repeated histories, only the \(qr,cr\) slots share an
outside holder. The first component attaches \(t\) to the seed and
the later components have no seed slot. There are 32 and 48 initial
passes in the two models respectively, and zero survive. The script
checks the projection from all seven components in the archived
one-, two-, and four-stage histories. Removing the seed-free pair
test makes a control word pass every remaining test.
[Named repeated histories](families.json)

In particular, take a nonshrinking source with a unique ternary seed,
maximum degree five, and four-place blocks with cycles all of the
shape above. The short-shore and through-five equation arguments
apply, so every source equation is common and a shortest extra
rival equation would have size six. The block exclusion precludes
it. Equality of equation spaces then forces equality of actual
stars by the missing-site parity argument. Thus the repeated family,
at every finite length, has the same full join menu and actual
junctions as any reachable rival matching through \(K=6\).
[Short-shore and source equations](nonshrinking.md) · [Actual-junction recovery](cycle_inverse.md#actual-supports-and-next-groups)

~~~sh
.venv/bin/python -B proofs/VARIABLE-OUTPUT-READER-20261118-001I/VARIABLE-OUTPUT-READER-20261118-001I-P001_cycle_obstruction/dense_check.py
~~~

[Replay checker](dense_check.py) · [Exact counts](dense_check.json)
