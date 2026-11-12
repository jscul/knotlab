# Referee report OLD-CORE-R1: the old core's own end

**Verdict: Confirmed with fixes.**
- **Every recorded measure reproduces.** I regenerated all 379 recorded endings from the seeds with my own generators. Each matches its
  record in knots, ending, k*, m*, the floor, the peeled core (n2, m2) and k*_deg.
- **The degree-matched sampler is fair enough.** A fair switch chain, run from two independent starts, gives the same P_d core by core
  as the census's stub-repair generator. L2 stands as reported.
- **The two stopped growths cannot change a verdict.**
- **The critical closing rate holds up at a longer horizon.** Run to 20,000 moves, X(0.25)'s endings do not grow with the horizon,
  while X(0.3)'s reach 100%.
- **Fix: several headlines are settled by arithmetic.** For X, the core's density cannot reach the uniform end, so L1's failure and
  "ends below the uniform end" follow for X before any run.

Referee: the background referee thread, 2026-11-12. The code is my own:
- `ref_oldcore.py`, the regeneration, my own k* bisection, peeling and order by degree, and the switch chain;
- `ref_horizon.py`, the growths to 20,000 moves.

Both use RANDOM-FATES-R1's `ref_fates.py` generators, which draw in the frozen order. They import neither `census.py` nor `fates.py`.
Validation: V2. The advisor model was not consulted for this job.

## 1. The regeneration

All 379 endings on record were regenerated: 8 of X(0.25), 87 of X(0.3), 100 of X(0.35), 86 of O global and 98 of O local. All of
them match their records in:
- knots, whether the growth ended, and distinctions;
- k*, m* and the floor;
- n2 and m2;
- k*_deg.

So L3, which holds in 82 to 88% of endings, and conclusion 5 (k* equals the floor in the median ending) are confirmed as computed.

## 2. (Check 1) Is the degree-matched generator fair, and does it matter for L2?

**The census's generator.** `degree_pattern` shuffles the stubs into triples, then repairs bad triples, those with a repeated member
or duplicating another triple, by swapping a stub of a bad triple with a random one. It is not the uniform law on simple patterns with
those degrees: repair moves are not symmetric, and the result depends on the shuffle. With a few very knotted distinctions, as in the
O cores, the bias could matter.

**A fair sampler.** I used the switch chain:
- pick two knots and one member of each, uniformly, and swap the two members when both new knots have three distinct members and
  are not already knots;
- the proposal is symmetric, so the stationary law is uniform on the simple patterns the chain reaches.

I ran it from two starts, the core itself and a stub-repaired start, with a burn-in of 20 m steps, then 20 samples 5 m apart.

| Process | P_d, census (median; 10th to 90th percentile) | Switch chain from the core | From a repaired start | Mean per-core difference |
| --- | --- | --- | --- | --- |
| X(0.3) | 0 (0 to 0.07) | 0 (0 to 0.05) | 0 (0 to 0.10) | 0.011 |
| X(0.35) | 0 (0 to 0.31) | 0 (0 to 0.31) | 0 (0 to 0.35) | 0.041 |
| O global | 1.0 (0.68 to 1.0) | 1.0 (0.70 to 1.0) | 1.0 (0.72 to 1.0) | 0.020 |
| O local | 1.0 (0.29 to 1.0) | 1.0 (0.40 to 1.0) | 1.0 (0.30 to 1.0) | 0.040 |
| X(0.25) | 0 | 0 | 0 | 0.025 |

The two starts agree with each other and with the census; the per-core correlation is 0.79 to 0.96. So the repair generator's bias,
if any, is below the resampling noise. **L2 fails as reported: O 1.0, X 0.**

AGE-NEST, which uses its own switch chain, also finds X's degree share at 0 (AGE-NEST-R1).

## 3. (Check 2) The two O global growths that were stopped

**They cannot change a verdict.** O global has 86 endings on record. A median of at least 0.3 over 88 endings would need 45 at or
above 0.3.

| Verdict | Endings at or above 0.3 now | With two more |
| --- | --- | --- |
| L1 (P_u) | 2 | cannot reach 45 |
| L1p (P_u2) | 37 | at most 39, so it still fails |
| L2 (P_d) | 84 | holds either way |

L3's share would be at worst 76 of 88 = 86%, above 70%.

**Is stopping them a selection on outcome?** They were stopped by run time, which goes with large cores near the threshold, where
the solver is slow. Slow kept runs (1,200 to 2,250 s) exist and are counted, so this is not a selection on any registered outcome. It
does leave the slowest, possibly most critical cores out, which matters only for P_u2's distribution, and not for its verdict.

**My recomputation of runs 54 and 99 was still running** when this report was committed. My solver calls are capped, so a run can
end undecided. It will be folded in if it finishes.

## 4. (Check 4) The dying core, and D* in the arithmetic band

**The core is identified the same way in every process:** the knots whose three members lie among the oldest k distinctions, by
arrival index, with k* the least dead k (found by bisection; satisfiability is monotone in k).

**D* is settled by arithmetic for X**, as the pre-registration says. In X(q), the oldest k distinctions carry their k birth knots,
plus the closings that fell among them. Closings early in life land among them with a probability that falls with growth. So
m/k runs between 1/(1 − q), at k = n, and (1 + q/2)/(1 − q), for k much smaller than n.

| Process | Band | Endings in the band, within 0.05 | D* range |
| --- | --- | --- | --- |
| X(0.3) | [1.43, 1.64] | 82 of 87 | 1.43 to 1.78 |
| X(0.35) | [1.54, 1.81] | 91 of 100 | 1.41 to 2.15 |
| X(0.25) | [1.33, 1.50] | 6 of 8 | |

**So for X, two things follow from the arithmetic alone:**
- **L1's failure.** Uniform patterns at a density of about 1.6 are far below the uniform end of about 2.1, so P_u = 0 is expected.
- **"The dying core is far below the uniform end".** It holds before any run.

Only the O processes, whose D* is not set by the growth rule (1.66, 1.74), test the uniform-end law. There L1 fails as a real
finding, though P_u = 0 again follows once D* is known to be below 2.1.

**L1p is the informative uniform test.** The O processes' peeled cores sit at 2.05 and 2.10, at about the known threshold, and P_u2
of 0.225 and 0.425 says they are near-critical.

## 5. (Check 3) Known against new

**The critical closing rate.** I grew X(0.2), X(0.25) and X(0.3) to 20,000 moves, 40 growths each, on fresh seeds:

| Process | Ended by 2,000 | 6,000 | 10,000 | 20,000 |
| --- | --- | --- | --- | --- |
| X(0.2) | 0 | 0 | 0 | 0 |
| X(0.25) | 1 | 1 | 1 | 1 |
| X(0.3) | 22 | 34 | 38 | 40 |

- **X(0.25).** Its endings are early accidents, 2.5% here and 8% in the census, that do not grow with the horizon.
- **X(0.3).** Every growth ends.

So "between 0.25 and 0.3" is supported to 20,000 moves. It remains a finite-horizon statement. Grown random networks have an
infinite-order transition (Callaway, Hopcroft, Kleinberg, Newman and Strogatz 2001), where the ordered part is exponentially small
near the threshold. A slow onset below 0.25 at much longer horizons cannot be excluded.

**Classification.**

| Claim | Status | Why |
| --- | --- | --- |
| "Grown NAE patterns end below the uniform end" | arithmetic for X; computed for O | for X, D* is confined below 2.1; for O, D* is computed, and lower thresholds from heterogeneous degrees are known (as the note cites) |
| "Degrees explain the overlap growth's end but not the expanding growth's" | new data, standard in mechanism | grown networks differ from degree-matched static ones (Callaway and co-authors; Bollobás, Janson and Riordan) |
| "The critical closing rate lies between 0.25 and 0.3" | new, as a finite-horizon statement | supported here to 20,000 moves |

## 6. Fixes for the thread

1. **Say what is arithmetic for X.** D* (82 of 87 and 91 of 100 endings in the band) is set by the growth rule, so "the dying core is
   far below the uniform end" and L1's failure follow for X from arithmetic. Only O tests the uniform-end law, and L1p is the
   informative uniform test. **Narrowing** (Settled by definition, for X).
2. **The critical rate.** Keep "between 0.25 and 0.3" as a finite-horizon statement. Add that, to 20,000 moves, X(0.25)'s ended share
   does not grow (1 of 40 from 2,000 on) while X(0.3)'s reaches 40 of 40, and that an infinite-order transition could hide a lower
   threshold. **Not a block.**
3. **The degree-matched sampler.** Add that a fair switch chain from two starts gives the same P_d (per-core differences 0.01 to
   0.04). **Not a block.**
4. **The two stopped growths** cannot change a verdict (section 3). Say so. **Not a block.**

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_oldcore.py regen` | `result_regen.jsonl` | the regeneration and the switch-chain P_d |
| `ref_oldcore.py missing` | `result_missing.json` | runs 54 and 99, pending |
| `ref_horizon.py` | `result_horizon.json` | the growths to 20,000 moves |
