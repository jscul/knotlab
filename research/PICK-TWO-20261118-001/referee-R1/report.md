# Referee report PICK-TWO-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The proofs hold.** S1 to S7 were checked by hand, S2, S4 and S5 line by line.
- **The fill enumeration is correct.** The study's fast `fills()` equals the referee's brute-force closure on all 77 bases tested
  (n = 4 to 17).
- **Every rule's behaviour reproduces.** The referee's own engine (29 batches of runs, to n = 60) gives:
  - **Caps give their number:** CAP(3) gives three, and CAP(4) gives four.
  - **Quadratic prices settle where they should:** 4, 3, 2, 1 orders at w = 0.25, 0.35, 0.5, 1.0.
  - **KEEP and CC conserve:** they keep a line at one order and three-way starts at three.
  - **ODD and SEED hold two:** two orders from every line, with full two-way grids recurring.
  - **λ equals the clique number** at every step of every run.
- **The owner's question: is "the one way to two without naming it is arity" fair?** In part. Arity explains why one fill on a
  line makes exactly one new order (S6). But SEED's switch fixes the number of order-making steps at one, and the line start is
  needed for λ.
  - From uncrossed starts that branch, one fill can already make λ = 3, though the crossing graph stays two-colourable.
  - So the two is the line's one, plus one step that the rule allows, plus arity making that step one order. **Narrowing
    (wording)** (§2).

## What holds

- **S1 (λ and k never decrease).** Restricting the new base to the old distinctions maps each new split onto an old one. It keeps
  every nesting and every non-crossing, and the crossings among restrictions are crossings of the new splits.
- **S2 (CC keeps every relation).** The referee checked the three cases of r against two non-crossing old splits s, s′:
  - when neither is t₁ or t₂, r lies with c;
  - when one is t₁, r lies with x, which agrees with c off t₁;
  - t₁ and t₂ themselves cross.

  So r never lands in an empty intersection. k depends only on the crossings. λ depends only on which side unions are everything,
  which is the relation. Both are kept.
- **S3** is N3 with d chains. The complete d-partite crossing graph fixes the chains. A fill that kept λ ≤ d and made two splits of
  one chain cross would give d + 1 pairwise crossing splits. The layer cells after a subdivision are medians of p, x and y.
- **S4 (the corner pin).**
  - **The pin.** B(a, r, b) pins r = a where a = b. Where a ≠ b, c equals one of them, and the end knot naming the other pins r to
    it. Every state extends uniquely.
  - **At a full grid.** For a, c, b at positions i − 1, i, i + 1 of a chain, r lies below t_i and above t_(i+1), their one empty
    intersection, and with a, b or c for every other pair.
  - **The new count.** C without t_i is still a chain, since r is monotone along it, so λ = d + 1 exactly.
  - **Q_d.** Every pair already crosses, so a fill lies in an occupied cell, and Q_d has none. The referee's closure finds no fill
    on Q₂ or Q₃.
- **S5 (prices).**
  - **The moves.** Fills that keep λ beat everything. At a full non-cube grid none exists (S3), and S4's raise beats any larger
    jump. On a line every fill gives two (S6).
  - **The windows.** For f = wλ² the window that holds D orders is w(2D − 1) < 2 ≤ w(2D + 1). That gives D = 4, 3, 2, 1 for
    w = 0.25, 0.35, 0.5, 1.0, and 0.4 ≤ w < 2/3 for D = 2, as stated.
  - **Scope.** The statements are about full grids and lines. Elsewhere the rule compares whatever raise is cheapest, as the note
    says.
- **S6 (one fill on a line).**
  - **How the crossings form.** The pair t_i ⊂ t_j comes to cross exactly when r ∈ t_i and r ∉ t_j, so every new crossing joins A
    (the cuts holding r) to B (the rest). Each of A and B stays a chain.
  - **The wording to fix.** "Its value changes more than once" should read "changes at least three times along the cuts".
    - Read from the all-zero state to the all-one state, r's membership changes an odd number of times.
    - Exactly once would make r a copy of a line distinction.
- **S7 (SEED stays two-colourable).** The proof treats one gained split at a time. The referee checked that the colouring also
  works when several splits gain at once.
  - Give each gained u the colour of its twin v_u.
  - An edge u–w with w active, or u–u′ with both gained, forces an old edge between two active splits. That edge is properly
    coloured.

### The fill enumeration (the owner's flag; `referee_pick_fills_check.json`)

- **The test set.** Lines of 4 to 8, Q₂, Q₃, and the bases along six of the referee's runs (CAP 3 and 4, SEED twice, ODD, a
  price) to n = 17: 77 bases in all.
- **The result.** On every one, `picklib.fills()` equals the referee's closure: every intersection of one to three knots' allowed
  masks, admitted, with no state added. The referee's own fast enumeration equals both.
- **A spot check.** The counts on lines are C(m, 3), the fills of triples.

### The rules (`referee_pick.py runs`; summary in `referee_pick_runs_summary.json`)

The referee wrote its own rules from the pre-registration's words, on its own fill enumeration, its own λ and an exact k.

| Rule, start | Runs | λ at the end (largest) | Full grids per run | First fill at n | λ = clique number at every step |
| --- | --- | --- | --- | --- | --- |
| CAP(3), lines of 5, 6, 7, 8 (to 60) | 5 each | 3 (3) | at least 6, 5, 4, 3 | 6, 7, 8, 9 | yes |
| CAP(3) first full three-way grid | 5 each | — | at 12; 16, 18; 20, 24, 27; 30, 32, with no subdivision before | — | — |
| CAP(4), line of 5 (to 50); Q₄ (to 24) | 5; 3 | 4 (4) | at least 4; 2 | 6; 18 | yes |
| QPRICE w = 0.25, 0.35, 0.5, 1.0, lines of 5 and 8 (to 40) | 5 each | 4, 3, 2, 1 in every run | at least 5, 5, 7, 0 (line of 5) | 6 (none at 1.0) | yes |
| KEEP, CC: line of 6; Q₃; 3 × 3 × 3 | 3; 3; 2 | 1; 3; 3 | 0; at least 4; at least 1 | never; 10; 29 | yes |
| ODD, lines of 6 and 10 (to 60) | 5 each | 2 (2) | at least 9, 5 | 7, 11 | yes |
| SEED, lines of 5, 6, 8, 10, 12 (to 60) | 5 each | 2 (2) | at least 10, 9, 7, 5, 3 | n0 + 1 | yes |
| SEED, Q₃; 3 × 3 × 3 | 3; 2 | 3; 3 | at least 4; 1 | 10; 29 | yes |

- **Everything agrees with the study.** The first full three-way grid also came at 20 from the line of seven, a value the study's
  sample did not meet (it gave 24 or 27).
- **Not rerun:** the linear prices, FRESH and NEWCROSS. S5 settles the linear price, and FRESH and NEWCROSS are reported weak.
- **FRESH's k ≤ 2 is not S7.** The limitations attribute it to S7, which is about SEED. It follows from S6's argument: from a line
  the splits that crossed nothing stay one chain, so any new crossings among them form a bipartite set.

## 1. What the referee checked beyond the study

- **Uncrossed starts that are not lines** (`referee_pick_trees.json`). The referee took trees with a branching distinction
  (spiders, stars, two branch points), as bases of their halfspaces, and listed every fill by brute force.

  | Start | Fills | k after one fill | λ after one fill |
  | --- | --- | --- | --- |
  | Star of four; spiders 2,1,1; 2,2,1; 2,2,2; star of five; two branch points | 3 to 27 | 2 always | 2 always |
  | Spider with four legs of two (λ = 2 before, k = 1) | 52 | 2 always | 2 (24 fills) or **3** (28 fills) |

  - **One fill keeps the crossing graph two-colourable from every start tested.** That is arity's work.
  - **But λ can go to 3.** A tree's λ already counts its branching: it is ⌈leaves/2⌉ with no crossing at all. So λ = 2 after the
    first fill needs the start to be a line.
  - **"λ equals the clique number"** holds on every base reached from lines and grids. It fails on such trees, where ω = 1 and
    λ = ⌈leaves/2⌉. A99's line should say "on every base reached".

## 2. Is "the one way to two without naming it is arity" fair? (the owner's question; Narrowing, wording)

- **What arity does.** S6 shows that one fill on a line makes exactly two orders, never more. The new distinction's two sides
  split the cuts into the two chains A and B. Without S6, a free fill could jump further. So arity sets the size of a step: one
  order.
- **What the rule does.** SEED's switch is "while nothing crosses". Every fill on a line creates a crossing (S6), so the free phase
  is exactly one fill. After it SEED conserves: new crossings only copy existing ones (S7).
  - So SEED is told no number of orders. But it is told "one order-making step".
  - Its number is the start's λ plus one when the start is uncrossed, and the start's λ otherwise: three from the three-way starts,
    as observed.
  - That is a count handed over, a count of steps rather than of orders. From a line it gives 1 + 1 = 2.
- **What the start does.** From an uncrossed start that branches, the same single step can give λ = 3 (§1). So the two in λ also
  needs the line.
- **A fair sentence.** "SEED names no number of orders. It allows one free step, the one that makes the first crossing, and then
  conserves. Arity makes that step exactly one order, and the line start has one. So the two is the line's one plus one step's one.
  The rule chooses the one step, and arity chooses one order per step."
- **For A101.** "Under challenge" is fair: two arises without the number two being written. It is not a law that picks two from
  any start, which is what the note's own position table says ("a law that picks two from any start: obstruction learned").

## 3. Smaller points (Not a block)

- **ODD** is the cap of two in parity's words, as the note says. On these bases λ = ω and the crossing graphs are perfect, so
  "no odd cycle" means k ≤ 2, which means λ ≤ 2.
- **The note's Answer says "a single fill on a line always makes exactly two orders, because one new distinction has two sides
  (proved)".** That is right. Keep "on a line" wherever it is quoted.
- **Known results, labelled:** lattice dimension (Eppstein), chain covers (Dilworth), and medians. Add that ⌈leaves/2⌉ is a tree's
  lattice dimension (Ovchinnikov), for §1.

## Fixes for the thread (listed for the owner, not folded in)

1. **"The one way to two without naming it is arity."** Replace with §2's sentence: one free step, by the rule; one order per
   step, by arity; one order to start, by the line. **Narrowing (wording).**
2. **The line start.** Say that λ = 2 after the first fill needs it: from branching uncrossed starts one fill can give λ = 3, while
   k stays 2. **Not a block.**
3. **FRESH's k ≤ 2.** It is S6's argument (the uncrossed splits stay a chain), not S7. **Not a block.**
4. **S6's wording.** "Changes at least three times", not "more than once". **Not a block.**
5. **λ = clique number.** It holds on every base reached, not in general (trees). **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs S1 to S7, `picklib.py` and nnlib's helpers;
  - checked the proofs by hand;
  - wrote `referee_pick.py`: two fill enumerations (brute-force closure and a fast one), its own rules, the tree starts and the fill
    check. It builds on its CUBE-DOUBLING-R1, KNOT-CAP-R1 and COUNT-BALLS-R1 code.
- **The study's `picklib`** was imported only in the fill check, to compare its `fills()` with the referee's closure.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_pick.py`.**
- **`referee_pick_fills_check.json`.**
- **`referee_pick_trees.json`.**
- **`referee_pick_runs_summary.json`.**
- **`runs/`:** each batch's JSON, and the CAP(3) detail at `runs/CAPdetail_*`.

Reproduce, from `research/PICK-TWO-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_pick.py fills_check > referee_pick_fills_check.json
../../../.venv/bin/python -B referee_pick.py trees > referee_pick_trees.json
../../../.venv/bin/python -B referee_pick.py runs SEED line8 5 60 > runs/SEED_line8_5_60.json      # likewise each batch
```
