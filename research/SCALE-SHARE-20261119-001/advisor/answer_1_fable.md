<!-- modelUsage: claude-fable-5-2 -->

I had no file access in this session, so everything below rests on your description. In particular I assume "round-1 demand" is non-decreasing in a knot's shared places and "open" = size − shared places. Nothing here is run; all of it is for you to check.

## The main point: the measure drives the stall trend

The uniform labelled measure counts descriptions, and descriptions with more shared distinctions are far more numerous. A heuristic count, treating shared places as sparse:

- Let E = Σ(5 − shared places of knot i), with m ≈ 5n/2 shared distinctions in total.
- A knot with 4 shared places has two size choices (4 or 5), so adding one shared distinction between two such knots changes the count by about E²/(4·5n).
- The count therefore peaks near E ≈ 2√(5n): about 2√(5n) knots sit one short of 5, half of them at size 4 with nothing open.
- Total open places ≈ √(5n), so **open places per knot ≈ √(5/n) → 0** and mean shared places per knot ≈ 5 − 2√(5/n).

Crude values: mean shared places 3.6 at n = 10 and 4.0 at n = 20; open per knot 0.7 and 0.5. Your whole plan (n ≤ 20) is pre-asymptotic, since 2√(5n) is not small against n until n ≫ 20. The trend is rule-free and you can read it straight off the sampler.

Two side effects at large n:
- **Connectivity** stops constraining: near-5-regular random multigraphs are connected with high probability.
- **Multiplicities ≥ 2** drop to O(1) per start in total.

## 1. Stall share

- **Rate.** Large sparse starts are locally tree-like, so over-demand events at different knots are weakly dependent. With p_n the per-knot over-demand frequency, non-stall ≈ exp(−n·p_n).
- **Pilot fit.** −ln(non-stall)/n is 0.118, 0.117, 0.10, 0.126, 0.18, 0.134, so q ≈ 0.88 per knot so far.
- **Faster than q^n.** p_n rises with n because open per knot falls, so the decay should outrun a fixed geometric rate.
- **Limit.** The stall share tends to 1. If a knot with nothing open and four or five neighbours is over-demanded, non-stall needs Θ(n) open places against a typical √(5n). That costs about exp(−Θ(n log n)), which is super-exponential.
- **Clustering.** The total shared-distinction count m is a common driver, so over-demand is positively correlated across knots. Expect P(no over-demanded knot) ≥ exp(−E[number over-demanded]), with the ratio tending to 1.

## 2. Among growers

The non-stalled ensemble is not the typical one. It is tilted toward few shared places, many leaves and tree-like structure, then filled with as many shared distinctions as the demand rule tolerates.

- **Dimension.** I expect two dimensions to stay the most common through n = 20. The pilot's dim 2 : dim 1 ratio is steady at about 4–5, and dimension 3 needs three endless chains into one piece of at most 5 places.
- **Rings.** This depends on the cycle rank the non-stall condition permits. If it allows a positive density of knots with three or more neighbours, cycles of length ≥ 5 are generic and the exponential share among growers should rise with n. If it forces near-trees, rings stay rare.
- **Pilot evidence.** Zero rings in about 150 non-stalled samples, which included dense starts at n = 8–10, suggests "something extra" is the binding condition. My low-confidence prediction: under 1% of all labelled starts for n ≤ 20, and non-decreasing as a share of growers.
- **Cheap discriminator.** Measure cycle rank m − n + 1 among non-stalled samples as n grows.

## 3. The break shape

- **Scaling.** It is a fixed local pattern containing a cycle (two centres sharing two knots). In a bounded-degree random structure, a pattern with v knots and e shared distinctions has about n^(v−e) expected copies. That is O(1) for one cycle and O(1/n) for two, so it does not grow with n.
- **Where it peaks.** At small n the starts are dense, so I expect the share of all labelled starts to peak around n = 7–10 at no more than 1–2%, then fall as stalls take over.
- **What to report.** Give it as a share of non-stalled starts, where it matters. There it could be several percent.
- **Bigger risk: new break shapes at n ≥ 7.** The rule is exhaustively verified only through five knots. About half of 200 spot checks per n are stalls, which leaves about 100 informative checks. Zero failures then bounds the failure rate only at about 3% (95%).
- **Suggested change to the spot checks.** Take 200 non-stalled samples per n and add n = 10 and 12, since the classification at 10–20 otherwise rests on unvalidated extrapolation.

## 4. The measure and the sampler

- **Keep uniform-labelled as primary.** It has no parameters and continues the census. State in the freeze that its large-n stall share reflects the counting above as much as the rule. Add shares conditional on non-stall, and shares stratified by m, which hold up under a change of measure.
- **Importance weights.** At large n almost all descriptions have trivial automorphisms, so the two weightings converge; that is harmless. The trap is at n = 6–10: rare, highly symmetric starts carry weight up to n! times typical and are almost never sampled. The distinct-weighted shares are then high-variance and biased low for symmetric classes, probably "closes". Report the effective sample size (Σw)²/Σw².
- **Twin leaves.** Among growers, two equal leaves on the same knot give order-2 automorphisms that stay common.
- **Irreducibility.** One-step moves under the connectivity and cap constraints need an argument: bridges cannot be removed, and saturated knots cannot accept. The decisive check is that the chain's reachable set at n = 5 equals the enumerated census. 200 samples "within noise" is weak, so run a chi-square with about 10⁴.
- **Mixing.** The slow mode is m. Start the 8 chains dispersed (a spanning tree and a saturated start), thin by at least 10·n² proposals, and compute R-hat on both m and the stall indicator.
- **Rare classes.** At n = 20, 8,000 samples give only about 400 non-stalled, so shares near 10⁻³ are unresolvable. Add a chain tilted by exp(−β·number of over-demanded knots) and reweight, or restrict to non-stalled if that set is connected under the moves.

## 5. Predictions to freeze, with falsifiers

| # | Prediction | Falsified if |
| --- | --- | --- |
| P1 | Mean open places per knot falls with n, about √(5/n) within a factor 1.5 (≈ 0.5 at n = 20) | Flat or rising from n = 8 to 20 |
| P2 | Stall share is non-decreasing from n = 7. Non-stall is in [0.12, 0.22] at 12, [0.06, 0.13] at 16 and [0.03, 0.08] at 20 | Non-stall(20) > 0.12 |
| P3 | −ln(non-stall)/n does not decrease from n = 10 to 20, and P(none over-demanded) ≥ exp(−mean number over-demanded) | Either inequality fails beyond noise |
| P4 | Closes as a share of non-stalled declines with n | It rises from n = 6 to 16 |
| P5 | Two dimensions is the most common among polynomial growers at every n, with dim 2 : dim 1 between 2.5 and 6; dim 3 is at most 2% of all; no dim ≥ 4 | Any of these fails |
| P6 | Exponential is under 1% of labelled starts at every n ≤ 20 (low confidence) | Above 3% at any n |
| P7 | Out-of-scope share of all labelled starts peaks at n in 7–10 and stays at or below 2% | Still rising at n = 16–20 |
| P8 | The labelled-versus-distinct share difference shrinks with n and is within noise by n ≥ 12 | A stable gap at n = 16–20 |

The single sharpest falsifier of this analysis is P1, because it is rule-free. If open places per knot do not fall, my account of why stalls take over is wrong, and the stall trend must come from the rule's demand growth alone.
