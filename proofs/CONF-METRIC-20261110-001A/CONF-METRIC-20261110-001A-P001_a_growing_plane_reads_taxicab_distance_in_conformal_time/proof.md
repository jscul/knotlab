# A growing plane reads taxicab distance in conformal time

Status: Proved by hand (Lemma 1, Theorem 2, Corollary 3). `check.py` checks Lemma 1 against breadth-first search and Theorem 2 against
the census and fresh schedules; Corollary 4 is a computation, not a theorem.

Ticket `CONF-METRIC-20261110-001A`, 2026-11-10. The statement was frozen in `603df0d23` before this proof was written.

## Standard statement

- **Setting.** The open n × n tube (n ≥ 3) of rule-60 rings of 4g cells (g ≥ 2) with law (12, 12) contacts, under the doubling law with
  open births and any schedule: a doubling at lag 0, then runs of P_1, …, P_m ≥ 1 lags, each followed by a doubling. Stage k is the
  network after the k-th doubling following lag 0; it is a square torus of side n 2^(k+1) rings. Ring (i, r) has its E contact at
  position 0 (shared with position 2g of ring (i + 1, r)), its N contact at position g (shared with position 3g of ring (i, r + 1)), its
  W contact at 2g and its S contact at 3g; the other positions are own cells.
- **Routes.** A route is a sequence of cells, one per lag, each read by the next: an own cell is read by itself and by the next
  position on its ring; a contact by the next position on each of its two rings. At a doubling lag a route must be on an own cell of an
  old ring, the only cells a doubling keeps. **T1(v)** is the first lag at which a route from ring (0, 0)'s own cell at position 1 at
  lag 0 reaches the own cell at position 1 of the original ring at displacement v, the time length of `METRIC-GROW-20261110-001` before
  its freeze readings.
- **Conformal time (A56).** φ(t) = Σ_{τ < t} 2^−k(τ), where k(τ) is the stage of the step τ → τ + 1. d(v) is the taxicab distance on the
  original n × n torus.

**Lemma 1 (one stage).** With no doubling between lags t_0 and t, the earliest arrival from an own cell c to an own cell c' that is not
ahead of c on its segment is t_0 + ℓ_out(c) + g H_k(c_out, c_in) + ℓ_in(c'): c_out is the first contact after c on its ring, ℓ_out cells
away; c_in the last contact before c', ℓ_in cells before it; H_k the hop distance on the contact lattice of stage k. Placing ring (i, r)
on the unit square [i, i + 1] × [r, r + 1], its contacts sit at the midpoints of its sides, and H_k(P, Q) = 2 |Q − P|_1 between two E–W
contacts or two N–S contacts and 2 |Q − P|_1 ± 1 between one of each (the exact value below), minimised over the torus's images. From a
position-1 cell to the position-1 cell of the ring at ring displacement (a, b) ≠ 0 it is 2g + 2g min(|a + 1| + |b|, |a| + |b − 1|).

**Theorem 2 (conformal time reads taxicab distance).** For every schedule and every v ≠ 0, whenever T1(v) is defined,
4g d(v) − 6g ≤ φ(T1(v)) < 4g d(v) + 9g + 2; and T1(v) is defined once the schedule's conformal length reaches 4g d(v) + 9g + 2.

**Corollary 3 (a metric up to a constant).** Wherever R̃(v) = φ(T1(v)) + φ(T1(−v)) is defined, 8g d(v) − 12g ≤ R̃(v) < 8g d(v) + 18g + 4,
so R̃(u + w) < R̃(u) + R̃(w) + 42g + 4: at every size and for every schedule the conformal round trip is a metric up to an additive
constant, and up to a constant it is 8g times the lattice's taxicab distance.

## Proof of Lemma 1

An own cell's only successor besides itself is the next position on its ring, so a route from c, unless the target lies ahead on c's
segment, reaches c_out after exactly ℓ_out moves, and staying only delays. Symmetrically c' is entered only from the previous position,
so every route into c' passes c_in, ℓ_in moves before. From a contact a route continues along one of its two rings, and the cells up to
the next contact on that ring are forced: a **hop** of g moves. So between c_out and c_in a fastest route is a shortest sequence of hops,
and the earliest arrival is as stated.

The hops. Along ring (i, r) the contacts follow E → N → W → S → E, so a hop moves from one side midpoint to the next counterclockwise, by
(−½, ½), (−½, −½), (½, −½) or (½, ½). An E–W contact lies on two rings, the E side of its left ring and the W side of its right ring, so
its two hops are (−½, ½) and (½, −½); an N–S contact's are (−½, −½) and (½, ½). Hops alternate the two kinds. From an E–W contact the
four two-hop walks displace it by (−1, 0), (0, 1), (0, −1) and (1, 0), one unit along each axis, and every two-hop walk is one of these;
likewise from an N–S contact. Between contacts of one kind the number of hops is even, each pair moves one unit, and the taxicab
displacement changes by at most one per pair: H = 2 |Q − P|_1. Between kinds the first hop is one of the two, and then pairs:
H = 1 + 2 min over the first hop δ of |Q − P − δ|_1, which is 2 |Q − P|_1 − 1 when Q − P lies in the closed quadrant of one of the two
hops and 2 |Q − P|_1 + 1 otherwise. On the torus, shortest hop walks lift to the plane, so H is the minimum over images.

For position 1 to position 1: c_out is the N contact of ring (0, 0) at (½, 1), ℓ_out = g − 1; c_in is the E contact of ring (a, b) at
(a + 1, b + ½), ℓ_in = 1; Q − P = (a + ½, b − ½), and the first hop from an N–S contact is (½, ½) or (−½, −½), leaving (a, b − 1) or
(a + 1, b). So the arrival is (g − 1) + g (1 + 2 min(|a| + |b − 1|, |a + 1| + |b|)) + 1. ∎

## Proof of Theorem 2

Fix v ≠ 0 and the target cell τ, position 1 of the original ring Y at v. For a route on cell c at lag t, with stage k in force for the
step from t, write D_k(c) for the stage-k earliest arrival time from c to τ (Lemma 1, as if no doubling followed) and set

  Ψ(t) = φ(t) + 2^−k D_k(c).

At the start Ψ(0) = D_0(source) = 2g + 2g min(|2v_x + 1| + |2v_y|, |2v_x| + |2v_y − 1|) over images (stage 0 has 2 ring steps per original
spacing), and this lies between 4g d(v) and 4g d(v) + 4g, since the minimum is between 2 d(v) − 1 and 2 d(v) + 1. At arrival Ψ = φ(T1(v)).

(a) **Within a stage Ψ never decreases**, and it stays constant exactly along a fastest route: one step changes D_k by at least −1 and
adds 2^−k to φ.

(b) **At a doubling Ψ jumps by J_k ∈ [−6g 2^−(k+1), 5g 2^−(k+1)].** The route is on an own cell c of an old ring. Its ℓ_out and τ's
ℓ_in = 1 are cell counts, unchanged; so with Lemma 1, J_k = 2^−(k+1) D_(k+1)(c) − 2^−k D_k(c) = −2^−(k+1) (ℓ_out + ℓ_in) +
g 2^−(k+1) (H_(k+1) − 2 H_k). In units of stage-k ring sides, the doubling shrinks every old ring to the lower-left quarter of its square,
so c_out moves by (−½, −¼), (−¼, −½), (0, −¼) or (−¼, 0) as it is an E, N, W or S contact, and c_in, always Y's E contact, by
(−½, −¼); their difference δ has |δ|_1 ≤ ½. Stage-(k+1) hop distances count in half units, so H_(k+1) = 4 |Δ + δ|_1 + ε' and
H_k = 2 |Δ|_1 + ε for the same pair of kinds, with ε, ε' both 0 (same kind) or both ±1 (different kinds), image by image. Hence
|H_(k+1) − 2 H_k| ≤ 4 · ½ + 3 = 5, and with 2 ≤ ℓ_out + ℓ_in ≤ g the bounds follow.

(c) **Lower bound.** Along a fastest route to τ, arriving in stage K, Ψ only grows except at the K doublings it crosses:
φ(T1(v)) ≥ 4g d(v) − 6g Σ_{k < K} 2^−(k+1) > 4g d(v) − 6g.

(d) **Upper bound.** Follow a fastest stage-k route from the current cell, recomputed after each doubling, except that when its next cell
is a contact and the next lag is a doubling lag, stay one lag instead (a contact is always followed by an own cell, since g ≥ 2, so this
is the only case where a route would be lost). This waits at most once per stage, each wait adding 2^−k to Ψ, and Ψ is otherwise constant
within stages and jumps by at most 5g 2^−(k+1) at doublings. So Ψ(t) < D_0 + Σ_k 2^−k + 5g Σ_k 2^−(k+1) ≤ 4g d(v) + 4g + 2 + 5g at
every lag before arrival. Before arrival D_k ≥ 1, so φ(t) ≤ Ψ(t) − 2^−k < 4g d(v) + 9g + 2: the route has arrived by the first lag at which
φ reaches that bound, if the schedule lasts so long, and at its arrival φ = Ψ is below it. T1(v) is no later. ∎

## Proof of Corollary 3

Add the bounds for v and −v (d(−v) = d(v)): 8g d(v) − 12g ≤ R̃(v) < 8g d(v) + 18g + 4. Then R̃(u + w) < 8g d(u + w) + 18g + 4 ≤
8g d(u) + 8g d(w) + 18g + 4 ≤ R̃(u) + 12g + R̃(w) + 12g + 18g + 4. ∎

## Remarks

- **The 4g 2^k law is a consequence of the construction.** Lemma 1 gives two hops, 2g lags, per ring step along an axis in every stage,
  and stage k has 2^(k+1) ring steps per original spacing, so a front moving along an axis within one stage gains one spacing per
  4g 2^k lags. `EXPAND-READ-20261110-001`'s 2,368 exact ring-to-ring increments are that consequence read in the census; its 28 shorter
  cell-to-cell increments show that the increment between two particular targets also depends on where their fastest routes entered
  the stage, which Lemma 1 alone does not fix.
- **Why conformal time.** In lags, a doubling halves the plane's speed in original units, so trips that cross more doublings cost more
  than the sum of shorter ones: Corollary 4's family shows the plain excess growing without bound. Counting a lag after k doublings as
  2^−k makes the speed 1/(4g) original spacings per conformal lag at every stage; what remains are bounded jumps at doublings (a ring
  shrinking toward its corner) and at most one wait per stage, both summable because they shrink with the stage.
- **The constants are loose.** In checks 2 and 3, φ(T1) − 4g d(v) stays between −6 and 4g (the upper end is the first stage's own offset, Lemma 1), and the largest conformal round-trip excess is 3, against the bound 42g + 4; the lower constant 6g is the loosest.
- **Conformal horizon.** The schedule's total conformal length can be finite (doubling every lag from stage k adds at most 2^(1−k)), and
  then rings beyond conformal distance about that length are never reached, as `GROW-HORIZON-20261109-001` found in lags.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Lemma 1 against breadth-first search on the cell digraph of fixed stages (n = 3, 5; g = 2 to 5; sides 2n and 4n; every own cell from 12 random own cells each): 326,400 pairs | pass: no mismatch |
| 2 | Theorem 2 on every schedule of `EXPAND-READ-20261110-001A-E001` (891, 13,614 route arrivals; this check's own route code agrees with `metric_lib` on every 40th schedule): both bounds, and every unreached ring below the reach bound | pass: φ(T1) − 4g d(v) runs from −5 to 4g; largest conformal round-trip excess 3 |
| 3 | Theorem 2 on 240 fresh random schedules (n = 5, 7, 9; g = 2 to 5; one to four runs, short runs favoured): 1,759 arrivals | pass: φ(T1) − 4g d(v) from −5.75 to 4g; largest excess 2 |
| 4 | Computed (Corollary 4): on [28, 2 repeated K times, 40·2^(K+1)] at n = 5, g = 3, with u = (1, 1), the plain excess R1(2u) − 2 R1(u) is 42, 114, 260, 548 for K = 0 to 3, roughly doubling, while the conformal excess stays at most 1 | pass |

## Nonclaims

- **The time length is the route first arrival.** `METRIC-GROW-20261110-001` also read it through explicit freezes (A41), which agreed
  in most cases; the theorem is about the route arrival.
- **Balance is not involved.** The theorem holds for every schedule, balanced or not; which schedules keep their knots is the census
  line's question.
- **Conformal time is a reading (A56)**, defined from the declared schedule's doublings; the network's own crossing times keep it (the
  first remark). No physics claim. Declared rings (A45) on a declared board (A51); open births (A44).
