**Verdict: P3 and P4 can pass on ties alone, and P2 is mostly the cap restating the control. Fix those before running.**

**Settled by construction**
- **P3:** yes, it is forced. Constraining means F(knot) ⊉ knot, and the cheapest way to get that is a tied port relation. Your own SETTLED list says ties propagate to every level below, so those families give L=2 at any d. Make P3 primary on tie-free bonds (3 ≤ L ≤ 5, L < d+2) and report ties separately.
- **P2:** under the ruler L=d+2, d ≥ 4 means L ≥ 6, which is "none within five" by the cap, and d ≤ 3 means L ≤ 5. If monotone families are mostly Berge-acyclic, P2 is P1 again. Test P2 on non-acyclic monotone families only, and report the acyclic share per stratum.
- **Unreachable pairs:** these have no bond by construction. Drop them from P2's "≤ 10%" denominator and count them separately.
- **P1:** this is a reader check against a proved result. Label it a code control, not a prediction.

**P4's form**
- Level and d are confounded, since the substitution sets the steps. Level 1 is near-d pairs and level ≥ 4 is far pairs, so the difference measures distance, except in tied families, where it passes automatically.
- A point estimate with no CI and a −0.10 margin cannot separate hold from die.
- Use a within-family slope of tie-free bonded share over level, stratified by d or measured relative to the uniform baseline at the same d.
- Pre-declare three bands (grow, hold, die) with a CI requirement.

**Other flaws**
- **Selection:** t ≤ 12 with ≤ 60 distinctions and level ≥ 4 keeps only slow-growing, chain-like families. Report keep rates per stratum and scope the claims to those.
- **Direct variant:** shared arguments probably collapse d to 1–2 across levels, so the d ≥ 4 cell may be near-empty. Set a minimum count, and compare by level, not d.
- **Direct variant definition:** define "constraining" for 4–6-port definitions explicitly.

**Overclaiming wording**
- "Carry influence" and "holds with level" should read "bonded within five" and "over levels 1 to the maximum observed". Nothing here speaks to asymptotics.
- A 0.10 share when monotone is allowed ≤ 0.10 is a weak bar. Rely on the CI of the difference, tie-free.

**Cheap additions**
- A per-family flag for a tied or forced port relation in F(knot), used as a covariate.
- A reread at depth t−1 for stability.
- A baseline matched on level as well as d.
- Counts per cell.
