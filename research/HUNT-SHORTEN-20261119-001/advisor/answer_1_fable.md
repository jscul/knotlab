Answered from your description without re-opening the EXTEND-ROUND records, so check the definitional assumptions flagged below.

**(1) H1 is a theorem, given two conditions.**
- **No old entry changes.** A one-parent junction n has a single bond to the rest, so no shortest route passes through it. By K2, forgetting n's fresh distinctions leaves the parent's loose distinction unconstrained, so the allowed states on the old variables are unchanged.
- **New entries copy the parent's row.** d(n,x) = d(p,x) + c, where c depends only on f and the parent's local type. Since phi matches type (star onto star, loose onto loose), set phi(n) = n and the extension holds.
- **Conditions.** This needs c to be a function of the matched type alone, and table entries to depend only on routes and allowed states.
- **Prediction to add.** The same argument covers |S| = 1, f = 1.

**(2) A Part 1 failure is not a Claim B counterexample.**
- **Why not.** Claim B assumes phi keeps R and applies the whole round. A single attachment is not a round, and static pairs never keep R.
- **Suggested wording.** "Table isometry alone does not survive attaching one pair-junction; Claim B is untested by this."
- **What it does show.** Any proof of B must use R; step-by-step induction on attachments from isometry alone is dead.
- **Diagnostic for the failing pair.** If the table were a path metric on live junctions, the new entries would be d'(x,y) = min(d(x,y), d(x,a)+2+d(b,y), d(x,b)+2+d(a,y)). That is a function of the old table and S, so phi would extend automatically. The failure therefore means the table is not closed under this formula. Compute the formula's prediction on each side and record which entries deviate, since that locates what the table omits. My guess is the cost of crossing a junction between particular distinctions, or routes through non-live junctions.

**(3) Getting a real Claim B test beyond 7 junctions.**
1. **Self-pairs.** Take one structure and a nontrivial table self-isometry that keeps R. There is no pair enumeration, the hypothesis is non-vacuous, and it scales well past 7.
2. **Grown pairs.** Iterate the round from GROW-SMALL's 64 reached pairs and test the extension at each round. These keep R by construction.
3. **Targeted search.** Take the failing local pattern (two matched junctions bridged with one fresh distinction) and use a constraint solver to look for R-keeping pairs that contain it after a full round.

**Bets.**

| Claim | Probability |
|---|---|
| H1 holds | 95% |
| H1 holds at f = 1 as well | 85% |
| H2 holds | 99% (already seen) |
| H3 holds within 7 junctions | 90%, mostly because Part 2 is vacuous |
| Part 2 has fewer than 1% non-vacuous cases | 75% |
| Claim B survives self-pairs and grown pairs | 65% |
| The failing entries all deviate from the min formula | 80% |

If a counterexample to B exists, I expect it where two loose distinctions on matched junctions are bridged in one round while R reads only the stars.
