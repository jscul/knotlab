# A growing plane reads taxicab distance in conformal time

Status: Partial (frozen statement, before the proof is written)

Ticket `CONF-METRIC-20261110-001A`, 2026-11-10.

## Frozen statement

- **Setting.** The open n × n tube (n ≥ 3) of rule-60 rings of 4g cells (g ≥ 2) with law (12, 12) contacts, under the doubling law with
  open births and any schedule: a doubling at lag 0, then runs of P_1, …, P_m ≥ 1 lags, each followed by a doubling. Stage k is the
  network between the k-th and (k + 1)-th doublings after lag 0; its square torus has side n 2^(k+1) rings. A **route** is a sequence of
  cells, each read by the next one lag later (an own cell reads itself and its left neighbour, a contact its two left neighbours), and
  at a doubling lag a route must be on an own cell of an old ring. **T1(v)** is the first lag at which a route from ring (0, 0)'s own
  cell at position 1 at lag 0 reaches the own cell at position 1 of the original ring at displacement v. **Conformal time** is
  φ(t) = Σ_{τ < t} 2^−k(τ), k(τ) the stage of the step τ → τ + 1 (A56). d(v) is the taxicab distance on the original n × n torus.
- **Lemma 1 (one stage).** With no doubling between lags t_0 and t, the earliest arrival from a cell c to a cell c' not on c's segment
  is t_0 + ℓ_out(c) + g H_k(c_out, c_in) + ℓ_in(c'), where c_out is the first contact after c on its ring (ℓ_out cells away), c_in the
  last contact before c' (ℓ_in cells), and H_k the hop distance of the contact lattice: 2 |Q − P|_1 / s_k between contacts of the same
  orientation and 2 |Q − P|_1 / s_k ± 1 otherwise (s_k the ring side). From a position-1 cell to the position-1 cell of the ring at
  ring displacement (a, b): 2g + 2g min(|a + 1| + |b|, |a| + |b − 1|), the minimum also over the torus's images.
- **Theorem 2 (conformal time reads taxicab distance).** For every schedule and every v ≠ 0, whenever T1(v) is defined,
  4g d(v) − 6g ≤ φ(T1(v)) ≤ 4g d(v) + 9g + 2; and T1(v) is defined as soon as the schedule's conformal length reaches 4g d(v) + 9g + 2.
- **Corollary 3 (a metric up to a constant).** The conformal round trip R̃(v) = φ(T1(v)) + φ(T1(−v)) lies in [8g d(v) − 12g,
  8g d(v) + 18g + 4] wherever it is defined, so R̃(u + w) ≤ R̃(u) + R̃(w) + 42g + 4: at every size and for every schedule, a metric up to
  an additive constant, and up to that constant 8g times the lattice's taxicab distance.
- **Corollary 4 (computed, not proved).** Plain lags have no such bound: a family of schedules whose plain round-trip excess grows
  without bound.
- **Remark to establish.** Whether the 4g 2^k crossing law is a consequence of the construction (expected from Lemma 1: two hops,
  2g lags, per ring step along an axis, and 2^(k+1) ring steps per original spacing in stage k).

## Stop rule

Stop at a proof of Lemma 1 and Theorem 2 with these constants, each checked: Lemma 1 against breadth-first search on fixed stages, and
Theorem 2 against every reading of `EXPAND-READ-20261110-001A-E001` and against fresh random schedules on the 5 × 5, 7 × 7 and 9 × 9
tubes at g = 2 to 5. If any reading breaks a bound, the proof has a gap: report the case and the step, and narrow the statement
(larger constants or fewer schedules) rather than claim it.

## Provenance of the statement

Not blind. The one-stage formula and the constants were worked out while tracing `EXPAND-READ-20261110-001`'s 28 residual schedules
(the first step the coordinator set): the formula was checked there against all 7,695 first-stage readings (all equal), and the constants
come from a sketch (the potential φ(t) + 2^−k d_k, nondecreasing along routes within a stage, with bounded jumps at doublings). No
reading has been checked against Theorem 2's bounds before this freeze.
