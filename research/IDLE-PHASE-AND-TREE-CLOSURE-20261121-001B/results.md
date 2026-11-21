# How often ordinary growth closes on the complete labelled-tree population

**The exact four-cut probability of parity closure is 591/16,000 (3.69375%). The probability that a draw closes and admits an operator reading after its closing sign is reversed is 339/64,000 (0.5296875%). Among closing draws, the exact admission share is 113/788 (14.3401%).** Under not-all-equal, the same founders have zero closure probability and no signed test applies. These values use equal probabilities for four through eight starting holders, uniform labelled trees at each size and independent extra-opening probability 1/4 at every holder. [Former source law](../ERASURE-AND-CLOSING-SIGNS-20261121-001B/preregistration.md) · [Frozen count](preregistration.md) · [Exact machine-readable table](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/census_audit.json)

**With this opening rule, a tree starting with six or more knots can never close at any finite age.** Its live parts either continue separately or its first cut cannot be funded. A fundable tree that could close has a single spent central holder and at most four live leaves. This conclusion holds at every size under the stated opening bound. The fraction among the three- and four-leaf founders uses the four actual cuts. [Structural proof and four named closing types](tree_count.md)

## Exact counts by starting size

For row \(n\), divide the integer masses in the table by \(D_n=n^{n-2}4^n\). There are \(n^{n-2}2^n\) distinct labelled decorated trees before the independent permutation of distinction names. A particular binary decoration with \(k\) extra openings has numerator \(3^{n-k}\), so the integer masses account for the original Bernoulli weighting. The two laws have the same funding stops. A still-open source has completed all four funded cuts.

| Initial knots | Decorated types | \(D_n\) | Initial stall, both laws | Parity open after four | Parity closes | Parity closes and admits | Admission given parity closure | Not-all-equal open after four |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 18 | 4,096 | 0 | 3,340 | 756 | 108 | 1/7 | 4,096 |
| 5 | 54 | 128,000 | 97,260 | 30,725 | 15 | 15 | 1 | 30,740 |
| 6 | 189 | 5,308,416 | 4,939,776 | 368,640 | 0 | 0 | Undefined | 368,640 |
| 7 | 700 | 275,365,888 | 247,464,448 | 27,901,440 | 0 | 0 | Undefined | 27,901,440 |
| 8 | 2,778 | 17,179,869,184 | 15,268,902,784 | 1,910,966,400 | 0 | 0 | Undefined | 1,910,966,400 |

At size four, the closure and admitting-closure probabilities are **189/1,024** and **27/1,024**. At size five both equal **3/25,600**. At the larger sizes both equal zero. Across the five equally weighted sizes the initial stall probability is 252,170,535,473,071/362,538,860,544,000 (69.5568%) for either law. The parity open-at-horizon probability is 19,395,409,181,917/72,507,772,108,800 (26.7494%). The not-all-equal open probability is 110,368,325,070,929/362,538,860,544,000 (30.4432%). For the mixed conditional, we divide the mean admitting-closure probability by the mean closure probability. [Mass by age, source size, number of extras, paid births and final arity](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/census_audit.json)

## The four closing types

The central holder has zero loose names in each type.

| Initial configuration | Weighted mass within its size | Paid closing cut | Closing size | Final places | One supplied odd sign |
| --- | ---: | ---: | --- | ---: | --- |
| Three leaves, none gets the extra opening | 324/4,096 | 2 | 8 knots, 12 names | 3 | Ordinary words vanish, operator refused |
| Three leaves, one gets the extra opening | 324/4,096 | 3 | 12 knots, 20 names | 3 | Ordinary words vanish, operator refused |
| Three leaves, two get the extra opening | 108/4,096 | 4 | 18 knots, 33 names | 3 | Ordinary words vanish, operator admits |
| Four leaves, all get the extra opening | 15/128,000 | 3 | 16 knots, 32 names | 4 | Ordinary words vanish, operator admits |

The three-leaf founder with an extra at every leaf remains open at the measured fourth cut, at 26 knots and 54 names. The four-leaf founder with any underfunded leaf stalls on its initial cut. No actual closure was a two-place tie, so using all terminal arities or requiring at least three gives the same table. Ordinary growth uses the sign implied by the older parity equations. The opposite sign is supplied only for the operator comparison. [All named representatives, shortfalls and signed certificates](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/representatives.json.gz) · [Physical replay details](representatives.md)

## Coverage and weighting checks

The census represented **69,347,360 labelled decorated trees** by 3,739 exact decorated types. An independent calculation decoded every one of the **280,388 Prüfer words** over all five sizes. It matched each uncoloured shape's multiplicity and every decorated orbit's weight, with separate mass checks at every number of extra openings. All 4,256 literal labelled decorated trees at sizes four and five were also grown under both laws, giving the same histories up to renaming. Source lawfulness follows by extending each locally permitted holder word outward along its tree under either rule. Human label order can change which private name is assigned to a child. The proof shows that the funded multiplicities, prices and signed outcome are invariant under these choices. [Proof of weighting and slot invariance](tree_count.md) · [Independent labelled path](../../experiments/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/literal_inputs.py)

Every class ran under both laws without outcome pruning. All 6,852 initial stalls (3,426 per law) had recorded physical shortages. Every paid cut was reproduced by an independent calculation of the groups witnessed at the growing end, their next demands and their fresh prices. A zero grant was checked on the physical holdings, on the previously loose names and against the complete old parity equations. The largest observed stage had 75 knots and 155 distinctions. The earlier observational limits of 512 and 4,096 therefore censor zero mass. [Physical and relabelling checks](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/representatives_audit.json) · [Independent reconciliation](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/census_audit.json)

The earlier sample contained 39, 44, 62, 43 and 68 draws at the five sizes. All 256 named founders and 504 recorded funded cuts across the two laws were replayed. The six observed closures all came from the 39 four-knot sources, with one admitting. The earlier 95% intervals were 0.865–5.031% for closure, 0.010–2.157% for admitting closure, and 0.421–64.123% for admission among closures. All three exact probabilities fall inside their corresponding intervals. The intervals belong to those 256 draws; this complete census introduces no sampling uncertainty. [Original observations](../ERASURE-AND-CLOSING-SIGNS-20261121-001B/populations.md) · [Actual named replay](../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/archived_tree_replay.json.gz)

The source weighting matters even though every physical growth and sign verdict is fixed.

| Probability of one extra opening per holder | Parity closure | Admitting parity closure | Admission given parity closure |
| --- | ---: | ---: | ---: |
| 0 | 1/20 | 0 | 0 |
| 1/4, original | 591/16,000 | 339/64,000 | 113/788 |
| 1/2 | 177/8,000 | 77/8,000 | 77/177 |
| 1 | 0 | 0 | Undefined |

The expression for arbitrary independent extra probability follows from the four classes. Changing the maximum number of loose distinctions would change the structural obstruction. Independent scientific referee pending. [Derivation](tree_count.md) · [Referee handoff](referee_handoff.md)

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — exact labelled-tree law | **Status: Successful** | All sizes, masses and terminal signs verified |
| Local direction — four-cut tree probabilities | Complete | Four closing classes exhaust the population |
| Broader exploration — G17 meeting patterns | Known alternatives | Changing the loose supply permits other closings |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | Exact proportions for a stated founder weighting |
| G18 Comparing growth laws and G5 Dynamics | Capability gained | Rule-dependent closure and a structural obstruction |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Predict operator admission from the holdings of longer founders known to close | 3/3 — connects ordinary growth to the signed obstruction | 2/3 — closure criterion known, signed pattern open | Examine chains of spent three-place witnesses with fully funded live connectors → certify a proposed criterion or exhibit equal proposed readings with opposite signed verdicts | Selected · awaiting go-ahead |
| 2 | Exact initial funding probabilities for larger labelled trees | 2/3 — distinguishes continuing growth from a stall | 3/3 — explicit local shortage formula | Count the next larger size by degree and live neighbours → exact funding probability | Alternative · deferred |

The first direction asks whether a signed verdict on a large closing whole can already be recognized in its original holdings. The existing cluster result supplies candidate families and their funding thresholds. A first comparison can use the shortest two chain lengths, then stop if the proposed criterion fails. The second uses a known finite test but refines only the funding frequency under this one weighting. Both are prospective directions outside the completed census. [Earlier chain law](../CHAIN-IDENT-20261119-001/chain_ident.md) · [Earlier relay criterion](../RELAY-IDENT-20261119-001/relay_ident.md)

**Corrections:** None to the earlier six observed closures and one admission or to the earlier closed-type census.

**Goals:** B288 completes the exact finite source question under G17 and compares the two ordinary laws for G18 and G5.

**Assumptions:** A176 fixes the source weighting and four-cut observation. Sensitivity was checked at three other extra-opening probabilities.

**Scaffolds:** Uniform starting size, labelled Prüfer weighting, independent private openings, the supplied ordinary law and the supplied single-sign operator test.
