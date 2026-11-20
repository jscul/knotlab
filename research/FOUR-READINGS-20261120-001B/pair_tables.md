# What a receiver can read before growth

For each pair of already present distinctions record the number D of allowed words in which they disagree. Its rate is D/N under equal weight on the N allowed words. A new distinction creates new entries. On common distinctions a change in raw count can come entirely from the altered number of allowed states. Here the receiver sees the entire physical support of its marked knot. The two marks of a receiver-local pair are therefore already held together before growth. [Frozen inputs and matching](preregistration.md) · [Exact tables in lexicographic order, marks, denominators and sample pairs](../../artifacts/FOUR-READINGS-20261120-001B/FOUR-READINGS-20261120-001B-E001_state_growth/pair_tables.json)

## The loose-count path, every separation

There are d+1 live knots in order and d spent witnesses. Between consecutive live knots a witness holds a single distinction toward the left and two toward the right. The end receiver has its single shared distinction and two private ones. The sender at the other end has its two shared distinctions and one private distinction. The edit gives it a second private distinction. Under not-all-equal the **three receiver-local rates agree exactly**. Of the pairs containing one receiver mark and one outside mark, **exactly the nine involving an old sender mark change**. The largest change in a uniform disagreement rate is

\[
\frac{3}{55\,23^{d-1}}.
\]

To see this, write a and t for consecutive single shared distinctions. Between them are a three-place witness holding a and a shared pair, then a five-place live holder holding that pair, t and two private distinctions. For fixed a,t, there are 12 completions when a=t and 11 when they differ. The first rule excludes one of four possible shared pairs and the second removes one of the 12 remaining words just when the pair can equal (t,t). Consequently at each intervening holder a signed one-bit correlation is multiplied by 1/23. Sum over the sender and final witness conditional on their incoming single distinction. There are 5 completions before and 11 after, for either incoming value. Every pair outside the three old sender marks therefore retains its uniform rate. A receiver mark has correlation 1 with the outgoing single mark if it is that mark, or −1/3 if it is either of the two other marks of the receiver ternary.

At the final witness let the incoming value be 0 and read a bit as +1 for 0 and −1 for 1. The conditional mean on either shared sender mark goes from −1/5 to −3/11, and on the existing private sender mark from 1/5 to 1/11. With incoming value 1 each sign reverses. A disagreement rate is one half of one minus the signed correlation. This gives the stated maximum, attained between the two end marks with the largest responses, and proves all nine normalized changes are nonzero. The total solution counts are \(30\,23^{d-1}\) and \(66\,23^{d-1}\). The raw receiver-local counts consequently change even though the local rates agree. The argument describes all finite d≥1 in these prepared paths. [Physical matched edits](../INFLUENCE-CONE-20261120-001/fixed_edits.md) · [Independent exact checks](../../artifacts/FOUR-READINGS-20261120-001B/FOUR-READINGS-20261120-001B-E001_state_growth/verification.json)

| Witnessed separation d | N before / after | Receiver-local rates changed | Receiver-to-sender rates changed | Largest absolute receiver-to-sender rate change | Raw counts at a pair attaining it |
| ---: | --- | --- | --- | --- | --- |
| 2 | 690 / 1,518 | 0/3 | 9/9 | 3/1265 | 342 / 756 |
| 3 | 15,870 / 34,914 | 0/3 | 9/9 | 3/29095 | 7,932 / 17,454 |
| 5 | 8,395,230 / 18,469,506 | 0/3 | 9/9 | 3/15391255 | 4,197,612 / 9,234,750 |
| 8 | 102,144,763,410 / 224,718,479,502 | 0/3 | 9/9 | 3/187265399585 | 51,072,381,702 / 112,359,239,748 |

## Changing the witness and changing one holding

In the first structural preparation two other live knots begin to have a common witness when a new distinction is added. The fixed-width preparation instead gives a spent holder a second holding of a distinction that was already at one of those live knots. In both, all of the receiver's old holdings agree. The cycle preparation removes one holding at a knot of a shared distinction, retaining the other holder. Its control gives a loose distinction to that other holder in the intact cycle. These matchings follow the earlier physical records. [Witness-specific preparations](../INFLUENCE-CONE-20261120-001/fixed_edits.md) · [Six-knot control](../INFLUENCE-CONE-20261120-001/physical_edits.md)

For not-all-equal, each entry of the next table gives **raw counts changed / rates changed / common pairs**. “Sender” includes the stated live participants of a structural edit, or both physical ends of a removed holding. The categories are mutually exclusive, beginning with pairs both in the receiver. The last column counts pairs containing a new mark in the second start. Uniform-rate differences in this table are exact even where they are very small.

| Preparation | Within receiver | Receiver to sender | Receiver to other | All remaining pairs | New pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Switch at two leaves, observing U | 0/0/6 | 56/56/56 | 0/0/40 | 206/206/276 | 0 |
| Two loose names from Z to W, observing U and V | 231/231/231 | 682/682/682 | 396/396/396 | 1176/1176/1176 | 0 |
| Loose-count path, d=2 | 3/0/3 | 9/9/9 | 15/0/15 | 28/18/28 | 11 |
| Loose-count path, d=3 | 3/0/3 | 9/9/9 | 30/0/30 | 78/33/78 | 16 |
| Loose-count path, d=5 | 3/0/3 | 9/9/9 | 60/0/60 | 253/63/253 | 26 |
| Loose-count path, d=8 | 3/0/3 | 9/9/9 | 105/0/105 | 703/108/703 | 41 |
| New shared distinction, d=2 | 15/15/15 | 72/72/72 | 156/156/156 | 703/703/703 | 44 |
| Second holding, d=2 | 15/15/15 | 78/78/78 | 156/156/156 | 735/741/741 | 0 |
| New shared distinction, d=3 | 6/6/6 | 48/48/48 | 136/136/136 | 1035/1035/1035 | 50 |
| Second holding, d=3 | 6/6/6 | 52/52/52 | 136/136/136 | 1075/1081/1081 | 0 |
| Six-knot cycle, remove one holding | 10/10/10 | 37/40/40 | 55/55/55 | 168/171/171 | 0 |
| Intact cycle, one extra loose distinction | 10/10/10 | 25/25/25 | 70/70/70 | 171/171/171 | 24 |
| Removed holding versus extra loose distinction | 10/10/10 | 40/40/40 | 55/55/55 | 171/171/171 | 24 |

In the second table, each pair attains the largest absolute **receiver-local** uniform rate change for that comparison. Distinction names x0, x1 and so on index the literal holdings in the receipt. The two counts and the two denominators give the exact magnitude directly. Displayed scales in the last column are rounded only for readability.

| Preparation | Pair | D before / after | N before / after | Absolute rate change |
| --- | --- | --- | --- | ---: |
| Two loose names from Z to W, observing U and V | x0, x1 | 1,179,132,759,025,448,325,120 / 1,178,275,657,822,494,511,104 | 2,355,962,524,342,355,567,430 / 2,354,249,995,962,206,729,796 | 1.19613e-14 |
| New shared distinction, d=2 | x4, x5 | 4,005,119,283,104 / 8,761,996,077,568 | 6,827,857,207,532 / 14,937,290,732,224 | 2.63964e-07 |
| Second holding, d=2 | x0, x1 | 7,409,700,999,424 / 7,914,583,570,432 | 13,984,420,284,664 / 14,937,290,732,224 | 2.37435e-08 |
| New shared distinction, d=3 | x30, x31 | 222,852,854,997,472 / 487,534,775,608,832 | 348,480,174,955,828 / 762,369,428,899,904 | 4.06821e-10 |
| Second holding, d=3 | x30, x31 | 456,434,257,888,448 / 487,534,775,608,832 | 713,736,828,499,400 / 762,369,428,899,904 | 1.73612e-11 |
| Six-knot cycle, remove one holding | x0, x1 | 6,075,008 / 5,670,000 | 11,390,626 / 10,631,250 | 6.5551e-07 |
| Intact cycle, one extra loose distinction | x0, x1 | 6,075,008 / 12,555,008 | 11,390,626 / 23,540,626 | 3.38328e-07 |
| Removed holding versus extra loose distinction | x0, x1 | 5,670,000 / 12,555,008 | 10,631,250 / 23,540,626 | 3.17182e-07 |

On the 28-distinction switch source the within-U maximum is zero. The largest receiver-to-switched-leaf change is 44/105,763, where the raw count changes by 64,680 at fixed N=155,471,610. On the seven-holder example the displacement changes every rate in the full table, and the first table gives the 231/231 changes within the union of the two marked parents' holdings. The two matched sources are deliberate preparations. The local growth counterexample at three distinctions uses two presentations of *identical* states.

Under parity no receiver-local normalized rate changes on any of these matched edits. On the loose-count path, one pair outside the receiver changes uniform rate, while the original receiver-to-sender rates all agree. On the structural fixed-width examples and the six-knot removal, the complete raw parity tables agree. A change of raw counts under an added distinction is tabulated separately in the receipt for each class.

## Independent exact counts

The primary not-all-equal count uses inclusion–exclusion over monochromatic holdings. Within a selected set of failed holdings equate the names on each such holding. With c resulting classes of names, that event has \(2^c\) words. A pair in different classes disagrees on exactly half, and names in the same class always agree. The sum with alternating signs gives N and all D. Truth-table enumeration independently checks four small presentations, including a deliberate duplicate support and the nine-distinction case. For parity we reduce the binary constraint matrix. Its rank supplies N. A pair has disagreement zero when its two-name check is generated by the rows, and otherwise N/2.

A separate positive-integer calculation assigns words directly. Group positions with the same holders. Under any pins, count the all-zero, all-one and mixed choices in each group. For each holder keep only which values have already occurred, and on its last group require that both values occurred. The only weighting is the count of assignments to that literal collection of named positions. For D, pin one mark to zero and the other to one and double by complement symmetry. This recalculated all **19,130 pair entries** across both arms of the thirteen comparisons, including pairs newly present in the larger arm. It also checked that every possible mixed local word type extends on both switched 28-distinction starts (142 types each) and on the two 71-distinction starts (139 and 157 types). All their parity local projections have exactly one independent check. These are two algorithms run by the study team. Independent program review remains pending. [Inclusion–exclusion code](../../experiments/FOUR-READINGS-20261120-001B/FOUR-READINGS-20261120-001B-E001_state_growth/model.py) · [Independent direct counting code](../../experiments/FOUR-READINGS-20261120-001B/FOUR-READINGS-20261120-001B-E001_state_growth/verify.py) · [Verification receipt](../../artifacts/FOUR-READINGS-20261120-001B/FOUR-READINGS-20261120-001B-E001_state_growth/verification.json)
