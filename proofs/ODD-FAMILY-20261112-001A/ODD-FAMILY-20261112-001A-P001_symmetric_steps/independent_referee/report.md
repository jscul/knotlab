# Independent referee of the period-73 and period-193 harmonies (a fresh session, 2026-11-12)

A fresh model session with no access to this work's reasoning. Brief: brief.md. Code written by the referee: referee_ref.py, referee_c.py, referee_c2.py (copied from its scratch directory, renamed).

Claims A and B hold on every point. Claim C holds for the H ∪ 2H sets at 89 and 97, but as literally worded it fails for one case at 67 and 71: t = ±3 gives a vacuous harmony. I wrote my own code (`ref.py`, `c.py`, `c2.py`, in the referee directory) and used CaDiCaL through python-sat.

**(1) Kinds.** I listed every pair 0<a<b<n where {0,a,b} mod n is a translate of {0,s,2s}.
- **A:** 12 kinds: (1,2), (1,72), (2,4), (2,71), (19,38), (19,46), (19,54), (27,46), (27,54), (35,54), (69,71), (71,72). S closed under negation is {1, 2, 19, 27, 46, 54, 71, 72}.
- **B:** 18 kinds, as claimed.

**(2) Counts and classes.** I enumerated all compatible words with SAT plus blocking clauses.
- **A:** 730 words, 5 classes under rotation and flipping every value.
- **B:** 386 words, 1 class.
- Every word is non-constant. Since 73 and 193 are prime, each word's minimal period is n.

**(3) Distance.** No two compatible words are at Hamming distance 1. Over all pairs, the least distance is 8 for A and 19 for B.

**(4) Window lemma.** The proof is sound and I found no gap:
- n is odd, so each triple {r, r+s, r+2s} has three distinct residues.
- In any n consecutive positions, those residues sit at p<q<r with r−p<n. Then {0, q−p, r−p} is also a translate of {0,s,2s}, so (q−p, r−p) is a kind and its constraint applies there. So both windows are compatible words, and they differ only at residue j.
- If x_j = x_{j+n} for all j, then x is n-periodic.
- The converse also holds: every compatible word extends to an allowed n-periodic assignment, so harmony here is not vacuous.

**(5) Direct SAT check.** I imposed every constraint that fits inside a window of length 4n, plus x_{2n} ≠ x_{3n}. This is UNSAT for both A and B. The stronger version, a window of length n+1 with x_0 ≠ x_n, is also UNSAT for both.

**(6) gcd of offsets.** It is 1 for both A and B.

**(7) Claim C.**
- **89 and 97:** With H the fourth roots of 1 (H = {1,34,55,88} at 89 and {1,22,75,96} at 97), there is a compatible word whose flip at one position is again compatible. This does imply "not a harmony": joining w on the left to w′ on the right gives an allowed assignment that is not periodic, because any period would have to agree with w's n-period on the left tail. The 4n-window SAT check agrees: an assignment with x_j ≠ x_{j+n} exists.
- **67 and 71:** For every t except t = ±3, compatible words exist and a one-position flip exists, so none of those sets is a harmony.
- **The exception:** For t = ±3, S = {±1, ±2, ±3} has no compatible words at all, and even a single window of length n is UNSAT. So no allowed assignment exists, and K_S is vacuously a harmony under the stated definition. The claim needs to say "non-vacuous harmony" or exclude t = ±3.

**Overall:** A and B are confirmed, including the window lemma and the direct finite-window check. C is confirmed except for the vacuous t = ±3 case at 67 and 71, which needs rewording.
