# Referee report MARK-RATE-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Theorem M is sound and Lemma S holds. The three things the owner was least sure of
check out, and the corrected count 479 is right. The fixes are three overstated sentences in the line summary.

**What holds.**
- **Theorem M.** Read step by step below. The union over contexts in the below-signature cut (item b) is harmless. Soundness needs
  only that the computed families contain every achievable signature.
- **Lemma S (item a).**
  - 3,600 real signatures from SAT were checked: random markings of 1 to 8 marks on 56 descriptions at N = 8 and 9, 2,335 of them
    proper subsets. All lie in marks.py's families.
  - The cut sets contain every full state's values (1,200 orbits).
- **An independent recursion.** The helper's own families equal marks.py's type by type on 439 descriptions, and its Theorem M test
  gives the same pass/fail on all 439. That covers every cyclic ruler with r = 2 or 3, all 43 half-rate and all 228 with r = 1.
- **The conclusion directly.** On 20 of the 55 newly passing cyclic rulers at N = 10 (5 also at 11):
  - there is no tie from level 3 at any s;
  - there is no three-member bond meeting levels 3 and 5, or 3 and 6;
  - so L ≥ s + 1 holds at s = 2 and 3;
  - a restricted search of 70.7 M four-member sets also finds no four-member bond at s = 3, with the detector validated on a
    half-rate description.
- **The 6 over the limit (item c).** None is a ruler (2 direct, 1 other, 3 undecided), and none is counted as a pass, so no ruler
  result depends on them.
- **The correction.** Counted directly, 479 alive descriptions have growing orbits, and there are 23 dead ones (22 growing, 1 small).
  So 1,288 − 786 = 502 = 479 + 23, as logged.

**What needs fixing** (line summary, wording):
- **"exactly where"** should say sufficient, not exactly. **Narrowing.**
- **"at a rate set by how many levels it takes to forget"** contradicts this study's own result. **Narrowing.**
- **"every-depth"** upper bounds hold at N ≥ 9. **Not a block.**

**How the work was split.**
- **The referee.** Read the proof, `marks.py`'s design, the predictions, the commit order and the line summary.
- **One Claude helper.** Recomputed with fresh code, reusing its DIRECT-REACH and BLOCK-REACH oracles, and called `marks.Marks` only
  as the thing under test (`NOTES.md`).
- **Codex** was not used. **The advisor** was not consulted.

## 1. The referee's reading

### Theorem M (sound, given Lemma S's families are supersets)

**The decomposition.** Group i is O_(k+i), the side subtrees of O_(k+i−1)'s other children, and the knots placed at O_(k+i−1).
Groups below i share only O_(k+i−1), and groups above share only O_(k+i). So with B ∩ group i = ∅, every knot lies in exactly one of
three parts:
- the upper part: X, the up signature of O_(k+i−1) given σ_L;
- the step: T_i, the side subtrees unmarked, with F stable because r₀ = 0;
- the lower part: Y, the below signature of O_(k+i) given σ_R.

So σ is allowed iff some (x, y) ∈ T_i has x ∈ X and y ∈ Y.

**The cuts.**
- An empty X-cut means σ_L does not extend: no x reaches a feasible child. Then L is constrained, a contradiction.
- An empty Y-cut means no up-feasible x reaches y. Then R is constrained, again a contradiction.
- Otherwise the hypothesis gives a meeting pair, so σ is allowed and B is free, a contradiction.
- So each of groups 1..s − 1 holds a member, and |B| ≥ s + 1.

**The union over contexts in the Y-cut (owner's item b) is harmless.**
- The code cuts Y with T's image of a union over contexts of the up-free set, which is a superset of the true context's up-free set.
- Any meeting pair (x, y) with x ∈ X has x in the true context's up-free set, since X ⊆ up-free. So y is in the true Y-cut.
- So a pass with the larger cut implies the true cuts meet.
- If the larger cut is empty, the true cut is empty too, so skipping it is justified.
- So soundness needs only that the computed families U(t) and below(t) CONTAIN every achievable signature.

**Lemma S (owner's item a).**
- Joins through blocks are exactly how projections compose on a tree of blocks (Theorem W).
- A least fixed point of "join one down signature per child", plus pins on own coordinates, reaches every finite marking's
  signature, by induction on the marking's depth extent.
- Unions over contexts only enlarge the families.
- So the lemma is right in principle. Whether marks.py implements it is tested empirically in §2 of the report.

### Pilot and predictions

- **The freeze.** predictions.md is in f273f812e (22:33:17 UTC), together with the pilot (`exploratory/pilot.json`) and before
  census_marks.json, which first appears in 199d0db87 at 23:13 UTC.
- **What was seen** is disclosed: the pilot's per-class pass counts, the right-part cut tightened during the pilot (rerun unchanged),
  and the gate.
- **Exclusion.** The pilot's 16 descriptions are excluded from P1 and P2.
- **Code changes.** marks.py is unchanged between the freeze and the close. run_census.py gained only the 120 s limit after the first
  run hung, which is disclosed.
- **Judgement.** Fair.

### The line summary (for overstatement)

1. **"The top binds every depth with a bounded bond exactly where a fixed relation between two orbits survives at every distance."**
   - "Exactly" is not established, even for small orbits. Four small-orbit descriptions never forget and are not known to be bounded,
     and 46 of the 100 constant ones are open.
   - The sentence sits under "interpretation", but should say "where … (a sufficient condition, and the only one found)".
   - **Narrowing** (wording).
2. **"… the bond has to pick up members as it goes down, at a rate set by how many levels it takes to forget."**
   - Forgetting over r levels gives a lower bound of one member per r levels (Theorem F), not the rate.
   - MARK-RATE's own 55 cyclic rulers with r = 2 grow one member per level.
   - Say "at least one member per r levels".
   - **Narrowing** (wording).
3. **"Become every-depth results" and "the first levels are exact"** (three members at s = 1, 2 for every half-rate description and
   at s = 1 for every ruler).
   - The upper bounds come from Lemma U, which holds for N ≥ 9 (depth-9 bonds within level 9 − r₀).
   - So "exact at every depth" should be "at every depth N ≥ 9". The lower bounds do hold at every depth.
   - **Not a block** (wording).
4. **The rest checks against the refereed records.**
   - The theorem table matches its sources.
   - 54 of 100 constant descriptions are bounded: 42 by blocks and 12 by descents.
   - Forgetting decides 782 of the 786.
   - 139 of 146 have life by finite readers.
   - The ruler-part disclaimer ("computed after the referee and not separately refereed") is honest.

## 2. The fresh checks (helper; `NOTES.md`)

| Item | Size | Result |
| --- | --- | --- |
| Lemma S closure (a) | random markings of 1–8 marks (on the orbit, its parent, nearby and deep below), 56 descriptions with r₀ = 0 at N = 8 and 9, including 17 newly passing and 12 failing cyclic rulers with r = 2; 3,600 nonempty SAT signatures (up, below, down) | every one lies in marks.py's U, below or D |
| The cuts (b) | 1,200 orbits, no marks | every full state's orbit value lies in the step's image of `_up_free`; the parent's value extends to a feasible child; the unmarked up signature is in U |
| An independent recursion and test | 439 descriptions (all cyclic r = 2 and 3, 47 acyclic r = 2, 43 half-rate, 228 with r = 1) | families equal type by type, pass/fail equal on all 439 |
| The conclusion | 20 newly passing cyclic rulers, N = 10 (5 at N = 11) | no tie; no three-member bond at s = 2, 3 (exhaustive); no four-member bond at s = 3 in a 70.7 M-set restricted search (detector validated) |
| The 479 count | every census record | 479 growing alive, 786 small alive, 23 dead |

## Fixes for the thread (listed for the owner, not folded in)

1. **Line summary, "exactly where a fixed relation between two orbits survives".** Make it a sufficient condition: four small-orbit
   descriptions never forget and are not known to be bounded, and 46 of the 100 constant ones are open. **Narrowing** (wording).
2. **Line summary, "at a rate set by how many levels it takes to forget".** Say "at least one member per r levels". This study's 55
   cyclic rulers with r = 2 grow one member per level. **Narrowing** (wording).
3. **Line summary, "every-depth results" and "the first levels are exact".** The upper bounds from Lemma U hold at N ≥ 9, so say "at
   every depth N ≥ 9" there. **Not a block.**
4. **Optional, mark_rate.md.** The theorem's "no bond of size ≤ s" needs only ties and three-member sets at s = 2. The referee's
   deeper searches go one size further, to the census values.

## Files

- `NOTES.md`: the helper's notes.
- `referee_*.py` and `referee_*.json`: the checks and their outputs.
- `report_draft_reading.md`: the referee's reading, the same text as §1.
