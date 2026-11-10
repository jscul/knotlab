# Uniform growth

Status: Proved by hand (claim U), from `UNIFORM-FANO-20261107-001A` and `OTHER-ATOMS-20261110-001`; the census checked by `check.py`
(1 second), as frozen in `research/NATIVE-ATOM-20261110-001/preregistration.md` (commit `4a6ce578f`).

## The class

A rule σ(T, p) fires at a violated line and splices in T less a point, T a lattice-torus type of `OTHER-ATOMS-20261110-001D`, with the
uniform law p: the same sign pattern (p_0, p_1, p_2) on the three sides of every line, by side index. The new sides are forced up to gauge.

## Claim U (by hand)

σ(T, p) grows an atom that acts as its replaced line, and so holds the dissonance it was fired at, exactly when T is the Fano torus and p
is constant.

*Proof.* Every face of a lattice torus has three line corners, one of each side index, so a uniform pattern flips each face by
2(p_0 + p_1 + p_2), an even number: the law has no even face. By lemma 2 of `OTHER-ATOMS-20261110-001A` and the freeness of every lattice
torus (ticket D there), the atom acts exactly when its torus's law, here the uniform one, has no satisfying state. If p is not constant,
every line carries signs that are not all equal, so the all-zero state satisfies every line (theorem 1 of `UNIFORM-FANO-20261107-001A`). If
p is constant, the law is the plain not-all-equal law, unsatisfiable exactly when the triple system is not 2-colourable; a lattice torus is
point- and line-transitive under its translations, so by that record's corollary this happens only for the Fano plane. ∎

So the four-point thin atom, and every class-forced atom except the Fano atom, is grown by a uniform rule only as a transparent atom:
growth alone deletes the line's constraint and removes the dissonance. Its acting class is not uniform.

## The census (computed)

All 157 types × 8 patterns = 1,256 uniform laws have no even face; all are satisfiable except the Fano torus's two constant laws (000 and
111, one class). The 19 thin tori of even index, class-forced every one, have no unsatisfiable uniform law. As claimed; the failure line was
not crossed.
