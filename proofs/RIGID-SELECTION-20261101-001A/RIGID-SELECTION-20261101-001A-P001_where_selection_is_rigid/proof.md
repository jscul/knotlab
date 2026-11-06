# Where selection is rigid, and the criterion over Z_(p^k)

Status: Proved

Ticket `RIGID-SELECTION-20261101-001A`, 2026-11-01.

## Question

- **What BEYOND-TWO found.** A law that composes like cycles and selects in the knot's full sense: blurred Z3 on corank-1 substrates.
  Its selected spaces are *rigid*: after a line is removed, only ties remain.
- **The question.** Is rigidity forced by composing like cycles? This ticket proves rigidity where it holds and gives the exact
  criterion over Z_(p^k), where it can fail.

## Dependencies

- **`BEYOND-TWO-20261101-001`.**
  - B: the blurring lemma (circuits and failures are kept).
  - C: global failure, the census, and parity never failing globally on cubic substrates.
- **`KNOT-CIRCUITS-20261020-001B`.** Constrained sets, circuits and ties (range-relative). Theorem 1 (which Mal'tsev laws compose like
  cycles).

## Setting

- **Systems.** A substrate is a connected k-regular k-uniform system: n points and n lines. A knot system puts on every line a linear
  equation over a ring R, with unit coefficients on the line's points and a right-hand side c_L. Its matrix A is n × n.
- **Global failure.** The system fails globally when it has no solution but removing any one line makes it solvable.
- **Rigidity.** It is rigid when, after any line is removed, every circuit of the solution set is a tie of two variables.

## Theorem

1. **Fields.** Over a field, every global failure has corank 1. Removing any line leaves an affine line of solutions, so only ties
   remain. Every global failure is rigid, at every arity.
2. **Z_(p^k).** Let M be the cokernel of A and g_L the class of the unit vector of line L.
   - **The criterion.** The system fails globally iff the class [c] is a nonzero element of every cyclic subgroup ⟨g_L⟩.
   - **The solutions after removing L.** They form a coset of a group K_L of order |M| · |ann(g_L)|.
   - **Cyclic groups give ties.** If K_L is cyclic, only ties remain.
3. **Other families are rigid.**
   - **Blurred laws.** Blurring keeps rigidity.
   - **S3 and D_p.** For G = D_p (p an odd prime; D_3 = S3), the only proper subgroup of G³ with full 2-projections is the
     sign-parity subgroup. So these laws' knots on full ranges are blurred parity: never global on cubic substrates, and rigid.
     Their knots on smaller ranges live in abelian sections, which are fields here, so they are rigid too.
   - **Simple three-value algebras.** A simple non-affine Mal'tsev algebra on three values has no knot on full ranges.

## Proof

**Item 1.**
- **Setup.** Let Y be the left kernel of A and f(y) = y · c. Failure means f ≠ 0 on Y. Removing line L makes the system solvable iff
  f vanishes on Y_L = {y ∈ Y : y_L = 0}.
- **Every coordinate is nonzero.** If some L had y_L = 0 for all y ∈ Y, then Y_L = Y and the failure would survive the removal of L.
  So for a global failure every coordinate functional π_L on Y is nonzero, and Y_L = ker π_L is a hyperplane.
- **Corank 1.** Each hyperplane ker π_L lies in ker f, hence equals it. So all π_L are proportional to f. The inclusion Y → Fⁿ then
  has rank 1, so dim Y = 1.
- **After a removal.** The left kernel of A_{−L} is Y_L = 0. So A_{−L} has full row rank n − 1, and its solutions are x₀ + tv
  (t ∈ F). Two moving variables (v_i, v_j ≠ 0) determine each other, so they are tied. Any three of them contain such a pair. ∎

**Item 2.**
- **The criterion.** A_{−L}x = c_{−L} is solvable iff Ax = c + t e_L for some x and t, iff [c] = −t g_L, iff [c] ∈ ⟨g_L⟩.
- **The order of K_L.** K_L = {x : Ax ∈ R e_L}. The map x ↦ (Ax)_L sends it onto {t : t g_L = 0} = ann(g_L), with kernel ker A.
  For a square matrix over a finite ring, |ker A| = |coker A| = |M|.
- **Cyclic means ties.** If K_L = ⟨v⟩, the solutions are x₀ + tv. Variable i takes ord(v_i) values and is a function of t mod
  ord(v_i). Two moving variables have max(ord_i, ord_j) < ord_i · ord_j joint values, so they are constrained: a tie. Larger sets
  contain such a pair, so they are not circuits.
- **Fields again.** For k = 1, M is a vector space and the cyclic subgroups ⟨g_L⟩ are lines. A nonzero common element forces all of
  them to be one line, which generates M. So M has dimension 1, as in item 1. ∎

**Item 3.**
- **Blurring.** Blurring keeps failures and circuits (BEYOND-TWO B), hence rigidity.
- **S3 and D_p.** Let H ≤ G³ have full 2-projections, and let K = H ∩ (G × 1 × 1). Then K is normal in G and |H| = |G|²|K|. By
  symmetry the same K-order holds at every coordinate.
  - **K = 1.** H is the graph of a homomorphism f: G² → G whose restrictions f(·,1) and f(1,·) are onto. Their images commute, so G
    would be abelian, which it is not.
  - **K = C_p.** H ⊇ C_p³, and H/C_p³ is a subgroup of order 4 of (G/C_p)³ = Z2³ with full 2-projections. That is even parity, so H is
    the sign-parity subgroup.
  - **K = G.** H = G³.
  - **The failures.** Sign-parity is parity blurred by the sign map, so its failures are parity's: never global on cubic substrates
    (BEYOND-TWO C), and rigid at even arity (item 1 and blurring).
  - **Smaller ranges.** On smaller ranges the variables live in C_p or C_2, which are fields, so item 1 applies.
- **Simple three-value algebras.** In a congruence-permutable variety, every subdirect power of a simple non-abelian algebra is defined
  by graphs of automorphisms between coordinates (commutator theory, the skew-free property). Such a ternary relation with full
  2-projections is the whole cube, so no knot has full ranges. ∎

## Checks

`check.py` (`result.json`, about 8 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Random knot systems over GF(3), GF(5), GF(7), at arities 3 and 4. | 140 global failures; all corank 1 and rigid at every removal |
| 2 | The Z_(p^k) criterion against direct computation, on random square systems over Z4, Z8, Z9 with every right-hand side; and \|K_L\| = \|M\| · \|ann(g_L)\| at every line. | 9031 failures, 2650 global; all agree |
| 3 | Random global failures over Z4, Z8, Z9, Z25, Z27, arities 3 and 4. | 1885 removals with a cyclic group: all ties. 512 with a non-cyclic group: 106 keep a knot (ticket B) |
| 4 | Subgroups of S3³ generated by two elements, with full 2-projections. | only the sign-parity subgroup (781 subgroups checked) |
| 5 | 200 sampled simple non-affine Mal'tsev algebras on three values. | 70200 two-generated subuniverses of A³; none proper with full 2-projections |

## What this does not establish

- **Non-rigid failures.** Whether they exist is ticket B. Check 3 already sees them; B verifies examples.
- **The full skew-free theorem.** It is cited from commutator theory, not reproved; check 5 samples it.
- **D_p for p > 3.** Only S3 was enumerated; the other D_p rest on the order argument.

## Novelty

- **Classical.** Linear algebra over fields and local rings, Goursat-type subgroup arguments, and the skew-free property.
- **New here.** The rigidity statements for global failures and the cokernel criterion. They are elementary, with moderate folklore
  risk.
