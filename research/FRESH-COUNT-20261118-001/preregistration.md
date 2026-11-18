# Can a growth rule read its own dimension from distances? Pre-registration

Epic `FRESH-COUNT-20261118-001` (the coordinator's go-ahead, 18 November 2026; goals G2 and G1; tests A97; a relative of A101),
2026-11-18. Proofs (ticket A) written before the census; census code (ticket B) written and gated before this freeze; the census
launched by the thread with the shared runner after the freeze. The canonical K1–K3 test is unchanged.

## The question

Under the parity law, `CUBIC-FROM-A-KNOT-20261117-001` grew a pattern whose bond balls grow as r³ from one knot, and its referee
noted that the three is put in by the law: every join takes three fresh distinctions. Here the joining policy is kept and the number
of fresh distinctions of every new junction is left to a **count rule** that reads only the current pattern (through its bond
distances: no names, no history). Which counts keep the policy running? What does each natural count rule build, and what is
typical, rare or forced? Does any criterion read from distances (for instance the stall at four) single out a number without being
told one? A proved "no, and here is why" is as welcome as a yes.

## What the rule is given, and what it can do

The coordinator asked that this be explicit, since the content of `TWO-PROBE-ALIGNMENT-20261118-001` turned out to sit there.

| | |
| --- | --- |
| **Given offline** | The parity law (every junction allows exactly the even assignments of its distinctions). The joining policy of `CUBIC-FROM-A-KNOT-20261117-001`, with groups of any size, or capped at three as in the original (a control). One count rule from the menu below. For the distance-only reading: the threshold reader of `BOND-NEXT-JOIN-20261117-001`, run up to the largest junction. |
| **Read at run time** | The current bond-distance table of all current distinctions. Nothing else: no names, no growth history, no round number (the menu's rules use only the current pattern; the crossed start below is the one exception and says so). |
| **Actions** | Each round, for every group the policy names, one new junction on one loose distinction of each member, plus the number of fresh distinctions the count rule chooses (0 allowed only where the junction's parity is already implied, so that no old allowed state is lost). A round in which some junction is in more groups than it has loose distinctions is unavailable: a stall. |

## Words (advisor's suggestions, adopted for this study)

- **Offshoot**: a junction with exactly one parent (the junction the policy gives a loose distinction of its own; the literature's
  *join-irreducible element*). Replaces "singleton".
- **Demand** of a new junction: the number of joins of the next round that take a distinction from it (computable from the
  pattern after the round).
- **Surplus distinctions**: the fresh distinctions of a junction beyond its demand; each becomes an offshoot next round.
- **Descent order**: the offshoots, one below another when the second descends from the first; its **breadth**, the most offshoots
  none of which descends from another (the literature's *width*). Breadth is not the dimension: the dimension (lesson 4.6) is how
  fast balls grow, and it can be smaller than the breadth.

## The count rules

- **uniform c**: c fresh distinctions at every join.
- **fewest**: the demand; at least three distinctions per junction (the program's smallest knot); at least one unless the parity is
  implied; at an implied junction none (fresh distinctions there would have a forced parity; openness wins over the floor).
- **axis**: the demand, and one surplus distinction at every offshoot.
- **inherit max / inherit min**: the largest or smallest count among the junction's parents.
- **balance**: as many fresh distinctions as old ones taken.
- **blind K**: uniform on 1..K, chosen without looking.
- **surplus q**: the demand, plus one surplus distinction with probability q at every junction whose demand is positive.
- **crossed start**: fewest, except that the junctions of round a − 1 get one surplus distinction each (it reads the round number:
  a designed start, not a rule).

All rules except blind and uniform are floored (three distinctions per junction, one fresh unless implied).

## Theorems written before the run (ticket A)

`proofs/FRESH-COUNT-20261118-001A/FRESH-COUNT-20261118-001A-P001_free_count/proof.md`, checked by the advisor (below):

- **T1 (the descent order decides the pattern).** If no round stalls, the pattern after round t is the literature's distributive
  lattice of ideals of the descent order, truncated at size t: junctions are the ideals, parents are lower covers, round is size.
  The groups of the next round are the lower covers of the ideals of size t + 1; the demand of an ideal I is the number of minimal
  offshoots outside it; every surplus distinction is a new offshoot directly above I. A count below the demand stalls the next
  round. A new junction's parity is implied exactly when it takes every loose distinction, exactly when its demand is 0.
- **T2 (one count for every join).** From one knot on a distinctions, a single count c keeps the policy running exactly when c = a,
  and then it builds a counting chains' product (the literature's orthant ℕ^a). Otherwise it stalls at round 2 (c ≤ a − 2), 4
  (c = a − 1) or 3 (c ≥ a + 1).
- **T3 (the cap of three).** With groups of at most three, one count keeps it running exactly when c = a = 3. The capped and uncapped
  policies agree on a round exactly when no ideal of the next size has four or more maximal elements.
- **T4 (fewest).** From one knot on a distinctions the fewest counts build the 2^a pattern (the literature's Boolean lattice; the
  a-cube's meeting pattern: every junction a distinctions) and stop: the last junction's parity is implied. Under the fewest counts
  an offshoot whose demand is 1 starts a chain of offshoots that never ends and no other offshoot is ever created, so from any
  hand-over the number of offshoots per round is constant: the number of offshoots of the first round with demand 1. The crossed
  start keeps a chains for every a.
- **T5.** Bond balls of the a-fold product are of order r^a for every a ≥ 3.
- **T6.** For one count a ≥ 3 the threshold reader recovers every junction from bond distances.

## Prior work in the program

Searches (all `--until 2026-11-18 --exclude FRESH-COUNT-20261118-001`):

`python3 -B scripts/track.py objects "fresh distinctions per join" --until 2026-11-18 --exclude FRESH-COUNT-20261118-001`
`python3 -B scripts/track.py objects "growth rule dimension from bond distances" --until 2026-11-18 --exclude FRESH-COUNT-20261118-001`
`python3 -B scripts/track.py objects "distributive lattice order ideals join-irreducible" --until 2026-11-18 --exclude FRESH-COUNT-20261118-001`
`python3 -B scripts/track.py objects "parity junctions grown from one knot" --until 2026-11-18 --exclude FRESH-COUNT-20261118-001`

- `SHARED-REPORT-CANCELLATION-20261115-001`, `BRANCH-DEPTH-20261112-001`, `TWO-BIT-ROWS-20261112-001` — unrelated (fresh witness
  distinctions in proofs; bond depth of recursive branches; not-all-equal generations).
- `RULER-20261111-001` — a relative: bond balls of an endless weave grow quadratically; here the exponent of the parity product.
- `COUNT-BALLS-20261118-001` — a relative: whether a count's ball growth reads the number of orders of split bases; here parity and
  bond distance.
- `STATE-RULES-20261117-001` — a relative: under betweenness, fewest-knot growth from one knot makes Q3 at 8 and Q4 at 16 and keeps
  going; here, under parity, the fewest counts close one knot into the 2^a pattern and stop.
- `DISTANCE-DIM-20261117-001` — a relative: implication bases' states are an order's down-sets, and their order dimension is read;
  here the grown pattern is itself the down-set structure of the descent order.
- `TREE-STEPS-20261118-001`, `CHEAP-COUNT-20261112-001`, `PICK-TWO-20261118-001` — `PICK-TWO` is the betweenness analogue (a cap of
  d gives d; conservative rules keep the start's number); the others unrelated.
- `PREFIX-END-20261112-001`, `NAE-METRIC-20261118-001`, `MEET-DIST-20261118-001`, `OVERLAP-READ-20261111-001`,
  `MEET-HIST-20261118-001`, `OLD-CORE-20261112-001` — unrelated populations (not-all-equal growth, betweenness lines).
- Not indexed but the direct predecessors: `CUBIC-FROM-A-KNOT-20261117-001` (the policy, three fresh distinctions, r³) and its
  referee's two- and four-distinction variants; `BOND-NEXT-JOIN-20261117-001` (the reader, three fresh distinctions);
  `BOND-METRIC-20261118-001` (bond distance a metric on parity bases); `LOGIC-AXIS-20261107-001A` (r^D on ℤ^D);
  `COPY-READ-20261118-001`'s line summary (betweenness: no rule picks two from nothing).
- **A companion question, not yet run:** `VARIABLE-OUTPUT-READER-20261118-001` (planned, Codex, owned by
  `TWO-PROBE-ALIGNMENT-20261118-001`) asks whether bond distances still identify the joins when either two or three fresh
  distinctions are allowed; its exploratory scout found the fixed-three reader fails after three junctions while no table collision
  appeared through six junctions. This study does not take that question: it uses the reader only where T6 proves it, and records
  the threshold reader's misreads on mixed sizes as a check (P8c).

## Prior work outside the program

Birkhoff's representation theorem in its finitary form (Stanley, *Enumerative Combinatorics* I, Prop. 3.4.3): locally finite
distributive lattices with a least element are the finite ideals of a poset with finite principal ideals. Configurations of a
conflict-free prime event structure (Nielsen, Plotkin and Winskel 1981) are the same object, events being the offshoots. The policy's
valid-set test is the cube condition of median graphs and of the literature's CAT(0) cube complexes (Barthélemy and Constantin 1993;
Chepoi 2000). Order dimension of a distributive lattice is the width of its join-irreducibles (Dilworth 1950). Growth: width w bounds
the number of ideals of size ≤ t by O(t^w); infinite width can give the partition numbers (ideals of ℕ², Hardy and Ramanujan).
Connectedness of minimal cuts when short cycles generate the cycle space: Babson and Benjamini (1999), Timár (2013). Tseitin's law.
What this study adds: the parity growth law of the program is this construction; the count rule's only freedom is where to put
offshoots; the uniform-count, cap and fewest-count theorems; and the answer to the coordinator's question.

## Settled by construction

- Every lookahead rule (count at least the demand) never stalls (T1).
- The census's surplus rule gives surplus only where the demand is positive, so it creates no forced distinction.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Nine gate checks pass (`checks.py`): the policy replays the predecessor's N³ layers and its referee's two- and four-distinction variants; the structural implied-parity test equals GF(2) elimination; the ideal checker passes a grown run and flags two mutants; bond distances by cut enumeration equal those from the allowed states; the reader replays N³'s first rounds; the forced-distinction detector equals GF(2) and finds a planted one; demand at birth equals the multi-parent children formed | any fails |
| P1 | (replay of T2) groups of any size, a = 3..7, c = 1..a + 3, eight rounds: runs on exactly when c = a, with the product's counts C(t + a − 1, a − 1) per round; stalls at round 2, 4, 3 for c ≤ a − 2, c = a − 1, c ≥ a + 1 | any cell differs |
| P2 | (replay of T3) groups of at most three: runs on exactly when c = a = 3; for a ≥ 4 and c = a, a stall at round 4; other c as P1 | any cell differs |
| P3 | Menu from one knot, a = 3..6: fewest closes with counts C(a, j), every junction a distinctions, no forced distinction; axis, inherit max and inherit min give the product's counts every round; balance stalls, at round 2 for a ≥ 4 and within six rounds for a = 3 | any differs |
| P4 | (T1) on every census run that did not stall: no ideal built twice, every parent a lower cover, round = size, no ideal of size below the last round missing | any error |
| P5 | Blind counts uniform on 1..K, K = 2..6, a = 3, 4, 200 runs each: at most 10% have not stalled by round 10 | more than 20 of 200 in some cell |
| P6 | Surplus q = 0.05, 0.1, 0.2, 0.4, a = 3, 4, 200 runs each, ten rounds: no stall, no forced distinction; the number of runs not closed by round 10 rises strictly with q; for q ≥ 0.2 the median number of offshoots in the last round of the runs not closed is at least 3 | any of these fails |
| P7 | (T4) 200 hand-overs (1 to 4 surplus rounds, then fewest for up to 25 rounds): in every run the number of offshoots per round, from the second fewest round on, equals the number of first-round offshoots whose demand is 1; crossed starts a = 3..6: exactly a offshoots in every round after round a, not closed by round 12 | any run differs |
| P8 | The threshold reader: (a) exact on the uniform stages (a = 3 rounds 0–3, a = 4 rounds 0–2, a = 5 rounds 0–1); (b) on the fewest stages of a = 3, 4, exact except the stage after round a − 1, where it also reads the set of all loose distinctions as a junction; (c) on the surplus stages of at most 16 junctions (60 runs), at least one misread | any of (a)–(c) fails |
| P9 | (T3) in every round of every surplus run: the capped and uncapped policies form the same groups exactly when no uncapped group has four or more members | any round differs |

P1–P4, P7 and P9 replay theorems; P5, P6 and P8c are the census's own predictions.

**Exploration disclosed.** Before this freeze the pilot code (the same policy, earlier versions of these rules) ran: uniform counts
for a = 3..6 (stall rounds as T2 and T3); the menu from one knot (as P3, balance at a = 3 stalling at round 5); 30 surplus runs
(T1's check passed); blind counts, 100 runs per cell (alive at round 10: 2 of 100 at a = 3, K = 2, none elsewhere); surplus runs at
q ≤ 0.2 (not closed: 10, 19 and 36 of 60 at a = 3); 60 hand-overs under a fewest rule that still floored implied junctions (which
the advisor showed can create a forced distinction; the frozen rule does not); the reader on small presentations (misreads on 141 of
809 mixed stages). The first conjecture for T4 ("eventually at most two offshoots per round") was refuted before the freeze, by the
crossed start (found by the thread and independently by the advisor), and replaced by T4's constancy theorem.

## Runs and stop rule

One job, `job.py`, through the shared runner: 3,982 cases (uniform 80, menu 20, blind 2,000, surplus 1,600, hand-overs 200,
crossed 4, readers 78), 8 workers, 2G per case, a 900-second case timeout. The slowest cases (the a = 6 and 7 products to 6,000 or
more junctions) take about 100 seconds; the whole run is expected to take 15 to 30 minutes and is registered in the long-running
index. `merge.py` scores P1–P9. Stop: one run, its read-out, the proofs, referee
hand-off, report.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It confirmed T1–T3 and the 2^a construction, refuted the first T4
conjecture with the crossed start and gave the constancy theorem that replaces it, showed T6 does not extend beyond the product,
noted that the floored fewest rule can make a forced distinction at an implied two-parent junction (the frozen rule applies no floor
there), corrected "breadth w gives t^w" (only an upper bound), gave the literature (Birkhoff finitary form, event structures, the
cube condition, Babson–Benjamini) and proposed the words offshoot, demand, surplus, descent order and breadth. It found no
distance-only criterion that picks a number.
