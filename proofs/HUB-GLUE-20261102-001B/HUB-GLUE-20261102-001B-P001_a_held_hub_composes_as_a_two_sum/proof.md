# Through a held hub, emergence composes as a 2-sum

Status: Proved

Ticket `HUB-GLUE-20261102-001B`, 2026-11-02.

## Question

- **From ticket A.** Selection's leftover is the hub side of a 3-edge cut, and the knot's spaces are spliced along such cuts.
- **What a scouting probe saw.** In spliced spaces, after a line is removed, many kept knots cross the cut.
- **The question.** How does emergence cross the glue?

## Dependencies

- **`HUB-GLUE-20261102-001A`.** The leftover hub, splices, contractions, and `glue_lib.py`.

## Setting

- **The cut.** A knot space H has a simple 3-edge cut.
  - **Point side P.** Its points, including the three ports p1, p2, p3.
  - **Line side Q.** Its points.
  - **Slot lines.** Each of the three slot lines holds one port and two points of Q.
- **The removal.** A line M off the point side: a line of Q or a slot line. S is the set of solutions without M.
- **The two parts.**
  - **The P-part A** is the projection of S onto P.
  - **The other part B** is the projection onto Q and the ports.
- **Circuits.** They are minimal constrained sets, relative to ranges.
  - **Ties** have two elements and **knots** three or more.
  - **Crossing.** A circuit crosses when it meets both P minus the ports and Q.

## Theorem

1. **The hub holds.** On every solution in S the ports take two complementary all-equal patterns, so they carry one binary value h.
2. **The structure of S.**
   - **A join.** S is the join of A and B along h.
   - **Complement.** A and B are closed under complementing every value, which flips h.
   - **Equal halves.** For every set X of P's non-ports, the halves A_X(0) and A_X(1) of its projection (at h = 0 and at h = 1) have
     equal size, and likewise on Q's side.
3. **The 2-sum.** Let X be a nonempty set of P's non-ports and Y a nonempty subset of Q. Then:
   - X ∪ Y is a circuit of S exactly when X ∪ {p} is a circuit of A and Y ∪ {p} is a circuit of B, for a port p. Any port will do,
     since the ports are tied.
   - No crossing circuit contains a port.
   - **In other words** the crossing knots are the 2-sum of the two sides' circuits through the hub, ties included. A tie X ∪ {p}
     simply moves a circuit of B across the hub.
4. **What it takes.** Without complement symmetry the forward direction fails: two circuits through a bit, each deficient at one value
   only, eliminate to a free set.

## Proof

**Item 1.**
- **Every point-side line remains.** M is off the point side, so the P-part of a solution solves the system P.
- **Apply ticket A.** P is the point-side contraction H_P (a knot space, by A, item 3) minus its closing line. By A, item 1, its
  solutions give the ports exactly the two all-equal patterns under that line's signs.
- **S is not empty**, since the failure is global. ∎

**Item 2.**
- **A join.** The only incidences between P's points and Q's lines are the three cut edges, at the ports. So a solution is any pair of
  side solutions that agree on the ports, that is, on h.
- **Complement.** The knot is symmetric under complementing its three inputs, and the signs are fixed, so complementing every variable
  maps S onto S. It flips the ports, hence h. So A_X(1) is the complement of A_X(0), and the two have equal size. ∎

**Item 3. A lemma.** Suppose X is free in A and Y is free in B. Then X ∪ Y is constrained in S iff X ∪ {p} is constrained in A and
Y ∪ {p} in B.
- **Why freeness matters.** Since X is free, A_X(0) ∪ A_X(1) = Π_X, and likewise for Y.
- **(⇐).** If X ∪ {p} is constrained, some half of X is a proper subset, hence both are, being of equal size. Likewise for Y. Choose
  a ∉ A_X(0) and c ∉ B_Y(1). Then (a, c) lies in neither A_X(0) × B_Y(0) nor A_X(1) × B_Y(1), so it is missing.
- **(⇒).** If X ∪ {p} is free, then A_X(0) = A_X(1) = Π_X, and the projection is Π_X × Π_Y.

**Item 3. Circuits.**
- **(⇒).** Let C = X ∪ Y be a circuit.
  - **The sides are constrained.** X and Y are free (proper subsets), so by the lemma X ∪ {p} and Y ∪ {p} are constrained.
  - **They are minimal.** If X′ ∪ {p} were constrained for some X′ ⊊ X, the lemma would make X′ ∪ Y constrained, against the
    minimality of C. The subsets of X itself are free.
  - **Conclusion.** So X ∪ {p} is a circuit, and likewise Y ∪ {p}.
- **(⇐).** Let X ∪ {p} and Y ∪ {p} be circuits.
  - **Constrained.** X and Y are free, so the lemma makes X ∪ Y constrained.
  - **Minimal.** Take a proper subset X′ ∪ Y′. If X′ ⊊ X, then X′ ∪ {p} is free, and the lemma (⇒) makes X′ ∪ Y′ free. Likewise if
    Y′ ⊊ Y.
- **No port in a crossing circuit.**
  - **One port.** If a crossing circuit C contains a port p, then X ∪ {p} and Y ∪ {p} are proper subsets, hence free. Then both halves
    are full on each side, and C is free.
  - **Two ports** form a tie, a constrained proper subset. ∎

**Item 4.** The control is computed in check 3. ∎

## Reading

- **Cycle-like composition at the hub.** At a held hub, two knots that meet at the hub compose into a knot spanning both pieces, and
  every spanning knot arises this way. This is circuit elimination exactly at the hub, and the 2-sum of matroids.
- **A matroid parallel.** In matroids, 2-sums are the gluing along a 2-separation. Here a 3-edge cut of the substrate becomes, after
  selection removes a line off the point side, a 2-sum of the solutions.
- **The reason is the knot's own symmetry.** Complementing every value is a symmetry of the knot. Most constraints lack it, the OR
  of the control for one.
- **Fit with SELECT-COUNT.** Selection and cycle-like composition exclude each other as properties of a whole law (SELECT-COUNT A).
  Here they meet locally, inside the knot's own selected spaces, at the hubs selection leaves.

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Every splice of two census knot spaces up to 13 points (first line and point), every removal off the point side. | 200 removals: ports tied, solutions closed under complement |
| 2 | The crossing circuits against the predicted 2-sums (all circuits up to 11 points; circuits up to 7 elements at 12 and 13). | 2300 crossing circuits, exactly the 2300 predicted; none contains a port |
| 3 | Control: OR circuits against knot circuits joined along a bit. | OR eliminates to a free set; the knot's to a constrained one |

## What this does not establish

- **Removals on the point side.** There the hub opens. That is ticket C.
- **Non-simple cuts and 4-sum glue.** Not treated.
- **The largest circuits.** Circuits above 7 elements on the 12- and 13-point spaces are covered by the proof, not by the check.

## Novelty

- **Classical.** The 2-sum of matroids, and circuit elimination.
- **New here.**
  - The relational 2-sum through a hub whose halves have equal size.
  - Its source in the knot's complement symmetry.
  - Its reading as composition at the hubs selection leaves.

  The lemma is elementary, with moderate folklore risk.
