# How distance and load change the moving count

This is a reading of original marks fixed before growth. In separate preparations the positions and reading radii vary. A measurement in one preparation has one fixed radius. All distances to the original attachment below are in ordinary incidence hops.

In a sufficiently long single-ring path take two, three or four consecutive marks to its right, whose nearest original holder is 2k old knot steps from the attachment, with k at least two. The quiet and loaded counts at radius 2k+3 in the first affected layer k+1 are (k+2)(m+2k+3)+6 and (k+2)(m+2k+3)+4, where m is the packet size. Both counts are permanent once that layer is reached. The original attachment is 4k+1 hops away. The difference of two keeps the same size as the attachment moves farther away. Its fraction of the quiet count tends to zero. At each fixed smaller radius there is an exact null in this preparation. At fixed radius r, letting the attachment recede eventually makes *every* layer agree. [All-size proof](local_proof.md) · [Fixed test before readout](moving_count_design.md)

| Nearest original holder offset | Reading radius | Hops to original attachment | First affected layer | Count for two marks, quiet / loaded |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 7 | 9 | 3 | 42 / 40 |
| 6 | 9 | 13 | 4 | 61 / 59 |
| 8 | 11 | 17 | 5 | 84 / 82 |
| 10 | 13 | 21 | 6 | 111 / 109 |
| 12 | 15 | 25 | 7 | 142 / 140 |
| 14 | 17 | 29 | 8 | 177 / 175 |

We rebuilt the actual holders of every distinction before computing these distances, and retained both absolute counts, full cumulative shells through the specified radius and the original ancestors of the counted knots. The five registered sources supplied 57 matched packet/offset/side cases with their specified generous endpoint margin. We also tested the proof's more conservative sufficient margin by taking 128 path marks with seam at index 12. The quiet and loaded paths match through k=7 there for each packet of two, three and four marks. The quiet arm exceeded the 6,000-knot cap when attempting the next layer. On the k=2 literal two-mark example the quiet ball counts 12 knots with some ancestry outside the marked side, the loaded ball two. Neither ball reaches an original ring holder. This checks why present reach and original ancestry must be scored separately. A scrambled copy of the knot and distinction names gives the same reading. [Literal counts](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/moving_count.json) · [Long path within the proof's sufficient padding](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/proof_padding.json)

## Which part of a partial load matters

For this particular reading on a singly attached doubled-meeting ring, the change is exactly −2 if the attachment holder carries activity, and zero otherwise, at arbitrary k under the same padding. The two lists in the proof begin with the children of the pairs of path holders at offsets 0 and 2, or at offsets 1 and 3. The first pair survives exactly when the attachment itself is quiet. When it survives, the outer parent has two loose distinctions and just one other child. The inner parent has four loose distinctions and three other children regardless of which other proposals were vetoed. None of these other three can share a second parent with the sole outer sibling. Thus the child has four loose distinctions, just as in the quiet proof. When the attachment is active the outer parent's formerly paired input instead gives a unary with two fresh distinctions. In the odd list the attachment's path neighbor at offset one always stays cold on a shared-ring-only loading. The same calculation gives four fresh distinctions there independently of which adjoining ring holder is active. The rest of the induction uses only these two leading counts and the unchanged outward path. Physical double meetings change neither ordinary neighbor sets nor these retained opening counts.

| Number of original distinctions loaded | Physical assignments | Giving the two-knot decrease |
| ---: | ---: | ---: |
| 0 | 1 | 0 |
| 2 | 5 | 2 |
| 4 | 10 | 7 |
| 5 | 32 | 32 |
| 6 | 10 | 9 |
| 8 | 5 | 5 |
| 10 | 1 | 1 |

In the even sector choose which of five physical meetings have both copies active. The attachment is quiet exactly when both its incident meetings are omitted. At weight 2j that gives choose(3,j) of choose(5,j) assignments with no response. In the other sector each meeting has exactly one occupied copy and every attachment is active. Every allowed physical assignment receives one vote. The sign on this early, small ball differs from the excess on the larger first-layer ball containing the ring. [Comparison over all 64 words](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/moving_loads.json)

With a second ring on the inward side four or eight old steps past the nearer donor, the farther donor contributes zero to this particular reading, at either fixed near-ring load. In the proof of the range bound put W=k+1. The farther holder is at least 2k+4 old knot steps away, strictly more than 2W. The two *changes* therefore add on this observed ball. Sixty-one matched four-arm packet cells, including two additional long-path controls for this calculation, gave zero interaction. Other same-side balls on these very starts have nonzero interaction. [Two-loop counts](side_routes.md)

## An independent count of the seven-bond-radius witness

For the old marks e8,e12 in the original attached background, the union of their bond-radius balls at layer three contains 4, 4, 4, 16, 16, 30, 30 and **45** quiet knots at radii zero through seven. Under load the same list ends in **46**. We checked this with a second algorithm. Give each holder one side bit and each actual distinction a cut bit equal to the difference of its two endpoint sides, wiring loose ends to the auxiliary exterior. Require the chosen anchor to cross and the cut to have at most eight physical distinctions. For any satisfying assignment, contract the connections that do not cross. The graph of components is connected. Choose a component whose removal leaves the remaining components connected. The cut around that component is a genuine nonempty bond contained in the candidate. Record it if it contains the anchor, and exclude every superset of that bond from the remaining search. This is safe whether or not it contains the anchor because one bond cannot properly contain another. Exhaustion enumerates every eligible bond of this size through the anchor. At e8 the quiet and loaded enumerations exhausted 33 and 34 such bonds, while e12 had 36 in each. All eight anchors on a separate four-knot system agree with direct sums of the parity equations. [Reproducible checker](../../experiments/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/far_bond_ball.py) · [Exact small-bond supports](../../artifacts/SAME-SIDE-READING-20261119-001/SAME-SIDE-READING-20261119-001-E001_side/far_bond_ball.json)

At the original source every old holder has its own loose distinction. Consequently every assignment on *all* the original shared background marks is allowed: extend it by choosing the loose value needed for even parity at each original knot. Each later birth has a fresh variable available for extending the old equations, so these projections stay free at every reached finite size. The particular prepared state also keeps all original path values at the reference. The change is observable by reading how these marks relate to other distinctions and knots.
