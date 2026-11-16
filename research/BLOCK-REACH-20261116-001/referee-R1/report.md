# Referee report BLOCK-REACH-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Theorem F and Lemma U hold. The block step is as stated, and Corollary F reproduces on
all 786 descriptions. The fixes are one index in the proof's prose, a time stamp, and an upgrade the study missed.

**What holds.**
- **Theorem F, both cases.**
  - Case 2's bookkeeping holds (the owner's item a): u in group 1, v in group k + s − b, windows over groups 2, …, k + s − b − 1.
  - The splicing through a rectangular window is right, and so is the remaining-depth tier N ≥ k + s + r₀ − 1.
- **The block step leaves the path child unrestricted by its own subtree and by its own knots** (item b), and that is the relation
  the sub-pattern actually has. Restricting the child changes 12 of 480 windows, and none of the 12 then matches SAT.
- **Lemma U** (item c): checked by SAT at N = 9, 12 and 13, beyond the study's 11.
- **Corollary F.** The table, P3's failure, and the gap counts reproduce exactly. No census value lies below the bound.

**What needs fixing.**
- **Theorem F's interface index.** **Not a block** (wording).
  - **The slip.** The proof says "the interface between groups j − 1 and j is the assignment of O_(k+j)". Group j holds the knots
    placed at O_(k+j−1), so the shared distinctions are O_(k+j−1).
  - **Fix.** Read "between groups j and j + 1"; the count is unaffected.
- **A missed upgrade.** All 43 half-rate descriptions have L_N(3, s) = 3 exactly at every depth N ≥ 9 for s = 1, 2.
  - **Lower bound.** DIRECT-REACH's Theorem W shows no tie at any depth, so L ≥ 3. That is the max(3, ·) in the proof's own remark.
  - **Upper bound.** Lemma U gives L ≤ 3.
  - **What the study says.** It reports these cells as "gap 1" against the bare bound 1 + ⌈s/r⌉. Against max(3, ·) the half-rate gap
    is 0 in 86 cells and 1 in 86.
  - **Upgrade**, not a correction of a claim.
- **The prediction file's time.** "Frozen 2026-11-16 21:00 UTC", but the file is in commit 169c0d53f at 20:45:54 UTC.
  - The substance is fine: the commit precedes the census output, which first appears in 6c9ce0f8a at 20:50:23 UTC, and what was seen
    before is disclosed.
  - **Not a block.**

**How the work was split.**
- **The referee.** Read the proof and `forget.py` and checked the census tallies from `census_forget.json`. See `NOTES_reading.md`.
- **One Claude helper.** Wrote the fresh checks, reusing the oracles it wrote for DIRECT-REACH-R1 (`../../DIRECT-REACH-20261115-001/referee-R1/`).
  It read the study's code for definitions only and never called it. Its notes are in `NOTES.md`.
- **Codex** was not used. **The advisor** was not consulted.
- **Runtime.** All runs took under 4 minutes.

## 1. Theorem F

**The reading** (`NOTES_reading.md`).
- **A window.** Groups i, …, i + r − 1 relate O_(k+i−1) to O_(k+i+r−1) by the composition of r block steps.
- **Splicing.** The left state and the right state agree with a window filling exactly when their cut values are related, which a
  rectangular relation guarantees. The right part supplies the last orbit's own knots and subtree.
- **The count.** Every r consecutive groups among 1, …, s − 1 hold a member of B, so |B| ≥ 2 + ⌊(s − 1)/r⌋ = 1 + ⌈s/r⌉.
- **Case 2.** The count is over groups 2, …, k + s − b − 1, and k − b − 1 ≥ 0.
- **Remaining depths.** The windows used end at levels ≤ k + s − 1, so every step has ρ ≥ N − k − s + 1.
- **`forget.py` checks more than it needs.** It also checks windows ending at ρ = 0, which only makes it more conservative.

**The fresh checks** (helper):
- **Forgetting lengths** (`referee_forget.py`). Recomputed independently for all 786 descriptions: r_stable, r_all and r₀ equal the
  census in every one.
- **Windows against SAT** (`referee_window_sat.py`).
  - 480 random windows at N = 11 and 12, over 90 descriptions, including every r₀ = 1 description and 39 windows ending at remaining
    depth 0.
  - In every one, the composed relation equals the SAT projection of the knots placed under the top orbit and not under the bottom
    one.
  - All 212 windows of length at least r are rectangular. 59 of the 82 shorter ones are not, so the claimed r is not loose.
- **The bound against exact values** (`referee_bound.py`).
  - 45 rulers with r = 1 (21 acyclic, 24 cyclic) and all 43 half-rate, at N = 11.
  - Exact ties, plus an exhaustive search of every three-member set with one member at level 3, one at level 6 and the third
    anywhere.
  - The least bond is never below 1 + ⌈s/r⌉ for s ≤ 3.

**Verdict.** Holds. The interface index is a wording fix.

## 2. Lemma U

- **The reading.** The projection onto addresses at levels ≤ m sees the deeper pattern only through F_(N−m) at the level-m orbits,
  and F is constant for N − m ≥ r₀. So every projection onto such a set, and onto its subsets, is constant for N ≥ m + r₀.
- **The fresh check** (`referee_lemmaU.py`).
  - 40 descriptions, 5 of them with r₀ = 1: 132 depth-9 least bonds of sizes 2 to 6.
  - Their exact projections are equal at N = 9, 12 and 13. Each is a bond at all three depths, lies within level 9 − r₀, and has the
    census's size.

**Verdict.** Holds.

## 3. The upgrade for the half-rate descriptions

- **The two populations are the same.** The 43 small-orbit half-rate descriptions here are DIRECT-REACH's 43; the referee checked
  the keys. Theorem W gives them no tie at any depth.
- **The upper bound.** Lemma U gives L_N(3, s) ≤ 3 for s = 1, 2 and every N ≥ 9 (their depth-9 values).
- **So** L_N(3, 1) = L_N(3, 2) = 3 at every depth N ≥ 9.
- **The SAT confirmation at N = 12, for all 43** (`referee_upgrade_all43.json`). There is no tie at s = 1, 2, and the census's
  three-member bond is still constrained, with every pair free.

## Fixes for the thread (listed for the owner, not folded in)

1. **Theorem F's interface index.** Change it to O_(k+j−1), or reword it as "between groups j and j + 1 is O_(k+j)". **Not a block.**
2. **Record the upgrade.** For the 43 half-rate descriptions, L_N(3, s) = 3 exactly for s = 1, 2 at every N ≥ 9. The gap there is 0,
   not 1. **Upgrade.**
3. **Fix the prediction file's time.** "21:00 UTC" should be no later than 20:45 UTC, its commit time. **Not a block.**

## Files

- `NOTES_reading.md`: the referee's reading and census tallies.
- `NOTES.md`: the helper's notes.
- `referee_*.py` and `referee_*.json`: the checks and their outputs.
