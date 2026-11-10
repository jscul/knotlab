# A learner that grows only when stuck

Status: Proved by hand (theorems 1 and 2); the learner's behaviour is computed (`check.py` check 2, and the stress test
`research/GROW-STUCK-20261110-001/stress_test.py` on K_6). Pre-registered in `research/GROW-STUCK-20261110-001/preregistration.md`.

## 1. The dissonance weight and its floor

For a law s and a state x on a knot space over a closed surface, let W = (violated lines) + E + |D| / 2, with E = Σ_v ⌊agree_v / 2⌋ and D
the even faces: each kind of dissonance (A46) weighed as the count weighs it.

**Theorem 1 (the floor; proved).** W ≥ |χ| / 2 in every state of every law.

*Proof.* The count (`COUNT-SURFACES-20261107-001A` theorem 3) is violated − E + |D| / 2 = χ / 2. Every term of W is nonnegative, so
W = violated + E + |D| / 2 ≥ |violated − E + |D| / 2| = |χ| / 2. ∎

So the floor is 1 on the sphere, 0 on a torus and g − 1 at genus g ≥ 2, and only a torus can be resolved (W = 0), which is
`LEARN-HANDLES-20261109-001` theorem 1 again. On a torus W = 2E, so W falls only when E does and reaches 0 only at resolution.

**Theorem 2 (growth arithmetic; proved).** Growing a Fano atom lowers χ by 2 (`GROW-HANDLE-20261110-001` theorem 1). From a sphere, one
growth gives a torus, whose floor is 0; every further growth raises the floor by one, so after a second growth no learning ever resolves the
dissonance, and each further handle adds one more unit that no learning removes.

*Proof.* χ = 2 − 2g after g growths, and theorem 1 gives the floor |1 − g|. ∎

A flat state of a knot sphere has W = 1, the floor, so no sequence of learning steps lowers W: a learner that waits for a lowering is stuck
at once, and the only dissonance it sees is the violated line l0.

## 2. The learner GROW-r (computed)

GROW-r holds the state fixed and takes the first step of a shortest sequence of at most r learning steps that lowers W; when none exists it
grows a Fano atom at a violated line (`stuck_lib.grow_r`; the growth move of `GROW-HANDLE-20261110-001` on any orientable knot space).
From the flat state at one line of each line orbit of K_2, K_3, K_4 and K_5 (17 starts), r = 1 to 4:

- **Every start is stuck at once and grows at l0**, for every r (68 of 68 runs).
- **r = 3 and 4:** one growth, then 3 sign changes, resolved, χ = 0 (34 of 34). The resolution is visible within 3 steps because the
  cheapest resolution after growing at the dissonance costs 3 (`GROW-HANDLE-20261110-001`).
- **r = 1 and 2:** after the first growth the learner is stuck again, since on the torus W = 2E falls only at resolution, which is 3
  steps away. It grows again at the violated line, now inside the atom, and again, to the cap of three growths, never changing a sign:
  χ = 2, 0, −2, −4 with W = 1, 2, 3, 4, one unit above the previous value each time and 2 above the floor from the torus on (34 of 34).
- **W ≥ |χ| / 2** held on every configuration visited (check 1).
- **One size past** (K_6, every line orbit, r = 2 and 3): the same.

Against the pre-registration: P0 to P2 held. P3 held in what the learner does; its clause "W at the floor of each new genus" did not: an
over-grown learner sits 2 above the floor, one class-forced pair, not at it.

## 3. Scope and novelty

The octahedral knot spheres K_2 to K_6 with their Kasteleyn law, the Fano atom of A48, the learner of A26 with the weight W (A49).
Theorem 1 is an immediate reading of the count; new as far as the record goes is its use as a floor for learning and growth, and the
computed behaviour of the stuck learner.
