# Referee report DISTANCE-ORDER-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - All seven statements of Proof A are correct. Statement 3(b), with its recovery of N, is proved for every n ≥ 4, not only
    decoded on the sizes checked.
  - Every number of ticket B recomputes with the referee's own code, the weave's exact counts included (own transfer matrix, own
    Chinese-remainder moduli).
  - The freeze preceded the results.
- **The fix.** "With cycles they split" is what one strict reading (A98's exact additive betweenness) finds on two cyclic bases. It
  is not a property of cycles. Under the weakest order-only reading, the disagreement count does carry a local order on the weave.
  The same reading also shows why it is not the weave's own steps.

## What holds

- **Order.** The freeze, `9becfe4b8`, is at 18:36:24 UTC.
  - **The run came after it.** The run's artifact directory was created at 18:36:33 and `results.json` written at 18:38:49. `order.py`
    and `run.py` are unchanged from the freeze to HEAD.
  - **The predictions** were committed before any result existed.
  - **Post-freeze changes.** Only `check.py`'s result format (a status field) and the knot-tree corollary, which is marked "Added at
    the close".
- **Statements 1, 2, 4, 5 and 6 (proved; Not a block).** The referee checked each proof line by line.
  - Statement 6's step "the triangle inequality in the other direction for the steps it skips" is sound. The chain's equalities
    telescope, d(o, v_l) = Σ d(v_t, v_(t+1)). The chain of inequalities d(o, v_l) ≤ d(o, v_i) + d(v_i, v_j) + d(v_j, v_l) ≤ that sum
    is then tight, which forces d(v_i, v_l) = d(v_i, v_j) + d(v_j, v_l).
  - It does not even need strictness.
- **Statement 3 (proved for every size; Not a block).**
  - **3(a).** Every complement-closed constraint on at most three places is a conjunction of the four named kinds. Each kind is read
    from the table and N. The base is the set of states satisfying every constraint that holds on it.
  - **3(b), the recovery of N** (the owner's item 1):
    - if the base is full, every count is 2^(n−1);
    - if not, some defining knot holds, so the largest triple sum is 2N;
    - a non-full base with every count 2^(n−1) would make every triple a knot with N = 3·2^(n−2), impossible for n ≥ 5 (pigeonhole)
      and for n = 4 (6 ≠ 12).

    The decoder's last step is also right. The triples with sum 2N include the defining knots and hold on the base, so their
    intersection is the base. The argument holds for every n ≥ 4.
  - **The referee's decoder** (`referee_order.py`, from the table alone) rebuilds all 16, 1,023 and 97,248 relations at n = 4, 5 and
    6. At n = 3 it rebuilds 1 of the 2 (one knot against none), as 3(c) says.
- **Statement 7 and the corollary (proved; Not a block; the owner's item 2).**
  - **The induction holds:** each earlier state keeps its weight; E[s_y | s_x] = −s_x/3; E[s_u s_y] = −E[s_u s_x]/3; and steps add
    one through x.
  - **Adding a knot** at one existing distinction changes neither the earlier correlations nor the earlier steps apart.
  - **The corollary is right.** If three distinctions pairwise share knots but no one knot, the last of the knots holding their pairs
    meets two earlier distinctions.
  - **One slip.** "Exactly three completions ... (four if x is also new)" should read six: a separate knot of three new distinctions
    allows six. Only the equal weight is used, so nothing changes.
  - **The referee's check.** On 300 random knot trees of up to 13 distinctions, by brute force, every pair has correlation exactly
    (−1/3)^s, or 0 with no row, and in every tree the knots are exactly the triples pairwise one step apart.
- **Ticket B recomputes.**
  - **The weave's counts are exact** (`referee_weave.py`, `.json`; the owner's item 4). The referee wrote its own row transfer
    matrix: exact int64 powers with an exact Python-integer diagonal at L ≤ 9, and float64 products modulo its own six primes below
    2^20, joined by its own Chinese-remainder step, at L = 12. N is 263,640, 547,003,370,634 and 379,028,233,842,678,000,000. All
    three equal the study's; the trailing zeros at L = 12 are genuine.
  - **The rates along a row** are exactly the study's: 2/3 at one step, and below ½ exactly at multiples of 3 at L = 6, 9 and 12.
  - **The study's CRT code** keeps every product below 2^40 and every sum below 2^52, so it is exact. Its moduli are prime and
    pairwise coprime, and its CRT is standard.
  - **No betweenness on the weave, exactly.** Statement 1 makes "c lies between a and b" the absence of a state with a = b ≠ c, and
    translations let a be v(0, 0). A SAT check of every (b, c) finds 0 betweenness triples at L = 6 and 9.
  - **The thread and the chain.** Exact pair counts by the referee's own transfer give N = 2,692,538 for the thread. Both have 0
    strict betweenness triples. τ differs from steps apart by up to 2.15 on the thread, and by 1.2·10⁻⁹ on the chain (float).
  - **The census** gives:
    - strict betweenness in 0, 732 and 87,924 relations at n = 4, 5 and 6;
    - gap paths 0;
    - P1 in 2, 93 and 871;
    - distinct τ-with-N tables 16, 674 and 63,355.

    All as published.
    - **"Non-constant P1" is 0, 72 and 780 by the referee's definition**, the positive counts taking at least two values. The
      study's 92 and 870 also count tables with zeros and a single positive value, which are trivially "unit steps". This is
      exploratory and unpredicted; Not a block.
- **"Steps apart and bond distance do not carry everything"** (the owner's item 5). It was only cited, so the referee reran it:
  - On four distinctions, three knots allow 8 states and four knots allow 6.
  - Both have steps apart 1 for every pair, and bond distance 2 for every pair under either bond definition (sizes ≥ 2 or ≥ 3).
  - It holds. Both bases have cycles of knots.

## 1. "With cycles they split" is what one strict reading finds on two bases (Narrowing)

The owner's summary reads "where knots form no cycle, one distance read from the states does both jobs; with cycles they split".
The no-cycle half is proved (statement 7 and the corollary). The cycle half is computed, on the thread (n = 30) and the weave (L ≤ 12),
for three candidates and τ, under A98's exact additive betweenness. Three things limit it.

- **It is not a property of cycles.** The census has 732 cyclic not-all-equal relations at n = 5 and 87,924 at n = 6 with strict
  betweenness. The threshold-line control has cycles of knots, yet its count both determines the base (with N, statement 3(a)) and
  is a line. What the data show is about the thread and the weave, spatial bases with many states. That fits statement 6's price:
  order costs states.
- **A weaker reading finds a local order on the weave** (`referee_ordinal.py`, `.json`; the coordinator's question). The setup:
  - read τ as closeness, and call w ordinally between u and v when it is nearer to each than they are to each other;
  - under this weakest, order-only reading of "something lies between", find the start's gaps, the distinctions with nothing
    between them and v(0, 0).

  **The result.** At L = 6, 9 and 12 those gaps are exactly twelve: the six knot-neighbours (τ = 1) and the six second neighbours in
  the start's own class (τ 0.61 to 0.66). Every other distinction has something between it and the start. So the disagreement
  count does carry a local, translation-invariant structure on the weave with nothing skipped, read ordinally. Its unit neighbours
  are not the weave's own: they add the same-class second neighbours. A strictly monotone unit-step path back to the start fails
  for 11 of 35, 26 of 80 and 47 of 143 distinctions, because τ is not monotone in steps apart.

  So "on the thread and the weave nothing lies between anything" holds for exact additive betweenness only. "The disagreement count
  has no order of its own on the program's spatial bases" (the note's answer) is stronger than the data.
- **John's words.** "Distance is topological ... you can't just skip 4 to get to 5, so there is an order." This supports A98's
  metric reading (4 lies between 3 and 5 as d(3, 5) = d(3, 4) + d(4, 5)), and it also admits an order-only reading. That is how
  "topological" is usually meant: order and adjacency, not additive values.
  - *A98 is fair.* It is a natural and strict formalization of the number-line picture, and it is recorded as an assumption with
    "order by levels" and "betweenness of sets" as challenges.
  - *But the A97 narrowing rests on it.* A97 is narrowed "to bases whose knots form no cycle". Under the ordinal reading the weave's
    count already shows a local order, so that narrowing depends on A98.
- **A fair wording.** "On knot trees one distance read from the states does both (proved). On the thread and the weave, under exact
  additive betweenness, the count that carries the information has no betweenness at all (computed). Under an order-only reading it
  has a local order whose unit neighbours are the knot-neighbours plus the same-class second neighbours, not the weave's own steps."
- **One placement in the intuition entry.** It lists "a chain of knots" under "With cycles of knots the two jobs split". The chain is
  a knot tree, where τ does both. It belongs with the no-cycle half: the count alone has no betweenness there, τ does.

## 2. Smaller points (Not a block)

- **Statement 7's slip.** "four if x is also new" should be six.
- **"Non-constant P1".** Define it, or give 72 and 780 beside 92 and 870.
- **Bond distance and order.** "Bond distance ... has the order with nothing skipped" holds only up to its offset (steps apart + 1).
  It fails P1 by that offset (E7), so "has the order" should say "up to the offset".
- **Known mathematics.** It is well named: Menger, Deza–Laurent, the degree-two form, pairwise independence, nested cuts,
  Cavender–Farris–Neyman, Stephenson, IN₂. Two additions would place statements 3 and 7:
  - *Statement 3.* A constraint whose violation count is a nonnegative degree-two polynomial holds on a set of states exactly when
    that polynomial has mean zero over it. This is the second-moment reading behind degree-two Sherali–Adams and sum-of-squares
    arguments.
  - *Statement 7.* It is the broadcast process on a tree with flip probability 2/3 (Evans, Kenyon, Peres and Schulman 2000).
- **Labels.** The note and the proof keep proved and computed apart throughout. The owner's one-line summary and the intuition
  entry's "With cycles of knots the two jobs split" state the computed, reading-dependent half as plainly as the proved half.

## Fixes for the thread (listed for the owner, not folded in)

1. **"With cycles they split."** Scope it to "on the thread and the weave, under exact additive betweenness (computed)". Add the
   ordinal reading's result: a local order of twelve neighbours, not the weave's six. Note in A97 and A98 that the narrowing "to
   bases whose knots form no cycle" rests on A98's strict reading. Move "a chain of knots" out of the intuition entry's "with cycles"
   sentence. **Narrowing.**
2. **Small fixes.** Statement 7's "four" → "six"; define non-constant P1; bond distance's order "up to its offset"; add the
   second-moment and broadcast-on-trees names. **Not a block.**

## How the work was split

- **The referee:**
  - read the proof, the pre-registration, the note, `order.py` (the CRT code), `run.py`, A97, A98 and John's reply;
  - checked every proof by hand;
  - recomputed the census, the decoder, knot trees, the thread and chain, and the weave, with own transfer matrices and own CRT
    moduli;
  - checked betweenness by SAT through statement 1;
  - ran two weaker readings of "no skipping";
  - re-ran the four-distinction collision.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_weave.py` and `.json`: the weave's exact N and row rates at L = 6, 9 and 12, and SAT betweenness at L = 6 and 9.
- `referee_order.py` and `.json`:
  - the census (decoder, betweenness, P1, gap paths, τ tables);
  - knot trees;
  - the thread and chain;
  - the weave's τ and the monotone-path reading.
- `referee_ordinal.py` and `.json`: the weave's ordinal gaps.
