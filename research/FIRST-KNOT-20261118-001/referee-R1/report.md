# Referee report FIRST-KNOT-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Every statement checks, and the post hoc Proposition 4 holds one size past (m = 6) by
independent code. One wording fix: "grows m-dimensionally" counts junctions by round; it is not a bond-ball statement.
- **The proofs check by hand.**
  - Lemma 1 (pieces).
  - Theorem 2 (one count: every start knot must have 0, 1 or c open distinctions).
  - Corollary 2.1 (the presentation decides).
  - Lemma 3 (implied parity with several components).
  - Theorem 3 (the fewest counts: apart, both close; touching, two quadrants, through a relay).
  - Proposition 4 (mutually touching knots).
- **Replayed with the referee's own simulator** (`referee_first.py`, on its FRESH-COUNT-R1 engine), past the study's sizes:
  - **Theorem 2:** all 360 cells agree. Knots of 3..7 places (study 3..6), apart or sharing one or two distinctions, counts 2..9 (study
    2..8). This includes "a three-place and a four-place knot, apart or touching once, grow under no count".
  - **Theorem 3:** every apart pair closes into its two Boolean patterns.
    - Every touching pair grows with exactly the per-round counts stated, for 30 rounds.
    - At every top, GF(2) confirms u = h (the relay).
  - **Corollary 2.1** holds as stated:
    - as one knot, only c = 4;
    - as A, B through a hidden h, only c = 2;
    - as A, A + B, c = 2 with one copy a round late;
    - and A, B with h forgotten give exactly the four-place knot's states.
- **Proposition 4 (post hoc, weighed with care).** It was found after Q4 failed and is labelled as such. Its proof is a reduction to
  FRESH-COUNT's crossed start, which the referee checked: after round 1 the candidate pattern is the crossed start's at its round a.
  - The reduction is sound by the referee's reading.
  - It holds for m = 3, 4, 5 and **6** (one size past). The growth equals the crossed start's, shifted, round for round, with exactly
    m offshoots each round.
  - The per-round junction counts are exactly polynomials of degree m − 1: their (m − 1)-th differences are constant 1.
  - The controls close as stated: three knots of five places, and four of four.
- **The fix (Narrowing, wording).** "Two-dimensionally", "(a − 1)-dimensionally" and "m-dimensionally" are statements about how many
  junctions are made by round t.
  - Bond balls are proved only for ℕ^a with a ≥ 3 (FRESH-COUNT's T5).
  - The ℕ² pieces (a = 2) and the crossed orders have no bond-ball theorem.

## What holds

| Claim | Referee (fresh code) | Study |
| --- | --- | --- |
| Theorem 2: one count runs exactly when every start knot has 0, 1 or c open distinctions; stall round from the table | 360 of 360 cells (sizes 3..7, shared 0, 1, 2, counts 2..9) | 226 cells in scope |
| A three-place and a four-place first knot, apart or touching once: no count | every count 2..9 stalls | counts 2..8 |
| Theorem 3, apart: both close as Boolean patterns | 15 of 15 pairs (sizes 3..7) | 10 pairs |
| Theorem 3, touching once: per-round counts t + 1, or C(ℓ, t), 1, t − ℓ, per piece | 15 of 15 pairs, 30 rounds | 10 pairs, 30 rounds |
| The relay: each top's one fresh distinction equals h | every top (GF(2): u + h in the span) | every relay |
| Corollary 2.1: one knot c = 4; A, B c = 2; A, A + B c = 2 | as stated; projection equal | as stated |
| Proposition 4: m mutually touching knots of m + 1 places, the fewest counts | m = 3, 4, 5, **6**: the crossed start shifted, m offshoots a round, per-round counts of degree exactly m − 1 | m = 3, 4, 5 (14 rounds) |
| Controls: three knots of five places; four of four | both close | both close |

## 1. The proofs

- **Lemma 1** checks.
  - In round 1 the start knots have no common neighbour, so every open distinction becomes an offshoot of its own knot.
  - Afterwards, a live junction's neighbours are its parents, all in its own piece, so two pieces never meet as candidates.
  - Touching knots are neighbours of each other, not neighbours in common, so they fit the hypothesis.
- **Theorem 2** checks.
  - ℓ ≥ 3 is FRESH-COUNT's Theorem 2.
  - For ℓ = 2, the pair needs 2s ≤ 1 + s, so only c = 2 runs.
  - For ℓ = 1, the lone offshoot becomes a seed on c distinctions, one round late, so every count fits.
  - The touching pair of a-place knots therefore runs only at c = a − 1.
- **Lemma 3 and Theorem 3** check.
  - Apart, each top takes every loose distinction of its component, so its parity is implied and it closes.
  - Touching once, a top with ℓ ≥ 3 is not implied, because the other piece still holds loose distinctions. It gets one fresh
    distinction u.
  - The piece's equations sum to the top's old distinctions plus h, so u = h.
  - u then makes a lone offshoot of demand 0 that is not implied. It gets 2, giving two chains, a quadrant.
  - The a = b case, where both tops form in one round, is handled.
- **Corollary 2.1** checks: A + B = x₁ + x₂ + x₃ + x₄ shares x₁, x₂ with A, so the open counts are 1 and 2.
- **Proposition 4** checks.
  - In round 1 every pair of knots has the other m − 2 as common neighbours. Every set missing a knot R_k has R_k in common. So the
    only group is all m knots, the junction T.
  - Each knot's other open distinction becomes an offshoot c_i. Its only neighbour is R_i, whose live children are T and c_i, so its
    demand is 1. The rule gives it 2: a chain.
  - T has demand m and gets m.
  - From round 2 on, candidates are read only through round-1 junctions and later ones. That pattern, T joined to R_i and c_i joined
    to R_i, is the crossed start's at its round a = m, with its top and the offshoots above its level-(a − 1) junctions. The counts
    given agree too: m for T, 2 for each c_i.
  - No later junction has implied parity, since the growth never ends, so the two growths coincide.

## 2. Proposition 4, weighed with care (the coordinator's ask)

- **Provenance.** It was written after the read-out, to explain Q4's failure (the ring of three four-place knots grew three-dimensionally).
  - The note labels it "proved after the read-out" in the answer, the table and the proof.
  - Q4 is scored as failed, on both clauses: the vacuous closure clause and the growth bound.
  - That is the right treatment.
- **Is it sound?** By the referee's reading, yes. The reduction is local: the candidate structure from round 2 on depends only on the
  round-1 junctions, their parents and the counts given, and these match the crossed start's. Every number the proof needs was
  recomputed independently, not taken from the study.
- **One size past** (`referee_first_mutual.json`):
  - for m = 3, 4, 5 and 6, the growth equals the crossed start's from round 2, round for round (15, 15, 12 and 10 rounds compared);
  - there are exactly m offshoots every round;
  - the per-round counts are polynomials of degree exactly m − 1, so the junctions up to round t grow as t^m.
  - The study's claim "like t^m" is exact in this sense.
- **What it shows.** The fewest counts pick no number, and the number of chains is the start's arrangement. The study draws exactly
  this conclusion. **Not a block.**

## 3. Wording

- **"m-dimensionally", "two-dimensionally", "(a − 1)-dimensionally."** In every case the evidence is the junction count by round:
  quadrants, products, crossed orders.
  - FRESH-COUNT's T5 proves bond balls of order r^a only for ℕ^a with a ≥ 3.
  - So "two touching knots grow two-dimensionally" (two copies of ℕ²) and "m mutually touching knots grow m-dimensionally" (crossed
    orders) are pattern and round-count statements.
  - Neither has a bond-ball theorem: T5's long-bond step needs three coordinates.
  - The note's limitations do not say so. **Narrowing (wording).**
- **"The rule never sees a knot's size, only how many of its distinctions are open (proved)."** This is true by the definition of the
  policy, which reads only loose distinctions and neighbours, for every start.
  - Lemma 1 proves the stronger piece decomposition only when no two start knots have a common neighbour.
  - Chains, rings and stars are computed, as the note says.
  - **Not a block.**
- **"The three is the foundation's definition."** This is correctly labelled a reading (A105, resting on A2). **Not a block.**

## Fixes for the thread (listed for the owner, not folded in)

1. **The dimension words.** Say that "grows two-, (a − 1)- or m-dimensionally" counts junctions by round. Bond balls are proved only
   for ℕ^a with a ≥ 3 (FRESH-COUNT's T5), not for ℕ² or the crossed orders. **Narrowing (wording).**
2. **Proposition 4.** Add the referee's check: m = 3 to 6, the crossed start's counts round for round, per-round counts of degree
   exactly m − 1. **Not a block.**
3. **Theorem 2 and 3's census** extends to sizes 3..7 and counts 2..9 with no exception. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof and `startlib.py`, and checked Lemma 1, Theorem 2, Corollary 2.1, Lemma 3,
    Theorem 3 and Proposition 4 by hand;
  - wrote `referee_first.py`: starts of several junctions on its own FRESH-COUNT-R1 engine, the pairs census, the presentations, the
    mutual starts to m = 6, the crossed start, and a GF(2) relay check.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_first.py`.**
- **`referee_first_pairs.json`, `_present.json` and `_mutual.json`.**

Reproduce, from `research/FIRST-KNOT-20261118-001/referee-R1/` (under a minute):

```sh
for p in pairs present mutual; do ../../../.venv/bin/python -B referee_first.py $p > referee_first_$p.json; done
```
