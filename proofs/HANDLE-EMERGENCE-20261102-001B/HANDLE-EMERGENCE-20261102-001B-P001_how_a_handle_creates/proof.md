# How a handle creates

Status: Proved (two elementary lemmas, and a finite classification by exhaustive computation)

Ticket `HANDLE-EMERGENCE-20261102-001B`, 2026-11-02.

## Question

- **From ticket A.** New knots at an opened cut appear only when the removed side is non-planar.
- **The question.** What do the new knots look like, and what makes them new?

## Dependencies

- **`HANDLE-EMERGENCE-20261102-001A`.** `planar_lib.py`.
- **`SPLICE-TREE-20261102-001C`.** `elim_lib.py` and the size lemma.

## Setting

- **The cut.** A knot space glued along one simple 3-edge cut, with ports X (three near points) and a line M removed on the near side.
  S is the solution set.
- **Port sets.** For a set U of near points and an assignment u, T(u) is the set of port patterns that some solution with u shows.
  T(v) is defined the same way for far points.
- **The hub.** M's tie class: removing M ties its three points (HUB-GLUE A).
- **Pinning and separating.** A pattern t is pinned by u when T(u) = {t}. A far point c separates the pair {t, t̄} (t̄ is t
  complemented) when one value of c excludes t and the other excludes t̄.
- **Odd port.** With six port patterns, the excluded pair is an all-equal pair {σ, σ̄}. Each remaining pair {t, t̄} has one port where t
  departs from σ or from σ̄; that port is the pair's odd port.

## Lemma 1 (the cut is a join)

**An assignment (u, v), with u on near points and v on far points, occurs in S iff T(u) ∩ T(v) ≠ ∅.**

*Proof.*
- **Every line lies on one side.** The near lines lie among the near points. The far lines and slot lines lie among the far points and
  the ports.
- **So S is a join.** A near solution and a far solution that agree on the ports combine into a solution.
- **The equivalence.** If t ∈ T(u) ∩ T(v), take solutions showing (u, t) and (v, t), and combine the near part of the first with the
  far part of the second. The converse is immediate. ∎

## Lemma 2 (three-point knots are decided locally)

**A three-point knot T is generated iff it lies in the base, or two generated three-point knots inside T ∪ {y}, both through y,
cover T ∪ {y} for some tie class y.**

*Proof.*
- **The size lemma.** By SPLICE-TREE C, the last elimination producing T uses knots A, B ⊆ T ∪ {y}, both no larger than T. Knots have
  at least three points, so A and B have exactly three.
- **Induction.** The same holds for A and B, so the whole derivation uses only three-point knots. ∎

## Results (finite classification)

The sample is every ordered pair of census knot spaces, with lines 0 and 1 of the first spliced into point 0 of the second: 768
removals on the near side.

1. **Shape.** Every new knot (936) has three points:
   - one in the hub;
   - one near point off the ports;
   - one far point.
2. **Locality, checked.** At all 768 removals, eliminations among three-point knots alone generate the same three-point knots as the
   full closure.
3. **Pin and separate.** Take every new knot {h, a, c}.
   - The hub point h and the near point a pin the ports to one pattern t for one pair of values, and to t̄ when both values flip.
   - Each value of the far point c excludes one of t and t̄.
   - **What this means.** Fixing h and a decides all three ports at once. No knot through a single port carries that across, so by
     Lemma 2 no elimination produces it.
4. **Necessary, not sufficient.**

   | Removals | Count | With new knots |
   | --- | --- | --- |
   | Four-pattern | 512 | 0 |
   | Six-pattern, no pinned pair separated | 56 | 0 |
   | Six-pattern, some pinned pair separated by a far point | 200 | 100 |

5. **How the Fano plane creates.**
   - **The Fano plane.** At all 96 of its six-pattern removals, the removed line meets the closing line in one port (any two lines of
     the Fano plane meet), the hub is tied to that port, and every pinned pair's odd port is that same port. 52 of them create.
   - **Census 58.** It creates this way, and also with the removed line missing the closing line and the hub tied to no port.

## Reading

- **What a new knot is.** A new knot is a three-point constraint through the hub that reaches across the cut: the hub and one near point
  fix all three ports jointly, and one far point answers to that whole pattern.
- **Why the Fano plane fits.** Its lines always meet, so the hub sits on a port. The joint pattern it pins is the one where that port
  stands against the other two.
- **The planar contrast (ticket A).** Planar sides never complete this.
- **Ticket C** asks why.

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Shape of new knots | 936 of 936 three points: hub, near point off the ports, far point |
| 2 | Locality of three-point generation | 768 of 768 removals |
| 3 | Pin and separate | 936 of 936 |
| 4 | Necessary, not sufficient | as tabulated |
| 5 | The Fano plane and census 58 | as stated |

## What this does not establish

- **No rule for creation.** Pin and separate is necessary, but which pinned and separated pairs create is not decided here.
- **Coverage.** The census pairs, two splice lines each.

## Novelty

- **New here.** The classification.
- **Elementary.** The lemmas.
