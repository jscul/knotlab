# Referee report ENDLESS-BLOCK-R1: endless blocks

**Verdict: Confirmed with fixes. The headline needs a substantial narrowing.**

What reproduces:
- every count, including the 1,376 loop ties in 17 cells;
- the same 7 harmonies.

What changes is how far the loop lock reaches:
- **The lock holds only on short loops, for every one of the seven harmonies.** Each harmony locks the copies on a closed loop only
  while the loop has fewer knots than a bound, the girth below. The girths are 4, 4, 7, 8, 8, 12 and 16 knots. At that length and
  beyond, the lock is gone entirely: the root copy is tied to no copy on the loop.
- **So the frozen range could not see the bound.** The record tested loops of 3, 4 and 6 knots only. It reads five harmonies as
  locking "at 3, 4 and 6" and two as locking "only short loops". In fact all seven lock only short loops, with a bound at or below the
  harmony's period.
- **The open-chain side is now proved for every length.** No open chain ties copies, at any length: the nine-fold unrolling was a
  sample of a theorem.
- **The mathematics is the standard one.** A configuration on a cycle is a closed walk in the one-knot transfer graph. On a chain it
  is an open walk.

Referee: the background referee thread, 2026-11-12. The code is `ref_endless.py`, built on the referee's `ref_lib.py` from the
BASES-WITHIN referee folder. It imports neither `endless_lib.py`, `nest_lib.py` nor `check.py`. My harmonies carry the same kind sets
as the frozen ones. The one-order arm is computed two independent ways: exactly by transfer matrices over the harmony's states, and by
direct SAT on the substituted closed chains. Validation: V2. The advisor model was consulted once on the known mathematics (section 5).

## 1. Every order and lagged (E1, E2): confirmed

- **E1.** On the closed chain of 3 and the chain of 4, the nested base has exactly the harmony's states for all 40 harmonies with at
  most 40 states. The proof holds: a harmony has no spare distinction, so the pinning theorem locks every copy.
- **E2.** On the closed chain of 3 with a lag s on one member, s = 0 to P − 1, the states are exactly those fixed by the shift by
  gcd(P, s) in all 432 cells checked, and the base lives exactly when that set is nonempty. Lags are twists by shifts, so this is the
  twisted-pin lemma.
- **The post-freeze lemma, "no loop-length effect under lags", is correct and correctly labelled.** Suppose a move changes a set D that
  meets every knot at most once. Flipping one place p of D alone then keeps every knot through p satisfied, because the other members
  of that knot are unchanged, so p would be spare. A harmony has no spare distinction, so it has no moves, and the k-move rule reduces
  to t∘h = t.

## 2. One order: the record reproduces

- **R contains the diagonal.** Each copy's own kinds make three equal copies allowed. So every pattern lives, and no tie inside a copy
  goes beyond the harmony's own (P3).
- **A single knot ties copies only for the alternation 01,** between its first two members (slots 0 and 1). No harmony ties the two
  loop members of a knot (slots 0 and 2).
- **The 7 locking harmonies are the record's 7.** On the closed chains of 3, 4 and 6 knots there are 17 cells and 1,376 ties, exactly
  the record's count.
- **State counts agree.** For example, 00101101 has 216, 648 and 5,832 states on closed chains of 3, 4 and 6, which is 8 · 3^k.
- **Direct SAT agrees with the transfer matrices.** I checked all 7 locking harmonies, at loop lengths 3, girth − 1, girth and
  girth + 1: 28 cells in all. The SAT root ties sit exactly where the transfer computation says the loop is locked or unlocked:
  - at 3 and at girth − 1, place 0 of x_0 equals place 0 of x_1 and is opposite to the half-period place;
  - at the girth and beyond, there are no ties at all.

  State counts agree wherever they are small enough to enumerate (11 cells). For 00101101, 216 states at 3 knots and 17,496 at 7.
  At 8 knots the transfer count is 52,496 = 8 · 3^8 + 8: eight winding states appear at the girth. Details are in
  `result_sat.json`.

## 3. The lock holds only below the girth (new, exact)

Take the closed chain of k knots, with copies x_0, …, x_(k−1) on the loop; x_i sits in slot 0 and x_(i+1) in slot 2 of knot i, with
a pendant copy in slot 1.
- **The transfer graph.** Let A(u, w) hold when some pendant state v makes (u, v, w) allowed. The loop's states are then the closed
  walks of length k in A, weighted by the pendants: trace(M^k), where M counts pendants.
- **When the loop locks.** A contains the diagonal. So all copies on the loop are forced equal exactly when k is less than the
  shortest closed walk that takes at least one non-diagonal step: the girth of A without its loops.
- **Every girth is finite and at most P, for all 45 harmonies (computed).** A is shift-equivariant, so when a step u → σ^d u stays
  inside one orbit it can be repeated, and P / gcd(d, P) repeats return to u. In general the bound needs such a step. If every step
  went between orbits, along an acyclic order of orbits, every loop would lock (the advisor's point: then A's closure is a partial
  order). None of the 45 harmonies does that. So for these bindings a long enough loop always unlocks.

| Harmony (orbits) | P | Girth | Loops that lock (knots) | Ties of the root with any loop copy at the girth |
| --- | --- | --- | --- | --- |
| 00101101 | 8 | 8 | 2 to 7 | none |
| 0010011011 | 10 | 4 | 2, 3 | none |
| 00101101 + 0011 | 8 | 4 | 2, 3 | none |
| 00100101101101 + 01 | 14 | 7 | 2 to 6 | none |
| the four-orbit harmony of period 16 | 16 | 8 | 2 to 7 | none |
| 001010110101 | 12 | 12 | 2 to 11 | none |
| 0010101011010101 | 16 | 16 | 2 to 15 | none |

- **The unlock is complete, at every length from the girth g on (proved).** At k = g the root is tied to no copy on the loop
  (computed). For k ≥ g and any loop position j, choose j0 between max(1, g − k + j) and min(j, g − 1). Then
  A^j ⊇ A^(j0) and A^(k−j) ⊇ A^(g−j0), since A contains the diagonal. So the pairs allowed at (k, j) contain those at (g, j0), and
  ties can only disappear. The transfer computation agrees: from the girth to 48 knots, no loop locks. Locking is all or nothing in
  the loop's length.
- **The mechanism.** Consecutive copies may sit at offsets that differ by an allowed step. Around a loop the steps must add up to a
  whole turn. A loop shorter than the girth has no room for that, so every step must be zero.

## 4. The coordinator's questions

**1. Is "cycle-born" real, or built in? Is the nine-fold unrolling a fair certificate?**
- **Open chains: no tie at any length (proved).** On an open chain the root and a spine copy d knots away range over A^d. Every
  partial state extends, by copying, since A contains the diagonal. And A^d ⊇ A^(d−1) ⊇ … ⊇ A. So a relation forced at distance d is
  forced at distance 1. No harmony forces one between the two loop members of a knot. So no open chain of any length ties the copies,
  and the nine-fold unrolling is an instance of this.
- **The lock is real, and it needs the whole loop.** No proper part of the loop forces anything, because each part is an open chain.
  The closing knot adds one more step. What forces equality is the joint condition that k steps return to the start.
- **How much is the closing knot alone, and how much the whole loop.** The answer is quantitative: the lock exists only while the
  loop is shorter than the girth, at most P knots. It is a short-loop condition, like a winding that cannot fit, not a reach that grows
  with the loop.
- **What is built in.** The stitch uses the harmony's own kinds, so A is shift-equivariant. That is why the girth is at most P, and
  why every long loop unlocks. The record's sceptic paragraph (a consistency condition on offsets around the loop) is right. It should
  add that long enough loops always unlock.

**2. Is this known mathematics under another name?** Yes. These names fit:
- configurations on a cycle of length k are closed walks of length k in a transfer graph, counted by the trace of its k-th power: the
  periodic points of a shift of finite type (Lind and Marcus, *Symbolic Dynamics and Coding*);
- the chain is the cycle's universal cover, and the gap between solutions on a structure and on its tree unfolding is the gap that
  arc consistency and tree duality measure (Feder and Vardi);
- path consistency on cycles in constraint networks (Montanari 1974; Mackworth 1977);
- for shift-equivariant steps, a winding or holonomy condition, as in Z_P clock models and voltage graphs (Gross and Tucker).

More precisely, in the advisor's words (checked here): the states on the loop are the homomorphisms from the directed k-cycle to the
reflexive digraph (W, A) (Hell and Nešetřil, *Graphs and Homomorphisms*), and "every such homomorphism is constant iff k is below the
directed girth of A without its loops" is folklore, not a named theorem. Its limiting case, infinite girth, is antisymmetry. The
nearest setting is the homotopy theory of reflexive binary structures (Larose and Tardif). With A reflexive, arc consistency never
sees the lock; path consistency does.

Two caveats from the advisor, both checked:
- **Orientation.** The closed chains here are coherently oriented: knot i holds x_i in slot 0 and x_(i+1) in slot 2. A loop with
  reversed steps would never lock.
- **Above the girth.** The loop still restricts which pairs of states occur, but forces no tie, as proved in section 3.

What is new here is only the data: which harmonies' one-order stitch has a girth above 2, and what the girth is. "Prior work on such
loop-born phase locking was not found" should give way to these names.

**3. Frozen against after the run.**
- **Frozen:** E1 and E2 on every cell; the one-order census on the frozen range (loops of 3, 4 and 6 knots), with the 3k unrolling
  criterion; P3; P4, including the rings of 6 and 7.
- **After the run, and labelled so in the proof and the evidence table:** the nine-fold unrolling, and E2's "no loop-length effect".
- **Not labelled in the answer:** the answer bullet says "unrolled three or nine times" without saying that the nine is after the run.

## 5. Fixes for the thread

1. **The headline, the answer, "What it changes", the owner's words and the owner report.** Narrow "a whole loop can lock every copy
   on it into one state, which no open chain does" to: "a loop shorter than the harmony's girth (4 to 16 knots, at most its period)
   locks every copy on it; longer loops do not lock at all; no open chain ever ties". Replace "two of the seven lock only short loops"
   with "all seven lock only short loops", and give the bounds. **Narrowing** (Overreading: the frozen range of 3, 4 and 6 knots could
   not see the bound). The theory under test, influence born of a whole loop, stands, but bounded in loop length.
2. **The prior-work line.** Replace it with the known names in section 4 (closed walks, periodic points, tree duality, winding). This
   is a novelty classification: known mechanism, new instances. **Not a block.**
3. **Open chains.** Replace "robust to a nine-fold unrolling" with the proof that no open chain of any length ties copies.
   **Not a block** (strengthening).
4. **The answer bullet** "unrolled three or nine times" needs "nine after the run". **Not a block.**

## Files

`brief.md`; `ref_endless.py`, which writes:
- `result_one.json`: the transfer matrices for all 45 harmonies, loops of 2 to 48 knots;
- `result_sat.json`: the direct SAT cross-checks;
- `result_every.json`: E1 and E2.

The advisor's answer on the known mathematics is in `advisor_answer.json`.
