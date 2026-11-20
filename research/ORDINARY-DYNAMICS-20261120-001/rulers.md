# Three readings of the same ordinary growth

At the first reached stage, the three shared births have the same complete witnessed growing-end component in both preparations. Their next common birth takes exactly the same three parents. It has zero fresh distinctions when it takes every loose distinction, and one when the other growing-end component is present. Both steps are funded. The first preparation closes. The preparation with one more loose distinction continues. This holds for the four-knot example and for every length in the three-route construction below. [Frozen comparisons](definitions.md) · [Literal replay](../../experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/rulers.py) · [Full receipt](../../artifacts/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/rulers.json)

## Which reading detects the difference?

Let `S` be the common neighbour of the three live source knots `U₁,U₂,U₃`. In the stretched preparation the three paths from `S` to `Z` each take `L` ordinary steps and share only `S,Z`. Each `Uᵢ` is one step from `S`, has two loose distinctions, and gives one to each of its two pair births. Consecutive interior knots on each path share two distinctions. The additional loose distinction, when present, is at `Z`. In the small example `S=Z`, with one shared distinction between `S` and each `Uᵢ`.

| First reached stage, pairs of loose distinctions | Number of pairs | Growing-end steps between holders | Whole-stage ordinary steps between holders | Whole-stage steps between distinctions through written knots | Bond distance |
| --- | ---: | ---: | ---: | ---: | ---: |
| Both in the three pair births, closing preparation | 3 | 1 | 2 | 3 | 2 |
| Both in the three pair births, continuing preparation | 3 | 1 | 2 | 3 | 3 |
| One in a pair birth and one in the extra unary birth | 6 | No route | `L+1` | `L+2` | 4 |
| Both in the extra unary birth | 1 | 0 | 0 | 1 | 2 |

The cross-component ordinary readings in the four-knot example are 3 holder steps and 4 distinction steps. Both readings above apply to all scored pairs, including the doubled variant. The ordinary step reading uses only the written incidences. Two consecutive distinctions share a written knot, and two consecutive holders share a physical distinction. For two distinct loose marks these step counts differ by one. The bond reading is the size of the least actual parity bond containing the two distinctions, less one. It ranges over the full stage's allowed relation. [Reading definitions](definitions.md)

The three pair births have three separate pair witnesses, namely `U₁,U₂,U₃`, and no common witness. Their three-node component is identical with each possible root, even when all three witnesses are shown. Hence every finite growing-end ball at a shared birth gives the same data while the next fresh count differs. An ordinary incidence ball of prescribed radius also misses the changed site once `L` is large enough. In the stretched construction the additional unary birth lies `L+1` steps away through actual holders. The bond reading separates these two preparations already on the shared loose distinctions. This example leaves locality with the bond reading open.

## Why the ordinary update differs

The common source witness `S` excludes a three-parent birth in the first round. The three remaining pairs are funded with the two loose distinctions at each `Uᵢ`. The pair births share a different parent for each pair of births, so the next demand is one at each and the first round gives each one fresh distinction. If `Z` has its own loose distinction, it is isolated at the growing end and produces an additional unary birth with two fresh distinctions. No other source knot is live. The first round is binary apart from this unary birth, each candidate pair has only one distinct common neighbour, both starts have at least two loose distinctions, and every source knot has at least three places. These are the relevant first-round gates of the proved identification class. [Identification theorem](../../proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/proof.md)

In the closing preparation, the sum of all current even equations has support exactly the three loose distinctions. The ternary birth on those inputs is already implied and writes no fresh distinction. In the continuing preparation, the same inputs form a proper nonempty subset of the loose distinctions. In a connected presentation the only such sums supported wholly on loose distinctions have either empty support or the whole loose set, since summands must agree across every shared distinction. So the same ternary birth requires one fresh distinction. The other component makes two unary births. Each has two loose distinctions and they share their sole parent. They grow into a path of live knots with two loose distinctions at each knot and one separate witness per pair along it. For any such path with at least two knots the complete update has one binary birth per consecutive pair and one unary birth at each end. Each new live knot again has two loose distinctions, so the path gains one knot and remains funded. The shared ternary birth, meanwhile, makes a unary birth with two loose distinctions one step later and its own pair of unary births the following step. The two components stay separate because births with no shared parents cannot share a next-round witness. This proves continued growth without measuring later layers. [Full end update](end_operator.md) · [Finite-piece relay theorem](../../proofs/RELAY-IDENT-20261119-001A/RELAY-IDENT-20261119-001A-P001_relays/proof.md)

| Formation | Matched changes | Additional births in continuing preparation |
| --- | --- | --- |
| Source | 1 changed support among `J` matched knots | 0 among `J` source knots |
| First | 0 among 3 matched births | 1 among 4 births |
| Second | 0 of 1 change parents, 1 of 1 changes fresh count | 2 among 3 births |

`J` is 4 in the small example and `3L−1` in the stretched examples. The last implied birth counts among births. There is no common live denominator after closure.

## Exact bond calculation and controls

The checker sums even equations over subsets of holders. To calculate these sums, it uses an exterior vertex joined to each loose distinction, retaining every parallel shared distinction separately. The support of a sum consists of the distinctions crossing the chosen subset of holders. A nonempty support is inclusion-minimal exactly when both parts of this partition are connected. Over the binary allowed-state relation, such a support has one parity constraint and no constraint on any proper projection. These are the bonds enumerated here. The exterior vertex is an aid to the cut calculation and is absent from the two ordinary step readings.

For long paths an exact calculation keeps `Uᵢ,Z` and replaces the intermediate part of each path with one link at the multiplicity of its final link into `Z`. Any physical cut separating the two ends incurs at least that multiplicity along the path. Any same-side connection through erased knots must go all the way between those two ends, so restricting each part and keeping the new link preserves connectedness on the retained vertices. For the converse, put all erased knots on the side of `Uᵢ`. This gives a physical cut of exactly the compressed cost, with both parts connected and every marked loose distinction retained. The compressed minimum equals the physical minimum. This argument applies at both stages for any `L≥4`, since the erased interior knots remain spent. Literal exhaustive cuts agree for the small example, the length-four construction, and length four with every link doubled. Every reported minimum also carries one lifted witness in the complete physical stage. There are 294 pair readings, 147 checked through direct exhaustive cuts as well.

| Source bond readings | Two at one `Uᵢ` | At distinct `Uᵢ`, closing / continuing | `Uᵢ` to extra at `Z` |
| --- | ---: | ---: | ---: |
| Four knots | 2 | 4 / 5 | 4 |
| Stretched, interior links doubled | 3 | 5 / 6 | 5 |
| Stretched, all links doubled | 5 | 5 / 6 | 6 |

The four stretched lengths measured are 4, 5, 8 and 16, plus the fully doubled length-four control. The largest complete replay has 54 knots and 107 distinctions at the second formation. For each preparation the checker independently reconstructs the growing end from physical incidence, shuffles knot order and distinction names, and peels the first reached stage back to the exact source. It checks K1–K3 on local parity projections by rank and the canonical relation checker. Source, first and second stages under not-all-equal were checked by explicit allowed states on the small example, with respectively 162, 570, 1,020 states in the baseline and 378, 3,900, 62,640 with the additional loose distinction. Both ternary births require one fresh distinction under that law. Every earlier allowed state has an extension, and the projected local relation at every written knot is exactly not-all-equal. This control tests the parity closing mechanism on this example.

The comparisons are of named physical preparations, with no prevalence weighting. All measurements here end with Stage 1, at the second ordinary formation. No later study panel was run.
