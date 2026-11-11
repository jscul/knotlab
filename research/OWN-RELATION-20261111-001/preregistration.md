# Pre-registration: does a knot space read its own relation?

Epic `OWN-RELATION-20261111-001` (direction #1 of `HOLD-COUNT-20261111-001`, G8 with G15), written on 2026-11-11 before the census runs,
at the coordinator's go-ahead under the owner's standing mandate. Code frozen with this file in
`proofs/OWN-RELATION-20261111-001A/OWN-RELATION-20261111-001A-P001_four_point_maps_on_larger_spaces/` (`own_lib.py`, `check.py`,
`own_referee.py`). Before the freeze the reader was timed on two spaces with seeds outside the frozen range, results discarded unread
(16 points, genus 3: 8 seconds; 18 points, genus 3: 21 seconds), its class check (R1 of the referee) was run, and both counters were
compared on one space of `HOLD-COUNT-20261111-001`'s census (10 points, genus 2, seed 1: the same 20 A and 3 B as recorded there).

## The question

A decided total map of four held points in a knot space with the not-all-equal law is self-dual (theorem D of `IN-OUT-20261110-001`).
The self-dual maps that use all four held points form exactly four classes under permuting and negating inputs and negating the
output (by exhaustion of the 256 self-dual maps, checked again by the referee's fresh code):

- **A**, the weighted majority [2a + b + c + d ≥ 3];
- **B**, maj(a, b, a ⊕ c ⊕ d);
- **C**, the switch: the parity of a, b and c when d agrees with a, their majority otherwise;
- **D**, a ⊕ NAE(b, c, d): the knot's own relation read against a fourth point.

Only C and D, with one input held fixed, give a bit that a count mod 3 needs. `HOLD-COUNT-20261111-001` found, on 1,128 spaces, 6,783
outputs of kind A and 74 of kind B, none of C or D, and none of any kind using four held points on a lattice torus: they occur only on
random spaces of genus 2 or more, and B grows with size (3 at 10 points, 8 at 12, 63 at 14). Does C or D occur on larger spaces?

## Is the answer forced? (reasoning, before any compute)

- **Not by self-duality.** All four classes are self-dual, so theorem D forbids none of them.
- **Not by the law alone.** Not-all-equal with negations and hidden points defines every relation closed under flipping every point
  (write the relation as a CNF, add one hidden point t to every clause as a not-all-equal constraint, split long not-all-equal
  constraints with hidden points; Schaefer 1978). The graph of D is such a relation, so general signed not-all-equal systems realise C
  and D.
- **So an obstruction, if there is one, comes from the knot-space structure**: every point on three lines and every line on three
  points, a two-coloured triangulation of an orientable surface, the Kasteleyn law. A first structural handle, to be tried in the proof
  attempt: modulo the global flip, a floor state is a choice of one odd side on each line: a point of an affine space over F2 in
  which each line carries a vector of odd weight, with the points where some line carries 111 removed (flats of codimension at most 2),
  and every held difference and output is an affine function of it.

## The census (frozen; exact)

- **Spaces.** `UNATE-20261111-001`'s random knot spaces steered to a genus as in `PARITY-NEEDS-20261111-001` (`needs_lib.steered`):
  n = 16, 18 and 20 points, genus 2, 3 and 4, seeds 0 to 99 for each (n, genus); unreached, disconnected or not simple spaces counted
  and skipped. Every class; all floor states by brute force.
- **Readings.** Every set of four held points whose 16 patterns all occur; every decided output point; its kind (A, B, C, D, or the
  number of held points it uses).
- **Caps, set now.** Each space 1,200 seconds; the census part 3 hours of wall-clock time, enforced by its systemd unit, with a memory
  cap of 16 GB. Expected: well over ten minutes, so it is registered as a long-running row.
- **Positive control, run first.** Synthetic floor states realising each of A, B, C and D over four held points, with three free extra
  points: the reader must report each class at its output and no other of the four. If it fails, nothing is read.
- **Referee (fresh code, `own_referee.py`).** R1: the four classes, and that only C and D can give a mod-3 bit, recomputed by closing
  under generators. R2: on every tenth space read (by label) and on every space with a C or D instance, the counts of A, B, C and D
  recomputed from the lines and signs alone must equal the census's.

## Predictions and failure criteria

- **P1.** Neither C nor D occurs anywhere in the range. Predicted: none, weakly.
- **P2.** B keeps growing with size: more B outputs per space at genus 3 at 18 points than at 16, and at 20 than at 18. Predicted: yes.
- **An instance of C or D counts only after the referee confirms its space.** If one is confirmed, the answer is yes: a knot space reads
  its own relation (D) or the switch (C), and the least such space is reported. P1 then fails.
- **The census is inconclusive** if more than 10% of the reached spaces are dropped by their caps; it is then reported as such.
- **The proof attempt** counts only as a proof valid for every knot space with the not-all-equal law, at any size, that no decided
  total map of four held points is of kind C or D; otherwise it is reported as not found, with what was learned.
- **Answer by rule.** P1 and P2 as found, the totals by size and genus, any instance with its least space, and the proof attempt's
  outcome. Stop there; report and hold.

Assumptions in force: A47, A58; A65 is not used (no reference is held). Nothing here bears on P versus NP.
