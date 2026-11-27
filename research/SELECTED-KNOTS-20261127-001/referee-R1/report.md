# Independent referee report on which second-layer knots ordinary parity growth selects
**Refuted. Block on the claim that growth selects only knots that meet as a tree. The fixed-scale cluster result stands.**

On the study's own three rings of four knots, the same nine disjoint carriers support **two different independent sets of four equations**. Both give exactly the same 32 allowed joint states. One set meets as the reported tree. The other contains three knots meeting in a cycle through three different shared facts. Removing any equation from either set doubles its allowed states to 64. Neither carrier choice, redundant equations, nor solver error explains the difference. [Carrier and deletion certificate](natural_places.json) · [Two bases](record_checks.json)

## What holds

| Hand-off claim | Independent result |
| --- | --- |
| 1. Two second-layer knots share a fact | All six stages and all 30 least changes agree. The five carriers have eight joint values. Both triples have exactly 000, 011, 101 and 110. At scale 12, three of the five are class facts in round 4 and all five in rounds 5 and 6. In round 5 their least costs are 15, 15, 15, 13 and 13. Of 168 single-law deletions, 18 free only the whole-ring triple, six free only the first ring's family triple, and 144 free neither. No first-layer knot has a nonconstant local class fact at that scale in any of rounds 4–6. [Witness counts](witness_check.json) |
| 2. The earlier chosen reading gives a third-layer knot | All 18 chosen knots pass K1–K3. Their equations have rank 17 on 29 places and admit the measured 4,096 states. The ten least changes have size four and rank ten. The three proposed third-layer facts span two bits, take the four even triples, and each costs five to flip. Both additional four-place knots pass K1–K3. Each reads one independent third-layer bit. Admitting both preserves the relation and makes every third-layer class parity a sum of local reads. The round-24 physical replay also gave those 4,096 states on 29 disjoint carriers. [Witness and controls](witness_check.json) |
| 3. Exact two-family costs | Of 6,839 frozen pair tests, the formula missed three of 1,875 at round zero and passed all 4,964 at positive rounds. The eight-knot exception costs six against eight. The two twelve-knot exceptions cost eight against nine and six against eight. Both twelve-knot starts stalled before round one. On the eight-knot start, the direct and intervening-family routes tie at ten in round one. The funded nine-knot and seventeen-knot counterexamples below overturn the extrapolation. [Cost replay](cost_check.json) · [Attaining changes](pair_shortcut.json) |
| 4. A family sum costs the least crossing pair, and the fixed scales give the clusters | All 6,871 complementary-set comparisons on 3,465 stages agree with the least **measured** crossing pair. Only 1,735 comparisons on 204 stages admitted a competitor flipping four or more families that could change the requested sum. At each of scales 8 and 12, membership and dimension agree on all 3,465 stages. Only 119 and 115 stages respectively kept a proper nonzero space of sums. Across the 967 starts with scale readings, 144 of 180 nonroot internal clusters appeared as blocks at either recorded scale. [Stage costs](cost_check.json) · [Opportunity counts](recount.json) |
| 5. A single knot reads each third-layer fact of the chosen tree | A literal single-reader test passes all **224** nonzero class parities across 156 frozen starts. The other 819 eligible starts have zero such facts. The author's test computed whether the local reads **together span** the facts. On two larger witnesses exactly two of seven kept parities lack a single reader, while the local span still contains all seven. [Frozen recount and five-family witness](recount.json) · [Six-family witness](natural_places.json) |
| 6. The shortest-change reading | Some family sum survives on 105/928 census, 245/1,268 held-out, 69/216 sampled and 86/86 built positive-round stages. Combined, that is 505/2,498 stages and 137/628 starts with a positive read round. Of the 505 stages, 373 keep **every** family sum. Of the remaining 132, only **48** reproduce an intermediate threshold level of the tree. The other **84** keep a different set of parities. [Exact mask comparison](cost_check.json) |
| 7. Growth selects the tree's knots and precludes a whole-held third layer | The cluster hierarchy is determined by the start for the fixed-scale reading of family sums. Restricting its equations to each parent with its immediate children is an additional choice. We found 11 minimal knots on its nine places in the frozen three-ring example. A third-layer parity outside the span of local class facts remains open for other growth-supplied readings. [All 11 projections](natural_places.json) · [Tree-span argument](natural_notes.md) |

## The fixes

**Block — selection of knots.** Replace “Its nodes, each bound with its children, are the second-layer knots growth selects” in [decision, item 2](../decision.md), and the corresponding claim in [the closing summary](../README.md), with “The family costs determine the threshold partitions. Parent-with-children equations give one presentation of their facts.”

For ring *i*, let its two family parities be *pᵢ* and *qᵢ*, with ring parity *Rᵢ = pᵢ + qᵢ*. Use each ring's starting loose distinctions for its sum and its families' first-round fresh distinctions for the summands. At round five, all nine are whole-held facts at scale 12. The complete list of minimal parity relations has four triples, three quadruples, three quintuples and one sextuple. All pass K1–K3. The three quadruples are

| Knot | Its four places |
| --- | --- |
| First | p₁, q₁, R₂, R₃ |
| Second | R₁, p₂, q₂, R₃ |
| Third | R₁, R₂, p₃, q₃ |

Each pair shares a different ring fact. None is shared by all three. Removing any of ring *i*'s six first-round birth laws frees only its quadruple among these three. To obtain the second independent basis, keep the whole-ring triple and add it to each of the three family triples. The tree basis uses 12 place occurrences and the other uses 15. Both rules respect renaming. A preference for shorter equations would distinguish them, if growth supplied such a preference. The alternative using every family's generation is checked separately on three rings of five knots. [Minimal relations and physical controls](natural_notes.md) · [Basis checks](record_checks.json)

**Block — the unrestricted positive-round pair formula.** Replace “Prove the pair cost d + 2 + 2t from round 1 (and the round-0 route through a third family), and with it the tree” in [the proposed direction](../decision.md) with “The direct route costs d + 2 + 2t. The exact pair cost is the least sum of direct costs along a chain of families.” Here *d* counts start-holder steps and *t* counts funded rounds. On a nine-knot start the outer families are eight steps apart. In round one each outer family can change with the middle family for five distinctions. Adding the two changes preserves the middle fact. The exact minimum is **10**, against **12** directly. The original solver independently returns 10. At round five a seventeen-knot start with 233 distinctions costs **26**, against **28**. Lengthening the middle family gives this failure at any specified finite round. [Attaining changes](pair_shortcut.json) · [Construction](pair_shortcut.py)

A bookkeeping holder for each family's loose distinctions turns an exact two-family change into a route between the two odd holders. This route may pass through a third family. New births preserve old holder-step distances because every pair of their parents already has a common witness. Thus direct routes grow by two steps per funded round. Every route that flips a set's sum must cross its cut, and one direct crossing attains the least such cost. This explains why the cost of a **set sum** and its threshold partition survive failures of the direct **pair** formula. [Derivation](cost_notes.md) · [Earlier proof for set sums](../../THIRD-LAYER-20261126-001/referee-R1/argument.md)

**Block — the universal single-reader inference.** Replace “They share facts only parent to child, never in a loop, and every fact of the layer above is read by one of them (all 156 starts with such facts)” in [decision item 3](../decision.md) with “For the parent-with-children presentation under globally least changes, the local class parities span all class parities. Each of the 224 frozen nonzero parities also has a single reader.” Replace the following sentence about a third layer needing chosen places with “A third-layer fact outside the local span on a different growth-supplied reading remains open.”

Rename “layer-three facts read by no single second-layer knot (dimension)” in [the calculator](../tree.py) to “dimension outside the span of the knots' class facts”. A literal single-reader test uses the **union** of the knots' local functions modulo the laws. The calculator uses their **span**. At round five on six five-knot rings, all nine physical places are whole-held at scale 12. Of seven nonzero upper class parities, two need more than one of the four tree knots. Both have single readers when all minimal knots are admitted. The tree-span test itself had **zero possible counterexamples**. Its globally least words flip two sibling leaves. A kept parity assigns all leaf siblings of each parent the same coefficient, and their sum is readable at that parent. Those sums generate every kept parity. Switching the upper-layer rule to all tied shortest changes **through each place** gives zero class parities on all 975 frozen starts. [Physical counterexample](natural_notes.md) · [Second witness and argument](recount_notes.md)

**Narrowing — which places qualify.** Qualify “a second-layer knot for every node with two or more children” in [the tree calculation](../tree.py). The all-family root parity is fixed and is omitted as a place. Of the 1,187 listed equations, **863** are two-place equalities between complementary root-child sums. The other 324 are 304 triples and 20 quadruples. If the intended claim requires each constituent fact to be whole-held at the layer below, 221 of those 324 equations include a leaf family whose entire starting carrier lies in one knot. When that parity is a class fact, that knot already reads it. Report the two-place ties separately and require a local-read check for claims about whole-held places. [Arity counts](recount.json) · [Single-holder counts](record_checks.json)

**Narrowing — freeze, coverage and reading.** Replace the opening sentence of [the results, ending “no deviation”](../README.md#what-was-found) with “The frozen protocol ran. Its all-round pair prediction failed. Positive rounds are a retrospective restriction. The planned follow-up on a cost failure was not reported at closure.” The committed predictions, scales and solver source are intact. The three-ring witness was examined before the freeze. All 2,333 starts repeat the preceding study's rosters in order. The census set samples 1,000 of 7,075 representatives up to renaming. The other two sampled rosters use labelled draws with replacement, conditioned on connectedness, minimum arity three, and caps of 18 or 30 distinctions. The 33 built starts were chosen constructions. In the raw files, 24 eight-family stages have empty sum-failure fields although the sum check was skipped. The original crossing comparator uses predicted direct costs. The independent replay used the measured pair costs as well. [Freeze and weighting](record_checks.json) · [Recount](recount.json)

Replace “under the shortest changes the tree is seen on a minority of starts” in [the closing summary](../README.md) with “505 of 2,498 later stages keep a family sum. A proper nonzero space agrees with a threshold level on 48 and disagrees on 84.” Replace “two rounds per two distinctions” there with “one round per two distinctions”. All 1,870 matched partitions agree at scale 8 in round *t* and scale 12 in round *t* + 2. [Mask comparison](cost_check.json) · [Shift check](recount.json)

**Not a block — public wording and credit.** Apply the selection and single-reader replacements above to the [G17/G18 checkpoint](../../../docs/RESEARCH_GOALS.md#L6163), starting at “growth selects the tree's nodes as second-layer knots”. In [assumption A303](../../../docs/ASSUMPTIONS.md#L6305), replace the justification beginning “Given the places, the knots are the minimal relations and nothing else is chosen” with “The parent-with-children roster selects some of the minimal relations among these places.” The [guide's tower row](../../../publication/knotlab/INTUITIONS.md#L6302) leaves selection open. Its preceding row still says “on 10 of 12 three-ring built starts read”. Replace that phrase with “on 8 of 12 for family facts and 4 of 12 for whole-ring facts at the tested scales”, matching the guide's own prose and the earlier raw scale rows. Earlier work already established the separately carried facts, the funded-round increment for sums, and the chosen 29-place example. The study adds pair measurements and the fixed-scale cluster comparison. [Five prior-work searches and guide recount](record_checks.json) · [Binding review](../../BINDING-20261126-001/referee-R1/report.md) · [Third-layer review](../../THIRD-LAYER-20261126-001/referee-R1/report.md)

## What was not run

Exhaustive larger starts, all later rounds, the forbidding laws, every carrier rule, and an exhaustive search for a third layer were not run. Beyond the frozen rows the cost replay covered 1,969 stages, through round seven or 512 distinctions, including 144 additional labelled draws and four larger ring constructions. All 58 eligible larger sampled starts stalled before round one. Attained higher rounds on constructed starts therefore carry different evidence. [Coverage and seeds](cost_check.json)

## How it was checked

The growth and reading implementations are independent. The canonical checker tested the projected allowed states. Regrowth matched 8,601 archived births across 1,866 round logs. Literal enumeration checked all 234,368 allowed states on 37 small stages against the family-signature minima. The frozen tables store exceptions and counts. Their missing solver assignments were replaced by an independent calculation from the holdings. [Growth and costs](cost_check.py) · [Witness verification](witness_check.py)

Unmodified low-level solver functions were isolated as test targets. No author reading or analysis module was imported. Literal states agreed on 202 single-target and 1,008 joint-target checks and 126 tuple images, including fixed, incompatible and zero targets. Cap controls straddled 40 and 60. The joint-target solver uses the same cap string for impossibility and an over-cap solution. All frozen pair targets were feasible and had minimum at most 17. The largest frozen set minimum was 15. [Solver checks](record_checks.json)

Run from the repository root. Each timed pilot uses the same process and memory settings as its full run. The commands execute sequentially. The JSON outputs beside this report hold the detailed counts.

```sh
r=research/SELECTED-KNOTS-20261127-001/referee-R1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
for check in pair_shortcut cost_check recount natural_places witness_check record_checks
do
    (ulimit -v 2621440
     /usr/bin/time -f '%e seconds, %M KiB' .venv/bin/python -B "$r/$check.py" --pilot &&
     .venv/bin/python -B "$r/$check.py") || exit 1
done
```

| Scope | Verdict | Why |
| --- | --- | --- |
| Closed study | Refuted | Same nine places admit an independent basis with a cycle |
| Family sums under fixed scales | Confirmed | All 6,871 set costs and both scale tables agree |
| Parent-with-children presentation | Conditional obstruction | Its local facts span its upper class space |
| G17 meeting patterns and G18 comparing growth laws | Selection remains open | The law and start permit different knot rosters |

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Identify a growth rule that distinguishes the two bases | 3/3 | 2/3 | Test a rule stated on the holdings against both 32-state presentations | Alternative · deferred |
| 2 | Correct the closed record | 2/3 | 3/3 | Apply the replacement sentences to the cited files and compare with the certificates | Alternative · deferred |

**STOP.** The cycle and positive-round cost witness settle the claims under review. A law distinguishing the two presentations would reopen the selection question.

**Corrections:** Blocks on unique tree selection, the unrestricted pair formula and universal single-reader inference. The fixed-scale cost and cluster counts stand.  
**Goals:** Qualify the G17/G18 checkpoint as specified above.  
**Assumptions:** A303 governs both places and the choice of equations among them.  
**Scaffolds:** The scales, the two distinct shortest-change rules, the carriers, and the rule for retaining knots each have an explicit comparison. The proposed source corrections are recorded here for the owner.
