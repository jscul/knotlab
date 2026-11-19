# Referee report CHAIN-IDENT-001-R1 (proof read line by line; own extended complex, class test, growth, cover and clusters)

**Verdict: confirmed. Theorems 1 and 2 and Corollary 3 hold. No Block. One correction to the machine check's control count, which
also shows that (S5⁺) is stronger than needed; three wording points.**
- **The proof is correct** (Section 1).
  - The fresh table and both implied cases hold.
  - Lemma 0.5 on one-parent clusters is right: the chain clusters are exactly {w̃, o} and {w̃, o, a₁ … a_k}.
  - Lemma 4 carries over through Lemma 0.2. Lemma 5's counts are right.
  - Theorem 2's composition count, its degree R − 1, its coefficient Σ N_Y/(R − 1)! and its threshold t ≥ max |F_Y| are right.
- **The identification checks out with an independent enumeration**, comparing parents, fresh distinctions and the parents' keys,
  which is stricter than the study's check.
  - **2 to 7 knots:** all 81 starts in the class agree at every round to 6.
  - **One size past (8 knots, all 23 trees and a sample with cycles, with and without one surplus):** all 47 in the class agree.
- **Theorem 2 holds wherever tested.** On all 28 trees in the class to 7 knots and all 38 at 8 knots, with R = 1, 2 or 3:
  - the growth's counts equal the theorem's composition formula at every round from 0 to 20;
  - from t = max |F_Y| on, the (R − 1)-th differences are constant and equal to Σ N_Y, and the next differences are zero.
- **The four named starts, regrown by the referee's engine:**

| Start | Growth | Cluster count |
| --- | --- | --- |
| A pair | 2, 4, 6, 8, …, 26 = 2(t + 1) | the same |
| The path of three | 3, 4, 6, 8, …, 26 = 2t + 2 from t = 1 | the same |
| The path of four | constant 4 | the same |
| The path of five | 5, 5, 6, 8, 10, … | 5, 5, 5, 6, 7, … |

  The path of five is in the relay class. Its keys differ from round 1, where the top of {B, D} takes the floor's one fresh
  distinction, and its counts from round 2.
- **The correction: the relay control is not 137 of 137.**
  - **What the machine check does.** `machine_check.py`'s model loops over every point of X⁺ as a root, non-live knots included.
    It then adds each non-live knot again at round 0, so it counts every non-live knot twice.
  - **In the class** no start has a non-live knot, so the 81 of 81 stand.
  - **In the relay class** the double count is the only difference on 22 of the 137 starts, the stars K₁,₃ and K₁,₄ with their
    surplus variants. Grown with GF(2) implication they close exactly as the clusters say: 4, 3, 1 and then closed.
  - **What those 22 have in common:** each has one live component, finite, so its top takes every loose distinction, is implied
    and closes. Every relay-class start that does differ, 115 of 137 (and 161 of 169 at 8 knots), has two live components.
  - **So (S5⁺) can be weakened** to "every live component is infinite, or there is only one". The text's reading, "what (S5⁺)
    excludes is the relay", needs that qualifier.

## 1. The proof

- **The Setting and X⁺.**
  - open_k = max(3 − sh_k, d_k) + surplus_k.
  - The ray counts R(open) = max(0, 3 − open) are exactly what makes (b) hold for the round-1 offshoot. Its fresh count is
    max(open − 1, 2), and |∂{w̃, o}| = open − 1 + R.
- **Lemma 0.**
  - (1) A non-live knot has d = 0, so no knot lies at distance two from it. It is isolated, and it joins no two classes.
  - (2) Any pendant or ray point of a knot-holding cluster brings its own knot in. So two knot-holding clusters with a common
    point share a knot.
  - (5) **One-parent clusters (the hand-off's point).**
    - With one knot, C is a tree hanging from w̃, and R*(C) is its leaves other than w̃.
    - |R*(C)| = 1 exactly for {w̃, o} and {w̃, o, a₁ … a_k} entered from a lone pendant point.
    - The pair case is right: if v and v′ are both removable, no pendant point hangs on them, so C − {v, v′} keeps a knot unless
      C = {v, v′}.
    - **Correct.**
- **Lemmas 1 to 3.** Rays and pendant points lie on no cycle, and an axis is a doubly infinite geodesic, so it stays in the core.
  RING-IDENT's lemmas carry over verbatim. **Correct.**
- **Lemma 4.** Every place where RING-IDENT used "holds a knot" is supplied by Lemma 0.2. Chain clusters have one removable point,
  so they enter no group. The advisor's triple {w, o}, {w, o′}, {w, w′} has w as a common neighbour. **Correct.**
- **Lemma 5.**
  - d + r = |∂C|.
  - If |R*(C)| ≥ 2, every removable point other than the attaching one stays removable, so r = 0.
  - Otherwise r is s_w, R(open_w) or 1.
  - **Correct.**
- **The fresh table.**
  1. |R*| ≥ 2: d ≥ 1, so the junction gets d.
  2. {w̃, o}: max(open − 1, 2) = open − 1 + R(open).
  3. Chain clusters: d = 1, r = 1, giving 2.
  4. Implied cases:
     - **Case 3** is not implied: the parent holds |∂P| ≥ 2 loose distinctions and the offshoot takes one.
     - **Case 2** is not implied: a connected simple K with at least two knots holds at least two loose distinctions, and K₂ holds
       four.

  **Correct.**
- **Theorem 1's induction.** No stall. The offshoot extensions of one C are interchangeable and have equal |∂|, so any bijection
  serves for φ_{t+1}. **Correct.**
- **Theorem 2.**
  - For a tree, I(X) lies in K's bipartite double cover, so Γ is trivial.
  - A cluster is Q ∪ ray prefixes, with Q a knot-holding cluster of the core.
  - Ray prefixes of total length m − |Q| over a nonempty set S of rays based in Q number C(m − |Q| − 1, |S| − 1). That is a
    polynomial in m once m ≥ |Q| + 1, vanishing where it should.
  - The top degree comes only from the Q holding every ray base, N_Y of them.
  - **Correct.** It is checked numerically above.
- **Corollary 3.** Correct for bare trees with at least four knots.

**Wording points (not gaps):**
- **(a) The path of three.** Corollary 3 says "the middle knot has one pendant point with two rays". Its two leaves also each have
  a pendant point with one ray, since their neighbour has degree 2. Both parity classes have R = 2, which is why the coefficient is
  2 (1 + 1) and the count is 2t + 2.
- **(b) The fresh table's case 3.** It reads "|∂P| ≥ 2 …, a group extension and a_k". For open_w = 1 and k = 1, P = {w̃, o} has no
  group extension: its two loose distinctions are the two rays' first points. |∂P| ≥ 2 still holds.
- **(c) The Setting's "or exactly d if it is implied".** The program's fewest rule gives 0 only when implied with demand 0, and
  otherwise max(d, 3 − p, 1). It is the same point as RING-IDENT's (a), and harmless here.
- **(d) `machine_check.py`'s (S6)**, at least two live knots, is not among the proof's conditions. It never fires.

## 2. The referee's run (`job_chain.py` under `scripts/longrun.py`, 42 cases, all ok)

| Population | Starts | In the class: keys agree | Relay class (S5⁺ failing): differ / agree | Out by (S3) / by (S4) |
| --- | ---: | ---: | --- | --- |
| 2 to 7 knots, no surplus or one at one knot | 7,775 | **81 of 81** | **115 / 22** (the 22: one live component) | 7,151 / 406 |
| One size past: 8 knots (23 trees, 40 graphs with a cycle), the same variants | 567 | **47 of 47** | 161 / 8 (the 8: one live component) | 279 / 72 |

| Theorem 2, trees in the class | 2 to 7 knots | 8 knots |
| --- | ---: | ---: |
| Counts equal the composition formula, rounds 0 to 20 | 28 of 28 | 38 of 38 |
| (R − 1)-th differences constant and equal to Σ N_Y from max \|F_Y\| on; the next ones zero | 28 of 28 | 38 of 38 |
| R = 1 / 2 / 3 | 14 / 14 / 0 | 26 / 11 / 1 |

**The double count, located.** The study's own machine check, run read-only on K₁,₃ and K₁,₄ as a labelled cross-check, gives
growth and model multisets that differ only at round 0. There it has (0, 0) once for the growth and twice for the model, the
non-live centre counted twice.

## Corrections for the owner (listed, not folded in)

1. **The relay control** ("In the relay class, the control (S5⁺ failing): 137 of 137 differ") is 115 of 137. The other 22 differ
   only through `machine_check.py` counting each non-live knot twice. Correctly counted they agree, because their one live
   component closes by implication. The Validation and the S5⁺ paragraph should say that (S5⁺) can be weakened to "every live
   component is infinite, or there is only one". **Not a block:** the theorems are unaffected, since they hold under the stated
   (S5⁺).
2. **Wording points (a) to (d)** above. **Not a block.**

## How the work was split

- **The referee:**
  - read `chain_ident.md`, `proof.md` and `machine_check.py` with its output;
  - wrote `job_chain.py`: its own X⁺, class test, Theorem 2 formula and checks. It builds on its RING-IDENT-R1 `job_ring.py` (round-1
    groups, lazy cover, frontier enumeration, keys) and the FIRST-KNOT-R1 engine.
- **Run read-only as a labelled cross-check:** the study's `machine_check.py` (`classify`, `growth`, `model`) on the two stars, to
  locate the double count.
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 187 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
