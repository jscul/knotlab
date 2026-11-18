# Referee report RIM-EXCESS-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **Lemma P, its corollary and Lemma C check by hand.**
  - The referee also checked Lemma P one size past the study, on every disc of ten knots: 319,114 bonds and 319,117 tight cyclic
    orders.
  - Every tight order has D-sum exactly 3(m − 2) and is geodesic at every member.
- **The search's correctness claim holds,** as argued: Proposition 3 with Lemma P, Lemma C and Theorem 7.
  - The frozen R2 tested it only on discs to nine knots, where no bonded pair has an excess.
  - The referee tested it where it matters, against brute force at excess 1 and 2, with its own search and with the study's: no
    mismatch.
- **The 20 timed-out searches are settled, except three.**
  - 9 have excess 0.
  - 8 are certified unbonded: the search was exhausted to the largest excess the patch allows, |V| − 2 − s.
  - 3 have no bond up to excess 8, 8 and 9.
  - So none of them hides an excess between 1 and 8.
- **Past the study, the excess stops rising.**
  - Every disc of thirteen knots (104,902) has largest excess 2, on 24 pairs.
  - Every disc of fourteen knots (291,312) has largest excess 2, on 102 pairs.
  - Every other facing pair settled: excess 0 or 1, or certified unbonded.
  - So "rises by one about every two knots, which points to growth" now meets 2, 2 at thirteen and fourteen. **Narrowing (wording).**
- **Two wording fixes (Not a block).**
  - R2's reading should say that it validated excess 0 and the unbonded pairs only.
  - "Unbondedness is certified only by brute force over the states" is too pessimistic: the search certifies it at the size bound.
- **WEAVE-HEIGHTS's fold-in (`3d65100fe`) is faithful.**

## What holds

| Reading | Referee | Study |
| --- | --- | --- |
| Lemma P: bonds with least cyclic D-sum 3(m − 2) | every disc of 10 knots, 319,114 of 319,114; all 319,117 tight orders geodesic | discs to 9 knots, 116,932 (least D-sum only) |
| Search = brute force, excess 1 | 60 pairs (10 and 11 knots, every one) + 24 (random 12 and 13) | none tested (no excess to 9 knots) |
| Search = brute force, excess 2 | 6 pairs (3,000 random discs each of 12 and 13 knots) | the gate disc only |
| Search = brute force, unbonded | 10,560 (10 and 11 knots, every one) + 2,810 (random 12 and 13) | to 9 knots |
| The study's own search = brute force on the excess and unbonded pairs of 10 and 11 knots | 10,620 of 10,620, no timeout | — |
| Excess and unbonded pairs lone, opposite, facing | every pair at 10 and 11 knots; 3,000 random discs of 13 knots by brute force; none below steps + 1 | 11 and 12 knots |
| Largest excess, every disc of 13 knots (104,902; 88,308 facing pairs) | **2** (24 pairs; 636 at 1; 24,972 at 0; 62,676 certified unbonded) | not run |
| Largest excess, every disc of 14 knots (291,312; 263,673 facing pairs) | **2** (102 pairs; 2,076 at 1; 82,878 at 0; 178,617 certified unbonded) | not run |
| The study's 160 random patches, 274 facing pairs | 262 at 0, 1 at 1, 8 certified unbonded, 3 with no bond to excess 8 or 9 | 253 at 0, 1 at 1, 20 timeouts |

**The referee's search** (`referee_rim.py`, `search`) follows ticket A's statement: levels e = 0, 1, …, Lemma C's candidates, cyclic
sequences of s + 2 + e members with D-sum 3(s + e), and geodesics at every member. It adds three prunings, each valid for bonds:
- the walk's lower bound;
- no contiguous run of the partial sequence, closed up, may be tight (it would be a tight proper sub-collection);
- removing two consecutive members lowers the D-sum by at most 3 (Lemma P's remark).

Minimality uses the referee's own numpy Held–Karp over every sub-collection and every cyclic order. Brute force comes from the
states, as in DOUBLE-MEET-R1, and walk weights from WEAVE-HEIGHTS-R1.

## 1. Lemma P (pressed hardest)

**Every step holds.**
- **Cyclic D-sums are multiples of 3.** By Lemma 2(i), every walk weighs ≡ c(t) − c(s).
- **δ_s is a non-negative multiple of 3.** We have δ_s = D(p, s) + D(s, n) − D(p, n). It is ≥ 0 by the triangle inequality for D,
  and ≡ 0 because each D term is ≡ the class difference.
- **For m ≥ 4.**
  - B − s is free, so its induced order (m − 1 ≥ 3 members) is not tight: L − δ_s > 3(m − 3).
  - With L ≤ 3(m − 2) this gives δ_s < 3, so δ_s = 0.
  - Then L > 3(m − 3), and since L is a multiple of 3, L = 3(m − 2).
  - The argument applies to every s and to every cyclic order with D-sum ≤ 3(m − 2), not only Corollary 4's.
- **For m = 3.**
  - The pair left has D-sum 3 s(p, n) ≥ 3 (Lemma 6, so the case rests on Lemma 5's cited theorems).
  - So δ_s ≤ L − 3 ≤ 0 and L = 3.
- **The remark.** Removing r members, leaving at least three, leaves a free set, so the D-sum drops by less than 3r, hence by at most
  3(r − 1). It holds for m − r = 2 as well, by Lemma 6. The referee's search uses r = 2.
- **The corollary is the definition of e rearranged.** All tight orders of a bond have D-sum 3(|B| − 2) by Lemma P, so W does not
  depend on the order chosen.
- **Lemma C holds.** The two arcs are walks from x to y and back, so each exceeds its D by a non-negative multiple of 3. A member's
  detour is at most its arc's excess.
- **Checked one size past** (`referee_rim_lemmaP.json`, every disc of ten knots, bonds by brute force from the states):
  - every one of the 319,117 cyclic orders with D-sum ≤ 3(m − 2) was enumerated;
  - every one has D-sum exactly 3(m − 2) and is geodesic at every member;
  - no bond lacks a tight order.
  - The study's R1 checked only the least D-sum, not the geodesic property.

## 2. The search's correctness claim (pressed hardest)

**The argument is right.**
- **Soundness.** A returned set has a cyclic order of D-sum 3(m − 2), so it is constrained (Proposition 3). It has no tight proper
  sub-collection, so every proper subset is free. So it is a bond of s + 2 + e members holding x and y, and b ≤ s + 1 + e.
- **Completeness.**
  - Let b = s + 1 + e*, with e* ≥ 0 by Theorem 7.
  - A least bond has s + 2 + e* members. Every tight order of it has D-sum 3(s + e*) and is geodesic (Lemma P), and every member is a
    candidate (Lemma C).
  - So level e* finds it or another bond of the same size.
  - Levels below e* find nothing, since a bond found there would be smaller.
- **The study's code implements this** (read: `polylib.pair_b_polygons`).
  - The geodesic test is applied at every member, including x and the last.
  - The bound on the rest of the walk is valid.
  - Minimality is tested over every sub-collection in every order.

**What the frozen check could see.**
- R2 compared the search with brute force on every pair to nine knots. Up to nine knots no bonded pair has an excess.
- So R2 validated only level 0 and the unbonded pairs (none to 6). At excess ≥ 1 the search was checked on the gate disc alone.
- **The referee closed the gap:**
  - its own search on every excess and unbonded pair of every disc of ten and eleven knots (60 at excess 1, 10,560 unbonded), plus
    the facing pairs and a sample of the rest;
  - the study's own search on the same 10,620 excess and unbonded pairs: no mismatch, no timeout;
  - its own search on every excess and unbonded pair of 3,000 random discs each of twelve and thirteen knots: 24 at excess 1, 6 at
    excess 2, 2,810 unbonded, no mismatch.
- **Narrowing (wording).** R2's reading should say "validated at excess 0 and on unbonded pairs". The referee's checks add excess 1
  and 2.

**An addition.**
- "Unbondedness is certified only by brute force over the states" is too pessimistic. No bond has more than |V| members, so running
  the search to emax = |V| − 2 − s exhausts every possible bond.
- The referee used this to certify 62,676 pairs at thirteen knots, 178,617 at fourteen, and 8 of the timed-out random pairs.
- It cost about 0.03 s a pair at thirteen knots.

## 3. The 20 timed-out random searches (pressed hardest)

- **The patches.** The referee regenerated the study's 160 random patches with the study's own generator and seeds (its weavelib's
  `nbrs` and `is_disc`, imported only for this). They have the same 274 facing pairs.
- **The searches.** It ran its own search on every pair: emax 12, 300 s each. Pairs left open were rerun to the size bound, 540 s
  each (`referee_rim_random.json`, `referee_rim_finish.json`).

| Outcome | Pairs |
| --- | --- |
| excess 0 | 262 (the study's 253 and 9 of its timeouts) |
| excess 1 | 1 (the study's example, seed 6032) |
| unbonded, certified (search exhausted to |V| − 2 − s) | 8 (patches of 20 to 25 knots) |
| unsettled after 540 s: no bond with excess ≤ 8, ≤ 8, ≤ 9 | 3 (two pairs of one 38-knot patch, seed 6017; one of a 37-knot patch, seed 6018) |

- **None of the 20 hides an excess between 1 and 8.** Most were unbonded pairs, which the study's search had to exhaust to excess 6
  within 20 s.
- The three left open have no bond of excess ≤ 8. They are most likely unbonded, but only an exhaustive search to excess 27 or 31
  would show it.
- **R5 ("no excess 3 or more") stands,** now tested on 271 of the 274 pairs, against 254 before.

## 4. One size past: does the excess keep rising?

**Not at thirteen or fourteen knots.**

| Knots | Discs | Facing pairs | Largest excess | At 2 | At 1 | Certified unbonded |
| --- | --- | --- | --- | --- | --- | --- |
| 10 (referee, brute force) | 5,005 | — | 1 | 0 | 12 | — |
| 11 (referee, brute force) | 13,746 | — | 1 | 0 | 48 | — |
| 12 (study, brute force) | 37,901 | — | 2 | 6 | 192 | — |
| 13 (referee, search) | 104,902 | 88,308 | **2** | 24 | 636 | 62,676 |
| 14 (referee, search) | 291,312 | 263,673 | **2** | 102 | 2,076 | 178,617 |

- **Coverage.**
  - At thirteen and fourteen knots the census covers the lone opposite facing pairs: every one, each settled.
  - That every other pair has excess 0 and is bonded is R3's statement. The referee checked it at thirteen knots on 3,000 random discs
    by brute force (every excess and unbonded pair lone, opposite, facing; none below steps + 1), but not exhaustively.
  - The fourteen-knot maximum is therefore over the facing pairs.
- **What it means.**
  - The exhaustive maxima run 0 to nine knots, 1 at ten and eleven, and 2 from twelve to fourteen.
  - The note's "rise by one about every two knots, which points to growth" would predict 3 by fourteen. Fourteen still has 2.
  - Growth stays unsettled, as the note says. But the exhaustive trend no longer points to it: the excess-2 pairs multiply (6, 24,
    102) without an excess-3 pair appearing.
  - **Narrowing (wording).**

## 5. Other points

- **The figure-eight** is labelled as the advisor's sketch and is not used. Not checked here.
- **The "In the owner's terms" table.**
  - Its random row should read: 274 facing pairs, 262 at 0, 1 at 1, 8 certified unbonded, 3 unsettled with no bond to excess 8.
  - Its growth sentence should cite thirteen and fourteen knots.
- **WEAVE-HEIGHTS's fold-in (`3d65100fe`) is faithful.**
  - The status, the Referee section and the Lemma 5 caveat are updated.
  - The Proposition 3 sentence is reworded as the referee asked.
  - The two stale DOUBLE-MEET phrases are corrected, with no new CORRECTIONS entry.

## Fixes for the thread (listed for the owner, not folded in)

1. **R2's reading.** "The polygon search equals brute force to nine knots" validated level 0 and unbonded pairs only, since no bonded
   pair has an excess there. Cite the referee's checks at excess 1 and 2 (90 pairs, no mismatch, both searches). **Narrowing
   (wording).**
2. **The random row and R5.** Replace "20 searches ran out of time" with the referee's settlement: 9 at 0, 8 certified unbonded, 3
   with no bond to excess 8 or 9. **Not a block.**
3. **The growth sentence.** "Rises by one about every two knots, which points to growth" should give the exhaustive maxima to fourteen
   knots: 2 at thirteen (24 pairs) and fourteen (102 pairs), no 3. **Narrowing (wording).**
4. **The search's certificate.** Say that run to |V| − 2 − s the search certifies that no bond holds a pair, without states. **Not a
   block; an addition.**
5. **Lemma P's m = 3 case** uses Lemma 6, which uses Lemma 5's cited theorems. The note's Limitations could say so. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `polylib.py`, `job.py` and the results, and checked Lemma P, the corollary,
    Lemma C and the search's argument by hand;
  - wrote `referee_rim.py`: its own polygon search, numpy Held–Karp minimality, brute force from the states, Lemma P with every tight
    order enumerated, the validations, the thirteen- and fourteen-knot censuses, and the random patches with their settlement;
  - read the WEAVE-HEIGHTS fold-in.
- **Imports of the study's code**, both read only:
  - its `polylib` search, as a cross-check of its own implementation;
  - its weavelib generator, to regenerate its random patches exactly.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_rim.py`.**
- **`referee_rim_lemmaP.json`, `_validate.json`, `_validate_big.json`, `_random.json`, `_finish.json`, `_k13.json` and `_k14.json`.**

Reproduce, from `research/RIM-EXCESS-20261118-001/referee-R1/`, one part per command (16 workers). Wall times: lemmaP 26 s, validate
7 min, validate_big 3 min, random 5 min, finish 9 min, k13 7 min, k14 18 min.

```sh
for p in lemmaP validate validate_big random finish k13 k14; do
  ../../../.venv/bin/python -B referee_rim.py $p > referee_rim_$p.json
done
```
