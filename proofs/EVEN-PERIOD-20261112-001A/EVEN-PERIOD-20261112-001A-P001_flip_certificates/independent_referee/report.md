# Independent referee (a fresh session, 2026-11-12)

Model: claude-opus-5-5. Brief: brief.md. Code written by the referee from scratch: ref.py, run.py, checks.py, extra.py; log: census.log.

The proof holds up, and so does the computation for p ≤ 21. Above 21 I only checked samples and the author's listed certificates, so the full p ≤ 29 claim is confirmed only in part. All my code is in the referee directory: `ref.py`, `run.py`, `checks.py`, `extra.py` and `census.log`. I wrote it from scratch, used Minisat through python-sat, and imported nothing from the author.

## Lemmas

- **L1: correct.** NAE treats 0 and 1 the same way, so flipping every value keeps a state allowed. If the flip of u equalled u shifted by s, then shifting by 2s would give u back. So p divides 2s, and with p odd, p divides s. That would make u equal to its own flip, which is impossible.
- **L2: correct.** The first part restates the definitions. For odd p, a pair (0, β) would force u[r] ≠ u[r+β] for every r. Then u repeats every 2β, so p divides β, and the triple is constant. The cases β = 0 and α = β go the same way. One consequence matters for L3: every triple of a kind the base uses covers three different residues.
- **L3: correct**, including the residue-class worry. Only one integer position n (with n ≡ r0) is flipped. Other positions in the same residue class keep their c-value. By L2, no kind's triple holds two positions of the same residue, so n appears in a triple at most once and the other two entries are unflipped. A triple through n becomes constant exactly when its other two values are equal and differ from c[r0], which flippability forbids. Triples that miss n are allowed because c is compatible. The new state y does not repeat: if it had period q, then y at n + kpq would equal c[r0] ≠ y_n.
- **L4: correct, and it needs p odd.** The window argument works:
  - **Compatibility:** take any p consecutive positions of an allowed state x and read them cyclically as c. Every set of three distinct residues can be placed inside that window with span less than p. Whether u satisfies a kind depends only on the triple's pattern up to shifting, so that placement is a kind of B_u, and x is not constant on it. With p odd, G(u) has no degenerate pairs to worry about, so c is compatible.
  - **Flippability:** suppose x_n ≠ x_{n+p}. The windows starting at n and n+1 give c, and c with the value at residue n mod p flipped. Both are compatible, so that residue is flippable in c. This gives u a certificate, which contradicts the hypothesis. So every allowed state has period p, and u itself is one of them.
  - **Even p fails:** for u = 01 there are no kinds of span below 2, and with span below 3 the base B_u is not a harmony (check 5 below).

  So "every word of odd period p has a certificate" is equivalent to "no harmony has a state of period p": one direction is L3, the other is L4.

## Computations

1. **Listed certificates: 560 of 560 pass, 0 failures.** For each row I checked that u is a Lyndon word of minimal period p, that c is compatible, and that the listed residue is flippable. I also confirmed that u is not its own certificate. The author's total of 25,328,938 words matches the sum of their tallies.
2. **Full census, odd p from 3 to 21: every word has a certificate.** My tallies match the author's exactly:

   | p | words | satisfies no kind | own certificate | certificate from another word |
   |---|---|---|---|---|
   | 17 | 7,710 | 6,374 | 1,328 | 8 |
   | 19 | 27,594 | 24,120 | 3,456 | 18 |
   | 21 | 99,858 | 79,906 | 19,922 | 30 |

   The smaller p also match, and no word lacks a certificate.
3. **Random samples at p = 23, 25, 27, 29:** 300 words each, all with a certificate. Most of these words satisfy no kind and are certified trivially. So I also drew 200 words per p that satisfy at least one kind. All were their own certificate. The rare "another word" case (about 0.03%) never came up in sampling. At those p it rests on the 560 listed certificates I verified.
4. **Controls:** I used the literal definition with all pairs, including degenerate ones. 01, 0011, 000111, 00001111 and 00101101 each have **no certificate**, as expected.
5. **Direct window check at p = 17:** u = 00000011101010111, c = 11111000111110000, r0 = 0. u satisfies 35 kinds of span ≤ 40. The repeating c with one value flipped at position 0 breaks none of them on the window [−300, 300], and it differs from repeating c at only that position.
6. **0011 (the even-period direction of L4):** with kinds of span below 4, B_u has 3 kinds and is a harmony, every allowed state having period 4. That holds by hand too: every 4-window must hold exactly two 0s and two 1s, which forces x_{i+4} = x_i. It is also a harmony with span below 5, 6 and 8. 000111 and 00101101 behave the same way. For 01, span below 3 gives no harmony and span below 4 does, which is why L4 needs p odd.

## Verdict

L1 to L4 are correct, and I found no flaws. The reduction to certificates is sound, every listed certificate checks out, and my independent census for odd p ≤ 21 agrees exactly. The controls behave as they should. For 23 ≤ p ≤ 29 I did not recompute everything: the samples and the 560 listed certificates support the claim, but the full census at those p rests on the author's run.
