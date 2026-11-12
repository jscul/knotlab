# Referee report SHORT-DESC-R1: meeting patterns weighted by short descriptions

**Verdict: Confirmed with fixes.** Everything recomputes. I regenerated one worker of each variant with my own sampler, expander, port
evaluator and SAT checks, and it matches the records exactly. The chains give the same dead shares at eight times their length. The
one substantive fix is about reading the result:
- **The effect is largely the language's own self-similarity.** Nested families live at every depth because, in 98.1% of them,
  substituting the definition for its own knot allows at least what the knot allows. That one-step check settles "forever" in 99.2% of
  the families that live forever.
- **Large patterns are always nested.** Every pattern of 100 knots or more uses SELF. So "short descriptions die less than uniform
  patterns of their size" mostly measures that a small random gadget seldom constrains its ports more than a knot does.

Referee: the background referee thread, 2026-11-12.
- **Code.** It is my own: `ref_sd.py` holds the sampler in the frozen draw order, the expander, the port evaluator, my SAT check, the
  chains and rejection sampling. It imports none of `dlang.py`, `census.py` or `fates.py`.
- **Validation.** V2. The advisor model was not consulted for this job.

## 1. What reproduces

**Worker 0 of each variant** was regenerated from the census's seed (sha256 of "SD:variant:0").

| Variant | Patterns matching (bits, n, m, t) | Families matching (fate, first death, limit, limit kinds, revival) | 7+ knots: SAT = record = port evaluation |
| --- | --- | --- | --- |
| main | 53,577 of 53,577 | 27,705 of 27,705 | 2,931 of 2,931 |
| wide | 59,009 of 59,009 | 28,681 of 28,681 | 3,449 of 3,449 |
| noself | 57,858 of 57,858 | — | 1,882 of 1,882 |

So the gate (port evaluation against a solver) and every family's fate are confirmed with independent code on these workers. I did
not recompute the paired baselines' dead shares directly. I checked the chains (section 2).

## 2. The chains

**The test.** I drew 300 patterns of 7+ knots and, separately, 400 of 25+ knots, where the baselines die often, from main's
workers 0 to 3. Each was resampled with each chain at its length and longer.

| Sample | Description | Uniform: 30, 60, 240 steps per knot | Same degrees: 20, 40, 160 |
| --- | --- | --- | --- |
| 300 patterns, 7+ knots | 6 dead | 15, 19, 15 | 18, 23, 18 |
| 400 patterns, 25+ knots | 24 dead | 73, 68, 72 | 106, 117, 106 |

**The dead shares do not move with chain length.**
- **The degree chain's 0.007.** Its doubling step from 20 to 40 is noise: it falls back at 160.
- **It could not move S2.** S2's paired difference is −0.061, with interval −0.065 to −0.058.

**Connectivity is not proved.** I compared the replace-one-knot chain with exact rejection sampling (uniform distinct triples,
accepted when every distinction is in a knot) on 187 small patterns, and both gave 0 dead, which is uninformative at that size. The
chain is symmetric, so it is uniform on its component. Its component could be smaller than the whole space where coverage is tight
(n near 2m, where removing a knot uncovers distinctions only that knot holds). The stable dead shares over an eightfold range of
lengths show no sign of that mattering.

## 3. The treewidth bound is correct

Take one bag per call instance, holding that definition's k + l distinctions, and connect each call to its callee. A knot from a K
call lies in its definition's bag. A distinction lies in the bag where it is created and in the bags of the calls it is passed down
to as a port, which form a connected subtree. So the primal treewidth is at most max(k + l) − 1: 11 for main, 13 for wide. Dropping
unused distinctions can only lower it.

## 4. The limit, and families that die at a finite depth while the limit lives

**The compactness argument is sound.** Let F be the map from a SELF relation to the next.
- **The depth-t pattern** has port relation F^t(knot): its leaves are knots.
- **The infinite pattern** has none: every SELF is replaced, forever. By compactness it allows a state iff the greatest fixed point
  below TOP, reached from TOP by F in finitely many steps, has a non-empty main relation.
- **"Forever implies a living limit".** F is monotone and knot ⊆ TOP, so F^t(knot) ⊆ F^t(TOP). A family alive at every depth
  therefore has a living limit, as the pre-registration says.

**The converse cell is a real distinction.**
- **Two different objects.** The depth-t pattern is not a part of the infinite pattern: it holds the leaf knots, which the infinite
  pattern never contains.
- **Where they die.** The families that die at a finite depth while the limit lives (172 on worker 0 of main; 1,392 in the census) die
  in those leaf knots, as the note's conclusion 7 says.
- **What the limit is.** "The limit lives" is a statement about the pattern with no bottom. It is not a limit of the depth-t
  relations, which need not converge: 232 families have period above 1, and 2 revive.

**Free limits are mostly trivial.** On worker 0 of main:
- every one of the 20,306 free limit relations is free at the first step from TOP (F(TOP) = TOP);
- 73% (14,820) belong to definitions whose only calls are SELF, so the limit holds no knot at all;
- 76% (15,415) have no K call in the body.

So of the 66% free limits, about three quarters are empty bodies. The non-trivially free limits are about 17% of all limits.

## 5. How much of "nested patterns die less" the language settles

**Reuse alone does nothing.** Without SELF, patterns die exactly like uniform ones (+0.001), so the effect is the nesting, as S5
says.

**Nesting is mostly settled in one step.** On worker 0 of main:
- **The one-step check.** In 27,189 of the 27,705 nested families (98.1%), F(knot) contains the knot for every SELF definition.
  Substituting the definition for its own knot then allows at least what the knot allowed.
- **Why it settles life.** By monotonicity, every depth then allows at least depth 1's relation, so the family lives forever as soon
  as depth 1 lives.
- **How much it covers.** That holds for 27,188 of the 27,420 families that live forever (99.2%).

A random small gadget with locals usually leaves its three ports at least as free as a knot does.

**Large patterns are always nested.** Every pattern of 100 knots or more uses SELF. So the large-pattern contrast (13% against 33% and
55% dead) mostly compares self-similar substitutions of a gadget that is monotone at the knot with uniform patterns. That is what
the language's structure predicts. It is not a finding about "short descriptions" in general.

**What is not settled.** The size of the effect at 7 to 99 knots (the bins 13–24, 25–49 and 50–99 all differ from uniform) and the
small dead cores (median 10 distinctions against 25) are measurements.

## 6. The look before freezing

The pre-registration discloses that the smoke run showed S1 and S2 on 405 pairs, and it calls S1 and S2 replications on fresh seeds.
They were frozen before the registered run, with thresholds (≤ −0.01) looser than the effects seen (−0.032, −0.059). The run on fresh
seeds replicates them, but they are not forecasts. The note's table says "S1, S2 held". It should say "replicated (seen in the smoke
before freezing)". S3 and S4, not looked at, are the real tests, and both failed.

## 7. Built in, known, new; proved against computed

**Built in.**
- Short descriptions weigh more, by the definition of the weighting.
- Below seven knots everything lives (m(3) = 7, the Fano plane).
- The treewidth bound.
- "Forever implies a living limit".
- Most of "nested families live", through the one-step monotone check (section 5).

**Known.**
- Bounded-width instances are easier.
- The satisfiability of iterated substitutions is a fixed point of a monotone map.
- Compactness for the infinite pattern.

**New data.**
- The weighted shares.
- The paired differences at 7 to 99 knots.
- The core sizes.
- S3's reversal: living descriptions are less tied.
- The fate shares.
- The converse cell.

**Proved:** the per-family fates and limits, which are exact. **Computed:** everything else.

## 8. Fixes for the thread

1. **The reading of S1, S2 and S5.** Say the following:
   - 98.1% of nested families are monotone at the knot (F(knot) ⊇ knot), which settles "forever" in 99.2% of them;
   - every pattern of 100+ knots is nested.

   So the large-pattern contrast is largely the self-similar language's own property: a random small gadget seldom constrains its
   ports more than a knot. The effect at 13 to 99 knots and the small dead cores are the measured part. **Narrowing** (Settled by
   construction, in part).
2. **S1 and S2 are replications.** Write "replicated", seen on 405 pairs before freezing, not "held" as forecasts. **Not a block.**
3. **Free limits.** Of the 66%, about three quarters are bodies with only SELF calls, and about 76% have no K call. Say that the
   non-trivially free limits are about 17% of limits. The note already says "by construction" for SELF-only bodies; give the share.
   **Not a block.**
4. **The chains.** Add that dead shares do not move at eight times the chain length (uniform 73, 68, 72; same degrees 106, 117, 106
   on 400 patterns of 25+ knots), and that the replace-one-knot chain's connectivity is not proved. **Not a block.**

## Files

`report.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_sd.py regen` | `result_regen.json` | the regeneration and the family features |
| `ref_sd.py chains` | `result_chains.json` | 300 patterns of 7+ knots |
| `ref_sd.py chainsbig` | `result_chains_big.json` | 400 patterns of 25+ knots |
