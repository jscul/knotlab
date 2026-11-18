<!-- modelUsage: claude-fable-5-2 -->

**Short version:** I can give you an exact, cheaply computable criterion for constrained sets, and from it a proof of b ≥ steps + 1 on every disc patch and a proof that any bond through opposite-kind corners has a special "figure-eight" form. I cannot prove b ≤ steps + 1, the existence of bonds for all other pairs, or a closed-form geometric criterion for question 1. Nothing below has been machine-checked.

## The tool: a cycle criterion

Orient every edge so that up triangles are counterclockwise; the forward directions are e1 = (1,0), e2 = (−1,1), e3 = (0,−1). On a disc patch, states (mod global flip) are height functions h with h(v) ≡ i+2j (mod 3), increment +1 or −2 along each forward edge, and spin = parity of h.

Let D(s,t) be the shortest directed path weight inside the patch, with forward edges costing 1 and backward edges 2. Then h(t) − h(s) takes exactly the values of the right residue in [−D(t,s), D(s,t)], and any values on S respecting these bounds extend to a state.

**Criterion.** S is constrained iff it contains m ≥ 3 distinct points in some cyclic order with Σ D(sᵢ, sᵢ₊₁) ≤ 3(m−2).

Sketch: fixing spins on S fixes h mod 6 there. Writing h = r + 6k gives difference constraints on k with weights ⌊(D − Δr)/6⌋, which are infeasible iff there is a negative cycle. Each term is an integer or half-integer, and the parities can be chosen to lose ½ on all edges of a cycle (all but one if the parity is wrong), which gives the inequality.

**Consequences for a bond S of size m:**
- The cycle uses all of S and has ΣD = 3(m−2) exactly.
- Every point is "on the way": D(s₋,s) + D(s,s₊) = D(s₋,s₊).
- Every proper sub-collection, in any order, has ΣD ≥ 3(|T|−1).

## Question 2

**Lemma (proved, given one standard fact): D(x,y) + D(y,x) = 3·steps(x,y) on every disc patch.**

- **≤:** go out along a geodesic and back along it; each edge costs 1 + 2.
- **≥:** let δ = steps from x. No triangle has δ constant. This is the fact I rely on: disc patches are systolic (bridged) complexes, where equidistant adjacent vertices have a common neighbour one step closer and balls are convex; the lattice has no K4.
- So each triangle has exactly one forward edge where δ decreases and one where it increases. Putting the −2 on the decreasing edges gives a state h₁; putting it on the increasing edges gives h₂.
- Then (h₁ − h₂)(y) − (h₁ − h₂)(x) = 3δ(y), and D(x,y) ≥ h₁(y) − h₁(x), D(y,x) ≥ h₂(x) − h₂(y).

**b ≥ steps + 1 always (proved).** A bond's cycle through x and y has weight 3(m−2) ≥ D(x,y) + D(y,x) = 3·steps. More generally, every bond has diameter ≤ |S| − 2.

**b ≤ steps + 1 when a bond exists: not proved.** It needs steps + 2 once-visited points on a weight-3·steps closed walk through x and y with no constrained sub-collection. The shapes vary: a side plus the apex of an up triangle, or {(0,0),(2,0),(1,1),(0,1)} in a one-row strip. I found no uniform construction.

## Question 3

I can prove the "opposite kinds" part only as a structure theorem, not the full necessary condition.

- **A corner is the midpoint of a backward edge.** For a corner x with forward order x→u→v→x, D(s,x) = D(s,v) + 1 and D(x,t) = 1 + D(u,t). So a bond's walk passes v→x→u, with the triangle on its left at an up corner and on its right at a down corner.
- **No simple loop through opposite corners.** A simple closed walk in a disc encloses only patch, so it must be counterclockwise at an up corner and clockwise at a down corner. It cannot pass through one of each.
- **Splitting.** If a bond's walk revisits a vertex w, then w ∉ S, and S = (B₁ ∪ B₂) ∖ {w} with B₁, B₂ bonds meeting only in w. This follows by counting weights against the freeness of the two halves.

**Result:** every bond through an up corner x and a down corner z is a resolvent of a bond through x and w and a bond through w and z. The first has a counterclockwise loop enclosing more up than down triangles; the second is the clockwise mirror.

This explains why opposite kinds are special. It does not explain "back to back", and I have no proof that every other pair has a bond.

## Question 1

The exact statement I can stand behind is recursive: an opposite-kind corner pair has a bond iff some w and bonds B₁ ∋ x,w and B₂ ∋ w,z exist with B₁ ∩ B₂ = {w} and a minimal resolvent.

My geometric guess, at low confidence: failure means the two loops cannot be made to share only one vertex. In a bare parallelogram, the loop at x and the loop at z are forced onto the same anti-diagonals. For 3×3, the only candidate 6-sets contain a triangle or a side-plus-apex bond. If so, the 52 "inside but bonded" cases should all have patch material outside the parallelogram, alongside it.

Cheap tests:
1. Run Floyd–Warshall for D, then check the criterion against your brute force on all subsets.
2. For each back-to-back pair, list the w with bonds on both sides meeting only at w, and compare with bond or no bond.
3. Record the orientation of z's wedge. Your definition is one-sided: z can lie in x's cone with its wedge either exactly opposite (the parallelogram case) or skew. This may split the 329/74.

## Question 4

These are from memory, so check them before citing.

- **Height mapping for the triangular antiferromagnet:** Blöte–Hilhorst (1982) and Nienhuis–Hilhorst–Blöte (1984).
- **Heights as difference constraints:** Thurston, "Conway's tiling groups" (1990), where tileability is exactly a D-type inequality. The lattice structure of tilings is in Propp and in Rémila.
- **Opposite charges:** the closest analogue is Ciucu's work on triangular holes in lozenge tilings, where up and down holes interact like opposite charges; also Fisher–Stephenson monomer correlations.
- **Forcing:** the forcing-number literature for perfect matchings of hexagonal systems (Harary–Klein–Živković; Zhang–Li).
- **Systolic and bridged graphs:** Chepoi; Januszkiewicz–Świątkowski.

I do not know of b = steps + 1 or the corner-pair exception stated anywhere.

## Question 5: predictions to freeze

**Derived here (expect zero exceptions on disc patches):**
- D(x,y) + D(y,x) = 3·steps for every pair; no triangle is equidistant from any vertex.
- The cycle criterion matches brute force.
- b ≥ steps + 1.
- Every bond has ΣD = 3(|S|−2) and diameter ≤ |S|−2.
- Every bond through opposite-kind corners splits at a revisited vertex outside S.

**Empirical (not derived):**
- b = steps + 1 whenever finite.
- Unbonded pairs are only back-to-back opposite-kind corners.
- Each parallelogram up to 3×5 has exactly one unbonded pair.
- Patches with no single-triangle vertices are metric.

**Closed weaves:** none of my proofs apply, because the height is multivalued. I would freeze "metric" as an observation only, and log tori with a side not divisible by 3 separately, since the mod-3 class is not globally defined there.
