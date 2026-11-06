# Holes in the shape of partial colourings, and what they say about refutations

Epic `HOLE-CRITERION-COLOURING-20261019-001`, 2026-10-19. This is the epic's
decision note, written at the repository owner's request. It answers the
owner's question whether this work uses the program's understanding of knots
and holes. It does, and the answer is mostly negative, with one positive
theorem.

## The question

Braun's exponential Res(⊕) bound for the bit pigeonhole principle
(arXiv:2609.23015, audited in `BPHP-RES-PARITY-AUDIT-20261019-001`) needs
"moments" for partial matchings up to degree about n/2:
- The moments are built one degree at a time.
- Each step fills a cycle in a chessboard complex.
- Filling always works while the chessboard has no hole in the relevant
  dimension (Björner, Lovász, Vrećica and Živaljević, 1994).

In this program's terms, the chessboard complex is the shape (free-set complex)
of the pigeonhole principle's pairwise rules.

The pigeonhole principle is the statement that the complete graph K_{n+1} has
no colouring with n colours. For a graph G with N colours, the same argument
needs a different complex: the complex of partial proper colourings,
Ind(G[S] □ K_N), must have no hole in dimension |S|−2 on every small vertex
set S. Let B_hole be the largest B for which this holds on every S with
|S| ≤ B. The criterion then gives Nullstellensatz degree over GF(2) greater
than B_hole.

The epic asked two questions:
1. Do these holes predict the degree of colouring refutations?
2. Does bit-encoded colouring give the second formula family that Braun's
   Theorem 9.1 lacks (his Remark 9.3)?

## Literature check

- **Braun (2026), arXiv:2609.23015.**
  - Theorem 4.2 builds the moments from chessboard homology.
  - Theorem 9.1 is the generic size criterion.
  - Remark 9.3 says no second family is known.
  - The moment construction "needs no hypothesis m ≥ B" on the number of
    pigeons m.
- **Björner, Lovász, Vrećica and Živaljević (1994).** Chessboard complexes are
  highly connected.
- **Shareshian and Wachs (2007).** That connectivity bound is sharp, and there
  is torsion in the first nonvanishing homology.
- **Lauria and Nordström (CCC 2017).** Bounded-degree graphs with no
  k-colouring need linear polynomial-calculus degree, over every field.
- **Conneryd, de Rezende, Nordström, Pang and Risse (FOCS 2023).** The same
  holds for sparse random graphs.
- **Efremenko, Garlík and Itsykson.**
  - Regular Res(⊕) lower bounds for bit PHP.
  - For weak bit PHP, a tree-like size bound of 2^{Ω(n)} and a DAG-like width
    bound.
- No DAG-like Res(⊕) size bound for weak bit PHP, or for bit-colouring beyond
  complete graphs, was found in a brief search.

## What was found

### The holes carry no graph-specific information (ticket A)

`HOLE-CRITERION-COLOURING-20261019-001A-E001` is an exact, exploratory
computation. An independent recomputation agreed on every value.

- **No hole once there are enough colours.** All 51 graphs on 2 to 5 vertices
  have no hole in dimension s−2 once N ≥ 2s−1. Only the complete graphs need
  that many colours. The vanishing is not monotone in N. For example, C₄ has
  a hole only at N = 4, and K_{2,3} only at N = 5.
- **The criterion holds on the roster, often tightly.** On all 13 roster
  graphs, the Nullstellensatz degree over GF(2) exceeds B_hole. It exceeds it
  by exactly one on 10 graphs, and by two on K₅ with 4 colours, the Moser
  spindle and the Mycielskian of K₄.
- **But B_hole is the same for every graph.** On every roster graph, B_hole
  equals ⌊(N+1)/2⌋, the floor that every graph has. This floor needs no
  topology:
  1. A graph's colouring system is a subsystem of the complete graph's on the
     same vertices.
  2. So its degree is at least that of the pigeonhole principle.
  3. Braun's moment theorem bounds that degree from below.
- **Small pieces always have holes.** Every graph with no N-colouring has a
  vertex with N neighbours. Those N+1 vertices induce a cone, and every cone
  on at most 5 vertices has a hole at N colours. Hence:
  - With 3 colours, every non-3-colourable graph has B_hole = 2, because an
    induced three-vertex path or a triangle has a hole.
  - With 4 colours, B_hole ≤ 3.
  - With a fixed number of colours the criterion cannot certify more than a
    constant degree. Lauria and Nordström give linear degree for some
    3-colouring instances, so the gap is unbounded.

The holes are a worst-case obstruction. They guarantee that every choice of
lower moments extends. With few colours, tiny pieces of the graph already have
holes, so the criterion says nothing about the graph. It is informative only
in pigeonhole-like settings: injective constraints with many values per
variable.

### The holes do not care how many pigeons there are (ticket B)

The chessboard holes depend on the number of holes N, not on the number of
pigeons. Braun's formal lemmas also take the number of pigeons as a parameter.
`HOLE-CRITERION-COLOURING-20261019-001B-P001` proves the following in Lean,
against his replayed development:

1. **More pigeons.** Let ℓ ≥ 32 and n = 2^ℓ. For every m with n < m and
   8192·m·ℓ²(2ℓ+5) ≤ n², every refutation of bit PHP with m pigeons has more
   than exp(n²/(8192·m·ℓ²)) lines. The bound is superpolynomial while
   m = o(n²/log³ n).
2. **Colouring reduces to bit PHP.** Take a proper colouring of G with m
   classes. Reading each vertex's bits as its class's bits maps every
   refutation of the bit encoding of 2^ℓ-colouring G, line by line, to a
   refutation of bit PHP with m pigeons.
3. **Bound for colouring.** Combining the two: bit-colouring of every graph
   whose chromatic number lies in that range needs exponential-size Res(⊕)
   refutations.

Two consequences follow:
- **Bit-colouring is not a second family.** Every instance is bit PHP after a
  substitution, so it does not answer Remark 9.3.
- **The result is still worth having.** It extends Braun's bound to weak bit
  PHP and to every graph with moderately large chromatic number. Both are
  corollaries of his machinery that his preprint does not state.

## What this says about knots and holes

- **Grouping distinctions removes small holes.** The moment argument needs a
  shape whose small pieces are hole-free.
  - The pigeonhole principle has such a shape only because each pigeon is
    treated as one many-valued distinction (the functional encoding).
  - Treated as separate Boolean distinctions, the same rules contain
    conflicts at every small scale.
  - Prose derivation for CNF formulas, by Alexander duality and the nerve
    lemma:
    - Take the complex of partial assignments to a variable set S that
      falsify no clause inside S.
    - It has a hole in dimension |S|−2 exactly when those clauses'
      falsifying assignments split into mutually incompatible groups.
    - So two clauses that clash on one variable already give a hole on
      their at most 2k−1 variables.
    - A scratch computation confirmed this on one 5-variable example; it is
      not recorded as evidence.
- **Colouring with few colours is full of small holes.** A path, a star or a
  triangle already has one, so the plain criterion is silent there.
- **The useful property was independence from the pigeons.** The holes that
  matter are those of injective constraints with many values. Their absence
  does not depend on how many variables share them, and that is what extended
  the bound to more pigeons.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: hole criterion for colouring refutations | **Status:** Successful | The criterion holds on every tested graph. It carries no graph-specific information, and the decision rule's signal is explained by the PHP floor. The bit-colouring question is settled: bit-colouring is bit PHP after substitution, and Theorems 1–3 bound it. |
| Local direction: plain (worst-case) hole criterion | Practically exhausted for colouring; for CNF formulas too, by the prose clash argument | Small cones, paths and triangles, or two clashing clauses, always have holes. Accepted results are kept: A-E001 data, B-P001 theorems. |
| Broader exploration: second formula family for Braun's Theorem 9.1 | Searching; one class ruled out | Colouring is ruled out as a new family, and plain criteria fail on CNF formulas. Not assessed: relative or equivariant hole criteria, and other injective constraint families. |
| Long-term goal: Res(⊕) lower bounds beyond bit PHP | Capability gained (modest) | Kernel-checked bounds now cover weak bit PHP and bit-colouring for chromatic numbers up to about n²/(16384 ℓ³). Formulas that do not reduce to bit PHP remain open. |
| Next recommendation: Theorems 1–3 of B-P001 | **Next step:** Continue (conversion). Prepare a two-page statement of Theorems 1–3 with the Lean file, which Braun or a Res(⊕) reader could check by running `check.py`. | Efremenko, Garlík and Itsykson studied weak bit PHP and left DAG-like size open, so this reader has a need for it. Completion check: the statement is self-contained and `check.py` replays. |
| Interest: that conversion | **2/3 — Promising** | A machine-checked, apparently unstated extension of a frontier result to a regime that has been studied. Main uncertainty: experts may see it as an immediate corollary, and Braun may already have it. Alternative not selected, rated **1/3 — Exploratory poking**: search for a non-PHP family whose allowed-assignment shape is hole-free up to linear size. Colouring with few colours and CNF formulas have holes at bounded size. A hand argument, not computed, suggests that choice encodings of counting principles do too: choosing a block forces its other members' choices. |
| Execution: that conversion | Deferred | Whether to share anything with Braun, and how, is the owner's decision. `proof.md` of B-P001 already states and proves the result. Stop if the owner does not want it shared. Reassess the hole search only if a relative criterion, one counting only the holes that moment cycles reach, can be defined without recomputing the degree itself. |
