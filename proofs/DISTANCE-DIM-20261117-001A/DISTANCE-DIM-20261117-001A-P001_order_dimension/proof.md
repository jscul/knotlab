# Implications read their order and its dimension from the states

Status: Proved

Ticket `DISTANCE-DIM-20261117-001A`, 17 November 2026, by Claude. Epic `DISTANCE-DIM-20261117-001`. The proofs are below.
`check.py` checks D1 to D3 on 400 random orders of up to eight elements, D4 on small chain grids, and D5's formula. That is a
check, not the proof.

## Words

- **Implication base.** Let P be a finite order (a poset). Its implication base has one distinction for each element and the
  two-place implications u → v for u < v. Its allowed states are exactly the up-sets of P: the sets that contain everything above
  each of their members.
- **Disagreement count** d(u, v) and **between** are as in `DISTANCE-ORDER-20261117-001A`. Here d(u, v) is the number of up-sets
  that contain exactly one of u and v.
- **Order dimension.** The least number of linear orders whose intersection is P (Dushnik and Miller 1941). It is the same for P
  and its reverse.

## Statements

- **D1. Betweenness is the order's intervals.** In an implication base, w lies between u and v (d(u, v) = d(u, w) + d(w, v)) iff
  u ≤ w ≤ v or v ≤ w ≤ u. For distinct elements, every count is positive.
- **D2. Pairs read comparability.** In an implication base, u and v are comparable iff one of the joint patterns 00, 01, 10, 11
  never occurs; for u < v it is 10. In a not-all-equal base with no tie, every pair shows all four.
- **D3. Betweenness reads the order up to reversal.**
  - If every comparable pair of P lies in a chain of three, then the pairs occurring together in a strict betweenness triple are
    exactly the comparable pairs.
  - If P is moreover connected, betweenness determines P up to reversal.
  - So the order dimension of P is read from the allowed states. On a chain it is 1, on a product of two chains of length at least
    two it is 2, and on a product of three it is 3.
- **D4. The chain grid has no betweenness among its grid distinctions.** Take the not-all-equal chain grid: the square grid on a
  torus, each edge one knot (u, p, v) with a private distinction p. Every assignment of values to the grid distinctions extends to
  an allowed state. So every pattern on three of them occurs, and none lies between two others.
- **D5. The chain grid is an Ising model above its critical point.** Summing out the private distinctions gives each edge weight 1
  when its ends agree and 2 when they differ. That is the Ising model with tanh K = −1/3 on the square grid, and |tanh K| = 1/3 <
  √2 − 1, so it is above the critical point. By Onsager, the correlation length along an axis is 1/ξ = ln coth|K| − 2|K| = ln 3 −
  ln 2 = ln(3/2), that is 1 − log₃ 2 ≈ 0.3691 per step in base 3. Every private distinction's conditional mean is −(s_u + s_v)/2,
  so its correlations follow from the grid's.

## Proofs

**D1.** Suppose u ≤ w ≤ v. An up-set with x_u = x_v = 1 contains u, so it contains w. An up-set with x_u = x_v = 0 misses v, so it
misses w, since w ≤ v. So no state has x_u = x_v ≠ x_w, and by statement 1 of `DISTANCE-ORDER-20261117-001A`, w lies between u and
v. The case v ≤ w ≤ u is the same.

Conversely, suppose w is distinct from u and v and no state has x_u = x_v ≠ x_w.
- If w ≥ neither u nor v, the up-set ↑u ∪ ↑v contains u and v and not w, which is such a state.
- If w ≤ neither u nor v, the up-set P \ (↓u ∪ ↓v) contains w and neither u nor v, which is such a state.
- So w ≥ u or w ≥ v, and w ≤ u or w ≤ v. Since w is distinct from u and v, this forces u ≤ w ≤ v or v ≤ w ≤ u.

For distinct u and v, one of ↑u and ↑v contains exactly one of them, so d(u, v) > 0. ∎

**D2.** If u < v, no up-set contains u and not v, so 10 never occurs. If u and v are incomparable, ↑u gives 10, ↑v gives 01, the
empty up-set gives 00 and P gives 11. In a not-all-equal base every pair's patterns are closed under flipping both. So a pair
missing one pattern misses its flip too, and keeps 00 and 11 only (a tie u = v) or 01 and 10 only (a tie u ≠ v). With no tie, all
four occur. ∎

**D3.** By D1, a strict triple is a chain of three, and its three pairs are comparable. Conversely, a comparable pair in a chain of
three occurs in that chain's triple.

Now let P be connected, with every comparable pair in a chain of three. Take two comparable pairs {x, w} and {w, y} that share w.
- If x and y are comparable, the three form a chain, and betweenness names its middle. If the middle is w, the two pairs point the
  same way through w. If the middle is x or y, both pairs are ordered by that chain.
- If x and y are incomparable, w is above both or below both.

Either way the orientation of one pair fixes the other. Every comparable pair is linked to every other through a sequence of
comparable pairs sharing an element, since P is connected and each comparable pair lies in a chain of three. So the orientation
of one pair fixes all of them: P or its reverse.

Order dimension is the same for P and its reverse. It depends only on the comparability graph (Gallai 1967; Trotter, Moore and
Sumner 1976). For a product of D chains of length at least two:
- the D coordinate orders, each broken by the remaining coordinates, form a realizer;
- the product contains the Boolean lattice 2^D, whose dimension is D (Komm 1948).
So its dimension is D. ∎

**D4.** Fix values on the grid distinctions. For each edge (u, v): if u = v, the knot forces p to the other value; if u ≠ v, p is
free. No other knot touches p. So every assignment extends. A strict betweenness among grid distinctions a, b, c needs a pattern
a = b ≠ c never to occur (statement 1 of `DISTANCE-ORDER-20261117-001A`), and every pattern occurs. ∎

**D5.** For one edge, summing over p gives 1 way when u = v and 2 ways when u ≠ v. These are the Boltzmann weights e^{K s_u s_v}
up to a constant, with e^{2K} = 1/2, so tanh K = (1 − 2)/(1 + 2) = −1/3. The square grid is bipartite, so flipping one sublattice
maps the model to the ferromagnet with tanh K = 1/3, and correlations keep their size. The critical point is tanh K_c = √2 − 1
≈ 0.414, so 1/3 lies above it. Onsager's row correlation length above the critical point gives 1/ξ = ln coth K − 2K, with
coth K = 3 and 2K = ln 2. The conditional mean of s_p given the grid is −s_u when s_u = s_v, since p is forced, and 0 when they
differ, since p is free; both are −(s_u + s_v)/2. ∎

## Provenance

- **D1** is folklore level, and no novelty is claimed. In symmetric-difference terms d(u, v) = |F_u Δ F_v|, with F_u the up-sets
  containing u. Betweenness F_u ∩ F_v ⊆ F_w ⊆ F_u ∪ F_v is standard for such metrics (Glivenko 1936; Pitcher and Smiley 1942).
  The content here is that for these sets it is the order interval.
- **D2** is elementary.
- **D3** cites the comparability invariance of dimension (Gallai; Trotter, Moore and Sumner) and Komm for the Boolean lattice. The
  up-to-reversal argument is the advisor's, checked here.
- **D4** is elementary.
- **D5** is Onsager 1944, applied.
- **The advisor** was consulted twice before the freeze. It confirmed D1, and gave D3's hypothesis and argument, D4's
  full-support proof and D5's slope.
