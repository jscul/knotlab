# The contact-first foundation: a reading of known logic

Written on 2026-10-19, when `KNOT-FOUNDATION-20261019-001` met its stop rule.
This is an exposition. Theorem status lives in the proofs and decision notes
it cites. The working document, with its intuitions and open questions, is
`docs/KNOT_INTUITION.md`. Its wording was revised on 2026-11-11 under the
program's language rule, in the words of the glossary of
[the Intuitions guide](../INTUITIONS.md#glossary): the program's own objects
are named by distinctions, knots and counts, and each spatial word is the
literature's or a drawn picture. No claim changed, and the earlier text is in
git history.

## In one paragraph

The program asks whether logic can build relative structure without
presupposing space. Its foundation now reads as follows:
- The smallest thing is a **distinction**, one bit.
- A **loop** is a logical structure that carries an open distinction, a bit
  it leaves free.
- A **knot** is a relation on distinctions that is constrained as a whole and
  free in every part: information that exists only in the whole.

Every piece of mathematics this rests on is classical. What the program adds
is the reading, and one presentation-independent test that the repository now
enforces.

## Definitions

- **Relation.** The joint states that a system of constraints allows, which
  earlier versions of this page called a pattern. Witness variables are
  quantified away, and no executor,
  scheduler or checker may supply an input. Every verdict depends only on the
  allowed states.
- **Open distinction and loop.** A variable, or a named relation such as a
  parity, that a structure leaves free. A loop is any logical structure with
  one.
- **Knot (K1–K3).** A relation over the open distinctions of loops and one
  contact, where erasing a loop forgets it:
  - K1: it is constrained as a whole;
  - K2: forgetting any one variable leaves the rest unconstrained;
  - K3: some state is allowed.
- **Free complex, bonds, ties.** A system's free sets are the sets whose
  every assignment it allows. They form a simplicial complex, its free complex
  (earlier, its shape). Its bonds are the knots inside it, and its ties are
  constrained pairs.
- **Hole versus knot.** A hole is any gap in the free complex. A knot is the
  smallest kind: a hollow triple, drawn as an empty triangle, where every pair
  is free and the whole is not. Pairwise ties can make holes, as when two ties
  leave a hollow cycle of four, drawn as a square, but never a hollow triple.
  Every knot is a hole, but not every hole is a knot
  (`docs/KNOT_INTUITION.md`, "Holes and knots").

## What is established

| Claim | Classical source | The program's reading | Evidence |
| --- | --- | --- | --- |
| Two loops and a contact have 34 knots in five classes. The atom `¬A ∨ ¬B ∨ c` hides the least; parity hides the most, one full bit. | Finite classification; parity codes are the binary codes of distance two | The odd/even pattern that started the program is the extreme knot | `KNOT-FOUNDATION-20261019-001E-P001` |
| No 2-CNF, even with witnesses, defines a knot | Majority closure (Schaefer 1978); pairwise determination (Baker and Pixley 1975) | 2-clauses are logic, not topology: a variable acts on others one at a time | `…001A-P001`, `…001E-P001` (Lean) |
| Three-literal clauses with named intermediates define every knot. Parity on n variables needs 4n − 3 such clauses, against 2^(n−1) without names | Tseitin encoding (1968) | Naming a relation with a new variable gives relations of relations, the owner's patterns of patterns | `…001E-P001` (Lean) |
| Knots need alternatives and never select. Requirement and choice are one knot read two ways | Horn and dual-Horn clauses; least models (Horn 1951; van Emden and Kowalski 1976) | Choice is native wherever knots are; a loop carries a choice | `research/KNOT-FOUNDATION-20261019-001/choice.md` |
| Computation is a forced world, search is choice, and systems of knots state any 3-SAT instance | P-completeness of Horn-SAT and monotone circuit value (Jones and Laaser 1976; Goldschlager 1977); Cook (1971) | Requirements give one world; open distinctions give many | `docs/KNOT_INTUITION.md`, "Requirement and choice"; `knotlab worlds`, `knotlab choice` |
| No set of finite clauses binds infinitely many loops into one contact | Compactness | An endless chain is a tower of finite knots | `…001E-P001`, Theorem 7 |
| A knot is a hollow simplex of its free complex; the two-loop knot is a hollow triple, the literature's circle. Bonds compose by resolution. Every simplicial complex is some system's free complex | Shattered sets (Vapnik and Chervonenkis 1971; Sauer 1972; Shelah 1972); resolution (Robinson 1965); matroid circuits (Whitney 1935) | One knot is literally the first atomic topology. Logic allows every free complex, so space must come from a law | `research/KNOT-FOUNDATION-20261019-001/space.md` |
| A ring of knots joined through witnesses excludes an assignment of its distinctions exactly when every transfer is a permutation and an odd number swap, so it composes into a knot or nothing. Only parity keeps a full bit at every length; a parity knot pattern keeps one bit per independent loop | Transfer matrices; Tseitin (1968); bounded width (Barto and Kozik 2009); Protasov and Voynov for many values | On bits only group-like contact, parity, keeps a lasting record of a loop; with more values, contact group-like modulo blocks does (`LOOP-HOMOLOGY-20261021-001A-P001`) | `KNOT-LOOPS-20261019-001B-P001` (Lean), `…001C-E001` |
| A network of permutation contact allows an assignment exactly when its holonomy group has a common fixed point. Free contact keeps one H¹ class per loop and never binds loops; contact with fixed points binds them into atoms whose free complex is the nerve of the fixed-point sets, and a knot among k loops needs k + 1 values. Only unpinned two-witness linear reasoning misses an impossible network, exactly by orbit arithmetic | Coverings and H¹ of graphs; bijection constraints (Unique Games); BLP+AIP (Brakensiek et al. 2020); Lichter and Pago (2024) | Among permutation contact, loops bind only through fixed points, as atoms; outside it, twisted affine contact binds loops in pairs (`LOOP-HOMOLOGY-20261021-001A-P001`); permutation holes are shallow | `HOLES-COHOMOLOGY-20261019-001B-P001` (Lean), `…001C-P001` |
| A knot pattern with knots at the vertices of a graph and its edges as distinctions allows nothing when its total charge is nonzero. Linear local reasoning refutes it at the size of one knot over rings that compute in the charge group, and exactly at the graph's toggle width over every other field, whatever the charges: cutwidth + 1 on every cubic graph. Every non-atom knot is a hole at its own scope, so local holes do not measure depth | Tseitin formulas (1968); degree lower bounds outside characteristic 2 (Grigoriev 1998; Buss, Grigoriev, Impagliazzo and Pitassi 2001). The depth is the Nullstellensatz degree of the Tseitin formula | Loop holes are shallow; charge holes are as deep as the layout's cut width | `DEEP-HOLES-20261020-001B-P001`, `CUTWIDTH-DEPTH-20261020-001B-P001`, `TSEITIN-NS-DEGREE-NOTE-20261020-001-P001` |
| Proof 0009's executor supplied a loop's presence as a hidden literal | (the program's own correction) | Verdicts must come from allowed states alone | `…001A-P001` (Lean) |
| Every law on bits is pairwise (no knots), frozen (only "not all on" or "not all off" knots, which never compose) or transmitting (knots compose exactly when they force a shared distinction oppositely). A law keeps a lasting record of loops exactly when all its polymorphisms are affine, and then no bounded local reasoning decides it | Majority closure; resolution; Post's lattice; Schaefer (1978); Feder and Vardi (1998) | Each step up adds one capability: identity, isolated emergence, transmission, memory, search | `BASE-THREE-20261021-001A-P001`, `…001B-P001` |
| A law's knots compose like cycles exactly when every range has a top, ties are bijections modulo the tops, and one ternary polymorphism is Mal'tsev modulo the top of every knot range; the tops are affine over finite fields | Rectangularity and Mal'tsev polymorphisms (Dyer and Richerby); Herrmann's theorem; representable matroids | Composition without hubs is linear algebra modulo the tops | `CYCLE-TOPS-20261021-001`, `AFFINE-TOPS-20261021-001` |
| The bits a relation hides from its pairs vanish exactly for 2-CNF relations; a knot hides at most one bit (only parity hides one), n distinctions up to about n − log₂log₂n. With hidden witnesses a knot pattern holds at most one bit per independent loop, filled only by parity, and frustrated parts add up | Majority closure; facial sets of exponential families; covering arrays (Kleitman and Spencer; Katona); Hadamard designs | Emergence is a quantity; one contact holds at most a bit, and only reversible contact carries it over distance | `EMERGENCE-BITS-20261021-001A-P001`, `…001B-P001` |
| A not-all-equal knot pattern on a drawn lattice, with fair visible distinctions, is, after recolouring, a uniformly random orientation of its hidden implications; reach in it is bond percolation at 1/2. Such a pattern with no directed crossing of its drawn cut surface in one direction is consistent. Global emergence vanishes below a drawn lattice's bond threshold, stays bounded on the drawn square lattice, and diverges when two-way contacts percolate. On drawn square tori it depends only on their proportions (an experiment) | Grimmett's randomly oriented lattice (2001); Kesten (1980); Russo, Seymour and Welsh (1978) | Fairness is criticality: self-duality puts the drawn square lattice's threshold exactly at 1/2 | `BASE-CRITICALITY-20261022-001A-P001`, `…001B-E001` |
| Of the 204 ways to place a three-variable knot as a fair contact on drawn square-lattice tori, six classes have a vacuum and hold nothing, parity and swap-or-order frustrate locally, and only not-all-equal and "x or (h ≠ h′)" hold a scale-free amount. "x or (h ≠ h′)" is consistent exactly when its disequality edges, bond percolation at 1/2, are bipartite, so its amount is bounded on both sides. Its limit matches Pinson's torus formula on six tori of different proportions (an experiment) | Pinson (1994); Russo, Seymour and Welsh (1978); Harris and FKG inequalities | For one contact, the emergence of the base logic is a winding quantity of critical percolation | `CONTACT-CENSUS-20261022-001A-P001`, `…001B-E001` |
| A fair not-all-equal knot pattern is inconsistent exactly when the swap-reversed random orientation of its double cover has a swap-invariant strong component, that is, when its cyclic edges wrap an odd cycle. On twisted tori primal and dual cyclic edges are exactly complementary, so P(contractible) = P(cross). The amount is a wrapping probability of strongly-connected percolation (dimension 1.80). No Coulomb-gas formula fits; on square tori with one odd side the amount is 0.4963 bits, not half a bit (an experiment) | Aspvall, Plass and Tarjan (1979); Minty (1966); de Noronha et al. (2018); Newman, Grassberger and Ziff (2026) | A three-literal knot's critical emergence is the wrapping of two-way connection in its two-literal residual | `NAE-INVARIANT-20261022-001A-P001`, `…001B-E001`, `SC-TORUS-EXACT-20261022-001B-E001` |
| On a drawn torus, the classes of an orientation's directed closed walks fill exactly a closed convex cone, and the rotated dual orientation's fill its polar. The uniform law is invariant under taking polars, so the published one-direction wrapping 3/4 of strongly-connected percolation means: no directed closed walk winds horizontally with probability exactly 1/4. That value survives a precise test, but no identity that holds at every size can force it | Minty (1966); homology flows and cohomology cuts (Chambers, Erickson and Nayyeri 2009); Newman, Grassberger and Ziff (2026) | The knot's twist reads as a duality of directed winding; duality fixes what the critical values mean, not what they are | `SC-TORUS-EXACT-20261022-001A-P001`, `…001B-E001` |

## What the program adds

The program's contribution is a reading of these results:
- **Emergence is joint information.** It is a difference held by the whole
  and by no part.
- **Loops carry open distinctions,** and a knot relates them without fixing
  them.
- **"The thing between the loops" is the missing whole** in the free complex:
  the hole that the free pairs surround.

The program also enforces one test, K1–K3 with erasure as forgetting.
`tools/knotlab` decides it from allowed states, and AGENTS.md requires it for
every knot or contact claim.

## What it does not show

- **No new mathematics in the foundation itself.** Later epics proved some new
  results, each labelled with its novelty in its decision note. Within the
  foundation, the census and classification facts are finite and
  elementary. Everything else is cited.
- **No space.** Logic allows every free complex, so whatever space a system
  has comes from its law.
- **No physics,** and nothing about whether P equals NP.
- **No proof that every alternative is equally real.** That is the
  modal-plurality interpretation, which the results fit but do not prove.

## What remains open

These are numbered as in `docs/KNOT_INTUITION.md`:
- **Space from a law (9).** Which uniform, local law, not written on a space
  in advance, gives a meeting pattern of knots that looks like a
  low-dimensional space? This question is shared with causal
  sets, quantum graphity and hypergraph rewriting. On declared lattices, the
  global emergence of not-all-equal patterns is critical exactly where the
  drawn lattice's bond threshold equals the
  fairness 1/2 of the visible distinctions (`BASE-CRITICALITY-20261022-001`).
  Exactly two fair contacts are critical there. The amount for "x or
  (h ≠ h′)" matches a conformal winding formula
  (`CONTACT-CENSUS-20261022-001`). Not-all-equal's is a wrapping probability
  of strongly-connected percolation on twisted tori, a known class with no
  known torus formula (`NAE-INVARIANT-20261022-001`). Its value on square
  tori with one odd side is 0.4963 bits, not the half bit once suspected;
  directed winding there obeys an exact polar duality
  (`SC-TORUS-EXACT-20261022-001`). The lattice is still declared, not
  created.
- **Competition (10).** Mapped, not decided, by
  `KNOT-COMPETITION-20261019-001`
  ([decision note](../research/KNOT-COMPETITION-20261019-001/competition.md)):
  - under competition, rules on pairs make exactly the four not-all-equal
    knots on three variables and none on four or more (Lean);
  - under the strict reading they make none;
  - competition turns a drawn triangulated layout into a chain of knots with
    growing separation, but supplies no layout.

  Whether a system may allow its least-violation states remains the owner's
  decision.
- **Native loops (1).** Which finite structures count as native loops remains
  interpretive. For infinite systems the owner adopted the source-aware
  reading on 2026-10-20, and it can be reopened: a loop's distinction must be
  flipped by a change of finitely many variables. See the decision notes of
  `HOLES-AT-INFINITY-20261020-001`
  ([note](../research/HOLES-AT-INFINITY-20261020-001/holes_at_infinity.md))
  and `FROZEN-WORLDS-20261020-001`
  ([note](../research/FROZEN-WORLDS-20261020-001/frozen_worlds.md)).
- **Composition (3).** Answered for loops by `KNOT-LOOPS-20261019-001`
  ([decision note](../research/KNOT-LOOPS-20261019-001/loops.md)): only
  permutation transfers carry a loop, and parity alone carries it at full
  strength. Extended to networks by `HOLES-COHOMOLOGY-20261019-001`
  ([decision note](../research/HOLES-COHOMOLOGY-20261019-001/holes_cohomology.md)):
  free contact keeps loops independent, and contact with fixed points binds
  them into atoms. Later epics answered composition without groups: on bits
  knots compose exactly when they force a shared distinction oppositely
  (`BASE-THREE-20261021-001`); knots compose like cycles exactly when the law
  is affine over a finite field modulo its tops (`CYCLE-TOPS-20261021-001`,
  `AFFINE-TOPS-20261021-001`); such pairs pass the contact-network gates
  (`NATIVE-NETWORK-20261021-001`); and a knot pattern holds at most one bit
  per independent loop, filled only by parity (`EMERGENCE-BITS-20261021-001`).
- **Depth of a pattern's hole.** Settled for charge patterns, Tseitin's, by
  `DEEP-HOLES-20261020-001`
  ([decision note](../research/DEEP-HOLES-20261020-001/deep_holes.md)): the
  depth is the toggle width. On graphs of maximum degree at most 3 that is
  exactly cutwidth + 1 (`CUTWIDTH-DEPTH-20261020-001`,
  [decision note](../research/CUTWIDTH-DEPTH-20261020-001/cutwidth_depth.md)).
  In proof-complexity terms the depth is the Nullstellensatz degree of the
  Tseitin formula, written up for outside readers with a standalone replay
  in `TSEITIN-NS-DEGREE-NOTE-20261020-001`. Polynomial calculus, which can
  multiply as well as combine, follows tree layouts at half size: its degree
  is ⌈cvw/2⌉ or ⌊cvw/2⌋ + 1 for carving width cvw (`PC-DEGREE-20261020-001`,
  [decision note](../research/PC-DEGREE-20261020-001/pc_degree.md)).
  Whether vertex removals ever help at higher degree remains open; none
  helped on 1,453 census graphs.
- **Witnesses (2), dynamics (4) and limits (7).**

## The earlier corpus

The foundation triage (`research/KNOT-FOUNDATION-20261019-001/foundation_triage.md`)
labels the 63 foundations and topology discovery records:
- 2 stand;
- 29 reduce to atoms composing or to known facts;
- 24 depend on the earlier gate's vocabulary;
- 8 are independent mathematics.

The program's one externally useful result, the counterexample to Conjecture
1.4/4.2 of ECCC TR26-007, is independent of the foundation.

## How to check

```bash
for command in demo worlds patterns choice space competition presence; do
  PYTHONPATH=tools python3 -B -m knotlab "$command"
done
python3 -B -m unittest tests.test_knotlab
python3 -B proofs/KNOT-FOUNDATION-20261019-001A/*/check.py
python3 -B proofs/KNOT-FOUNDATION-20261019-001E/*/check.py
python3 -B proofs/KNOT-COMPETITION-20261019-001A/*/check.py
```

Each command exits nonzero if a result changes. The proof checkers compile
their Lean kernels with Lean 4.32.2 and run every control on a deliberately
wrong input.
