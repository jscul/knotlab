# The knot's three-fold spaces are built from the Fano plane

Status: Proved (the general classification is conditional on the stated one-twist lemma)

Ticket `THREEFOLD-SPACES-20261030-001A`, 2026-10-30.

**What it uses:**
- `SPACE-SELECTION-20261030-001C`, Theorem 2 (duality). Take a gadget whose contacts all join three triangles with an odd number of base
  incidences, and whose corner triangles are distinct. Signed not-all-equal is exact on it iff two conditions hold for its dual triple
  system G* (triangles as points, contacts as lines):
  - G* is 2-colourable;
  - G* together with the corner line T_A T_B T_C is not 2-colourable.
- `SPACE-SELECTION-20261030-001A`, for the gadget library.
- Classical results:
  - Seymour's linear-algebra argument (1974).
  - Sign-nonsingular matrices and even cycles (Bassett, Maybee and Quirk).
  - Tight cuts and braces (Lovász; Lovász–Plummer).
  - Robertson, Seymour and Thomas (1999).
  - McCuaig (2000): F7 is the only strongly 2-connected digraph with no even directed cycle.

## Why this ticket exists

The recommendation of `SPACE-SELECTION-20261030-001` asked to prove that the Fano plane is the only connected 3-regular triple system that
is not 2-colourable. That would have made the Fano gadgets the knot's only three-fold spaces.

The premise is false (Corollary 6). Splicing one Fano plane into another gives a 13-point counterexample. Under the owner's rule of adopting
the more interesting reading, the question becomes: is every three-fold space of the knot built from Fano planes?

## Standard statement

**Setting.**
- **Cubic triple systems.** A *cubic triple system* H has n points and n lines. Each line has three distinct points, lines may repeat, and
  every point is on exactly three lines.
- **Associated objects.**
  - The incidence matrix A has lines as rows and points as columns.
  - The incidence graph B(H) is cubic and bipartite.
  - A perfect matching M of B(H) assigns each line one of its points. The digraph D(H, M) on the points has arcs from M(ℓ) to the two other
    points of ℓ, so it is 2-in, 2-out.
- **Signings and twists.**
  - A *signing* negates some incidences.
  - A *twist* is a single negated incidence (ℓ, p). In colouring terms, the colour of p is complemented inside ℓ.
- **Sign-nonsingular.** A signed matrix is *sign-nonsingular (SNS)* when all nonzero terms of its determinant have the same sign, i.e.
  |det| = per(|A|) > 0.
- **Braces.** A nontrivial *tight cut* of B(H) is an edge cut met exactly once by every perfect matching, with both shores of size at least
  three. B(H) is a *brace* when it has none.
- **Splices.**
  - The *point splice* of H₂ (at a line M) into H₁ (at a point t) removes t and M. It replaces t in the three lines through t by the three
    points of M.
  - The *line splice* is the dual operation.
  - A *Fano composition* is obtained from Fano planes by repeated splices.

**Results.**
- **Theorem 1 (dictionary).** For connected cubic H the following are equivalent:
  - (a) H is not 2-colourable;
  - (b) H is minimally not 2-colourable;
  - (c) A is SNS;
  - (d) every nice cycle of B(H) has length 2 mod 4;
  - (e) D(H, M) has no even directed cycle, for one (equivalently, every) perfect matching M.
- **Theorem 2 (splice calculus).** Let H be the point splice of H₂ at M into H₁ at t, both connected cubic.
  - (i) The three edges joining the three points of M to the three lines that contained t form a nontrivial tight cut of B(H).
    Contracting either shore of a tight cut of this form gives back H₁ and H₂.
  - (ii) For every perfect matching μ of H, with pieces μ₁ and μ₂ through the same cut edge, the matching signs relative to a fixed
    reference factorize: s(μ) = s₁(μ₁) · s₂(μ₂).
  - (iii) Hence H is SNS iff there is σ ∈ {±1}³ on the three cut edges such that both pieces, with their cut incidences signed by σ, are
    SNS. Up to switching, σ is either trivial (*untwisted*) or negates one cut edge (*twisted*).
  - (iv) If H₂ is not 2-colourable, every proper colouring of H₂ − M makes M monochromatic. So H is 2-colourable iff H₁ is: an untwisted
    non-colourable piece acts as a single point. Dually, a line splice of a non-colourable piece acts as a single line.
- **Theorem 3 (infinitely many three-fold spaces).**
  - Every Fano composition is connected, cubic and not 2-colourable, and has 7 + 6k points.
  - By the duality, for every k ≥ 0 the knot is exact on three-fold gadgets with 7 + 6k triangles: the dual of any Fano composition with
    any of its lines as corner line, and any base assignment.
  - In gadget terms:
    - a point splice substitutes a Fano gadget into a triangle;
    - a line splice replaces a three-fold contact by six new triangles and seven contacts arranged as a Fano plane minus a point.
  - The checked examples have λ(0) = 5^(k+1).
- **Theorem 4 (the reduction).** Assume the **one-twist lemma**: no cubic brace has an SNS signing with exactly one negative edge. Then:
  - every connected cubic triple system that is not 2-colourable is a Fano composition;
  - no connected cubic triple system has an SNS signing with exactly one twist;
  - the knot's three-fold spaces with distinct corner triangles are exactly the duals of Fano compositions, and they have 7 + 6k
    triangles.
- **Lemma 5 (the one-twist lemma, partial).** The lemma holds for:
  - the Heawood graph, the incidence graph of the Fano plane: each of its 21 single negations is not SNS, and each twisted Fano plane is
    2-colourable;
  - every planar cubic brace.

  The untwisted case of any brace (no negative edge) is McCuaig's theorem. The remaining case, non-planar Pfaffian cubic braces other than
  the Heawood graph, is open here. By Robertson–Seymour–Thomas these are built from planar braces by 4-sums. Ticket B verifies the lemma
  for all braces with at most 13 points.
- **Corollary 6 (the premise is false).** The point splice of a Fano plane into a Fano plane is a linear, connected cubic triple system on
  13 points that is not 2-colourable.
- **Proposition 7 (mixed gluings do not exist).** Consider a gadget whose contacts are all two-fold phase locks (one base incidence) or
  three-fold contacts with an odd base count. It has no locks. So the "mixed gluings of locks and knots" of the previous recommendation form
  an empty class. Mixing locks with knots needs free contacts of even base count, which carry weights rather than constraints.

## Nearest known result

- **Square hypergraphs.** Minimally non-2-colourable square hypergraphs, sign-nonsingular matrices, Pfaffian bipartite graphs and even
  directed cycles are polynomially equivalent problems (Seymour 1974; Seymour–Thomassen 1987; Vazirani–Yannakakis 1989; Robertson–
  Seymour–Thomas 1999). The Heawood graph is the only non-planar Pfaffian brace that is not a 4-sum (RST 1.3).
- **McCuaig 2000.** F7 = D(Heawood, M) is the unique strongly 2-connected digraph with no even dicycle.
- **Classification.**
  - Theorem 1 is classical in substance; its pieces are standard.
  - Theorem 2 is standard tight-cut reasoning, with an explicit sign twist.
  - "Cubic triple systems that are not 2-colourable are exactly Fano compositions", equivalently "2-diregular digraphs without even cycles
    are exactly the compositions of F7", may be known to specialists. Our search did not find it stated, so the folklore risk is moderate.
  - The reading as the knot's three-fold spaces, and Proposition 7, are new here (candidate local delta).

## Proof of Theorem 1

- **(a) ⇒ (b).** Let H′ ⊆ H be minimally non-2-colourable (delete lines while non-colourability holds).
  - **Seymour's lemma.** The columns of its incidence matrix are independent. Suppose instead A′x = 0 with x ≠ 0. Colour {x > 0} red and
    {x < 0} blue. Every line meeting the support of x then meets both colours. The lines missing the support form a proper sub-hypergraph,
    which is 2-colourable by minimality, and together these colour H′.
  - **Counting.** So |E′| ≥ |V′|. But 3|E′| = Σ_{v ∈ V′} deg′(v) ≤ 3|V′|. Hence equality, and every point of H′ has all three of its lines
    in H′.
  - So H′ is a union of components, and H′ = H.
- **(b) ⇒ (c).**
  - per(A) > 0, because cubic bipartite graphs have perfect matchings.
  - Suppose two nonzero terms of det A have opposite signs. Weighting the support positively and concentrating the weight on either term
    makes det take both signs. Since the positive weightings form a connected set, some positive B with the same support is singular.
  - Seymour's argument applied to B then 2-colours H, a contradiction.
- **(c) ⇒ (a).** Let c ∈ {±1}^points be a proper colouring. Give each line positive weights with Σ_{p∈ℓ} b_ℓp c_p = 0, which is possible
  because each line sees both colours. Then Bc = 0, so a positive matrix with the support of A is singular. That contradicts (c).
- **(c) ⇔ (d).**
  - Two perfect matchings differ on disjoint cycles. Their relative sign is Π (−1)^(|C|/2 − 1) over those cycles.
  - Every nice cycle arises this way: match the rest, then take either half of the cycle.
  - So all terms agree iff every nice cycle has |C|/2 odd.
- **(c) ⇔ (e).**
  - Order the lines so that M is the diagonal. Then A = I + Adj(D(H, M)) up to permutation.
  - Determinant terms are covers by directed cycles and fixed points. A term has sign Π (−1)^(length − 1) relative to the diagonal.
  - One even dicycle plus fixed points gives a negative term. Conversely, terms factor over disjoint dicycles. ∎

## Proof of Theorem 2

- **(i) The cut.**
  - Let S be the shore consisting of the points of H₂ and the lines of H₂ − M. It has one more point than lines.
  - Its lines have all their points in S. Its points have 3|S_points| = 3|S_lines| + 3 incidences, so exactly three leave S.
  - **Tightness.** A perfect matching matches the lines of S into the points of S. That leaves exactly one point of S, which must be matched
    across the cut. So the cut is tight.
  - **Contractions.** Contracting S to one point gives H₁. Contracting the complement to one line gives H₂.
- **(ii) Signs.**
  - μ Δ μ₀ consists of cycles inside one shore, which are cycles of μ₁ Δ μ₁⁰ or μ₂ Δ μ₂⁰ avoiding the contracted vertex. When the cut
    edges differ, it contains one crossing cycle C.
  - C contracts to cycles C₁, C₂ through the contracted vertices, with |C| = |C₁| + |C₂| − 2.
  - So (−1)^(|C|/2 − 1) = (−1)^(|C₁|/2 − 1) · (−1)^(|C₂|/2 − 1).
- **(iii) The twist.**
  - Fix a cut edge e. All μ₁ through e combine with all μ₂ through e. So H is SNS iff s₁ is constant (σ(e)) on matchings through e, s₂ is
    constant (σ(e)) likewise, and the two constants agree.
  - That is, both pieces are SNS after signing their cut edges by σ.
  - Switching at the contracted vertex negates all three cut edges, which leaves the patterns {none, one edge} up to switching.
- **(iv) Pieces act as single vertices.** Every proper colouring of H₂ − M colours M monochromatically, since otherwise H₂ is colourable.
  So the three points of M behave as the single point t of H₁. The line case is dual: Fano minus a point behaves as a line on its three
  completions, checked exhaustively. ∎

## Proof of Theorem 3

- **Fano compositions.** Each is cubic, connected and not 2-colourable, by Theorem 2(iv) and induction from the Fano plane. Each splice adds
  6 points.
- **The duality.** For a non-colourable cubic H and any line L₀, H − L₀ is 2-colourable by minimality (Theorem 1(b)). So the duality's two
  conditions hold.
- **A gadget exists.** Its base incidences need a bijection from contacts to triangles other than T_A, matching each contact to one of its
  triangles. Since B(H) is cubic bipartite, every edge lies in a perfect matching. Take one that contains the edge (L₀, T_A) and remove that
  edge. The rest of the roles can be chosen freely.
- **Point splice.** Substituting a Fano gadget into a triangle t of a three-fold gadget replaces the point t of the dual by a Fano plane minus
  a line. That is a point splice.
- **Line splice.** The line splice corresponds to the dual operation on a contact.
- **The check.** It confirms non-colourability at 7, 13, 19, 25 and 49 points, and exactness at the knot of the dual gadgets with 7, 13 and
  19 triangles (λ(0) = 5, 25, 125). ∎

## Proof of Theorem 4

The proof is a joint induction on n for two statements:
- (U) non-colourable connected cubic systems on at most n points are Fano compositions;
- (T) no connected cubic system on at most n points has an SNS signing with exactly one twist.

**The untwisted statement (U).** Let H be non-colourable on n points.
- **If B(H) is a brace.** Then D(H, M) is strongly 2-connected (2-extendable ⟺ strongly 2-connected; Lovász–Plummer, RST 7.5). By
  Theorem 1(e) it has no even dicycle, so by McCuaig it is F7, and H is the Fano plane.
- **Otherwise** take a nontrivial tight cut.
  - It is a 3-edge cut of the form in Theorem 2(i): a shore has one more vertex on one side, and its minority vertices have no neighbour
    outside. This is the tight-cut characterization for bipartite matching-covered graphs (Lucchesi, de Carvalho and Murty). Counting
    degrees gives three edges.
  - The pieces are smaller, and their common pattern σ is untwisted or twisted.
  - A twisted pattern would make the pieces counterexamples to (T) on fewer points.
  - Untwisted pieces are non-colourable, so by (U) for smaller sizes they are Fano compositions, and H is one too.

**The twisted statement (T).** Let T on n points carry an SNS signing with one negative edge e.
- If B(T) is a brace, this contradicts the one-twist lemma.
- Otherwise split along a tight cut. The signed version of Theorem 2(ii) holds verbatim, attributing e's sign to the piece containing e.
- The other piece carries only the cut pattern σ:
  - if σ is twisted, that piece violates (T) on fewer points;
  - if σ is untwisted, that piece is a non-colourable Fano composition by (U). It acts as a single vertex (Theorem 2(iv) and its signed
    form), and contracting it leaves a smaller one-twist counterexample.

**Points mod 6.** Each splice adds 6 points to the total. ∎

## Proof of Lemma 5

- **The Heawood graph.** The 21 single negations are checked exactly: |det| < per for each. Each twisted Fano plane is 2-colourable.
- **Planar cubic braces.**
  - For a cubic plane graph, Euler's formula gives Σ_f (6 − |f|) = 12. All faces have even length at least 4, so there are at least six
    faces of length 4.
  - In a brace every 4-cycle is nice: the two opposite edges of the cycle extend to a perfect matching.
  - Under an SNS signing, a nice cycle of length 2l carries l − 1 negative edges mod 2. So every 4-face needs an odd number of negative
    edges.
  - One negative edge lies on at most two faces, which falls short of six.
- **Examples.** The check also verifies two planar examples, the cube and the hexagonal prism: no signing with at most two negative edges is
  SNS. ∎

## Proof of Proposition 7

- **Slot counts.** In a gadget with n triangles, n − 1 base slots and 2n − 2 other slots lie at contacts. The base slots of T_A, and the b
  and c slots of T_B and T_C, are corners.
- **The three contact types.**
  - A lock uses (1 base, 1 other).
  - An odd three-fold contact uses (1, 2) or (3, 0).
- **Solving.** With L locks, K₁ contacts of type (1, 2) and K₃ of type (3, 0):
  - L + K₁ + 3K₃ = n − 1;
  - L + 2K₁ = 2n − 2.
  - Hence K₁ = n − 1 + 3K₃ and L = −6K₃, so L = K₃ = 0.
- **The check** confirms it on every gadget with at most five triangles (1, 2, 24, 256 such gadgets, none with a lock). ∎

## What the computation checks

`check.py` (about 20 seconds):
- **Theorem 1** on the Fano compositions with 7, 13 and 19 points, and on 300 random connected cubic systems. Colourable ⟺ not SNS on all
  of them, and ⟺ even dicycle on those with n ≤ 9.
- **Theorem 2.**
  - The tight cut of the 13-point splice.
  - Sign factorization over all 192 matchings of the Fano splice and all 72 of two 2-colourable splices with mixed signs.
  - The forcing behaviour of Fano minus a line and of Fano minus a point.
- **Theorem 3.** Compositions with 25 and 49 points are not 2-colourable (SAT). The dual gadgets with 7, 13 and 19 triangles are exact at
  the knot.
- **Lemma 5** on the Heawood graph, the cube and the hexagonal prism.
- **Corollary 6.**
- **Proposition 7** on every gadget with n ≤ 5.
- **Controls:**
  - a 2-colourable system is not SNS, and its dual gadget is not exact;
  - deleting a line breaks non-colourability.

## Reading

- **The knot's own space is generated by one atom.** Gluings built only from three-fold knot contacts reproduce the knot exactly when their
  dual configuration resists 2-colouring as a whole but not once the corner line is removed. These are not just the Fano plane. They form an
  infinite family, the Fano compositions, with 7, 13, 19, … triangles. Every member checked so far is built from Fano planes. The family is
  closed under substitution into triangles and into contacts, and conjecturally (Theorem 4) it is exactly the Fano compositions.
- **The two/three boundary at the level of matchings.** Two-fold contacts lock phases, and their gluings interfere and stay small. Three-fold
  contacts turn the knot into its unsigned dual. The unsigned problem is the classical even-cycle problem, whose single exceptional object
  is the Fano plane, or F7.
- **The premise was a sampling artefact.** A random probe of 25,000 systems missed the rare 13-point splices. The structural question
  replaces it.

## Nonclaims

- **The general classification** (every non-colourable cubic system is a Fano composition) is proved only under the one-twist lemma. The
  lemma is proved for planar braces and the Heawood graph, and verified up to 13 points in ticket B. The non-planar 4-sum case is open.
- **Theorem 4** uses McCuaig's theorem as an external input. It is not replayed here.
- **Even base counts.** Gadgets whose contacts have even base count, or degree other than two or three, are outside these statements.
