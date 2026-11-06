# A removal opens exactly the cuts that point away from it

Status: Proved

Ticket `SPLICE-TREE-20261102-001A`, 2026-11-02.

## Question

- **The setting.** A knot space glued from several pieces has a tree of cuts.
- **The question.** When one line is removed, which cuts hold and which open, and what stays fixed?

## Dependencies

- **`HUB-GLUE-20261102-001`.**
  - A: the leftover hub, splices, contractions, and `glue_lib.py`.
  - B: the 2-sum at a held hub.
  - C: the opened interface.

## Setting

- **Assembly.** Pieces (knot spaces) are glued along a tree: each splice joins a line of one piece to a point of the next, using
  `tree_lib.assemble`.
- **Orientation.** Each cut is oriented from its point side (the part that gave the line) to its line side (the part that gave the
  point). Check 1 confirms that every cut stays a simple 3-edge cut of the whole space.
- **Pointing toward M.** A cut points toward a line M when M lies on its line side, and away when M lies on its point side.

## Theorem

1. **Which cuts open.** Removing M holds every cut that points toward it and opens every cut that points away from it.
2. **Beyond a held cut nothing depends on M.** The far point side keeps exactly the circuits of its own system. These are the knots of
   its contraction without the closing line.
3. **Beyond an opened cut M acts only through the interface.** The interface is the set of patterns the near contraction (which
   contains M) allows on the closing line once M is gone.

## Proof

- **Each cut by itself.** Every cut of the tree is a simple 3-edge cut of the whole space (check 1). So HUB-GLUE B and C apply to each
  cut by itself, whatever other cuts lie on either side.
- **Item 1.**
  - **Held.** If M is off the point side, every point-side line remains, and the ports are tied (HUB-GLUE B, item 1).
  - **Opened.** If M lies on the point side, the interface is the near contraction's patterns without M (HUB-GLUE C, item 1).
- **Item 2.**
  - **The solutions are a join.** At a held cut they join the far side's solutions to the near side's along one bit.
  - **The near side admits both values of the bit.** Its solutions are closed under complement and nonempty.
  - **So.** The projection onto the far side is the far side's whole solution set, and its circuits are that set's.
- **Item 3.** At an opened cut the far side is the line side, untouched by M, joined along the interface. ∎

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Six assemblies: K4 > K4 > K4, K4 > K4 < K4, K4 > Fano > K4, Fano > K4 > Fano, a chain of four K4s, a star of four K4s (10 to 16 points). | all fail globally; every cut simple |
| 2 | Every removal, every cut. | 107 held cuts, all with tied ports; 69 opened cuts, all matching the interface formula (36 with four patterns, 33 with six) |
| 3 | The far point side of every held cut. | in all 107 cases its circuits are exactly those of its own system |

## What this does not establish

- **How knots cross several cuts.** That is tickets B and C.
- **Non-simple cuts and 4-sums.** Not covered.

## Novelty

- **A corollary.** It follows from HUB-GLUE A–C.
- **New here.** The reading by orientation (held toward the removed line, opened away from it) and the locality statement.
