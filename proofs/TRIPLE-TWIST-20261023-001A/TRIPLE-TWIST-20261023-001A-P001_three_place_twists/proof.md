# Twisted three-place worlds: when a twist is defined, hidden, frozen or forced to wind

Status: Proved

Ticket `TRIPLE-TWIST-20261023-001A`, 2026-10-23.

**What it uses:**
- from `CONTACT-CENSUS-20261022-001A-P001`: fair contacts with a visible bit, and pair-worlds;
- from `BASE-THREE-20261021-001A-P001`: frozen, forcing and choice regimes, and the transmission rule;
- from `ODD-LOOP-20261023-001B-P001`: twists as cocycles and gauges.

## Standard statement

**Setting.**
- **The complex.** X is a triangulated surface (a closed one, such as a triangular torus, or a planar patch) with hidden bits h_v at
  its vertices. Each triangle T has an ordered list of corners (a_T, b_T, c_T) and a fair visible bit x_T.
- **The contact.** A fair contact is a pair of relations R₀, R₁ ⊆ {0, 1}³. Triangle T requires its corner values to lie in R_{x_T}.
- **Twists.** A twist is a mod-2 cocycle t on the edges. Its gauge on T is g_T(v) = t(a_T v), and T requires (h_v + g_T(v)) ∈ R_{x_T}.
- **Complement-closed contacts.** The contact is complement-closed when R₁ = R̄₀, where R̄ = {p + 111 : p ∈ R} flips all three
  places, or when both relations are self-complementary.
- **The world.** W(t) is the resulting random constraint system.

**Lemma 1 (when a twist is a class).**
- **(a) Closed contacts.** If the contact is complement-closed, then for every vertex set S the world W(t + δ1_S) with x is the world
  W(t) with x flipped on the triangles whose first corner lies in S, after relabelling h by 1_S. Changing a triangle's first corner
  is likewise a flip of x.
  - **Hence** the law of W(t), and of every event invariant under relabelling, depends only on the class [t] ∈ H¹(X; ℤ₂).
- **(b) The converse.** On a single triangle, moving the twist by the coboundary of the first corner preserves the law of the
  relabelled solution set only for complement-closed contacts.
- **(c) What fails otherwise.** For other contacts a contractible seam is a physical defect: for "x or 1-in-3" it creates
  contradictions on planar patches that have none without it.

**Lemma 2 (independent polarities hide every twist).** Suppose each triangle draws independent uniform polarities σ_T ∈ {0, 1}³ and
requires (h + σ_T) ∈ R_{x_T}. Then W(t) has the same law for every cocycle t, since σ_T ↦ σ_T + g_T preserves the uniform law.

**Lemma 3 (two hidden places give pair-worlds).** A contact with a visible bit and two hidden places leaves, once the bit is fixed, a
relation on two bits. Every such relation is defined by clauses of two literals (it is closed under majority), so the hidden world is
a two-literal world.

**Proposition 4 (the monotone world).** Take the contact from not-all-equal on four places with one visible bit: R₀ forbids 000 and R₁
forbids 111.
- **The universal satisfier.** On a closed triangulated surface, W(t) is satisfiable for every x whenever a twisted not-all-equal
  colouring exists: an h with no triangle whose gauged values are all equal.
- **When one exists.** Such h exist exactly when the cubic dual graph has a 2-factor whose mod-2 homology class is dual to [t].
- **On triangular tori.** They exist in 220 of the 224 (shape, twist) pairs of the triangular tori with sides 2 to 5 and every shear.
  - **The exceptions.** The four without one are the two-row tori with shear 1, in one twist each. These are not simplicial: vertex
    pairs are joined by several edges.
  - **The world is still frozen there.** Enumerating every x shows that the monotone world never contradicts on them either.
  - **So** it never contradicts on any of these tori: it is frozen in every twist, by a universal satisfier except in the four
    exceptional cases.

**Theorem 5 (a tiling forces contradictions to wind).** Let the contact be complement-closed, U = R₀ ∩ R₁ the doubly allowed patterns,
and suppose the triangular lattice of the plane has an assignment with every triangle's pattern in U (a U-tiling). Then:
- **(a) No planar contradiction.** Every planar patch is satisfiable for every x.
- **(b) Fitting twists.** On a torus, every twist in which a doubly allowed assignment exists is satisfiable for every x.
- **(c) Contradictions wind.** On a torus in any twist, every minimal contradicting set of triangles has a support whose period lattice
  (the image of its cycles in H₁) is nonzero.
- **(d) Contradictions wind where the twist is odd.** If W is that lattice and q_f is any fitting twist of the torus, the class q − q_f
  is not zero on W. In particular, a contradiction whose lattice is ℤc runs along a class c with (q − q_f)(c) odd.

**Corollary 6 (where the twist decides contradiction).** For complement-closed contacts with a U-tiling:
- **The twists split.** On each torus they fall into fitting twists, which never contradict, and the rest.
- **Every contradiction is global and winds.** A contradiction is a line (period lattice of rank 1) or a cross (rank 2).
- **Lines run along odd classes.** A line runs along a class on which the twist, measured from every fitting twist, is odd. This is
  how contradiction loops of the two-literal side run along classes where the twist is odd.
- **The lone-contradiction event.** "The world contradicts, and its minimal contradicting sets wind along one class c" is therefore
  well defined. It is the three-place analogue of the line events of the two-literal side.

## Nearest known result

- **Lemmas 1–3.** They are elementary.
  - **Lemma 2** is the familiar fact that uniformly random literal signs make a random formula gauge-invariant.
  - **Lemma 3** is the classical fact that relations on two bits are bijunctive.
  - **Folklore risk:** high for the facts, low for the use in the program.
- **Proposition 4.** It combines the correspondence between not-all-equal colourings of a triangulation and 2-factors of its dual
  with Poincaré duality.
  - **Untwisted case:** classical. It is the dual form of Petersen-type statements for cubic graphs.
  - **Twisted reading:** new to the program.
  - **Folklore risk:** moderate.
- **Theorem 5.** It is a lifting argument, which is standard. The statement about fair three-place contacts is new to the program.
  - **The literature.** No search was run in this epic.
  - **Folklore risk:** moderate. Frustration-free tilings with global obstructions are a common theme in tiling and spin-model
    studies.

## Proof

### Lemma 1

**(a) Closed contacts.**
- **Relabel.** Substitute h = h′ + 1_S in W(t). On a triangle T the gauged values become h′_v + g′_T(v) + 1_S(a_T), where
  g′_T(v) = g_T(v) + 1_S(v) + 1_S(a_T) is the gauge of t + δ1_S.
- **The constraint.** So the constraint reads (h′ + g′_T) + 1_S(a_T)·111 ∈ R_{x_T}. Equivalently, (h′ + g′_T) lies in R_{x_T}
  when a_T ∉ S, and in its complement when a_T ∈ S.
- **Complement closure.** It turns the complement of R_x into R_{1−x}. So this is W(t + δ1_S) with x_T flipped on the triangles
  whose first corner lies in S.
- **The law.** The flip is a bijection of fair x, so the law is unchanged.
- **Changing the first corner.** It changes every gauge on the triangle by the same bit, which is again a complement, hence a flip of x.

**(b) The converse.** On one triangle with S = {a}:
- **The relabelled solution sets.** After relabelling they are R̄₀ and R̄₁.
- **Equality of laws.** The law equals that of {R₀, R₁} under fair x exactly when {R̄₀, R̄₁} = {R₀, R₁}, that is, when the contact
  is complement-closed.

**(c) A defect.** The check exhibits a contractible seam on a planar patch for "x or 1-in-3", which creates contradictions. ∎

### Lemmas 2 and 3

- **Lemma 2.** On triangle T, (h + g_T + σ_T) ∈ R_x is the untwisted constraint with polarity σ_T + g_T. The map σ ↦ σ + g is a
  bijection of independent uniform polarities.
- **Lemma 3.** A relation on two bits contains, with any three of its points, their majority: the coordinatewise majority of three
  points of {0, 1}² is one of them. Relations closed under majority are exactly those defined by clauses of two literals. ∎

### Proposition 4

- **The cocycle d.** For an assignment h put d = t + δh. It is a cocycle in the class [t], and a triangle has gauged values all equal
  exactly when d vanishes on its three sides.
- **Two sides per triangle.** A cocycle has an even number of ones on each triangle, 0 or 2. So h is a twisted not-all-equal colouring
  exactly when d has two ones on every triangle.
- **The dual 2-factor.** That holds exactly when the dual edges crossing the support of d form a 2-regular spanning subgraph of the
  dual, a 2-factor. Its homology class is dual to [d] = [t].
- **The converse.** A 2-factor in the class dual to [t] gives a cocycle d with two ones on every triangle and [d] = [t], so
  d − t = δh for some h.
- **Every x is satisfied.** A colouring satisfies both R₀ and R₁ on every triangle. ∎

### Theorem 5

- **(a) No planar contradiction.** A planar patch carries no nontrivial twist: every cocycle there is a coboundary, removable by
  Lemma 1. The U-tiling restricted to the patch puts a pattern of U ⊆ R₀ ∩ R₁ on every triangle, so it satisfies every triangle for
  either value of x.
- **(b) Fitting twists.** This is immediate.
- **(c) Contradictions wind.** Let K be a minimal contradicting set with support S, and suppose its period lattice is 0.
  - **S lifts to the plane.** Every closed walk of S is null-homologous in the torus. The fundamental group of the torus is abelian,
    so S lifts to the universal cover, the plane.
  - **The twist is removable on S.** The twist's value on every cycle of S is its value on a null class, 0. So t restricted to S is a
    coboundary δ1_A, and Lemma 1 turns K into untwisted constraints on the lifted copy of S (each R₀ or R₁).
  - **Contradiction.** The U-tiling satisfies all of them, so K is satisfiable, a contradiction.
- **(d) Contradictions wind where the twist is odd.** Let q_f be a fitting twist, with a doubly allowed assignment u, and suppose
  q − q_f vanishes on W.
  - **The twists agree on S up to a gauge.** Every cycle of S has its class in W, so the cocycles of q and q_f differ on S by a
    coboundary δ1_A.
  - **Regauge.** By Lemma 1, K in twist q is equisatisfiable with K in twist q_f, with x flipped on some triangles.
  - **Contradiction.** In twist q_f, u puts a pattern of U on every triangle of K, so it satisfies K for every x. ∎

## Interpretation (not theorem)

- **A twist needs complement-closed contacts.** For a twist to be a sector rather than a defect, the contact must not care which way
  all its places are read. That is the three-place form of the two-literal fact that an implication reversed is an implication.
- **Three regimes, as in the base map.**
  - **Frozen (the monotone world).** There is always a universal satisfier, and the twist only changes how many there are.
  - **Locally frustrated.** Contradictions appear in small planar patches, so the twist hardly matters.
  - **The third regime.** The doubly allowed patterns tile the plane but do not close on the torus in every twist. There the twist
    decides whether the world can contradict at all, and every contradiction runs around the torus.
- **The analogue of the two-literal loops.** These winding contradictions are what can carry the two-literal story (shielding, walls,
  dual pairs) over to three places. Whether they do is the question for the next step.

## Check

`check.py` (standard library, with a small solver by unit propagation and branching):
- **Lemma 1.** On 240 random instances (random complement-closed placements, tori, twists and seams), the two worlds are
  equisatisfiable, both under the seam move and under the change of first corner. The converse is checked over all 65,536 contact
  pairs.
- **Lemma 2.** It is checked on 120 instances.
- **Lemma 3.** It is checked over all 16 relations on two bits.
- **Proposition 4.** On the 3 × 3 and 4 × 4 tori in every twist, every twisted not-all-equal colouring found has two sides with d = 1
  on every triangle and the class of d equal to the twist. On every triangular torus with sides 2 to 5 and every shear, colourings
  exist in 220 of 224 (shape, twist) pairs. On the other four every x is enumerated, and none contradicts.
- **Theorem 5.** For every complement-closed placement with a doubly allowed assignment on the 3 × 3 or 4 × 4 torus:
  - radius-3 patches never contradict;
  - fitting twists never contradict;
  - every minimal contradicting set found winds, along a lattice on which the twist differs from every fitting twist.
- **Controls (each rejected):**
  - placements without a doubly allowed assignment do contradict on planar patches;
  - a contractible seam creates contradictions for "x or 1-in-3".

## Scope

- **Exact results.** Lemmas 1–3, Proposition 4 and Theorem 5 are exact.
- **Computed observations.** The frozenness of the monotone world is checked on small tori, not proved for all of them.

## Correction recorded during the proof

- **The first version was wrong.** It said that twisted not-all-equal colourings exist in every twist of every triangular torus up to
  5 × 5. Scoping had tried 20 shapes, none with two rows and shear 1.
- **How it was caught.** The check found four exceptions, the two-row tori with shear 1.
- **What survives.** Enumerating every x there shows the monotone world still never contradicts, so frozenness survives on these
  tori. In those four cases it rests on the fair bits, not on a universal satisfier.
- **Not claimed.** Nothing is claimed about walls, shielding or dual pairs for winding contradictions.
- **Not claimed.** No space or physics is claimed.
