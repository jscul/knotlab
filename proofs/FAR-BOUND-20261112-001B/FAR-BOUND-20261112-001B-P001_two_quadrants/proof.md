# No length on two quadrants of a typical travelling base

Status: Proved (computer-assisted: a hand argument with exact finite checks), referee pending

Ticket `FAR-BOUND-20261112-001B`, 2026-11-12. The base was selected by the pre-registration's frozen rule: the first base, in the
order r ascending and then sample index, that ticket A's recheck classes bounded across. It is sample 24 of
`COMMON-FOLD-20261112-001A-E001` at r = 3.

## Standard statement

Let H be the 3-uniform hypergraph on ℤ² whose edges are the translates of {0, (0,1), (1,2)}, {0, (1,−4), (2,0)} and {0, (0,4), (2,2)},
under proper 2-colourings. Write t′ = (1, 2) and u = (0, 1) (a basis of ℤ²), and (α, y) for α t′ + y u. Then for every (α, y) with
α ≥ 1 and y ≥ 0, and for every (α, y) with α ≤ −1 and y ≤ 0, some minimal non-shattered set of at most four vertices contains the
origin and (α, y). So the bond distance from the origin is at most 3 on those two quadrants of the frame.

In the program's words: on this base the law reads no length at all on two opposite quadrants: every distinction there is within
bond distance 3 of the origin, however many steps away.

## Proof

**The frame.** In the frame the kinds are {(0,0), (0,1), (1,0)}, {(0,0), (1,−6), (2,−4)} and {(0,0), (0,4), (2,−2)}. Let
T_j = {(0, j), (0, j+1), (0, j+2)}.

**Travel in two directions (C1).** The pattern 000 on T_0 forces 111 on T_0 + t′ = {(1,0), (1,1), (1,2)} and 111 on
T_0 + 4u = {(0,4), (0,5), (0,6)}: each forced value is a refutation in a finite window, so it holds in every state of H. The base and
not-all-equal are unchanged by translations and by complementing every value, so the pattern σ(p) on any translate T_0 + w forces
the complement on T_0 + w + t′ and on T_0 + w + 4u. By induction on m + n, the pattern 000 on T_0 forces (−1)^{m+n} on
T_0 + m t′ + 4n u for all m, n ≥ 0; so it forces the value at (α, y) for every α ≥ 0 and y ≥ 0 with y mod 4 in {0, 1, 2}. By
translation, the pattern 000 on T_j forces (α, y) for α ≥ 0, y ≥ j and (y − j) mod 4 in {0, 1, 2}.

**Freeness (C2, C3).** T_0 is free: each of its four patterns up to complement is carried by an eventually periodic strip, a state of
H periodic across and repeating along outside a finite stretch (a sound certificate: the SAT window holds two copies of each tail
block, constrained equal, with periods at least the kinds' spans, so every solution extends by repetition and every edge of the
extension is a translate of one inside the window). Its translates T_{−1}, T_{−2} are free too. For the parts with x: take one state
family that repeats with period 4 along outside the along-counts [−2, 2) and with period 8 across outside [−4, 4), constrained in the
same way in both directions. Its value at x = (α, y) equals its value at x's representative (α itself for α < 2, else 2 + (α − 2)
mod 4; y itself for y < 4, else 4 + (y − 4) mod 8), and a representative never coincides with a cell of T_j. So whether a pattern on
π ∪ {x} (π a pair of T_j) is carried depends only on x's representative: finitely many cases. Check C3 verifies, for every
representative with α ≥ 1 and y ≥ 0, that some j ∈ {0, −1, −2} with (y − j) mod 4 in {0, 1, 2} has every pattern of every part
π ∪ {x} carried (1,620 cases).

**The bond.** For x = (α, y) with α ≥ 1, y ≥ 0, choose j as in C3. Then T_j ∪ {x} is not shattered (T_j's pattern 000 forces x, C1),
T_j is free (C2), and each π ∪ {x} is free (C3); its other proper subsets are subsets of these. So T_j ∪ {x} is a bond of four holding
the origin (every T_j with j ∈ {0, −1, −2} holds (0,0)) and x. The second quadrant follows from d(0, v) = d(0, −v) and translation. ∎

**Why the census called this base rank 1.** Its second travelling direction is 4u, longer than the census's shifts (entries at most
2): rank ≥ 1 was a lower bound. Without the kind {0, (0,4), (2,2)} the travel along 4u disappears (C4).

## Nearest known result

Directional determinism with two independent directions gives forced cones (Boyle and Lind; bootstrap percolation's stable directions,
Bollobás, Smith and Uzzell). The statement for not-all-equal, read as bond distance, was not found. Classification: known-with-delta
for the mechanism.

## Checks

`check.py` (result in `result.json`): C1 the two travels; C2 T_0 free; C3 the parts free at every representative; C4 the mutation.
