# MARK-RATE-R1: referee's reading (folded into report.md)

## Theorem M (sound, given Lemma S's families are supersets)

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

## Pilot and predictions

- **The freeze.** predictions.md is in f273f812e (22:33:17 UTC), together with the pilot (`exploratory/pilot.json`) and before
  census_marks.json, which first appears in 199d0db87 at 23:13 UTC.
- **What was seen** is disclosed: the pilot's per-class pass counts, the right-part cut tightened during the pilot (rerun unchanged),
  and the gate.
- **Exclusion.** The pilot's 16 descriptions are excluded from P1 and P2.
- **Code changes.** marks.py is unchanged between the freeze and the close. run_census.py gained only the 120 s limit after the first
  run hung, which is disclosed.
- **Judgement.** Fair.

## The line summary (for overstatement)

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
