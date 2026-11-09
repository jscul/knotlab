# Why doubling keeps every stage balanced

Epic `DOUBLE-BALANCE-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** Backlog B50. `GROW-ALL-20261109-001` computed, to lag 2, that the doubling law (every ring of a running tube split
  into a 2 × 2 block each lag) keeps every stage balanced, and `GROW-HORIZON-20261109-001` proved that it isolates every ring. The
  coordinator asked for B50 next on 2026-11-09.
- **The question.** Why does doubling keep every stage balanced, at every lag, and what does slower doubling do?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Transfer.** If at a lag no cell outside a ring X holds any part of X's born cells and X's own cells hold them independently, then every contact binds X from then on exactly as it does in the static stage. | proved | A |
| 2 | **Doubling every lag keeps every stage balanced, at every lag.** Isolation gives the first condition; the second holds because, with every contact newborn before each step, X's own cells evolve by a unipotent map in each corner. The stages are square tori with sides at least 3, balanced, so whenever growth stops every contact persists. | proved; checked to 48 × 48 | A |
| 3 | **Slower doubling loses balance.** From the 3 × 3 tube at g = 2: doubling every 2, 4, 6 or 8 lags lets own cells hear other rings from the second doubling on, and a stage is unbalanced by 24 × 24 at the latest; every 3 lags the rings stay isolated and every stage balanced, by a cancellation particular to corners of one cell. | computed, exact | A |

## Answer

Doubling every lag keeps every stage balanced at every lag, by proof: it isolates every ring, and an isolated ring with independent own
cells is, for its contacts, as good as a fresh first row. The same isolation is what makes the doubling network read no distance while
it grows (`GROW-HORIZON-20261109-001`). Slower doubling lets rings hear each other, and then balance fails within two or three doublings
in every schedule read except one that happens to isolate. So in this family a network that grows while it runs keeps its knots across
time exactly when its rings do not hear one another, as far as computed.

## Reading

**Interpretation, not a theorem.**
- **Knots or neighbours, not both, while growing.** Under growth while running, persistence survives where the old mixtures cannot reach
  the cut contacts (`GROW-RUN-20261109-001A`, Theorem 1); the doubling law achieves that everywhere by cutting every contact at once.
  The price is that no ring hears another. Letting rings hear each other between doublings brings the mixtures back, and balance goes.
- **For G1 and G5.** A uniform local law can grow a plane of rings with every stage balanced, and growth can let rings hear each other
  within a horizon, but in the schedules read not both: distance across time and persistent knots across growth exclude each other here.
  Doubling every P lags already is growth that pauses for P − 1 lags, and it fails.

## Lag cutoffs and census-only claims

- **The theorem has no cutoff.** Conclusion 3 is read at each doubling lag to 48 × 48, at g = 2 only.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The theorem (2) | 48 × 48 from 3 × 3 at g = 2 (`GROW-ALL-20261109-001` read 24 × 24), 24 × 32 from 3 × 4, and g = 3 | pass (checks 1 and 2) |

## Literature and provenance

- **Sources.** Unipotent maps over GF(2); the return-cancellation criterion (`LOOP-NET-20261108-001A`); balanced tori
  (`GROW-NET-20261108-001A`).
- **Classification.** Known-with-delta.

## Workspace assumptions

- **Relied on.** A30, A32, A42 (confirmed), A44 (born cells open), A45 (declared rings).
- **Added.** None.

## Correction

**2026-11-09 · Narrowing** (`docs/CORRECTIONS.md`). The exclusion read here, knots across growth against rings hearing each other, was
read only at g = 2 (corners of one own cell). At g = 3, doubling every 2 or every 4 lags with open births keeps every stage balanced
while rings hear each other, to 24 × 24 (`ISOLATION-NEED-20261109-001`). The results stand; the reading holds at g = 2.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with four checks.
- **Administrative.** This note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — why doubling keeps every stage balanced | **Status:** Successful | Proved at every lag, by isolation; slower doubling computed to lose balance |
| Local direction — growth that keeps knots and lets rings hear each other | Research directions | In the schedules read the two exclude each other |
| Broader exploration — G1 with G5 | Known alternatives | Another birth rule (challenging A44); the horizon as a theorem; an invertible substrate (B39) |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | A plane grown while running keeps its knots only by isolating its rings |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned), B50 marked taken, B51 and B52 added. **Assumptions:**
none added.

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Another birth rule (B51; challenges A44) | 3/3 — Major | 2/3 — Testable | Under doubling every P ≥ 2 lags, let the new cells be born as copies of the cells they are inserted beside, or the cut contacts split by copy, and read balance and hearing at each doubling → a birth rule under which rings hear each other and every stage stays balanced, or none | Alternative · deferred |
| 2 | Isolation is necessary (B52) | 2/3 — Substantial | 2/3 — Testable | Prove that a doubling schedule in which some own cell hears another ring at a doubling lag leaves a stage unbalanced within a bounded number of doublings, or find a schedule that is balanced without isolating | Alternative · deferred |
| 3 | The horizon as a theorem | 2/3 — Substantial | 2/3 — Testable | As in `GROW-HORIZON-20261109-001` | Alternative · deferred |
| 4 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | As before | Alternative · deferred |

1. **Another birth rule.** Payoff 3: the way left in this family to a grown plane that keeps its knots and reads its distance, since
   pausing between doublings (P ≥ 2) already fails with open-born cells. Concreteness 2: the readings are exact and cheap; a copied cell
   holds no distinction of its own, so the binding of the new rings must be read anew.
2. **Isolation necessary.** Payoff 2: makes the exclusion a theorem. Concreteness 2.
3. **Horizon.** As before.
4. **Invertible substrate.** As before.

**Recommendation.** Research directions, #1 first: it tests whether the exclusion is a law of growth or of the open-birth rule.

## Final report as sent

Sent to the owner on 2026-11-09 at 23:35 UTC and copied here verbatim.

**Why doubling keeps every stage balanced (B50) is closed and published, with a proof for every lag.** ([decision note](https://github.com/jscul/knotlab/blob/main/research/DOUBLE-BALANCE-20261109-001/double_balance.md))

- **Proved:** if nothing outside a ring holds its born cells, and its own cells hold them independently, its contacts bind it exactly as they would from a fresh first row. Doubling every lag isolates every ring, and each ring's own cells evolve invertibly. So every stage, a balanced torus, stays balanced at every lag. This confirms B38's doubling at every size, not just to lag 2.
- **Computed:** doubling every 2, 4, 6 or 8 lags lets rings hear each other from the second doubling, and a stage is unbalanced by 24 × 24. Every 3 lags happens to keep the rings isolated, and stays balanced to 48 × 48.
- **So:** while this network grows, persistent knots and rings hearing each other exclude each other in every schedule read. The doubling law keeps its knots by keeping its rings apart.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: why doubling stays balanced | Successful | Proved at every lag, by isolation |
| Local direction: growth that keeps knots and lets rings hear each other | Research directions | In the schedules read the two exclude each other |
| Broader exploration: G1 with G5 | Known alternatives | Another birth rule (B51); B39 |
| Long-term goal: G1 Space from a law | Obstruction learned | A plane grown while running keeps its knots only by isolating its rings |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Another birth rule (B51; challenges A44) | 3/3 | 2/3 | New cells copy their neighbours, or contacts split by copy, under doubling every P ≥ 2 lags → balance with hearing, or none |
| 2 | Isolation is necessary (B52) | 2/3 | 2/3 | Follow the first hearing ring's returns across a doubling → a proof |
| 3 | The horizon as a theorem | 2/3 | 2/3 | Bound crossings by the time of flight → a proved radius per P |
| 4 | Invertible substrate (B39) | 2/3 | 3/3 | As before |

**Corrections:** none new. **Goals:** G1/G5 checkpoint (obstruction learned); B50 taken; B51 and B52 added. **Assumptions:** none added.

I recommend #1. It's the one route left in this family to a grown plane that keeps its knots and reads its own distance. Seven epics have closed in this thread today, so it's also a natural place to pause if you'd rather.
