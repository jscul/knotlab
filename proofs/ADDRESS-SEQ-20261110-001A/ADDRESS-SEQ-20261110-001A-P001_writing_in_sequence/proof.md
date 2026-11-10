# Writing in sequence

Status: Computed (`check.py`, with `seq_lib.py`), pre-registered in `research/ADDRESS-SEQ-20261110-001/preregistration.md`.

On 14 spaces (three Fano atoms on every line orbit of K_3 and K_4 and on the first three orbits of K_5, one size past K_4; four atoms on
every orbit of K_3), addresses were written in turn by the frozen targeted search, each write starting where the last ended, and after each
write one random upper-level flip was undone by the learner M1. Six writes per three-atom space (every pair twice), eight per four-atom
space (every triple twice): 90 writes.

- Every write reached its target (90 of 90; 14 of 14 first writes, 76 of 76 later ones).
- Every written address was held after its disturbance (90 of 90): the acting atoms after the return were the address just written, never
  the previous one and never another set.

So the memory holds one address at a time, is rewritten cleanly, and keeps no trace of earlier addresses at these sizes. Neither the frozen
interference outcome nor the frozen failure occurred. Computed on small cases (K_3 to K_5, three and four atoms).
