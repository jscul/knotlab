# Are the composing lags native? Interpretation

Experiment `INTERMITTENT-NET-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 7,040 chains in 65 s on 16
workers. 71 did not repeat within 4,096 lags and are counted apart. Every other measure is exact over the eventual cycle. Rows are
in `rows.json`, totals in `result.json`.

## Control

It passes: every linear and affine chain with an affine law composes exactly at its arrival lags (ticket A's Theorem 2).

## Primary observable

244 chains compose at some lags of their eventual cycle but not at all of them.

| Chains composing at recurring lags | Composing | H1: composing = arrival | H2: both contacts bind there | Both |
| --- | --- | --- | --- | --- |
| Affine rule, affine law | 148 | 148 | 88 | 88 |
| Affine rule, other law | 16 | 4 | 12 | 4 |
| Nonlinear rule, affine law | 68 | 2 | 2 | 0 |
| Nonlinear rule, other law | 12 | 0 | 2 | 0 |
| All | 244 | 154 | 104 | 92 |

- **The affine rules here.** The shift rules 15 and 170 and the additive rules 60, 90, 105 and 150.
- **H1 fails.** In 90 chains c2 depends on both end rings at more cycle lags than those at which the chain composes. There the
  other cells can override an end, as in rule 30 at 5/6/5 with an XOR combiner, where both ends arrive at all 280 cycle lags and
  the chain composes at 248.
- **H2 fails.** In 140 chains some composing lag has a contact that does not bind its own pair. This includes 60 affine chains,
  such as rules 105 and 150 at 5/6/5, which compose at 18 of 30 cycle lags while both contacts bind at 23.
- **H3 fails.** Of the 121 rule-law groups that compose somewhere, 101 do not compose at every decided size. Twenty do:
  - the shifts 15 and 170 with both proposal parities and with several self-blind laws;
  - the additive rules 105 and 150 with the self-blind laws u = 3, 5, 10 and 12.

## Reading against the decision rule

- **Not native in general.** None of H1 to H3 holds as a universal statement.
- **Native in affine chains.** In 92 chains the composing lags are singled out by the chain: composition happens exactly where both
  ends' influence arrives, and both contacts bind there. Every one of the 92 runs an affine rule. With a nonlinear rule,
  intermittent composition is never singled out, because arrival does not settle it: some other cells can always override an end.
- **Shares and periods.** The share of composing cycle lags in the 92 ranges from 0.12 to 0.83. Their cycles have periods 4 to 62.

## Nonclaims

- **Declared chains only.** The stress test repeats the measures at 5/7/5 and 5/8/5.
- **Undecided chains.** 71 are counted apart.
- **Two-time knots only** (A30).
