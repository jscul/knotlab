# Two kinds of interface: parity across 2-edge cuts, knot against hub across 3-edge cuts

Status: Proved

Ticket `NATIVE-PATHS-20261101-001A`, 2026-11-01.

## Question

- **What is already known.** `KNOT-COMPOSE-20261101-001A` classified the nontrivial 3-edge cuts of a knot's space. Its Theorem 4
  states that across each such cut the line side accepts exactly not-all-equal and the point side exactly equality, and that the knot's
  spaces therefore compose only through hubs (equality fan-outs). Its complementarity lemma says that two sides which both accept knots
  can fail together only as complementary parity cosets.
- **The question here.** This is the first check of the native-paths epic. Before asking whether a path through hubs is fixed by the law,
  we ask which interfaces the law itself presents. KNOT-COMPOSE did not consider cuts of two edges that separate the space.

## Dependencies

- **`THREEFOLD-SPACES-20261030-001A`.**
  - Theorem 1(b): a connected non-2-colourable cubic system is minimally so.
  - The library: Fano, splices, the colourability test.
- **`THREEFOLD-SPACES-20261030-001C`.** The odd cycles of Fano blocks (`cycles_lib`).
- **`KNOT-COUPLING-20261031-001A`.** The atom lemma: cutting one incidence of a knot's space leaves a system that accepts exactly the
  disequality (port colour, slot value) ∈ {(0,1), (1,0)}.
- **`KNOT-COMPOSE-20261101-001A`.** The setting (balance, failure across a cut). Its Theorem 4(1) and 4(3) are corrected here.
- **`THREEFOLD-GRAMMAR-20261030-001A`.** Its library (`decorate`, `kasteleyn_signing`) builds the twisted cube. It is used only as a
  constructor; check 1 verifies directly that the result is a knot's space.

## Setting

- **Systems.**
  - A cubic system H has lines of three points, and every point lies on three lines. B(H) is its incidence graph.
  - The knot's law is not-all-equal on every line. A *knot's space* is a connected cubic system on which it fails.
- **Cuts.**
  - A *nontrivial k-edge cut* is a set of k edges of B(H) whose removal leaves exactly two components X and X̄, each with more than one
    vertex, with every removed edge joining them.
  - The removed edges are the *channels*. Each joins a point (a *port*, on one shore) to a line (a *slot*, on the other).
- **Accepted relations.**
  - The value of a channel is the colour of its port. The slot's line reads that value in place of its missing point.
  - R_X ⊆ {0,1}^k is the set of channel values for which X's points can be coloured so that every line of X is proper.
  - H is colourable iff R_X ∩ R_X̄ ≠ ∅ (KNOT-COMPOSE Lemma 2).
- **Hubs.** A side *acts as a hub* when it accepts equality on three or more channels: from outside, it is one distinction shared by
  three relations, an equality fan-out. A two-place equality is a wire: it shares one distinction between two relations and fans out
  nothing.

## Theorem

Let H be a knot's space and ∂(X) a nontrivial k-edge cut.

1. **Balance.**
   - If k = 2, each shore has as many points as lines, one port and one slot.
   - If k = 3, one shore, the *point side*, has one more point than lines and holds all three ports. The other, the *line side*, holds
     all three slots.
2. **Two edges: parity, no hub.** One shore accepts exactly equality {00, 11} on the two channels and the other exactly disequality
   {01, 10}. Cutting either channel alone leaves an exact negation. So the shores meet as complementary two-place parity, and neither
   acts as a hub.
3. **Three edges: knot against hub, up to signs.**
   - The point side accepts exactly one antipodal pair {v, v̄} ⊂ {0,1}³.
   - The line side accepts exactly the six other assignments.
   - Reading the channels where v is 1 with their colours exchanged turns these into equality (a hub) and not-all-equal (the knot).

**Corollary (correction of KNOT-COMPOSE-20261101-001A).**
- **Theorem 4(3) fails.** "The knot's spaces compose only through hubs" is false wherever a knot's space has a nontrivial 2-edge cut.
  Odd cycles of Fano blocks, the twisted cube, and splices containing them all have such cuts.
- **Theorem 4(1) holds only up to signs.** "Exactly equality and exactly not-all-equal" is true up to the exchange of colours in item 3.
  The point lemma it cites applies to the piece H_X(τ) for a sign pattern τ, which need not be 000. Its proof read the ports as constant
  "as seen from z" without τ. Its check 3 (5/5) tested only splice trees, where v = 000.
- **What stands.**
  - The second sentence of Theorem 4(3), that a failing hub-free composition is a parity composition. 2-edge cuts realize it at k = 2.
  - Theorem 4(2), on double cuts, and 4(4), the transpose.

## Proof

**Item 1 (balance).**
- Shore X has p points and l lines, with i incidences inside X. Let a and b count the channels at X's points and at X's lines. Then 3p =
  i + a and 3l = i + b, so 3(p − l) = a − b, with a + b = k.
- For k = 2, a − b ∈ {2, 0, −2} and divisibility by 3 force a = b = 1 and p = l.
- For k = 3, a − b ∈ {±1, ±3} forces a − b = ±3.

**Four facts about the side relations.** These hold for any nontrivial cut of a knot's space.
- **(a) Disjoint.** H is not colourable.
- **(b) Closed under complement.** Exchanging every colour preserves not-all-equal.
- **(c) Non-empty.**
  - H is minimally non-colourable (THREEFOLD-SPACES A, Theorem 1(b)).
  - So for a line L of X̄, H − L has a colouring. Its restriction to X shows R_X ≠ ∅. The same argument applies to X̄.
- **(d) The atom condition.** For every channel e and each value c of its port, some w ∈ R_X and w′ ∈ R_X̄ differ exactly at e, with the
  port's value c.
  - Cutting e alone leaves an exact negation (atom lemma). So H with e cut has a solution in which e's port has colour c and e's slot
    reads c̄.
  - On e's port side the channel values are some w. On the other side they are w with e's value exchanged.

**Item 2.**
- The complement-closed subsets of {0,1}² are ∅, {00, 11}, {01, 10} and {0,1}².
- By (a)–(c), R_X and R_X̄ are non-empty, disjoint and complement-closed. So one is {00, 11} and the other {01, 10}.
- Cutting either channel then leaves the composite of an equality and a disequality, which is a negation. This agrees with the atom
  lemma.

**Item 3.**
- **Possible sizes.** By (a)–(c), R_X and R_X̄ are non-empty, disjoint unions of antipodal pairs, so their sizes lie in {2, 4, 6}.
- **No side has four states.**
  - A complement-closed set of four states is u ⊕ {000, 111, d, d̄} with d of weight one, say d = e_j.
  - Such a set is closed under exchanging channel j, so (d) fails at e_j.
  - Condition (d) is symmetric in the two sides, so this applies to both.
- **Not both two.**
  - If R_X = {v, v̄} and R_X̄ = {w, w̄}, then (d) needs {w, w̄} = {v ⊕ e_j, v̄ ⊕ e_j} for each j = 1, 2, 3.
  - These are three different pairs, so this is impossible.
- **So one side has two states and the other six.** The six must be the complement of the two, by (a).
- **The two-state side is the point side.** Suppose instead that the line side X̄ accepts only {u, ū}.
  - **The system B.** Join a new point z to the three slot lines ℓ₁, ℓ₂, ℓ₃ of X̄, with signs chosen so that z = c makes them read the
    channel values c ⊕ u ⊕ e₁.
  - **Properties of B.** B is a connected cubic signed system. It is not colourable, since c ⊕ u ⊕ e₁ ∉ {u, ū}.
  - **B is minimally non-colourable.**
    - Seymour's bound (a minimally non-colourable system has at least as many lines as points) holds for signed systems. His
      linear-algebra proof goes through with the signed incidence matrix M, whose entry for an incidence is (−1)^sign.
    - Suppose a minimally non-colourable signed system had more points than lines. Take a real x ≠ 0 with Mx = 0. Colour the points with
      x > 0 by 0 and those with x < 0 by 1. Colour the other points by a colouring of the lines that avoid the support of x; these form
      a proper subsystem, so the colouring exists by minimality.
    - A line meeting the support has signed terms of both signs, so it reads both values. This colours the system, a contradiction.
    - So a non-colourable subsystem of B, with point set V′ and line set E′, contains a minimal one with |E″| ≥ |V″|. In the cubic B,
      every set of lines covers at least as many points, with equality only for a union of components. So the subsystem is all of B,
      by connectivity, and B minus any line is colourable.
  - **The contradiction.**
    - B − ℓ₂ has a colouring, say with z = c. In it ℓ₂ is not proper (else B is colourable), so it reads three equal values.
    - Exchanging the value it reads at z's incidence makes ℓ₂ proper. The other lines are unchanged.
    - So X̄ accepts c ⊕ u ⊕ e₁ ⊕ e₂ ∉ {u, ū}, a contradiction.
    - This is the bijection in the proof of the point lemma (THREEFOLD-AMPLITUDE A, Lemma 3). If ℓ₂ = ℓ₁, the same exchange applies.
- **Conclusion.** So R_X = {v, v̄}, and R_X̄ is its complement.

**The reading.** Exchange the colour names on the channels where v is 1. Then {v, v̄} becomes {000, 111}, equality on three channels (a
hub). Its complement becomes not-all-equal, the knot. ∎

## Checks

`check.py` (`result.json`, about 70 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Ten knot's spaces: Fano; chains of 2, 3, 4; a star of 4; cycles of 3, 5, 7 Fano blocks; the twisted cube (43 points); the 3-cycle spliced into Fano. All connected, cubic, not 2-colourable. | pass |
| 2 | Balance at every nontrivial 2-edge cut. | 40 cuts |
| 3 | At every nontrivial 2-edge cut, one side is equality and the other disequality, and both cut edges carry the atom. | 40/40 |
| 4 | At every nontrivial 3-edge cut of five spaces, the point side is an antipodal pair and the line side its complement. All plain in the chain of 3 and the star of 4; twisted cuts in the three cyclic spaces. | 48/48; 21 twisted |
| 5 | Where 2-edge cuts occur: splice trees 0; a cycle of k blocks k(k − 1)/2; the twisted cube 3; the 3-cycle spliced into Fano 3. | pass |
| 6 | Control: in a colourable cubic system with a 2-edge cut (two K4^(3) joined crosswise), the sides accept four states each, not two-place parity. | pass |

**Counts per space (check 4).**
- The 3-cycle: 12 cuts, 6 twisted.
- The twisted cube: 18 cuts, 9 twisted.
- The 3-cycle spliced into Fano: 13 cuts, 6 twisted.

**Corrections inside the ticket.**
- **The cut enumeration.** It first counted 2-edge cuts together with a spare edge as 3-edge cuts. It now requires every removed edge to
  join the two shores.
- **Check 4.** It first expected plain equality and not-all-equal in cyclic spaces, and failed. That failure is the signed finding of
  item 3.
- **Activation order.** Check 1–6 first ran before the ticket was marked active. It was rerun after activation, and the frozen result
  comes from that run.

## What this does not establish

- **Cuts of four or more edges.** These are not classified.
- **Where 2-edge cuts occur in general.** Only the ten spaces were enumerated.
- **Paths.** Whether routes through these interfaces are fixed by the space, and what they carry, is ticket B.

## Novelty

- **Ours.** The atom lemma, the point lemma and the cycles of Fano blocks (KNOT-COUPLING, THREEFOLD-AMPLITUDE, THREEFOLD-SPACES).
- **Classical.** Seymour's bound (1974), here in its signed form.
- **New here.** The two-interface statement, the signed form of the 3-edge statement, and the correction. No source checked states
  them. They are elementary consequences of the above, and folklore risk is moderate.
