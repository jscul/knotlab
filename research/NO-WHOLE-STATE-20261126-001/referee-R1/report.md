# Independent referee report on patterns read part by part
**Confirmed with fixes. No Block.**

Ordinary growth closes the three-knot fixture even. Changing that sign gives exactly the three-reader table. Rule R forces the odd sign on the finished fixture and on 12 of the 121 reached types. Every one of the 173 stored types admits an odd closing on a common state under some choice of commutation signs.

## What was rebuilt

**C. One funded birth.** The three older knots witness the three pairs of live knots. No older knot witnesses all three. The resulting single proposal takes the loose distinctions 2, 4 and 5. All eight older states already have even parity there, the next demand is zero, and the grant is zero. Each of the six distinctions now has two holders. The even close preserves all eight states. The odd close admits zero assignments to the whole.

The target was fixed before comparing either sign. In reader order, X and Y correspond to (4,0), (5,1) and (2,3). We used the state (|000⟩ − |111⟩)/√2 and labelled the +1 and −1 outcomes 0 and 1. We computed the target from squared amplitudes and the part tables by enumerating allowed words. With the odd close, **64/64** entries match, with 16 zeros, 16 quarters and 32 eighths. With the even close, **56/64** match that same target and **64/64** match the even whole's marginals. For each sign all 76 marginal entries agree across 28 pairs of settings, including four empty overlaps. Erasing any one scored equation leaves eight assignments projecting to four words. The other three equations force the opposite parity at **4/4** scored settings with the odd close, and the same parity at **4/4** with the even close. [Fixture rebuild](fixture_check.py)

**D. Reordering.** Among the 115 stored signed-identity witnesses, every distinction squared to the identity, every pair held together commuted, and all knot products were signed identities. In **115/115**, multiplying the operators and counting interleaved anticommuting pairs independently gave the same odd total sign. For the five mutually meeting knots the sign bits were `00001` and the count was five. On the four-knot fixture the explicit reader operators obey R on every pair. All six pairs of knot products commute. On the state above the signs are `0001`, with one interleaved anticommuting pair. To see the identity, cancel the two occurrences of one distinction. Another distinction contributes a minus sign precisely when it anticommutes and appears once between them. Repeating counts each contributing pair once. [Operator rebuild](sign_check.py)

**E. Census.** R1 asks whether every pair of knot products commutes under R. R2 is the total sign when R1 holds. R3 asks whether some choice of anticommuting unheld pairs gives commuting knot products with an odd total. These are rebuilt counts. The stored input supplies the holder patterns and the earlier signed-identity classification. We recomputed the possible last knots, the labelled multiplicities, and every R column before comparing the 173 output rows. [Census rebuild](census_check.py)

| Weighting | Set | Total | R1 | R2 odd | R2 even | R3 |
|---|---|---:|---:|---:|---:|---:|
| One vote per type | All | 173 | 21 | 14 | 7 | 173 |
| One vote per type | Reached | 121 | 17 | 12 | 5 | 121 |
| One vote per type | Reached, no odd signed-identity reading | 42 | 4 | 2 | 2 | 42 |
| One vote per labelled pattern | All | 238,811 | 3,425 | 1,165 | 2,260 | 238,811 |
| One vote per labelled pattern | Reached | 177,321 | 3,240 | 1,085 | 2,155 | 177,321 |
| One vote per labelled pattern | Reached, no odd signed-identity reading | 80,300 | 1,901 | 11 | 1,890 | 80,300 |

For each of the 173 types the checker finds one R3 solution, constructs a nonzero state, checks that all older knots have eigenvalue +1, and applies the closing product to verify −1. Under R it also builds a state for each of the 21 feasible types. The degree formula agrees on 173/173. The literature's planarity test selects exactly the 58 stored odd signed-identity negatives. All 420 order and name shuffles preserved R2 (20 per R1 type, seed 20261127). The named six- and seven-knot all-pairs controls and the one knot meeting all of two groups of three give odd. The three-against-four control gives even. The three-reader and nine-distinction controls give R1 and odd. R3 fails for the two-reader pattern and for each of the four repeated-meeting controls. These reproduce the eight preregistered tests, with the representation qualification to prediction 7 below. [Preregistration](../preregistration.md)

**Why the R3 criterion extends beyond the census.** For a finite connected pattern with two distinct holders per distinction, add one knot. For each old knot $v$, give it a fresh distinction $y_v$ shared with the new knot. Given R3, assign $y_v$ the old knot product $K_v$. The enlarged old products are +I, and the new product is −I. Conversely, take an odd signed-identity Pauli reading of the enlargement. The $y_v$ commute in the new knot, and each old $K_v$ equals its $y_v$ up to the prescribed sign. Thus the $K_v$ commute and their product is −I. A common eigenstate exists. Negating a distinction flips the two incident signs, so connectedness permits any placement of signs with the same total. Arkhipov's Theorem 21 and Pauli construction in Corollary 30 give precisely this reading when the enlarged sharing is nonplanar. Adding one universal holder gives the literature's cone, which is planar exactly when the original is outerplanar. Removal exposes every old holder to the same region, and insertion there reverses the operation. Repeated meetings preserve the equivalence. This proves the stated criterion within R3's assumptions. We also searched holder orders directly on the finite inputs. [Arkhipov (2012), Theorem 21 and Corollary 30](https://arxiv.org/pdf/1209.3819)

**32 against 16.** With two four-knot closures sharing one knot, we chose all seven signs even, a consistent choice under R. The six shared-knot distinctions commute. One closed-part parity equation permits 32 words. Projecting a concrete state onto each of the 64 outcomes gives **16 probabilities of 1/16** and 48 zeros. Each of the two triples has odd parity in this signing. These are actual outcome probabilities, independently of a rank count. [State and part rebuild](part_check.py)

**F and G.** On the two-reader pattern the first reader reports the parity of its two distinctions and the second reports one distinction. At each of the four settings there are four equiprobable local words. The complete local records have identical marginals when the other setting changes. The four correlators are (1, 1, 1, −1), hence **CHSH 4**. The all-even control on the same holders gives **2**. On the eight-knot pattern of three-label subsets, R1 fails but an explicit R3 state reproduces all **64/64 single-knot probabilities**. At the fixture birth the ordered product of 2, 4 and 5 squares to −I in the pre-birth reading and +I in the post-birth reading. Even the three older knot products anticommute in pairs before that change and commute in pairs afterwards. [Argument checks](part_check.py)

## Fixes and their evidence

1. **Not a block — fix the target in the control.** The exact output field is `'probabilities matching the three-reader target': '%d of 64' % match`. Lines 35–37 derive its reference parity from the pattern being tested, so the reported field gives 64 under either sign. With one reference drawn from the stated reader state, the even close disagrees in all eight entries at the closing setting. The reported odd match holds independently. [fixture.py, lines 35–39 and 59](../fixture.py#L35)

2. **Narrowing — state the algebra and the scope of “only.”** The sentence is “So **the even closing rule is entailed only by the assumption that values commute**; drop it and the closing sign is a reordering cost.” The same section says “so c is that drawing's crossing count.” The reordering formula assumes involutions with pairwise swap signs +1 or −1. For example, X and H = (X+Z)/√2 are involutions, but XHXH = XZ is nonscalar. Count interleavings only for anticommuting pairs. Counting every unheld interleaving works under R. The formula gives the **total** sign, hence the closing sign when the older signs are even. Universal commutation suffices for even parity and is the ordinary engine's premise. A weaker rule can also force even, as R does on five reached types. [README, part D](../README.md#L81)

3. **Narrowing — distinguish central products from scalar products.** Prediction 7 reads “under R no knot of the four-knot closure commutes with every value (the reading needs a state), and every knot of the five-knot closure does (each knot a signed identity).” The counts are zero and five. In the full signed bit-flip representation all five central products move the zero basis word, so **none** is scalar there. Each acts as a signed identity after restriction to a common central eigenspace, which the distinction operators preserve. This establishes the claimed existence of a signed-identity reading. [Preregistration, prediction 7](../preregistration.md#L55) · [Direct check](part_check.py)

4. **Not a block — replace the reached example.** “R forces even at 5 reached types, among them types that do admit a signed-identity reading with an odd sign (K3,4, two groups of three and four with every cross pair sharing: R and the stored witness disagree there).” No deletion of a proposed last knot in that example gives an ordinary closing birth. Three of the five reached even types have odd signed-identity readings. One valid example has two groups of three, all cross-group pairs sharing, and every pair within one group also sharing. Three choices of the last knot restore it. [README, part E](../README.md#L118)

5. **Not a block — correct which product fixes which triple.** “On two four-knot closures sharing one knot, R1 holds, yet reading the shared knot's six places part counting allows 32 words and the state that R's signed knots fix allows 16: the product of one side's four knots constrains the shared knot's three places on that side, and part counting sees only single knots.” Multiplying the three unshared knots on one side leaves its same-side triple. Including the six-place shared knot cancels that triple and leaves the opposite triple. Both constraints hold and the word counts stand. [README, part F](../README.md#L144)

6. **Narrowing — R fails as a persistent reading through this birth.** “R can only be read off the finished pattern ("some knot ever holds both"): which values commute is then a fact of the whole presentation, as closing itself is.” R is evaluable on each current pattern using its current holders. The birth changes three old commutation signs. An operator assignment preserving those old relations cannot implement the new parity knot. Recomputing R after the birth changes the algebra and supplies no preserving map. This rules out fixed, persistent R for this ordinary birth. It leaves open other growth laws and rules for updating operators. The assertion also appears in decision item 5 and register entry A295. [README, part G](../README.md#L157) · [Decision](../decision.md#L23)

7. **Narrowing — limit the inference about CHSH and counting.** “**The bound needs a whole of another kind.**” Also, “A CHSH excess between 2 and 2√2 needs a state that is not a count.” The two-reader counterexample rules out a bound below 4 from closed-part counting alone. Matching a stabilised state's counts can require additional product constraints, as the 32-to-16 example shows. R3 tests the feasibility of definite **odd** parity in a specified algebra. The same holder pattern fails R3 with either the CHSH-4 or the CHSH-2 table. The 2√2 bound uses a common state, bounded reader observables and cross-reader compatibility. The study does not establish that these are the only possible restrictions. Even an equal-amplitude stabiliser state (|00⟩ + |11⟩)/√2 gives CHSH 14/5 for Z and X against (4Z+3X)/5 and (4Z−3X)/5. Every probability here is an integer count out of 20 per setting. The measurements go beyond Pauli choices. Thus a numerical excess cannot diagnose the state as “not a count.” [Decision, item 6](../decision.md#L26) · [README, part F](../README.md#L149) · [Exact example](part_check.py) · [Cirel'son (1980)](https://www.ma.huji.ac.il/~ohadfeld/Tsirelson/download/qbell80.pdf)

8. **Not a block — credit the theorem and distinguish the proofs.** “Arkhipov's proof (already cited at README line 77) is this same crossing argument.” His planar implication contracts a drawing and cancels adjacent occurrences. It applies without arbitrary pairs having scalar swap signs. In the study's own proof sketch, “Row (u, v) is exactly the change in the crossing vector when knots u and v swap places in the row” holds for **adjacent** swaps. Linear combinations of swap rows alone do not exhibit a single order. The enlargement argument above supplies both implications and the source. [Recorded advice](../advisor_answer.md#L13) · [Swap claim](../advisor_answer.md#L24) · [Arkhipov, Theorem 22](https://arxiv.org/pdf/1209.3819)

9. **Not a block — update the prior-review status at closure.** “None of the three had been refereed; their referees are running.” The odd signed-identity census already had a “confirmed with fixes” report in commit `4c3404ae0f`, before this study's decision in `fe3780e41d`. This affects the provenance sentence only. [README, prior work](../README.md#L12) · [Prior census referee](../../FOUR-READINGS-20261120-001A/referee-R1/report.md)

## Logged correction and novelty

**Existing correction upheld — Not a block.** The recorded advice said the even rule “is not entailed at operator-positive closures (79 of the 121 reached types), and is entailed at the rest”. The other 42 exclude an odd **signed-identity** reading. All 42 admit an odd total on a common state under a suitable choice of swap signs, and R itself forces odd on two of them. This reconciles the correction with the unchanged ordinary growth law. A126 asks for extension of **every** old assignment. A294 records an interpretation of consistent views. A295 supplies universal commutation for the ordinary parity sum. The finite knot test still asks for a nonempty allowed relation. [Corrections register, “The even closing sign is not entailed at the operator-negative closures either”](../../../docs/CORRECTIONS.md#2026-11-26--the-even-closing-sign-is-not-entailed-at-the-operator-negative-closures-either) · [Assumptions register](../../../docs/ASSUMPTIONS.md)

**No false novelty claim found for the four named sources.** The three-reader contradiction, the signed-identity criterion, stabiliser measurement rules, and the CHSH-4 table with agreeing marginals have their respective antecedents. The study connects ordinary growth to the first example, counts the consequences of R on reached patterns, and exhibits where two ways of counting words differ. Its general R3 criterion also follows from Arkhipov after the enlargement above. [Mermin (1990)](https://www.yorku.ca/koniuk/PHYS5000/mermin90.pdf) · [Arkhipov (2012)](https://arxiv.org/abs/1209.3819) · [Gottesman (1998)](https://arxiv.org/abs/quant-ph/9807006) · [Popescu–Rohrlich (1994)](https://link.springer.com/article/10.1007/BF02058098)

## Reproduction and limits

From the repository root, set `r=research/NO-WHOLE-STATE-20261126-001/referee-R1`. Invoke each listed file with `.venv/bin/python -B "$r/<file>"`. Use a subshell with `ulimit -v 1048576` (2,097,152 KiB for the census). Each checker is single-process. The table gives the timed prefix and full run at the same configuration.

| Check | Timed prefix | Prefix / full wall seconds |
|---|---|---:|
| `fixture_check.py` | `--context-limit 2` | 0.02 / 0.02 |
| `sign_check.py` | `--limit 4` | 0.01 / 0.03 |
| `census_check.py` | `--limit 20` | 0.12 / 0.61 |
| `part_check.py` | `--pilot` | 0.02 / 0.02 |

The largest full run used 35,344 KiB peak RSS. The checks use no study implementation. Stored certificates and holder lists are inputs. Per-type labelled counts were rebuilt from relabellings preserving the holders, and possible closing knots from the published last-birth criterion. The two preregistration checksum entries matched. The checksums verify file identity. Freeze timing was read from the study record.

**Not run:** Part B's 2,400 alternate-law growth runs, regeneration of the prior census from scratch, independent replay of its 58 arbitrary-operator refutations or its separate reader games, and a census beyond seven knots apart from the named eight-knot control. All five items of the referee brief were reached.

## Referee disposition

| Position | Status | Evidence |
|---|---|---|
| Finite study and general R3 criterion | Confirmed with fixes | Exact probabilities, 115 witnesses, 173 types, and the reduction to signed identities |
| Persistent R through ordinary growth | STOP for this fixture | The three pre-birth commutation signs reverse |

**Next step:** STOP at the requested referee report. The evidence supports the editorial fixes above.

| Direction | Payoff | Concreteness | Disposition |
|---|---|---|---|
| Apply the listed qualifications to the study record | 2/3, clarifies which claims generalise | 3/3, exact passages and replacements identified | For the study owner |

**Corrections:** Four narrowings and five other fixes above. The earlier logged correction is upheld.  
**Goals:** No goal change.  
**Assumptions:** A126, A294 and A295 read in their stated roles.  
**Scaffolds:** Fixed reader labels, signed involutions, and the all-even signing of the shared-knot comparison are explicit above.
