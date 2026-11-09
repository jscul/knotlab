# Is isolation necessary for balance under doubling?

Epic `ISOLATION-NEED-20261109-001` (program foundations), 2026-11-09. A pre-registered frozen census.

## The question

- **Where it comes from.** Backlog B52. `DOUBLE-BALANCE-20261109-001` proved that isolation keeps every stage of the doubling law balanced
  and found, at g = 2, that schedules whose rings hear each other lose balance; `BIRTH-RULE-20261109-001` found the same for other births.
  The coordinator asked for B52 on 2026-11-09.
- **The question.** Does every doubling schedule whose rings hear each other leave a stage unbalanced within boundedly many doublings?
  The bound, two doublings, was frozen before reading.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No: isolation is not necessary.** At g = 3, open births doubling every 2 and every 4 lags keep every stage balanced while 144 to 1,152 own cells hear another ring, to 24 × 24. | exploratory, exact | A |
| 2 | **At g = 2 the bound holds.** Every hearing schedule there (open P = 2, 4, 5, 6, 8; open plus copy P = 1 to 8) has an unbalanced stage within two doublings of its first hearing, and P = 1, 3 and 7, one less than a power of two, isolate and stay balanced to 48 × 48. | exploratory, exact | A |
| 3 | **At g = 3 open plus copy fails at once** (12 × 12 at every P), and open P = 3 hears and fails at 12 × 12. | exploratory, exact | A |

## Answer

Isolation is sufficient for balance (proved, `DOUBLE-BALANCE-20261109-001A`) but not necessary: with corners of two own cells (g = 3) a
network that doubles every 2 or every 4 lags keeps its knots across growth while its rings hear each other, as far as read. The exclusion
reported by the last two epics was a fact about g = 2, and is corrected to say so. This reopens the route to a grown plane that keeps its
knots and reads its own distance while it grows.

## Reading

**Interpretation, not a theorem.**
- **Spacing decides what growth can keep.** With one own cell per corner, every mixture a ring hears reaches a cut contact at once; with
  two, the parity of the routes through a corner can cancel what crosses, and balance survives the hearing.
- **For G1.** The g = 3 schedules are the first native growth laws read that grow a plane of rings both ways while the network runs, keep
  every stage balanced, and let rings hear each other: growth with a horizon that still keeps its knots.

## Lag cutoffs and census-only claims

- **Exact per reading.** **Census-only.** All conclusions; the g = 3 counterexamples to 24 × 24.

## Stress test

**Pending** (`docs/LONG_RUNNING.md`, ISOLATION-NEED-A2): the two g = 3 counterexamples read further, to 48 × 48, as the frozen rule asks
(`read_further.py` beside this note; its output will be `read_further.json` and its log `read_further_log.txt`).

## Literature and provenance

- **Classification.** New as far as found, a frozen exploratory census.

## Workspace assumptions

- **Relied on.** A30, A32, A42, A44 (open births), A45.
- **Added.** None. A44's confirmation reason narrowed.

## Correction

This epic narrows `DOUBLE-BALANCE-20261109-001` and `BIRTH-RULE-20261109-001`: their exclusion was read at g = 2 only (`docs/CORRECTIONS.md`,
2026-11-09, Narrowing; a qualification of `DOUBLE-BALANCE-20261109-001-D001` on knotlab).

## Ratio

Since the epic opened:
- **Substantive.** One frozen exploratory census (A), 24 runs; the reading further, pending.
- **Administrative.** The pre-registration, this note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — is isolation necessary | **Status:** Successful | Refuted by a frozen census: two g = 3 schedules keep balance while rings hear each other |
| Local direction — a grown space that keeps its knots and reads distance | Continue | The g = 3 schedules are the first candidates |
| Broader exploration — G1 with G5 | Known alternatives | Why g = 3 keeps balance; their distance and horizon; larger g |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A native growth law grows a plane both ways while it runs, keeps every stage balanced, and lets rings hear each other (to 24 × 24) |

**Corrections:** one, Narrowing: the exclusion of the last two epics holds at g = 2 only. **Goals:** a G1 and G5 checkpoint (capability
gained), B52 marked taken, B53 added. **Assumptions:** A44's reason narrowed.

**Next step:** Continue — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Distance in the g = 3 growing plane (B53) | 3/3 — Major | 3/3 — Ready | On the open doubling law every 2 and 4 lags at g = 3, read each original ring's reach and the rings that hear it, as `GROW-HORIZON-20261109-001` did at g = 2, while confirming balance to 48 × 48 → a grown plane that keeps its knots and reads a distance within a horizon, or the size where balance fails | Selected · awaiting go-ahead |
| 2 | Why g = 3 keeps balance | 2/3 — Substantial | 2/3 — Testable | Follow a hearing ring's returns across one doubling at g = 2 and g = 3 → the cancellation, as a lemma | Alternative · deferred |
| 3 | Larger spacings | 2/3 — Substantial | 3/3 — Ready | Repeat the census at g = 4 and 5 → which schedules keep balance with hearing | Alternative · deferred |
| 4 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | As before | Alternative · deferred |

**Recommendation.** Continue with #1; stop it at a reading of distance on a balanced, hearing growing plane, or at the size where its
balance fails.
