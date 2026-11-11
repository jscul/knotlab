# Learning gates at deeper and wider groups

Status: Proved (exact realizability; learning computed, frozen). `check.py` (about sixteen minutes, 24 groups in parallel), ticket A of
`research/DEEP-MEM-20261111-001/preregistration.md`, frozen with the code in commit `6decb62ff` before any run on the test spaces.

## The test

The credit learner of `CREDIT-PIN-20261110-001B` with the sturdier probe of `STURDY-PROBE-20261110-001A`, unchanged but for an
8,000,000-step budget per target, at every group of three new spaces: T1 (two D2(thin) composites, each with a leaf three levels down),
T2 (two C3(thin) composites of three atoms each) and T3 (as T1 with Fano leaves); targets `1uu0`, `u10u`, `uuuu`, `0uu1`, then `0001`.

## Results

- **Check 1 (exact):** every gate target is realizable at every one of the 24 groups.
- **Check 2 (computed, frozen):**

| Kind of group | Writes learned and held | Median steps of learned gate-on writes |
| --- | --- | --- |
| Leaf (14) | 55 of 56 | 120,200 (27 writes) |
| One-atom composite, two levels down (4) | 16 of 16 | 129,400 (8) |
| Two-atom composite, three levels down (4) | 16 of 16 | 2,300,700 (8) |
| Three-atom composite (2) | 8 of 8 | 2,155,300 (4) |

- The one miss: a leaf of T1 three levels down (`0uu1`) did not stop within the budget, its map still `uuuu`.
- `0001` never stopped (24 of 24); no inexact stop anywhere. The probe took 1.2 billion walk steps in all.

## Against the pre-registration

L (98%), D1, D3 (100%), W3 (100%), A and R all held. **The predictions that D3 and W3 fail were wrong:** every composite write was
learned and held. The cost prediction held in part: depth alone costs nothing (a one-atom composite two levels down cost about what a
leaf did), a second atom under a composite multiplied it about eighteen times, and a third added nothing more here.
