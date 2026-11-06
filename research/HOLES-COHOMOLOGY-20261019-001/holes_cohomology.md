# Holes as cohomology: what contact networks remember, and where local reasoning fails

Epic `HOLES-COHOMOLOGY-20261019-001`, 2026-10-19. This is the decision note.
It follows `KNOT-LOOPS-20261019-001`, which found that only group-like
(permutation) contact remembers a loop, and it takes up that epic's
recommended next step in two parts.

## The questions

1. **What does a network of permutation contact remember** once its
   witnesses are forgotten?
   - Is the composite the vanishing of an H¹ class, as for parity?
   - With non-commuting contact, does the composite record more than the
     conjugacy class of each loop's holonomy?
   - Can loops bind to one another?
2. **Where does local reasoning fail** to see that such a network is
   impossible? We compare consistency methods and linear relaxations over
   F₂, F₃, Q and Z, plain and pinned. The calibration is Lichter and Pago's
   coprime counterexample (arXiv:2407.09097).

## What was found

### Part 1: free contact records loops, contact with fixed points binds them (B, Lean; A, census)

`HOLES-COHOMOLOGY-20261019-001B-P001`:
- **The network rule** (prose; the loop and bouquet cases in Lean). A network
  allows a pattern exactly when its holonomy group has a common fixed point.
  Equivalently, the label-extended covering has a sheet that closes up.
- **Free contact keeps one H¹ class per loop.** Parity, addition mod q and
  every regular action are free contact. A pattern is allowed exactly when
  its class in H¹(G; Γ) vanishes.
  - With uniform group contact the allowed fraction depends on the network
    only through its number of independent loops b₁. This holds even for
    non-abelian groups: S₃ allows 2/3, 5/18 and 11/108 at one, two and three
    loops (prose; census on 38 graph–group pairs).
- **Non-free contact records more than each loop's conjugacy class.** In S₄,
  the holonomy pairs ((03), (13)) and ((03), (12)) consist of transpositions,
  but only the first shares a fixed point. The census finds such
  type-ambiguous pairs for S₃ and S₄ links, and none for Z₂ and Z₃ (P6). This
  answers the stop condition KNOT-LOOPS set for this direction. Non-abelian
  composites record how loop holonomies sit relative to one another, a
  simultaneous-conjugacy invariant, and not only what each one is.
- **Loops bind, and the binding shape is a nerve** (Lean).
  - Give each loop a selector: unselected, its holonomy is the identity;
    selected, it is h_i.
  - The shape of the selector relation is the nerve of the fixed-point sets
    Fix(h_i).
  - A minimal non-face is excluded alone. So **a tie between two loops, or a
    knot among three or more, is always an atom**: any proper subset of the
    loops can be on together, but not all of them.
  - Every simplicial complex arises as such a shape.
- **Free contact never binds two loops** (Lean).
- **Binding costs witness values** (Lean).
  - A knot among k loops needs at least k + 1 values, and the star
    transpositions (j k) achieve it.
  - So Boolean contact cannot even tie two loops; three values can tie two;
    three loops need four values, e.g. (03), (13), (23).
  - On four values the knots among three loops are exactly the 24 star
    configurations (census, exhaustive).

### Part 2: the holes of permutation networks are shallow (C, prose with verified certificates; A, census)

`HOLES-COHOMOLOGY-20261019-001C-P001`:

| Method | Refutes an impossible network of permutation contact |
| --- | --- |
| Arc consistency; basic LP; level-2 affine over Q | never |
| Level-2 affine over F_p | exactly when p divides every holonomy-orbit size |
| Level-2 affine over Z (AIP); BLP+AIP | exactly when the orbit sizes are not coprime |
| Level 2 pinned at one witness, over any ring | always |
| Path consistency; level-3 affine over any ring; level-3 Sherali–Adams | always |

- **The coprime tie is the smallest blind spot of integer reasoning.** Two
  loops with holonomies (01) and (234) on five values each close alone but
  not together. Integer reasoning accepts them because 3 − 2 = 1.
- **It is Lichter and Pago's arithmetic in its simplest form, without their
  robustness.** Their counterexample combines unsatisfiable Z₂ and Z₃ Tseitin
  systems on expanders and survives every level. Permutation networks never
  survive level 3.
- **Every verdict carries a certificate.**
  - The census found every verdict with a general solver, and its independent
    check verified all 1,844 certificates by substitution.
  - C's own check built the certificate predicted by the proof for each of 469
    networks and verified it. For example, the level-3 refutation is an integer
    combination of ±1 coefficients reading 0 = 1, valid over every ring at
    once.

### The census (A, exploratory; all six frozen predictions hold)

`HOLES-COHOMOLOGY-20261019-001A-E001`:
- P1, the composite rule: on 38 graph–group pairs and 300 random link
  assignments.
- P2, memory depends on b₁ only.
- P3, shapes are nerves: 23,652 holonomy tuples, every knot among loops an
  atom by knotlab's check.
- P4, all 193 complexes on at most four vertices realized, and the k + 1 bound
  exhaustive for k = 2, 3, 4.
- P5, the local-reasoning table: 80 instances.
- P6, the type-ambiguous pairs above.

**One correction happened before the freeze.** The planning-stage claim was
that linear relaxations below a loop's length are fooled. A short derivation
showed that three witnesses at a time refute every impossible network, so the
claim was withdrawn. The contract records the withdrawal, and its level-3 rows
discriminate the two claims.

## What it means

- **Holes of a network come in two kinds, and the contact decides which.**
  - Free contact (parity, cyclic, any regular action) records each
    independent loop separately: the network's H¹ with coefficients in the
    contact group. Its minimal non-faces are single loops that cannot close.
  - Contact with fixed points binds loops. The binding shape can be any
    simplicial complex, so its holes are arbitrary.
- **Knots among loops are a second-order knot, and always the weakest kind.**
  Their parts are loops, which are themselves made of contact. The knot test
  passes on the selectors, but the knot is always the atom. Parity, the knot
  that hides the most, never binds loops: free contact makes loops
  independent. So the program's two extreme knots play opposite roles:
  - parity carries a single loop at full strength (`KNOT-LOOPS-20261019-001`);
  - the atom is the only way loops bind one another.
- **These holes do not make local reasoning hard.** The obstruction of a
  permutation network is visible to any method that holds three witnesses, or
  pins one. Hard holes, invisible at every level, need contact among three or
  more distinctions over an expander-like layout. That is the territory of
  Tseitin formulas, Lichter and Pago, and the hole criterion of
  `HOLE-CRITERION-COLOURING-20261019-001`.
- **For question 9 (space from a law):** a law whose contacts have fixed
  points can make its loops bind into knots, at a cost of k + 1 witness values
  per knot among k loops. That is a native way for loops to compose. It is not
  yet a law that makes the network: every network here was laid out by hand.

## Nearest known results

- **Bijection constraints** are the satisfiable side of Unique Games. They are
  decided by propagation and by path consistency. Their label-extended graph
  is the covering used here.
- **Holonomy, coverings and H¹ of graphs** are classical, with abelian and
  non-abelian coefficients. Every simplicial complex is a nerve.
- **BLP+AIP and AIP.** Brakensiek, Guruswami, Wrochna and Živný (2020).
  Nakajima and Živný (arXiv:2210.03343): for balanced templates, BLP+AIP is no
  stronger than AIP.
- **Coprime counterexamples.** Lichter and Pago (arXiv:2407.09097).
- **Pinned, or singleton, reasoning.** Zhuk (arXiv:2509.18434). Singleton
  BLP+AIP solves every tractable CSP on at most seven values.
- **Cohomology of local sections.** Abramsky, Mansfield and Barbosa (2011);
  Ó Conghaile (2022).

**Novelty: known-overlap-likely** for the network rule, the H¹ reading, the
count and the local-reasoning table. We found no statement of:
- knots among loops as atoms;
- the k + 1 bound, with stars attaining it;
- selector shapes as nerves of fixed-point sets;
- the orbit-ideal criterion over an arbitrary ring;
- the coprime tie as the smallest integer-fooled case.

All of these are elementary. The program's reading is new.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: holes as cohomology (memory of networks; local reasoning) | **Status:** Successful | Part 1 proved (Lean for loops, bouquets, nerves, free contact, the k + 1 bound, every complex; prose for networks, H¹ and the count). Part 2 proved in prose with verified certificates. All six frozen census predictions hold. One planning-stage claim was withdrawn before the freeze. |
| Local direction: networks of permutation (group-like) contact | Practically exhausted for these questions | Memory and local reasoning are both fully classified for this class. More groups or graphs would not change either conclusion. |
| Broader exploration: knots, holes and local-to-global reasoning | Known alternatives | Hard holes need contact among three or more distinctions (Tseitin-like networks of knots), which this program has not tested. Native network formation (question 9) is unmapped beyond hand-laid networks. |
| Long-term goal: native structure from knots (questions 3 and 9) | Capability gained; obstruction learned | Gained: loops compose into knots natively under contact with fixed points, at k + 1 values for k loops; free contact keeps them independent. Learned: permutation holes are shallow, so they cannot carry hardness. Still missing: a law that makes the network. |
| Next recommendation: deep holes in networks of three-distinction knots | **Next step:** Continue in a fresh epic. Put a knot on three witness distinctions at each hyperedge of small layouts: parity (Tseitin), Z₃-sum and NAE knots on K₄, K₃,₃, the Petersen graph and the cube. Measure the least refuting level of affine relaxations over F₂, F₃, Q and Z, and test whether the shape's holes (the hole criterion's bound) predict that level better than treewidth does. | It asks whether the program's holes say anything about hardness beyond classical expansion. The alternative, a bounded search for a law that makes networks (question 9), rates 1/3: no concrete lead yet. |
| Interest | **2/3 — Promising** | A real discriminator: holes either track the refuting level or they do not, and either answer settles the hole criterion's use as a hardness tool. Main uncertainty: classical Tseitin results (Grigoriev; Buss, Grigoriev, Impagliazzo and Pitassi) may already determine the answer, so the test may only rediscover them. |
| Execution | Not started | Needs the owner's go-ahead. Stop if, on the declared layouts, the refuting level is a function of treewidth alone and the hole bound adds nothing. |
