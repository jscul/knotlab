# The knot's junction is a similitude: unbranched twists count in polynomial time

Status: Proved

Ticket `TWIST-COUNT-20261030-001A`, 2026-10-30.

**What it uses:**
- **`SEYMOUR-COUNT-20261030-001A`:**
  - Lemma 1(i): with odd square parity, exactly one square line sees c0 = c2;
  - Lemma 2: the support lemma, the boundary of a closed non-colourable piece;
  - Proposition 4: the view from c3 is the swapped split.
- **`SEYMOUR-COUNT-20261030-001B`:**
  - Lemma 1: the trisum tree. Squares are disjoint trisectors, leaves planar braces, squares faces of their leaves.
  - Lemma 2: one Pfaffian sign pattern per square, glued Kasteleyn signings.
  - The splitting code.
- **`THREEFOLD-AMPLITUDE-20261030-001A`, Lemma 1:** Pfaffian signings of a matching covered bipartite graph form one switching class.
- **`THREEFOLD-AMPLITUDE-20261030-001C` and `THREEFOLD-SPINSUM-20261030-001A`:** the Ising (even-subgraph) form of the count without signs.
  Lemma 1 below is its signed form.
- **External, not replayed:**
  - **Valiant's matchgates and holographic algorithms.** A planar matchgate network with its external nodes on the outer face has a
    signature satisfying the matchgate identities (MGI).
  - **Cai–Gorenstein (2014):** every signature satisfying the parity condition and the MGIs is realized by a planar matchgate.
  - **FKT (Kasteleyn, Temperley–Fisher):** the perfect matching polynomial of a planar weighted graph is a Pfaffian.
  - **Signatures of arity at most 3:** every even signature of arity at most 3 is a matchgate signature (no identity beyond parity).

## Why this ticket exists

The owner approved asking what happens one twist off Seymour's bound. Keep a three-fold space's incidence graph and change its signs away
from the knot's own class. The system becomes colourable. Is counting still easy?

A probe found that the polynomial algorithm's mechanism survives a twist exactly as long as no trisum square sees twists on all three of its
sides. This ticket proves it.

## Standard statement

**Setting.**
- **Signed graphs.** B is a connected cubic bipartite graph with n points and n lines, and a *signing* σ is a set of its edges.
  - #col(B, σ) counts the point colourings in which every line sees (colour ⊕ sign) not all equal.
  - B is *Pfaffian* when some signing κ makes it non-colourable (`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4). The incidence graph of a
    three-fold space is Pfaffian, with κ the empty signing.
  - The *twist* of σ is σ ⊕ κ up to cuts. σ lies in the knot's class iff σ ⊕ κ is a cut.
- **The Hadamard basis.** H = [[1, 1], [1, −1]] is applied on every edge (the y-basis), and Ĥ F = H^{⊗4} F.
- **Trisum trees** (`SEYMOUR-COUNT-20261030-001B`). For a cubic Pfaffian brace T that is neither planar nor the Heawood graph:
  - leaves are planar braces, and squares are disjoint trisectors (c0, c1, c2, c3);
  - leaves and squares form a tree, and each square has three *branches*, the components of the tree minus it;
  - a branch's *own edges* are the edges of T in its leaves.
- **Branch tensors.** F_{S,b}(z0, z1, z2, z3) counts the colourings of branch b's own points that make its own lines proper.
  - z0 and z2 are the colours of c0 and c2; z1 and z3 are those of the neighbours of c1 and c3 in b.
  - The signs of c1's and c3's incidences belong to the junction.
- **The junction** at S, seen from branch h with closed branches Q and R and incidence signs s1 = (s1h, s1q, s1r) at c1 and s3 at c3, is

  W(x0, z1, x2, z3) = Σ F_Q(x0, q1, x2, q3) F_R(x0, r1, x2, r3) · NAE(z1 ⊕ s1h, q1 ⊕ s1q, r1 ⊕ s1r) · NAE(z3 ⊕ s3h, q3 ⊕ s3q, r3 ⊕ s3r),

  summed over q1, q3, r1, r3.
- **The matchgate identity.** For a 4-ary f with legs in the cyclic order c0, c1, c2, c3:

  MGI(f) = f0000 f1111 − f1100 f0011 + f1010 f0101 − f1001 f0110.

  An even 4-ary f (supported on even weights) is a matchgate signature iff MGI(f) = 0.
- **Twisted branches.** Branch b at S is *twisted* when σ ⊕ κ restricted to its own edges is not a cut of the graph they form.
- **The split form.** For α, β, an odd pattern τ = (t10, t12, t30, t32) and leg signs s1, s3, let v1 = z1 ⊕ s1 and v3 = z3 ⊕ s3. Then
  F(x0, z1, x2, z3) is:
  - if x0 ⊕ t10 = x2 ⊕ t12: [v1 = x0 ⊕ t10] · (α[v3 = x0 ⊕ t30] + β[v3 = x2 ⊕ t32]);
  - otherwise: [v3 = x0 ⊕ t30] · (β[v1 = x0 ⊕ t10] + α[v1 = x2 ⊕ t12]).

**Results.**
- **Lemma 1 (the Hadamard form).**
  - (i) For every signing, #col(B, σ) = (3/2)^n Σ_χ (−1/3)^{|χ|/2} (−1)^{|σ ∩ χ|}, summed over even subgraphs χ. In the y-basis, points
    carry EVEN3 = [1, 0, 1, 0], lines (1/4)[3, 0, −1, 0], and negated edges Z = diag(1, −1).
  - (ii) Flipping one incidence (L, p) of a non-colourable signed system H gives #col = #col(H − L) = 2A(H, L).
- **Lemma 2 (branch tensors).**
  - (i) Every Ĥ F_{S,b} is even.
  - (ii) If the branch is a single leaf, Ĥ F_{S,b} is a matchgate signature in the cyclic order of the square, whatever the signing.
- **Lemma 3 (untwisted branches).**
  - (i) Branch b at S is untwisted iff some pattern on S's edges completes σ on G_{S,b} to a Pfaffian signing.
  - (ii) Then F_{S,b} has the split form, with the split (α, β) of G_{S,b} under that completion. Every split form is an even matchgate
    signature in the y-basis.
  - (iii) A branch that contains a twisted branch is twisted.
- **Theorem 4 (the junction is a similitude).** Let Q be untwisted, with split (α, β). Then for every R,

  MGI(Ĥ W) = (−1)^{s1h + s3h + s1r + s3r} (α² + αβ + β²) MGI(Ĥ F_R).

  - The factor α² + αβ + β² = |α + β e^{iπ/3}|² is positive, so W is a matchgate signature iff F_R is.
  - e^{iπ/3} is the knot's exactness angle.
- **Lemma 5 (a good root).** If no square has all three branches twisted, some leaf r sees at most one twisted branch among the two closed
  branches of every square. If some square has three twisted branches, no leaf does.
- **Theorem 6 (unbranched twists count in polynomial time).** Let T be a cubic Pfaffian brace and σ a signing in which no square of the
  trisum tree has three twisted branches. Then #col(T, σ) is computable in polynomial time.
  - From a good root every junction is a matchgate signature. Each leaf is then a planar matchgate computation (FKT).
  - The same holds for any connected cubic bipartite Pfaffian graph, through its tight cuts, whose three-edge gadgets are always matchgates.
- **Proposition 7 (branched junctions leave the class).** Junctions of two twisted pages can violate the matchgate identity.
  - Examples: cube and 6-prism pages, including *exclusive crossings*: zero turning entries, zero double entry, and MGI ≠ 0.
  - For generic matchgate pages, MGI(Ĥ W) is not identically zero.

## Nearest known result

- **Valiant's holographic algorithms.** They count planar not-all-equal instances: #PL-3-NAE-SAT, and here every planar leaf. The
  matchgate identities and their sufficiency are due to Valiant and Cai–Gorenstein.
- **`SEYMOUR-COUNT-20261030-001`** counts the knot's own class by Berman determinants. Theorem 6 reaches every unbranched twist by
  matchgates.
- **What is new here** (no overlap found, candidate local delta):
  - the junction as a similitude of the matchgate quadric, with the Eisenstein norm of the split as multiplier;
  - the unbranched-twist criterion and its tractability.

## Proof of Lemma 1

**(i)** Insert H H⁻¹ = I on every edge, with H⁻¹ = H/2.
- **Points.** A point's equality on three edges becomes (=3) H^{⊗3} = [2, 0, 2, 0].
- **Lines.** A line's NAE3 = (1, 1)^{⊗3} − e0^{⊗3} − e1^{⊗3} becomes (H/2)^{⊗3} NAE3 = (1/8)(8 e0^{⊗3} − [1, 1, 1, 1] − [1, −1, 1, −1])
  = (1/4)[3, 0, −1, 0].
- **Negations.** A negated incidence is X on its edge, and (H/2) X H = Z.
- **The sum.** Only even edge sets χ contribute. Each point gives 2, and each line gives 3/4 off χ and −1/4 on it. A cycle through m lines
  has length 2m, so the sum is 2^n 4^{−n} Σ_χ 3^{n−|χ|/2} (−1)^{|χ|/2} (−1)^{|σ∩χ|}.

**(ii)**
- Flipping (L, p) changes only what L sees.
- A colouring of H − L makes L constant as seen in H (H is not colourable), so the flipped L sees one value changed: it is proper.
- Conversely, a colouring proper in the flipped system is a colouring of H − L, unless L is not-all-equal in H too. That would colour H. ∎

## Proof of Lemma 2

**(i) Evenness.** F is invariant under complementing all colours, since NAE and equality are. Complementing all four arguments multiplies the
y-coefficient by (−1)^{|y|}, so odd entries vanish.

**(ii) Planar leaves.** In the y-basis the leaf is a planar network of EVEN3, (1/4)[3, 0, −1, 0] and Z.
- These are matchgate signatures: even of arity at most 3.
- The legs leave the square's face in cyclic order on its boundary.
- A planar matchgate network with its external nodes in order on one face has a matchgate signature (Valiant). ∎

## Proof of Lemma 3

**(i)** Let K′ = G_{S,b} − E(S).
- κ restricted to K′, with the pattern τ_S, is Pfaffian on G_{S,b} (`SEYMOUR-COUNT-20261030-001B`, Lemma 2), and Pfaffian signings of
  G_{S,b} form one switching class.
- So σ on K′ has a Pfaffian completion iff σ and κ differ on K′ by a switching. That holds iff σ ⊕ κ is a cut of K′.
- No cycle of K′ passes through a square vertex, which has degree 1 there, so only the own edges of b matter.

**(ii)** Under the completion, G_{S,b} is a piece with an odd square pattern.
- The support lemma (`SEYMOUR-COUNT-20261030-001A`, Lemma 2) with Proposition 4 gives the split form.
- That a split form is even with MGI(Ĥ F) = 0, for every pattern, every leg sign and symbolic α, β, is a finite polynomial computation
  (check, section 3).

**(iii)** A cut of a graph restricts to a cut of every subgraph. The own edges of a sub-branch are own edges of the larger branch. ∎

## Proof of Theorem 4

- **Linearity.** W is linear in F_R. MGI is a quadratic form, so MGI(Ĥ W) is a quadratic form in F_R, with coefficients polynomial in α
  and β.
- **The identity with zero signs on the host and on R.** For each of the 8 odd patterns τ and the 4 signs of Q's own legs, the identity
  MGI(Ĥ W) = (α² + αβ + β²) MGI(Ĥ F_R) holds with F_R generic (8 free even y-entries). Exact symbolic computation verifies it (check,
  section 3).
- **Signs on R or on the host.**
  - A sign on R's incidence at c1 is the substitution r1 ↦ r1 ⊕ 1 in F_R, which is X on R's leg. In the y-basis it is Z on that leg, and
    Z on one leg changes the sign of MGI.
  - A sign on the host's incidence is X on W's leg, likewise. Signs on Q's incidences are Q's leg signs, already covered.
  - Random checks on all 64 sign choices confirm the sign rule (check, section 3).
- **Positivity.** α² + αβ + β² = (α + β/2)² + 3β²/4 > 0 unless α = β = 0, which a piece's split never is. ∎

## Proof of Lemma 5

- **The doubly twisted squares.** Let D be the set of squares with exactly two twisted branches, and u(S) the untwisted branch of S ∈ D.
- **u(S) contains no square of D.** If S′ ∈ D lay in u(S), one of S′'s twisted branches would avoid S, hence lie inside u(S). By Lemma 3(iii)
  u(S) would then be twisted.
- **The root.** If D is empty, any leaf will do. Otherwise take S ∈ D, a twisted branch b of S, and r the leaf of b at S.
  - r is not in u(S).
  - For S′ ≠ S in D, u(S′) is a component of the tree minus S′. If it contained r, it would contain the adjacent square S ∈ D, which is
    impossible.
- **Why r works.** At every S ∈ D, the closed branches are u(S) and one twisted branch. At a square with at most one twisted branch, any
  root works.
- **The converse.** If a square has three twisted branches, both of its closed branches are twisted, whatever the root. ∎

## Proof of Theorem 6

**The algorithm.**
1. Compute κ by gluing Kasteleyn signings over the tree (`SEYMOUR-COUNT-20261030-001B`, Lemma 2).
2. Decide which branches are twisted by cut tests, and find a good root r (Lemma 5). This takes polynomial time.
3. Process branches away from r. Let a closed branch with leaf ℓ at its square have child squares D.

**At each child square D.**
- At most one of D's two closed branches is twisted.
- An untwisted branch has the split form (Lemma 3(ii)). Its split is a split in the knot's class (Lemma 3(i), switching), computed by
  `SEYMOUR-COUNT-20261030-001B`.
- A twisted branch's tensor is, by induction, the external signature of a planar matchgate network. It is therefore a matchgate signature
  (Valiant), computed by FKT with each of its 8 even boundary patterns fixed.
- By Theorem 4 the junction at D is then a matchgate signature in the cyclic order of D's face. If both closed branches are untwisted, the
  split form is itself a matchgate (Lemma 3(ii)).

**The leaf computation.**
- ℓ in the y-basis, with each child junction placed in its face, is a planar network of matchgate signatures.
- Cai–Gorenstein realizes each by a planar matchgate of constant size, so its value with given external legs is one FKT Pfaffian.
- At r there are no external legs, and the value is #col(T, σ) up to the normalizations of Lemma 1. There are fewer than n leaves.

**General Pfaffian graphs.**
- A tight cut contributes a three-leg gadget, even (Lemma 2(i)) and hence a matchgate at arity 3.
- A Heawood brace has constant size and is summed directly.
- Branches are then taken in the whole graph. ∎

## Proof of Proposition 7

- **Exhaustive pairs (check, section 4).**
  - Among all pairs of sign classes of cube and 6-prism pages (three sign choices each), junctions of two twisted pages violate the identity
    in 18 + 144 + 468 cases.
  - 56 of these are exclusive crossings.
  - With one untwisted page, no junction violates it, as Theorem 4 requires.
- **Generic pages.** With both pages parametrized as generic even matchgates by their Pfaffian minors, MGI(Ĥ W) is a nonzero polynomial,
  with 72 terms. ∎

## What the computation checks

`check.py` (a few seconds):
- **1, the Hadamard form.** The cube, the 6-prism and the trisum of three cubes, eight random signings each, all even subgraphs.
  - One flip: every incidence of two non-colourable systems.
- **2, pages.** Every sign class of the cube, the 6- and 8-prisms, the truncated octahedron and Omni(K₂,₃) pages: 8, 32, 128, 2048 and 2048
  classes.
  - All are even with MGI = 0.
  - Untwisted (the cut test against a Kasteleyn signing) coincides exactly with the split form.
- **3, the similitude.**
  - The identity holds symbolically for all 8 patterns and 4 leg signs.
  - Split forms are even matchgates.
  - The sign rule holds on all 64 sign choices with random integers.
- **4, branched junctions.** As in Proposition 7.
- **5, junction networks.** A 3-leaf trisum, a 5-leaf nested trisum, a 7-leaf depth-3 chain and a 7-leaf star were tested.
  - Signings: the Kasteleyn signing, then local, two-leaf and global twists.
  - The network count equals the direct count every time, and the Kasteleyn signing gives 0.
  - A good root exists iff no square has three twisted branches. From it every junction is a matchgate, and branched signings show junctions
    off the class.
- **6, controls.**
  - Both signs of the similitude occur.
  - (α + β)² is not the multiplier.
  - No twisted page has the split form.
  - Some branched signing has a junction off the matchgate class.

## Reading

- **The knot's junction is a similitude.**
  - At every trisum square, a side carrying the knot's own signs acts on the other closed side as a similitude of the matchgate quadric. Its
    scale is |α + βζ|², ζ = e^{iπ/3} the knot's own angle.
  - Its two leanings combine as one complex number at the knot's phase.
- **What a twist can and cannot do.**
  - A twist anywhere along one path of the tree is carried along: one twisted side at a time stays planar in the matchgate sense.
  - Only where three twisted sides meet at one square does the junction leave the planar class. There the knot's own mechanism for easy
    counting is gone.
- **The answer so far.** Counting stays easy one twist off the bound, and much further: along any unbranched twist. Whether branched twists
  are hard is ticket B.

## Nonclaims

- **Hardness.** Branched twists are not shown hard here. Proposition 7 only shows that the matchgate route fails there.
- **External results.** The polynomial-time claim rests on Valiant, Cai–Gorenstein and FKT. The computation checks the matchgate identity
  and exact counts, not an FKT implementation.
- **Normalization.** Other normalizations of the y-basis signatures change the multiplier by a constant factor. With the integer
  signatures [1, 0, 1, 0] and [3, 0, −1, 0] used in scoping, it reads 256(α² + αβ + β²).
