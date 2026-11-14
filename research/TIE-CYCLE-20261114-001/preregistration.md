# Is identity the whole story of forgetting: pre-registration

Epic `TIE-CYCLE-20261114-001` (`FORGET-RULE-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. Frozen in
two stages: the split now, before the tie status of any family is computed; the rule and the held-out predictions after exploring
the training half. The thread's work, reusing FREE-TARGET's per-call relations. The canonical K1–K3 test is unchanged.

## The question

`FORGET-RULE-20261114-001` proved that a port handed to itself around a cycle of calls prevents forgetting (rule N). In the census,
having no such cycle means forgetting in every chain and in 94% of the other families, and the exceptions carry a value through
knots that force equality. Generalise identity to a tie: at the end of a call word, a port equal or opposite to a start port in
every allowed state. Is "no tie cycle" exactly forgetting?

## In standard terms

For a finite semigroup of complement-closed relations on {0,1}³ × {0,1}³, whether some element has a coordinate equality or
inequality from a start bit to the same end bit (a self-tie). The question is whether the absence of self-ties characterises
eventual rectangularity.

## Prior work in the program

`python3 -B scripts/track.py objects "forced tie along a call word equal or opposite port" --until 2026-11-14 --exclude TIE-CYCLE-20261114-001`
`python3 -B scripts/track.py objects "affine dependence between top and depth ports parity" --until 2026-11-14 --exclude TIE-CYCLE-20261114-001`
`python3 -B scripts/track.py objects "identity cycle prevents forgetting" --until 2026-11-14 --exclude TIE-CYCLE-20261114-001`

- `FORGET-RULE-20261114-001`: rule N (identity cycles) and rule A, the starting point; this study generalises N.
- `TRUE-RATE-20261113-001`: carried top ports, the identity mechanism, a relative.
- `REACH-CENSUS-20261113-001`, `BOND-DEPTH-20261112-001`: the census and the ray bonds, relatives.
- `FAR-BOUND-20261112-001`, `NEST-COUNT-20261112-001`, `BOARD-DIST-20261110-001`: unrelated (other bases and objects).

## Stage 1: the split (frozen now)

A family is **training** when `int(sha256("TIE:" + key).hexdigest()[:8], 16)` is even, otherwise **held out**. This is a fresh salt,
so the halves differ from FORGET-RULE's. The census's forgetting verdicts have been seen in aggregate counts. No family's tie status
has been computed. One- and several-definition families are reported apart.

## Proved before stage 1 (stated, not tested)

- **On single bits a complement-closed relation is full, an equality or an inequality.** Any pairwise dependence a word forces
  between two port bits is therefore a tie.
- **Ties compose.** A tie from port j to port k along u, followed by one from k to l along v, is a tie from j to l along uv, with the
  signs multiplied.
- **A tie cycle prevents forgetting.** Suppose some word w gives a self-tie, port j to port j. Then every power of w carries it. The
  projection on (start j, end j) is an equality or an inequality containing both values, which is never a product. So no power of
  w is rectangular. Rule N is the equality case.

## Stage 2 (to be frozen after exploring the training half)

The rule's exact test (the finite semigroup's elements, checked for a self-tie), any variant found on the training half, the
advisor's view, and the held-out predictions.

## Stage 2: the rules, frozen before the held-out half is read (2026-11-14)

The equivalence is stated on **forgetting itself** (rectangularity of long products). Reading forgetting as growth of the free bond
is scoped, as both referees require: it holds for depth-s targets in copies of S reached through S calls
(`CENSUS-FORGET-20261114-001`, FREE-TARGET's referee), with one level fewer for wrapper mains. The advisor model reviewed the plan
cold (`advisor_review_answer.md`); its points are adopted.

**Theorem I (the reduction, proved).** A family forgets exactly when every idempotent E (E·E = E) of its product semigroup is
rectangular. Proof:
- Rectangular relations, with the empty one, form an ideal, since X·(A × B)·Z is rectangular.
- If a non-rectangular idempotent E = R_w exists, then every power of w has product E. So no length r makes all products
  rectangular.
- Conversely, in a finite semigroup every sufficiently long product has a factor whose product is idempotent. If every idempotent is
  rectangular, every long product has a rectangular factor and is rectangular.
- Every call word is allowed, so pumping is free.

**Classification (the advisor's).** For a non-rectangular idempotent E, the core {x : xEx} carries the preorder x ≤ y iff (x, y) ∈ E,
and E is non-rectangular exactly when the core has at least two classes. If the classes are pairwise incomparable, E conserves a
label from start to end: a **tie** when the label is one bit, a **parity** when it is linear, otherwise **non-linear**. If two
classes are comparable, E is a one-way **order** with no conserved quantity.

**Training results (seen).**
- Theorem I's check held: every non-forgetting family has a non-rectangular idempotent, and no forgetting family has one (3,708 of
  3,708 non-chains).
- A tie cycle never occurs with forgetting.
- Among families without a tie cycle, forgetting holds in all 2,126 chains and in 780 of 835 non-chains (93.4%).
- Of the 3,382 non-forgetting families, 3,322 have an identity cycle, 5 a tie forced through knots, and 55 no tie at all. Of those 55,
  52 have only order-type idempotents.
- No parity cycle occurs without a tie.
- 26 families the census left capped have a tie cycle, which settles them as non-forgetting.

## Predictions on the held-out half (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| H1 | **A tie cycle prevents forgetting.** No held-out family with a tie cycle is certified (a proof check). Also reported with identity cycles excluded (ties forced through knots). | any |
| H2 | **No tie cycle almost means forgetting.** Among held-out families without a tie cycle, every chain forgets (0 violations; a census fact, not a theorem), and the forgetting share among non-chains lies between 91.5% and 95.5%. So "no tie cycle ⟺ forgetting" is refuted in non-chains whenever one exception occurs. | a chain violation, or the share outside the band |
| H3 | **Theorem I's check.** Every held-out family forgets exactly when its semigroup has no non-rectangular idempotent. | any |
| H4 | **The residual is order, not identity.** Among held-out non-chains that do not forget and have no tie cycle, at least 80% have only order-type non-rectangular idempotents. | below 80% |
| — | Reported: parities without a tie (a count, since the generator may not produce them); capped families settled by a tie cycle; one- and several-definition families apart. | — |
