# Rules that read only the states: what they grow

Epic `STATE-RULES-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. It takes the first direction of
`GRID-GROW-20261117-001`, sharpened by that study's referee, and adds the owner's second arm, passed on from Codex. Goals G1 and
G16; tests A97. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no Block, folded in on 17 November (see
Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `fa975f08b` at 21:38:45 UTC.
- Proof: [proof.md](../../proofs/STATE-RULES-20261117-001A/STATE-RULES-20261117-001A-P001_cheapest_steps/proof.md).
- Code: [rules.py, run.py, checks.py and posthoc.py](../../experiments/STATE-RULES-20261117-001B/STATE-RULES-20261117-001B-E001_rules/).
- Results: [results.json and posthoc.json](../../artifacts/STATE-RULES-20261117-001B/STATE-RULES-20261117-001B-E001_rules/).

**The run, and two amendments made before the parts they touch were read.**
- The first run, one process from 21:39, spent over an hour in one exact count (the two-knot rule to n = 9) and was stopped.
  Amendment 1 (`06442c962`, 22:45 UTC) ran each part as its own process and stopped that count at n = 7. Only the line extensions
  and the one-knot rule's exact count had printed.
- Three parts then stalled in an isomorphism search that grows exponentially as lines grow. Amendment 2 (`5ebe208b5`, 23:18 UTC)
  compares the disagreement-weighted graph instead, which gives the same classes (DISTANCE-ORDER statement 3(a); a new check
  agrees on 166 pairs). Those three parts were rerun from the start.
- No rule, start, reading, prediction or decision rule changed. The parts ran from 22:46:44 to 23:26:44 UTC.

## The answer

**No rule tried settles on two orders by itself.** Among all the extensions the states admit:
- **Cheapest one-knot steps** keep whatever number of orders the start had (proved).
- **Cheapest three-knot steps** make a second order at once from one knot, with no coin. After that a coin picks the route, but
  every route reaches the same cube each time the number of distinctions doubles: one more order each time (computed to 16).
- **Uniform choice** gives many orders.
- **Reading which knots meet** changes which bases grow, but not how many orders they have, for these two starts (*scoped on 18
  November 2026 by `KNOT-CAP-20261117-001`: for another matched pair, and under a cap, it changes the number of orders too*). *Narrowed after the referee: with
  1,000 runs per start, two starts with the same states and different knots grow different bases (they share 1 of 4 classes at
  n = 7) with the same number of orders.*

Here "an order" is one line of the least number of lines whose product holds the distinctions, with the disagreement count as
twice the distance along them (the literature's lattice dimension, Eppstein). "Two orders" means two lines and a crossing.

### Is the placement handed over?

The rule sees only the states, renamed at random. The question is whether the states decide each step or a coin does.
- **They decide the first step from one knot.** The only extension of the line of three that adds no state is the 2 × 2 pattern
  (proved). So the second order starts with no coin: two orders are the cheapest continuation of one knot.
- **From a longer line they do not.** A line of n admits exactly C(n, 3) extensions that add no state, one for each triple of its
  distinctions, and every one starts a second order: 20, 35 and 56 for n = 6, 7 and 8, in 10, 19 and 28 classes (proved, and
  computed). This is the grid study's referee's point, made exact. The states admit a second order at every triple, and nothing in
  them picks one.
- **Along the cheapest three-knot growth** the top options are inequivalent at n = 5, 6 and 9 to 14, where the coin chooses. They
  are one class at the steps that complete a cube (n = 7, 8, 15, 16), where the states decide.

### Does the rule or the start supply the number of orders?

- **One knot per step: the start.** From the line, every step keeps the line (20 of 20 runs to 14, and the exact distribution to
  9). From the 2 × 2 pattern, (k, λ) stays (2, 2), and from the three-leaf star (1, 2), at every step of every run. That is proved:
  the cheapest single knots only split a split in two or hang a copy off an end.
- **Three knots per step: the rule, without bound.** The cube with three orders at n = 8 and with four at n = 16, in 40 of 40 runs.
  This holds both counting every extension and counting each class of outcome once (the owner's item), each time with 8 and 10
  states.

### Is a second order typical or rare?

- **Exact, from one knot.**

  | Rule | n = 4 | n = 5 | n = 6 | n = 7 |
  | --- | --- | --- | --- | --- |
  | Fewest states, up to three knots | 1 | 1 | 1/2 | 0 |
  | The same, classes counted once | 1 | 1 | 5/12 | 0 |
  | Uniform, one knot | 3/9 | 0.62 | 0.28 | 0.07 |
  | Uniform, up to three knots | 1/2 | 0.78 | 0.42 | (not computed) |

- **Sampled at n = 10.** Two orders in:
  - 0 of 50 runs for each uniform rule;
  - 0 of 40 at each softmax weight between them (β = 0.5, 1, 2);
  - 0 of 40 for fewest states.

  The number of orders is then 5 to 21 (uniform, one knot), 4 to 9 (uniform, three knots), 3 to 7 (softmax) and 3 to 4
  (fewest).
- **Counting equivalent placements once** changes the n = 6 value from 1/2 to 5/12 and nothing else.

Two orders are typical only at n = 4 and 5, under the cheapest rule. They are a stage, not a stop, under every weighting tried.

### Does reading which knots meet change it? (the owner's second arm)

The rule may also read the knots, with names and history erased. A new knot must join two distinctions that already share a knot
(knot-local), or in the strict arm the whole step must sit inside one existing knot.
- **From one knot.** Two orders at n = 6 with probability 2/3, against 1/2 for the states-only rule, and 0 at n = 7. The cube at
  n = 8 in 30 of 30 runs, and 3 or 4 orders at n = 12 with 10 states, as for the states-only rule. *Narrowed after the referee:
  the 2/3 is the knot arm's weighting (each knot set counts, not each extension), not its reading of knots. The closure control,
  a function of the states with the same weighting, gives 0.70 against the knot-local rule's 0.65 (1,000 runs each); the
  comparison to quote is between those two.*
- **From two starts with the same 12 states and different knots.** One start has a distinction in all four knots, the other none.
  - The knots decide where the first fill can go: only at the knots' own four triples, which differ between the starts.
  - Two orders at n = 8 in 11 and 15 of 30 runs; the closure-local control, a function of the states alone, gives 22 and 23.
    Then 3 to 5 orders by n = 12, with 12 states in 30 of 30 runs. *Withdrawn after the referee: "so the difference is within
    sampling". With 30 runs per start the comparison had about 3% power at these rates and could show nothing either way.*
  - **The referee's 1,000 runs per start, identical seeds.** The number of orders does not depend on the knots: two orders at
    n = 8 in 375 and 361 runs (Fisher p = 0.55), and the same distributions of λ at n = 10 and 12 (χ² p = 0.68, 0.81). The grown
    bases do depend on them. The classes of states (knots ignored) at n = 7 are four from each start and only one is shared, total
    variation distance 0.76; at n = 8 it is 0.81.
  - States-only rules give identical runs from the two starts, as they must.
- **The strict arm** does not stall. It takes the costlier steps and reaches 5 or 6 orders by n = 12.
- **Uniform over knot-local steps:** two orders at n = 10 in 1 of 30, 0 and 0.

So how the knots meet does carry information the states do not: it fixes where the first fill can go, and the bases grown from
the same states then differ (the referee's 1,000 runs). For these two starts it does not change how many orders they have (exactly
equal through n = 9; `KNOT-CAP-20261117-001` found other starts where it does). No knot-reading rule tried
keeps two orders.

### A rule with no coin (Codex's check)

Keep every old state, and require the one continuation to respect every symmetry of the base, including swapping the values of
any distinction.
- From one knot exactly one open, constrained continuation qualifies: parity, which gives the 2 × 2 pattern (two as relations, one
  up to flipping the new bit).
- At the 2 × 2 pattern only the fixed and the free ones remain, so a coin-free states-only rule grows one square and stops.
- Under renamings with only the global swap, the 2 × 2 pattern has exactly one invariant knot continuation, the centre point with
  10 states, so the coin-free rule goes one step further.
- Which group "every renaming" means is a choice. Both are recorded, and Codex's (the signed group) gives "one square and stop".

**In the owner's terms.** The cheapest way one knot can continue is two orders, and the states choose it alone. But the same
cheapness keeps going, to three orders and then four, one more each time the distinctions double. Nothing in these laws stops at
two: either the start hands the number of orders over, or the growth keeps adding them. Reading how the knots meet changes what
grows from the same states, and for some starts how many orders it has (`KNOT-CAP-20261117-001`).

## Referee

Report [R1](referee-R1/report.md), 17 November 2026, by a background referee thread with fresh code and no Codex: confirmed with
fixes, no Block.
- S1 to S5 hold (S4's case analysis is complete for at most three knots). The referee's code recomputes, one size past:
  - the C(n, 3) zero-cost fills at n = 3 to 10, all two orders;
  - every extension of a line with k, λ ≤ 2, and exactly n + 1 keeping a line;
  - (k, λ) conserved to n = 13 from all three starts;
  - the exact 1, 1/2 and 0 at n = 5, 6 and 7, and 5/12 with classes counted once.
- The amendments changed no read-out or prediction, and amendment 2's class equivalence is right. The number of orders is read from
  the states alone, so no arrangement is smuggled in. "No rule tried makes two orders and keeps them" is fair as scoped.

Folded in the same day, each item logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing (the one that bears on the owner's premise).**
   - The fan and non-fan comparison with 30 runs per start had about 3% power, so "within sampling" carried nothing and is
     withdrawn.
   - With 1,000 runs per start and identical seeds, the number of orders does not depend on the knots, but the grown bases do (TV
     distance 0.76 at n = 7, 0.81 at n = 8).
   - How the knots meet carries information that changes what grows, not (for these starts) how many orders it has. Not yet tested: other start
     pairs, other knot rules, and which state differences matter. `KNOT-CAP-20261117-001` takes these up.
2. **Narrowing.** The 2/3 against 1/2 at n = 6 is the weighting (knot sets against extensions), not knot reading: the closure
   control gives 0.70 and the knot-local rule 0.65.
3. **Not a block.** R16 failed only because the seed string includes the start. R17 and R19 were held on a post hoc read, as
   labelled.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| R1 | Line extensions: k, λ ≤ 2 | held | max λ = k = 2 at n = 6, 7, 8 |
| R2 | Exactly n + 1 keep a line, all at N + 2 | held | 7, 8, 9 |
| R3 | C(n, 3) zero-cost extensions, all two orders, in 10, 19, 28 classes | held | 20, 35, 56; 10, 19, 28 |
| R4 | Uniform fraction with two orders above 0.9 | held | 0.961, 0.981, 0.990 |
| R5 | One knot per step, fewest: the line with probability 1; top one class | held | to n = 9 |
| R6 | Two knots: the line at n = 4 strictly between 0 and 1 | held | 1/2 |
| R7 | Three knots, fewest: 2 × 2 at 4 (decided); 1/2 and 1/2 at 5; two orders 1/2 at 6, 0 at 7; the cube at 8 | held | all exact |
| R8 | The same, classes once: two orders 5/12 at 6; the cube at 8 | held | 5/12; 1 |
| R9 | Uniform one knot at n = 4: line 4/9, two orders 3/9, tree 2/9 | held | exact |
| R10 | One knot from three starts keeps (k, λ); line top always one class, others not | held | 240, 220, 220 steps; line 220 of 220 decided, 2 × 2 none, star 21 of 200 |
| R11 | Cube at 8 and 16 in 40/40 (both counts); top inequivalent at a majority of steps from 5 | held | 40/40 and 40/40, and 40/40 and 40/40 with classes once; 309 of 480 steps (counting extensions) |
| R12 | Uniform: two orders under 10% at 10, λ ≥ 3 in a majority; three knots k ≥ 3 in a majority at 7 | held | 0/50, 0/50; 42 of 50 |
| R13 | Softmax: two orders in under half at 10, every β | held | 0/40 at each |
| R14 | Signed group: one open invariant continuation from one knot (parity), none at 2 × 2, no knot one | held | 2 literal (6 states); none; none |
| R15 | Global swap only: one open invariant knot continuation at 2 × 2, 10 states | held | exactly one, 10 states |
| R16 | Identical runs from the two six-starts for states-only rules and the closure control | **held for the states-only rules; failed as worded for the control** | The frozen code seeded the control differently for the two starts; its distributions agree within sampling (two orders at 8: 22 and 23 of 30; at 10: 5 and 5; at 12: 0 and 0) |
| R17 | Knot-local, exact: 1/2, 1/2 at 5; two orders 2/3 at 6, 0 at 7 | held | the n = 5 split read post hoc from the frozen run's classes |
| R18 | Knot-local from one knot: cube at 8 in ≥ 24/30; two orders in none at 12 | held | 30/30; 0 |
| R19 | Knot-local from the six-starts: 12 states to 12 in ≥ 24/30; ≤ 3 two-order runs at 12; at 8 at least one each, counts differ | held | 30/30 both (post hoc count from the frozen seeds); 0 and 0; 11 and 15 |
| R20 | Uniform knot-local: two orders under 10% at 10 | held | 1, 0, 0 of 30 |

19 of 20 held, and R16 held in part. With classes counted once the top weight goes only to the smallest classes in a tie, so its
step-by-step class reading (158 of 480 steps inequivalent) is not comparable with R11's and is not scored. Two readings were counted post hoc from the frozen runs, recomputed from the frozen seeds:
R17's n = 5 split and R19's state counts. They are labelled, and `posthoc.py` gives them. The stress test, one size past (the cheapest rule to n = 32, five runs), held: the cube of five orders, Q5, at n = 32 in 5 of
5 runs, with 12 states (folded in 17 November 2026; 546 s; `stress.json`).

## What the knot picture explained

- **Why the cheapest step from one knot is two orders.** A new distinction adds no state only if every old state fixes it. On a
  line that needs one knot between two outer distinctions and two knots carrying it to either side of a third. The pattern it makes
  is "with the first, then against, then with": a crossing. From three distinctions there is one such pattern, the square.
- **Why it does not stop.** Every time the states hold room for a new point that adds no state, the cheapest rule takes it. With s
  splits there is room for 2^s points: the cube. Only when the cube is full must a step add a split, and that split doubles the
  room.
- **Why one knot per step keeps the number.** A single knot either splits one split in two, beside its twin, or hangs a copy off a
  distinction at the far end of everything. Neither can make a new crossing.

Known mathematics, labelled:
- split systems and compatibility (Buneman 1971; Bandelt and Dress 1992);
- products of trees (Bandelt and van de Vel 1989);
- lattice dimension by a matching (Eppstein 2005);
- crossing graphs (Klavžar and Mulder).

Local: the costs, the conservation, the C(n, 3) fills, the cube growth and the comparisons.

## What it means for A97 and the goals

- **A97** (distance is the only form of information) stays under challenge. Under A98's reading, the disagreement count, a base of
  knots grown by any of these laws has its orders read back exactly. But how many orders it has is either handed over by the start
  or keeps growing; none of these laws makes two orders and keeps them.
- **G1** (space from a law): obstruction learned for these laws, all uniform and reading only the states, with or without the
  knots. The cheapest law makes the second order at once and does not stop there. A law that stops at two would need something
  these do not have.
- **G16** (learning the rules behind what a system allows): capability gained. The orders a states-only rule grows are predicted
  exactly (costs, conservation, C(n, 3), cubes).
- **New assumption A99.** States-only growth is judged on conservative betweenness extensions with up to three knots per step. That
  is the move set this study and the grid study share, recorded so it can be challenged.

## Limitations

- **Knots.** Betweenness knots only, in three roles, up to three per step. Other three-place knots, four-place knots and larger
  steps are untested.
- **Every old state kept.** Steps that remove old states are out.
- **Sizes.** Exact counts reach n = 6 to 9, runs reach 10 to 16, and the stress test reaches 32 (five runs).
- **Weightings.** Fewest states, uniform and softmax, by state count alone, or by knot-locality. A rule weighing something else
  (knots per distinction, say) is untested.

## Reproduce

```sh
cd experiments/STATE-RULES-20261117-001B/STATE-RULES-20261117-001B-E001_rules
../../../.venv/bin/python -B checks.py                                            # 23 checks
for P in E6 E1 E2 E3 E4 E5 E3c E7 E8; do ../../../.venv/bin/python -B run.py --part $P; done
../../../.venv/bin/python -B run.py --merge
../../../.venv/bin/python -B posthoc.py
```

## Advisor

Consulted three times before the freeze. It:
- proved the conservation of k and gave the twin argument;
- found the zero-cost fills after first missing them, and gave the C(n, 3) count;
- predicted the cube growth, the n = 5 to 8 probabilities and the counted-once value;
- gave the knot-arm predictions, the closure-local control and the strict arm;
- found that the two readings of Codex's check differ at the 2 × 2 pattern.

Every advisor prediction checked here held. It was not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what states-only rules grow | **Status:** Successful (referee pending) | 19 of 20 predictions held; the number of orders is inherited (one knot) or grows like log₂ n (three knots); two orders typical only at n = 4, 5 |
| Local direction: a law that selects its dimension | Obstructed for these laws | Uniform state-count weightings and knot-locality all pass through two orders without stopping |
| Broader exploration: what would stop growth at two orders | Unexplored | A cost on knots per distinction, a bounded reach, or a different knot |
| Long-term goal: G1 | Obstruction learned | No uniform law tried makes two orders and keeps them |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A law that stops: fewest states with each distinction in at most c knots (c = 3 to 9). Does a cap on how many knots a distinction joins stop the cube and keep two orders? | 3/3 | 2/3 | Freeze the capped rule from one knot to n = 16 → stop at the orders it keeps | Alternative |
| 2 | The coin-free rule under the global swap: after the centre point, does a rule with no coin grow anything further, and what? | 2/3 | 3/3 | Iterate the invariant continuation to a stop → stop at its last base | Alternative |
| 3 | Other knots: the same weightings with all 34 three-place knots, or four-place ones (the parity fill is one knot) | 2/3 | 2/3 | Rerun E1 and E3 with the wider move set → stop at the orders grown | Alternative |

**Corrections:** none.

**Goals:** a G1 checkpoint (obstruction learned) and a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A97 stays under challenge, with this obstruction recorded; new entry A99 (the move set).

**Basket:** read; nothing taken.
