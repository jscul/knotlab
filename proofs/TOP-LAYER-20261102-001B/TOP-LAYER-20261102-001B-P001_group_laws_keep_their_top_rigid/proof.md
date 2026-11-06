# Group laws keep their top rigid

Status: Proved

Ticket `TOP-LAYER-20261102-001B`, 2026-11-02.

## Question

- **The test the owner asked for.** The non-abelian groups that compose like cycles, up to order 24.
- **What is asked.** Which groups compose like cycles? When one of their knot systems fails globally on a substrate, does the top
  stay rigid?

## Dependencies

- **`KNOT-CIRCUITS-20261020-001`.** Theorem 1: a Mal'tsev law composes like cycles iff every subalgebra has a unique maximal
  congruence.
- **`RIGID-SELECTION-20261101-001`.**
  - D: the top-layer theorem over finite chain rings.
  - B: the Z4 example.
  - A: `zlocal.py`.
- **`TOP-LAYER-20261102-001A`** (order of tickets only).

## Setting

- **The coset law of G.** Its relations are the cosets of subgroups of G^k, and its Mal'tsev operation is xy⁻¹z.
- **Subalgebras and congruences.** Subalgebras are cosets of subgroups. The congruences of a coset gH correspond to the normal
  subgroups of H.
- **The top.** If G has a unique maximal normal subgroup N, the algebra's top is G → G/N.

## Theorem

1. **Which groups compose like cycles.** The coset law of G composes like cycles iff every subgroup of G has a unique maximal normal
   subgroup. Call such a group a U-group.
2. **Their structure.** In a U-group:
   - every Sylow subgroup is cyclic;
   - G/N has prime order q;
   - the abelianization of every subgroup is a cyclic p-group.

   **Up to order 60.** The U-groups are the cyclic p-groups and 18 non-abelian groups:
   - the dihedral groups of order 2p^k, for p^k = 3, 5, 7, 9, 11, 13, 17, 19, 23, 25, 27, 29;
   - C5⋊C4, C7⋊C3, C13⋊C3, C13⋊C4, C11⋊C5 and C19⋊C3.
3. **Knots.** Every knot of a U-group law is pulled back from a linear relation over a cyclic p-group quotient of its ranges.
4. **Systems.** Every system's solutions are pulled back from a linear system over the cyclic p-groups A_v/A_v′, where A_v is the
   subgroup of a variable's ambient range. A global failure lives in one prime p, as a square system over Z_(p^K).
5. **The top is rigid.** After any removal from a global failure on a substrate, the image of the solutions in (G/N)^n is at most
   one line, so only ties remain.
6. **Depth.**
   - **Squarefree order.** The law is rigid when |G| is squarefree.
   - **Knots below the top.** It keeps knots below its top in C5⋊C4 and D9, through their cyclic subgroups of order 4 and 9.

## Proof

**Item 1.** By Theorem 1 with the setting above: a coset gH has a unique maximal congruence iff H has a unique maximal normal subgroup.

**Item 2.**
- **Cyclic Sylows.** In a p-group every maximal subgroup is normal of index p. A unique maximal normal subgroup is therefore the unique
  maximal subgroup. Then P/Φ(P) is cyclic, and so is P (Burnside's basis theorem).
- **Metacyclic.** A group whose Sylow subgroups are all cyclic is metacyclic (Hölder, Burnside, Zassenhaus), with a presentation
  ⟨a, b | a^m, b^n, b a b⁻¹ = a^r⟩ where gcd((r − 1)n, m) = 1. Such a group is solvable.
- **The top.** G/N is simple and solvable, so it is cyclic of prime order.
- **Abelianizations.** For a subgroup H, the maximal subgroups of H/H′ correspond to the maximal normal subgroups of H containing H′.
  There is only one. A finite abelian group with a unique maximal subgroup is a cyclic p-group.

**Item 3.**
- **The kernels.** Let H ≤ R_1 × … × R_k (k ≥ 3) have every (k − 1)-projection full. Let N_i be the set of x ∈ R_i with
  (1, …, x, …, 1) ∈ H.
- **The graph.** N_i is normal in R_i and H ⊇ Π N_i. H / Π N_i is the graph of a homomorphism f from R_1 × … × R_(k−1) onto
  Q = R_k / N_k.
- **Each factor reaches all of Q.** The projection of H away from coordinate i is full, so each restriction f_i: R_i → Q is onto.
- **Q is abelian.** The images of different factors commute, so Q is abelian. As a quotient of R_k^ab, Q is a cyclic p-group.
- **Conclusion.** By symmetry R_i / N_i ≅ Q for every i, and H = {x : Σ f_i(x_i) = 0} pulled back. Cosets are translates.

**Item 4.**
- **Saturation.**
  - **Setup.** Let A_v be the intersection of the subgroups of v's ranges in the lines that remain. Each line's relation, restricted
    to these ranges, is invariant under right multiplication by Π (N_(L,v) ∩ A_v).
  - **This contains Π A_v′.** A_v′ ⊆ R_(L,v)′ ⊆ N_(L,v), since R_(L,v)/N_(L,v) is abelian. So the solution set is a union of cosets
    of Π A_v′.
  - **The pulled-back system.** It is pulled back from a system over the cyclic p-groups A_v/A_v′.
- **Primes separate.** A line's equation lives in one prime, and a variable of another prime does not enter it. Removing a line of a
  solvable prime leaves a failing prime failing, so a global failure has all its lines in one prime p.
- **One ring.** Write each p-variable, valued in C_(p^j), as y ∈ Z_(p^K) (K the largest exponent) taken mod p^j. An equation valued
  in C_(p^j) becomes p^(K−j)(Σ a y) = p^(K−j) c over Z_(p^K).
- **What this gives.** A square system over Z_(p^K): n lines and at most n columns. Its solutions are the pull-back, and global
  failure is preserved.

**Item 5.**
- **The top layer.** By RIGID-SELECTION D, the top layer (y mod p) of the solutions after a removal has dimension at most one.
- **The group's top map.** On a variable, the map to G/N factors through A_v^ab, since G/N is abelian. It is zero unless p = q and
  A_v ⊄ N, and then it is y mod q up to a unit.
- **So the top image** is at most one line, with only ties.
- **If p ≠ q.** No line constrains the q-variables, so their tops are free and independent: no circuits.

**Item 6.**
- **Squarefree.** Every A_v^ab has prime order, so K = 1, a field, and the solutions after a removal form a line: only ties.
- **The examples (check 3).**
  - **C5⋊C4.** RIGID-SELECTION B's signed Z4 example, placed in a cyclic subgroup of order 4, keeps knots after every removal. Its
    top image is one line.
  - **D9.** A unit-weighted Z9 system, placed in the cyclic subgroup of order 9, keeps knots after two removals. Its top is constant,
    because that subgroup lies in N.

∎

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | All groups with a metacyclic presentation up to order 60 (102 classes), the U-property tested on every subgroup. | 25 cyclic p-groups and the 18 non-abelian groups listed; all structural facts of item 2 hold |
| 2 | Random knot systems (pull-backs, consistent ranges, some lines reading their own ranges) in the seven non-abelian U-groups up to order 24, on cubic substrates with 4–7 points and on K5^(4), brute force over G^n. | every global failure saturated by the derived subgroups and with a top image of at most one line, only ties; none keeps a knot |
| 3 | The examples in C5⋊C4 and D9. | global; knots kept below the top; top rigid |

## What this does not establish

- **Beyond order 60.** Groups larger than 60 are covered by the proof, not by the checks.
- **Other groups with depth.** Knots kept below the top are shown for C5⋊C4 and D9 only. D25, D27 and C13⋊C4 have cyclic subgroups of
  order 25, 27 and 4, where RIGID-SELECTION B found or built such examples, but they are not placed here.

## Novelty

- **Classical.** Z-groups (Hölder, Burnside, Zassenhaus), Burnside's basis theorem, and Goursat-type arguments.
- **New here.**
  - The list of groups that compose like cycles, read through KNOT-CIRCUITS Theorem 1.
  - The top theorem for group laws.
