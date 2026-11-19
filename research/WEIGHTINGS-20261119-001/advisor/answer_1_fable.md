**Short answer:** none of the three is a clean contrast. Each moves several things at once, and two of them fix the exponential share by a parameter you chose. I worked only from your text, taking the bare-tree ray rule as stated. I could not evaluate S3 or S6′ from it.

## 1. Are the contrasts honest?

- **tree** is tilted against "two" in the limit and towards it at your sizes.
  - No stall, no surplus and no cycle means every leaf beside a degree-2 knot is a ray.
  - The expected number of such leaves is exactly (n−1)(1−2/n)^(n−3), which tends to n/e² ≈ 0.135n. The dimension therefore grows linearly, about n/15 per parity class.
  - At n ≤ 20 the mean is only 1.4 to 3.2 such leaves, so two still wins. Here "two is typical" would be a size effect.
  - Prüfer trees also have knots above 5 places (roughly 7% of samples at n = 20), which is outside SCALE-SHARE's 3–5 range. Report them separately or cap them.
- **tree+** has its exponential share set by the Poisson parameter. With probability e⁻¹ ≈ 37% it is the tree weighting. Otherwise it has a cycle with pendants, which your theorem calls exponential.
  - "Mostly long" is wrong at these sizes. Distances in a random tree scale like √n, so many extra lines close cycles of three or four.
  - A cycle of four gives two knots with two common neighbours, so S4 ejects it. S4 will therefore remove a large, dimension-correlated part of this weighting.
- **grow** is dominated by cycles. The chance of no cycle is (2/3)^(n−1): 20% at n = 5, 6% at 8, 1% at 12, 0.05% at 20. It also has surplus (1–4 open places per new knot), so dead ends are common. It tests cycles and stalls, and hardly tests tree cores.

Two weightings are missing:

- **Bare tree with surplus.** Give each knot one extra open place with probability p, for p = 0, 0.25, 0.5, 1. This is the one-knob path from tree towards SCALE-SHARE, and the cleanest test of whether "two" belongs to surplus.
- **Configuration model.** Fix sizes 3–5, pair places uniformly, and condition on connected. This is the natural check that SCALE-SHARE's result is not an artefact of counting labelled descriptions. I expect it to behave like SCALE-SHARE, but I am unsure.

## 2. Predictions

My reading of the rule: each parity class is a piece with dimension equal to its ray count, or 2 by relay if it has none, and the growth takes the larger. Please confirm that before freezing.

**Share in the proved class**

| Weighting | Prediction | Confidence |
|---|---|---|
| tree | S0 and S4 hold automatically; the share is whatever S3 and S6′ leave. I guess high. | Low: I cannot compute S3 or S6′ from the text |
| tree+ | Tree share on the 37% with no extra line; clearly lower otherwise, since S4 ejects cycles of four | Medium |
| grow | Low and falling with n (stalls, S4, dead ends) | Medium |

**Dimension shares**

- **tree, three or more** (as a share of all trees):
  - n = 5, 6: exactly 0. Three rays in one class need 7 knots.
  - n = 7: exactly 840/16,807 = 5.0%. The only case is the three-armed tree with arms of two.
  - n = 8: exactly 6,720/262,144 = 2.6%. The share falls from 7 to 8 because the extra knot usually breaks the parity match.
  - Larger n, low confidence: about 5% at 10, 8% at 12, 15–20% at 16, 25–30% at 20, crossing 10% somewhere in n = 12–16. A Poisson estimate gives 14, 18, 27 and 38%, but it overshoots fourfold at n = 8.
- **tree, exponential:** 0.
- **tree+, exponential:** above 10% of in-class growers from n = 5, roughly 30–50%, set by how many cycles of four S4 removes. The no-extra-line stratum should match tree within noise. A bare single cycle (dimension 1) is negligible past n = 5.
- **grow:** among in-class growers, exponential dominates from n ≈ 8. Among the rest, two dominates as in SCALE-SHARE, and three or more stays under 2%.

## 3. What to freeze, and the main trap

Risky predictions worth freezing:

1. Tree at n = 7 and n = 8: about 100 ± 20 and 51 ± 14 of 2,000 with three, none at n = 5 or 6, and the dip from 7 to 8.
2. The mean ray-leaf count (n−1)(1−2/n)^(n−3) per size. This checks the sampler independently of the classifier.
3. Tree+ split by number of extra lines: zero lines equals tree, and the exponential share is a function of that number alone.
4. Grow: cycle-free share (2/3)^(n−1), with three or more under 2%.

**Main trap:** "share among in-class growers" is conditioned on S3, S4 and S6′, and these eject samples in a way correlated with dimension. Report shares of all samples next to shares of in-class samples, with the ejection reason.

Two smaller traps:

- **"Two" has two sources.** Relay and a core with two rays both read as two. Tabulate them separately, or tree will seem to confirm SCALE-SHARE for a different reason.
- **Thirty random regrowths will miss the rare cases.** At n = 8 they contain fewer than one predicted three. Stratify by predicted class and include every predicted three-or-more and exponential sample.