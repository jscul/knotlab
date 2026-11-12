# Twisted pins on cycles

Status: Proved (T1 to T3 by hand, in the advisor model's form) with a small exact census; **referee pending** (the background referee
thread). Ticket A of `research/TWIST-PIN-20261112-001/preregistration.md`, frozen with the code in commit `1422c900f`.

Words, as in the pre-registration: twist, holonomy, the classes balanced, N-balanced and N-twisted, the quotient block B/H.

## 1. Settled by definition

T1 (transport), T2 (gauge: a twist undoes copy by copy exactly when every holonomy is trivial; so on a pattern with no closed chain of
knots it always undoes) and T3 (a twisted pin is ordinary pinning with the block folded by the holonomy group H) are proved in the
pre-registration. So pins that vary, in the frozen sense, exist exactly where a holonomy is N-twisted: there the folded block ties a
pinned distinction to another the block alone does not tie it to.

## 2. The census (exact)

| Check | Outcome |
| --- | --- |
| The advisor's form of the binding (at most one non-unanimous place per knot of the block) | holds on all 87 blocks |
| Chain of 4 knots (no cycle), any twist | identical to untwisted (P1) |
| Balanced cells | 308, all identical to untwisted |
| N-twisted cells: pins that vary (new tie inside a copy) or an end | 51 of 51 in the frozen run; after the run (below) 60 live with new ties, 37 end |
| Necessary and sufficient conditions for living (P4) | never violated |
| The advisor's exact condition on one cycle (P5) | 60 of 60 frozen (two knots sharing two), 180 of 180 after the run (cycles of 2, 3 and 6) |
| Measured ties inside a copy equal the quotient's | 389 of 390 living cells frozen, 156 of 159 after; the exceptions below |
| Rings with every knot's middle member twisted by an involution (P7) | undo on the ring of 6 (43 of 43 balanced), never on the ring of 7 |

**A flaw in the frozen placement, and the follow-up.** The frozen census twisted knot 0's second member. In the closed chains and the
two cycles that member is the knot's own distinction outside the cycle, so those cells were balanced, as T2 says, and tested only the
null; the length question (P6) was untested by the frozen run. After the run (descriptive, `after_run_on_cycle.py`, the frozen
functions) the twist was put on a member on the cycle: for every one of the 60 pairs of block and symmetry, living was the same on
cycles of 2, 3 and 6 knots (37 live at every length, 23 end at every length), and the advisor's exact condition agreed in all 180
cells. **No cycle-length effect in range**: the outcome depends on the holonomy alone.

**Beyond the quotient.** In one block (knots (0,1,2), (0,1,3), (0,1,4), (2,3,4), (2,3,5)), the symmetry exchanging 2 and 3 is
N-balanced, yet on every cycle it ties the spare distinctions 4 and 5 inside each copy: the quotient of the pinned layer does not see
it. Ending can also come from the spare distinctions: 69 N-balanced cells end with no pin varying.

## What this establishes

- Proved: a twisted pin is ordinary pinning with the block folded by the holonomy of the pattern's cycles; twists on patterns without
  closed chains undo; pins vary exactly where a holonomy moves a pinned distinction off its own tie class.
- Exact on the range (18 blocks; cycles of 2, 3, 6 knots; two cycles; rings of 6 and 7): no dependence on cycle length; the advisor's
  condition exact; one block whose fold also ties two spare distinctions. On the native one-shift rings, a middle twist by an
  involution folds the pins on the ring of 7 and undoes on the ring of 6: the ring's parity decides.
