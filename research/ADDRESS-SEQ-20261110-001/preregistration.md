# Pre-registration: several addresses in sequence

Epic `ADDRESS-SEQ-20261110-001` (backlog B88, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## Ticket A: writing in sequence

Spaces: three Fano atoms (at l0 and line distances 2 and 3) on every line orbit of K_3 and K_4, and on the first three line orbits of K_5
(one size past K_4); four atoms (at l0 and distances 2, 3 and 4) on every orbit of K_3. From the floor state the sight-4 learner leaves,
write a sequence of addresses in turn with the frozen targeted search of `ADDRESS-20261110-001` (same moves, bound, target rule and cap),
each write starting from where the last ended, and after each write disturb the state by one random upper-level flip and let the learner
M1 of `ADDRESS-STEER-20261110-001` return to the floor. Sequences: for three atoms the pairs (0,1), (1,2), (0,2), (0,1), (1,2), (0,2); for
four the triples (0,1,2), (1,2,3), (0,2,3), (0,1,3), then the same again. Seed random.Random(88).

At each step record: whether the write reached its target; the acting atoms right after the write; the acting atoms after the
disturbance and return.

- **Held:** the acting atoms after the disturbance equal the address just written.
- **Interference (frozen):** a successful write whose acting atoms after the disturbance are the previous address (a trace of the old one)
  or any set other than the new address.
- **Expected:** every write succeeds and at least 95% of disturbed addresses are held, with no difference between first and later writes.
- **Failure (frozen): the memory does not hold more than one address** if later writes fail where first writes succeeded on the same
  space, or if the held share of later writes falls below 80%.

## Ticket B: the 17 runs of `ADDRESS-STEER-20261110-001` that did not settle back

Rerun that epic's ticket C exactly (same seed and order) and, for each run at two or three flips that did not end with the written acting
atoms, record where it ended: the acting atoms, where the units sit, W, and whether the exact rule of that epic's ticket A holds there (each
acting atom holds a unit). Expected: the runs at the floor that lost an acting atom obey the rule (learning steps during the return wound
through that atom's handle, so it turned transparent and its unit became free); the runs not at the floor stopped above it with no move
lowering W.
