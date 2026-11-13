<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-13 -->

**Verdict:** the sampling is sound, but as frozen it will almost certainly return "undecided", and two of the predictions need tightening.

**Flaws**

1. **The 5% rule contradicts the 15% cap rate.** Every stratum will be undecided on arrival. The against/for bands already treat unresolved families honestly, so the rule is redundant; drop it or replace it.
2. **The bands alone are still too wide.** At 15% unresolved, P1 holds only if at least about 93% of resolved growers are bounded and fails only below about 66%. The bottleneck is the cap, not n: 400 gives ±4 points, the cap gives 15.
3. **P1 has several readings.** Count, weight and uncarried are all read; name the one that gives the verdict, or it forks.

**Fix for 1 and 2:** freeze a second phase now that reruns every unresolved family at about 10× the cap (around 60 families, at most about 17 h on 3 workers). G = 300 plus that phase beats G = 400 without it.

**Settled by construction, or nearly**

- **Weight majority:** 6,989 draws over 6,925 distinct families means weight share ≈ count share, so "weight majority" is implied by the 75% count test. The ratio estimator is sound but idle here.
- **Equivalent calls:** if a family's SELF calls are equivalent, L_path = L_ray and it grows by construction. Exclude these from P1's denominator or report them separately, otherwise they dilute the share.
- **P3:** the first ray is itself a path with no bond, so the min-object cannot show persistence. P3 is existential over paths; state that quantifier and how a bondless path enters the min.
- **Uncarried:** L_path^unc ≥ L_path, so uncarried-bounded implies bounded. Add a class for "no uncarried path exists".

**Overclaims to avoid**

- P2 and P3 can be confirmed by sampling but not refuted. Zero in 200 only bounds the share below about 1.5% (about 97 families), so call that "not found".
- Unresolved families should not block an existence hit.
- Use Wilson or exact intervals for shares near 0 or 1; the bootstrap degenerates there.
- B = 100 gives ±10 points: descriptive only.