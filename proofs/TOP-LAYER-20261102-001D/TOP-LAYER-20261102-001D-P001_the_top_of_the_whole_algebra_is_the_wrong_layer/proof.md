# The top of the whole algebra is the wrong layer

Status: Proved

Ticket `TOP-LAYER-20261102-001D`, 2026-11-02.

## Question

- **The question.** Does every law that composes like cycles keep the top layer of its selected spaces rigid? "Top" means the image
  under the algebra's unique maximal congruence.
- **Answered in part.**
  - Tickets A and C: rigid whenever every abelian section is simple.
  - Ticket B: group laws keep their top rigid.
- **What remains.** Laws whose top is not a single layer.

## Dependencies

- **`TOP-LAYER-20261102-001C`.** Knots are abelian, systems with declared domains are linear over the sections, and simple sections
  force rigidity.
- **`TOP-LAYER-20261102-001B`.** The group theorem, corrected here.
- **`RIGID-SELECTION-20261101-001`.**
  - B: the two signed Z4 systems.
  - D: the top-layer theorem over finite chain rings.
  - A: `zlocal.py`.
- **`MUTUAL-SELECTION-20261031-001C`.** The census, for the Fano plane.

## Theorem

1. **A counterexample.** The Mal'tsev operation on {0, 1, 2, 3, e} given in `check.py` has these properties.
   - It extends x − y + z on Z4.
   - Its subalgebras are the five points, {0, 2}, {1, 3}, Z4 and the whole set, and each has a unique maximal congruence.
   - The whole algebra is simple.
   - **So** its law composes like cycles (KNOT-CIRCUITS Theorem 1), and its top is the whole algebra.
2. **The top-layer statement fails.**
   - **The systems.** RIGID-SELECTION B's two signed Z4 systems are systems of this law, with every point's domain Z4.
   - **What they do.** They fail globally and keep knots after removals: after every one of the 6 removals on 6 points, and after one
     of the 9 on 9 points.
   - **The top image.** The top is the whole algebra, so the top image is the solution set itself and keeps those knots.
   - **Conclusion.** "Every law that composes like cycles keeps its top layer rigid" is false.
3. **The layer that stays rigid: the top of each point's own section.**
   - **The hypothesis.** A system with declared domains fails globally, and the abelian sections of its failing part are cyclic modules
     over one finite chain ring R.
   - **The conclusion.** After any removal, the leading digits of the variables, each read in its own section, form at most one line.
   - **Consequences.**
     - Every kept knot has at most one variable whose leading digit varies.
     - The top of the whole algebra is rigid whenever it factors through these digits, as for groups and chain rings.
4. **Two chain rings joined only through their tops.** Take Z4 and F2[s]/(s²). In the checked systems no global failure keeps a knot
   among the leading digits. This is not proved.
5. **What sets the knot apart.**
   - **Laws that compose like cycles.** They keep emergence inside a selected space only through an abelian section with two layers,
     which needs at least four values (ticket C). When their sections come from one chain ring, they keep it only below that
     section's top (item 3).
   - **The knot.** It keeps three-place emergence on two values, in its only layer: on the Fano plane, after every removal.
6. **Correction to ticket B.**
   - **What holds.** Its theorem holds for systems with declared domains.
   - **What is not covered.** Lines that give a point their own smaller range are not covered by its proof, although every such case
     met was rigid.

## Proof

**Item 1.** Checked exhaustively: the operation, its 9 subalgebras, their congruence lattices, and the simplicity of the whole. Then
apply KNOT-CIRCUITS Theorem 1.

**Item 2.**
- **They are systems of this law.** Z4 is a subalgebra, so the relations of RIGID-SELECTION B's systems, which lie inside Z4^k, are
  subuniverses of A5^k. Check 2 confirms the closure.
- **Same solutions.** Their solutions over five values are those over Z4. Brute force over 5^6 and 5^9 confirms global failure and
  the kept knots.
- **The top.** The algebra is simple, so its unique maximal congruence is equality and the top map is the identity.

**Item 3.**
- **The linear system.** By ticket C, item 2, the system is pulled back from one linear system over its sections M_v = D_v/δ_v.
  Removing a line deletes one equation.
- **Lifting to R.**
  - **The setting.** In the failing part every M_v is a cyclic R-module R/π^(j_v)R, and every coefficient, a homomorphism between
    cyclic R-modules, is multiplication by an element of R.
  - **Variables.** Lift each x_v to y_v ∈ R with x_v = y_v mod π^(j_v).
  - **Equations.** An equation valued in R/π^j R becomes π^(K−j)(Σ a y) = π^(K−j) c over R, where K is the length of R.
- **What the lift preserves.** The lifted system has the same rows and its solutions are the pull-back, so it fails globally as well.
- **Apply RIGID-SELECTION D.** The top layer (y mod π) of its solutions after any removal has dimension at most one.
- **Back to the sections.** y_v mod π is the leading digit of x_v in its section. So the varying leading digits are pairwise tied,
  and a knot, which has no constrained pair, contains at most one of them.
- **The whole algebra's top.** Where that top factors through the leading digits (ticket B for groups; RIGID-SELECTION D), it is rigid.

**Item 4.** Evidence only: check 4.

**Item 5.**
- **Ticket C** gives rigidity unless some abelian section is not simple. A module that is not simple has a proper nonzero submodule
  and a nonzero quotient, so it has at least four elements.
- **Item 3** places the kept knots below the section's top.
- **The knot.** Check 5, together with BEYOND-TWO C's census: the knot keeps knots after every removal on 5 of the 8 Pfaffian
  substrates.

**Item 6.**
- **Where B's proof breaks.** Its items 4 and 5 give each variable the same range in all its lines.
- **Why.** When a line gives a point a smaller range, removing that line enlarges the point's range. The abelianized system after the
  removal is then not the full system minus a row.
- **The evidence.** Ticket B's check 2 placed such lines in 15% of cases, and every top it met was rigid.
- **Status.** Ticket C records mixed domains as a conjecture. ∎

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | The five-value algebra: Mal'tsev, subalgebras, congruences. | 9 subalgebras, each with a unique maximal congruence; the whole algebra simple |
| 2 | RIGID-SELECTION B's systems inside it, by brute force over five values. | relations closed; global failures; knots kept after 6 of 6 and after some of 9 removals; the top image equals the solutions |
| 3 | Systems of the five-value law with declared domains Z4, {0,2}, {1,3}: RIGID-SELECTION B's example and random systems. | the example keeps knots after all 6 removals and 316 random systems fail globally; in all, the leading digits form at most one line after every removal and every kept knot has at most one varying leading digit |
| 4 | Two chain rings joined only through their tops. | 407 global failures (385 with points of both kinds), none with a knot among the leading digits (evidence) |
| 5 | The knot on the Fano plane. | fails globally; keeps a knot after each of the 7 removals |

## What this does not establish

- **Sections of other kinds.** Sections from different chain rings, and uniserial modules over non-commutative rings with layers of
  different types, are not covered by item 3. Item 4 and ticket C's T2(F2) example are evidence only.
- **Mixed domains.** Not covered (ticket C).
- **Selection in the full sense.** Whether the five-value law also counts hard was not checked. It was not needed here.

## Novelty

- **New here.**
  - The counterexample.
  - The reading "rigid at the top of each section, not at the top of the algebra".
  - The scope correction to ticket B.
