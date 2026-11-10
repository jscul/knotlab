# Writing with more addresses

Status: Computed (searches and random learners; not exhaustive). `check.py` (6 seconds), ticket C of
`research/MANY-POINTS-20261110-001/preregistration.md`, frozen in commit `880f19375` before any run: the re-test of
`NEST-ATOMS-20261110-001C` with more addresses.

## What is checked

That ticket's procedure unchanged, on its space (outer host K_2) and on the same space with the outer host K_3, for each leaf type, with
the targets A1, A2, A4, A3 cycled six times: 96 writes, random.Random(105). Primary: held when the acting leaves after the return equal the
target. Secondary: exact writes (acting leaves after the write equal the target) and the held share among them.

## Results

| Leaves | Writes | Reached | Held | Exact writes | Held among exact writes |
| --- | --- | --- | --- | --- | --- |
| Fano | 48 | 48 | 43 (89.6%) | 43 | 43 |
| thin (2,1,2) | 48 | 48 | 48 (100%) | 48 | 48 |

With thin leaves the expectation (at least 95%) held. With Fano leaves the result landed between the marks again, 89.6%, below 95% and
above the 80% failure line, all five misses on the K_2 host. Every miss was an inexact write, the frozen search stopping with a unit in a
leaf that did not act; every exact write, 91 of 91, held after the disturbance. So the return is reliable here, and the misses are the
search's stopping rule, which reads units rather than roles.
