# Referee report RELAY-IDENT-001-R1 (proof read line by line; own relayed model, growth with the program's rule, Theorem 5 check, census tally)

**Verdict: confirmed. Theorems 4 and 5 and Corollary 6 hold. No Block; two wording points. A correction to my own earlier
reports is recorded below.**
- **The proof is correct** (Section 1). Step 3's invariant, step 4's induction on the J(i, l) and Theorem 5's assembly all hold.
- **The identification with relays checks out with an independent model.** On all 218 starts on 2 to 7 knots with (S3) and (S4),
  the referee's relayed model agrees with its own growth at every round to 9, comparing keys that include the parents' keys:
  - 81 with chains only;
  - 115 with a relay;
  - 22 with a single finite piece, which close.
- **Theorem 5 holds on every tree on 2 to 9 knots** (94 trees, no surplus). From the last core or top size on, the (D − 1)-th
  differences of the counts to round 24 are constant and equal to the stated leading coefficient times (D − 1)!. Values: D = 0
  (closes) 6, D = 1 11, D = 2 72, D = 3 4, D = 4 1.
- **The named starts reproduce.**
  - **The path of seven:** 7, 7, 7, 8, 10, 12, …, 34 to round 16, with D = 2 through a relay.
  - **The spider with four legs of two:** 9, 14, 18, 25, 40, 62, 91, …, 986, with D = 4. It equals C(t + 3, 3) + t + 1 at every
    round from 4 to 16. Rounds 0 to 3 differ: 9, 14, 18, 25 against 2, 6, 13, 24.
- **The tally reads the census's sizes, and correctly.** The census's own sizes give open_k = places − shared, and d_k is counted
  among live knots, as the growth counts it.
  - **The simple trees:** the referee's own count gives 307 that agree with the measured dimension, 119 stalls and no difference,
    as the study found.
  - **The wider figure is right too:** 3,753 of the 4,055 growing tree-shaped arrangements are two-dimensional, and every one is
    of dimension 1 or 2.
- **The non-live-knot double count is not here.** This study's check removes it. The referee's model counts each non-live knot
  once, and agrees with the study's tallies.

## 1. The proof

- **The Setting.** Finite pieces occur only when K is a tree, and a finite piece has at least two points. A lone live knot with no
  X⁺-neighbour has open = s pendant points, which carry rays unless open ≥ 3.
- **Step 1.** A junction's parents lie in its piece. Round-1 candidates are X⁺-adjacent knots. Later candidates share a parent. So
  only the implied test couples pieces. **Correct.**
- **Step 2.** CHAIN-IDENT applies piece by piece. In a finite piece, ∂ ≠ ∅ holds for every cluster but the top. The top has
  p = |R*(Y)| ≥ 2: the non-cut points, or at least three leaf pendant points around a lone knot. Its demand is 0. **Correct.**
- **Step 3 (the invariant).**
  - In a connected presentation, a junction is implied exactly when it takes every loose distinction.
  - With q ≥ 2 pieces, every piece's latest junctions always hold at least one loose distinction: proper clusters have ∂ ≠ ∅, a top
    gets 1, relay junctions get 2.
  - A junction takes distinctions only from its own piece, so none is implied. That covers two tops in one round and the relay
    point.
  - With q = 1 the top takes everything, is implied, gets d = 0 and closes.
  - Before the top, every one-parent cluster is {w, o} with d = open_w − 1 ≥ 2, so the implied rule changes nothing.
  - **Correct.**
- **Step 4 (the induction on J(i, l)).**
  - **k = 1.** The top's one distinction makes the offshoot J(0, 0): p = 1, d = 0, so 2 fresh.
  - **Candidates.** Two junctions of a round share a parent exactly when they are neighbours (J(i, l) and J(i − 1, l + 1) share
    J(i − 1, l)). So the groups are the k − 1 neighbouring pairs.
  - **Fresh counts.** The two chain ends have d = 1 and p = 1, so they get 2 and leave one offshoot each. Inner junctions have
    p = 2 and d = 2, so they get 2 and leave none.
  - **The count.** That makes (k − 1) + 2 = k + 1 junctions, J(i, l) with i + l = k.
  - **The dictionary.** The clusters Y ∪ {z} ∪ A ∪ B with |A| + |B| = k − 1 match the junctions with their R* and boundary.
  - **Correct.**
- **Theorem 5.**
  - Pieces add.
  - A finite piece with q ≥ 2 contributes k in round r_Y + k: degree 1, coefficient 1.
  - An infinite piece contributes degree R_Y − 1 with N_Y/(R_Y − 1)!.
  - The top degree D − 1 and its coefficients follow, the finite pieces adding to the D = 2 coefficient.
  - **Correct.** It is checked on 94 trees.
- **Corollary 6.** Correct for bare trees with at least four knots.

## 2. The referee's runs (`job_relay.py`, `job_relay_census.py` under `scripts/longrun.py`)

| Part | Result |
| --- | --- |
| K: 218 starts on 2 to 7 knots with (S3) and (S4), keys to round 9 | **218 of 218 agree** (81 chains only, 115 relay, 22 single finite piece) |
| D: every tree on 2 to 9 knots, counts to round 24 | **94 of 94**: closes when D = 0; (D − 1)-th differences constant and equal to the stated coefficient times (D − 1)! |
| N: path of seven | 7, 7, 7, 8, 10, 12, 14, …, 34 |
| N: spider with four legs of two | 9, 14, 18, 25, 40, 62, 91, 128, …, 986; C(t + 3, 3) + t + 1 at every round 4 to 16 |
| C: simple trees of the touch census (census sizes, demand among live knots) | **307 agree**, 119 stall, 0 differ |
| C: tree-shaped growing arrangements (dimension 1 or 2), simple and with double touches | 4,055, of which **3,753 two-dimensional** |

## Wording points for the owner (listed, not folded in)

1. **The tally goes beyond the proofs' Setting in two ways**, and should say so.
   - **Non-bare starts.** 36 of the 307 simple trees are not bare starts with surplus: a non-live knot has a common K-neighbour with
     a live knot. That is against the proofs' convention, where such a knot is live (CHAIN-IDENT Lemma 0.1). There the tally counts
     d among live knots, as the growth does, and agrees in all 36. The note's "the proofs use only open_k and d_k" should add "with
     d_k counted among live knots".
   - **Double touches.** "93% of growing tree-shaped starts (3,753 of 4,055) are two-dimensional" and "a relay is part of the
     reason in 2,678 of them" count arrangements with double touches: 3,487 and 2,434 of them. The proofs assume K simple, and the
     tally's prediction differs on 32 of those arrangements. The simple trees, where the theorem applies, are 266 of 292 growing
     (91%).

   **Not a block.**
2. **"C(t + 3, 3) + t + 1 from round 4 on"** is exact from round 4 (rounds 0 to 3 are 9, 14, 18, 25 against 2, 6, 13, 24). As
   worded, correct. **Not a block.**

## A correction to the referee's own earlier reports

In RING-IDENT-001-R1 (point a) and CHAIN-IDENT-001-R1 (point c), the referee wrote that the program's fresh rule gives 0 only when a
junction is implied with demand 0, and otherwise max(d, 3 − p, 1). That is wrong.
- **What the program does.** `freelib.floored` (FRESH-COUNT-20261118-001) gives exactly d at an implied junction, with no floor,
  as the proofs said.
- **What the referee's engine does** (FRESH-COUNT-R1) is the other rule.
- **Why it made no difference.** On a connected presentation an implied junction takes every loose distinction, so it is the
  round's only new junction and its demand is 0. Both rules then give 0.
- **What it touched.**
  - **The two proofs.** The folds (94e027daf, 581a639a2) kept the code's rule.
  - **The referee's earlier checks.** All were on connected presentations, except DROPPED-JUNCTION's re-choices. Those can be
    disconnected, and an implied junction there could have demand 1 or more. The 19 differences reported there were traced to
    an implied junction with demand 0, where both rules agree.
- **This report** grows with the program's rule.
- **Verdict on this correction:** Not a block, a wording correction to two referee reports. It is for the coordinator to log.

## How the work was split

- **The referee:**
  - read `relay_ident.md`, `proof.md`, `machine_check.py` with its output, and `tally.py` with its output;
  - wrote `job_relay.py` and `job_relay_census.py`. These cover the relayed model, the growth with `floored`'s rule, the
    Theorem 5 checks and the census tally. They build on its CHAIN-IDENT-R1 and RING-IDENT-R1 jobs and the FIRST-KNOT-R1 engine.
- **Read as data:** the touch census's runs and the networkx atlas.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 345 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
