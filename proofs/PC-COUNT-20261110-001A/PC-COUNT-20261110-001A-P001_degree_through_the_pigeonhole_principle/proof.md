# The count needs polynomial-calculus degree n^{Ω(1)} over every field

Status: Proved by hand from Mikša and Nordström's degree bound and the program's reductions. The new reduction step (Lemma 1) and its
composition with `COUNT-SYSTEMS-20261110-001A`'s chain are checked in `check.py`; the transfer of degree (Lemma 2) is the standard
substitution argument, written out below.

Ticket `PC-COUNT-20261110-001A`, 2026-11-10.

## Standard statement

- **The count.** NAE(K_k), the Kasteleyn-signed not-all-equal formula of the octahedral knot sphere K_k: n = 4k² points, two 3-clauses
  per line (`COUNT-NOTE-20261107-001`).
- **Polynomial calculus (PC) over a field F.** Lines are polynomials over F with the Boolean axioms x² − x. From the falsifiers J_C of
  the clauses (J_C is the product of x for each literal ¬x of C and of 1 − x for each literal x) one may take linear combinations and
  multiply a line of degree at most D − 1 by a variable. A refutation of degree D derives 1 with every line of degree at most D. (The
  multilinear variant of `TREE-XOR-20261110-001B`, which also multiplies a degree-D line when the product stays within degree D, has
  degree at least this one minus 1.)
- **FPHP_G.** For a bipartite graph G with pigeons 0, …, N and holes 1, …, N, the functional pigeonhole principle on G has a variable
  x_ph for each edge, and clauses: each pigeon sits in a hole adjacent to it, no pigeon sits in two holes, no two pigeons share a hole.
- **LeftPigeon_N** as in `COUNT-SYSTEMS-20261110-001A`: maps f (pigeons to holes) and g (holes to pigeons); a solution is a pigeon x
  with g(f(x)) ≠ x.

**Theorem.** There is c > 0 such that over every field every polynomial-calculus refutation of NAE(K_k) has degree at least
c·n^{1/4}/log n.

**Corollaries (over F2).**
1. Every tree-like Res(⊕) refutation of the count has size at least 2^{c n^{1/4}/log n − 4} (`TREE-XOR-20261110-001B`: size at least
   2^{d − 3} for the multilinear degree d, which is at least the standard degree minus 1).
2. Every parity decision tree for the count, so every tree-like Res(⊕) refutation, has depth at least c n^{1/4}/log n − 3: a depth-d tree
   is an F2 Nullstellensatz refutation of degree d + 3 (`TREE-XOR-20261110-001A`, Lemma 1), and a Nullstellensatz refutation is a
   polynomial-calculus refutation of the same degree. This improves `TREE-XOR-20261110-001A`'s c n^{1/8}/log n, which stays true.
3. The F2 Nullstellensatz degree of the count is at least the same bound.

## Nearest known result

- **The degree bound.** Mikša and Nordström, *A generalized method for proving polynomial calculus degree lower bounds* (CCC 2015;
  *J. ACM* 71(6), 2024), Theorem 4.9: if G is a bipartite (s, δ)-boundary expander with left degree at most d, refuting FPHP_G in
  polynomial calculus needs degree greater than δs/(2d); their results hold over every field. Alekhnovich and Razborov (2003) had the
  same for the graph PHP without functionality.
- **Where FPHP_G sits.** FPHP_G has a unary Sherali–Adams refutation of degree d (count pigeons by their holes), so it lies in PPADS^dt
  (Göös, Hollender, Jain, Maystre, Pires, Robere and Tao, *Separations in Proof Complexity and TFNP*, J. ACM 2024); Lemma 1 below is a
  direct reduction to LeftPigeon. The count is PPADS^dt-complete (`COUNT-TFNP-20261107-001B`).
- **Not found.** A bounded search (Mikša–Nordström, Göös et al., Itsykson–Sokolov and later Res(⊕) work, recent TFNP surveys) found no
  published polynomial-calculus degree bound for a PPADS-complete principle, Sperner's lemma, or this formula. Li (2024, *Metamathematics
  of resolution lower bounds: a TFNP perspective*) lists the polynomial calculus as future work.
- **Classification.** Known-with-delta, folklore risk high: each step is standard and an expert would expect the conclusion. The delta is
  the explicit chain for this formula and its consequences for tree-like Res(⊕), which `TREE-XOR-20261110-001` left open.

## Proof

**Lemma 1 (FPHP_G reduces to LeftPigeon_N).** Let Δ be the largest degree of a vertex of G (at least 3). Put f(p) = the first hole h
adjacent to p with x_ph = 1 (hole 1 if none) and g(h) = the first pigeon p adjacent to h with x_ph = 1 (pigeon 0 if none). Reading one
value of f or g costs at most Δ queries. Let x be a LeftPigeon solution, g(f(x)) ≠ x. Read x's edges. If none is set, x's pigeon clause
is falsified; if two are, a functionality clause is. Otherwise x sits in exactly one hole h = f(x), and g(h) ≠ x means the first set edge
at h belongs to another pigeon z: the clause "x and z not both in h" is falsified. The decoding reads at most 2Δ variables. Check 1
confirms it on every graph and assignment with N ≤ 2 and on 300 random graphs with N = 3 (64,692 assignments, 143,184 answers).

**The chain to the sphere.** `COUNT-SYSTEMS-20261110-001A` reduces LeftPigeon_N to SINK (succ = f, pred = g), SINK to one-sided grid
Sperner of side m = O(N²) (`COUNT-TFNP-20261107-001A`: each vertex's colour is a function of O(1) pointers) and that to the count on
K_k, k = 2m + 4 (`FLAT-STATES-20261107-001B`: each point reads at most two colours); each violated line decodes, through O(1) pointers,
to a LeftPigeon solution. With Lemma 1 each pointer costs at most Δ queries of FPHP_G, so every point of K_k is a decision tree P_p of
depth t ≤ c₁Δ over FPHP_G's variables, and every violated line decodes by a tree of depth at most c₂Δ to a falsified clause of FPHP_G.
Check 2 composes the chain on 72 instances with N = 2 (76 counterclockwise full triangles). The sizes give n = 4k² = O(N⁴) (check 3).

**Lemma 2 (degree transfers).** Suppose NAE(K_k) has a PC refutation of degree D over F. Replace each variable y_p by the multilinear
polynomial of P_p, of degree at most t; Boolean axioms stay valid because P_p is 0/1-valued.
- *The substituted clauses are derivable.* For a clause C of line ℓ, the polynomial J_C(P) is, as a multilinear polynomial, the sum of the
  path indicators 1_λ over the leaves λ of the tree that evaluates ℓ's three points (depth at most 3t) at which C is falsified, since both
  sides agree on every assignment. At such a leaf ℓ is violated; extending λ by the decoding tree, 1_λ = Σ_μ 1_μ over leaves μ, and each
  μ fixes every variable of a clause C′ of FPHP_G that it falsifies, so 1_μ = J_{C′} times the remaining literals of μ. Each J_C(P) is thus
  derived from FPHP_G's axioms in degree at most 3t + c₂Δ.
- *The lines transfer.* Linear combinations carry over. A step multiplying a line q of degree at most D − 1 by y_v becomes the product of
  q(P), of degree at most (D − 1)t, with P_v, done monomial by monomial through at most t multiplications by variables, every
  intermediate line of degree at most Dt.
So FPHP_G has a PC refutation of degree at most max(Dt, 3t + c₂Δ) ≤ c₃ΔD.

**Lemma 3 (the graph).** For large N there is a bipartite graph G with N + 1 pigeons of degree 3 and N holes, every hole of degree at
most 3 log N, that is a (γN, δ)-boundary expander for constants γ, δ > 0. A random left-3-regular graph has small sets expanding by
(2 − ε)|S|, hence unique-neighbour expansion (1 − 2ε)|S|, for |S| ≤ γN with probability 1 − o(1) (the standard first-moment count;
Mikša and Nordström note that left-degree-3 boundary expanders exist), and its largest hole degree is at most 3 log N with probability
1 − o(1) (balls in bins), so both hold for some G.

**Conclusion.** For G from Lemma 3, FPHP_G needs degree greater than δγN/6 (Mikša–Nordström). By Lemma 2, c₃ΔD > δγN/6 with
Δ ≤ 3 log N, so D ≥ c′N/log N. Since n = O(N⁴), D ≥ c n^{1/4}/log n. ∎

## Remarks

- **The logarithm.** It comes only from the hole degree. With a boundary expander of bounded degree on both sides and N + 1 pigeons
  (for instance a random 3-regular bipartite graph with one pigeon added) the bound is c n^{1/4}; that construction is standard but not
  cited here.
- **Every field.** The bound holds over every field, the rationals included, where the count has a Sherali–Adams refutation of degree 3
  (`COUNT-NOTE-20261107-001B`): positivity, not algebra, is what makes the count easy.
- **Small spheres.** `PC-COUNT-20261110-001B` reads the exact F2 degrees: 3 on K_2, 4 on K_3 and at least 5 on K_4. The bound here is
  asymptotic and below 1 at those sizes.
- **Upper bound.** The polynomial calculus simulates resolution with degree at most its width plus 1, so the degree is O(√n)
  (`SPHERE-WIDTH-20261107-001`). The degree lies between c n^{1/4}/log n and O(√n).

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Lemma 1: every LeftPigeon answer decodes to a falsified clause of FPHP_G within 2Δ reads; every graph with N ≤ 2, 300 random with N = 3 | pass: 64,692 assignments, 143,184 answers |
| 2 | The composed chain: every counterclockwise full triangle decodes to a falsified clause of FPHP_G | pass: 72 instances with N = 2, 76 triangles |
| 3 | Sizes: grid side, k and n for N = 2 to 6; N/n^{1/4} between 0.066 and 0.106 | pass |

## Nonclaims

- **The expander bound, Lemma 3's probability estimates and the substitution argument are cited or argued, not formalized.**
- **No polynomial-calculus size bound** follows: the size-degree relation needs degree above √n.
- **No dag-like Res(⊕) or cutting-planes bound** is claimed.
