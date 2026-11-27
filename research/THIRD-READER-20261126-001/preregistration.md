# Preregistration: the middle as a third reader (tripartite.py)

Frozen before `tripartite.py 2` is run on the families. Written 26 November 2026, after the advisor's attack
([question](advisor_question.md), [answer](advisor_answer.md)), which found every prediction I drafted entailed (by the
separability argument, by the identity g = the readers' value correlation, and by a lemma that settles the real-reads
search) and one wrong as worded. Its by-hand values are frozen here as the expected output; the run is a check of them
and of the code, not a test that could have gone the other way, except where marked.

## Seen before freezing

`real_paradox.py` (run before this freeze): with positive amplitudes and real reads, no three-reader game of certainty
on one or two copies of the shared triple, with two settings per reader (0 of 1 and 0 of 46,656) or three on two copies
(0 of 592,704), every certainty's sign equal to the advisor's lemma's; the positive control with signed amplitudes gives
1 of 1; with quarter-turn reads one copy gives Mermin's game. A check that the named change of the game is allowed.

## Expected (the advisor's values, frozen)

| Rows ('places' readers, rounds 0 to 2) | E(A), E(B), E(M) | e(AB), e(AM), e(BM) | g |
|---|---|---|---|
| Pairs of rings, three-ring families (the loose family's other two pairs included) | 2, 2, 3 | 0, 1, 1 | 1 |
| The pair of the two-ring family | 1, 1, 1 | 0, 0, 0 | 1 |
| The loose chain's pair | 2, 2, 4 | 0, 2, 2 | 0 |
| Rings 0 and 2 together, ring 1 | 3, 2, 3 | 0, 1, 0 | 2 |
| The same on the loose family | 3, 2, 4 | 0, 2, 1 | 1 |

The three routes for g and the fourth (certainties not generated on two readers; 0 for laws) agree. No birth has
parents in two regions through round 2.

The game at round 0: win 1 against 3/4 on the three-ring families with dead chains (detour and direct links; **the
direct-link row could fail**); exactly 3/4 on the loose-chain family (**could fail**); probabilities nonnegative; no
reader or pair of readers sees another's setting; a list in which the middle hears both ring settings gives the same
table (the advisor's contact list).

## Scaffolds named

The middle as one reader holding every distinction outside the two rings' regions; its two settings; the quarter-turn
read (a fourth supplied piece, with the coherent counting state and combined questions); the built families at round 0
for the game; the 'places' reader regions.
