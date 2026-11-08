# Paths across time reduce to row sequences

Status: Proved by hand. The finite claims are checked against full state spaces (`check.py`).

Ticket `NATIVE-PATH-20261108-001A`, 2026-11-08.

## Standard statement

- **The setting.** A path of n rings R_0, …, R_(n−1). Contact c_(i+1) is a cell of both R_i and R_(i+1), so both rings read it.
  - **Middle rings.** A middle ring R_i holds two contacts, c_i at its index 0 and c_(i+1) at index k_i, d_i = min(k_i, m_i − k_i)
    cells apart.
  - **Rules and laws.** Every non-contact cell updates by its ring's elementary rule, and each contact has its own law.
  - **Two cases.** Four rings and three contacts is the case searched in ticket B. Three rings is `PROCESS-CHAIN-20261108-001`.
- **Binding.** A contact binds two rings at lag T when every minimally decisive set of its value meets both rings' first-row cells.
  - **A native path.** Every contact binds its own two rings at every lag, and the last contact binds the end rings R_0 and
    R_(n−1) at every lag from the light-cone lag on.

The results:

1. **Theorem 1 (light cone).** Contact c_j does not depend on R_0's first row before lag d_1 + … + d_(j−1) + 1. So the last
   contact can bind the end rings only from lag L = d_1 + … + d_(n−2) + 1.
2. **Theorem 2 (affine reduction).** For linear or affine rules and affine laws:
   - a contact binds two rings at lag T exactly when the support of its row of M^T meets both;
   - each contact's row sequence is eventually periodic, so iterating the contacts' row vectors until they repeat decides every
     verdict above exactly;
   - for each finite path, that iteration is a complete proof.

## Nearest known result

- **Light cones on graphs.** Theorem 1 is the light cone of an automaton on the path's graph.
- **The three-ring case.** Theorem 2 is `AFFINE-WIRE-20261108-001A` extended from three rings to n.
- **Classification.** Known-with-delta: elementary. The delta is the native-path reading of the contact-network gate.

## Theorem 1

*Proof.*
- **The induction.** By `PROCESS-CHAIN-20261108-001A`'s Theorem 2 applied ring by ring, R_0's influence reaches c_1 at lag 1 at the
  earliest. It then crosses each middle ring at one cell per step.
- **Contact by contact.** R_(i−1)'s cells read only their ring, and c_i reads only its two rings. So c_(i+1) can depend on R_0
  only from d_i lags after c_i can. Summing gives the bound. ∎

**Computed (check 4).** On 400 random four-ring paths with arbitrary elementary rules, the last contact never depends on R_0 before
lag d_1 + d_2 + 1.

## Theorem 2

*Proof.* As in `AFFINE-WIRE-20261108-001A`, with more contacts:
- **The linear form.** Each contact's value at lag T is the parity of its row of M^T, plus a constant.
- **Binding.** A parity is fixed only by covering its whole support, so a contact binds two rings exactly when its support meets
  both.
- **Eventual periodicity.** Each row sequence r ↦ rM is eventually periodic, and the verdicts at the lags up to the repeat stand
  for all lags. ∎

**Computed.**
- **Check 1.** For three rings the path reduction gives AFFINE-WIRE's verdicts on 3,000 random chains.
- **Check 2.** The matrix rows equal the full state space's linear map on 300 random four-ring paths.
- **Check 3.** The verdicts equal the full-state-space verdicts on 800 random affine four-ring paths. None of the 800 is a native
  path.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | Three rings: agreement with AFFINE-WIRE on 3,000 chains | pass |
| 2 | The linear map, 300 four-ring paths | pass |
| 3 | Full-state-space verdicts, 800 four-ring paths | pass |
| 4 | The light cone, 400 paths with arbitrary rules | pass |

## Nonclaims

- **Two-time knots only** (A30).
- **No physics.** No physical time or dynamics is claimed.
