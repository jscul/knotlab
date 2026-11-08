# A census of second bands: interpretation

Experiment `GENUS-BAND-20261108-001A-E001` (exploratory), run 2026-11-08 under the frozen contract: 2,745,424 second bands in 13 s on 12
workers. Exact, with no lag cutoff. Counts are in `result.json`.

## Control

Subdividing every rung of the n × 2 torus contains the torus band rule, which `BAND-SURFACE-20261108-001A` proves balanced. It appears:
exactly one balanced second band in that family for each n = 3, 4, 5, of genus 1, the n × 3 torus.

## Primary observable

| Base | Family | Second bands | Balanced |
| --- | --- | --- | --- |
| The 20 genus-2 first bands on loops of 5 | every rung subdivided, every way | 155,520 | none |
| | stacked by single rungs, every way | 311,040 | none |
| | stacked by double rungs, uniform rules | 2,880 | none |
| | joined to both rows, uniform rules and 300,000 random cases | 301,080 | none |
| The n × 2 tori, n = 3, 4, 5 | every rung subdivided, every way | 9,288 | 3, one per n, all genus 1 (the torus band rule) |
| | stacked by single rungs, every way | 37,376 | none |
| | joined twice to one row: every way at n = 3, uniform rules and 100,000 random cases at n = 4, 5 | 1,928,240 | none |

The 20 genus-2 bases are exactly the first bands with two or three twisted columns, a column being twisted when both of its rings reverse
their order (10 of each).

## Reading against the decision rule

- **H1 holds.** The second band is the step where every band fails for genus 2: no second band in the families keeps a genus-2 base
  balanced.
- **H2 holds.** On the n × 2 tori the only balanced second band in the families is the torus band rule, which keeps genus 1. No second
  band adds a handle while every contact persists, so "one band per handle" does not extend within these families.

## Nonclaims

- **These families only.** Bands not aligned column by column with the first, or of another length, are not covered.
- **Two-time knots only** (A30).
