<!-- modelUsage: claude-fable-5-2 -->

**Verdict:** T1, T2, T3 and the T4 construction are correct; the T4 conjecture and the "at most two directions" line in the proposed answer are false; T6 does not extend beyond N^a. I checked these by hand against the policy as you state it and ran no code; the only thing I looked up was word use in `publication/knotlab/INTUITIONS.md`.

## 1. T1–T6

**T1: correct.** The candidate relation is exactly "common lower cover": live junctions all have rank t, their only neighbours are at rank t−1, and I ∩ I′ of size t−1 is an ideal, so it is present. The sunflower/co-star dichotomy is standard, and two members fix the union U, so each pair lies in one group. Three things to add:

- **Simpler demand.** d(I) = |min(Q_t \ I)|, the number of minimal elements of the current order outside I. Every such q gives a non-principal I ∪ {q}, because an element whose strict down-set is I does not exist yet. This also shows the lookahead is well defined: d depends only on one-parent junctions of rank ≤ t.
- **Missing clause.** The hypothesis should read k ≥ d, and k ≥ 1 unless the parity is implied.
- **Implied parity.** A new junction's parity is implied iff its group takes every loose bit, which is iff d = 0, which is iff it is the only live junction (I = Q_t). So "d = 0 and parity not implied" never happens.

**T2: correct.** I re-derived all three stall rounds, including the S–S sibling pairs at round 3, which do not change the count.
- Reconcile with the public text: section 9.6 says four fresh distinctions stall "at its fourth round" with 3(k−2) groups. That is your T3 with a 4-place seed. From a 3-place seed with c = 4, T2 gives round 3. State which seed the earlier study used.

**T3: correct.** A sharper form worth stating: the capped and uncapped policies agree exactly while no ideal has four or more maximal elements, i.e. while the width of Q is at most 3. The cap is a bound on width.

**T4: construction correct; two errors around it.**
- **Wrong surplus description.** F adds surplus at a one-parent junction with d ≤ 1, or at a two-parent junction with d = 0. The second case is the floor 3 − p = 1, and it fires even though the parity is implied.
- **Forced bit.** In that second case the fresh bit is forced to 0, so it is not an open distinction. It cannot arise from a bare knot, but it can after random surplus. Decide which wins, the floor or openness, and have the census flag forced bits.
- **Conjecture false**: see section 3.

**T5: plausible, not checked line by line.**
- Geodesic paths in a bipartite graph are induced, so your cut size is exact.
- The lower bound on bond size is the connectedness of minimal cuts when short cycles generate the cycle space (Babson–Benjamini 1999, Timár 2013). Cite it rather than re-prove it.
- Say whether the claim is for the limit or uniform in the round, since the outside vertex adds cycles at the frontier.

**T6: correct for N^a only.** The 3a − 2 bound is tight at {0, e1, e2}. The lemma "three junctions cut more than any star" fails on mixed sizes:
- In the 3-cube any path of three junctions cuts 5 ≤ 2a = 6.
- Under F after surplus, three consecutive chain junctions cut 3+3+3−4 = 5, the size of a two-parent junction with d = 3.

So a threshold reader is unproved off N^a, and P8 is at risk.

**Literature.** Yes, known in substance:
- Birkhoff's theorem in its finitary form (Stanley, EC1, Prop. 3.4.3): locally finite distributive lattices with a bottom are the finite ideals of a poset with finite principal ideals.
- Closest match: prime event structures without conflict and their configuration domains (Nielsen–Plotkin–Winskel 1981). Events are your one-parent junctions, and adding surplus is adding an event.
- Your valid-set rule is the cube condition of median graphs and CAT(0) cube complexes (Chepoi 2000; Barthélemy–Constantin 1993): pairwise squares with no common corner fill in a cube.
- The parity system itself is the cycle code of the cover graph, and bonds are its cocircuits.

## 2. A distance-only criterion that picks a number

I see none. By T1 a rule's only freedom is the surplus s(I) ≥ 0, read from a local view. The only numbers in that view are p, d, the parents' sizes and the floor.

The one positive statement available: if every junction and every join has the smallest knot's size, the result is three (seed 3, count 3, cap vacuous by T3). That is one told number, the knot's three places, used twice. It is not distance-derived.

One untested candidate: choose the least k that leaves every already-read bond distance unchanged in later rounds. I have no evidence it selects anything.

## 3. T4 conjecture: false

**Counterexample (a = 3).**
1. Grow the cube under F to level 2.
2. Give each pair junction P_jk one surplus bit; its child is q_i.
3. Apply F from round 3. The live junctions are T (three parents) and q_1, q_2, q_3 (one parent each).
4. Each q_i is a candidate only with T, so d = 1, k = max(1, 2) = 2, one surplus.
5. I followed rounds 4 and 5 by the policy: each chain end is again in exactly one pair, with no stall and no forced bit.

That is three new one-parent junctions every round, forever. The same construction on 2^a minus its top gives a chains for any a.

**Replacement theorem (short proof).** Under F, a one-parent junction with d ≤ 1 starts a chain that never ends.
- Its child S has the parent as its only neighbour.
- The parent has exactly one other child G, so S's only candidate is G.
- A valid set needs three, so S is in exactly the pair {S, G}: d(S) = 1 and it gets one surplus.

F creates one-parent junctions nowhere else, apart from the forced-bit case. So from F's first round the number created per round is constant: the number of live one-parent junctions with d = 1 at the hand-over, or 2 if a sole live junction has d = 0.

**Consequences.**
- F from a bare knot sustains zero directions, and otherwise F conserves whatever it is handed, with any number possible. The proposed answer must say this instead of "at most two".
- Your pilot fits: constant per-round counts are one chain, linear counts are two. Three or more need a parent with d ≤ 1 at the hand-over, which random surplus rarely produces.

## 4. Growth on J(Q)

- **Proxy.** Ideals of size ≤ t is the right proxy only when junction sizes are bounded. Size is p + k and d ≤ width, so finite width suffices. With unbounded sizes, bits and junctions grow differently and a path's cut is no longer proportional to its length.
- **"Width w gives t^w" is false.** Width w gives only the upper bound O(t^w), since Q is a union of w chains and J(Q) sits inside N^w. Example: two chains with x_i < y_{i+1} and y_i < x_{i+1} have width 2 and linear growth. The exponent is the number of chains that are eventually independent, anywhere from 1 to w.
- **Infinite width.** J(N²) grows like the partition numbers, exp(π√(2n/3)) (Hardy–Ramanujan). J(N³) grows like plane partitions, exp(c·n^(2/3)) (Wright). Neither has an exponent.

## 5. Predictions

| | Verdict | Change |
|---|---|---|
| P1, P2 | Theorems now | Keep as replay checks, not predictions. State the seed size against section 9.6. |
| P3 | Fine | Balance stalls at round 2 (k = 1 < a − 1). |
| P4 | Fine | Also check no ideal is built twice and no bit is forced. |
| P5 | Risky at K = 2, a = 3 | There the floor makes one-parent counts always 2, so single chains never stall. Pilot that cell first. Report forced bits separately from stalls. |
| P6 | "Never stalls" is true by construction | At q = 0.05, a = 3, about two thirds of runs close as the plain cube by round 3. Predict the alive fraction at round 10, increasing in q, and state "≥ 3 per round" only for q ≥ 0.2. |
| P7 | False | Replace: under F the number of new one-parent junctions per round is constant from the first F round and equals the hand-over count above. Add the explicit run: 2^a minus top with one surplus per level-(a−1) junction gives a chains, a = 3, 4, 5. |
| P8 | At risk | Split into uniform-size presentations (predict exact) and mixed-size (predict at least one misread from a three-junction cut no larger than a star). |

Add **P9**: the capped policy equals the uncapped one on a run iff no ideal has four or more maximal elements.

## 6. Words

- **(a) One-parent junction:** you already call it a "singleton" in the policy. That is one meaning with two words; keep one. I suggest **offshoot**, which the glossary does not use, and dropping "singleton".
- **(b)** **Surplus distinctions** is fine; the glossary does not use "surplus".
- **(c)** **Demand** is unused and better than "asked count". Define it as the number of joins of the next round that take a distinction from the junction.
- **(d)** **Descent order** for the poset, and **breadth** for its width. Avoid "width" (the glossary uses it for resolution width) and "thread" for chains of offshoots (taken: a system joined in one line). "Spread" appears once in the glossary; check its sense before using it.
- Do not call breadth the dimension: by the ladder example the growth exponent can be smaller.