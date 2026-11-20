# One bond containing several original marks

With two five-rings attached four original knot steps apart, loading the
first ring changes a simultaneous reading of three marks between the
rings. At the first completed layer, the smallest physical bond
containing \(e_4,e_5,e_6\) has size **14 quiet and 16 first-loaded**,
whether the second ring is quiet or loaded. The three separate bond
distances remain **5, 7 and 3**, in \((e_4,e_5),(e_4,e_6),(e_5,e_6)\)
order.

| Preparation and fixed marks | Quiet | First only | Second only | Both |
| --- | ---: | ---: | ---: | ---: |
| Four-step double, \(e_4,e_5,e_6\) | 14 | 16 | 14 | 16 |
| Four-step double, \(e_5,e_6,e_7\) | 14 | 14 | 16 | 16 |
| Four added knots at each end, \(e_8,e_9,e_{10}\) | 14 | 16 | 14 | 16 |
| Same padded double, \(e_9,e_{10},e_{11}\) | 14 | 14 | 16 | 16 |

Both triples lie between the attachment positions under the registered
same-side rule. Each contains a mark held by its responding attachment.
The quiet witness for \(e_4,e_5,e_6\) uses \(b_4,b_6\) and their joint
child. The loaded witness uses \(b_5,b_7\) and their joint child. The
quiet witness includes the responding attachment itself and both
minimizations range over the full stage. The result establishes a
same-side reading of fixed marks. A strict observation confined to the
marked-side ancestry or a fixed-radius observation at arbitrary offset
would need its own certificate. The padded result increases the
distance from the physical ends while preserving the offset to the
responding attachment. [Frozen readings and offsets](definitions.md)

## Why the three-mark reading changes

The three original crossings require alternating sides for
\(b_4,b_5,b_6,b_7\). Two assignments remain on these four holders
after the auxiliary exterior names the outer side. If \(b_4,b_6\)
are both inside, \(b_5\) and \(b_7\) are outside. The first-layer connection between \(b_4\)
and \(b_6\) across \(b_5\) must use their binary child. Another retained
extent of the path cannot replace this connection. After the off-path
ring pieces are removed by the first-layer cut argument, old path
connections have one step and binary connections have two. The only
such connection across \(b_5\), with that knot outside, goes from
\(b_4\) to \(b_6\).

The quiet child on that pair has four fresh distinctions. The old
crossing cost is 12, consisting of six used original loose distinctions,
four old path crossings, and two original ring crossings at \(b_4\).
Putting the child inside adds two, because it contributes four fresh
crossings and removes its two crossings to the old parents. The first
load vetoes that child. The alternative coloring puts \(b_5,b_7\)
inside and uses their common child across \(b_6\). Both parents stay
cold, and their child has six fresh distinctions. There are eight used
original loose distinctions and four old path crossings, plus four
from inserting the child. Thus this choice costs 16 in every arm.
Keeping more old path holders beyond either selected pair cannot reduce
these values. It cannot remove the required gap, bridge prices are
nonnegative, and moving a boundary to a physical end can save at most
one crossing for at least two additional original openings. Off-path
quiet connections at an omitted attachment are covered by the direct
binary connection between its path neighbors. The earlier cut
reduction removes entire attached ring pieces without an increase for
any prescribed set of path marks. This also proves the reflected
example near the second attachment. [First-layer cut reduction](../OLD-MARK-GEOMETRY-20261119-001/distances_proof.md)

## Coverage and controls

On the single one-spare ring, the exact core panel has 72 pairs, 224
triples and 496 quadruples. Every pair has a finite, equal reading in
both arms at ages zero through two. All of the triples and quadruples
have infinite reading at source. With the auxiliary exterior outside,
the inside holders of an original connected cut meet the path in one
interval. At most the two ends of that interval can supply original
path crossings. Every one of those registered triples and quadruples
has a finite bond at age one and at age two. Every matched quiet and
loaded reading agrees at both ages. The 40 focused later queries,
including 17 pairs taken from the larger sets, also agree through age
six. The original far pair \(e_8,e_{12}\) stays at bond distance 9.

The translated registry uses the fixed displacements and offsets from
the contract. Padded single attachments, the eight-step doubles and
the doubled-meeting sources have no strict difference in their tested
sets at ages one and two. The two three-mark effects in the first table
are the only first- or second-layer changes among the translated
two-ring controls. Each is additive under the two load switches.
Infinity on the source triples and quadruples leaves their numerical
factorial contrast undefined.

The focused later panel is exact through age six for the four doubles
and the three padded singles. Each padded single has 35 named sets,
with 26 additional pairs from the larger sets. The base doubles have
18 and 25 named sets for the four- and eight-step placements. Their
padded copies have 27 and 43. The same two triples give the only
strict size changes in each four-step preparation. All finite
factorial interactions in this focused panel are zero. The full
pair vectors stay equal in each matched comparison.

An independent run on the two changed triples retains the values in
the table at every reached positive age. The four-step double reaches
ages 6, 7, 7 and 10 in quiet, first-only, second-only and jointly
loaded order. The padded double reaches 6, 7, 7 and 8. The short arms
hit the physical limits of 6,000 knots or 32,000 distinctions. The
padded jointly loaded arm reaches its requested age eight. The
comparison of all four arms therefore applies through age six.

The registered dose uses all 64 physical assignments on each of the
unmodified and padded doubled-meeting sources. The words fall into 17
source activity sets. Words with the same activity set share growth
geometry because all later growing ends are cold. The receipt restores
one vote per physical assignment when making a dose count. Every
registered matched size is equal across the 64 assignments at ages
one and two, on each of the two fixed physical sources.

## Exactness

A bond is a minimal nonfree projection in the allowed parity relation.
Connecting every loose distinction to one auxiliary exterior makes a
parity sum of a set of knot equations its cut. A nonempty cut is
minimal precisely when both sides are connected. For each marked
distinction, its two holders must be assigned opposite sides. Other
distinctions may also cross. The common reading is the least number of
distinct crossings. For a pair, subtract one to obtain bond distance.
The exterior is part of this cut bookkeeping only.

The separator computation stores holder colors and the connected
pieces of those colors at a separator. At the earlier eliminated
holder of a marked distinction, require its crossing. It can then
forget that mark requirement while retaining the connectivity state.
That lets two different queries share exactly identical subproblems.
A prior checked witness restricts the cost only when it is rechecked
on the current physical frame. If no prior witness exists the ceiling
is the number of all physical distinctions, which every cut satisfies.
An empty certified minimum at this full ceiling means infinity.
Resource limits merely leave a bound.

The fallback verifies an integer flow of matching value for each
relaxed minimum cut with the marked holders pinned to opposite sides.
A disconnected piece of one side must have a pin, since moving a
pinless piece out would strictly lower the cost. Branch over which
previously unpinned boundary holder first connects that piece to
another same-side pin. The remaining open branch bounds give a lower
bound at the cap. Independently recomputing the parity sum and the
crossings of every stored witness checks both connected sides and
every required mark. A separate tiny control enumerates literal allowed
assignments and tests every projection, yielding 671 agreeing queries
of sizes two through four across three wirings with finite and infinite
cases. Transporting every knot and distinction name in a single-ring
frame preserves the selected pair, triple and quadruple readings. For
the two changed triples, independent integer flows match the separator
minima at ages one and two. All sixteen age-one triple-arm readings also
survive transport of every name. A separate parser and connectivity
checker validates the literal crossing lists from all reached positive
layers for both triples.

The first later double scan left 172 bounded readings, all at age four
in the jointly loaded arms. Lowering the separator width limit from 14
to 12 sent those expensive frames directly to the integer-flow
fallback, which resolved all intervals without changing any certified
value. The fallback uses at most 1,000 integer relaxations per query
on the doubles. The separators use at most two million transitions
per query. The receipts retain the physical stage sizes and any limits.

Replay from the repository root with the following commands.

~~~sh
E=experiments/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side
A=artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side
.venv/bin/python -B "$E/common_bonds.py"
.venv/bin/python -B "$E/common_bonds.py" --panel translated --through 1 --seconds 25
.venv/bin/python -B "$E/common_bonds.py" --panel translated --cases P4 P8 P16 T4 T8 PT4 PT8 J1x2 PX4 B --through 2 --seconds 40 --out "$A/common_bonds_translated_age_two.json"
.venv/bin/python -B "$E/common_bonds.py" --panel later --through 6 --seconds 23 --flows 1000
.venv/bin/python -B "$E/common_bonds.py" --panel later --cases P4 P8 P16 --through 6 --seconds 10 --width 12 --flows 750 --out "$A/common_bonds_pads_later.json"
.venv/bin/python -B "$E/common_bonds.py" --panel later --cases T4 T8 PT4 PT8 --through 6 --seconds 17 --width 12 --flows 1000 --out "$A/common_bonds_doubles_later_2.json"
.venv/bin/python -B "$E/common_bonds_witnesses.py"
.venv/bin/python -B "$E/common_bonds_contrasts.py" "$A/common_bonds_translated_age_two.json" "$A/common_bonds_doubles_later_2.json"
~~~

[Exhaustive single-ring table](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/common_bonds_core.json) ·
[Translated age-two tables](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/common_bonds_translated_age_two.json) ·
[Later double tables](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/common_bonds_doubles_later_2.json) ·
[Changed-triple witnesses](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/common_bonds_witnesses.json) ·
[Four-arm and dose comparisons](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/common_bonds_contrasts.json)
