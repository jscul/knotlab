# Rules that read only the states: what they grow. Pre-registration

Epic `STATE-RULES-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. It takes the first direction of
`GRID-GROW-20261117-001`, sharpened by that study's referee, and adds the owner's second arm, passed on from Codex. Goals G1 and
G16; tests A97. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

The grid study's referee found that the states do not say where a second order starts. A straight run's states admit a fill at
every inner distinction, and the given arrangement chose among them. So the question here:
- Among all the extensions the states admit, what do uniform rules that read only the states grow, with names and history erased?
- Does the rule or the start supply the number of orders?
- At each step, do the states decide the outcome, or does a coin?
- Under a stated weighting, is a second order typical or rare?

The owner's second arm asks whether how the knots meet carries information the states do not. A rule that may also read which
knots meet is compared with the states-only rule, from two starts that have the same states and different knots.

## What is handed over, and how this contract tests it

- **Handed over by construction, and said so:**
  - the move set: up to K betweenness knots, each on the new distinction and two old ones, every old state kept;
  - the weighting;
  - the start.
- **The rule reads only the states.** Its weights depend on the state count of each extension alone. The names are erased (renamed
  at random before each read), and ties are uniform. Nothing else enters.
- **Do the states decide?** At every step the record holds how many inequivalent outcomes share the top weight (D1). One means the
  states decide the outcome. More than one means a coin chooses among inequivalent continuations, so the placement is the coin's.
- **Does the rule or the start supply the number of orders?** The one-knot fewest-states rule is run from three starts with one,
  two and branching orders (S2 says it keeps each).
- **Is a second order typical or rare?** Exact distributions to n = 6 to 9, and sampled runs to n = 10 to 16, under:
  - fewest states;
  - uniform choice;
  - a softmax between them;
  - each with extensions counted one by one, or with each class of outcome counted once (the owner's item).
- **The move set includes the event counted.** The fill needs three knots, so the comparisons that count a second order use K = 3.
  K = 1 and K = 2 are shown as well.

## Ticket A: the proof (written before this freeze)

`proofs/STATE-RULES-20261117-001A/STATE-RULES-20261117-001A-P001_cheapest_steps/proof.md`.
- **S1.** Single-knot costs N + d or 2N − d, so at least N + 2: reached by subdivisions and pendants only.
- **S2.** The one-knot fewest-states rule keeps (k, λ): (1, 1) from a line, (2, 2) from the 2 × 2 pattern, (1, 2) from the star.
- **S3.** One step from a line makes at most two orders. It keeps a line only at the n + 1 placements.
- **S4.** The zero-cost three-knot steps of a line are exactly the C(n, 3) fills, each two orders. From one knot the only one is the
  2 × 2 pattern.
- **S5.** From one knot, fewest states with three knots gives the 2 × 2 pattern at n = 4, then 8 options at n = 5 in two classes.
- **S6** is the advisor's conjecture: two orders with probability 1/2 at n = 6 and 0 at n = 7, and the cube Q_d at n = 2^d.

## Ticket B: computations

Code: `rules.py`, `run.py` and `checks.py` in `experiments/STATE-RULES-20261117-001B/STATE-RULES-20261117-001B-E001_rules/`. The 19
checks pass before this freeze:
- knot masks against direct evaluation;
- extensions against brute force over knot sets;
- the lattice dimension λ by matching against brute force;
- known shapes (line, 2 × 2, star, grids, Q3);
- the two six-starts;
- the locality rules;
- blindness to names.

Rules (K is the most knots per step; c counts each class of outcome once):

| Name | Weighting |
| --- | --- |
| F1, F2, F3 | fewest states, K = 1, 2, 3 |
| F3c | fewest states, K = 3, classes counted once |
| U1, U3 | uniform over extensions, K = 1, 3 |
| U3c | uniform over classes, K = 3 |
| softmax β | K = 3, weight exp(−β(N′ − N_min)), β = 0.5, 1, 2 |
| KF3 | fewest states over knot-local moves: each new knot's two old distinctions lie together in one existing knot |
| KS3 | the same, strict: all the move's old distinctions lie in one existing knot |
| KC3 | the control: each new knot's old pair lies in some betweenness triple every state satisfies (a function of the states) |
| KU3 | uniform over knot-local moves |

In the knot arm, distinct knot sets are distinct moves, even with equal states. The moves are irredundant: no knot can be dropped
without changing the states.

Parts:
- **E1.** Exact class distributions from one knot B(0, 1, 2): F1, F2, F3 and F3c to n = 9, U1 to n = 7, U3 and U3c to n = 6. Also
  the probability mass whose top options form one class (D1).
- **E2.** F1 from the line, the 2 × 2 pattern and the star, 20 runs each to n = 14: (k, λ) at every step, and D1.
- **E3.** F3 and F3c from one knot, 40 runs each to n = 16: kinds, states, the classes at n = 8 and 16, D1.
- **E4.** U1, 50 runs to n = 12; U3, 50 runs to n = 10.
- **E5.** Softmax at β = 0.5, 1 and 2, 40 runs each to n = 10.
- **E6.** The referee's sharp form: every admitted extension with up to three knots of a line of 6, 7 and 8. By kind, cost and class:
  the line-keeping ones, the zero-cost ones, the largest λ and k, and the uniform fraction with two orders.
- **E7.** Codex's check: continuations invariant under every symmetry of the base, over all relations and over knot extensions,
  for the 3-line and for the 2 × 2 pattern. Two readings of "every renaming", frozen both:
  - the signed group (permutations with any value swaps);
  - permutations with no swap or the global swap.
- **E8.** The knot arm.
  - Exact KF3 and KS3 from one knot to n = 7.
  - 30 runs each of KF3, KS3, KC3 (to n = 12) and KU3 (to n = 10), from three starts:
    - one knot;
    - the fan of six: B(a,b,c), B(a,c,d), B(a,d,e), B(a,e,f), with a in all four;
    - the non-fan of six: B(b,c,d), B(b,d,e), B(e,b,a), B(a,e,f), with no distinction in all four.
  - Both six-starts have exactly the line's 12 states and four knots.
  - States-only F3 and U3 from both six-starts with the same seeds, as the identity control.

Readings: k (exact when ≤ 2, else ≥ 3; exact up to 4 for at most 24 splits), λ (exact), states, splits, crossings, the kind (a
line, a branching tree, two orders, a cube, m orders).

## Predictions (frozen; the advisor's derivations where marked)

| # | Prediction | Fails when |
| --- | --- | --- |
| R1 | E6: every extension of a line of 6, 7, 8 has k ≤ 2 and λ ≤ 2 (S3) | any has more |
| R2 | E6: exactly n + 1 extensions keep a line (7, 8, 9), all at N + 2 (S3) | otherwise |
| R3 | E6: exactly C(n, 3) zero-cost extensions (20, 35, 56), all two orders (S4), in 10, 19 and 28 classes | otherwise |
| R4 | E6: the uniform fraction with two orders is above 0.9 (advisor) | 0.9 or less |
| R5 | E1: F1 gives the line with probability 1 at every n to 9, and every step's top options are one class | otherwise |
| R6 | E1: F2 gives the line at n = 4 with probability strictly between 0 and 1 (advisor: about 1/2) | 0 or 1 |
| R7 | E1: F3 gives the 2 × 2 pattern at n = 4 with probability 1 and one class at the top. At n = 5 two classes of 1/2 each, both two orders. Two orders with probability 1/2 at n = 6 and 0 at n = 7; Q3 at n = 8 with probability 1 (S5; S6, advisor) | any differs |
| R8 | E1: F3c as F3 at n = 4, 5. Two orders 5/12 at n = 6; Q3 at n = 8 with probability 1 (advisor) | otherwise |
| R9 | E1: U1 at n = 4: line 4/9, two orders 3/9, tree 2/9 (advisor) | otherwise |
| R10 | E2: (k, λ) = (1, 1), (2, 2), (1, 2) at every step of every run (S2). The line's top options are always one class; the 2 × 2 pattern's and the star's are not | any differs |
| R11 | E3: Q3 at n = 8 and Q4 at n = 16 in 40 of 40 runs of F3 and of F3c. The top options are more than one class at a majority of steps from n = 5 on (advisor) | otherwise |
| R12 | E4: U1 and U3 give two orders in under 10% of runs at n = 10, and λ ≥ 3 in a majority. U3 gives k ≥ 3 in a majority at n = 7 (advisor) | otherwise |
| R13 | E5: at n = 10, two orders in fewer than half the runs at every β (advisor) | half or more at some β |
| R14 | E7, signed group: from the 3-line exactly one invariant, open, constrained continuation over all relations, up to flipping the new bit (parity, giving the 2 × 2 pattern's 6 states; two as literal relations). From the 2 × 2 pattern only the fixed and the free ones, and no invariant knot extension (Codex; advisor) | otherwise |
| R15 | E7, permutations with the global swap: at the 2 × 2 pattern exactly one invariant, open, constrained knot extension, the centre point, with 10 states (advisor) | otherwise |
| R16 | E8: states-only F3 and U3 give identical runs from the two six-starts (by construction), and so does KC3 | any difference |
| R17 | E8 exact: KF3 from one knot gives two classes of 1/2 at n = 5. Two orders with probability 2/3 at n = 6 (F3: 1/2) and 0 at n = 7 (advisor) | otherwise |
| R18 | E8: KF3 from one knot reaches Q3 at n = 8 in at least 24 of 30 runs (advisor: about 80% that all do), with two orders in none at n = 12 | otherwise |
| R19 | E8: KF3 from each six-start keeps 12 states to n = 12 in at least 24 of 30 runs. Two orders in at most 3 runs at n = 12; at n = 8 two orders in at least one run from each start, in counts that differ (advisor) | otherwise |
| R20 | E8: KU3 gives two orders in under 10% of runs at n = 10 from each start | otherwise |

KS3 has no directional prediction. The advisor expects it to stall early: its fills come from single knots only.

**What would count against the headline.**
- A states-only rule whose second order is typical and stays, without being handed it.
- F3 missing the cube.
- A line extension with λ = 3.
- A zero-cost count other than C(n, 3).

Most of all, a knot-reading rule (KF3 or KS3) that keeps two orders to n = 12 in most runs where F3 does not. That would mean how
the knots meet carries what the states do not: the owner's premise, positive.

**The headline, stated before running.** Among all the extensions the states admit:
- The cheapest one-knot steps keep whatever number of orders the start had.
- The cheapest three-knot steps make a second order at once from one knot, with no coin, at the first step only. After that a coin
  picks the route, and every route reaches the same cube each time the count of distinctions doubles: one more order each time.
- Uniform choice gives many orders.
- No rule tried settles on two orders by itself. Either the start hands the number over, or it keeps growing.
- Reading which knots meet shifts the odds along the way, but not, I predict, the destination.

**Classical:** split systems and compatibility (Buneman; Bandelt and Dress); products of trees (Bandelt and van de Vel); lattice
dimension (Eppstein). **Local:** the costs, the conservation, the C(n, 3) fills and the rule comparisons.

## Prior work in the program

`python3 -B scripts/track.py objects "growth rule reads states fewest states orders cube lattice dimension knots meet" --until 2026-11-17 --exclude STATE-RULES-20261117-001`

- `KNOT-ORDER-20261117-001`: the line's n + 1 placements; an outside rule growing a line from its states.
- `GRID-GROW-20261117-001`: the grid's costs on a given arrangement, and its referee's Block (the predecessor).
- `DISTANCE-DIM-20261117-001`: order and order dimension read from implication bases.
- `OPEN-END-GROWTH-20261107-001`: growth at knots with two open ends grows the thread.
- `GROW-COUNT-20261111-001`, `RANDOM-FATES-20261112-001`: free growth of not-all-equal patterns (different move sets).
- `CARRY-FIFTH-20261117-001` (Codex): the four-to-five step, the line of four's two two-knot presentations, and what retained knots
  mark.

## Runs and stop rule

One script, `run.py`, one process. It is expected to take under an hour; it is run in the background and registered in
`docs/LONG_RUNNING.md` if it passes ten minutes. A stress test, F3 to n = 32 (five runs, `run.py --stress`, prediction Q5 at
n = 32 in all five), runs after the main read-out and does not block it. The study stops after its read-out, followed by A97
status, the decision note, the referee hand-off and the report.

The advisor model was consulted three times before this freeze. It:
- proved the conservation of k and gave S2's twin argument;
- corrected my design: a step must allow the event counted, and the zero-cost fills exist;
- gave the C(n, 3) count, the cube growth, the n = 5 to 8 probabilities and the counted-once values;
- gave the knot-arm predictions, the closure-local control and the strict arm;
- found that the two readings of Codex's check differ at the 2 × 2 pattern.
