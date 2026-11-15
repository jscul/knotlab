**What I checked:** the logic of each step from your description only, taking a bond to be a smallest constrained set with every proper subset free. I did not open the census code or data, so the nesting claim below is yours to verify.

## (1) Persistence: right, with three conditions
- **Why size 2 is special:** adding knots only shrinks the allowed states, so a constrained set stays constrained. A larger bond can stop being smallest when a subset becomes constrained (this is how L moves both ways in N), but a tie's only subsets are singletons, which stay free.
- **Nesting:** the depth-N pattern must literally be a sub-pattern of depth N+1. Check that no placement rule depends on N, such as last-level treatment.
- **Life:** "while the pattern lives" needs a satisfiability proof at every depth, per family. It is not a by-product.
- **Scope:** you get L(s)=2 for all N ≥ the certified depth, not "all depths".

Composition is right, but only through a shared member. A tie u3–u4 and a tie u4'–u5 with u4 ≠ u4' give nothing. So compute tie classes (union-find over forced pairs): L(s)=2 exactly when one class meets level 3 and level 3+s. That is one polynomial computation replacing the per-s searches for L=2; sample states to propose pairs, then confirm each with two SAT calls.

For the certificate, a homomorphism is enough. If a level-shifting map σ sends every knot of the core to a knot, with the three images distinct, then every allowed state pulls back along σ. A tie a–b in the core then gives a tie σ(a)–σ(b). With σ(a)=b the chain follows by induction. σ need not be injective.

Names in the literature: equivalent literals (SAT preprocessing), frozen or rigid pairs (the pair version of the backbone; the plain backbone is empty under complement symmetry), parallel elements or 2-circuits (matroids).

## (2) Sound only with a control
Top level 2 reads a different quantity, with three sources of bias:
- **Fewer starts:** level 2 has fewer members, which pushes L up.
- **Transient automaton:** at length 2 the automaton may not have reached its recurrent states.
- **Thinner buffer:** s=6 leaves one level below the target, less than any original reading, and L is sensitive to that.

Fixes:
- Run top 2 at s=1..4 as well and compare with the top-3 profiles. Use s=5,6 only where they agree up to the expected shift.
- For bounded and finitary descriptions, keep top 3 and raise N to 11 instead, if it is affordable.
- Ask threshold questions rather than exact L. "Is there a bond of size ≤ 3?" is a polynomial number of SAT calls over pairs and triples, and it is all P2's first half needs. Only the 45 half-rate ones need "≤ 4?". Report timeouts as intervals. This should cut the 8 hours substantially.

Constant 3 through s=6 excludes half-rate only. A third-rate or logarithmic profile looks the same, so say "direct as far as read".

## (3) Cut or pilot
Tripling the budget on an exponential search usually buys little. Before spending the time:
- Look at the solve times of the decided instances. If few finished between 100 and 300 s, few will finish between 300 and 900 s.
- Run tie classes and the ≤3 threshold on the 88 first. That may decide many of them cheaply.
- Then pilot 10 descriptions at 900 s and continue only if at least 3 decide.

The 2-hour cap never binds: 4 × 900 s is 1 hour. The worst case is 88 hours over 6 workers, about 15 hours.

## (4) Add two features
- Whether one tie class spans all the levels read.
- Whether a level-shifting homomorphism exists. I expect this to be the actual common cause.

## Predictions
- **P1:** not settled by construction, since ties at s=1 and s=2 can sit in different classes. Fix the k range (3..8) and require a linked chain, meaning one class.
- **P2:** word the second half as "L ≥ 5 at s=6 from top 2". The phase may shift with the top level, so [3,4,4,5,5,6] is possible. Condition on the control agreeing.
- **P3:** optimistic. I would freeze "at least a fifth", or freeze it after the timing check.

## Settled by construction (do not count as findings)
- L=2 at N=9 gives L=2 at every larger N, given nesting and life.
- L ≥ 2 always.
- Any s reached by a single spanning tie class.
