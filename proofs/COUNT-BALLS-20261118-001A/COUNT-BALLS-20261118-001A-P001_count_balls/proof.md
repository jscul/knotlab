# Count balls: what is settled by construction and by classical results

Ticket `COUNT-BALLS-20261118-001A`, 18 November 2026. Checked by ticket B's gates and frozen run
(`experiments/COUNT-BALLS-20261118-001B/COUNT-BALLS-20261118-001B-E001_outlines/`). Referee pending.

Notation. A base has N allowed states; for distinctions x, y the disagreement count d(x, y) is the number of states in which
they differ, and C(x, y) = 1 − 2d/N. The count's **ball** at level ρ around x is {y : d(x, y) ≤ ρ}; its **outline** is the set of
ball members with a count-nearest distinction outside the ball. A **split base** is one whose states are the two all-equal states
and, for each of a set of splits {S, S̄} of the distinctions, both S and S̄ (as the set of distinctions with value 1). k is the
least number of colours of the splits' crossing graph; λ is the least number of chains of nested oriented splits that cover them
(Eppstein's lattice dimension).

## S1. Split bases: the count is twice the number of separating splits

For a split base, d(x, y) = 2 · #{splits separating x and y}: a state S puts x and y on different values exactly when the split
{S, S̄} separates them, and each split contributes its two states; the all-equal states separate nothing. ∎

**Boxes.** For the box of sides n₁ × … × n_d (states: the cuts {x : xᵢ ≤ c}, 0 ≤ c < nᵢ − 1, their complements and the all-equal
states; `KNOT-ORDER-20261117-001` and `GRID-GROW-20261117-001` show betweenness knots give exactly these for d = 2), the cuts of
coordinate i separating x and y number |xᵢ − yᵢ|, so d = 2‖x − y‖₁. The ball of count 2j is the L1 ball of radius j clipped to the
box; from a start at L1 distance at least j from every side, the outline (count exactly 2j) has Σᵢ 2ⁱ C(d, i) C(j − 1, i − 1)
members: 4j for d = 2 and 4j² + 2 for d = 3. The ball grows like (2j)^d/d!, the outline like ball^((d − 1)/d). In two orders the
outline's norm is the taxicab norm, whose unit ball is a parallelogram, so its Gołąb π is 4. The crossing graph is complete
d-partite (cuts of different coordinates cross when all nᵢ ≥ 2; cuts of one coordinate are nested), so k = d, and λ = d. ∎

**Q_d** (all nᵢ = 2): the outline at count 2j has C(d, j) members. ∎

**λ = 2 bases (NN's grids, `NEVER-NEST-20261118-001#4`).** Cover the oriented splits by two chains of nested sets and give each
distinction the pair (number of chain-1 splits not containing it, number of chain-2 splits not containing it). Two distinctions
are separated by a split of chain i exactly when it lies between their i-th coordinates, so by S1 d = 2‖x − y‖₁ in these
coordinates. So on every base with λ = 2, NN's grown grids included, the count is twice the L1 distance of its two orders: a
two-way ruler on the grown shape, its balls taxicab diamonds clipped to that shape. (This is the defining property of the lattice
dimension, stated in the program's terms.) ∎

## S2. The count's growth does not read k

The 2 × m ladder is the box of sides 2 and m: k = λ = 2. The comb is the line 0, …, m − 1 with one pendant distinction joined to
each inner one; as a tree its splits cross nothing, so k = 1, and λ = ⌈leaves/2⌉ (Ovchinnikov), 5 at m = 10. From a middle
distinction i of the line, at count 2j with 2 ≤ j ≤ the steps to the nearer end:
- ladder: (0, i ± j) and (1, i ± (j − 1)), 4 members;
- comb: i ± j on the line and the pendants of i ± (j − 1), 4 members.

So every middle start sees the same outlines, 4 at every count from 4 on, in a base with two orders and in one with one; the
ball's growth is linear in both (outline against ball, exponent 0). The count's growth reads how the distinctions spread, not how
the splits cross. (Checked: gate G-ladder-and-comb-layers at m = 10.) ∎

## S3. Parity bases are blank

If the states form a linear code in which no pair of distinctions is tied, every pair takes all four joint values equally often,
so d = N/2 for every pair (`DISTANCE-ORDER-20261117-001A`, statement 4): every ball is the start alone or everything. ∎

## S4. The state side

Let D(X, Y) = |X Δ Y| on states (the states within r disagreements of a state).
1. **Parity bases.** For a code, Y ↦ Y Δ X is an isometry of the state set for every state X, so every state sees the same profile:
   the code's weight enumerator. ∎
2. **Blind to translation.** For any base and any allowed state X, the translate {Y Δ X} is isometric to the state set. When X
   is not all-equal the translate is another base (its all-equal state is X's image), and its crossing graph can differ. The run's
   census meets this at four distinctions: the star with three tips (k = 1) and its translate (k = 2) have the same state profile
   (computed; the advisor's example). ∎
3. **Rooted at the all-equal state, it reads the orders.** With Z the all-zero state, |X| = D(Z, X) and
   |X ∩ Y| = (|X| + |Y| − D(X, Y))/2, so the four quadrant sizes of every two splits are known. Two splits cross exactly when all
   four are positive, and two oriented splits are joined in the semicube graph exactly when |X ∪ Y| = n. So the state metric with
   Z marked determines the crossing graph and the semicube graph, hence k and λ. (Marking Z needs the values 0 and 1, not the
   distinctions' names.) ∎

## S5. The chain grid reduces to a two-valued pair law

A not-all-equal knot (a, b, p) whose p lies in no other knot: given a and b, p is forced (to the other value) when a = b and free
when a ≠ b. So summing p out weights the pair (a, b) by 1 if equal and 2 if not, and a chain of l knots between u and v weights
it by the entries of [[1, 2], [2, 1]]^l: (w_eq, w_ne) = ((3^l + (−1)^l)/2, (3^l − (−1)^l)/2), and
(w_eq − w_ne)/(w_eq + w_ne) = (−1/3)^l. On the grid distinctions this is the square-lattice Ising model at tanh K = (−1/3)^l, a
high-temperature model for every l (|t| ≤ 1/3 < √2 − 1). The grid is bipartite, so flipping one class turns it into the model at
t = 3^(−l), and C = (−1)^(l·‖x − y‖₁) C₊ with C₊ > 0: for odd l the raw count makes two classes. For the loose distinction,
E[s_p | s_a, s_b] = −(s_a + s_b)/2, so C(x, p) = −[C(x, a) + C(x, b)]/2. (Gates: literal enumeration against the reduced law on
2 × 2 at l = 1, 2, 3 and on 3 × 3 open and wrapped at l = 1; the two classes; the loose identity.) ∎

## S6. The chain grid's outline (classical)

Above Tc the square-lattice Ising correlation decays in direction n as C₊(rn) ≍ r^(−1/2) e^(−m(n) r), where m is the support
function of Q = {q : cosh q₁ + cosh q₂ ≤ A}, A = (1 + t²)²/(2t(1 − t²)) = cosh² 2K / sinh 2K: the zero set of Onsager's symbol
(1 + t²)² − 2t(1 − t²)(cos k₁ + cos k₂) at imaginary momentum (Cheng and Wu 1967; by Kramers–Wannier duality the Wulff shape of
the crystal below Tc, Rottman and Wortis 1981, Avron, van Beijeren, Schulman and Zia 1982, Holzer 1990, Akutsu and Akutsu 1990;
Ornstein–Zernike form, analytic and strictly convex, Campanino, Ioffe and Velenik 2003). Along an axis m = 2(K* − K)
(Onsager); at l = 1 this is ln(3/2), 0.369070 per step in τ. So τ(x) = m(x)/ln 3 + O(log |x|), and the count's outline at large τ
is the unit ball of m, scaled.

- **Strictly convex and analytic for every l.** Q is a sublevel set of the strictly convex analytic f(q) = cosh q₁ + cosh q₂ with
  ∇f ≠ 0 on ∂Q (A > 2), so ∂Q is analytic with positive curvature; the polar of such a body has the same property. So the outline
  has no corner and no flat side. ∎
- **Toward the taxicab diamond.** As l → ∞, A ~ 1/(2t) → ∞ and ∂Q tends, after dividing by ln A, to the square
  max(|q₁|, |q₂|) = 1, so m/ln A tends to |n₁| + |n₂|, and Gołąb's π, continuous in the norm, tends to 4. ∎
- **Computed from the formula** (not a measurement): largest to smallest rate per unit length 1.003400, 1.068608, 1.141877 at
  l = 1, 2, 3; Gołąb π 3.141701, 3.182439, 3.297933, 3.418831 (l = 4), 3.589386 (l = 6), 3.687920 (l = 8), 3.790555 (l = 12).

## S7. The weave (classical)

The endless six-regular weave under not-all-equal is the triangular Ising antiferromagnet at zero temperature. Its pair
correlation is C(r) ≈ a r^(−1/2) cos(Q·r), with Q at the corner of the literature's Brillouin zone, so cos(Q·r) = 1 on the start's
own class and −1/2 on the other two, and a = 2·3^(−1/4)·E₀², E₀ = 2^(1/12) e^(3ζ′(−1)), a = 0.6322260804 (Stephenson 1964, 1970;
the exponent η = 1/2 from the height mapping, Blöte and Hilhorst 1982, Nienhuis, Hilhorst and Blöte 1984). The amplitude is the
same along every repeat because the height field's stiffness is isotropic (three-fold symmetry of a quadratic form). Consequently:
- the raw count's ball below N/2 holds only the start's class, with outline the literature's circle of reach R = (a/u)², u = 1 − 2ρ/N,
  and 2π/(3√3) · a⁴ · u^(−4) members (the class has density 2/(3√3) per unit area of the drawing);
- in τ, the other classes' outlines have reach 1/4 of the own class's, and the ball grows like 3^(4τ), exponentially;
- in the count's own scale the ball grows like u^(−d/η) = u^(−4) and its outline like u^(−(d−1)/η) = u^(−2), so the exponent of the
  outline against the ball, (d − 1)/d = 1/2, reads the dimension d = 2 whatever the scale, while the count's scale alone reads d/η.
(The run checks a, the isotropy to 1e-4 at r ≈ 60, η, the other classes' −1/2, the ball counts and the outline exponent.)
