<!-- modelUsage: claude-fable-5-2 -->

Everything below is derived by hand, with nothing run; I mark what is proved, what is a sketch, and what is a conjecture to test.

## A. Soundness of δ

**|κ_S| can exceed 1, so the clamp is essential.**
- The base {0000, 1111} gives κ₄ = 1 − 3 = −2.
- For fully locked spins, |κ_{2j}| follows the tangent numbers 1, 2, 16, 272, 7936, …, which outgrow 3^{2j−2} from |S| = 10. Without the clamp δ is unbounded below on ordered bases.
- With the clamp, δ ≥ |S| − 2 for every S. So δ ≥ 0, δ = 0 only for copies or complements, and the search is finite: only sets with |S| ≤ (current best) + 2 matter.
- The triangle inequality is not automatic. It holds on trees, but I have no general proof.

**(1) and (2) are right.** Complement closure sends κ_S to (−1)^{|S|} κ_S, so odd cumulants vanish, all means are 0 and κ_xy = C.

**Parity trees: δ = k exactly (proved).**
- Moments on a linear base are 1 if the set is a dual codeword (a sum of checks) and 0 otherwise.
- The sum of the k path knots has support T = {x, y, one third-variable per path knot}, so |T| = k + 2.
- A proper sub-codeword of T would be a sum over a proper subset A of the knots. Its support contains a shared variable at the boundary of A, which is not in T. So no proper subset of T carries a moment, and κ_T = +1 exactly.
- Lower bound: if S omits the third variable p_j of path knot j, no codeword inside S uses knot j. Codewords in S then split into left and right parts with disjoint supports, so S∩left and S∩right are independent and κ_S = 0. Hence |S| ≥ k + 2.
- A codeword that skips middle knots, such as K₁ + K_k of size 6, has κ = 1 − 1 = 0, so it is no shortcut.

**Mixed trees: δ ≤ k by an exact identity; the lower bound is a conjecture.**
- Write η_j = s_{m_{j−1}} s_{m_j} across path knot j. The η_j are independent of each other and of s_x. For a parity knot η_j = s_{p_j} (the pendant, mean 0); for an NAE knot E[η_j] = −1/3.
- Take S = {x, y} ∪ {pendants of the parity knots on the path}. The only sub-block with a nonzero moment is S itself, so κ_S = (−1/3)^a exactly, where a is the number of NAE knots.
- With b parity knots, δ ≤ b + a = k. Smallest case: parity {x, p, m} glued to NAE {m, q, y} gives C(x,y) = 0 and κ_{xpy} = −1/3, so δ = 2.
- Mixed bases are not complement-closed, so odd cumulants are live here.

**NAE trees: no 4-set shortcut (proved); |S| ≥ 6 is open.**
- On a flip-symmetric tree, if one variable w separates {x,u} from {y,v} (w may be one of the four), then E[xuyv] = E[xu]E[yv]. The reason is that even functions of one side are independent of w.
- So κ₄ = −2·3^{−(d(x,y)+d(u,v))} when the separated pairing is xu|yv, and −2·3^{−(d(x,u)+d(y,v))} with d(x,u)+d(y,v) ≥ k+2 when it is xy|uv.
- Such a separator exists for every 4-set unless x and y share a knot (k = 1). Either way 2 + τ(κ₄) > k.
- For |S| ≥ 6 the same argument gives |κ_S| ≤ A_m·3^{−k}, where A_m is the absolute coefficient sum. A shortcut needs A_m > 3^{m−2}. I have not bounded A₆ or A₈, and for m ≥ 10 the crude bound fails. I expect no shortcut, because true cumulants carry extra powers (compare p+2q+r with p+q+r), but this needs enumeration.

## B. Cubic parity, chain grid, weave

**Every parity base: δ = bond distance − 1 (theorem).**
- A "knot set" (constrained as a whole, every proper subset free) is a circuit of the matroid of dual codewords. A circuit has κ = ±1, so δ ≤ |circuit| − 2.
- Conversely, κ_S ≠ 0 means S does not split into independent parts, so the restricted matroid M|S is connected. In a connected matroid any two elements lie in a common circuit, which sits inside S.
- So δ(x,y) = (smallest circuit through x and y) − 2, and ∞ if there is none.
- On the cubic system, circuits are graph bonds δA with A and its complement connected. Two edges at a common vertex give δ = 4. A tree-like A with m vertices has |δA| = 4m + 2, so δ = 4m. This is consistent with r³ balls.

**Chain grid: δ = τ on node pairs (sketch, one number to check).**
- Summing out the chains gives a nearest-neighbour Ising model with tanh K = 3^{−L} ≤ 1/3 < √2 − 1, gauge-ferromagnetic on the bipartite grid.
- Griffiths II gives ⟨xz⟩ ≥ ⟨xy⟩⟨yz⟩, so τ is a genuine metric there.
- Lebowitz gives κ₄ ≤ 0. The Aizenman tree bound (quoted from memory; verify its form) is |κ₄| ≤ 2 Σ_z ⟨xz⟩⟨yz⟩⟨uz⟩⟨vz⟩ ≤ 2⟨xy⟩·Σ_z⟨uz⟩⟨zv⟩.
- So no 4-set shortcut if the bubble Σ_z⟨0z⟩² is at most 4.5. I estimate about 2–3 at tanh K = 1/3, but this is unverified.
- Sets containing chain-interior or pendant variables need the tree-separator lemma from A in addition.

**Critical weave: no shortcut asymptotically (heuristic).** κ₄ ≈ −2C² plus an energy-channel term of order r^{−2}, against the needed 9|C| ~ r^{−1/4}. Short range needs a numerical check.

**"Decays like the Steiner tree" is only an upper bound.** In zero field the true rate double-covers the middle: the chain gives −2θ^{p+2q+r}.

## C. Switching

**The obstruction is real, and total in one dimension.**
- For the split line on points 0..n, put the N = 2(n+1) states on a cycle. Column i is a half-circle at phase i, and its complement is the half-circle at phase i + n + 1.
- Rotating the cycle by one step maps the base to itself via i → i+1, n → ¬0. I checked n = 2 by hand.
- So up to switching the split line is a circle of n + 1 points, with the endpoints adjacent. No switching-invariant statistic of any order can read the line's L1.
- What is readable is the wrapped distance min(L1, N/2 − L1), which is exactly what |C| gives.

**In 2D the far corner wraps too.** With N = 2(a+b+1), ¬(a,b) has |C| identical to a phantom point at (−1,0) against every grid point. Whether the 2D class is rigid (no extra automorphism) I do not know; it is a small computation.

**Your proposed fix does not work.** Switching by any state of a complement-closed base produces another base containing both all-equal states. On the line it produces another betweenness line with a different order. "Contains the constant states" leaves N/2 gauges.

**Your three candidates:**
- Pair mutual information is an even function of C, so it folds identically.
- |κ_S| is switching-invariant for every S, but it cannot beat the automorphism. On the line, κ₄ = −2 + 4(p+2q+r) − 8(pr+pq+qr+q²), with gaps in units of n+1.
- "States where a 3-set is constant" is not invariant, because the constant class moves. The multiset of the four class counts is invariant, and an empty class marks a knotted triple.

**What the pair data does carry.** Beyond |C| there are the cycle signs sign(C_ab C_bc C_ca), which form the two-graph. Together they give C up to switching and nothing more. On the line, even the "most ferromagnetic gauge" ties exactly: left half versus right half has ΣC = 0.

**Consequence.** Either values are data, in which case signed C reads 2·L1 directly, or the invariant geometry of a split grid is the wrapped one.

**A second problem for δ on split grids.** Here δ = −log₃|1 − 4L1/N|, which is about 3.64·L1/N for near pairs. Four-sets then cap it at about 2 + log₃2 ≈ 2.63, since κ₄ = −8pr = −1/2 at C = 0. So δ is in knot units and saturates on dense ordered bases.

## D. Recommendation

Do (ii), sharpened around the two theorems. The ladder (i) has no crisp pass/fail by comparison. Frozen predictions:

| # | Prediction | Fail condition |
|---|---|---|
| 1 | On every linear base, δ = min circuit through the pair − 2; circuits have κ = ±1 | Any S smaller than that circuit with κ_S ≠ 0 |
| 2 | Cubic block (periodic): edges at a common vertex δ = 4; opposite edges of a square δ = 8 | Any other value |
| 3 | NAE trees, k ≤ 6, all S with \|S\| ≤ k+1: δ = k; separated 4-sets have κ₄ = −2·3^{−D} as in A | Any S with (\|S\|−2) + τ < k (watch \|S\| = 6, 8) |
| 4 | Mixed trees: κ of {x,y} ∪ parity pendants = (−1/3)^a exactly, and δ = k | Identity off, or a smaller set wins |
| 5 | Chain grid L = 1: bubble ≤ 4.5; min over 4-sets of 2 + τ(κ₄) − τ(C) > 0 | Either fails |
| 6 | Weave patch: same margin positive at all separations in the patch | Any non-positive margin |
| 7 | Split line: every \|κ_S\| invariant under i → i+1 mod n+1; κ₄ matches the formula; δ capped near 2.63 | Any asymmetry or a different cap |
| 8 | Split grid a,b ≥ 2: ¬(a,b) matches phantom (−1,0) in \|C\|; record the automorphism group of signed C modulo switching | Mismatch; an extra automorphism means L1 is unreadable in 2D too |

## E. Literature and what would be new

- **Cumulants:** Ursell functions (Ursell; Sylvester 1975); Lebowitz and GHS inequalities; Aizenman's tree bound; strong cluster properties (Duneau–Iagolnitzer–Souillard); partition-lattice cumulants (Speed, Rota).
- **Tree metrics:** −log|ρ| is additive on trees. This is the Cavender–Farris–Neyman and log-det distance of phylogenetics (Steel), and the "information distance" of latent-tree learning (Choi–Tan–Anandkumar–Willsky); also Chow–Liu. Your proved τ = steps on NAE trees is this.
- **Irreducible k-body correlation:** connected information (Schneidman–Still–Berry–Bialek 2003) and Linden–Popescu–Wootters match "constrained as a whole, subsets free"; parity is their canonical example.
- **Matroids:** circuits through pairs and connectivity (Tutte).
- **Switching:** Seidel switching and two-graphs; signed-graph balance (Harary, Zaslavsky); gauge and frustration (Toulouse, Mattis).
- **Cuts:** the cut cone and L1-embeddability (Deza–Laurent); circular split systems (Bandelt–Dress). "Count = 2·L1" is a cut decomposition, and the line's splits being circular is the circle result.

As far as I know, these would be new:
- the single functional (|S| − 2) + τ(κ_S) with the clamp;
- the exact identities: δ = circuit − 2 on linear bases, and κ = (−1/3)^a on mixed trees;
- the statement that a split line is a circle up to switching, with the resulting saturation of δ.

Each is easy once seen, so a targeted literature check is warranted before claiming novelty.
