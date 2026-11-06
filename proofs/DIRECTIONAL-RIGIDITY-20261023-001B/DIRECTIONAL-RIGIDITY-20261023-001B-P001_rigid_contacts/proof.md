# Which three-place contacts are rigid in direction: stripes and straight walls, not algebra

Status: Proved

Ticket `DIRECTIONAL-RIGIDITY-20261023-001B`, 2026-10-23.

**What it uses:**
- from `TRIPLE-TWIST-20261023-001A-P001`: the twisted three-place model, tiling placements and doubly allowed assignments;
- from `TRIPLE-SHIELD-20261023-001B-P001`: Theorem 1 (cylinders contradict only along classes odd relative to every fitting
  twist) and the vertex flips;
- from `LINE-DETECTOR-20261023-001B-P001`: the contradiction set S(x), the cylinder covers and their certificates, and the
  trichotomy for two-literal worlds;
- from `DIRECTIONAL-RIGIDITY-20261023-001A-E001` (frozen, supported, independently checked): the counts in Proposition 6
  and the selectivity of bending placements beyond 3 × 3.

## Standard statement

### Setting

- **Worlds.** A world is a tiling placement R on the L × M triangular torus, a twist q and a configuration x, as in
  `TRIPLE-SHIELD-20261023-001B-P001`. The coin of a triangle chooses R or its complement R̄, the relation with every pattern
  complemented.
- **Places.** The places 0, 1, 2 of the up triangle at (i, j) are (i, j), (i+1, j), (i+1, j+1); those of the down triangle at
  (i, j) are (i, j), (i, j+1), (i+1, j+1).
  - So places 0 and 2 span the diagonal edge, of direction (1, 1), in both kinds of triangle.
  - Places 0 and 1 span a horizontal edge in up triangles and a vertical one in down triangles; places 1 and 2 the reverse.
- **Patterns.** U = R ∩ R̄ is the set of doubly allowed patterns. A pattern other than 000 and 111 has a lone place: the place
  whose value differs from the other two.
- **Classes.** S(x) is the set of primitive classes whose cylinder cover has no hidden assignment. A class is odd when it is odd
  relative to every fitting twist; S(x) contains only odd classes. A configuration is selective when S(x) has at least two classes
  and misses an odd class.
- **Rigidity.** A placement is rigid when no configuration in any twist on any torus is selective.
- **The diagonal class.** Let g = gcd(L, M) and l = lcm(L, M). The diagonal class is d = (l/L, l/M), the class of the lattice
  lines of direction (1, 1).
- **The constant frame.** It is R itself when U contains 000, and R with place 1 complemented when U contains 010 but not 000.
  Complementing place 1 is the vertex flip at the vertices with i + j odd (Lemma B). In the constant frame, U contains the
  constant patterns. Two sets of places describe the frame:
  - the free places Φ, the lone places of doubly allowed patterns;
  - the allowed places Λ, the lone places of patterns of R or R̄.

**Definition (four kinds of three-place tiling placement).**
- **h/v stripes:** for some α, U contains every pattern with p₀ + p₁ = α and every pattern with p₁ + p₂ = α (mod 2).
- **Diagonal stripes:** not the above, and for some β, U contains every pattern with p₀ + p₂ = β.
- **Straight walls:** neither of the above. The constant frame exists, 1 ∉ Φ, and Λ omits place 0 or place 2.
- **Bending walls:** the same, except that Λ contains both places 0 and 2.

**Proposition 0 (census).** The 30 three-place tiling placements of the census of `TRIPLE-TWIST-20261023-001B-E001` fall into
the four kinds as follows.

| Kind | Placements | Group of `DIRECTIONAL-RIGIDITY-20261023-001A-E001` |
| --- | --- | --- |
| h/v stripes | 127, 223 | never contradicting |
| diagonal stripes | 91, 94, 123, 167, 173, 183, 191, 239 | one-dimensional; and 191, 239 of never contradicting |
| straight walls | 45, 61, 101, 103, 135, 149, 157, 199 | saturated |
| bending walls | 54, 62, 109, 110, 111, 125, 147, 151, 155, 159, 203, 215 | selective |

In the constant frame:
- the straight-wall placements have Λ = {0, 1} (45, 61, 135, 199) or Λ = {1, 2} (101, 103, 149, 157);
- the bending-wall placements have Λ = {0, 2} or {0, 1, 2};
- Φ is empty or a single end of the diagonal edge.

The frame complements place 1 for 45, 61, 101 and 103, and for the bending placements 54, 62, 109, 110, 111 and 125.

**Proposition 1 (no relational criterion).**
- **(a) Polymorphisms.** For every three-place tiling placement, the operations on {0, 1} of any arity that preserve both R and
  R̄ are the projections, together with the two constants when U contains 000. Every two-literal tiling placement is preserved by
  majority.
- **(b) Renaming places.** Under renaming the places and complementing, the 30 three-place placements fall into 12 classes. Five
  of these contain both a bending-wall placement and a rigid one: {135, 147, 149}, {62, 94, 110}, {111, 123, 125}, {159, 183, 215}
  and {155, 157, 167, 173, 199, 203}. The last mixes three kinds.
- **What follows.** No property of the pair (R, R̄) that is invariant under renaming places decides rigidity, and polymorphisms
  are such a property. What decides it is which places sit at the ends of the diagonal edge.

**Theorem 2 (stripes).** Fix a twist and a configuration.
- **(a) Diagonal stripes.** If U contains every pattern with p₀ + p₂ = β, the cylinder along every class other than ±d has a
  doubly allowed assignment. So S(x) ⊆ {±d}.
- **(b) h/v stripes.** If U contains every pattern with p₀ + p₁ = α and every pattern with p₁ + p₂ = α, every cylinder has a
  doubly allowed assignment. So S(x) = ∅.

**Theorem 3 (straight walls).** Take a straight-wall placement on an L × M torus. It has exactly one fitting twist q_f. Take a
twist q ≠ q_f, let r = q − q_f, and take a configuration x.
- **(i)** If r(d) is odd, S(x) is the set of all odd classes, for every configuration.
- **(ii)** If r(d) is even, S(x) is empty when one of the torus's g staircases is compatible (defined in the proof), and is the set
  of all odd classes otherwise.
- **The count.** Exactly 2^{2LM} − (2^{2l} − 2)^g configurations have S(x) empty in case (ii).
- **Hence** straight-wall placements are rigid: no configuration is selective. Single lines appear only on tori where just one
  listed class is odd.

**Proposition 4 (bending walls).** Each of the twelve bending-wall placements has a selective configuration on the 3 × 3 torus.
Each verdict is certified both ways.

| Placement | Twist | Configuration | Contradicts along | Has an assignment along (odd classes) |
| --- | --- | --- | --- | --- |
| 54 | 00 | 168100 | (1,0), (0,1), (1,−2), (2,−1) | (1,2), (2,1) |
| 62 | 00 | 77851 | (1,0), (0,1), (1,−2), (2,−1) | (1,2), (2,1) |
| 109 | 00 | 204805 | (0,1), (1,2) | (1,0), (2,1), (1,−2), (2,−1) |
| 110 | 00 | 24642 | (1,0), (0,1), (1,−2), (2,−1) | (1,2), (2,1) |
| 111 | 00 | 36954 | (1,0), (1,2) | (0,1), (2,1), (1,−2), (2,−1) |
| 125 | 00 | 49253 | (1,0), (1,2) | (0,1), (2,1), (1,−2), (2,−1) |
| 147 | 01 | 30817 | (0,1), (1,−1) | (1,1), (2,1), (2,−1) |
| 151 | 01 | 110633 | (0,1), (2,1), (2,−1) | (1,1), (1,−1) |
| 155 | 01 | 45276 | (0,1), (1,−1) | (1,1), (2,1), (2,−1) |
| 159 | 01 | 227852 | (0,1), (1,1) | (1,−1), (2,1), (2,−1) |
| 203 | 01 | 123079 | (0,1), (1,−1) | (1,1), (2,1), (2,−1) |
| 215 | 01 | 45302 | (0,1), (1,1) | (1,−1), (2,1), (2,−1) |

**Theorem 7 (rotating walls).** Take a bending-wall placement with no free place: 54, 109, 147 or 151. In its constant frame
every lone pattern of R has one lone value v, and Λ is {0, 2} (54, 147) or {0, 1, 2} (109, 151).
- **Wall states and moves.** A wall state is a triangle T, one of its edges E (where the wall enters) and a value ℓ (the value on
  the wall's left).
  - In T the wall turns left when v + x̃(T) = ℓ and right otherwise, with x̃ the frame's lifted coins.
  - The corner inside the turn, its lone corner, must have its place in Λ; otherwise the wall stops.
  - The wall leaves through the third edge into the next triangle, with the same ℓ.
- **Cycles.** Read on the torus, with ℓ taken relative to the twist, the moves form an injective partial map on 12LM states.
  - Its cycles are the valid wall cycles.
  - A cycle C has a class e(C), its displacement in classes.
  - It has an overlap set D(C): the differences of the positions of two visits to one torus triangle within a period.
- **The statement.** For every odd class c, the cylinder along c has an assignment exactly when some valid cycle C has
  det(c, e(C)) ≠ 0 and no overlap in ℤc + ℤe(C).
- **Hence** S(x) is decided on the torus alone. A configuration is selective exactly when its valid cycles' overlaps fall in
  ℤc + ℤe(C) for some odd classes c and not for others: a wall that collides with its own copy on one cylinder can pass on
  another.

**Remark 8 (walls with choices).** The direction (⇐) of Theorem 7 uses no determinism. Consider the eight bending placements with
a free place. Let a turn be allowed when its lone corner's place is free, or pinned with the coin's value matching. Then a valid
wall cycle with det(c, e) ≠ 0 and no overlap in ℤc + ℤe still gives the cylinder along c an assignment. Whether such cycles are
also necessary there is open (see "What this does not show").

**Corollary 5 (which three-place contacts are rigid).**
- **Proved rigid.** The 18 placements with stripes or straight walls are rigid on every torus, in every twist, for all classes.
  - The two with h/v stripes never contradict.
  - The eight with diagonal stripes contradict at most along the diagonal class.
  - The eight with straight walls contradict along all odd classes or none.
- **Selective.** The twelve bending-wall placements are selective on 3 × 3 (Proposition 4). In A every bending placement
  computed was selective on every torus computed (Proposition 6). For the four with no free place, Theorem 7 says why: a wall
  collides with its own copy on some cylinders and not on others.
- **The mixed law reduced.** A three-place placement whose configurations on some torus include both a single line and a global
  contradiction has bending walls. That is because stripes give at most single lines and straight walls give no single lines
  alongside global ones. The prediction P7 of A therefore reduces to the observation that bending-wall placements are selective.

**Remark (the picture: walls).** Work in the constant frame. Away from the configuration's defects an assignment is constant;
where it changes value, every triangle it cuts has its lone place on the far side of the wall.
- **Free or pinned walls.** A wall through doubly allowed patterns is free. A wall through patterns of R or R̄ alone is pinned:
  the coin fixes the value on the lone side.
- **Straight or bending walls.**
  - A wall that must always cross the edge of places 0 and 1, or always the edge of places 1 and 2, is forced into a straight
    diagonal staircase.
  - A wall that may have its lone corner at either end of the diagonal edge crosses that edge and can turn.

The four kinds are then a two-by-two table:

|  | straight | bending |
| --- | --- | --- |
| free | diagonal stripes: contradict at most along d | h/v stripes: never contradict |
| pinned | straight walls: all odd classes or none | bending walls: selective; with no free place, exactly where walls collide with their own copies (Theorem 7) |

**Proposition 6 (the counts of A).** These counts come from `DIRECTIONAL-RIGIDITY-20261023-001A-E001` (frozen, supported, independently checked).
- **The tori.**
  - Every configuration on 3 × 3 (16 classes) and 3 × 4 (13 classes).
  - Samples per twist on 4 × 4 (2^22, 12 classes), 4 × 5 (2^22, 9 classes) and 5 × 5 (2^20, 6 classes), for the 19 orbit
    representatives.
- **Straight walls (Theorem 3).**
  - On 3 × 3 and 3 × 4, in every non-fitting twist of all eight placements, each configuration contradicts along every listed
    odd class or along none.
  - The number contradicting along none is the formula's: 23816 of 262144 on 3 × 3 and 2 of 16777216 on 3 × 4 when r(d) is even,
    and 0 when it is odd.
  - The samples agree. On 4 × 4: 129677 and 129493 of 4194304 against 129544 expected. On 5 × 5: 10084 and 10176 of 1048576
    against 10200. On 4 × 5: 0, against an expected 2^{−39} fraction. Always 0 when r(d) is odd.
- **Stripes (Theorem 2).**
  - No pattern outside the diagonal class ever appears for diagonal stripes, and no nonzero pattern for h/v stripes.
  - Placements 191 and 239, whose diagonal stripes allow a contradiction along the diagonal class, show none. That holds on
    3 × 3 and, for 191, on 4 × 4 and 5 × 5, where the diagonal class is listed.
- **Bending walls.** Every bending placement computed is selective on every torus computed.
  - All twelve on 3 × 3 and 3 × 4.
  - The representatives 54, 62, 109 and 111 on 4 × 4, 4 × 5 and 5 × 5. On 4 × 5 they have 2948, 197024, 514936 and 36655
    selective configurations in the sample; on 5 × 5, 234, 29914, 66769 and 2296.
- **Two literals.** No selective pattern on any torus (the trichotomy).
- **The mixed law.** Single lines together with global contradictions occur on 26 (placement, torus) pairs, all with bending
  walls.

## Nearest known result

- **Proposition 1(a).** Classical. Polymorphisms of Boolean relations (Post's lattice), Świerczkowski's lemma (1960) on
  identification minors, and Schaefer's dichotomy in its polymorphism form (Jeavons, Cohen and Gyssens): languages with only
  essentially unary polymorphisms are the hard ones.
- **Proposition 1(b).** Elementary; the contrast with LINE-DETECTOR, where clause width alone (majority) decides rigidity, is the
  program's.
- **Theorem 2.** Elementary. In the language of ℤ² subshifts, free stripes along a direction make that direction non-expansive for
  the doubly allowed subshift (Boyle and Lind). Theorem 2 says contradictions can only run along such a direction. The statement
  for these worlds is new to the program; moderate folklore risk.
- **Theorem 3.** Elementary. It is a domain-wall argument: walls of a rigid ground state pinned by a quenched field, here the coins.
  Walls forced straight by local rules are familiar from constrained Ising models. The exact statement and count are new to the
  program; low to moderate folklore risk.
- **Proposition 4.** A certified computation.
- **Theorem 7.** The walls are deterministic walks among fixed rotators on the honeycomb lattice, as in Lorentz lattice gases
  and mirror models (Ruijgrok and Cohen). Reading S(x) off the self-overlaps of their torus cycles is new to the program; low
  folklore risk for the exact statement.
- **Corollary 5.** It combines the above with the frozen record of A.

## Proof

### Lemma A (the lifted picture)

Fix a class c and let w = (c₁L, c₂M). The cylinder along c has a hidden assignment exactly when there is F: ℤ² → {0, 1} with
the following properties:
- **Quasi-periodicity.** F(p + w) = F(p) + q(c).
- **Constraints.** On every triangle T of the lattice, F takes a pattern of the relation chosen by the lifted coin x̃(T).
- **Lifted coins.** x̃(T_f + (aL, bM)) = x_f + q·(a, b), for the triangle T_f of the fundamental domain.

*Proof.*
- **The change of variables.** A node of the cylinder cover is a vertex with a sheet, and it represents the lifts p that differ
  by multiples of w. Put F(p) = H(node(p)) + q·deck(p); conversely H(node) = F(p) + q·deck(p). This is well defined exactly when F
  has the quasi-periodicity.
- **The constraints.** The cover's constraint for T_f reads H(node(p_k)) + q·deck(p_k) ∈ R_{x_f}, that is F|_{T_f} ∈ R_{x_f}. A
  copy shifted by (aL, bM) has all three values of F changed by q·(a, b), and complementing all three places of a pattern of R_x
  gives a pattern of R_{x+1}. ∎

In particular every world's constraints are R and R̄ alone.

### Lemma B (two symmetries)

- **The frame flip.** Let e(i, j) = i + j mod 2. On every triangle e is e(p₀)·111 + 010. So F ↦ F + e is a bijection between
  assignments of the following two worlds, on every cylinder:
  - the world (R, q, x);
  - the world (R′, q + (L, M), x′), where R′ is R with place 1 complemented and x′_f = x_f + e(p₀(T_f)).

  The lifted coins match because e(p + (aL, bM)) = e(p) + aL + bM. The flip carries doubly allowed assignments to doubly allowed
  ones, so fitting twists move by (L, M). Relative twists, odd classes and S(x) are therefore unchanged, and x ↦ x′ is a
  bijection. This is one of the vertex flips of `TRIPLE-SHIELD-20261023-001B-P001`.
- **The half turn.** (i, j) ↦ (−i, −j) maps the up triangle at (i, j) onto the down triangle at (−i−1, −j−1), and the down
  triangle onto an up triangle. In both cases places 0 and 2 are exchanged. It maps the torus to itself, every class to its
  negative, and every twist to itself. So R and R with places 0 and 2 exchanged have the same contradiction sets, up to a
  bijection of configurations. It exchanges Λ ⊆ {0, 1} with Λ ⊆ {1, 2}.

### Proposition 0

`check.py` computes the kinds and the frames. ∎

### Proposition 1

**(a)**
- **The ternary operations.** By Lemma A the polymorphisms of every world are those of the pair (R, R̄). `check.py` tests all 256
  ternary operations against R and R̄ for the 54 tiling placements.
- **Constants.** A constant operation preserves both relations exactly when its constant pattern lies in U. Since U is closed
  under complement, it holds 000 exactly when it holds 111.
- **Higher arities without constants.** Świerczkowski's lemma: an operation of arity n ≥ 4 whose identification minors are all
  projections agrees with one projection on every tuple with a repeated entry. On {0, 1} every tuple of length at least 3 has one,
  so the operation is a projection. By induction on the arity, a clone whose ternary members are projections has only projections.
- **Higher arities with both constants.** Suppose the clone holds both constants.
  - An operation that is not monotone yields negation by substituting constants.
  - Let f be monotone, neither constant nor a projection. If some minimal true point of f has two ones, set its other ones to 1
    and every other variable to 0; this yields conjunction. Otherwise f has at least two minimal true points, each a single one;
    setting the other variables to 0 yields disjunction.
  - Negation, conjunction and disjunction would be ternary members with dummy variables. So the clone is the projections and the
    constants.
- **Two-literal placements.** Majority preserves every conjunction of two-literal clauses and commutes with complement; the check
  confirms it for the 24.

**(b)** Renaming coordinates does not change a relation's polymorphisms. `check.py` lists the classes with their kinds. ∎

### Theorem 2

Fix c ≠ 0, w = (w₁, w₂) = (c₁L, c₂M), and a target parity ε = q(c). By Lemma A it suffices to give F with
F(p + w) = F(p) + ε whose pattern lies in U on every triangle. Such an F satisfies every coin.

**(a)**
- **The assignment.** Let δ = w₁ − w₂; it is 0 exactly when c = ±d. For c ≠ ±d choose φ: ℤ → {0, 1} with
  φ(s + δ) = φ(s) + ε + βw₁, possible since δ ≠ 0. Put F(i, j) = φ(i − j) + βi.
- **Quasi-periodicity.** F(p + w) = φ(i − j + δ) + β(i + w₁) = F(p) + ε.
- **The patterns.** Places 0 and 2 of every triangle are (i, j) and (i+1, j+1). Their values differ by β, so the pattern lies in
  U. ∎

**(b)**
- **Rows, when w₂ ≠ 0.** Choose ψ with ψ(j + w₂) = ψ(j) + ε + αw₁ and put F(i, j) = ψ(j) + αi.
  - Places 0 and 1 of an up triangle are (i, j) and (i+1, j); their values differ by α.
  - Places 1 and 2 of a down triangle are (i, j+1) and (i+1, j+1); their values differ by α.
- **Columns, when w₁ ≠ 0.** Choose χ with χ(i + w₁) = χ(i) + ε + αw₂ and put F(i, j) = χ(i) + αj.
  - Places 1 and 2 of an up triangle are (i+1, j) and (i+1, j+1); places 0 and 1 of a down triangle are (i, j) and (i, j+1).
  - Their values differ by α.
- **Conclusion.** Since w ≠ 0, one of the two applies. ∎

### Theorem 3

By Lemma B (the frame flip, then the half turn if needed), assume the placement is in its constant frame with Λ = {0, 1}
(Proposition 0). Then:
- U consists of the constants and, if Φ = {0}, the two lone-0 patterns;
- every other pattern of R or R̄ has lone place 0 or 1;
- a lone-1 pattern lies in R or R̄ but not in U, so each of R and R̄ contains exactly one of the two lone-1 patterns. On a lone-1
  triangle the coin therefore fixes the lone value.

**Staircases.**
- **Definition.** Z_s = {up triangle at (s+t, t), down triangle at (s+t+1, t) : t ∈ ℤ}, ordered by t, with each up triangle before
  the down triangle that follows it.
- **The diagonals.** D_s = {(i, j) : i − j = s}.
- **(Z1)** The staircases partition the triangles. In Z_s, the edge of places 0 and 1 of each triangle is the edge of places 1 and
  2 of its predecessor.
- **(Z2)** Every corner of a triangle of Z_s lies on D_s or D_{s+1}.
  - In an up triangle, places 0 and 2 lie on D_s and place 1 on D_{s+1}.
  - In a down triangle, places 0 and 2 lie on D_{s+1} and place 1 on D_s.
- **(Z3)** Translation by (a, b) maps Z_s onto Z_{s+a−b}. Translation by (l, l) = (l/L·L, l/M·M) maps Z_s to itself and changes
  lifted coins by q(d).
- **(Z4)** On the torus there are g staircases (s mod g), each of 2l triangles.
- **Compatible.** Z_s is compatible when the lifted coins are constant on its up triangles, constant on its down triangles, and
  the two constants differ. When q(d) = 0 this is a property of the torus staircase, by (Z3).

**The fitting twist.**
- In this frame the constant assignment is doubly allowed, so q = 0 fits.
- It is the only fitting twist. A non-constant doubly allowed assignment would have a lone-0 triangle (Φ ⊆ {0}). Its edge of
  places 0 and 1 is cut, so its predecessor has its edge of places 1 and 2 cut. That makes the predecessor lone 1, since lone 2 is
  excluded. But no lone-1 pattern is doubly allowed.
- Hence r = q here.

**Ray lemma.** Let F be an assignment on some cylinder and T ∈ Z_s a non-constant triangle. Then:
- every triangle of Z_s before T is lone 1;
- F is constant on the corners of these triangles in D_s, and constant with the other value on those in D_{s+1};
- the lifted coins are constant on their up triangles and constant, with the other value, on their down triangles.

*Proof.*
- **Induction backwards.** T has two cut edges at its lone place, which is 0 or 1. Either way the edge of places 0 and 1 is cut.
  By (Z1), the predecessor has its edge of places 1 and 2 cut. Its lone place is therefore 1 or 2, hence 1. Its edge of places 0
  and 1 is cut too, and so on backwards.
- **Values.** In a lone-1 triangle places 0 and 2 agree. By (Z2) this chains the D_s corners through the up triangles and the
  D_{s+1} corners through the down triangles. The two values differ.
- **Coins.** The lone corner of an up triangle lies on D_{s+1} and that of a down triangle on D_s. The coin fixes the lone value.
  So the coins are constant on the up triangles, constant on the down triangles, and opposite. ∎

**(i) r(d) odd.**
- Suppose a cylinder assignment had a non-constant triangle T.
- The triangles of its staircase before T include an up triangle and its translate by −(l, l). Their lifted coins differ by
  (Z3), against the ray lemma.
- So every triangle is constant, and F is constant on the connected lattice. Then F(p + w) = F(p) + q(c) forces q(c) = 0.
- Conversely the constant assignment serves every even class. So S(x) is the set of odd classes. ∎

**(ii) r(d) even.**
- **Even classes** have the constant assignment.
- **Odd classes are not ±d**, since r(d) is even.
- **(⇒)** An assignment along an odd c is not constant, since F(p + w) = F(p) + 1. By the ray lemma, some staircase has a
  compatible ray. By (Z3) with q(d) = 0, coins along Z_s repeat with period (l, l), so the whole staircase is compatible.
- **(⇐) The construction.** Let Z_s be compatible, with lone values ā on D_{s+1} and a on D_s.
  - Let δ = w₁ − w₂ ≠ 0, and orient c so that δ > 0.
  - Translation by w maps Z_s onto Z_{s+δ} and changes every coin. So Z_{s+kδ} is compatible with a replaced by a + k.
  - Put F = a + k + 1 on the diagonals D_t with s + kδ < t ≤ s + (k+1)δ.
- **Checking the construction.**
  - At the walls Z_{s+kδ} the triangles are lone 1 with the lone values the coins require.
  - Every other triangle has its corners on two diagonals of one strip, so it is constant.
  - Translation by w moves each strip to the next, so F(p + w) = F(p) + 1.
  - The conditions do not depend on c. So S(x) is empty if some staircase is compatible, and the set of odd classes otherwise.
- **The count.**
  - The g staircases partition the torus's 2LM triangles into blocks of 2l, and the lifted coins on a block are a fixed
    translate of x there.
  - A block is compatible for 2 of its 2^{2l} coin patterns.
  - So (2^{2l} − 2)^g configurations have no compatible staircase. ∎

### Proposition 4

`check.py` certifies each verdict with its own search:
- a contradiction along a class by a strip of 12, 24 or 36 periods with no assignment;
- an assignment by a cyclic cover of at most 12 sheets, whose assignment is then verified clause by clause.

The configurations were located with the producer's program of A. ∎

### Theorem 7

Work in the constant frame (Lemma B). U is {000, 111}, and every lone pattern of R or R̄ is pinned. For these four placements
the pinned lone values of R are all equal, to v (Proposition 0 and the check).

**Walls of an assignment.** Let F be an assignment of the cylinder along c, lifted to ℤ² (Lemma A).
- Call an edge cut when its ends differ. Every triangle is constant or lone, so it has 0 or 2 cut edges.
- So the cut edges, as edges of the dual honeycomb lattice, split into disjoint simple paths and cycles: the walls.
- **The left value is constant.** Consecutive triangles of a wall share an edge, and both use its left endpoint as a left
  corner. Within a triangle the left corners are joined by its uncut edge, and no other wall crosses a triangle that this one
  crosses. So F is constant on the left side of a wall; call it ℓ.
- **The moves.** The lone corner of a crossed triangle is the corner inside the wall's turn there. It lies on the left for a
  left turn and on the right for a right turn. Its value is fixed by the coin to v + x̃(T). So the wall turns left exactly when
  v + x̃(T) = ℓ, and the lone corner's place must be in Λ. These are the moves of the statement.
- **Walls are periodic.** Reversing a wall exchanges left and right and replaces ℓ by ℓ + 1, so the moves are also determined
  backwards: the map is injective. A bi-infinite wall therefore projects onto a cycle of the finite state set of the torus, and
  is periodic in ℤ² with period h = e(C)·(L, M). Closing up includes returning with the same relative ℓ, and since coins change
  by r(e) under translation by h, this forces r(e) even.

**(⇒)**
- Let c be odd, so F(p + w) = F(p) + 1, and let γ be a path from p to p + w. It crosses an odd number of cut edges.
- On the cylinder, a wall that is a closed curve meets the closed loop γ an even number of times, whether it is contractible or
  winds around. A periodic wall that is not closed goes from one end of the cylinder to the other and meets γ an odd number of
  times. So some wall W is a lift of a valid cycle C with det(c, e(C)) ≠ 0.
- Suppose some d ∈ D(C) lies in ℤc + ℤe(C), say d = kc + me(C). Two visits of one torus triangle, at positions differing by d,
  put the same lattice triangle on W and on W + kw (using W + mh = W). If k ≠ 0, the walls W and W + kw of the assignment cross
  one triangle. If k = 0, W crosses one triangle twice. Both are impossible, since a triangle has at most two cut edges.

**(⇐)**
- **The walls.** Let C satisfy the condition, with a lift W of left value ℓ.
  - The translates W + kw (k ∈ ℤ) are pairwise disjoint, since a common triangle would give an overlap in ℤc + ℤe(C). W crosses
    no triangle twice, for the same reason with k = 0.
  - Since W is periodic along h, which is not parallel to w, they are disjoint parallel curves that cut the plane into strips.
- **The assignment.** Give F the value ℓ + k on the strip left of W + kw and right of W + (k−1)w (orienting w accordingly).
- **Checking it.**
  - Translation by w changes every coin and moves each strip to the next. So W + kw is a valid wall with left value ℓ + k, and
    F(p + w) = F(p) + 1.
  - Crossed triangles carry the lone patterns the coins allow. Every other triangle lies inside one strip and is constant. ∎

### Corollary 5

- **Rigidity** follows from Theorems 2 and 3 and Proposition 0.
- **The mixed law.**
  - Under stripes, S(x) is empty or {±d}, so global contradictions, which need two classes, do not occur.
  - Under straight walls, S(x) is empty or all odd classes, so a single line occurs only when one class is odd, and then no global
    contradiction does.
- **Selectivity** is Proposition 4 together with the record of A. ∎

## Checks

`check.py` uses the standard library only (seed 20261023). Every result below was obtained:
- **Kinds.** The four kinds equal the groups of A as stated in Proposition 0, and the frames and lone places are as listed.
- **Proposition 1.**
  - Among the 256 ternary operations, all 30 three-place placements have exactly the projections, plus both constants when U
    holds 000.
  - All 24 two-literal placements are preserved by majority.
  - The 30 fall into 12 renaming classes, and five mix bending and rigid placements.
- **Theorem 2.**
  - 3472 stripe assignments satisfy every clause of a strip of 24 periods: 10 placements, five tori, four twists, and 18 classes
    except the diagonal class (128 cases excluded).
  - Controls: all 600 stripe assignments with the opposite parity fail, and all 600 diagonal stripes on wall placements along
    odd classes fail.
- **Theorem 3.** 168 configurations of the eight placements on 3 × 3, 3 × 4 and 4 × 4 in 72 non-fitting twist cases, 24 of them
  planted. None was undetermined.
  - In all 168 the odd classes agree, and the cylinders have assignments exactly when a wall construction verifies.
  - All 96 configurations whose twist is odd on the diagonal class contradict.
  - 26 have assignments.
- **Proposition 4.** The twelve configurations are certified and selective, none undetermined.
- **Theorem 7.**
  - The predicted 3 × 3 histograms over 16 classes equal A's for the four placements in all four twists: 234984 non-global
    nonzero patterns predicted exactly.
  - 28 certified configurations on 3 × 3 and 3 × 4, 4 of them selective, have the predicted patterns.
- **Results of A.** The counts in Proposition 6: exact counts equal on 3 × 3 and 3 × 4; sampled counts within |z| ≤ 1.15.

## What this does not show

- That bending walls make a contact selective on every torus. This is certified on 3 × 3 and seen on every torus computed in A.
- An exact rule for the eight bending placements with a free place. Their walls have choices, so only the sufficient condition of
  Remark 8 is proved. Without determinism a wall need not be periodic, and extracting a cycle that avoids its own copies needs an
  argument not given here.
- Whether placements 191 and 239 ever contradict along the diagonal class. Theorem 2 confines them to it, and on the tori computed
  they never contradict at all.
- Anything about two-literal placements beyond Proposition 1(a); their direction structure is the trichotomy of
  `LINE-DETECTOR-20261023-001B-P001`.
- Anything about other triangulations, larger cells, or classes beyond the arguments' hypotheses. Theorems 2 and 3 hold for all
  tori and classes.
- Anything about space or physics. Lattices and twists are declared.
