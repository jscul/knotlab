# The final shortest route in the quiet four-step double

The original path distinctions `e0` and `e15` are 30 incidence hops apart in the quiet four-step double. The reached age-six stage has 3,431 shortest routes between them. The funded age-seven roster adds one, giving **3,432 shortest routes at every later completed age**. The roster would bring the stage to 4,627 knots and 33,512 distinctions, above the 32,000-distinction cap. The check materializes incidence through age six and counts the final route from the prospective roster. [Frozen follow-up design](last_route_design.md)

## Counting the only eligible midpoint

From either original mark, reaching an age-seven knot takes at least 15 incidence hops. A shortest route through such a knot must put it at the midpoint. Its two neighbors in the route are spent distinctions, one from each of two age-six parents. Each eligible parent must therefore lie exactly 13 hops from its corresponding marked endpoint in the reached stage. Every other part of the route lies in that stage. Two such prefixes cannot meet because their meeting would give an old route of at most 26 hops between marks whose least distance is 30. Distinct eligible parents contribute via distinct spent distinctions. Summing shortest prefixes over eligible parents at each end and multiplying the two sums consequently counts all new shortest routes through the proposed midpoint once.

Only one proposed knot qualifies. Its two parents are 1910 and 1949 in the literal receipt. Each supplies one prefix for its end. In the replay they spend distinctions 12139 and 12418 respectively. The number of new routes is $1\cdot1=1$. Which equal-valued loose distinction is allocated does not change the count. The new knot's original ancestors are the eight path knots `b1,b3,b5,b7,b9,b11,b13,b15`. It has no exclusive ring ancestry on either side. The old route set persists. An age-eight or later knot requires at least 17 hops from each end, so it cannot add a shortest route.

The complete next-round check accounts for all 8,034 loose distinctions and spends each once across 1,121 parents. The plan has 2,481 births. The check performs the ordinary lookahead on this roster and verifies the fresh supply at every planned birth. It computes the exact total without building the over-cap incidence stage. All other quiet four-step pairs had saturated by age six. This follow-up counts the final routes and their midpoint set. The full balls around these points still have the bounds of the physically measured stages. [Reached stages and earlier bounds](routes.md)

## Literal comparisons at age seven

The same parent calculation is compared to the complete materialized age-seven stage in both one-spare single-attachment preparations and all four eight-step double preparations. Every control agrees on the total and the contribution at each newly born midpoint.

| Control | Age-six count | New at age seven | Complete count |
|---|---:|---:|---:|
| One-spare single, quiet | 3,431 | 1 | 3,432 |
| One-spare single, loaded | 2,219 | 1 | 2,220 |
| Eight-step double, quiet | 3,431 | 1 | 3,432 |
| Eight-step double, first only | 2,219 | 1 | 2,220 |
| Eight-step double, second only | 2,219 | 1 | 2,220 |
| Eight-step double, both loaded | 1,619 | 1 | 1,620 |

[Code](../../experiments/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/last_routes.py) · [Exact receipt](../../artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/last_routes.json)
