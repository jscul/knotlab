# Symmetry cancels returns in networks of loops; a shared ring with more contacts does not

Status: Proved by hand. The finite claims are checked in `check.py`.

Ticket `LOOP-NET-20261108-001A`, 2026-11-08.

## Standard statement

- **Networks.** Rings of rule-60 cells (cell j reads cells j − 1 and j) joined by contacts. A contact is a cell of two rings that
  reads, on each of them, its left neighbour (law (12, 12)) and nothing else (`net_lib.py`). Every ring has at least two contacts,
  and consecutive contacts on a ring are at least two cells apart, so each contact's left neighbours are own cells. A contact
  **binds** a ring at lag T when its value at lag T depends on the ring's own first-row cells (A32); it **persists** when it binds both
  of its rings at every lag.
- **Corners and the contact graph.** On a ring, consecutive contacts d and e (in increasing position) bound a **corner**, the ℓ ≥ 1 own
  cells between them. The **contact graph** Γ has a vertex for each contact and an arc d → e for each corner, of weight z a^ℓ, where
  a = z/(1 + z) over GF(2). Each contact has two arcs in and two out, one on each of its rings. K is the weighted adjacency matrix
  (K_ed sums the weights of the corners from d to e), D = (I + K)^(−1), and the **returns** to c are the closed walks of Γ from c back
  to c.
- **The surface.** Positions give each ring a cyclic order of its contacts. That is a rotation system on the ring graph (rings as
  vertices, contacts as edges), which embeds the ring graph in an oriented closed surface. A closed walk of Γ that keeps to one ring at
  every contact goes round a ring; one that changes ring at every contact goes round a face. Γ is the directed medial graph of the
  embedded ring graph, and every corner lies on exactly one ring and one face.
- **Size and density.** A ring or face has a **size**, its contacts plus the own cells of its corners, and a **density**, its size
  divided by its contacts. The network is **uniform** when, after rescaling contacts, every corner has the same weight ω, so that any
  two returns of the same length to a contact weigh the same.

**Theorem 1 (the criterion).** The two chain-end witnesses of a contact c, the last own cells of its two in-corners, each have
coefficient D_cc · z/(1 + z) in c's value. Both keep coefficient 1 at every lag exactly when D_cc = 1, that is when the returns to c
cancel: the weights of all returns to c add to 0. Otherwise both first have coefficient 0 at lag v + 1, where v is the order of
D_cc − 1 at z = 0. When D_cc = 1, c binds both of its rings at every lag.

**Theorem 2 (uniform networks).** A network is uniform when (a) its contacts are equally spaced, every ring of m contacts having
m·g cells (g ≥ 2), or (b) its surface is a sphere and every ring and every face has the same density κ. In a uniform network
D_cc = 1 + Σ_k N_k(c) ω^k, where N_k(c) is the number of returns of length k to c, mod 2. So the returns to c cancel exactly when every
N_k(c) is even.

**Theorem 3 (symmetry cancels returns).** If an automorphism of Γ that preserves weights up to rescaling fixes c and exchanges its two
out-arcs, the returns to c cancel. Hence in every orientably regular map built as a uniform network, every contact persists at every
lag, at every ring size. These include:
1. loops of r rings (the dihedra), which recovers `LOOP-ANY-20261108-001A`'s balanced loops for law (12, 12);
2. two rings sharing m contacts (the hosohedra), balanced when every face has 2s/m cells, s the rings' size;
3. the five Platonic networks, from the tetrahedron (four rings of three contacts) to the icosahedron (twelve rings of five);
4. lattices of rings on a torus with equally spaced contacts: square (four contacts per ring), triangular (six) and honeycomb (three),
   on an n × n torus for every n ≥ 3 (n ≥ 2 for the honeycomb).

**Theorem 4 (the obstruction where loops meet).** If c joins a ring of two contacts to a ring of three or more, and neither face at c
has two contacts, exactly one return of length 2 reaches c: N_2(c) = 1. In a uniform network the returns to c then do not cancel, and
its witnesses first lapse at lag 2κ + 1 (2g + 1 when equally spaced). Every figure-eight (one ring shared by two loops, one of them of
at least three rings) and every chord across a loop (a theta whose three paths are not all single contacts) has such contacts.

## Nearest known result

- **Determinants and walks.** D_cc = Σ_k (K^k)_cc sums the weights of the returns to c, and by Cramer's rule
  D_cc = det(I + K without row and column c) / det(I + K), each determinant over GF(2) a sum over families of disjoint cycles.
- **Maps.** Rotation systems, medial graphs, and orientably regular maps, whose orientation-preserving automorphisms act transitively on
  darts (Coxeter and Moser, *Generators and Relations for Discrete Groups*, ch. 8; Jones and Singerman 1978). The regular maps on the
  torus are {4,4}, {3,6} and {6,3}.
- **Classification.** Known-with-delta. The ingredients are classical. The delta is reading persistence across time as the
  cancellation of returns in the contact graph, that cancellation by a map's edge-reversing symmetries, and the local obstruction at a
  ring of two contacts.

## Proof of Theorem 1

Index a corner's own cells x_1, …, x_ℓ from the contact d it leaves, so that x_1 reads d. Under rule 60, x_j(t + 1) = x_j(t) + x_(j−1)(t),
so the generating functions X_j = Σ_t x_j(t) z^t satisfy X_j = a X_(j−1) + x_j(0)/(1 + z), with X_0 = C_d, and the last cell is

  X_ℓ = a^ℓ C_d + Σ_j a^(ℓ−j) x_j(0)/(1 + z).

The contact e that ends the corner reads the last cells of its two in-corners: C_e = e(0) + z(X_ℓ + X′_ℓ′). Collecting, C = S + KC,
where S_e is e(0) plus z a^(ℓ−j) x_j(0)/(1 + z) for every own cell x_j of e's two in-corners. Every entry of K is divisible by z, so
I + K is invertible over GF(2)[[z]] and C = DS.

An own cell belongs to exactly one corner and is read only along it. So the last cell of an in-corner of c occurs only in S_c, with
coefficient z/(1 + z), and its coefficient in C_c is D_cc · z/(1 + z). The coefficient of z^T says whether c's value at lag T depends
on that cell. Since z/(1 + z) = Σ_(T≥1) z^T, the witness has coefficient 1 at every lag exactly when D_cc = 1. Expanding,
D_cc = Σ_k (K^k)_cc = 1 + (the sum of the weights of the returns to c).

If D_cc = 1 + E with E ≠ 0 of order v, then D_cc · z/(1 + z) = z/(1 + z) + E · z/(1 + z), and the second term has order v + 1 with
lowest coefficient 1: the witness first has coefficient 0 at lag v + 1. Both witnesses of c carry the same coefficient. When D_cc = 1
both have coefficient 1 at every lag, and each is an own cell of one of c's two rings, so c binds both rings at every lag. ∎

## Proof of Theorem 2

**(a)** Every corner has ℓ = g − 1, so every arc weighs ω = z a^(g−1).

**(b)** A ring or face with d contacts and λ own cells has holonomy (the product of its arcs' weights) z^d a^λ. With density κ,
λ = (κ − 1)d, so the holonomy is ω^d with ω = z a^(κ−1), taken in an algebraic closure when κ is not an integer. On the sphere the rings
and the faces are the faces of the plane graph Γ, and the faces of a connected plane graph generate its cycles. So the given weighting
and the constant weighting ω have the same holonomy round every cycle of Γ. Rescale both to weight 1 on a spanning tree; each remaining
arc closes a cycle whose holonomy both share, so the two weightings differ only by rescaling contacts.

Rescaling contacts by a diagonal Λ replaces K by ΛKΛ^(−1) and leaves the diagonal of D unchanged. So K may be taken to be ωA, with A
the matrix counting Γ's arcs mod 2, and D_cc = Σ_k ω^k (A^k)_cc = 1 + Σ_k N_k(c) ω^k. If every N_k(c) is even, D_cc = 1. Conversely, ω is
nonzero with positive order at z = 0, so it is transcendental over GF(2); by Cramer's rule D_cc = P(ω)/Q(ω) for polynomials P and Q
over GF(2), and D_cc = 1 forces P = Q. Then Σ_k N_k(c) t^k = 0 as a power series in an indeterminate t, so every N_k(c) is even. ∎

## Proof of Theorem 3

Let φ be the automorphism and Λ the rescaling, so that the weight of φ(q) is Λ_(φ(head q)) · weight(q) · Λ_(φ(tail q))^(−1) for every
arc q. φ maps a return W to c onto a return φ(W) to c of the same weight, since the rescalings at its two ends are both Λ_c and cancel.
Every return to c starts with exactly one of c's two out-arcs, and φ exchanges them. So φ maps the returns starting on one of c's rings
bijectively, length by length and weight for weight, onto those starting on the other. The two sums are equal, so the total vanishes
mod 2 and D_cc = 1.

In an orientably regular map the orientation-preserving automorphisms act transitively on darts, the edges with a direction. For each
contact c, joining rings u and v, one of them takes the dart from u to v along c to the dart from v to u. It preserves the rotation
system, so it is an automorphism of Γ; it fixes c and exchanges u and v, so it exchanges c's out-arcs. In a uniform network of kind (a)
every arc weighs ω and it preserves weights. In one of kind (b) every ring has the same contacts and density, and every face the same,
so it preserves every holonomy and hence the weights up to rescaling. By Theorem 1 every contact persists at every lag.

The families listed are orientably regular: the dihedra {r, 2}, the hosohedra {2, m}, the Platonic solids, and the toroidal maps
{4,4}, {3,6} and {6,3} built from an n × n quotient of the plane lattice, which keeps all its rotations. For two rings of s cells
sharing m contacts, density s/m gives every face, which has two contacts, 2s/m cells. Its contact graph is the bidirected cycle on m
contacts, as for a loop of m rings, with rings and faces exchanged: the two networks are surface duals. ∎

## Proof of Theorem 4

A return of length 2 runs c → d along a ring R and d → c along a ring R′.
- **R′ = R.** Then d follows c and c follows d on R, so R has exactly the two contacts c and d, and the return goes round R.
- **R′ ≠ R.** Then c and d both lie on R and R′, and the return changes ring at d and again at c, so it goes round a face whose two
  contacts are c and d.

Each ring or face of two contacts through c gives exactly one return of length 2, so N_2(c) counts them, and under the hypothesis
N_2(c) = 1. No ring has a single contact, so no return has length 1. In a uniform network D_cc = 1 + ω² + (higher powers of ω); ω has
order κ at z = 0, so D_cc − 1 has order 2κ and the witnesses first lapse at lag 2κ + 1 by Theorem 1.

**Where such contacts occur.** In a path of rings of two contacts each, a face that enters the path runs along all of it: arriving at a
contact on one of the path's rings, it changes to the contact's other ring, which leads to the next contact of the path. So a face
through a contact where the path meets a ring of more contacts contains every contact of the path and at least one more.
- **Figure-eights.** The shared ring has four contacts. Where a loop of r ≥ 3 rings meets it, the contact joins the shared ring to a
  ring of two contacts, and each face there runs along the loop's r − 1 ≥ 2 other rings, so has at least three contacts.
- **Chords.** The two rings at the ends of the chord have three contacts. If a path has k ≥ 2 contacts, its end contact joins such a
  ring to a ring of two contacts, and each face there contains the whole path and at least one more contact. ∎

## Remarks

- **Two short loops.** A figure-eight of two loops of two rings each escapes Theorem 4: the faces inside the loops have two contacts,
  so N_2 = 2 at the shared ring's contacts. In the equally spaced network the two corners from one contact to the next, on the shared
  ring and on the loop's ring, weigh the same and cancel. The contact graph mod 2 then has no cycle and no influence returns: a
  degenerate balance (check 7).
- **Balance per loop.** For a network of loops the balance condition is per face: the inside of each elementary loop carries the rings'
  density. For two rings of s cells sharing three contacts each face then has 2s/3 cells, so s is divisible by 3, and check 4 finds that
  these are exactly the placements whose returns all cancel.
- **Beyond symmetry.** Return counts can be even without a symmetry: ticket B finds a plane ring graph of six rings, not regular, whose
  return counts are all even.
- **Other cells at wide spacing.** Theorem 4 stops the witnesses, not every cell. Equally spaced, eight figure-eights and chords all
  miss a ring by lag 600 at spacings 2, 3, 4, 8 and 16. At spacings 5, 6, 7 and 9 the chords (1, 1, 2) and (1, 2, 2) and the
  figure-eight of two four-ring loops persist at every lag through other cells, while the flat figure-eight of two three-ring loops
  and the theta (2, 2, 2) miss a ring as late as lag 1,143 (computed, check 9). None of them persists at every size.
- **Not a metric.** Density is used only in an equality, as the sum of positions was in `LOOP-ANY-20261108-001A`. No length or
  distance is formed.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Theorem 1 on 400 random networks (2 to 5 rings, random rotations and positions): D_cc = 1 exactly when the witnesses hold to lag 300, and otherwise they first lapse at v + 1 | pass |
| 2 | Surfaces: every corner on one ring and one face; genus 0 for plane rotations and 1 for the tori | pass |
| 3 | Theorem 2 (a) on 400 random equally spaced networks: D_cc = 1 exactly when every return count is even | pass |
| 4 | Theorem 2 (b) and its converse at equal ring sizes: two rings sharing three contacts (sizes 6 to 12) and the tetrahedron (6 to 8), every planar placement: every return cancels exactly when every face has the same size | pass: 2,974 placements, 79 balanced |
| 5 | Theorem 3: loops of 2 to 8 rings, two rings sharing 2 to 6 contacts, the five Platonic networks, square tori of side 3 to 6, triangular 3 to 5 and honeycomb 2 to 5, at g = 2, 3, 4: a flip at every contact, every return count even, every contact persistent through its witnesses to lag 300, and D_cc = 1 wherever computed exactly (up to 18 contacts) | pass: 84 networks |
| 6 | Theorem 4: figure-eights (loops of 2 to 6 rings, one of at least 3, both orders on the shared ring) and chords (paths of 1 to 4 contacts, not all 1, flat and on the torus) at g = 2 to 5: at every contact where a ring of two contacts meets a larger ring with no two-contact face, N_2 = 1 and the witnesses first lapse at 2g + 1 | pass: 264 networks, 1,136 such contacts |
| 7 | Two short loops: the contact graph mod 2 is nilpotent | pass |
| 8 | Full state spaces: two rings sharing three contacts, the tetrahedron and a figure-eight of two three-ring loops, at g = 2 | pass |
| 9 | Computed, not a theorem: eight equally spaced figure-eights and chords at spacings 2 to 16 miss a ring by lag 600 at spacings 2, 3, 4, 8 and 16; the rest are followed exactly to the repeat of their rows at spacings up to 9 | pass |

## Nonclaims

- **These networks only:** rule-60 rings (rule 102 by mirror symmetry) with law (12, 12) at every contact.
- **Theorem 4 is about the witnesses.** Other cells can still bind: 254 of the 264 networks of check 6 miss a ring by lag 300, and
  check 9 follows eight of them across spacings. These are computations, not theorems.
- **No distance.** No length, path count used as a magnitude, or metric is formed.
- **Two-time knots only** (A30).
