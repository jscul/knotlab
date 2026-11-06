# The value-free four-place knots

Status: Proved

Ticket `FOUR-PLACE-20261031-001A`, 2026-10-31.

## Question

- **At three places.** The knot (not-all-equal) is the only knot with no preferred value (PINNING A), and that is why it cannot pin and
  why its failures stay recognisable.
- **The question here.** At four places, which knots have no preferred value, and what do they do on 4-regular 4-uniform systems?
- **The guards.** This ticket applies the two guards of `PARITY-CORRECTION-20261031-001`. No family is called easy from a one-sided
  transform; here only decisions and counts of solutions are used.

## Dependencies

- **`PINNING-20261031-001`.** The three-place picture: five classes, only not-all-equal value-free, and the pinning theorem.
- **`PARITY-CORRECTION-20261031-001`.** The guards: parity's failures are local, and its weighted family is hard.
- **The cubic census of `MUTUAL-SELECTION-20261031-001C`.** All 13 connected cubic bipartite graphs on 7 + 7 vertices, used to enumerate
  the systems with n = 7.
- **External.** Schaefer (1978).

## Definitions

- **Value-free.** A four-place relation R ⊆ {0,1}⁴ is value-free if complementing all four places preserves it. Equivalently, R is a
  union of antipodal pairs {v, v̄}.
- **Knot.** R is a knot (K1–K3) if it is neither empty nor full and every three-place projection is full.
- **Signed law.** A signed law is the orbit of R under flips and permutations of the places.
- **System.** A 4-regular 4-uniform system has lines that are 4-tuples of distinct points, with every point on exactly four lines.

## Lemma 1 (the catalogue)

**Statement.** There are exactly 30 value-free four-place knots. Under flips and permutations they form four classes:

| Class | States | Relations | Symmetric member |
| --- | --- | --- | --- |
| parity | 8 | 2 | even and odd parity |
| not-exactly-two | 10 | 8 | weights {0, 1, 3, 4} |
| twelve | 12 | 12 | none |
| not-all-equal | 14 | 8 | weights {1, 2, 3} |

**Proof.** Enumerate the 254 non-trivial unions of the eight antipodal pairs, keep the knots, and group them under the 384 flips and
permutations. A brute-force pass over all 2¹⁶ relations confirms the count 30 (check 1). ∎

**What the classes are.** Every class has relations excluding both constants:
- odd parity;
- odd parity plus one balanced pair (not-exactly-two class);
- odd parity plus two balanced pairs (twelve class);
- not-all-equal.

## Lemma 2 (no pinning)

**Statement.** If every line carries a complement-invariant relation, the solution set of every system and the accepted relation of every
piece are complement-invariant. So no piece forces a port to a value.

**Proof.** Complementing a solution gives a solution. ∎

**The difference from three places.** At three places this made the knot the unique law that cannot pin. At four places all 30 relations
share the property, so "no preferred value" no longer singles out one law. Check 2 confirms it on every piece with three or four
internal points.

## Lemma 3 (Schaefer)

**Statement.** Only the parity class is closed under a tractable polymorphism (minority, so affine). The not-exactly-two, twelve and
not-all-equal classes are closed under none of the six.

**Consequence.** With unbounded occurrences, deciding them is NP-complete (Schaefer). The signed classes are not 0-valid, 1-valid,
Horn, dual Horn, bijunctive or affine (check 3).

## Lemma 4 (plain systems)

**Statement.** On plain systems a law can fail only if it excludes both constant colourings. Eight relations do (check 4).

## Census

**The systems.** The 4-regular 4-uniform systems with n ≤ 7 are the complements in K_{n,n} of the (n − 4)-regular bipartite graphs:
- n = 4: one system;
- n = 5: one system;
- n = 6: four systems, from the even cycle covers C12, C8 + C4, C6 + C6, C4 + C4 + C4;
- n = 7: fourteen systems, from the 13 connected cubic bipartite graphs plus K3,3 ∪ Q3.

They are pairwise non-isomorphic (check 5).

**Signings.** Over every signing (one member relation per line), check 6 finds:
- **not-all-equal never fails:** 0 of 8ⁿ signings on every system;
- **parity and not-exactly-two** fail on every system;
- **twelve** fails on every system with n ≤ 6, and on 11 of the 14 with n = 7. On the other three, all 12⁷ signings are solvable.

## What this does not establish

- **Not-all-equal never fails for every n.** That is ticket B (via Thomassen).
- **Whether the failing classes' failures can be recognised.** That is ticket C.
- **Counting complexity.** Not addressed.
- **Four-place laws that prefer a value.** Not classified here.

## Novelty

The four-class census is elementary. No source was found.

## Files

- `four_lib.py`: relations, classes, Schaefer polymorphisms, the systems, failure counts, pieces, regularization (used by C), and
  sign-nonsingular signings (used by B).
- `check.py`, `result.json`: the checks (about 70 s).
