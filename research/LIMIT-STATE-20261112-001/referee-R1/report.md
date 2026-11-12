# Referee report LIMIT-STATE-R1 (lean, as asked)

**Verdict: Confirmed with fixes: one Narrowing, two Not a block.**

**Every number recomputes exactly.** My own expansion, CNF and cardinality encoding reproduce the census exactly.

**"Must spread" is almost entirely settled by the definition.** The restriction lemma holds inside every copy, not only at the top.
- **Where the bound forces two witnesses.** In 788 of the 800 branching families it forces two or more witnesses at some depth from
  T to T+2. In 767 of them that happens already at T+1, where every copy made at the first level needs its own witness.
- **One-definition families.** This holds in all 596 of them.
- **What is left to measure.** P1 and P2 are measured only on the 12 families the bound leaves open: 3 allow single and 2 a single
  ray.

**Exactly one witness at depth T alone** is possible in 417 of the 800.

Referee: the background referee thread, 2026-11-12.
- **Code.** `ref_state.py`, my own. It uses LIMIT-ONLY-R1's bitset relations for the usual limit, its own expansion with copy
  tracking, its own CNF, the ladder encoding for exactly one and the sequential counter for at most k. It imports none of
  `dlang.py` or `census.py`.
- **Advisor.** The advisor model was not consulted.

## 1. What reproduces

| Item | Census | Referee |
| --- | --- | --- |
| Genuine families (usual limit) | 894 | 894 |
| Loose | 87.4% | 781 of 894 (87.4%) |
| Limit relations: free / knot / three tied | 921 / 101 / 2 | the same |
| Read; over 60,000 knots; recurrent | 801; 92; 1 | the same |
| Gate failures (lemma at T..T+2, finite part alive) | 0 | 0 |
| Chains; branching | 1; 800 | 1; 800 |
| Single; single ray (branching) | 3; 2 | 3; 2 |
| Single among loose branching | 0 of 702 | 0 of 702 |
| Median calls at T, T+1, T+2 | 64, 256, 1,296 | the same |

**The depth indexing is right.** "Calls of depth t" are the SELF calls made from copies at level t − 1. A call through another
definition keeps its caller's level. That is exactly the set of bottom knots of the depth-t pattern, which is what the lemma needs.

**The parent links are right.** A call's parent is the SELF call that made its enclosing copy, carried unchanged through calls to
other definitions. My independent construction gives the same single-ray verdicts.

**The gates are implied.** The lemma's check follows because the depth-t pattern is a part of the constrained system. The finite
part's life follows from genuineness, at the fixed point. So both are code checks, as the pre-registration says.

**The pass-through split difference is detection.** The census marks a family when any definition has a pass-through call; I
marked it only when a definition the main definition reaches has one. Exactly 9 genuine families have a pass-through call only in an
unreachable definition: 82 − 9 = 73. Nothing else depends on it, since an unreachable definition changes neither G nor the pattern.

## 2. The copy bound: "must spread" by construction

**The lemma, applied inside each copy.** If a self-holding definition i, read as its own family (`defs[:i+1]`), is dead at depth s,
then every copy of i made by a SELF call at level j holds a witness among the calls of depth j + s inside it, in every living state.
- **Proof.** Impose not-all-equal on those calls. The copy then holds definition i's depth-s pattern, which allows no state, whatever
  the copy's ends are.
- **The bound.** Copies made by SELF calls at one level are disjoint, so depth t needs at least B(t) witnesses: the largest number,
  over levels j, of level-j copies of definitions dead at depth t − j.
- **One definition.** For a one-definition family whose definition makes c SELF calls, B(T + j) = c^j: one witness per level-j copy.
  That is a fixed share c^−T of the calls at every depth, by construction.

| Branching families (800) | Count | Single possible |
| --- | --- | --- |
| B ≥ 2 at some depth T..T+2 (single impossible by the bound) | 788 | 0 |
| of which already at T+1 | 767 | 0 |
| of which one-definition families | 596 (all of them) | 0 |
| B = 1 at all three depths (the only measured cases) | 12 | 3 (single ray: 2) |

**Depth T alone.** Exactly one witness at depth T alone is possible in 417 of 800. That includes 309 of the 596 one-definition
families. Exactly one at T+1 alone is possible in only 6, and at T+2 alone in only 3. So "exactly one per depth" mostly fails at
T+1, where the bound first exceeds one. That is the thread's question answered.

**Is the bound reached?**
- **By depth.** Separately at each depth, at most B(t) witnesses suffice in 417 of 800 at T, 156 of 800 at T+1 and 58 of 796 at
  T+2 (4 were too large to query).
- **What that means.** The floor is set by construction. How far above it the least number of witnesses lies is the measurable part.

**What this changes.**
- **The Answer and the Reading.** "Every living state spreads the all-equal state over two or more knots" and "needs it in several
  of its inner parts at once" follow from the definition in 788 of 800 families. Each inner copy holds the whole dying family, so each
  needs its own witness.
- **P1 and P2 failed as frozen.** Their failure measures the language's self-similarity, not a property found in the states.
- **The 0 of 702 loose families.** The bound leaves single open in only 1 of them, and that one does not allow it.
- **Direction #1.** It asks whether the least number of witnesses per depth is "a constant, a fixed share, or growth". For
  one-definition families a constant is excluded and a share of at least c^−T is guaranteed, both by construction. It should measure
  the excess over B(t) instead.

## 3. Settled, known and new

**Settled by definition.**
- The finite part's states are the limit's restrictions (the fixed point).
- The gates.
- Loose, which the pre-registration already says.
- Chains.
- The copy bound, and with it P1 and P2 in 788 of 800.

**Known.**
- Compactness and fixed points.
- That self-similar instances inherit every constraint of the whole at each copy, the standard reading of hyperedge-replacement
  families.

**New.**
- The counts.
- The 12 families the bound leaves open.
- How far the least number of witnesses exceeds the bound.

**Proved:** the copy bound. **Computed:** the queries, which are exact per family.

## Fixes for the thread

1. **"Must spread" is settled by the definition in 788 of 800.**
   - State the copy bound and its one-line proof: the lemma applies inside every copy, so depth T + j needs a witness in every
     level-j copy of a definition dead at depth T.
   - Say that P1 and P2 are measured only on the 12 families where the bound is one at every depth read: 3 allow single, and 2 a
     single ray.
   - Say that one witness at depth T alone is possible in 417 of 800.
   - Reword the Answer and the Reading to say the spread comes from each copy holding the whole dying family.
   - Re-aim direction #1 at the excess over the bound. For one-definition families the bound already gives a fixed share c^−T of
     the calls.

   **Narrowing** (settled by construction).
2. **The pass-through split.** The difference is 9 families whose only pass-through call is in an unreachable definition. Say so, or
   detect only reachable definitions. **Not a block.**
3. **The gates are code checks.** Implied by the lemma and genuineness, as the pre-registration labels them. **Not a block.**

## Files

| Command | Output | What it does |
| --- | --- | --- |
| `ref_state.py run W 10` | `result_*.jsonl` | every family: the usual limit, the queries, the copy bound and whether it is reached |
| `ref_state.py summary` | `result_summary.json` | the counts |

Run with the workspace's `.venv` Python (pysat). The first unit ran out of memory on the totalizer encoding at 46,656 calls. The
rerun uses linear encodings, about 11 minutes on 10 workers.
