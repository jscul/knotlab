# Advisor answer: TRANSFER-TABLES-20261126-001, before the freeze

Nothing was run; everything below is from reading the code or worked by hand, and is `unverified` unless marked "read in the code".

Three things to settle before freezing:

- **The readers are joined.** "Readers whom no listed law joins" fails once knots are taken in the whole of the reached states. Each old distinction and another child's fresh pair carry a three-place relation, and every one of the 30 splits is joined by one.
- **Expectation 2 is wrong on the number.** With any reads the named split gives 1 + √2 ≈ 2.4142 from the start, not "maybe not". With the model's reads it gives exactly 2.
- **The model's-reads test never runs.** As coded it is skipped on this founder and prints 0.

## Read in the code (fix before the freeze)

- **`chsh_pauli` is skipped on every split.** `tables.py` line 160 runs it only when `na + nb <= 6`. The founder has 9 distinctions and one or two unread, so the readers hold 8 or 7. Line 180 then prints 0 through `.get(..., 0)`. Compute the expectations from the 13 nonzero amplitudes directly (4,095 × 15 strings at most).
- **No signalling is computed.** The docstring of `chsh_values` promises a check; the function returns only `best` (lines 73–87).
- **`exact_two` and `any_pair` are one arm here.** Each child has two fresh distinctions (`growth.py` 160–166: floor 2, demand 2), `permits_pair` is true for both modes, and `combinations(fresh, 2)` has one member (`transfer.py` 29–30, 38–39). The study has two lift arms, not three.
- **The positive control's value reads print 0.0.** Each reader has one distinction, so `combinations(subsA, 2)` is empty (lines 83–84, 211).
- **The failing control can be silent or empty.** If no sampled start passes the filters, the loop at lines 186–207 prints nothing. If the chosen start has no split, `default=None` prints a row of Nones.
- **Cost of the failing control.** At 12 distinctions the seesaw does about 2,400 eigen-decompositions of a matrix of up to 1,024 rows per split. Time one split first, and run everything under the memory cap.

## 1. Value reads: entailed, with one thing to add

- **CHSH ≤ 2 and no signalling are entailed** for any weighting; the run can only catch a bug.
- **Sharper prediction: exactly 2.0000** as the largest value over splits, in every mode and counting. At C = {2}, parity{0,1} and parity{1,3,4} are the same function (law 034 makes parity{0,3,4} constant), both equal to x2 = parity{7,8}. Parity{7} has correlation 0 with them, so the sum is 1 + 0 + 1 − 0.
- **Six splits return 0.0 by convention.** These are C = {i, a fresh distinction of child i}, where one reader holds a single distinction.
- **"Signals" has a second meaning to report.** If a setting is a value of the reader's own old distinctions (the keyed setting, A226), then at x2 = 0 the pair {7,8} reads 00 against 11 with certainty. That is what the law was built to do (A114, A115), through the parent that holds 0, 1 and 2.

## 2. The coherent version, by hand

From the start, with ψ₊ = (|10⟩ + |01⟩)/√2 and places ordered (012)(34)(56)(78):

ψ = ½ [ |000⟩|00⟩|00⟩|00⟩ + |110⟩ψ₊ψ₊|11⟩ + |101⟩ψ₊|11⟩ψ₊ + |011⟩|11⟩ψ₊ψ₊ ]

With 2 unread, A = {0,1,3,4,5,6}, B = {7,8}:

- **Your structure is right.** Half the weight is (e0 ⊗ 00 + e1 ⊗ 11)/√2, with e0 all quiet and e1 = |11⟩ψ₊ψ₊. The other half is a product, f ⊗ ψ₊.
- **Your visibility bound does not apply.** Distinction 2 is not hidden: A holds x2 as parity{0,1} and B holds it as parity{7,8}. Each reader can choose its reads separately in the two halves, giving 2√2 on one and 2 on the other.
- **Any reads: exactly 1 + √2.** Convexity gives the same number as an upper bound.
- **The model's reads: exactly 2.** e0 and e1 differ in the value of distinction 0, so a Pauli product either keeps that value (nothing between e0 and e1) or flips it (nothing on the diagonal). The largest element between them is ½, for example X0X1X3X5. I went through all 15 products on {7,8} against every product on A; the largest sum is 2, attained by Z0Z1 with Z7Z8.
- **Spot values to check the code against:** E(Z0, Z7) = ½, E(X0X1X3X5, X7X8) = ½, E(Z0Z1, Z7Z8) = 1.

The twelve splits C = {i, a fresh distinction of another child} are entangled too. For C = {0,5}, the part with x0 = 0 and x5 = 0 has weight 3/8 and is √(2/3)|00⟩b0 + √(1/3)|11⟩b1. Any reads give (5 + √17)/4 ≈ 2.2808; the model's reads give 2 (worked from the start only).

## 3. Minimum lift: entailed

- The minimum weighting is a product of one factor per listed law (`transfer_check.json`: 13 states from local supports, 13 reached).
- Fixing the unread values then gives a product across any split, under either counting and any reads.
- Prediction: 0 of 30 entangled, any reads 2.0. No run can fail it.

## 4. The other knot rule

- **The pair transfer is parity-only.** `transfer.py` 25–26 and `growth.py` 68–73 admit even overlap only. "Even input" and "occupied" need a quiet reference, and the all-quiet word is forbidden under not-all-equal.
- **Do not write "none in the record" without naming A210.** `WRITTEN-BIT-AND-JOIN-VETO-20261122-001` has a not-all-equal value-reading growth (`verify.py` 205–206: `nae_lexicographic`, `nae_opposite`).
- **A210 is not a transfer in your sense.** Its fill reads only the newborn's own paid inputs and their reference (`verify.py` 87–101), so at a fixed history it should factor like the minimum lift. Its veto reads every distinction of the proposed parents (104–107) and gives different histories for different values.
- Report as: no not-all-equal pair transfer exists; A210 is the nearest law and was not run.

## 5. Is the coherent version fair, and which control

It is fair as a bound on what the non-factoring could give if coherence and rotated reads were supplied. It is not evidence that the model makes a table above 2:

- **The weights are declared.** `RING-TO-END` `definitions.md` line 20 says there is no weighting on all growths, and referee R2 says the law does not prescribe the probabilities. Only the 13-state support is the law's. Any weighting positive on it gives an excess with any reads, and the size (anything up to 2√2) belongs to the weighting.
- **"Entangled" restates R2's table.** With positive amplitudes, a split is a product given the unread values exactly when the readers are conditionally independent given them. Test that directly in fractions: it should fail on the same 15 splits.
- **The excess is the reads'.** It needs sums of a value read and a change read, and a read exchanging e0 with e1. The model's reads give 2.
- **"From the finish" needs a definition.** The record's finish counting is every allowed word of the structure once, which is 32 words here and ignores the transfer law. Yours is the 13 reached states once.

Controls:

- **Passing arm:** the ordinary 32 words on the same four laws. Prediction: 0 of 30 entangled, 2.0 everywhere.
- **Positive control for the model's reads:** the current one (a Bell pair) gives only 2 with Pauli reads, so nothing shows that test can exceed. Three words 00, 01, 10 equally weighted give 7/3 with X and Z (correlations 2/3, 2/3, 2/3, −1/3), and 2√13/3 ≈ 2.4037 with any reads.
- **The factoring study's one-stage division:** I expect it to return 0 entangled splits by construction. Its weight is a function of the start word. With one or two unread, the splits should isolate only the fresh distinctions of last-round births, so the whole start lies inside one reader. Pick the start by an exact failing minor across a split, or report that the control does not exercise the test.

## 6. Predictions to freeze

Pair lift (one arm under two names), 13 reached states, 30 splits:

| Quantity | From the start | From the finish (13 states once) |
| --- | --- | --- |
| Value reads, largest | 2.0000 | 2.0000 |
| Entangled splits | 15 of 30 | 15 of 30 |
| Negativity, 3 splits C = {k} | 1/4 | 2/13 ≈ 0.1538 |
| Negativity, 12 splits | √2/8 ≈ 0.1768 | √2/13 ≈ 0.1088 |
| Any reads, 3 splits C = {k} | 1 + √2 ≈ 2.4142 | (16 + 2√41)/13 ≈ 2.2159 |
| Any reads, 12 splits | (5 + √17)/4 ≈ 2.2808 | (20 + 2√17)/13 ≈ 2.1728 |
| Model's reads, largest | 2.0000 | 2.0000 |

- The other 15 splits (two old distinctions unread, or an old one with its own child's fresh) are separable, at most 2.
- "Model's reads = 2" is the one prediction at risk: it is not entailed, since the state is not a counting state of a parity structure, and I worked only two kinds of split.
- Minimum lift and the 32-word arm: 0 entangled, 2.0.
- Positive control as coded: value reads 0.0, negativity 0.5, any reads 2.8284, model's reads 2.0.

## What a referee will press first

1. **Knots in the whole** (referee R2's own Block 1).
   - In the 13 reached states the patterns on {0,7,8} are all but 011 and 100. This is not-all-equal with the old place reversed.
   - The same relation sits on {1,7,8}, {1,3,4}, {2,3,4}, {0,5,6} and {2,5,6}.
   - Every two-place part is free, so each passes K1–K3 by forgetting (`knots.py` 69–89).
   - The 13 states are exactly the words of the four listed laws and three of these relations, one per child.
   - The start weighting factors over those seven.
   - All 30 splits are joined by one of the relations.
   - Check: run the canonical `knotlab check` on the reached support for these scopes.
2. **The model's reads never ran**, and the excess with any reads belongs to supplied reads.
3. **Declared weights**, and the name "from the finish".
4. **Checks that cannot fail** presented as tests: value reads, the minimum lift, the failing control.
5. **Scope:** one founder, one round, two arms. A second round changes the structure by values (the veto on active joins), which pools histories.

## Hivemind

I added one consultation entry and one standing fact (the lift's three-place relation, parity-only, A210) to `docs/ADVISOR_HIVEMIND.md`, both marked `unverified`. I touched nothing else. Nothing here bears on the publication hold.
