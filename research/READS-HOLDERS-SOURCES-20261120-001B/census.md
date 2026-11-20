# Allowed states and growth through nine distinctions

The complete census found exactly one type of not-all-equal state set with different named irredundant holdings. Its two presentations on six distinctions are related by a state symmetry, and both are already closed. Every counted not-all-equal state set determines its ordinary growth. Under parity, five distinctions suffice for equal states with four births in one presentation and three in the other. Independent program referee review is pending. [Frozen design](preregistration.md) · [Exact census](../../artifacts/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant/census_summary.json)

## Denominators

In increasing order of width from three through nine, the connected structural counts are 2, 4, 9, 25, 67, 200 and 645 up to renaming, or 2, 12, 117, 1,733, 31,516, 717,650 and 19,552,861 with named distinctions. These include starts that fail the local projection or deletion test. Holder order supplies no additional name. The table counts state classes after both gates. In columns with two values, the first keeps distinction names and the second admits renaming. The last column gives named growth ambiguity, growth ambiguity under state-preserving renaming, and ambiguity with only participating parents and births retained, in that order.

| Distinctions | Law | Lawful starts, named / renamed | Irredundant starts, named / renamed | State classes, named / renamed | State classes with different holdings, named / renamed | State classes with different growth, named / state-matched / unmarked |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 3 | Not-all-equal | 2 / 2 | 1 / 1 | 1 / 1 | 0 / 0 | 0 / 0 / 0 |
| 4 | Not-all-equal | 8 / 3 | 7 / 2 | 7 / 2 | 0 / 0 | 0 / 0 / 0 |
| 5 | Not-all-equal | 87 / 6 | 86 / 5 | 86 / 5 | 0 / 0 | 0 / 0 / 0 |
| 6 | Not-all-equal | 1,412 / 17 | 1,411 / 16 | 1,396 / 16 | 15 / 0 | 0 / 0 / 0 |
| 7 | Not-all-equal | 27,533 / 46 | 27,532 / 45 | 27,532 / 45 | 0 / 0 | 0 / 0 / 0 |
| 8 | Not-all-equal | 648,797 / 144 | 648,796 / 143 | 648,796 / 143 | 0 / 0 | 0 / 0 / 0 |
| 9 | Not-all-equal | 18,080,457 / 480 | 18,072,896 / 478 | 18,072,896 / 478 | 0 / 0 | 0 / 0 / 0 |
| 3 | Even parity | 2 / 2 | 1 / 1 | 1 / 1 | 0 / 0 | 0 / 0 / 0 |
| 4 | Even parity | 8 / 3 | 7 / 2 | 7 / 2 | 0 / 0 | 0 / 0 / 0 |
| 5 | Even parity | 72 / 6 | 56 / 4 | 26 / 3 | 15 / 1 | 15 / 1 / 1 |
| 6 | Even parity | 1,142 / 15 | 991 / 10 | 346 / 7 | 330 / 2 | 330 / 2 / 2 |
| 7 | Even parity | 19,518 / 36 | 16,822 / 27 | 4,607 / 15 | 4,585 / 7 | 4,585 / 7 / 7 |
| 8 | Even parity | 462,597 / 103 | 405,623 / 81 | 79,192 / 34 | 79,163 / 19 | 79,163 / 19 / 16 |
| 9 | Even parity | 12,658,110 / 327 | 11,209,144 / 265 | 1,862,744 / 92 | 1,862,707 / 55 | 1,827,427 / 55 / 44 |

## Smallest comparisons and information costs

**Not-all-equal.** The presentations `012, 034, 135, 245` and `013, 024, 125, 345` have the same 18 allowed states. A sequence such as `012` denotes the support consisting of distinctions 0, 1 and 2. With these support orders, the integer words that violate just the deleted rule can be (7, 6, 5, 3) and (20, 21, 17, 5), respectively, with distinction i holding the bit of value 2ⁱ. The state permutation sending (0, 1, 2, 3, 4, 5) to (0, 2, 4, 1, 3, 5) exchanges the presentations. Every distinction is held twice in both, so there are no births. Each of the 15 named state sets in this class has exactly two named presentations. All other counted not-all-equal state sets have just one. [Earlier six-distinction example](../STATES-GROWTH-20261119-001/preregistration.md) · [Literal witnesses and counts](../../artifacts/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant/census_summary.json)

**Even parity.** The two starts `014, 234` and `0123, 234` have the same eight allowed states. Summing the parity rules on `014` and `234` gives the rule on `0123`, and summing those on `0123` and `234` recovers the rule on `014`. Deletion witnesses in the indicated order can be (1, 4) and (1, 16). In the first start each holder has two loose distinctions, and each gives two one-parent births. In the second start `0123` gives two and `234` gives one. Each child has two fresh distinctions. The difference survives discarding names and original supports. This state set has a third named presentation `014, 0123`, with three named rosters in all and two fully unmarked rosters. A pair with matching terminal outcomes first occurs at eight distinctions, where `014, 256, 357, 467` and `014, 256, 357, 0167` both stall for lack of loose distinctions. At nine distinctions, 35,280 named state sets have multiple holdings and a single named first roster, all funding stalls. [Minimum comparisons and exact first rosters](../../artifacts/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant/census_summary.json)

For a fixed, known state set with k possible outputs, any fixed-length index needs at least ⌈log₂ k⌉ bits, and enumerating the outputs supplies an index of that length. The not-all-equal census needs at most one bit for named holdings and zero bits for growth. At the parity minimum, named holdings and named growth each need two bits, and fully unmarked growth needs one. Through width nine, the parity maxima over state sets are 72 named holdings, 54 named rosters, 15 roster types under state-preserving renaming and seven fully unmarked histories, requiring seven, six, four and three bits respectively. The first parent lists determine the next witnesses by their common parents, and induction carries equality of the first roster through later steps. [Why the first roster suffices](../FOUR-READINGS-20261120-001B/results.md#all-parity-changes-that-preserve-the-states)

## Completeness and replay

Each distinction is specified up to naming by its one or two holders. The inherited complete enumeration supplies all multiplicities on all meeting patterns at these widths. Its structural totals agree with the independent permutation-fixed counts. We restricted it to connected starts, tested both laws on all 2ⁿ words, and required each actual support to project onto the full local law. The two erasure tests agreed on every lawful start. A word gained on deleting a rule violates precisely that rule, so the projection on its former support gains a word as well. All original names remain in the comparison. [Prior structural check](../FOUR-READINGS-20261120-001C/results.md#with-settings-inside-the-state-no-strict-excess-appeared-through-ten-distinctions)

For each lawful relation we computed the whole family of supports whose projection equals the local law. Their conjunction recovers the relation because every candidate rule follows from the states and the family contains every actual support. Permuting the distinction names of that family is therefore equivalent to permuting the entire state set. Adding the first roster with parent supports, multiplicities and fresh counts detects exactly the renamings that preserve both state and growth. The named counts follow by orbit–stabilizer from these symmetries. Direct named enumeration through five independently reproduced the lawful and irredundant denominators and the named ambiguities. [Enumeration code](../../experiments/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant/census_irredundant.py)

A second implementation searched the full candidate family for irredundant covers of the forbidden words. It reproduced all named holding counts on the 844 representative state sets and confirmed the literal words, projections, deletion witnesses and first growth records of the 1,080 presentation representatives. For every ambiguous state class it independently permuted the allowed words and confirmed the number of presentation and growth classes under those symmetries. It used the ordinary end operator for growth and the canonical knot checker on the 14 full local relations. The earlier seven-distinction comparison has 52 states in both arms, with only 28 of the 30 not-all-equal words in the wider five-place projection. The nine-distinction example with a central ternary and three ternaries each sharing one of its distinctions has 162 states and five exact candidate supports. The four ternaries alone are indispensable in the full candidate family and give its unique irredundant presentation. The final census and replay took 6.47 and 4.92 seconds, with peaks of 82,768 and 23,424 KiB under a six-GiB cap. [Replay code](../../experiments/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant/census_verify.py) · [Replay receipt](../../artifacts/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant/census_verification.json) · [Whole states and presentations](../../artifacts/READS-HOLDERS-SOURCES-20261120-001B/READS-HOLDERS-SOURCES-20261120-001B-E001_irredundant/census_cases.json.gz)

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| Complete census through nine distinctions | **Status:** Successful · referee pending | One not-all-equal named ambiguity, with identical closure |
| Local direction · recover first parents | Bounded result | Not-all-equal determines growth through nine, and even parity fails at five |
| Broader exploration · physical recovery | Known sufficient cases | The nine-distinction control is recovered by indispensable candidate rules |
| G5 and G18 · ordinary growth under the two laws | Obstruction and capability | The laws differ under the same local projection and deletion gates |

**Next step:** Continue — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- |
| 1 | Integrate the complete census with the recovery study | 2/3 | 3/3 | Check both minima and share the replay → place the finite bound alongside the named-class results | Selected · started |
| 2 | Not-all-equal recovery beyond nine distinctions | 2/3 | 1/3 | Seek a wider ambiguity with a live parent → find a witness or prove a broader sufficient condition | Alternative · deferred |

The first direction combines the bounded identification result with the separate proof and sample evidence. The in-study replay has passed, and the referee still needs to check the enumeration. The second would decide whether the observed recovery extends to wider sources. The sole observed ambiguity gives a closed comparison and leaves the wider live case open.

**Corrections:** None. The earlier seven-distinction case remains an equal-state pair under its own gate. Its wider support fails the full-projection gate used here.

**Goals:** G5 gains a minimum counterexample for irredundant parity growth. G18 gains a like-for-like comparison with not-all-equal.

**Assumptions:** A97 remains under challenge for state-derived readings. The parity example loses growth information even with all states supplied. The not-all-equal census preserves growth information through nine, with a difference in named holdings at six.

**Scaffolds:** The two supplied laws, physical holding limit, connection and projection gates, census bound and three growth matchings define the comparison. Each object contributes once to its corresponding census count.
