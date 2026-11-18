# Cuts, blocks, rings and split bases: what is proved

Ticket `NAE-METRIC-20261118-001A`, 18 November 2026. Written before the frozen run; checked by ticket B's gates and census
(`experiments/NAE-METRIC-20261118-001B/NAE-METRIC-20261118-001B-E001_blocks/`). Referee pending. Lemmas 1 and 2, the gluing and C4 are
the thread's, checked by the advisor (claude-fable-5-2); the exact bond structure in C1, the weaker hypothesis, the primal-graph
definition of blocks and the ring lower bound (C3) are the advisor's, checked here.

## Terms

As in `BOND-METRIC-20261118-001A`: free and constrained sets, bonds (minimal constrained sets), bond distance b (least bond holding
both, minus one; infinite when none). A base is **complement-closed** when the complement of every allowed state is allowed; every
base of not-all-equal and betweenness knots (forbid a pattern and its complement), of any arity, is. A distinction y **separates** when
the knots split into nonempty groups 𝓛 and 𝓡 whose distinctions meet only in y; write L and R for their distinctions other than y.

- (F1) The allowed states of the base are the pairs of allowed states of 𝓛 and of 𝓡 that agree on y.
- (F2) If y takes both values on each side, every allowed state of 𝓛 extends to the base, so the projection onto L ∪ {y} is 𝓛's own
  state set and the bonds inside L ∪ {y} are 𝓛's bonds. Complement-closure (with some state) gives this.
- (F3) If a bond B through y misses a pattern π, then π restricted to B − y occurs (B − y is free) and forces y to the value opposite
  to π's; under complement-closure the complement of π is missing too and forces y the other way. So y can be forced to either value
  from B − y.

## C1. Bonds at a separating distinction

**Lemma 1 (sides).** For x, w ∈ L ∪ {y}, b(x, w) is 𝓛's own. Let T be a bond holding x and w with T_R = T ∩ R nonempty, T_L = T ∩ L.
If y ∈ T: T_R ∪ {y} is a proper subset (x or w lies in T_L), so it is free, and by F1 the projection onto T is the projection onto
T_L ∪ {y} times all values on T_R; T constrained makes T_L ∪ {y} constrained, a proper subset: impossible. If y ∉ T: T_L and T_R are free,
so for each value u on T_L the set Y_L(u) of y-values it allows is nonempty, likewise Y_R(r), and the projection onto T is
{(u, r) : Y_L(u) ∩ Y_R(r) ≠ ∅}. T constrained gives u₀, r₀ with Y_L(u₀) = {v}, Y_R(r₀) = {¬v}. So T_L ∪ {y} is constrained and holds a
bond B′ of 𝓛, with y ∈ B′ (else B′ ⊆ T_L, a free set). If x ∉ B′, B′ − y ⊆ T_L − x forces y to v (F3), and with r₀ the set
(T_L − x) ∪ T_R, which is T − x, is constrained: impossible. So x ∈ B′, likewise w, and |B′| ≤ |T_L| + 1 ≤ |T|. ∎

**Lemma 2 (additivity).** For x ∈ L and z ∈ R, b(x, z) − 1 = (b(x, y) − 1) + (b(y, z) − 1), infinite when either is.
- *Upper.* Take bonds S₁ of 𝓛 holding x, y and S₂ of 𝓡 holding y, z, and T = (S₁ ∪ S₂) − y, so |T| = |S₁| + |S₂| − 2. For t ∈ S₁ − y,
  T − t is free: given its values, those on S₂ − y (free) allow some value of y, and S₁ − t is free and holds y, so 𝓛's side extends with
  that value; F1 joins the two (symmetrically for t ∈ S₂ − y). T is constrained: S₂ misses ρ, and ρ on S₂ − z occurs and forces z;
  choose values on S₁ − y forcing y to ρ's value (F3); together they force z, so a pattern of T is missing. So T is a bond.
- *Lower.* Let T be a bond holding x and z. y ∉ T, for otherwise T − x ⊇ T_R ∪ {y} and T − z ⊇ T_L ∪ {y} are free and the projection onto
  T, their join over y, is full. As in Lemma 1, T_L ∪ {y} and T_R ∪ {y} are constrained and hold bonds B_L ∋ y, x and B_R ∋ y, z (else
  T − x or T − z is constrained). So |T| = |T_L| + |T_R| ≥ b(x, y) + b(y, z). ∎

**The bond structure** (the advisor). The upper argument never uses leastness, so for any bonds B_L of 𝓛 and B_R of 𝓡 through y the
set (B_L ∪ B_R) − y is constrained, with every proper subset free: a bond. With the lower argument, the bonds of the base are exactly
𝓛's, 𝓡's and these. So the number of bonds is #bonds(𝓛) + #bonds(𝓡) + (𝓛's bonds through y) × (𝓡's bonds through y).

**Hypothesis.** Only F2 and F3 were used: y takes both values on each side, and every bond through y can force y both ways. So C1 holds
for parity bases wherever y is not fixed (the missing patterns of a parity bond form a coset); there it is the parallel connection
of matroids (Brylawski 1971).

## C2. Blocks

The blocks are the biconnected components of the primal graph (distinctions adjacent when they share a knot); each knot lies in one,
and the cut vertices are exactly the separating distinctions. Applying Lemma 1 at each cut distinction, b between two distinctions of
a block is the block's own; applying Lemma 2 along the block-cut tree, for x and z in different blocks b(x, z) − 1 is the sum of
(b − 1) between the distinctions where the route enters and leaves each block on the way.

**Theorem.** On a complement-closed base, b is a metric exactly when b is a metric on every block (as a base on its own).
- *Only if:* by Lemma 1 the block's values are the base's.
- *If:* write d = b − 1 (d(u, u) = 0 for the sum only); the triangle inequality for b is d(x, z) ≤ d(x, y) + d(y, z) + 1. Let the three
  routes meet at a cut distinction c: then the right side exceeds the left by 2d(c, y) + 1 > 0. Or at a block, entered at x′, y′, z′:
  the inequality reduces to d(x′, z′) ≤ d(x′, y′) + d(y′, z′) + 1 + 2d(y, y′), which is the block's triangle inequality when the three
  gates differ and follows from d ≥ 0 otherwise. ∎

So every violating triple has three distinct gates in one block: no violation spans two blocks.

## C3. Rings

Take m ≥ 3 knots K_i = {v_{i−1}, p_i, v_i} (indices mod m) of not-all-equal or betweenness laws in any mixture (plain or twisted),
p_i in K_i alone. Steps apart s(x, z) counts the knots of a least chain.
- *Upper.* Take the shorter route from x to z and S = {x, z} together with the third distinction, relative to the route, of each knot
  on it; |S| = s + 2. S is constrained: fixing x and choosing each third to agree with its knot's forbidden pattern (or its
  complement) at the previous route distinction forces the next, so z is forced (knot by knot, as in `FREE-READ-20261118-001A`, U).
  Every S − t is free: given its values, choose the route's ring distinctions greedily from both ends (each knot with two values set
  allows a third, L0), and complete the other arc, whose own distinctions are all outside S: choosing its ring distinctions freely, each
  of its knots then allows a value of its own distinction. So b ≤ s + 1.
- *Lower* (the advisor). (i) Forgetting p_j removes K_j: any values of v_{j−1}, v_j extend to p_j. So a bond missing p_j is a bond of the
  chain of the other m − 1 knots. (ii) The bonds of a chain of such knots are exactly its runs {v_{a−1}, p_a, …, p_b, v_b}: a single
  knot's only bond is itself, and C1 at each shared distinction gives the rest. So a bond missing some own distinction holds every knot on
  one route between x and z and has at least s + 2 members. (iii) The set P of all own distinctions is free. Given its two ring distinctions, a
  knot leaves its own distinction free exactly when they stand in one relation (equal or different, by the knot's law) and forces it
  when they stand in the other. Choose the ring distinctions around the ring so that K₁ to K_{m−1} leave theirs free; K_m then leaves p_m
  free or forces it, and complementing every ring distinction keeps every relation and flips the forced value. So every joint value of
  P occurs. So a bond holding all of P is bigger than P: at least m + 1 members, and m + 1 ≥ s + 2 since s ≤ ⌊m/2⌋ + 1 ≤ m − 1 for m ≥ 3.
  So b ≥ s + 1. ∎

So b = s + 1 on every pair of a ring, a metric (steps apart is one). **Corollary:** on every complement-closed base of three-place knots
whose blocks are single knots and rings, b − 1 = steps apart everywhere (C2 and C3), so b is a metric.

## C4. Split bases (tonight's grown lines and grids)

Let the allowed states be a complement-closed set holding both constant states (every split base: the constants and both sides of
each split). On {x, y} the constants give 00 and 11, and 01 occurs exactly when 10 does, so {x, y} is constrained exactly when no state
separates x and y: then b = 1. On {x, y, z} the constants give 000 and 111 and the other patterns come in complementary pairs, each
saying which of the three stands alone; so {x, y, z} is a bond exactly when its pairs are separated and one of the three is never alone
against the other two (it lies between them in the split metric). So b(x, y) = 2 exactly when such a z exists.
- On a line of n ≥ 3 distinctions (the cuts) every pair has one: a distinction between them, or one beyond an end for neighbours.
- On a full grid (row cuts and column cuts) every pair has one: a corner of the box they span, or a neighbour along the other order.

So b = 2 for every pair there. Any function with values in [1, 2] on distinct pairs satisfies the triangle inequality, so this says
the grown bases have bond-distance diameter two (bond distance gives them no spacing, as `FREE-READ-20261118-001` found on split
grids); it is not evidence on the metric question (the advisor).

## Computed in ticket B (frozen)

- C1 and C2 held on 1,000 glued bases (16,719 separated triples, with parity and four-place not-all-equal knots among them; the bond
  count identity exact on 858) and on 1,000 sparse bases on nine distinctions (no violating triple spans two blocks).
- C3 held on rings of 3 to 9 knots, plain and twisted, with exactly m(m − 1) runs, largest b = ⌊m/2⌋ + 2, and the bonds holding every
  own distinction (they exist only for plain rings of odd length and twisted rings of even length) of exactly m + 1 members.
- Every failing pure not-all-equal block on at most seven distinctions with at most six knots has two knots sharing two distinctions
  (325,395 failing of 1,327,830 on seven distinctions with six knots).
- Graph-like bases (knots meeting at most once, each distinction in at most two knots) whose knot graph is series-parallel: none of
  354 fails, plain or twisted (conjecture P6). With a K4 minor, 3 of 6 fail.
