# Why a planar side cannot create, in part

Status: Proved (items 1–4; item 5 stays open)

Ticket `HANDLE-EMERGENCE-20261102-001C`, 2026-11-02.

## Question

- **From tickets A and B.** Planar removed sides never create (finitely, beyond the census), and handles create through three-point
  knots that use all three ports at once.
- **The question.** What is it about a plane space that prevents this?

## Dependencies

- **`HANDLE-EMERGENCE-20261102-001A`.** The planar spaces (`planar_lib.py`).
- **`HANDLE-EMERGENCE-20261102-001B`.** The shape of new knots.

## Setting

- **Spaces.** H is a connected knot space with n points and n lines. Each line L carries signs s on its three incidences, and Γ is its
  incidence graph.
- **Removal.** M is a removed line, and Γ − M is the incidence graph without M.
- **Odd point.** For a solution x and a line L, the signed values x_p ⊕ s_{L,p} are not all equal. So exactly one point of L differs
  from the other two: L's odd point o(L).

## 1. The odd-point model (proved)

**Solutions of H − M, up to complement, correspond one to one with choices of one incidence (L, o(L)) per line L ≠ M whose number on
every cycle C of Γ − M has the parity s(C) of C's signs.**

*Proof.*
- **The basic identity.** For two points p, q of a line L,
  x_p ⊕ x_q = s_{L,p} ⊕ s_{L,q} ⊕ [o(L) ∈ {p, q}]   (∗)
  The two signed values differ exactly when one of p, q is the odd point.
- **Forward.** Summing (∗) around a cycle C gives |F ∩ C| ≡ s(C), where F is the set of chosen incidences.
- **Backward.** Given such an F, define x along a spanning tree of Γ − M from a root value.
  - **Consistency.** Every other step of (∗) closes a cycle, so the parity condition makes the definition consistent.
  - **Each line.** With (∗) holding on every line, L's signed values have odd point o(L), so x solves H − M.
- **Two roots.** The two root values give x and its complement. ∎

## 2. The skip model on plane knot spaces (proved)

- **Corners.** Embed Γ in the plane. Each line has three corners, one between each pair of consecutive incidences, and each face is a
  cyclic sequence of corners.
- **Skipping.** A line skips the corner opposite its odd point, that is, the corner between its two other incidences.
- **The face condition.** The signs satisfy Kasteleyn's face condition: a face of length 2k carries a number of negative incidences
  congruent to k + 1 mod 2.

**Lemma.**
- **The parity on one face.** On a face f with k lines, F satisfies the cycle parity on ∂f iff f holds an odd number of skipped
  corners.
- **Why.** A line on f has its selected incidence on ∂f iff it does not skip its corner in f. So |F ∩ ∂f| = k − c(f), where c(f) counts
  the skipped corners in f, and k − c(f) ≡ k + 1 iff c(f) is odd.

**Theorem.**
- **(a) The knot fails on H.**
  - **Reduction.** Face boundaries generate the cycle space of a plane graph, so a solution would need c(f) odd, hence at least 1,
    on every face.
  - **Counting.** Euler's formula for Γ (2n vertices, 3n edges) gives n + 2 faces. That needs at least n + 2 skipped corners, but each
    line skips exactly one, so there are only n.
- **(b) The solutions after a removal are perfect matchings.** After M is removed, the solutions up to complement are exactly the
  assignments in which every line L ≠ M skips one corner and every face of Γ holds exactly one skipped corner, counting M's three
  corners as skipped. When each line's three corners lie in three faces (as in all spaces checked), these are the perfect matchings of
  the lines L ≠ M to the faces not touching M, each line to one of its own faces.

*Proof of (b).*
- **The faces of Γ − M.** They are the faces of Γ away from M, which need odd counts, and one face merged from M's corner faces. The
  merged face needs an even number of corners skipped by the other lines: summing its boundary's signs gives Σ (k_i + 1) over M's
  three faces, against Σ k_i − 3 lines.
- **Counting.** The other lines skip n − 1 corners in all. The faces away from M need at least one each, and they number n + 2 − 3
  when M's corners lie in three faces (fewer faces would make H − M unsatisfiable, but knot spaces fail globally, so every removal has
  solutions). So each face away from M gets exactly one skipped corner, and M's faces get none from other lines.
- **The converse.** Such an assignment meets every face condition of Γ − M, and part 1 turns it into a solution. ∎

## 3. Interfaces (proved)

- **The odd points.** After M is removed, a line L's possible odd points are exactly the incidences opposite its faces that some
  perfect matching assigns to L.
- **Meeting M.** If L meets M at a point p, the face containing the corner L–p–M holds a corner of L and a corner of M. So it is an
  M-face, and L can never skip there.
- **Consequence.** The incidence of L opposite that face is never odd, the other two points of L are tied, and the interface on L has
  at most four patterns (two if L shares two faces with M).
- **Six patterns** need L to share no face with M.
- **Why planar sides never offer the Fano plane's mechanism.** In the Fano plane every removed line meets the closing line, and ticket B
  found that its creation pins the pair whose odd port lies on M. On a plane side a removed line that meets the closing line shares a
  face with it and leaves at most four patterns, while ticket A found that four-pattern interfaces never create.

## 4. A handle leaves slack (proved count; computed example)

- **The count on a surface.** For a cellular embedding on an orientable surface of genus g, Euler's formula gives n + 2 − 2g faces.
  The cycle space is spanned by face boundaries and 2g further cycles.
- **What a solution needs.** With face-condition signs, every face must hold an odd number of skipped corners, and 2g homology parities
  must hold.
- **Consequence.** For g ≥ 1 counting no longer forces failure.
- **The Fano plane on the torus.**
  - **The embeddings.** All 16 of its torus embeddings (rotation systems with 7 faces) consist of 7 hexagons, and on each the knot's
    signs satisfy the face condition. So 7 lines meet 7 faces.
  - **After a removal.** The 9 skipped corners cover the 7 faces oddly only with one face holding three. 14 assignments do this, and
    only 5 of them (times 2 for the complement) are solutions: the two homology parities, absent on a plane space, select them.

## 5. Open

- **What remains.** A planar removed side never creates (ticket A, finitely).
- **The reduction.**
  - **The near side.** By part 2 its solutions are perfect matchings of lines to faces. The closing line's matched face picks the
    interface pair (part 3).
  - **The pinning.** Ticket B's pinning asks that one near relative value force that face. What remains is to show that such forcing
    always passes through a single port class in a plane matching structure.
- **The handle counterpart.** On a handle, parts 4 and B suggest that the face slack and the homology parities are what let the hub
  and one near point fix all three ports at once.

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Odd-point model on every census space and removal | 56 of 56 |
| 2 | Skip model on 17 plane knot spaces; census signings | every removal; 488 of 488 signings satisfy the face condition |
| 3 | Interfaces | 1494 of 1494 pairs as predicted; 722 meeting pairs, all with a shared face and at most four patterns |
| 4 | The Fano plane on the torus | 16 embeddings, 7 hexagons, face condition; 14 face-odd assignments, 5 solutions per removal |

## Novelty and provenance

- **Classical.**
  - Kasteleyn's face condition (plane Pfaffian orientations).
  - Moret's theorem that planar not-all-equal 3-SAT is polynomial, by reduction to planar maximum cut ([Moret 1988, SIGACT News
    19(2):51–54](https://en.wikipedia.org/wiki/Not-all-equal_3-satisfiability)). It works from the same planar duality.
- **New here, as stated.**
  - The skip model: failure by counting, solutions as perfect matchings of lines to faces, interfaces read off matched faces.
  - Its genus count.

  A bounded search found no statement of them, so folklore risk is moderate.
