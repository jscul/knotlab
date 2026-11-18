# Referee report COUNT-BALLS-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The numbers stand.** The referee recomputed them with its own code:
  - Gołąb's π of the chain grids at l = 1, 2, 3, 4 and 6, to six digits;
  - the closed form's axis rate, which equals Onsager's 2(K* − K), and its diagonal-to-axis ratio 1.003400;
  - the chain grid's reduction, literally on a 3 × 3 grid;
  - the census, class for class: the cheapest growth to twelve distinctions and one-split growth to eight, with the same merges
    and the same failures;
  - the first merge at seven, the star and its translate, and the ladder and the comb.
- **The owner's four flags.**
  - **The citations are right.** Cheng and Wu 1967 is Phys. Rev. 164, 719, the paper on spins off a common row, which is what the
    outline needs. One decimal is not the literature's: "a = 0.6322260804" is the advisor's arithmetic. Its own formula gives
    0.6322260823.
  - **The Gołąb π values hold.** At l ≥ 4 the sixth decimal depends on the polygon used.
  - **The census readings hold exactly**, class for class, through 59,675 classes at eight distinctions. The study's
    determination code computes the colour number exactly, as it must.
  - **"Round" need not be read only in the drawing.** A drawing-free form exists, and the note should use it (§1).
- **Two wording narrowings.**
  - "A periodic law's balls are round" holds for one law, the critical weave. Under the count, split grids still give a polygon.
  - "The ladder and the comb grow identically" holds only from the line's middle starts. The comb's pendant starts grow
    differently, so every start's growth together does tell them apart.

## What holds

- **The weave.**
  - **Amplitude.** The closed form a = 2·3^(−1/4)·E₀², with E₀ = 2^(1/12)·e^(3ζ′(−1)) = 0.6450024485, gives a = 0.632226082255.
    The study's fit, 0.6322259968, is within 1.4e-7 of it.
  - **Short range.** The referee's own not-all-equal transfer on cylinders of width 9 and 12 (WEAVE-MIX-R1's row product) gives
    −1/3 at r = 1. At r = 2 it gives −0.18803 and −0.18985, and at r = 3 it gives 0.34430 and 0.35007. Extrapolated in 1/w², these
    are −0.1922 and 0.3575, against the study's exact row values of −0.19285 and 0.35852. That agrees to about 1e-3 from two widths,
    an independent check of the exact kernel's first terms.
  - **The isotropy at r ≈ 60** rests on the study's exact kernel. It was not recomputed. Its explanation (S7) is classical: the
    height field's stiffness form is isotropic.
- **The chain grids.**
  - **S5 literally.** The referee enumerated the 3 × 3 grid with one not-all-equal knot, on a loose distinction, on every pair.
    Its correlations equal the Ising model's at tanh K = −1/3 to 1.1e-16 (corner to corner 0.076212).
  - **The closed form, from scratch.** The rate in direction x is m(x) = max{q·x : cosh q₁ + cosh q₂ = A}, with
    A = (1 + t²)²/(2t(1 − t²)) and t = 3^(−l).
    - At l = 1, A = 25/12. The axis rate acosh(A − 1) = 0.4054651 = ln(3/2) equals Onsager's 2(K* − K).
    - The diagonal rate per unit length is 0.4068439, and the ratio is 1.0034005.
    - At l = 2, A − 1 = 3.66945 and the axis rate is ln 7.2 = 1.97408, the note's Onsager value.
  - **Gołąb's π** (`referee_golab.json`; half the outline's perimeter measured in m itself). The routine's gates give the circle
    3.1415923, the taxicab diamond 4.0000000 and the hexagon 3.0000000.

    | l | 1 | 2 | 3 | 4 | 6 | 8 | 12 |
    | --- | --- | --- | --- | --- | --- | --- | --- |
    | Referee, 4,000-point polygon | 3.141701 | 3.182439 | 3.297932 | 3.418830 | 3.589379 | 3.687913 | 3.790553 |
    | Referee, 16,000 points | — | — | 3.297933 | 3.418832 | 3.589388 | 3.687923 | 3.790555 |
    | Pre-registration | 3.141701 | 3.182439 | 3.297932 | 3.418830 | 3.589379 | — | — |
    | Proof S6 | 3.141701 | 3.182439 | 3.297933 | 3.418831 | 3.589386 | 3.687920 | 3.790555 |

    Every value agrees. At l ≥ 4 the sixth decimal moves with the polygon, which underestimates as the corners sharpen. The
    pre-registration's values are the coarse polygon's, and the proof's are nearer the limit.
- **The census** (`referee_census.py`, its own engine, canonical form and exact colour number).
  - **The engine.** CUBE-DOUBLING-R1's closure of one to three betweenness knots, with A99 admission.
  - **The classes** are tables of distinctions' sides of the splits, taken up to renaming distinctions, reordering splits and
    swapping sides.

  | Population | n | Classes | (a) groups / merged / k differs / λ differs | (c) groups / merged / k differs / λ differs |
  | --- | --- | --- | --- | --- |
  | Cheapest | 3 to 12 | 1, 1, 2, 3, 1, 1, 2, 8, 8, 14 | never merges | first fails at 6 (1/1); 10: 2/2; 11: 1/1; 12: 1/1 |
  | One split | 4 | 4 | 4 / 0 / 0 / 0 | 3 / 1 / 1 / 0 |
  | One split | 5 | 12 | 12 / 0 / 0 / 0 | 5 / 4 / 2 / 1 |
  | One split | 6 | 101 | 101 / 0 / 0 / 0 | 27 / 24 / 18 / 16 |
  | One split | 7 | 1,656 | 1,651 / 5 / 3 / 3 | 283 / 280 / 249 / 243 |
  | One split | 8 | 59,675 | 58,985 / 672 / 227 / 234 | 4,327 / 4,322 / 4,155 / 4,123 |

  - **Every entry equals the study's results.json.**
  - **The colour count.** The referee's first pass took k from its KNOT-CAP-R1 `measure`, which stops at "3 or more". That pass
    gave 219 instead of 249 at seven, and missed the four-colour classes at ten to twelve. With the exact colour number, every entry
    agrees. The study's own `chromatic` is exact. At n = 7, k and λ are 1,1: 1; 1,2: 7; 2,2: 528; 2,3: 38; 3,3: 980; 4,4: 102.
  - **At n = 8** the classes run up to k = λ = 6 (three classes). A merged pair, for example: cf|abdegh, bcdeg|afh, cdfg|abeh,
    cefg|abdh, cdfh|abeg and bcdegh|af (k = λ = 4) against bcde|afgh, cf|abdegh, cdf|abegh, cefg|abdh, cdfh|abeg and bcdegh|af
    (k = λ = 3), both with 14 states.
- **The first merge at seven.** The referee rebuilt both bases from the splits printed in the note. Each has 14 states, and their
  multisets of sorted count rows are identical. The first has k = λ = 3 and the second k = λ = 2.
- **S1 to S4.**
  - The split-base count, the box's outline numbers (4j and 4j² + 2) and the λ = 2 ruler are right.
  - The parity blank is right.
  - The state side's translation blindness is right. The star with three tips (k = 1) and its translate by one tip's state
    (k = 2) have the same state profile, which the referee recomputed.
  - The rooted repair is right: with the all-equal state marked, |X ∩ Y| gives every two splits' four quadrants.
  - These are one-line arguments, and the note presents them as such.

## 1. Should "round" be read only in the literature's drawing? (the owner's question)

**No. There is a drawing-free form, and the note should lead with it.**
- **Gołąb's π does not depend on the drawing.** It is half the outline's perimeter measured in the outline's own norm. So any
  linear change of the drawing leaves it unchanged. It is π for every ellipse.
  - A periodic law's repeats, its translations, are automorphisms of the law, so the law supplies them.
  - The drawing adds only an angle measure on the plane of repeats.
- **The weave.**
  - Proof S7 already holds the drawing-free statement: the outline is a level set of the height field's stiffness form, a
    quadratic form the law determines. So it is an ellipse in every linear drawing of the repeats, with Gołąb π = π.
  - The law's six-fold symmetry acts on the repeats. An ellipse invariant under a rotation of order three is a circle. So the
    literature's drawing is the one in which the law's own symmetries are rotations, and only there is the ellipse a circle.
  - The study's isotropy test along (4,1), (5,2) and (1,1) is made in that drawing. It is a valid test, because being the
    drawing's circle implies being an ellipse.
- **The chain grids.** Gołąb's π at l = 1 is 3.141701, above π by 1.08e-4. The routine's own error is about 4e-7 on the circle.
  So the outline is not an ellipse in any drawing, and "not round" is a drawing-free statement.
  - "Off round by 1.0034" (the diagonal's rate per unit length against the axis's) is the drawing's measure.
  - The drawing-free measure is π_G − π.
- **The comparison is fair.** Bond distance's hexagon and the count's circle sit in the same drawing, and Gołąb's π compares them
  without it: rational, 3 to 4, against π.
- **Suggested wording.** "On the weave the count's outline is an ellipse in every drawing of the repeats (Gołąb π = π). It is the
  circle of the drawing in which the law's symmetries are rotations. A chain grid's outline is no ellipse in any drawing
  (Gołąb π 3.1417 at l = 1)."

## 2. The headline's scope (Narrowing)

- **"Read by the disagreement count, a periodic law's balls are round"** (the answer, its first bullet, the final report and the
  G1 checkpoint).
  - It holds for one law, the critical weave. Off its critical point a chain grid's outline is smooth and not round.
  - Grown split grids, which are periodic when endless, give the taxicab diamond under the count. That is a polygon with π = 4,
    as the note's own table shows.
  - Fix: "can be round: the critical weave's are".
- **"The polygons belong to bond distance"** (the published Intuitions guide sentence) and "belongs to bond distance, not to
  periodic laws" (the note).
  - Right in that periodicity alone does not force a polygon.
  - Too broad if read as "under the count no periodic law gives a polygon".
  - Fix: "Under bond distance every periodic law gives a polygon (proved). Under the count the outline depends on the law: a
    polygon on split grids (the diamond), smooth and not round on chain grids, round on the critical weave."
- **The published sentence was not false as a statement about the record.** The record's polygon verdict was stated for bond
  distance, so the note's "Corrections: none" stands. The narrowing is to this study's own new wording.

## 3. Ladder and comb (Narrowing, wording)

- **What S2 proves.** From a middle distinction of the line, up to the nearer end, the ladder and the comb have 4 distinctions
  at every count from 4 on. The referee's layers at m = 10 agree: from start 4, the ladder has 3, 4, 4, 4 and the comb 3, 4, 4, 4
  at counts 2 to 8.
- **What it does not say.**
  - The comb's pendant starts see 1, 2, 4, 4, … (one distinction at count 2), and no ladder start does.
  - So the two bases' profiles, every start's growth together (reading (a)), differ. The referee computed that they are unequal.
- **So "a ladder of two orders and a comb of one order grow identically"** (the answer) is a statement about single starts.
  - The fair sentence: "one start's growth does not read the number of orders (ladder against comb, proved). Every start's growth
    together reads it on small bases, and stops reading it at seven distinctions (computed)."
  - The table row "same growth, different orders" should say "from the line's middle starts".

## 4. Smaller points (Not a block)

- **The amplitude's decimal.** The pre-registration, proof S7 and `score.py` give "the literature's 0.6322260804".
  - That number is the advisor's. The fallback model gave 0.6322260813. The closed form both quote gives 0.6322260823, so the slip
    is in their last step.
  - W4 is unaffected: within 1e-3, the fit off by 1.4e-7.
  - Fix: write 0.6322260823 (from the closed form). Cite Stephenson's series for the form: I, J. Math. Phys. 5, 1009 (1964), and
    III, the isotropic antiferromagnet. The referee did not check the paper's printed digits.
- **"The full table determines the base."** True for these bases.
  - Each betweenness knot holds exactly when d(a, b) = d(a, c) + d(c, b) (DISTANCE-ORDER-20261117-001, statement 1, with no need
    for N). The census bases are cut out by their betweenness knots.
  - Cite it at that spot.
  - It is not true for split systems in general. The star of four tips and the three crossing splits of four distinctions both
    give every pair 4, but neither is a betweenness base.
- **The count's scale on the weave is logarithmic.** The ball grows like 3^(4τ). The count orders distinctions by reach, and its
  outline is a level set, but it is not a length there. The note says so ("4 = d/η by the count's scale"). Keep it beside every
  "round".
- **The failed predictions are reported honestly.** C1, C1b, C4b and C4c are pre-asymptotic or a missing sign; G1 and G3 are the
  census failing at seven.
- **Known results (John's folklore rule).** These are classical and rightly cited:
  - roundness at a critical point;
  - the Ising rate in every direction and its Wulff duality;
  - Ornstein–Zernike decay;
  - lattice dimension;
  - Gołąb's π.

  The count is the correlation up to scale, ρ = N(1 − C)/2, so its balls are the correlation's level sets. What the program adds is
  the reading: the information-carrying count gives the outlines that bond distance does not. The note claims no more.

## Fixes for the thread (listed for the owner, not folded in)

1. **The headline.** "A periodic law's balls can be round: the critical weave's are." In the Intuitions guide, replace "The
   polygons belong to bond distance" with the sentence in §2. **Narrowing.**
2. **Ladder and comb.** "One start's growth does not read the orders." Every start's growth together does on small bases. Add
   "from the line's middle starts" in the table. **Narrowing.**
3. **"Round" without the drawing.** Lead with the ellipse (Gołąb π = π, drawing-free) and name the drawing as the one in which
   the law's symmetries are rotations. For chain grids, give π_G − π = 1.1e-4 as the drawing-free measure. **Not a block.**
4. **The amplitude's decimal.** 0.6322260823 from the closed form, not "the literature's 0.6322260804". **Not a block.**
5. **Gołąb π at l ≥ 4.** The sixth decimal depends on the polygon: 3.418832 and 3.589388 at 16,000 points. **Not a block.**
6. **The full table.** Cite DISTANCE-ORDER statement 1 for "the full table determines the base". **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs S1 to S7, and `census.py` and the results;
  - wrote `referee_balls.py`: the weave's transfer, the closed forms, S5 literally, the first merge, Gołąb's π with gates, the
    ladder and comb, and the star and its translate;
  - wrote `referee_census.py`: its own census with its own canonical form and exact colour number.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
- **The literature.** Two web searches confirmed the Cheng–Wu citation and Stephenson's series.

## Files

- **`referee_balls.py`.**
- **`referee_balls.json`:** parts 1 to 4.
- **`referee_golab.json` and `referee_golab_fine.json`:** Gołąb's π.
- **`referee_small.json`:** the ladder, the comb, and the star and its translate.
- **`referee_census.py`.**
- **`referee_census_cheap_12.json` and `referee_census_one-split_8.json`:** the census.

Reproduce, from `research/COUNT-BALLS-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_balls.py > referee_balls.json
../../../.venv/bin/python -B referee_balls.py golab > referee_golab.json
../../../.venv/bin/python -B referee_balls.py small > referee_small.json
../../../.venv/bin/python -B referee_census.py cheap 12 > referee_census_cheap_12.json
../../../.venv/bin/python -B referee_census.py one-split 8 > referee_census_one-split_8.json
```
