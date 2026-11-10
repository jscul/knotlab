# Pre-registration: other atoms, a challenge of A48

Epic `OTHER-ATOMS-20261110-001` (backlog B97, G15 with G16), written on 2026-11-10 before any run, at the coordinator's go-ahead. It is
the challenge of assumption A48 (a grown handle is a Fano atom with the uniform law).

## The question

Every learning result since `GROW-HANDLE-20261110-001` grows the Fano atom. Is the learned memory a property of the Fano plane, or of any
torus atom that stands for a line?

## The atoms, named before any run

An **atom** is a torus knot space less one point, spliced at a knot sphere's line by a compatible splice (one of three bijections and two
chiralities, those that lower the Euler characteristic by 2), as in `GROW-HANDLE-20261110-001`. The candidates are the simple lattice
tori `torus(p, q, r)` of `COUNT-SURFACES-20261107-001A`, grouped up to isomorphism of maps and mirror images by an exact canonical form
(computed before this freeze; the grouping reads no law and no state). Lattice tori are point-transitive, so one point per torus is
enough. The frozen list has 29 types, named by their first parameters:

- **Class-forced** (one of the four sign classes is satisfied by no state), 8 types: the **Fano torus** (7,2,1), the control, with its
  mirror (7,4,1); and the **thin tori of even index** (2,1,2) with 4 points, (3,2,2) with 6, (4,3,2) with 8, (5,4,2) with 10, (6,5,2)
  with 12, (7,6,2) with 14 and (8,7,2) with 16.
- **Every class satisfiable**, 21 types, every one up to 12 points, as controls: the thin tori of odd index (3,1,1), (5,1,1), (7,1,1),
  (9,1,1), (11,1,1); and the others (2,0,2), (2,0,3), (2,0,4), (2,1,4), (4,1,2), (3,0,3), (3,1,3), (2,0,5), (5,1,2), (11,2,1),
  (2,0,6), (2,1,6), (3,0,4), (3,1,4), (4,2,3), (6,2,2).

Outside the test, named so that nothing is claimed for them: tori that are not lattice quotients (faces with other than three line
corners), atoms of genus 2 or more, non-orientable atoms, and atoms brought with a law that has even faces.

## What "acts like the Fano atom" means

Three tiers, each measured as stated; an atom acts like the Fano atom when it passes all three.

- **T1, acts as its line in one class (ticket A, exhaustive on every gadget type).** On every line orbit of K_2, K_3 and K_4, every
  compatible splice: the atom's sides take a Kasteleyn law of its torus, the old signs are kept, and the three new sides are signed so that
  no face is even (that such a signing exists is checked too). The atom's four classes are reached by flat changes inside the atom, which
  keep every sphere side and every new side (lemma A of `ATOM-RULE-20261110-001A`). In each class the check reads the patterns the atom
  allows on its three outer points (one SAT call per pattern) and the local system of `ATOM-RULE-20261110-001A` (every line with a corner at
  a region face satisfied, at most one agreeing corner at each region face; the region is every face at an atom triangle). **Pass:** on
  every splice, exactly one class allows exactly the six patterns the replaced line allowed and has an unsatisfiable local system, and the
  other three allow all eight. The check also confirms that the orbits of K_2 to K_4 cover the four line neighbourhood types of that
  record's lemma C. Lemmas A to C there do not use the Fano plane; the proof re-checks that, and T1 then gives that record's theorem 1 (the
  role, R-a and R-b) for the atom on every octahedral knot sphere with separated atoms.
- **T2, holds a unit (ticket B, exact on small cases, SAT over every state).** For each atom passing T1 with at most 8 points: on K_3,
  every line orbit l0, two atoms (at l0 and at the first line at distance 3) in all 16 classes, and three atoms (at l0 and at distances 2
  and 3) in all 64. **Pass:** in every class, R-a (if every atom acts, no state satisfies every line) and R-b (in every state satisfying
  every line, each acting atom has a face with three agreeing corners in its region). Atoms at distance 2 may have overlapping gadgets;
  they are included.
- **T3, write and return (ticket C, computed).** For each atom passing T1 and T2 with at most 8 points, and for the Fano atom through the
  same code: `ADDRESS-SEQ-20261110-001A`'s procedure unchanged except for the atom (K_3, every line orbit, three atoms at l0 and distances
  2 and 3, the six two-atom addresses in turn, after each write a one-point disturbance and the learner M1), with random.Random(97).
  **Pass:** every write written and at least 95% held, that record's expectation. **Failure:** a write not reached, or fewer than 80% held.

**Code control.** The Fano atom through the new code must reproduce `ATOM-RULE-20261110-001A`'s check 1 on K_2 to K_4, splice by
splice (the multiset of role, own-pattern match and local satisfiability over the four classes). If it does not, the code is fixed before
any other atom is read, and the fix is recorded.

## Predictions, frozen

- **P1.** Every class-forced atom passes T1, and its acting class is the image of its torus's unsatisfiable class.
- **P2.** No atom whose torus has every class satisfiable acts as its line in any class; each is transparent in all four on every splice.
  Growing one would then remove a sphere's dissonance by growth alone, holding no memory.
- **P3.** Every atom passing T1 passes T2.
- **P4.** Every atom tested in ticket C passes T3.

## What the outcome does to A48

- **At least one atom other than the Fano atom passes T1 to T3:** the memory does not need the Fano plane. A48 is overturned as a limit
  (as A26 was), and a new entry records the premise the results use: a grown handle is an atom that acts like the Fano atom, with the
  atoms proved to.
- **No other atom passes T1:** A48 is confirmed for a stated reason: among lattice-torus atoms the memory needs the Fano plane.
- **Others pass T1 but fail T2 or T3:** A48 returns to Assumed, with what failed recorded.

Either way, what is proved for the Fano atom stands. If P2 fails, what the acting all-satisfiable atom does is recorded as found.

## Runs

Each ticket's check is expected to take under ten minutes. A check expected to take longer is registered in `docs/LONG_RUNNING.md`
before it is launched. Assumptions in force: A20, A21, A46, A47, A49, A50; A48 under challenge.

## Addendum, 2026-11-10, after ticket A ran and before ticket D runs

Ticket A ran at 04:35 UTC (34 seconds): P1 and P2 held on all 29 types, and every atom's role was the same on all 60 splices. Reading the
result, a by-hand reduction was found (it goes in ticket A's proof): an atom's allowed patterns depend only on its torus and the class read
from its sides. The constant pair of patterns is excluded exactly when the torus is unsatisfiable in that class, and the six other patterns
are allowed exactly when the torus is **free** at its point in that class: for each of the point's three sides e, the law with e's sign
flipped (two adjacent even faces) has a satisfying state. So the role needs only twelve satisfiability facts about the torus itself, and no
host. **Ticket D** (computed, exhaustive per torus), frozen here before it runs:

- **Scope.** Every simple lattice torus with at most 30 points, and every thin torus of even index with at most 40 points, grouped up to
  isomorphism as in ticket A; one point per torus (they are point-transitive).
- **Measured.** For each of the four classes: whether a state satisfies the law, and, for each of the point's three sides, whether the law
  with that side's sign flipped has a satisfying state (SAT).
- **Predictions.** D1: every torus is free at its point in every class. D2: the class-forced types are exactly the Fano tori and the thin
  tori of even index, each with exactly one unsatisfiable class. D3: on the 29 types of ticket A, the role read from these facts equals the
  role ticket A found on every splice.
- **Failure.** A torus not free in some class (its atom would then allow a relation other than the line's or all eight there), or a
  class-forced type with two unsatisfiable classes.
