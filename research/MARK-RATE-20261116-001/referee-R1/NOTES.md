# Referee R1 — MARK-RATE-20261116-001, fresh-code recheck

2026-11-16.
- **My own code.** My DIRECT-REACH and BLOCK-REACH referee oracles are imported read-only: `referee_pattern.py` (builder and SAT),
  `referee_blocks.py` (block DP), `referee_check_s5.py` (exhaustive three-member search) and `referee_window_sat.placed_knots`
  (knots with their placing address).
- **Study code called as the thing under test:** `marks.Marks` on `window_tree.WindowTree` (items 1 and 2).
- **Data read as claims:** `census_marks.json`, the census records and `docs/CORRECTIONS.md`.
- No git; scratch removed.

## Summary

| Item | Verdict |
| --- | --- |
| 1. Lemma S closure, empirical (owner's (a)) | **Matches.** 3,600 real signatures from markings of up to 8 marks (56 descriptions, N = 8 and 9) all lie in marks.py's families; 1,200 cut checks hold |
| 2. My own families | **Matches.** Equal to marks.py's type by type (D, U, below, Ufree) on 439 descriptions, with the same pass/fail on all 439 |
| 3. The conclusion directly | **Matches.** 20 newly passing cyclic rulers at N = 10 (5 also at N = 11): no tie, no three-member bond at s = 2 or 3, no four-member bond in the band at s = 3 |
| 4. The logged correction | **Matches.** 479 alive descriptions have growing orbits; 1,288 − 786 = 502 counts 23 dead ones too |

Nothing differs. On reading, the coordinator's argument for the cut (owner's (b)) is right: cutting with a larger set (a union over
contexts) leaves the cut sets larger, and the test needs them only to be nonempty and to meet T. The empirical cut checks in item 1
confirm the facts the argument uses.

## 1. Lemma S closure (owner's (a)) — Matches

`referee_signatures.py` → `referee_signatures_N9.json` (seed 9099) and `referee_signatures_N8.json` (seed 9098).

**Sample.** Each run draws 30 descriptions with r₀ = 0 and marks.py time ≤ 20 s; the two runs share some, for 56 distinct:

| Class | Descriptions |
| --- | ---: |
| newly passing cyclic r = 2 | 17 |
| failing cyclic r = 2 | 12 |
| failing cyclic r = 3 | 5 |
| passing acyclic r = 1 | 8 |
| failing acyclic r = 2 | 6 |
| failing half-rate | 8 |

**Setup.**
- marks.py's types and children are first checked identical to my block DP's, so element orders agree.
- For 20 random explicit orbits per description (levels 1 to 6) I draw random markings of 1 to 8 marks. Up markings mix marks on O
  itself, its parent orbit, nearby levels and anywhere allowed. Below markings mix children, grandchildren and deep levels.
- Mark counts: 1: 331, 2: 396, 3: 436, 4: 376, 5: 342, 6: 275, 7: 191, 8: 47. In 6 more markings every drawn pool was empty, so
  they had no marks.

**Signatures**, each by my SAT on my explicit P_N:
- **up:** knots placed outside O's subtree; marks outside O's proper subtree, O allowed;
- **below:** knots placed at O or below; marks strictly below;
- **down:** the below marks plus pins on O.

**Results.**
- **All 3,600 nonempty signatures lie in marks.py's families:** U(t), below(t) and D(t) respectively. 1,200 up, 1,200 below and
  1,200 down; 316 markings were empty and skipped.
- Most are proper subsets: 874 up, 462 below and 999 down. 496 up, 310 below and 450 down are distinct (description, type, set)
  values.
- **Cut checks (owner's (b)), 1,200 orbits:**
  - every full state's value on O lies in the step's image of marks.py's Ufree (ran);
  - its value on O's parent orbit extends through the step to a feasible child (dom);
  - the unmarked up signature is in U(t) and within Ufree(t).

  All hold.

## 2. My own families — Matches

`referee_marks_lib.py` (my recursion) and `referee_families.py` → `referee_families.json` (all 439, 704 s) and
`referee_families_balanced.json` (6 per class).

**My recursion**, over my blocks, with bitmask sets and written from Lemma S:
- **D:** pins on F, then joins of one child down signature per child through the block, then pins.
- **below:** the joins with no pin.
- **U:** at the root, all assignments pinned. Then the parent's up signature joined with the other children's down signatures, then
  pinned, as a union over every (parent type, child) context.
- **Ufree:** the union over contexts of the unmarked values.
- **Each family** is iterated to a fixed point.
- **My Theorem M test** uses the dom and ran cuts.

**Results.**
- **439 descriptions**: every cyclic ruler with r = 2 (55 newly passing, 48 failing), every cyclic r = 3 (18), 47 acyclic r = 2, all
  43 half-rate and the 228 rulers with r = 1. Only the single acyclic r = 3 ruler is missing.
- **The families are equal to marks.py's for every type** (D, U, below and Ufree), up to 128 types and family totals of 1,527 sets.
- **My verdict equals marks.py's and census_marks.json's on all 439** (the 55 + 228 passes and every failure).

## 3. Theorem M's conclusion directly — Matches

`referee_no_skip_sat.py` → `referee_no_skip_N10.json` (20 descriptions) and `referee_no_skip_N11.json` (5).

**Sample.** 20 of the 55 newly passing cyclic rulers with r = 2, drawn at random (seed 333). All have census profile [3, 4, 5, 6].

**At N = 10:**
- **Ties.** Exact ties from level 3 to every deeper level: none, at any s. That gives L ≥ 3 at s = 2, Theorem M's claim.
- **Three-member sets, exhaustive.** Every {x at level 3, y at level 5 or 6, z any}: 523,520 and 1,047,040 sets per description. Every
  one was seen with all 8 patterns in checked models, so none is constrained. That gives L ≥ 4 at s = 2 (the census value) and L ≥ 4
  at s = 3 (Theorem M's claim).
- **Four-member sets at s = 3**, which would test the census value 5:
  - A full search is not feasible (about 10⁹ sets), so it was **restricted**: every {x at level 3, y at level 6, z, w in levels 3..6}.
    That is 3.5M sets per description, 70.7M in all.
  - 43,580 were not covered by the models. All but 60 contain a tied pair or a constrained triple (decided exactly). Those 60 were
    decided by SAT: **0 four-member bonds.**
  - The detector works: on a half-rate description it finds 128 four-member bonds meeting levels 3 and 6, as L₉(3, 3) = 4 there
    predicts.
- **At N = 11 (5 of the 20): the same, 0 of everything.**

**On your wording.** "No bond of size ≤ s" is Theorem M's claim, and it needs only the ties (s = 2) and the three-member search
(s = 3). The three-member search at s = 2 and the four-member search at s = 3 go one size further, to the census values.

## 4. The logged correction — Matches

`referee_count_growing.py` → `referee_count_growing.json` (4 s).

Every census record was counted directly, by two independent criteria (my block closure, and explicit orbit sizes at levels 0 to 10),
which agree on all 1,288:

| | Small orbits | Growing |
| --- | ---: | ---: |
| alive | 786 | **479** |
| dead | 1 | 22 |

So 1,288 − 786 = 502 = 479 + 23 dead, as `docs/CORRECTIONS.md` says. The first level with an orbit over 4 addresses: 3 (451),
4 (35), 5 (9), 6 (4), 7 (1), 9 (1).

## Runtime

All runs took under 12 minutes. Most took seconds; the full 439-description families comparison took 704 s.
