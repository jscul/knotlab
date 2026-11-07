# Islands keep the count hard

Status: Proved by hand, on top of `SPHERE-WIDTH-20261107-001A` (whose winding bound and isoperimetric constant are by sketch). The
island terms, the feasibility and the certificates are checked by computation.

Ticket `SPHERE-SIZE-20261107-001A`, 2026-11-07.

## Standard statement

**Lemma (islands).** Fix s ≥ 1. An island restriction ρ of the knot-sphere formula NAE(K_k) fixes the points of disjoint balls
B_j = B(c_j, s) in the point graph, where:
- the balls are pairwise at distance at least 17 and lie farther than s + 3 from the corners;
- ball B_j is coloured by one constant label ℓ_j in a frame developed over it: x_p = S_{ℓ_j}[σ_j(p)] ⊕ g_j(p).

Every resolution refutation of NAE(K_k)|ρ has width at least c(s)·k − 1. The constant c(s) > 0 depends only on s.

## Nearest known result

- **Dantchev–Riis's paradigm.** Grid formulas are randomized zone by zone (Dantchev–Riis 2001; Dantchev's thesis BRICS DS-02-2), and a
  coarse game must survive inside the restricted formula. This repository's `CELL-SIZE-20261020-001` used the same paradigm for Tseitin
  formulas on cellular graphs.
- **Classification.** new as far as found for height principles with a vortex. The delta: constant-label islands are permanent pebbles
  that add no budget to an obstruction, so `SPHERE-WIDTH-20261107-001A`'s density argument survives the restriction.

## Proof

**States.** A compatible state is a label state with its vortex z in the free region (the complement of the islands, at distance ≥ 2
from them) whose colours agree with ρ. By the window criterion, with the island points as permanent pebbles alongside Spoiler's, such a
state exists iff the sheet system has no negative cycle.

**Trivialization.**
- **The cut star.** Choose the cut star from z through triangles that meet no island. Such a star exists: the free region is connected
  (the islands are disjoint balls), it contains the corners' neighbourhoods, and it leaves room for six disjoint paths.
- **Island labels.** No cut meets an island, so each island has one label ℓ̃_j ∈ {0, …, 5} in the developed frame.
- **Representatives.** Take island arc starts a_p in [ℓ̃_j − 2, ℓ̃_j] and other pebbles' a_p in [0, 5]. Cycle sums do not depend on
  these choices.

**Claim 1 (terms).** The term of a segment from p to q is b = ⌊(d(p, q) + a_p + 2 − a_q)/6⌋, with d ≥ 0.
- (i) **Same island:** b ≥ 0, since a_p + 2 − a_q ≥ 0.
- (ii) **Different islands:** b ≥ ⌊(dist(p, q) − 11)/6⌋ ≥ 1. A d-shortest path gains at most 6 from the six arcs, because turns
  around the vortex or a corner never pay (`SPHERE-WIDTH-20261107-001A` lemma 3). So d ≥ dist − 6, while a_p − a_q ≥ −7 and dist ≥ 17.
- (iii) **Touching a Spoiler pebble:** b ≥ ⌊(2 − 7)/6⌋ = −1.

**Consequence.** Without Spoiler pebbles every term is ≥ 0, so every free vortex position admits a compatible state (check 1).

**Claim 2 (certificates are short).** Let a negative cycle have Σb ≤ −1 and pass through r Spoiler pebbles.
- **There is a Spoiler pebble.** By (i)–(ii), r ≥ 1.
- **Budget.** Each Spoiler pebble lies on at most two segments, so the negative terms total at least −2r. Hence the positive terms total
  at most 2r − 1.
- **Hops between islands.** By (ii), there are at most 2r − 1 of them.
- **Island visits.** At most 4r. Each visit passes through at most |B_j| = 3s² + 3s + 1 island points (the cycle is pebble-simple),
  along same-island segments of length O(s).
- **Other segments.** Between-island and Spoiler segments have length O(b + 1) each, so O(r) in total.
- **Total.** The certificate walk B has length L(B) ≤ C·s³·r.

**Claim 3 (separation).** As in `SPHERE-WIDTH-20261107-001A` lemma 2(b), B winds differently around the old and new vortex positions or
passes through the old one. Use one trivialization, with the vortex-moving path π kept in the free region.

**Conclusion.**
- **The bad set.** Let D_s(P) be the set of points with at least t/(C′s³) Spoiler pebbles within distance t, for some t. Its size is
  O(s⁶w²) (Vitali).
- **Room left.** The islands are separated balls, so they cover at most a fraction |B(s)|/|B(s + 8)| < 1 of the sphere; the free region
  is a constant fraction of it.
- **Duplicator.** Duplicator keeps the vortex in the free region, outside D_s(P), at distance ≥ 2 from the islands. Exactly as in
  `SPHERE-WIDTH-20261107-001A`, she survives w ≤ c(s)·k Spoiler pebbles, so the width is at least c(s)·k − 1 (Atserias–Dalmau). ∎

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Islands alone never obstruct (maximal packings, random labels; K_14, K_18, K_26 with separation 17) | every tested free vortex position feasible |
| 2 | Certificates with Spoiler rings through two islands (K_14 and K_18 at separation 6; K_30 at separation 17) | every certificate sums to ≤ −1; same-island terms ≥ 0; between-island terms obey the bound; at separation 17 no negative term away from a Spoiler pebble |

At separation 6 a between-island term of −1 does occur. The bound ⌊(dist − 11)/6⌋ allows it, which is why the lemma asks for
separation 17.

## What this does not establish

- **Size.** The size bound is `SPHERE-SIZE-20261107-001B`, which needs a random packing that fixes every point with constant probability.
- **Constants.** c(s) is not computed. It inherits the sketched constants of `SPHERE-WIDTH-20261107-001A`.
