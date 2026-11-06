# The other value-free four-place laws build equality and are NP-complete

Status: Proved

Ticket `FOUR-PLACE-20261031-001C`, 2026-10-31.

## Statement

**Theorem.** For the not-exactly-two class and the twelve class (ticket A), deciding solvability on simple 4-regular 4-uniform systems
without repeated lines is NP-complete. So recognising their failing systems is coNP-complete, and polynomial only if NP-complete
problems are.

## Dependencies

- **`FOUR-PLACE-20261031-001A`.** The classes, the Schaefer status (neither class is closed under a tractable polymorphism), and the library
  (`four_lib.structures`, `accepted_relations`, `link_form`, `regularize`, `sat`).
- **External.** Schaefer (1978).

## Lemma 1 (link pieces)

**Statement.** Each class has a piece with:
- five internal points, each on four lines;
- four ports, each on one line;
- six distinct lines: (0,1,2,3), (0,1,2,4), (0,1,2,5), (0,1,3,4), (2,3,4,6), (3,4,7,8), with ports 5, 6, 7, 8.

Its accepted port relation is exactly (p₇ = p₈) × {0,1}² on (p₅, p₆). So ports 7 and 8 are forced equal, and ports 5 and 6 are free
and lie on different lines. The relations on the six lines are listed in `result.json`, check 1. They were found by search and recomputed
by brute force.

**Why pinning is not needed.** Value-free laws cannot pin (ticket A, Lemma 2). This piece builds equality without any constant.

## Lemma 2 (regularization)

**Input.** A signed instance: constraints on four distinct variables, each with a relation of the class.

**The construction.**
1. **Copies.** For each variable x with d occurrences, make m = max(d, 2) copies. (For a disequality link, m is rounded up to even and
   the copies alternate.) Each occurrence uses its own copy.
2. **Cycle.** Join the copies in a cycle by m link pieces: piece i has port 7 = copy i and port 8 = copy i + 1.
3. **Spare incidences.** Each copy has 2 link incidences, plus its occurrence if it has one. So copies have 2m − d spare incidences in
   all. The cycle's pieces offer 2m free ports, and 2m − d of them fill those spares, never placing a point twice on one line.
4. **Absorbers.** Over all variables, Σ d = 4 × (number of constraints) free ports remain. They go to absorber points, four each. They
   are taken from distinct lines, which is possible because each line has at most one free port.

**The result.**
- It is a simple 4-regular 4-uniform system without repeated lines, over the same class.
- A solution of the instance extends: copies take the variable's value, each piece's internals extend because its accepted relation
  is a product, and absorbers are free.
- A solution of the system makes all copies of a variable equal through the links, which gives a solution of the instance. ∎

## Proof of the theorem

- **Hardness.** Schaefer: the signed class is NP-complete with unbounded occurrences. Lemma 2 makes it NP-complete on 4-regular
  systems.
- **Membership.** Membership in NP is clear. ∎

## Checks

`check.py` (`result.json`, about 6 min):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; ticket A passed. | pass |
| 1 | The link pieces, found by search over the 10 piece structures without repeated lines and recomputed by brute force over 2⁹ assignments. Degrees, distinct lines, free ports on different lines. | pass |
| 2 | Schaefer status (ticket A, check 3). | pass |
| 3 | Regularization end to end on 160 random instances (both classes; 96 satisfiable and 64 unsatisfiable). Each result is simple, 4-regular, free of repeated lines, over the class, with the same satisfiability (SAT solver on both sides). | 160/160 |
| 4 | Control: a piece accepting everything in place of the link decouples the copies, and satisfiability changes on 21 of 60 instances. | pass |

**Correction inside the ticket.** The first run chose, for not-exactly-two, a piece whose two free ports share a line. On instances with
a single constraint the one absorber then met that line twice (3 of 80 instances; satisfiability was still preserved). The selection now
requires free ports on different lines, which both classes have.

## What this does not establish

- **Counting.** The counts of these laws are not addressed.
- **Locality.** Whether their failures are local is moot, since recognising them is already coNP-complete.

## Novelty

- **Classical ingredients.** Bounded-occurrence hardness through equality gadgets (Tovey; Dalmau–Ford, who use constants).
- **New here.** The constant-free link pieces are explicit and new.
