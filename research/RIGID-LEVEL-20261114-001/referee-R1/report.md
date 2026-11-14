# Referee report RIGID-LEVEL-R1 (light check, fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**

**What holds.**
- **The central claim.** "Rigidity at every level is not proved" is correct.
- **The two statements asked about.** Both recompute: the constraint is not affine, and the pair graph is not bipartite at levels 5
  to 12.

**What overreaches.**
- **The closure.** The range at level 5 is 3 to 6.
- **"Certified for n ≤ 14".** It overstates the levels: #2 is not rigid at levels 3 to 5.
- **"Eight to forty-fold".** The proof-size step ratio is misreported.
- **The obstruction.** Points 3 and 4 do not support "a global obstruction" or "practically exhausted".

**How the work was split.**
- **The referee.** Fresh code, `check_pairs.py`, reusing the pattern builder of LEVEL-RETURN-R1's referee (not the study's
  `certify`). The study's `closure.py` was run once only to compare outputs.
- **Codex.** Not used, as the coordinator asked.
- **Advisor.** The advisor model was not consulted.

## 1. Not affine

**Correct. Not a block.**
- **The derivation.** Parity satisfies every kept knot, so each knot has two same-parity addresses (the pair) and one apex. With
  g = f ⊕ parity, NAE on f becomes "not (g_pair = t, t and g_apex = ¬t)".
- **Why it is not affine.** The allowed set has 6 of the 8 triples, which is not a power of two, so it is not an affine subspace.
  For example, 000 ⊕ 011 ⊕ 010 = 001 is forbidden.

## 2. The pair graph and one-sided closure

The referee rebuilt #2's knots and recomputed both from them (`check_pairs.py`, `check_pairs.json`).

| Level | Knots | Parity-violated (removed) | Pair graph bipartite | Closure of one pair, min to max |
| --- | --- | --- | --- | --- |
| 5 | 82 | 0 | no | **3 to 6** |
| 6 | 176 | 2 | no | 3 to 5 |
| 7 | 366 | 0 | no | 3 to 5 |
| 8 | 748 | 2 | no | 3 to 5 |
| 9 | 1,514 | 0 | no | 3 to 5 |
| 10 | 3,048 | 2 | no | 3 to 5 |
| 11 | 6,118 | 0 | no | 3 to 5 |
| 12 | 12,260 | 2 | no | 3 to 5 |

**The comparison.**
- **The knot counts** after removal (82, 174, 366, ...) equal the study's.
- **The two removed knots** at each even level are exactly the two that parity violates, as LEVEL-RETURN-R1 proved.
- **Level 5.** The study's own `closure.py` also prints "max 6" there, so the note's "3 to 5 addresses at levels 5 to 12" is a
  transcription slip. **Not a block:** say 3 to 6 at level 5, 3 to 5 at levels 6 to 12.

## 3. Wording

1. **"Rigidity stays certified for n ≤ 14".** **Narrowing.**
   - **The levels.** #2 is not rigid at levels 3, 4 and 5: LEVEL-RETURN-R1 found other states at 3 and 5, and 4 is the non-rigid
     control.
   - **The evidence.** The odd-level and level-14 certificates are run-time records with no archived proofs (LEVEL-RETURN-R1's
     Block on the archive). The even levels 6 to 12 were freshly recertified there.
   - **The fix.** Write "certified at even levels 6 to 14 (reduced pattern) and odd levels 7 to 13 (full pattern), with 14 and the
     odd levels resting on run-time certificates", as the note's own Question section has it.
2. **Point 4, "the proof eight to forty-fold".** The note's own step counts give these ratios per two levels:
   - **Even levels** (6 to 14): 8.4, 20.3, **3.6**, 39.0.
   - **Odd levels** (7 to 13): 11.0, **2.5**, 53.8.

   Two steps grow more slowly than the pattern's 4 times.
   - **The fresh proofs.** LEVEL-RETURN-R1's fresh, independently checked DRUP proofs (53, 654, 6,487 and 47,750 steps at 6 to 12)
     grow 12.3, 9.9 and 7.4 times. The ratio is falling.
   - **What follows.** Proof size outgrows the pattern overall, but not per step, and these are non-minimal proofs from one solver
     in each case.

   **Narrowing:** give the ratios and drop "eight to forty-fold".
3. **Points 3 and 4 as evidence.** The probing used depth at most 2 on 36 + 6 + 3 sampled addresses: depth 1 fails at 6, 8 and 10,
   and depth 2 refutes 3 of 6 at level 6 and 0 of 3 at level 8. That shows no bound on the depth needed. Three phrases go beyond it:
   - "Propagation needs growing depth";
   - "points to a global obstruction rather than a local one";
   - "local derivations ... practically exhausted".

   The note's Lag cutoffs ("Nothing here proves that no uniform proof exists") are right. **Narrowing:** say "depth 1 does not
   suffice at 6 to 10; the small depth-2 sample refutes fewer at level 8; no growth of the needed depth is shown", and call the
   global obstruction a conjecture.
4. **Point 5** (no projection along the two-to-one map; 2^k coupled functions) is stated as checked by hand for one step, which is
   what it is. **Not a block.**

## Fixes for the thread

1. **Point 2.** The closure range is 3 to 6 at level 5. **Not a block.**
2. **"Certified for n ≤ 14".** State the exact levels and the evidence class. **Narrowing.**
3. **Point 4.** Give the step ratios, with the two below 4 times, and the fresh proofs' falling ratio. **Narrowing.**
4. **The obstruction.** Soften "needs growing depth", "global obstruction" and "practically exhausted" to what the samples show.
   **Narrowing.**

## Files

`check_pairs.py` and `check_pairs.json`, the referee's fresh recomputation.
