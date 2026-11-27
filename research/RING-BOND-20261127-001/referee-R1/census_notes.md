# What the before-growth census counted

With one vote per archived start, the registered search finds 64,845 bonds on 2,919 of all 7,075 starts. The held-out sample has 9,524 bonds on 408 of 1,000 starts. The frozen definition uses three disjoint agreements, two or three places per carrier and connected holders of at most four laws. Each holder law must be essential on the holders alone. Adding the other laws must preserve the image, and the complete values of any one stage knot must leave each reading undetermined on at least one feasible fixing. [Complete roster](census_population.json) · [Sample replay](census_heldout4.json)

| Change to the registered reading | Bonds on the 1,000 sampled starts | Starts with at least one |
| --- | ---: | ---: |
| Every selected holder law is individually essential on the whole start | 9,090 | 408 |
| Every law of the entire start is individually essential | 177 | 10 |
| Dropping one carrier place keeps the exact joint image | 1,067 | 86 |
| Dropping one carrier place keeps that image and all readings remain unread at single knots | 811 | 80 |
| Replacing one carrier input by an independent distinction keeps the exact joint image | 344 | 32 |
| Every carrier input can change its reading in some allowed single-distinction change | 9,516 | 408 |
| Every carrier uses at most one place of each knot | 2 | 1 |
| Each of the three readings takes both values under every feasible fixing of one knot | 0 | 0 |

None of the 9,524 agreements is unchanged as a function of the source states by dropping a place. A bond can nevertheless retain its *joint image* under a change to one of those functions. Removing a place leaves 8,713 bonds on 407 starts for which every single deletion fails to preserve a bond with the same image. [Carrier controls](census_heldout4.json) · [Independent-input control](census_population.json)

The two one-place bonds on the sample come from the closed four-knot start with supports (0,1,2), (0,3,4), (1,2,5), (3,4,5). In both, the first carrier is (0,5). For the other two use (1,3), (2,4) or (1,4), (2,3). Both bonds miss 001 and 010, every pair takes all four values, and removing each of the four laws restores both missing words. All 15 disjoint carrier triples were checked. Six pass the joint-state test before the single-knot filter and two survive that filter. [Literal counts and canonical knot checks](census_targeted.json)

A second search removed every holder restriction. Across all 7,075 sources, 10 of 21,726,950 unread disjoint triples satisfying the one-place rule have a bond, on five starts. Four of 15,797,484 triples with each reading open under every feasible one-knot fixing have a bond, on two starts. None retains its full joint image under every such fixing. The sampled counts are 2 of 3,071,175 and 0 of 2,232,122. On the source with supports (0,1,2), (0,3,4), (1,3,5), (2,4,6), the separately open comparisons [1=4], [2=3], [5=6] miss 001. The canonical checker passes all three contact assignments. The earlier seven-knot construction uses grouped comparisons outside this class. [Complete strict search](census_strict.json) · [Literal witness](census_targeted.json) · [Earlier construction](../../NAE-LAYER-20261127-001/referee-R1/carrier_notes.md)

Allowing disconnected sufficient holders of at most four knots adds 14,357 different bonds on 390 sampled starts, including 198 starts with no registered bond. The two searches together find bonds on 606 of the 1,000. Across the full roster this change adds 103,267 different bonds and gives bonds on 4,285 starts. One such source has a central (0,1,2) and three other knots (0,3,4), (1,5,6), (2,7,8). The latter three are pairwise disjoint. With [0=1=3], [2=4=7], [5=6=8] all true, call their common values u, v and w respectively. The three sufficient laws require u≠v, u≠w and v≠w. Removing any one restores 111. The central law is dispensable. [Disconnected holders](census_population.json) · [Witness and canonical knot test](census_targeted.json)

The separate prediction for the one-loose three-knot source, archive rank 21, holds. Its new knot is (4,5,6). The comparisons [0=5], [1=6], [2=3=4] miss 001. Their unique sufficient minimal holder consists of (0,2,3), (1,2,3), (4,5,6). The third knot shares no distinction with either of the others. On another source two different connected holders give the *same* 111 exclusion, with just two laws essential on the whole start. In all 434 sampled source bonds where the globally essential set is smaller than the chosen holder, that set alone admits an extra word. The 130 bonds with two or more registered equal-image certificates are a subset of those cases. [Literal holder deletions](census_targeted.json) · [Holder counts](census_heldout4.json)

Across both sampled rounds, 358 carrier triples had more than one local holder. Two on grown stages had different local missing sets. In both, the stage forbids a pair of values, so the first-holder tie rule changed zero acceptances. Of 44,370 local candidates, 5,092 kept their image but acquired a single-knot reading, and 444 changed image. Of the 38,834 accepted occurrences, 38,828 had a holder count and carrier lengths for which a word could violate the frozen bound. All 227,281 such word positions occurred. The search never uses that bound to discard a candidate. [Local and stage images](census_alternatives.json)

The larger-cap run matches all 100 of the every-tenth selected starts and all 175 stages. The totals are 4,867 at four holders and 6,153 at five. One grown stage with no bond at four gains two at five. Across the 1,000-start run, 730 starts fund an ordinary first round. Their stages give 29,310 bonds, including 23,760 with a birth among the chosen holders on 433 starts. A total of 480 stages have a reading shared by multiple bonds. The independent reconstruction agrees with all numerical row fields, all 2,651 saved examples at four holders and all 250 examples at five holders. Only three examples at most were saved per positive stage in the original run. [Four holders](census_heldout4.json) · [Five holders](census_heldout5.json)

Deleting each candidate law from the complete grown stage gives 23,663 bonds with a birth essential, on the same 433 starts. The remaining 97 counted with a birth among the chosen holders occur on 20 starts. Each individual birth can be removed from the full stage while its reading relation persists. In 28,663 of 29,310 grown bonds every chosen holder law is essential on the stage. No sampled grown bond needs every law of its entire stage. [Whole-stage birth deletion](census_birth.json)

Under even parity the loose distinctions on the three-knot ring have even sum on all eight source states. The one birth takes those three loose distinctions with zero fresh demand and its law already holds. Afterwards each distinction has two holders. At both stages, of the 15 disjoint triples only one has three readings unread at every knot, and zero of the 15 pass the joint-state test. The second stage tests the same eight states on the same six distinctions. [Literal parity ring](census_targeted.json)

## Exact wording for the decision

- **Narrowing.** In the [decision, opening](../decision.md), replace `"Held by the whole" means every law of its holders is essential.` with “In the local search, the chosen holders already give the stage's image and each of their laws is essential on those holders alone. Other stage laws can substitute for a holder law.” Under “On the owner's rungs”, replace the sentence beginning “A relation held by the whole and by no part” with “Of 9,524 sampled before-growth bonds, 177 need every law of the start. None of 29,310 sampled grown bonds needs every law of its whole stage. A birth is individually essential to at least one bond on 433 of the 730 funded starts.”
- **Narrowing.** In the [decision, answer 2](../decision.md), replace “The search would have reported any bond whose readings fail only that test, and none is counted” with “The search excludes readings determined on every feasible fixing of some one knot. Of the sampled local candidates evaluated on the complete stage, 5,092 kept their joint image but gained a single-knot reading. None of the 9,524 accepted before-growth bonds keeps each reading open under every feasible fixing of every knot.”
- **Narrowing.** In the [decision, scaffolds](../decision.md), replace “Each result above is about the model, except the choice of one bond, which is ours” with “The 408 of 1,000 before-growth result uses the registered carriers and connected holders. Keeping the carrier class but allowing disconnected holders gives 606 of 1,000. Requiring each carrier to use at most one place per knot gives one of 1,000.”
- **Record update.** In the [decision, last line](../decision.md), replace “Its census 21 prediction (a disconnected essential set) was not tested” with “The frozen run omitted disconnected holders. The independent check confirms the predicted relation after the one-loose three-knot start grows (4,5,6).”

## How to reproduce

The search enumerates finite truth tables modulo global complementation for not-all-equal. It searches every carrier in each candidate holder and checks word images after deleting each holder law. A private holder distinction outside all three carriers would let its law be satisfied freely, so such a holder cannot be minimal. Grown-stage images are checked separately with incremental satisfiability queries. The raw 7,075 starts supply the source supports. Growth uses the [independent ordinary rule](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py), previously compared with 33 archived first rounds and 199 births. Its funding status matches the current 1,000 rows and every grown knot count and distinction count. The stricter complete-stage enumeration uses no holder search. [Prior growth check](../../NAE-LAYER-20261127-001/referee-R1/growth_notes.md)

From the repository root, run one command at a time. The four-rank pilots measured about 0.29 seconds at four holders and 0.77 seconds at five, giving estimates of 72 and 20 seconds for the respective samples. The six-rank population and strict pilots took 0.21 and 0.08 seconds, giving estimates of 248 and 93 seconds. The alternative-holder pilot took 0.29 seconds for four starts, giving an estimate of 72 seconds. The literal witness pilot took 0.07 seconds. The birth-deletion pilot took 0.30 seconds for four starts, giving an estimate of 74 seconds. Exact times are in each output.

```sh
ulimit -v 2500000
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
r=research/RING-BOND-20261127-001/referee-R1
.venv/bin/python -B "$r/census_replay.py" --cap 4 --ranks 1 1695 3572 5273 --out "$r/census_pilot4.json"
.venv/bin/python -B "$r/census_replay.py" --cap 4 --out "$r/census_heldout4.json"
.venv/bin/python -B "$r/census_replay.py" --cap 5 --ranks 1 1695 3572 5273 --out "$r/census_pilot5.json"
.venv/bin/python -B "$r/census_replay.py" --cap 5 --out "$r/census_heldout5.json"
.venv/bin/python -B "$r/census_controls.py" targeted --limit 1 --out census_targeted_pilot.json
.venv/bin/python -B "$r/census_controls.py" targeted --out census_targeted.json
.venv/bin/python -B "$r/census_controls.py" alternatives --ranks 1 1695 3572 5273 --out census_alternatives_pilot.json
.venv/bin/python -B "$r/census_controls.py" alternatives --out census_alternatives.json
.venv/bin/python -B "$r/census_controls.py" population --ranks 1 477 1695 3572 5273 7000 --out census_population_pilot.json
.venv/bin/python -B "$r/census_controls.py" population --out census_population.json
.venv/bin/python -B "$r/census_strict.py" --ranks 1 477 1695 3572 5273 7000 --out census_strict_pilot.json
.venv/bin/python -B "$r/census_strict.py" --out census_strict.json
.venv/bin/python -B "$r/census_birth.py" --ranks 1 1695 3572 5273 --out census_birth_pilot.json
.venv/bin/python -B "$r/census_birth.py" --out census_birth.json
```

Grown stages outside the selected sample, unrestricted carrier functions, and unrestricted agreements with more than three carrier places were not run here. The complete-source searches cover all 7,075 archived starts with three to five knots. The unrestricted-holder search checks the two stronger single-knot readings for carriers of two or three places. The more permissive search admitting two places per knot under arbitrary holder sizes on the entire roster was not run.
