# Persistent composition in affine chains is a question about row sequences

Status: Proved by hand. The reduction is checked against full state spaces (`check.py`).

Ticket `AFFINE-WIRE-20261108-001A`, 2026-11-08.

## Standard statement

- **The setting.** A chain of three rings A, B and C, as in `PROCESS-CHAIN-20261108-001`, but each ring has its own rule and each
  contact its own law.
- **Affine chains.** Every ring rule is linear or affine. Every contact law is affine: a parity of the two rings' proposals, or a
  self-blind sum u_X(left, right) + u_Y(left, right) of affine u.
- **Rows.** The dynamics is s ↦ Ms + b over GF(2). For a contact c, let r_T(c) = e_c M^T, the support of c's value at lag T.

The results:

1. **Theorem 1.** c1 binds rings A and B at lag T exactly when r_T(c1) meets both rings' own cells. c2 binds B and C exactly when
   r_T(c2) meets both. The chain composes at T exactly when r_T(c2) meets A and C.
2. **Theorem 2.** Each sequence r_T(c), T = 1, 2, …, is eventually periodic. So the question is decided exactly by iterating
   r ↦ rM for each contact until the row repeats: do both contacts persist, and does the chain compose at every lag from d + 1 on?
3. **Theorem 3.** For a given finite chain this iteration is a complete proof of its verdicts.

## Nearest known result

- **Linear recurring sequences over finite fields.** Eventual periodicity of r ↦ rM is classical.
- **Classification.** Known-with-delta. The delta is the reduction of the contact-network gate across time, on affine substrates,
  to four row-part sequences that must never vanish.

## Theorem 1

*Proof.*
- **The linear form.** c(T) is the parity of the first-row cells in r_T(c), plus a constant: unwind T steps of s ↦ Ms + b.
- **When the outside decides.** A parity of a set R is fixed by a setting exactly when the setting covers all of R. So the cells
  outside ring X decide c(T) exactly when r_T(c) has no cell of X.
- **Binding.** By the definition of binding (`PROCESS-CHAIN-20261108-001A`), c binds X and Y at T exactly when r_T(c) meets both. ∎

## Theorem 2

*Proof.*
- **Finitely many rows.** r_(T+1) = r_T M, and r ranges over the 2^N subsets of the cells. So the sequence repeats: r_(T1 + P) =
  r_(T1) for some T1 and P ≥ 1, and from then on it is periodic.
- **The decision.** A condition on r_T that must hold for every T ≥ t0 holds exactly when it holds for every T from min(t0, T1) to
  T1 + P − 1, and for every computed T ≥ t0.
- **The four sequences.** Both contacts persist and the chain composes from d + 1 on exactly when ring A's and ring B's parts of
  r_T(c1) never vanish for T ≥ 1, ring B's and ring C's parts of r_T(c2) never vanish for T ≥ 1, and ring A's part of r_T(c2) never
  vanishes for T ≥ d + 1. ∎

## Theorem 3

*Proof.* The iteration of Theorem 2 computes every r_T exactly, and Theorem 1 turns each into its verdicts. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | The matrix rows equal the chain's linear map, read off the full state space, for 400 random chains with each ring its own linear rule, each contact its own law, sizes 3–5/3–6/3–5 and every contact position | pass |
| 2 | On 1,200 random affine chains (sizes 3–4/3–5/3–4) the row-sequence verdicts equal the full-state-space verdicts | pass |

In check 2, 12 chains compose at every lag from d + 1 on, which the census of `PROCESS-CHAIN-20261108-001B`, with one rule and one
law for the whole chain, never found.

## Reading

**Interpretation, not a theorem.**
- **The search.** The contact-network gate across time becomes a finite search on affine substrates: four row parts of M^T must
  never vanish. Each test takes a few hundred row operations, so whole families can be searched.
- **The obstruction to look for.** If none is found, the obstruction would be a gap that some row part of every affine chain is
  forced to have.

## Nonclaims

- **Affine chains only.** Nonlinear chains need their full state space.
- **Two-time knots only** (A30).
- **No physics.** No physical time or dynamics is claimed.
