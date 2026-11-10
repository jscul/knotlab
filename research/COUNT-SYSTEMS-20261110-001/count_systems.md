# The sphere's count in stronger proof systems

Epic `COUNT-SYSTEMS-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `TWO-ROUND-BRIDGE-20261106-001`'s lead L1 asked for lower bounds for the sphere's count in every proof system.
  Resolution (size 2^{Θ(√n)}, `SPHERE-SIZE-20261107-001`) and the Nullstellensatz (the count is PPADS^dt-complete, outside PPA^dt and
  PPAD^dt, `COUNT-TFNP-20261107-001`) were settled; bounded-depth Frege, Res(⊕) and cutting planes were open. The reassessment pass
  surfaced the lead at (2, 2), and the coordinator selected it on 2026-11-10 as the closest open lead to P vs NP.
- **The question.** What do the known reductions settle in the open systems, and what does the count need from each one?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Bounded-depth Frege needs exponential size.** Every depth-d Frege refutation of the sphere's NAE formula has size exp(n^{ε_d}). The binary left-pigeon principle reduces to SINK by succ = f, pred = g; SINK reduces to one-sided grid Sperner and Sperner to the sphere by decision trees of depth O(log N); and the bijective pigeonhole principle needs exp(N^{ε_d}) at depth d. | proved (from published lower bounds) | A |
| 2 | **Over corner atoms the count is linear.** With a variable for each corner's agreement (a 2-XOR of two points), cutting planes refutes the count in O(n) lines: each line gives Σ ≤ 1, each face Σ ≥ 1, and the two sums contradict because F − L = 2. | proved | B |
| 3 | **Every corner parity holds.** Under every assignment each line has 1 or 3 agreeing corners and each face an odd number, so the contradiction is the integer fact "exactly one, not three", invisible modulo 2. Over the points alone the linear relaxation is feasible at x ≡ 1/2. | proved | B |

## Answer

Bounded-depth Frege is settled: the count needs exponential size at every fixed depth, as any PPADS^dt-hard principle does once the
pigeonhole lower bounds are in hand, and close to what Dantchev showed for Sperner's lemma in 2006. Res(⊕) and cutting planes stay open, and the corner count shows why each one is open. Cutting
planes can add and round but sees the corner agreements only as quadratics in the points. Res(⊕) names every agreement as a parity, but
every parity among them holds, so its linear algebra finds nothing and the count would have to be carried inside its clauses. Tseitin is
a parity and the pigeonhole principle a count of variables; the sphere's count is a count of parities, and each of the two systems has
only one of its ingredients.

## Reading

**Interpretation, not a theorem.**
- **The count is between Tseitin and the pigeonhole principle.** Res(⊕) refutes Tseitin by its parity and cutting planes refutes the
  pigeonhole principle by its count; this formula needs both at once. It is a natural candidate to separate both systems from
  Sherali–Adams, which refutes it at degree 3.
- **The lower bound that transferred is the expected one.** Bounded-depth Frege cannot count, and the count's PPADS^dt-hardness carries
  the pigeonhole principle's lower bound to it. The new lower bounds the program would need are for systems that can count or can take
  parities.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** None: both tickets are proofs, with finite checks.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The left-pigeon map to SINK (1) | every instance with N = 4 (checked to 3) | pass: 640,000 instances, 947,200 answers |
| Its composition through the grid colouring (1) | 12 random instances with N = 4, grid side 468 (checked to N = 3) | pass: 16 triangles decoded |
| The corner identities and corner LP (2) | K_9 and K_10 (checked to K_8 and K_6) | pass |

The script is `stress_test.py` beside this note, its output `stress_test.json`; it ran in 103 seconds.

## Literature and provenance

- **Sources.** Ajtai (1988); Pitassi, Beame and Impagliazzo (*Computational Complexity*, 1993); Krajíček, Pudlák and Woods (*Random
  Structures & Algorithms*, 1995); Håstad (FOCS 2023; *TheoretiCS* 2025) for the pigeonhole lower bounds. Beame, Cook, Edmonds,
  Impagliazzo and Pitassi (*JCSS*, 1998) for SINK and PPADS. Göös, Hollender, Jain, Maystre, Pires, Robere and Tao (*Separations in Proof
  Complexity and TFNP*, 2022) for decision-tree reductions, LeftPigeon and unary Sherali–Adams. Buss (*TCS*, 2006), whose Hex
  tautologies, a relative of Sperner's lemma, get the same constant-depth lower bound through a SINK principle.
- **Prior work on Sperner's lemma.** Dantchev (CiE 2006) reduced the pigeonhole principle to Sperner's lemma and showed it has no short
  constant-depth Frege proofs; with `FLAT-STATES-20261107-001B` that already gives a superpolynomial bound for the sphere, for Sperner
  encodings that reduce to the one-sided grid version. Ticket A is a self-contained chain with explicit sizes.
- **Classification.** Known-with-delta for both tickets. Folklore risk is high for ticket A, close to Dantchev's result; the value is the
  program's table, now filled for bounded-depth Frege.

## Workspace assumptions

- **Relied on.** None of the register's dynamics assumptions; the formulas are fixed CNFs.
- **Added.** None.
- **Scope.** The octahedral knot sphere's Kasteleyn-signed NAE formula.

## Ratio

Since the epic opened:
- **Substantive.** Two proofs (A, B) and one stress test.
- **Administrative.** This note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the sphere's count in stronger systems | **Status:** Partially successful | Bounded-depth Frege settled (exponential); Res(⊕) and cutting planes open, with what each lacks located |
| Local direction — lower bounds that need counting or parities | Research directions | No technique for either system applies off the shelf |
| Broader exploration — G3 | Known alternatives | Grown spheres and their flat radius (`HARD-FLAT-20261107-001`'s directions) |
| Long-term goal — G3 Hardness at three places | Obstruction learned | The count's hardness for the strong systems is exactly what Sherali–Adams has and they each half-have: a count of parities |

**Corrections:** none. **Goals:** a G3 checkpoint (obstruction learned); lead `TWO-ROUND-BRIDGE-20261106-001#L1` taken; direction 1
recorded as a sub-goal under G3 (3/3, not taken); directions 2 and 3 to the backlog. **Assumptions:** none added or changed.

- **What the attempt leaves open.** A cutting-planes or Res(⊕) lower bound for the count, or a short refutation in either.
- **The missing bridge to the program's composed topology.** None here; this line asks how hard the sphere's contradiction is, not how
  space is read.

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Cutting planes on the count (G3) | 3/3 — Barrier | 1/3 — Stated | Try to count corner agreements without naming them: derive Σ_{c∈l} e_c ≤ 1 per line from linear combinations of the point inequalities with rounding, on K_2 to K_4, measuring the rank → a short refutation's shape, or a rank that grows with k | Alternative · deferred |
| 2 | Tree-like Res(⊕) on the count (G3) | 2/3 — Substantial | 2/3 — Testable | Play the vortex adversary of `SPHERE-WIDTH-20261107-001` against parity queries: can a parity of points always be answered without fixing the vortex? Compute parity-decision-tree depth on K_2 and K_3 exhaustively → an adversary, or the parity that catches the vortex | Alternative · deferred |
| 3 | Polynomial calculus over F2 on the count (G3) | 2/3 — Substantial | 1/3 — Stated | The count is outside low-degree F2-NS (`COUNT-TFNP-20261107-001B`); read the F2-PC degree on K_2 to K_5 by linear algebra → degree growing with k, or bounded | Alternative · deferred |

1. **Cutting planes.** Payoff 3: a cutting-planes lower bound for a natural PPADS-complete principle would be new in proof complexity and
   would place the sphere's hardness against counting; Concreteness 1: interpolation and lifting, the known methods, do not fit this
   formula, and the rank experiment only probes it.
2. **Tree-like Res(⊕).** Payoff 2: tree-like is the weakest Res(⊕) but no bound is known; Concreteness 2: the adversary exists for
   ordinary queries, and small cases can be computed.
3. **F2 polynomial calculus.** Payoff 2: the dynamic form of the F2 Nullstellensatz, which the count already defeats; Concreteness 1:
   degree computations grow fast with k.

**Recommendation.** Research directions, none selected; direction 1 is recorded as a sub-goal under G3, directions 2 and 3 go to the
backlog, for the coordinator to choose.
