# End to end: formulas counted through certified Pfaffian instances

Status: Proved (finite check)

Ticket `SOFT-CROSS-20261031-001C`, 2026-10-31.

**What it uses:**
- **`SOFT-CROSS-20261031-001B`:** the graphs G_k (Theorem 3) and the composition (Theorem 4).
- **`SOFT-CROSS-20261031-001A`:** snakes, the compensated crossover and the Pfaffian certificate (Lemma 2, Theorem 5, Corollary 6).
- **`TWIST-COUNT-20261030-001A`:** twisted branches and good roots (Lemma 5).

## Why this ticket exists

Ticket B's plan promised an end-to-end demonstration on a small instance, but its artifact proved the composition only as a theorem. That
gap is recorded there as a nonclaim. This ticket runs the whole chain on two formulas:

formula → G_k → Pfaffian instances → counts → #formula.

## Standard statement

**Setting.**
- **The formulas.** Two positive NAE-3SAT formulas: (a, a, b), with 2 solutions, and (b, a, c)(c, b, c), with 4. Their graphs G_k (ticket B)
  are non-planar for every k checked.
- **The drawing.** Each G_k has a drawing with one crossing, between a clause incidence e₁ and the first edge e₂ of a merge path:
  - removing e₁ leaves a planar graph;
  - in its embedding, a face at each end of e₁ contains e₂, and e₂ has no end in common with e₁.
- **The instances.** The crossing is replaced by a k_S-snake, as in `cross_lib.k33_instance`: e₁ is wire B, e₂ wire A, and k_S = 1, 3, 5, 7.

**Result (finite check).** For each formula and each of D + 1 values of k (k = 2, …, D + 2):
- each of the four instances is certified Pfaffian: its pieces are planar and the glued Kasteleyn signing is non-colourable;
- each is itself non-planar;
- each has three twisted branches at every junction, and no good root;
- solving ticket A's 4 × 4 system and applying the compensated crossover gives 9·#col(G_k), equal to the direct count.

Ticket B's interpolation over k then returns #formula = 2 and 4 exactly. In all there are 44 instances, the largest of 922 vertices, with
176 junctions.

## Proof

**By computation** (`check.py`, about 5 seconds).
- **Section 1** checks the drawings.
- **Section 2** checks the certificates, non-planarity and twisted branches.
- **Section 3** runs the recovery end to end.
- **Section 4 is a control.** Without the compensation, the bare exact crossover replaces the snakes. The recovery then returns wrong values
  at every k: the inserted line on wire A acts by 3M, and only w = [[−1, 2], [2, −1]] undoes it. ∎

## Reading

- **Theorem 4 is a working reduction, not only a composition on paper.** A formula's count is read off counts on graphs that are Pfaffian,
  where perfect matchings count in polynomial time.
  - On these graphs the knot's own sign class counts in polynomial time.
  - The signs that carry the formula are twisted at every junction, three branches deep.

## Nonclaims

- **Two formulas, one crossing.** The general construction (many crossings, long edges, the two-parameter system of A's Theorem 5) is not
  run here. These are finite checks of the composition, and add no general claim.
- **The drawings were found by search.** Formulas whose graphs have a one-crossing drawing were selected for this check.
