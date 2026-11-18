# Which double meetings are harmless

Epic `DOUBLE-MEET-20261118-001`, 18 November 2026, by Claude. The coordinator's go-ahead on `NAE-METRIC-20261118-001`'s direction 2:
which double meetings (two knots sharing two distinctions) are harmless for not-all-equal bond distance, the weave's against lone
pairs. Goals G1 and G16; tests A97 and A39; sub-goal B200. **Refereed:** report [R1](referee-R1/report.md): a **Block** on one reading (see Referee), the rest confirmed with fixes,
folded in on 18 November.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `9802904ff` at 11:19 UTC; the census ran from 11:19 to
  11:25 UTC through the shared runner (`DOUBLE-MEET-B1`, 102 cases, none failed).
- Proofs and sketches: [proof.md](../../proofs/DOUBLE-MEET-20261118-001A/DOUBLE-MEET-20261118-001A-P001_lone/proof.md).
- Code: [weavelib.py, job.py, merge.py, checks.py](../../experiments/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches/).
- Results: [results.json](../../artifacts/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches/results.json).

## The answer

**In the owner's terms.**
- **A double meeting is never the cause.** On every patch of the weave without holes, 22,143 of them (every one up to eleven knots,
  and 480 random ones to sixteen distinctions), bond distance fails to be a true distance exactly when some pair is held by no bond,
  and every such pair is two **lone** distinctions (each in a single knot of the patch) whose knots are of **opposite classes** and
  that **face each other**: each lies in the wedge the other's knot opens onto (computed, no exception among 12,318 such pairs). The
  "exactly when" is blocked beyond the census (see the last bullet).
- **The lone pair is the smallest case.** Two knots sharing two distinctions: their other two distinctions are lone, of opposite
  classes, and face each other, so no bond holds them (proved). Inside the weave the same double meeting is harmless because its outer
  distinctions are not lone: other knots hold them. So the rhombi of a patch never hurt; what hurts is a pair of lone distinctions of
  opposite classes looking at each other across the patch. Every parallelogram of the weave (the literature's word) has exactly one
  such pair, its two acute lone distinctions, and only that pair is unbonded (all eleven checked, up to 16 distinctions).
- **So a patch whose distinctions all lie in at least two knots is a true distance** (no lone distinctions at all; computed), and so is
  one whose lone distinctions are all of one class, or never face each other. Facing is necessary, not sufficient: of 15,290 facing
  pairs of opposite classes, 2,972 are bonded after all; no simple rule found yet says which.
- **How far, when held.** Bond distance is never below steps apart + 1 on a patch without holes (sketched by the advisor through the
  weave's height function, and checked on 1.56 million pairs; now proved in `WEAVE-HEIGHTS-20261118-001`), and it is exactly steps
  apart + 1 on all but 64 of the 1.56 million bonded pairs; those 64 are steps apart + 2, first on patches of ten knots. In the census
  they do not break the triangle inequality.
- ***Corrected after the referee (Block on this reading):*** "fails exactly when some pair is held by no bond" holds on the census (to
  eleven knots and the random discs) but not beyond it. From twelve knots a lone pair of opposite classes facing each other can be held
  by a bond that is too large: on the 12-knot disc d(0,1), d(0,2), d(1,0), d(1,1), d(2,0), d(2,1), u(1,1), u(1,2), u(2,1), u(2,2), u(3,0),
  u(3,1), every pair has a bond, yet b((0,3), (1,2)) = 2, b((1,2), (4,0)) = 4 and b((0,3), (4,0)) = 7 with steps apart 4 (checked here). So
  the corrected statement: **a patch fails only through lone pairs of opposite classes facing each other, when they are unbonded or (from
  twelve knots) bonded too far.** Double meetings remain harmless; the rim is still the only cause.

| Patch | True distance? | Evidence |
| --- | --- | --- |
| Two knots sharing two distinctions | no (one unbonded pair) | proved |
| Parallelograms to 16 distinctions | no, exactly one unbonded pair: the two acute lone distinctions | computed (11) |
| Patches with no lone distinctions (hexagons and the like) | yes | computed |
| Lone distinctions all of one class (triangles, trapezoids) | yes | computed |
| Every patch without holes to eleven knots | exactly when no lone pair of opposite classes facing each other is unbonded | computed (21,663); beyond, facing pairs can also fail bonded (the referee) |
| Closed weaves (tori 3 × 3 to 4 × 5; the endless weave) | yes | computed (BOND-METRIC); proved (RULER) |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 5 gates | held | all pass |
| P0 | (advisor) the cyclic criterion gives the constrained sets; D + D = 3·steps | held | 156,160 sets of 405 discs; 1,564,004 pairs |
| P1 | bonded pairs: b = steps apart + 1 | **failed** | 64 of 1,564,004 pairs at steps + 2 (first at ten knots); none below |
| P2 | unbonded pairs are lone, opposite classes, facing each other | held | all 12,318 |
| P3 | facing pairs with no knot outside their parallelogram are unbonded | **failed** | 7 of 502 such pairs are bonded |
| P4 | parallelograms: exactly one unbonded pair, the lone pair; b = steps + 1 elsewhere | held | all 11 |
| P5 | a patch is a true distance exactly when it has no unbonded pair | held on the frozen sample; **false** one size past (the referee) | all 22,143 here; a 12-knot disc with every pair bonded fails through a facing pair at steps + 3 |

4 of 6 held; P1 and P3 failed narrowly, both on the record.

## What it means for A97, A39 and B200

On the weave, the owner's main base, bond distance is a true distance wherever the patch has no pair of lone distinctions of opposite
classes facing each other with nothing holding them, and on every closed weave checked; the double meetings that make up the weave
are harmless. The obstruction is a property of the patch's rim (its lone distinctions and their classes), not of how the knots meet
inside. Together with `NAE-METRIC-20261118-001` (blocks decide; joints add), A39's spacing by knots that compose holds on weave
patches up to this rim effect.

## Known results, and what this adds

Known, cited once: not-all-equal on the weave is the triangular Ising antiferromagnet at zero temperature, with height functions
(Blöte and Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984), dimer coverings and lozenge tilings; heights as difference constraints
(Thurston 1990); opposite-class holes in lozenge tilings attract like opposite charges (Ciucu). What this adds: the unbonded pairs of
weave patches located (lone, opposite classes, facing), the metric criterion that follows, the advisor's cyclic criterion for
constrained sets and the lower bound b ≥ steps + 1 checked at scale, and the 64 exceptions to the upper bound. The advisor knew no
statement of these; no literature search was run.

## Limitations

- Only H's criterion (to seven knots) and L's identity are checked set by set; their proofs are the advisor's sketches.
- The census stops at eleven knots and sixteen random distinctions; which facing pairs are bonded is not explained.
- Only patches without holes; annuli are not covered.

## Reproduce

```sh
d=experiments/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches
.venv/bin/python -B $d/checks.py
.venv/bin/python -B scripts/longrun.py launch $d/job.py --out runs/double-meet --workers 8 --case-mem 1500M
.venv/bin/python -B $d/merge.py runs/double-meet
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage`
names claude-fable-5-2), asked before the freeze. It gave the height description, the cyclic criterion for constrained sets, the
identity D + D = 3·steps and the lower bound b ≥ steps + 1 on discs (sketches; the first two now checked at scale, the bound never
contradicted), a structure statement for bonds through lone distinctions of opposite classes, and the literature. It could not prove
the upper bound (now known false in 64 pairs) or give a rule for which facing pairs are bonded.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by the coordinator's background referee thread with its own code. Reproduced: every
disc to ten knots (7,917; all 4,272 unbonded pairs lone, opposite and facing; none below steps + 1; 12 pairs at steps + 2; metric exactly
when no pair is unbonded); 2,500 random discs each of twelve and thirteen knots (every unbonded pair lone, opposite and facing; none
below steps + 1); parallelograms to 18 distinctions (exactly the acute lone pair unbonded). Folded in the same day, logged in
`docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Block (one reading).** P5 and "fails exactly when some pair is held by no bond" are false one size past the census: discs of twelve
   and thirteen knots with every pair bonded fail through a lone pair of opposite classes facing each other at steps + 3 (the example
   above). The census to eleven knots stands. What survives: every long side of a failure is such a pair, so the rim is the cause and the
   double meetings are harmless.
2. **Not a block.** The position table's "at least steps apart + 1 throughout" is marked sketched and computed (now proved, in
   `WEAVE-HEIGHTS-20261118-001`).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which double meetings are harmless | **Status:** Successful (refereed; one reading blocked) | All of them inside the weave; the failures are lone pairs of opposite classes facing each other (every one of 12,318); on the census to eleven knots a patch is a true distance exactly when it has no unbonded such pair (from twelve knots such a pair can also fail bonded); 4 of 6 held |
| Local direction: one distance for both laws (B200) | Promising | On weave patches bond distance is a true distance up to a rim effect, and at least steps apart + 1 throughout (sketched and computed here; proved in WEAVE-HEIGHTS) |
| Broader exploration: heights and tilings | Known alternatives | The triangular antiferromagnet's height function and lozenge tilings carry the mechanism |
| Long-term goal: G1 and G16 | G1 capability gained; G16 capability gained | G1: where the weave's distance is a true distance, and why the rim can break it. G16: lone distinctions and their classes as what decides it |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which facing pairs are bonded: test the advisor's resolvent rule (a bond through x and z splits at one distinction w into bonds through x, w and w, z) on the 2,972 bonded and 12,318 unbonded facing pairs | 2/3 | 2/3 | the rule's prediction on every facing pair to eleven knots → stop at a rule that predicts all, or a counterexample | Alternative |
| 2 | Prove the lower bound and the necessary condition from the height function (write out the advisor's sketches as proofs) | 2/3 | 2/3 | the cyclic criterion's proof, then the corollary → stop at a refereeable proof or a gap | Alternative |
| 3 | Annuli and closed weaves with lone distinctions or holes: does a hole act like a rim? | 1/3 | 2/3 | cylinders and tori with one knot removed → stop at the first failure or a pattern | Alternative |

**Corrections:** none for this study.

**Goals:** G1 checkpoint (capability gained: in the weave, double meetings are harmless; bond distance fails only through unbonded lone
pairs of opposite classes facing each other) and G16 checkpoint (capability gained: lone distinctions and their classes decide it); no
goal changed.

**Assumptions:** A39 gains the weave form; A97 gains this study; no status changed, no new entry.

## The final report as sent (18 November 2026)

*As sent; its "stops being a true distance only when some pair is held by no bond" was blocked by the referee beyond the census (see Referee).*

**Outcome:** inside the weave, double meetings are harmless. On every patch without holes checked (22,143 of them), bond distance stops
being a true distance only when some pair is held by no bond, and every such pair is two lone distinctions (each in a single knot)
whose knots are of opposite classes and which face each other across the patch. Two knots meeting twice on their own are the smallest
such patch; inside a larger weave the same meeting is harmless because other knots hold its outer distinctions. Bond distance is never
below the steps apart plus one there (the advisor's height-function argument, checked on 1.56 million pairs) and equals it on all but
64 bonded pairs. 4 of 6 frozen predictions held; the two misses (those 64 pairs, and 7 facing pairs that are bonded inside their
parallelogram) are on the record. Closed, referee pending.

The position table, the next-step line and the three directions as in Position above.

**Corrections:** none for this study (NAE-METRIC's referee fold-in earlier today was one Narrowing). **Goals:** G1 and G16 checkpoints
(capability gained). **Assumptions:** A39 gains the weave form, A97 this study; no status changed. **Advisor:** before the freeze
(the height description, the constrained-set criterion, the lower bound, the literature).
