# Shared contacts that do not read themselves: interpretation

Experiment `SHARED-CONTACT-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 68,992 configurations in 11 s
on 16 workers. A verdict is exact at every lag where the dynamics repeated within 4,096 lags, and 148 configurations did not.
Rows are in `rows.json` (compact columns), totals in `result.json`.

## Controls

All three pass.
- **Lag 1.** Every configuration binds at lag 1, as ticket A's Theorem 2 says for parities of nonconstant u and v.
- **The linear case.** Linear and affine rules with affine u and v lose binding exactly where the contact's row of M^T stops
  meeting both rings.
- **A second implementation.** On 300 sampled rows the direct simulation, read with `process_contact_lib.binds`, gives the same
  first failure to lag 8.

## Primary observable

| Size | Every lag | From some lag on | Recurring | Decays | Undecided |
| --- | --- | --- | --- | --- | --- |
| 3 + 4 | 572 (3.3%) | 72 | 2,788 | 13,816 | 0 |
| 4 + 4 | 1,196 (6.9%) | 448 | 3,110 | 12,494 | 0 |
| 4 + 5 | 854 (5.0%) | 498 | 3,672 | 12,216 | 8 |
| 5 + 6 | 1,806 (10.5%) | 638 | 4,058 | 10,606 | 140 |

- **Against the proposal family.** 6.4% of self-blind configurations bind at every lag, against 4.5% of proposal parities on the
  same rings (`PROCESS-CONTACT-20261108-001B`). H1, which asked for at least twice, fails.
- **Without the rings that never read the contact.** Rules 51 (negation) and 204 (identity) ignore their neighbours. Their rings
  never read the contact, so the contact only listens, and all 1,568 of their configurations bind at every lag. Without them, 4.2% of
  self-blind configurations persist, against 4.7% for the proposal parities.
- **Many more rules persist.** 157 (rule, size) pairs have some persistent self-blind law, against 22 for the proposals. Only
  rule 94 at 5 + 6 persists under a proposal parity and no self-blind law. 69 rules persist somewhere, and 12 at every size: 12,
  25, 51, 54, 60, 76, 108, 126, 140, 200, 204 and 232.
- **Which laws.** Laws with u = v persist in 6.7% of configurations, others in 4.1%. Laws where u and v are both XOR or XNOR
  persist in 10.3%.
- **Binding decays early.** Of the 49,132 configurations whose binding decays, 21,296 lose it at lag 2 and 17,136 at lag 3.

## Reading against the decision rule

- **H1 fails.** The rarity of persistent shared contacts does not belong mainly to the contact reading its own value. Removing that
  makes every parity bind at lag 1 and spreads persistence over many more rules. But once the rings that never read the contact
  are set aside, it does not make persistence more common.
- **The contact's past comes back through the rings.** Both rings read the contact, so c(0) enters a_1(1) and a_{m−1}(1), which a
  self-blind contact reads at the next step. Its own past returns to it after two steps.
  - **Rules canalizing in a neighbour.** For the 27 rule classes canalizing in a neighbour input, the contact's past fixes what it
    will read, and their rings persist in 1.1% of configurations.
  - **Rules canalizing in neither.** The 58 classes canalizing in neither neighbour persist in 5.8%.
  - **Rules that read no neighbour.** The three classes whose rule reads no neighbour (0, 51 and 204) never feed the contact back;
    two of them persist everywhere and rule 0 forgets at once.
- **Size.** Persistence rises with size, from 3.3% at 3 + 4 to 10.5% at 5 + 6. Ticket C measures that trend to 8 + 9.

## Nonclaims

- **Declared sizes only.** The 148 undecided configurations are counted apart.
- **Two-time knots only** (A30).
- **Parities only.** Self-blind parities only, not every self-blind law.
