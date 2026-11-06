# Knot test: read erasure as forgetting

Status: adopted on 2026-10-19 by the repository owner
Raised: 2026-10-19
Commitment: Canonical knot test (docs/FOUNDATIONAL_THESIS.md, "Canonical knot test")
Decision: Read erasure in K1–K3 as forgetting: a knot is a relation over the loops' open distinctions and a contact that is constrained as a whole and unconstrained in every part.
Implementation: KNOT-FOUNDATION-20261019-001E (tickets/KNOT-FOUNDATION-20261019-001E.json)

## Why

The knot test adopted earlier the same day read erasure as absence: each loop
had a presence variable, and erasing a loop set it to absent. That reading
came from the 2026-10-19 formalization. It was not part of the original
gate. `docs/INTUITION.md`, in the workspace's first commit, introduced erasure
as a test against the common hub:

> Erasing `B` leaves the `A-k` relation meaningful, so there was never one
> irreducibly joint touch between the recurrences.

That is a test of disconnection: remove a loop and see whether anything is
left between the other loop and the contact. The owner confirmed that reading
("what happened to the larger structure when you broke/disconnected a loop").
They also described a loop as a logical structure that can get entwined with
another, not a spatial thing.

The program began from a post about the odd and even parity patterns, in
which one variable decides whether two others match. Under absence, those
patterns are not knots. Under forgetting, they are the knots that hide the
most.

## What changes

- **K1–K3** keep their names:
  - K1, binding: the relation is constrained as a whole.
  - K2, loss on erasure: forgetting any one variable, a loop or the contact,
    leaves the rest unconstrained.
  - K3, coexistence: some state is allowed.
- **Two-loop knots.** There are 34 relations in five shapes, from the atom
  `¬A ∨ ¬B ∨ c` to parity. Under absence only the atom qualified.
- **Doctrine.** A parity relation among open distinctions is a knot when it
  passes K1–K3. An XOR over values fixed elsewhere is still a classifier, and
  an XOR value is still never a magnitude or metric.
- **Ticket B** (where a loop's presence comes from) is retired: presence is no
  longer a variable.

## What does not change

- No 2-CNF with witnesses defines a knot, under either reading.
- Width three with witnesses defines every knot.
- The cross-wired guard diagnosis of Proof 0009 stands.
- The earlier kernel's relation `(A ↔ B) ∧ (A → c)` fails.
- No knot binds infinitely many loops (compactness).
- Every knot of the absence reading remains a knot.

## Evidence

- `proofs/KNOT-FOUNDATION-20261019-001E/KNOT-FOUNDATION-20261019-001E-P001_forgetting_reading/`:
  Lean 4.32.2 kernel and independent checker for the census, the 2-CNF
  obstruction, the width facts, the parity chain and the relation between the
  readings.
- `proofs/KNOT-FOUNDATION-20261019-001A/KNOT-FOUNDATION-20261019-001A-P001_relational_knot_boundary/`:
  the absence reading, unchanged.
- `PYTHONPATH=tools python3 -B -m knotlab demo` shows both readings for every
  reference case.

## Documents changed

- `docs/FOUNDATIONAL_THESIS.md`, `docs/FOUNDATIONS.md`, `docs/COMMON_VERBIAGE.md`,
  `AGENTS.md` and `docs/KNOT_INTUITION.md`;
- the guard, foundations, vocabulary, arity, proof-runner and textbook
  skills;
- `tools/knotlab`, whose default reading is now forgetting;
- the foundations program page and the foundation triage note.
