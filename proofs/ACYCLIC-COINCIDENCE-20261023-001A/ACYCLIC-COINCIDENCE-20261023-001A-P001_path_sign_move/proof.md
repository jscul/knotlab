# The path-sign move: why non-isomorphic shrunken graphs have equal acyclic counts

Status: Proved

Ticket `ACYCLIC-COINCIDENCE-20261023-001A`, 2026-10-23.

**What it uses:**
- from `TWIST-MAP-20261023-001A-P001`, Theorem 1: a skeleton's count factorizes as N = c · A, where A = T(2, 0) is the number of
  acyclic orientations of the shrunken signed graph (the frame matroid contracted by the skeleton);
- from `TWIST-MAP-20261023-001B-E001`, the residue: six exact twist relations on L(3,1,3,1) whose 48 skeletons have identical
  clusters but shrunken graphs that are neither isomorphic nor Tutte-equivalent, with equal A.

## Standard statement

**Setting.**
- **Signed graphs.** A signed graph has links (two distinct ends) of sign + or −, negative loops and half-edges.
- **Colourings.** For odd λ = 2k + 1, a proper colouring gives each vertex a colour in {−k, …, k}. A link uw of sign σ needs
  c(w) ≠ σ c(u), and a negative loop or half-edge at v needs c(v) ≠ 0. For even λ = 2k, the zero-free colourings use only the
  nonzero colours.
- **Polynomials.** The chromatic polynomial is χ(λ) = Σ_S (−1)^|S| λ^{b(S)}, where b(S) counts the balanced components of the
  spanning subgraph with edge set S; for odd λ it counts proper colourings. The frame matroid has rank r(S) = |V| − b(S) and
  characteristic polynomial p(λ) = Σ_S (−1)^|S| λ^{r(E) − r(S)}, so χ = λ^{b(E)} p and T(x, 0) = (−1)^{r(E)} p(1 − x).
- **A hanging path.** P is a path a = v₀, v₁, …, v_k = b (k ≥ 1, a ≠ b) whose inner vertices meet no other element. Its sign σ_P is
  the product of its edge signs. H is the rest of the graph.

**Lemma 1 (colourings along the path).** Given the colours of a and b, the number of ways to colour the inner vertices properly on
P is

  N = ((λ − 1)^k − (−1)^k) / λ + (−1)^k [c(a) = σ_P c(b)],

for odd λ with the colours −k…k and for even λ with the zero-free colours.

**Theorem 2 (the path-sign move).**
- **Hypothesis.** H contains a positive and a negative link between a and b (a doubled edge, ±K₂).
- **The move.** G′ is G with the sign of one edge of P changed.
- **Conclusion.**
  - G and G′ have the same chromatic polynomial, χ_G = χ_H · ((λ − 1)^k − (−1)^k) / λ.
  - They have the same zero-free chromatic polynomial (the same formula at even λ).
  - Their frame matroids have the same characteristic polynomial and the same T(x, 0).
  - In particular, G and G′ have the same number of acyclic orientations, T(2, 0).
- **Not in the conclusion.** The full Tutte polynomial is not preserved in general. In 149 of 300 random cases it changes, so
  the move is not a matroid isomorphism.

**Corollary 3 (the residue on L(3,1,3,1)).**
- **The move suffices.** Take each of the 48 skeletons behind the six residual relations of `TWIST-MAP-20261023-001B-E001`. The
  second twist's shrunken graph has a hanging path whose ends carry links of both signs. Flipping it makes that graph's frame
  matroid isomorphic to the first twist's, by an explicit bijection of circuits.
- **The move is needed.** Without the flip the two Tutte polynomials differ.
- **The counts follow.** A agrees by Theorem 2, and c agrees because the clusters are identical. So the six relations hold
  skeleton by skeleton.
- **The twist map is complete.** Every exact twist relation that walls and symmetries left on the four fresh genus-2 surfaces
  holds through isomorphic reduced pieces:
  - 25 relations with nothing more;
  - 6 relations with one path-sign move on 48 of their skeletons.

**Remark 4 (what the move hides and what it shows).**
- **Why acyclic counts cannot see it.** The doubled edge forces c(a) ≠ ±c(b). So the only thing the path's sign could decide
  for a colouring, whether c(a) = σ_P c(b), never happens. Acyclic counts (and all of χ) are blind to it.
- **What does see it.** Bases and cyclic counts, T(0, y), see it. In the TWIST-MAP example the two shrunken graphs have 20 and
  21 bases.
- **In the twisted orientation world.**
  - The factor A counts the orientations of the non-skeleton edges that create no new cycle.
  - It cannot see a twist that only changes the sign of a path running beside an unbalanced digon.
  - The factor c (and the cyclic structure) is untouched by such a change only because here the clusters are identical.

**Remark 5 (interpretation, not a theorem).**
- **A local shield.** Two points joined by links of both signs form the smallest odd loop: an unbalanced cycle of length 2. Its
  two constraints are c(a) ≠ c(b) and c(a) ≠ −c(b). Together they cancel the sign of every path between its ends, as far as
  acyclic counts are concerned.
- **The relation to LOOP-SHIELD.** This is the same shape as the lone-loop shield, where an odd loop hides the twist dual to it.
  Here it acts at the scale of a single digon and only for the acyclic factor.

## Nearest known result

- **Classical ingredients.**
  - Zaslavsky's colourings and chromatic polynomials of signed graphs (1982).
  - Zaslavsky's count of acyclic orientations as (−1)^n χ(−1) (1991).
  - The transfer-matrix count of walks in a complete graph.
  - The unsigned version of the closed form: adding a path of length k between adjacent vertices multiplies χ by
    ((λ − 1)^k − (−1)^k)/λ, a clique-cutset gluing along K₂.
- **Theorem 2 is the same gluing along ±K₂.** All proper colourings of ±K₂ extend along the path in the same number of ways.
- **The closest literature found.**
  - Greaves, Syatriadi and Utomo (arXiv:2407.00883, 2024) exhibit simple signed graphs with a common underlying graph and
    common chromatic polynomials that are not switching isomorphic, answering a question of Zaslavsky. Their examples are
    explicit gem graphs, not this move.
  - A 2026 abstract by de Vera studies clique cut sets for zero-free chromatic equivalence.
  - The move itself was not found stated.
- **Folklore risk.** High: the theorem is a few lines from Zaslavsky's framework, and specialists would likely regard it as
  immediate.
- **What is new to the program.** It explains the six relations that `TWIST-MAP-20261023-001` left open, so the genus-2 twist
  map has no unexplained residue.

## Proof

### Lemma 1

- **Switching the inner vertices.** Replacing c(vᵢ) by −c(vᵢ) at an inner vertex maps proper colourings bijectively onto
  proper colourings of the graph with both path edges at vᵢ flipped. This keeps σ_P, and it preserves the palette, both
  {−k, …, k} and the zero-free one.
- **The reduced conditions.** So we may assume edges 1, …, k − 1 are positive and edge k has sign σ_P. The conditions are then
  c(v₁) ≠ c(a), c(vᵢ₊₁) ≠ c(vᵢ), and c(b) ≠ σ_P c(v_{k−1}). The last is the same as c(v_{k−1}) ≠ σ_P c(b), because σ_P = ±1
  and negation is a bijection.
- **Counting walks.** The colourings counted are therefore the walks of length k from c(a) to σ_P c(b) in the complete graph on
  the λ colours. Their number is the (c(a), σ_P c(b)) entry of (J − I)^k = ((λ − 1)^k − (−1)^k)/λ · J + (−1)^k I. This holds
  because J − I has eigenvalue λ − 1 on the all-ones vector and −1 on its complement. ∎

### Theorem 2

- **Restriction and extension.** Every proper colouring of G restricts to a proper colouring of H. Conversely, each proper
  colouring of H extends in exactly N ways, by Lemma 1, since the inner vertices meet only P.
- **The doubled edge.** In every proper colouring of H, the positive link gives c(b) ≠ c(a) and the negative link gives
  c(b) ≠ −c(a). So [c(a) = σ c(b)] = 0 for both signs σ, and N = ((λ − 1)^k − (−1)^k)/λ whatever the sign of P.
- **The chromatic polynomials.** Hence χ_G(λ) = χ_H(λ) · ((λ − 1)^k − (−1)^k)/λ = χ_{G′}(λ) for every odd λ ≥ 1. The same holds
  at every even λ for the zero-free counts. Polynomials that agree at infinitely many points are equal.
- **Balanced components.** The component of a and b is unbalanced in G and in G′, since the two links form a negative digon.
  The other components coincide. So b(E), and with it r(E) = |V| − b(E), is the same for both.
- **The frame matroid.** From χ = λ^{b(E)} p, the characteristic polynomials agree. Then T(x, 0) = (−1)^{r(E)} p(1 − x) agrees.
- **Acyclic orientations.** T(2, 0) is the number of acyclic orientations, by Zaslavsky. In the twisted world it is the factor
  A, by `TWIST-MAP-20261023-001A-P001`, Remark 6. ∎

**On the expansion of χ.** Fix S ⊆ E. The colourings that violate every element of S are counted as follows:
- on a balanced component of (V, S), after switching all its links to positive, the colour is constant: λ choices;
- on an unbalanced component, an unbalanced cycle, negative loop or half-edge forces colour 0 and then 0 throughout: 1 choice.

So the count is λ^{b(S)}, and inclusion–exclusion gives χ(λ) = Σ_S (−1)^|S| λ^{b(S)} at odd λ.

### Corollary 3

- **Rebuilding the residue.** `check.py` rebuilds L(3,1,3,1) by its own construction and reads the 48 skeletons from the
  artifact of `TWIST-MAP-20261023-001B-E001`. For both twists it rebuilds the clusters, their gauges and the shrunken graph
  (simplified by merging parallel elements, which keeps T(x, 0)).
- **Confirming the rebuild.** c = T(0, 2) of the skeleton times A = T(2, 0) of the shrunken graph reproduces all 96 recorded
  skeleton counts.
- **The pairs.**
  - All 48 pairs have equal characteristic polynomials and different Tutte polynomials.
  - In each pair, the second graph has a hanging path with links of both signs between its ends.
  - Flipping that one path gives a frame matroid isomorphic to the first graph's.
- **Conclusion.** Theorem 2 applies, so A agrees. The clusters are identical (`TWIST-MAP-20261023-001B-E001` matched them by
  identity), so c agrees. ∎

## Checks

`check.py` uses the standard library only (seed 20261023). Every result below was obtained:

- **Theorem 2 on 300 random signed graphs.** H has 2 to 4 vertices, a doubled edge and random links, half-edges and negative
  loops; the path has 2 to 4 edges with random signs.
  - The chromatic polynomial, the characteristic polynomial and T(2, 0) are unchanged in all 300 cases.
  - The closed form holds at λ = 3, 5, 7, 9 in all 300.
  - On the 271 graphs with at most six vertices, brute-force colourings agree with the subset expansion at λ = 3 and 5.
  - On the same 271, zero-free colourings at λ = 2 and 4 are unchanged and obey the closed form.
  - The Tutte polynomial changed in 149 cases.
- **Corollary 3 on the 48 residual skeletons.**
  - c · A reproduces the 96 recorded counts.
  - The characteristic polynomials are equal and the Tutte polynomials differ in all 48.
  - One flip gives isomorphic frame matroids in all 48.
- **The six relations.** The check lists them: twists 0111/1111 and 1101/1111 with count 434952 (four relations), and twists
  0011/1011 and 1100/1110 with count 203328 (two relations).
- **Controls, all rejected.**
  - With a link of only one sign between the ends, the flip changes χ in 159 of 300 cases.
  - Through an inner vertex of degree 3, it changes χ in 136 of 300.
  - Shrinking without the clusters' gauges breaks c · A = count on all 48 skeletons.
  - No residual pair is isomorphic without the flip.

## What this does not show

- That the path-sign move accounts for every equality of acyclic counts between non-isomorphic signed graphs. It accounts for
  the 48 skeletons of this residue.
- Anything about the Tutte polynomial away from y = 0, which the move changes.
- Anything about space or physics. Graphs and surfaces are declared.
