# Referee job PREFIX-END-R1: the brief

The coordinator handed this job over on 2026-11-12 (17:29 UTC). It comes from the random-meeting-patterns thread:
`PREFIX-END-20261112-001`, in commits 8db5147a7 and f6c277f43, pre-registered in 22005bffb. Its subject is X(0.3): 685 endings, each
matched with 3 risk-set negatives. Status: partially successful.

## Claims under review

| # | Claim | Result | Outcome |
| --- | --- | --- | --- |
| E0 | Knots per distinction reads the end | concordance 0.685 | held |
| E1 | No early part's uniform resample allows no state more than half the time | — | held |
| E2 | Pnest reads beyond density | 0.747, which is 0.062 over m/n | held |
| — | κ = Σd(d − 1)/Σd (reported) | 0.744, tying Pnest | — |
| E3 | The largest early density, maxD, is no better than density | 0.727, +0.042 over m/n against a bound of 0.03 | failed |
| E4 | A logistic fit on the prefix densities beats κ | 0.773, +0.009 over κ | failed |
| — | The law's own ties: the hazard | 0.947 | — |

## Questions

1. The risk-set sampling: are the negatives, those alive past age M, fair?
2. The hand-rolled conditional logit, against a standard implementation.
3. The bootstrap, which resamples positives only.
4. Is the reading "reads beyond density but not beyond degrees" fair?
5. The claim that Bollobás–Janson–Riordan gives no threshold condition for 2-colourability.

Also the usual: what is built in or known against new, frozen against after-run, and proved against computed.
