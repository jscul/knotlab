# Polynomial counting on Seymour's cubic bound

Status: Proved

Ticket `SEYMOUR-COUNT-20261030-001B`, 2026-10-30.

**What it uses:**
- **`SEYMOUR-COUNT-20261030-001A`:**
  - Lemma 1(i): when a square's four signs have odd parity, exactly one of its lines sees c0 and c2 equal;
  - Lemma 2 (support), Theorem 3 (the trisum law), Proposition 4 (the other view is swapped);
  - Proposition 5 (children as weights) and its proof.
- **`THREEFOLD-AMPLITUDE-20261030-001C`** (through ticket A):
  - Corollary 5: for a connected cubic signed system H that is not colourable, A(H, L) = Π_B a(B) over the braces B of B(H), each brace
    being not colourable, with one amplitude, under any Pfaffian signing;
  - Lemma 4: such a system is not colourable iff its signing is Pfaffian.
- **`THREEFOLD-AMPLITUDE-20261030-001A`:**
  - Lemma 1: Pfaffian signings form one switching class, and switching changes no count;
  - Proposition 5: the Heawood graph has amplitude 5 and the doubled square 1. For a planar brace P with a Pfaffian signing, every such
    signing is Kasteleyn, and the colourings of P − L correspond two to one to the Tutte matchings with outer triangle L (the pointer
    argument).
- **`THREEFOLD-AMPLITUDE-20261030-001B`:** the brace kinds and the two-vertex brace (amplitude 1).
- **`THREEFOLD-GRAMMAR-20261030-001A`:** the tight-cut decomposition, the brace types, and decoration (used to build test spaces).
- **External, not replayed:**
  - **Robertson, Seymour and Thomas** (Ann. Math. 150 (1999); arXiv math/9911268). Their Pfaffian orientations of bipartite graphs are the
    Pfaffian signings here: a central cycle of length 2k carries k − 1 negations mod 2.
    - 6.5: for a 4-sum, (ii) Pfaffian orientations of the two parts that agree on the 4-cycle glue to a Pfaffian orientation, and (iii) if
      the sum is a brace, so are the parts;
    - 6.8: a brace is Pfaffian iff it is the Heawood graph or is obtained from planar braces by repeated trisums;
    - 8.3: the parts of a trisum that is a connected Pfaffian brace are Pfaffian;
    - 8.4: in a connected brace, a set X of four vertices is a *trisector* (G − X has at least three components) iff the brace is a trisum
      along a 4-cycle on X, and then X has two vertices of each colour;
    - 8.7: a Pfaffian brace has no subgraph K₂,₃;
    - 8.8: a trisector other than V(C) of a trisum along C is a trisector of one of its parts, and conversely.
  - **Berman (1980):** in the 0/1 matrix between the lines other than L and the faces not at L, all Tutte matchings contribute with one
    sign.
  - **Standard:**
    - braces on at least six vertices are 3-connected;
    - a 3-connected planar graph has one embedding, and two of its faces meet in nothing, a vertex or an edge;
    - tight-cut decomposition, planarity testing and Bareiss elimination run in polynomial time.

## Why this ticket exists

The owner approved the question: is counting easy on Seymour's bound and hard just off it? Ticket A proved two things. A trisum's amplitude
is the knot's not-all-equal rule applied to its pieces' leanings, and pieces glued below act as weights. This ticket turns that into an
algorithm and proves that it counts in polynomial time on every three-fold space. That settles the easy side.

## Standard statement

**Setting.**
- **Three-fold spaces.** A *three-fold space* is a connected cubic triple system H that is not 2-colourable.
  - It has n points and n lines, so it sits on Seymour's bound for minimally non-2-colourable systems. It is minimal
    (`THREEFOLD-SPACES-20261030-001A`, Theorem 1).
  - B(H) is its incidence graph, and A(H, L) = #col(H − L)/2.
  - Everything below holds as well for connected cubic *signed* systems that are not colourable.
- **Braces.** The braces of B(H) are cubic. They are:
  - the two-vertex brace (θ);
  - the doubled square;
  - the Heawood graph;
  - planar braces;
  - other braces, which are simple, non-planar and Pfaffian.
- **Squares and trisectors.** A *square* (c0, c1, c2, c3) is four vertices: points c0 and c2, lines c1 and c3, listed around a 4-cycle.
  - A *trisector* of a cubic brace K is a set of four vertices whose removal leaves at least three components.
  - Written as a square X, its *pieces* are the components of K − X, each with X and the square's four edges added.
- **The trisum tree.**
  - Split T along a trisector. Then split every non-planar piece along one of its own trisectors, until every piece is planar.
  - The final pieces are the *leaves*. The trisectors used are the *squares*.
  - Leaves and squares are joined when the leaf contains the square.
- **Branches.**
  - For a square S, the components of the tree minus S are its three *branches*.
  - The *branch composite* G_{S,b} is the union of the leaves of branch b. The edges of every square inside the branch are removed, and S
    keeps its edges.
- **Splits and weights.**
  - The *split* (α, β) of a branch composite at S is its leaning split (ticket A): half the colourings of G_{S,b} − c1 in which the third
    point of c3 agrees, as seen by c3, with c0, respectively with c2.
  - For two splits (α_Q, β_Q) and (α_R, β_R), let ρ = α + β, W_α = ρ_Qρ_R − α_Qα_R and W_β = ρ_Qρ_R − β_Qβ_R.
- **The weighted line–face matrix.** Take a planar brace ℓ, a line L of ℓ, and *child squares* D, each with weights (W_α, W_β).
  - Rows are the lines other than L, and columns the faces not at L.
  - The entry for line w and face f is 1 if w lies on f, else 0, except on the rows of a child square:

    | Row | Its side face through d0 | Its side face through d2 | D's own face |
    |---|---|---|---|
    | d3 | W_α | W_β | 1 |
    | d1 | W_β | W_α | 1 |

  - A *restricted* row keeps one of its entries and sets the others to 0.

**Results.**
- **Lemma 1 (the trisum tree).** Let T be a cubic Pfaffian brace that is neither planar nor the Heawood graph.
  - (i) T has a trisector. Every trisector X of a cubic Pfaffian brace:
    - is two points and two lines, pairwise non-adjacent, none on a 4-cycle;
    - leaves exactly three components when removed, and each vertex of X has one neighbour in each.
  - (ii) The splitting stops, and every leaf is a planar brace.
    - Every square is a trisector of T, and distinct squares are disjoint.
    - Every square lies in exactly three leaves, and leaves and squares form a tree with 2s + 1 leaves for s squares.
    - For every square S, the three components of T − S are its branches minus S. G_{S,b} is that component with S and S's edges, the
      part of T's trisum along S.
  - (iii) Every square is a face of each of its three leaves.
- **Lemma 2 (one sign pattern per square).** Fix a Pfaffian signing σ of T.
  - For every square S there is exactly one sign pattern τ_S on its four edges such that the three branch composites at S, signed by σ
    and τ_S, are Pfaffian. It has an odd number of negations.
  - Every leaf, signed by σ and the patterns of its squares, is Pfaffian.
- **Proposition 3 (a leaf with its children).** Let S be a square, b one of its branches, and ℓ the leaf of b at S.
  - For every other square D of ℓ, form (W_α^D, W_β^D) from the splits at D of the two branch composites of D away from ℓ.
  - Let M_α and M_β be the weighted line–face matrices of ℓ with L = c1 and these child squares. The row of c3 is restricted to its side
    face through c0 in M_α, through c2 in M_β.
  - Then the split of G_{S,b} at S is (|det M_α|, |det M_β|).
- **Lemma 4 (weighted Berman).** For a planar brace, a line L and nonnegative weights on the nonzero entries of its line–face matrix:
  - |det| is the weighted number of Tutte matchings with outer triangle L;
  - as a polynomial in the weights, the determinant has all its coefficients of one sign.
- **Theorem 5 (polynomial counting).** For every three-fold space H and every line L, #col(H − L) = 2 Π_B a(B) is computed exactly in time
  polynomial in n:
  1. Decompose B(H) into braces along tight cuts.
  2. Compute one factor per brace:

     | Brace | Factor |
     |---|---|
     | two-vertex or four-vertex brace | 1 |
     | Heawood graph | 5 |
     | planar brace | \|det\| of its line–face matrix, at any line |
     | any other brace | the trisum law at one square of its trisum tree |

     For the last kind, each branch's split comes from Proposition 3, with the children's splits computed the same way one level down: two
     determinants per leaf.
  3. No signing is used at any step.
- **Corollary 6 (the knot's factor).** On every three-fold odd gadget whose dual is a three-fold space, the knot's exactness factor
  λ(0) = (−1)^(n−1) A(H, L₀) is computable in polynomial time.

## Nearest known result

- **Recognition.** Robertson–Seymour–Thomas (1999) and McCuaig (2004) recognize Pfaffian bipartite graphs in polynomial time through the
  same trisum structure. With Seymour (1974) and Klee–Ladner–Manber, that decides which hypergraphs with n vertices and n edges are
  minimally non-2-colourable. This ticket uses their structure to count instead.
- **Planar not-all-equal counting.**
  - Valiant's holographic algorithms count planar 3-NAE-SAT (#PL-3-NAE-SAT) in polynomial time. Cai, Lu and Xia (2010) show that matchgates
    capture exactly the tractable planar Boolean #CSPs.
  - A planar piece's count here falls within that territory, and Lemma 4 is an immediate consequence of Berman's sign coherence.
  - Folklore risk for the planar part is high.
- **General hardness.** Counting NAE-3SAT solutions is #P-complete (Creignou–Hermann 1996).
  - The incidence graphs of three-fold spaces are generally non-planar: the Heawood graph, trisums.
  - The Kasteleyn route on a minimal surface needs 4^genus Pfaffians (Galluccio–Loebl, Tesler, Cimasoni–Reshetikhin), and the genus grows
    with the number of trisums.
  - Here the non-planar part is assembled from planar pieces that exchange two numbers per square.
- **Deficiency.** Szeider (2004) showed SAT is fixed-parameter tractable in maximum deficiency. Three-fold spaces have deficiency zero (n lines
  on n points).
- **Searches.** Several web searches found no source counting the colourings of minimally non-2-colourable hypergraphs, or not-all-equal
  solutions on non-planar instances with Pfaffian structure.
  - **Folklore risk (moderate).** A holographic algorithm on a Pfaffian matchgrid might reach the same class. None was found stated.
- **What is new here** (candidate local delta):
  - Proposition 3: a non-planar piece's leaning split as one weighted determinant per planar leaf;
  - Theorem 5: polynomial counting on every three-fold space.

## Proof of Lemma 1

**(i) Existence.**
- By RST 6.8, T is obtained from planar braces by repeated trisums. It is not planar, so at least one trisum was applied.
- The last one expresses T as a trisum along a 4-cycle C, and V(C) is a trisector (RST 8.4).

**(i) Structure.** Let X be a trisector of a cubic Pfaffian brace K.
- **The parts.** By RST 8.4, K is a trisum of parts K₁, K₂, K₃ along a 4-cycle C on X, and X has two vertices of each colour.
  - The parts are braces (6.5(iii)) and Pfaffian (8.3).
  - Each part strictly contains C and has a perfect matching, so it has at least six vertices and is 3-connected.
- **One edge into each part.** A vertex x of X has at most two edges of C in each part. So it has at least one edge into each part's own
  vertices, and these are distinct edges of K.
  - Since x has degree 3 in K, it has exactly one edge into each part, and K keeps no edge of C. So X is independent.
- **Three components.** Suppose a part's own vertices formed two or more components.
  - Some component Y would receive at most two of the four edges from X.
  - Y has at least two vertices: a single vertex would need three neighbours in X of the other colour.
  - So Y would be cut off by at most two edges, impossible in a 3-connected cubic graph.
  - Hence K − X has exactly three components.
- **No 4-cycle.** Suppose x ∈ X lay on a 4-cycle x a y b.
  - Then a and b are x's neighbours in two different components, so y, adjacent to both, lies in X. It is the other vertex of x's colour.
  - The part containing a then contains x and y, both adjacent to a and to the two other vertices of C. That is a K₂,₃, contrary to RST 8.7.

**(ii) Termination and squares.**
- **Termination.** Each piece of a split is a cubic Pfaffian brace (by (i), 6.5(iii) and 8.3) with fewer vertices.
  - A non-planar piece contains a 4-cycle, so it is not the Heawood graph, whose girth is 6. By (i) it has a trisector.
- **Squares are trisectors of T.** A square Y found in a piece K_i of K's split at X is a trisector of K_i. It is not X, because K_i − X is
  connected. So by RST 8.8 it is a trisector of K, and by induction of T.
- **Disjointness.** When a piece g is split at Y, every earlier square of g is a 4-cycle of g, so it misses Y by (i).
  - It therefore lies in one component of g − Y and goes into exactly one new piece.
  - A vertex of a square lies only in pieces that contain the whole square. So distinct squares are disjoint.
- **Three leaves per square.** A square enters three pieces when it is created, then follows one piece per later split.
- **A tree.** A split replaces a piece by three pieces joined at a new square, and hands each old square to one of them. That keeps leaves
  and squares a tree, and adds two leaves per square.
- **Branches.**
  - Every edge of T lies in exactly one leaf.
  - Two leaves in different branches of S share no vertex outside S, because a shared vertex lies on a square they share.
  - So T − S has no edge between branches. By (i) it has exactly three components: the branches minus S.

**(iii) Faces.**
- Let D be a 4-cycle of a leaf ℓ, a 3-connected planar cubic bipartite graph. If D did not bound a face, its inside and its outside would
  both be non-empty.
- Neither side is a single vertex, which would need three neighbours of the other colour on D.
- So each side is cut off by at least three of the four edges leaving D, which is impossible. ∎

## Proof of Lemma 2

**One square.**
- S is a trisector of T (Lemma 1(ii)), so T is the trisum of its three branch composites, which are Pfaffian braces (RST 8.4, 8.3,
  6.5(iii)).
- Switch each composite at its own vertices so that the three agree on S (the moves of ticket A, Lemma 1(ii)). Glued, they give a Pfaffian
  signing of T. This is the proof of RST 6.5(ii), applied twice: first keeping S's edges, then deleting them; S is central each time.
- σ is a switching of it (`THREEFOLD-AMPLITUDE-20261030-001A`, Lemma 1(i)). Apply the same switching to the three composites. They stay
  Pfaffian, now carry σ on T's edges, and still agree on S.
- **Uniqueness.** Two such patterns on one composite differ by a switching that changes none of its other edges. The composite minus S's
  edges is connected (Lemma 1(i)), so that switching changes no edge at all.
- **Odd.** S is central in a brace, so a Pfaffian signing negates an odd number of its edges.

**Leaves.** Claim, by induction on the number of vertices: for every cubic Pfaffian brace K with a Pfaffian signing ς, every leaf of a
splitting of K is Pfaffian under ς and the patterns τ^{K,ς} of its squares.
- **Base.** If K is planar, it is its own leaf.
- **Step.**
  - Otherwise let Z be the first square and K₁, K₂, K₃ its pieces. Each K_i is Pfaffian under ς_i = ς with τ^{K,ς}_Z.
  - The leaves of K are the leaves of the splittings of the K_i, so by induction they are Pfaffian under ς_i and the patterns
    τ^{K_i,ς_i}.
- **The patterns agree.** For a square D of K_i's splitting, the two components of K_i − D that miss Z are components of K − D as well.
  - Their vertices have the same neighbours in K and K_i.
  - So D's two branch composites away from Z are the same graphs in K and in K_i, with the same signs.
  - By uniqueness, τ^{K_i,ς_i}_D = τ^{K,ς}_D. ∎

## Proof of Proposition 3

**The pieces around ℓ.**
- By Lemma 1(ii), branch b consists of ℓ and, for each other square D of ℓ, the two branches of D away from ℓ.
- Their composites Q_D and R_D meet ℓ and each other only in D. Different D give disjoint vertex sets outside ℓ.
- Sign G_{S,b} by σ and τ_S, which is Pfaffian by Lemma 2, so its split is defined. Restore every D's edges in ℓ with τ_D. By Lemma 2, ℓ is
  then Pfaffian.

**One child square at a time.** Fix a colouring of ℓ's points, including the points of all its squares.
- For each D, sum over the colourings of the points of Q_D and R_D outside D that make their own lines, and D's two lines in G_{S,b}, proper.
- Q_D and R_D are pieces under σ and τ_D (Lemma 2), carrying the same odd pattern on D as ℓ. So the case analysis of ticket A's
  Proposition 5 applies:
  - the sum is 0 unless ℓ's own d1 and d3 (with D's edges) are proper;
  - if d1 sees d0 = d2, the sum is W_α^D when the third point of d3 leans to d0, and W_β^D when it leans to d2;
  - if d3 sees d0 = d2, the sum is W_β^D when the third point of d1 leans to d0, and W_α^D when it leans to d2.
- **No other gauge needed.** That proof, and those of Lemma 2, Theorem 3 and Proposition 4 of ticket A, compare only values *as seen* by
  the square's lines. They use only that the three pieces carry one odd pattern on the square, not the positivity of the other incidences in
  ticket A's uniform gauge.

**The sums multiply.** They involve disjoint sets of points and different lines. So the colourings of G_{S,b} − c1 with the leaning α at S,
counted with these sums, number Σ_c Π_D W^D(state of c at D). The sum runs over the colourings c of ℓ − c1 with the leaning α at S.

**Pointers.** ℓ is a planar brace with a Pfaffian, hence Kasteleyn, signing. By the pointer argument, its colourings of ℓ − c1 come in
complementary pairs, one pair per Tutte matching with outer triangle c1. A line points to the face at it that misses its odd incidence.
- **At S.** c1 is the outer triangle. If the third point of c3 agrees with c0, the odd incidence of c3 is the one at c2. So c3 points to its
  side face through c0. In the other case it points to its side face through c2.
- **At a child square D.**
  - If d1 sees d0 = d2 and is proper, its odd incidence is its third point, so d1 points to D's face. Then d3 points to its side face
    through d0 or d2, as its third point leans.
  - Symmetrically, if d3 sees d0 = d2.
  - D's face receives exactly one pointer, from d1 or from d3. So each matching determines the state at D, and the product of the entries in
    rows d1 and d3 is that state's weight.
- **Halving.** Complementary colourings have the same states. Hence α is the weighted number of Tutte matchings in which c3 points through
  c0, and likewise β.

**Determinants.** Lemma 4 turns these weighted counts into |det M_α| and |det M_β|. ∎

## Proof of Lemma 4

- A term of the determinant is nonzero only for a bijection with every entry nonzero, which is a Tutte matching.
- By Berman, |det| of the 0/1 matrix equals the number of Tutte matchings. That number is a sum of that many terms ±1, so they all carry one
  sign ε.
- Weights change no term's sign, so the determinant is ε times the weighted count. Every monomial of the polynomial collects terms of the one
  sign ε. ∎

## Proof of Theorem 5

**Correctness.**
- **The product.** The amplitude is the product of the braces' amplitudes (`THREEFOLD-AMPLITUDE-20261030-001C`, Corollary 5), whatever the
  line.
- **Small and planar braces.**
  - The two-vertex brace has amplitude 1, and the Heawood graph and the doubled square have 5 and 1 (`THREEFOLD-AMPLITUDE-20261030-001A`,
    Proposition 5).
  - A planar brace has amplitude |M_T(L)|, the number of Tutte matchings, which is |det| by Lemma 4.
- **Any other brace T.**
  - Lemma 1 gives the trisum tree. Its first square X is a trisector, and T is the trisum of the three branch composites at X.
  - Under σ and τ_X these are pieces with one odd pattern on X (Lemma 2). So ticket A's Theorem 3 gives A(T) = A(T, c1) as the law of their
    splits.
  - Proposition 3 computes each split from its leaf at X. The weights there are splits of branch composites at the leaf's other squares,
    computed by Proposition 3 again.
  - The recursion follows the tree away from X and ends at leaves with no further squares.
- **No signing.** Splits, weights and the line–face matrices are defined without signs.

**Running time.** Let N = 2n be the number of vertices of B(H).
- **The tight-cut decomposition** is polynomial. For example, test each pair of disjoint edges for a perfect matching of the rest: O(N²)
  bipartite matchings per cut, and fewer than N cuts.
- **Per brace.**
  - Planarity takes linear time.
  - A trisector search tries O(N³) choices of c0, c2 and c1, each with one depth-first search for cut vertices.
  - There are fewer than N/4 splits.
- **Determinants.**
  - There are two per leaf, fewer than N leaves, and each matrix has fewer than N rows.
  - Every split and weight is at most 4^N, so entries have O(N) bits.
  - Bareiss elimination is polynomial in the size and the bit length. ∎

## Proof of Corollary 6

λ(0) = (−1)^(n−1) A(H, L₀) (`THREEFOLD-AMPLITUDE-20261030-001C`, Corollary 5, with `THREEFOLD-AMPLITUDE-20261030-001A`, Theorem 2), and
Theorem 5 computes A(H, L₀). ∎

## What the computation checks

`check.py` (about fifty seconds):
- **1, Berman on planar braces.** The 4- to 12-prisms, the truncated octahedron and Omni(K₂,₃) were tested.
  - At every line, |det| = the number of Tutte matchings (Ryser's permanent) = the amplitude by direct count with a Kasteleyn signing.
  - At every square face, in both labellings (114 cases), the restricted determinants equal the restricted permanents and the leaning splits
    counted directly.
- **2, weighted rows.** On the truncated octahedron and the 10- and 12-prisms with one or two child squares:
  - |det| = the weighted permanent for random weights (24 cases);
  - the determinant as a polynomial in symbolic weights has all its coefficients of one sign (6 polynomials).
- **3, the trisum tree** on 67 braces, found by search:
  - leaves are planar braces, checked to be 2-extendable;
  - squares are disjoint trisectors of the whole brace with exactly three components, on no 4-cycle, and faces of their three leaves;
  - leaves and squares form a tree.
  - On five braces, the unpruned search lists every trisector (1 to 3); all miss 4-cycles, and there are at most n − 5.
- **4, brace amplitudes.** The braces are 44 trisums of prisms, 14 nested trisums, 6 depth-3 chains and 3 stars, with 16 to 80 vertices and 3
  to 7 planar pieces.
  - The tree value equals the direct count with a Pfaffian signing from a minimal map, at three lines.
  - It is the same at every choice of root square, and with the colour classes exchanged.
- **5, the whole pipeline.** On seven three-fold spaces of 22 to 118 points, the pipeline value equals the direct count at three lines, and
  every space is non-colourable.
  - Glue: doubled squares, the cube, the hexagonal prism, the truncated octahedron, the trisum of three cubes, a trisum of prisms and a nested
    trisum.
- **6, scale.**
  - **Against direct counts.** Trisums and a depth-3 chain of omnitruncations (208, 352 and 480 vertices) equal direct counts. Those use a
    Pfaffian signing glued from the leaves' Kasteleyn signings, checked non-colourable.
  - **Beyond elimination.** Trisums of three omnitruncated k × k grids, k = 5, 7, 9 (472, 1000 and 1720 vertices), take 0.1 to 2.6 s.
    - Min-degree variable elimination would need factors on 17, 24 and 30 variables.
    - The values agree with the colour classes exchanged.
    - Each piece's α + β is the number of spanning trees of the grid (Kirchhoff).
- **7, controls.**
  - Unswapped weights on c1's row give wrong amplitudes.
  - Dropping the children's weights gives a wrong amplitude.
  - Reading one asymmetric piece's split from the wrong side breaks the law.
  - K₃,₃ and the Heawood graph are refused by the tree.

## Reading

- **Where counting stays easy.** On Seymour's bound the knot's spaces are exactly the cubic systems whose non-colourability is a
  determinant condition (sign-nonsingularity).
  - Their colourings with one contact removed are counted by determinants too: one per planar piece.
  - The pieces exchange only their two leanings at each square, and the knot's not-all-equal rule closes each trisum.
- **Why the surface does not matter.** The handles of a three-fold space live in its Heawood atoms and trisums. Counting does not need the
  surface: each handle is a factor 5 or a not-all-equal junction of planar pieces.
- **The boundary question.** If counting becomes hard, it does so off the bound: more lines than points, or a system that is not regular.
  That is the next question.

## Nonclaims

- **The hard side.** Counting off the bound is not treated.
- **Recognition.** Deciding whether a cubic system is a three-fold space is polynomial by Robertson–Seymour–Thomas with Seymour and
  Klee–Ladner–Manber. It is not implemented, and the pipeline assumes its input is a three-fold space, or a non-colourable signed cubic
  system.
- **Running time.** The bounds are not optimized. The trisector search is a simple O(N⁴) one, not Robertson–Seymour–Thomas's O(N³). The
  computation's pruning (skipping vertices on 4-cycles) is justified by Lemma 1(i).
- **External results.** Berman's sign coherence and the Robertson–Seymour–Thomas structure results are not replayed. The computation checks
  Berman's statement on the planar braces it uses, and the structure on its test braces.
