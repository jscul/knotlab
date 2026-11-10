# Pre-registration: the leading form at every order

Epic `LEADING-FORM-20261110-001` (sub-goals B73 and B91, G5), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## The question

`CHAIN-ORDERS-20261110-001` reduced the chain lemma to one leading form: on the eigenvectors G·Y^j the reduction of the family starts at
u^(2k−1−2(i+j)) with coefficient [k − i − j a power of two]. It computed the form at every eigenvalue for sides 8 to 256 and proved it
for co-distance t = k − i − j ≤ 2. Can it be proved at every order?

## Two routes

- **Co-distance (ticket A, selected).** Find the reduction's vectors ψ_r in closed form order by order and read the leading coefficient
  at u^(2t−1) from ψ_1, …, ψ_(t−1) by the 2n + 1 rule.
- **Halving (ticket B, a frozen side check first).** If the reduction at k = 2c splits into u times those at c and c − 1 with u
  replaced by u², an induction on k may be shorter.

## Frozen

- **Stop rule for ticket A.** The first order r ≥ 2 with no closed form of ψ_r, verified exactly at every eigenvalue for sides 8 to 64,
  ends the attempt.
- **Ticket B's test, prediction and decision** are as written in its proof stub
  (`proofs/LEADING-FORM-20261110-001B/LEADING-FORM-20261110-001B-P001_does_the_reduction_split_when_the_index_halves/proof.md`), run
  before ticket A's attempt.

## What would count against

- For the leading form: an eigenvalue at which a coefficient differs from the form (none at sides 8 to 256 so far).
- For the halving route: every variant of ticket B's test failing at some eigenvalue.
