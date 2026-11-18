# Why does a growth begin with the smallest knot? Pre-registration

Epic `FIRST-KNOT-20261118-001` (the coordinator's go-ahead on `FRESH-COUNT-20261118-001#2`, sub-goal B201; goals G2 and G1;
challenges A105), 2026-11-18. Proofs (ticket A) written before the census; census code (ticket B) written and gated before this
freeze; the census launched by the thread with the shared runner after it. The canonical K1–K3 test is unchanged.

## The question

`FRESH-COUNT-20261118-001` proved that, under the parity law and the cubic study's joining rule, one fresh count for every join must
equal the first knot's size, so a growth is three-dimensional only if its first knot has three places (A105). Is there a reason in
the law, or in the joining rule, why the first knot should be the smallest? The first step the coordinator named: a three-place
against a four-place first knot under one count, apart and sharing one distinction, and the same under the fewest counts. Stop at a
reason that prefers one, or a proof that nothing prefers either.

## In standard terms

Growth of the cycle code of a cover graph by upward closure (the cube condition), from a start of several constraints; which constant
arities admit an infinite closure, and what the least closure does.

## What the rule is given, and what it can do

As in `FRESH-COUNT-20261118-001`: given offline the parity law, the joining rule (groups of any size), one count rule (one count c
for every join, or the fewest counts); read at run time the current pattern; actions: one new junction per group with the chosen
number of fresh distinctions, or a stall. The start is given: two knots, or a small set of knots.

## Theorems written before the run (ticket A), corrected with the advisor before this freeze

`proofs/FIRST-KNOT-20261118-001A/FIRST-KNOT-20261118-001A-P001_two_knots/proof.md`:
- **Lemma 1 (pieces).** A start whose neighbour graph is a matching (lone knots and touching pairs, sharing any number of
  distinctions) grows as independent pieces, one per start knot, each a single seed on that knot's ℓ open distinctions. The rule
  never sees a size, only ℓ.
- **Theorem 2 (one count c ≥ 2).** The growth runs exactly when every start knot has ℓ ∈ {0, 1, c}; otherwise it stalls at the
  earliest r(ℓ, c): 2 if c ≤ ℓ − 2, 4 if c = ℓ − 1 and ℓ ≥ 3, 3 if c ≥ ℓ + 1 and ℓ ≥ 2. A three-place and a four-place first knot,
  apart or sharing one distinction, cannot grow under any one count; sharing two distinctions, they grow at c = 2. Corollary 2.1:
  the same four-place relation, presented as one junction, as two three-place knots through a hidden distinction, or as A and A + B,
  grows at c = 4, 2, 2.
- **Theorem 3 (fewest).** Apart, two knots close (2^a and 2^b). Sharing one distinction, the growth runs forever with exact per-round
  counts per piece (ℓ = 2: t + 1; ℓ ≥ 3: C(ℓ, t) to the top, then 1, then t − ℓ): two copies of ℕ² for every pair of sizes; each top
  of a piece with ℓ ≥ 3 gets one fresh distinction equal to h in every state (a relay). The two is the rule's floor less one.
- **S4 (cheapness).** Each junction multiplies the allowed states by 2^(c − 1).

## Prior work in the program

Searches (`--until 2026-11-18 --exclude FIRST-KNOT-20261118-001`):

`python3 -B scripts/track.py objects "first knot size two knots growth" --until 2026-11-18 --exclude FIRST-KNOT-20261118-001`
`python3 -B scripts/track.py objects "smallest knot first emergence" --until 2026-11-18 --exclude FIRST-KNOT-20261118-001`
`python3 -B scripts/track.py objects "growth from several seeds median graph" --until 2026-11-18 --exclude FIRST-KNOT-20261118-001`

- `FRESH-COUNT-20261118-001` — the same object from one seed (the predecessor): this study extends its Theorems 2 and 4 to starts
  of two knots and asks its direction 2.
- `PICK-TWO-20261118-001` — the betweenness analogue (a cap of d gives d; conservative rules keep the start's number).
- `GROW-FACE-20261110-001`, `CUBE-DOUBLING-20261118-001` — relatives (what growth needs to make the plane; the cheapest betweenness
  growth gains an order at every doubling).
- `GROWTH-LAW-20261107-001` — a relative in words only: "a beginning is a knot" there means the knots of a history's acyclicity; here,
  which knot a growth begins with.
- `LOGIC-AXIS-20261107-001` — the r^D law on ℤ^D, used through the predecessor.
- `COMMON-FOLD-20261112-001`, `RANDOM-FATES-20261112-001`, `BRANCH-DEPTH-20261112-001`, `LIFE-JUMPS-20261112-001`,
  `BRAID-READOUT-20261114-001`, `NAE-SURFACE-20261111-001`, `TREE-STEPS-20261118-001`, `ROW-NEST-20261112-001`,
  `REBASE-KNOTS-20261109-001`, `LOGIC-CIRCLE-20261107-001`, `INVERT-STEP-20261110-001`, `PATH-GROWTH-20261108-001`,
  `HANDLE-EMERGENCE-20261102-001`, `HUB-SURVIVORS-20261029-001`, `PROCESS-CONTACT-20261108-001`, `SPLICE-TREE-20261102-001`,
  `CYCLE-RULER-20261115-001`, `GROW-COIN-20261107-001`, `GROW-PLAIN-20261109-001`, `GROW-NET-20261108-001`,
  `ATOM-LAYERS-20261110-001` — unrelated objects or populations.
- `VARIABLE-OUTPUT-READER-20261118-001` (Codex, another scope) — the reader under mixed counts; not used.

## Prior work outside the program

Birkhoff's representation and the cube condition as cited in `FRESH-COUNT-20261118-001`. Every parity constraint of arity a ≥ 4 is
the projection of a − 2 three-place ones through a − 3 hidden variables (splitting a vertex of a graph into two adjacent ones keeps
its cycle space on the old edges): the three-place constraint is the only parity constraint not so composed. Every parity knot hides
exactly one bit (`EMERGENCE-BITS-20261021-001`).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Five gate checks pass (`checks.py`): a one-knot start replays `FRESH-COUNT-20261118-001`'s single-seed growth; two separate three-place knots close under the fewest counts (the GF(2) test); the two pieces of a touching start never mix; a distinction in three knots is refused; two separate three-place knots under count 3 make two ℕ³ | any fails |
| Q1 | (Theorem 2) every pair of sizes 3 ≤ a ≤ b ≤ 6, apart and sharing one or two distinctions, and the thirteen small starts, counts 2 to 8 (2 to 5 for small starts), nine rounds: survival, stall round and junctions per round exactly as predicted from the open counts alone (`startlib.predicted_uniform`); this holds also for the small starts outside Lemma 1's scope only if the prediction happens to fit, so a mismatch there is recorded and scored | any start in Lemma 1's scope differs (small starts outside it are reported, not scored) |
| Q2 | (Theorem 3) the same pairs under the fewest counts, 30 rounds: apart, closed with C(a, j) + C(b, j) junctions in round j; sharing one distinction, still growing with exactly the predicted junctions per round, one relay per piece with ℓ ≥ 3, each equal to h in every state; no forced distinction | any pair differs |
| Q4 | The thirteen small starts and the pairs sharing two distinctions under the fewest counts, 30 rounds: closed exactly when every demand-0 junction had implied parity; otherwise junctions per round with constant differences over the last ten rounds (so at most quadratic in all); no forced distinction | any differs |
| Q5 | The floor control (floors 2 and 4 in place of three) on four touching starts, 14 rounds: with floor 2, junctions per round constant over the last six rounds; with floor 4, still growing with strictly increasing differences | any differs |

The coordinator's first step is Q1's cells 3 + 4 apart and sharing one (no count runs). The presented four-place knot is Q1's small
starts "single 4", "presented 4: A and B" and "presented 4: A and A+B".

## Runs and stop rule

`job.py` through the shared runner: 313 cases, 7 workers; the slowest (two ℕ⁶ to 6,000 junctions) about 30 seconds; a few minutes
in all. `merge.py` scores G and Q1 to Q5. Stop: one run, its read-out, the proofs, referee hand-off, report.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It found the first form of S2 ("first knots of different sizes never grow
together, apart or touching") false beyond one shared distinction: the condition is ℓ ∈ {0, 1, c}, with counterexamples (a
three-place and a four-place knot sharing two distinctions grow at c = 2; a lone three-place knot beside two touching four-place
knots grows at c = 3); gave the stall-round table; found that S3's proof wrongly called h open and repaired it (Lemma 3), added the
relay (the top's fresh distinction equals h) and the exact per-round counts; said the two of S3 is the fewest rule's floor, not a
finding, and proposed the floor control; strengthened the presentation point (A and A + B: same distinctions, same states, other
growth); and found no reason inside the growth that prefers the three-place knot.

**Exploration disclosed.** Before this freeze the pilot (the same policy and rules) ran every pair of sizes 3 to 5, apart and
sharing one distinction, under counts 2 to 6 and the fewest counts, and ten small starts under the fewest counts, with outcomes as
stated in Theorems 2 and 3 (chains of three knots kept 3 or 4 offshoots per round, the star and the ring of three closed, the ring
of four kept 4); spot checks of `predicted_uniform` on a three-and-four start sharing two distinctions and of the floor control on the
three-and-three start (floor 4: growing differences; floor 2: constant). A full run of the census code was started before the freeze
and stopped before it printed anything. An earlier pilot with the single-seed library's structural implied-parity test gave false
tails for separate knots; the frozen code uses GF(2).
