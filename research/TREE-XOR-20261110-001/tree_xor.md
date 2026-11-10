# Tree-like Res(⊕) on the sphere's count

Epic `TREE-XOR-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `COUNT-SYSTEMS-20261110-001` settled bounded-depth Frege on the sphere's count and left Res(⊕) and cutting
  planes open; its direction 2, backlog B83, asked for tree-like Res(⊕), the weakest Res(⊕), equivalently parity decision trees that find
  a violated line. The coordinator selected it on 2026-11-10 as the more concrete of the close-rated options.
- **The question.** How deep and how large must a parity decision tree for the count be?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Polynomial height.** Every parity decision tree for the count, hence every tree-like Res(⊕) refutation, has depth at least c n^{1/8} / log n. A depth-d parity tree is an F2 Nullstellensatz refutation of degree d + 3, and the count needs F2 degree Ω(n^{1/8}/log n): Beame et al.'s Ω(√N) for the sink-counting principle, carried through linear substitution and the decision-tree reductions. | proved (from published bounds) | A |
| 2 | **Size is the polynomial calculus's degree.** A parity tree with s leaves gives an F2 polynomial-calculus refutation of degree log₂ s + w, so tree-like Res(⊕) on the count has size at least 2^{deg_PC − 3}. A size lower bound follows from an F2 polynomial-calculus degree lower bound, B84. | proved | B |

## Answer

Parity queries do not find the sphere's violated line fast: every parity decision tree needs depth polynomial in n, because a shallow
tree would be a low-degree F2 refutation and the count's contradiction, a count of parities that all hold, has none. The size of such
trees is the open part, and it is no longer a separate question: it is bounded below by 2 to the count's F2 polynomial-calculus degree,
which is B84.

## Reading

**Interpretation, not a theorem.**
- **Two F2 questions became one.** B83 (tree-like Res(⊕) size) and B84 (F2 polynomial-calculus degree) are linked: any degree lower bound
  for B84 gives a size lower bound for B83.
- **Why the depth bound does not give size.** The Nullstellensatz is static, so a polynomial degree bound limits a tree's depth only. The
  polynomial calculus may refute the count in lower degree than the Nullstellensatz, and then the size argument gives less.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** None: both tickets are proofs, with finite checks.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Lemma 1 (a parity tree is a degree-(d + 3) F2 refutation) (1) | K_3, 36 points (checked exhaustively on K_2): two complete trees of 1,031,316 leaves, depth 36 | pass: every leaf's clause falsified on it, and the leaves partition F2^36 exactly |
| The size–degree bound (2) | random unsatisfiable 3-CNFs on 10 variables (checked on 8) | pass, 6 formulas |

The script is `stress_test.py` beside this note, its output `stress_test.json`; it ran in 1,163 seconds. It was launched expecting a few
minutes and ran 19, so it was registered in the long-running index only after it finished (TREE-XOR-S1).

## Literature and provenance

- **Sources.** Beame, Cook, Edmonds, Impagliazzo and Pitassi (*JCSS* 57, 1998), §3.3 and Theorem 12 (the Ω(√N) degree bound);
  Itsykson and Sokolov (parity decision trees and tree-like Res(⊕)); Göös, Hollender, Jain, Maystre, Pires, Robere and Tao (2022) for
  decision-tree reductions; Ben-Sasson and Wigderson (*JACM*, 2001) and Impagliazzo, Pudlák and Sgall (*Computational Complexity*, 1999)
  for the size arguments; Beame–Koroth and Chattopadhyay–Mande–Sanyal–Sherif for lifting, which this formula does not have ready.
- **Classification.** Known-with-delta for both tickets: each is the expected combination of known arguments, written for this formula.

## Workspace assumptions

- **Relied on.** None of the register's entries; the formulas are fixed CNFs.
- **Added.** None.
- **Scope.** The octahedral knot sphere's Kasteleyn-signed NAE formula; parity decision trees and tree-like Res(⊕).

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
| This attempt — tree-like Res(⊕) on the count | **Status:** Partially successful | Height n^{Ω(1)} proved; size reduced to the F2 polynomial-calculus degree |
| Local direction — F2 proof systems on the count | Research directions | The polynomial-calculus degree (B84) now decides both |
| Broader exploration — G3 | Known alternatives | Cutting planes on the count (sub-goal B82) |
| Long-term goal — G3 Hardness at three places | Obstruction learned | Parities alone cannot find the sphere's contradiction quickly; whether they can refute it in small size is one degree question |

**Corrections:** none. **Goals:** a G3 checkpoint (obstruction learned); B83 taken; B84's entry updated to say it now also decides
tree-like Res(⊕) size. **Assumptions:** none added or changed.

- **What the attempt leaves open.** A size lower bound for tree-like Res(⊕), equivalently enough of an F2 polynomial-calculus degree
  bound; anything for dag-like Res(⊕).
- **The missing bridge to the program's composed topology.** None here; this line asks how hard the sphere's contradiction is.

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | F2 polynomial calculus on the count, now deciding tree-like Res(⊕) size (B84, G3) | 2/3 — Substantial | 2/3 — Testable | Compute the count's exact F2 polynomial-calculus degree on K_2 and K_3 by degree-bounded linear algebra over the 16 and 36 points, against its Nullstellensatz degree → degree growing with k (a size bound for tree-like Res(⊕)), or a low-degree refutation (a short tree-like Res(⊕) proof may exist) | Alternative · deferred |
| 2 | Cutting planes on the count (sub-goal B82, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |

1. **The polynomial calculus.** Payoff 2: one degree bound would give the first size lower bound for a Res(⊕) fragment on the count;
   Concreteness 2: the computation is linear algebra, feasible on K_2 and perhaps K_3, and the dynamic degree may well be small.
2. **Cutting planes.** As in `COUNT-SYSTEMS-20261110-001`.

**Recommendation.** Research directions, none selected, for the coordinator; B84 is re-rated 2/2 because it now decides both questions.
