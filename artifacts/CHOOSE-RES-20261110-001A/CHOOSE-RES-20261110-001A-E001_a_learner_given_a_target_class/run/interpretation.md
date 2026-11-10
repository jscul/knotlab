# Interpretation of CHOOSE-RES-20261110-001A-E001

Exploratory, against the frozen contract and the pre-registration (`research/CHOOSE-RES-20261110-001/preregistration.md`).

- **Q1 (proved bound) holds as data.** On torus(N, 1, 1) the class change across the short circumference has lower bound 2 and the two
  others about N / 2 (20 and 21 at 40 points); every cheapest walk meets its bound within a few sign changes.
- **Q2 held in part.** C7, told a target class, reached it in 3,173 of 3,186 runs (99.6%): every target on all 19 thin tori, 147 of 150
  and 150 of 150 on the two Fano tori, 170 of 180 on the grown tori. All 13 misses resolved, into another class: the greedy second hole
  entered the over-agreeing face in the wrong sheet. Its mean cost was within twice the cheapest walk everywhere, and on the thin tori
  within 0.4 of it: at 40 points 8.3 for the short class (cheapest 8.1) and 20.7 and 21.2 for the long ones (cheapest 20.6 and 21.0).
  One size past (42 to 46 points) C7 reached all 450 targets.
- **Q3 failed.** Without a target, learners do not default to the short class. On the 11 thin tori of at least 20 points, random moves
  (R0) ended in the short class in 71 of 550 runs (13%) and in each long class in about 44%; sight of radius 3 (R3) in 348 of 550 (63%).
  One size past, R0 16 to 20% and R3 42 to 58%. The outside-distance rule of `LEARN-HANDLES-20261109-001` took the short class in 96 to
  99%. So which resolution an untargeted learner reaches depends on how it moves, and random learning mostly goes the long way around.
- **Q4 failed.** On the grown tori C7 missed 10 of 180 targets (all one class change) and needed up to 19 sign changes. Post hoc, not
  pre-registered: C7', which refuses to enter the over-agreeing face in the wrong sheet when another move exists, reached all 180.

Answer to B62: a learner given a target class can choose its resolution, at a cost close to the cheapest walk, which on a thin torus is
about half the torus for a long class against a few steps for the short one; the misses came from entering the target face in the wrong
sheet, which refusing that move removes. Without a target the resolution reached is set by how the learner moves.
