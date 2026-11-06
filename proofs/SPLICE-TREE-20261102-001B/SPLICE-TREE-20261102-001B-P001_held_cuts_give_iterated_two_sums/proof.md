# Knots that cross only held cuts are iterated 2-sums

Status: Proved

Ticket `SPLICE-TREE-20261102-001B`, 2026-11-02.

## Question

- **From ticket A.** In a tree of cuts, a removal holds the cuts that point toward it.
- **The question.** Is every kept knot that crosses only held cuts built from knots inside pieces by 2-sums at the hubs?

## Dependencies

- **`SPLICE-TREE-20261102-001A`.** Held and opened cuts, and `tree_lib.py`.
- **Through it, `HUB-GLUE-20261102-001B`.** The 2-sum at a held hub.

## Setting

- **The space.** A knot space assembled along a tree of simple 3-edge cuts, with one line M removed.
- **Crossing.** A circuit C crosses a cut c when it meets both of these:
  - the point side of c away from c's ports;
  - the line side of c.
- **Base circuits** cross no cut.
- **A 2-sum at a held cut c** is (K1 − p) ∪ (K2 − p′), with K1 inside c's point side through exactly one port p, and K2 inside c's line
  side plus ports through exactly one port p′.

## Theorem

1. **Decomposition.** Every circuit that crosses at least one cut, all of them held, is an iterated 2-sum of base circuits through held
   hubs.
2. **Composition.** Every such iterated 2-sum is a circuit.
3. **So** a circuit not obtained this way crosses a cut that M opens: new emergence lives only across opened cuts.

## Proof

- **Item 2.** It is HUB-GLUE B (⇐), applied at each step.
- **Item 1, by induction on the number of cuts crossed.**
  - **Split at one cut.** Let C cross a held cut c. By HUB-GLUE B, C = (K1 − p) ∪ (K2 − p′), with K1 on c's point side and K2 on its
    line side, both circuits through the hub. Neither crosses c.
- **No new cuts.** Every cut c′ ≠ c crossed by K1 or K2 is crossed by C.
  - **Where c′ sits.** In a tree, c′ lies inside one side of c, say its point side (the other case is symmetric). Then c's line side
    and the piece holding c's ports lie together on one side of c′.
  - **K2 cannot cross c′.** It lies inside that one side.
  - **If K1 crosses c′.** Its point beyond c′ comes from C. C's line-side points sit on the other side of c′ and are none of c′'s
    ports, since c′'s ports lie next to c′, inside c's point side. So C crosses c′ too.
- **Conclusion.** K1 and K2 therefore cross only held cuts, and fewer of them than C. By induction they are iterated 2-sums of base
  circuits. ∎

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Seven assemblies (ticket A's six and a 19-point Fano chain, one removal per piece there): circuits crossing only held cuts against iterated 2-sums of base circuits. Circuits are complete up to 13 points, with up to 6 elements at 16 and 5 at 19. | exact equality at every removal: 510 circuits, 162 of them across two held cuts at once; every 2-sum produced is a circuit |

## What this does not establish

- **Opened cuts.** That is ticket C.
- **The K4-only assemblies.** They have no circuits crossing a held cut, since a K4 piece has a single interior point, so they test
  only the empty case.

## Novelty

- **New here.** An induction on HUB-GLUE B, using that the cuts form a tree.
