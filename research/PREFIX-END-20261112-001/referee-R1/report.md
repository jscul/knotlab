# Referee report PREFIX-END-R1: an end read from the prefix counts

**Verdict: Confirmed, with two small fixes (both Not a block).**
- **Everything reproduces.** I regenerated all 800 growths, and every base's cheap features match exactly. Every matched concordance
  recomputes. A sample of the random and exact features agrees.
- **The hand-rolled conditional logit is fine.** A standard implementation (statsmodels' ConditionalLogit, on the proper 1:3 matched
  likelihood) gives the same held-out concordance, 0.772 against 0.773.
- **The fixes.**
  - Bootstrapping growths rather than positives widens the intervals, because one growth serves as a negative up to 14 times. E3's
    failure then rests on its point estimate only.
  - The literature point stands. In correcting my own wording about it, I found an overstatement in my AGE-NEST-R1 report, now fixed.

Referee: the background referee thread, 2026-11-12.
- **Code.**
  - `ref_prefix.py` recounts from the records. It holds my concordances, three logit fits and both bootstraps.
  - `ref_prefix_regen.py` regenerates the growths with RANDOM-FATES-R1's generator and recomputes the features.
  - Pnest uses AGE-NEST-R1's redraw. The hazard uses exact tie classes from RANDOM-FATES-R1's reader.
  - Neither imports `census.py` or `fates.py`.
  - statsmodels 0.15.0 was installed in a scratch folder only for the cross-check.
- **Validation.** V2. The advisor model was not consulted for this job.

## 1. What reproduces

**The regeneration.**
- **Growths.** All 800 growths have the recorded knots and ending: 685 end.
- **Cheap features.** All 4,750 bases read (positives, negatives and secondary negatives) have identical m/n, κ, maxD and nine decile
  densities. The largest deviation is 0.
- **Pnest.** On 60 bases (20 positives, 40 negatives) my own 100 redraws correlate with the record at 0.977. The mean absolute
  difference is 0.044, which is resampling noise.
- **The hazard,** from exact tie classes, is identical on all 45 sampled bases with at most 2,500 knots.

**Concordances**, matched (positive above its negative, ties half), are identical to `summary.json`:

| Feature | All runs | Odd runs |
| --- | --- | --- |
| m/n | 0.685 | 0.695 |
| κ | 0.744 | 0.764 |
| maxD | 0.727 | 0.726 |
| Uprefix | 0.546 | 0.547 |
| Pnest | 0.747 | 0.755 |
| hazard | 0.947 | 0.935 |

**E1.** No positive and no negative has an early part whose uniform resample allows no state more than half the time: 0 of each.

## 2. (1) The risk set

**The negatives are fair.**
- **Drawn from the risk set.** They are drawn uniformly among growths of the same run parity with more than M knots, read at age M.
  This is nested case-control sampling from the risk set at the positive's age.
- **No same-time ends.** None of the 2,055 negatives ends at the very next knot, which would make it a positive of the same age.
- **Later fates.** 1,386 end later, and 669 never end within 6,000 moves.

**One thing to note.** The 2,055 negative readings come from only 587 growths, and one growth serves up to 14 times. That is normal for
risk-set sampling, but it matters for the bootstrap (section 4).

## 3. (2) The conditional logit

I fitted the frozen model (paired differences of m/n, κ, maxD and the nine decile densities, standardized) on even runs, three ways,
and scored each by matched concordance on odd runs.

| Fit | Odd-run concordance |
| --- | --- |
| the census's pairwise objective, solved exactly by Newton's method | 0.773, as reported |
| the proper conditional likelihood for 1:3 matched sets (a softmax over each set), my Newton | 0.772 |
| statsmodels' ConditionalLogit on the same sets | 0.772 |

The two 1:3 fits agree to 0.001 in every weight. The census's gradient-descent fit treats each matched set as three independent pairs,
which is not quite the conditional likelihood. It reaches the same ranking, so E4's failure (+0.009 over κ) stands.

## 4. (3) The bootstrap

The census resamples positive growths and keeps their matched negatives. Since negatives are shared between matched sets, I also
resampled growths: each growth once, in whichever roles it has, with weights for repeats.

| Difference | Value | Over positives (95%) | Over growths (95%) |
| --- | --- | --- | --- |
| Pnest − m/n | 0.062 | 0.035 to 0.090 | 0.021 to 0.108 |
| Pnest − κ | 0.003 | −0.020 to 0.024 | −0.032 to 0.040 |
| maxD − m/n | 0.042 | 0.013 to 0.070 | −0.006 to 0.089 |
| fit − κ (odd runs) | 0.009 | −0.021 to 0.036 | −0.038 to 0.054 |

**E2 holds under either bootstrap:** the interval for Pnest − m/n stays above 0.

**E3's failure rests on its point estimate.** The registered rule is "fails when above 0.03", and 0.042 is above. But both intervals
include 0.03, and the growth-level interval includes 0. So the data do not establish that maxD beats density by more than 0.03,
only that the point estimate does.

**E4 fails under either bootstrap.**

## 5. (4) "Reads beyond density but not beyond degrees"

**Fair on the frozen comparisons.**
- **Beyond density:** Pnest beats m/n by 0.062, with an interval above 0 under both bootstraps.
- **Not beyond degrees:** Pnest ties κ (0.003, with an interval about 0), and the fit, which includes κ, adds 0.009, which is not
  significant.

**Two qualifications for the reading.**
- **The two features overlap.** κ and Pnest are rank-correlated at 0.75 over all bases read.
- **A forecast, not a mechanism.** κ here is a forecast summary: in X growth, high degree means old. AGE-NEST found that resamples
  keeping only the degrees never end. "The degrees read the end as well as the profile does" and "the degrees do not carry the end"
  are both true, of different questions. The note's Answer says this, which fits.

**The hazard ceiling (0.947)** is by definition the end's chance per closing, so it is a ceiling, as frozen. It is not a finding
about counts.

## 6. (5) Does Bollobás–Janson–Riordan give a 2-colourability threshold?

**No, and the claim is fair.**
- **What BJR gives.** The theory of inhomogeneous random graphs (Bollobás, Janson and Riordan 2007), and its extension to clustered
  and hyperedge models, gives the giant component's threshold, by the norm of the kernel operator. Riordan (2008) gives the k-core
  thresholds.
- **Why that falls short.** A core is necessary for an end: in a minimal pattern with no state, every distinction is in at least two
  knots, since a distinction in one knot can always be set to satisfy it. So these theories give necessary conditions, but not the
  2-colourability threshold.
- **The uniform case** needs other methods (second moments and cavity arguments: Achlioptas and Moore; Coja-Oghlan and Panagiotou).
- **For age kernels** I know of no 2-colourability threshold.

**A correction to my own report.** AGE-NEST-R1 said "inhomogeneous random hypergraphs, whose thresholds are set by the age kernel
(Bollobás, Janson and Riordan 2007)", which read as if that theory gave a 2-colourability threshold. I have corrected that sentence
in place, with a dated note: the theory gives component and core thresholds. The AGE-NEST verdict does not change. That thread may
want to check its own wording if it used mine.

## 7. Built in, known, new; frozen against after-run

**Built in.**
- The hazard as a ceiling.
- E0, since endings select closing-rich histories.
- E1's null, for the typical prefix density of about 1.64. The pre-registration says all three.

**Known.**
- **The mechanism:** age-inhomogeneous growth, grown against degree-matched networks.
- **The general idea:** discriminating an event from a risk set, which is nested case-control sampling.

**New data.** The concordances, the κ tie, and the hazard gap.

**Frozen.** E0 to E4, the features (κ included), the risk set and the split. Reported in advance: the tertiles and the secondary
negatives.

**Evidence class.** Nothing is proved; everything is computed.

## 8. Fixes for the thread (both Not a block)

1. **Intervals.** One growth serves as a negative up to 14 times, so give growth-level bootstrap intervals beside the positive-level
   ones. With them:
   - E2 still holds (Pnest − m/n, 0.021 to 0.108);
   - E3's failure is a point-estimate failure (maxD − m/n, −0.006 to 0.089, which includes the 0.03 bound).
2. **The fit.** Note that the gradient-descent fit treats each 1:3 set as three pairs. A standard conditional logit on the 1:3 sets
   gives the same held-out concordance, 0.772, so E4 stands.

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_prefix.py` | `result_prefix.json` | concordances, three fits, two bootstraps, correlations |
| `ref_prefix_regen.py` | `result_prefix_regen.json` | the regeneration, the features, Pnest and the hazard on a sample |

The within-tercile table in `result_prefix.json` stratifies on the positive's own m/n, which biases m/n's concordance inside each
tercile by construction. It is not used here.
