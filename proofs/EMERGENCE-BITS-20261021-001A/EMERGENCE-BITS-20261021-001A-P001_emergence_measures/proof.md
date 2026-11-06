# Measuring emergence in bits

Status: Proved

Ticket `EMERGENCE-BITS-20261021-001A`, 2026-10-21. It uses:
- `KNOT-FOUNDATION-20261019-001E-P001`: the knot test K1–K3 with erasure read
  as forgetting;
- `KNOT-COMPETITION-20261019-001A-P001` ("the competition proof"):
  - a relation on m ≥ 3 bits is a knot exactly when its excluded points are
    nonempty and no two of them are neighbours;
  - the knots that are least sets of pairwise energies are exactly the four
    not-all-equal relations on three bits;
- `BASE-THREE-20261021-001A-P001`: pairwise laws are the majority-closed ones
  and have no knots.

It also cites:
- majority closure and pairwise determination (Baker and Pixley 1975;
  Schaefer 1978);
- the closure of exponential families, whose boundary pieces are the families
  restricted to facial sets (Barndorff-Nielsen 1978; Csiszár and Matúš 2005;
  Geiger, Meek and Sturmfels 2006), and the circuit criterion for facial sets
  (Rauh, Kahle and Ay 2011);
- binary covering arrays of strength two: the largest number of columns with
  k rows is C(k−1, ⌈k/2⌉) (Kleitman and Spencer 1973; Katona 1973);
- orthogonal arrays OA(4λ, 4λ−1, 2, 2) correspond to Hadamard matrices of
  order 4λ (Plackett and Burman 1946; Hedayat, Sloane and Stufken 1999);
- the Hamming bound and shortened Hamming codes.

## Standard statement

For a nonempty R ⊆ {0,1}^n, let pc(R) be the set of points whose every
two-coordinate projection occurs in R (the join of the two-dimensional
projections of R). Let
- E(R) = log₂|pc(R)| − log₂|R|, and
- I(R) be the information divergence of the uniform distribution on R from
  the binary pairwise (Ising) exponential family.

Then:
- E = 0 exactly for majority-closed relations;
- 0 ≤ I ≤ E, with I = 0 exactly when R is a facial set of the pairwise model;
- a relation all of whose (n−1)-coordinate projections are full has
  E ≤ 1, with equality only for the two parity hyperplanes;
- the maximum of E on n bits is n − log₂ CAN(2,n,2), attained by minimum
  covering arrays;
- I ≤ n − log₂(n+1), with equality exactly for orthogonal arrays of strength
  two with n + 1 runs;
- for affine relations I = E ≤ n − ⌈log₂(n+1)⌉.

## Nearest known result

- **E = 0 and I = 0.** Both are textbook:
  - majority-closed relations are those determined by their two-coordinate
    projections (Baker and Pixley; Schaefer);
  - the uniform distribution on R lies in the closure of an exponential
    family exactly when R is facial.
- **What I is.** I is the connected information of order three and above in
  the hierarchical decomposition (Amari 2001; Schneidman et al. 2003).
- **Maximizers of divergence.** The maximizers of divergence from
  exponential families, over all distributions, are studied by Ay and Knauf
  (2006), Matúš and Ay (2003) and Rauh (2011). Rauh treats the binary
  pairwise model on four bits as an example.
- **The capacity statements.** A bounded search did not find the bound
  n − log₂(n+1) for uniform distributions on sets, with its Hadamard equality
  case. It did not find the maximum of |pc(R)|/|R| either. Both follow
  quickly from standard facts, so the folklore risk is moderate.

Novelty: `known-overlap-found` for the zero sets. The delta is
`candidate-local-delta`:
- the two capacities for relations;
- the 480 maximizers on seven bits;
- the statement that the not-all-equal triangles are the only statistically
  silent knots;
- the reading of both measures as emergence.

## Definitions

- **Relation, knot.** A relation is a nonempty R ⊆ {0,1}^n: the joint states a
  system allows, with witnesses forgotten. Under K1–K3 with forgetting, a
  relation on N ≥ 3 bits is a knot when it is not the whole cube and every
  projection that forgets one coordinate is the whole (N−1)-cube.
- **Logical emergence.** E(R) = log₂|pc(R)| − log₂|R| =
  −log₂ Pr[x ∈ R] for x uniform on pc(R). It is the surprise, in bits, of a
  state consistent with every view of a pair being consistent with the
  whole.
- **Statistical emergence.** Let p* be the distribution of maximum entropy
  whose two-coordinate marginals equal those of the uniform distribution u_R.
  Then I(R) = H(p*) − log₂|R|.

## Theorem 1: the zero set of E

E(R) ≥ 0, and E(R) = 0 exactly when R is closed under coordinatewise
majority, which is exactly when R is the solution set of clauses of at most
two literals.

*Proof.* R ⊆ pc(R), so E ≥ 0.
- **If R is majority-closed, then pc(R) = R.** Let t ∈ pc(R). By induction on
  k ≥ 2, every k-coordinate projection of t occurs in R: for a set S of
  k + 1 ≥ 3 coordinates, choose rows r₁, r₂, r₃ of R agreeing with t on S
  minus one of three different coordinates each. Their majority agrees with
  t on all of S, because each coordinate is missed by at most one of them.
- **If pc(R) = R, then R is the solution set** of the clauses describing its
  two-coordinate projections. Every binary relation on bits is
  majority-closed, so R is too.
- **The clause form.** If R is the solution set of a formula φ of clauses of
  at most two literals, each clause holds on R, hence on its pair projection,
  hence on pc(R). So pc(R) ⊆ R. ∎

*Check.* All relations on two, three and four bits (15, 255, 65,535). E = 0
holds for 15, 165 and 4,169 of them, exactly the majority-closed ones.

## Theorem 2: knots

A relation on N ≥ 3 bits is a knot exactly when its excluded set Z is a
nonempty independent set of the N-cube (the competition proof). Then every
pair of coordinates is free, pc(R) is the whole cube, and

E(R) = −log₂(1 − |Z|/2^N) ≤ 1,

with equality exactly for the two parity relations.

*Proof.* The formula is immediate from pc(R) = {0,1}^N.
- **The bound.** The cube is a connected N-regular bipartite graph with
  colour classes A (even weight) and B (odd weight). Let I be independent and
  I_B = I ∩ B. Its neighbourhood N(I_B) lies in A ∖ I, and |N(I_B)| ≥ |I_B| by
  regularity (count edges). So |I| ≤ |A| − |N(I_B)| + |I_B| ≤ 2^(N−1).
- **The equality case.** Equality forces |N(I_B)| = |I_B|. Then every edge
  at N(I_B) returns to I_B, so I_B is a union of components: ∅ or all of B.
  Hence Z is a colour class, and R, the other class, is a parity relation. ∎

*Values.*
- A single clause on three bits holds log₂(8/7) ≈ 0.193 bits. A clause on N
  bits holds −log₂(1 − 2^(−N)).
- Parity holds one bit at every size.

*Check.*
- For N = 3 and 4, the knots found from the definition coincide with the
  complements of nonempty independent sets (34 and 742).
- The formula holds for every knot, and only parity reaches one bit.
- The 5-cube has 254,475 independent sets, so there are 254,474 knots on
  five bits.

## Theorem 3: statistical emergence

1. I(R) = min D(u_R ‖ q) over q in the closure of the pairwise exponential
   family, and 0 ≤ I(R) ≤ E(R).
2. I(R) = 0 exactly when R is the least set of a pairwise energy, a sum of
   functions of two coordinates. That is, R is a facial set of the pairwise
   model.

*Proof.*
- **I is a divergence.** p* lies in the closure of the family. On its
  support, log p* is a sum of functions of at most two coordinates. u_R has
  the same pair marginals as p* and lives inside its support, so
  E_{u_R}[log p*] = E_{p*}[log p*]. Hence D(u_R ‖ p*) = H(p*) − H(u_R).
  The Pythagorean identity D(u_R ‖ q) = D(u_R ‖ p*) + D(p* ‖ q) for q in the
  closure gives the minimum.
- **I ≥ 0.** u_R is feasible for the entropy maximization.
- **I ≤ E.** pc(R) is the least set of the pairwise energy that counts
  violated pair patterns, so u_{pc(R)} lies in the closure. Hence
  I ≤ D(u_R ‖ u_{pc(R)}) = E.
- **I = 0.** I = 0 exactly when p* = u_R. The support of the max-entropy
  solution is the largest support of any feasible distribution, the facial
  closure of R. So I = 0 exactly when the facial closure is R itself, that
  is, when R is facial. Facial sets are exactly the least sets of quadratic
  pseudo-Boolean functions. ∎

*Check.* All 255 relations on three bits:
- **I = 0 exactly on the least sets.** The facial closure is computed by
  exact rational linear programming. Least-set membership is decided by
  exact feasibility. I is computed by iterative proportional fitting on the
  closure. I = 0 holds exactly on the 225 least sets, and 60 of them have
  E > 0.
- **The bounds hold.** 0 ≤ I ≤ E everywhere. Every closure is either R or
  the whole cube.
- **The circuit criterion agrees.** On three bits the pairwise model has one
  circuit, the alternating sum over the cube. So R is facial exactly when
  "R contains every even point" and "R contains every odd point" are both
  true or both false. This agrees on all 255 relations.

### Corollary: the silent knots

By the competition proof, the only knots that are least sets of pairwise
energies are the four not-all-equal relations on three bits.
- **So they are the only statistically silent knots.** They are exactly the
  knots with I = 0. Every other knot, of any size, has positive statistical
  emergence.
- **On three bits,** I > 0 exactly for the 30 knots whose excluded points
  share a parity. Their I depends only on |Z|:

| Excluded points | Knots | E | I |
| --- | --- | --- | --- |
| 1 (one clause) | 8 | 0.193 | 0.078 |
| 2, at distance 2 | 12 | 0.415 | 0.252 |
| 2, antipodal (not-all-equal) | 4 | 0.415 | **0** |
| 3 | 8 | 0.678 | 0.536 |
| 4 (parity) | 2 | 1 | 1 |

The clause's value solves its symmetric equation. Write p*(000) = 1/7 − b,
weight one b, weight two 2/7 − b and weight three b. The third difference of
log p* vanishes when (1/7 − b)(2/7 − b)³ = b⁴. The fitted value 0.07847 agrees
to 10⁻⁶. A sample of 40 knots on four bits are not least sets.

## Theorem 4: logical capacity

For n ≥ 2 the largest E on n bits is n − log₂ CAN(n). Here
CAN(n) = min{k : C(k−1, ⌈k/2⌉) ≥ n} is the fewest rows of a binary covering
array of strength two with n columns.
- **Who attains it.** Every minimum covering array, since pc is then the
  whole cube. On three and four bits these are the only maximizers (2 and 16
  relations).
- **How large it is.** CAN(n) = log₂n + ½log₂log₂n + O(1). So n
  distinctions can hide from their pairs all but log₂log₂n + o(1) bits. Ten
  distinctions with six states hide 7.415 bits.

*Proof.*
- **The covering view.** Let S = pc(R). Then S is pair-closed, R ⊆ S, and R
  realizes every pair pattern of S. Let c(S) be the fewest points of S that
  realize them all. It suffices that |S|·CAN(n) ≤ 2^n·c(S).
- **Reduction.** Deleting a constant coordinate, or one of two tied
  coordinates, changes neither |S| nor c(S). The bound n − log₂ CAN(n) does
  not decrease with n, because CAN(n) ≤ 2·CAN(n−1): stack two copies of an
  array, with a new column of zeros and then of ones. So assume every pair
  of coordinates shows three or four patterns.
- **The clause graph.** Let G be the graph of pairs showing exactly three
  patterns. If G is empty, S is the whole cube and c(S) = CAN(n).

Let ν be the matching number of G and α its independence number. Then:
- **(F1)** |S| ≤ 2^n(3/4)^ν, since clauses on disjoint pairs exclude
  independently.
- **(F2)** c(S) ≥ CAN(α) when α ≥ 2. The projection of S on an independent
  set is majority-closed with every pair full, hence the whole cube.
- **(F3)** α ≥ n − 2ν, since the matched vertices cover G.
- **(F4)** c(S) ≥ 3 if G is nonempty, and c(S) ≥ 4 if some pair is full.
- **(F5)** If no pair is full, S shatters no pair. Its VC dimension is then
  at most 1, so |S| ≤ n + 1 (Sauer–Shelah).

**n ≥ 6.** We have (3/4)^ν CAN(n) ≤ max(CAN(n − 2ν), 3) for every
1 ≤ ν ≤ n/2.
- **Up to 5000:** checked directly.
- **Beyond, with 2ν ≤ n/2:** let T(j) = C(j−1, ⌈j/2⌉). The ratio T(j+2)/T(j)
  is 2(2m+1)/(m+1) for j = 2m and 2(2m+1)/(m+2) for j = 2m+1, so
  T(j+2) ≥ 2T(j). Hence
  CAN(n − 2ν) ≥ CAN(⌈n/2⌉) ≥ CAN(n) − 2. Also (3/4)CAN(n) ≤ CAN(n) − 2 once
  CAN(n) ≥ 8.
- **Beyond, with 2ν > n/2:** (3/4)^(n/4) CAN(n) < 3.

With (F1)–(F4) and CAN nondecreasing, this gives
|S|·CAN(n) ≤ 2^n·max(CAN(α), 3) ≤ 2^n·c(S).

**n = 5** (CAN = 6, 2^n = 32).
- **ν ≥ 2:** |S| ≤ 18. If a pair is full, c ≥ 4, and 6·18 ≤ 32·4.
  Otherwise |S| ≤ 6 and 6·6 ≤ 32·3.
- **ν = 1, star:** G is a star, so α ≥ 4. Then c ≥ CAN(4) = 5 and
  6·24 ≤ 32·5.
- **ν = 1, triangle:** G is a triangle, so (F5) on its three coordinates
  gives |S| ≤ 4·4 = 16. α = 3, so c ≥ 4, and 6·16 ≤ 32·4.

**n ≤ 4** by exhaustion. ∎

*Check.*
- **Exhaustive maxima.** On 2, 3 and 4 bits, the maxima are 0, 1 and
  4 − log₂5, and the maximizers are as stated.
- **Five bits.** A relation above 5 − log₂6 would need at most five points.
  No relation with at most five points exceeds 2.0.
- **The construction.** The Kleitman–Spencer array (columns: the 3-subsets
  of five rows, plus a row of zeros) reaches n − log₂6 for n = 5, …, 10.
- **The inequality** holds for 6 ≤ n ≤ 5000, and T(j+2) ≥ 2T(j) for
  3 ≤ j < 400.

## Theorem 5: statistical capacity

I(R) ≤ min(n, |R| − 1) − log₂|R| ≤ n − log₂(n+1).
- **When equality holds.** Exactly when |R| = n + 1 and every pair of
  coordinates is uniform on R, that is, R is an orthogonal array
  OA(n+1, n, 2, 2). Such arrays exist exactly when a Hadamard matrix of
  order n + 1 does, for example n = 3, 7, 11, 15, 19.
- **On seven bits** the maximizers are exactly 480 relations: the cosets of
  the 30 labelled simplex codes, one for each Fano plane on the seven
  coordinates. So the worlds of seven distinctions that hide the most from
  their pairs statistically are the Fano plane's parity networks, and nothing
  else.

*Proof.*
- **Setup.** Let v_t = (1, (−1)^{t₁}, …, (−1)^{t_n}) and M = E_{u_R}[v vᵀ].
  M depends only on the pair marginals. Let V be its column space, the span
  of the v_t for t ∈ R, and r = dim V ≤ min(n+1, |R|).
- **Support.** p* has the same M. So for c ⊥ V, E_{p*}[(c·v)²] = 0, and the
  support of p* lies in {t : v_t ∈ V}.
- **Counting ±1 vectors.** V has r coordinates on which its projection is
  injective, so it contains at most 2^r vectors of {±1}^(n+1). They come in
  pairs ±v, so at most 2^(r−1) have first entry +1.
- **The bound.** So H(p*) ≤ r − 1 ≤ min(n, |R| − 1). The function
  k ↦ min(n, k−1) − log₂k is largest at k = n + 1.
- **Equality.** Equality needs |R| = n + 1 and H(p*) = n. Then p* is
  uniform, so every pair marginal of u_R is uniform. Conversely, an
  orthogonal array has uniform p*, so I = n − log₂(n+1).
- **Seven bits.** The rows of an OA(8,7,2,2), with a column of ones added,
  form a Hadamard matrix. Its rows are orthogonal, so any two rows of the
  array differ in four places. Translate one row to zero. The other seven
  are weight-4 vectors that meet pairwise in two places. ∎

*Check.*
- **The bound holds** on all 255 three-bit relations and on 60 random
  four-bit relations.
- **Four bits.** The best four-bit relation with all pairs free reaches about
  1.4617, below 4 − log₂5 ≈ 1.678: there is no Hadamard matrix of order 5.
- **Seven bits.** An exhaustive clique search finds exactly 30 seven-sets of
  weight-4 vectors meeting pairwise in two places. All are linear (simplex
  codes), and with their translates they give 480 relations. Each has
  uniform pairs and E = I = 4.

## Theorem 6: affine relations

For an affine relation (a coset of a linear code) I = E, and both are at
most n − ⌈log₂(n+1)⌉. This is attained by the duals of shortened Hamming
codes; at n = 2^m − 1 these are the simplex codes.

*Proof.* Pair marginals of an affine relation are uniform on the pairs it
leaves free, and concentrated on a tie or a constant otherwise.
- **I = E.** u_{pc(R)} has the same pair marginals, and every feasible
  distribution lives in pc(R). So p* = u_{pc(R)} and I = E.
- **The bound.** After deleting constant and tied coordinates, E is the
  codimension of a code whose dual has minimum distance at least 3. The
  Hamming bound gives the limit. ∎

*Check.*
- **Exhaustive for n ≤ 6.** Every subspace of F₂ⁿ is enumerated (2,825 for
  n = 6). With all pairs free, the largest codimension is n − ⌈log₂(n+1)⌉.
- **Constructed for n ≤ 15.** The punctured simplex construction reaches the
  bound.

## Additivity

For relations on disjoint coordinates:
- E(R₁ × R₂) = E(R₁) + E(R₂), because pc(R₁ × R₂) = pc(R₁) × pc(R₂);
- I(R₁ × R₂) = I(R₁) + I(R₂), because the product of the two max-entropy
  distributions has the required marginals and lies in the family.

Checked on 25 random pairs.

## What this means (interpretation, not theorem)

- **Pairs hold nothing.** A world built from pairs determines every global
  fact from the views of its pairs. Exactly at clauses of three literals the
  whole can hold something back: log₂(8/7) bits for one clause, at most one
  bit for one knot, and one bit for parity.
- **The largest emergence is not one knot.** Capacity grows to nearly every
  bit (all but log₂log₂n logically, all but log₂(n+1) statistically). But it
  belongs to tiny worlds of about log n states, codes and covering arrays,
  that are joined by many knots.
- **Frustration is statistically silent.** The not-all-equal triangle is a
  knot in its support, but its pair statistics predict it exactly. Competing
  pairs make support-level emergence and nothing more. Every other knot holds
  correlations no pairwise interaction explains.
- **Reversible worlds agree with themselves.** For affine (parity) worlds the
  two measures coincide. The Fano plane is the most emergent world of seven
  distinctions.

## Scope

- I concerns uniform distributions on relations, not arbitrary distributions,
  where larger divergences are possible.
- Finite checks support, and do not replace, the uniform arguments. The
  inequality of Theorem 4 is checked numerically up to n = 5000 and argued
  beyond.
- The knot status of the clause, the not-all-equal relation and parity was
  confirmed with `knotlab check` before this proof opened.
