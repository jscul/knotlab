# Pre-registration: layers through atoms

Epic `ATOM-LAYERS-20261110-001` (sub-goal B54, G15 with G16), written on 2026-11-10 before any run, at the coordinator's go-ahead; the owner
flagged the direction.

## The question

A Fano atom spliced in for a line acts from outside exactly as that line, in its class (`GROW-HANDLE-20261110-001`). Read the sphere's
points and lines as the upper level and each atom's inside as a lower level that stands for one upper line. When several lines are
atoms, where does the forced dissonance sit, and does learning carry it between the levels and between atoms?

## The spaces and the learner

- **Spaces.** K_2 and K_3, at one line l0 of each line orbit, with atoms (`stuck_lib.grow_any`) at a set Λ of lines: Λ = {l0}; Λ = {a}
  with a at line distance 2 from l0; Λ = {l0, b} with b at distance 1, 2 and 3; and Λ = {a, b} with a and b at distances 2 and 3. Genus
  |Λ|.
- **Levels.** A line or face is upper when every triangle at it comes from the sphere, lower (in atom j) when every one comes from atom j,
  and a junction otherwise. A dissonance (A46) has the level of its line or face.
- **State.** The sphere's flat state at l0 (one violated line), extended to each atom's points by the first assignment that violates the
  fewest lines, then held fixed (A26).
- **Learner.** The W-lowering learner of `GROW-STUCK-20261110-001` with sight r = 4 and no growth, at most 40 sign changes (W weighed as
  in A49). Its path is recorded with the level of every dissonance after each step.
- **Census.** On every genus-2 space, the faces that can host a floor configuration (one face with three agreeing corners, every other
  face one, no violated line): a perfect matching of the lines with the faces, that face taken three times.

## Expectations, frozen

- **B1 (the floor unit is frozen; proved).** With g atoms the floor is g − 1. At genus 2 a state at the floor has no violated line and no
  even face and exactly one face with three agreeing corners, so it offers no learning step (A26): a learner at the floor cannot move it.
- **B2 (both levels can hold it; computed).** On every genus-2 space the census finds host faces at the upper level and inside atoms.
- **B3 (one atom; proved and computed).** With Λ = {l0} or {a} the learner resolves the dissonance (W = 0), and every resolution changes a
  sign in the atom (`GROW-HANDLE-20261110-001` theorem 4): with Λ = {a} the dissonance starts at the upper level and is removed through the
  lower one.
- **B4 (two atoms; computed).** The learner reaches the floor W = 1 from every start, and the remaining unit ends inside an atom (the lower
  level) in most runs.

## What would count against them

A genus-2 floor state with a learning step, or a host census with faces of one level only (against B1, B2); a one-atom space the learner
does not resolve (against B3); a two-atom start where the learner stops above the floor, or a unit that ends at the upper level in most
runs (against B4).
