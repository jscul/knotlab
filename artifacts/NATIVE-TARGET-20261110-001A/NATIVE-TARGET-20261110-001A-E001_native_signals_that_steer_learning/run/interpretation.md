# Interpretation of NATIVE-TARGET-20261110-001A-E001

Exploratory, against the frozen contract and the pre-registration (`research/NATIVE-TARGET-20261110-001/preregistration.md`).

- **Counting.** The transfer matrix agreed with enumeration on all 540 test configurations (20 on each of the 27 thin tori of at most
  20 points).
- **F1 (sight) held, but for one clause on one torus.** R1, R2 and R3 resolved every run on all 59 tori and beat R0's mean on every torus
  of at least 10 points. The mean fell with r everywhere except torus(5, 4, 2), 10 points, where R2 took 3.18 steps and R3 3.20. At 40
  points (torus(40, 1, 1)): R1 21.4, R2 15.5, R3 12.9 steps, against R0 64.4 and the outside-distance R7 7.5.
- **F2 (entropic attraction) held on its bar; the diagnostic held as a trend, not strictly.** R4 and R5 resolved all 50 runs on each of
  the 21 tori and beat R0 on every one of at least 10 points: at 40 points R4 19.3 and R5 17.9 steps against R0's 64.4. Along R0's walks
  the mean of log N falls from distance 1 to the largest distance on every torus (at 40 points from 5.99 to 1.01), and at the largest
  distance N is 2 (log 2 = 0.693), only x and its complement. It is not monotone at every step: on six tori of 22 to 38 points the mean
  at distance 1 is below that at distance 2. So the pre-registered diagnostic, read strictly ("falls with distance on every torus"),
  fails; the attraction is real at range and uneven at contact.
- **F3 (control) held.** R6, the fewest states, resolved none of its 50 runs on each Fano torus. On the thin tori it resolved every run,
  slower than R0 on 10 of the 16 of at least 10 points (97.3 against 65.3 at 38 points) and faster on 6 (46.6 against 64.4 at 40).
- **Replay.** Every resolved run of every rule replayed as learning steps at the dissonance (A26) ending resolved with a winding change.
- **Stress test** (`research/NATIVE-TARGET-20261110-001/stress_test.py`, one size past, 42 to 46 points): R4 and R5 resolved all 50
  runs on each and beat R0 (R4 18.8 to 20.4, R5 16.4 to 19.2, R0 67.8 to 73.3).

Answer to B61: yes. Two native signals steer learning to the over-agreeing face without the outside distance: the learner's own sight
of its moves (local), and the number of states that share the state's dissonance (global, A27 weighed by the state). Neither matches the
outside distance (7.5 steps at 40 points against 12.9 and 17.9), and both beat random moves about three to five times over.
