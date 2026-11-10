# Closure of the Jordan chains from one polynomial

Status: Proved

Ticket `JORDAN-CHAINS-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/JORDAN-CHAINS-20261110-001/jordan_chains.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | One family Z(w) carries the spectrum (det Z = w^(h(1−n)) det(I + C_s)), is S + (a + δ)M_(Φ(a² + δ²)) near each eigenvalue parameter, and has first derivative a⁻¹(Z(a) + S). | new as far as found; proved | A (Theorem 1) |
| 2 | Z(w) is self-adjoint at every w, so the Jordan blocks are those of a ⌈k/2⌉ × ⌈k/2⌉ symmetric reduction. | proved | A (Theorem 2) |
| 3 | The first-order reduction is a⁻¹ times the Hankel matrix of the top coefficients of N(G) = G(k)G(k + 1); each eigenvalue has exactly k mod 2 blocks of size 1. | new as far as found; proved | A (Theorem 3) |
| 4 | a⁻¹kGY^i is the second vector of the chain GY^i heads when 2i < k − 1. | new as far as found; proved | A (lemma) |
| 5 | GY^j heads a chain of exactly 2k − 1 − 4j and these are the blocks: every eigenvalue, sides 8 to 64; nine at side 128 (pending at closure). | computed | A (checks 5 to 7) |
| 6 | The chain lemma beyond first order, and the degree law, are not proved. | the gap | A |

## Answer

An eigenvalue's Jordan structure follows the degree of its one polynomial wherever computed, and its first order is proved; the higher
orders and the degree law, and with them the collapse, are open.

## Recommendation

**Continue**, selected #1 (the chain lemma at every order, sub-goal B73), unless the coordinator chooses otherwise. The table is in the
decision note.
