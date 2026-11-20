# Independent connected-cut certificates for marks on one side

Two triples of original path marks distinguish quiet and loaded preparations of the **four-step double attachment**. The three pair readings within each triple agree across all four loadings. For the single one-spare attachment, \(e_8,e_{12}\) have bond distance 9 at every common completed age through eight. All sizes below count physical distinctions. For pair bond distance subtract one. [Frozen readings and marks](definitions.md)

## One bond through three marks

Let \(e_i\) be the original distinction shared by \(b_i,b_{i+1}\). The two attachments in the four-step double are at \(b_4,b_8\). The marks below lie between the attachments. The first triple is incident to \(b_4\) and one old knot step from \(b_8\). The second reverses those offsets.

| Marks at age one | Smallest common bond sizes, quiet / first / second / both | Sizes for the three pairs in index order |
| --- | --- | --- |
| \(e_4,e_5,e_6\) | 14 / 16 / 14 / 16 | 6 / 8 / 4 in each loading |
| \(e_5,e_6,e_7\) | 14 / 14 / 16 / 16 | 4 / 8 / 6 in each loading |

For the first triple, each cut must alternate the colours of \(b_4,b_5,b_6,b_7\). In the quiet arm a size-14 bond has inside knots \(b_4,b_6\) and their common child, which uses four fresh distinctions. Its 14 crossings are \(3,4,5,6,16,20,36,38,39,45,120,121,122,123\). Loading the first ring vetoes that child. A size-16 bond uses \(b_5,b_7\) and their common child, which has six fresh distinctions. The corresponding inside node lists, including child names, are \(4,6,31\) and \(5,7,28\). Both shores were checked in the literal holder data. With \(b_4\) outside, the quiet minimum is already 16. The smaller quiet bond therefore uses the attachment itself even though every prescribed mark is on one side. [Literal witnesses and orientation receipts](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert_between.json)

Adding four funded path holders at each end moves the attachments to \(b_8,b_{12}\). The two translated triples have the same two vectors and the same pair controls. All 11 sets drawn from the four between-attachment marks have certified readings in each of the four arms of both starts at ages zero through five. The tabled effects persist through age five. At age six, three of the 88 individual readings have intervals only. These are the first triple under first-only loading on each start, with sizes in \([9,16]\), and the padded triple \(e_8,e_{10},e_{11}\) under both loads, with size in \([11,16]\). The other 85 readings are exact. [Extended work-limit replay](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert_between_deeper.json)

## A second first-layer lower certificate

For a fixed inside set \(S\) of original knots, putting all children outside costs the original cut size, including the old open distinctions. A child with \(p\) parents, \(a\) inside parents and \(f\) fresh distinctions changes the cost by \(f+p-2a\) if put inside. Every actual first-layer child in these four loadings has one or two parents and \(f\ge p\). Each change is nonnegative. Consequently a size-at-most-16 candidate has at most 13 old opens on its inside knots, since the three marked original distinctions already cross.

For each of the two alternating colourings, the checker enumerates exactly those original sets that satisfy this opening bound. It computes their original cut cost by XOR of literal source equations. The only inside children that can connect different old components are binary children whose two parents are inside. Choosing the least total \(f-2\) cost of connectors is a minimum spanning tree calculation on the components of \(S\). The calculation covers all ways to connect the chosen original knots, and the resulting upper cuts also pass the direct connectivity check on their outside shores.

For example, with \(b_4,b_6\) inside and the first ring loaded, 563 T4 sets pass the opening bound, of which 16 have original cut size at most 16. All 16 are disconnected under every actual choice of connecting children. With \(b_5,b_7\) inside, only one of the 13 affordable original cuts can connect, at full cost 16. With the first ring quiet, the former alternating choice attains 14. The same check gives both mirrors and all four loadings on the padded start. [Separate source-subset checker](../../experiments/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert_first.py) · [Per-orientation counts and witnesses](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert_first.json)

## One attachment and the remote controls

| Comparison | Exact coverage | Result |
| --- | --- | --- |
| One-spare attachment at \(b_4\), remote \(e_8,e_{12}\) | Quiet at 0–8, loaded at 0–12 | Bond distance 9 throughout |
| Same start, 21 order-two to order-four sets at nearest offset 0 or 1 | Ages 0–6 in both arms | All 147 matched readings agree, including 11 no-bond cases at source |
| Single attachments after padding each end by 4, 8 or 16 | 32, 43 and 53 registered sets at offsets 0, 4, 8 or 16, each through age 6 | 886 matched equalities and 10 interval-bounded comparisons |

The quiet remote run reaches 3,389 knots at age eight and the next funded roster would have 6,495. The registered knot cap is 6,000. The bounds in the padded comparisons overlap between the arms. The two-attachment witnesses touch the donor, so they establish sensitivity of a common-bond reading on one side and leave a strictly remote same-side bond contrast open. [Remote pair](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert_remote.json) · [Near sets](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert_near.json) · [Padded sets](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert_translated.json)

## Exact thresholds on full incidence

The solver considers each consistent colouring that makes all marked distinctions cross and places the bookkeeping exterior outside. An integral feasible flow from the inside pins to the outside pins gives a lower bound \(\lambda\). For any cut consistent with the pins, its physical cost equals \(\lambda\) plus the sum of its outward residual capacities. Flow capacity and balance are checked against actual multiplicities. The remaining search therefore spends only the nonnegative residual budget. It keeps the physical connectivity of both colours, including across distinctions with zero residual cost.

With some colours fixed, add the capacities crossing between them. For each uncoloured knot, add the cheaper of the two residual costs it incurs against fixed knots. Those arcs are distinct and give a lower bound for every completion. If one colour choice already exceeds the residual budget, the other is forced. A knot can take a colour only if it can still reach that colour's fixed root through possible knots of that colour. If fixed same-colour knots are separated, every valid connecting path crosses each distance level between the fixed root's current component and the nearest separated fixed knot. The search branches at the level with the fewest knots, trying the first knot of the required colour. If both sets of fixed knots are already connected, it tries assigning all uncoloured knots outside. Any other feasible connected inside shore must enter at a neighbour of the fixed inside set, which supplies the exhaustive branches. Every branch fixes another knot.

A fully searched impossible threshold raises the lower bound by one. A work cap retains only the already certified bounds. The code claims no common bond only after ruling out the full cost range or every consistent colouring. An older cut supplies an upper bound after checking its exact crossing distinctions and both shores in the new stage. At the age-one double-attachment witnesses each orientation has a relaxed flow bound of 12. Residual propagation rejects both orientations at the threshold immediately below the attaining cost, without needing deeper branches.

Four tiny controls compare **733** pair, triple and quadruple queries against inclusion-minimal parity supports enumerated by XOR, including disconnected lobes, a contradictory three-mark colouring and parallel physical distinctions. The two positive triples retain their minima under simultaneous permutation of physical knot and distinction names in all four arms. The independent broad tables agree on all 1,384 exact stage, arm and mark-set readings common to both runs. [Python driver](../../experiments/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert.py) · [Integer threshold solver](../../experiments/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/side_cert.cpp) · [Broad exact tables for the doubles](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/common_bonds_doubles_later.json)

~~~bash
mark_side=experiments/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side
mark_side_data=artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side
.venv/bin/python -B "$mark_side/side_cert.py" --panel remote
.venv/bin/python -B "$mark_side/side_cert.py" --panel near --through 6
.venv/bin/python -B "$mark_side/side_cert.py" --panel translated --cases P4 P8 P16 --through 6
.venv/bin/python -B "$mark_side/side_cert.py" --panel between --cases T4 PT4 --through 6
.venv/bin/python -B "$mark_side/side_cert.py" --panel between --cases T4 PT4 --through 6 \
  --work-limit 20000000 --out "$mark_side_data/side_cert_between_deeper.json"
.venv/bin/python -B "$mark_side/side_cert_first.py"
~~~
