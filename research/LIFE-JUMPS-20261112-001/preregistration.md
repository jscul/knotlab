# Jumps over a whole life: pre-registration

Epic `LIFE-JUMPS-20261112-001` (sub-goal B167, from `RANDOM-FATES-20261112-001` direction 1; G17 Typical and rare meeting patterns,
with G7), 2026-11-12, at the coordinator's go-ahead under the owner's standing mandate. Frozen before the registered run. The
canonical K1–K3 test is unchanged. Words as in the guide's glossary and `RANDOM-FATES-20261112-001` (tie class, ends, last base,
move, horizon); **share** is the largest tie class over the distinctions in some knot.

## The question

`RANDOM-FATES-20261112-001` found that uniform knots end in a jump (the largest tie class going from about 1/n to 87 to 89% of the
base over about the last twenty knots, at every n from 50 to 300), while growth that keeps adding distinctions carries large tie
classes long before its end; after its run, ten whole lives per process suggested jumps at random times during life (exploratory,
other seeds). The owner asks what the patterns that "go for a while then die" look like on the way, and senses a limit. Over whole
lives, under fresh seeds: how does the largest tie class grow, does the end come with or without a jump, does the law signal the end
long before, and does living growth with rare closings stay free of a large class?

## In standard terms

For random 3-uniform hypergraph processes under proper 2-colouring, the backbone up to global flip (pairs forced equal or unequal)
along a single realization, from the start to the step at which 2-colourability is lost.

## Prior work (bounded search, 2026-11-12)

Discontinuous backbones at the threshold of random satisfiability (Monasson, Zecchina, Kirkpatrick, Selman and Troyansky 1999; a
simplest model in Ricci-Tersenghi, Weigt and Zecchina 2001), spines that jump (Istrate, Boettcher and Percus 2005), frozen
variables inside clusters and the freezing threshold (Achlioptas and Ricci-Tersenghi 2006; Semerjian 2008; Molloy and Restrepo),
and discontinuous jumps in growing random graphs (explosive percolation; Achlioptas, D'Souza and Spencer 2009) are known. Not
found: the backbone up to flip along one growth of these processes, its course in growth that adds variables, and its use as an
early signal of the end.

## Facts that hold by definition or by proof (checks, not predictions)

- **The largest class's size never falls.** A knot with a new distinction leaves the old distinctions' allowed states unchanged
  (Lemma A of `RANDOM-FATES-20261112-001B`), and a closing knot only removes states; so ties persist and classes only merge or gain
  members. The share can fall as distinctions arrive.
- **A knot with a new distinction ties it iff its pair is tied equal** (then the new distinction is forced opposite to them), and
  merges no classes; so every increase of the largest class by more than one happens at a closing knot. (The advisor model's
  observation, checked by the author: when the pair can be unequal the new distinction takes both values in some state.)
- **The end's hazard is the class profile.** A closing knot ends the growth exactly when its three distinctions lie on one side of
  one tie class, so the chance that a uniform closing ends it is the share of triples on one side of one class (h, recorded at every
  reading, ignoring triples already present).
- **At the last base the ending knot's three distinctions are tied equal** (by definition).

## Design (frozen; `census.py`)

Settings: U(n) at n = 100 (100 runs), 200 (60) and 300 (30), grown until the end; X(0.2) and X(0.3) to 6,000 moves; X(0.35),
O global (0.3) and O local (0.3) to 2,000 moves, 100 runs each; seeds sha256 of "LJ:label:run". Exact tie classes at every 2% of
the life, at 1 to 20, 30, 40 and 50 knots before an end, and after 300, 500, 1,000, 2,000, 3,000 and 6,000 knots.

## Predictions (frozen)

The advisor model (Fable 5.2) reviewed a draft cold, under the owner's rule of 2026-11-12. It judged the draft's "reaches 0.10 by
75% of life" confounded by small numbers and by selecting on ends, the draft's "no final jump" mechanical unless made a contrast,
the median-ratio form of the signal near-vacuous, and the bound for X(0.2) settled by the pilot; these were replaced as below. It
suggested the hazard fact above and the reading that jumps are events in the oldest, densest distinctions (J6).

| # | Prediction | Fails when |
| --- | --- | --- |
| J1 | **Uniform knots: one late jump.** At n = 100, 200, 300: the share is at most 0.05 forty knots before the end in at least 90% of runs, and at least 0.5 at the last base in at least 80%. | any n |
| J1b | **Its length is a number of knots, not a share of life.** The median share ten knots before the end at n = 300 is within a factor of two of that at n = 100. | outside the factor |
| J2 | **Growth that adds distinctions forms its class early.** For X(0.3), X(0.35), O global (0.3) and O local (0.3), among growths that end after at least 200 knots: at half of the life the largest class has at least 10 members and a share of at least 0.05 in at least 60%, in each process. (Survivors are reported beside it.) | any process below 60% |
| J3 | **No final jump, against uniform knots.** The median over endings of the share 20 knots before the end divided by the share at the last base is at least 0.7 in each of those four processes, and at most 0.2 at each n of U. | any setting |
| J4 | **The law signals the end long before.** At X(0.3), among growths still bases after 300 knots (and, separately, after 1,000), the share then separates those that end before 6,000 knots from those that do not with an area under the ROC curve of at least 0.75 at both. (The same for the hazard h is reported.) | either AUC below 0.75 |
| J5 | **Rare closings, no large class.** At X(0.2), the largest class after 6,000 knots has at most 15 members in at least 90% of runs. | below 90% |
| J6 | **The class is old.** For endings of those four processes, the median arrival index of the largest class's members at the last base is below half of the distinctions at the end in at least 80% of endings, in each process. | any process below 80% |

## Pilot (disclosed)

Four growths per setting with seeds 777000 to 777003 (scratchpad), and `RANDOM-FATES-20261112-001`'s exploratory `life_ties.py`
(ten lives per setting, its census's seeds): X(0.2) to 6,000 moves kept classes of 1 to 6; X(0.3) endings rose in jumps to shares of
0.1 to 0.37 well before the end, its one survivor stayed near 0.008; X(0.35) and O(0.3) held 0.1 to 0.5 through most of life. A
smoke test of the frozen code read one growth each of X(0.3), O global (0.3), U(100) and X(0.2) (registered seeds, run 0).

## Stop rule and runtime

One run, its summary, a hand-off to the referee thread, report. About an hour on ten workers; registered in `docs/LONG_RUNNING.md`.
