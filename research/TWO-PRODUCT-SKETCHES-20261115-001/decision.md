# How much two fixed product XORs can save

2026-11-15. Goals G3 and G16.

The path has $m$ consecutive Boolean products $x_{i-1}x_i$. Each evaluator computes the XOR $Q$ of them all. Their displayed totals are required to disagree. One extra displayed bit per evaluator is the XOR of any fixed subset of its own products. The subsets may differ. Each case takes the affine hull of each evaluator's actual possibilities separately and intersects the two, repeating to a fixed point. Any adaptive XOR of all the original inputs, totals and two extra bits is a legal question. We count terminal cases in a deterministic proof tree. With an equal-total requirement every original input has an honest extension.

## Exact small answers

| Number of products | Minimum terminal cases | Minimum worst-case questions |
| --- | --- | --- |
| 1 or 2 | 2 | 1 |
| 3 or 4 | 4 | 2 |
| 5 or 6 | 6 | 3 |
| 7 or 8 | 8 | 3 |

The minima optimize both masks and the full adaptive tree. One length beyond the table the proved range is eight through twelve cases. On six products a common split after two products takes six cases. Splitting after three requires eight even with the best adaptive questions for those bits. On five products, out of all 1,024 ordered mask pairs, 92 require six leaves, 72 require seven and 860 require eight. Genuinely different masks occur among the six-leaf choices. The exact finite results combine minimax checks with affine embeddings that map each evaluator's genuine points into the corresponding evaluator of the longer instance. [Finite proof](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001A/TWO-PRODUCT-SKETCHES-20261115-001A-P001_small_minimax/proof.md) · [Reproducible checks](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001A/TWO-PRODUCT-SKETCHES-20261115-001A-P001_small_minimax/checks.json)

## Optimal growth

Put $k=\lceil m/2\rceil$, half the rank of the total's polar form. For $k\ge2$, splitting the products after $2\lfloor k/2\rfloor$ gives
$$
 U(k)=2^{\lfloor k/2\rfloor}+2^{\lceil k/2\rceil}.
$$
Both sides reveal their prefix. A question comparing the prefixes tells which block has inconsistent reported totals. Fixing one input in each independent product pair of that block makes its total affine and closes the case. For $k=1$ the original two-case proof suffices.

Let $L^*(m)$ be the minimum after optimizing both fixed masks and the tree. For $k\ge2$, $\lceil 2U(k)/3\rceil\le L^*(m)\le U(k)$. The lower bound holds for every pair, and the shared prefix gives the upper bound. To see the lower bound, put $h=\lfloor k/2\rfloor$. When each sketch and each sketch plus its own total has half-rank at least $h$, the large-rank theorem from C gives at least $2^{h+1}$ cases for $h\ge2$. Otherwise one of those four quadratics becomes affine after at most $h-1$ input restrictions. B's one-sided bound then gives at least $(2/3)2^{k-h+1}$ cases. For even $k=2h$ these two bounds imply $2U(k)/3$. For odd $k=2h+1$ both are at least $2^{h+1}=2U(k)/3$. The cases $k=2,3$ are in the exact table. Therefore the optimum has order $2^{m/4}$ and the balanced-rank construction is within a factor of $3/2$ at every length. [All-mask lower bound](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001B/TWO-PRODUCT-SKETCHES-20261115-001B-P001_uniform_lower/proof.md) · [Large-rank theorem and common masks](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001C/TWO-PRODUCT-SKETCHES-20261115-001C-P001_sketch_strategies/proof.md)

An elementary obstruction explains why arbitrary mixed questions cannot make the growth polynomial. Keep every third product and label each by the two bits saying whether it enters the left and right sums. One label covers at least $\lceil m/12\rceil$ products. Set every input outside their endpoints to zero. These independent products are now the only survivors. Each extra sum on this restriction is either zero or its own evaluator's total. Every visible question restricts to a question of the original public-only problem, which costs at least $2^{\lceil m/12\rceil}$ cases. The sharper theorem also controls how many left-honest assignments fit in a case when the right evaluator can first contribute a new affine equation. [Both arguments](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001B/TWO-PRODUCT-SKETCHES-20261115-001B-P001_uniform_lower/proof.md)

If the observation budget may grow, let $p$ and $q$ count additional fixed XORs on the two sides. Applying the honest-assignment bound to the evaluator with fewer exposed bits gives at least $(2/3)2^{\lceil k/(\min(p,q)+1)\rceil}$ cases. Thus a polynomial case bound requires $\Omega(m/\log m)$ extra bits on **each** side, even if the other reveals every product. Conversely, giving both evaluators matching prefix XORs that delimit blocks of $O(\log m)$ products uses $O(m/\log m)$ extra bits per side and yields polynomially many cases. [Growing observation budget](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001B/TWO-PRODUCT-SKETCHES-20261115-001B-P001_uniform_lower/proof.md)

## The 31-product optimum

With only the two totals the minimum is 65,536. With the same first 16 products on each side the minimum is exactly 512 at worst-case depth nine. Before taking any questions, the prefix and its complement each have eight independent quadratic pairs. The prefix comparison selects which group to check, giving 256 leaves in either branch. An induction over arbitrary mixed questions proves this tree optimal for its masks. A noncontiguous common choice also attains 512. Every common choice, and every choice differing only by complementing the other mask, takes at least 512. [Midpoint and noncontiguous tree replays](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001C/TWO-PRODUCT-SKETCHES-20261115-001C-P001_sketch_strategies/checks.json)

For *all* independent choices the certified interval is **342 to 512**, inclusive. For each mask let its smaller rank be the smaller half-rank of its own product sum and its complementary sum. Below 512 both smaller ranks must belong to seven and eight, and at least one must be seven. Each rank-seven component must split off as an independent quadratic summand of the total, equivalently its complement has half-rank nine. There are 203,060 eligible rank-seven masks including complements and 313,685,130 masks of smaller rank eight. This leaves at most $203060^2+2(203060)(313685130)=127435038359200$ ordered pairs out of $2^{62}$ before any other exclusions. The ratio is below 0.00277 percent. These counts follow from necessary conditions. Whether any remaining pair gives a smaller tree is open. [One-side estimates and mask census](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001B/TWO-PRODUCT-SKETCHES-20261115-001B-P001_uniform_lower/checks.json) · [Simultaneous rank exclusions](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001C/TWO-PRODUCT-SKETCHES-20261115-001C-P001_sketch_strategies/proof.md)

A concrete asymmetric test numbers the edges from one. Reveal edges 1 through 14 on the left and edges 16, 18, 20, 22, 24, 26, 28, 30 on the right. Including each complementary sum, their respective half-ranks are $(7,9)$ and $(8,16)$. Set $x_0,\ldots,x_{13}$ to zero and leave $x_{14}$ free. The last 17 products remain a path of half-rank nine. Only its second, fourth and subsequent even-numbered products enter the single surviving extra bit. The restriction already gives a concrete smaller problem with a 512-case public-only upper bound. More generally a proof that an arbitrary one-sided quadratic observation always costs at least 512 when the total has half-rank nine would settle the 31-product question. For a higher residual rank one may keep nine polar pairs and fix the other inputs. A cheaper proof on a restriction would still need a construction lifting it to 31 products.

This addresses a restricted decision procedure on one explicitly inconsistent family. The existing linear-size quadratic proof of that same contradiction still applies. General SAT running time remains open. [Proof on the original strict clauses](../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/proof.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — two fixed product XORs | **Status:** Successful on growth | The optimal case count is of order $2^{m/4}$. |
| Local direction — exact 31-product optimum | Unresolved | All pairs need at least 342 cases, and common masks need at least 512. |
| Broader exploration — polynomially many affine cases | Threshold proved | Each evaluator needs order $m/\log m$ exposed bits, and matched prefixes suffice. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Obstruction learned | Two local observations cannot make this affine proof polynomial. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One evaluator with a single extra XOR | 2/3 — Substantial | 3/3 — Ready | Restrict to nine independent quadratic pairs → prove 512 or find a smaller one-sided tree | Selected · started |
| 2 | Construct unequal 31-product masks | 1/3 — Incremental | 2/3 — Testable | Lift a small asymmetric tree → verify fewer than 512 leaves on all 31 products | Alternative · deferred |

For #1 a universal one-sided bound of 512 at half-rank nine would settle the 31-product optimum. The 17-product restriction with every even-numbered product in the one remaining sketch gives a first concrete test. For #2 different masks attain the optimum on five products. Moving their saved cases to a rank-16 total would require an explicit tree on the original inputs.

**Basis:** Three scoped proofs with V1 checks. The finite mask minimax uses exhaustive budgets, exact evaluator hulls, contraction certificates and explicit trees. The uniform lower bounds are symbolic and the implementation checks their finite consequences. Prior work on inner-product parity queries was consulted as background. The separate external design advisor's weekly allowance was exhausted.

**Goals:** G3 and G16 gain a lower bound on a specified proof procedure and a threshold for the amount of local product information it needs. The case count concerns that procedure on the opposed evaluators.

**Assumptions:** The fixed masks, separately computed outputs, deterministic affine questions, exact repeated local hull deductions and terminal leaf count are parameters specified by the question and its predecessor. No standing premise or correction changes.

**Corrections:** None. The earlier 512-case construction attains the exact optimum for its midpoint choice.

**Basket:** The preceding epic's first direction was taken. The one-sided restriction provides a first discriminator for the remaining 31-product question.

## Final report as sent

2026-11-15 22:45:52 UTC

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — two fixed product XORs | **Status:** Successful on growth | The optimal case count is of order $2^{m/4}$. |
| Local direction — exact 31-product optimum | Unresolved | All pairs need at least 342 cases, and common masks need at least 512. |
| Broader exploration — polynomially many affine cases | Threshold proved | Each evaluator needs order $m/\log m$ exposed bits, and matched prefixes suffice. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Obstruction learned | Two local observations cannot make this affine proof polynomial. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One evaluator with a single extra XOR | 2/3 — Substantial | 3/3 — Ready | Restrict to nine independent quadratic pairs → prove 512 or find a smaller one-sided tree | Selected · started |
| 2 | Construct unequal 31-product masks | 1/3 — Incremental | 2/3 — Testable | Lift a small asymmetric tree → verify fewer than 512 leaves on all 31 products | Alternative · deferred |

For #1 a universal one-sided bound of 512 at half-rank nine would settle the 31-product optimum. The 17-product restriction with every even-numbered product in the one remaining sketch gives a first concrete test. For #2 different masks attain the optimum on five products. Moving their saved cases to a rank-16 total would require an explicit tree on the original inputs.
