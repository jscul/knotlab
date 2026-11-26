# Independent referee report on rule R read off the whole structure
**Confirmed with fixes. No Block.**

The closed-part exception, the 290 permanent failures in the sample, the flip formula and the three-reader value of 4 hold. The failure is an obstruction to imposing all knot parities with certainty on one state in the study's signed-operator reading. The ordinary engine's even-parity constraints still have the all-zero assignment.

## A. Counting the words on every read set

**Rebuilt.** From the 173 raw lists of holders, 21 types have pairwise commuting knot operators under R. Fourteen force an odd total sign and seven force even. Their 428 maximal read sets give 3,789 distinct nonempty subsets, counting each subset once per type. We also checked the empty set once per type. For the reference probabilities we projected a basis word onto the signed knot conditions, evaluated every commuting product on the resulting vector and recovered the outcome probabilities by exact inversion. Independently, we counted signs from swaps and tested the candidate parity equations on every outcome word. Every nonzero reference probability on a given read set was equal. [Checker](part_a_check.py) · [Per-type counts and witnesses](part_a_results.json)

| Rules used on a nonempty read set | Same allowed words as the state | No word allowed | Different, nonempty set of words |
|---|---:|---:|---:|
| Operator-signed products | 3,789 | 0 | 0 |
| Knots wholly inside the read set | 3,774 | 0 | 15 |
| GF(2) signs, products with at least one distinction left | 3,685 | 89 | 15 |
| GF(2) signs, including products with nothing left | 917 | 2,857 | 15 |

All 15 closed-part exceptions belong to the two four-knot closures sharing one knot. On that knot's six distinctions, closed counting permits 32 words. The state permits 16, with both triples odd. GF(2) permits the other 16, with both triples even. On the 14 odd types, a knot and the product of all its companions leave its own distinctions with opposite GF(2) signs. This accounts for all 89 contradictory nonempty reads under the study's convention. Each of the first three rules in the table agrees on all 21 empty reads. The last agrees on seven and gives a contradiction on fourteen.

## B. Ordinary growth and earlier readings

**Rebuilt.** We sampled 300 indices without replacement from the archived 7,075 census starts of three to five knots, with seed 20261128 and equal weighting per start. The checker reconstructs the holders, funding, births and fresh distinctions without importing the engine. It reads the archived results only after computing its own. All fields matched on all 300 starts and on the five named controls. [Growth checker](part_b_check.py)

| Status after up to four rounds and a funding test | Sampled starts | Starts with a permanently anticommuting knot pair |
|---|---:|---:|
| Still growing | 134 | 134 |
| Stalled | 70 | 70 |
| Closed | 96 | 86 |
| **Total** | **300** | **290** |

**Settling and stalls.** The engine's line 71 checks that the consumed distinctions have distinct parents. Line 81 equates their multiset with the full multiset of loose distinctions. Lines 85–87 retain the old knots and check that each distinction has one or two holders. Thus an already co-held pair stays co-held. Once either distinction has two holders, a later birth cannot take it. Two loose distinctions on different newest knots have their final co-holding decided by the next funded round, or by a terminal stop. At a shortage this engine admits no partial round: lines 39–43 return without a successor, and retrying the unchanged input gives the same shortage. Treating a stall as the whole is correct for this growth law. All 70 stalls were at the initial round. Even leaving their loose pairs open would already certify 52 of those 70; the terminal rule matters for the other 18. [Engine](../../../experiments/FORBIDDING-JOIN-20261120-001B/FORBIDDING-JOIN-20261120-001B-E001_free_readings/rival_growth.py#L35)

**Flip formula.** Compare the swap sign for two *existing* knot operators before and after a funded round. Each common child newly holds exactly one pair of their formerly loose distinctions. That removes one minus sign from their product interchange. No other change can affect the interchange. Only newest knots have loose distinctions provisionally available, with every initial knot counted as newest at round zero. On 29,572 comparisons of old pairs there were 1,035 changes, all and only those predicted by odd common-child parity: 383 from commuting to anticommuting and 652 the other way.

**Frozen predictions.** Prediction 2 failed and the README explicitly reports it as failed. It required more than one third of the 96 closers to have commuting knots, hence at least 33. There were 10. Of the 134 still growing, 112 had their first settled failure at round zero, 19 at round one and three at round two. Before the first failure, a commuting choice of open pairs existed at all 36 funded rounds, was unique at 13 and was realised at 16. At the other 589 funded rounds no choice worked. Of the 10 commuting closers, four force odd and six force even. The four odd ones each contradict GF(2) signs on a read set, and the six even ones do so on none. Two of the ten were closed from the start. On the eight with an earlier round, the earlier knots using the whole's signs already generated the entire final signed group. All 57 nonempty restrictions of maximal read sets to the earlier distinctions agreed. For prediction 7, the named four-place and three-place knots had no common child in the first round and their own pair settled commuting. The predicted conditional flip had no instance there. [Frozen predictions](../preregistration.md#L22) · [Outcome as reported](../README.md#L67)

## C. Three readers and the product-setting bound

**Three readers.** On the four knots with distinctions `012, 034, 135, 245`, use setting pairs `(0,5), (1,4), (2,3)`. The correlations at settings `000, 011, 101, 110` are respectively +1, +1, +1, −1. Their signed sum is **4**. In any single list of six values, multiplying those four triple products gives +1 because each distinction occurs twice. Hence a list scores at most 2. The four other setting triples have zero correlation.

**CHSH at most 2 is true** for the specified counting state and Hermitian products of distinction operators, with each setting of one reader commuting with both settings of the other. The counting state is the normalized projector onto the common signed knot conditions. Every nonscalar Pauli has trace zero, so a Hermitian monomial has expectation +1 or −1 when it is a signed member of the group generated by the signed knots, and zero otherwise. If each reader's own two settings commute, all four settings have a joint distribution and each outcome scores at most 2 in absolute value. If a reader's settings anticommute, multiplying each by the same other-reader setting gives two anticommuting correlation operators. At most one can be definite in a common state. Across the other reader's two settings, at most two correlations are nonzero. This proves the bound for every number of distinctions. The general bound for arbitrary bounded settings and the earlier referee's 14/5 example use a wider class of settings. [Stabilizer formalism](https://arxiv.org/abs/quant-ph/9807006) · [General two-reader bound](https://doi.org/10.1007/BF00417500) · [Earlier referee's exact example](../../NO-WHOLE-STATE-20261126-001/referee-R1/report.md)

**Rebuilt beyond single distinctions.** All 2,192 choices of knots on the 21 commuting census types yielded 1,096 distinct supports summed by type. None left exactly two distinctions, so every correlation between two different jointly readable single distinctions is zero. On the four-knot closure we tested all 63 nonidentity Hermitian products modulo overall sign, choosing two different settings per reader and allowing the two readers to reuse a setting. All four cross-reader pairs had to commute. Of 205,065 choices, 18,081 attained CHSH 2 after outcome relabelling. None exceeded 2. The bound is attained even by products whose constituents within each setting commute. The checked example has correlations (+1, 0, 0, −1). The proof also covers identity and repeated settings. [Product checker](part_c_check.py) · [Exact results](part_c_results.json)

## Fixes and evidence

1. **Not a block. Specify which GF(2) products were counted.** The README defines the domain with “Its *laws* are the products of knots whose distinctions left over after cancelling lie inside it, each with the sign of that product.” The table's GF(2) variant reads “products of knots, signed by the GF(2) sum of their signs”. Its implementation discards every product whose support cancels completely. The 3,685 agreements reproduce that implementation. If every product is retained, the product of all knots on an odd type asserts `0 = 1` even on the empty read. The 917 agreements and 2,857 contradictions on nonempty reads in the table above give the result for that reading. [README, part A](../README.md#L28) · [Filter in the study code](../part_a.py#L20)

2. **Narrowing. Identify the choice of counting state.** “The counting state is the one the signed knots fix: every knot even except, in each closed component, its last knot, which takes the sign the component's product forces; read by counting, it is uniform on each read set's allowed words.” The signs specify a common eigenspace. Uniform weighting on that eigenspace selects the counting state. On the five mutually meeting knots, the same signs admit two states in which distinction 0 takes opposite definite values. Its expectation in the counting state is zero. This also qualifies the rationale for A297. [README, definition](../README.md#L13) · [Register A297](../../../docs/ASSUMPTIONS.md#L6180) · [State witnesses](part_a_results.json)

3. **Narrowing. State what an earlier reading uses.** “R read off the whole is well defined and consistent with earlier readings.” Keeping a single final operator assignment and its signs makes earlier products of commuting knots retain their signs by inclusion. Agreement of the full law sets on earlier read sets was tested on the ten commuting closers, eight with an earlier stage. Recomputing R from the holders visible at each stage changes 1,035 old knot-pair signs. In A297, “the last round grown” describes a finite prefix for the 134 still growing. Its settled failures certify the whole, while pairs left open at the cutoff carry no final sign in that test. [Decision, item 2](../decision.md#L15) · [README, earlier readings](../README.md#L48) · [Register A297](../../../docs/ASSUMPTIONS.md#L6174)

4. **Narrowing. Specify the law that fails and its weighting.** “What R contradicts is the knots' own laws.” For the study's interchange signs, if `KL = −LK`, a simultaneous eigenvector with signs k and l would require `kl = −kl`. Thus on 290 sampled starts *any* signing fails to give certainty to all knot parities in one operator state. Of the remaining ten, four require the odd signing: imposing the ordinary engine's all-even signs in the operator reading fails on **294/300**, while the ordinary GF(2) engine itself allows the all-zero word on **300/300**. “Only a reader who signs by GF(2), as the engines do, is contradicted by a later layer, on every commuting closer R forces odd (4 of 4).” The four contradictions concern GF(2) addition applied to R's odd closing sign. The engine never assigns that sign. The sample gives the frequency for the stated weighting.

   The minus sign on every unheld pair is essential. Bare failure to commute as operators would allow the direct sum `D′ᵢ = 1 ⊕ Dᵢ` for every distinction. These operators have exactly the same commuting pairs, yet the first summand gives all knot products value +1. This example lies outside A297's signed realization and explains why the realization belongs in the claim. [Decision, item 3 and scope table](../decision.md#L19) · [A295, ordinary parity](../../../docs/ASSUMPTIONS.md#L6127) · [A297, signed realization](../../../docs/ASSUMPTIONS.md#L6174)

5. **Narrowing. Use common-child parity to predict a change in an existing pair.** “Growth with ordinary births makes swaps one pair at a time and so changes commutation parity by its own counts of common children: a state needs those swaps to come in pairs.” The three initial knots in the named four-knot closure have a single common child. All three old pairs change from anticommuting to commuting, and the closure admits a state. Conversely, starting from one four-place knot, the first round introduces four four-place children. An old knot pair could not have changed, yet the original knot and a child now anticommute permanently. The formula describes changes for old pairs. To demand a state one must also test the signs of pairs when they first exist and the consistency of the prescribed knot signs. [Decision, intuition and proposed growth rule](../decision.md#L52) · [Named controls](part_b_check.py)

6. **Narrowing. Distinguish joint readability, holder separation and a representation with separate reader factors.** “Under R values are read together only inside knots, so the tables are contextuality, not separated readers.” And “Readers whose knots never meet have no joint table under R at all.” Primitive values commute when *each pair* has a common holder. For setting `001`, the distinctions 0, 1 and 3 are pairwise co-held by three different knots and have a joint distribution. No knot holds all three. For products, an even number of anticommuting primitive swaps can give commuting settings even with no cross-reader co-holding. In the connected nine-distinction example, the products on (0,1) and (5,8) each take both signs with equal weight and have correlation −1. All four cross pairs of primitive distinctions anticommute. In a second example, two disjoint closed components admit all four joint tables of the tested product settings. Giving a joint table for every constituent primitive value would require the stronger pairwise co-holding condition.

   The score 4 rules out a single setting-independent list of six values. The construction assigns joint readings through shared holders and supplies no independent reader locations. The same table nevertheless admits three separate tensor factors. On the vector `(|000⟩ + |111⟩)/√2`, put settings `(X,Y)`, `(X,Y)`, `(X,−Y)` on the three respective factors. All 64 outcome probabilities match those from R: 16 zeroes, 16 quarters and 32 eighths. Thus the holder account and a mathematical three-party reading are compatible. [Decision, item 4](../decision.md#L23) · [README, reader claim](../README.md#L87) · [Exact checks](part_c_check.py) · [Mermin's inequality](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.65.1838)

## Reproduction and limits

From the repository root use `r=research/EVENTUAL-R-20261126-001/referee-R1`. Each command below uses `.venv/bin/python -B "$r/<script>"`. Each checker used one process under a 2 GiB address-space cap (`ulimit -v 2097152`); timed prefixes used the full-run settings. The two Part B invocations used at most two processes in total. Numerical library thread counts for Part C were set to one.

| Script | Timed prefix | Full computation | Prefix / full seconds |
|---|---|---|---:|
| `part_a_check.py` | `--limit 15` raw types | All 173 raw types | 0.03 / 0.20 |
| `part_b_check.py` | `--limit 8` of the seeded sample | All 300 starts | 0.12 / 0.27 |
| `part_b_check.py --named` | `--limit 1` | All five controls | 0.10 / 0.10 |
| `part_c_check.py` | `--pilot`, including 12 first-reader setting pairs | 1,953 first-reader pairs, eight triples, 173 raw types and product controls | 0.03 / 0.25 |

The largest recorded peak for a full checker was 41,052 KiB. Rerunning A and C reproduced every scientific field of the saved results. The frozen preregistration text through “Scaffolds named” matches its recorded checksum after removing the declared post-run addendum. The current growth checker from the study and its operator library also match their frozen checksums. The study documents the input-source changes in its own A and C scripts.

**Read as prior evidence.** The earlier refereed study distinguishes stage-by-stage R from a persistent assignment and establishes the earlier two-reader counterexample under its own rules. The present rebuild uses its raw census source. A295 records universal commutation in the ordinary engine. A297 adds the signed realization, the counting state and the weighting. None of these choices alters the canonical test on allowed states. [Earlier referee report](../../NO-WHOLE-STATE-20261126-001/referee-R1/report.md) · [A295 and A297](../../../docs/ASSUMPTIONS.md#L6127) · [Repository foundation and research discipline](../../../AGENTS.md#canonical-foundation)

**Not run.** Regeneration of the two input censuses, the other 6,775 growth starts, growth beyond four rounds, other engines or weightings, a full product-setting sweep on the other 20 commuting census types, or a fresh replay of the earlier study's separate two-reader example. The general CHSH argument covers those 20 types under the stated assumptions. All four items in the brief were reached.

## Referee disposition

| Scope | Verdict | Evidence |
|---|---|---|
| Whole-structure R study | Confirmed with fixes | Parts A, B and C rebuilt |
| R with a common definite-parity state | STOP as a rule for every grown start | 290 permanent counterexamples to any signing in the sample |
| Other growth or commutation rules | Unassessed | This replay used ordinary parity and R |
| G18, comparing growth laws | Obstruction confirmed | Four further closers require an odd signing |

**Next step:** STOP at the requested referee report.

| Direction | Payoff | Concreteness | Disposition |
|---|---|---|---|
| Qualify the six passages above | 2/3, keeps the numerical findings usable | 3/3, exact text and witnesses identified | For the study owner |

**Corrections:** Five narrowings and one other wording fix. No Block.  
**Goals:** G18 unchanged.  
**Assumptions:** A295 and A297 supply the two readings compared.  
**Scaffolds:** The 290/300 frequency gives one vote to each sampled start. The Part A totals count each read set once per type. The scalar-law convention, normalized counting projector and product-settings domain are explicit above.
