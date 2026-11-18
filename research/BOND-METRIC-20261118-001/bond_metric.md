# Is bond distance a metric?

Epic `BOND-METRIC-20261118-001`, 18 November 2026, by Claude. The coordinator's go-ahead on `FREE-READ-20261118-001`'s direction 2:
is bond distance a metric on every base, prove the triangle inequality or find the base where it fails. Goals G1 and G16; tests A97
and A39; sub-goal B200. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `c26b2177d` at 09:11 UTC; the census ran from 09:11 to
  09:35 UTC through the shared runner (`BOND-METRIC-B1`, 814 cases, none failed).
- Proofs: [proof.md](../../proofs/BOND-METRIC-20261118-001A/BOND-METRIC-20261118-001A-P001_metric/proof.md).
- Code: [metriclib.py, job.py, merge.py, checks.py](../../experiments/BOND-METRIC-20261118-001B/BOND-METRIC-20261118-001B-E001_triangles/).
- Results: [results.json](../../artifacts/BOND-METRIC-20261118-001B/BOND-METRIC-20261118-001B-E001_triangles/results.json).

## The answer

**In the owner's terms.**
- **No, bond distance is not a metric on every base.** Take two not-all-equal knots that share two distinctions. Each knot's third
  distinction is one knot away from the shared ones, but no knot of the allowed states holds the two thirds together, so they are
  infinitely far apart while each is one knot from a common distinction (proved). It is a metric on every parity base, and so is bond
  distance minus one (proved), on every knot tree (`FREE-READ-20261118-001`), and on every not-all-equal torus checked (3 × 3 to 4 × 5).
- **Exactly parity.** Every three-place law that passes the knot test (34 laws, nine kinds once places are reordered and all values
  switched together) was settled: bond distance is a metric on every base built from copies of one law exactly when that law is
  parity (proved: parity by T1, and a failing base for each of the other eight, T2 to T5). This is the distance form of what the
  program already had: a law composes like cycles exactly when it is parity (`KNOT-CIRCUITS-20261020-001`), and chains of knots add
  nothing to bond distance exactly where knots compose (`BOND-CHAIN-20261108-001`, A39).
- **Why.** The triangle inequality is composition. On a parity base, any two knots that meet contain, inside their union, a knot
  holding their far ends (two circuits of a matroid that share an element). Under any other law two knots can meet at a hub: the
  shared distinctions can take values that leave both knots slack, so the far ends never share a knot. The foundation's own contact
  rule says the same: a common hub is not one touch.
- **How small, and where.** The census (frozen):
  - No failure of bond distance or of bond distance minus one on 439,652 parity bases (every base to seven distinctions and four
    knots, and 2,000 random ones to twelve distinctions).
  - Six of the eight other kinds fail on the smallest possible base, two knots on four distinctions: not-all-equal, betweenness, the
    clause and its twist, and both forms of "if one place is 1 the other two agree (or differ)".
  - "Not exactly two ones" never fails up to seven distinctions and four knots (its failure needs eight and six), but its twist fails
    on four distinctions with three knots, through two ties of two that each run one way (one forbids both being 1, the other forbids
    one without the other), and one-way ties do not compose. That was not predicted.
  - Not-all-equal with knots meeting at most once: no failure on seven distinctions (all 4,095 systems that allow a state; the 30
    Fano planes allow none); on eight, failures only among
    five-knot systems (10,080 of 75,600), none with four, six, seven or eight knots. More knots can remove failures.
  - On 2,000 random bases of the program's six laws, 506 fail: 504 of the 1,918 whose knots share two distinctions somewhere, 2 of the
    82 whose knots meet at most once.
- **The failing pair is usually tied, not always.** In the two-knot base the far pair correlates (1/5): tied through the hub, held by
  no knot. But on the not-all-equal knots {0, 1, 2}, {0, 1, 3}, {0, 4, 5}, {2, 4, 5}, the pair 3, 4 is fully independent, though each
  is one knot from 0. So a failure can be a pair that bond distance rightly calls unrelated. That was not predicted either.

| Base | Bond distance a metric? | Evidence |
| --- | --- | --- |
| Parity, any base | yes, and bond distance − 1 too | proved (T1); 439,652 bases checked |
| Knot trees of parity, not-all-equal, betweenness | yes (steps apart + 1) | proved (`FREE-READ-20261118-001`) |
| Copies of any other three-place law | no | proved by a failing base for each of the eight (T2 to T5) |
| Not-all-equal, knots meeting at most once | yes to seven distinctions; no from eight (five knots) | computed |
| Not-all-equal tori 3 × 3, 3 × 4, 4 × 4, 4 × 5 | yes | computed |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 10 gates | held | all pass |
| P1 | parity bases: bond distance satisfies the triangle inequality | held | 0 of 439,652 bases fail |
| P2 | the same for bond distance − 1 | held | 0 fail |
| P3 | six languages fail on two knots on four distinctions | held | all six |
| P3b | (advisor) neither R5 language fails within six distinctions and four knots | **failed** | R5 never fails to seven; its twist fails on four distinctions with three knots (12 of 108 bases) |
| P4 | not-all-equal meeting at most once, seven distinctions: no failure | held | 0 of 4,095 (the 30 Fano planes allow no state) |
| P5 | the same on eight distinctions with at most four knots: no failure | held | 0 of 26,040 |
| P6 | every infinite failure under pure not-all-equal has a correlated pair | **failed** | an independent pair on six distinctions and four knots |

5 of 7 held; P3b and P6 failed, both on the record.

## What it means for A97, A39 and B200

A39 (space is spaced by knots that compose) gains a metric form: bond distance obeys the triangle inequality on every base exactly
for the law whose knots always compose, and fails, already on two knots, wherever a hub can stand between them. The results that rest
on A39 (rulers, circles, ball growth) were measured on weaves, trees and parity bases, where bond distance is a metric (proved, or
checked here on tori), so none of them changes. For A97 (distance is the only form of information) and B200, bond distance is a
distance only where knots compose; elsewhere it reads how far one knot reaches, which does not add up along a chain. The step that
would make it add up is composition, which the foundation reserves for native networks (two contacts composing by a substrate law),
not a choice of reading.

## Known results, and what this adds

Known, cited once: "equal or on a common circuit" is an equivalence relation in every matroid (Whitney; Oxley, *Matroid Theory*,
Prop. 4.1.2); bonds are the minimal non-shattered sets of the allowed states; R5 is a closure system (Horn), whose free sets are the
sets in which no member is in the closure of the others; in the program, `KNOT-CIRCUITS-20261020-001` (composes like cycles exactly
when affine) and `BOND-CHAIN-20261108-001` (on parity laws chains add nothing; off them the measures part at gates), the latter
missed by the pre-registration's prior-work searches and the closest relative. What this adds: the triangle inequality as the test,
proved for every base whose knots compose (with bond distance − 1, the advisor's step), settled for all 34 three-place laws by explicit
failing bases, and a census of where not-all-equal fails. The advisor knew no literature on the triangle inequality for minimal
non-shattered sets; no search was run.

## Limitations

- The "exactly parity" theorem is for three-place laws on two values. For other laws, whether "a metric on every base" and "composes
  like cycles" coincide is open.
- The census is bounded: seven distinctions and four knots for the languages, eight distinctions for not-all-equal meeting at most
  once, four small tori, and random bases above that.
- Two predictions failed (P3b, P6); the failures are recorded, not explained beyond the one-way ties of the twisted R5 base.

## Reproduce

```sh
d=experiments/BOND-METRIC-20261118-001B/BOND-METRIC-20261118-001B-E001_triangles
.venv/bin/python -B $d/checks.py
.venv/bin/python -B scripts/longrun.py launch $d/job.py --out runs/bond-metric --workers 8 --case-mem 1500M
.venv/bin/python -B $d/merge.py runs/bond-metric
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage`
names claude-fable-5-2), asked before the freeze. It confirmed T1 to T3, proved that bond distance − 1 is a metric too wherever knots
compose (in T1), gave the failing bases for R6, R5 and the twisted kinds (T4, T5; checked by hand and by the gates), corrected the
unit from five classes to nine languages, predicted that R5 would pass within six distinctions and four knots (P3b: right for R5,
wrong for its twist), and asked for exact arithmetic in P6. It saw no uniform construction for general laws.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is bond distance a metric? | **Status:** Successful (referee pending) | Proved a metric exactly where knots compose (all parity bases; with b − 1); proved failing for every other three-place law; census of smallest failures; 5 of 7 held |
| Local direction: one distance for both laws (B200) | Narrowed | Bond distance adds up only where knots compose; under not-all-equal it is a metric on trees, the tori checked and small bases meeting once, not in general |
| Broader exploration: distances read from the states | Known alternatives | Matroid connectivity and the program's own composition results (KNOT-CIRCUITS, BOND-CHAIN) carry the mechanism |
| Long-term goal: G1 and G16 | G1 obstruction learned; G16 capability gained | G1: the program's distance is a metric only where knots compose. G16: the triangle inequality as a test that tells composing laws from the rest |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does "a metric on every base" equal "composes like cycles" for every law (four places, three values)? | 2/3 | 2/3 | for each four-place law whose knots fail to compose, search bases of up to four knots for a triangle failure (the advisor's test) → stop at a law with none, or a proof | Alternative |
| 2 | Where is not-all-equal bond distance a metric? Weaves, tori, and the meeting-once systems (rings of three knots in every failure on eight distinctions) | 2/3 | 2/3 | census on nine distinctions meeting once and on larger tori and closed weaves → stop at a rule that predicts every failure, or a counterexample to each candidate | Alternative |
| 3 | One-way ties: read the twisted R5 failure's implications as orders, and test whether ties that run one way are the program's orders | 1/3 | 3/3 | list the ties of two in every failing twisted-R5 base and their directions → stop at the list | Alternative |

**Corrections:** none for this study (the correction it began from, FREE-READ's referee check, is logged under `FREE-READ-20261118-001`).

**Goals:** G1 checkpoint (obstruction learned: bond distance is a metric exactly where knots compose; among three-place laws, exactly
parity) and G16 checkpoint (capability gained: the triangle inequality as a test of composition); no goal changed.

**Assumptions:** A39 gains a metric form (status unchanged); A97 gains this study; no new entry.

## The final report as sent (18 November 2026)

**Outcome:** bond distance is not a metric on every base, and the reason is the program's own contact rule. Two not-all-equal knots
that share two distinctions put each third distinction one knot from the shared ones, while no knot holds the two thirds together, so
they are infinitely far apart (proved). Bond distance is a metric exactly where knots compose: on every parity base, and so is bond
distance minus one (proved; 439,652 bases checked). Among all 34 three-place laws that pass the knot test, parity is the only one
under which it is a metric on every base (proved, with a failing base for each of the other eight kinds). Under not-all-equal it holds
on trees and on the woven tori checked, but not in general. 5 of 7 frozen predictions held; two missed: the twisted "not exactly two
ones" law fails much sooner than the advisor expected, and a failing pair can be fully independent rather than tied. Closed, referee
pending.

The position table, the next-step line and the three directions as in Position above.

**Corrections:** none for this study. **Goals:** G1 checkpoint (obstruction learned), G16 checkpoint (capability gained).
**Assumptions:** A39 gains a metric form, A97 this study; no status changed. **Advisor:** before the freeze (proof check, bond
distance minus one, the R5 and R6 bases, nine languages).
