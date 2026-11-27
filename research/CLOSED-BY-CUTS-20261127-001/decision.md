# Under the forbidding cuts, does growth close a stage that carries the step one layer up? What stands

`CLOSED-BY-CUTS-20261127-001`. Frozen in commit 7167b99346. Results are in `out/`. Referee pending.

**Answer: growth under the cuts does close stages, but only small ones, and none carries the step.** Every census
start (7,075) was grown for at most six rounds under each rival law.

| Under | Closed after growth | Their knots | Closed at the start | Stalled | Funded at round 6 |
| --- | --- | --- | --- | --- | --- |
| A129, a join takes one fresh distinction fewer | 171 (149 after round 1, 22 after round 2) | 4 to 9 (6 in 117) | 230 | 5,857 | 817 |
| A130, only what its arity needs | the same 171 | the same | 230 | 5,857 | 817 |

- **K1 failed narrowly.** 171 of 7,075 is 2.4%, against a frozen bound of 2%.
- **K2 held.** No stage closed by growth has twelve or more knots. The largest has nine knots and fifteen distinctions.
- **K3 held.** The full search finds no box on any of the 171 (nor, therefore, one needing a birth).

The two laws differ only in when some starts stall (rounds 1 and 3), not in which starts close.

**Reading.** Boxes need a closed system of at least twelve three-place knots: none on 117 closed systems with fewer, 49
of 85 with twelve, and none survives one cut. Ordinary growth never closes a connected stage. The cuts close only stages
of at most nine knots within six rounds on census starts. So no growth law recorded makes the step one layer up on the
starts read. Whether larger starts under the cuts close at twelve or more knots is not run.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: closure by the forbidding cuts | **Status:** STOP (K2, K3 held; K1 failed at 2.4%) | The cuts close small stages only; none carries a box |
| Local direction: the step one layer up made by growth | Not reached on the starts read | Needs closure at twelve or more knots; no recorded law gives it on census starts |
| Long-term goal: G17 with G18 | Obstruction learned | The second step is a property of closed systems of twelve knots, which growth on small starts does not reach |

**Next step:** Research directions (the coordinator's call; the law between parity and not-all-equal waits for the owner).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Larger starts under the cuts: sampled starts of 10 to 14 knots, grown to closure; search those closing at twelve or more knots | 3/3 | 2/3 | 1,000 seeded starts per size → a growth-made box, or the closed sizes by start size | Proposed |
| 2 | Which twelve-knot closed systems carry boxes (49 of 85): a structural rule | 2/3 | 3/3 | Compare the 49 with the 36 by girth, connectivity and automorphisms → a rule, or none | Proposed |
| 3 | A third layer on larger closed systems (sampled cubic graphs of 14 to 18 points) | 3/3 | 1/3 | Search upper clauses forming a product pattern → one, or a size bound | Proposed |

**Corrections:** none.
**Goals:** checkpoint row added (G17, G18).
**Assumptions:** none added (A129, A130 and A309 cover the laws and the box form).
**Scaffolds:** the six-round limit (not swapped), the census as the population of starts, the box form (A309).
**Advisor:** not consulted (usage limit).
