# Referee report NEVER-NEST-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The proofs hold.** N1 to N6 are correct, and the referee checked them line by line: N4's minimal empty cell, N3's medians, N5's
  refill and N6's invariance.
- **The referee's own reimplementation agrees.** It wrote NN and NNF itself, on its own KF3 move enumeration and its own order count.
  - **Eight NN runs to n = 40** (bracketings of 5 to 8):
    - two orders at every step, and none stalls;
    - no subdivision before the first full grid, which comes at 9, 12, 15 and 20;
    - after it, every subdivision at a full grid;
    - a fill fraction of 0.80 on steps 21 to 40.
  - **Four NNF runs to n = 32,** stopped there by the memory cap. Each matches N3 and N4.
- **What is read and what is given.** The note's table is right in substance, but it needs three additions.
  - **NNF reads only the states.** Its order count is a function of the state set alone, but a global one.
  - **What is given is the cap "at most two orders" and the fallback step, a subdivision.** NN2 shows that the fallback can be
    loosened.
  - **NNF is CUBE-DOUBLING's cheapest rule with that cap.** Uncapped, the same rule goes to every order. So the "two" is wholly the
    cap's, and the rule does not choose it.
- **It settles LOCAL-ROOM's open point.** A states-only rule that reads more than reach does hold two orders and fill them. The
  memory of LOCAL-ROOM's class law is not needed, once the rule is told "two".

## What holds

- **N1 (subdivision keeps the orders).** t becomes two nested splits with t's crossings. The crossing graph gains a twin of t, and
  the λ-cover argument (insert t_v ⊂ t_u in t's chain; delete p for the converse) is right.
- **N2 (fills of triples; full only with at most two middles).**
  - The end bounds from Lemma C, the gap colouring and the count n ≤ (m + 1) + Σ g_{i−1}g_i ≤ (s₀ + 1)(s₁ + 1) are right.
  - Equality needs h ≤ 2, since otherwise g₀g₃ is missing.
- **N3 (refill from a full grid; NNF).**
  - *(i)* After a fill the crossing graph is still complete bipartite and connected, so its bipartition is fixed. A fill that keeps
    two orders must respect each chain's nesting, so it is an empty cell. On a full grid there is none.
  - *(ii)* A subdivision adds a column.
  - *(iii)* Each empty cell of the new column is the median of p, x and y. The three middle knots pin it on every state, so it is a
    fill and keeps two orders.
  - Because (i) applies after the subdivision too (still complete bipartite), these are the only fills.
- **N4 (from any line, a full grid before the first subdivision).**
  - The line runs along a monotone path P in the grid of any two-chain cover.
  - For a minimal empty cell r = (i, j) below P (in the order i ≤ i′, j ≥ j′), its neighbours x = (i − 1, j) and y = (i, j + 1)
    and its corner c = (i − 1, j + 1) are on P or below it. P's cells in column i − 1 are no higher than its lowest in column i, and
    every cell below P is smaller than r, so all three are occupied.
  - The corner fill {B(x, r, y), B(c, x, r), B(c, y, r)} pins r to its cell on every state.
  - Column 0 has no cell below P.
  - When the crossing graph is disconnected the argument applies to each cover. A fill exists while any cover's grid has an empty
    cell, and n is bounded, so NNF ends at a full grid.
- **N5 (CC).** The corner fill keeps two orders. From a full grid it refills a new column outward from p, since the corner's two
  splits cross: the four quadrants hold c, q, x and the old (i′, j₀ + 2). On a line nothing crosses, so CC never fills.
- **N6 (an uncrossed split stays uncrossed under CC; proved after the read-out).**
  - A corner fill r agrees with c off t₁ and t₂. An uncrossed t is neither. For every split s, r lands in a quadrant of (t, s) that
    is already occupied, by c, or by x or y, which share c's side of t.
  - A full grid has no uncrossed split, so a first fill that misses a step of the line rules out every full grid.
  - A first fill spanning the line gives K_{c, m − c}, and N4's corner then has crossing splits.
  - The proof is sound. Being post hoc (the coordinator's question) changes only its standing as a prediction: P8 was frozen, and N6
    explains its 31 of 200 exactly, with expected rates 0.30, 0.20, 0.14 and 0.11.
- **The reimplementation (`referee_nest.py`).** The referee's NN uses its MEET-ORDERS-R1 options (knot-local, irredundant, 1 to 3
  knots, uniform over knot sets). Its subdivision is a single knot B(u, p, v) on a co-knotted pair one split apart. The order count
  is its KNOT-CAP-R1 `measure`. NNF is the same with all pairs, uniform over distinct extensions.

  | Run (seed 1) | Two orders every step | First full grid | Subdivisions before it | Every later subdivision at a full grid | Fill fraction, steps 21–40 |
  | --- | --- | --- | --- | --- | --- |
  | NN, five (2 bracketings) | yes, yes | 9, 9 | 0, 0 | yes, yes | 0.80, 0.80 |
  | NN, six (2) | yes, yes | 12, 12 | 0, 0 | yes, yes | 0.80, 0.80 |
  | NN, seven (2) | yes, yes | 15, 15 | 0, 0 | yes, yes | 0.80, 0.80 |
  | NN, eight (2) | yes, yes | 20, 20 | 0, 0 | yes, yes | 0.80, 0.80 |
  | NNF, five to eight (to n = 32) | yes | 8, 12, 15, 18 | 0 | yes | — |

  - These agree with the study: median fill 0.80, and NNF's first full grids at 8, 12, 15 and 18, all in its stated sets.
  - These eight NN runs do not include the study's 13 runs with holes or its 4 without a full grid, which is expected at 8 of 254.

## 1. What is read and what is given (the coordinator's question)

- **"NNF reads only the states" is exact.**
  - Its candidate fills and subdivisions are read from the states on any pairs.
  - It decides between them by the order count (k and λ) of each candidate's extension, and that count is a function of the state
    set alone (its splits and their crossings).
  - It is a global reading: all splits at once. NN adds which pairs share a knot.
- **"The number two is given" is not quite all that is supplied.**
  - **The cap "at most two orders"** (A101).
  - **The fallback when no fill keeps two orders: a subdivision,** one knot on a pair one split apart. The cheapest rule would also
    allow pendants. The proofs N1 and N3 use the subdivision. NN2 (any cheapest step keeping two orders) behaves the same in the
    study's runs, so the fallback can be loosened, but NNF's proof is for the subdivision.
  - **A99's move set and uniform tie-breaking,** as for every rule in this line.
  - **A start that is a line,** from a bracketing.
- **The fix.** Write "given: the cap of two orders and the subdivision fallback". Cite NN2 for the fallback.
- **CC's "local".** CC reads two splits near one distinction and whether they cross. Whether two splits cross depends on all
  distinctions (their four quadrants), so CC is "reads two splits", not strictly local. This is a wording point.

## 2. Against LOCAL-ROOM and CUBE-DOUBLING (the coordinator's question)

- **LOCAL-ROOM.**
  - **The open point.** LOCAL-ROOM-R1 narrowed "two orders need a remembered distinction" to reach limits, and named a states-only
    rule that reads more as untested.
  - **NNF is such a rule, and it succeeds.** It holds two orders and fills them from any line, proved. So two orders do not need
    memory.
  - **What they do need** is a rule that reads the global order count and is told the cap.
  - The class law's per-split classes are read here from the crossings: on a full grid, the two sides of the complete bipartite
    crossing graph.
- **CUBE-DOUBLING.**
  - NNF is CUBE-DOUBLING's cheapest rule (A99, fills first) restricted to steps that leave at most two orders. Uncapped, the same
    rule makes every order (λ = d at n = 2^d, proved). The study's KF3 comparator reaches λ = 5 to 7 by n = 40.
  - **So the dimension two is wholly the cap's.**
  - "A law told to keep three would fill a three-way grid" is a conjecture here, untested.
  - This matches the referee's CUBIC-FROM-A-KNOT finding, where the law's arity set the three.
- **The plain reading for G1.**
  - "A law that grows two orders and keeps them, filled, forever exists. It reads only the states, and is told 'at most two orders'
    and to lengthen by a subdivision when no such fill exists. Nothing per split is handed over or remembered."
  - "It does not choose two."

## 3. Smaller points (Not a block)

- **NN is computed, not proved.**
  - The study's 13 runs with holes and 4 without a full grid by n = 40 stand.
  - The referee's eight runs had none.
  - The note says this.
- **The study's P1, P3 and P5 failures** are one finding: no starvation. They are reported honestly.

## Fixes for the thread (listed for the owner, not folded in)

1. **What is given.** The cap of two orders and the subdivision fallback, not only "the number two". Note that NN2 shows the
   fallback can be loosened. **Not a block.**
2. **The dimension.** Say that NNF is the cheapest rule capped at two orders. Uncapped, it goes to every order (CUBE-DOUBLING). The
   two is the cap's, and a three-way cap is untested. **Not a block.**
3. **LOCAL-ROOM.** Record that NNF settles its open point: a states-only rule reading the order count holds two orders and fills
   them. **Not a block.**
4. **CC's "local".** Write "reads two splits and whether they cross" instead. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proofs N1 to N6 and nnlib's rule definitions;
  - checked every proof by hand;
  - wrote its own NN and NNF (`referee_nest.py`) on its MEET-ORDERS-R1 and KNOT-CAP-R1 code, and ran twelve runs.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_nest.py`.**
- **`referee_nest_NN.json`:** eight NN runs to n = 40.
- **`referee_nest_NNF.json`:** four NNF runs to n = 32, from their traces.

Reproduce one run, from `research/NEVER-NEST-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_nest.py NN 6 0 1 40
```
