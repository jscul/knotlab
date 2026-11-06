# Interference: what the ETH refutations give the contact-first program

Epic `INTERFERENCE-20261029-001`, 2026-10-29.

## The question

- **The owner's request (2026-10-29).** After reading about the two October 2026 refutations of the Exponential Time Hypothesis:
  "Let's see if we can use anything from their proof to further our local research. This should be comprehensive."
- **What the two proofs share.** Both count the satisfying assignments of a k-CNF exactly in time 2^{O(n/√log n)} when clauses
  grow linearly with variables, and both get their speed from cancellation:
  - every clause is written as 1 − Π(1 − ℓ);
  - intermediate sums are signed and count nothing;
  - OpenAI recovers the count by interpolation, after a low-degree polynomial matches (−1)^j on the bulk of a binomial;
  - Anthropic uses the octonion eight-square identity to trade two crossing equality tests for a four-place parity times signs.
- **The program's position.** It has worked only with allowed states and nonnegative witness counts. Three epics recommended
  "signed witnesses" without taking it up (`HUB-DIMENSION-20261024-001`, `NATIVE-COUNTING-20261024-001`, `TWIST-3D-20261025-001`).
- **The three tests.**
  - (A) Definability: do cancelling witnesses move the two/three boundary?
  - (B) Patterns of patterns: do signed laws survive native coarse-graining?
  - (C) Cost: do the papers' finite cancellation cores replay independently?
- **Intuitions targeted:** the two/three boundary; everything relational (harmonies as cancellation); growth of emergent
  information across scales; space from logic without a drawn space.

**The evidence:**
- [One cancelling witness per knot](../../proofs/INTERFERENCE-20261029-001A/INTERFERENCE-20261029-001A-P001_one_cancelling_witness_per_knot/proof.md) (A, proof);
- [Signed laws survive native coarse-graining](../../proofs/INTERFERENCE-20261029-001B/INTERFERENCE-20261029-001B-P001_signed_laws_survive_native_coarse_graining/proof.md) (B, proof);
- [Replay of the cancellation cores](../../experiments/INTERFERENCE-20261029-001C/INTERFERENCE-20261029-001C-E001_cancellation_cores_replay/contract.json) (C, exploratory experiment; results in `artifacts/INTERFERENCE-20261029-001C/`);
- the owner decision request, [canonical_correction_request.md](canonical_correction_request.md);
- scoping (scratch, not evidence): the first signed census, the hyperdeterminant and isometry probes, and the shared-boundary probe.

## Outcome in one paragraph

**Cancellation is the resource the program has been missing, and it is exactly what the ETH refutations run on.**
- **A (proved).** The program's two/three boundary, that no 2-CNF with witnesses defines a knot, is a boundary of positivity. With
  nonnegative weights no sum over hidden bits of two-variable factors has a knot as its support. With signs, every three-bit knot
  is exactly one hidden bit away from pairwise parts, and a 3-CNF is one hidden bit per clause. That signed form is where both
  refutations begin.
- **B (proved).** Under counting, native coarse-graining keeps only parity. With weights ±1:
  - 14 of 16 classes are rebuilt and 12 are reproduced exactly by native gadgets of three or five copies;
  - 10 are exact on the native triangle, so the Sierpinski gasket carries signed not-all-equal at every level;
  - signs supply identity wires, the role hubs played in `EXACT-TOWERS`.
- **What did not change.** The Fibonacci knots are never rebuilt with ±1 weights, and the shared-boundary (triangular-lattice)
  substitution stays parity-only on the first three spheres. Interference revives knots in finitely ramified towers, but has not
  built two-dimensional space.
- **C (exploratory replay).** The finite cancellation cores of both refutations recompute exactly from the papers' statements, with every control failing as it should: the eight-square identity (the octonion sign table is a Hadamard matrix of order 8), the grouped pieces of Anthropic's Lemma 2, the partition pieces of its Theorem B at 1, 2 and 3 bits, and the swap-matrix lemmas of OpenAI's construction. No discrepancy was found. This is a small-size replay, not a check of the asymptotics or of the Lean files.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorems 1–2 | Nonnegative sums over hidden bits of two-variable factors have majority-closed supports and never give a knot; with no hidden bits the support is never a knot, whatever the signs. |
| A, Theorem 3 | A clause of any width is 1 − Π(1 − ℓ), one hidden bit; a k-CNF with m clauses is a signed pairwise sum with m hidden bits; a relation excluding z tuples needs at most z. |
| A, Theorem 4 | All 16 classes of three-bit knots are exactly one hidden bit away from pairs: real tensor rank 2 (hyperdeterminant 1, 4, 4, 5 for atoms, pairs at distance two, parity, three-excluded), with not-all-equal and twisted not-all-equal (hyperdeterminant −3) after one pairwise sign; golden ratio in the three-excluded and not-all-equal decompositions; every decomposition has a negative entry. |
| B, Theorem 1 | An exact signed fixed point (legs relabelled) multiplies any network's signed sum by λ per copy and keeps its law at every level of its tower (7,108 cases iterated to level 4). |
| B, Lemma 2 | Two copies sharing two variables contract to an identity exactly when a flattening has orthogonal rows of equal norm; unsigned, only parity; every exact fixed point of the doubled-edge shape contracts it to an invertible matrix (a signed wire in 19,840 of 19,872 cases, a shear in the other 32). |
| B, Theorem 3 | Census over native gadgets of three and five copies, every shape, placement and ±1 sign pattern: 14 classes rebuilt, 12 exact, 10 on the triangle; never rebuilt: the Fibonacci knots; rebuilt but never exact: or and nand. |
| B, Proposition 4 | Signed not-all-equal (−1 on 110) is exact on the native triangle with factor 3; every signed not-all-equal-type law with positive hyperdeterminant is (sufficient, not necessary). |
| B, Proposition 5 | Shared-boundary substitution, signed laws constant on rotation orbits, tetrahedron/octahedron/icosahedron: exact only for parity. |


## Technique inventory

The sources: OpenAI, "The Exponential Time Hypothesis is False" (17 October 2026, revised 25 October); Anthropic, "A 2^{o(n)} Time
Algorithm for 3-SAT" (hexagon:2610.00577v1, 27 October); S. Kintali, "A simplified proof of ETH is false" (26 October). All
three are unreviewed.

The verdicts:
- **used** — the technique enters a proof of this epic;
- **replayed** — independently recomputed in ticket C;
- **reading** — a statement about the program that rests on the technique but is not a new theorem;
- **candidate** — a possible future transfer, not attempted;
- **no transfer** — classical machinery with no open question in the program that needs it.

### OpenAI's proof (with Kintali's simplification)

| Technique | What it does | Program question | Verdict |
| --- | --- | --- | --- |
| Clause polynomials Φ_e = 1 − Π(1 − ℓ), #F = Σ_x Π_e Φ_e | Moves every clause into a signed sum of products of one-variable terms | Two/three boundary (question 2, witnesses) | **used** (ticket A, Theorem 3): a clause is one cancelling witness, so every 3-CNF is a signed pairwise gadget. With nonnegative weights no knot arises (Theorem 1). |
| Count-preserving sparsification (Impagliazzo–Paturi–Zane; Dell et al.) | Reduces to formulas with linearly many clauses | — | **no transfer**: native networks are already sparse. |
| Bounded occurrences by cycles of implications | Replaces a variable in d clauses by d copies tied by a 2-clause cycle | Hubs (`NATIVE-HARDNESS-20261024-001`: hardness needs knots and hubs) | **reading**: a hub (equality fan-out) is a cycle of two-place implications, with no emergence. This agrees with the hub/contact distinction of 2026-10-29. Nothing new. |
| Deformation L_{e,v}(T; X): at T = t the formula splits into groups joined only by a few integer linear measurements; Taylor data at t = 1..Q, then Hermite interpolation back to T = 0 | Cuts contact algebraically, at the price of enumerating the measurements | Depth of holes (charge networks), cut widths | **candidate**: "how many linear measurements decouple a network" is trivial for parity networks (one sum per cut) and not native for other knots. Not attempted. |
| Swap matrices Π_t on ([r]×[r])^Q, A = V f(W), with f matching (−1)^j on the binomial bulk; I − A has low rank, and nonzero entries disagree at fewer than R nodes | The core lemma. Parity of the swap count is low-degree on the bulk (non-rigidity of Walsh–Hadamard matrices, Alman–Williams) | Degree of parity: our NS/PC degree theorems for Tseitin (`DEEP-HOLES`, `CUTWIDTH-DEPTH`, `PC-DEGREE`) | **replayed** (ticket C, part 4). **Reading**: our lower bounds say parity needs high degree everywhere. OpenAI needs it only on the bulk of a binomial, and pays for the tails with measurements. **Candidate**: refutation degree of Tseitin restricted to a Hamming-weight window. |
| Boolean inclusion–exclusion over small supports | Extracts Taylor coefficients without expanding | — | **no transfer** (classical). |
| Balanced schedules by conditional expectations | Derandomizes the placement of variables | — | **no transfer** (classical). |
| Parity tests on violation vectors (Tanner/expander codes over the clauses), modular counting of violated clauses | The general-k bound | Charge networks are Tanner-type parity networks | **candidate**: "violation parity networks". Not attempted. |
| Rate 2^{O(n/√log n)}: R ≈ √Q from the central limit theorem | The √ comes from Gaussian concentration of the number of antisymmetric factors | — | **reading** (see the √log note below). |

### Anthropic's proof

| Technique | What it does | Program question | Verdict |
| --- | --- | --- | --- |
| Clause graph: nodes are clauses, edges are equality tests on shared variables; the cost of an edge is the number of bits through which it factors (integer rank, eq. 3); merge and cut | Counting as a sum over the bits crossing cuts. On expanders every balanced cut is crossed by Ω(n) bits | Our layout-width theorems (NS degree = toggle width, PC degree ≈ half the carving width, sizes 2^Θ(tw) on cellular graphs) | **reading**: the barrier they break is the one we measured for positive and linear reasoning. **Positivity barrier** (below): nonnegative rewritings never lower a crossing's cost. |
| Eight-square identity: 2[x=v][y=u] = [x⊕y⊕u⊕v=0](σ(x,y)σ(v,u) + σ(x,u)σ(v,y)) | Rewrites two crossing equality contacts as a four-place parity times row-local or column-local signs. The row term crosses the row cut with 3 bits instead of 6 | Knots versus contacts | **replayed** (ticket C, part 1). knotlab: one bit-slice of the hyperedge is a knot, while the two equalities are not (they fail K2). **Reading**: cancellation buys a cheaper cut by adding emergence. σ is a Hadamard matrix of order 8 (replayed). Normalized, its rows form an OA(8,7,2,2), one of the 480 maximal-emergence relations on seven bits of `EMERGENCE-BITS-20261021-001A`. This is a coincidence of the unique order-8 Hadamard matrix, not a mechanism. |
| Grid, rows or columns merged per term; grouped pieces A_i with costs t + 3(t−i) + 6i and t + 6(t−i) + 3i | The per-level factor 11/12 | — | **replayed** (ticket C, part 2). |
| Theorem B: pieces as matrix entries of operators on Q[t₁, t₂, …] (Heisenberg modes, partitions); costs log Σ p(·) | Per-level factor 1/√2, which gives the exponent (log m)^{1/2} | — | **replayed** at 1, 2 and 3 bits (ticket C, part 3). **Reading**: the √ is the √E growth of log p(E) (Hardy–Ramanujan). |
| Balancing by random grouping; recursion e_ℓ → 0 | — | — | **no transfer** (classical). |
| Inclusion–exclusion over sets of violated clauses with sparse parity checks (Appendix D, the bound in n) | — | As OpenAI's parity tests | **candidate** (as above). |
| Lean statement about Mathlib Turing machines | — | Tooling | **no transfer** in this epic. |

### Where the transfers land

| Program question | Transfer | Outcome |
| --- | --- | --- |
| Two/three boundary (thesis; question 2, witnesses) | Clause = 1 − Π(1 − ℓ); signed pairwise gadgets | **Proved** (A): the boundary is positivity. Every three-bit knot is one cancelling witness away from pairs. |
| Patterns of patterns (question 9) | Signed laws in native gadgets | **Proved** (B): 14 of 16 classes rebuilt and 12 exact with signs, against 2 without. The shared-boundary substitution stays parity-only on the first surfaces. |
| Complexity: the HHH conditional benchmark | ETH refuted (claimed) | §4 of `COMPRESSION-ROBUST-PROOF-COMPLEXITY-001HHH` assumes E3, a deterministic ETH for strict 3-CNF. If the claims hold, that benchmark is vacuous. No proved result depends on it. Not edited (closed, outside this scope). |
| Proof complexity (Tseitin degree and size) | — | Unaffected: the algorithms are not resolution, PC or SoS proofs, which need 2^Ω(n) on random 3-CNF. |
| Counting dichotomies (#P-hard versus polynomial) | — | Unaffected: polynomial-time reductions. No result in the repository uses #ETH. |
| Verification of the claims | Replay | Ticket C (see the decision note). |

### The positivity barrier (recorded here, not a ticket: elementary)

Let C = [x=v][y=u] on b-bit strings, and write C = Σ_s A_s with every A_s nonnegative. Each A_s ≤ C entrywise, so its support lies
in the support of C. That support is a permutation pattern both in the row flattening {x,y}|{u,v} and in the column flattening
{x,u}|{y,v}. A nonnegative matrix supported in a permutation pattern has rank equal to its number of nonzero entries. So every
piece costs log₂|supp A_s| bits in both flattenings, and covering 2^{2b} support points with N pieces forces
max_s min(row cost, column cost) ≥ 2b − log₂ N. For the recursion this means ρ ≥ 1 − o(1): **counted (nonnegative) rewritings
cannot lower the cut cost of a crossing at all**, while the signed eight-square identity lowers it to 11/12 per level, and the
pieces of Theorem B to 1/√2. This is a fooling-set argument, labelled textbook. It is the cut-cost form of ticket A's
Theorem 1.

### The √log n rate (reading, not a result)

- **Both proofs land on √log n for sparse formulas.**
  - In OpenAI's proof the √ comes from the central limit theorem. A degree-R polynomial can match (−1)^j only on about R values,
    and the binomial's mass lies within √Q of its mean.
  - In Anthropic's proof it comes from log p(E) ~ c√E, the entropy of a free boson. The per-level factor of Theorem B is
    ρ = f(2h)/(2f(h)) with f = log dim V_E. Every vertex algebra has f(E) ∝ √E (Cardy growth), which gives ρ = 1/√2 and an
    exponent of 1/2.
- **What would beat it.** A structure with log dim V_E ~ E^β for β < 1/2 that keeps the locality identity of Lemma 9 would give
  ρ = 2^{β−1} and a better rate.
- **What blocks lower bounds.** Lower bounds on such crossing decompositions are close to algebraic circuit lower bounds
  (Hrubeš–Wigderson–Yehudayoff; Rossman–Zhu 2025), so a barrier result here is unlikely to be cheap.
- **Status.** Recorded as an orthogonal direction, not attempted.

## What was replayed (C)

Ticket C is an exploratory experiment (`INTERFERENCE-20261029-001C-E001`): an independent reimplementation from the papers'
statements, at small parameters, with one control per part that must fail. Evidence is the two runs made after activation
(`result_parts_1_2_4.json`, `result_parts_3.json`, combined in `result.json`). Earlier runs were feasibility runs.

| Part | What was recomputed | Outcome |
| --- | --- | --- |
| 1. Eight-square identity (Anthropic eq. 12) | All 4,096 settings; the costs of the crossing and of the two terms across rows and columns; the sign table; knotlab on the hyperedge | 0 violations. Crossing 6 and 6 bits, row choice 3 and 6, column choice 6 and 3. σ is a Hadamard matrix of order 8. knotlab: one bit-slice of [x⊕y⊕u⊕v = 0] is a knot (minimum width 4); the two equalities are not (they fail K2). Control (one flipped table entry): 28 violations. |
| 2. Lemma 2 grouped pieces | t = 1, 2 blocks (3 and 6 bits per string); Σ_i A_i and the ranks of every A_i by rows and by columns | Σ_i A_i = 2^t[x=v][y=u] exactly. Every rank is within its bound; at t = 2 the mixed piece has rank 960 against 2^11. Control (row and column costs swapped): a bound is violated. |
| 3. Theorem B pieces | λ = 1, 2, 3 bits (h = 2, 4, 6): the operators of eqs. (47)–(48) on Q[t₁, t₂, …] via the one-part recursion (O2), the pieces A_s of eq. (53), their sum, and the ranks of every A_s by rows and by columns | Σ_s A_s = h![x=v][y=u] exactly at all three sizes (the 3-bit case took 1.8 hours on one CPU). Every rank is within the stated counts R_s^row = Σ_i p(s+i) and R_s^col = Σ_i p(2h−s−i). At these sizes the worst piece costs more than the plain crossing: 7.2, 12.1 and 16.2 bits against 4, 8 and 12. The paper's saving to ρ = 1/√2 is asymptotic, as it states. Control (the sign (−1)^i dropped from Q_s): the sum identity fails. |
| 4. Swap-matrix construction (OpenAI, via Kintali) | (r, Q, R) = (2,4,2), (2,5,2), (3,3,2), (2,6,3), with D = 256 to 4,096 | A fixes every basis vector whose count of antisymmetric factors lies in the window. rank(I − A) equals the number of exceptional vectors (94, 349, 243, 883). Every nonzero entry disagrees at no more than R − 1 nodes. Control (degree R instead of R − 1): the bound is exceeded. |

None of the parts found a discrepancy with the papers. This is a finite check at small sizes. It does not test the asymptotic
accounting, the parameter choices or the Lean formalizations.

## Related work that landed during this epic

`SHARED-SUBDIVISION-20261029-001` closed while this epic ran. It took the owner's recommended shared-boundary route with counts,
on the triangular lattice: only affine rules reproduce themselves with a knot, and not-all-equal never does. Ticket B's
Proposition 5 is the signed analogue on closed spheres (cyclic signs, three spheres), computed independently. It agrees: signs
do not yet make any non-linear law exact on genuine two-dimensional space.

## Assumptions this challenges

- **"No 2-CNF with witnesses defines a knot" is about the canonical (existential) reading.** It is equally a statement about
  nonnegative counts, and it fails once witnesses may cancel (A). The thesis is best stated as a positivity boundary.
- **"Only parity survives native patterns of patterns"** holds for allowed states and for counts, not for signed laws (B). Ten
  classes are exact on the native triangle once signs are allowed.
- **"Hubs are needed for non-parity self-reproduction"** (`EXACT-TOWERS`, `HUB-SURVIVORS`): signs supply identity wires
  natively. Not-all-equal is reproduced by three native copies with one sign, where counting needed seven copies on the Fano
  plane with hubs.
- **Not challenged.** The canonical K1–K3 test (signed sums are a second reading, recorded in the decision request), and the
  parity-only answer on genuine two-dimensional space (`SHARED-SUBDIVISION`; B, Proposition 5).

## Complexity notes

- **COMPRESSION-ROBUST-PROOF-COMPLEXITY-001HHH, §4.** It states a conditional benchmark under E3, deterministic ETH for strict
  3-CNF. If the 2026 refutations hold, E3 is false and the benchmark is vacuous. The implication itself stays true, and the record
  already marked E3 as an unproved premise. The record is closed and outside this scope, so it was not edited. A future
  maintenance pass could add a note.
- **The program's proof-complexity lower bounds** (Tseitin degree and size) and counting dichotomies (polynomial-time
  reductions) are unaffected.

## Owner decision requested

[canonical_correction_request.md](canonical_correction_request.md): should witnesses be allowed to cancel, as a second reading
beside the existential one, as a declared substrate (like hubs), or not at all? This epic tested both sides, as the owner prefers.
The signed side gives more results (A, B), and the canonical side is untouched.

## Process notes

- **Ticket C.** The replay's first runs (parts 1, 2 and 4) were made before the ticket's preflight transition was recorded. They
  were treated as feasibility runs, moved to scratch, and rerun after activation. Only the post-activation runs are evidence.
- **Ticket B, three checker failures fixed.**
  - A first statement that every doubled-edge contraction is a signed permutation was refuted by the check (32 shear cases) and
    corrected.
  - A control used triangle placements from the scoping script in a different slot convention; it now uses the explicit formula
    of the proof.
  - A control meant to fail, a non-cyclic sign on parity, did not fire: the sign is a pairwise gauge and parity stays exact. This
    is recorded as an observation, and the control is now a change of magnitude.
- **Ratio** (focus policy, section 7). Artifacts that changed a conclusion: 3 (A, B, C). Administrative: 3 (the decision note,
  the decision request and the Z ledger). Administrative artifacts are half of the total, so the next action must be substantive
  or stopping, not another record.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — use the ETH refutations in the program (INTERFERENCE-20261029-001) | **Status:** Successful | A: the two/three boundary is a positivity boundary, one cancelling witness per three-bit knot. B: signed laws survive native coarse-graining (14/16 rebuilt, 12 exact, 10 on the triangle). C: all four finite cores replay exactly, with every control failing as it should (exploratory). Unresolved: genuine two-dimensional space, the Fibonacci knots, weights other than ±1. |
| Local direction — interference (signed witnesses) | Continue | The first test of the resource reversed a core reading: only parity survives becomes most knots survive. The remaining discriminators (real weights, genuine space, signed hub gadgets) are cheap and decisive. |
| Broader exploration — question 9, space from a law | Known alternatives | Genuine two-dimensional space: parity-only with counts (`SHARED-SUBDIVISION`) and with cyclic signs (B). Real weights, signed hub gadgets and orientation rules are untested. |
| Long-term goal — the two/three thesis and space from logic | Capability gained: a reading. Obstruction: none new | The thesis becomes a positivity statement. Interference revives knots across hierarchical scales but has not yet built two-dimensional space. |
| Next recommendation — interference on genuine space | **Next step:** Continue, as a fresh epic. Test signed and real-weighted laws on the triangular-lattice rules of `SHARED-SUBDIVISION` (every sign pattern and orientation rule), starting from the golden-ratio weights of the Fibonacci knots whose one cancelling witness carries φ, and signed hub gadgets for not-all-equal below seven copies. | First discriminator: exactness at scale 2 for any non-affine rule. Scratch probe (not evidence): for not-all-equal, no real cyclic weighting is exact on the three spheres (per-face log factors always spread by at least 0.245). For the three-orbit knots, an unconstrained optimizer collapsed onto degenerate, nearly frozen weights, so a constrained search is the first task. |
| Interest — that recommendation | **2/3 — Promising** | A non-affine law exact under shared subdivision would be the program's first two-dimensional space built from a law, and it is the natural meeting point of this epic and `SHARED-SUBDIVISION`. Main uncertainty: both the counted census and the cyclic signed probe point to affine-only exactness, so a theorem "exact self-reproduction on genuine space is affine, even with interference" is a likely outcome. That would also be informative. |
| Execution — that next action | Deferred to the owner | The owner also needs to decide the interference request. Stop condition: no non-affine signed or real-weighted rule is exact at scale 2 on the first tori and spheres. |

