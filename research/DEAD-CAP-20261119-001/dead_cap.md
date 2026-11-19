# Dead knots within five places: the growth class is the rank of the map

Epic `DEAD-CAP-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-CORES-20261119-001#2`. Goal G17.
**Referee pending.**

**Record.**
- **The proof** (ticket A):
  [proof.md](../../proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead/proof.md). It was frozen as Partial in commit
  `91a132df1`, with its checks D1–D6 stated before the run, then completed.
- **The machine check:**
  [deadlib.py, job.py, merge.py](../../proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead/), run through the shared
  runner (`DEAD-CAP-A1`, `runs/dead-cap`, 51 cases, all ok). Its output is
  [machine_check.json](../../proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead/machine_check.json).
- **A pilot** before the freeze (disclosed) caught one slip: a finished piece's relay counts its spares among its points.
- **A post-hoc refinement** of the fastest rates is in `posthoc_rates.py` and `posthoc_rates.json` in the same folder.
- **The advisor** checked the statements before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **Within five places the whole proved class is now classified, dead knots included.** Draw the map of joins: a point for each
  live knot, and a block for each knot's live neighbours. Count its independent cycles, its rank.
  - **No cycle (a tree):** the growth closes or is polynomial, with dimension equal to the number of endless chains in a piece. A
    finished piece counts two. Any dimension occurs; three or more need a dead knot.
  - **One cycle:** constant if the cycle is bare. Otherwise it is exponential at the root of W(1/x) = 1, where W is a product round
    the cycle that includes the trees hung off it. Its count series is rational.
  - **Two or more cycles:** exponential at an algebraic rate, the singularity of a small system of equations. This needs a dead knot
    and at least 11 knots.
- **Every count is exact.** A short system of equations, one per point and block it sits in, gives each piece's junctions round
  by round. It equals the program's own growth on all 13,307 starts tried, every round:
  - the 10,549 census starts with a dead knot;
  - 1,254 random starts;
  - 1,500 starts built round dead hubs;
  - the families.
- **Why five places shapes the map.** A live knot's places must cover the blocks it sits in, so their sizes sum to at most five.
  - A knot sits in at most two blocks: one of two points and one of two or three, or a single block of up to five.
  - Blocks of three are the only branch points, with at most three ways on.
  - A dead knot spends no place on demand, so it is what lets branches start.
- **The fastest growth within five places.**
  - All-live rings top out at the golden ratio, 1.618.
  - With dead knots, the theta does better. It is two dead three-place hubs, each holding three five-place knots, joined pairwise
    through three connectors: 11 knots in all. It grows at 2.3830, the root of 4z³ + 4z² = 1 read as 1/z.
  - No start in the run grew faster. I conjecture that 2.3830 is the ceiling for the class within five places: the theta's map
    unrolls into the most branched map the cap allows.
- **Where groups of three begin.** Inside the class a block of three is never a group, because its three points share the block's
  knot. A first-round group of three is exactly a cycle of three blocks: three knots pairwise joined through three different
  knots, with none common to all three. This is checked on every small datum. It is where the class ends, and it is the entry point
  for the explosive kind of eddy, which stays next in the basket.

## Theorem and checks

| Statement | Status | Evidence |
| --- | --- | --- |
| Lemma 1: blocks of 2 to 5 points meeting in at most one; groups are candidate pairs; each knot's blocks sum to at most five | proved | D1: 167,349 data on every graph to 6 knots (43,702 in the class), no exception |
| Lemma 2: the skeleton (3-blocks branch, at most 3 ways); the class boundary (no cycle of two or three blocks); rays only at lone points and 2-block ends | proved | D1, including all 15,470 data failing (S3): each has a cycle of three blocks |
| Theorem 3: every piece's count from the branch system with pointing | proved | D2: 13,307 starts, counts equal to the engine on every round reached |
| Theorem 4: the growth class is the rank | proved | D3: dims.predict agrees on all 13,307 |
| Rank-1 rates as the root of W(1/x) = 1, compared numerically with the system's radius | failed as scored (numerics) | D4: 0 of 30 within 10⁻⁶; the radius estimate stops early on a linear system (1.3187 for 1.3247). With 50 times the iterations it agrees to 10⁻⁴, and D2's exact counts carry the denominator 1 − W |
| The theta and T_1–T_3 | proved, computed | D5: in the class; the theta's counts follow the system, and it grows at 2.3830; T_1–T_3 have dimensions 3, 6, 12 |
| No sampled start grows faster than the theta | held (conjecture) | D6: the run's fastest is 2.3830, reached by 133 starts. A post-hoc refinement of the 284 pieces above 2.25 gives at most 2.3829757679, the theta's exact rate |

5 of 6 checks held as scored. D4's failure is in the radius estimator, not the theorem (post hoc).

## Assumptions

- **A109** gets a history line: within five places, every in-class eddy is classified by its map's rank, and every rate is given
  exactly. The out-of-class explosive kind keeps A109 under challenge.
- No new entry.

## Known results, and what this adds

- **Known, cited once.**
  - Animals on Husimi trees and tree-like covers (Harary and Uhlenbeck 1953).
  - The Drmota–Lalley–Woods theorem for positive polynomial systems (Drmota 1997; Lalley 1993; Woods 1997).
  - Analytic combinatorics of such systems (Flajolet and Sedgewick, VII).
- **What this adds.**
  - The cheapest growth within five places, classified on the whole proved class, with every count exact.
  - The rank of the map decides polynomial, constant or exponential growth.
  - A ceiling conjectured at 2.3830 and reached by the 11-knot theta.

## Limitations

- **The ceiling of 2.3830** is a conjecture backed by the sampled starts, not a proof.
- **The random sampler rarely makes cycles** (6 of 1,254). The cycles were tested through the 1,500 skeleton starts and the
  families.
- **Outside the class or the cap** the theorem says nothing:
  - cycles of two or three blocks, where groups of three overlap;
  - knots of six or more places;
  - stalls.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze, staying within its text.
- **It confirmed** the profile bound, the boundary, the pointing (adding torsion-freeness) and the theta's equation.
- **It predicted the theta's rounds 12 and 13 by hand** (8,910 and 18,375). The system gives the same.
- **It argued** rank two needs 11 knots and a dead knot. The run's smallest rank-two start has 11 knots.
- **It corrected** "rational rate" to "rational series, algebraic rate".
- **It listed what to test first,** which the samplers covered.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: dead knots within five places | **Status:** Successful (proved; 5 of 6 checks as scored, D4 an estimator failure) | Shape theorem with a rank rule: trees polynomial, one cycle constant or rational, two or more algebraic; every count exact on 13,307 starts |
| Local direction: what the cheapest growth builds within five places | Research directions | The proved class within five places is classified; the cap's fastest growth is conjectured at the theta's 2.3830 |
| Broader exploration: the eddy catalogue (A109) | Research directions | Inside the class it is complete; the explosive kind outside starts exactly at a cycle of three blocks |
| Long-term goal: G17 | Capability gained | Typical and rare growth within five places is classified on the whole proved class, with exact counts |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The explosive kind (`BREAK-EDDIES-20261119-001`): the first starts past the class, a cycle of three blocks, where groups of three overlap | 3/3 — it decides A109 | 2/3 — the entry point is now exact: one cycle of three blocks | grow the smallest starts holding one cycle of three blocks and read what their groups of three do round by round → stop at a description, or a size where it changes kind | Alternative · proposed |
| 2 | Prove the ceiling: no start in the class within five places grows faster than 2.3830 | 2/3 — a sharp bound on growth from knot size | 2/3 — compare every branch system with the theta's, which is the most branched the cap allows | bound each b_{p,B} by the theta's solution at the same z → stop at a proof, or a start that beats it | Alternative · proposed |
| 3 | Dimension grows linearly under random trees (`WEIGHTINGS-20261119-001#1`) | 2/3 | 3/3 | prove each parity class's chain-carrying leaves concentrate → stop at a proof, or a size where the measured dimension departs | Alternative · in the basket |

## Final report as sent (2026-11-19 17:13 UTC)

**Outcome:** Within five places, the whole proved class is now classified, dead knots included. The growth class is read off how many independent cycles the map of joins has, and a short system of equations gives every count exactly. It matches the program's growth on all 13,307 starts I tried, every round. The fastest growth found is 2.3830, from an 11-knot start with two dead hubs. Closed, referee pending.

- **The shape.** A live knot's places must cover the blocks it sits in, so their sizes sum to at most five. A knot therefore sits in at most two blocks, or in a single block of up to five, and blocks of three are the only branch points. A dead knot spends no place on demand, which is what lets branches start.
- **The rule.**
  - **No cycle:** the growth closes, or is polynomial with one dimension per endless chain, and any dimension occurs.
  - **One cycle:** constant if bare; otherwise exponential, with a rational count series and rate the root of W(1/x) = 1.
  - **Two or more cycles:** exponential at an algebraic rate. This needs a dead knot and at least 11 knots.
- **Every count is exact.** Each piece has one equation per point and block it sits in, and they give the junctions round by round. They match the engine on all 10,549 census starts with a dead knot, 1,254 random starts, 1,500 starts built round dead hubs, and the families, every round.
- **The fastest.** Rings of live knots top out at the golden ratio. With dead knots, the theta does better: two dead three-place hubs whose knots are joined pairwise. It grows at 2.3830, the root of 4z³ + 4z² = 1 read as 1/z. No sampled start beat it, and 133 tied it. I conjecture it's the ceiling for the class within five places.
- **Where groups of three begin.** A first-round group of three is exactly a cycle of three blocks: three knots pairwise joined through three different knots, none common to all. I checked this on every small datum (15,470 that fail S3). It's the exact entry point for the explosive kind.
- **One check failed as scored (D4).** I compared the one-cycle root with a numeric radius estimate. The estimator stops too early on linear systems: it reads 1.3187 where the true root is 1.3247, and agrees to 10⁻⁴ with 50 times the iterations. The exact counts carry the 1 − W denominator, so the theorem stands. The fault is the estimator's, and I've said so as post hoc.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: dead knots within five places | **Status:** Successful (proved; 5 of 6 checks as scored, D4 an estimator failure) | Shape theorem with a rank rule; every count exact on 13,307 starts |
| Local direction: what the cheapest growth builds within five places | Research directions | The proved class within five places is classified; the ceiling is conjectured at the theta's 2.3830 |
| Broader exploration: the eddy catalogue (A109) | Research directions | Complete inside the class; the explosive kind starts exactly at a cycle of three blocks |
| Long-term goal: G17 | Capability gained | Growth within five places classified on the whole proved class, with exact counts |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The explosive kind: the first starts past the class, holding one cycle of three blocks | 3/3 | 2/3 — the entry point is now exact | grow the smallest starts with one cycle of three blocks and read what their groups of three do round by round → stop at a description, or a size where it changes kind | Alternative · proposed |
| 2 | Prove the ceiling: nothing in the class within five places beats 2.3830 | 2/3 | 2/3 | bound every branch system by the theta's, the most branched the cap allows → stop at a proof, or a start that beats it | Alternative · proposed |
| 3 | Dimension grows linearly under random trees | 2/3 | 3/3 | prove each parity class's chain-carrying leaves concentrate → stop at a proof, or a size where the measured dimension departs | Alternative · in the basket |

**Corrections:** one, from the ring study's referee fold (e652e6d5c), reported earlier: a Narrowing. The golden-ratio ceiling is for rings of live knots, and "nothing within five places" was false. **Goals:** G17 checkpoint (capability gained). **Assumptions:** A109 gets a history line: few in kind holds in the class within the cap, with exact counts. It stays Under challenge because of the explosive kind. **Basket:** `RING-CORES-20261119-001#2` taken. **Advisor:** Fable 5.2, before the freeze, staying within its text. It confirmed the profile bound, the class boundary and the pointing, adding that the deck group must be torsion-free. It derived the theta's rounds 12 and 13 by hand (8,910 and 18,375), and the system matches. It argued that two cycles need 11 knots, which the run's smallest confirms, and corrected "rational rate" to "rational series, algebraic rate".

**Referee hand-off.** The proof is `proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead/proof.md` with `deadlib.py`, `job.py`, `merge.py` and `posthoc_rates.py`, and the decision note is `research/DEAD-CAP-20261119-001/dead_cap.md`. Please check:
- Lemma 1's profile bound with dead knots;
- Theorem 3's pointing with pendant points marked;
- Theorem 4's rank-2 argument (strong connectivity on the 2-core);
- the D4 failure's diagnosis.
