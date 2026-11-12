# Outcomes of random meeting patterns: pre-registration

Epic `RANDOM-FATES-20261112-001` (G1 Space from a law, question 9; also G6 and G7; program topology, group spacing), 2026-11-12,
from the owner's question of that night, under his standing mandate. This note is committed before the registered run of ticket
A. The canonical K1–K3 test is unchanged.

## Words

The guide's glossary (`publication/knotlab/INTUITIONS.md`, "Glossary") is the reference: distinction, knot, meeting pattern,
knot pattern, base, contradiction, free, bond, bond distance, steps apart, ball, faithful, shortcut. In this record:

- **Tied pair**, as in `OVERLAP-READ-20261111-001`: two distinctions equal in every allowed state, or unequal in every allowed
  state. Being tied is an equivalence, and a **tie class** is one of its classes with two or more members: a largest set of
  distinctions every pair of which is tied. Under not-all-equal nothing is ever frozen (proved there), so a tie class is the
  strongest thing the law can force.
- **Ends.** A growing knot pattern ends at the first knot after which it allows no state (assumption A72 below; the owner's
  "dies"). Its **last base** is the pattern just before that knot, and **k knots before the end** is the pattern with the last k
  knots removed, so k = 1 is the last base.
- **Minimal contradiction.** A set of knots that allows no state while every proper subset allows one; found by deleting knots,
  so it is one of possibly several, and minimal means under removal, not smallest (the literature's minimal unsatisfiable
  subformula).
- **Move and horizon.** A **move** of a growth adds one knot, or nothing when the process has nothing left to add; growth is
  counted in moves, never in steps, which belong to steps apart. The **horizon** is the number of moves computed, and a growth
  **still a base at the horizon** allows a state after that many moves.
- **Step ball.** The distinctions within r steps of one distinction, a count on the meeting pattern; the glossary's ball is
  measured by bond distance.
- **The ruler at d.** Two distinctions d steps apart whose least bond has d + 2 distinctions (bond distance d + 1).
- **Outcomes** of a growth, after the owner's three: it "resolves to nothing" (no state from its first knots), it goes "for a
  while then" ends, or no end is found by the horizon. The third is a limit of the computation, not a property of the growth,
  and "goes on forever" is said only where a proof shows it.

## The question

- **Where it comes from.** The owner, 2026-11-12: different meeting patterns make different bases, and "there are infinite
  possibilities"; "some combinations should resolve to nothing, some can go for a while then die. Others will go on forever and
  create sets like the natural numbers." Nothing chooses a meeting pattern: every one exists, ours is one random draw, and "it is
  indifferent", "purely coincidental". So ask what is typical and what is rare. In a later message he asked what the ones that go
  for a while look like just before they die, said it reminds him of limits, and that the right measures are "just relative to
  each other". The knots-alone line read meeting patterns put in by us (two-fold weaves, periodic bases); this epic reads meeting
  patterns picked at random.
- **The question.** Under the not-all-equal law (NAE) on every knot, grow meeting patterns by several random processes. (a) Which
  outcomes occur under each process, and how often? (b) On the patterns that live, what does the law read: faithfulness, ties,
  bond distance against steps apart, shortcuts, how fast step balls grow, how far forcing reaches? (c) On the bases just before
  the end, and on the way there, do the law's own quantities (the largest tie class, how far ties reach in steps, bond distance
  against steps apart) approach a limit, or jump?

## The question in standard terms

Random 3-uniform hypergraphs under proper 2-colouring (property B; positive NAE-3-SAT). For several random hypergraph processes,
the probability of becoming non-2-colourable within a given number of edges; a minimal non-2-colourable subhypergraph at that point; and, for
the 2-colourings of the hypergraph before it, the backbone up to global flip (pairs forced equal or unequal), and the least
non-shattered vertex set with every proper subset shattered that contains two vertices at hypergraph distance d.

## Prior work (bounded search, 2026-11-12)

- **Known, uniform knots.** Random 3-uniform hypergraph bicolouring and random NAE-3-SAT have a satisfiability threshold near 2.1
  knots per distinction: the one-step replica-symmetry-breaking value 2.107 (average degree 6.32) is unstable for three-place
  knots, so the exact threshold is open; clustering, condensation and the Kesten–Stigum bound coincide at 1.5 knots per
  distinction (average degree 4.5) for bicolouring (Gabrié, Dani, Semerjian and Zdeborová 2017, Table 1; Castellani, Napolano,
  Ricci-Tersenghi and Zecchina 2003). Freezing thresholds for NAE-SAT and bicolouring
  (Molloy and Restrepo), rigidity (Ayre and Greenhill), the clustering transition (Budzynski and Semerjian), condensation
  (Coja-Oghlan and Zdeborová 2012) and the large-k thresholds (Coja-Oghlan and Panagiotou; Ding, Sly and Sun) are known. In a
  minimal contradiction every distinction lies in at least two of its knots, and at any fixed density a uniform pattern almost
  surely has no set of knots that dense on fewer than a constant fraction of its distinctions, so its minimal contradictions are
  a constant fraction of the pattern (the expansion argument behind Chvátal and Szemerédi 1988). Backbones that jump at the threshold are known for random 3-SAT (Monasson, Zecchina,
  Kirkpatrick, Selman and Troyansky 1999), and spines with a discontinuous jump for problems with no implicates of size two
  (Istrate, Boettcher and Percus 2005). The smallest three-place pattern that allows no state is the Fano pattern, seven knots
  (property B, m(3) = 7).
- **Known, other processes.** Spatially coupled chains of random constraint problems have the threshold of the uncoupled model
  (Hassani, Macris and Urbanke 2012). Grown random graphs (Callaway, Hopcroft, Kleinberg, Newman and Strogatz 2001) and random
  2-trees are classical as graphs.
- **Not found.** What the allowed states of random meeting patterns read as bond distance, shortcuts or tie classes against steps
  apart; the outcomes of growth processes other than uniform knots on a fixed set (growth with new distinctions, growth along
  co-knotted pairs with overlap, growth among the newest distinctions); and how the backbone up to flip grows over the last
  knots before the end in a single growth.

The census aims at the last group and states known against new in every result.

## The processes (each one weighting of many, A71)

Knots are sets: a process never makes a knot twice. Distinctions are numbered in order of arrival.

| Name | One move | Fixed or growing |
| --- | --- | --- |
| U(n) | a uniform knot on n distinctions, not yet present | fixed n; grown until it ends |
| X(q) | with probability q a uniform new knot on existing distinctions; otherwise a knot of one new distinction and a uniform pair of existing ones | growing; knots per distinction tends to 1/(1 − q) |
| O global (q) | pick a uniform knot and a uniform pair of it (so a pair is picked in proportion to its knots), then a third distinction: new with probability 1 − q, otherwise uniform over all | growing, with overlap |
| O local (q) | as O global, but an existing third distinction is uniform over those within two steps of the pair | growing, with overlap, closing near the pair |
| newest-w (q) | with probability q a uniform missing knot on the w newest distinctions (nothing if all are knots); otherwise a new distinction with a uniform pair of the w − 1 newest before it | growing; every knot within w consecutive distinctions |
| T | a knot of one uniform existing distinction and two new ones | growing; no cycle of knots (the control) |

Code label for newest-w (q): `L{w}_{q}`. Parameters: U at n = 50, 100, 200, 300 (200 runs each, 60 at 300; a minimal contradiction for every run at n ≤ 200 and the first
5 at 300; the first 30 runs read); X at q = 0.1, 0.2, 0.3, 0.35, 0.5; O global at
q = 0, 0.05, 0.1, 0.2, 0.3; O local at q = 0.05, 0.1, 0.2, 0.3; newest-w at w = 4, 5, 6 and q = 0.3, 0.5, 0.7; 100 runs each, horizon 2,000 moves,
the first 30 read; T 30 runs of 300 moves.

## What holds by definition or by proof, so it is a check, not a prediction

- **C1, the last base.** If knot {a, b, c} ends a pattern, its last base allows only the patterns 000 and 111 on {a, b, c}, so
  a, b and c lie in one tie class, all equal. The census checks this on every last base it reads; a failure is a bug.
- **A knot with a new distinction never ends a pattern** (choose the new distinction's value opposite to an equal pair, or freely).
  So O global (0) and T never end, and every ending is made by a closing knot.
- **Ticket B's proofs, stated before the run** (`proofs/RANDOM-FATES-20261112-001B/`): on every pattern with no cycle of knots,
  NAE reads faithfully and bond distance is steps apart plus one at every distance (so T is a control, C2: every sampled pair has
  least bond d + 2 and no tie); every pattern whose knots each lie within four consecutive distinctions allows a state, so
  newest-four growth never ends (a check, P4a); within five consecutive distinctions all ten knots allow no state, so newest-w
  growth with w ≥ 5 and q > 0 ends with probability one.

## The pilot (disclosed)

Before freezing, a pilot (seeds 0 to 9, different from the registered seeds, code in the session's scratchpad) ran 2 to 10 growths
per process. It showed: U ending near 2.1 knots per distinction; no tie at half and three quarters of the way to the end and the
ruler at d = 1, 2, 3 on every sampled pair there; no tie 50 knots before the end and a tie class of 54 to 167 of 200 distinctions
at the last base, most of it formed in the last 20 knots; X and both O processes still bases at 1,500 moves at small q and ending at
q = 0.3 to 0.35; newest-five and newest-six growth ending within a few hundred knots at q = 0.5 with minimal contradictions of 10
to 17 knots; newest-four growth still a base, with small tie classes and shortcuts. U at 400 distinctions took over ten minutes per growth
and was dropped. The predictions below are informed by the pilot, so they test whether its picture holds on fresh seeds and more
runs; they are not blind.

## Readings (frozen; `fates.py`, `read_base`)

For each base read: the tie classes, exactly (each tie shown by the solver); the largest class and its share of the distinctions
in some knot; how far ties reach (the most steps apart of two tied distinctions, from up to 300 sources) and the median steps
apart of tied pairs; the most knots on a pair. In full readings also: for bases of at most 150 distinctions, every unnamed
hollow triple and faithfulness; for 8 sampled pairs at each of d = 1, 2, 3 steps apart, the least bond containing them, searched
over all distinctions at sizes 2 and 3, at size 4 over all distinctions when the base has at most 600 distinctions and otherwise
over the lens, and up to size min(d + 2, 5) over the lens (the distinctions w with steps(u, w) + steps(w, v) ≤ d + 1, the 40
nearest); step balls to radius 6 from three distinctions. So "least bond d + 2" at d = 3 is lens-relative for its size-5 part,
and beyond 600 distinctions also for size 4. 200 sampled states (random solver phases) only show patterns that occur; every
"does not occur" is a solver refutation.

## Predictions (frozen before the run)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | **Far from the end, uniform patterns read as rulers.** For U at n = 100, 200, 300 and at half and three quarters of the knots at which it ends: no tied pair in at least 90% of the bases, and least bond d + 2 for at least 95% of the sampled pairs at each d = 1, 2, 3. | any (n, point, d) below either share |
| P2 | **The end of a uniform pattern is sudden and global.** (a) 50 knots before the end the largest tie class holds at most 5% of the distinctions in at least 90% of runs, at every n; (b) at the last base its median share is at least 0.4 at n = 100, 200, 300; (c) at k = 1, 5, 10, 20 knots before the end, the median share at n = 300 is within a factor of two of that at n = 100 (or both are at most 0.05), so the end takes a fixed number of knots, not a fixed share of them. | each part separately |
| P3 | **Uniform endings are global.** The median minimal contradiction has at least half of the knots at which the pattern ends, at n = 100 and 200 (that it is a constant fraction is known; the size of the fraction is the new number). | either n below one half |
| P4 | **Outcomes by process.** (a) newest-four growth and O global (0) are still bases at the horizon in every run (a check of the proofs); (b) newest-five and newest-six growth at q = 0.5 and 0.7 end before the horizon in at least 90% of runs; (c) X is still a base at the horizon in at least 80% of runs for q ≤ 0.2 and in at most 20% for q ≥ 0.35; (d) O global and O local at q = 0.3 are still bases at the horizon in at most 20% of runs. | each part separately |
| P5 | **Endings among the newest distinctions are local; growth with overlap ends globally.** (a) For newest-five and newest-six endings, the minimal contradiction has at most 20 knots within 20 consecutive distinctions in at least 90% of them; (b) their last bases have a largest tie class of at most 40 distinctions in at least 90%, and its size does not grow with the age of the pattern (Spearman correlation with the number of distinctions at the end below 0.3); (c) for X and O endings, the largest tie class at the last base holds at least 10% of the distinctions in at least 70% of them. | each part separately |
| P6 | **Living patterns grown with closings anywhere read as rulers with no finite dimension.** For X at q ≤ 0.2 and O global at q ≤ 0.1, still bases at the horizon: least bond d + 2 for at least 90% of the sampled pairs at each d = 1, 2, 3, and the median step ball at radius 3 at least nine times the one at radius 1. | any setting or d below |
| P7 | **Newest-four growth: the law shortens the meeting pattern's distance locally and keeps it linear.** Patterns at the horizon (all still bases) at q = 0.5 and 0.7: (a) at least 30% of the sampled pairs at d = 2 and 3 together have a shortcut (least bond below d + 2); (b) ties reach at most 8 steps in at least 90% of them; (c) the median step ball at radius 6 has at most 60 distinctions. | each part separately |

## Decision rules

- **P1 and P6 hold:** away from the end, random patterns with closings anywhere read as rulers: bond distance follows steps apart,
  and the step balls grow by a constant factor per step, so the law reads no finite dimension (the literature's tree-like
  neighbourhoods). **They fail by shortcuts:** the law's distance is shorter than the meeting pattern's on typical patterns there.
- **P2 holds:** the end is a jump, not a limit: the law's quantities stay small until a fixed number of knots before the end and
  then tie most of the base into one class. **P2(c) fails:** the last stretch is a share of the knots, a gradual approach.
- **P5 holds:** local endings stay bounded however old the pattern is (a limit, in the owner's word), and only processes that
  close anywhere end by tying the whole base.
- **P7 holds:** the one process that never ends with closings reads a line whose law distance is shorter than its steps but whose
  ties stay local.

## Stop rule and runtime

One registered run, then the frozen summary (`census.py --summary`), one referee pass, report. A second stage, if the results call
for one, gets its own frozen addendum before its run. Expected runtime: about one to two hours on 10 workers; registered in
`docs/LONG_RUNNING.md` and run under `systemd-run --user -p MemoryMax=16G -p MemorySwapMax=0`.

## Assumptions

- **A71 added:** each random process is one weighting of many; "typical" means typical under a named process, and growth among
  the newest distinctions comes with the order of arrival.
- **A72 added:** a growing pattern ends when it allows no state; the other reading (it stops producing anything new) waits on the
  owner's answer.
- **Relied on:** A67 (a base is read on sets of at most three distinctions, for faithfulness only; bond distance reads larger sets).

## Recorded alternatives, not tested here

- The owner, 2026-11-12: "each boolean variable could be its own micro infinite series of logic, that's bound to others". A
  living random pattern could stand in for one distinction of a larger one, as the learning line's pieces stand in for knots
  (`NEST-ATOMS-20261110-001`). Not part of this census.
- The owner's operations on harmonies (subtraction, division) and his calculus of limits for logic: not part of this census.
