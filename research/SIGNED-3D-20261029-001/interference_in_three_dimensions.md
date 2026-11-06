# Interference in three dimensions

Epic `SIGNED-3D-20261029-001`, 2026-10-29.

## The question

- **The owner's request (2026-10-29).** "Yes, let's continue," on the recommendation of `SIMPLEX-GASKETS-20261029-001`:
  - run a census of signed bit laws on the edges of ordered triangulations of three-manifolds;
  - decide whether signs let bits see more of a three-manifold than mod-2 cohomology;
  - decide whether anything beyond twisted Dijkgraaf–Witten appears.
- **Setting.** Ordered triangulations with the ordered 2–3 and 1–4 moves of `TWIST-3D-20261025-001A`.
  - One bit sits on each edge, and each tetrahedron labelling has a weight in {−1, 0, 1}, which may depend on the orientation.
  - The move identities must hold for every boundary labelling.
- **Why it matters.** Counting with one bit per edge sees only |H¹(M; Z/2)| (`HUB-DIMENSION-20261024-001`, `TWIST-3D-20261025-001`), and
  three earlier notes named phases as the missing ingredient. The interference line has since made signed laws natural: they build exact
  space on Sierpinski simplices of every dimension.
- **Intuitions targeted:** space from logic without a drawn space; everything relational (phases and cancellation); the two/three
  boundary through positivity.

**The evidence:**
- [Signed bit laws on ordered triangulations: one twist and nothing else](../../proofs/SIGNED-3D-20261029-001A/SIGNED-3D-20261029-001A-P001_one_twist_and_nothing_else/proof.md)
  (A, exhaustive census);
- [What the twist sees of a three-manifold](../../proofs/SIGNED-3D-20261029-001B/SIGNED-3D-20261029-001B-P001_what_the_twist_sees/proof.md)
  (B, invariants, checked on sampled triangulations);
- scoping (scratch, not evidence): the first factor scan, the support and sign enumerations, and the counts for the excluded readings.

## Outcome in one paragraph

**Signs add one phase and one bit, nothing more.**
- **A (exhaustive).** Every signed one-bit edge law with μ ≠ 0 has, up to the global sign, the factors of a counting law.
  - Its support is one of the seven counting supports.
  - Up to the face gauge, it is one of twelve laws: the seven counting laws, the twisted Dijkgraaf–Witten law (−1)^(x₀₁x₁₂x₂₃) on even
    cocycles, its translate on odd cocycles, and three mixed twisted laws.
  - **Interference never creates a relation, only a phase on the parity relations.**
  - **The twist needs the vertex order.** No twisted class has a symmetric member. Signs alone add nothing, as order alone added nothing.
- **B.** The twisted laws compute D(M) = Σ_a (−1)^⟨a³,[M]⟩ over H¹(M; Z/2).
  - a ↦ a³ is linear (Wu), so D is |H¹| or 0. It is 0 exactly when the linking form gives 1/2 on an element of order 2.
  - That bit is not a function of homology: RP³ # RP³ and the quaternion space S³/Q₈ share H₁ = (Z/2)², and sampled triangulations of
    both kinds are told apart.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | The global sign sends (λ, μ) to (−λ, −μ); the face gauge (a sign per face labelling) keeps factors and state sums. |
| A, Theorem 2 | Census: with μ ≠ 0, factors (1, 1), (1, 2), (2, 16) up to sign; supports = the seven counting supports; twelve classes up to gauge, all orientation-independent. |
| A, Corollary 3 | No twisted class has a member invariant under the vertex permutations: the twist needs the order. |
| A, Remark 4 | Laws with μ = 0 exist (no normalized invariant). The 2–3 move alone admits more than 3,000 supports in scoping, many degenerate; not classified. |
| B, Theorem 1 | Normalized values: counting 1, 1, 2, h/2, h/2, h, 1; twisted D/2, D/2, (D + h)/2 twice, D. |
| B, Propositions 2–3 | a ↦ a³ is linear; D ∈ {0, h}; D = 0 iff lk(t, t) = 1/2 for some t of order 2; cyclic H₁ = Z/n: D = 0 iff n ≡ 2 (mod 4). |
| B, Corollary 4 | D is not a function of homology (RP³ # RP³ versus S³/Q₈; both values on sampled (Z/2)² triangulations). |

## Reading

- **What interference does in three dimensions.**
  - The relations are unchanged: constants, the parity (cocycle) relations, and the free law. Signs can only weight them.
  - The single admissible weighting is the cubic phase along the spine 0–1–2–3 of each ordered tetrahedron. Summed over a manifold it is
    a Gauss sum, and it cancels completely or not at all.
  - What it sees is one global bit of the linking form.
- **Three regimes of space from a law.**
  - On shared subdivision of the plane: parity only, even with signs (`SIGNED-SUBDIVISION-20261029-001`).
  - On finitely ramified Sierpinski simplices: non-affine knots, the standing waves, in every dimension (`SIMPLEX-GASKETS-20261029-001`).
  - On three-manifolds: parity, plus one phase bit from interference (this epic).
  - Bulk coupling through shared faces keeps the relations affine. Signs then add global phases, not structure. Non-affine knots build
    space only where cells meet at points.
- **Harmonies.** The owner's "incommensurables cancelling" appears here exactly. When the cubic form is nonzero, the classes with
  a³ = 1 cancel those with a³ = 0, and the cancellation is the information.
- **The excluded readings.** Laws satisfying only the 2–3 identity give invariants of one-vertex triangulations
  (Matveev–Piergallini). That fork has far more solutions, most degenerate, and remains open.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — interference in three dimensions | **Status:** Successful | Exhaustive census: one twist and nothing else. Its invariant is one bit beyond \|H¹(M; Z/2)\|, separating manifolds counting cannot. Open: the 2–3-only reading; complex phases. |
| Local direction — one-bit edge laws on three-manifolds | Practically exhausted | Counting (`HUB-DIMENSION`, `TWIST-3D`) and signs (this epic) are classified. What remains are other readings and labels, where classical answers are expected (Dijkgraaf–Witten with larger groups; Turaev–Viro needs irrational weights). |
| Broader exploration — space from a law (question 9) | Known alternatives | The three regimes are mapped. The positive line is the finitely ramified one, where the open question is on the law's side: is the standing wave forced? |
| Long-term goal — space from logic without a drawn space | Obstruction confirmed | On manifolds even interference keeps relations affine and adds only global phases. Space-building knots live on finitely ramified gluings, which are chosen. |
| Next recommendation — uniqueness of the standing wave | **Next step:** Continue, as a fresh epic. Classify the laws, with real or complex weights, that reproduce themselves on two consecutive Sierpinski levels. Start in the plane with the laws f(x₀, m) (six weights), then general three-bit laws, by Gröbner bases and exact census. Decide whether every non-degenerate solution is a standing wave (sine, or cosine at odd simplex counts) or a known trivial law. | A characterization would say that self-reproduction at every scale forces a harmony, and the censuses in dimensions 2–4 support it. A counterexample would be a new self-similar law. |
| Interest — that recommendation | **2/3 — Promising** | Evidence: three censuses (±1 weights) in which only standing waves persist, and a sector proof that explains them. Main uncertainty: the algebra in more than six unknowns may be heavy, and real weights may admit families the ±1 censuses could not see. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: nothing beyond the earlier censuses. Stop when the planar f(x₀, m) case is decided at levels 2 and 3, or if the Gröbner computation does not finish at that size. |

**Recommendation.** **Continue**, as a fresh epic: uniqueness of the standing wave (2/3). Three alternatives were considered.
- **Whether a law can select its own space (1/3).** Which finitely ramified gluings the wave reproduces on, with dangling parts excluded.
  It is closer to the program's aim but not yet well-posed.
- **The 2–3-only reading in three dimensions (1/3).** More than 3,000 supports, mostly degenerate; the payoff is unclear.
- **Complex phases with one bit per edge (1/3).** Classically nothing new is expected, since H³(Z/2; U(1)) = Z/2.
