# Interpretation of PC-COUNT-20261110-001B-E001

Exploratory and exact, pre-registered (frozen contract committed in e84692cb2 before any degree of the count was computed). The run took
50 seconds.

| Formula | System | K_2 (16 points) | K_3 (36 points) | K_4 (64 points) |
| --- | --- | --- | --- | --- |
| The count NAE(K_k) | polynomial calculus | 3 | 4 | at least 5 (degree 5 passes the memory cap) |
| The count NAE(K_k) | Nullstellensatz | 6 | at least 6 (degree 6 passes the cap) | at least 5 (degree 5 passes the cap) |
| Control NAE and FACE | both | 3 | 3 | 3 |

- **H1 holds:** the count's polynomial-calculus degree is 4 on K_3, above K_2's 3.
- **H2 holds:** the polynomial calculus gains over the Nullstellensatz, 3 against 6 on K_2 and 4 against at least 6 on K_3.
- **H3 holds:** the control has degree 3 in both systems on all three spheres.
- **H4 holds as computed:** K_4 is not refuted at degree 4, so its degree is at least 5, above K_3's 4. The contract's text reads H4 only
  when both degrees are decided; run.py, frozen with it, compares K_4's lower bound with K_3's exact degree, which decides the comparison
  without deciding K_4's exact degree. Both readings are given here: K_4's exact degree is undecided, and it is above K_3's.

Reading, as the decision rule fixed it: growth at every decided step, one degree per step so far (3, 4, at least 5, with k = 2, 3, 4),
read as the small-size face of ticket A's asymptotic bound, which itself is below 1 at these sizes. The two smallest spheres have
low-degree refutations (degree 3 and 4); these are refutations at fixed small sizes, not an algorithm, and ticket A shows no family of
bounded degree exists. The pattern k + 1 would mean degree of order √n, the resolution width (`SPHERE-WIDTH-20261107-001`), which is
the upper bound; it is three points and not a claim.
