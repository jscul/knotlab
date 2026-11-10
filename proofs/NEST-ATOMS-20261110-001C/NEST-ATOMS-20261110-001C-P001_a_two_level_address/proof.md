# A two-level address

Status: Computed (searches and random learners; not exhaustive). `check.py` (2 seconds), ticket C of
`research/NEST-ATOMS-20261110-001/preregistration.md`, frozen in commit `4b27647cb` before any run.

## What is checked

Space (b) of ticket B for each leaf type: the outer host K_2 with two composites C(2, leaf), leaves 0 and 1 in the first and 2 and 3 in
the second, floor 3 units. `ADDRESS-SEQ-20261110-001A`'s frozen targeted search and learner M1, unchanged except that a leaf's role is
read by SAT on its outer points, write the acting leaf sets {0, 1, 2}, {0, 2, 3}, {0, 1, 3}, {1, 2, 3}, {0, 1, 2}, {0, 2, 3} in turn, so
that the acting composite alternates (first, second, first, second, first, second). The run starts in the class where every leaf is
transparent, at the solver's first satisfying state. After each write one random point of the outer host is flipped and M1 runs to the
floor (random.Random(104)).

## Results

| Leaves | Writes | Reached | Held | Outer address held |
| --- | --- | --- | --- | --- |
| Fano | 6 | 6 | 5 | 5 |
| thin (2,1,2) | 6 | 6 | 6 | 6 |

Every write was reached, and every outer address held whenever its address did. With Fano leaves the fifth write missed: the search
stops when every named leaf holds a unit, and it stopped with leaf 0 holding a unit without acting, so the acting set was {1, 2} and no
composite acted; the disturbance changed nothing. That is the search's stopping rule reading units rather than roles, which the atom rule
allows (a unit may sit in a leaf that does not act, `ADDRESS-STEER-20261110-001`'s R-c), not a failed return.

Against the pre-registration: the expectation (at least 95% held) was not met with Fano leaves (5 of 6, 83%), and the failure criterion
(a write not reached, or under 80% held) was not met either. With thin leaves the expectation held. The stress test
(`research/NEST-ATOMS-20261110-001/stress_test.py`, outer host K_3) held 12 of 12. Six writes per leaf type is a small sample.
