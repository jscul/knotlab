# Intuitions

The contact-first program asks whether logic can build structure, such as
holes, paths and spaces, without assuming a space to start from. Its working
answer begins with one object: the **logical knot**, two or more open
distinctions bound together so that the whole is constrained but no part is.

This page states the intuitions behind that answer in plain terms. Each one is
tied to what has been proved or checked in this repository, and each is
labelled by what kind of claim it is.

| Label | Meaning |
| --- | --- |
| **Proved (Lean)** | Kernel-checked in [`lean/`](lean/), core Lean 4, standard axioms only |
| **Proved (note)** | Proved in a note in [`notes/`](notes/), whose numbers a script rechecks |
| **Proved (here)** | A short proof given on this page |
| **Checked** | Verified exhaustively on finite cases by [`tests/test_knotlab.py`](tests/test_knotlab.py) |
| **Classical** | A known theorem the intuition relies on, with its source |
| **Reading** | Our interpretation. It is not a theorem and nothing is proved from it |

Most of the mathematics under the first sections is classical. What is ours
there is the reading: which questions to ask, and what the known answers mean
when asked this way. Sections 9 and 10 report results that are new as far as
we found. Section 11 lists what is classical and what is ours.

To try anything on this page, run commands from the repository root:

```bash
PYTHONPATH=tools python3 -m knotlab demo
```

## Contents

1. [The picture](#1-the-picture)
2. [The knot test](#2-the-knot-test)
3. [Pairs cannot make a knot; three places can](#3-pairs-cannot-make-a-knot-three-places-can)
4. [What a knot hides](#4-what-a-knot-hides)
5. [Holes and knots](#5-holes-and-knots)
6. [Requirement and choice](#6-requirement-and-choice)
7. [Knots from competing pairs](#7-knots-from-competing-pairs)
8. [Which knots remember a loop](#8-which-knots-remember-a-loop)
9. [How deep a hole is](#9-how-deep-a-hole-is)
10. [Counting what emerges](#10-counting-what-emerges)
11. [What is classical and what is ours](#11-what-is-classical-and-what-is-ours)
12. [Open questions](#12-open-questions)
13. [Glossary](#13-glossary)

## 1. The picture

- **A line is not enough.** A chain of implications only orders its members,
  and open strings can always be rearranged into one another.
- **A single loop is not enough.** A loop of implications forces all its
  members to be equal, so it collapses to a point. A loop of "equal" and
  "unequal" steps collapses to one free bit, or contradicts itself.
- **What is real is what lies between bound loops.** The binding belongs to
  the pair, not to either loop. No part smaller than the whole shows it, and
  erasing either loop removes it.
- **A loop is a logical structure, not a spatial one.** What it brings to a
  binding is an *open distinction*: a bit it leaves free.

## 2. The knot test

Read a system of constraints as the set of joint states it allows. Auxiliary
"witness" variables may appear, and are quantified away. Nothing outside the
constraints, such as an executor or a scheduler, may supply an input. A
verdict depends only on the allowed states, never on how the constraints are
written.

Each loop contributes an open distinction. The contact is one more variable,
`c`. **Erasing a loop forgets it**: its variable is no longer constrained by
anything.

A relation over the loops' distinctions and the contact is a **knot** when:

- **K1, binding:** it is constrained as a whole;
- **K2, loss on erasure:** forgetting any one variable, a loop's or the
  contact's, leaves the others unconstrained;
- **K3, coexistence:** some joint state is allowed (K2 already implies it).

In short: **constrained as a whole, unconstrained in every part**, like
Borromean rings. Forgetting the contact must free the loops too, so loops tied
directly to each other do not count.

| Relation | Knot? | Why |
| --- | --- | --- |
| `¬A ∨ ¬B ∨ c` (the **atom**: if A and B, then c) | yes | excludes one state; every pair is free |
| `A ⊕ B ⊕ c = 0` (**parity**) | yes | excludes four states; every pair is free |
| not-all-equal(A, B, c) | yes | excludes 000 and 111; every pair is free |
| `(¬A ∨ c) ∧ (¬B ∨ c)` (a **common hub**) | no | forget B, and A still forces c |
| `A ≠ B`, with c unused | no | forget c, and A and B stay tied |
| `c = A ⊕ B` with A fixed true | no | A is not open, so it is constrained alone |

```bash
PYTHONPATH=tools python3 -m knotlab check --cnf "~A ~B c" --loops A B --contact c
PYTHONPATH=tools python3 -m knotlab check --cnf "~A c; ~B c" --loops A B --contact c
```

The first command reports a knot. The second reports a hub, and explains which
binding survives each erasure. *Proved (Lean):* `ForgettingKernel.lean`
(`atom_isKnot`, `parity_isKnot`, `hub_not_knot`, `tied_not_knot`).

## 3. Pairs cannot make a knot; three places can

**The intuition.** Whatever a two-place rule says, it says about a pair. A
system of two-place rules that must all hold is therefore known from its
pairs. A knot shows nothing in any pair, so pairs can never pin one down.
Three-place rules can.

- **Classical.** Relations definable by 2-CNF, even with witnesses quantified
  away, are exactly those closed under the majority operation (Schaefer
  1978). A majority-closed relation is the conjunction of its two-variable
  projections (Baker and Pixley 1975).
- **Hence no 2-CNF defines a knot.** If one did, the knot would equal the
  conjunction of its pairwise projections. Those are all unconstrained, so it
  would allow everything, contradicting K1. More witnesses do not help.
  *Proved (Lean)* for three variables directly: for any target state, take
  allowed states agreeing with it on each pair; their majority is the target
  (`no_two_cnf_defines_knot`, `majority_with_free_pairs_is_full`).
- **Width 3 binds any number of loops.** A chain of three-literal clauses
  joined by witnesses does it: `w1 ∨ ¬L1 ∨ ¬L2`, then `w2 ∨ ¬w1 ∨ ¬L3`, and so
  on, ending with `¬w(n−2) ∨ ¬Ln ∨ c`. Each witness `wi` is forced exactly when
  the loops before it are all present, so it records that they are bound.
  Naming each partial parity does the same for parity. *Proved (Lean):*
  `chain_defines_knot`, `parity_chain_defines_parity`.
- **Without witnesses, a knot needs full width.** A knot on m variables
  implies no clause on fewer than m of them, because every proper projection
  is unconstrained. *Proved (here)*; Lean checks the three-variable case
  (`no_clause_on_a_b` and its two companions).

So **3 is the exact threshold**. Width 2 is closed: pairwise in, pairwise out.
Width 3 reaches every knot.

**Reading.** Two-place rules are logic, not topology. The first place where
logic binds something that no part shows is the step from two-literal to
three-literal clauses. This is a statement about what can be *expressed*, not
about how hard anything is to compute. There are easy knots: the atom is a
Horn clause, and Horn satisfiability takes linear time. So this boundary is
not the boundary between P and NP, and nothing here addresses that question.

## 4. What a knot hides

**The intuition.** A knot is invisible in its parts, so the whole holds
information that no part holds. That information can be measured, and it is
small: a knot hides at most one bit.

- **Two loops and a contact have exactly 34 knots, in five shapes.** *Checked*
  against all 256 relations on three variables:

  | Excluded states | Relations | Bits the whole holds and no pair does |
  | --- | --- | --- |
  | 1 (a single three-literal clause: the atom) | 8 | 0.193 |
  | 2, opposite corners | 4 | 0.415 |
  | 2, at distance two | 12 | 0.415 |
  | 3 | 8 | 0.678 |
  | 4 (parity, even or odd) | 2 | 1.000 |

  A relation on three variables has every pair free exactly when no two of
  its excluded states differ in one coordinate. So a knot's excluded states
  form a nonempty independent set of the 3-cube. There are 34 such sets, in
  five classes under the cube's 48 symmetries.
- **A knot hides at most one bit, and only parity hides a full bit.**
  *Proved (here).* Forgetting one variable of a knot on m variables leaves all
  2^(m−1) assignments of the others, and each needs at least one allowed
  state. So a knot allows at least half of its states. If it allows exactly
  half, forgetting the last variable is a bijection, so the relation is the
  graph of a function f. Two allowed states that differ in one coordinate
  would make that projection two-to-one, so f changes whenever one input bit
  changes. That makes f parity or its complement.
- **The atom is the smallest bond.** It excludes the fewest states. It is
  also what an AND gate adds to its two-place parts: a two-input gate's
  relation is pairwise exactly when the gate ignores an input, so each of the
  ten gates that use both inputs needs a three-place clause, which is an atom
  up to which value of each variable counts as present. *Checked*
  (`knotlab worlds`).

**Reading.** A distinction is the material and an atom is what holds material
together. Digital hardware can build anything because its gates supply atoms.

```bash
PYTHONPATH=tools python3 -m knotlab patterns
```

## 5. Holes and knots

The two words are easy to confuse. A system's **shape** is built from what it
leaves free: each free distinction is a point, each pair that takes all four
combinations is an edge, each free triple is a filled triangle, and so on. A
**hole** is any gap in that shape. A **knot** is the smallest kind of hole: a
set whose every part is free, but which is not free itself.

```text
a knot: an empty triangle            a hole made by ties: a square

        A                               a ──── b
       / \                              │      │
      B ─ c                             d ──── c

all three pairs are free;            the pairs a–c and b–d are tied, so
A, B and c together are not          those edges are missing; the gap is
                                     made of missing edges
```

- **Pairwise rules make only "flag" shapes.** In a 2-CNF system a set is free
  exactly when all its pairs are free. So two-place rules can make holes, as
  the square shows, but never an empty triangle. *Checked* (`SpaceTest`; of
  399 random 2-clause systems on six variables, 29 have holes and none has an
  empty triangle).
- **Every knot is a hole, but not every hole is a knot.** To tell whether
  things are bound, look at the knots, not at the size of the holes. Two
  unrelated knots side by side leave a three-dimensional hole, because the
  join of two circles is a 3-sphere, yet nothing binds them.
- **Logic allows every shape.** Every simplicial complex is the shape of some
  system. *Proved (Lean):* `every_complex_is_a_nerve` in `LoopNerve.lean`
  builds one from loops whose contacts permute witness values.

**Reading.** Logic gives intrinsic holes, paths and separation, but it selects
no space. Whatever space there is has to come from a law. Which law gives a
shape that looks like a space of low dimension is open (question 1 below).

```bash
PYTHONPATH=tools python3 -m knotlab space
```

## 6. Requirement and choice

- **A requirement** says what must exist when other things do: `A ∧ B → c`.
  A system of requirements has exactly one least world, and propagation finds
  it in linear time. *Classical:* van Emden and Kowalski 1976; Dowling and
  Gallier 1984.
- **Computation is a forced world.** Carry each bit as which of two things
  exists, "x = 0" or "x = 1". Every gate then becomes four atoms, so every
  circuit runs as a least world. *Classical:* Horn satisfiability and monotone
  circuit value are complete for polynomial time. *Checked:* 4-bit addition
  comes out right for all 256 input pairs.
- **A choice** says that when something exists, one of several things must:
  `c → A ∨ B`. With c present there are two minimal worlds, {A} and {B}, and
  nothing ranks them.
- **Requirement and choice are one knot read two ways.** "A and B require c"
  becomes "c requires A or B" when false is read as "exists". 16 of the 34
  two-loop knots are a pure requirement under one reading and a pure choice
  under the other. The other 18, parity among them, offer choices under both.
  *Checked* (`knotlab choice`).
- **Knots never select.** Every variable of a knot takes both values, and
  fixing one loop's value removes it from the binding.

**Reading.** Requirements never select, since their world is unique. A choice
leaves alternatives that the constraints do not rank. The program's
interpretive stance is that coherent alternatives are equally real, with no
global selector. The mathematics shows only that the constraints do not
select. It neither proves nor refutes that stance.

## 7. Knots from competing pairs

Two-place rules can be combined in two ways. Under **conjunction** every rule
must hold, and, as section 3 shows, pairs then never make a knot. Under
**competition** the rules are preferences, and the allowed states are those
that break the fewest.

**The intuition.** Ask three distinctions to differ pairwise. Around the
triangle the differences cannot all hold, so the preferences are
*frustrated*. The states that break exactly one preference are the six
not-all-equal states, and those form a knot. Competition can make a knot from
pairs, but only this kind.

- **Exactly four knots come from competing pairs on three variables.** A knot
  on three variables is the set of least states of an energy with only one-
  and two-variable terms exactly when its excluded states are an opposite
  pair. These are the four not-all-equal relations, the frustrated triangles.
- **None on four or more variables.**
- **With hidden variables, competing pairs make every knot.** Ten 2-clauses
  and one hidden variable have the clause `x ∨ y ∨ z` as their best states.
  *Classical:* this is the gadget behind the NP-hardness of MAX-2-SAT (Garey,
  Johnson and Stockmeyer 1976).

*Proved (Lean):* `CompetitionKernel.lean` (`three_variable_classification`,
`no_knot_beyond_three`, `every_relation_by_gadgets`, and 16 more). The
three-variable case is an instance of a known criterion for least sets of
pairwise energies (faces of the correlation polytope; Rauh, Kahle and Ay
2011). We have not found the four-variable statement in print.

**Why only four** (*proved here*). Every function of Boolean variables is a
unique polynomial with one coefficient per set of variables. A pairwise energy
has no coefficient on three variables. On three variables that top coefficient
is the energy summed over the states with an odd number of ones, minus the sum
over the rest. Shift the energy so its least value is zero. Then only the
excluded states count, each positively, so if they all had the same parity the
top coefficient would not vanish. A knot's excluded states are never
neighbours, and two of opposite parity must be opposite. So the excluded
states are one opposite pair.

**Reading.** What a knot certifies depends on what is hidden. With every
variable visible, a knot other than the frustrated triangles cannot come from
pairwise terms, even competing ones. With hidden variables, a knot certifies
only that the rules are not pairwise rules that must all hold.

## 8. Which knots remember a loop

**The intuition.** Join copies of a knot into a ring, each passing a witness
to the next and the last passing back to the first. Then forget the
witnesses. Does the ring still remember that it is a loop? Only if going
around can flip something, and only a contact that acts like a group element
can flip without losing information.

*Proved (Lean):* `RingKernel.lean`, all under the forgetting reading.

- **Transfers.** For fixed values of a copy's other distinctions, the copy
  passes its witness through a 2×2 table. Every such table of a knot is a
  permutation (identity or swap), or misses at most one pair
  (`transfer_cases`).
- **A ring excludes exactly the odd loops.** A ring rules out a pattern
  exactly when every table along it is a permutation and an odd number of
  them swap (`ring_excludes_iff`). So a ring of knots composes into a knot or
  into nothing (`ring_one_flip`).
- **Only parity carries a loop at full strength.** A knot whose tables are all
  permutations is a parity relation (`all_permutations_iff_parity`). A ring of
  parity knots keeps one full bit at every length.
- **Other knots fade.** Their share of excluded patterns shrinks exponentially
  with the ring's length. A ring of not-all-equal knots forgets the loop
  completely.

Networks extend this. *Proved (Lean):* `LoopNerve.lean`.

- **Free contact records each loop separately.** When a contact's every
  holonomy that fixes one value fixes all of them, as for parity or addition
  mod q, no two loops ever tie (`free_contact_binds_nothing`). Each
  independent loop then carries its own class, a first cohomology class.
- **Contact with fixed points binds loops, into atoms.** The loops a network
  can switch on together form the nerve of the holonomies' fixed-point sets
  (`shape_is_nerve`). A minimal set of loops that cannot all be on is a knot
  among loops that excludes exactly one pattern: an atom
  (`minimal_nonface_is_knot`).
- **Binding costs witness values.** A knot among k loops needs k + 1 witness
  values (`knot_needs_more_values`). Boolean witnesses cannot even tie two
  loops (`boolean_contact_never_ties`).

**Classical background.** Composing tables is the transfer-matrix method. A
parity ring with an odd number of swaps is Tseitin's parity contradiction on a
cycle. Local consistency methods fail exactly on constraints that can simulate
equations over a group (Barto and Kozik 2009), the same dividing line. The
mathematics here is elementary. The reading is ours.

**Reading.** The two extreme knots play opposite roles. Parity, which hides
the most, carries a single loop at full strength. The atom, which hides the
least, binds loops together through fixed points. A law can keep a lasting
record of its own loops only if its contacts act as group elements.

```bash
PYTHONPATH=tools python3 -m knotlab rings
PYTHONPATH=tools python3 -m knotlab holonomy
```

## 9. How deep a hole is

**The intuition.** Put a parity knot at every vertex of a graph, sharing the
graph's edges as distinctions: each vertex asks its edges to sum to a charge.
Such a network is impossible exactly when the total charge is odd. That is a
hole, but every small window of the network looks perfectly consistent, since
the odd unit of charge can be pushed anywhere by flipping edges along a path.
So how much of the network must an observer hold at once to see the hole? The
answer is a width of the graph: the charge has to be carried across the widest
boundary of the best sweep.

These networks are Tseitin formulas, and "how much an observer must hold"
becomes the degree of a refutation.

- **Reasoning mod 2 sees the hole at once.** Summing every vertex's equation
  counts each edge twice, so a refutation of the size of one knot exists.
- **Every other field needs the toggle width.** *Proved (note):* over every
  field of characteristic other than 2, the Nullstellensatz degree of the
  Tseitin formula, written clause by clause, equals the **toggle width** of
  the graph: the cheapest way to grow the empty vertex set into the whole
  graph by adding or removing one vertex at a time, where each step costs the
  edges it must keep track of. On graphs of maximum degree at most three this
  is exactly **cutwidth + 1**. In the ±1 encoding, with degree measured after
  reduction, it is exactly the cutwidth. The upper bound sweeps the charge
  across a layout, and the lower bound is a design whose values are signed
  sums over cuts.
  See [notes/tseitin-nullstellensatz-degree](notes/tseitin-nullstellensatz-degree/).

**Reading.** A hidden bit has a depth: the width an observer must hold to
carry it to where it shows. Holes made by loops of witnesses (section 8) are
shallow, and local reasoning sees them. Holes made by charges are as deep as
the graph's layout is wide, unless the reasoning computes in the charge's own
group. We have related results for other proof systems, with tree layouts in
place of linear ones; they are not yet published here.

```bash
PYTHONPATH=tools python3 -m knotlab depth
```

## 10. Counting what emerges

Deciding whether a network of knots allows any world can be easy while
counting its worlds is hard. Two notes in this repository locate where
counting turns hard.

- **The worlds of not-all-equal knots.** A 3-regular 3-uniform hypergraph is
  a network of not-all-equal knots in which every distinction sits in exactly
  three knots. Its proper 2-colourings are the network's worlds. Networks
  with no world at all are where these knots close up on themselves, and the
  program calls them three-fold spaces. Counting is #P-hard in general (Fan
  and Cai) and easy when the incidence graph is planar (Valiant). The note
  studies the class in between, Pfaffian incidence graphs, which contains
  every network with no world. *Proved (note):*
  - remove any one knot from a connected network with no world, and the
    worlds of what is left can be counted in polynomial time;
  - counting stays polynomial under twists that do not branch;
  - counting becomes #P-hard once twists branch. It stays #P-hard without any
    signs, and even when the incidence graph is a Pfaffian brace.

  See [notes/pfaffian-hypergraph-colourings](notes/pfaffian-hypergraph-colourings/).
- **Patterns in three dimensions.** When the laws counted are group laws on a
  3-manifold, counting worlds means counting homomorphisms from its
  fundamental group to a finite group. Rowell conjectured in 2009 that this
  count is computable in polynomial time for solvable groups. *Proved (note):*
  unless every #P function is computable in polynomial time, the conjecture
  fails. On links it fails already for S₃. On knots it fails for S₄, the
  smallest group for which it can, and for some groups of Fitting height two.
  For Heisenberg-type groups the note proves an exact dividing line.
  See [notes/knot-group-counting](notes/knot-group-counting/).

**Reading.** In the Heisenberg families, hardness appears exactly when the
twisted obstruction joins three nontrivial characters at once, which
three-component, pairwise-unlinked (Borromean) surgeries supply. Everything
pairwise stays countable. This echoes the K2 pattern of section 2, but it is a
statement about counting complexity, not about knots in our sense. The knot
test cannot tell hard groups from easy ones: every group law, read as the
relation x·y = z, is constrained as a whole and free in every pair.

## 11. What is classical and what is ours

- **Classical:**
  - 2-CNF relations are the majority-closed ones (Schaefer 1978) and are
    determined by their pairs (Baker and Pixley 1975);
  - three-place relations build every relation while two-place ones do not
    (Peirce's reduction thesis);
  - least worlds of Horn clauses (van Emden and Kowalski 1976);
  - Post's lattice and the Galois connection behind it (Post 1941; Geiger
    1968; Bodnarčuk, Kalužnin, Kotov and Romov 1969);
  - the compactness theorem;
  - frustration (Toulouse 1977) and the MAX-2-SAT gadget (Garey, Johnson and
    Stockmeyer 1976);
  - Tseitin formulas and their parity contradictions (Tseitin 1968);
  - Borromean and Brunnian links in topology.
- **Ours, as reading:**
  - the knot test K1–K3, read on allowed states with erasure as forgetting;
  - a binding is a constraint with no trace in any part, which vanishes when
    either loop is erased;
  - loops, their open distinctions and their witnesses are the units;
  - emergence begins at the first such binding;
  - distinctions are the material and atoms are the bonds;
  - a hidden bit has a depth.
- **Ours, as results.** The classifications and constants marked as proved
  here or in Lean are elementary. Several are classical facts in new language,
  and we give sources where we know them. The three notes contain results that
  are new as far as our searches found, and each note states its own novelty
  and folklore risk. See [FINDINGS.md](FINDINGS.md).
- **Not implied:**
  - Requirements alone run in linear time, and requirements with choice are
    NP-complete. That locates where hardness enters, but says nothing about
    whether P equals NP.
  - Nothing here is physics.
  - The interpretation that coherent alternatives are co-real is an
    interpretation, and nothing is proved from it.

## 12. Open questions

1. **Space from a law.** Logic allows every shape. Which uniform, local law,
   not written on a space in advance, gives a shape that looks like a space of
   low dimension? One necessary condition is known: a law keeps a lasting
   record of its loops only if its contacts act as group elements (section 8).
2. **Dynamics.** Are loops better modelled as processes whose outputs over
   time are the data, and does the static test survive that change?
3. **Limits.** No set of finite clauses binds infinitely many loops into one
   contact (by compactness). Does the program need a limit rule that does?
4. **Competition.** If least-violation states count as allowed, frustrated
   pairs make knots (section 7). Should they count?

## 13. Glossary

- **Distinction.** Two alternatives of which exactly one holds: one bit.
- **Loop.** A logical structure that leaves a distinction open.
- **Contact.** The variable through which loops are bound.
- **Witness.** An auxiliary variable that reports on something, such as
  whether two loops are bound. Witnesses are quantified away before a verdict.
- **Knot.** A relation that is constrained as a whole and unconstrained in
  every part (section 2).
- **Atom.** The knot `¬A ∨ ¬B ∨ c`: the smallest bond.
- **Hub.** One variable shared by several separate relations, such as
  `(¬A ∨ c) ∧ (¬B ∨ c)`. Sharing identity is not a binding.
- **Shape.** The simplicial complex of sets of distinctions a system leaves
  free. A **hole** is a gap in it, and a knot is the smallest kind of hole.
- **Depth.** How much of a network an observer must hold at once to see a
  hole in it (section 9).
