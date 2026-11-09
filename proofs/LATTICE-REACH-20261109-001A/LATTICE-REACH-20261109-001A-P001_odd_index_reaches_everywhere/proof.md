# Composition reaches everywhere at odd index except at digons and the honeycomb's pinned ring

Status: Theorems 1 and 2 proved by hand, their finite claims checked in `check.py`; the classification at odd index and the reading of
even index are computed (checks 3 and 4, and the stress test of `LATTICE-REACH-20261109-001`).

Ticket `LATTICE-REACH-20261109-001A`, 2026-11-09.

## Standard statement

- **Tori of every shape.** The square, triangular and honeycomb lattices of rule-60 rings with equally spaced law-(12, 12) contacts, modulo
  any sublattice Λ of Z² whose quotient joins no ring to itself, in the coordinates of `RESCUE-MAP-20261109-001A`; the **index** N is the
  number of rings (of A rings on the honeycomb), and G = Z²/Λ.
- **Composing everywhere.** A contact c needs ring X when an odd number of walks of some length lead from one of X's contacts to c
  (`LATTICE-NET-20261108-001A`, Theorem 1). A torus **composes everywhere** when every contact needs every ring, as the odd square n × n
  tori do (`LATTICE-NET-20261108-001A`, Theorem 2).
- **Walk polynomials.** On the square lattice two arcs between contacts of one kind multiply by L = x + 1/x + y + 1/y = (x + y)(1 + 1/xy);
  on the honeycomb three arcs multiply by M = (1 + x)(1 + y/x)(1 + 1/y) (`HONEY-REACH-20261109-001A`, Theorem 1); on the triangular
  lattice, in its coordinates, by x⁻¹(1 + x)(1 + 1/y)(1 + xy), its six-neighbour sum. Each is a product of one-step factors 1 + u.
- **Digons.** A torus has a **digon face** when two contacts consecutive on a ring are also consecutive on the other ring they share.

**Theorem 1 (digons stop composition).** A square torus has a digon face exactly when Λ holds (1, 1) or (1, −1), a honeycomb torus
exactly when Λ holds a unit (1, 0), (0, 1) or (1, −1), and no triangular torus has one. On a digon torus a one-step factor of the walk
polynomial vanishes in GF(2)[G], every walk of two or more arcs (square) or three or more (honeycomb) cancels,
and every contact needs at most 6 rings (square) or 14 (honeycomb); in every digon torus read, at most 4 and 6. So a digon torus with more
rings than that does not compose everywhere.

**Theorem 2 (the power 2^r − 1 on odd square tori).** Let N be odd, Λ without a digon, e the exponent of G and 2^r ≡ 1 (mod e). Write A
and B for the images in G of the two diagonals Z(1, −1) and Z(1, 1). Then L^(2^r − 1) is 1 exactly at the points of G outside
(A Δ B) ∪ {0}. When A ∩ B = 0, as on the n × n torus, this is `LATTICE-NET-20261108-001A`'s off-diagonal power.

**Computed (checks 3 and 4, stress test).**
1. **Odd index (3 to 151).** A square torus of odd index composes everywhere exactly when it has no digon (6,945 tori). Every triangular
   torus of odd index composes everywhere (6,870). A honeycomb torus of odd index composes everywhere exactly when it has no digon and is
   not the n × n torus with 3 ∤ n (`HONEY-REACH-20261109-001A`, Theorem 4), with one exception up to rotation: the three lattices
   ⟨(63, 0), (8, 1)⟩, ⟨(63, 0), (54, 1)⟩ and ⟨(7, 0), (6, 9)⟩ of index 63, each symmetric under one mirror, where each contact never needs 6 of
   the 126 rings, although every ring needs every ring (7,095 tori).
2. **Even index (to 48).** Composition reaches everywhere on 1,002 of 1,124 square tori without digons, 967 of 1,147 triangular and 780 of
   1,147 honeycomb. No rule by the lattice modulo 16, by the 2-part of G or by its mirror symmetries decides it: each splits classes that
   hold both verdicts (26 of 71, 10 of 11 and 2 of 2 on the square lattice).

## Nearest known result

- **Additive cellular automata.** Linear cellular automata over GF(2) on finite abelian groups (Martin, Odlyzko and Wolfram 1984);
  `LATTICE-NET-20261108-001A`, Theorem 2, and `HONEY-REACH-20261109-001A`, Theorem 4, for the square and honeycomb n × n tori.
- **Classification.** Known-with-delta. The delta is composition across time on tori of every shape: at odd index only digon faces and the
  honeycomb's pinned ring stop it, apart from one torus; even index has no rule by the invariants tried.

## Proof of Theorem 1

**Digons.** On the square lattice a ring at p lists contacts towards p + e1, p + e2, p − e1, p − e2, and two consecutive ones lead to the
same ring exactly when the difference of their directions, e1 − e2 or e1 + e2 up to sign, lies in Λ. On the honeycomb A(p) leads to
B(p), B(p − e1) and B(p − e2), and consecutive ones coincide exactly when e1, e2 or e1 − e2 lies in Λ (B rings likewise). On the triangular
lattice consecutive directions differ by a unit, so a digon would join a ring to itself.

**A factor vanishes.** On the square lattice, (1, 1) ∈ Λ makes xy = 1 in G, so 1 + 1/xy = 0, and (1, −1) ∈ Λ makes x = y, so x + y = 0;
either way L = 0. A walk of 2k arcs between contacts of one kind counts L^k and one of 2k + 1 arcs from the other kind counts a one-step
factor times L^k, so every walk of 2 or more arcs cancels, and a contact c needs only its own two rings and the rings of the at most two
contacts with an arc into c: 6 rings at most. On the honeycomb a unit in Λ makes 1 + x, 1 + 1/y or 1 + y/x vanish, so M = 0, and a walk of
3m + s arcs counts P_ij M^m (`HONEY-REACH-20261109-001A`, Theorem 1): every walk of 3 or more arcs cancels, and c needs only the rings of the
at most 1 + 2 + 4 contacts within two arcs of it: 14 at most. Check 1 reads every digon torus of index up to 81 (odd) and 48 (even): at
most 4 and 6 rings, and only the tori of two rings compose everywhere. ∎

## Proof of Theorem 2

Since N is odd, 2 is invertible in G and k = 2^r − 1 is a multiple of the order of every element. All binomials C(k, i) are odd, so
(x + y)^k = y^k Σ_(i = 0..k) (x/y)^i. The element x/y generates A, of odd order o dividing k; the k + 1 terms run k/o times round A and once
more at the identity, and k/o is odd, so (x + y)^k = δ_0 + J_A, where J_A is the sum of the elements of A and y^k = 1. Likewise
(1 + 1/xy)^k = δ_0 + J_B. Their product is δ_0 + J_A + J_B + J_A J_B, and J_A J_B = |A ∩ B|·J_(A+B) = J_G, since A + B contains 2e1 and
2e2, hence all of G, and |A ∩ B| is odd. At q ∈ G the value is [q = 0] + [q ∈ A] + [q ∈ B] + 1, which is 0 exactly when q = 0 or q lies in
exactly one of A and B. Check 2 confirms it on all 671 odd square tori without digons of index up to 49. ∎

## Remarks

- **Why odd index is easy and even is not.** Squaring is additive over GF(2), so L^(2k) is L^k pushed forward by doubling on G. At odd
  index doubling is a bijection and powers only permute; at even index doubling folds G onto 2G and the fibres over the 2-torsion add up
  mod 2, so the reached set depends on the parity of sums over cosets of G[2] at every scale. That is why no invariant of the lattice modulo
  a power of 2 decided it.
- **Contact level and ring level.** On digon tori every ring may still need every ring (on the square and honeycomb, 4 and 6 more tori
  are full at ring level than at contact level at odd index), and on the index-63 honeycomb torus every ring needs every ring while each
  contact misses 6.
- **The positive half is computed.** Theorem 2 gives every square torus of odd index a power that reaches all but the two diagonal
  subgroups' symmetric difference; when A ∩ B ≠ 0 the rings left over are not covered by it alone, and full reach there is computed.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Theorem 1: no triangular digon; on every digon torus to index 81 (odd) and 48 (even) every contact needs at most 4 (square) or 6 (honeycomb) rings | pass: 127 square, 193 honeycomb |
| 2 | Theorem 2: L^(2^r − 1) on every odd square torus without digons to index 49 | pass: 671 tori |
| 3 | Computed: the odd-index rule on every torus of odd index 3 to 81, with the index-63 honeycomb class as its only exception | pass |
| 4 | Computed: even index to 48, the share composing everywhere, and the classes by lattice mod 16, 2-part and mirrors that hold both verdicts | pass |

## Nonclaims

- **Full reach at odd index is computed** (to index 151, with the stress test), not proved, except on the square and honeycomb n × n tori.
- **No even-index rule is claimed**; three invariants are shown not to be one.
- **Two-time knots only** (A30); equally spaced rings only; no distance.
