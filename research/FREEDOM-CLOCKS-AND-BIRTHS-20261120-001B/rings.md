# Ring turns and two birth records

One leftover distinction on a clean ring gives one marked two-parent
birth per turn under parity and not-all-equal. Its period is the ring's
length for an odd ring and half its length for a qualifying even ring.
The maximum immutable arity and maximum parent count give different
records. An actual attachment can erase the whole-cohort count variation
while the marked birth continues.
[Frozen reading](preregistration.md) · [Physical checks and exact counts](../../artifacts/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B-E001_clocks/rings.json)

## The first marked birth and the two records

A two-parent birth takes one distinction from each of exactly two
distinct older knots. On a clean ring each original has one shared
distinction with each of its two neighbours, plus two loose distinctions
to fund the first pairs and any specified leftovers. The witnessed
continuation takes two original meetings per step. Write $L=n$ for
an odd ring of $n$ knots and $L=n/2$ on each of the two continuations
of an even ring. The proof covers odd $n\ge5$ and even $n\ge8$.
Rings of three, four and six fail the pairwise identification
conditions. The all-size argument uses the established identification
of knots with clusters and of true parents with connected deletions.
Every cluster has two extensions along its continuation and the whole
growth has multiple births, so both laws continue with the same
parent rosters.
[Cluster identification](../../proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/proof.md) · [Ring formula](../RING-FORMULA-20261118-001/ring_formula.md) · [Law-specific closure](../NAE-GROWTH-20261119-001/nae_growth.md#why-it-holds)

At parent age $t$, a cluster of size $t+1$ consists of $r$
consecutive original occurrences and $k$ selected copies of the
leftover. Let $M$ be the number of eligible copies and $e$ count
the end originals with a selected copy, for $r\ge2$. Each selected
copy can be deleted. Each end original can be deleted when its own
copy is absent. There are $p=2+k-e$ actual parents and
$f=2+M-k$ fresh distinctions. The immutable arity is $4+M-e$.

A bare run gives one two-parent birth per original phase. A run
with one selected leftover at an end gives two choices across the
phases. A run with both selected gives one birth when the two ends
are a positive multiple of $L$ occurrences apart. Each of its two
actual parents omits one of those selected copies. The one-original
cluster with a leftover at age one has one parent. In the whole
ring this gives $n$ two-parent births at age one, then $n+2$ with
one additional birth at ages $L+2,2L+2,3L+2,\ldots$. A plain ring
gives $n$ throughout. The receiver identifies the extra birth from
its two deletion parents and the present holdings. The age
congruence follows from the identification.
[Ring growth](../RING-GROWTH-20261118-001/ring_growth.md)

The largest arity is $5+\lfloor t/L\rfloor$. A run of length $t+1$
with no selected copies maximizes the number of eligible copies and
keeps both end deletions. The largest parent count is
$3+\lfloor(t-3)/(L+1)\rfloor$ for $t\ge1$. To gain $k\ge1$ parents
over two, the shortest run holds $k$ eligible occurrences with
one original beyond either end. Its length is $(k-1)L+3$ and its
selected copies bring the age to $(k-1)(L+1)+3$. Selected end
copies cancel their own contribution to the parent count and
cannot make an earlier record. Arity records rise at positive
multiples of $L$. Parent-count records above two start at age
three and rise every $L+1$ cuts.

| Original ring | Witnessed period | First extra two-parent birth | Arity record spacing | Parent-count record spacing | Literal ages checked per law |
| --- | ---: | ---: | ---: | ---: | ---: |
| Plain five-knot ring | 5 | None | None | None after age one | 32 |
| Five with one leftover | 5 | 7 | 5 | 6 | 25 |
| Seven with one leftover | 7 | 9 | 7 | 8 | 30 |
| Eight with one leftover | 4 | 6 | 4 | 5 | 21 |
| Nine with one leftover | 9 | 11 | 9 | 10 | 32 |
| Ten with one leftover | 5 | 7 | 5 | 6 | 24 |
| Twenty-three with one leftover | 23 | 25 | 23 | 24 | 32 |

## Several leftover marks

On one clean continuation let $w_i$ count the optional leftover
choices at original phase $i$, modulo $L$. For $t\ge3$ the number
of two-parent births is

$$
N_2(t)=L+2\sum_i w_i+\sum_i w_i w_{i+t-2}.
$$

At age two the last sum becomes $\sum_i\binom{w_i}{2}$ because two
selected copies would come from one original. At age one only bare
pairs count. The eventual count has the same least cyclic period
as the array $w$. To see this, expand $\sum_i(w_i-w_{i+d})^2$.
The autocorrelation is largest exactly at shifts preserving the
array. Any period of the array preserves the count, and any period
of the count must return it to its maximum. On an even ring the
total adds the two continuations. A maximum shift must maximize
each, so the least eventual period is the least common multiple
of their array periods.

If $F(r)$ is the greatest number of eligible copies over $r$
consecutive originals, the maximum arity is $4+F(t+1)$. The
first age with at least $k+2$ parents for $k\ge1$ is

$$
k+1+\min\{r\ge1:F(r)\ge k\}.
$$

The minimum gives the internal run. Add its two end originals
and the $k$ selected internal copies. A single-original cluster
with $k+2$ selected copies can also reach $k+2$ parents, at the
same age as three originals and $k$ copies at the internal original.
If a period of $d$ phases has $J$ eligible copies, then
$F(r+d)=F(r)+J$. The arity maximum rises by $J$ over $d$ cuts.
For $J>0$ the inverse minimum shifts a block of $J$ parent records
by $d+J$ cuts. With two continuations the whole maximum takes
the greater of these records at each age.

Two leftovers at originals 0 and 4 in the eight-knot start give
the sequence $12,14,12,14,\ldots$ from age three. The least period
is two. A five-knot ring with one leftover at every holder gives
the constant value 20 from age three, even though its total births
grow by the golden-ratio factor. The total-birth growth factor of
a clean continuation solves $x^L=(1+1/x)^J$ when $J$ counts the
extras over the full $L$ phases. The record shifts and periods above
come from the parent count.
[Ring growth formula](../RING-FORMULA-20261118-001/ring_formula.md)

## Attach one actual knot

Retain every old distinction of the eight-knot ring with one leftover
at original 0. Attach one new knot by a shared distinction at
original 3. Give it two loose distinctions and add one loose
distinction at each of old holders 2 and 4. For the alternative
attachment at original 2, add the same loose supply at its own two
neighbours. In each case the new knot serves as a parent in two
first pairs, each with one neighbour of its old holder. The added
loose distinctions fund those pairs. Both source projections and
all witnessed rosters pass under both laws.
[Ring with one attached knot](../RING-CORES-20261119-001/ring_cores.md)

The new knot is available through the witness of two consecutive
original occurrences in one continuation. It counts as one extra
choice between those occurrences. A selected copy beyond an end
blocks deletion of that end original. A copy between the originals
is independently removable and does not block either end deletion.
In a run of at least two originals, each end can have at most one
external choice in these fixtures. A two-parent excess above the
baseline occurs with one selected choice at each end. With the
attachment at 3, the pairs of choices are two leftovers, two copies
of the attached knot, and the two mixed orders. Their ages are
respectively congruent to 2, 1, 3 and 0 modulo four. Each residue
adds one birth for $t\ge3$. With the attachment at 2 only the two
unmixed choices occur, at residues 2 and 1. In each attachment two
new pairs occur at age one and the whole two-parent count is 12 at
age two.

| Eight-knot original and its matched change | Whole two-parent pattern from age three | Marked two-end birth | Total-birth growth factor |
| --- | --- | --- | ---: |
| Original with one leftover | 10, 10, 10, 11 | Every four cuts from age 6 | 1.1673 |
| Attachment at 3, same continuation | 13, 13, 13, 13 | Every four cuts from age 6 | 1.3247 |
| Attachment at 2, other continuation | 12, 12, 13, 13 | Every four cuts from age 6 | 1.1673 |

Within the old continuation, clusters that omit the new knot
retain their actual parent sets. This preserves the marked two-end
birth. New options can change their fresh counts. Placement also
changes the maximum arity and maximum parent count over the whole
cohort. For attachment at 3, the maximum arity rises every two cuts
from age one and the maximum parent count every three cuts from age
two. A run of $r$ originals has $r$ positions for leftovers and
$r+1$ positions for copies of the attached knot. Taking four more
original occurrences adds one eligible copy of each. For the
parent maximum use only choices inside the ends. The shortest runs
for one and two internal choices have respectively two and four
originals. Each further pair of choices requires four more
originals. For attachment at 2, the continuation with the attached
knot attains the whole maxima. Its extra choices yield an arity
record every four cuts from age three and a parent record every five
from age two. The specified cases agree with the exact profiles
through age 32, and with the literal growth through ages 11 and 16,
respectively.

## What the readers can see

The full present holdings recover the original ring. In every
positive complete cut all live knots belong to the newest cohort
and directly share distinctions only with older input holders.
Peel the live cohort while retaining its input distinctions at those
earlier holders. Each peel recovers the preceding cut. The original
ring is the first cut with a shared distinction between two live
knots. Equivalently the fewest ordinary sharing steps from a new
knot to the recovered originals equal its age. Each positive sharing
step can change age by only one, and actual parents attain the
bound. Reconstructing the old witnesses and the unique leftover
identifies the two-end birth under renaming and reversal.

The present witnessed end determines the whole two-parent count
and both current maxima for these cases. Each older parent is spent
on at least two children. Distinct parents with any common child
have only one such child. In the identification proof a common
child has the connected union of the two lifted parents, with the
relative lift fixed by their witness. The two parent sets of
children therefore cannot hide one inside another. The number of
maximal witnessed sets containing a query equals its actual parent
count. Adding its loose count gives its arity. Detecting a record
increase also requires the preceding maximum. Identifying the old
witness of a particular continuation uses the full ancestry recovery.
[Unique relative lifts](../../proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/proof.md#lemma-3-consequences)

A single live holder reads its own input count as immutable arity
minus loose count. On the marked five-knot ring a one-end birth at
age five and the two-end birth at age seven both have arity four
and two loose distinctions. Their separate single-holder views are
isomorphic. Those fields alone leave the marked turn unresolved.
[B203 scouting record](../../docs/RESEARCH_GOALS.md#b203--a-clock-inside-the-growing-ring-g5)

With a known one-leftover period, the same fields give a bounded
age estimate. For immutable arity $a$, parent count $p$ and number
of blocked ends $e\in\{0,1,2\}$, substitute $M=a-4+e$ and
$k=p-2+e$. A run with $M$ marked occurrences has length between
$(M-1)L+1$ and $(M+1)L-1$. Intersect with $r\ge2$ and with the
physically eligible end choices. Since $t=r+k-1$, the combined
feasible ages are in an interval of width at most $4L$. The
one-original cases can be checked separately. The replay lists
the feasible ages for its queried holders.

For any fixed radius $R$, use an odd period $L\ge3R+4$ with the
only leftover at phase zero. Compare bare runs of lengths $R+2$
and $R+3$ beginning at phase $R+1$. Every cluster reached within
$R$ actual sharing steps retains at least two originals and uses
only phases 1 through $3R+3$. The marked phase and the originals
are both outside the observations. Adding one occurrence at the
same end of each reached run gives an isomorphism of the rooted
holdings, preserving all recorded co-holdings, arities and loose
counts. The ages and their residues modulo $L$ differ. This rules out a
uniform finite radius across ring lengths. On a fixed plain ring
the same rooted holdings recur at all sufficiently old ages.
For the marked 23-knot ring, the literal age-seven and age-eight
radius-six views each contain 46 knots and are isomorphic under
both laws. The plain five-knot control gives equal 35-knot views.
The tested marked five-knot views differ, leaving open a local
decoder for that particular marked ring.

## Two rings in one growing structure

Join unmarked holders of marked five- and seven-knot rings with
one shared distinction, or through one new intermediate holder.
Fund every first group. Both rings then belong to one witnessed
part. The identified growth contains their old continuations as
families closed under taking actual parents. Additional groups
can change their fresh counts. The marked events keep both
actual deletion parents in their respective families.
[Proved scope for joined rings](../../proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/proof.md) · [Joined-ring preparation](../RING-PAIR-20261119-001/ring_pair.md)

The marked turns have counts $\max(0,\lfloor (t-2)/L\rfloor)$
for $L=5$ and 7. The five-knot count divided by the seven-knot
count tends to $7/5$. The count of parent-maximum gains above two
is zero through age two, then $1+\lfloor(t-3)/(L+1)\rfloor$.
Its ratio tends to $8/6$. At age 4,096 the two marked counts
are 818 and 584, and the respective parent-record counts are 683
and 512. The formulas hold in both joined preparations. In
literal growth at age four the structures have respectively 101
and 90 births and give different fresh counts to the marked
continuations. The selected five- and seven-knot continuations
still give seven and nine two-parent births, respectively.
The literal rosters were checked through age four. The two readings
give different conversions even in one joined structure.

## Validation and scope

The replay matched 9,128 actual births per law across 248 complete
positive cuts. It checked physical source projections, true parent
rosters, fresh distinctions, immutable arities, and both whole-cut
readings. The ancestry reader also recovered its original cut after
independent renaming of knots and distinctions. A separate spot
check fully peeled renamed holdings of the marked five-knot ring,
both attached eight-knot rings and both joined controls. It recovered
1,724 selected births and ten marked events across the two laws
using the original loose supplies and the recovered actual parent
sets. Individual literal cohorts were capped at 128 births. An exact binomial profile checked
the displayed formulas through age 32 independently of individual
cluster enumeration. The order-three partnered runaway provides a
separate explosive comparison. Every positive birth there has at
least three parents, so this two-parent event never occurs.
[Runaway control](../FOUR-READINGS-20261120-001D/deep_explosive.md#partnered-runaway)

The prepared original holdings, chosen turn and observer are
scaffolds. The all-size formulas, attachment effects and count
ratios shown here concern ordinary parentage on the stated classes
of holdings. Independent referee pending.

The replay took 10.14 seconds and 49,220 KiB peak memory. Its
receipt SHA-256 is `82bd3cd8b02e5e81a651ae0ddf350d43e566e4498ff5ae89ddf1a328c2c13f44`.
A replay with a different Python hash seed reproduced the receipt
byte for byte. [Replay code](../../experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B-E001_clocks/rings.py)

```bash
PYTHONHASHSEED=7 .venv/bin/python -B \
  experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B-E001_clocks/rings.py |
  cmp - artifacts/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B-E001_clocks/rings.json
```
