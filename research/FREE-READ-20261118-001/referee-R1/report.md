# Referee report FREE-READ-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The tree theorem holds.** Bond distance is steps apart plus one on every knot tree of parity, not-all-equal and betweenness
  knots, in any mixture.
  - **The proofs check by hand.** That covers U, Lo with L0 to L2, C and M.
  - **The referee's own code reproduces it** on 3,360 trees and 222,768 pairs, with none off. That includes every five-knot tree
    under every assignment of the three laws (1,876 bases with betweenness, each middle placed at random), every six-knot tree
    under parity and not-all-equal, and 200 random seven-knot trees.
- **The owner's three points.**
  - **(1) The splitting lemma is right** (§1).
  - **(2) The post hoc claims hold, with one wording fix.**
    - Bond distance is flat on split grids. But "every three distinctions form a knot" holds only on the line: on the 3 × 3 grid,
      16 of 84 triples are free.
    - The hub set is free, so freedom gating keeps the shortcut.
    - δ_KB misreads the cross-parity pairs, by up to 5 where steps apart is 2.
  - **(3) The triangle inequality.** For bond distance it holds on 400 random bases that are not trees (62,154 triples), on 16
    rings, and, proved here, on every parity base. For bond distance minus one, the quantity compared with steps apart, it fails on
    48 of the 400 random bases, wherever two distinctions form a bond of two.

## What holds

- **L0 to L2.**
  - **L1's step.** In a tree incidence, each added knot meets the knots already placed in exactly one distinction; a second one
    would close a cycle. L0 then completes its two new distinctions.
  - **L2.** It is L1 applied to the path's knots, which form a connected set.
- **U (the upper bound).**
  - **S is constrained.** With S = {x, y, p₁, …, p_k}, choose each p_j to match the knot's forbidden pattern relative to v_(j−1).
    Then every v_j is forced: a not-all-equal or betweenness knot forbids a pattern and its complement, and a parity knot forces
    v_j outright. So y is forced, and the joint value with y flipped is missing.
  - **A mixture needs no global switching.** The proof's phrase "betweenness is a switch of not-all-equal" is true. But a
    distinction can be a middle in one knot and an end in another, so one switch may not serve all the knots at once. The forcing
    step works knot by knot, for each of the six laws (parity of either constant, and the four "forbid a pattern and its complement"
    knots), so the mixture holds directly.
  - **Every k + 1 of S is free.** That is by L0, choosing forward and backward along the path, and L2.
- **C (the clause "not all ones").** With every distinction outside S set to 0, S is constrained exactly when it contains a whole
  clause. A bond is then a single clause, so no bond holds the ends of a chain of two or more. The study's computation agrees (P6).
- **M (the mixed cycle).** {x, y, z} is constrained, since x + y + z is fixed. Its pairs are free: x and y are the path's ends,
  and z is determined by them.
  - The referee computed bond distance − 1 = steps apart on all 154 pairs of the four mixed cycles (`referee_free_cycles.json`).
  - δ_K differs from steps apart on 52 of them, as the note says. On 20 of those 52 the gap is more than 0.11.
- **Parity bases.** Free means no dual codeword inside, so the bonds are the circuits. This is the same fact as CUMULANT-DIST D1,
  with the hypothesis fixed in the referee's report there.

## 1. The lower-bound splitting lemma (the owner's point 1; holds)

- **The setting.** Let S be a bond holding x and y that misses the third branch T_j, so p_j ∉ S. Removing K_j splits the
  distinctions into L_j ∋ x, R_j ∋ y and T_j ∋ p_j, so S ⊆ L_j ∪ R_j.
- **The projection is a product.** Every allowed state of the knots inside L_j, a connected subtree, can be joined to every
  allowed state of those inside R_j:
  - L0 gives p_j for the pair (v_(j−1), v_j);
  - L1 extends the result through T_j's knots;
  - conversely, any allowed state of the base restricts to allowed states on each side.

  So the projection onto L_j ∪ R_j is the product of the two sides' projections, and so is the projection onto S.
- **The contradiction.** S is constrained, so one factor is not full. That factor is a proper subset of S, since x ∈ L_j and
  y ∈ R_j, and it is constrained, against K2.
- **The count.** The k third branches are pairwise disjoint and avoid x and y, so |S| ≥ k + 2.
- **What the proof should say.** The lemma needs only L0 (each knot passes K2) and the tree. The proof should name the two places
  it uses connectedness: the knots inside L_j and inside R_j form subtrees, and L1 needs a connected starting set.
- **Known.** This is the lossless join of an acyclic scheme (Beeri, Fagin, Maier and Yannakakis), rightly cited.

## 2. The post hoc claims (the owner's point 2)

- **Split grids** (`referee_free_grids.json`).
  - **Bond distance is 2 for every pair** of the split line of six, the 3 × 3 grid and the 3 × 4 grid. So it is flat, as claimed.
  - **"Every three distinctions form a knot" holds on the line only** (0 of 20 triples free).
    - On the 3 × 3 grid, 16 of 84 triples are free. An example is (0,0), (0,2), (1,1): each of the three can be cut away from the
      other two.
    - On the 3 × 4 grid, 52 of 220 are free.
  - **Why it is still flat.** Every pair has some third distinction between them, on a shortest path or beyond an end, that no cut
    isolates. That triple is a bond.
  - **Fix:** "every pair lies in a bond of three", not "every three distinctions form a knot". **Not a block.**
- **Freedom gating keeps the hub** (`referee_free_hub.json`).
  - The hub set {x, y, one child of each of N not-all-equal knots hung on x} is free for N = 1 to 8, computed. It is free for every
    N, because given x each other member takes both values, independently, by the tree process.
  - So all its proper subsets are free, δ_F admits it, and TREE-STEPS H1 and H2 give the shortcut at 32 copies.
  - The note's "argued, not computed at 32 copies" is fair. The argument is complete: freedom does not depend on N, and the
    cumulant identity is exact.
- **δ_KB on the mixed cycles** (`referee_free_cycles.json`). min(δ_K, the cumulant reading over bonds) is off steps apart by more
  than 0.11 on 0, 2, 5 and 9 pairs at k = 2, 3, 4 and 5.
  - The worst is the pair (0, 9) at k = 5, with steps apart 2 and δ_KB = δ_K = 5. The bond-cumulant reading is 6.36 there.
  - This confirms the note's example ("5 where steps apart is 2").

## 3. The triangle inequality (the owner's point 3)

- **Bond distance (the least bond's size minus one), on the referee's tests** (`referee_free_triangle.json`):
  - 0 violations on 62,154 triples of 400 random connected bases that are not trees (6 to 8 distinctions, 3 to 7 knots of mixed
    parity, not-all-equal and betweenness);
  - 0 on every ring of three to six knots under parity, not-all-equal, betweenness and alternating laws.
- **Proved for parity bases.**
  - **The setup.** Let x, y lie on a least circuit C₁ and y, z on a least circuit C₂.
  - **A circuit through x and z exists inside C₁ ∪ C₂.** Two circuits sharing an element have a connected union: connectivity is
    an equivalence, and its transitivity is proved inside the union.
  - **The bound.** b(x, z) + 1 ≤ |C₁ ∪ C₂| ≤ |C₁| + |C₂| − 1, so b(x, z) ≤ b(x, y) + b(y, z).
  - This settles the parity case of the note's direction 2.
  - On knot trees the inequality is immediate from the theorem.
- **Bond distance minus one is not a metric in general.** It fails on 604 triples of 48 of the 400 random bases.
  - Every failure involves a bond of two (b = 1): two distinctions tied by the knots around them, so that b − 1 = 0 between
    distinct distinctions. Of the 604, 600 have the shape (b(x, z), b(x, y), b(y, z)) = (2, 1, 1) and 4 have (3, 2, 1).
  - An example on six distinctions: b(0, 1) = b(1, 2) = 1 and b(0, 2) = 2.
  - The study compares δ, δ_K and τ with b − 1, which equals steps apart on trees. So the triangle inequality should be claimed for
    b, not for b − 1, off trees.

## 4. Smaller points (Not a block)

- **The study's own Narrowing 01941028d is right.** "Bond distance gives not-all-equal trees nothing" was false: it is steps apart
  plus one there, as the referee computed on every pure not-all-equal tree in range.
  - The referee's CUMULANT-DIST report did not catch that sentence. It is noted here.
- **Known results.** These are rightly cited: bonds are minimal non-shattered sets (Sauer–Shelah, Pajor), acyclic joins, and
  circuits.
  - The tree statement is a short consequence of acyclic losslessness, plus a forcing argument for the upper bound.
  - The advisor knew no published statement, and no search was run. Calling it "the program's" is fair if it is labelled as
    likely folklore-level.
- **The headline is fair.** "The distance that reads freedom is bond distance itself", proved on trees, flat on split grids.

## Fixes for the thread (listed for the owner, not folded in)

1. **Split grids.** Write "every pair lies in a bond of three", not "every three distinctions form a knot". On the 3 × 3 grid,
   16 of 84 triples are free. **Not a block.**
2. **The triangle inequality.** Claim it for bond distance, which held on 400 random non-tree bases and 16 rings and is proved here
   for parity bases. It fails for bond distance minus one wherever bonds of two exist (48 of 400 random bases). **Not a block.**
3. **U's mixture.** Say that the forcing works knot by knot for each of the six laws, rather than "a switch of not-all-equal",
   since one switch may not serve two knots that share a distinction. **Not a block.**
4. **Lo.** Name the connectedness that L1 uses: the knots inside L_j and R_j form subtrees. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, and `freelib.py`, `job.py` and `posthoc.py`;
  - checked U, Lo, L0 to L2, C and M by hand, and proved the parity triangle inequality;
  - wrote `referee_free.py` (own freedom and bond search; trees under all three laws; split grids; mixed cycles with δ_K and δ_KB;
    random non-tree bases for the triangle inequality; the hub set's freedom) on its CUMULANT-DIST-R1 and TREE-STEPS-R1 code.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_free.py`.**
- **`referee_free_trees.json`, `_grids.json`, `_cycles.json`, `_triangle.json` and `_hub.json`.**

Reproduce, from `research/FREE-READ-20261118-001/referee-R1/`:

```sh
for p in trees grids cycles triangle hub; do ../../../.venv/bin/python -B referee_free.py $p > referee_free_$p.json; done
```
