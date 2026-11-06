# Counting what emerges natively

Epic `NATIVE-COUNTING-20261024-001`, closed 2026-10-24.

## The question

The owner asked to continue both directions recommended at the close of `SURFACE-GLUING-20261024-001` and
`NATIVE-HARDNESS-20261024-001`. This epic took the counting direction.
- **What was known.** Native networks of every law are decided in polynomial time (`NATIVE-HARDNESS-20261024-001C`).
- **The question.** Emergent information is a count of witnesses: is counting it easy?
- **Intuitions this epic targets:** the complexity side of the thesis; the growth of emergent information; space from logic, through
  the genus of the network's surface.

**The evidence:**
- [Emergence is countable exactly when it is topological](../../proofs/NATIVE-COUNTING-20261024-001A/NATIVE-COUNTING-20261024-001A-P001_countable_exactly_when_topological/proof.md)
  (A, proof; hardness conditional on Backens's dichotomy);
- [Not-all-equal worlds count like an Ising model](../../proofs/NATIVE-COUNTING-20261024-001B/NATIVE-COUNTING-20261024-001B-P001_nae_worlds_are_ising/proof.md)
  (B, proof; determinant formula, genus dependence and hardness cited);
- [bounded scan](scan.md) (Holant dichotomies, Fibonacci gates, Kac–Ward);
- **scoping (scratch, not evidence):**
  - the first family classification;
  - the first Kac–Ward runs on prisms;
  - a generator defect producing overlapping edges, found and fixed in B's check (disclosed there).

## Outcome in one paragraph

**Counting what emerges is easy exactly when the law sees only the surface.**
- **The criterion is the Fibonacci recurrence (A).** For a symmetric three-place relation, the criterion for gluing topologically, that
  two glued copies are symmetric in four legs, is the equation f₀ f₂ + f₁ f₃ = f₁² + f₂².
  - That equation is the generalized Fibonacci-gate recurrence of holographic algorithms, plus the generalized equalities.
  - Among the 34 knots it selects exactly the four topological knots: the parity and Fibonacci fusion rules.
  - Each is a sum of two cubes of orthonormal vectors. So any native network counts by a closed formula: 2^g for parity, Verlinde
    dimensions for Fibonacci.
- **The other 30 knots are hard to count (A).** They lie in no tractable family of Backens's Holant dichotomy with pins, so counting is
  #P-hard given that theorem, although deciding is easy.
- **Closed not-all-equal worlds are an Ising model (B).** Without pins, the count of a not-all-equal world is 2^(−n/2) 3^n times the
  even-subgraph sum at −1/3, an antiferromagnetic Ising partition function with e^(2b) = 1/2.
  - On the sphere it is a determinant (Kac–Ward), so polynomial.
  - With the same methods a genus-g surface needs 4^g determinants.
  - On general cubic graphs it is #P-hard (cited).

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Translate native counting with pins into Holant^c | Backens's dichotomy applies, with the knot as the only constraint | Background |
| Expand the topological gluing criterion | It reduces to one equation, the Fibonacci recurrence | Proved (A, Theorem 1) |
| Decompose the topological knots | Sums of two orthonormal cubes; closed count formulas | Proved (A, Theorem 2); 366 networks against brute force |
| Classify the 34 knots against the families | 4 in a family (orthogonal generalized equality), 30 in none | Proved (A, Theorem 3); controls accept a member of each family |
| Fourier transform of not-all-equal | [6, 0, −2, 0], supported on even weights: closed worlds are even-subgraph sums | Proved (B, Theorem 1) |
| Planar determinant | det = Z² on 26 planar straight-line cubic graphs; fails for crossing drawings | Checked (B, Corollary 2, given Kac–Ward) |

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | Topological gluing of a symmetric signature ⟺ f₀ f₂ + f₁ f₃ = f₁² + f₂² ⟺ generalized Fibonacci gate or [a, 0, 0, b]; exactly four knots. |
| A, Theorem 2 | The four topological knots count every native network by Σⱼ λⱼⁿ ∏ legs, in polynomial time. |
| A, Theorem 3 (conditional) | The other 30 knots lie in no tractable family, so their native counting is #P-hard given Backens. |
| B, Theorem 1 | Closed not-all-equal worlds count 2^(−n/2) 3^n Z(−1/3), an Ising model with e^(2b) = 1/2. |
| B, Corollary 2 (given Kac–Ward) | Polynomial on the sphere; 4^g determinants on genus g and #P-hardness in general are cited. |

## What this changes

- **Three statements of the same boundary.** `NATIVE-HARDNESS-20261024-001` showed that native contradictions are parity systems,
  decided in polynomial time. This epic adds the counting side, and three statements now line up:
  - knots that see only the surface (`SURFACE-GLUING-20261024-001A`);
  - Fibonacci gates (holographic algorithms);
  - knots whose emergence is countable.
- **The growth of emergent information.**
  - For the topological laws the count grows by a fixed factor per handle: 2 for parity, and asymptotically D² for Fibonacci.
  - For not-all-equal the cost of computing the count grows per handle (4^g determinants), and in general it is hard.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Native logic is easy | Reading of `NATIVE-HARDNESS-20261024-001C` | **Refined.** Deciding is easy for every law; counting is easy only for the topological laws (given Backens). |
| The topological knots are special to the program | `SURFACE-GLUING-20261024-001` | **Identified.** They are the Fibonacci gates of holographic algorithms, the knots among the tractable counting problems. |
| Emergence counting is a geometry-free notion | Implicit in `EMERGENCE-BITS-20261021-001` | **Refined.** For not-all-equal the cost of counting depends on the genus of the network's own surface. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Theorem 1 | Expanding the gluing criterion | The equation is the Fibonacci-gate recurrence (Cai, Lu and Xia); the identification with topological gluing is `candidate-local-delta`, folklore risk high |
| A, Theorem 2 | Orthonormal diagonalization; Verlinde formula | Classical (holographic algorithm; two-dimensional field theory) |
| A, Theorem 3 | Backens's families, tested finitely | Classical theorem applied; conditional |
| B | Fourier transform of not-all-equal; Kac–Ward | Classical (Ising high-temperature expansion); the reading is new to the program |

**Did the perspective do real work?** Partly.
- **What it supplied.** The question, whether emergence is countable, and the gluing criterion came from the program, and the criterion
  turned out to be exactly the known tractability condition.
- **What is classical.** The complexity statements are classical or cited.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: counting what emerges natively | **Status:** Successful | Exact counting is easy exactly for the topological knots (given Backens); closed not-all-equal worlds are an Ising model, a determinant on the sphere. |
| Local direction: exact native counting | Practically exhausted | All 34 knots classified, with pins; closed worlds treated for not-all-equal. |
| Broader exploration: complexity program | Known alternatives | Approximate counting is unexamined; signed counting is named by the topology epic. |
| Long-term goal: the complexity side of the thesis | Capability gained | Deciding native networks is easy for every law; counting what emerges is easy exactly for the topological laws. |
| Next recommendation: approximate counting of native emergence | **Next step:** Continue, with a fresh epic | Is emergence hard to count exactly but easy to approximate? Lead: closed not-all-equal worlds are antiferromagnetic Ising with tanh b = −1/3 on cubic graphs. That lies inside the uniqueness region (|tanh b| < 1/2), where approximation schemes are known (Sinclair, Srivastava and Thurley). First discriminator: for each knot, test the correlation-decay condition on native trees, and look for a knot whose approximation is hard. |
| Interest: that recommendation | **2/3: promising** | It could split "hard to count" into exact and approximate, refining the thesis reading. Main uncertainty: known results may settle most knots. |
| Execution | Deferred to the owner | Bound: one epic; stop if every knot falls under known approximation schemes or known hardness. |

**Alternatives:** signed witness counts, shared with the topology epic (1/3); a note collecting the decision, refutation and counting
results for native networks (1/3: moderate magnitude, folklore risk medium to high).
