# Pre-registration: what it takes to hold a count

Epic `HOLD-COUNT-20261111-001` (backlog B152, G8 with G15), written on 2026-11-11 before the census runs, at the coordinator's go-ahead
under the owner's standing mandate. Code frozen with this file in
`proofs/HOLD-COUNT-20261111-001A/HOLD-COUNT-20261111-001A-P001_the_mirror_lemma_and_the_census/` (`hold_lib.py`, `check.py`,
`hold_referee.py`). Before the freeze the census code was timed on two spaces with its results discarded unread (a steered space of 14
points and genus 3 outside the frozen seeds, 3.5 seconds; one 20-point torus, 2.3 seconds), so the whole run is expected to take a
few minutes and is not registered as long-running.

## Where it comes from

The owner asked on 2026-11-11 whether solving a pseudo-polynomial problem is "statistical", some choices leading to the solution faster
than others, and whether knapsack, whose choices are logical, could be "an emergent representation of what's happening at the logical
emergence scale". The answer given in the thread: knapsack's table is fast because every partial choice is summarised by one running
total, and many choices merge into it; a total is a magnitude, and the knot's own law, not-all-equal, is the only three-place knot with
no preferred value (`PINNING-20261031-001`, `MUTUAL-SELECTION-20261031-001`). This epic asks what a knot space with that law can do
with a count, with and without one fixed value supplied by the world.

## The mirror lemma (proof by hand, to be refereed before it is published as proved)

**Setting.** A knot space whose floor states (every line satisfied) are closed under flipping every point. Every space here is one: each
line is not-all-equal on its signed literals, so flipping every point flips every literal and keeps every line satisfied (theorem D of
`IN-OUT-20261110-001`). The world holds n points; outputs are read at the floor (A58). A reading is **total** when every pattern of the
held points occurs among the floor states, and an output point is **decided** when it has one value in every floor state with the same
pattern. A set of decided output points **holds the count mod m** when, for some choice of literals ℓ_i = x_i ⊕ ε_i, its value at every
pattern is e(Σℓ_i mod m) for a map e from residues to values that takes different values on different residues.

**Lemma.** Let n ≥ m − 1, so that every residue mod m is the count of some pattern. If a total reading of decided points is a function
e of the count mod m, then m is even and n is odd, and e sends the residues of c and n − c to complementary values. In particular no
reading holds the count of three held points mod 3 (P0 below), and the readings that hold their count mod 4 are exactly the full
adders: one point reading their parity and another a majority of their literals, each up to negation.

**Proof.** By theorem D the floor states with held pattern p and output values v correspond one to one with those with pattern ¬p and
values ¬v, so a decided total reading F satisfies F(¬p) = ¬F(p). Flipping every held point turns the literal count c into n − c, so
e((n − c) mod m) = ¬e(c mod m) for every count c from 0 to n. If m is odd, 2 is invertible mod m and c* = n · 2⁻¹ mod m satisfies
n − c* ≡ c*; since n ≥ m − 1 some count c in 0..n is congruent to c*, and then e(c*) = ¬e(c*), which is impossible. If m and n are
both even, the count c = n/2 gives the same contradiction. For n = 3 and m = 4 the condition reads e(3) = ¬e(0) and e(2) = ¬e(1);
a single output bit b with b(3 − c) = ¬b(c) is fixed by b(0) and b(1), and the four choices give majority, parity, negated parity and
negated majority of the literal count; distinguishing four residues needs one parity bit and one majority bit. ∎

**With a reference.** If one more point r is held at 0 (A65), the reading uses only the floor states with r = 0, whose mirrors all have
r = 1. The lemma then constrains nothing: holding r at 1 instead gives the same readings with every held literal negated.

**Provenance.** The case m = 2 is already in the program: parity of an even number of held points is not self-dual (backlog B149).
The general statement is a short consequence of self-duality and is classical in substance: Post's self-dual functions, and spin
systems without fields, whose ground states come in mirror pairs, so that ground-state spin logic uses local fields or ancilla spins as
references (Whitfield, Faccin and Biamonte, Europhysics Letters 99, 57004, 2012). What is new here, if anything, is the census below.

**Referee (fresh code, `hold_referee.py`, run before closure).** R1: the lemma's combinatorial core checked exhaustively for n = 1..8,
m = 2..6 and codes of one to three points. R2: every class of every census space has floor states closed under flipping every point,
the lemma's only hypothesis. R3: every least instance the census reports is recomputed from the space's lines alone. It is independent
code by the same author, not an independent reviewer.

## The census (frozen; exact)

- **Spaces.** `PARITY-NEEDS-20261111-001`'s: every simple, non-degenerate triangular-lattice torus with up to 20 points (281), and the
  random knot spaces of n = 8, 10, 12, 14 points steered to genus 1, 2 and 3, seeds 0 to 99 for each (n, genus), with the same rules
  (unreached, disconnected or not simple: counted and skipped). Every class; all floor states enumerated by brute force.
- **Readings.** Every triple T of held points, and every triple with every reference point r held at 0. Kinds: parity of T at one point;
  a majority of T's literals at one point; a full adder (both on the same T); a pair holding the count mod 3; a pair holding it mod 4;
  each without a reference and with one.
- **Caps, set now.** Each space 300 seconds; each part 30 minutes of wall-clock time. A space or a part over its cap is dropped by rule
  and reported.
- **Least space** for a kind: fewest points, then lowest genus, then fewest faces, then label.

## Predictions and failure criteria

- **P0 (the lemma, n = 3, m = 3).** No pair holds the count of three held points mod 3 without a reference, on any class of any space.
  A counterexample means a bug or a wrong lemma: stop, find which, and log it.
- **P1.** Some space holds a full adder without a reference. Predicted: yes.
- **P2.** Some space holds the count of three held points mod 3 with one reference point. Predicted: yes.
- **P3.** The least space for P2 has more than 8 points (the least parity torus, (2, 0, 4), has 8). Predicted: yes, weakly.
- **A no on P1 or P2 is a finding**, not a failure: holding that count in one space of this range needs composition (backlog B148).
- **The census fails as a measure of what a count costs** if the least spaces for parity without a reference, for the full adder and
  for the count mod 3 with a reference are one and the same space.
- **Controls; a failure is a bug, to be fixed and logged before any result is read.** C1: on every space read by both epics, the numbers
  of total parity and total majority interfaces equal `PARITY-NEEDS-20261111-001`'s. C2: on every space, the triples holding the count
  mod 4 without a reference are exactly the full adders (the lemma).
- **Answer by rule.** P0 to P3 as found, the least space for each kind with its first instance, and the number of spaces holding each.
  Stop there; report and hold.

Assumptions in force: A47, A58, A65 (added for this epic). Nothing here bears on P versus NP.
