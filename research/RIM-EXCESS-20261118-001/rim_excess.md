# How far the weave's rim pushes bond distance

Epic `RIM-EXCESS-20261118-001`, 18 November 2026, by Claude. The coordinator's go-ahead on `WEAVE-HEIGHTS-20261118-001`'s direction 1:
which facing lone pairs are bonded and how far, a formula or bound for the excess of bond distance over steps apart + 1, and whether it
grows without limit. Goal G1; tests A39 and A97. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `8ef604495` at 14:16 UTC; the census ran from 14:16 to
  14:52 UTC through the shared runner (`RIM-EXCESS-B1`, 109 cases, none failed).
- Proofs: [proof.md](../../proofs/RIM-EXCESS-20261118-001A/RIM-EXCESS-20261118-001A-P001_polygons/proof.md).
- Code: [polylib.py, job.py, merge.py, checks.py](../../experiments/RIM-EXCESS-20261118-001B/RIM-EXCESS-20261118-001B-E001_excess/).
- Results: [results.json](../../artifacts/RIM-EXCESS-20261118-001B/RIM-EXCESS-20261118-001B-E001_excess/results.json).

## The answer

**In the owner's terms.**
- **What the excess is** (proved). A bond, visited in the right order, is a closed route through its members that is exactly as short as
  the heights allow: weight 3(m − 2) for m members, every member on a shortest way between its two neighbours. So bond distance is one
  more than the steps apart plus the **excess**, and the excess is how much longer the least bond's route is than the plain round trip
  between the two distinctions, in units of 3. A least bond's members stay within that much of the round trip, which gives an exact bond
  search that never lists the states.
- **Where it lives** (computed, every patch without holes of eleven and twelve knots, 51,647 of them). Every pair with an excess, and
  every pair with no bond, is a lone pair of opposite classes facing each other. Everywhere else on these patches bond distance is exactly
  steps apart + 1.
- **How large** (computed). The largest excess is 0 up to nine knots, 1 from ten knots, and 2 from twelve (6 pairs among 3.4 million).
  Random patches of 20 to 40 knots gave 0 almost always (253 of 254 settled facing pairs; 20 searches ran out of time), and searches on
  shape never passed 2.
- **Does it grow without limit?** Not settled. The extremal values rise by one about every two knots in the exhaustive range, which
  points to growth, but random and searched larger patches never exceed 2, and the one candidate family tried (a narrow band ending in a
  cap) leaves the pair unbonded. The advisor sketches a structure for every bond through such a pair, a figure-eight crossing itself at a
  distinction outside the bond, which would split the excess into two loops and a detour; it is not checked here.

| Size | Largest excess | Where | Evidence |
| --- | --- | --- | --- |
| to nine knots | 0 | — | exhaustive |
| ten and eleven knots | 1 | lone opposite facing pairs only | exhaustive (12 and 48 pairs) |
| twelve knots | 2 | lone opposite facing pairs only | exhaustive (198 pairs, 6 at 2) |
| 20 to 40 knots, random | 1 seen | facing pairs | 254 settled, 20 unsettled |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 4 gates | held | all pass |
| R1 | Lemma P on every bond to nine knots | held | 116,932 bonds |
| R2 | the polygon search equals brute force to nine knots | held | 142,413 pairs |
| R3 | excess and unbonded pairs only lone, opposite, facing (eleven and twelve knots) | held | 246 excess pairs, every unbonded pair |
| R4 | the largest excess at twelve knots is exactly 2 | held | 6 pairs |
| R5 | no excess of 3 or more on random patches of 20 to 40 knots | held | largest 1; 20 searches unsettled |

5 of 5 held.

## What it means for A97, A39 and B200

On the weave without holes bond distance is a ruler (steps apart + 1) everywhere except on lone pairs of opposite classes facing each
other, and there it is too large, never too small, by an amount that is exactly the extra length of a route around the rim. Whether that
amount stays bounded decides whether the rim can push two distinctions arbitrarily far apart in bond distance while they stay a few steps
apart; that is the open part.

## Known results, and what this adds

Known, cited once: the height description and difference constraints (as in `WEAVE-HEIGHTS-20261118-001`). What this adds: bond polygons
(Lemma P), the excess formula and the candidate lemma, an exact bond search without states, and the census locating the excess. No
literature search was run.

## Limitations

- The census of where the excess lives stops at twelve knots; larger patches are sampled and their searches capped at excess 6 and 20
  seconds.
- Growth is unsettled; the figure-eight is a sketch.

## Reproduce

```sh
d=experiments/RIM-EXCESS-20261118-001B/RIM-EXCESS-20261118-001B-E001_excess
.venv/bin/python -B $d/checks.py
.venv/bin/python -B scripts/longrun.py launch $d/job.py --out runs/rim-excess --workers 8 --case-mem 1800M
.venv/bin/python -B $d/merge.py runs/rim-excess
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage`
names claude-fable-5-2), before the freeze: it checked Lemma P (with m = 3 explicit), the corollary and Lemma C (sharpened), flagged that
sub-collections must be tested in every order (the search does), sketched the figure-eight, proposed a growing family (unbonded in the
exploration), and set R3 and R4 with its confidence (80% and 90%).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: how far the rim pushes bond distance | **Status:** Successful (referee pending) | The excess is a polygon's extra length (proved); it lives only on lone opposite facing pairs to twelve knots, at most 2 there; growth unsettled; 5 of 5 held |
| Local direction: one distance for both laws (B200) | Promising | On the weave bond distance is a ruler except at facing rim pairs |
| Broader exploration: heights and tilings | Known alternatives | The mechanism is the height function's |
| Long-term goal: G1 | G1 capability gained | Where and by how much the weave's distance departs from the ruler, to twelve knots |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Check the figure-eight on every bond through a facing pair to twelve knots, and use its split of the excess (two loops and a detour) to build patches whose excess grows | 2/3 | 2/3 | extract the crossing distinction and the two loops from every excess bond → stop at a family with excess 3 or a reason the loops cannot grow | Alternative |
| 2 | Exhaustive excess at thirteen knots with the polygon search (about 100,000 discs) | 1/3 | 3/3 | the largest excess at thirteen knots → stop at 3 or at 2 | Alternative |
| 3 | Prove that every pair other than a lone opposite facing pair has b = steps + 1 | 2/3 | 1/3 | a geodesic polygon of s + 2 members for a pair with a non-lone end → stop at a proof or a counterexample | Alternative |

**Corrections:** none for this study.

**Goals:** G1 checkpoint (capability gained: the excess located and bounded to twelve knots; growth open); no goal changed.

**Assumptions:** A39 gains the excess form; no status changed, no new entry.

## The final report as sent (18 November 2026)

**Outcome:** the rim's excess now has an exact meaning. A bond, visited in the right order, is a closed route exactly as short as the
heights allow, so bond distance is the steps apart plus one plus how much longer the shortest bond's route is than the plain round trip
(proved). That gives an exact bond search that never lists the states. On every patch without holes of eleven and twelve knots (51,647),
that excess is zero except on lone pairs of opposite classes facing each other; it is at most 1 up to eleven knots and 2 at twelve.
Random patches of 20 to 40 knots showed at most 1. Whether it grows without limit is still open. All 5 frozen predictions held. Closed,
referee pending.

The position table, the next-step line and the three directions as in Position above.

**Corrections:** none for this study. **Goals:** G1 checkpoint (capability gained). **Assumptions:** A39 gains the excess form; no status
changed. **Advisor:** before the freeze (checked the lemmas, sketched the figure-eight, proposed a growing family that stayed unbonded).
