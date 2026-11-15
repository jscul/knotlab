# One evaluator can reveal the even products and the 17-product minimum stays at 512

2026-11-15. Goals G3 and G16.

The path has inputs $x_0,\ldots,x_{17}$ and products $p_i=x_{i-1}x_i$ numbered from one. Put $Q=\bigoplus_{i=1}^{17}p_i$. Both evaluators compute $Q$ and their displayed totals must disagree. Only one side exposes $B=p_2\oplus p_4\oplus\cdots\oplus p_{16}$. After imposing the contrary totals, its relation is $s=Q(x),v=B(x)$. The other relation is $s=1+Q(x)$ with $v$ free. Each branch takes all affine consequences of either full evaluator in its current affine cell, intersects them and repeats to a fixed point. Each paid question can mix $x,s,v$ arbitrarily by XOR. We count terminal cases and worst-case questions in a deterministic tree.

## The 17-product answer

**The minimum is 512 terminal cases and nine worst-case questions.** Fixing all nine even-indexed inputs makes every product affine in what remains, so a tree of depth nine closes on all 512 leaves. The lower bound allows every adaptive mixed XOR query. It has two proofs, one using the even-edge sketch's actual ranks and a second applying to any one-sided quadratic observation. [Direct proof](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001A/ONE-SIDED-PATH-SKETCH-20261115-001A-P001_even_path/proof.md) · [All 262,144 literal assignments checked](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001A/ONE-SIDED-PATH-SKETCH-20261115-001A-P001_even_path/checks.json)

A shorter successful branch explains why a bound on every individual branch would have been wrong. Set $x_4,x_6,\ldots,x_{16}$ to zero. Only $x_0x_1+x_1x_2+x_2x_3$ survives in the total, and the sketch equals $x_1x_2$. If it equals one, $x_1=x_2=1$ and both evaluators' totals have to equal $x_0+1+x_3$. That branch closes at depth eight. After arbitrary answers to the seven questions, an affine correction gives the same residual product test. One optimal unbalanced tree has 128 leaves at depth eight, 128 at depth nine and 256 at depth ten. On the smaller seven-product path, asking for the sketch first has exact child costs nine on zero and seven on one. [Short and long branches](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001A/ONE-SIDED-PATH-SKETCH-20261115-001A-P001_even_path/checks.json) · [Seven-product trees](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001C/ONE-SIDED-PATH-SKETCH-20261115-001C-P001_affine_controls/trees.json)

## Why an arbitrary one-sided quadratic still costs the full amount

For a Boolean quadratic $Q$, write $r$ for half the rank of the alternating bilinear form $Q(x+y)+Q(x)+Q(y)+Q(0)$. In linear coordinates the quadratic part of $Q$ is a sum of $r$ independent pair products. For **every** Boolean quadratic $B$ on the input bits, giving one evaluator the additional observation $B(x)$ leaves the exact minimum at $2^r$ cases and $r$ worst-case queries. This permits arbitrary affine terms, mismatched product groupings, extra radical coordinates, and different legal XOR questions in different branches. An XOR of original private product coordinates is a special case. [General proof](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001B/ONE-SIDED-PATH-SKETCH-20261115-001B-P001_one_sided_rank/proof.md) · [Replayable checker](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001B/ONE-SIDED-PATH-SKETCH-20261115-001B-P001_one_sided_rank/check.py)

To see how the proof accounts for both answers, consider a first question that contains the extra bit. On the observing side its value is $F(x)=B(x)+\alpha Q(x)+\ell(x)$ for some affine $\ell$. After fixing it, only the usual shared inputs and the total remain free. Its two possible answers partition the observing evaluator's inputs. If $Q+F$ retains half-rank $r$, each answer that covers a fraction $\theta$ of the inputs costs at least $2^r\theta$ leaves. The two fractions sum to one. If $Q+F$ loses rank on a nonsingular $2r$-variable section of $Q$, its polar radical supplies a direction on which $Q$ and $F$ have the same polar derivative. One source coordinate can then encode the smaller sketch in each child, embedding an instance with $r-1$ pairs in each. Pure input splits and questions of the public total admit their own two-child restrictions or a full-rank graph argument. Fixing one member of every pair attains the upper bound. [All first questions](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001B/ONE-SIDED-PATH-SKETCH-20261115-001B-P001_one_sided_rank/proof.md)

The density estimate is itself a theorem about the current inference rule. Put $t=\min(\rho(Q),\rho(Q+F))$ with $\rho$ denoting polar half-rank. For the promise $F=0$ of density $\theta$, an unpinned total costs at least $2^t\theta$. With a pinned total the needed estimate is $2^{t-1}\theta$ for $t\ge3$. High rank ensures each needed truth value occurs on every relevant affine hyperplane. The small cases reduce to two, four or six input bits by taking a simultaneous nonsingular restriction of the two polar forms and a translate that retains at least the original promise density. The finite checker enumerates all relevant polar and affine cases including both signs. A four-variable counterexample shows why extending the pinned estimate to $t=2$ would fail. [Conditional bounds and scope](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001B/ONE-SIDED-PATH-SKETCH-20261115-001B-P001_one_sided_rank/proof.md) · [Finite basis checker](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001B/ONE-SIDED-PATH-SKETCH-20261115-001B-P001_one_sided_rank/conditional_bases.py)

## What this settles on 31 products

The optimal choice of one fixed product XOR on **each** evaluator has exactly **512 cases**. If all four partial sums (each mask and its complement) have half-rank at least eight, the preceding large-rank theorem already gives this lower bound. Otherwise a partial sum of half-rank at most seven becomes affine on an input subspace of codimension at most seven. On that subspace the corresponding extra bit is an affine function of the inputs and possibly that evaluator's own total. This leaves a one-sided problem. The original total's half-rank was 16, so its restriction retains at least nine, even when the other sketch acquires a new quadratic form. The one-sided theorem gives at least $2^9$ leaves. A common prefix of 16 products attains 512. Some individual mask pairs cost more, including 65,536 for the two empty masks. The specific asymmetric 31-product pair that motivated the 17-product test inherits a lower bound of 512. Its own optimum would require its own matching upper bound. [Transfer and input restrictions](../../proofs/ONE-SIDED-PATH-SKETCH-20261115-001C/ONE-SIDED-PATH-SKETCH-20261115-001C-P001_affine_controls/proof.md) · [Midpoint construction and large-rank theorem](../../proofs/TWO-PRODUCT-SKETCHES-20261115-001C/TWO-PRODUCT-SKETCHES-20261115-001C-P001_sketch_strategies/proof.md)

These results concern deterministic tree refutations using the separate affine hulls. The existing direct quadratic proof of the same contradictory totals is linear in the path length. [Proof on the original strict clauses](../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/proof.md)

## A first check for a further observation

One quadratic observation at one evaluator is now settled. For a future two-observation test, the four-input control from B allows two arbitrary Boolean labels to cover the inputs in three terminal cases. In the original three-product path dictionary there are only eight product masks. Testing all 64 ordered pairs on the same evaluator found no three-leaf refutation. A public tree with four leaves still works. This is a direction screen on three products. It distinguishes the permitted quadratic masks from the arbitrary labels and leaves two quadratic observations at higher ranks as a separate question.

To replay this screen, run the following using the B family's `conditional_bases.py` on the Python import path. It enumerates the raw coordinates $(x_0,x_1,x_2,x_3,s,u,v)$ and uses the same exact hull search as the conditional bases.

```python
from conditional_bases import AffineSearch, parity

search = AffineSearch(7)
for first in range(8):
    for second in range(8):
        left = right = 0
        for x in range(16):
            products = x & (x >> 1) & 7
            total = parity(products)
            flags = parity(products & first) + 2 * parity(products & second)
            left |= 1 << (x | (total << 4) | (flags << 5))
            for free in range(4):
                right |= 1 << (x | ((total ^ 1) << 4) | (free << 5))
        assert not search.fits(left, right, 3)
```

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — one-sided even-products XOR on 17 products | **Status:** Successful | Exactly 512 terminal cases and nine worst-case questions. |
| Local direction — any one-sided quadratic observation | Settled | The minimum is exactly $2^r$ for total half-rank $r$. |
| Broader exploration — two masks on 31 products | Optimum settled | Every pair costs at least 512 and the common midpoint attains it. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Obstruction learned | A single evaluator's extra quadratic cannot reduce the tree's leaf count. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two quadratic observations on the same evaluator | 2/3 — Substantial | 3/3 — Ready | Check the three- and five-product cases → exhibit a strict saving or classify the five-product masks | Selected · started |
| 2 | A hand proof of the small conditional bounds | 1/3 — Incremental | 2/3 — Testable | Analyze the six-input pinned case → replace its finite search with a short lemma | Alternative · deferred |

For #1, all 64 ordered mask pairs on the three-product path still take four leaves. The five-product case can show whether two genuine local product XORs can save work where one cannot. For #2, the four-input failure of a stronger pinned claim identifies the distinction a shorter proof must preserve.

**Basis:** Three locally proved results with V1 validation. Direct path evaluation, exact finite mixed-query minimax, conditional-density induction, affine embeddings and an independent same-task audit cover the stated proof system. The optional external design advisor could not authenticate. External parity-tree papers supplied background.

**Goals:** G3 and G16 gain an exact obstruction for one-sided quadratic observations and a tight 31-product optimum after both local masks are chosen.

**Assumptions:** The evaluator partition, individual fixed quadratic observation, deterministic tree, all affine questions and repeated whole-evaluator affine hulls are explicit parameters. No standing assumption changed.

**Corrections:** None to a prior accepted result. The stronger pinned-density claim at half-rank two fails on four inputs. The proof and checker preserve that witness and use the pinned bound only from half-rank three.

**Basket:** The previous study's first direction was taken. Its cheaper-17-to-31 construction was conditional on a smaller 17-product tree. The exact one-sided lower bound settles the 31-product optimum by restriction.

## Final report as sent

2026-11-15 23:40:57 UTC

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — one-sided even-products XOR on 17 products | **Status:** Successful | Exactly 512 terminal cases and nine worst-case questions. |
| Local direction — any one-sided quadratic observation | Settled | The minimum is exactly $2^r$ for total half-rank $r$. |
| Broader exploration — two masks on 31 products | Optimum settled | Every pair costs at least 512 and the common midpoint attains it. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Obstruction learned | A single evaluator's extra quadratic cannot reduce the tree's leaf count. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two quadratic observations on the same evaluator | 2/3 — Substantial | 3/3 — Ready | Check the three- and five-product cases → exhibit a strict saving or classify the five-product masks | Selected · started |
| 2 | A hand proof of the small conditional bounds | 1/3 — Incremental | 2/3 — Testable | Analyze the six-input pinned case → replace its finite search with a short lemma | Alternative · deferred |

For #1, all 64 ordered mask pairs on the three-product path still take four leaves. The five-product case can show whether two genuine local product XORs can save work where one cannot. For #2, the four-input failure of a stronger pinned claim identifies the distinction a shorter proof must preserve.
