# Pre-registration: grow where learning is stuck

Epic `GROW-STUCK-20261110-001` (backlog B68, G15 with G1), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## The question

In `GROW-HANDLE-20261110-001` the experimenter chose where to grow a Fano atom. Can the learner's own state decide: grow only where
learning is stuck, and does such a rule grow once, at the dissonance, and then resolve?

## Definitions

- **Dissonance weight.** W = violated lines + E + |D| / 2, each part counted as the count weighs it (E = Σ⌊agree/2⌋, D the even faces).
  The count (`COUNT-SURFACES-20261107-001A` theorem 3) gives violated lines − E + |D| / 2 = χ / 2 in every state and law.
- **The learner GROW-r.** The state is held fixed (A26). At each step it looks at every sequence of at most r learning steps (a sign
  change on a side of a violated line, or on a side with an end at an even face). If one lowers W, it takes the first step of a shortest
  such sequence. If none does and W > 0, it is stuck: it grows a Fano atom at a violated line (the lowest-numbered one; if there is none,
  at a line with a corner at an even face), by the first bijection that lowers χ by 2, with chirality 0, the old signs kept, the atom's
  signs 0 and the three new sides signed to add no even face, and extends the state to the atom's points by the first assignment that
  violates the fewest lines (A48). Caps: three growths, 60 steps.
- **Starts.** The flat states of `RESIGN-STEER-20261107-001` (one violated line l0, no over-agreement) at one line of each line orbit of
  K_2, K_3, K_4 and K_5; r = 1, 2, 3 and 4.

## Expectations, frozen

- **P0 (a dissonance floor; proved).** W ≥ |χ| / 2 in every state of every law, since W bounds |violated − E + |D|/2|. On a sphere the
  floor is 1, on a torus 0, and on a surface of genus g ≥ 2 it is g − 1. So only a torus can be resolved, and each handle beyond the first
  adds one unit of dissonance that no learning removes.
- **P1 (the sphere is stuck at once; proved).** A flat state already has W = 1, the sphere's floor, so no sequence of learning steps lowers
  W: GROW-r grows at once, at l0, the dissonance it sees, for every r.
- **P2 (one growth is the right amount; proved).** A Fano atom splice lowers χ by 2 (`GROW-HANDLE-20261110-001` theorem 1), so one growth
  makes a torus (floor 0) and a second makes genus 2 (floor 1), after which no learning ever resolves.
- **P3 (sight decides; computed).** On the grown torus W = 2E, which falls only at resolution, and the cheapest resolution from the extended
  state costs 3 (`GROW-HANDLE-20261110-001`). So with r ≥ 3 GROW-r grows exactly once, at the dissonance, and resolves in 3 more sign
  changes on every start; with r ≤ 2 it is stuck again, grows a second time, and never resolves, growing to the cap with W at the floor
  of each new genus.

## What would count against them

A start where GROW-r with r ≥ 3 grows more than once or fails to resolve, or where r ≤ 2 resolves, counts against P3. Any state with
W < |χ| / 2 would refute P0 and the count.
