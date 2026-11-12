# Referee report LIMIT-ONLY-R1 (lean, as asked)

**Verdict: Confirmed with fixes: one Narrowing, four Not a block.**
- **Every number recomputes exactly.** My own code reproduced every number. It matches the census row by row on all 223,261 W
  families and on every count of E.
- **The gates and the L2 proofs are sound.**
- **The Narrowing is about what "the limit" is.** In a third of the families alive only in the limit, every self-holding
  definition passes its own three ends straight to a SELF call. There the finite patterns grow, each containing the one before, and
  their limit in the usual sense dies, as compactness says it must. The bottomless pattern lives only because it drops a knot that
  every later finite pattern carries.
  - **Under the usual limit,** 894 of the 1,341 live only in the limit. That is 37.5% of the dying families, not 56%, and 91% of
    the 894 are incomparable.
- **The logged correction went too far.** The first wording, "needs", was true. It follows from the definition by restriction, not
  from L1.

Referee: the background referee thread, 2026-11-12.
- **Code.** `ref_limit.py`, my own. It computes port relations by bitset algebra (checked against brute force on 300 random
  definitions), has its own orbit and cycle detection, and uses the sampler from SHORT-DESC-R1. It also checks expanded patterns
  with a SAT solver (CaDiCaL). It imports none of `dlang.py` or `census.py`.
- **Advisor.** The advisor model was not consulted.

## 1. What reproduces

| Item | Census | Referee |
| --- | --- | --- |
| E: families, all alive at every depth and in the limit | 516,880 | 516,880 (my own enumeration) |
| E: equal / up / incomparable | 82,670 / 430,106 / 4,104 | the same |
| E: L2 failures (fixed point outside / period above 1) | 1,320 (1,296 / 24) | the same |
| W: rows, compared one by one (fate, first death, period, after, limit, comparability, L1, L2, failure kind, limit kinds, bits) | 223,261 | 223,261, no mismatch |
| W: alive only in the limit; of the dying | 1,341; 56.3% of 2,381 | the same |
| W: down / incomparable / equal among them | 508 / 831 / 2 | the same |
| W: L2 failures among incomparable | 310 of 2,440 (193 / 117) | the same |
| L1 exceptions; L2 failures where knot and image compare | 0; 0 | 0; 0 |
| Families with no K in the bottomless pattern | 10 | 10 |

**SAT on expanded patterns** (independent of every port relation):
- **Families alive only in the limit.** Each is alive at the depth before its first death (1,319 checked) and dead at its first
  death and the depth after (2,680 checked). Its bottomless truncations, with SELF at the bottom dropped, are alive (6,353 checked).
- **L2 failures.** Each is alive at every depth through its cycle: 1,376 depths in W and 5,904 in E.
- **The cap.** Seventeen patterns were over the cap of 60,000 knots and were not checked.

**E's "never dies" is exact.** The map on tuples of relations is a function on a finite set. Every orbit is read until it returns to
a tuple already seen, and every depth in its cycle is checked. The 1,340 families that "stay dead" have no living depth anywhere after
their first death, in the tail or in the cycle. So "all but one stay dead at every depth after" holds.

## 2. The limit notion (the coordinator's main point)

**What the census computes is sound for the object it defines.** The bottomless pattern replaces every SELF forever. Its finite
parts lie in its truncations, with SELF at the bottom dropped, so by compactness it lives iff the iteration from TOP (a decreasing
chain) ends in a fixed point with a living main relation. The finite depths are not finite parts of the bottomless pattern: they
carry knots at the bottom that it lacks. So "dead at every finite depth, alive in the bottomless pattern" does not contradict
compactness.

**What compactness does give** (0 violations in E and W): if the bottomless pattern dies, the family dies at every depth from some
depth on. So a family alive at infinitely many depths has a living bottomless pattern. That is slightly more than the note's
"alive at every depth".

**But the bottomless pattern is not always the limit of the finite patterns.** Name each distinction by the copy that makes it.
- **The usual limit.** The limit of the depth-t patterns, in the usual sense, keeps the knots present at all but finitely many
  depths.
- **Without a pass-through call,** a bottom knot sits on distinctions made at its own depth, so it appears in one finite pattern
  only. The usual limit is then exactly the bottomless pattern, and the cell is genuine.
- **With a pass-through call,** a self-holding definition has a SELF call on its own three ends, in any order. Then the bottom knot on
  each copy's ends returns at every later depth. So the usual limit is the bottomless pattern with the knot on the ends of every copy
  of such a definition.
- **When every self-holding definition passes through,** each finite pattern contains the one before it. Their union dies as soon as
  one depth dies, by compactness: exactly the coordinator's worry.

| Families alive only in the bottomless pattern (W) | Count | Usual limit lives | Down |
| --- | --- | --- | --- |
| no self-holding definition passes through | 821 | 821 | 72 |
| some do | 114 | 73 | 33 |
| all do | 406 | 0 | 403 |
| **total** | **1,341** | **894** | 508 |

These counts are computed by the greatest fixed point with the extra knots, and every dead verdict is confirmed by SAT: 447 of 447.
Living verdicts are confirmed by SAT through the depth the orbit was read plus two (799 checked, 95 over the cap).

**What changes.**
- **The size of the cell.** Under the usual limit, 894 families live only in the limit: 0.40% of W, and 37.5% of the 2,381 dying
  families. P4 held as frozen, because it was frozen with the bottomless reading. Under the usual limit it would not, since 37.5% is
  below half.
- **What the families are.**
  - The cut-off cell is almost entirely incomparable: 813 of 894 (91%). Of the 508 down families, 427 (84%) are pass-through
    artefacts.
  - All 10 families with no K are pass-through, so in the genuine cell every bottomless pattern holds knots.
  - Of the genuine families' limit relations, 95% are free.
- **The Reading.** "The death belongs to the cut-off, not to the pattern" holds for the 894. It does not hold for the 447. There the
  bottom knot is not at a cut-off: it sits on the same three distinctions at every later depth.

## 3. The proofs

**L1 is sound.**
- **The argument.** If every limit relation G lies inside the knot, then G = Φ^t(G) ⊆ Φ^t(knot) by monotonicity, so every depth
  lives.
- **The all-equal state.** Every relation here is closed under flipping all distinctions, so G holds 000 iff it holds 111, and the
  test on 000 alone is right.

**The note's first wording ("needs") was true.** Take a family dead at depth t and any state of the bottomless pattern. Restrict it
to the copies above nesting level t. If every self-holding copy at level t had ends not all equal, the restriction would satisfy the
depth-t pattern. So every state of the bottomless pattern has, at every dead depth t, some copy at level t with its three ends all
equal. For the 1,340 that stay dead, that is at every level from the first death on. L1 gives only "allows" for the limit relation.
The stronger statement holds by this restriction, so the logged correction's "Wrong" is itself too strong.

**L2 is sound where claimed.**
- **The easy direction.** main(P) non-empty gives life at every depth (P ⊆ Φ^t(P) ⊆ Φ^t(knot)). So L2 can fail only one way: alive at
  every depth with main(P) empty. All failures are of that way.
- **Up.** P is the knot and the depths widen.
- **Down.** X ↦ knot ∧ Φ(X) from the knot is the orbit itself, which descends to P.

**The two failure kinds are one mechanism.** In every failure (310 in W, 1,320 in E) the orbit's cycle leaves the knot: some
relation in it holds the all-equal state. This is proved. If a cycle lay inside the knot, the union of its relations would be a
post-fixed point inside the knot, so P would contain it and main(P) would be non-empty. "Fixed point outside the knot" is the
period-1 case of this, and "period above 1" is the rest.

## 4. Settled by the language and the class

- **The finite depths end in knots,** by definition. That is why they can die where the bottomless pattern does not.
- **E's conclusion 2 is mostly a first-step fact about small bodies.**
  - **Depth 1.** At most three knots always allow a state, because seven knots (the Fano plane) are the fewest that forbid every
    state.
  - **The first image.** It leaves out the all-equal state exactly when some call lies on the three ends, and it is then the knot
    itself. I checked this on all 516,880.
  - **What follows.** "Equal" means a call on the three ends; no family is down; up and equal families never die (proved). The
    computed part over depth is that the 4,104 incomparable families never die.
- **A pass-through definition's first image lies inside the knot,** because the knot is the same under any order of its ends.
  - **Families where all pass through** are therefore down or equal: 405 of 406. The exception is one through a self-holding
    definition that the main definition never reaches.
  - **Among the down families alive only in the bottomless pattern,** 436 of 508 (86%) have a pass-through call.

## 5. Known and new

**Known.**
- Compactness, Knaster–Tarski, and Park's coinduction (L1 is its one-line case).
- That iterating from a seed which is not a post-fixed point need not reach the greatest fixed point (Cousot and Cousot 1979).
- That a pattern built by self-reference can be read in two ways: by its finite approximations from a seed, or by its greatest
  fixed point, the infinite unfolding (Kozen; hyperedge-replacement grammars). The limit of an increasing chain dies with its finite
  parts.

**New.**
- The counts.
- The pass-through split, where the two readings part.
- The incomparable cell, which is where the genuine phenomenon lives.

**Proved and computed.**
- **Proved:** the gates, the failure mechanism, the restriction statement and the pass-through nesting.
- **Computed:** E and W, exactly per family.

## 6. Small points

- **"5% a knot again".**
  - Of the 79 knot limits, 72 are the holding knot itself, for one self-holding definition in a family with several.
  - The other 7 are a knot with one end flipped, which allows all-equal ends.
- **Conclusion 4.** The 2 "equal" families alive only in the limit are both pass-through. They die at once and are dead under the
  usual limit.

## Fixes for the thread

1. **What "the limit" is.**
   - Say that the bottomless pattern is the limit of the finite patterns only when no self-holding definition passes its own three
     ends to a SELF call.
   - Give the split: 821 with none, 114 with some, of which 73 still live under the usual limit, and 406 with all, which die under
     it, as compactness requires.
   - Report the genuine cell as 894 of 1,341: 37.5% of dying families, 91% incomparable. Note that P4 held only under the frozen
     bottomless reading.
   - Scope the Reading to the 894.

   **Narrowing.**
2. **"Needs" was true.** Every state of the bottomless pattern has all-equal ends at some self-holding copy on every dead level. This
   follows by restriction, not by L1. The logged correction should say that the claim stood and only its evidence was missing.
   **Not a block.**
3. **One failure mechanism.** In every L2 failure the orbit's cycle leaves the knot (proved), and L2 fails only one way. **Not a
   block.**
4. **Conclusion 2 is a first-step fact.** The first image leaves out all-equal ends exactly when a call lies on the three ends, and
   is then the knot. Only the 4,104 incomparable families needed iterating. **Not a block.**
5. **"A knot again".** It is mostly the holding knot itself (72 of 79). **Not a block.**

## Files

| Command | Output | What it does |
| --- | --- | --- |
| `ref_limit.py e W 8`, `ref_limit.py w W` | per-family rows (not kept: about 250 MB, regenerated in about a minute) | E and W recomputed; W compared row by row |
| `ref_limit.py summary` | `result_summary.json` | the counts |
| `ref_limit.py sat` | `result_sat.json` | SAT on expanded patterns |
| `ref_limit.py pt` | `result_pt.json` | the pass-through split, the usual limit, SAT on its truncations |

The SAT steps need the workspace's `.venv` Python (pysat).
