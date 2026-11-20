# What the two local settings reveal

On the hand-built parity start, reading one of two distinctions at each side gives a CHSH score of 4 when the two selector values come from the state. Each reported bit stays fair in all four setting pairs under uniform complete-state weighting. Alice can nevertheless read Bob’s selector exactly from her two local distinctions. An external choice of which distinction to read on the same states gives a score of 2. Both results persist through the first ordinary growth round.

## Construction and eligibility

Alice’s displayed knot holds `X,A0,A1,P`, and Bob’s holds `Y,B0,B1`. Between `A0,B1` put four three-place knots. Knots 0 and 1 each hold one of the two named distinctions. Every pair among 0,1,2,3 except 0,1 shares one fresh distinction. Put a separate copy between `A1,B0`. The two selectors are `X,Y`. Reading I takes the distinction at the specified index. Reading II asks whether the local pair has both bits equal to the specified index. The ordered marks, their readings, the start and the state weightings were specified before measurement. [Frozen design](preregistration.md)

The start has 17 distinctions in 10 displayed knots. Each distinction belongs to one or two knots. Any two knots share at most one distinction. For either law, the ordinary uncapped group rule gives three new knots, each with one parent, spending `X,P,Y` in this order. Their respective next-round demands are 1, 1, 0. Each receives two fresh distinctions. Two implementations agree on the parent identities, fresh counts and demands. [Full growth implementation](../../experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py) · [Growing-end operator](../../experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py)

| Law | Allowed start states | Allowed states after one round | Extensions of each start state | K1–K3 for every displayed support |
| --- | ---: | ---: | ---: | --- |
| Even parity | 128 | 1,024 | 8 | 10/10 at the start, 13/13 after growth |
| Not-all-equal | 7,582 | 204,714 | 27 | 10/10 at the start, 13/13 after growth |

Every projected support has all states of its stated law. These checks enumerate every assignment on 17 and then 23 distinctions, project the allowed states on each support, and submit that relation to `knotlab check`. The finite witness counts are positive on every supported word. Both the two-step and the three-step separation criteria admit the frozen placement at both stages. The fewest displayed-knot steps between the two sets of marks is three, attained by `A0,B1` and `A1,B0`. The two selectors are five steps apart. Under parity, each of the two three-step pairs has equal values in every state. The step count describes the meeting pattern. [Projections, steps and counts](embodied_control.json)

## The four setting pairs

Adding the four parity equations in either copy cancels the five shared distinctions in pairs. Its two terminal values agree, with four internal assignments for each equal pair. Write `r=A0=B1` and `q=A1=B0`. Bob’s knot gives `Y=r⊕q`, and Alice’s gives `P=X⊕Y`. Under uniform complete-state weighting the eight choices of `(X,Y,r)` have equal mass. When the state supplies both selectors, reading I therefore gives Alice `r⊕XY` and Bob `r`.

| Selector values `XY` | Endogenous joint counts `00,01,10,11` | External-index joint counts `00,01,10,11` | Endogenous correlation | External correlation |
| --- | --- | --- | ---: | ---: |
| 00 | 16, 0, 0, 16 | 32, 32, 32, 32 | 1 | 0 |
| 01 | 16, 0, 0, 16 | 64, 0, 0, 64 | 1 | 1 |
| 10 | 16, 0, 0, 16 | 64, 0, 0, 64 | 1 | 1 |
| 11 | 0, 16, 16, 0 | 32, 32, 32, 32 | −1 | 0 |

The endogenous column conditions the 128 start states on their two selectors. The external column uses all 128 states in each row. The endogenous score of 4 exceeds the quantum bound. The two selectors are mutually independent fair bits, but their pair is statistically dependent on the available responses. Their four-response distribution in each conditional ensemble differs from the common distribution by total variation 1/2. Alice reads `Y=A0⊕A1` from her pair. At either fixed `X`, changing the value conditioned on for `Y` gives disjoint distributions for Alice’s pair, with total variation 1. Holding `Y` fixed gives total variation 0 for Bob’s pair across `X`. These are conditional distributions. An operation that changes a distant setting while holding its causes fixed has not been supplied.

## What the readings and weightings change

U weights complete stage states equally. L gives each start state one unit and divides it equally over its extensions. U and L give the same normalized marked distributions at both stages of this construction, for each of the two laws. T doubles a state’s U weight when `A0=1`. The table gives the ordinary signed CHSH score and the largest of its eight orientations for parity.

| Reading | Weighting | External signed / largest | Endogenous signed / largest | Endogenous selected-bit change for Alice at fixed `X=0,1` | Endogenous selected-bit change for Bob at fixed `Y=0,1` |
| --- | --- | --- | --- | --- | --- |
| I, choose a distinction | U or L | 2 / 2 | 4 / 4 | 0, 0 | 0, 0 |
| I, choose a distinction | T | 2 / 2 | 4 / 4 | 0, 1/3 | 0, 0 |
| II, ask for a pair pattern | U or L | 0 / 2 | 0 / 4 | 1/2, 1/2 | 0, 0 |
| II, ask for a pair pattern | T | 0 / 2 | 0 / 4 | 1/3, 2/3 | 0, 0 |

For reading II the four endogenous correlations in order `00,01,10,11` are `1,1,−1,1`. Its orientation with value 4 already has a change in Alice’s reported marginal under U. Under T the endogenous settings still have equal mass, but `r` takes the value 1 with probability 2/3. This breaks the fair-bit masking in reading I. All external marginal changes are zero.

Under not-all-equal the same four-knot groups have nine internal assignments for each equal terminal pair and ten for each unequal pair. All four terminal combinations occur. The largest CHSH orientations were as follows. [All raw joint counts, correlations, signed scores, exact marginal changes and zero cells](embodied_control.json)

| Weighting | I, external | I, endogenous | II, external | II, endogenous |
| --- | ---: | ---: | ---: | ---: |
| U or L | 418/3791 | 26/127 | 3010/3791 | 922/635 |
| T | 418/3791 | 1223654051/3002715025 | 3730/3791 | 999687631/600543005 |

The four endogenous setting cells under not-all-equal and U contain 1,886, 1,905, 1,905 and 1,886 start states. All are populated. The largest endogenous orientation over the two readings and three weightings remains below two. Under U, reading I has nonzero selected-bit changes at both sides. For reading II, Bob’s endogenous bit is always zero because his three-place not-all-equal knot forbids his two response bits from both equalling his selector.

## Reproduction

```sh
.venv/bin/python -B research/ENTANGLEMENT-READ-20261120-001/embodied_control.py
python3 -B research/ENTANGLEMENT-READ-20261120-001/embodied_control_replay.py --compare research/ENTANGLEMENT-READ-20261120-001/embodied_control.json
```

The second program enumerates the 32 hidden assignments for each terminal pair of one four-knot group, combines two copies, and independently counts the first-round extensions. It matched all 1,536 seven-mark weighted counts and all 48 reading tables, including their correlations and marginal changes. This is an exact replay for one deliberately constructed start. The two marks on each side are held on the initial knots at both stages. The broader study separately tests newborn marks and other starts. Independent referee pending.
