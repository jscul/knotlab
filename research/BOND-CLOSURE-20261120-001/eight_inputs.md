# Eight inputs hide the closing decision from every pair

**Built after the ternary criterion was derived. Independent program referee pending.** Fourteen physical knots suffice for an eight-parent example where every pair in the marked parents' combined supports agrees. The marked inputs give pair bond distance 7 in both starts. Each of their triples gives minimum bond size 8 in the closing start and 9 in the continuing start. No claim of size minimality is made.

## Physical starts

Use three spent knots A, B and C. For each of three parents give it one shared distinction with B and one with C. Give three other parents one meeting each with A and C. The last two meet A and B. Give each of these eight parents one loose distinction. No further distinction is loose in the first start.

Add a knot X and two intermediates. One intermediate meets A once and X twice. The other meets B once and X twice. The second start adds just one loose distinction to X. The respective counts are 14 knots with 30 and 31 distinctions. In both starts all physical supports have at least three places. Deleting any holder in the wired presentation leaves a connected remainder. Its full star is therefore a bond and the initial knot passes the allowed-state test. In the whole group every two parents have a common holder, and no holder meets all eight. The single wanted group is funded. In the second start X has no common holder with any of the eight and makes its own birth. The eight-input join has zero next demand in both and receives zero versus one fresh distinction. The second history continues through the two separate growing parts.

## Why the loose pair table agrees

A bond containing two loose distinctions puts both their parents on the shore opposite the exterior. If the shore contains no A, B or C, it cannot connect those parents. If it contains two or three of those hubs, each of the eight parents costs at least one crossing. Each parent on the shore has its loose distinction crossing, and every parent outside meets at least one of the inside hubs. If it contains just A or just B, five parent links meet that hub. Moving a parent adjacent to that hub from outside to inside adds one crossing; moving a nonadjacent parent inside costs three. The auxiliary route between A and B costs at least one. Two marked parents therefore cost at least eight. With just C, six parent links meet C, so the lower bound is again eight. This argument applies with or without X's additional loose distinction.

Conversely, choose any common hub of the two parents. Taking just that hub and the two parents gives a connected shore with connected complement. It costs exactly eight, including the auxiliary link at A or B when applicable. Thus all 28 pairs have the same minimum size eight.

## Exhaustive check on larger observations

The checker visits every ordinary shore with the exterior held outside, requires both shores connected, retains parallel distinctions separately, and computes each minimum from the cuts that actually contain its marks. The 2,574 and 4,310 bonds enumerated in the two wired presentations include all sizes. For this source family every bond touching the proposed loose inputs qualifies for the three-place reading. Each original star and each proposed parent was verified.

| Order on the eight loose inputs | Number of marked sets | Minimum bond size, closing | Minimum bond size, continuing |
|---:|---:|---:|---:|
| 1 | 8 | 3 | 3 |
| 2 | 28 | 8 | 8 |
| 3 | 56 | 8 | 9 |
| 4 to 8 | 163 | 8 | 9 |

Allow the observer all 24 distinctions held in the eight parent knots. All 276 pair readings still agree entry by entry, with the literal identity as the renaming. These are two starts with genuinely different next developments. The direct numerical claim is a finite exhaustive statement for these two starts. It establishes existence and gives no frequency under a population weighting. [Checker](../../experiments/BOND-CLOSURE-20261120-001A/BOND-CLOSURE-20261120-001A-E001_proposals/eight_inputs.py) · [Exact receipt](../../artifacts/BOND-CLOSURE-20261120-001A/BOND-CLOSURE-20261120-001A-E001_proposals/eight_inputs.json)
