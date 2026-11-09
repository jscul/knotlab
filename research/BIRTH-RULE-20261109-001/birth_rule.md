# Another birth rule for growth while running

Epic `BIRTH-RULE-20261109-001` (program foundations), 2026-11-09. A pre-registered frozen test of A44.

## The question

- **Where it comes from.** Backlog B51. `DOUBLE-BALANCE-20261109-001` proved that the doubling law keeps every stage balanced by isolating
  its rings, and found that with open-born cells (A44) slower doubling lets rings hear each other and loses balance. The coordinator gave
  B51 the go-ahead on 2026-11-09 as a frozen test of A44, whose challenge asks for cells born with values the network computes.
- **The question.** Is there a birth rule for the cells a doubling bears under which a growing network keeps every stage balanced while
  its rings hear each other?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Copies and zeros cannot be bound.** If the cells a doubling bears copy the cells they split from, or are zero, a new ring holds no distinction of its own and no contact can bind it: no stage is balanced, at any P. | exploratory, exact (H1) | A |
| 2 | **Open plus copy holds two doublings.** Adding the parent's value to an open distinction lets each new ring hear its parent from birth, and every stage stays balanced through 12 × 12 at P = 1 (6 × 6 at every P) while hundreds of own cells hear another ring; at 24 × 24 it fails at every P. | exploratory, exact (H2 refuted; H4 refuted narrowly) | A |
| 3 | **Open birth reproduces the control** (balanced at P = 1 and 3 with no hearing, unbalanced at P = 2 and 4), and under copy the old rings stay bound only at the first doubling. | exploratory, exact (H3, H5) | A |

## Answer

Not one that lasts. A new ring must bear open distinctions to be bound, so copies and zeros fail at once, as A44's reason said. The
mixed rule, an open distinction plus the parent's value, is the first rule in this line under which a growing network is balanced while
its rings hear each other, but only for two doublings: at 24 × 24 it fails at every schedule. A44 is confirmed for growth that keeps
going, with that qualification.

## Reading

**Interpretation, not a theorem.**
- **A beginning must be open.** A ring is bound only through distinctions of its own, so whatever a birth rule inherits, it must also
  open something. This is A44's reason, now tested.
- **Inheritance spreads the mixtures it must not.** Copying the parent's value into the new ring makes the new ring hear its parent at
  once, which balance survives for a doubling or two; then the mixtures reach the cut contacts and the returns stop cancelling, as under
  growth while running (`GROW-RUN-20261109-001`).
- **The exclusion holds for sustained growth.** In every rule and schedule read, a network that keeps growing keeps its knots across
  growth only while its rings stay isolated.

## Lag cutoffs and census-only claims

- **Exact.** Every reading is through a full cycle of the state. **Census-only.** All conclusions: one tube, four rules, P to 4, 24 × 24.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Open plus copy fails by 24 × 24 (2) | already the frozen run's size limit | not run further: 48 × 48 with every born cell a variable is the next size |

## Literature and provenance

- **Classification.** New as far as found, a frozen exploratory test.

## Workspace assumptions

- **Challenged.** A44: confirmed for stated reasons, with the qualification of conclusion 2.
- **Relied on.** A30, A32, A42, A45.

## Correction

**2026-11-09 · Narrowing** (`docs/CORRECTIONS.md`). The exclusion read here, knots across growth against rings hearing each other, was
read only at g = 2 (corners of one own cell). At g = 3, doubling every 2 or every 4 lags with open births keeps every stage balanced
while rings hear each other, to 24 × 24 (`ISOLATION-NEED-20261109-001`). The results stand; the reading holds at g = 2.

## Ratio

Since the epic opened:
- **Substantive.** One frozen exploratory test (A), 16 runs.
- **Administrative.** The pre-registration, this note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — another birth rule | **Status:** Successful | Every rule read; none sustains balance with hearing; open plus copy holds two doublings |
| Local direction — growth that keeps knots and lets rings hear each other | Research directions | Open plus copy is the only partial success; why it fails at 24 × 24 is open |
| Broader exploration — G1 with G5 | Known alternatives | Isolation is necessary (B52); the horizon as a theorem; invertible substrate (B39) |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Sustained growth while running keeps its knots only by isolating its rings, under every birth rule read |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned), B51 marked taken. **Assumptions:** A44 confirmed for stated
reasons.

**Next step:** Research directions — #1, B52, as the coordinator asked.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Isolation is necessary (B52) | 2/3 — Substantial | 2/3 — Testable | Follow the first hearing ring's returns across the next doubling, open birth and open plus copy → a proof that hearing breaks balance within a bounded number of doublings, or a schedule that is balanced without isolating | Selected |
| 2 | Why open plus copy lasts two doublings | 1/3 — Minor | 2/3 — Testable | Read the returns of the first unbalanced contact at 24 × 24 → the mechanism | Alternative · deferred |
| 3 | The horizon as a theorem | 2/3 — Substantial | 2/3 — Testable | As in `GROW-HORIZON-20261109-001` | Alternative · deferred |
| 4 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | As before | Alternative · deferred |

**Recommendation.** Research directions, #1 as ordered.

## Final report as sent

Sent to the owner on 2026-11-09 at 23:40 UTC and copied here verbatim.

**Another birth rule (B51) is closed and published. It was a frozen test of A44, and A44 is confirmed.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/BIRTH-RULE-20261109-001/birth_rule.md))

- **Copies and zeros cannot be bound:** a new ring that copies its parent, or starts at zero, has no distinction of its own, so no contact can bind it. No stage is balanced.
- **Open plus copy holds two doublings:** if each new ring gets an open distinction plus its parent's value, the network stays balanced through 12 × 12 while hundreds of its cells hear another ring. That's the first time in this line that a growing network keeps its knots and lets rings hear each other. It fails at 24 × 24 under every schedule.
- **Open birth** reproduced the earlier control exactly.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: another birth rule | Successful | Every rule read; none sustains balance while rings hear each other |
| Local direction: knots plus hearing while growing | Research directions | Open plus copy is the only partial success |
| Broader exploration: G1 with G5 | Known alternatives | Isolation as necessary (B52); horizon theorem; B39 |
| Long-term goal: G1 Space from a law | Obstruction learned | Sustained growth while running keeps its knots only by isolating its rings, under every birth rule read |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Isolation is necessary (B52) | 2/3 | 2/3 | Follow the first hearing ring's returns across a doubling → a proof, or a balanced schedule without isolation |
| 2 | Why open plus copy lasts two doublings | 1/3 | 2/3 | Read the first failing contact's returns at 24 × 24 |
| 3 | The horizon as a theorem | 2/3 | 2/3 | As before |
| 4 | Invertible substrate (B39) | 2/3 | 3/3 | As before |

**Corrections:** none. **Goals:** G1/G5 checkpoint; B51 taken. **Assumptions:** A44 confirmed: new cells must be open. Open plus copy is a two-doubling exception.

As the coordinator asked, I'm on #1 (B52) next. Open plus copy already shows that hearing doesn't break balance right away, so I'll aim for a bounded-delay statement, not an immediate one.
