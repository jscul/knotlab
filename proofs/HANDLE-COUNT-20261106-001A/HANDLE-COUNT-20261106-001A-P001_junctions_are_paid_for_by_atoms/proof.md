# Which handles cost: tight cuts are free, junctions are paid for by atoms

Status: Proved

Ticket `HANDLE-COUNT-20261106-001A`, 2026-11-06.

**What it uses:**
- **`TWIST-COUNT-20261030-001A`:** Lemma 1 (the Hadamard form for λ = 0), Lemma 3 (untwisted branches have the split form; a branch
  containing a twisted branch is twisted), Theorem 4 (the junction is a similitude), Lemma 5 (a good root) and Theorem 6.
- **`SEYMOUR-COUNT-20261030-001B`:** Lemma 1 (the trisum tree: pieces are planar braces, squares are disjoint trisectors and faces of
  their pieces, each square vertex has one neighbour in each of its three pieces; 2s + 1 pieces for s squares) and Lemma 2 (a Pfaffian
  signing of the brace, with one pattern on each square, is Pfaffian on every piece).
- **`THREEFOLD-AMPLITUDE-20261030-001A`:** Lemma 1 (Pfaffian signings of a matching covered bipartite graph form one switching class)
  and Proposition 5 (every Pfaffian signing of a planar brace is Kasteleyn: a face of length 2k carries k − 1 negations mod 2).
- **`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4:** a connected cubic signed system is not 2-colourable iff its signing is Pfaffian.
- **`THREEFOLD-GRAMMAR-20261030-001A`:** tight cuts of cubic bipartite graphs are 3-edge cuts; the braces are cubic, and a brace with a
  parallel pair is the doubled square; decoration (used only to build test spaces).
- **`PLAIN-COUNT-20261031-001B`, `PLAIN-BRACE-20261031-001B`, `SOFT-CROSS-20261031-001B`, `KNOT-COUPLING-20261031-001B`:** the
  hardness results quoted in Corollaries 2 and 3.
- **External, not replayed:**
  - Valiant's holographic algorithms and Holant theorem; Cai and Gorenstein: every signature satisfying the parity condition and the
    matchgate identities is the signature of a planar matchgate; every even signature of arity at most 3 is a matchgate signature.
  - Kasteleyn, Temperley–Fisher: perfect matchings of a planar weighted graph are a Pfaffian, computable in polynomial time (FKT).
  - Robertson, Seymour and Thomas (Ann. Math. 1999): a Pfaffian brace is the Heawood graph, planar, or obtained from planar braces by
    repeated trisums (6.8); trisectors (8.4, 8.8).
  - Standard: tight-cut decompositions are computable in polynomial time; contracting a shore of a tight cut keeps a graph Pfaffian
    (Little; Vazirani–Yannakakis); Euler's formula; two faces of a 3-connected plane graph meet in nothing, a vertex or an edge.

## Why this ticket exists

The owner asked whether handles govern counting hardness. Plain Pfaffian triple systems are #P-hard to count; the knot's own spaces are
counted in polynomial time with one line removed; native creation reads the tree of Fano atoms. The hypothesis was that planar or
Pfaffian glue is tractable and hardness lives in the handles. The question: are the counts fixed-parameter tractable in the number of
Fano atoms (the genus), or hard already at bounded genus?

The genus half is classical (see "Nearest known result"). This ticket answers the atom half: which handles a count must pay for.

## Standard statement

**Setting.**
- A *cubic system* H has n points and n lines; every line is a set of three points and every point lies on three lines (a 3-regular
  3-uniform hypergraph). Its incidence graph B is cubic bipartite. A *signing* σ is a set of negated incidences.
- For λ ∈ ℂ, Z(H, σ; λ) = Σ_x Π_lines w_λ, summed over 0/1 colourings x of the points, where a line weighs λ if its three values
  (colour xor sign) are equal and 1 otherwise. Z(H, σ; 0) counts proper 2-colourings; λ = 0 is the knot's law.
- B is *Pfaffian* if some signing κ has |det A_κ| = per A > 0 (A the incidence matrix). Then (H, κ) is not 2-colourable, and
  conversely (`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4). A *three-fold space* is a connected cubic system with a signing σ under
  which it is not 2-colourable; it is *plain* if σ = ∅.
- *Braces.* The tight-cut decomposition of B gives braces, joined in a tree T by the tight cuts (each a 3-edge cut). In each brace the
  far side of every cut is one *contracted vertex*; deg_T(G) is the number of contracted vertices of G. The braces of a Pfaffian B are:
  two-vertex and doubled-square braces (with parallel edges), Heawood graphs (the *atoms*; a = their number), planar braces (p = their
  number) and *trisum braces* (non-planar, not Heawood).
- *Trisum trees* (`SEYMOUR-COUNT-20261030-001B`, Lemma 1). A trisum brace splits along its trisectors into planar *pieces* joined by
  *squares*; j(G) is its number of squares and J = Σ j(G). An *end piece* contains exactly one square.
- *The y-basis.* H = [[1, 1], [1, −1]] on every edge. A tensor is *even* if it vanishes on odd y. For a 4-ary tensor with legs in cyclic
  order, MGI(f) = f0000 f1111 − f1100 f0011 + f1010 f0101 − f1001 f0110; an even 4-ary tensor is a matchgate signature iff MGI = 0.
- *Junctions.* In a trisum tree rooted at a piece, each square D is *hosted* by its piece on the root's side. Its *junction* W_D is the
  tensor, on the host's four edges at D, of the two other branches at D together with D's four vertices. c(ℓ) is the number of squares
  hosted by the piece ℓ whose junction violates MGI in the y-basis.

**Results.**
- **Lemma 1 (the Hadamard form).** In the y-basis a point becomes EVEN (equality on d legs becomes 2·[1, 0, 1, 0, …]), a line with signs s
  becomes (−1)^{s·y}·[2λ + 6, 0, 2λ − 2, 0], and Z is a sum over even subgraphs of B. All signatures are even.
- **Lemma 2 (three ports are free).** (i) The tensor of any sub-network on its legs is even. (ii) Every even tensor of arity at most 3 is
  a matchgate signature. So the far side of a tight cut acts in every brace as one matchgate vertex of degree 3.
- **Lemma 3 (two matchgates).** Every even 4-ary tensor is the sum of two matchgate signatures, one of which has a single nonzero entry.
- **Theorem 1 (what junctions cost).** Let B be Pfaffian, σ any signing and λ ∈ ℂ. Then Z(H, σ; λ) is computed with polynomially many
  constant-size contractions and at most Σ_ℓ 8·2^{c(ℓ)} perfect-matching counts of planar graphs (Pfaffians) per trisum brace evaluation,
  four evaluations per non-root brace. Hence it takes time poly(n)·2^{c*}, where c* = max_ℓ c(ℓ) ≤ max_G j(G) ≤ J.
  - Tight cuts and atoms cost nothing; planar braces cost one Pfaffian per evaluation.
- **Corollary 1 (λ = 0).** For colourings under any signing, with the root of `TWIST-COUNT-20261030-001A` Lemma 5, a junction can
  violate MGI only at or above a square with three twisted branches. So Z(H, σ; 0) takes time poly(n)·2^{b}, where b is the number of such
  squares. (b = 0 is `TWIST-COUNT-20261030-001A` Theorem 6.)
- **Lemma 4 (end pieces need a sign).** Every end piece of a trisum tree has a face of length divisible by 4 that shares no edge with its
  square. Every Pfaffian signing of the brace negates an odd number of that face's edges, all of them edges of the end piece.
- **Lemma 5 (tight cuts move signs to the cut).** If σ is a Pfaffian signing of B, every brace G has a Pfaffian signing that agrees with σ
  on the edges between genuine vertices of G and negates at most one edge at each contracted vertex.
- **Theorem 2 (junctions are paid for by atoms and signs).** Let B be a simple Pfaffian cubic bipartite graph other than the Heawood
  graph, and σ any Pfaffian signing of B. Then

  J + p ≤ a + |σ| − 2.

  - In particular, for every plain three-fold space other than the Fano plane, J + p ≤ a − 2: every junction and every planar brace of
    the glue is paid for by an atom.
- **Proposition 6 (the bound is sharp).** Let κ be a Pfaffian signing with the fewest signs, ν, of a Pfaffian glue graph. Putting the
  knot's edge atom (`KNOT-COUPLING-20261031-001A`: a Fano plane with one incidence of a line moved onto the edge) on each negated edge
  gives a plain three-fold space with a = ν, the same junctions and the same planar braces. For the trisum of three cubes ν = 3 and J = 1:
  a 29-point plain space with J + p = a − 2 exactly. For chains of two and three cube trisums ν = J + 3, one above the bound.
- **Corollary 2 (the knot's plain spaces are FPT in the number of atoms).** For every plain three-fold space H, every signing σ′ of B(H)
  and every λ ∈ ℂ, Z(H, σ′; λ) is computable in time poly(n)·2^{a−2}; with planar glue (J = 0), in polynomial time whatever a is. So a
  family of plain three-fold spaces on which some such count is #P-hard (`KNOT-COUPLING-20261031-001B`: every λ ∉ {0, 1, −1, −3})
  has unboundedly many atoms and junctions, unless counting #P-complete problems is polynomial.
- **Corollary 3 (off the knot's plain spaces, atoms do not govern).** Counting colourings is #P-hard on plain Pfaffian braces, which have
  no atom (`PLAIN-BRACE-20261031-001B`), and on Pfaffian graphs under signings (`SOFT-CROSS-20261031-001B`). So counting is not FPT in
  the number of atoms on Pfaffian triple systems in general; there the junctions are paid for by the signs of the Pfaffian class.

## Nearest known result

- **The genus question is classical.** Kasteleyn stated, and Galluccio and Loebl (Electron. J. Combin. 6 (1999) R6) and Tesler (J.
  Combin. Theory B 78 (2000)) proved, that the perfect matchings of a graph of orientable genus g are a linear combination of 4^g
  Pfaffians. For the Ising model, Cimasoni (J. Stat. Mech. 2010, "A generalized Kac–Ward formula") writes the even-subgraph
  generating function of a genus-g graph as an alternating sum of 2^{2g} determinants; Loebl and Masbaum (Adv. Math. 2011) prove the
  Arf-invariant formula optimal; Pant and Singh (arXiv 2605.21077, 2026) show (8/3)^g Pfaffians are sometimes necessary, even for cubic
  bipartite graphs.
  - By Lemma 1, Z(H, σ; λ) is such an even-subgraph sum on B with edge weight √((λ − 1)/(λ + 3)) and signs. More generally, by Lemmas 1
    and 2 every vertex is a planar matchgate gadget; substituting the gadgets keeps the surface, so Z is a weighted perfect-matching count
    of a genus-g graph, a combination of 4^g Pfaffians (this also covers the dimer law λ = −3). So Z is **fixed-parameter tractable in the
    genus of B, and never hard at bounded genus** (unless counting #P-complete problems is polynomial). This is a direct composition of
    known results (`THREEFOLD-SPINSUM-20261030-001A` checked the spin-sector form at λ = 0 on genus 1 and 2). Classification: known; not
    re-proved here.
- **Small separations.** Counting perfect matchings through decompositions along separations of size at most 3 is standard: Curticapean
  (ICALP 2014, single-crossing-minor-free graphs); Straub, Thierauf and Wagner (Theory Comput. Syst. 2016, K5-free graphs). Lemma 2 is
  the matchgate form of the same fact: three ports carry no matchgate identity.
- **Matchgate splitting** (Lemma 3) is elementary; Theorem 1 combines it with the trisum trees of Robertson, Seymour and Thomas.
  Classification: known technique; the parameter (junctions violating MGI per piece) is a candidate local delta.
- **Theorem 2:** no overlap found in a bounded search (Pfaffian number, genus, crossing-number and clique-sum literature). It uses only
  Euler's formula, Kasteleyn's face parity, the trisum tree and the tight-cut contraction of Pfaffian signings.

## Proof of Lemma 1

- A line's weight is w_λ = 1 + (λ − 1)[x constant]. Since Σ_x (−1)^{x·y} = 8δ_{y,0} and the two constant patterns give 1 + (−1)^{|y|},
  ŵ(y) = 8δ_{y,0} + (λ − 1)(1 + (−1)^{|y|}), which is [2λ + 6, 0, 2λ − 2, 0] by weight. A sign s shifts x by s and multiplies ŵ by
  (−1)^{s·y}.
- Equality on d legs: Σ over the two constant patterns of (−1)^{x·y} = 1 + (−1)^{|y|}.
- Inserting H H/2 = I on every edge turns Z into 2^{−|E|} Σ_y Π_v f̂_v, and only even y at every vertex contribute: even subgraphs. ∎
  (Check, section 1, symbolic in λ for all eight sign patterns.)

## Proof of Lemma 2

**(i)** In the y-basis every vertex signature is even. For a sub-network with legs L, Σ_v Σ_{e∋v} y_e counts internal edges twice and
legs once, and is even; so Σ_{e∈L} y_e is even.

**(ii)** The matchgate identities begin at arity 4 (Valiant; Cai–Gorenstein). For a ternary even signature [f000, f011, f101, f110] with
nonzero last three entries, the planar gadget K4 with centre c, spokes u_i = f(e_j + e_k) for {i, j, k} = {1, 2, 3} and triangle weights
f000/(3u_i) on the opposite edges, has exactly this perfect-matching signature (check, section 2, symbolic). ∎

## Proof of Lemma 3

Let f be even, 4-ary, with MGI(f) ≠ 0. Some entry f_z is nonzero, and z lies in exactly one complementary pair {z, z̄} of the identity.
MGI is affine in f_{z̄} with coefficient ±f_z ≠ 0. Let M equal f except at z̄, where it takes the unique value with MGI(M) = 0, and let
C = f − M, supported on z̄. Every product in MGI pairs complementary entries, so a single-entry tensor satisfies MGI. Both are even. ∎
(Check, section 3: symbolic for each of the eight anchors; 4000 random integer and Gaussian tensors.)

## Proof of Theorem 1

1. **Tight cuts.** Root the brace tree. A non-root brace G is evaluated with its parent's contracted vertex x_p replaced by the character
   χ_y of each even pattern y on x_p's three edges (an even signature, Fourier-supported on y), giving the parent's tensor in the y-basis
   by four closed evaluations (odd y vanish by Lemma 2(i)). Its children are contracted vertices carrying their tensors, which are even
   ternary, hence matchgates (Lemma 2).
2. **Planar braces and atoms.** In the y-basis a planar brace is a planar network of matchgate signatures (Lemma 1, Lemma 2, signs absorbed
   into the lines). By Cai–Gorenstein each is a planar matchgate, and by Valiant's Holant theorem the value is the number of perfect
   matchings of a planar graph of size O(|G|): one Pfaffian (FKT). A Heawood brace has fourteen vertices: constant work.
3. **Trisum braces.** Root the trisum tree at a piece. Process pieces away from the root; a non-root piece ℓ with parent square S yields its
   branch tensor on its four edges at S, read in the y-basis (eight even patterns, each a character placed in S's face).
   - At each square D hosted by ℓ, the junction W_D is a constant-size contraction of the two branch tensors beyond D with D's four vertex
     factors. It is even (Lemma 2(i)).
   - D is a face of ℓ (`SEYMOUR-COUNT-20261030-001B`, Lemma 1(iii)). If MGI(Ŵ_D) = 0, a planar matchgate for W_D is placed in that face,
     joined to D's four neighbours in ℓ in face order (MGI is invariant under the dihedral symmetries of the square). Otherwise Lemma 3
     writes W_D = M + C, two matchgates, and the piece's value, multilinear in its junctions, is the sum over the 2^{c(ℓ)} choices.
   - Each choice is a planar matchgate network: one Pfaffian.
4. **Count.** Per closed evaluation of a trisum brace, at most 8·Σ_{ℓ≠root} 2^{c(ℓ)} + 2^{c(root)} Pfaffians, plus O(n) constant-size
   contractions. Finding tight cuts, trisectors and planar embeddings takes polynomial time. Since c(ℓ) is at most the number of squares
   hosted by ℓ, c* ≤ max j(G) ≤ J. ∎

The computation (check, section 4) evaluates every network exactly by elimination instead of FKT: it checks the decomposition, the
splitting and the evenness, not an FKT implementation.

## Proof of Corollary 1

- **The root.** Let D2 be the squares with exactly two twisted branches. For S ∈ D2 the untwisted branch u(S) contains no square of D2 and
  no square with three twisted branches: such a square would have a twisted branch avoiding S inside u(S), which would make u(S) twisted
  (`TWIST-COUNT-20261030-001A`, Lemma 3(iii)). The root r of Lemma 5 there (a leaf of a twisted branch of some S ∈ D2, or any leaf if D2 is
  empty) therefore still lies outside every u(S′), S′ ∈ D2, when squares with three twisted branches are present.
- **Induction.** Every square that does not have three twisted branches then has at most one twisted closed branch. Inside a closed branch
  that contains no square with three twisted branches, the induction of `TWIST-COUNT-20261030-001A` Theorem 6 applies unchanged: twisted
  branch tensors are planar matchgate signatures, untwisted ones have the split form, and by the similitude (Theorem 4) every junction
  there is a matchgate.
- So a junction violating MGI is at a square with three twisted branches, or has one in a closed branch. A piece hosts at most b of them. ∎
  (Check, section 5: 48 random signings of twelve trisum braces; every violating junction is at or above such a square.)

## Proof of Lemma 4

Let P be an end piece with square S. P is a planar brace, so 3-connected with a unique embedding, and S is one of its faces.
- **Euler.** For a cubic plane graph Σ_f (6 − |f|) = 12. Faces of a bipartite graph have even length at least 4, so P has at least six
  faces of length 4.
- **Faces at S.** Each edge of S lies on S and on one other face, and two faces share at most one edge, so at most four faces share an
  edge with S. Some 4-face f* ≠ S shares none; its edges are edges of P other than S's, hence edges of the brace.
- **Parity.** A Pfaffian signing σ of the brace, completed by its pattern on S, is a Pfaffian signing of P (`SEYMOUR-COUNT-20261030-001B`,
  Lemma 2), hence Kasteleyn (`THREEFOLD-AMPLITUDE-20261030-001A`, Proposition 5): f*, of length 4, carries an odd number of negations. ∎

(Check, section 6: every end piece of the test trees has such a face, odd under six Pfaffian signings each; every planar piece has at
least six 4-faces.)

## Proof of Lemma 5

Let C = ∂(X) be a tight cut and G₁ = B/X̄, with X̄ shrunk to x̄. Order the rows (lines) and columns (points) of the signed incidence
matrix with X̄ last.
- Every perfect matching of B uses exactly one edge e ∈ C. It is M₁ ∪ N, with M₁ a perfect matching of G₁ using e at x̄ and N a perfect
  matching of X̄ minus the end v_e of e. Its determinant term is the term of M₁ in G₁'s matrix, times a sign depending only on e (the
  position of v_e among X̄'s vertices), times the signed term of N.
- Since σ is Pfaffian, all terms of B are equal; fixing M₁ and varying N shows that all perfect matchings of X̄ − v_e have one signed term
  s_e. Put σ₁(e) = σ(e)·(sign of e's position)·s_e on the three edges of C and σ₁ = σ elsewhere. Every term of G₁ then equals a term of
  B, so σ₁ is Pfaffian.
- Switching at x̄ leaves at most one negated edge among its three. Repeating along the laminar family of tight cuts changes only edges at
  contracted vertices. ∎

## Proof of Theorem 2

- **One brace.** If B is itself a brace other than Heawood: a planar brace has at least six 4-faces, each needing an odd number of
  negations, and each edge lies on two faces, so |σ| ≥ 3 = p + 2. A trisum brace has at least j + 2 end pieces (a tree with j squares of
  degree 3 and 2j + 1 pieces), each with its own negated edge (Lemma 4), so |σ| ≥ J + 2.
- **Several braces.** Let s_G be the number of edges negated by σ between genuine vertices of G. By Lemma 5, G has a Pfaffian signing
  whose negations are those s_G edges plus at most one edge at each of its deg_T(G) contracted vertices. So
  - a planar brace needs 3 ≤ s_G + deg_T(G);
  - a trisum brace needs j(G) + 2 ≤ s_G + deg_T(G): its end pieces have disjoint own edges, and one contracted vertex negates one edge.
- **The tree.** Σ_{G∈T} (deg_T(G) − 2) = −2. A Heawood brace contributes −1 if it is a leaf and at least 0 otherwise. A two-vertex or
  doubled-square brace has at least two contracted vertices when B is simple (a genuine vertex has no parallel edges), so contributes at
  least 0. Hence Σ_{planar, trisum} (deg_T(G) − 2) ≤ a − 2.
- **Summing.** Σ_trisum (j(G) + 2) + 3p ≤ Σ s_G + (a − 2) + 2(p + #trisum braces), that is J + p ≤ a + Σ s_G − 2 ≤ a + |σ| − 2.
- **Plain spaces.** σ = ∅ is Pfaffian exactly for plain three-fold spaces (Lemma 4 of `THREEFOLD-AMPLITUDE-20261030-001C`). ∎

## Proof of Proposition 6

- At the knot's law an edge atom acts on its edge as an exact negation (`KNOT-COUPLING-20261031-001A`, result 1, in the accepted
  lineage of `KNOT-COUPLING-20261031-001B`). So the decorated plain system is not 2-colourable iff the glue under κ is not, which holds
  because κ is Pfaffian (`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4). For the systems computed, non-colourability is also checked
  directly by SAT.
- Each atom is one Heawood brace, cut off by tight cuts together with doubled squares. The glue keeps its braces with contracted vertices
  in place of the atoms' ends, so J and p are unchanged and a = ν.
- Theorem 2 with a = 0 gives ν ≥ J + p + 2, so a = ν is the fewest atoms this construction can use. The values of ν, a, J and p and the
  non-colourability are computed (check, section 6b). ∎

## Proof of Corollaries 2 and 3

- **Corollary 2.** B(H) is Pfaffian with σ = ∅. Theorem 1 applies to every signing σ′ and coupling: time poly(n)·2^{J}, and J ≤ a − 2 by
  Theorem 2. With J = 0, every evaluation is a planar matchgate network. If a family had bounded a, its counts would be polynomial.
- **Corollary 3.** Plain Pfaffian braces are braces other than Heawood, so a = 0, and counting their colourings is #P-hard
  (`PLAIN-BRACE-20261031-001B`, Theorem 7). The hard instances of `SOFT-CROSS-20261031-001B` (Theorem 4) are Pfaffian graphs under
  signings. An algorithm in time f(a)·poly(n) would solve them in polynomial time. By Theorem 1 their J is unbounded, and by Theorem 2
  their Pfaffian signings have unboundedly many negations. ∎

## What the computation checks

`check.py`:
- **1.** Lemma 1, symbolic in λ, all eight sign patterns; equality on 1 to 4 legs.
- **2.** Lemma 2's gadget, symbolic.
- **3.** Lemma 3: symbolic for each anchor; 4000 random integer and Gaussian even tensors.
- **4.** Theorem 1: twelve random trisum braces built from cubes and prisms (one to three trisums), under their glued Kasteleyn signing
  and under a random signing, at λ = 0, 2, −1/2 and 1 + i; and three plain three-fold spaces with trisum glue (the 35-point space of
  `THREEFOLD-SURFACES-20261030-001B` and two decorated braces, of 118 and 167 points) at λ = 0, 2, 1 + i. The brace-and-junction value
  equals an independent elimination count every time (105 counts); each piece is evaluated 2^{(violating junctions)} times (on the
  braces, 71 of 192 junction evaluations violate MGI and are split); ternary tensors are even. At λ = 0 on a plain space every junction
  is a matchgate; at λ = 2 and 1 + i the same junction is not.
- **5.** Corollary 1 on 48 random signings.
- **6.** Lemma 4 on every end piece (48), ≥ 6 squares on every planar piece (60), and the inequality of Theorem 2 on the braces (with their glued
  Kasteleyn signings) and on the plain spaces. On the plain spaces every non-Heawood brace's Pfaffian class, restricted to edges between
  genuine vertices, is a cut (Lemma 5), with enough contracted vertices, and every end piece meets one.
- **6b.** Proposition 6: the trisum of three cubes and two chains of cube trisums, decorated with an edge atom on every sign of a
  fewest-sign Pfaffian signing (found by MaxSAT over switchings): not colourable, a = ν, J and p unchanged; J + p = a − 2 for the first.
- **7. Controls**, each of which must fire:
  - a split with the wrong sign leaves MGI ≠ 0;
  - contracted tensors on the wrong edge order change the count;
  - with the signs ignored, J + p ≤ a − 2 fails on a signed trisum brace;
  - one extra negation on an end piece's far face makes the face even, and the system becomes colourable.

## Reading

- **Three ports are below the first matchgate identity.** The knot's handles meet the rest of a space through three edges, and every
  even tensor on three edges is a planar gadget. So a Fano atom never costs anything to count through, however many there are.
- **Four ports can cost.** Where three planar pieces meet at a square, the junction can leave the planar class, and then it costs a
  factor 2 on the piece it hangs from. At the knot's law, with any signs, only squares with three twisted sides (or above them) do this.
- **On the knot's own spaces, atoms pay for the junctions.** A plain space has no signs to spend. Every planar piece needs an odd number
  of negations on some square face, and in a plain space negations can only come from the twisted sides of its tight cuts, whose leaves are
  atoms. So J + p ≤ a − 2: hardness needs handles, and the handles that cost are the glue's junctions, which the atoms finance.
- **Off the knot's spaces, signs pay instead.** With signs, or on colourable plain Pfaffian braces, junctions are free to multiply and
  counting is #P-hard with no atom at all.
- **Two against three, once more.** Two twisted sides at a square pass through as a similitude; three cost a factor 2. Three ports are
  free; four ports are where a cost can appear.

## Nonclaims

- **No lower bound.** Nothing here shows that 2^{J} (or 4^g) is necessary. Exponential-time hypotheses are not used (their status is
  under review).
- **The genus statement is classical.** FPT in genus is quoted, not claimed.
- **FKT is not implemented.** The computation checks identities and exact counts by elimination, not an FKT implementation.
