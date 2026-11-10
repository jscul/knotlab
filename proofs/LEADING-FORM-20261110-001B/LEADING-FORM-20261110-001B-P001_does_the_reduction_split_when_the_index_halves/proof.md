# Does the reduction split when the index halves

Status: Partial (pre-registered 2026-11-10, frozen before any run).

Ticket `LEADING-FORM-20261110-001B`, epic `LEADING-FORM-20261110-001` (sub-goal B91, its first step, as a side check).

## The test, frozen

At every eigenvalue with even k = 2c ≥ 4 for sides 16, 32 and 64, compute the reduction M of the family to ker X_b = G·F[Y]_(<J) (G
monic, basis G·Y^j) to order 2k, with two complements: W_0, the monomials off the kernel's top degrees, and W′, containing k·G·Y^j for
2j < k − 1 and filled with monomials. Each in two parametrizations: the family Ẑ in λ = u/(1 + u), and Z(a + au)/(1 + u) in u. That
makes four variants.

- **S1.** Every entry (i, j) with i + j odd vanishes modulo the parameter to the power 2k.
- **S2.** Every entry with i + j even has only odd powers of the parameter below 2k.

## The prediction and the decision

- **B91's strong form.** The reduction at k = 2c is the parameter times the reductions at c and c − 1 with the parameter squared,
  on the even and odd powers of Y. It predicts S1 and S2 for at least one variant at every tested eigenvalue.
- **Decision, frozen.** If a variant passes at every tested eigenvalue, the epic considers the induction on k and says which route it
  takes and why. If every variant fails somewhere, B91's strong form is recorded as refuted at these sides, the halving of the leading
  matrix (`CHAIN-ORDERS-20261110-001A`, Theorem 3, proved) stands, and the epic proceeds with ticket A's co-distance induction.
- **Disclosed before the run.** At k = 6, side 32, a = α^23, the W_0 entry (0, 1) has valuation 10 < 12 in u. Valuations do not depend
  on the parametrization, so S1 already fails for W_0 there; the prediction rests on W′.
