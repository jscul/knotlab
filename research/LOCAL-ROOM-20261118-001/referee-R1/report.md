# Referee report LOCAL-ROOM-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - R1 and R3 are correct.
  - R2's conclusion holds under every tie rule. The referee's own engine enumerated every reachable class to n = 33, so this is one
    doubling past the study's 100 runs to 16. But R2's proof leaves out a case (§1).
  - The exact reach-one distributions reproduce: the kinds and the class counts.
  - The class law reproduces in the referee's own implementation. It has two orders at every step of 200 of 200 runs and no stall,
    and every run passes a full grid after n = 9. A new split is never added before the grid is full.
- **What changes.**
  - **R2's proof** says "for s ≥ 3 only subdivisions are allowed". Under reach 2, pendants are allowed (8 of the 20 cheapest
    extensions of Q₃). The conclusion survives by the proof's own s = 2 bootstrap, applied at every s. **Not a block.**
  - **"Two orders need a remembered distinction"** is shown only against reach limits. A states-only rule that reads more than reach
    is not excluded. **Narrowing.**
  - **At reach one, "both orders keep growing" holds in most runs, not all.** In one two-order run in six, one order is still a
    single split at n = 20. The matching-based chain lengths count splits that cross nothing. **Not a block, wording.**
  - **The class law's "full grid beyond n = 9"** is now computed per run. It is not proved.

## What holds

- **R1 (proved).**
  - **The argument.** A zero-cost fill needs a consistent middle knot B(u, p, v), so A(u) ∩ A(v) = ∅. At reach 1, A(u) Δ A(v) is one
    split, so one of the A sets is empty and the target is a copy.
  - **Checked.** In the exact runs below, no reachable base at reach 1 has a free step: 0 of every class from both starts to n = 11
    and 10.
- **R3 (proved, for reach limits).**
  - **The argument.** A grid cell's fill uses pairs at reaches 1, 1 and 2. So does a line's F(a, c, b) on three consecutive
    distinctions. On a grid, that fill is the twisted corner: it makes two nested column splits cross, which is a third order.
  - **The limit of the proof.** A rule that reads only the pairs' disagreement counts cannot tell the two fills apart.
- **R2, under every tie rule (`referee_room.py r23`).**
  - **The run.** Every class reachable by LF3(2) and LF3(3), from one knot and from the 2 × 2 pattern. Classes are sets of
    orientations up to the cube's symmetries, and the run goes to n = 33.
  - **What it finds.** Q₂, Q₃, Q₄ and Q₅ come at 4, 8, 16 and 32, each the only class:
    - at r = 2 the classes number 46, 239 and 43 at n = 20, 24 and 28;
    - at r = 3 they number 58, 276 and 44.
  - **Matches.** The study's exact numbers reproduce, for instance 6 and 12 classes at n = 10 and 12 at r = 2.
- **Reach one, exact (`r1`).** The referee's engine merges bases up to renaming, by the distinction–state incidence (a WL hash, then
  VF2).
  - **From one knot**, from n = 5 to 11, every level has: a line 10/33, a branching tree 5/22, two orders 5/11, three orders 1/66.
    That is 30.3%, 22.7%, 45.5% and 1.5%, with 7, 12, …, 73 classes.
  - **From the 2 × 2 pattern**, from n = 6 to 10: two orders 137/156 and three orders 19/156 (87.8% and 12.2%), with 14, …, 272
    classes.
  - All of these equal the study's.
- **The kinds freeze run by run, not only in distribution (`runs1`, 300 seeded runs per start to n = 20).**
  - From one knot, no run changes kind after n = 5.
  - From the 2 × 2 pattern, the kinds freeze from n = 6: its first two steps can make a third order, in 48 runs.
  - The note's "from n = 5 on" is for one knot. For the 2 × 2 start the kinds are fixed from n = 6, which its table shows.
- **The class law (`class`, the referee's own implementation from the note's words).**
  - **The rules.**
    - Each split carries a class.
    - A knot's old pair may be separated only by splits of different classes.
    - No pendant.
    - A new split inherits the class of its restriction to the old distinctions.
  - **The result, from the 2 × 2 pattern, 200 seeded runs to n = 30.**
    - Two orders (k = λ = 2) at every step of every run, and no stall.
    - Every run has a full grid, (a + 1)(b + 1) = n, at some n > 9.
    - A new split is never added while the grid is not full: 0 times. So each row or column completes before the next starts.
    - Full grids at 12: 166 of 200, as in the study. At 30: 103 (the study had 100, with other seeds).

## 1. R2's proof omits the pendant class for s ≥ 3 (Not a block)

- **The proof's claim.** "A pendant needs B(v̄, v, p) at reach s, so for s ≥ 3 only subdivisions are allowed."
- **Why that is wrong.** A pendant only needs p forced to v on every split. It can be realised by several end knots B(u, v, p),
  each forcing p = v on the splits where u ≠ v. With up to three knots of reach 2, that covers up to six splits.
- **Checked.** Under r = 2, the cheapest extensions of Q₃ are 12 subdivisions and 8 pendants. Those of Q₄ are 32 and 16. So at
  every doubling the rule can take a pendant.
- **The repair.**
  - The pendant certificate works within reach 2 for a target (x, 1) whose x is next to c: the middle pair (c, 1)–(x, 0) differs on
    two splits, and the end pairs on one.
  - Every farther x has a filled neighbour (x′, 1) to play c's part. This is the proof's own argument for s = 2, and it needs
    nothing about s.
  - So R2 holds, and the exhaustive run confirms it through Q₅.
- **The fix.** Replace the sentence with the bootstrap for every s.

## 2. "Two orders need a remembered distinction between them" (Narrowing)

- **Where it is said.** The G1 position line and the owner's-terms paragraph ("What holds two orders and fills them is memory")
  read as a necessity.
- **What R3 covers.** Only rules that read the pairs' disagreement counts, that is reach limits.
- **What it does not cover.** Other states-only rules are not excluded. One example: a rule that reads the crossing graph of the
  splits, which the states determine.
  - On a full grid the crossing graph is complete bipartite, and its two sides are exactly the class law's two classes.
  - Whether such a rule can stand in for the remembered class during growth is untested. A new split may cross nothing at first, and
    then its side is not readable.
- **What is shown.** Reach limits cannot hold two orders and fill. One remembered class per split, handed over by the start, can.
  Whether a states-only rule beyond reach can is open (direction #3 is close to this question).
- **The fix.** Write "needs more than reach" rather than "needs memory".

## 3. Reach one: "two orders that keep growing" (the coordinator's question; Not a block, wording)

- **How the referee read the two orders.** By the crossing graph's two colour classes, which are canonical when the crossing graph
  is connected. That holds in all 131 two-order runs from one knot and all 252 from the 2 × 2 pattern.
- **Why not the matching.** The study's maximum matching also assigns the splits that cross nothing (about 1.4 at n = 6 rising to
  2.9 at n = 20), and it assigns them arbitrarily. So its "shorter chain" is inflated, and it depends on which matching is found.
- **What the colour classes show.**
  - **Crossings grow.** The median is 3, 10, 20 and 56 at n = 6, 10, 14 and 20 from one knot (44 at n = 20 from the 2 × 2 pattern).
  - **The shorter class grows on average:** a mean of 1.24, 2.02, 2.87 and 4.20.
  - **Not in every run.** At n = 20, 22 of 131 two-order runs from one knot still have a single split in the shorter class, and 21
    have two. From the 2 × 2 pattern, 9 of 252 have one. Those runs are a long chain crossed by one split: close to "a tree with one
    crossing".
- **The fair reading.** In most two-order runs both orders keep growing, unfilled. In about one in six from one knot, one order
  stays a single split.
- **The splits.** "n distinctions carry n − 1 splits" is right from one knot. From the 2 × 2 pattern it is n − 2.

## 4. The class law: how much is put in (the coordinator's question; compared with GRID-GROW)

- **What the law supplies.**
  - Two classes, given at the start: the 2 × 2 pattern's two splits.
  - A class for every new split, by inheritance.
  - A ban on knots joining two splits of one class. That is exactly the twisted corner, the only fill that makes a third order (R3).
  - A ban on pendants, which would make a split with no class.
- **So "two orders at every step" is close to built in.**
- **What is genuinely grown.**
  - It never stalls.
  - The cheapest growth completes each row before the next (computed, 0 exceptions).
  - Full grids recur, and their shapes vary widely: (3, 7), (4, 5) and (2, 9) at n = 30.
- **Against GRID-GROW's Block.** There the drawing supplied the placement the states lacked. Here the memory supplies which order a
  split belongs to. In both, the second order's identity is supplied, not read from the states.
- **"A full grid beyond n = 9".** It is held, and now computed per run (200 of 200). The study argued it from row completion. Row
  completion is itself computed, not proved. A proof would show that a partial row's cells are always fillable within the class
  rule, and that no other fill exists.

## Fixes for the thread (listed for the owner, not folded in)

1. **R2's proof.** Pendants are allowed at s ≥ 3 under reach 2. Use the s = 2 bootstrap for every s. **Not a block.**
2. **Necessity.** "Two orders need a remembered distinction" should read "need more than a reach limit". Name the crossing-graph
   reading as untested. **Narrowing.**
3. **Reach one.**
   - Say that in about one two-order run in six from one knot, one order stays a single split at n = 20.
   - Read the chains from the crossing graph's colours, not from a matching.
   - The 2 × 2 start has n − 2 splits.

   **Not a block.**
4. **The class law.** "Full grid beyond n = 9" and row completion are computed, not proved. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `locallib.py` (the reach filter, `class_extensions`, `carry_classes`),
    `posthoc.py` and the results;
  - checked R1 to R3 by hand;
  - wrote its own reach-limited extensions, exhaustive class enumeration, reach-one exact engine (incidence isomorphism), seeded
    runs with colour-class chains, and class law (`referee_room.py`), reusing its CUBE-DOUBLING-R1 and KNOT-CAP-R1 code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_room.py`**, with parts `r23`, `r1`, `runs1` and `class`.
- **Outputs:** `referee_room_<part>.json`.

Reproduce, from `research/LOCAL-ROOM-20261118-001/referee-R1/`:

```sh
for P in r23 r1 runs1 class; do ../../../.venv/bin/python -B referee_room.py $P > referee_room_$P.json; done
```
