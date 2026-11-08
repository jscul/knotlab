# When intermittent composition is a law

Status: Proved by hand. The finite claims are checked on the census chains (`check.py`).

Ticket `INTERMITTENT-NET-20261108-001A`, 2026-11-08.

## Standard statement

- **The setting.** Chains of three rings joined by two shared contacts, as in `PROCESS-CHAIN-20261108-001`: ring A and ring B share
  c1, ring B and ring C share c2, and every non-contact cell updates by its ring's elementary rule.
- **Composition.** The chain *composes at lag T* when c2 binds the end rings A and C at T: every minimally decisive set of c2(T)
  meets both end rings' first-row cells.
- **The T-step maps.** The chain's state space is finite, so its T-step maps M^T are eventually periodic: there are T1 and P with
  M^(T + P) = M^T for every T ≥ T1.

The results:

1. **Theorem 1 (strobing).** For T ≥ T1 every verdict about c2(T) as a function of the first row, composition included, has period
   P. So the chain observed only at the lags T ≡ r (mod P), with r ≥ T1, composes at every observed lag or at none. Intermittent
   composition is persistent composition of a strobed chain, and the phase r is the only input that the chain does not fix.
2. **Theorem 2 (linear arrival).** For linear or affine rules with affine contact laws, the chain composes at lag T exactly when
   c2 depends on both end rings at T. Its composing lags are the lags at which both ends' influence arrives.
3. **Theorem 3 (composition needs arrival).** For any chain, if it composes at lag T, then c2 depends on both end rings at T.

## Nearest known result

- **Eventual periodicity.** It is classical for finite deterministic dynamics.
- **The linear case.** It is `PROCESS-CHAIN-20261108-001A`'s Theorem 3, read as an arrival law.
- **Classification.** Known-with-delta. The delta is the doctrine's reading. A strobe is an input supplied from outside, like a
  scheduler, unless the chain itself singles out its phase. So intermittent composition is native only where the chain fixes its
  composing lags.

## Theorem 1 (strobing)

*Proof.*
- **The maps repeat.** c2(T) is the contact bit of M^T applied to the first row. For T ≥ T1, M^(T + P) = M^T, so c2(T + P) and
  c2(T) are the same function of the first row.
- **So do the verdicts.** Every verdict computed from that function, binding and dependence included, is the same at T and T + P.
- **Strobing.** At the lags r, r + P, r + 2P, …, with r ≥ T1, c2 is one fixed function, so the chain composes at all of them or at
  none. ∎

**Computed (check 1).** On 264 random chains, every rule class three times at random census sizes and laws, the verdicts at a random
cycle lag T recur at T + P, T + 2P and T + 3P, with the maps recomputed from scratch. One chain did not repeat within 4,096 lags;
the other 263 agree.

## Theorem 2 (linear arrival)

*Proof.*
- **The linear form.** For linear or affine rules and affine contact laws, c2(T) is the parity of a support set R_T plus a constant
  (`PROCESS-CHAIN-20261108-001A`, Theorem 3).
- **Dependence.** c2(T) depends on a ring exactly when R_T meets that ring's cells.
- **Binding.** It binds two rings exactly when R_T meets both.
- **So composition is arrival.** The chain composes at T exactly when c2 depends on both A and C at T. ∎

**Computed (check 2).** The 16 linear and affine rules with affine laws of both families, at the four census sizes: 512 chains and
6,016 lags up to their repeats, all agreeing.

## Theorem 3 (composition needs arrival)

*Proof.*
- **No dependence, no binding.** If c2(T) does not depend on ring A, a full setting of the cells outside ring A fixes it. So the
  cells outside ring A decide c2(T), and c2 does not bind A.
- **The other end.** The same holds for ring C. ∎

The converse fails in general: c2 can depend on both end rings while the cells outside one of them can still fix it
(`PROCESS-CHAIN-20261108-001B`'s overriding chains).

**Computed (check 3).** All 2,816 chains of 3/4/3 and 4/4/4 cells: 75,114 lags, and at each composing lag c2 depends on both end
rings.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | Theorem 1: verdicts recur with the period of the maps (263 chains) | pass |
| 2 | Theorem 2: 6,016 lags of linear chains | pass |
| 3 | Theorem 3: 75,114 lags | pass |

## Reading

**Interpretation, not a theorem.**
- **When a phase is native.** The doctrine lets no executor, scheduler or checker supply an input. An observer who looks only at
  composing lags supplies a phase, unless the chain singles those lags out itself.
- **Linear chains.** Here it does: the composing lags are the arrival lags of both ends' influence, fixed by the chain's own
  algebra (Theorem 2).
- **Other chains.** Arrival is necessary (Theorem 3) but not sufficient. Whether the composing lags are still singled out by the
  chain, and whether they survive transport to other ring sizes, is ticket B's question.

## Nonclaims

- **Two-time knots only** (A30).
- **No physics.** No physical time or dynamics is claimed.
