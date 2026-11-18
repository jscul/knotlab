# Is bond distance a metric? Pre-registration

Epic `BOND-METRIC-20261118-001` (the coordinator's go-ahead on `FREE-READ-20261118-001`'s direction 2; G1 and G16; tests A97; B200),
18 November 2026. Frozen before the run. Code by the thread (Claude); the run through the shared runner. The canonical K1–K3 test is
unchanged.

## The question, and what was found while designing it

Bond distance b(x, y) is the size of the least set holding x and y on which the allowed states, everything else forgotten, form a
knot (a bond: constrained, every set of one fewer free), minus one; it is infinite when no bond holds them. Is it a metric on every
base: b(x, z) ≤ b(x, y) + b(y, z) for every three distinctions, an infinite left side against a finite right side counting as a
failure?

No. While designing the study I found that it fails on the smallest base that could fail: two not-all-equal knots sharing two
distinctions, {a, b, c} and {a, b, d}. Each third is one knot from a shared distinction (b(c, a) = b(a, d) = 2), but no bond holds c
and d (T2 below). It also fails where knots meet at most once (the mixed four-knot system on six distinctions that the literature
calls the Pasch configuration; pure not-all-equal on eight distinctions with five knots), and with a finite left side (pure
not-all-equal on ten distinctions: 5 > 2 + 2). It holds on every parity base (T1) and on every knot tree (`FREE-READ-20261118-001`).
This study proves those, shows that among three-place laws only parity gives a metric on every base built from copies of one law
(with the advisor's exhibits), measures the smallest failures by census, finds the smallest not-all-equal failures where knots meet
at most once, and checks that the failing pairs are tied by correlation though no bond holds them.

Conventions: the triangle inequality is checked on three distinct distinctions; a base with no allowed state is left out (it has no
K3); a law's pattern p has bit i for its place i (places 0, 1, 2).

## In standard terms

Bonds are the minimal non-shattered sets of the family of allowed states. On parity bases they are the circuits of a binary matroid,
and "x = z or x and z lie on a common circuit" is an equivalence relation (Whitney; Oxley, *Matroid Theory*, Prop. 4.1.2), proved
inside the union of the two circuits. For general set families the relation "lie in a common minimal non-shattered set" need not be
transitive. `KNOT-CIRCUITS-20261020-001` proved that a Boolean law composes like cycles (its bonds satisfy circuit elimination in every
system) exactly when it is affine.

## Prior work in the program

`python3 -B scripts/track.py objects "bond distance triangle inequality metric" --until 2026-11-18 --exclude BOND-METRIC-20261118-001`
`python3 -B scripts/track.py objects "knots compose like cycles circuit elimination matroid" --until 2026-11-18 --exclude BOND-METRIC-20261118-001`
`python3 -B scripts/track.py objects "two knots sharing two distinctions common hub bonds" --until 2026-11-18 --exclude BOND-METRIC-20261118-001`

- `FREE-READ-20261118-001` — same object: bond distance; steps apart + 1 on every knot tree (so a metric there); its referee proved
  the parity case and found b − 1 failing where bonds of two exist; the referee's 400-base check left out pairs no bond holds
  (Narrowing, `50647493f`). This study starts from that narrowing.
- `KNOT-CIRCUITS-20261020-001` — relative: Boolean laws compose like cycles exactly when affine; knot hubs for every other law with
  knots. T1 uses its direction "composes like cycles ⇒ matroid".
- `RULER-20261111-001`, `RULER-FLAT-20261111-001`, `LONG-LOOP-20261111-001` — relatives: bond distance on not-all-equal weaves (steps
  apart + 1 on the endless weave; a cutoff on closed weaves).
- `KNOTS-ALONE-20261111-001` — relative: bond distance two between every two distinctions of not-exactly-one weaves.
- `CUMULANT-DIST-20261118-001` — relative: bond distance minus one equals the cumulant distance on parity bases (its D1, matroid
  connectivity), the same matroid fact T1 uses.
- `DISTANCE-ORDER-20261117-001`, `TREE-STEPS-20261118-001`, `MEET-ORDERS-20261118-001` — unrelated (matched on words).

## Settled by construction (proofs in ticket A)

- **T1. Where bonds compose like cycles, bond distance is a metric, and so is bond distance minus one.** Constrained sets are
  closed upward, so bonds are the minimal constrained sets, an antichain, and the free sets are the sets containing no bond. If the
  bonds of a base satisfy circuit elimination, they are therefore the circuits of a matroid whose independent sets are the free sets
  (the circuit axioms; `KNOT-CIRCUITS-20261020-001` has the same). Let x, y lie
  on a least bond C₁ and y, z on a least bond C₂. In the restriction of the matroid to C₁ ∪ C₂, whose circuits are the bonds inside
  C₁ ∪ C₂, x is connected to y and y to z, so x and z lie on a common circuit C₃ ⊆ C₁ ∪ C₂ (connectivity is an equivalence relation).
  Then b(x, z) ≤ |C₃| − 1 ≤ |C₁| + |C₂| − 2 = b(x, y) + b(y, z). b is infinite exactly between different connected parts, so the
  inequality holds with infinities too. Moreover C₃ ≠ C₁ ∪ C₂ when C₁ ≠ C₂, since C₁ ∪ C₂ properly contains the circuit C₁; so
  |C₃| ≤ |C₁| + |C₂| − 2, which is the triangle inequality for b − 1 (the advisor's observation; if C₁ = C₂ it holds as |C| ≥ 2).
  b − 1 is zero between the two members of a bond of two (parallel elements), so it is a pseudometric. Every parity base qualifies
  (its bonds are the minimal supports of sums of its checks). ∎
- **T2. Two not-all-equal knots sharing two distinctions.** On the base {a, b, c}, {a, b, d}: each knot is a bond, so
  b(c, a) = b(a, d) = 2. A set holding c and d but not a is free: given any values on it, set a to differ from b, and both knots
  hold whatever c and d are (likewise without b). So a bond holding c and d contains a and b, hence the knot {a, b, c}, a constrained
  proper subset, unless it is that knot, which lacks d. So no bond holds c and d, and the inequality fails. Their correlation is 1/5:
  of the ten allowed states, the two with a = b have c = d and the eight others leave c and d free. In the doctrine's words, c and d
  meet only through the shared pair, a common hub of the two knots, never one touch. Switching c and d turns both knots into copies
  of one betweenness law, so betweenness fails on four distinctions too. ∎
- **T3. The clause "not all ones".** On any base of such clauses, a set is constrained exactly when it contains a whole clause
  (`FREE-READ-20261118-001A`, C), so the bonds are the clauses. Two clauses sharing a distinction give b = 2 from it to each other
  distinction of either clause, and b infinite between their two private distinctions when no clause holds both: the inequality
  fails on two clauses sharing two distinctions (four distinctions), and on two sharing one (five, knots meeting once). Switching
  the two private distinctions gives the twisted clause (forbid one pattern with two ones), which fails the same way. ∎
- **T4. R6 ("if place 2 is 1, places 0 and 1 agree").** On R6(a; b, c), R6(d; b, c) (a and d in the switching place), a set without
  b is free (set b equal to c) and likewise without c, so a bond holding a and d contains the knot {a, b, c}: no bond holds them,
  while b(a, b) = b(b, d) = 2. On R6(a; b, c), R6(a; d, e) (five distinctions, knots meeting once) no bond holds b and d. Switching c
  gives the twisted R6 ("if place 2 is 1, places 0 and 1 differ"), failing the same way. (The advisor's bases; checked.) ∎
- **T5. R5 ("not exactly two ones").** R5 is a closure law: the allowed states are the sets of ones closed under "two ones of a knot
  force the third", and a set is free exactly when none of its members lies in the closure of the others. On the eight distinctions
  a, b, f₁, g₁, c, f₂, g₂, d with knots {a, b, f₁}, {a, b, g₁}, {f₁, g₁, c}, {a, b, f₂}, {a, b, g₂}, {f₂, g₂, d} (34 allowed states),
  {a, f₁, c} and {a, f₂, d} are bonds, so b(c, a) = b(a, d) = 2. A bond S holding c and d has S − c and S − d free; with T = S − {c, d},
  if T holds a or b it is that one alone (any second member closes to everything) and {a, c, d} is free; otherwise T holds at most
  one of f₁, g₁ and one of f₂, g₂ (else c or d is closed), and then every subset of S is the trace of its closure, so S is free. So no
  bond holds c and d. Switching a, c and d (each knot holds exactly one of them) gives the twisted R5, failing the same way. Two R5
  knots sharing two distinctions do not fail: given a = 1, c = d, so {a, c, d} is a bond. (The advisor's base and argument; checked.) ∎
- **Consequence.** The 34 three-place laws passing K1–K3 form nine languages under reordering places and switching every value at
  once (the operations that turn a base of copies of one law into a base of copies of another with the same bonds; switching one
  place is not among them): parity, and two each from the other four classes (not-all-equal and betweenness; the clause and the
  twisted clause; R5 and its twist; R6 and its twist). By T1 to T5, **bond distance is a metric on every base of copies of one
  three-place law exactly when the law is parity**, the same line as `KNOT-CIRCUITS-20261020-001`'s "a Boolean law composes like
  cycles exactly when it is affine". Whether "metric on every base" and "composes like cycles" coincide for every law is open (the
  advisor sees no uniform construction: a gadget's bonds through auxiliary distinctions can reconnect the pair, as R5's small
  bases do).

## Exploration disclosed

Before the freeze (scratch code, then the frozen code's smoke test): every base on four and five distinctions with at most three
knots and on six with at most four, under the six program laws (parity of either constant, not-all-equal, the three betweenness
forms), with and without the condition that knots meet at most once; every base meeting at most once on seven distinctions with at
most three knots; every three-place law passing K2 on five distinctions with at most three knots meeting at most once; parity bases
on six distinctions with at most four knots (both b and b − 1); random bases (3,000 meeting at most once, 1,500 pure not-all-equal,
1,500 parity, 2,000 under all 34 laws) on six to ten distinctions; the FREE-READ referee's 400 random bases recounted; the four
exhibits checked with the referee's code; the advisor's R5, R6 and twisted exhibits checked with this study's code (T4, T5). The
smoke test read six cases of the frozen job: not-all-equal and the clause on four distinctions with two knots, R5 on five with two
knots (no failure), the 3 × 3 weave (no failure), 400 of the 1,050 five-knot not-all-equal systems meeting at most once on seven
distinctions (no failure), and parity on five distinctions with three knots. One shard of R6 on seven distinctions was timed without
reading its result.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): bond distance against FREE-READ's separate search on 150 random bases of all 34 laws; the four exhibits read with the FREE-READ referee's code; the eight languages' exhibits (T2 to T5) and R6 meeting once; 34 laws in 9 languages; parity bonds equal the minimal supports of sums of checks; the violation finder on a planted case; the 34 laws in 5 classes; the correlations 1/5 and the exact test | any fails |
| P1 | Every parity base (either constant on each knot) on four to seven distinctions with at most four knots (all distinctions used), and 2,000 random parity bases on 8 to 12 distinctions: b satisfies the triangle inequality on every triple (T1's check) | any failure |
| P2 | The same bases: b − 1 also satisfies it (T1's check) | any failure |
| P3 | For each of six languages, not-all-equal, betweenness, the clause, the twisted clause, R6 and the twisted R6, built from copies of its law placed in any order of places, the smallest failing base is two knots on four distinctions (the least possible) | any of the six without a failure there |
| P3b | (advisor) The two R5 languages have no failing base on at most six distinctions with at most four knots (their failure, T5, needs eight and six) | a failure in that range |
| P4 | No pure not-all-equal base on seven distinctions whose knots meet at most once (any number of knots, 4,125 systems) fails | any failure |
| P5 | No pure not-all-equal base on eight distinctions with at most four knots meeting at most once fails (the exploration found failures with five) | any failure |
| P6 | Every failure with an infinite long side under pure not-all-equal (P3's language, P4, P5 and the tori) has the long pair correlated, by the exact test N·Σ s_x s_z ≠ Σ s_x · Σ s_z | some such pair uncorrelated |

Recorded without prediction: the languages on seven distinctions, and each language's smallest failing base whose knots meet at
most once; every not-all-equal base meeting at most once on eight distinctions
(up to eight knots), with each failing base's shortest ring of knots; not-all-equal on the two-fold tori 3 × 3, 3 × 4, 4 × 4 and
4 × 5 of the six-regular weave; 2,000 random bases of the six program laws on six to nine distinctions, split by whether the knots
meet at most once.

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 814 cases (parity bases in 119 shards, 40 random parity cases, the eight languages in 632 shards,
19 not-all-equal cases meeting at most once, 4 tori, 40 random mixed cases); `merge.py` scores; about 20 minutes on 8 workers. Registered as BOND-METRIC-B1. One run; no
change after seeing results; later looks labelled post hoc. Stop at the read-out, the proofs, the referee hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` was asked before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2). It confirmed T1 to T3, proved that b − 1 is a metric too
wherever bonds compose like cycles (now in T1), gave the failing bases for R6 and R5 and the twisted languages (T4, T5; checked here),
corrected the unit from five classes to nine languages, expected R5 to pass within six distinctions and four knots (P3b), asked for
exact arithmetic in P6 and for the conventions above, saw no uniform construction for "metric on every base ⇒ composes like cycles"
for general laws, and knew no literature on the triangle inequality for minimal non-shattered sets (nearest: shattering-extremal
families; closure systems for R5).
