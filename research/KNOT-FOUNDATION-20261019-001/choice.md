# Whether the base logic has real alternatives

Ticket `KNOT-FOUNDATION-20261019-001C`, 2026-10-19. This decision note answers
the epic's second question. It gives short proofs and machine checks
(`PYTHONPATH=tools python3 -B -m knotlab choice`; tests `ChoiceTest` in
`tests/test_knotlab.py`). The main bound is Theorem 2 of
`KNOT-FOUNDATION-20261019-001E-P001`. Everything here uses the canonical
forgetting reading of the knot test.

## The question, made precise

"Several possible worlds, or only forced outcomes?" has two senses:
1. **Possibility.** Does the base's law allow more than one state? A law is a
   system of constraints, and its possible worlds are its allowed states.
2. **Actuality.** Is one allowed state singled out as the real one?

The mathematics answers the first sense. The second belongs to the
modal-plurality interpretation.

## Answer

- **The base has real alternatives wherever it has knots.**
  - Every variable of a knot takes both values.
  - A knot on m variables allows at least 2^(m−1) of its 2^m joint states, so
    it fixes at most one bit and leaves at least m − 1 bits open.
  - A law with a single allowed state has no open distinction, and so no loop
    and no knot.
- **Knots never select.** No knot forces any of its variables, so selection
  has to come from outside. Selecting one loop's value removes that loop from
  the binding. What remains between the other loop and the contact is a
  two-place relation: logic, not topology.
- **Requirement and choice are one knot read two ways.** Swapping which value
  counts as "exists" turns "A and B require c" into "c requires A or B". The
  34 two-loop knots are closed under such swaps.
  - 16 are a pure requirement under one reading and a pure choice under the
    other, 8 each way. A pure requirement has one least world, whatever is
    given.
  - The other 18, parity among them, offer choices under both readings.

  The forgetting reading favors neither value, so the base has choices
  exactly as much as it has requirements.
- **A single forced world needs an added rule.** The rule "nothing exists
  unless required" selects one world, but only for the 8 knots that are
  requirements under the reading it assumes. It presupposes which value
  counts as existing, which the forgetting reading does not supply. Under the
  other reading the same knots leave several minimal worlds.
- **Search is native.** Every three-literal clause on three open distinctions
  is a knot, so a system of knots can state any 3-SAT instance. Deciding
  whether such a system allows any world is therefore NP-complete (Cook 1971).
  Under the absence reading, knot systems were requirements only: they were
  closed under AND and had one least world, found in linear time.

## The smallest form of choice

The smallest form of choice is an open distinction: one bit that the
constraints leave free. That is exactly what a loop carries. At the base,
"loop", "choice" and "open distinction" name the same thing. A knot is a
pattern that relates choices without making them.

## Proofs

1. **Alternatives.** K2 says forgetting any one variable leaves the rest
   unconstrained. Every single-variable shadow is therefore full, and the
   count of at least 2^(m−1) states is Theorem 2 of
   `KNOT-FOUNDATION-20261019-001E-P001`. A law with one allowed state forces
   every variable, so none of its shadows is full and nothing in it is a knot.
2. **No selection, and selection leaves logic.** Every single-variable
   shadow of a knot is full, so no knot forces a variable. Restrict a
   three-variable knot to A = a and you get a relation on B and c. If both
   values of a left B and c free, the knot would allow all 8 states,
   contradicting K1. So some selected value leaves B and c tied.
3. **Requirement and choice.** Negating variables preserves both "every pair
   free" and "constrained as a whole", so the knots are closed under it.

   A relation has one least world for every choice of given values exactly
   when it is closed under AND. Suppose x and y are allowed but x ∧ y is not.
   Fix the coordinates on which x and y agree. No allowed state then lies
   below both x and y, so the minimal worlds below x differ from those below
   y. Negating every variable exchanges closure under AND with closure under
   OR. The counts 8, 8 and 18 come from enumeration.
4. **Clauses are knots.** A three-literal clause on distinct variables
   excludes exactly one state, so every pair stays free and the clause is a
   knot. 3-SAT with three distinct variables per clause is NP-complete.

## Nearest known results

- Horn clauses and their least models (Horn 1951; van Emden and Kowalski
  1976), and their mirror image, dual-Horn clauses;
- Schaefer's dichotomy (1978);
- the Cook–Levin theorem (1971).

Novelty: `known-overlap-found`. The delta is the reading: knots need
alternatives, knots never select, and requirement versus choice is a matter
of which value counts as existing.

## What follows for branches

A branch settles some distinctions, that is, it restricts the allowed states.
Knots among the distinctions it leaves open survive. A loop whose distinction
is settled drops out of its knots. A fully settled branch, with one state,
contains no knots. In this sense emergence lives across alternatives, and
settling them uses it up.

## Interpretation, not theorem

The modal-plurality doctrine treats every coherent admissible alternative as
co-real, with no global selector. The results fit that doctrine: the base as
formalized has no selector, and knots exist only across alternatives.

They do not prove it. Another reading is equally consistent with every
theorem above: one allowed state is actual, and the knots live in the law
that constrains all the states. What the theorems rule out is a base that is
forced all the way down and still has knots.

## Stop rule

The epic stops when the space question also adds only classical facts. This
ticket's results are classical (Horn and dual-Horn duality, Cook–Levin),
together with the reading above. They confirm the trend: the foundation is a
clean reading of known logic. Ticket D, whether contact structure becomes
space-like, is the last test.
