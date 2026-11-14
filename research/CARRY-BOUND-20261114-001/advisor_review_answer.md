<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

**Verdict:** B is sound once three premises are made explicit, it widens a long way, and P1 and P2 are mostly settled by construction.

## Soundness of B

The core argument holds. I did not run anything; this is checked by hand.

- **Minimality when p occurs elsewhere:** not a problem. Only p's marginal enters the projection on W. Since x and y are pendant, every allowed state extends to all six NAE triples, whatever else constrains p.
- **Missing premise, living:** "p takes both values" needs at least one allowed state in the limit. Complement closure alone gives nothing on an empty family (the same gap the referee found in Rule N).
- **"Occurs nowhere else":** the syntactic condition in S's block suffices for the whole pattern, provided own distinctions are fresh per copy and "no call's arguments" covers calls to every definition, not only SELF. Identity-graph edges must come from SELF calls only, or the depth-s copy is not "reached through S calls".
- **Quantifier order:** as written, k depends on s, but the knot is stated for one k. State it with K, the set of positions carrying a pendant knot: for every large s, some k in K is reachable in exactly s steps.
- **Residue test:** iterate the reachable sets R_s until one repeats, then check that every set in the cycle meets K. That is exact. If only some residues are covered, B bounds L_any on those progressions only; report that as its own cell, not as "every large s".
- **Tie variant:** sound only if the tie is derived from constraints (ties survive added constraints and compose with sign around the cycle). A tie read off a finite depth is not a proof.

## Widening

Non-shattered survives added constraints; only the freeness of subsets is fragile. Complement closure excludes frozen singletons. So take any constraint NAE(p, x, z) in the whole pattern, with x an own distinction of the depth-s copy and z anything (a port, a side-copy member, or non-pendant).

- {p, x, z} is non-shattered, so it contains a bond.
- That bond contains both p and x unless z is tied opposite to p or to x while {p, x} is free.
- If z equals p or x, NAE forces x = ¬p, a size-2 bond, which is better still.

Widened B: L_any(s) ≤ 3 unless one of those two opposite ties holds. This covers the carried size-3 bonds in TRUE-RATE. The cost is that "occurs nowhere else" becomes a semantic no-opposite-tie check, which needs its own periodic certificate.

## Design and predictions

- **P1** is a syntax count over the census generator. It measures coverage and tests nothing.
- **P2** is nearly settled by widened B: in stratum I, any knot joining the conserved port to an own distinction bounds L_any. Failures are confined to families where the conserved port is only passed on or knotted with ports, to residue gaps, and to opposite ties. Predict the size of that residual class instead.
- **P3** compares a near-syntactic rate with a real one. O's share alone carries the information, and with n = 91 the interval is about ±10 points. T at n = 5 supports no rate; report it family by family.
- **Step 3:** depth 6 may not clear the preperiod plus one period, and the DP is only an upper bound. "Grows to depth 6" must go in the undecided cell, never under unbounded. Fix how undecided counts in the P2 and P3 denominators before unblinding.
- **Sample:** stratify by period and by whether the conserved port touches an own distinction.