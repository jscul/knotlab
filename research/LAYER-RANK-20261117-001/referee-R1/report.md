# Referee report LAYER-RANK-R1 (light check; fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - The identity's proof is correct.
  - Every frozen number recomputes from the referee's own recursion, written from the gate rules: M1 to M7, S1, and S2's
    failure.
  - The post hoc largest-of-1,024 values reproduce.
- **What needs fixing** is how the √d law is worded and labelled:
  - The phase count is the largest standing, which follows √d. The (2/3)√d is the mean standing.
  - "The d^0.41 was the logarithmic correction" names the wrong correction.
  - The continuum law, the unlayered √(ln n) and the post hoc match go unlabelled where they are summarized.
- **Known mathematics.** That untangling phases equal least Strahler numbers is a known theorem, and it should be named.

## What holds

- **The identity (proved; Not a block).**
  - **The setting.** At infinite width the two inputs are independent. From layer 1 on, every true gate has rank at least 1
    (an OR of inputs gives max(0, 1) = 1, and an AND of two rank-0 inputs gives 1). So for every L ≥ 1:
    - an OR gate has rank ≤ r with chance 1 − (1 − Q)² = 2Q − Q²;
    - an AND gate has rank ≤ r exactly when both inputs are true with rank ≤ r and not both exactly r, with chance Q² − q².
  - **The average** is Q − q²/2, and the true fraction stays ½.
  - **The note states it for L ≥ 2.** It holds from L ≥ 1.
  - **The referee's check.** The referee's recursion (`referee_layer.py`) is written from the gate rules: OR = least
    max(rank, 1), AND = max, or i + 1 on a tie. The identity holds against it at every one of 10^5 layers, to 1.3·10⁻¹⁵.
- **The fixed-rank limits.** L·F_L(r) → β_r with β_r − β_(r−1) = 2√β_r is a consistent asymptotic solution of the exact recursion
  (put Q_L(r) ≈ β_r/(2L)), not a proof. The numbers agree: 3.9995 and 10.4707 at 10^5.
- **The frozen numbers recompute exactly** (`referee_layer.json`):
  - M1: 0.513;
  - M2: 0.619 and 0.658;
  - M3: 0.504;
  - M4: 3.9995 and 10.4707;
  - M5: 0.875;
  - M6: 1.020;
  - M7: 0.666.
- **The simulations, the referee's own.**
  - **S1** holds. At w = 2^17, 12 runs deviate from the recursion by a median of −1.5% to +0.3% at d = 256 to 1,024, with single
    runs within ±6%. That spread tracks the drifting true fraction, and no median of three exceeds 5% (`referee_s1_spread.py`).
  - **S2** reproduces, failure included. At w = 1,024, the median largest rank is 41 at d = 1,024 and 146.5 at d = 4,096 (the
    study's 40 and 142.5). All-false shares are 0.22 and 0.44; the study's 0.12 and 0.60 are inside the same frozen ranges.
- **The post hoc match reproduces.** The recursion's largest of 1,024 at d = 8 … 256 is 4, 5, 6, 9, 12, 16, against
  SEQUENTIAL-WALL's measured 4, 5, 7, 9, 11, 17.

## 1. The phase count is the largest standing, about √d, not (2/3)√d (Narrowing)

- **What a phase count is.** A circuit's number of untangling phases is its largest standing. That is what SEQUENTIAL-WALL
  measured, and what the post hoc comparison uses.
- **The recursion's largest of 1,024 follows the front √d:**

  | d | Largest of 1,024 | √d | (2/3)√d (the mean is about this) |
  | --- | ---: | ---: | ---: |
  | 256 | 16 | 16 | 10.7 |
  | 10^4 | 98 | 100 | 66.7 (the mean is 64.5) |
  | 10^5 | 313 | 316 | 211 (the mean is 208.1) |

  So the claims below describe the mean standing of a true gate, not the phases. The pre-registration itself gives "largest/mean
  3/2".
- **Where the claim appears:**
  - the note's answer ("need about (2/3)√d untangling phases");
  - the final report ("about (2/3)√d untangling stages");
  - the intuition entry ("gives about (2/3)√d phases at depth d");
  - the goals checkpoint ("phases grow like (2/3)√d");
  - the G3 row ("giving (2/3)√d").
- **A fair wording.** "Phases (the largest standing) grow like √d, the front of a triangular standing profile whose mean is
  (2/3)√d."

## 2. "The d^0.41 was this law's logarithmic correction": a pre-asymptotic offset of the largest standing (Narrowing, wording)

- **What is supported.** The measured statistic (largest of 1,024, d = 8 … 256) has exponent 0.40 under the recursion, so the old
  d^0.41 is a pre-asymptotic exponent of this law.
- **But it is not the −¼ ln d correction.**
  - That correction belongs to the mean. Over the same range, the mean's local exponent rises from 0.39 to 0.52 (8→16 to 128→256).
  - The largest standing sits above the √d front by 1.17, 1.0, 0.34, 1.0, 0.69 and 0 at d = 8 … 256. That fading constant offset
    is what holds its exponent at 0.40.
  - Asymptotically the −¼ ln d term raises the mean's local exponent above ½ (M1, 0.513).
- **A fair wording.** "The d^0.41 is a pre-asymptotic exponent: the largest standing is about √d plus a constant that fades by d =
  256." It is also a post hoc reading (below).

## 3. Labels: what is heuristic, untested or post hoc (Narrowing)

- **The continuum law is a heuristic.** The (2/3)√d, ¼ ln d and β_r laws are labelled correctly in the pre-registration
  ("Derived (heuristic; advisor)") and in the note's Limitations. Elsewhere they are not:
  - The note's answer: "Its solution, confirmed by the frozen numerics".
  - The intuition entry: "whose continuum limit gives about (2/3)√d phases".
  - The goals checkpoint: "proved identity and computed ... phases grow like (2/3)√d".
  - The objects row: "mean ~ (2/3)sqrt(L) − ln(L)/4" under "proved+computed".
  - The final report: "The cause is one exact identity, which I've proved ... The resulting law (a Burgers equation) matched to
    depth 100,000".

  Say "a heuristic continuum limit, confirmed numerically to depth 10^5" beside each.
- **"Unlayered circuits obey the same equation with depth about ln n, hence √(ln n)"** is the advisor's heuristic, and this study
  ran no unlayered circuit. Yet it appears in the note's answer, in the intuition entry (inside "computed, frozen"), in the final
  report, and as "both now explained" in prior work. Label it heuristic and untested here.
- **"Within one of every earlier measurement" is post hoc.** It is unlabelled in the note's answer and in the intuition entry.

## 4. Known mathematics to name (Not a block)

- **Phases equal least Strahler numbers: a known theorem.**
  - Newton's method for fixed-point equations over ω-continuous semirings: the k-th Newton approximant collects exactly the
    derivation trees of dimension, that is Strahler number, at most k. See Esparza, Kiefer and Luttenberger, "Newtonian program
    analysis", J. ACM 57(6), 2010, and the survey by Esparza, Luttenberger and Schlund, "A brief history of Strahler numbers",
    2014.
  - Untangling phases are such Newton iterates. So "rank = least Strahler number of a derivation = phase" (here, in
    SEQUENTIAL-WALL, and the gate of SPACE-ORDER) is their theorem.
  - The least Strahler number over derivations is the index of a grammar's derivations. Deciding it is P-complete (Ganardi and
    Lohrey, "On the complexity of computing Strahler numbers", STACS 2026, arXiv 2512.19060).
- **Strahler orders under random merging.** Kovchegov and Zaliapin, "Random self-similar trees: a mathematical theory of Horton
  laws" (Probability Surveys, 2020), derive coalescence equations for Horton–Strahler orders. This is a relative with no
  alternatives (no OR).
- **The equation.** ∂_L F + ¼ (∂_r F)² = 0 is a Hamilton–Jacobi equation, and its derivative u = ∂_r F solves inviscid Burgers, as
  the note says.
- **The recursion itself.** A search found no statement of this recursion (min over alternatives with Strahler joins, two
  independent inputs per layer) or of its √L law. The note's "found no statement" stands; name the two literatures above beside it.

## Fixes for the thread (listed for the owner, not folded in)

1. **"Phases ≈ (2/3)√d."** Replace it with "phases (the largest standing) ≈ √d; mean standing (2/3)√d" (note's answer, final
   report, intuition entry, goals checkpoint and G3 row). **Narrowing.**
2. **"The d^0.41 was the logarithmic correction."** Restate it as "a pre-asymptotic exponent of the largest standing (√d plus a
   fading constant)", labelled post hoc. **Narrowing.**
3. **Labels.** Label the continuum law heuristic and the unlayered √(ln n) heuristic and untested. Label the recursion-versus-
   measurement match post hoc, wherever each is summarized. **Narrowing.**
4. **Known mathematics.** Name Esparza, Kiefer and Luttenberger for phases = Strahler numbers, and Ganardi and Lohrey and the
   Horton-law literature as neighbours. **Not a block.**

## How the work was split

- **The referee:**
  - read the pre-registration, the note, `layer_rank.py` and the published summaries;
  - wrote the recursion from the gate rules and a finite-width simulator;
  - recomputed M1 to M7, S1 (with a 12-run spread) and S2, and the post hoc values;
  - searched the literature.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_layer.py` and `.json`: the recursion, the identity check, the frozen quantities, S1 and S2.
- `referee_s1_spread.py` and `.json`: the spread of S1.
