# An opened hub can create emergence that does not compose

Status: Proved

Ticket `HUB-GLUE-20261102-001C`, 2026-11-02.

## Question

- **From ticket B.** A held hub (a removal off the point side) composes emergence exactly as a 2-sum.
- **The question.** What happens when the removed line is on the point side, so that the hub itself loses a line?

## Dependencies

- **`HUB-GLUE-20261102-001B`.** The 2-sum through a held hub.
- **`HUB-GLUE-20261102-001A`.** The leftover hub, splices and contractions, and `glue_lib.py`.
- **`NATIVE-PATHS-20261101-001A`.** The line side of a 3-edge cut accepts exactly the complement of the point side's antipodal pair.

## Setting

- **The cut.** As in ticket B: a simple 3-edge cut with point side P (ports a, b, c on the closing line L of the contracted piece
  H_P) and line side Q.
- **The removal.** M is a line of P.
- **The interface.** I is the set of port patterns, read under L's signs, that occur on the solutions without M.

## Theorem

1. **The interface.** I = proj_L S(H_P − M): exactly the patterns that the closed point piece allows on its closing line once M is
   gone.
2. **Three types.** I is a complement-closed set of not-all-equal patterns, so it is one of these:
   - **one pair:** the hub re-ties in a new pattern and still carries one bit;
   - **two pairs:** one port is released and the other two stay tied;
   - **all three pairs:** the hub becomes a knot on its own three points.
3. **When the 2-sum survives.**
   - **One pair.** The 2-sum of ticket B holds unchanged.
   - **Two or three pairs.** The 2-sum fails in every way:
     - candidates that are not circuits;
     - crossing circuits outside the 2-sums;
     - crossing circuits through a port.
   - **New emergence.** In the 13-point Fano splice some crossing knots of an opened hub are produced by no chain of eliminations from
     one-sided knots.
4. **When M holds two ports.** Their tie survives, opposite under L's signs. So I has at most two pairs, and in every case checked
   exactly two, with the third port released. In every two-pair interface checked, the released port lies off M.

## Proof

**Item 1.**
- **A join on the ports.** The solutions without M are the join, on the ports, of the solutions of P − M and those of the line side.
- **The line side.** It accepts every pattern except the antipodal pair the point side accepts (NATIVE-PATHS A). That pair is the two
  all-equal patterns of L, since the full space fails.
- **The point side without M.** P − M is H_P − L − M. Its port patterns are those of S(H_P − M), all not-all-equal because L is
  present, together with some all-equal patterns, where L is violated.
- **Intersecting.** The line side removes exactly the all-equal patterns. ∎

**Item 2.**
- **Complement-closed.** The knot is symmetric under complementing every value, so I is closed under complement.
- **The three pairs.** Under L's signs the not-all-equal patterns form three complementary pairs, each singling out one point:
  {100, 011}, {010, 101} and {001, 110}.
- **Two pairs.** Leaving out the pair that singles out the point j leaves exactly the patterns in which the other two points differ,
  with j free.
- **All three** pairs make up NAE itself. ∎

**Item 3.** With one pair {w, w̄}, the ports carry one binary value (w or w̄), and complementing flips it. Ticket B's proof then
applies word for word. The failures for two and three pairs are computed (checks 3 and 4). ∎

**Item 4.**
- **The tie from M.** By ticket A, item 1, applied to H_P and M, the points of M are tied on S(H_P − M), equal under M's signs. So
  x_a ⊕ s_(M,a) = x_b ⊕ s_(M,b).
- **The 4-cycle a–M–b–L.** It is nice in every census space (check 5): the rest has a perfect matching.
- **The signs.** Sign-nonsingularity then makes the two permutation terms through it agree. That forces s_(L,a) ⊕ s_(L,b) ⊕ s_(M,a) ⊕
  s_(M,b) = 1. Hence x_a ⊕ s_(L,a) ≠ x_b ⊕ s_(L,b): a and b are opposite under L's signs.
- **So.** I lies inside the four patterns with a ≠ b, a complement-closed set of one or two pairs. The checks find two in all 340
  cases. ∎

## Reading

- **The hub is where emergence is controlled.**
  - **Held** (one bit). The pieces' knots compose across it exactly like cycles.
  - **Opened** by losing a line of its own side. It releases a point, or becomes a knot on its three points. Then emergence crosses
    the glue in ways no composition of the pieces' knots explains.
- **Selection decides which.** The same line removal that selects a space decides, by where it falls, whether the glue composes or
  creates.

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Every splice of two census knot spaces up to 13 points (every line, one point), every removal on the point side. | 1120 removals; the interface always equals the closed piece's patterns |
| 2 | The types. | 16 one pair, 716 two pairs (the released port always off M), 388 three pairs; all 340 with M holding two ports have two pairs |
| 3 | The 2-sum (full circuits up to 11 points; up to 6 elements at 12 and 13). | one pair: 120 crossing circuits, exactly the 2-sums. Two pairs: 28518 crossing circuits, 20109 outside the 2-sums, 10000 failed candidates, 10415 through a port. Three pairs: 30142, 26800, 11371, 16896 |
| 4 | Generation by eliminations in the 13-point Fano splice (all circuits). | held: 384 crossing knots, all generated; opened: 762, of which 72 are not generated |
| 5 | The 4-cycles through two lines sharing two points, in the census spaces. | 86, all nice with an odd sign product |

## What this does not establish

- **Why the released port lies off M** when M holds fewer than two ports: observed in every case, not proved.
- **What the new knots are.** The 72 ungenerated knots are counted, not classified.
- **Non-simple cuts and 4-sums.** Not treated.

## Novelty

- **New here.** The classification of opened interfaces, the failure of composition there, and the reading of the hub as the control
  point.
