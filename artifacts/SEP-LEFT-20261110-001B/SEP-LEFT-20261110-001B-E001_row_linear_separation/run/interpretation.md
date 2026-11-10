# Interpretation of SEP-LEFT-20261110-001B-E001

Exploratory and exact, pre-registered (frozen contract committed in f7ea4ba2b before any closure of the instances was computed). The
run took 105 seconds.

## An analysis bug in the frozen run.py, and the reading by the contract

run.py computed each set's horizon as the largest B reached by an unbroken run of fully separated readings starting at B = 1. The
degree-2 sets are read only from B = 2, so that loop stopped at B = 1 and reported horizon 0 for every degree-2 set; its "grows" test
then compared 0 with 0 and its verdict came out "intermediate". The contract defines the horizon as "the largest B read at which the
whole set is separated", and separation can only shrink as B grows, so the contract's definition needs no unbroken run. The table and
verdict below apply the contract's definition to the same readings; result.json keeps run.py's own output unchanged.

## Readings

Horizon: the largest degree B at which the whole set is separated (none: not at any B read). PC degree: the degree at which 1 is
derived.

| Instance | variables | L1 pigeon rows | L1 all rows | L2 pigeon rows | L2 all rows | PC degree |
| --- | --- | --- | --- | --- | --- | --- |
| BPHP_2 | 3 | none | none | none | none | 1 |
| BPHP_4 | 10 | 2 | 2 | none (45 of 51 at B = 2) | none | 3 |
| BPHP_8 | 27 | 4 | 4 | 4 | 4 | 5 |
| LP_2 | 7 | 2 | 2 | 2 | none (15 of 27 at B = 2) | 3 |
| LP_4 | 22 | 3 | 3 | 3 | 3 | 4 |
| LP_8 | 59 | at least 4 | at least 4 | at least 4 | at least 4 | at least 5 (degree 5 passes the memory cap) |

- **H1 holds:** bit PHP's row-linear spaces are fully separated through Braun's range (n = 4: k = 1, B ≤ 2; n = 8: k ≤ 2, B ≤ 4).
- **H2 holds:** LP's row-linear spaces over all rows reach at least as far as bit PHP's: 3 against 2 (k = 1) and 3 against none
  (k = 2) at n = 4, at least 4 against 4 at n = 8.
- **H3 holds** for the pigeon rows alike.
- **Inside Braun's range** at n = 8 nothing row-linear of degree at most 2 is derived, so the verdict is not "none".
- **The horizon grows** from n = 4 to n = 8: from 3 to at least 4 for k = 1 and k = 2.
- **Verdict by the frozen rule: density that grows.** By the rule the next step is a matching-moment theorem for LP's unary form.

## Reading

- At every size read, the binary left-pigeon principle keeps its row-linear spaces, hole rows included, separated at least as far
  as bit PHP does, and its PC degree is at least bit PHP's (3, 4, at least 5 against 1, 3, 5). The hole rows add separated dimension:
  L2 over all rows has 237 monomials at n = 4 and 1,696 at n = 8, against 51 and 352 for the pigeon rows.
- The polynomials that the substitution g(h) := Σ_x [f_x = h]·x sends to constants (Σ_h g_h,j, and Σ_h g_h,l + 1; ticket A) are in
  L1 over all rows, and they are not derived through the horizons read.
- These are degrees 4 and below on instances of at most 59 variables; Braun's criterion needs B = k(D + 1), far above. The readings say
  that bit LeftPigeon keeps pace with bit PHP where both can be computed, not that it has a separated space of useful density.
