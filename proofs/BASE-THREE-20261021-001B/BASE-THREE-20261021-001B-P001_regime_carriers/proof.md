# What the regimes carry

Status: Proved

Ticket `BASE-THREE-20261021-001B`, 2026-10-21. It uses:
- `BASE-THREE-20261021-001A-P001` ("the regime proof"): the pairwise, frozen
  and transmitting regimes of laws on bits;
- `KNOT-LOOPS-20261019-001B-P001` ("the ring theorem", Lean, two-valued
  witnesses):
  - a ring excludes a pattern exactly when every transfer is a permutation
    and an odd number swap;
  - a link's transfers are all permutations exactly when it is a parity
    relation;
- `CUTWIDTH-DEPTH-20261020-001B-P001`: an odd-charge parity network on a graph
  of maximum degree at most 3 needs Nullstellensatz degree cutwidth + 1
  outside characteristic 2;
- `HOLES-AT-INFINITY-20261020-001B-P001`: on infinite systems, the ends can
  supply open distinctions that no loop supplies.

It also cites:
- **Post's lattice** of clones on two elements. One fact is used: a clone
  that contains a non-affine operation contains conjunction, disjunction or
  majority. The census checks it at the ternary level.
- **The Galois connection** between polymorphisms and pp-definable relations.
- **Schaefer's dichotomy theorem** (1978).
- **Bounded width:**
  - Horn and dual-Horn laws are decided by unit propagation;
  - two-literal laws by path consistency;
  - systems of linear equations over Z₂ by no bounded level of local
    consistency (Feder and Vardi 1998).
- **The strongly connected components** of an implication graph (Aspvall,
  Plass and Tarjan 1979).

## Standard statement

1. **Pairs make loops** (Theorem 1).
   - **What a pairwise cycle is.** A cycle of implications
     x₁ → x₂ → … → xₙ → x₁ allows exactly the two constant states. It is one
     open distinction carried by n variables: a loop.
   - **The first-emergence structure.** Two such loops, plus one knot on a
     member of each and a contact, give exactly that knot on
     (loop, loop, contact). Forgetting a loop or the contact frees the rest.
   - **Pairs alone never do this.** Pairwise clauses never knot two loops.
2. **Memory** (Theorem 2). A law on bits keeps a lasting record of a loop
   (rings that stay constrained at every length, at full strength) exactly
   when it defines a parity knot. That happens exactly when every
   polymorphism of the law is affine.
3. **Memory is opacity** (Theorem 3). With constants added, a law has bounded
   width exactly when it keeps no lasting record. So a law on bits remembers
   its loops exactly when it can hide a contradiction from every bounded local
   view.
4. **Hardness lives inside transmission** (Theorem 4).
   - **Pairwise and frozen laws** have polynomial-time constraint problems, with
     or without constants.
   - **Every law that is NP-complete with constants** transmits and keeps
     memory.
   - **The transmitting regime splits three ways:**
     - **forcing:** conjunction or disjunction is a polymorphism; no memory;
       transparent; polynomial;
     - **conservation:** every polymorphism is affine, and minority is one;
       memory; opaque; polynomial by Gaussian elimination;
     - **choice:** every polymorphism is affine, and minority is not one;
       memory; opaque; NP-complete with constants.
5. **Shallow and deep contradictions** (Theorem 5).
   - **Pairwise contradictions are shallow.** An odd cycle of disequalities,
     the liar loop, is refuted by 3-consistency at every length.
   - **Parity contradictions are deep.** Odd charges survive every level of
     consistency below the layout's width.
6. **Two kinds of universal cycle** (Theorem 6).
   - **A cycle of equalities** shares one distinction among its n members.
     Flipping one member needs changing all n. On an infinite cycle no finite
     change flips it: visible at every point, changeable at none.
   - **A ring of parity knots with hidden witnesses** is different. Every
     visible distinction flips with a change of three variables. The ring's
     single constraint is one knot on all its distinctions: changeable at
     every point, visible at none.

## Nearest known results

- **Strongly connected components** of 2-SAT implication graphs: Aspvall,
  Plass and Tarjan.
- **Schaefer's dichotomy** and Post's lattice.
- **Bounded width of Boolean constraint problems** (Feder and Vardi). Its
  algebraic form: the Boolean laws of bounded width are the Horn, dual-Horn
  and two-literal ones.
- **The program's ring theorem and depth results.** These give the memory and
  depth halves.

**Classification: classical ingredients; the equivalences as stated are the
program's.**
- **The ingredients are classical.** Bounded width against affineness is
  standard in the algebraic theory of constraint satisfaction.
- **The program contributes:**
  - reading loops as pairwise cycles;
  - the identity "memory = opacity" via the ring theorem;
  - the placement of hardness inside transmission and memory;
  - the two kinds of universal cycle.

## Theorem 1 (pairs make loops)

*Proof.*
1. **A cycle of implications.** Around the cycle, x₁ = 1 forces every xᵢ = 1,
   and x₁ = 0 forces every xᵢ = 0. Each pair is tied, and the two constant
   states are allowed.
   - **In general,** the strongly connected components of the implication
     graph of any pairwise system are its loops, each one distinction, unless
     forced or contradictory.
2. **The first-emergence structure.** Take loops L₁ and L₂ with no constraint
   between them, a contact c, and a knot K on (a, b, c), with a ∈ L₁ and
   b ∈ L₂. The projection onto (a, b, c) is K, because each loop just copies
   its distinction.
   - Forgetting L₁, all its members, leaves the projection of K onto (b, c),
     which is free by K2. Likewise for L₂ and for c.
   - So the structure passes the canonical knot test with its loops as loops.
3. **Pairs alone never knot.** By the regime proof's Theorem 1, every
   pp-definition from pairwise clauses has only ties. ∎

**The reading, offered for the owner's thesis.**
- **Pairs supply recurrences.** A pairwise cycle closes on itself and carries
  one distinction.
- **Triples supply contacts.** The first emergence of the protected thesis is
  two pairwise cycles and one triple.
- **The arity thesis is untouched.** Nothing changes in the protected arity
  thesis: pairs still form no knot, and no contact.

## Theorem 2 (memory)

*Proof.*
1. **From the ring theorem.** A link on bits keeps a lasting record exactly
   when all its transfers are permutations, exactly when it is a parity
   relation. So a law keeps a lasting record exactly when it defines a parity
   knot on three or more variables.
2. **If it defines parity P,** every polymorphism of the law preserves P. The
   polymorphisms of a parity relation on three or more variables are affine.
3. **If every polymorphism is affine,** the law defines every relation
   invariant under all affine operations (the Galois connection). That
   includes even parity on four variables, which is a knot. ∎

**In the census.** All 32 forcing laws lack memory, and all 56 other
transmitting laws have it. The 10 explicit parity gadgets found all lie in
laws with memory. Rings of a parity link exclude half of all patterns at every
length. Rings of a Horn link exclude nothing at any length, since its
transfers are never swaps.

## Theorem 3 (memory is opacity)

With constants added, a law's polymorphisms are its idempotent ones.

*Proof.*
1. **Not every polymorphism affine.** Then, by Post's lattice, the law has
   conjunction, disjunction or majority. All three are idempotent, so they
   survive the constants, and the law has bounded width: unit propagation or
   path consistency decides it.
2. **Every polymorphism affine.** Then the law defines parity, by Theorem 2,
   also with constants. Systems of parity constraints have no bounded width
   (Feder and Vardi): for every k there are unsatisfiable parity networks that
   k-consistency accepts.
3. **So memory and opacity coincide.** By Theorem 2, a lasting record exists
   exactly in case 2, where bounded local reasoning fails. ∎

**In the census.** All 273 small laws satisfy the ternary form of the
Post-lattice fact, and memory coincides with opacity in all 273.

## Theorem 4 (hardness lives inside transmission)

*Proof.*
1. **Pairwise laws** are closed under majority, with or without constants, and
   are polynomial.
2. **Frozen laws** are definable by one-signed clauses, implications and units
   (the regime proof's Theorem 6), which are Horn or dual-Horn even with
   constants, and are polynomial.
3. **So every NP-complete law transmits.**
4. **With constants,** a law is polynomial when it has conjunction,
   disjunction, majority or minority (Schaefer). Otherwise it is NP-complete.
   So an NP-complete law has none of the four, and in particular every
   polymorphism is affine: it keeps memory.
5. **Splitting the laws with memory.** Minority separates conservation from
   choice. ∎

**In the census.** Of the 88 transmitting small laws:
- 32 are forcing;
- 2 are conservation (the two parity laws);
- 54 are choice.

All 54 choice laws are NP-complete with constants. 15 of them are NP-complete
even without constants, because they have no all-0 or all-1 state; the others
are trivially satisfied by such a "vacuum". No pairwise or frozen law is
NP-complete.

## Theorem 5 (shallow and deep contradictions)

*Proof.*
- **Shallow.** An unsatisfiable pairwise system is refuted by path
  consistency, which is bounded width 2 for two-literal laws.
  - **The liar loop.** An odd cycle of disequalities, x₁ ≠ x₂ ≠ … ≠ x_n ≠ x₁,
    is refuted by 3-consistency at every length.
- **Deep.** An odd-charge parity network is a system of linear equations over
  Z₂. By Feder and Vardi, no fixed level of consistency refutes all of them.
  - **The exact depth.** By the cutwidth proof, on graphs of maximum degree at
    most 3 it needs Nullstellensatz degree cutwidth + 1, outside
    characteristic 2. ∎

**In the checks.**
- **Liar loops.** Odd disequality cycles of lengths 3 to 11 are refuted by
  3-consistency and not by 2-consistency.
- **Odd charges.** These were tested on K₄, the prism, K₃,₃, the 3 × 3 grid and
  the cube.
  - They survive 2-, 3- and 4-consistency.
  - They are refuted once every variable is held (K₄).
  - Satisfiable even charges also survive every level, as they should.

## Theorem 6 (two kinds of universal cycle)

*Proof.*
1. **A cycle of equalities.** It has two solutions, all 0 and all 1. A
   solution with one member flipped differs from the start in all n members.
2. **On an infinite cycle,** no finite change flips any member. Under the
   adopted source-aware reading, such a distinction is not native: it is
   fixed everywhere and visible at every member.
3. **A ring of parity knots** xᵢ ⊕ yᵢ ⊕ xᵢ₊₁ = 0, with hidden witnesses xᵢ.
   - **Every flip is local.** Flipping y₁ is completed by flipping y₂ and x₂.
     That is three variables at every length, so every visible distinction is
     native.
   - **The constraint is everywhere.** The visible relation is Σyᵢ = 0: one
     knot on all n visible distinctions, seen by no proper part.
4. **On infinite networks,** that constraint moves to the ends (the
   ends-supply-openness proof). It becomes end-supplied, visible to no
   finite part. ∎

**The reading.** A cycle can act everywhere in two complementary ways.
- **By identity, in pairs:** every member shows the shared distinction, and no
  member can change it.
- **By holonomy, in triples:** every member can change, and no member shows
  the shared constraint.

The first is a fixed fact visible everywhere; the second is a hidden fact
changeable anywhere.

## Corollary 7 (the base map)

| Regime | Polymorphism signature | Knots | Composition | Lasting memory | Bounded width (with constants) | Hard |
| --- | --- | --- | --- | --- | --- | --- |
| pairs | majority | none (ties only) | collapses | no | yes (2) | no |
| frozen | conjunction or disjunction; one-signed clauses | "not all on" / "not all off" | never | no | yes (1) | no |
| forcing | conjunction or disjunction, with transmitting knots | two-signed | grows | no | yes (1) | no |
| conservation | affine, with minority | parity | grows, like cycles | yes | no | no |
| choice | affine, without minority | two-signed and parity | grows | yes | no | with constants |

Census of the 273 laws generated by one relation on at most three bits: 183
pairwise, 2 frozen, 32 forcing, 2 conservation, 54 choice.

## What this does not show

- **Only bits.** Larger domains are not treated.
- **One converse rests on Post's lattice:** a non-affine clone contains
  conjunction, disjunction or majority. It is checked at the ternary level on
  every small law.
- **Unbounded width** of parity systems is cited (Feder and Vardi). The checks
  show only that levels 2–4 fail on five graphs.
- **"Pairs make loops" is a reading.** It does not answer which structures
  count as native loops in general.
- **No physical claim.** "Universal cycle" names a mathematical structure, not
  a physical one.

## Checks

`check.py` writes `result.json` in about a second. All checks pass, and all
five controls are rejected.

- **Theorem 1.**
  - Implication cycles of lengths 2 to 6 allow exactly the two constant
    states, and tie every pair.
  - Two loops (of 3 and 4 implications) were joined by a parity, Horn or "not
    all on" contact. In each case the relation on (loop, loop, contact) is that
    knot, and forgetting a loop or the contact frees the rest.
  - 200 random pairwise joins of two loops never give a knot.
- **Theorems 2–4.** The ternary polymorphisms of all 273 small laws were
  computed.
  - The Post-lattice fact holds in all 273.
  - Memory equals opacity in all 273.
  - The regimes split as 183, 2, 32, 2 and 54.
  - NP-completeness with constants occurs in 54 laws, all choice. Without
    constants it occurs in 15, also all choice. None is pairwise or frozen.
  - All 10 parity gadgets found lie in laws with memory.
  - Parity rings exclude half the patterns at lengths 1–8; Horn rings exclude
    nothing.
- **Theorem 5.**
  - Liar cycles of lengths 3 to 11 are refuted at level 3 and not at level 2.
  - Odd-charge parity networks on five graphs survive levels 2–4, and K₄'s is
    refuted with every variable held.
  - Even charges survive.
- **Theorem 6.**
  - In equality cycles of lengths 3 to 20, the least flip of one member is n.
  - In parity rings of lengths 3 to 12, the least flip of a visible
    distinction is 3, and the visible relation is one knot.
- **Controls,** each rejected:
  - "every transmitting law keeps a lasting record";
  - "bounded local reasoning refutes every parity contradiction";
  - "a pairwise contradiction needs wider reasoning as it grows";
  - "some hard law is pairwise or frozen";
  - "pairwise clauses alone can knot two loops".
