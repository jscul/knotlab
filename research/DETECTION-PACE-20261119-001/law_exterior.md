# The same physically cut observation under sixteen laws

On the 17-knot path, cold plus with hot veto has the same first
detecting layers as cold pass with hot veto for every checked cutoff,
side and observation. At offsets three, four and five, the connected
mark component first differs at layers **2, 3 and 4** under each
law. The union of the retained components first differs at layers
**1, 2 and 3**. Thus the two committed cold-plus predictions hold,
and the agreement extends to offset five in this comparison.
The first unequal cuts can have very different sizes under those
two laws. [Frozen comparison](law_exterior_design.md)

| Right offset | First different connected layer | Connected knots under P/V, quiet / loaded | Connected knots under +/V, quiet / loaded | First different union layer |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 2 | 33 / 36 | 44 / 48 | 1 |
| 4 | 3 | 42 / 47 | 94 / 105 | 2 |
| 5 | 4 | 50 / 57 | 243 / 277 | 3 |

The agreement is specific to those two laws. Cold pass with hot plus,
and cold plus with hot pass, first change the connected component
one layer later at offsets two through four. At offset five their
components agree through layer four. Cold veto with hot P, + or −
changes the union at offsets three through six by layer four.
The rooted component still agrees at those four offsets.

## All onsets through the last common layer

Each seven-entry sequence below gives the first differing layer at
offsets **0, 1, 2, 3, 4, 5, 6**, in order. A dash records a
verified isomorphism at every measured common layer. Left and right
onsets agree at offsets zero through three, where both sides exist.
The right marks also supply offsets seven through eleven, which
agree in every test. All laws agree at layer zero.

| Cold / hot | Last common layer | Connected mark component | Union of components |
| --- | ---: | --- | --- |
| P / P | 4 | – – – – – – – | – – – – – – – |
| P / V | 4 | 1 1 1 2 3 4 – | 1 1 1 1 2 3 4 |
| P / + | 4 | 1 1 2 3 4 – – | 1 1 1 1 2 4 – |
| P / − | 1 | 1 1 – – – – – | 1 1 1 – – – – |
| V / P | 4 | 1 1 1 – – – – | 1 1 1 1 2 3 4 |
| V / V | 4 | – – – – – – – | – – – – – – – |
| V / + | 4 | 1 1 1 – – – – | 1 1 1 1 2 3 4 |
| V / − | 4 | 1 1 1 – – – – | 1 1 1 1 2 3 4 |
| + / P | 4 | 1 1 2 3 4 – – | 1 1 1 1 2 3 4 |
| + / V | 4 | 1 1 1 2 3 4 – | 1 1 1 1 2 3 4 |
| + / + | 4 | – – – – – – – | – – – – – – – |
| + / − | 1 | 1 1 – – – – – | 1 1 1 1 – – – |
| − / P | 1 | 1 1 – – – – – | 1 1 1 – – – – |
| − / V | 1 | 1 1 1 – – – – | 1 1 1 1 – – – |
| − / + | 1 | 1 1 – – – – – | 1 1 1 1 – – – |
| − / − | 1 | – – – – – – – | – – – – – – – |

The four constant laws agree in every comparison. All paired
histories ending at layer one have a funding shortage in at least
one arm at the attempted second layer. Both arms stall for cold
minus. Only the loaded arm stalls for P/− and +/−. All other paired
histories reach the analysis limit at layer four, with both arms
within the physical limits of 6,000 knots and 32,000 distinctions.
Each dash is limited to the paired history just stated.

## Constructing and checking the observation

The reader uses current knot–distinction incidence. It retains
exactly the nodes at least \(2d\) incidence hops from the original
attachment and all incidences between those nodes. The two types
and the chosen shared mark are its only labels. The component
reading starts at that shared mark. The union reading includes
all remaining components and still marks the root. Both omit
values and any information about incidences removed by the cut.

The implementation constructs the literal bipartite cutoff and
checks it against the holder-based version on each frame. A
knot's hop count from the attachment is even. A distinction's hop
count is one plus the minimum hop count of its actual holders.
Consequently a distinction survives this even cutoff precisely
when every holder survives. This gives the same induced observation
with both representations, including physically separate parts.

To test equality, a correspondence based on actual old parent sets
and sibling numbers proposes a map. Each map is checked against
the complete physical incidence of the two displayed observations.
The check requires a total bijection preserving both types, the
root and every incident neighbor in both directions. The proposed
codes are absent from the observation. If a proposal fails, the
implementation can use exact simultaneous refinement and a bounded
isomorphism search. All **1,470** equal observations in this panel
have validated literal correspondences. All **514** unequal
observations already differ in a count of displayed knots,
distinctions, incidences or components. Every one of the **1,984**
observations is resolved. Earlier structural replay verifies the
physical stage counts used as inputs. The equalities establish the
absence of *any* distinguishing typed reading of those observations
at the stated layers.

~~~sh
.venv/bin/python -B experiments/DETECTION-PACE-20261119-001/DETECTION-PACE-20261119-001-E001_pace/law_exterior.py
~~~

[Exact per-location comparisons and bijection receipts](../../artifacts/DETECTION-PACE-20261119-001/DETECTION-PACE-20261119-001-E001_pace/law_exterior.json) ·
[Pass/veto cutoff proof](current_separation.md)
