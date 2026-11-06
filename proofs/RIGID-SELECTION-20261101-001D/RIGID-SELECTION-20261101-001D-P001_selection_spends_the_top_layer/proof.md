# Selection spends the top layer

Status: Proved

Ticket `RIGID-SELECTION-20261101-001D`, 2026-11-01.

## Question

- **What tickets A and B found.**
  - **Ticket A.** Over a field, global failures are rigid.
  - **Ticket B.** Over Z4 and other rings Z_(p^k) with k ≥ 2, global failures can keep knots.
  - **What every kept knot in B looks like.** At most one variable takes all values, and the knot hides one digit.
- **The question.** Is that forced? What does a global failure spend, and what can survive it?

## Dependencies

- **`RIGID-SELECTION-20261101-001A`.** The criterion (item 2); its proof works over any finite chain ring. `zlocal.py`.
- **`RIGID-SELECTION-20261101-001B`.** The examples, which this ticket explains.

## Setting

- **Rings.** A finite chain ring R is a finite commutative local ring whose ideals form a chain R ⊋ πR ⊋ … ⊋ π^(k−1)R ⊋ 0.
  - **Notation.** F = R/πR is its residue field, of size f, and k is its length, so |R| = f^k.
  - **Examples.** Z_(p^k), GF(q) (k = 1), Galois rings, and GF(q)[t]/(t^k).
  - **Modules.** Every finite R-module is a sum of cyclic modules R/π^v R.
- **Systems.** Let A be an m × n matrix over R and c ∈ R^m: m equations in n variables, one per line.
  - **The cokernel.** M = R^m / A R^n, with g_L the class of the unit vector e_L.
  - **After a removal.** A_(−L) is A without row L, and K_L = ker A_(−L). After L is removed, the solutions form a coset of K_L
    whenever they exist.
- **The top layer.** The top layer of a set of vectors is the set of their residues mod π, in F^n.
  - **For a group.** For a group K of solutions it is a subspace of F^n. Multiplication by π^(k−1) shows it is isomorphic to π^(k−1)K.

## Theorem

**Main statement.** Suppose the system fails globally: it has no solution, but removing any one equation makes it solvable. Then
m ≤ n + 1, and for every equation L

  K_L ≅ R^(n−m+1) ⊕ N_L with π^(k−1) N_L = 0,

so the top layer of the solutions left after removing L has dimension exactly n − m + 1 over F.

**Consequences for square systems (m = n), the systems of a substrate.**
1. **Fields.** The top layer is one line. For k = 1 the solutions are a line, so only ties remain. This reproves ticket A, item 1.
2. **Kept knots.** A knot (a circuit of three or more variables) of the solutions left after a removal:
   - has at most one variable taking all |R| values;
   - has every other variable taking at most |R|/f = f^(k−1) values;
   - hides at most k − 1 digits: its index in the product of its ranges is at most f^(k−1).
3. **The bound is attained.** Over Z8 the index is 4, and over Z27 it is 9 (check 3). In check 1's sample, every ring with k ≥ 2 reaches
   p^(k−1), including Z16 with 8.

## Proof

**Lemma 1 (criterion; ticket A, item 2).**
- **Statement.** The system without L is solvable iff [c] ∈ R g_L. So it fails globally iff [c] is a nonzero element of every R g_L.
- **Proof.** A_(−L) x = c_(−L) iff Ax = c + t e_L for some t ∈ R, iff [c] = −t g_L.

**Lemma 2 (one socle line).** If some m ≠ 0 lies in every R g_L, then π^(k−1) M ⊆ R g_L for every L.
- **One socle line.** The socle of a nonzero cyclic module R g is one line over F, so a nonzero multiple π^j m lies in the socle.
  Since it lies in every R g_L, it spans the socle of each: every R g_L has the same socle line ℓ.
- **π^(k−1)M lies on ℓ.** The g_L generate M, so π^(k−1) M is spanned by the elements π^(k−1) g_L. Each is either 0 or a nonzero
  element of the socle of R g_L, hence lies in ℓ.
- **Conclusion.** π^(k−1) M ⊆ ℓ ⊆ R g_L. ∎

**Lemma 3.** The cokernel of A_(−L) is M / R g_L.
- **Proof.** Deleting coordinate L maps R^m onto R^(m−1) with kernel R e_L. So R^(m−1) / A_(−L) R^n ≅ R^m / (A R^n + R e_L).

**Proof of the theorem.**
- **Step 1: no free summand.** By Lemmas 1–3, π^(k−1) kills the cokernel of A_(−L): π^(k−1)(M / R g_L) = 0.
- **Step 2: the Smith form.** Bring A_(−L) to Smith form, with diagonal entries π^(u_1), …, π^(u_r) and r = min(m − 1, n) (u = k for
  a zero entry). Its cokernel is ⊕ R/π^(u_a) R plus a free part R^(m−1−r).
- **Step 3: what Step 1 forces.** Since π^(k−1) kills the cokernel:
  - there is no free part, so m − 1 ≤ n;
  - every u_a ≤ k − 1.
- **Step 4: the kernel.** It is ⊕ π^(k−u_a) R ⊕ R^(n−m+1). Each π^(k−u_a) R ≅ R/π^(u_a) R is killed by π^(k−1).
- **Step 5: the top layer.** π^(k−1) K_L ≅ F^(n−m+1). ∎

**Consequences.**
- **Item 1.** For m = n the top layer is a line F τ_L. When k = 1 it is all of K_L, and two moving variables of a line are tied.
- **Item 2.**
  - **Which variables have full range.** The range of variable i on K_L is an ideal of R. It is all of R iff some solution has a unit
    there, iff τ_L,i ≠ 0.
  - **Two full-range variables are tied.** If i and j both have full range, then x_j ≡ (τ_L,j / τ_L,i) x_i (mod π) on K_L. So the
    pair (1, 0) never occurs and the pair is constrained.
  - **At most one per knot.** In a circuit of three or more variables every pair is unconstrained, so at most one variable has full
    range. The others have ranges inside πR, of size at most f^(k−1).
  - **The index bound.** Let C be a circuit with projection H, and pick a variable i in C without full range. The other variables
    of C are unconstrained, so |H| is at least the product of their ranges. Hence the index of H is at most |range of i| ≤ f^(k−1).
  - **Cosets.** Translation preserves circuits, so all of this holds for the solution coset as well.
- **Item 3.** By computation (check 3); the Z8 example is checked by brute force over Z8^6. ∎

## What it means

- **What a global failure spends.** It spends exactly the top layer: after any removal, the residues of the solutions mod π form
  the space a field system would leave (one line for a substrate). This is rigid.
- **What survives.** Emergence survives only in the lower layers, killed by π^(k−1), with at most one full-range variable joining in
  through the shared top line.
- **Fields.** Over a field there is nothing below the top, hence ticket A's rigidity.
- **Rings Z_(p^k), k ≥ 2.** They have k − 1 lower layers, hence ticket B's kept knots. Each kept knot hides at most k − 1 digits, never
  all k.

## Checks

`check.py` (`result.json`, about 18 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Random systems over Z2, Z3, Z5, Z4, Z8, Z16, Z9, Z27, Z25: knot systems on random regular substrates, and arbitrary m × n systems with m = n − 1, n, n + 1, n + 2. Global classes are found exhaustively, since every one lies in R g_0. | 872 global failures (none with m = n + 2), 4418 removals, all top layers of dimension n − m + 1; 763 kept knots, none with two full-range variables or index above p^(k−1); the largest index reaches p^(k−1) in every ring with k ≥ 2 |
| 2 | Brute force over F2[t]/(t²) (characteristic 2, not Z4), with no Smith form: images enumerated, global right-hand sides found by search. | 198 global failures, 969 removals, all top layers of dimension n − m + 1; 261 kept knots in 46 removals, all within the bound |
| 3 | Attaining examples on cubic substrates: Z8 (brute force over Z8^6) and Z27. | knots of index 4 and 9 |

## What this does not establish

- **Other Mal'tsev laws.** Uniserial modules over non-commutative rings, and non-abelian laws beyond S3 and D_p, are not covered.
  For S3 and D_p, ticket A shows their full-range knots are blurred parity.
- **Which lower-layer knots occur.** The theorem bounds them; it does not classify them.
- **The two-valued knot.** It is not linear. Its kept knots on the Pfaffian substrates (BEYOND-TWO C) sit at two values, where a
  linear law would be rigid. That contrast is the point recorded in the epic closure.

## Novelty

- **Classical.** The Smith form over chain rings and the structure of their modules.
- **Closest literature.** Unsolvable modular linear systems are studied as an optimisation problem, Min-r-Lin(Z_m): remove the fewest
  equations to restore solvability. See [Dabrowski, Jonsson, Ordyniak, Osipov and Wahlström](https://arxiv.org/abs/2208.02732v1),
  [the FPT-approximation for Z_(p^n)](https://arxiv.org/abs/2509.04976v1) and
  [optimal FPT-approximability](https://arxiv.org/pdf/2604.10369).
  - **A parallel.** There too the prime-power case differs from the prime case, through layers of values.
- **Not found.** No source checked treats minimally unsolvable systems over chain rings, or the solutions they leave.
- **Assessment.** The theorem is elementary, so folklore risk is moderate. The reading "a global failure spends exactly the top layer"
  is new here.
