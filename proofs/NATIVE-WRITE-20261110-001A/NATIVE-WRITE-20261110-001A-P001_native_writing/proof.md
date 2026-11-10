# Native writing on four fresh spaces

Status: Proved (P1, P2 by hand) with computed and exact checks. `check.py` (about two minutes, the spaces in parallel), ticket A of
`research/NATIVE-WRITE-20261110-001/preregistration.md`, frozen with the code in commit `22c1a427f` before any run on the test spaces.

## The learner

It sees its own dissonance (violated lines, agreeing corners at each face, W and the change in W of each of its moves), the floor |χ|,
and the address asked for: a bit per atom, each atom given by its region (its lines and every face they touch). It never reads a role, a
class, a solver's answer or a target configuration (`write_lib.py`).

- **Probe.** On a copy, 20,000 steps of a state-only walk on the floor plateau (a random point flipped when W does not rise). An atom
  asked 1 fails if its region is ever free of dissonance; an atom asked 0 fails if its region is never free of it.
- **Attention.** Sign changes are allowed only on the lines of atoms the last probe failed.
- **Moves.** Random proposals (a state flip, or a sign change at a site where dissonance shows, A21), accepted by the Metropolis rule on
  φ = W + (dissonance outside the regions of atoms asked 1), at temperature 2.0 on a failing atom's lines and 0.7 elsewhere, never above
  floor + 4. Every 200 steps at the floor it probes, and it stops when nothing fails.

## Proved by hand

**P1.** *An acting atom has dissonance in its region in every state.* Lemma 3 of `OTHER-ATOMS-20261110-001A`: if the atom's torus is
unsatisfiable in its class, every state satisfying the atom's lines has a region face with at least two agreeing corners. So in every
state either an atom line is violated or some region face agrees at two or more corners. The probe changes only the state, so during a
probe each atom keeps its class. Hence the probe never fails an acting atom asked 1, and an atom asked 0 whose region the probe finds
free of dissonance does not act. ∎

**P2.** *A write changes only failing atoms.* An atom's role is its lines' relation on its three outer points, which depends only on the
signs of its own lines; the learner changes signs only on the lines of atoms the last probe failed; state flips change no role. ∎

**Consequence.** At every stop each atom asked 0 is transparent, and an inexact stop can only be an atom asked 1 that does not act and
whose dissonance stayed in its region through all 20,000 probe steps.

## Computed

**Check 1 (exact, every class).** On the two dev spaces and S1 to S4, an atom acts exactly when its own constraints (its lines satisfied,
each region face agreeing at exactly one corner) cannot hold together: 1,120 acting and 3,360 transparent atom-classes, no exception. So
"the region can be cleared" is the role, read from the atom alone.

**Check 2 (the frozen test).** 20 writes per space, each target drawn from the space's writable addresses (those of classes with a floor
state), after each write one random point of the outermost host flipped and M1 run to the floor:

| Space | Points | Atoms | Writable | Exact and held | Inexact | Median steps (max) | Median probes (max) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 K_3, three thin leaves | 45 | 3 | 7 | 20 of 20 | 0 | 4,200 (41,200) | 17.5 (113) |
| S2 K_3, three Fano leaves | 54 | 3 | 7 | 20 of 20 | 0 | 6,500 (24,800) | 23 (81) |
| S3 outer K_3, two C(2, thin) | 78 | 4 | 15 | 20 of 20 | 0 | 10,200 (48,400) | 44.5 (178) |
| S4 outer K_3, two C(2, Fano) | 90 | 4 | 15 | 20 of 20 | 0 | 8,300 (103,600) | 32.5 (256) |

Every write stopped well inside its budget of 2,000,000 steps; the probes cost 9 to 24 million plateau steps per space.

**Check 3 (control U).** The same learner with the probe replaced by the same test read at one instant: 65 of 80 writes were inexact
stops (it stopped with units sitting in atoms asked 1 that did not act), 11 never stopped, 4 were exact and held.

## Against the pre-registration

Every mark held: native writing on all four spaces (80 of 80; the mark was 18 of 20 on each), R (no inexact stop), U (65 inexact, the mark
was 20), and the census. B119 is answered yes for this learner.

## What it says

A learner that sees only its own dissonance and the address asked for writes every writable address exactly and the address holds. What
made the old targeted search stop inexactly was reading units instead of roles; the probe reads the role natively, because an atom acts
exactly when the dissonance in it cannot be walked away by the state (P1 one way, check 1 the other, the walk's speed computed). Writing
is also local: atoms already right are never touched (P2).

Scope: four spaces of 45 to 90 points with three or four atoms, one frozen learner, 20 writes each; the stress test one size past is
ticket B.
