# Which knots remember a loop

Epic `KNOT-LOOPS-20261019-001`, 2026-10-19. This is the decision note. It
addresses open question 3 of `docs/KNOT_INTUITION.md` (composition through
witnesses) and bears on question 9 (space from a law).

## The question

Join copies of a knot into a ring. Each copy passes one witness distinction to
the next, and the last passes one back to the first. Then forget the
witnesses. Does the composite on the remaining distinctions stay constrained,
so that the loop leaves a trace? And beyond rings: what happens in networks
with several loops, and with many-valued distinctions?

The useful object is the **transfer**: for each value of a copy's middle
distinctions, the 2×2 table of (witness in, witness out) pairs it allows. A
ring allows a pattern when the composed tables have a fixed point.

## What was found

### The ring theorem (B, proved in Lean)

`KNOT-LOOPS-20261019-001B-P001` proves five statements for every knot link
under the forgetting reading. A link has one witness in, one witness out and
any number of middle distinctions.
1. Every transfer is a permutation (identity or swap) or misses at most one
   pair.
2. A ring excludes a pattern exactly when every transfer along it is a
   permutation and an odd number of them swap. This holds for mixed rings,
   whose copies come from different knots.
3. Two patterns that differ in one middle distinction are never both
   excluded, so a ring composes into a knot or into nothing.
4. A link's transfers are all permutations exactly when it is a parity
   relation.
5. A ring of k copies of one link excludes something exactly when the link has
   a swap transfer and either k is odd or the link also has an identity
   transfer.

**Counting.** A link has S swap transfers and I identity transfers among its
2^d middle values. A ring of k copies then excludes ((S+I)^k − (I−S)^k)/2 of
its 2^{dk} patterns.
- **Parity keeps exactly half at every length**, which is one full bit.
- **Every other knot's memory fades** like ((S+I)/2^d)^k.

### The census (A, exploratory; one frozen prediction refuted)

`KNOT-LOOPS-20261019-001A-E001` covers:
- every knot on three variables (34) and four variables (742);
- every placement of the witness pair, which makes 9,108 ring placements;
- ring lengths up to 8;
- 82,824 mixed rings and 816 chains.

On these cases it confirms statements 1, 2, 3 and 5 and the counting formula
exactly.

**One frozen prediction failed.** P3 predicted that a placement keeps every
ring constrained only if it is parity. In fact 1,224 four-variable placements
keep some constraint at every length. A swap table plus an identity table is
enough, at exponentially small strength.

The correction (statement 5 and the counting formula) was found afterwards, on
the same data, and is now proved. The ticket is recorded as **refuted** for
its frozen signal.

### Beyond rings (C, exploratory)

`KNOT-LOOPS-20261019-001C-E001`:
- **Parity networks remember one bit per independent loop.** On the 4-cycle,
  K₄, K₂,₃, the triangular prism, the 3×3 grid and K₃,₃, the composite of
  parity copies keeps exactly E − V + 1 bits: 1, 3, 2, 4, 4 and 4. That is
  the number of independent loops. Wherever every transfer is a permutation,
  the holonomy rule is exact: a pattern is excluded exactly when some cycle
  has an odd number of swaps.
- **Other knots remember little, and only where implications can chain.**
  - At most 0.85 bits, and only on K₄, the prism and the grid. On the 4-cycle,
    K₂,₃ and K₃,₃ they remember nothing.
  - Post hoc: part of this memory has no odd cycle of permutation edges behind
    it.
  - It comes from transfers that forbid one pair, which act like implications
    and can frustrate one another, as in 2-SAT.
  - It vanishes where every edge points from one side to the other, so no
    implication chain can form.
- **Many-valued links with permutation transfers keep a constant amount.**
  - A Z₃ link keeps log₂3 bits at every length, whatever the order of its
    copies.
  - A link whose middle value picks any permutation in S₃ keeps log₂(3/2)
    bits at every length.
  - From length 3 on, its composite depends on the order of the loop: the
    holonomy no longer commutes.
  - Transposition links keep log₂3 bits at even lengths and none at odd ones.
- **Random three-valued knots forget.** Sampled knots almost never have
  permutation transfers (1,998 of 2,000 have none). Their memory falls below
  0.001 bits by length 7.

## What it means

- **A loop becomes a hole only through group-like contact.**
  - A ring of parity knots composes into one knot on all its middle
    distinctions. In this program's language that is a hollow simplex: the
    loop turns into a hole.
  - Every other knot either dissolves or keeps a trace that fades with the
    loop's length.
  - So the knots that can carry a loop are the ones whose transfers are
    permutations, which form a group.
- **Networks of parity knots remember their loops exactly.** One bit per
  independent loop is the first Betti number of the network: the composite
  records the network's cycle space. Classically, this is Tseitin's parity
  formula read backwards, and the same algebra as Z/2 holonomy.
- **Non-commuting contact remembers order.** With S₃-valued transfers the
  composite depends on the order of the copies around the loop. Abelian
  contact cannot see this.
- **Question 9 gains a necessary condition, not a construction.** A law can
  leave a lasting record of its own loops only if its contacts act as group
  elements on the witnesses. That rules out most knots. It does not make a
  space: the networks here were laid out by hand.
- **There is a link to local reasoning.** Local consistency methods fail
  exactly on constraints that can simulate linear equations over a group
  (Barto and Kozik 2009). The loops a knot can remember are the ones local
  reasoning cannot fill.

## Nearest known results

- **Transfer matrices.** Composing two-place constraints along a cycle and
  reading the diagonal of the product is classical.
- **Tseitin formulas.** Odd charge on a graph is a parity contradiction. Its
  algebra is Z/2 holonomy around cycles.
- **Bounded width.** Barto and Kozik, *Constraint satisfaction problems of
  bounded width* (FOCS 2009): local consistency fails exactly on
  group-equation structure.
- **Cohomology of local sections.** This is how contextuality (Abramsky,
  Mansfield and Barbosa 2011) and cohomological k-consistency (Ó Conghaile
  2022) treat local-to-global failure. The present results are the simplest
  case: H¹ of a graph with group coefficients.

**Novelty:** known-overlap-likely for the mathematics. The project's reading
is new: among knots, only group-like contact carries a loop, and parity
carries it at full strength.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: which knots remember a loop | **Status:** Successful | The ring theorem is proved, the census and the networks agree, and one frozen prediction was refuted and corrected. |
| Local direction: rings and networks of Boolean knots | Practically exhausted for rings | Rings are settled by the theorem. In networks, non-group memory is real but small, depends on edge orientation, and is classical 2-SAT frustration. |
| Broader exploration: knots, holes and loops | Known alternatives | Not yet explored: non-abelian contact on networks, and holes as local-to-global cohomology. |
| Long-term goal: native structure from knots (questions 3 and 9) | Obstruction learned | A lasting record of loops needs group-like contact. Space still needs a law that makes the network. |
| Next recommendation: holes as cohomology | **Next step:** Continue in a fresh epic. Show that a network's composite is the H¹ obstruction of its contact group: one bit per loop for parity, and loop data up to conjugacy for S₃. Then compare that obstruction with k-consistency and cohomological k-consistency on small instances. | It joins this result to the local-to-global literature and asks whether non-commuting contact records more than the number of loops. |
| Interest | **2/3 — Promising** | A clean bridge with a concrete test. Main uncertainty: the abelian case is classical, and the non-abelian one may be too. |
| Execution | Not started | Needs the owner's go-ahead. Stop if the non-abelian composites record nothing beyond the conjugacy classes of loop holonomies. |
