# Scoping for COPRIME-DICHOTOMY-20261027-001B-E001

Exploratory scripts run before the contract was frozen. They are not part of the frozen run; paths inside them point to the
session scratchpad where they were written.

- `scope_c1.py`, `scope_c2.py`: the four-way algebra at characters of order d > 2 on single knots and on K # K. At slope d/1 a
  cross-summand (z-channel) placement obstructs; at slope d/p every cross-summand placement lifts, while single-summand (local)
  placements still obstruct on twist knots. Reason: λ^p acts trivially on an exponent-p group, so S³_{d/p}(K) only imposes μ^d.
- `amph_test.py`: local four-way forms vanish on negative amphichiral 3-braid knots (4_1, 6_3, 8_9, 8_17, 8_18) at all 52 tested
  roots; 4 of 62 chiral rows vanish.
- `survey_nonsq.py`: random braid knots; vanishing local forms occur at non-square roots too, but rarely.
- `presmodel.py`, `twobridge_scan.py`, `genus2_scan.py`, `fox_check.py`: two-bridge knots from Schubert's normal form (odd β
  required; an even β gave wrong groups and was fixed). Genus-one b(4MN+1, 2N): the local form vanishes exactly when M ≡ N mod p,
  so only at square roots; genus-two knots also vanish at some non-square roots.
- `cable_test.py`: (2,1)-cables of amphichiral knots have vanishing local forms at every root, non-squares included; cables of
  chiral knots do not, except where the companion root is -1.
- `squier.py`: the solution space of Bur_{1/t}(g)^T J Bur_t(g) = J is two-dimensional; J_t lower unitriangular with
  J_{qq'} = (t - 1) t^(q - q' - 1) recovers the r = 2 form at t = -1.
- `steer_d.py`: the steering rule with d-strand bundles and κ_t = t^-2 - t^-1 matches exactly at d = 3, 4, 6.
- `t_gadget.py`, `t_class4.py`: gadget forms (four-way) and layer-4 steering through free layer-2 classes match at d = 3, 4, 6.
- `t_far.py`: after quotienting by failing pairs, every surviving triple failure is near (b = ±a), as Jacobi forces.
