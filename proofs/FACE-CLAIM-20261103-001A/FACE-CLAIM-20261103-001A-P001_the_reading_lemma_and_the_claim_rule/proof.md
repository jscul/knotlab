# The reading lemma and the claim rule

Status: Proved (the reading lemma, the claim lemma, and the claim rule's route direction); the rule's converse is computed

Ticket `FACE-CLAIM-20261103-001A`, 2026-11-03.

## Question

- **Background (PHASE-HALO).** With the Fano plane as handle, the halo beyond three steps lay on the faces opposite the attachment point.
  Census 58 also used the point's own long face.
- **The question.** What does each face around the attachment point read from the handle, and what decides whether a handle creates
  there?

## Dependencies

- **`HALO-FORCING-20261103-001A`.** The route lemma: a crossing knot with a route is generated.
- **`HALO-FORCING-20261103-001B`.** Point splits are plane matching systems whose solutions are corner matchings: each line skips the
  corner between its two agreeing points, and each face receives one skip.
- **`HALO-FORCING-20261103-001C`.** The validated pipeline.
- **`PHASE-HALO-20261103-001A`.** The claiming lemma and the plane families.

## Setting

- **The split.** A plane knot space is split at the attachment point z: its three lines through z each get their own copy of z, the
  ports 0, 1 and 2.
- **The merged face.** The three faces at z merge into one face F0. Its boundary is three **arcs**: the arc A(i, j) is the old face at
  z between the lines of ports i and j.
- **The opposite faces.** The face opposite port k is the face of the far corner of port k's line, the corner without the port.

## 1. The reading lemma (proved)

**The arc identity.**
- **Along one corner.** At a corner (p, q) of a line K, the raw values satisfy x_p + x_q = s_K(p) + s_K(q) + [the corner is not
  skipped] (mod 2).
- **Along an arc.** Adding these along A(i, j) gives x_i + x_j = κ(i, j) + (number of skips on the arc). Here the arc constant κ(i, j) is
  the sum of the sign differences at the arc's corners plus its number of corners.
- **The constants add to 1.** The boundary of F0 closes up, and F0 receives exactly one skip.

**The all-agree pattern.** Let e be the port pattern with e_i + e_j = κ(i, j) + 1 for every pair. It is consistent because the constants
add to 1.
- **It never occurs.** It would need a skip on every arc, so neither e nor its complement is a port pattern.
- **Every other pattern has an odd port.** Every other port pattern w differs from e (or its complement) at one port k, its **odd
  port**. We say w is in **class k**.
- **The merged face's skip.** Since F0's single skip lies on one arc, x differs from e exactly at the port off that arc. So **in class
  k, F0's skip lies on the arc opposite k**.

**What each face reads.**
- **The own arcs at port k carry no skip.** These are A(k, i) and A(k, j). So the own arc A(i, j) is barred (no skip) exactly when
  ports i and j disagree (relative to e).
- **The opposite face.** Port k's two port corners lie on the unskipped arcs, so its line skips its far corner. That line claims the
  face opposite k, and every other corner of that face is unskipped. So whenever i and j agree, the face opposite k is claimed by k's
  line.
- **Barred faces are frozen.** On a barred face every corner but the claimer's is unskipped. So all its points are fixed by one port
  value, and **each of its lines has the two points of its corner there fixed by the port pattern**.

The barred faces of class k are the face opposite k and the own arcs at k. ∎

*Check 1 (brute force):* 2,148 (split, solution) pairs on the planar census, two grown spaces and a ladder all obey the lemma. 2,052
(port pattern, barred corner) pairs have both points fixed.

## 2. The claim lemma (proved)

A frozen line **claims** its face when it skips its corner there instead.

**An own arc A(i, j).**
- **When it can happen.** Claiming puts F0's skip at that corner, so the class is the third port's.
- **How many patterns.** All other corners of F0 are then unskipped. So the claimed values fix the ports along both halves of the
  arc, and the class fixes the rest: **one port pattern per claimed value**.

**The face opposite k.**
- **When it can happen.** Claiming means k's line does not take its far corner. So k's line skips one of its port corners, F0's skip
  is there, and the class is i or j.
- **How many patterns.** The claimed values fix every point of the face, including the far points a and b of k's line. Skipping (k,
  a) or (k, b) then fixes port k, differently in the two cases, and the unskipped arc A(i, j) fixes x_i + x_j.
- **Port i is the same in both cases.** Its two values differ by x_a + x_b + s(a) + s(b) + 1, which is 0 because the corner (a, b) is
  unskipped.
- **So** there are **at most two port patterns per claimed value, one in each of classes i and j, agreeing on ports i and j and
  differing at port k**.

*Check 2 (brute force):* 114 own-arc corners and 318 opposite-face corners claimed in some solution all obey this. Every opposite-face
corner has a value claimed from two patterns.

## 3. The claim rule

**Candidates.** A pair of handle points pinned to values (r = ρ, o = ω) freezes a gluing line L when T, the set of L's patterns left
by the pair, has two elements with two points y1, y2 of L fixed at b1, b2. A far point that excludes exactly T (K4^(3) and census 6
can) gives a candidate knot {r, o, c}. **L's claims** at the two fixed values are the patterns (y1 = b1, y2 ≠ b2) and (y2 = b2, y1
≠ b1).

**The rule.** The knot is new exactly when each single point of the pair still allows both claims.

**Route direction (proved).** Suppose the single pin r = ρ excludes the claim (y1 = b1, y2 ≠ b2).
- **The route.** This is route (ii) of the route lemma with the pair (y1, y2) and values (b1, b2): T fixes y1, the far point
  excludes the block (y1 = b1, y2 = b2), which is T, and r alone excludes (b1, ¬b2).
- **Ties.** If y1 or y2 is tied to r, route (i) applies instead.
- **So** the knot is generated. The other claim is symmetric. ∎

**Converse (computed).** When each single point allows both claims, the knot is new in every case computed. The rule ignores the far
side beyond the existence of one excluding exactly T.

| # | Comparison | Cases | Disagreements |
| --- | --- | --- | --- |
| 3 | Against exact creation: two 10-point grown spaces, the Fano plane and census 58 (lines 0 and 6) at two points each, every removal and line | 728: 144 creating, 544 not, 40 near lines squeezed in another form (all creating) | 0 |
| 4 | Against the pipeline: thick tubes, a grid, two grown spaces, and every point of a ladder arm spliced onto a grid | far lines 26,634 (1,908 creating); near lines 3,018 where the rule applies; 585 near lines squeezed in another form (all creating) | 0 |

**Reading.**
- **What creation needs.** The handle must freeze the line through a pair of points, while each point alone leaves the line free to
  claim.
- **Why the faces differ.**
  - **The own arc's claim** is a single port pattern, which one handle point can easily rule out.
  - **The opposite face's claim** is a value of the other two ports with the third free, two patterns, which is harder to rule out.

## Checks

`check.py` (`result.json`, about three minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Reading lemma, brute force | 2,148 of 2,148 solutions; 2,052 of 2,052 barred corners fixed |
| 2 | Claim lemma, brute force | 114 own-arc and 318 opposite-face corners |
| 3 | Claim rule against exact creation | 728 cases, no disagreement |
| 4 | Claim rule against the pipeline | 26,634 far and 3,018 near lines, no disagreement |

## What this does not establish

- **The converse of the claim rule as a theorem.** It is computed, resting like the route criterion on exactness checked on small
  spaces.
- **Near lines squeezed in other forms.** Within three steps of the handle, some lines are squeezed to one pattern, or to two with one
  point fixed. The rule does not cover them; they all create.

## Novelty

- **New here.** The arc identity and the all-agree pattern of a split, the reading of the faces around a point, the claim lemma, and
  the claim rule.
- **Classical.** Kasteleyn parities and corner matchings.
