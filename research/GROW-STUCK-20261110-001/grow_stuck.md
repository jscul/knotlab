# Grow where learning is stuck

Epic `GROW-STUCK-20261110-001` (backlog B68; G15 with G1; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md). Proof family:
`proofs/GROW-STUCK-20261110-001A/GROW-STUCK-20261110-001A-P001_a_learner_that_grows_only_when_stuck/`; stress test on K_6 in
[stress_test.py](stress_test.py).

## The question

In `GROW-HANDLE-20261110-001` the experimenter chose where to grow. Can the learner decide: grow only where learning is stuck?

## The answer

- **A floor on dissonance (proved).** Weigh dissonance as the count does, W = violated lines + E + |D| / 2. Then W ≥ |χ| / 2 in every state
  of every law: 1 on a sphere, 0 on a torus, g − 1 at genus g. The torus is the only shape with no forced dissonance.
- **Growth arithmetic (proved).** Each Fano atom lowers χ by 2. From a sphere, one growth reaches the torus's floor of 0; every further
  growth raises the floor by one, which no learning can remove. One handle is exactly right; more lock dissonance in.
- **The stuck learner (computed).** A learner that takes a step only when some sequence of at most r steps lowers W, and otherwise grows
  an atom at a violated line, is stuck at once on a sphere (its flat state is already at the floor) and grows at the dissonance, on every
  start. With sight r ≥ 3 it grows once and resolves in 3 sign changes (34 of 34 runs on K_2 to K_5, and on K_6). With r ≤ 2 it cannot see
  the 3-step resolution the handle offers, so it grows again and again, never changing a sign, to genus 3 with W = 4 (34 of 34).

For the owner's picture: growing where you are stuck is the right rule only if you can see far enough to use what you grew. A learner that
grows at every impasse without looking ahead piles up handles, and each extra one is permanent, unresolvable dissonance.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| W ≥ \|χ\| / 2 in every state and law (theorem 1) | proved by hand; checked on every configuration visited |
| One growth from a sphere reaches floor 0; each further growth adds one unit forever (theorem 2) | proved by hand |
| A sphere's flat state is at its floor, so the learner is stuck at once and grows at the dissonance | proved; computed on every start |
| r ≥ 3: grows once and resolves in 3 sign changes; r ≤ 2: overgrows, never resolves | computed (K_2 to K_6) |

## Against the pre-registration

P0, P1 and P2 held. P3 held in what the learner does; its clause that an overgrown learner sits at the floor of each new genus did not:
it sits 2 above, carrying one class-forced pair.

## Provenance and novelty

Theorem 1 is an immediate reading of the count of `COUNT-SURFACES-20261107-001A`; its use as a floor for learning and growth, and the stuck
learner, are new as far as the record goes. No outside prior-work search was made.

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — grow where stuck (B68) | **Status:** Successful | grows once at the dissonance, given sight 3 |
| Local direction — steering by re-signing | Continue | growth is now triggered by the learner |
| Broader exploration — learning program | Known alternatives | layers through atoms, overgrown surfaces |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | the network grows from the learner's own state |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Layers through atoms (sub-goal B54) | 3/3 — Barrier | 2/3 — Testable | several lines of K_2 replaced by atoms → the dissonance crosses levels, or stays at one | Selected · started |
| 2 | Learning on an overgrown surface (B70) | 1/3 — Incremental | 3/3 — Ready | GROW-r with r ≥ 3 from genus 2 and 3 → it reaches the floor, or stops above it | Alternative · deferred |
| 3 | Why random learning goes the long way (B69) | 1/3 — Incremental | 3/3 — Ready | trace both holes → a reason | Alternative · deferred |

- **#1** is next by the coordinator's order; John flagged it.
- **#2** asks whether a far-sighted learner can bring an overgrown surface down to its floor.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B68 taken; B70 added. **Assumptions:** A49 added (dissonance is
weighed as the count weighs it).

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (01:01 UTC).

**B68 done: the learner can decide where to grow, and the right amount is exactly one handle.** I proved a floor: total dissonance is at least half the Euler characteristic's size. That's 1 on a sphere, 0 on a torus, and g − 1 at genus g, so the torus is the only shape that forces none. A learner that grows only when it can't see a way to lower the dissonance is stuck at once on the sphere, and grows right at the dissonance. If it looks 3 steps ahead, it grows once and resolves in 3 sign changes. If it looks 2 or fewer, it can't see what the new handle offers, keeps growing, and locks the dissonance in for good (computed, K_2 to K_6).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: grow where stuck (B68) | **Status:** Successful | grows once at the dissonance, given sight 3 |
| Local direction: steering by re-signing | Continue | growth now comes from the learner |
| Broader exploration: learning program | Known alternatives | layers through atoms, overgrown surfaces |
| Long-term goal: G15 | Capability gained | the network grows from the learner's own state |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Layers through atoms (B54) | 3/3 — Barrier | 2/3 — Testable | several lines of K_2 replaced by atoms → dissonance crosses levels, or not | Selected · started |
| 2 | Learning on an overgrown surface (B70) | 1/3 — Incremental | 3/3 — Ready | far-sighted learner from genus 2-3 → reaches the floor, or not | Alternative · deferred |
| 3 | Why random learning goes long (B69) | 1/3 — Incremental | 3/3 — Ready | trace both holes → a reason | Alternative · deferred |

**Corrections:** none. **Goals:** G15 checkpoint; B68 taken; B70 added. **Assumptions:** A49 added (dissonance weighed as the count weighs it).
