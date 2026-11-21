# Does one extra meeting let larger tree founders close?

**No. With six or more starting knots, adding one previously absent simple meeting to a tree never permits whole closure at any finite age under the registered opening cap.** For a funded founder there are two possibilities. Either separate groups of live knots keep separate descendants, or the source is a bare odd ring with exactly two loose distinctions at each knot. The latter pays the same number of two-parent births at every step. Ordinary parity never writes a zero-grant final knot in either case. Ordinary not-all-equal always requires a positive grant. [All-size proof](one_meeting.md) · [Earlier tree obstruction](../IDLE-PHASE-AND-TREE-CLOSURE-20261121-001/tree_proof.md)

The exact finite census covered **16,691 decorated founder types** across **376,737,408 distinct labelled decorated holdings**. Counting different trees and choices of the added meeting gives **1,442,385,024 labelled decorated histories**. Both ordinary laws produced the same funded parent rosters and grants throughout the four-cut observation. All 15,537 stalled types failed at their initial cut. Of the 1,154 funded types, 1,153 have more than one initial live group. The remaining type is the seven-knot ring. [Frozen source and minimum ordering](preregistration.md) · [Counting and independent checks](counting.md) · [Physical ledgers](../../artifacts/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings/physical_population.json.gz)

## Exact probabilities by founder weighting

Choose the starting size uniformly from six, seven and eight. At each holder the private supply is the amount required to reach three places at the new degree, plus one independent extra with probability \(1/4\). The first weighting chooses a uniform labelled tree and one uniform absent meeting. The second chooses uniformly among distinct labelled resulting meeting patterns. The following numerators are the masses funding all four cuts under either law. The remaining mass in each denominator stalled at cut one. [Exact numerator tables, stalls and coverage](../../artifacts/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings/population_table.json)

| Starting knots | Initial stalls / all decorated types | Types open after four cuts | Funded mass, tree then edit | Funded mass, distinct resulting holdings |
| ---: | ---: | ---: | ---: | ---: |
| 6 | 443 / 491 | 48 | 7,971,840 / 53,084,160 | 2,129,280 / 14,991,360 |
| 7 | 2,362 / 2,574 | 212 | 556,176,600 / 4,130,488,320 | 158,135,400 / 1,118,945,280 |
| 8 | 12,732 / 13,626 | 894 | 39,015,789,120 / 360,777,252,864 | 11,149,893,720 / 94,146,920,448 |

Across the three equally weighted sizes the probability of funding is \(2{,}279{,}463{,}687{,}661/17{,}401{,}865{,}306{,}112\), about **13.0990%**, for tree then edit. For distinct resulting holdings it is \(62{,}535{,}042{,}996{,}059/466{,}923{,}333{,}156{,}864\), about **13.3930%**. A resulting holding with a ring of length \(l\) has \(l\) possible deleted meetings giving its predecessor tree, so these weightings select different sources. Conditional on its starting size and ring length both give the following same funding probabilities.

| Ring length | 6 starting knots | 7 starting knots | 8 starting knots |
| ---: | ---: | ---: | ---: |
| 3 | 15/128 | 9/64 | 2,375,865/16,777,216 |
| 4 | 49/256 | 27/128 | 585/4,096 |
| 5 | 0 | 9/896 | 783/16,384 |
| 6 | 1 | 1/16 | 25/2,048 |
| 7 | Inapplicable | 1/16,384 | 0 |
| 8 | Inapplicable | Inapplicable | 1/65,536 |

At each age one through four, each starting size, and both weightings, whole-closure probability is **zero** for each ordinary law. The joint probability of parity closure with admission after reversing its final sign is **zero**. Admission *conditional on closure* is **undefined**, since there is no closing whole on which to perform this test. Not-all-equal has no corresponding sign choice. All terminal arity cells are empty, including the three-or-more-place criterion. The separately ranked ordinary and admitting least wholes and least founders do not exist in the registered class. Covered mass is one throughout. [Empty ranked witness sets](../../artifacts/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings/named_minima.json.gz)

## What the extra meeting changes

The controls below use genuine funded cases from the complete census. They illustrate the structural proof after the two separate minimum searches returned empty. Every eligible meeting deletion was replayed up to the symmetries of its decorated founder, keeping the same optional flags and recomputing the degree requirements. Identical private supplies were also tested wherever the resulting tree remained lawful. [Named holdings, allocations and all deletions](../../artifacts/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings/mechanism_controls.json.gz)

* In the bare six-knot ring with one opening at each knot, the alternating triples \(\{0,3,4\}\) and \(\{1,2,5\}\) each have pairwise witnesses and no single witness for the whole triple. Each knot owes one, so both triples are born together, each with one fresh distinction. Their live groups remain separate thereafter. All six ring deletions are equivalent here. In the fixed-flag predecessor two knots owe two with supply one, so its first cut stalls. Holding the complete private supply fixed during deletion would leave the two end knots with only two places apiece. The valid comparison measures the joint change in meeting and supply. [Six-knot controls](../../artifacts/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings/mechanism_controls.json.gz)
* In a six-knot founder with a four-knot ring the same parent pair \(\{1,2\}\) has two witnesses, knots 0 and 4. It owes one pair birth. The other related pairs \(\{1,3\}\) and \(\{2,3\}\) are already witnessed together with \(\{1,2\}\) by knot 0, so they remain separate pair births. Two other live groups also receive unary births. Of the two symmetry classes of deleted meetings, one predecessor stalls and one pays eight births. The edited founder pays six. At identical private supply both deletions would violate minimum arity. [Four-knot-ring controls](../../artifacts/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings/mechanism_controls.json.gz)
* In the bare seven-knot ring each holder has two openings. Seven distinct pairs each receive two new distinctions, and this end repeats. Removing any of the seven meetings gives a tree whose live relation has two groups. Keeping the optional flags gives the two new end knots three openings apiece and the first cut pays 11 births. Holding all supplies fixed at two gives a lawful tree in the registered flag domain and pays nine. Both trees have the same five multi-parent proposals. The seven-knot ring pays seven pair births and no unaries. Thus the new meeting changes the live connectivity even when every original private count is held fixed. [Both matched seven-knot controls](../../artifacts/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings/mechanism_controls.json.gz)

**A sign on a positive grant can be absorbed.** In that ring's first cut, parents 0 and 3 make knot 7 on two old inputs and two new names. Flipping its private name 21 reverses only knot 7's parity, with every older knot and its siblings held even. All 16,384 old even words survive. Each sign has exactly 2,097,152 extensions across the funded whole. The fresh-name flip pairs the two signs above each old word. A terminal sign reversal would require an actual implied, zero-fresh birth, of which the class has none. In a separate check at five founding knots, a three-knot ring with leaves on its two spent knots closes at the sixth parity cut on 35 knots and 71 distinctions. Its final four-parent equation follows from the 34 older rules and its supplied odd sign admits the operator reading. Under not-all-equal the same sixth birth brings one fresh name. This check lies outside the weighted size and cut ranges. [Actual fresh-grant word counts](../../artifacts/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings/mechanism_controls.json.gz) · [Boundary check outside the registered population](../KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001/boundary_checks.md)

The complete audit checked every funded cut, 4,616 per law, and all 44,037 births per law against a second roster and price calculation. Independent construction from decorated ring-and-branch codes agreed with the physical enumeration on every class, symmetry order, shortage and both four-cut histories. At six starting knots each of 829,440 labelled tree, edit and flag combinations was counted explicitly. No scientific run needed more than ten minutes. The numeric funding probabilities apply to the registered two weightings. The all-size closure exclusion holds separately for every founder satisfying the theorem. **Independent scientific referee pending.** [Proof](one_meeting.md) · [Independent checks](counting.md) · [Referee handoff](referee_handoff.md)

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — can one extra meeting give a larger closing whole? | **Status: Successful — complete exclusion** | No ranked ordinary or operator-admitting whole exists under the cap at six or more founders. |
| Local direction — connect tree closures to one additional meeting | Complete | Two witnesses for a pair, an unheld triple and changed connectivity were measured on funded founders. |
| Broader exploration — G17 meeting patterns and G18 law comparisons | Capability gained | An all-size restriction separates global closure from a paid repeating end or permanently separate live groups. |
| Long-term goal — G5 dynamics from native formation | Conditional progress | Receipts concern the supplied growth and funding law. They establish no derivation of that law. |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Test whether two added simple meetings can support whole closure under the same opening cap | 3/3 — locate the first change in eligibility as the old holdings acquire more meetings | 3/3 — finite labelled six-knot test with defined shortages and a physical closure criterion | Test connected six-knot founders with seven meetings → first fully verified closure or exhaustion through the declared cuts with the surviving live cases identified | Recommended · deferred |
| 2 | Predict the exact first-cut funding share under the one-meeting law for arbitrary size | 2/3 — changes a finite frequency into a scalable count | 2/3 — simple local charges are known, coupled flag counts remain | Count funded flags by the attached rooted trees → reproduce size eight and obtain the next exact size or exhibit a missing state in the count | Alternative · deferred |

**Corrections:** None to the earlier tree exclusion or the signed closing criterion.

**Goals:** B289 completes the one-added-meeting closure question for G17, with the ordinary-law comparison for G18 and the funded dynamics for G5.

**Assumptions:** A178 fixes the simple meeting edit, the cap, the two weightings and the four-cut observation for exact probability tables.

**Scaffolds:** The founder preparation, supply rule, whole-cut payment, ordinary knot laws and separately supplied sign comparison. Both weightings give the same closure exclusion and different funding frequencies.
