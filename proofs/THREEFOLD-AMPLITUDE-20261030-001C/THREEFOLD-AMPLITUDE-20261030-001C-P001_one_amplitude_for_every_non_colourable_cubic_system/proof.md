# One amplitude for every non-colourable cubic system

Status: Proved

Ticket `THREEFOLD-AMPLITUDE-20261030-001C`, 2026-10-30.

**What it uses:**
- **`THREEFOLD-AMPLITUDE-20261030-001A`:**
  - the setting: signed systems, colourings, the amplitude A(H, L), Pfaffian signings;
  - Lemma 1: Pfaffian signings form one switching class, and switching preserves amplitudes;
  - Theorem 2: the amplitude identity λ(0) = (−1)^(n−1) A(H, L₀);
  - Theorem 4: factorization across a tight cut;
  - Proposition 5: the pointer argument for planar braces.
- **`THREEFOLD-SPACES-20261030-001A`, Theorem 1**, through ticket A: the unsigned dictionary. Lemma 4 below is its signed form.
- **External, not replayed:** none beyond those of ticket A. Seymour's linear-algebra argument (1974) is reproved here in signed form.

## Why this ticket exists

Ticket A proved the product formula for Heawood graphs, doubled squares, planar braces and one trisum. Two points stayed open:
- corner independence for general non-planar braces;
- for planar braces, corner independence rested on Tutte's theorem.

A probe of trisums of three prisms then found one amplitude at every line, in every case, with a value that depends on how the pieces are
glued. This ticket proves corner independence for every non-colourable cubic system. It counts one weighted sum over the incidence graph in
two orders. The same count shows that a system and its transpose have the same amplitude.

## Standard statement

**Setting.**
- **Systems.** H is a cubic signed system as in ticket A: n points and n lines, three incidences at each, repeated incidences equally signed.
  - Write τ_e = ±1 for the sign of an incidence e = (w, p): −1 when negated.
  - With spins s ∈ {±1}, line w *sees* τ_e s_p at its incidence e. It is proper when its three seen values are not all equal.
- **The transpose.** Hᵀ exchanges points and lines and keeps the incidences and their signs. Its line p sees τ_e s_w at each incidence
  e = (w, p).
- **Counts.**
  - M_{Lp} is the multiplicity of p on L.
  - col(H) is the set of proper colourings.
  - N_H(L) counts the colourings proper on every line except L and improper on L. If H is not colourable, N_H(L) = 2A(H, L).
- **The correction term.** R(L) sums ε_e(y) over the colourings y ∈ col(Hᵀ) and the incidences e = (L, p).
  - In a proper colouring of Hᵀ, two of the three values seen by line p agree: the *majority*.
  - ε_e(y) = +1 when the value seen at e is the majority value, and −1 when it is the odd one.

**Results.**
- **Lemma 1 (the half-angle).** For m ∈ {±1, ±3}:
  - Σ_{s=±1} e^{iπsm/6} is √3 if |m| = 1 and 0 if |m| = 3;
  - Σ_{s=±1} s e^{iπsm/6} = 2i sin(πm/6), so m times it is i if |m| = 1 and 6i if |m| = 3.
- **Lemma 2 (two-way count).** For every cubic signed system H and every line L:
  - (a) #col(H) = #col(Hᵀ);
  - (b) #col(H) + 6 N_H(L) = 2 Σ_p M_{Lp} N_{Hᵀ}(p) + R(L).
- **Theorem 3 (one amplitude).** If H is connected and not colourable, then A(H, L) = A(Hᵀ, p) for every line L and every point p.
- **Lemma 4 (signed dictionary).** Let H be a connected cubic signed system.
  - (i) If its signing is Pfaffian, H is not colourable.
  - (ii) If H is not colourable, then H − L is colourable for every line L, and the signing is Pfaffian.
- **Corollary 5 (the product formula for every space).** Let H be a connected cubic signed system that is not colourable.
  - Every brace B of B(H), with any Pfaffian signing, is not colourable and has one positive amplitude a(B).
  - A(H, L) = Π_B a(B) for every line L.
  - On every three-fold odd gadget with distinct corner triangles, the knot's exactness factor is λ(0) = (−1)^(n−1) Π_B a(B), whatever the
    corner line.
- **Corollary 6 (Tutte matchings).** For a planar brace, the number of Tutte matchings of its trinity with outer triangle t is the same for
  every triangle t, white or black.

## Nearest known result

- **Valiant's Holant theorem** (holographic transformations preserve Holant values).
  - Lemma 2(a) is an instance: the edge weight e^{±iπss′/6} turns the equality constraint at a vertex into √3 times not-all-equal on its
    neighbours.
  - Folklore risk for (a) is moderate to high.
- **Seymour (1974).** A minimal non-2-colourable hypergraph has at least as many edges as vertices, by linear algebra. Lemma 4 is its signed,
  cubic form. `THREEFOLD-SPACES-20261030-001A` Theorem 1 is the unsigned case.
- **Tutte (1948).** The independence of the outer triangle in Corollary 6 also follows from Tutte's tree-trinity theorem. The proof here is
  different.
- **What is new here** (no overlap found in one search, candidate local delta):
  - the inserted count (b);
  - Theorem 3;
  - the product formula for every non-colourable cubic system.

## Proof of Lemma 1

- e^{iπ/6} + e^{−iπ/6} = 2cos(π/6) = √3, and e^{iπ/2} + e^{−iπ/2} = 0.
- Σ_s s e^{iπsm/6} = 2i sin(πm/6), with sin(±π/6) = ±1/2 and sin(±π/2) = ±1. ∎

## Proof of Lemma 2

**The weight.** Spins live on all points and lines: s ∈ {±1}^V. Put

Ω(s) = Π_{e=(w,p)} exp((iπ/6) τ_e s_w s_p).

- For a line w, m_w(s) = Σ_{e∋w} τ_e s_p is the sum of its seen values. It is proper iff |m_w| = 1.
- For a point p, M_p(s) = Σ_{e∋p} τ_e s_w. It is proper in Hᵀ iff |M_p| = 1.

**(a)** Sum Σ_s Ω(s) over the line spins first. Line w contributes Σ_{s_w} e^{(iπ/6)s_w m_w} = √3 · [w proper] (Lemma 1), so the sum is
(√3)^n #col(H). Summing over the point spins first gives (√3)^n #col(Hᵀ).

**(b)** Count Q_L = Σ_s s_L m_L(s) Ω(s) in both orders.
- **Lines first.**
  - Line L contributes m_L Σ_{s_L} s_L e^{(iπ/6)s_L m_L}: i if L is proper, 6i if not (Lemma 1).
  - Every other line contributes √3 · [proper].
  - So Q_L = i(√3)^(n−1) (#col(H) + 6 N_H(L)).
- **Points first.** s_L m_L = Σ_{e=(L,p)} τ_e s_L s_p. In the term of the incidence e = (L, p):
  - the spin s_p contributes Σ_{s_p} s_p e^{(iπ/6)s_p M_p} = 2i sin(πM_p/6);
  - every other point q contributes √3 · [q proper in Hᵀ];
  - with u_e = τ_e s_L, the term is i(√3)^(n−1) Σ_y 2u_e sin(πM_p/6), over line colourings y in which every point other than p is proper.
  - **If p is improper**, its three seen values equal some ε. Then M_p = 3ε and u_e = ε, so 2u_e sin(πM_p/6) = 2. These y are counted by
    N_{Hᵀ}(p).
  - **If p is proper**, y ∈ col(Hᵀ). Then M_p = ±1 is the majority value and 2 sin(πM_p/6) = M_p, so u_e M_p = ε_e(y).
  - So the term is i(√3)^(n−1) (2 N_{Hᵀ}(p) + Σ_{y∈col(Hᵀ)} ε_e(y)).
- **Equating.** Summing the terms over the three incidences of L and equating the two orders gives (b). ∎

## Proof of Theorem 3

- **The two identities.** By Lemma 2(a), Hᵀ is not colourable either.
  - So #col(H) = 0, R(L) = 0, N_H(L) = 2A(H, L) and N_{Hᵀ}(p) = 2A(Hᵀ, p). Lemma 2(b) becomes

    3A(H, L) = Σ_p M_{Lp} A(Hᵀ, p).

  - Applied to Hᵀ, whose transpose is H, it becomes

    3A(Hᵀ, p) = Σ_L M_{Lp} A(H, L).
- **Averages.** Each line and each point has three incidences. So A(H, L) is the average of A(Hᵀ, ·) over the incidences of L, and A(Hᵀ, p)
  is the average of A(H, ·) over the incidences of p.
- **Maximum principle.**
  - Let α be the largest of all these numbers, attained at a vertex v of the incidence graph B(H).
  - An average equals α only if every averaged value is α, so every neighbour of v attains α.
  - B(H) is connected, so every value is α. ∎

## Proof of Lemma 4

**Signed incidence matrices.**
- S has rows for lines, columns for points, and entry Σ τ_e over the incidences of a cell. Repeated incidences have equal signs, so a
  cell's entry has a single sign.
- A *positive weighting* replaces each τ_e by a positive multiple, giving a matrix with the sign pattern of S.
- The signing is Pfaffian iff the nonzero terms of det S have one sign and there is at least one. That holds iff every positive weighting
  is nonsingular:
  - **If all terms share a sign,** a positive weighting has the same nonzero terms with the same signs, so its determinant is nonzero.
  - **If two terms, of permutations π₊ and π₋, have opposite signs,** scaling the cells of π₊ by a large λ makes the determinant take π₊'s
    sign: every other permutation uses at most n − 1 of those cells. Scaling π₋'s cells gives π₋'s sign instead. The positive weightings form
    a connected set, so by continuity one of them is singular.

**(i)** Suppose a colouring s colours H.
- On each line, two seen values agree and one is odd. Weight the odd incidence 2 and the others 1. Every line's weighted sum of seen values
  is then 0.
- This positive weighting S_w satisfies S_w s = 0 with s ≠ 0, so it is singular, and the signing is not Pfaffian.

**(ii)** Let H′ be a non-colourable subsystem (a set of lines of H, with their points) with as few lines as possible. Suppose a positive
weighting of its matrix has S′y = 0 with y ≠ 0.
- **The support.** Give each point with y_p ≠ 0 the spin sgn(y_p).
  - A line of H′ meeting the support has weighted terms τ_e y_p summing to 0 with one of them nonzero. So two of its incidences have opposite
    signs of τ_e y_p, i.e. different seen values. It is proper.
- **The rest.**
  - Some line meets the support, since every point of H′ lies on a line of H′. So the lines inside {y = 0} form a smaller subsystem, which is
    colourable by minimality.
  - Colour the remaining points of {y = 0} arbitrarily.
- **The contradiction.** Now H′ is coloured, which is impossible. So the columns of S′ are independent, and |points(H′)| ≤ |lines(H′)|.
- **Counting incidences.** It gives 3|lines(H′)| ≤ 3|points(H′)|.
  - So equality holds, and every incidence of every point of H′ lies on a line of H′.
  - H′ is therefore a union of connected components, and H′ = H.
- **Minimality.** So H is minimally not colourable: H − L is colourable for every L.
- **Pfaffian.** Running the argument again on H itself, with any positive weighting, shows every positive weighting is nonsingular. So the
  signing is Pfaffian. ∎

## Proof of Corollary 5

- **Pfaffian.** By Lemma 4(ii), H's signing is Pfaffian.
- **Peeling.** Peel the decomposition tree as in ticket A's Theorem 6. At each step the leaf piece B has a Pfaffian signing (ticket A,
  Theorem 4). Then:
  - B is not colourable (Lemma 4(i));
  - B is connected and cubic;
  - B has one amplitude a(B) (Theorem 3), which is positive (Lemma 4(ii)).
- **One step.** Ticket A's Theorem 4 then contributes the factor a(B), and leaves a Pfaffian, non-colourable system with one brace fewer.
- **The signing does not matter.** a(B) is the same for every Pfaffian signing of B: they form one switching class, and switching preserves
  amplitudes (ticket A, Lemma 1).
- **The knot.** The formula for λ(0) is ticket A's Theorem 2. ∎

## Proof of Corollary 6

- **White outer triangles.** Ticket A's Proposition 5 gives A(P, L) = |M_T(L)| for a planar brace P with a Kasteleyn signing, where lines are
  the white triangles of the trinity.
- **Black outer triangles.** The transpose Pᵀ is the same plane graph with its colour classes exchanged. The face condition does not depend
  on which class is called points, so the same argument gives A(Pᵀ, p) = |M_T(p)|, the Tutte matchings with the black outer triangle p.
- **One value.** Theorem 3 makes all these numbers equal. ∎

## What the computation checks

`check.py` (about fifteen seconds):
- **Lemma 1** in exact arithmetic.
- **Lemma 2** by brute force on 400 random signed cubic systems with up to 7 points:
  - 258 colourable, 142 not;
  - most have repeated incidences.
- **The weighted sums** in both orders, in exact cyclotomic arithmetic: on the Fano plane, a doubled square and ten random systems.
- **Theorem 3** on fourteen systems, at every line and at every point of the transpose:
  - spaces from 7 to 43 points;
  - cores with repeated and twisted incidences;
  - four trisums of prisms, with amplitudes 13, 14, 29 and 36.
- **Lemma 4** on 233 random connected signed systems, comparing colourability with sign-nonsingularity (an exact permanent and determinant)
  and checking minimality.
- **Corollary 5** with the law: on two spaces whose glue is a non-planar trisum of prisms, with 62 and 90 points, λ(0) from the knot's corner
  relation equals (−1)^(n−1) times the product of brace amplitudes (−9·5⁸ and −14·5¹²).
- **Corollary 6** on the cube, the hexagonal prism and the truncated octahedron.
- **Controls:**
  - a colourable system has counts 8, 11 and 13 at different lines;
  - there the correction terms are nonzero and the identity still holds;
  - a disconnected non-colourable system has two amplitudes;
  - at the knot's own angle π/3, summing out a vertex gives 1 and −2, not a constraint.

## Reading

- **The amplitude belongs to the whole space.** The knot's exactness factor does not depend on where a three-fold space is opened. Reading the
  space from its points instead of its lines does not change it either.
- **Why.** At half the knot's angle, the incidence graph carries a weight that becomes not-all-equal whichever side is summed out.
  - Counting one marked contact in both orders makes each line's amplitude the average of its points' amplitudes, and each point's the
    average of its lines'.
  - On a connected space, a function equal to the average of its neighbours is constant.
- **The open part of ticket A** is now only the value a(B) of a non-planar brace. Ticket B finds that it depends on how a trisum is glued,
  not only on its pieces' amplitudes.
- **For the owner's relational view.** No contact is privileged: the number is a property of the whole relation. The two readings of the
  space, triangles first or contacts first, agree.

## Nonclaims

- **No closed form** is given for a(B) on non-planar braces other than the trisum of three cubes.
- **A counting device.** The complex weight is used only to count. It is not a physical model.
- **Lemma 2(a)** is likely an instance of known holographic identities.
