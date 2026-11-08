# One-sided additive paths compose at recurring lags at every ring size

Status: Proved by hand. The finite claims are checked in `check.py`, and the theorem's predictions against exact row sequences at
every ring size from 4 to 40.

Ticket `RECUR-PROOF-20261108-001A`, 2026-11-08.

## Standard statement

- **The setting.** A path of four rings A, B, C and D, each of s ≥ 4 cells, as in `NATIVE-PATH-20261108-001A`. Contact c1 is cell 0
  of A and of B, c2 is cell k1 of B and cell 0 of C, and c3 is cell k2 of C and cell 0 of D, with k1, k2 ∈ {2, s − 2}: the
  middle rings' contacts are two cells apart. Every non-contact cell runs its ring's rule, 60 (x_j' = x_(j−1) + x_j) or 102
  (x_j' = x_j + x_(j+1)), over GF(2).
- **Partners.** On a rule-60 ring the right neighbour of a contact reads the contact and itself; on a rule-102 ring the left
  neighbour does. Call that cell the contact's partner on the ring.
- **The laws.** Each contact is self-blind and adds up the cells it reads:
  - c1 reads its partner on A and its partner on B;
  - c2 reads both of its neighbours on B and its partner on C;
  - c3 reads both of its neighbours on C and its partner on D.

  These are the 64 families of `RECUR-PATH-20261108-001A` that compose at recurring lags with every contact persistent at every
  size of its two-apart schedule: 16 choices of rule, one per ring, times the 4 choices of k1 and k2.
- **Readings.** A contact binds a ring at lag T when its value at lag T depends on that ring's first-row cells; for a linear path,
  when its row of M^T meets them (`NATIVE-PATH-20261108-001A`, Theorem 2).

**Theorem.** For every s ≥ 4 and each of the 64 families, mirror every rule-102 ring (cell j ↦ −j), so that every ring runs rule
60, and let k1', k2' be the mirrored positions and m = k1' + k2' − 2, so m is 2, s − 2 or 2s − 6. Then:
1. **Persistence.** Every contact binds both of its rings at every lag T ≥ 1.
2. **Composition.** The last contact c3 binds ring D at every lag, and ring A exactly at the lags T ≥ 3 at which the binomial
   coefficient C(T − 3, m) is odd.
3. **So,** by Lucas' theorem, c3 binds both end rings exactly when every binary digit of m is a digit of T − 3: a set of lags
   periodic with period 2^b, where b is the bit length of m, and of density 2^(−w), where w is the number of ones in m. Each family
   composes at recurring lags with every contact persistent (A37) at every ring size, and at every lag from the light cone on
   (A34) at none.

## Nearest known result

- **The ingredients.** Rule 60's powers are Pascal's triangle mod 2, and Lucas' theorem says when a binomial coefficient is odd
  (Lucas 1878; for additive automata, Martin, Odlyzko and Wolfram 1984).
- **Classification.** Known-with-delta. The delta is the path: contacts that form closed loops with their partners, and the far
  contact's composing lags as one binomial coefficient.

## Lemma 1 (a contact and its two partners)

Let a contact c read two partners n and n', each updated as n ← n + c, and other cells u_1, …, u_r. Then n + n' is constant in
time, and for every T ≥ 1

  c(T) = n(0) + n'(0) + u_1(T − 1) + … + u_r(T − 1).

*Proof.* (n + n')(T + 1) = n(T) + n'(T) + 2c(T) = (n + n')(T) over GF(2), and c(T) = n(T − 1) + n'(T − 1) + Σ u_i(T − 1). ∎

So if none of the u_i depends on n(0) or n'(0), c depends on both n(0) and n'(0) at every lag T ≥ 1.

## Lemma 2 (mirrors)

Mirroring one ring, cell j ↦ −j mod s, keeps its contact at cell 0 in place, sends the other contact's position k to s − k, turns
rule 60 into rule 102 and back, and swaps each contact's left and right reads on that ring. It is a relabelling of cells, so every
reading of the path is unchanged.

*Proof.* Rule 60 reads the left neighbour and rule 102 the right one, and the mirror swaps left and right. ∎

The 64 families are the mirror images of the four families with rule 60 on every ring (k1, k2 ∈ {2, s − 2}), one per choice of
which rings to mirror (check 1). So it suffices to prove the theorem with rule 60 on every ring; then k1' = k1 and k2' = k2.

## Lemma 3 (Pascal steps)

Write a quantity's coefficient in a cell at lag T as C(T − d, e), with C(n, e) = 0 for n < e. Then:
- a cell updated as x ← x + y, with x(0) not containing the quantity, carries C(T − d, e + 1) when y carries C(T − d, e);
- a contact that reads y carries C(T − d − 1, e) in its own update when y carries C(T − d, e), and nothing else of the quantity.

*Proof.* In the first case x(T) = Σ_(t<T) y(t) = Σ_(n ≤ T − d − 1) C(n, e) = C(T − d, e + 1), the hockey-stick identity, which holds
over the integers and so mod 2. The second is the one-step delay. ∎

## Proof of the theorem (rule 60 on every ring)

- **Which cells matter.** On ring A, c1 reads only A_1, and A_j for j ≥ 2 reads A_(j−1) and A_j, so A_2, …, A_(s−1) feed nobody
  outside A. The same holds on D beyond D_1. So c3 depends on ring A only through A_1(0).
- **c1.** Its reads A_1 and B_1 are its partners and it reads nothing else, so by Lemma 1 c1(T) = A_1(0) + B_1(0) for T ≥ 1. It
  binds A and B at every lag.
- **c2.** It reads B_(k1+1), its partner on B, and C_1, its partner on C, and B_(k1−1). The cells B_1, …, B_(k1−1) form a chain:
  B_1 is c1's partner and B_j reads B_(j−1) and B_j. The chain depends only on c1, A_1(0) and the chain's own cells, never on
  B_(k1+1)(0) or C_1(0). By Lemma 1, c2(T) = B_(k1+1)(0) + C_1(0) + B_(k1−1)(T − 1), so c2 binds B and C at every lag.
- **c3.** In the same way c3(T) = C_(k2+1)(0) + D_1(0) + C_(k2−1)(T − 1). The chain C_1, …, C_(k2−1) starts at c2's partner C_1 and
  never depends on C_(k2+1)(0) or D_1(0). So c3 binds C and D at every lag, and part 1 is proved.
- **A_1(0) along the path.** By Lemmas 1 and 3, its coefficient is:
  - in c1(T): 1 = C(T − 1, 0), for T ≥ 1;
  - in B_j(T): C(T − 1, j), along the chain from c1's partner B_1;
  - in c2(T): C(T − 2, k1 − 1), read from B_(k1−1) with one lag's delay;
  - in C_j(T): C(T − 2, k1 + j − 1), from c2's partner C_1 along the chain;
  - in c3(T): C(T − 3, k1 + k2 − 2), read from C_(k2−1).

  Since c3 depends on A only through A_1(0), it binds A at lag T exactly when C(T − 3, m) is odd, with m = k1 + k2 − 2. That is
  part 2.
- **Part 3.** By Lucas' theorem C(n, m) is odd exactly when the binary digits of m are among those of n. For n = T − 3 that depends
  only on n mod 2^b, so the composing lags are periodic with period 2^b and density 2^(−w). As m ≥ 2, they are infinitely many and
  miss infinitely many lags past the light cone. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream statuses | pass |
| 1 | The 64 families are the mirror images of the four rule-60 families, with the laws stated, and are exactly `RECUR-PATH-20261108-001A-E002`'s 64 distinct two-apart families with every contact persistent at every size | pass |
| 2 | Lemma 1 on 2,000 random three-cell loops with random inputs | pass |
| 3 | The theorem's predictions (persistence of every contact, D at every lag, A exactly when C(T − 3, m) is odd) at every lag through the eventual cycle, for all 64 families at every ring size from 4 to 40 | pass |
| 4 | The composing density 2^(−w) against the measured share of the last contact's cycle, all 64 families, sizes 4 to 40 | pass |
| 5 | Full state spaces at ring sizes 4 and 5 (13 and 17 bits), all 64 families | pass |

## Nonclaims

- **These 64 families only.** The rule-90 families of `RECUR-PATH-20261108-001A` are not covered (see the epic's decision note).
- **Two-time knots only** (A30); the readings are A34's and A37's.
