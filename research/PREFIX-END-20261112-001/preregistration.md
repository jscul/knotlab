# An end read from the prefix counts: pre-registration

Epic `PREFIX-END-20261112-001` (`AGE-NEST-20261112-001` direction 1; G17, with G7), 2026-11-12, at the coordinator's go-ahead.
Frozen before the registered run. The canonical K1–K3 test is unchanged. Words as in `AGE-NEST-20261112-001`: the **prefix counts**
are e(j), the knots among the oldest j distinctions, for every j. The weighting is the process X(0.3) (A71).

## The question

Redrawn cores that keep the prefix counts end about half the time, and those that keep only the degrees never do
(`AGE-NEST-20261112-001`, referee pending). Can a growth's end be read from its prefix counts alone, better than from what uses less,
and how close to the base's own chance of ending (its closing hazard)?

## In standard terms

For the 2-colourable prefixes of a grown 3-uniform hypergraph process, how well do statistics of the prefix-edge-count profile
discriminate the step just before 2-colourability is lost from steps of growths still at risk at the same age?

## What is settled or expected by construction (not tests)

- **The typical prefix density.** Each knot brings, in expectation, 0.43 closings, and a closing at n distinctions lands among the
  oldest j with probability (j/n)³, so E[e(j)/j] ≈ 1.43 + 0.214(1 − (j/n)²): about 1.64 for old prefixes. `OLD-CORE-20261112-001`'s
  dying cores at 1.55 to 1.67 are this typical density (the advisor's arithmetic); the largest density over j ≥ 20 is mostly small-j
  noise on it. So the known uniform end (about 2.1) is replaced by a finite-size null (Uprefix: uniform patterns with a prefix's own
  j and e(j)).
- **Only closings end a growth**, and an ending selects closing-rich histories, so knots per distinction is expected to carry some
  signal (E0).
- **The closing hazard is the base's own chance of ending at a uniform closing** (a knot ends it exactly when it falls on one side of
  one tie class), so it is a ceiling, not a test.
- **Pnest is not the base's end chance:** it is the share of patterns with these prefix counts that are already dead, while every
  base read is alive; it means something only between bases of one age, which is how it is compared.

## Design (frozen; `census.py`)

800 fresh X(0.3) growths to 6,000 moves. **Positives:** each ending's last base, at its age M (knots before the killing knot).
**Negatives (risk set, primary):** for each positive, three growths of the same run parity alive past age M, read at age M,
whatever happens to them later; **secondary:** three that live at least 500 knots more (cheap features only). Features: knots per
distinction; κ = Σd(d − 1)/Σd over distinctions' knot counts; the largest prefix density (j ≥ 20); Uprefix; Pnest (100 resamples);
the closing hazard (exact tie classes); a conditional logistic regression on paired differences of the cheap features and nine
prefix densities, fit on even runs and scored on odd runs. Metric: matched concordance (positive above its matched negative, ties
half), with growth-level bootstrap intervals.

## Predictions (frozen)

The advisor model reviewed a draft cold: it showed the draft's "a prefix past 2.1" passes almost a priori, that negatives selected
for a long future answer an easier question, that Pnest drifts with age and needs at least 100 resamples, that the fit needs
conditioning on age and a parity-respecting split, and it proposed the finite-size null, risk-set negatives, the hazard ceiling and
the kill condition below.

| # | Prediction | Fails when |
| --- | --- | --- |
| E0 | **Density carries some signal.** Knots per distinction has concordance at least 0.55. | below |
| E1 | **No prefix is past its own uniform end.** Fewer than 10% of last bases have a prefix whose uniform resample allows no state more than half the time (the same share reported for negatives). | 10% or more |
| E2 | **The prefix counts read the end.** Pnest's concordance is at least 0.65 and at least 0.05 above knots per distinction's, with the bootstrap interval of the difference above 0. **Kill:** within 0.05 of knots per distinction, the counts add nothing beyond density. | any part |
| E3 | **The largest prefix density is no better than density.** Its concordance exceeds knots per distinction's by at most 0.03. | above 0.03 |
| E4 | **A fit on the prefix densities beats the best cheap feature** on the held-out runs, with the bootstrap interval of the difference above 0. | interval reaches 0 |
| — | Reported: the hazard (ceiling), κ, the secondary negatives, tertiles of age. | — |

## Pilot (disclosed)

Forty growths with seeds 999000 to 999039 (scratchpad), fifteen endings each read against three survivors (always the same three):
largest prefix density of last bases 1.6 to 2.07; Pnest 0 to 0.9 against 0 to 0.95 for survivors. A smoke test of the frozen code
read one base (run 0's last base).

## Stop rule and runtime

One run (growths, then bases), its summary, a hand-off to the referee thread, report. About forty minutes on eight workers;
registered in `docs/LONG_RUNNING.md`.
