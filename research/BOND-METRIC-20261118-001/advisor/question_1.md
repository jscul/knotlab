You are advising a research thread before it freezes a study. Work only from what is written here; you have no files or tools. Please check the mathematics and the design, and be concrete.

Setting. A "base" is a set of three-place Boolean constraints ("knots") on n variables ("distinctions"); its allowed states are the assignments satisfying every knot. A set S of variables is FREE when the projection of the allowed states onto S is all of {0,1}^S, CONSTRAINED otherwise. A BOND is a constrained set all of whose (|S|-1)-subsets are free (a minimal non-shattered set). Bond distance b(x,y) = (size of the least bond containing x and y) - 1, infinite if none. Question: is b a metric (triangle inequality, infinite left side vs finite right side counting as a failure)?

The draft pre-registration follows. My specific questions are after it.

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
This study proves those, asks which three-place laws give a metric on every base built from copies of them (expected: only parity),
finds the smallest not-all-equal failures where knots meet at most once, and checks that the failing pairs are tied by correlation
though no bond holds them.

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
- `DISTANCE-ORDER-20261117-001`, `TREE-STEPS-20261118-001`, `MEET-ORDERS-20261118-001` — unrelated (matched on words).

## Settled by construction (proofs in ticket A)

- **T1. Where bonds compose like cycles, bond distance is a metric.** If the bonds of a base satisfy circuit elimination, they are
  the circuits of a matroid on its distinctions whose independent sets are the free sets (`KNOT-CIRCUITS-20261020-001`). Let x, y lie
  on a least bond C₁ and y, z on a least bond C₂. In the restriction of the matroid to C₁ ∪ C₂, whose circuits are the bonds inside
  C₁ ∪ C₂, x is connected to y and y to z, so x and z lie on a common circuit C₃ ⊆ C₁ ∪ C₂ (connectivity is an equivalence relation).
  Then b(x, z) ≤ |C₃| − 1 ≤ |C₁| + |C₂| − 2 = b(x, y) + b(y, z). b is infinite exactly between different connected parts, so the
  inequality holds with infinities too. Every parity base qualifies (its bonds are the minimal supports of sums of its checks). ∎
- **T2. Two not-all-equal knots sharing two distinctions.** On the base {a, b, c}, {a, b, d}: each knot is a bond, so
  b(c, a) = b(a, d) = 2. A set holding c and d but not a is free: given any values on it, set a to differ from b, and both knots
  hold whatever c and d are (likewise without b). So a bond holding c and d contains a and b, hence the knot {a, b, c}, a constrained
  proper subset, unless it is that knot, which lacks d. So no bond holds c and d, and the inequality fails. Their correlation is 1/5:
  of the ten allowed states, the two with a = b have c = d and the eight others leave c and d free. In the doctrine's words, c and d
  meet only through the shared pair, a common hub of the two knots, never one touch. ∎
- **T3. The clause "not all ones".** On any base of such clauses, a set is constrained exactly when it contains a whole clause
  (`FREE-READ-20261118-001A`, C), so the bonds are the clauses. Two clauses sharing a distinction give b = 2 from it to each other
  distinction of either clause, and b infinite between their two private distinctions when no clause holds both: the inequality
  fails on two clauses sharing two distinctions (four distinctions), and on two sharing one. ∎
- **Consequence.** Parity gives a metric on every base (T1); not-all-equal and the clause fail on four distinctions (T2, T3). The two
  other classes of three-place laws passing K1–K3 (34 laws in five classes up to reordering places and switching values: parity,
  not-all-equal, the clause, "not exactly two ones" R5, and "if the third place is 1 the first two agree" R6) are computed (P3). If
  both fail, then among three-place laws, bond distance is a metric on every base of copies of one law exactly for parity, the same
  line as `KNOT-CIRCUITS-20261020-001`'s "composes like cycles exactly when affine".

## Exploration disclosed

Before the freeze (scratch code, then the frozen code's smoke test): every base on four and five distinctions with at most three
knots and on six with at most four, under the six program laws (parity of either constant, not-all-equal, the three betweenness
forms), with and without the condition that knots meet at most once; every base meeting at most once on seven distinctions with at
most three knots; every three-place law passing K2 on five distinctions with at most three knots meeting at most once; parity bases
on six distinctions with at most four knots (both b and b − 1); random bases (3,000 meeting at most once, 1,500 pure not-all-equal,
1,500 parity, 2,000 under all 34 laws) on six to ten distinctions; the FREE-READ referee's 400 random bases recounted; the four
exhibits checked with the referee's code. The smoke test read six cases of the frozen job: the not-all-equal and clause classes on
four distinctions with two knots, R5 on five with two knots (no failure), the 3 × 3 weave (no failure), 400 of the 1,050 five-knot
not-all-equal systems meeting at most once on seven distinctions (no failure), and parity on five distinctions with three knots.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): bond distance against FREE-READ's separate search on 150 random bases of all 34 laws; the four exhibits read with the FREE-READ referee's code; parity bonds equal the minimal supports of sums of checks; the violation finder on a planted case; the 34 laws in 5 classes; the correlation 1/5 | any fails |
| P1 | Every parity base (either constant on each knot) on four to seven distinctions with at most four knots (all distinctions used), and 2,000 random parity bases on 8 to 12 distinctions: b satisfies the triangle inequality on every triple (T1's check) | any failure |
| P2 | The same bases: b − 1 also satisfies it (not proved; bonds of two are parallel elements there) | any failure |
| P3 | Each of the four other classes, built from copies of one of its relations placed in any order of its places, fails on some base of at most six distinctions and four knots; for not-all-equal and the clause the smallest failing base is two knots on four distinctions | a class without a failure in range, or another smallest base for those two |
| P4 | No pure not-all-equal base on seven distinctions whose knots meet at most once (any number of knots, 4,125 systems) fails | any failure |
| P5 | No pure not-all-equal base on eight distinctions with at most four knots meeting at most once fails (the exploration found failures with five) | any failure |
| P6 | Every failure with an infinite long side under pure not-all-equal (P3's class, P4, P5 and the tori) has the long pair correlated, \|C\| > 0 | some such pair uncorrelated |

Recorded without prediction: the classes on seven distinctions; every not-all-equal base meeting at most once on eight distinctions
(up to eight knots), with each failing base's shortest ring of knots; not-all-equal on the two-fold tori 3 × 3, 3 × 4, 4 × 4 and
4 × 5 of the six-regular weave; 2,000 random bases of the six program laws on six to nine distinctions, split by whether the knots
meet at most once.

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 498 cases (parity bases in 119 shards, 40 random parity cases, the four classes in 316 shards, 19
not-all-equal cases meeting at most once, 4 tori, 40 random mixed cases); `merge.py` scores. Registered as BOND-METRIC-B1. One run; no
change after seeing results; later looks labelled post hoc. Stop at the read-out, the proofs, the referee hand-off and the report.

Questions.
1. Check T1 carefully. Is "bonds satisfy circuit elimination => they are the circuits of a matroid whose independent sets are the free sets" right as stated (bonds form an antichain; non-freeness is upward closed)? Is the restriction argument (connectivity inside M|(C1 u C2)) a correct citation of the transitivity proof?
2. Check T2 and T3. Any gap?
3. Is there a general theorem here: for a constraint language (set of relations) L, "b is a metric on every base built from L" <=> "L composes like cycles (bonds satisfy elimination in every base)"? The direction <= is T1. For => : given a base whose bonds fail elimination, can you always build (from copies of L, perhaps with extra knots) a base where the triangle inequality fails? Sketch a proof or a counterexample. If the honest answer is "unclear", say so and suggest the cheapest discriminating computation I could add.
4. P2: on binary matroids (parity bases), is the least circuit through x and z at most |C1|+|C2|-2 when C1 contains x,y and C2 contains y,z (x not in C2, z not in C1)? Known? Prove or give a counterexample. My exploration found no failure on parity bases of six variables with up to four knots.
5. P3: do you expect R5 ("not exactly two ones": allowed 000,001,010,100,111) and R6 (allowed 000,001,010,011,100,111, i.e. "if the third place is 1 then the first two agree") to fail within six variables and four knots? Can you give an explicit failing base for either? Note two R5 copies sharing two variables do NOT fail (the thirds c, d satisfy c = d when a = 1, giving the bond {a, c, d}).
6. P4/P5: any reason pure not-all-equal bases whose knots pairwise share at most one variable should have no failure on 7 variables (Fano-plane subsets) but fail on 8? The failing example: knots (0,4,6),(1,2,7),(0,3,7),(2,5,6),(1,3,5) on 8 variables: b(1,0)=3, b(0,4)=2, no bond holds 1 and 4.
7. P6: is "every infinite failure under pure NAE has the long pair correlated" plausible, or is there an easy uncorrelated example?
8. Literature: any known result on the triangle inequality, or transitivity of "lying in a common minimal non-shattered set", for general set families / CSPs? Any name for this distance?
9. Any prediction you would change, add or tighten before the freeze? Keep it short.
