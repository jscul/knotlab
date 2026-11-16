# BLOCK-REACH-R1: referee's reading notes (2026-11-16)

## Theorem F

**The interfaces.** As written, group j holds O_(k+j), the side subtrees of the other children of O_(k+j−1), and the knots placed
at O_(k+j−1). So its knots touch O_(k+j−1), which sits in group j − 1.
- The distinctions shared by groups j − 1 and j are therefore O_(k+j−1), not O_(k+j) as the proof says ("The interface between
  groups j − 1 and j is the assignment of O_(k+j)").
- Equivalently, the interface between groups j and j + 1 is O_(k+j).
- The relation of group j is correctly the block step from O_(k+j−1) to O_(k+j).

**The rest of the argument.**
- A window of groups i, …, i + r − 1 relates O_(k+i−1) to O_(k+i+r−1) by the composition of r block steps.
- Splicing a left state and a right state through a rectangular window gives a state: the right part supplies O_(k+i+r−1)'s own
  knots and subtree, which the step does not impose.
- The count 2 + ⌊(s − 1)/r⌋ = 1 + ⌈s/r⌉ is right.
- Case 2 is right: u lies in group 1, v in group k + s − b, and windows are counted over groups 2, …, k + s − b − 1, with
  k − b − 1 ≥ 0.
- The remaining-depth tier is right. The windows used end at levels ≤ k + s − 1, so every step has ρ ≥ N − k − s + 1.

**forget.py checks windows ending at ρ = 0 too.** That is stricter than the proof needs, which is conservative, not wrong.

**Verdict.** Holds. The interface index is a one-line wording fix (Not a block).

## The block step (the owner's item b)

- **The child is unrestricted.** `window_tree.WindowTree.step` restricts the parent orbit by the knots placed at it (W[t]) and every
  other child by F_ρ. The path child is restricted by neither its own subtree nor the knots placed at it; those knots belong to the
  next step's W.
- **Rectangularity.** `forget.Steps.rel` passes the identity on all 2^m assignments, so rectangularity is tested on all assignments.
  The proof's remark notes this is sufficient, not necessary.

**Verdict.** As stated.

## Lemma U

- **The proof.** The projection onto addresses at levels ≤ m sees the pattern below level m only through F_(N−m) at the level-m
  orbits, and F is constant for N − m ≥ r₀. So the projection, and the projection onto every subset, is the same for all
  N ≥ m + r₀, and a bond stays a bond.
- **The SAT check to depth 11.** A sanity check only. The lemma does not rest on it.

**Verdict.** Holds.

## The census (recomputed from census_forget.json by the referee)

- **Counts.** 786 descriptions, r₀ = 0 for 779 and 1 for 7, r_stable = r_all in all 786. The table reproduces exactly: rulers
  acyclic 197/47/1 and cyclic 31/105/18; half-rate 19/24; other 5/8/1 plus 2 never; undecided 6 plus 2 never; no bond 278; direct
  42 never.
- **Upper bounds.** Every decided ruler and half-rate cell at s = 1..4 has a depth-9 bond within level 9 − r₀.
- **Ruler gaps.** The gap to 1 + ⌈s/r⌉ is 1 in 1,083 of 1,596 cells, 2 in 323 and 3 in 190.
- **Half-rate gaps.** 148 of 172 have gap 1 against the bare bound 1 + ⌈s/r⌉. **Upgrade, not stated in the study:** for these 43
  descriptions DIRECT-REACH's Theorem W shows no tie at any depth, so the bound is max(3, 1 + ⌈s/r⌉), as the proof's own remark
  says. Against it the gap is 0 in 86 cells (s = 1 and 2) and 1 in 86 (s = 3 and 4). So L_N(3, s) = 3 exactly at every depth
  N ≥ 9 for s = 1 and 2, for all 43 half-rate descriptions.

## The predictions

- **Committed before the run.** `predictions.md` is in 169c0d53f (12:45:54 −0800, that is 20:45:54 UTC). census_forget.json first
  appears in 6c9ce0f8a (20:50:23 UTC).
- **A timestamp slip.** The file says "Frozen 2026-11-16 21:00 UTC", later than its own commit.
- **What was seen first** is disclosed: the exploratory stable lengths, which give most of P1's content, and the gate.
- **The outcomes reproduce.** P3's failure reproduces: r = 1 is 31 of 154 cyclic (20%) against 197 of 245 acyclic (80%).
