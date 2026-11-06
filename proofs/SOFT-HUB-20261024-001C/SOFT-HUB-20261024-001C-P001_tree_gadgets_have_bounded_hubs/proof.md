# Tree gadgets of the open knots have bounded hubs

Status: Proved

Ticket `SOFT-HUB-20261024-001C`, 2026-10-25.

**What it uses:**
- from `SOFT-HUB-20261024-001A-P001`:
  - Lemma 2 (exchange): F(u)F(ū) = sep_u + link_u with sep_u ≤ s_u;
  - Proposition 6: the eight non-windable knots are R_c = N[c] ∪ {c̄}, and a knot where a linked pair branches has local tuples c and
    c̄;
- from `SOFT-HUB-20261024-001B-E001` (supported): the annealed gadgets, used only as evidence for Conjecture 4.

## Standard statement

**Setting.**
- **Tree gadgets.** A gadget is a *tree gadget* when its knots and internal edges form a tree: connected, without cycles, and without
  loops. Pins and free legs are allowed.
- **Defects.** In a knot R_c, a slot is a *defect* when its value differs from c. The allowed tuples have 0, 1 or 3 defects.
- **Routes.** Let kᵢ be the knot carrying terminal i, and μ the *median* of k₁, k₂, k₃: the unique knot on all three tree paths between
  them. The *route* of terminal i is the tree path from kᵢ to μ.
- **The arm map.** For a linked pair (σ, τ) with terminal values (u, ū), walk the route of terminal i from kᵢ, and let b be the first
  knot on it whose three slots all differ.
  - The *arm* is terminal i's leg together with the route edges walked before b.
  - The arm map flips the arm in the configuration that has no defect at b.

**Theorem 1 (the arm inequality on trees).** Let R be one of the eight non-windable knots, in particular one of the six open knots.
For every tree gadget of R, every axis u and every terminal i:

  F(u) F(ū) ≤ s_u + F(u + eᵢ) F(ū) + F(u) F(ū + eᵢ).

**Corollary 2 (bounded hubs on trees).**
- **The bound.** Every tree gadget of R has hub ratio ρ_u ≤ 3 along every axis.
- **Not vacuous.** Tree gadgets do exceed 1: the eight-knot tree gadget stored in the check has F(001) = 13, F(110) = 12 and every other
  value at most 11, so ρ₀₀₁ = 12/11.

**Proposition 3 (where the argument stops).** In a gadget with a cycle, the walk of an arm along the difference is not determined by
the gadget. The seven-knot gadget stored in the check has a double edge at terminal 1's knot, and two different linked pairs with the
same image under the arm map. So the injection does not extend to gadgets with cycles as constructed.

**Conjecture 4 (all gadgets).** The arm inequality holds for every gadget of the six open knots. It would give ρ_u ≤ 3 for every
gadget, so no family of gadgets approaches an exact hub.

**Reading.**
- **Emergence on a tree cannot imitate a hub beyond ratio 3.** Without loops, rerouting one terminal's arm at the first knot that is
  empty on one side and full on the other accounts for every linked pair.
- **Loops are where it is open.** With a loop the arm can be rerouted in more than one way, and one image no longer identifies one pair.

## Nearest known result

- **The arm map is a one-sided path switch.** It is akin to the canonical paths of Jerrum and Sinclair and to McQuillan's winding,
  which switch a path of the symmetric difference on both configurations. Here the switch is one-sided, because the knot where the
  difference branches is rigid (`SOFT-HUB-20261024-001A`, Proposition 6).
- **The local content** is the inequality, its injective proof on trees, and the obstruction with cycles.
- **Novelty:** `candidate-local-delta`; folklore risk medium.

## Proof

### Theorem 1

Fix u and i. By Lemma 2 of ticket A, the separated pairs number at most s_u. It remains to map the linked pairs injectively into
Conf(u + eᵢ) × Conf(ū) ∪ Conf(u) × Conf(ū + eᵢ).
- **The arm follows the route.** Let (σ, τ) be linked, with K the difference component containing the three terminals.
  - The internal edges of K form a connected subgraph of the tree that reaches k₁, k₂ and k₃. So K contains the tree paths between
    them, and every route edge differs.
  - Every slot of μ leads towards one of the terminal knots, or carries a terminal leg, so all three slots of μ differ. Hence b
    exists and lies on the route.
  - A knot v before b has its entry and exit route slots differing, and its third slot not differing, by the choice of b.
- **The branching knot.** At b the local tuples are antipodal and both allowed. By Proposition 6 of ticket A they are c and c̄, so one
  configuration has no defect at b and the other has three.
- **The image is valid.**
  - A route knot before b has both of its differing slots flipped in one configuration, so that configuration now carries the other
    one's local tuple there.
  - At b the empty configuration has one slot flipped, so it has one defect, which is allowed.
  - Terminal i is flipped, and no other knot changes.
- **The image patterns.** If σ is empty at b, the image is (σ', τ) with terminal values (u + eᵢ, ū). If τ is empty, it is (σ, τ') with
  (u, ū + eᵢ). These two sets of patterns are disjoint.
- **Injectivity.** Take an image of the first kind (σ', τ).
  - Walking the route from kᵢ, every knot before b now agrees in all three slots, and so does terminal i.
  - At b, σ' has one defect at the route slot and τ has three, so they differ in b's other two slots.
  - So b is the first route knot where σ' and τ differ, the arm is the set of items walked before it, and flipping the arm back
    recovers σ.
  - The second kind is symmetric.
- **Conclusion.** link_u ≤ F(u + eᵢ) F(ū) + F(u) F(ū + eᵢ). Adding sep_u ≤ s_u gives the inequality. ∎

### Corollary 2

- **Notation.** Write m = min(F(u), F(ū)), m' = max(F(u), F(ū)) and M = M_u.
- **The bound.** By Theorem 1, s_u ≤ 3M², F(u + eᵢ) ≤ M and F(ū + eᵢ) ≤ M, so m m' ≤ 3M² + M(m + m'). Suppose m > M.
  - Then (m − M)(m' − M) ≤ 4M².
  - Since m' ≥ m, this gives (m − M)² ≤ 4M², that is m ≤ 3M.
- **The example.** The check counts the stored gadget exactly and confirms it is a tree. ∎

### Proposition 3

- **The gadget.** In the stored gadget, terminal 1's knot reaches a neighbouring knot through two parallel edges.
- **The collision.** For a linked pair whose difference leaves terminal 1's knot along either parallel edge, the arm walks one of them.
  The check finds two linked pairs that differ only in which of the two parallel edges carries the difference. After the arm is
  flipped in the configuration that is empty at the branching knot, the two images coincide. ∎

## Checks

`check.py` uses the standard library only (seed 20261024). It confirms:
- **Theorem 1** on 300 random tree gadgets with up to nine knots and fourteen unpinned variables, across 2,967 axis-terminal cases with
  41,160 linked pairs:
  - the arm structure is as stated (route knots before b differ exactly in their two route slots, and b has local tuples c and c̄);
  - the images are valid, lie on the stated patterns, and are injective;
  - the inequality holds.
- **Corollary 2** on the stored tree gadget: exact counts give ρ₀₀₁ = 12/11.
- **Proposition 3** on the stored cyclic gadget: a collision along the axis 000.
- **Conjecture 4, as evidence.** The inequality holds on 48,000 axis-terminal cases of 4,000 random gadgets with up to twelve knots
  (1,216 of them trees), counted exactly. It also holds on all 336 annealed gadgets of ticket B, whose largest hub ratio is
  65/53 ≈ 1.226.

**Controls.**
- **The empty side matters.** Flipping the arm in the configuration that is full at b gives an invalid assignment on some pair.
- **The inequality can fail.** The planted function [10, 1, 1, 1, 1, 1, 1, 10] violates it for every i.

## What this does not show

- **A bound for gadgets with cycles.** Conjecture 4 is open. The best gadgets found have cycles and reach 65/53, within the
  conjectured bound.
- **That 3 is sharp.** The largest tree ratio found in scoping was about 1.17.
- **Anything about approximate counting itself.** A bounded hub ratio closes one route to hardness, but proves no approximation scheme.
