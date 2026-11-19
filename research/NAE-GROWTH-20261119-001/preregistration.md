# Do loops keep branching under not-all-equal? Pre-registration

Epic `NAE-GROWTH-20261119-001` (the coordinator's go-ahead; goals G17 and G1), 2026-11-19. Written after a pilot (disclosed below)
and the advisor's answer, before the frozen run. The canonical K1–K3 test is unchanged.

## The question

Take the cheapest growth (FRESH-COUNT's complete-round joining policy and fewest counts) and read every junction as
not-all-equal (NAE) on its distinctions instead of even parity, the nearest law that is not parity. The coordinator asks:
- Does a ring still feed itself and grow by a fixed ratio, and is the ratio the same root?
- Does the cluster picture survive, or what replaces it?
- Is bond distance still enough to say who joins whom?

The stopping points are a clear yes with a ratio, a clear no with the reason growth fails, or the point where a law has no
well-defined cheapest growth.

## The definition

The joining policy (candidates through common neighbours, groups, offshoots, demand by lookahead) reads only which junctions hold
which distinctions. The fewest count is max(d, 3 − p, 1), or d when the new junction's constraint is already implied by the old
junctions (`freelib.floored`). Under NAE, implied means that no state allowed by the old junctions makes the new junction's old
distinctions all equal. `naelib` tests this with a SAT solver (pysat's Minisat), one solver per round. NAE on k ≥ 3 places passes
K1–K3 (gate G4), so every junction is a knot.

## What is argued before the run

These are arguments; the run checks them. The decision note writes them out.
- **T1 (the keep clause is K2).** A junction with at least one fresh distinction removes no old state exactly when the law's
  relation is free on every set of all but one of its places, which is K2. So for a knot law the law can enter the growth only
  through "implied". For a law failing K2, no junction is a knot, so the cheapest growth has nothing to make (G4). For one-in-three,
  in addition, no fresh count keeps the old states at the first join (G6).
- **T2 (NAE never implies; the advisor's lemma).** Suppose:
  - every distinction lies in at most two junctions;
  - every junction has at least three places;
  - each parent keeps at least two places outside the new junction.

  Then the new junction is not implied under NAE. The proof colours the lines of the remaining junction graph in two colours so
  that every junction sees both colours. It rests on the classical lemma that a connected graph which is not an odd cycle has a
  2-edge-colouring in which every vertex of degree at least two sees both colours (Bondy and Murty, *Graph Theory with
  Applications*, 1976, §6.1). The policy gives every new junction one distinction from each parent, and every junction has at
  least three places, so no NAE junction is ever implied. The brute-force form is gate G5.
- **T3 (parity implies only the closing top).** A parity junction on loose distinctions is implied exactly when it takes every
  loose distinction of a whole component. In a connected growth that is a junction alone in its round, after which nothing is
  loose. So parity's only implied junction is the top of a closing growth, with demand 0.
- **Consequence.** NAE growth equals parity growth at every round, except that where parity closes at round T, the NAE top takes
  max(0, 3 − p, 1) fresh distinctions and relays. Its tail is a junction with one or two loose distinctions. That grows the
  down-closed sets of two endless chains, with k junctions at round T + k (one fresh at the top, p ≥ 2) or k + 1 (two fresh,
  p = 1).

## Pilot (disclosed)

Under both laws, to 14 rounds or 3,000 junctions:
- **Identical** on two touching knots, a chain of three, the ring of five (bare, one spare per knot, 4,4,4,4,5, five five-place
  knots) and the bare two-ring join.
- **Lone knots.** Parity closes them; NAE relays them with tails 1, 2, 3, ….
- **Census shards.** Three shards (300 arrangements) and the first 30 one- and two-knot arrangements were run for timing. No NAE
  junction was implied. The parity collisions of part B in those 30 were all state collisions; four had no redundant junction,
  and each of those had different next joins.

## Method

- **Part C (census).** All 26,441 touch-census arrangements (arrlib; connected, one to five knots of three to five places), grown
  by both laws to 14 rounds, 3,000 junctions or 120 s. Every implied junction is logged, together with the lemma's hypotheses
  (fewest places, most distinctions one parent gives, fewest places a parent keeps).
- **Part P (pilot starts).** The starts named in the go-ahead (the ring of five with one spare per knot, a spare-less ring, a
  chain, a two-ring join) and five others, to 20,000 junctions.
- **Part B (bond distance).** Every stage of the NAE growth from the census arrangements of one to four knots with at most 15
  distinctions (to 8 rounds). For each stage, under both laws, the run records:
  - the exact bond-distance table (bondlib, BOND-METRIC's definition: least non-free set holding both distinctions, minus one);
  - the redundant junctions, those whose removal leaves the allowed states unchanged;
  - who joins whom in the next round (each new junction's parents).

  Two distinct presentations (stars different up to renaming) **collide** under a law when their tables agree up to renaming.
  A collision is a **state collision** when the allowed states also agree up to renaming, searched over the tables'
  isomorphisms. BOND-NEXT-JOIN's reader is run as a control outside its proved family.

## Prior work in the program

`python3 -B scripts/track.py objects "cheapest growth under not-all-equal law rings ratio closure relay" --until 2026-11-19 --exclude NAE-GROWTH-20261119-001`
`python3 -B scripts/track.py objects "bond distance tables determine junctions next joins not-all-equal parity collisions" --until 2026-11-19 --exclude NAE-GROWTH-20261119-001`

- `FRESH-COUNT-20261118-001`, `CLUSTER-ALL-20261119-001`, `JOIN-GROWTH-20261118-001`, `RING-PAIR-20261119-001`,
  `ROUND-FREE-20261119-001`: the same growth under parity only. This study changes the law.
- `FIRST-KNOT-20261118-001`: relative. "The same relation grows differently by presentation", under parity. Part B measures this
  for both laws.
- `BOND-NEXT-JOIN-20261117-001`, `RING-READ-20261118-001`: relative. Under parity and in their families, bond tables recover the
  junctions and the next joins. Part B asks the same question under NAE for the fewest-count family.
- `NAE-METRIC-20261118-001` (bonds at a joint, rings b = steps + 1), `DISTANCE-INFO-20261117-001` (NAE bond tables do not
  determine general NAE relations from four distinctions), `CUMULANT-DIST-20261118-001`: related objects, the same words.
- `DISTANCE-ORDER-20261117-001`: related object (pair disagreement counts determine every NAE base from four distinctions; on
  knot trees steps apart). *Added after the run, at the close, when `track.py objects-gate` named it; it bears on part B as an
  alternative to bond distance (direction #2), and no design choice depended on it.*

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | Every census arrangement with no parity-implied junction has identical counts and outcome under NAE | any differs |
| P2 | Every arrangement whose parity growth closes (one implied junction, its last round T) has NAE counts equal through T, then k at round T + k (the top took p ≥ 2 distinctions) or k + 1 (p = 1), alive at the horizon, with a tail of at least three rounds | any differs |
| P3 | No NAE junction is implied anywhere (SAT); every junction has ≥ 3 places, one parent gives a new junction exactly 1 distinction, and every parent keeps ≥ 2 places outside | any implied, or a hypothesis fails |
| P4 | Every parity-implied junction is the closing top: one per growth, at its last round, demand 0 | any other |
| P5 | The pilot starts are identical under both laws, ratios included (bare ring 5 per round, golden ratio on the five-place ring, 2.6075 on the two-ring join), except the lone knots, whose tails follow P2 | any differs |
| B1 | On tree stages (no cycle of junctions) the two laws' tables are equal | any differs |
| B2 | Some stage with a cycle has different tables under the two laws | none differs |
| B3 | Under NAE, every collision of distinct presentations is a state collision (the table loses nothing the allowed states keep) | any collision with different states, or undecided |
| B3c | The same under parity | as B3 |
| B4 | Every NAE collision has a redundant junction on one side | one has none |
| B5 | Under NAE, colliding presentations with no redundant junction have the same next joins (vacuous if B4 holds) | any differs |
| B5c | Under parity, some colliding pair with no redundant junction has different next joins (expected to fail as a statement of determination: the same states, presented differently, join differently) | none such |

B5c is stated as a positive prediction: such a pair exists. The pilot already shows four. The full stages test whether they remain
the only kind of failure.

## Runs and stop rule

`job.py` through the shared runner (283 cases, 6 workers), with `checks.py` as gates (G1–G6 pass); `merge.py` scores. The run takes
a few minutes and is registered. Stop at the read-out. The stopping point the go-ahead names is "a clear yes with a ratio", unless
P1 or P5 fails.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- **Law-blind.** It confirmed that the growth is law-blind except at implied junctions, for every law passing K2 (T1).
- **The lemma.** It gave T2 with its proof, a counterexample to my weaker argument (a six-place junction on the lone knot's six
  loose distinctions is implied), and the "swallow" case.
- **The tail.** It proposed the tail form (P2) and asked me to say why 1, 2, 3, … arises from "two chains". The answer is that the
  tail is the down-closed sets of two chains, ℕ², with k + 1 sets of size k.
- **Bond distance.** It said "who joins whom" is identical by construction, since the policy reads incidence. It advised
  computing NAE bond tables only if the record claims something about them. Part B does make that claim: whether tables determine
  the next joins.
- **Laws.** It warned that one-in-three and majority are not knot laws (G4, G6). It suggested "ones not divisible by 3" as a
  second knot arm, and recommended against it as a confirmation of the same theorem; this study does not run it.
- **Words.** Its point that many-place NAE junctions hide little (log2(2^k / (2^k − 2)) bits) is recorded in the note.
