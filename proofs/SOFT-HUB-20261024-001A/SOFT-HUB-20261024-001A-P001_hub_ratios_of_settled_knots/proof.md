# Hub ratios of the settled knots

Status: Proved

Ticket `SOFT-HUB-20261024-001A`, 2026-10-24.

**What it uses:**
- from `SURFACE-GLUING-20261024-001B-P001`: hub-free gluing, self-gluing and pinning keep relations co-independent (no two excluded
  tuples adjacent); forgetting one variable of a co-independent relation leaves the rest unconstrained (Lemma 1); a co-independent
  relation on n ≥ 1 variables excludes at most 2^(n−1) tuples (Lemma 4);
- from `NATIVE-APPROX-20261024-001A-P001`: the eight non-windable knots exclude three tuples, a parity class minus one tuple; every
  knot, both pins and the free unary function are strictly terraced;
- from `NATIVE-COUNTING-20261024-001A-P001`: the no-lone-1 knot is λ₀ v₀^⊗3 + λ₁ v₁^⊗3 with orthonormal v₀ = (1, φ)/D and
  v₁ = (φ, −1)/D;
- an external theorem, cited as a hypothesis and not admitted as local evidence:
  - **(M)** McQuillan, *Approximating Holant problems by winding* (arXiv:1301.2880): strictly terraced windable functions are closed
    under connected circuits (Theorem 4), and a function F on three bits is windable exactly when F(x)F(x̄) is at most the sum of the
    three split products of x, for every x (Theorem 6).

## Standard statement

**Setting.**
- **Gadgets.** A *gadget* of a knot R is a native network of copies of R with pins, *free legs* (unpinned legs that are summed over)
  and three *terminals* (unpinned legs whose values are recorded). F(x) is the number of its consistent assignments with terminal
  values x ∈ {0, 1}³.
- **Axes and hub ratio.**
  - An *axis* is an antipodal pair {u, ū}.
  - The *split products* of u are s_u(F) = Σᵢ F(u + eᵢ) F(ū + eᵢ), over the three places i.
  - The *hub ratio* along u is ρ_u(F) = min(F(u), F(ū)) / max{F(x) : x ∉ {u, ū}}.
  - A *soft hub* has ρ_u > 1. An *exact hub* has F(u), F(ū) > 0 and F = 0 elsewhere; for u = 000 this is the equality on three legs.
- **Difference graphs.** For two assignments σ, τ of one gadget, the *difference* is the set of edges, terminals and free legs on which
  they differ. Two of these are *joined* when they meet at a knot, and the classes form the *components* of the difference.
  - A pair (σ, τ) with terminal values (u, ū) is *linked* if one component contains all three terminals, and *separated* otherwise.
  - A knot *branches* in a pair when all three of its slots differ, so that its two local tuples are antipodal.

**Theorem 1 (no exact hub).** For every knot, the support of every gadget is co-independent and excludes at most four of the eight
terminal values. So no gadget is an exact hub along any axis. More generally, no gadget with k ≥ 3 terminals is supported exactly on
an antipodal pair of {0, 1}^k.

**Lemma 2 (exchange).** For every gadget of every knot, and every axis u:
- F(u) F(ū) = sep_u + link_u, where sep_u and link_u count the separated and the linked pairs with terminal values (u, ū);
- exchanging σ and τ on the component of terminal 1 maps the separated pairs injectively onto pairs with terminal values
  (u + X, ū + X), with X ∈ {e₁, e₁ + e₂, e₁ + e₃};
- hence sep_u ≤ s_u(F), and so F(u) F(ū) ≤ s_u(F) + link_u.

**Lemma 3 (linked pairs branch).**
- Every linked pair has a knot that branches.
- Parity knots allow no antipodal pair, so their gadgets have no linked pairs.

**Theorem 4 (windable knots, given M).** For each of the 26 windable knots, every gadget satisfies F(u)F(ū) ≤ s_u(F) for every u.
So ρ_u ≤ √3 along every axis.

**Theorem 5 (topological knots).**
- **(a) Parity.** Every gadget of a parity knot is constant on its support, and ρ_u ≤ 1 along every axis.
- **(b) No lone value.** Every connected gadget of the no-lone-1 knot depends only on the number w of terminals equal to 1. Its values
  f₀, f₁, f₂, f₃ satisfy the Fibonacci recurrence f₂ = f₀ + f₁ and f₃ = f₁ + f₂. Gadgets of the no-lone-0 knot satisfy the mirror
  recurrence f₁ = f₂ + f₃, f₀ = f₁ + f₂. In both cases ρ_u ≤ 1 along every axis.

**Proposition 6 (the eight non-windable knots).**
- **The shape.** Each knot excluding three tuples is R_c = N[c] ∪ {c̄}: a closed neighbourhood plus the antipode of its centre, for
  exactly one c.
  - The no-lone knots have constant c.
  - The six open knots have non-constant c.
- **Rigidity.** In R_c:
  - the only allowed antipodal pair is {c, c̄}, and exchanging one or two of its places never gives two allowed tuples;
  - every allowed pair at distance two has an excluded intermediate.
- **Consequence.** In a gadget of one of these knots, every exchange of σ and τ that keeps both valid is a union of whole components.
  So no exchange splits a linked pair, and the knots where a linked pair branches have local tuples c and c̄: all three slots are
  defects on one side and none on the other.

**Corollary 7 (where strong hubs could come from).**
- Every knot except the six open knots has ρ_u ≤ √3 for every gadget and axis. This is given M for the windable knots, and
  unconditional for the parity and no-lone knots.
- For the six, ρ_u ≤ √(3 + link_u / M_u²), where M_u is the largest value off the axis. So a bound link_u ≤ M_u² would give ρ_u ≤ 2.

**Reading.**
- **Emergence cannot imitate a hub exactly.** This holds for every knot, by co-independence.
- **The question is now about linked pairs.** Pairs of solutions that do not tie all three terminals together can always be
  rerouted onto off-diagonal values, so they never make a hub. Only linked pairs can.
  - For the windable knots, McQuillan's winding absorbs them.
  - For the six open knots, they pass through knots that are empty on one side and full on the other, where no rerouting is possible.

## Nearest known result

- **The windable bound** is immediate from McQuillan's Theorems 4 and 6.
- **The exchange lemma** is the elementary core of the winding argument: paths of the symmetric difference are switched as wholes.
- **The impossibility of exact hubs** follows from co-independence (`SURFACE-GLUING-20261024-001B`).
- **The local content** is:
  - the hub-ratio framing for native networks;
  - the bounds for the parity and no-lone gadgets;
  - the closed-neighbourhood description and rigidity of the eight non-windable knots;
  - the reduction of the open question to linked pairs.
- **Novelty:** elementary; folklore risk high for Lemmas 2 and 3 and Theorem 1, medium for Proposition 6 and Corollary 7.

## Proof

### Theorem 1

- **Supports are co-independent.** The support of a gadget is obtained from copies of R by gluing (each internal edge), self-gluing (a
  loop) and pinning. Each keeps co-independence (Lemmas 2 and 3 of `SURFACE-GLUING-20261024-001B`). A free leg quantifies one
  variable, which leaves the rest unconstrained (Lemma 1 there).
- **The count.** A co-independent relation on k variables excludes at most 2^(k−1) tuples (Lemma 4 there). An exact hub along an axis
  excludes 2^k − 2 tuples, which is more than 2^(k−1) when k ≥ 3. ∎

### Lemma 2

- **Exchange on whole components is valid.** Let (σ, τ) be a pair with terminal values (u, ū), and let K be the component of terminal 1.
  Define σ' to agree with τ on K and with σ elsewhere, and τ' likewise.
  - At every knot, either none of its differing slots lies in K, or all of them do, because the slots that differ at one knot are
    joined.
  - So each knot of σ' carries the local tuple of σ or of τ, and likewise for τ'. Both are consistent, and pins never differ.
- **The terminal values.** Terminal 1 lies in K. If the pair is separated, K misses terminal 2 or terminal 3.
  - So the terminals in K form X ∈ {e₁, e₁ + e₂, e₁ + e₃}.
  - σ' and τ' have terminal values u + X and ū + X, which are the three split patterns of u.
- **Injectivity.** The pair (σ', τ') has the same difference, so the same component K, and exchanging again returns (σ, τ). The map is
  an involution on separated pairs, hence injective.
- **Conclusion.** The separated pairs sent to pattern X number at most F(u + X) F(ū + X). Summing over the three patterns gives
  sep_u ≤ s_u(F). ∎

### Lemma 3

- **A branching knot exists.** Consider the component containing all three terminals as a multigraph. Its nodes are the knots with a
  differing slot in it and the terminal and free-leg ends; each knot has degree at most 3.
  - A connected multigraph of maximum degree at most 2 is a path or a cycle, with at most two leaves. This one has three terminal
    leaves.
  - So some knot has degree 3: all three of its slots differ, and its local tuples are antipodal.
- **Parity.** In a parity knot an antipodal pair has opposite parities, so one of its tuples is excluded. ∎

### Theorem 4

- **The gadget is windable.** The knot, the pins and the free unary function are strictly terraced (`NATIVE-APPROX-20261024-001A`,
  Lemma 1) and windable (there, Corollary 3). By (M) Theorem 4, a connected gadget is windable, and by (M) Theorem 6 it satisfies
  F(u)F(ū) ≤ s_u(F) for every u.
- **Disconnected gadgets.** They are products, covered by the remark below.
- **The ratio.** min(F(u), F(ū))² ≤ F(u)F(ū) ≤ s_u(F) ≤ 3 M_u². ∎

**Remark (products).** Suppose a gadget splits into parts with disjoint, non-empty terminal sets T₁ and T₂, so F = g(x_T₁) h(x_T₂).
Let y = u + e_T₁, which flips the places in T₁. Then F(u)F(ū) = F(y)F(ȳ), and y is off the axis. So min(F(u), F(ū))² ≤ M_u², and
ρ_u ≤ 1. Parts without terminals only multiply F by a constant.

### Theorem 5

- **(a) Parity gadgets.**
  - **Constant on the support.** A parity gadget is a linear system over GF(2) in the edges, free legs and terminals. With the
    terminals fixed to x, it has either no solution or 2^d solutions, where d is the dimension of the homogeneous solution space with
    the terminals fixed to 0, which does not depend on x.
  - **The ratio.** F is constant on its support A, an affine subspace.
    - If u and ū both lie in A together with some value off the axis, then ρ_u = 1.
    - If one of u, ū is missing from A, then ρ_u = 0.
    - A = {u, ū} would exclude six values, which Theorem 1 forbids.
- **(b) No-lone gadgets.**
  - **One spin.** Write the no-lone-1 knot as Σⱼ λⱼ vⱼ^⊗3. Contracting an internal edge gives Σₑ vⱼ(e) vₖ(e) = δⱼₖ by
    orthonormality, so all knots of a connected gadget carry one index j.
  - **The form.** Hence F(x) = α ∏ᵢ v₀(xᵢ) + β ∏ᵢ v₁(xᵢ), where α and β collect λⱼⁿ, the pins vⱼ(p) and the free legs
    vⱼ(0) + vⱼ(1). So F depends only on w = Σ xᵢ, with D³ f_w = α φ^w + β (−1)^w φ^(3−w).
  - **The recurrence.** Using φ² = φ + 1:
    - D³ (f₀ + f₁) = α(1 + φ) + β(φ³ − φ²) = αφ² + βφ = D³ f₂;
    - D³ (f₁ + f₂) = α(φ + φ²) + β(φ − φ²) = αφ³ − β = D³ f₃.
  - **The ratio.**
    - Along 000: f₀ ≤ f₂, a value off the axis.
    - Along an axis {u, ū} with u of weight 1: f₃ = f₁ + f₂ ≥ min(f₁, f₂), and the value 111 is off the axis.
    - So ρ_u ≤ 1 along every axis.
  - **The no-lone-0 knot** is the global complement, f'_w = f_(3−w), which gives the mirror recurrence and the same bound.
  - **Disconnected gadgets** are covered by the remark. ∎

### Proposition 6

- **The shape.** The excluded set is P \ {c} for a parity class P and some c ∈ P (`NATIVE-APPROX-20261024-001A`). The allowed set is
  the other class Q together with c. Q consists of the three neighbours of c and of c̄, so the allowed set is N[c] ∪ {c̄}. The centre is
  the unique allowed tuple whose three neighbours are all allowed.
- **Antipodal pairs.** For a neighbour aᵢ = c + eᵢ, the antipode c̄ + eᵢ lies at distance two from c and is not c̄, so it is excluded.
  - Exchanging place i of the pair (c, c̄) needs c + eᵢ and c̄ + eᵢ, and the second is excluded.
  - Exchanging two places is the same as exchanging the third, with the two tuples swapped.
- **Distance two.**
  - The pair (aᵢ, aⱼ) has intermediates c and c + eᵢ + eⱼ; the second is excluded.
  - The pair (aᵢ, c̄) has both intermediates at distance two from c and different from c̄, so both are excluded.
- **Consequence.** Let an exchange of σ and τ split the differing slots of some knot.
  - With two differing slots, the knot would need both intermediates allowed.
  - With three, it would need a one-place exchange of (c, c̄).
  - Both fail. So valid exchanges are unions of whole components, and a branching knot has local tuples c and c̄. ∎

### Corollary 7

- **The settled knots.** By Theorems 4 and 5.
- **The six.** By Lemma 2, F(u)F(ū) ≤ 3 M_u² + link_u, and min(F(u), F(ū))² ≤ F(u)F(ū). ∎

## Checks

`check.py` uses the standard library only (seed 20261024). It enumerates 476 random gadgets of all 34 knots, with up to six knots and
fifteen unpinned variables. It confirms:
- **Theorem 1.**
  - Every support is co-independent and excludes at most four values; none is an exact hub.
  - Exhaustively, no co-independent relation on three bits excludes more than four tuples.
- **Lemmas 2 and 3.** On 1,898 gadget-axis cases, with 439,439 pairs of which 80,129 are linked:
  - the exchange is valid, injective, and lands on the split patterns;
  - the counts add up, and sep_u ≤ s_u;
  - every linked pair has a branching knot with antipodal local tuples;
  - parity gadgets have no linked pairs.
- **Theorem 4, as a consistency check given M.** F(u)F(ū) ≤ s_u on all 1,450 windable gadget-axis cases.
- **Theorem 5.**
  - All 28 parity gadgets are constant on their support, with ρ_u ≤ 1.
  - All 28 no-lone gadgets satisfy the recurrence and have ρ_u ≤ 1.
- **Proposition 6.**
  - The eight knots are the R_c, with a unique centre each, and their rigidity is verified.
  - 32 knots allow an antipodal pair: all but parity.

**Controls.**
- **A real hub is detected.** Three equality wires sharing one variable, which is a hub and not native, give the equality on three legs.
  The co-independence test rejects that support.
- **Whole components matter.** Exchanging only terminal 1's own edge, instead of its whole component, gives an invalid assignment on
  some pair of an open-knot gadget.
- **The inequality can fail.** The open knot excluding 000, 011 and 101 violates F(u)F(ū) ≤ s_u along the axis 110.

## What this does not show

- **A bound for the six open knots.** Their linked pairs are not bounded here; tickets B and C examine them.
- **A proof of M.** The windable bound is conditional.
- **Anything about approximate counting itself.** A bounded hub ratio closes the hub-imitation route to hardness, but proves no
  approximation scheme.
