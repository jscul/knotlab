# Bounded scan: proving the arm inequality on gadgets with loops

Date 2026-10-25. Scope: a short idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and enter
claims only as cited hypotheses, never as admitted evidence.

## Question

The arm inequality F(u)F(ū) ≤ s_u + F(u + eᵢ)F(ū) + F(u)F(ū + eᵢ) is proved for tree gadgets of the open knots
(`SOFT-HUB-20261024-001C-P001`) by an injective one-sided switch along the tree route. With a cycle the switch collides. Which known
tools could replace it?

## Candidate tools

| Tool | Why it might help | Barrier found in scoping |
| --- | --- | --- |
| McQuillan, *Approximating Holant problems by winding*, arXiv:1301.2880 | Local fractional decompositions (windability) compose through any circuit, cycles included. | The open knots are not windable; the needed moves are one-sided, and one-sided switches change the difference set, so they do not compose as winding does. |
| Jerrum and Sinclair, canonical paths (1989); Huang, Lu and Zhang, arXiv:1510.04099 | Switching arguments with bounded congestion replace exact injections. | A congestion bound would give a constant, not the sharp inequality, unless congestion is exactly 1 on average. |
| Weitz, self-avoiding walk trees (2006); Godsil's path tree for matchings | Unfold a graph with cycles into a tree with pinned leaves, where tree arguments apply. | Exact for single marginals of pairwise models; the inequality is a joint statement about three terminals of a three-place constraint. |

## Discriminators

- **Adversarial search** for violations, aimed at cycles (ticket A).
- **Strengthenings** that a local proof would need: per partner solution, per image difference pattern, matchings by one-sided path
  flips. Scoping: each fails on some gadgets while the inequality holds, so any proof must be global (ticket B).

## Novelty status

- `no-overlap-in-bounded-search` for the inequality and its no-copy reading.
