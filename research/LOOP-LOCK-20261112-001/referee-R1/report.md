# Referee report LOOP-LOCK-R1: which loops lock

**Verdict: Confirmed with fixes.** The loop rule and the overlap rules are correct, and the ring claim is now proved for every ring
length, not only to 60. Three corrections follow, none a block.

**The ring summary covers 15 of the 45 harmonies.** The after-run script read only the overlap arm's harmonies with at most 20 states,
but the note words its summary as if it were all of them. Over all 45:
- 4 lock rings of every length;
- 21 lock every ring whose length is not a multiple of a fixed number;
- 20 lock only finitely many lengths.

The note names 3, 7 and "others" respectively. Every odd ring locks for 14 harmonies, not 4.

**"Collective" is mostly a shorter loop in disguise.** The crossed pair contains a loop of 2 knots. The circulant is genuinely
collective at exactly one size, n = 2g − 1, and there for 6 of the 7 locking harmonies; I checked this beyond the frozen range.

Referee: the background referee thread, 2026-11-12. My code is `ref_rings.py` and `ref_overlap.py`, built on the referee's own
`ref_endless.py` and `ref_lib.py`; it does not import `loop_lib.py`, `endless_lib.py` or `nest_lib.py`. Validation: V2. The advisor
model was not consulted for this job; its earlier answer on the known mathematics, in ENDLESS-BLOCK-R1, covers it.

## 1. The rule and the overlap rules

- **L1 (a closed chain of k knots locks exactly when k < g).** Correct, as proved in ENDLESS-BLOCK-R1: a loop is a closed walk of a
  reflexive step relation. My transfer computation for loops of 2 to 48 knots, on all 45 harmonies, and direct SAT agree.
- **L2 (an open chain is free at every length exactly when the step relation has a step).** Correct: copies can differ by one step
  and otherwise stay put. ENDLESS-BLOCK-R1 also shows that no tie arises at any distance.
- **L3 (one-orbit girth is the shortest zero sum of the step offsets).** Correct. The step relation is a Cayley digraph on Z_P. For
  one offset d the girth is P / gcd(d, P): 8, 12 and 16 for 00101101, 001010110101 and 0010101011010101. For 0010011011,
  D = {1, 4, 7}: no three offsets sum to 0 mod 10, but four do (1 + 1 + 1 + 7), so g = 4. Every other harmony has g = 2.
- **Figure eights and thetas: the advisor's rules hold (checked by hand; I did not recompute the 150 cells).** A shared copy can take
  any state, since R holds the diagonal, so figure eights are independent. In a theta, the only consistently oriented cycles are the
  two loops themselves. If loop A locks, its two shared copies are equal, and B's return path becomes a closed walk of b₂ steps.
  If A does not lock, padding A's return path gives B a non-constant state. So the theta locks exactly when g > max(1 + b₁, b₂), and
  never collectively.

## 2. The coordinator's questions

### Q2. Is collective locking real, or a relabelled shorter loop?

Mostly a relabelled loop.

**The crossed pair.** Loop 1 runs x → y in one knot and back in three. Loop 2 runs x → y in three knots and back in one. Each loop
has 4 knots, so each fails alone when g = 4. But the two one-knot halves make a consistently oriented loop of 2 knots, x → y → x.
A 2-knot loop locks x and y by L1, since 2 < 4. Once x and y are equal, each three-knot half becomes a closed walk of 3 steps, and
3 < 4 locks it too. The lock I measured on both g = 4 harmonies is therefore L1 applied to a 2-knot loop, not a collective effect.

**The circulants (n copies, steps +1 and +2).** The shortest consistently oriented loop has ⌈n/2⌉ knots. I checked every n from 3 to
2g + 1 by SAT, as far as size allowed:

| Harmony | g | Locks at n | Strict at 2g − 1 |
| --- | --- | --- | --- |
| 00101101 | 8 | ≤ 15 | yes, n = 15 |
| 001010110101 | 12 | ≤ 23 | yes, n = 23 |
| 0010101011010101 | 16 | ≤ 31 | yes, n = 31 |
| 00100101101101 + 01 | 7 | ≤ 13 | yes, n = 13 |
| the four-orbit harmony | 8 | ≤ 15 | yes, n = 15 |
| 00101101 + 0011 | 4 | ≤ 7 | yes, n = 7 |
| 0010011011 | 4 | ≤ 6 | no |

For n ≤ 2g − 2, a loop shorter than g explains the lock. At n = 2g − 1 every loop has at least g knots, yet the pattern locks: that
is the one genuinely collective size. It occurs for 6 of the 7 harmonies, and fails for 0010011011, whose three offsets allow other
round trips. This confirms the advisor's prediction for the one-offset harmonies at n = 15, 23 and 31, which were outside the frozen
range. From n = 2g on, nothing locks.

### Q1. Is "locks at every size in residue classes" provable for every n? What does "locks" mean on a ring?

Yes, it is provable for every n.

- **The setup.** A ring of n knots (j, j + 1, j + 2) is a closed walk of length n in the pair transfer. Its vertices are pairs
  (x_j, x_(j+1)) of states, with an edge (u, v) → (v, w) when R(u, v, w) holds.
- **What "locks" means.** All copies equal at every place, in every state. That is, every closed walk of length n stays on the
  diagonal. This is the same meaning as for loops.
- **The cases, from strongly connected components and their periods** (`result_rings.json`):
  - **No component off the diagonal has a cycle** (01, 0010011011, 00101101 + 0011, and the three-orbit harmony 00010001110111 +
    00011001110011 + 01). Then no closed walk can leave the diagonal, so the ring locks at every n.
  - **Every component off the diagonal has a period d > 1, and none touches the diagonal** (21 harmonies). In a component of period
    d, every closed walk has length a multiple of d, by the definition of the period. So the ring locks at every n that is not a
    multiple of any of these d. I also certified that every multiple of d occurs, from the smallest on: each component's walk lengths
    through one vertex form a numerical semigroup in dℤ that is full early. So the ring locks exactly when no d divides n, at every n.
  - **Some component has period 1** (20 harmonies). Then all large n unlock, and the finitely many lengths that lock are computed
    exactly.
- **The 21 harmonies with residue classes:**

  | Period | Rings that lock | Harmonies |
  | --- | --- | --- |
  | 2 | every odd length | 14 harmonies |
  | 4 | not a multiple of 4 | 0011 |
  | 7 | not a multiple of 7 | the three-orbit harmony of period 14 with 00100101101101 |
  | 8 | not a multiple of 8 | 00001111; 00101101 + 01 |
  | 12 | not a multiple of 12 | 000000111111; a three-orbit harmony of period 12 |
  | 2, 3, 6 | coprime to 6 | 000111 + 0011 + 01 |

- **Where the note and the census agree.** Their after-run lists to 60 match mine on every harmony they covered.
- **The note's wording.** "Others lock at finitely many lengths only" and "four harmonies every odd length" are statements about 15
  harmonies, not 45.
- **A weaker tie the frozen census also saw.** For a period-2 harmony on an even ring, the copies at even distance from the root are
  tied to it and the others are not. The proof's "half or less of each even one" is this partial tie. It is not a lock.

### Q3. Is a ring that locks at every size just the harmony's own periodicity restated?

In part.

- **What the extra states are.** For 40 of the 45 harmonies, every off-diagonal pair on a cycle of the pair transfer is a shear,
  (u, σ^c u); for the 4 that always lock this holds vacuously. So the only states besides "all copies equal" are copies stepped
  along the ring by shears.
- **When a shear is admissible.** A shear satisfies kind (a, b) exactly when u is not-all-equal at the offsets (0, a + c, b + 2c).
  Which shears pass is a property of the harmony's kinds, and is not settled by definition.
- **When a shear closes.** A shear closes around a ring of n copies exactly when n·c is a multiple of u's period.
- **The two kinds of residue class.** With one slope c used throughout, the class is "n a multiple of the order of c in Z_P": slope 1
  of order 4 for 0011, slope 3 of order 8 for 00001111, slope 5 of order 12 for 000000111111, slope 6 of order 7 for the period-14
  three-orbit harmony. For the 14 harmonies with period 2, every off-diagonal cycle has even length. For 00101101 the slopes alternate +3
  and −3, so copies alternate between u and σ^3 u, which needs an even ring; others mix several slopes, but still return only after
  an even number of steps. So every odd ring locks.

Given the admissible shears, the arithmetic is the period. Which shears are admissible is the computed content. The mechanism itself
is classical: periodic points of a shift of finite type, and the cyclic periods of its components (Lind and Marcus).

### Q4. Frozen against after-run

- **Frozen:** L1 and L2 on 495 cells each, figure eights and thetas, the crossed pair, circulants at n = 5, 7 and 9, rings to 12, and
  the nestings.
- **After the run, labelled so in the note:** the ring lengths to 60.
- **Not labelled as after-run:** the answer's bullet "Rings of overlapping knots lock by arithmetic (exact)" is frozen only to 12; the
  residue-class reading is the after-run part. "Bounded by the period, or at every size?" is labelled after the run.

## 3. Fixes for the thread

1. **The ring summary.** State its scope (15 harmonies of the overlap arm with at most 20 states), or replace it with the full count:
   4 lock at every length, 21 in residue classes (14 at every odd length), 20 at finitely many. Say the residue classes are proved for
   every n by the component periods, not just computed to 60. **Narrowing** (Overreading: the summary reads as covering all
   harmonies).
2. **"Collective."** The crossed pair contains a 2-knot loop, so its lock is L1, not collective. The circulant is genuinely
   collective only at n = 2g − 1: for 6 of the 7 harmonies, including the one-offset ones at 15, 23 and 31, and not for 0010011011.
   The owner's words "loops sharing two patterns can lock each other even when neither would alone" should say this. **Narrowing**.
3. **Ring wording.** Mark the residue-class reading as after-run in the answer's ring bullet, and distinguish the partial ties on even
   rings from locks. **Not a block**.

## Files

`brief.md`. `ref_rings.py` writes `result_rings.json`: the pair transfer, components, periods, shears, lock lengths to 120, and the
certificates. `ref_overlap.py` writes `result_overlap.json`: the crossed pair and the circulants by SAT. Not recomputed here: the
495 + 495 rule cells and the 150 figure-eight and theta cells (the rules are checked by hand above), and the drawn nestings.
