# Advisor question 1 (NAE-GROWTH-20261119-001, before the freeze)

Analysis please; I will check it. Background: the cheapest parity growth (FRESH-COUNT's complete-round joining policy and fewest
counts). Every ring result we have is for even-parity junctions. The coordinator asks whether loops keep branching under another
law. I took not-all-equal (NAE): every junction is read as NAE on its distinctions.

**The definition.** The joining policy (candidates through common neighbours, groups, offshoots, demand by lookahead) reads only
incidence. The fewest count is max(d, 3 − p, 1), except 0 when the new junction's constraint is implied by the old ones.
- Under parity, implied means it takes every loose bit of a connected presentation (GF(2)).
- Under NAE, implied means no state allowed by the old junctions makes its old bits all equal (two SAT calls).
- With one or more fresh bits, an NAE junction never removes an old state. So the policy's "keep every old state" clause holds,
  and the law enters only through "implied".

**Pilot.** Per-round counts are identical under NAE and parity on:
- two touching knots (3,3) and (4,4), a chain of three, and the bare ring of five (5 a round);
- the ring 4,4,4,4,5 (c(t) = c(t−5) + c(t−6)) and the ring of five five-place knots (5 F(t+2), golden ratio), to 14 rounds;
- the bare two-ring join (2.6075, algebraic), to 11 rounds.

The lone knot differs. Parity closes in its 2^a pattern; NAE gives [1, 3, 3, 1, 1, 2, 3, 4, ...]: the top is not implied, so it
relays (one fresh bit, then two endless chains). No NAE-implied junction appeared anywhere.

**My reading.**
- The growth is law-blind except at implied junctions.
- Parity's implied junctions are exactly the tops of finite pieces that hold all the loose bits, which are closures.
- NAE implies less, because a fresh bit can always break all-equal, so no NAE junction is ever implied in these starts.
- So under NAE, rings, ratios and the cluster picture are unchanged, closures become relays, and the census's "closes" class
  becomes growth.

## Planned freeze

All 26,441 census arrangements under both laws, 12 rounds or 3,000 junctions.
- **P1.** Every arrangement that does not close under parity has identical counts under NAE.
- **P2.** Every arrangement that closes under parity grows under NAE, equal to parity up to its last round.
- **P3.** No NAE-implied junction occurs anywhere.

## Questions

1. Is "law-blind except at implied junctions" right as a statement about this policy, or does the law enter elsewhere, such as
   whether a junction counts as a knot under K1–K3? NAE on three bits passes K1–K3. Does NAE on many bits?
2. Can an NAE junction ever be implied in this growth? Give a case, or an argument that it cannot: the old bits of a new junction
   come from different parents' loose bits, and loose bits are free in any NAE presentation where each junction has a loose bit.
3. Under NAE, does the closed form of a closing start become exactly parity + y^(T+1)/(1 − y)^2 (one relay at the top)?
4. "Is bond distance still enough to say who joins whom?" The policy reads incidence, which is identical. NAE bond distance differs
   from parity's on rings (NAE-METRIC: NAE rings steps + 1; parity rings below steps + 1 at 3 and 4 knots). Can I say anything
   sharp without computing NAE bond tables, which needs SAT-hard implication? Is a small-presentation brute-force check worth
   freezing?
5. Is a law with a genuinely different cheapest growth nearby (one where implication happens inside a growth, such as
   one-in-three, or a majority law), the better test of "loops keep branching"? Should I add one as a second arm?
