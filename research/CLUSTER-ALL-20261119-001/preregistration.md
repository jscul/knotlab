# Does one cluster rule predict every growth of touching knots? Pre-registration

Epic `CLUSTER-ALL-20261119-001` (`RING-PAIR-20261119-001#1`, the coordinator's go-ahead; goals G17 and G2), 2026-11-19. Written
after a pilot on every census arrangement of up to four knots (disclosed: fitting), before any five- or six-knot arrangement was
compared with the rule. The canonical K1–K3 test is unchanged. "Growth" counts junctions by round.

## The question

`RING-PAIR-20261119-001` found that, in a limited scope, the cheapest parity growth's round-t junctions are the clusters of t + 1
points of the start's unrolled candidate map. Extended to the floor's distinctions, to knots with two common neighbours and to
round-1 groups of three, does one rule predict, round by round, every arrangement of the touch census and one size past?

## The rule (`clusters.py`; found on the pilot)

The rule is as in `RING-PAIR-20261119-001`, with four additions. A live knot w (open distinctions = places − shared ≥ 1) with
round-1 demand d has open − d surplus offshoots, each of demand open − 1.
1. **Pendants.**
   - A leaf when open ≥ 3.
   - An endless chain when open = 2: the floor gives the offshoot one distinction beyond its demand, every round.
   - A point carrying two endless chains when open = 1, unless it holds the start's only loose distinction.
2. **Relay.** A finite piece of the map (a tree of blocks without chains) closes at its top. When other live knots exist, the
   top's parity is not implied, and it carries one more point with two endless chains (`FIRST-KNOT-20261118-001`'s relay).
3. **Merged blocks.** Simplices sharing two or more knots merge into one block, whose clusters are the sets connected through its
   edges (knots with two common neighbours).
4. **Hyperedges.** A round-1 group of three or more knots is one block whose clusters are one knot or all of it, made in one round.

Out of scope: a hyperedge sharing two or more knots with another block. Before the freeze, from the starts alone (no growth
compared), the scope holds 99.5% of the five-knot census: 13,688 predicted to grow or close, 10,695 to stall, 119 out of scope.

Added at the freeze, after the advisor and before any comparison: a finite piece holding a hyperedge tops one round per extra
knot of the hyperedge earlier, so its relay comes earlier too. No pilot start tested this clause; 748 five-knot starts hold a
hyperedge.

**Pilot (fitting, `pilot_census.py`).** Every one of the 1,939 census arrangements of up to four knots was regrown 20 rounds:
- 1,901 equal the rule at every round: 1,212 inside RING-PAIR's scope, 525 with two common neighbours and 164 with hyperedges;
  they include every stall, close and growth;
- 38 are out of scope.

The rule was revised four times on the pilot: implied closure of the single loose distinction; merged blocks; hyperedges; the
series' margin. Each revision is in the pilot's history (`pilot/`).

## Prior work in the program

`python3 -B scripts/track.py objects "dimension of the cheapest parity growth over every small arrangement of touching knots" --until 2026-11-19 --exclude CLUSTER-ALL-20261119-001`
`python3 -B scripts/track.py objects "clusters of the unrolled candidate map exact growth model" --until 2026-11-19 --exclude CLUSTER-ALL-20261119-001`
`python3 -B scripts/track.py objects "connected subgraphs of a cover with pendant chains generating function census" --until 2026-11-19 --exclude CLUSTER-ALL-20261119-001`

- `TOUCH-CENSUS-20261118-001` — the same population (the touch census) and the same growth. This study predicts each
  arrangement's counts, round by round, rather than reading its dimension.
- `PLUS-ONE-20261118-001` — the same population: a chain-birth rule for the dimension, missing ten cases. The cluster rule is
  exact where it applies.
- `JOIN-GROWTH-20261118-001` — the same growth; its 137 recorded starts are test T2.
- `RING-PAIR-20261119-001` — the model this extends; its scope and its 17 fresh starts are gate G4.
- `TRUE-RATE-20261113-001` — unrelated.
- `LEVEL-RETURN-20261113-001` — unrelated.
- `LEIBNIZ-BOARDS-20261110-001` — unrelated.

## Prior work outside the program

As `RING-PAIR-20261119-001` (lattice animals on trees, block-tree dissymmetry, positive algebraic systems), cited once there.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | `checks.py` passes: the pilot replays (1,901 equal, 38 out of scope); hand cases; two mutants differ; RING-PAIR's 17 fresh starts agree | any fails |
| P1 | **T1.** Every five-knot census arrangement (24,502) inside the scope equals the rule at every round regrown (20 rounds, 20,000 junctions or 120 s), stall and close included | any arrangement in scope differs |
| P2 | **T3.** Every one of 2,000 random six-knot arrangements inside the scope equals the rule (one size past; seeds fixed; counts reported per class) | any differs |
| P3 | **T4.** The advisor's falsifiers, hand-built: two triangles sharing one or two knots, a ring of six, a ring of five with unequal surplus and a pendant, partly overlapping simplices (b with no or one surplus), two pieces relaying at different rounds, triangles on single and double shares, a triangle with a pendant knot (out of scope, reported), a ring of seven with two lone knots, three touching five-place knots. Every one inside the scope equals the rule | any differs |
| P4 | **T5.** Every 100th five-knot arrangement that the rule says does not stall (by sorted key; 137), regrown to 45 rounds, equals the rule (the horizon check) | any differs |
| — | **T2**, a consistency check, not a prediction (the chain and relay clauses came from that line): JOIN-GROWTH's 137 recorded starts against the rule | reported |

**What it would mean.** If P1–P3 hold, the census's dimensions follow from each arrangement's map. For example, two-dimensional
growth is two endless chains on one cluster, and the rare three and four come from hyperedges and merged blocks. That reading is
for the note, not a prediction.

## Runs and stop rule

`job.py` through the shared runner (531 shards of 50, 6 workers); `merge.py` scores T1–T3. Under an hour, registered in the
long-running index. Stop at the read-out: every in-scope arrangement predicted, or the first that breaks the rule.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- It explained the 38 out-of-scope starts: with a hyperedge, clusters of one round have unequal sizes, so a clique that is not a
  star can supersede pairs.
- It proposed a set-level rule for them. That rule is not frozen here; it is a direction.
- It asked that the scope fraction be computed before the freeze (99.5%), that the scope predicate be fixed by hash, that T2 be a
  consistency check, that the six-knot sample be reported by class and that the horizon be checked (T5). All are done.
- It gave the hyperedge correction to the relay, now frozen, and the falsifiers of T4.
- It noted that the open = 1 pendant equals a one-point relay; the two clauses agree.
