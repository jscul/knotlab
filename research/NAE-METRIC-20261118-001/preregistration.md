# Where not-all-equal bond distance is a distance: pre-registration

Epic `NAE-METRIC-20261118-001` (the coordinator's go-ahead on `BOND-METRIC-20261118-001`'s direction 2; G1 and G16; tests A97 and
A39; B200), 18 November 2026. Frozen before the run. Code by the thread (Claude); the run through the shared runner. The canonical
K1–K3 test is unchanged.

## The question, and what was found while designing it

`BOND-METRIC-20261118-001` proved that bond distance b (the least bond holding two distinctions, minus one; infinite when none) is a
metric on every base of copies of one three-place law only for parity, and that two not-all-equal knots sharing two distinctions
already break it. The go-ahead: under not-all-equal, the owner's case, find a condition on how the knots meet that makes bond
distance a true distance, prove it if possible, and say whether tonight's grown bases (lines, two-order grids) satisfy it.

While designing it I found, and the advisor checked, that the question splits along the knots' blocks. On every complement-closed
base (the complement of every allowed state is allowed: every base of not-all-equal and betweenness knots, of any arity), a
distinction that separates the knots makes b − 1 add across it, and b between two distinctions on one side is that side's own. So b is
a metric on the base exactly when it is one on every block. Single knots and rings of knots are metric blocks (proved); two knots
meeting twice are not. Tonight's grown lines and grids put every pair in a knot of three, so b ≤ 2 there: a metric, trivially.

## Terms

A distinction y **separates** a base when its knots split into two nonempty groups whose distinctions meet only in y. The **primal
graph** joins two distinctions that share a knot; its biconnected components are the **blocks** (each knot lies in exactly one), and
its cut vertices are exactly the separating distinctions. A **ring** is a cycle of m ≥ 3 knots, each sharing one distinction with
the next and having one distinction of its own. A base is **graph-like** when each distinction lies in at most two knots and knots
meet at most once; its knots are then the vertices of a graph whose edges are the shared distinctions (the knot graph). Steps apart is
the number of knots on a least chain between two distinctions.

## In standard terms

Bonds are minimal non-shattered sets of the allowed states. For parity bases the bond structure at a separating distinction is the
parallel connection of matroids (Brylawski 1971; Oxley, ch. 7), whose circuits are those of the two sides and (C₁ ∪ C₂) − y; the
statement here is the same for complement-closed relations. The join over a separating distinction is the lossless join of an
acyclic scheme (Beeri, Fagin, Maier and Yannakakis 1983). Series-parallel graphs are those with no K4 minor (treewidth at most 2).

## Prior work in the program

`python3 -B scripts/track.py objects "bond distance triangle inequality metric not-all-equal blocks" --until 2026-11-18 --exclude NAE-METRIC-20261118-001`
`python3 -B scripts/track.py objects "pairs in no bond overlap faithful not-all-equal weaves" --until 2026-11-18 --exclude NAE-METRIC-20261118-001`
`python3 -B scripts/track.py objects "split bases lines grids betweenness growth" --until 2026-11-18 --exclude NAE-METRIC-20261118-001`

- `BOND-METRIC-20261118-001` — same object: where bond distance is a metric; this study asks the base-level question under
  not-all-equal that it left open.
- `FREE-READ-20261118-001` — knot trees: b − 1 = steps apart; recovered here as the case where every block is one knot.
- `OVERLAP-READ-20261111-001` — relative: some pairs at distance two in no bond at all, in overlapping bases.
- `RULER-20261111-001`, `RULER-FLAT-20261111-001`, `LONG-LOOP-20261111-001` — relatives: on weaves b = steps apart + 1 (the endless
  weave; closed weaves below a cutoff), so weaves are metric blocks there.
- `BOND-CHAIN-20261108-001` — relative: chains add nothing where knots compose; gates are hubs (A39).
- `KNOT-ORDER-20261117-001`, `PICK-TWO-20261118-001`, `KNOT-SWITCH-20261118-001` — the grown bases checked in P7;
  `GRID-GROW-20261117-001` — relative: grows the grid's cut system with betweenness knots (a grown base of the same kind, not run here).
- `KNOTS-ALONE-20261111-001` — relative: bond distance on not-all-equal weaves (faithful readings, bond distance two and three at
  graph distances one and two).
- `RANDOM-FATES-20261112-001` — unrelated (uniform not-all-equal growth on fixed distinctions; matched on words).
- `DISTANCE-ORDER-20261117-001` — relative (τ = steps apart on not-all-equal trees). *Added after the freeze:* the prior-work gate
  flagged it at the freeze and the line was missed; no case, reading or prediction depends on it.
- `CUMULANT-DIST-20261118-001` — relative (bond distance minus one equals the cumulant distance on parity bases). *Added after the
  freeze* for the same reason.

## Settled by construction (proofs in ticket A)

- **C1. Bonds at a separating distinction** (the advisor's statement; the thread's Lemmas 1 and 2). On a complement-closed base with
  a state, if y separates the knot groups 𝓛 and 𝓡, the bonds are exactly those of 𝓛, those of 𝓡, and (B_L ∪ B_R) − y for bonds
  B_L of 𝓛 and B_R of 𝓡 that both hold y. Hence, for x on 𝓛's side and z on 𝓡's, b(x, z) − 1 = (b(x, y) − 1) + (b(y, z) − 1),
  infinite when either is; for two distinctions on one side, b is that side's own. It needs only that y take both values on each side
  and that every bond through y miss patterns with both values of y, so it also holds for parity bases where y is not fixed.
- **C2. Blocks.** b is a metric on a complement-closed base exactly when it is a metric on every block (as a base on its own): b − 1
  adds along the cut distinctions (a tree sum), and the triangle inequality for three distinctions reduces to the block where their
  routes meet.
- **C3. Rings.** On a ring of not-all-equal or betweenness knots, plain or twisted, b = steps apart + 1 on every pair. Upper: the
  set of the two distinctions and the third of every knot on the shorter route is a bond (the other arc, with its own distinctions
  free, completes any end values). Lower (the advisor's argument): a bond missing some knot's own distinction is a bond of the chain
  left when that knot is dropped, and a chain's bonds are its runs, so it holds every knot on one route; a bond holding every own
  distinction has at least m + 1 members (the own distinctions alone are free), which is at least steps apart + 2.
- **Corollary.** On every complement-closed base whose blocks are single knots and rings (a cactus of knots), b − 1 is steps apart
  and b is a metric.
- **C4. Split bases.** On a complement-closed state set holding both constant states, b(x, y) = 1 when no state separates x and y,
  and b(x, y) = 2 when some z separated from both has one of the three never alone against the other two; on lines of at least three
  distinctions and on full grids every separated pair has such a z, so b = 2 for every pair. Any function with values in [1, 2] on
  distinct pairs satisfies the triangle inequality, so this is a diameter statement, not evidence on the metric question (the advisor).
- **Known.** Two not-all-equal knots sharing two distinctions fail (`BOND-METRIC-20261118-001`, T2): that block is not metric.

## Exploration disclosed

Before the freeze (scratch code): cut additivity, the block formula and "metric iff every block is" on 1,240 random bases of
not-all-equal-class knots (no exception); pure not-all-equal blocks on at most seven distinctions with at most five knots counted
without distinctions of their own, and on at most six distinctions with at most five knots counted with them (every failing block had
two knots sharing two distinctions); rings of three to eight knots, plain and twisted (b = steps apart + 1 on every pair); 18 growth
runs under six of PICK-TWO's rules (b ≤ 2 at every step). A census of not-all-equal-class blocks crashed before printing and was not
read. The frozen job's case kinds were smoke-tested reading only their keys, and four heavy shards were timed without reading them.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): the split criterion against brute force (200 random complement-closed state sets); the series-parallel test on known graphs; steps on a knot tree; primal blocks equal incidence blocks for three-place knots; four-place states complement-closed and three-place states as before; the ring builder and the two-knot exhibit; the bond count on a two-knot tree | any fails |
| P1 | On 1,000 random bases glued from small pieces at single distinctions (not-all-equal-class knots, four-place not-all-equal knots, and parity knots with no fixed distinction), b − 1 adds across every separating distinction | any separated triple fails |
| P1b | (advisor) At a separating distinction, the number of bonds is #bonds(𝓛) + #bonds(𝓡) + (bonds of 𝓛 through y) × (bonds of 𝓡 through y) | any base differs |
| P2 | On the same bases (three-place), b equals the block formula on every pair; b is a metric exactly when every block is; on 1,000 random pure not-all-equal bases on nine distinctions meeting at most once, the same, and no violating triple spans two blocks | any mismatch |
| P3 | Rings of 3 to 9 knots, plain and twisted: b = steps apart + 1 on every pair, no violation, exactly m(m − 1) bonds missing an own distinction (the runs), every other bond of at least m + 1 members, largest b = ⌊m/2⌋ + 2 (the advisor's) | any fails |
| P4 | 200 random cacti (rings of three to five knots and single knots, glued at single distinctions, mixed not-all-equal-class laws): b − 1 = steps apart on every pair | any pair differs |
| P5 | Every pure not-all-equal block on at most seven distinctions with at most six knots that fails has two knots sharing two distinctions | a failing block with knots meeting at most once |
| P6 | (conjecture) Every graph-like pure not-all-equal base whose knot graph is series-parallel is metric (360 random graph-like bases, plain and twisted) | a plain series-parallel base fails |
| P7 | Tonight's grown bases: at every step of 5 runs under each of PICK-TWO's SEED, ODD, FRESH, NEWCROSS, KEEP, CC, CAP(2), CAP(3) from lines of five to eight and the 2 × 2 grid, and of 6 runs under each of KNOT-SWITCH's KF3, NN, NN2, SEEDK from bracketings of five and six, b ≤ 2 for every pair; the triple criterion agrees with brute force wherever n ≤ 12 | any pair at 3 or more, or a disagreement |

Recorded without prediction: not-all-equal-class blocks (with betweenness) on at most six distinctions and four knots; graph-like
bases by plain or twisted and series-parallel or not; the failure rate on nine sparse distinctions.

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 269 cases (40 glued-base cases, 14 rings, 20 cactus cases, 88 block cases, 9 class-block cases, 30
graph-like cases, 20 sparse cases, 40 PICK-TWO growth cases, 8 KNOT-SWITCH growth cases); `merge.py` scores. Registered as NAE-METRIC-B1. One run;
no change after seeing results; later looks labelled post hoc. Stop at the read-out, the proofs, the referee hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` was asked before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2). It checked Lemmas 1 and 2 and the gluing, strengthened them to
the exact bond structure at a separating distinction (C1) and to the weaker hypothesis covering parity, corrected the definition of a
block to the primal graph (needed for knots of four places), gave the ring lower bound for every pair (C3), suggested the bond count
(P1b), the ring counts (P3) and "no violating triple spans two blocks" (P2), and asked that the split-base result be reported as a
diameter statement. Its H1 (graph-like blocks are metric) is already false: the eight-distinction failure of `BOND-METRIC-20261118-001`
is graph-like (K4 with one edge subdivided, one distinction of its own). P6 is the thread's variant of its H2 and was not put to it.
