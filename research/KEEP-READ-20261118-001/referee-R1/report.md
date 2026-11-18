# Referee report KEEP-READ-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The tier-0 and closure results replicate.** The referee used its own SEEDK runs (other seeds), its own pictures and exact
  isomorphism classes across all runs.
  - **The extensions.** 37,302 extensions after the switch, 3,636 of them keeping two orders. SEED refuses 146 of those.
  - **Tier 0.** The clean-witness fraction is 0.813 for keeping two orders and 0.847 for SEED's acceptance, against the study's
    0.790 and 0.825. There are 17 exact classes, as the study found by hash.
  - **The closure tier** adds 0.0003.
  - **"Two middles" never raises.** That holds at n ≤ 24 (634 extensions, recall 18%) and on larger bases, to n = 40: 2,179
    extensions, none raising.
- **The proofs hold.** R1 needs one wording fix. R2 is right as a bound on rules.
- **The owner's flags.**
  - **The picture definitions:** match the note's words.
  - **R2's measure:** sound for showing an obstruction. It is vacuous as positive evidence wherever most pictures occur once.
  - **Tier 1:** uninformative as positive evidence, for two reasons, coverage and uniqueness (§2). Its three look-alike pairs are a
    valid obstruction on these bases, but not about locality.
- **"No local reading" overreaches.** What is shown is the move's own knots (proved) and the betweenness among its distinctions
  (computed). One step out could not be tested on bases of 24. **Narrowing (wording).**

## What holds

- **R1.** The corner knot set {B(x, r, y), B(c, x, r), B(c, y, r)} has the same three knots and middles whether the splits t₁
  (c from x) and t₂ (c from y) cross or nest.
  - When they nest along a chain at a full grid, r makes them cross and λ rises by one (PICK-TWO S4).
  - When they cross and the corner's cell is empty, r fills it and the orders are kept.
  - **The wording fix.** "Both occur on full grids" is loose. On a full grid every cell is present, so a corner across crossing
    splits lands on an existing cell and is a copy. The keeping case needs an empty cell, as after a subdivision. Both cases occur
    on the bases met, as the confirmed pairs show.
- **R2.**
  - A rule reading a tier treats each picture class alike. If it never accepts a raising extension, it accepts only classes with
    no raising move.
  - So the fraction of keeping extensions with a knot set in such a class bounds the rule's recall, and "accept every clean class"
    attains it.
  - The proof is right. Acceptance goes by extension, through any of its knot sets, as the advisor corrected.
- **The picture definitions** (`keeplib.picture`, `picture_closure`) match the note:
  - **The marks.** The new distinction, the move's old distinctions (marked "start"), the move's knots, and each distinction's role
    in each knot.
  - **At radius r**, every old knot reached by r rounds of distinction → knots holding it → their distinctions.
  - **The closure picture** adds every betweenness the states imply among the move's old distinctions, with its middle.
  - **Coverage** is the picture's old distinctions over n, as stated.
- **The referee's replication** (`referee_keep_tier0.json`, `referee_keep_middles.json`):

  | Reading, SEEDK from 105 bracketings to n = 24 | Referee | Study |
  | --- | --- | --- |
  | Extensions after the switch; keeping; SEED refuses keeping | 37,302; 3,636; 146 | 36,229; 3,457; 144 |
  | Tier 0: classes, clean-witness (keep, SEED) | 17 exact; 0.813, 0.847 | 17 hashed; 0.790, 0.825 |
  | Closure: classes, clean-witness (keep, SEED) | 374 exact; 0.813, 0.847 | 381 hashed; 0.791, 0.825 |
  | Classes holding both outcomes, tier 0; closure | 5; 37 | 310 and 392 confirmed pairs within runs |
  | Two or more middle knots: extensions, raising, recall of SEED | 634, 0, 18.2% | 585 accepted, 0 raising, 17.7% |
  | Two or more middle knots to n = 40 (181,624 extensions) | 2,179, 0 raising; every raising extension has at most one middle knot | — |

  - The differences are the run seeds; the study used a different draw of moves.
  - The study's tier-0 hash classes are exact (17 = 17).

## 1. The headline "no local reading" (the owner's question; Narrowing)

- **What is shown.**
  - **Tier 0** is obstructed in general: R1 proves it, and both computations put the best rule near 0.8.
  - **The closure tier** is obstructed on the bases met: the betweenness among the move's distinctions adds nothing.
- **What is not shown.** At one step out, the bases of 24 distinctions give balls covering 88% of the base. So no reading at
  radius ≥ 1 is shown to be local or not local. The note's limitations say so, and its next direction 2 is the test.
- **Fair wording.** "No reading of a move's own knots, or of the betweenness among its distinctions, is SEED's second phase (proved
  at the knots, computed at the closure). One step out could not be tested on bases of 24." Also keep "the deciding fact is a
  crossing, which is global" as an interpretation, not a result.
- **The positive sign is stronger than the note says.** "The new distinction the middle of two or more of its knots" accepted no
  raising extension on bases up to n = 40 either. That supports the selected direction 1 (a rule built on it).

## 2. Is tier 1 informative? (the owner's flag)

- **As positive evidence, no.** It fails for two reasons.
  - **Coverage.** The radius-one ball holds 88% of the base on average, so the reading is nearly global, as the note says.
  - **Uniqueness, which the note does not say.** A picture met only once is clean by definition: no raising move shares it. In the
    study's read-out, tier 1 has 587,854 classes for 764,989 moves, and 482,120 of the classes are met once.
    - Only 1,098 of the 3,457 keeping extensions have any knot set in a repeated class.
    - So about 68% of keeping extensions are "clean" only because their picture is unique.
    - The headline fractions (0.997 for keeping, 1.0 for SEED's acceptance) mostly measure how sparse the sample is.
    - The same holds at tier 2 (760,189 classes, 4,256 repeated).
- **As an obstruction, yes, on these bases.** The three confirmed look-alike pairs at tier 1 show that even a near-global knot
  picture leaves a few outcomes undecided. With the knots outside the ball they would be decided, since all the knots determine the
  base. So they say little about locality.
- **What R2 needs for positive claims.** A held-out measure: classes learnt on some runs, scored on others. Report the share of
  test extensions whose class was seen at all, besides the clean-witness fraction among those. The coverage control catches balls
  that are the whole base; it does not catch pictures that are merely unique.

## 3. Smaller points (Not a block)

- **The 2 × 2 table** replicates: SEED refuses about 4% of the keeping extensions (146 of 3,636). It refuses them because they
  give a split crossings it did not copy.
- **P2, P4 and P5's misses** are as the note explains, and are reported honestly.
- **"A fill completing a square's corner and a fill twisting three distinctions in a row use the same three knots"** is R1, and is
  right with the empty-cell wording.

## Fixes for the thread (listed for the owner, not folded in)

1. **The headline.** "No reading of a move's own knots, or of the betweenness among its distinctions, is SEED's second phase. One
   step out could not be tested on bases of 24." **Narrowing (wording).**
2. **Tier 1's fractions.** Say that 68% of keeping extensions are clean by uniqueness (no repeated picture), besides the 88%
   coverage. Do not read 0.997 or 1.0 as evidence of a near-local rule. **Not a block.**
3. **R2.** Add a held-out version of the clean-witness fraction for any positive use. **Not a block.**
4. **R1.** "Both occur on full grids" should read "raising along a chain at a full grid; keeping at an empty cell, as after a
   subdivision". **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs R1 and R2, `keeplib.py` and `readout.py`, and the read-out;
  - checked R1 and R2 by hand;
  - wrote `referee_keep.py`: its own SEEDK recording after the switch, tier-0 and closure pictures, exact classes across runs, and
    the two-middles sign to n = 40. It builds on its MEET-ORDERS-R1, KNOT-CAP-R1 and KNOT-SWITCH-R1 code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_keep.py`.**
- **`referee_keep_tier0.json` and `referee_keep_middles.json`.**

Reproduce, from `research/KEEP-READ-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_keep.py tier0 > referee_keep_tier0.json
../../../.venv/bin/python -B referee_keep.py middles > referee_keep_middles.json
```
