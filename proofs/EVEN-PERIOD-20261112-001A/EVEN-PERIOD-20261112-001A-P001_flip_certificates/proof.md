# Flip certificates for odd-period words

Status: Proved (lemmas 1 to 4 by hand) with an exact census, refereed. Ticket A of
`research/EVEN-PERIOD-20261112-001/preregistration.md`, frozen with the code in commit `8f4b693b8` before the census ran. `check.py
--part control|census|summary|referee` reproduces each part.

Words, as in the pre-registration and the guide's glossary: harmony (A70), period, orbit; a **word** u of period p is the repeating
state x_i = u[i mod p]; its **residue pairs** G(u) are the pairs (α, β) mod p on which u is never constant; a word c of period p is
**compatible** with u when it is never constant on a triple of G(u); a residue r of c is **flippable** when no triple of G(u) through
r has its two other values equal and different from c[r]; a **certificate** for u is a compatible word with a flippable residue. The
bases have one distinction per whole number and knots of kinds (0, a, b), 0 < a < b, under the plain not-all-equal law.

## 1. The lemmas (by hand)

**Lemma 1 (what the mirror alone gives).** Flipping every value maps allowed states to allowed states, and never maps an orbit of
odd period onto itself. So the mirror pairs an odd orbit with a second one; it does not forbid odd periods. (Proof in the
pre-registration.)

**Lemma 2 (residues).** A word u of period p satisfies a kind (0, a, b) exactly when (a mod p, b mod p) is in G(u). For odd p, no
good pair has α = 0, β = 0 or α = β: such a pair would need u[r + β] ≠ u[r] for every r, hence u of period 2β, hence of period
dividing β, a contradiction. So every triple of G(u) has three distinct residues.

**Lemma 3 (a certificate forbids every harmony).** If u has a certificate c with flippable residue r, every base that allows u
allows c and c with the value at one position of residue r flipped, a state that does not repeat; so no harmony allows u, at any span
and with any number of knot kinds. (Proof in the pre-registration.)

**Lemma 4 (and a word without one would be a harmony).** Suggested by the advisor model (Fable 5.2, consulted on 2026-11-12) and
proved here. Let p be odd and let B_u be the base of all kinds (0, a, b) with b < p that u satisfies. If u has no certificate, every
allowed state of B_u repeats with period p, so B_u is a harmony allowing a state of odd period p.

*Proof.* Let x be allowed by B_u with x_i ≠ x_{i+p} for some i, and let c and c' be the words of period p read from x on the windows
[i, i + p − 1] and [i + 1, i + p]. They differ exactly at residue i. Each window holds every residue once, so every triple of G(u)
is met by three positions of the window, which sorted as j₁ < j₂ < j₃ give a kind (0, j₂ − j₁, j₃ − j₁) of span less than p; its
residue triple is a translate of the triple's, so u satisfies it (lemma 2) and the kind is in B_u, and x is not constant there. So c
and c' are compatible. A knot through one position of residue i in the repetition of c has its other two values at residues x and
y, so it is constant after flipping that position only if c[x] = c[y] ≠ c[i], that is, only if c' is constant on the triple
(i, x, y) of G(u), which it is not. So residue i is flippable and c is a certificate, against the assumption. Hence every state of
B_u has period p (it is the periodic repetition of its window), there are finitely many, and u is one of them. ∎

So, for odd p: **no harmony has a state of period p exactly when every word of period p has a certificate**, and a counterexample,
if one exists, appears already among the bases of span less than p.

## 2. The census (exact, frozen)

Every Lyndon word of odd length 3 to 29 (one per orbit; an orbit and its mirror both appear), 25,328,938 words; for each, its
residue pairs, whether it has a flippable residue, and if not a certificate found by SAT:

| Period | Words with no kind | Their own certificate | Certified by another word | Without a certificate |
| --- | --- | --- | --- | --- |
| 3 to 15 | 2,036 | 1,044 | 0 | 0 |
| 17 | 6,374 | 1,328 | 8 | 0 |
| 19 | 24,120 | 3,456 | 18 | 0 |
| 21 | 79,906 | 19,922 | 30 | 0 |
| 23 | 338,168 | 26,488 | 66 | 0 |
| 25 | 1,276,392 | 65,744 | 40 | 0 |
| 27 | 4,440,214 | 530,578 | 216 | 0 |
| 29 | 18,003,540 | 509,068 | 182 | 0 |

- **E1 holds:** every word of odd period 21 to 29 has a certificate. **E2 holds:** so does every one of period 3 to 19.
- **Control holds:** none of the 11 orbit words of the harmonies found in `HARMONY-ARITH-20261112-001` (periods 2 to 12) has a
  certificate, as lemma 3 requires of any word a harmony allows.
- The census took 38 minutes, nearly all of it at period 29, inside its cap.

**Theorem (computer-assisted).** No not-all-equal base along one shift, at any span and with any number of knot kinds, split or not,
whose allowed states all repeat has a state of odd period at most 29.

## 3. The proof for every odd period: not found

- **What would settle it.** By lemma 4 the statement for all odd p is equivalent to: every word of odd period has a certificate.
- **What is known.** A word with one pattern of good pairs (six ordered pairs, one triple shape) is always its own certificate: each
  residue would have to be the minority value of its triples exactly once, which forces as many 0s as 1s, impossible for odd p (the
  advisor's count, checked here). For more patterns the count no longer decides. In the census the words that need another word's certificate have exactly two patterns up to period 21; from period 23 on they
  also have three to eight (period 29: 56 with two, 28 with three, 42 with four, 28 with five, 28 with eight), and every one has
  a certificate.
- **The advisor's view** (to be checked, not a result): counterexamples are plausible near periods 21 to 35, among words with three or
  more patterns whose compatible words are only their own orbit and its mirror; a search over pattern sets rather than words would
  reach them. The census found none up to 29, though such words appear there and are certified by other words.

## 4. The referee

- **Fresh code (`even_referee.py`), passed.** R1: periods 3 to 19 recomputed by brute force, with identical counts in every class
  and no word without a certificate. R2: all 534 certificates listed at periods 21 to 29 checked directly. R3: 300 random words at
  each period 21 to 29 recomputed with its own SAT encoding (minisat22), all certified; none of them needed another word, so that
  path rests on R2. R4: lemma 3 checked on 1,188 actual bases (every word of odd period up to 11, every span 3 to 14), by testing every
  knot near the flip: no violation. It is independent code by the same author.
- **An independent session (a fresh model session that did not see this work's reasoning; `independent_referee/report.md`),
  passed.** It found lemmas 1 to 4 correct, including the worry about positions of the flipped residue class (by lemma 2 a knot never
  holds two positions of one residue), and lemma 4's window argument, which it showed needs p odd (for 01 the base of span below 3 is
  not a harmony). With its own code it recomputed the full census to period 21 with identical counts, verified all 560 listed
  certificates, sampled 300 words (and 200 words that satisfy a kind) at each of periods 23 to 29, confirmed the control words have no
  certificate, and checked one period-17 certificate with its flip against all 35 kinds of span up to 40 on a window of 601
  positions. Its caveat: at periods 23 to 29 the full census rests on this run; it checked samples and every listed certificate.

## What this establishes

- Proved: the mirror alone pairs odd orbits but does not forbid them; a certificate forbids every harmony allowing a word, and a word
  without one would itself give a harmony of span less than its period.
- Computer-assisted, refereed: no not-all-equal harmony has a state of odd period at most 29.
- Not established: odd periods above 29; the antiperiodicity of unsplit harmonies (`HARMONY-ARITH-20261112-001`'s H2), which
  certificates do not address, since they cover split bases too.
