# Every failing class builds a link

Status: Proved

Ticket `FOUR-PREFER-20261101-001B`, 2026-11-01.

## Statement

**Theorem.** Ten four-place knot classes that prefer a value are NP-complete to decide on 4-regular 4-uniform systems: classes 1, 2, 4,
5, 6, 7, 8, 9, 10 and 12 (numbering of ticket A). So their failing systems are coNP-complete to recognise.

## Dependencies

- **`FOUR-PREFER-20261101-001A`.** The catalogue, the Schaefer status, and `prefer_lib`.
- **`FOUR-PLACE-20261031-001C`.** The twelve class's link piece: five internal points, six lines, accepted relation (p₇ = p₈) × {0,1}²
  with free ports 5 and 6 on different lines.
- **External.** Schaefer (1978).

## Lemma 1 (realization)

**Statement.** Each of classes 2, 4, 5, 6, 7, 8, 9, 10, 12 has a piece on the three-point shape whose accepted relation lies in the twelve
class. The shape has lines {x, y, z, a}, {x, y, z, b}, {x, y, z, c}, {x, y, z, d}: internal points x, y, z each lie on all four lines, and
ports a, b, c, d lie on one line each. The relations are listed in `result.json`, check 2.

**Every member is realized.** Classes are closed under flips and permutations, and a port lies on one line only. So relabelling the ports
and flipping a port's place in its line turns this piece into one accepting any member of the twelve class (`prefer_lib.adapt`).

## Lemma 2 (lifting)

**The construction.** Let P be a piece whose lines carry relations of a class Γ′. Suppose every relation of Γ′ is accepted by a piece of
class Γ. Replace each line of P, a 4-tuple of points with relation S, by a fresh copy of a Γ-piece accepting S, whose four ports are the
line's four points.

**The result.** It is a Γ-piece with the same ports and the same accepted relation. Every point keeps its number of incidences, each line
being replaced by one port incidence per point. Internal points of different copies are distinct, so no line repeats.

**Applied here.** P is the twelve class's link piece. For each of the nine classes this gives a link piece with 23 internal points and 24
lines whose accepted relation is (port a = port b) × {0,1}². Its free ports lie on different lines (check 3, by SAT).

## Lemma 3 (class 1)

Class 1 realizes no link class on the three-point shape. It has a direct link piece with five internal points and six distinct lines
(check 4, recomputed by brute force).

## Lemma 4 (regularization for any link piece)

The construction of FOUR-PLACE C works for a link piece of any size (`prefer_lib.regularize`):
- **Copies.** A variable with d occurrences gets m = max(d, 2) copies (m even for a disequality link), joined in a cycle by m link pieces.
- **Spares.** The pieces' free ports fill the copies' 2m − d spare incidences.
- **Absorbers.** The remaining Σ d = 4 × (number of constraints) free ports go to absorber points, four each, from distinct lines.

**The result.** A simple 4-regular 4-uniform system over the same class, solvable iff the instance is.

## Proof of the theorem

1. None of the ten classes is closed under a Schaefer polymorphism (ticket A), so with unbounded occurrences each is NP-complete.
2. Lemmas 1–4 give each a link piece and a regularization, so it is NP-complete on 4-regular systems. ∎

## Checks

`check.py` (`result.json`, about 40 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; ticket A passed. | pass |
| 1 | The twelve link piece from FOUR-PLACE C, recomputed by brute force. | pass |
| 2 | Realizations on the three-point shape for the nine classes. | pass |
| 3 | Lifted link pieces: 23 internal points, 24 distinct lines, correct degrees, free ports apart; the accepted relation by 16 SAT calls each. | 9/9 |
| 4 | Class 1's direct link (seeded search, brute force). | pass |
| 5 | Regularization end to end: 24 random instances per class, each class with at least three satisfiable and three unsatisfiable ones. Every result is simple, 4-regular, over the class, with the same satisfiability. | 240/240 |
| 6 | Schaefer status of the ten classes. | pass |

## What this does not establish

- **Counting.** Counting complexity is not addressed.
- **The five weak classes.** Classes 13–17 exclude two or three states, and no failing system is known for them (ticket C).

## Novelty

- **Classical techniques.** Gadget composition (lifting) and bounded-occurrence regularization.
- **New here.** The explicit pieces, and the observation that a three-point core realizes the twelve class from nine different classes.
