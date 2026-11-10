# Where units sit together

Status: A1 and A3 proved by hand; A1 to A4 checked exactly (SAT over every state of every class). `check.py` (3 minutes), ticket A of
`research/MANY-POINTS-20261110-001/preregistration.md`, frozen in commit `880f19375` before any run.

## Setting

Space (b) of `NEST-ATOMS-20261110-001`: the outer host K_2 with composites C1 and C2, each K_2 with two leaves, genus 4, floor 3 units.
Regions: R1 and R2 the faces at C1's and C2's triangles (disjoint), R0 the rest; u_r the units in R_r at a floor state.

## Proofs

- **A1.** Lemma U of `NEST-ATOMS-20261110-001A` gives u_i ≥ 1 + [C_i acts]; u_0 ≥ 0; and at the floor u_0 + u_1 + u_2 = 3. So no region
  holds three units; both composites acting would need four; if C1 acts, u_1 ≥ 2 and u_2 ≥ 1 force (0, 2, 1), and symmetrically; if
  neither acts, the distributions with u_1, u_2 ≥ 1 are (1, 1, 1), (0, 2, 1) and (0, 1, 2). ∎
- **A3.** If C_i acts, u_i = 2 by A1, and both its leaves act (theorem N), so each holds at least one unit in its own region (lemma 3 of
  `OTHER-ATOMS-20261110-001A`). The two leaf regions are disjoint and lie in R_i, so each holds exactly one and the rest of R_i none. ∎

## Results (exact)

For both leaf types, in all 256 classes: 225 classes with neither composite acting realize exactly (1, 1, 1), (0, 2, 1) and (0, 1, 2); the
15 with C1 acting realize only (0, 2, 1), the 15 with C2 acting only (0, 1, 2); the one class with both acting has no floor state. So
**A1 and A3 held, and A2 held**: every distribution the theorem allows is realized in every class.

**A4 (recorded).** A composite that does not act can hold two units. If one of its leaves acts, that leaf holds one or both of them and
the other unit can sit in the other leaf or on the composite's sphere part, but neither of those can hold two. If no leaf acts, either
leaf or the sphere part can hold one or two. The same for both leaf types.

So two units sit together in a composite only one per leaf when it acts, and anywhere it allows when it does not; three never do.
