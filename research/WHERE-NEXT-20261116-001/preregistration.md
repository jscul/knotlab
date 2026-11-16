# Does a learned choice of where to act next, with memory, cut total work where plain search is costly?: pre-registration

Epic `WHERE-NEXT-20261116-001` (`FOLD-TRANSFER-20261114-001#2`; goals G15, G16), 2026-11-16. **Frozen** before any learned
agent was trained or scored (only the engine's gate, a timing check and a 20-iteration smoke of the trainer, on an earlier
engine version, ran before this text; their numbers are not results). Code by the thread (Claude) in
`experiments/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next/`; the long runs launched by the thread with
the shared runner. The canonical K1–K3 test is unchanged. The advisor model reviewed a draft
([advisor note](advisor_review.md)); the changes it led to are listed there and folded in below.

## The question

The owner's idea (2026-11-16): a learner reads the local context at one logical knot; an agent learns to turn from knot to
knot and act on their loops; it remembers the steps it has taken; choosing a knot activates it so that actions can happen
there; later, the knot structures themselves can be changed to improve results. The 22 fold studies of 11-14 and 11-15
(`research/FOLD-TRANSFER-20261114-001/line_record.md`) did not test this: no policy chose where to act, none saw its own
history, and every task had 3 to 9 inputs, where exact search is nearly free. This study tests the first half of the idea
fairly. On knot patterns of the not-all-equal law large enough that exact search takes real time, does a learned policy for
which knot to attend to next and which of its distinctions to flip, with memory of its earlier steps, reduce the work per
instance below that of tuned hand-written local rules, and what does its training cost before it pays; and does what it
learns carry over to unseen instances, to sizes up to 16 times its largest training size, and to a second meeting pattern?
Changing the knot structures is a second stage, not tested here.

## The objects, in the program's words

- **The knot law.** Every knot binds three distinct distinctions and allows every joint state of them except 000 and 111
  (not-all-equal, lesson 4.7). `knotlab check --cnf "a b c; ~a ~b ~c" --loops a b --contact c` returns K1, K2 and K3 yes (the
  same for any choice of contact, by symmetry); the gate reruns it. The law is the same on every knot, so an instance is a
  meeting pattern: which knots share which distinctions.
- **Instances are planted.** A hidden state (not constant) is drawn first and only knots it satisfies are kept, so every
  instance is a base (allows a state). Two families:
  - `rand`: each knot's three distinctions drawn uniformly, m = round(2.1·n) knots;
  - `local`: the distinctions in a fixed cyclic order; each knot takes a uniformly drawn distinction and two more within 10
    places of it in that order, m = round(4.0·n) knots.
- **A step.** The agent attends to one violated knot (its three distinctions all equal), the owner's "activation", and flips one
  of its three distinctions; any such flip satisfies that knot, and may violate others that share the flipped distinction. A
  flip is a change of state; the law and the meeting pattern never change during a run.
- **Where.** After a flip, the agent chooses the next knot to attend to among: the knots its flip just violated (each shares
  the flipped distinction with the knot it just acted on, so it overlaps that knot), up to three, and three violated knots drawn
  uniformly. The hand-written rules attend to a uniformly drawn violated knot (WalkSAT, probSAT, Novelty+, focused
  Metropolis), to a just-violated knot with probability q (the sticky rule), or to the candidate whose best flip violates fewest
  other knots (the greedy-where rule).
- **Memory.** For each candidate knot: how long since the agent last attended to it (log steps, clipped at 1,000), its rank by
  that among the candidates, and a recent-visit count (decay 50 steps); for each distinction of the attended knot: how long since
  it was last flipped (clipped likewise), its rank by that among the three, whether it was the last flipped, and a recent-flip
  count. These are what an attention over the agent's own past steps retrieves when it matches identities. A six-unit recurrent
  state carries the trend of the run. The memoryless agent sees only the present state: for each distinction, how many satisfied
  knots a flip would violate (its break) and how many violated knots contain it (its make); for each candidate knot, its least,
  mean and zero-count break, whether it was just violated, and whether it overlaps the knot just acted on.

## In standard terms

Planted random 3-uniform hypergraph 2-colouring (unsigned NAE-3-SAT) at clause density 2.1, near the random threshold
(cavity estimate about 2.105), and a bandwidth-limited variant at density 4.0. The agent is focused stochastic local search
whose clause choice and variable choice are both a learned softmax policy (326 weights: two 8-unit scorers and a 6-unit
recurrent state) over local features, trained by evolution strategies (OpenAI-ES), a policy-search form of reinforcement
learning. Work is measured as flips, as incidences touched (a knot–distinction pair read) and as CPU time in one C engine.

## Prior work in the program

Objects index, searched 2026-11-16 (this epic did not exist yet, so nothing needed excluding):

`python3 -B scripts/track.py objects "agent that chooses which knot to act on next" --until 2026-11-16 --exclude WHERE-NEXT-20261116-001`
`python3 -B scripts/track.py objects "learned local search policy for satisfiability" --until 2026-11-16 --exclude WHERE-NEXT-20261116-001`
`python3 -B scripts/track.py objects "planted not-all-equal instances" --until 2026-11-16 --exclude WHERE-NEXT-20261116-001`
`python3 -B scripts/track.py objects "WalkSAT" --until 2026-11-16 --exclude WHERE-NEXT-20261116-001`
`python3 -B scripts/track.py objects "reinforcement learning agent" --until 2026-11-16 --exclude WHERE-NEXT-20261116-001`

- "agent that chooses which knot to act on next": top hits `LEVEL-RETURN-20261113-001`, `TOP-INFO-20261114-001`,
  `BASES-WITHIN-20261112-001`: unrelated (rigidity, least bonds, tie classes; matched on words only).
- "learned local search policy for satisfiability": `SEARCH-AUDIT-20261112-001`: a relative; 91 learned cases of the learning
  line found their targets no faster than blind draws. Its lesson, score a learner against blind and tuned search and not
  against nothing, is this design. `FIVE-PRODUCT-TOTAL-WORK-20261115-001`, `NEST-COUNT-20261112-001`,
  `CLAMP-LEARN-20261112-001`: unrelated object.
- "planted not-all-equal instances": `WITNESS-COUNT-20261112-001`, `SHORT-DESC-20261112-001`, `NEST-READ-20261112-001`,
  `REACH-CENSUS-20261113-001`: same law, different object (life and bonds of nested not-all-equal patterns, no solving work).
- "WalkSAT": `STEER-LEARN-20261112-001`: unrelated object (steering rules in law learning).
- "reinforcement learning agent": `SEARCH-AUDIT-20261112-001` (above) and `FIVE-PRODUCT-TOTAL-WORK-20261115-001`: unrelated.

Records outside the index: the 22 fold studies (above; only `LOCAL-RULE-ACTIONS-20261114-001` had an agent, a tabular
Q-learner at a fixed position on chains of three to five rules); the archived notebooks of March and April 2026
(`archive/p-vs-np/experiments/02_pair_graph_ppo.ipynb`, `30_cnf_pair_vs_variable_agents.ipynb` with `cnf_agent_routing.py`,
`37_minimal_loop_agent_rl.ipynb`), where a variable or a shared pair acted as an agent passing activation through a fixed
five-clause formula, with no cost comparison; and the 2024 spatial Q-learner (`archive/dissonance/`). None measured work
against search.

## Prior work outside the program

Citations from memory except where marked checked; the referee is asked to verify them.

- Hand-written local search: WalkSAT (Selman, Kautz and Cohen 1994); Novelty and Novelty+, which use each variable's age, a
  memory of earlier steps (McAllester, Selman and Kautz 1997; Hoos 1999); probSAT, memoryless and the strongest simple rule on
  random k-SAT (Balint and Schöning 2012); focused Metropolis search (Seitz, Alava and Orponen 2005) and ChainSAT's
  chain-following (Alava et al., PNAS 2008), the published precedent for "follow what you just broke"; configuration
  checking, a memory of which neighbourhoods changed (Cai, Su and Sattar 2011 for vertex cover; Cai and Su 2013 for SAT); clause
  weighting (breakout, Morris 1993; SAPS, Hutter, Tompkins and Hoos 2002; PAWS; DDFW), a memory of where violations recur.
- Learned or evolved search for SAT: Yolcu and Póczos (NeurIPS 2019), variable selection by a graph network trained with
  REINFORCE, fewer flips than WalkSAT on small instances, a much higher cost per step, and an advantage that shrank with size;
  Interian and Bernardini (KR 2023, *Learning Interpretable Heuristics for WalkSAT*, checked), linear learned variable scores
  and noise with a random unsatisfied clause chosen first; Graph-Q-SAT (Kurin et al., NeurIPS 2020), learned CDCL branching
  that cut iterations two- to threefold and generalized to larger instances, without a wall-clock gain; NeuroSAT (Selsam et
  al., ICLR 2019); NeuroCore (Selsam and Bjørner, SAT 2019), unsat-core predictions periodically resetting CDCL activity, which
  solved more instances within time limits; NLocalSAT (Zhang et al., IJCAI 2020), learned initial states; ANYCSP (Tönshoff et
  al., IJCAI 2023), learned global search with recurrent memory; Fukunaga's evolved local-search heuristics (CLASS) and
  SATenstein (KhudaBukhsh et al., IJCAI 2009), automated assembly of local-search parts.
- Policy search and structure: evolution strategies as an alternative to gradient reinforcement learning (Salimans et al.
  2017); learned network structure by mutation (NEAT, Stanley and Miikkulainen 2002), for the second stage; neural algorithmic
  reasoning (Veličković and Blundell 2021).
- Instances: quiet planting in random constraint problems including NAE-SAT and colouring (Krzakala and Zdeborová 2009);
  rigorous NAE-3-SAT threshold bounds (Achlioptas and Moore 2002) and the cavity estimate near 2.105 (Castellani et al. 2003;
  Dall'Asta, Ramezanpour and Zecchina 2008). Near the threshold the planted ensemble may differ from the random one; the study
  is about planted instances only.

What is not found: a learned **choice of which violated clause to attend to**, jointly with the variable choice and with step
memory, compared with tuned hand-written rules at charged training cost, and tested for transfer to larger sizes and another
constraint structure. In the work found (a short search, checked: Interian and Bernardini), the clause is drawn at random.
What would be new here is that measurement and its answer, not the method, which is focused local search with a learned
policy.

## Settled by construction (stated, not tested)

- Flipping any distinction of a violated knot satisfies that knot, so every step is useful locally; the choices differ in what
  they violate elsewhere and in where they lead.
- With output weights zero the learned agent chooses uniformly; training starts from the random agent (first layers random, so
  the evolution signal is first order).
- The memoryless "what" scorer can express probSAT-like and WalkSAT-like preferences (a score falling with break), so a working
  learner should at least approach probSAT at its training size; the gate below makes this a condition of reading any loss.
- A local pattern with window 10 has bandwidth at most 20, so exact search by dynamic programming is linear in n there; plain
  exact search is cheap on `local` by construction, and that family tests only the transfer of the learned policy against the
  hand-written ones. Its knots meet about twice as often per distinction as `rand`'s (degree 12 against 6.3), so that transfer
  changes density as well as meeting pattern.
- The learned agent costs more per flip than probSAT, since it reads its where-candidates' breaks (incidences, counted) and
  evaluates two small networks per step (CPU, measured; about 10 times probSAT per flip in a timing check).

## Arms

All local-search arms run in one C engine (`nae_engine.c`) with the same data structures; each instance's run seed, and so its
initial state, is the same for every arm.

| Arm | Where | What | Memory | Tuned or trained on |
| --- | --- | --- | --- | --- |
| A0 random | uniform violated knot | uniform | none | nothing (context, n = 200 only) |
| A1 WalkSAT | uniform | zero-break flip if any, else noise p, else least break | none | p |
| A2 probSAT | uniform | P ∝ (1+break)^−cb or cb^−break | none | form and cb |
| A3 Novelty+ | uniform | least break − make, age tie-break, Novelty+ rule | ages | p and walk probability |
| A4 greedy-where | least min-break among the agent's candidates (noise q) | probSAT-poly | none | q and cb |
| A6 sticky | a just-violated knot with probability q, else uniform | probSAT-poly | last step | q and cb |
| A7 focused Metropolis | uniform | uniform, accepted with probability η^(break − make) when that is positive; a rejected try is a step | none | η |
| A5 CaDiCaL | exact CDCL (CaDiCaL 1.9.5 via PySAT) on the CNF encoding (two clauses per knot, one unit fixing the complement); context only | | | none |
| L1 | uniform | learned | none | ES |
| L2w | learned | probSAT-poly, the tuned cb | none | ES |
| L2 | learned | learned | none | ES |
| L3 | learned | learned | ages, ranks, recent counts, recurrent state | ES |

Out of scope, with the reason: clause-weighting algorithms that score every variable (SAPS, PAWS, DDFW), and survey
propagation, which are not focused local search; the learned agent's recent-visit count is the focused analogue of a clause
weight.

**Training (L1, L2w, L2, L3).** OpenAI-ES: 32 antithetic pairs, σ = 0.1, centred ranks, Adam with step 0.05, from output
weights zero. Curriculum on `rand` training instances (a pool of 2,000 per size, generator seeds disjoint from every test):
120 iterations at n = 200 (16 instances per iteration, cap 60,000 flips), 100 at n = 400 (16, cap 300,000), 40 at n = 800 (32,
cap 1,500,000), the caps about 20 times the calibrated probSAT median. All members of an iteration share instances and run
seeds. Fitness: −mean log(flips), an unsolved run scoring log(cap) + log(1 + least violated count reached). In the last stage
the mean weights are scored every 10 iterations, and at the end, on 64 fixed validation instances at n = 800 (cap
1,500,000); the best are kept. Two independent ES seeds per arm; the arm's policy is the seed with the better validation
score, and both trainings are charged.

**Tuning (A1–A4, A6, A7).** Two comparators.
- *Training-tuned*: grids scored on 64 training instances at n = 800 (the learner's selection size), cap 1,500,000, by the
  learner's objective; CPU charged. This is the symmetric transfer comparison.
- *Re-tuned per cell*: at each test size, each rule's five grid values nearest its training-tuned optimum scored on 16 tuning
  instances of that cell (disjoint seeds), cap equal to the cell's cap; at `rand` n = 12800 only the two best rules at n = 3200.
  This comparator decides the real-win rule.
In each test cell the comparator is the best hand-written rule in that cell, chosen after the fact and chosen again inside every
bootstrap resample.

## Test cells

Unseen instances (generator seeds disjoint from training, validation and tuning), one run per instance per arm, the same flip
cap for every arm in a cell.

| Family | n | Instances | Flip cap | Arms |
| --- | --- | --- | --- | --- |
| `rand` α = 2.1 | 200 | 100 | 10^6 | A0, A1–A4, A6, A7, L1, L2w, L2, L3 |
| `rand` α = 2.1 | 800 | 100 | 10^7 | A1–A4, A6, A7, learned |
| `rand` α = 2.1 | 3200 | 100 | 2·10^8 | A1–A4, A6, A7, learned (**primary cell**) |
| `rand` α = 2.1 | 12800 | 50 | 2·10^9 | two best rules at 3200, both comparators, learned (long run) |
| `local` α = 4.0, w = 10 | 200, 800, 3200 | 100 each | 10^6, 2·10^7, 4·10^8 | A1–A4, A6, A7, learned |
| `rand` α = 2.1 | 200, 400, 600 | 20 each | 600 s | A5 (context; n = 600 is a long run) |

**Measures.** Median flips and the fraction solved within the cap (a median is reported only where at most half the runs are
censored); run-length curves (fraction solved at fixed flip budgets); incidences touched and CPU per flip and per instance; the
ratio R = median flips of L3 / median flips of the best hand-written rule, with a paired bootstrap interval over instances
(10,000 resamples, the best rule chosen again in each); M = L3 / L2 (memory) and W = L2w / L2 and L2 / L1 (learned where).
Diagnostics of where: per where-step, the number of distinct candidates and whether a just-violated knot was available and
taken; if the median distinct count is at most 2, the report says that where was not really tested. Cost: the marginal cost
per instance (incidences and CPU), and the break-even count N* = training cost / per-instance saving against the re-tuned
best rule (infinite when there is no saving); the hand-written rules' tuning is charged the same way, and their decades of
human design are not.

## Predictions (frozen)

| # | Prediction | Probability | Fails when |
| --- | --- | --- | --- |
| G | Engine gate: on 200 small instances every reported solution satisfies every knot and every planted instance is a base (brute force); incremental counts equal recomputation over 60,000 random flips; at zero weights the agent's what-choice has the random agent's run-length law (KS); a break-preferring probSAT mutant is slower; every CaDiCaL model checks and an unsatisfiable control is refuted. | — | any fails |
| G-learn | Learner gate: L1's validation median flips at n = 800 at most 1.15 times the training-tuned probSAT's on the same instances. If it fails, the verdict is "learner failure", never "clean loss". | 80% | above 1.15 |
| P2 | At n = 200 (unseen), R lies in [0.7, 1.1]. | 70% | outside |
| P3 | No flips win on `rand`: R > 0.8 at n = 3200 (primary) and at n = 12800. | 70% | R ≤ 0.8 at either |
| P4 | A flips win on `local`: R ≤ 0.8 at n = 3200, against the best rule including the sticky rule. | 30% | R > 0.8 |
| P5 | Memory helps somewhere: M ≤ 0.9 on at least one of the three headline cells. | 45% | M > 0.9 on all three |
| P6 | L3 costs at least 5 times probSAT's CPU per flip at `rand` n = 3200. | 90% | less than 5 times |
| P8 | Plain exact search is costly here: CaDiCaL's median CPU at `rand` n = 600 is at least 10 s and at least 100 times the best local rule's. | 75% | either fails |
| P9 | No degradation with size: R at `rand` n = 12800 is at most 1.2 times R at n = 200. | 55% | above 1.2 |
| P10 | No marginal-cost win: on the primary cell L3's median CPU per instance exceeds the re-tuned best rule's, so N* is infinite there. | 90% | L3's is lower |

**Decision rule** (primary cell `rand` n = 3200, against the re-tuned comparator). *Real win*: R ≤ 0.8 with the 95% interval's
upper end below 0.9, **and** L3's median CPU and incidences per instance both below the best rule's, with N* stated.
*Mechanism win*: the flips condition holds and the marginal-cost condition does not. *Clean loss*: the interval's lower end is
above 0.9 (and G-learn passed). *Inconclusive*: otherwise. The secondary cells (`rand` 12800, `local` 3200) are read the same
way with 98.3% intervals. The memory question is answered separately: M ≤ 0.9 with the upper end below 1 on some headline cell,
memory helps; every interval inside [0.9, 1.1], memory inert. Expected overall: a clean loss or at best a mechanism win on
`rand`, a possible mechanism win on `local` (wall-following), and no marginal-cost win anywhere.

**Publication hold.** Nothing here can give an efficient general method for SAT: the instances are planted and the method is
local search. As a pre-specified check, the slope of log median flips against log n over `rand` n = 800, 3200, 12800 is fitted
for L3 and for every rule; if L3's slope is smaller than every rule's by at least 0.5, the thread tells the owner before
committing that result.

## Runs and stop rule

Calibration before freezing (disclosed): probSAT, WalkSAT, Novelty+ and CaDiCaL on 6–8 instances per cell chose α = 2.1 for
`rand` (hardest of 2.0–2.15 for local search at n = 800 and 3200) and α = 4.0, w = 10 for `local` (the hardest tried, flips
growing faster than n); a 20-iteration trainer smoke on an earlier engine checked the code. The trainings (eight ES runs) are one
registered long run with the shared runner (MemoryMax 16G); the test cells except `rand` n = 12800 and CaDiCaL at n = 600 are
the pilot, committed marked "stress test pending"; those two are long runs folded in when they finish. The study stops at the
decision rule; a second stage (changing knot structures, the owner's mutation; or the nested patterns of
`DIRECT-REACH-20261115-001` as a family with exact ground truth) is chosen only from its result.
