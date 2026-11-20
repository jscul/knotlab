# Exact bond readings on the built comparisons

The quantities below are least bond **sizes**, written (b(T)) for a query on distinctions (T). Pair bond distance is one less. Infinity means no canonical bond contains the queried support. The checker rebuilds each physical presentation and computes the ordinary update from its loose counts and witnessed parent sets. It computes parity bonds independently of that update. [Frozen design](preregistration.md) · [Checker](../../experiments/BOND-CLOSURE-20261120-001A/BOND-CLOSURE-20261120-001A-E001_proposals/bond_checks.py) · [Machine-readable receipt](../../artifacts/BOND-CLOSURE-20261120-001A/BOND-CLOSURE-20261120-001A-E001_proposals/bond_checks.json)

## A reached ternary proposal

In the four-knot source the three live leaves each give two loose distinctions to the three pair births. The center has one extra loose distinction in the continuing preparation. The three pair births and their next parent set are identical. All three pairs are one growing-end step apart, two ordinary holder steps apart and three ordinary distinction steps apart, in both preparations. The next common birth has zero fresh distinctions in the closing preparation and one in the continuing preparation.

| Reader on the three proposed loose distinctions | Closing parity | Continuing parity |
| --- | ---: | ---: |
| Each singleton's least bond size | 3 | 3 |
| Each pair's least bond size | 3 | 4 |
| All three's least bond size | 3 | 4 |
| Literal allowed assignments on all three | 4 | 8 |

There are nine distinct distinctions in the union of the three written parent supports. All 511 nonempty queries were evaluated on that union. The counts of unequal entries at orders one through nine are 0, 12, 63, 69, 18, 1, 0, 0 and 0. The first differing pair under the displayed names is ({3,8}), whose bond size increases from 4 to 5. Both the loose-input queries and the full parent-support queries agree with their images under the tested relabeling of all knots and distinctions.

For the funding control the first leaf has one loose distinction and two shared distinctions meeting the center. Every written support remains a canonical knot. All three pair groups are proposed, and the first leaf owes two uses. The whole step stalls with zero births. Restoring one loose distinction at that leaf funds all three pair births.

The real not-all-equal comparison has eight allowed assignments on the proposed ternary inputs in each preparation. All three pair minima are 5 in both. The ternary minimum is infinite when the proposal exhausts the loose distinctions and 7 when the other component is present. Both births require one fresh distinction under not-all-equal. Direct allowed-state counts at the first three stages are 162, 570 and 1,020 in the exhausting preparation and 378, 3,900 and 62,640 in the continuing one. Every old state extends and every written support has exactly its full not-all-equal relation. [Earlier comparison](../ORDINARY-DYNAMICS-20261120-001/rulers.md)

## Queries confined to (p-2) proposed inputs

Use (p-2) main parents, each with one loose distinction and meetings to both (H_1,H_2). Two other parents (v,w) each have one loose distinction, meet (H_1,H_2) respectively, and share two distinctions each with a holder (W). A single additional loose distinction at (W) distinguishes the two preparations. For the ternary control, double each main parent's meeting with (H_1) and (H_2) to give both holders at least three places. All (p) parents form one funded group with no common witness. The extra (W) has its own unary birth. The group's fresh count changes from zero to one.

| Proposal arity (p) | Matched nonempty queries confined to main parents | Bond sizes on each (p-1) query, closing / continuing | First differing query size on all parent supports |
| ---: | --- | --- | ---: |
| 3 | One singleton of size 3 | 3 / 4 | 1 |
| 4 | Two singletons of size 3, one pair of size 4 | 4 / 5 | 2 |
| 5 | Three singletons of size 3, four larger queries of size 5 | 5 / 6 | 2 |
| 6 | Four singletons of size 3, eleven larger queries of size 6 | 6 / 7 | 2 |

The parent-support pair histograms differ for (p=4,5,6), ruling out every relabeling of those full readings. Specific pairs on those unions change from 5 to 6, 6 to 7 and 7 to 8. These comparisons exhibit a failing choice of the single (p-2)-input query. The receipt also gives every query on all (p) proposed inputs, so the distinction between a prescribed query and a whole deck is directly checkable.

## Two-input exception

In the binary comparison the two live parents each meet their common holder twice. Each parent has one loose distinction. An extra loose distinction at the common holder changes the identical pair proposal from exhausting to continuing. The literal projection on the two inputs changes from ({00,11}) to all four assignments. Each input's singleton bond size is 3 on both sides. There is no canonical bond containing both in the exhausting presentation, and the continuing presentation gives size 3. The archived law records a funded zero-fresh binary closing step. With a forced third place, the two equal inputs would force its value to zero, so the resulting support fails K2. If subternary final steps are excluded, this exact binary closing example is outside the admitted steps.

## How the minima were verified

Every small parity calculation enumerates cuts whose two parts are each connected. Every loose distinction is wired to one auxiliary exterior holder for this calculation and every shared distinction is kept separately. An independent calculation enumerates the row span over the two-element field and retains inclusion-minimal nonzero supports. Supports of size one or two still prevent their supersets from being minimal, even though canonical bonds have at least three distinctions. The two methods agree on every built preparation. Whole-stage projection ranks prove that each written support realizes its full local even relation. Small actual allowed-state tables cross-check the projections and use the canonical K1–K3 checker. Under not-all-equal, the solver instead enumerates allowed states and tests for inclusion-minimal nonfull projections. The auxiliary exterior contributes no physical knot to an ordinary step reading.

Connectivity matters for optimization. In the three-knot control, the least cut containing two prescribed loose distinctions has size 6 and its two marked holders occupy disconnected parts of one side. The true least bond has size 7. The calculation inspects both parts of every cut before using its size. The binary-to-ternary distinction in the previous section likewise uses canonical bonds after checking minimality.

For a fast exact tightness check on large connected parity stages, the only possible nonempty dual word supported wholly on loose distinctions is the full loose roster. A sum with no shared distinction includes either both or neither of its two holders. Connectivity propagates this agreement across the whole stage. For a proposed support of at least three loose distinctions the equality (b(T)=|T|) is therefore exactly exhaustion. This tightness check needs only the incidence and never enumerates large cuts. The built examples and funding control use no sampling weighting.
