# Kasteleyn faces and even spin structures

Status: Proved

Ticket `THREEFOLD-SPIN-20261030-001A`, 2026-10-30.

**What it uses:**
- **`THREEFOLD-SURFACES-20261030-001A`:**
  - genus additivity across a 3-edge splice when both sides are rigid (keep their genus when the splice vertex is deleted);
  - Theorem 5: the minimal maps of such a splice are exactly the genus-additive gluings of minimal maps of the sides;
  - in a three-fold space with planar glue, every side of every tight cut is rigid;
  - the 16 minimal maps of the Heawood graph.
- **`THREEFOLD-AMPLITUDE-20261030-001A`:**
  - Lemma 1: Pfaffian signings of a matching covered bipartite graph form one switching class, and a bipartite ear decomposition gives
    nice cycles that span the cycle space;
  - Theorem 4: the pieces of a tight cut with Pfaffian signings;
  - Proposition 5: Pfaffian signings of planar braces are Kasteleyn.
- **`THREEFOLD-GRAMMAR-20261030-001A`:** the braces (Heawood graphs, doubled squares, planar braces); a doubled square is Pfaffian exactly
  with an odd number of negated classes.
- **`THREEFOLD-SPACES-20261030-001A`, Theorem 1:** the knot's trivial signing of a three-fold space is Pfaffian.
- **External, not replayed:**
  - Cimasoni and Reshetikhin, *Dimers on surface graphs and spin structures. I* (Comm. Math. Phys. 275, 2007):
    - Theorem 4.1, the quadratic form of a Kasteleyn orientation and a dimer configuration;
    - Proposition 4.2, its dependence on the configuration;
    - the sign identity in the proof of Theorem 5.1;
  - Johnson, *Spin structures and quadratic forms on surfaces* (1980): spin structures are the quadratic forms on H₁(Σ; Z₂) refining the
    intersection form.

## Why this ticket exists

`THREEFOLD-AMPLITUDE-20261030-001` closed with a question: do the knot's own signs, which are trivial on its three-fold spaces, satisfy
Kasteleyn's face condition on every minimal map? If so, each space carries a spin structure on its surface, and we want its Arf invariant
per Fano atom. A probe found every face of every minimal map of length 2 mod 4, and the Arf invariant 0. This ticket proves both for planar
glue and identifies which spin structures the knot's perfect matchings induce.

## Standard statement

**Setting.**
- **Maps.**
  - B(H) is the incidence graph of a three-fold space H: cubic and bipartite, points white, lines black.
  - A *map* is a rotation system, that is, a cellular embedding in a closed orientable surface Σ. A *minimal map* has least genus.
  - A face is a closed walk; its length is even.
- **Signings and orientations.**
  - A signing negates some edges. It gives an orientation K: point → line, reversed on negated edges.
  - The *Kasteleyn condition* on a face of length 2l: the face carries l − 1 negated edges mod 2.
  - For bipartite faces this is Cimasoni and Reshetikhin's condition (an odd number of edges oriented clockwise). Going around a face, the
    point → line orientation alternates with and against the traversal, and each negated edge changes that count by one.
  - The knot's signing is trivial. So it is Kasteleyn on a map iff every face has length 2 mod 4.
- **Spin structures.**
  - A spin structure on Σ is a quadratic form q on H₁(Σ; Z₂), that is, q(x + y) = q(x) + q(y) + x·y (Johnson).
  - Its Arf invariant is defined by Σ_x (−1)^{q(x)} = (−1)^{Arf(q)} 2^g. *Even* means Arf 0.
  - Given a Kasteleyn orientation K and a perfect matching D, Cimasoni and Reshetikhin define q_D by
    q_D([C]) = n_K(C) + ℓ_D(C) + 1 (mod 2) for a simple cycle C, additively over disjoint cycles. Here:
    - n_K(C) counts the edges of C oriented against a traversal;
    - ℓ_D(C) counts the vertices of C whose matching edge leaves C on one fixed side.
  - Write ξ_D for this spin structure.

**Results.**
- **Lemma 1 (face splice).** Let H be a cubic signed system with a Pfaffian signing, cut along a tight cut into pieces A and R with Pfaffian
  induced signings (ticket A of the amplitude epic, Theorem 4). Let ρ_A and ρ_R be maps of B(A) and B(R) in which the contracted vertices z_A
  and z_R each lie on three distinct faces, and let ρ be a genus-additive gluing. Then:
  - (i) exactly three faces of ρ cross the cut, each the union of one face of ρ_A at z_A and one face of ρ_R at z_R;
  - (ii) if every vertex of ρ_A and of ρ_R lies on three distinct faces, so does every vertex of ρ;
  - (iii) if the induced signings satisfy the Kasteleyn condition on ρ_A and ρ_R, H's signing satisfies it on ρ.
- **Theorem 2 (the knot's signs are Kasteleyn).** Let H be a three-fold space with planar glue, so its braces are Heawood graphs, doubled
  squares and planar braces. Then on every minimal map of B(H):
  - every vertex lies on three distinct faces;
  - every face has length 2 mod 4, so the knot's signing is a Kasteleyn signing.
- **Proposition 3 (Arf does not depend on the matching).** If a Pfaffian signing is Kasteleyn on a map, then for any perfect matchings D and
  D₀, q_{D₀} vanishes on [D Δ D₀], and Arf(q_D) = Arf(q_{D₀}).
- **Theorem 4 (even spin structures).** Let H have planar glue and h Fano atoms, and let ρ be a minimal map, of genus h.
  - (i) H₁(Σ; Z₂) is the orthogonal sum of the atoms' H₁, each of rank 2, and q_D splits accordingly.
  - (ii) On each atom, q_D has Arf invariant 0.
  - (iii) So every ξ_D is even.
  - (iv) [D Δ D₀] lies in the product of the atoms' zero sets of q_{D₀}. So every ξ_D restricts to an even spin structure on every handle,
    and at most 3^h spin structures arise from perfect matchings.
- **Proposition 5 (the Fano space).** On each of the 16 minimal maps of the Heawood graph (the torus), the 24 perfect matchings fall 8, 8, 8
  into the three classes where q_{D₀} vanishes. So the spin structures ξ_D are exactly the three even spin structures of the torus, each
  induced by 8 matchings. The odd one is never induced.

## Nearest known result

- **Kasteleyn's theorem** (planar graphs). The higher-genus formulas of Galluccio–Loebl and Tesler use 4^g Pfaffians.
- **Cimasoni–Reshetikhin (2007)**: the bijection between Kasteleyn orientations and spin structures given a dimer configuration, and the
  quadratic form used here.
- **Zhang–Zhang (2000)**: in a plane elementary bipartite graph every face is a nice cycle. This is the planar reason Pfaffian signings
  are Kasteleyn.
- **What is new here** (no overlap found in a bounded search, candidate local delta):
  - the face-splice lemma;
  - the face-length theorem for three-fold spaces;
  - the evenness of the knot's spin structures on every handle, and the 8, 8, 8 split.
- **Folklore risk.** Moderate for the splice lemma, which is natural.

## Proof of Lemma 1

- **Counting the crossing faces.**
  - Faces of ρ that avoid the cut edges are the faces of ρ_A not at z_A and the faces of ρ_R not at z_R, since rotations elsewhere are
    unchanged.
  - Genus additivity and Euler's formula give F(ρ) = F(ρ_A) + F(ρ_R) − 3, using V = V_A + V_R − 2 and E = E_A + E_R − 3.
  - So exactly (F(ρ_A) + F(ρ_R) − 3) − (F(ρ_A) − 3) − (F(ρ_R) − 3) = 3 faces cross the cut.
- **Arcs.** A crossing face is a cyclic sequence of *arcs*, maximal pieces on one side.
  - An arc on the A side is a face walk of ρ_A between two consecutive visits to z_A, with z_A's two edges replaced by the cut edges.
  - z_A lies on three distinct faces, so each of them visits z_A once and gives one arc: three A-arcs. Likewise there are three R-arcs.
  - Every crossing face has at least one arc on each side. So each of the three has exactly one A-arc and one R-arc: (i).
- **(ii).** The three faces at a vertex v of A other than z_A are distinct faces of ρ_A. Each is kept, or becomes the crossing face through
  its single A-arc. Distinct A-faces have distinct A-arcs, so they stay distinct.
- **(iii).** The non-crossing faces keep their lengths and signs. A crossing face f joins f_A and f_R through two cut edges e_i and e_j:
  - its length is |f| = |f_A| + |f_R| − 2;
  - the edges at z_A carry τ, those at z_R carry τ ⊕ s, and the cut edges of H carry s. Since τ_i + τ_j + (τ_i + s_i) + (τ_j + s_j) ≡
    s_i + s_j, the negated edges satisfy σ(f) ≡ σ_A(f_A) + σ_R(f_R) (mod 2);
  - so the conditions σ_A(f_A) ≡ |f_A|/2 − 1 and σ_R(f_R) ≡ |f_R|/2 − 1 give σ(f) ≡ (|f_A| + |f_R|)/2 − 2 = |f|/2 − 1. ∎

## Proof of Theorem 2

Induction over the tight-cut decomposition. The statement proved is the same for every connected cubic signed system with a Pfaffian
signing whose braces are of the three types. Every map of the system, with any Pfaffian signing:
- (a) has every vertex on three distinct faces;
- (b) satisfies the Kasteleyn condition.

Pfaffian signings form one switching class (ticket A of the amplitude epic, Lemma 1). Switching at a vertex flips two edges of each face
corner there, so it preserves the condition, and one Pfaffian signing suffices.

**Braces.**
- **Heawood graph.** All 16 minimal maps have seven hexagonal faces, with every vertex on three distinct faces (computed). The trivial
  signing satisfies the condition: a hexagon needs an even number of negated edges.
- **Doubled square.**
  - Its planar maps have two digons (the parallel pairs) and two 4-faces, and every vertex lies on three distinct faces.
  - A Pfaffian signing negates an odd number of the four classes, each class uniformly. So each digon carries 0 negated edges mod 2,
    which is what its length 2 requires. Each 4-face uses one edge of each class, hence an odd number of negated edges, which is what its
    length 4 requires.
- **Planar braces.** They are 3-connected, so they have a unique planar map up to mirror image, with three distinct faces at each vertex.
  Their Pfaffian signings are Kasteleyn (ticket A of the amplitude epic, Proposition 5).

**Splices.**
- At a tight cut both sides are rigid (`THREEFOLD-SURFACES-20261030-001A`). So the minimal maps of the system are exactly the genus-additive
  gluings of minimal maps of the two pieces.
- By induction, those maps have (a) and (b) for Pfaffian induced signings. Lemma 1 transfers (a) and (b) to the gluing.

**The knot's signing.** For the knot's trivial signing, (b) says that every face has length 2 mod 4. ∎

## Proof of Proposition 3

- **The bipartite Pfaffian.** For a bipartite graph the Pfaffian of the skew matrix of K is ± the determinant of the signed incidence
  matrix. The sign ε^K(D) of a matching's term is the sign of its term in that determinant.
- **Vanishing on differences.** The proof of Cimasoni–Reshetikhin's Theorem 5.1 gives ε^K(D₀)ε^K(D) = (−1)^{q_{D₀}([D Δ D₀])}. A Pfaffian
  signing gives every matching the same sign, so q_{D₀}([D Δ D₀]) = 0.
- **Changing the matching.** By their Proposition 4.2, q_D = q_{D₀} + (a · −) with a = [D Δ D₀].
- **The Arf invariant.** Arf(q + a·−) = Arf(q) + q(a): substituting x ↦ x + a in the Gauss sum gives
  Σ_x (−1)^{q(x)+a·x} = (−1)^{q(a)} Σ_x (−1)^{q(x)}. Since q_{D₀}(a) = 0, Arf(q_D) = Arf(q_{D₀}). ∎

## Proof of Theorem 4

**(i) Splitting.** Use the gluing of Lemma 1 at a tight cut.
- **The disk around z_A.** z_A lies on three distinct faces. Their union with z_A and its three edges is an open disk. Removing z_A
  therefore leaves a cellular decomposition of Σ_A whose 1-skeleton is A − z_A.
- **Representatives.** So cycles of A − z_A represent all of H₁(Σ_A), and likewise for R.
- **The direct sum.** In the connected sum Σ = Σ_A # Σ_R these classes give H₁(Σ) = H₁(Σ_A) ⊕ H₁(Σ_R). They are orthogonal, since their
  supports are disjoint.
- **The form agrees.** For a cycle C of A − z_A, q_D([C]) computed in ρ equals q_{D_A}([C]) computed in ρ_A, where D_A is the piece's
  matching induced by D:
  - n_K(C) agrees, because signs agree away from z_A;
  - ℓ_D(C) agrees, because the matching edge at each vertex of C is the same edge (a cut edge becomes z_A's edge) and leaves C on the same
    side, since rotations at C's vertices are unchanged.
- **Induction.** Inducting down to the braces, the planar ones contribute no homology. q_D is the orthogonal sum of the forms of the
  Fano atoms.

**(ii) Each atom is even.**
- **Nice cycles span.** A bipartite ear decomposition of the Heawood graph gives nice cycles C = M₁ Δ M₂ forming a basis of its cycle space
  (ticket A of the amplitude epic, Lemma 1). The cycle space maps onto H₁ of the torus.
- **So differences span.** [C] = [M₁ Δ D₀] + [M₂ Δ D₀], so the classes of matching differences relative to D₀ span H₁ = Z₂².
- **Arf 0.** By Proposition 3, q_{D₀} vanishes on all of them. A spanning set of Z₂² contains two distinct nonzero classes. A form on Z₂²
  with Arf invariant 1 vanishes only at 0. So Arf = 0.

**(iii) The whole space.** Arf invariants add over orthogonal sums, because Gauss sums multiply.

**(iv) Restriction to every handle.**
- **Closures.** A matching difference crosses each cut through pairs of cut edges. Closing its pieces through z_A and z_R gives cycles on
  each side whose classes sum to its class in Σ_A # Σ_R.
- **On each side.** The closures are the differences D_A Δ D₀_A and D_R Δ D₀_R of the induced matchings. Each lies in its side's zero set
  of q (Proposition 3 for the piece).
- **Even on each handle.** Inducting, [D Δ D₀] has, on each atom, a component in the atom's zero set {0, a, b}. So ξ_D = ξ_{D₀} +
  PD[D Δ D₀] restricts on each atom to the even form plus a zero, which is even (Proposition 3's formula). ∎

## Proof of Proposition 5

- **The computation.** On each of the 16 Heawood maps, the classes of the 24 differences D Δ D₀ are 8, 8 and 8 on three classes, and these
  are exactly the zeros of q_{D₀} (computed).
- **The spin structures.** By Proposition 3, ξ_D = ξ_{D₀} + PD[D Δ D₀]. As D varies this runs over ξ_{D₀} plus the three zeros, which are
  the three even spin structures. ∎

## What the computation checks

`check.py` (about fifteen seconds):
- **Base pieces:**
  - the 16 Heawood maps;
  - all planar maps of the doubled square with every signing (Kasteleyn exactly for 1 or 3 negated classes);
  - the cube, hexagonal prism and truncated octahedron with their Kasteleyn signings.
- **Lemma 1 and Theorem 2:**
  - all 128 minimal maps of the 13-point space;
  - 256 of the 19-point composition;
  - 64 each of the 21- and 22-point spaces.

  Every tight cut is crossed by three faces using two of its edges, every vertex lies on three distinct faces, and every face has length
  2 mod 4.
- **Propositions 3 and 5** on the Fano space:
  - the form evaluated on all 256 cycle-space elements of every map, with no inconsistency;
  - Arf 0 for each of the 24 matchings;
  - the 8, 8, 8 split.
- **Theorem 4** on the 13-point space:
  - all 128 maps have Arf 0;
  - the form vanishes on all 192 matching differences;
  - 9 of the 10 even classes are realized (the product of the atoms' zero sets);
  - exhaustive well-definedness on four maps.
- **Spanning:** on every Heawood map, single nice cycles span H₁.
- **Controls:**
  - 19.5% of random non-minimal Heawood maps fail the face condition, so it is not automatic;
  - one flipped sign breaks the condition and makes the form ill-defined;
  - among the three other Kasteleyn classes of a Heawood map exactly one gives an odd spin structure.

## Reading

- **The knot's own signs are a Kasteleyn structure on its own surface.** On every minimal map, every face has length 2 mod 4. Each perfect
  matching then gives a spin structure, all with the same Arf invariant.
- **The spin structure is even, handle by handle.**
  - On each Fano handle the matchings see exactly the three even spin structures of the torus. The odd one is never induced; it is the
    only spin structure of the torus that does not bound a spin 3-manifold.
  - Since the Arf invariant is the spin bordism class of a surface, every knot surface with any of its induced spin structures bounds a
    spin 3-manifold.
- **Evenness belongs to the minimal surface.** Ticket B finds odd spin structures for the same signs on some non-minimal maps, of genus 3
  and higher.
- **The two/three boundary, once more.** The Fano atom, the three-place obstruction, carries the handle and its even spin structure. The
  two-place glue stays flat and carries none.

## Nonclaims

- **Non-planar glue** (trisums) is not covered by the theorem. Ticket B computes it.
- **Non-minimal embeddings** are not treated.
- **Equality** with all 3^h handle-even spin structures is shown only for the Fano space here. Ticket B computes it for larger spaces.
- **External inputs.** Cimasoni–Reshetikhin and Johnson are used, not replayed. The computation confirms their consequences on the stated
  maps.
