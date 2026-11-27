# Does the step one layer up need a closed system? What stands

`CUT-BOXES-20261127-001`. Frozen in commit a14cb272a5. Results are in `out/`. Referee pending.

**Answer: on the systems read, yes.** Each of the 49 closed twelve-knot systems that carry a box (`UPPER-GROWN-20261127-001`)
had one seeded link cut into two loose distinctions. After the cut:
- **C1 held.** No cut system has a box. Before the cut there were 801 boxes on these systems; after it, none, old or
  new.
- **C2 held.** Every cut system still has many bonds, between 131,578 and 223,829 each. The lower layer survives the
  opening, and the layer above does not.

**What follows, and what does not.** In the closed systems every box needs all twelve knots. A knot that holds a
distinction no other holder holds and no carrier reads can satisfy its law there, so it is never needed. Cutting a link
gives two knots such a distinction, and at most a box that reads both loose distinctions could survive. None does, on
the 49 cuts read.

A connected grown stage under ordinary growth always has loose distinctions, so it has no closed part: a closed part
holds each distinction twice, so nothing else meets it. If boxes need a closed holder set, ordinary growth never makes
one. That "if" is not proved. A box on an open holder set whose loose distinctions all lie in its carriers is not ruled
out, only unseen: one cut per system, 49 systems.

## Intuition (a link, not evidence)

The fresh distinction is what keeps ordinary growth from closing anything. Every birth brings one, and a fresh
distinction is exactly where a law can always be satisfied. So the layer above, which needs every knot of a closed part,
is out of ordinary growth's reach for the same reason that ordinary growth never changes what earlier distinctions
allow.

The rival laws recorded beside ordinary growth (the forbidding cuts, register entries A129 and A130) allow births with
no fresh distinction, which can close a part (lesson 12.3, part (d)). Cheapest test: grow sampled starts under those
laws and look for a closed part of twelve or more knots that carries a box.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: openness against the step one layer up | **Status:** STOP (C1, C2 held) | One cut removes every box on all 49 systems; bonds remain |
| Local direction: the step one layer up made by growth | Narrowed | Under ordinary growth, apparently out of reach (no closed part); under the forbidding cuts, open |
| Long-term goal: G17 with G18 | Obstruction learned | The second step appears to need closure, which ordinary growth never gives |

**Next step:** Continue with direction 1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The step one layer up under the forbidding cuts: do births with no fresh distinction close parts that carry boxes? | 3/3 | 2/3 | Grow 200 sampled starts under each cut to round 6; find closed parts; test those of twelve or more knots → a growth-made box, or no closed part | Proposed |
| 2 | Prove or break "a box's needed knots form a closed set" | 3/3 | 2/3 | Every cut of the witness's 18 links, and of two links → a surviving box, or a proof sketch | Proposed |

**Corrections:** none.
**Goals:** checkpoint row added (G17, G18).
**Assumptions:** none added (A309 covers the box form); the seeded choice of the cut link is a scaffold of this study,
one per system, not swapped.
**Scaffolds:** the cut link (one seeded choice per system; the other 17 links not run), the box form (A309).
**Advisor:** not consulted (usage limit).
