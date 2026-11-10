# F2 polynomial calculus on the sphere's count

Epic `PC-COUNT-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `TREE-XOR-20261110-001` proved that tree-like Res(⊕) size on the sphere's count is at least 2 to the count's
  F2 polynomial-calculus degree, minus 3, and left that degree open as backlog B84. The coordinator selected B84 on 2026-11-10 as the
  more concrete row, asking for a frozen prediction before the small-sphere computation, a bounded literature check, and a check of any
  low-degree refutation against the publication hold.
- **The question.** Does the count's F2 polynomial-calculus degree grow with the sphere, and what does that give for tree-like Res(⊕)?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Degree n^{Ω(1)} over every field.** Every polynomial-calculus refutation of the count has degree at least c n^{1/4}/log n, over every field. The functional pigeonhole principle on a bipartite boundary expander (Mikša and Nordström: degree linear in the holes over every field) reduces to LeftPigeon by trees reading a pointer in O(log N) queries, and through `COUNT-SYSTEMS-20261110-001A`'s chain to the count with n = O(N⁴); degree transfers through such reductions at the cost of the trees' depth. | proved (from published bounds) | A |
| 2 | **Tree-like Res(⊕) needs exponential size.** Over F2, with `TREE-XOR-20261110-001B`, every tree-like Res(⊕) refutation of the count has size at least 2^{c n^{1/4}/log n}, and every parity decision tree has depth at least c n^{1/4}/log n, improving `TREE-XOR-20261110-001A`'s n^{1/8}/log n. | proved | A |
| 3 | **Exact small degrees.** The count's F2 polynomial-calculus degree is 3 on K_2, 4 on K_3 and at least 5 on K_4; its Nullstellensatz degree is 6 on K_2 and at least 6 on K_3; the two-sided control has degree 3 throughout. All four frozen hypotheses hold. | computed (pre-registered, exact) | B |

## Answer

Yes. Algebra cannot refute the count in low degree over any field: a bounded-degree polynomial-calculus refutation would give one for the
pigeonhole principle on an expander, which has none. Over F2 this settles the size question `TREE-XOR-20261110-001` left open: parity
decision trees for the count need exponential size, not only polynomial depth. On the smallest spheres the degree already climbs by one
per step (3, 4, at least 5), while the Nullstellensatz needs 6 on K_2, so the polynomial calculus gains but not enough.

## Reading

**Interpretation, not a theorem.**
- **Positivity, not algebra.** The count has a Sherali–Adams refutation of degree 3 (`COUNT-NOTE-20261107-001B`), yet over the
  rationals, where Sherali–Adams lives, the polynomial calculus needs polynomial degree. What refutes the count cheaply is the sign of a
  sum, not its value: the count is a count of things that cannot be negative.
- **The open window.** The degree lies between c n^{1/4}/log n and O(√n) (the resolution width plus 1, `SPHERE-WIDTH-20261107-001`). The
  small spheres fit k + 1, which is of order √n; that is three points, read as a pattern only.
- **Why only tree-like.** Dag-like Res(⊕) is not closed under the substitutions used here, and no superpolynomial dag-like Res(⊕) bound
  is known for any formula; the strongest known results need lifted formulas.

## Publication hold

The small spheres have refutations of degree 3 and 4: proof-system upper bounds at fixed sizes, and ticket A rules out a bounded-degree
family. Nothing here is an algorithm for SAT, factoring or cryptography; the hold does not apply.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** Conclusion 3 is exact at K_2 and K_3 and a lower bound at K_4; degrees past the 15,000 MiB cap are undecided, not
  zero.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Lemma 1 of A (FPHP_G reduces to LeftPigeon) (1) | N = 4, 200 random graphs, 64 assignments each (checked with N ≤ 3) | pass: 34,657 answers decoded, at most 7 reads |
| The composed chain (1) | N = 3, 20 instances, grid side 336 (checked with N = 2) | pass: 24 counterclockwise full triangles decoded |
| The small degrees (3) | an independent pure-Python solver on K_2 and on K_3 at degree 3, 16 and 36 variables (pcdeg.c was cross-checked on at most 12) | pass: polynomial calculus 3 on K_2 and not 3 on K_3; Nullstellensatz not 5 and 6 on K_2; control 3 on K_3 |

The script is `stress_test.py` beside this note, its output `stress_test.json`; registered before launch as PC-COUNT-S1, it ran in 127
seconds. K_3's degree 4 and the K_4 bound were not recomputed independently: the pure-Python solver is too slow at 66,712 columns.

## Literature and provenance

- **Sources.** Mikša and Nordström, *A generalized method for proving polynomial calculus degree lower bounds* (CCC 2015; *J. ACM*
  71(6), 2024), Theorem 4.9, and their remark that onto-FPHP is easy while FPHP and onto-PHP are hard; Alekhnovich and Razborov (2003);
  Göös, Hollender, Jain, Maystre, Pires, Robere and Tao (*J. ACM* 2024) for PPADS^dt and unary Sherali–Adams; Itsykson and Sokolov for
  tree-like Res(⊕); Li (2024) for the TFNP view of resolution, which leaves the polynomial calculus for future work.
- **Searched and not found.** A polynomial-calculus degree bound for a PPADS-complete principle, Sperner's lemma or this formula.
- **Classification.** Ticket A: known-with-delta, folklore risk high (each step is standard). Ticket B: new as computed numbers for this
  formula.

## Workspace assumptions

- **Relied on.** None of the register's entries; the formulas are fixed CNFs.
- **Added.** None.
- **Scope.** The octahedral knot sphere's Kasteleyn-signed NAE formula; the polynomial calculus, the Nullstellensatz and tree-like Res(⊕).

## Ratio

Since the epic opened:
- **Substantive.** One proof (A), one pre-registered computation (B) with its solver, one stress test.
- **Administrative.** This note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — F2 polynomial calculus on the count | **Status:** Successful | Degree n^{Ω(1)} over every field proved; tree-like Res(⊕) size exponential |
| Local direction — Res(⊕) on the count | Research directions | Tree-like is settled; regular and dag-like Res(⊕) are open |
| Broader exploration — G3 | Known alternatives | Cutting planes on the count (sub-goal B82) |
| Long-term goal — G3 Hardness at three places | Obstruction learned | No algebraic system refutes the count in low degree over any field; only positivity does |

**Corrections:** none (`TREE-XOR-20261110-001A`'s depth bound stays true and is improved). **Goals:** a G3 checkpoint (obstruction
learned); B84 taken; one sub-goal (B93) and one backlog entry (B94) added. **Assumptions:** none added or changed.

- **What the attempt leaves open.** The exponent (n^{1/4}/log n against O(√n)); K_4's exact degree; any Res(⊕) beyond tree-like.
- **The missing bridge to the program's composed topology.** None here; this line asks how hard the sphere's contradiction is.

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Res(⊕) beyond tree-like on the count: regular or bounded-depth (G3) | 3/3 — Barrier | 1/3 — Stated | Read whether the count's search problem lifts or embeds a formula with a known regular or bounded-depth Res(⊕) lower bound (Efremenko–Itsykson 2024 and the bounded-depth line), against the transfer of `COUNT-SYSTEMS-20261110-001A` → a transfer, or the step that fails | Alternative · deferred |
| 2 | Cutting planes on the count (sub-goal B82, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |
| 3 | Is the degree of order √n? (G3) | 2/3 — Substantial | 2/3 — Testable | Decide K_4's exact degree by a restricted closure (an upper bound of 5 would match k + 1) and look for a shorter embedding of SINK in the sphere than side O(N²) → the exponent 1/2, or the step that costs it | Alternative · deferred |

1. **Res(⊕) beyond tree-like.** Payoff 3: a superpolynomial regular or dag-like Res(⊕) bound for an unlifted natural formula would cross
   a known barrier; Concreteness 1: no route is known, and the known lower bounds need lifted formulas.
2. **Cutting planes.** As in `COUNT-SYSTEMS-20261110-001`.
3. **The exponent.** Payoff 2: 2^{Ω(√n)} for tree-like Res(⊕) would match resolution; Concreteness 2: the K_4 reading is a computation, the
   shorter embedding a construction.

**Recommendation.** Research directions, none selected, for the coordinator. Direction 1 is recorded as sub-goal B93 (owner rule
for untaken 3/3 directions) and direction 3 as backlog B94; B82 stays as recorded.
