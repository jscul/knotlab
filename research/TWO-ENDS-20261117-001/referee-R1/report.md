# Referee report TWO-ENDS-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - Lemma S, Theorem D, Lemma R and Theorem G are proofs, and they are correct as written.
  - The owner's points (b) and (c) are fine:
    - (b) Theorem D's window needs no special orbit, which is exactly its hypothesis.
    - (c) Theorem G's factorisation across several disjoint product crossings is right.
  - The certified reading recomputes: both bonds of 7 at depth 12 are bonds of P₁₂ by direct SAT.
  - The product test equals forgetting on every census description.
- **What changes.**
  - **Theorem N's step 3 has a gap,** at the owner's point (a). Two branch points joined by a short edge can each be "near" only the
    other, and the written induction then gives no bound. The repair is direct: move such a cluster as one unit. Until it is
    written, N is proved for anchor trees without that configuration. **Narrowing.**
  - **"C\* holds" is a three-end statement.** C\* as stated, with two ends, stays open, as the note says. The summaries should say "a
    three-end form of C\*". **Narrowing, wording.**
  - **"Decidable in principle" is a sketch.** The proof note says so; the answer and the goals line state it as a result.
    **Narrowing, wording.**
  - **The counts are counts of descriptions.**
    - "Exactly the 740 that forget, none of the 46" is 139 and 42 distinct patterns.
    - "The 25 open" are 10.
    - "−79 reads exactly 7" is the pattern of −73 and −79, which are one.

    The thread is already correcting this in its working copy, uncommitted. **Narrowing.**
  - **The carried mode carries more than an all-equal strand.** By SAT at depth 11 on −73, the one non-product joint at each
    distance from 4 to 7 has two parts. One is the all-equal link, alternating with each step. The other: the lower orbit's split
    assignments 0011 and 1100 force the upper orbit to be split the same way. **Narrowing.**

## What holds

- **Lemma S (proved).**
  - The states reached in exactly ℓ steps from a fixed start evolve by a fixed map on a finite set, so they repeat.
  - The lengths of paths from a state p to a state q are therefore ultimately periodic, and finitely many starts give a uniform T
    and Q.
- **The factorisation and moves (proved).**
  - The projection onto B is read from S, the ancestor closure of B's orbits. The other children are quantified into F at their
    remaining depth.
  - A move replaces a segment, whose interior holds no member and no branch point, by another path from the same child with the
    same end type and composite.
  - It changes nothing in the projection while no orbit at which F is read changes tier.
  - Disjointness holds because the new path stays under the same child, which holds only that segment's part of S.
- **Theorem D (proved; the owner's point (b)).**
  - **The crossings.** Every orbit of S in a window of W saturated levels with no special orbit has a member below it. It is neither
    a member nor a branch point, so it has exactly one child in S. So it runs through the window, and the crossings are disjoint.
  - **Lengthening.** Each crossing lies in a segment longer than T, so it can be lengthened by Q. Doing so moves everything below,
    v included, down by Q while N grows by Q, so every tier below is kept. That gives f(s + Q) ≤ f(s) on the same tier r.
  - **Without a window.** The special orbits, at most 2|B| − 3 of them, meet every run of W of the n(s) saturated levels.
  - **The dichotomy.** Once f falls below the bound it stays below, so f is non-increasing along the residue.
  - **Assumption (b).** "No special orbit in the window" is the hypothesis itself, branch points included. Nothing more is needed.
- **Lemma R (proved).**
  - Below level k + s there are r − R saturated levels and at most 2c − 1 special orbits, so a window exists.
  - Lengthening it moves only what lies below the window. That includes the case where no orbit of S crosses it: then only N
    grows, and every orbit of S stays saturated.
- **Theorem G (proved; the owner's point (c)).** With every ℓ₀-step composite a product, each crossing's condition splits into a
  condition on its top (a condition on the part above) and one on its bottom (on its own subtree). So the allowed states factor as
  (above) × Π (below_i), however many crossings there are. Then B's projection is the product of its projections onto its parts
  above and below, which are proper subsets and so free. So B is free.
- **The certified reading (P1)** (`referee_two_ends.py`, item 1).
  - Both bonds of 7 are bonds of P₁₂ by the referee's direct SAT on the whole pattern: constrained, with every subset of six free.
    They are [11, 14, 17, 71, 119, 196, 1919] at s = 7 (levels 3, 3, 4, 6, 6, 7, 10) and [11, 14, 48, 143, 351, 393, 3839] at s = 8
    (levels 3, 3, 5, 7, 8, 8, 11).
  - With CARRIER's certified "> 6" at depth 12, L₁₂(3, 7) = L₁₂(3, 8) = 7.
  - They are bonds of −73's pattern as well, the same clause set.
- **The product test against forgetting** (item 2). On all 786 census descriptions, the test holds exactly where forgetting holds.
  No group of identical descriptions has mixed verdicts. P5's ℓ₀ ≤ r + 1 holds on all 740.

## 1. Theorem N's step 3 (the owner's point (a); Narrowing)

**What the step does.** Branch points of the anchor tree A are taken from the top down. A branch point b whose upper edge holds a
long segment moves up when every edge below it holds a segment of length at least T, by shortening above and lengthening each edge
below. Otherwise some edge below b has every segment shorter than T, "so b lies within 2c·T blocks of that edge's lower node".

**The gap.** The conclusion says: "By induction from the bottom of A, each branch point ends within 2c(T + Q) blocks of an anchor, or
of a node one edge nearer the top." That does not cover the following configuration:
- b has a long edge above it, a short edge (every segment shorter than T) to a branch point b′, and a long edge to an anchor x;
- b′ has long edges to anchors y and z.

Then:
- b is not moved, since its edge to b′ is short. It is "near" b′, a node one edge farther from the top.
- b′ is not moved either, since its upper edge, the one from b, holds no long segment. So it is "near" b.
- Each is near only the other, and both can sit arbitrarily far from every anchor.
- The members on the long edges next to them are then not within K blocks of any anchor.

Nothing in the setting rules this configuration out: three anchors below a pair of close branch points.

**The repair.** Treat a cluster as one unit: a maximal set of branch points joined by edges whose segments are all shorter than T.
- If every edge leaving the cluster downward holds a segment of length at least T, shorten the edge above the cluster by a multiple
  of Q and lengthen one such segment on each downward edge by the same amount. Every anchor keeps its level, and the cluster moves
  up.
- Otherwise a downward edge from the cluster is short, and its lower node joins the cluster.

A cluster has at most c − 1 branch points and diameter below 2c²T. So every node ends within a bound polynomial in c, T and Q of an
anchor. That bound is larger than the stated K = 4c²(T + Q) + k + R, which needs recomputing.

**What it means.** The theorem looks true, and the repair is in the spirit of the advisor's third repair. But as written, step 3
does not prove the stated bound. "Proved by hand" should read "proved, with step 3 for clusters added", once the cluster version is
written. Nothing computed rests on K.

## 2. What is claimed for C\* and decidability (the coordinator's question; Narrowing, wording)

- **"C\* holds."**
  - Theorem N with Theorem K\* gives a three-end form: bounded reach exactly when a bond inside bounded pieces near the top, near the
    lower member and near a bounded number of bottom-band orbits exists at every s and depth.
  - C\* as stated, with two ends, is not shown, and the note says so ("two ends may not suffice").
  - Two summaries drop the qualifier: the intuition entry ("so the conjecture holds with three ends") and the goals line ("So C\*
    holds with three ends").
  - **A fair line:** "a three-end form of C\* holds (Theorem N, once its step 3 is completed); C\* with two ends is open".
- **The 13 being open** does not bear on C\*'s truth. C\* is an equivalence, and it does not decide their boundedness.
- **"Decidable in principle."** The corollary is labelled a proof sketch in the proof note, and that is right: the reduction to
  finitely many cluster types, residues and tiers is outlined, not carried out. But the answer ("Decidable in principle. For each
  c, ... is decidable") and the goals line state it as a result. Say "decidable in principle (proof sketch)".

## 3. Counts (Narrowing)

As found in `CARRIER-R1`, descriptions are not patterns. In distinct clause sets (item 2):

| Count | Descriptions | Distinct patterns |
| --- | --- | --- |
| the census alive at every depth with small orbits | 786 | 181 |
| that forget, and pass the product test | 740 | 139 |
| that do not forget, and fail it | 46 | 42 |
| KEEP-REACH's open | 25 | 10 |
| −73 and −79 | 2 | 1 |

The thread's working copy is already correcting the proof note's counts. That correction is uncommitted, and this report refers to
the committed version. The note, the intuition entry and the goals line still need it.

## 4. The carried mode (Narrowing)

The note says that across a long stretch the 13 carry "one thing, an orbit frozen all equal down a self-similar strand". The
referee checked this by SAT on P₁₁ of −73 (item 3). It took every orbit O at level 4 and every orbit O′ 4 to 7 levels below it
inside its subtree, 960 joints in all.
- **One line carries anything.** At every distance exactly one joint is not a product: the line down from O = [3, 7, 9, 15], the
  self-similar strand. The other 959 are products. That agrees with "2 of 43 periodic states are not products" (one per parity).
- **That joint has two parts.** At distances 5, 6 and 7 it misses 54 of the 256 pairs:
  - **30 are the all-equal link the note describes.** O all equal forces O′ all equal and the reverse, with the value alternating at
    odd distance.
  - **24 have no all-equal end.** When O′ is split, 0011 or 1100 (its first two addresses equal, its last two equal, the two
    halves different), O must be split the same way. All 12 other values of O that are not all equal are excluded.

  The split part is one-directional: a split O leaves O′ free.
- **What it means for the next step.** A bond across the stretch could use either part. The selected direction searches for "the
  least set near the top whose assignment forces an orbit of the self-similar type all equal". It should also search for sets
  that make the lower orbit split while forbidding the upper one's split, or the reverse use. "The only thing carried is an
  all-equal strand" should read "an all-equal link and a split link along one self-similar strand".

## 5. Smaller points (Not a block)

- **P2.** It is undecided at depth 13, as reported.
- **P6.** It was tested only on −73, as reported.
- **"Nothing grows slowly".** Theorem D is per depth tier and residue: for fixed r and s → ∞ along a residue. The headline "nothing
  grows between bounded and linear" should keep that scope. "Reach" bounded over all (s, N) also involves N → ∞ at fixed s, which
  Lemma R addresses separately.

## Fixes for the thread (listed for the owner, not folded in)

1. **Theorem N.** Add the cluster case to step 3 and recompute K, or mark N as proved up to that case. **Narrowing.**
2. **Wording.**
   - "A three-end form of C\* holds" in place of "C\* holds", in the intuition entry and the goals line.
   - "Decidable in principle (proof sketch)" in the answer and the goals line.

   **Narrowing.**
3. **Counts.** Use distinct patterns: 139 and 42 of 181; 10 open; −73 and −79 one pattern. Commit the thread's working-copy fix and
   carry it to the note, the intuition entry and the goals line. **Narrowing.**
4. **The carried mode.** Describe the non-product composite with both its parts, the all-equal link and the split link, and add
   the split channel to direction 1's search. **Narrowing.**

## How the work was split

- **The referee:**
  - read the note, the predictions, the proof, `composite.py`'s outputs and the certified readings;
  - checked Lemma S, Theorems N, D and G, Lemma R and the corollary by hand;
  - wrote direct SAT checks of the certified bonds, the census counts by distinct pattern and the carried mode
    (`referee_two_ends.py`), reusing its own SAT tools from `CARRIER-R1`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_two_ends.py` and `.json`:**
  - 1, the bonds of 7;
  - 2, the product test by distinct pattern;
  - 3, the carried mode by SAT at depth 11.

Reproduce, from `research/TWO-ENDS-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_two_ends.py > referee_two_ends.json
```
