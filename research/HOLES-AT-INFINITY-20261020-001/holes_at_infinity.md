# Holes at infinity: ends as a second source of open distinctions

Epic `HOLES-AT-INFINITY-20261020-001`, closed 2026-10-20.

## The question

The owner asked about the program's actual topological structure and about
infinite CNF structures. Earlier work had left two boundaries:
- INFINITE-CNF-001: no knot forms only at infinity unless there is "an
  explicitly infinitary recurrence/contact source".
- Open questions 1 and 7 of `docs/KNOT_INTUITION.md`: which structures count
  as native loops, and what limits contribute.

The starting observation is that a parity hole can only be trapped in a
finite system. In an infinite connected graph, every Tseitin system is
satisfiable, because the hole drains away along a ray to an end.

The proofs are:
- [B: ends supply open distinctions](../../proofs/HOLES-AT-INFINITY-20261020-001B/HOLES-AT-INFINITY-20261020-001B-P001_ends_supply_openness/proof.md)
- [C: the ends of a constraint system](../../proofs/HOLES-AT-INFINITY-20261020-001C/HOLES-AT-INFINITY-20261020-001C-P001_logical_ends/proof.md)

## What was found

- **Openness has two sources.** In an infinite parity system, a non-constant
  parity of finitely many variables comes from one of two places (B,
  Theorem 1):
  - **a finite loop**, which flips it by a finite change;
  - **the ends**: it is a finite cut with infinitely many vertices on both
    sides. No finite change, and nothing in the closure of the finite changes,
    flips it.

  Closed finite systems have only the first kind. Each solution records where
  its hole went, as a finitely additive measure on the end space
  (Proposition 2).
- **Knots without loops.** A vertex relation passes K1–K3 exactly when its
  edges are open (Theorem 2).
  - The 3-regular tree has no loop, yet every vertex carries a knot, opened
    entirely by ends.
  - A finite tree has none.
- **The knot test cannot see the source.** Adding one edge outside any finite
  ball turns an end-supplied distinction into a loop-supplied one, and changes
  nothing a finite part or a K1–K3 verdict can see (Theorem 3).
- **An end is a tangle of every order.** Its tangle pseudo-expectation (the
  formula of `SOS-SIZE-20261020-001B-P001`, Theorem 1) is the actual moment
  sequence of the uniform measure on the solutions whose hole went to that end
  (Theorem 4). In a finite graph, the tangle tells the adversary where the
  hole hides. At an end, the hole really escapes.
- **The law, not the geometry, decides what a loop is** (C, Theorem 2(d)).
  Take two parity laws on the same square grid:
  - Tseitin's vertex law: all openness comes from finite loops, and there is a
    single end class.
  - Ledrappier's triangle law: no finitely supported homogeneous solution
    exists. No finite change is possible at all, every triangle carries a
    parity knot, and all openness comes from infinity, although the grid has
    one end.
- **Things at infinity and trends** (C, Theorems 1 and 5).
  - The readable invariants of "differ in finitely many variables" form a
    Boolean algebra. Its Stone space is the system's ends: things at
    infinity, which the knot test can see.
  - Invariants that no readable function sees are trends, which no relation
    can see. Examples:
    - where an implication chain's switch went;
    - the slope of a grid 3-colouring's height function;
    - a circle through the end of the one-way ladder.
- **Relations form at finite stages; rigidity does not** (C, Proposition 3).
  This agrees with INFINITE-CNF-001A1-P001. What infinity adds is the source
  of openness, not new relations. No two-literal system has a knot among its
  variables (Proposition 4).
- **The escape route need not be computable** (B, Proposition 5). A computable
  tree carries a satisfiable system with no computable solution.

## How this meets the owner's intuitions

This section is interpretation, kept apart from the proofs.

- **"Infinite bonds are like perfect circles: trends, not things."**
  - An end is a class of rays, a trend.
  - It carries a readable bit of its own only when it is isolated.
  - A circle that closes only through an end is a limit of finite loops. No
    readable invariant sees it, so it is a trend in the precise sense of C.
- **"Infinite threads are towers of finite knots."** On the 3-regular tree,
  conservation over a Cantor set of ends is a tower of three-way parity knots,
  one per vertex. No single contact binds infinitely many distinctions.
- **Base realities.**
  - One infinite system has many global completions. They agree on every
    local law and differ only in where escaped holes went.
  - Reading a finite cut narrows them. Nothing in the law selects one, and
    for some computable systems no computable completion exists.
  - That has the shape of "no global selector". It is a theorem about one
    system, not evidence for co-reality, which stays interpretation.

## The fork for the owner

[canonical_correction_request.md](canonical_correction_request.md) asks
whether open distinctions supplied by ends count as native loops. Both
readings are mapped there:
- **Source-blind:** the canonical test as adopted. Knots exist in loopless
  infinite systems.
- **Source-aware:** each loop's distinction must be changed by a finite
  change. The tree and Ledrappier's grid then have no knots.

The two readings agree on every closed finite system.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Two sources of openness; where the hole goes | holes view (a hole drains to an end); classical machinery | Restates Diestel–Kühn, Bruhn–Stein and Berger–Bruhn |
| Knots without loops | the knot test read on trees | Short consequence; new to the program |
| Source invisible to finite parts | holes view | Not found stated; elementary |
| End tangle = Haar moments | link to the SoS epic's tangles | Not found stated; elementary |
| Ends of a system; linear systems | the homoclinic relation of symbolic dynamics | Known in substance (Lind–Schmidt) |
| Ledrappier: openness without loops | the law-relative reading | Example classical; the reading is the program's |
| Trends | owner's "trends, not things" | Examples classical (height functions, frozen colourings) |
| No computable escape | Kleene's tree | Folklore |

**Ratio since the last checkpoint:**
- 2 artifacts changed a conclusion: proofs B and C.
- 3 are administrative: this note, the decision request and the closure
  ledger.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — ends of infinite constraint systems | **Successful** | Ends shown to be a second source of open distinctions, invisible to K1–K3. The law decides what a loop and an end are. Things at infinity separated from trends. Mathematical additions small; classical core cited. |
| Local direction — parity and linear laws at infinity | Practically settled | Theorem 2 of C classifies the linear case. What remains is the owner's decision on the fork. |
| Broader exploration — topology at infinity | One open question named | Whether a non-linear law can supply things at infinity except through equality-like (group-like) propagation. Every example so far fits: equality and permutation chains are rigid; implication chains and 3-colourings have dense classes. |
| Long-term goal — intrinsic structure from logic | Capability gained | A law-generated compact space at infinity (its ends), and a precise sense in which infinity supplies openness but never new relations. The infinite source INFINITE-CNF-001 named now exists, if the owner counts it. |
| Next recommendation — rigidity beyond groups | **Next step:** Continue, as a fresh epic after the owner's decision on the fork. Census of edge-uniform binary laws (one symmetric relation on every edge, up to 3 values) on the line and the 3-regular tree: which have things at infinity, and are those exactly the group-like ones? Then a proof attempt linking it to `KNOT-LOOPS-20261019-001` ("only permutation contact keeps a loop"). | Would join the program's group-like theme (questions 3 and 9) to infinity. A non-group law with things at infinity would refute the guess cheaply. |
| Interest — rigidity beyond groups | **2/3 — Promising** | Every example points one way, and the census is cheap. The main uncertainty is whether the right statement concerns the law or its long-range relations; the triangular-lattice 3-colouring is rigid through a global permutation. |
| Execution — that action | Deferred to the owner | Not started. Bound: one epic; census first. Stop if the census finds a non-group law with things at infinity and no repair. |
