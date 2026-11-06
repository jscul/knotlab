# Knot's spaces compose only through hubs

Status: Proved

Ticket `KNOT-COMPOSE-20261101-001A`, 2026-11-01.

## Question

- **What is already known.** The knot's spaces are the connected cubic systems on which not-all-equal fails. They are built from Fano
  atoms by splices and glue (THREEFOLD-SPACES, THREEFOLD-GRAMMAR). Across a splice the knot's law is exact, and amplitudes multiply
  (THREEFOLD-AMPLITUDE: point lemma and factorization).
- **The question here.** When the parts of a knot's space meet across a cut, what meets what: a knot meeting a knot, or a knot meeting a
  hub (an equality fan-out)? The contact-first program distinguishes the two.

## Dependencies

- **`THREEFOLD-SPACES-20261030-001A`.**
  - Theorem 1: a connected non-2-colourable cubic system is minimally so, and its incidence matrix is sign-nonsingular.
  - Theorem 2: the splice calculus. Every nontrivial tight cut is a 3-edge cut.
- **`THREEFOLD-AMPLITUDE-20261030-001A`.** Lemma 3 (the point lemma) and Theorem 4 (factorization across tight cuts).
- **`FOUR-PLACE-20261031-001A`.** The four-place classes (the twelve class) and the library.

## Lemma 1 (balance)

**Statement.** Let ∂(X) be a 3-edge cut of a cubic incidence graph whose shores both have more than one vertex. Then one shore has one more
point than lines. All three cut edges join its points to lines of the other shore.

**Proof.** Shore X has p points and l lines, with i incidences inside X. Then 3p = i + a and 3l = i + b, where a and b count the cut edges
at X's points and lines, with a + b = 3. So 3(p − l) = a − b ∈ {3, 1, −1, −3}, and divisibility by 3 forces a − b = ±3. ∎

The point side presents three ports, which are points. The line side presents three slots, which are lines missing a point.

## Lemma 2 (failure across a cut)

**Statement.** The whole system is solvable iff some channel assignment is accepted by both sides. So a composition fails exactly when the
two sides' accepted relations are disjoint. ∎

## Lemma 3 (complementarity)

**Statement.** A relation on k channels whose (k − 1)-place projections are all full has at least 2^{k−1} states. Equality holds only for
a parity coset.

**Proof.**
1. **The bound.** Every assignment of k − 1 channels extends, so there are at least 2^{k−1} states.
2. **The equality case.** With exactly 2^{k−1} states, each such assignment extends exactly once. So no two states differ in a single
   channel, and the relation is an independent set of size 2^{k−1} in the k-cube.
3. **Independent sets of the cube.** The k-cube is connected, k-regular and bipartite, so its only independent sets of that size are its
   two colour classes, the parity cosets. ∎

**Corollary.** If both sides of a cut accept knots, which have full projections, they can be disjoint only as the two complementary
parity cosets. A failing hub-free composition is a parity composition.

## Theorem 4

**Statement.** Let H be a knot's space.
1. **Every 3-edge cut is knot against hub.** Across every nontrivial 3-edge cut, the line side accepts exactly not-all-equal on its three
   slots, and the point side accepts exactly equality on its three ports. These are complementary halves of {0,1}³. So the parts of a
   knot's space meet as a knot against a hub.
2. **Double cuts.** Two cut incidences leave a balanced four-channel interface, two ports and two slots. Its accepted relation is either
   a twelve-class knot (12 states) or no knot at all. Two twelve-class sides never fail together, since 12 + 12 > 16.
3. **The consequence.** Every failing composition of the knot's spaces passes through a hub. A failing composition joining knot to knot is
   a parity composition. Parity does fail this way (the control).
4. **The transpose.** The transpose of H, with points and lines exchanged, is again a knot's space, and on every 3-edge cut it exchanges
   the knot side and the hub side.

**Proof.**
1. **Item 1.**
   - The point side X has one more point than lines. Join its ports to one new line z: since H is not colourable, every colouring of X
     proper on its own lines makes the ports constant as seen from z. This is the line case of the point lemma, applied to the piece
     H_X(τ) of the factorization theorem.
   - Both constant patterns occur, by complementation. So the point side accepts exactly equality.
   - The line side, with a new point z on its slots, is the other piece. The point lemma gives N(c ⊕ t) = 0 and N(c ⊕ t ⊕ e_i) =
     A(·, ℓ_i) > 0, so it accepts exactly the non-constant patterns.
2. **Items 2 and 3.** Item 2 is Lemma 3 with k = 4, together with the computed classification of double cuts (check 5). Item 3 follows
   from items 1 and 2 and Lemma 3.
3. **Item 4.** Sign-nonsingularity is invariant under transposition, and failure is equivalent to it (THREEFOLD-SPACES Theorem 1).
   Transposing exchanges points and lines, so it exchanges the two shores' roles in Lemma 1. ∎

## Checks

`check.py` (`result.json`, about 20 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Four knot's spaces: Fano, the 13-point splice, two 19-point splices. | pass |
| 2 | Balance on every nontrivial 3-edge cut (Fano has none; it is a brace). | 5 cuts |
| 3 | At every nontrivial 3-edge cut the point side is exactly equality and the line side exactly not-all-equal. | 5/5 |
| 4 | Complementarity for k = 2, 3, 4: the 2^{k−1}-state relations with full projections are the parity cosets. | pass |
| 5 | Double cuts of Fano (168) and of the 13-point splice (300): twelve-class knots or no knot; 200 random knot-to-knot joins never fail. | pass |
| 6 | Control: a parity piece joined knot to knot with a sign-flipped copy has complementary sides, and the joined cubic system has no parity solution. | pass |
| 7 | The transposes of the four spaces are knot's spaces; cut shores exchange roles. | pass |

**Correction inside the ticket.**
- **The bug.** Binding the census file (used by check 6) broke check 0's status test, which expected every bound JSON file to carry a
  status.
- **What happened.** The ticket's transitions ran in the same shell command, after a failed verification, because the steps were chained
  with `;`.
- **The fix.** The status test was restricted to the upstream proofs. Both runs (write and verify) then passed before anything was
  committed. The mathematics is unchanged.

## What this does not establish

- **Cuts larger than three edges with a hub on one side.** Trisum glue along 4-cycles is one example. Only double cuts are classified
  here.
- **Spaces outside the tested ones.** Only Fano and splices of Fano were tested. Glue pieces were not.
- **Counting.** Item 1 cites the amplitude results; no new count is claimed.

## Novelty

- **From THREEFOLD-SPACES and THREEFOLD-AMPLITUDE.** Tight cuts, the splice calculus, the point lemma and the factorization (on
  Lovász–Plummer and Robertson–Seymour–Thomas).
- **Elementary.** Lemma 3.
- **New reading.** "Knot's spaces meet only through hubs; hub-free failure is parity" was found in no source checked.
