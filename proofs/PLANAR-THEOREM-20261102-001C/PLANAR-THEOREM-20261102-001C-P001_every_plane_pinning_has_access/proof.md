# Every pinning on a plane side has access; what the premise still needs

Status: Proved (items 1–3); items 4 and 5 are computations

Ticket `PLANAR-THEOREM-20261102-001C`, 2026-11-02.

## Question

- **The premise.** Every new knot at an opened cut is a pinned-and-separated three-point knot through the hub.
- **The access lemma (ticket A).** It is proved for pinnings by the hub and one near point. Ticket B disposes of every crossing knot that one
  port separates.
- **This ticket asks two things.**
  - Is the hub special, or does every pinning on a plane side have access?
  - Which crossing knots remain, and what do they need?

## Dependencies

- **`PLANAR-THEOREM-20261102-001A`.** Potentials, the staircase, and the midpoint argument.
- **`PLANAR-THEOREM-20261102-001B`.** One-port 2-sums.
- **`PLANAR-COMPOSE-20261102-001A`.** The route lemma and the pinning classifier.
- **Classical.** L-convex and L-natural convex sets (Murota, *Discrete Convex Analysis*, 2003). The integer solutions of a system of
  difference constraints form an L-convex set. Fixing one coordinate of an L-convex set to 0 leaves an L-natural convex set in the others.

## Setting

As in ticket A:
- H is a plane knot space with Kasteleyn signs, and M is a removed line.
- L is a gluing line whose ports show six patterns, all but {σ, σ̄}.
- A **pinning** is an ordered pair (p, a) of points, not tied to each other, whose values (π, α) leave one pattern t on L. Ports and the
  hub's class are allowed.
- t has an **odd port** and two **non-odd ports** y, y′.

## 1. The access lemma holds for every pinning (proved)

**On a plane side, every pinning (p, a) of t satisfies, relative to p:**
- **(i)** if p is a port, or is tied to a port y₀, then y₀ is not t's odd port;
- **(ii)** otherwise, {p, y, y′} is a near knot that excludes, at p = π, a pattern one step from t.

*Proof.* Re-centre ticket A's potentials at p.

- **The L-convex set.** Drop the normalisation at the hole. The integer solutions c of the difference constraints
  −μ₀(e) ≤ c(q) − c(p′) ≤ 1 − μ₀(e) form a set Ĉ (one coordinate per region of B, the hole included).
  - Ĉ is L-convex: it is closed under adding 1 to every coordinate and under rounded midpoints.
  - Ticket A's potential set is the section of Ĉ at c(hole) = 0.
- **The section at p.** C_p = {c ∈ Ĉ : c(p) = 0} is an L-natural convex set in the remaining coordinates. Its elements are exactly the
  potentials re-centred at p, c − c(p), one per matching. In particular, its coordinate ranges and its sections are integer intervals
  and L-natural convex sets.
- **The parity reading.** c(q) − c(p) mod 2 is q's value relative to p, compared with the reference solution. So q is tied to p exactly
  when its coordinate in C_p is constant.
- **The staircase.** Ticket A §2 speaks only of differences of port potentials, and of the jumps across L's edges, which a matching
  fixes. So it holds in C_p unchanged.
  - (a) The non-odd difference takes neighbouring values on and off each state.
  - (b) A port whose coordinate is constant (p itself, or a port tied to p) forces the other two ports to trace a chain with that port's
    state in the middle.
- **The midpoint argument.** Ticket A §3 uses only three things: rounded midpoints in an L-natural convex set, the parity reading, and the
  staircase. So it applies verbatim with C_p and with A = c(a) − c(p).
  - If a is itself a port, A is one of the port coordinates, and the argument is unchanged. In case (i), it closes at once: the two
    end states of the chain give A different parities.
- ∎

So the hub is not special on a plane side. Every point, including every port, has access whenever it takes part in a pinning.

## 2. The route lemma holds for every pinning (proved, any side)

- **The lemma.** PLANAR-COMPOSE A item 2 states the route lemma for the hub. Its proof never uses that h is the hub. Read with p in place of
  h:
  - **The hypothesis.** (p, a) pins t, p has access (i) or (ii), and a far point c separates t.
  - **The conclusion.** The crossing knot K = {p, a, c} is generated, whatever the far side.
- **When p is itself a non-odd port y.** Route (i) reads: eliminate y′ from the near knot {y, a, y′} and the far knot {y, y′, c}.
- **The trivial case.** If K is tie-equivalent to a one-sided knot, it already lies in the base.

## 3. Consequence (proved from 1 and 2)

- **The theorem.** On a plane near side with Kasteleyn signs, at a six-pattern removal, every crossing knot pinned by two near points and
  separated by one far point is generated, for any far side.
- **Scope.** This holds whether or not the knot passes through the hub, and whether or not a pinning point is a port.
- **With ticket B.** Every crossing knot on a plane near side is generated if it is separated by one port, or is pinned by two near points
  and separated by one far point.

## Checks

`check.py` (`result.json`, about a minute and a half):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Every pinning on 30 plane spaces (ports and hub included) | 167,704 ordered pinnings, all of type (i) or (ii) |
| 1 | The Fano plane and census 58 | none of the 1,536 pinnings by two non-port points has access relative to either point |
| 2 | Routes on splices (six census and two 10-point near sides; far sides K4^(3), census 6, Fano, census 58) | plane near sides: 3,438 near-pinned three-point knots that no single port separates. Of these, 2,322 follow the access routes (1,665 route (i), 1,161 route (ii), some both) and 1,116 are tie-equivalent to one-sided knots |
| 3 | Census and reduction (same splices, every near removal) | see item 4 |
| 4 | Point-split sides | see item 5 |

**The non-planar contrast (check 1, roles relative to p).**
- **Fano plane.** Hub-pinned pairs: the hub is tied to the odd port (i′). Their mirror pairs: the other point is free of the non-odd
  ports (iv). Every pinning by two non-port points involves the hub.
- **Census 58.** The same two failures occur, plus 144 two-step knots (ii′) and 96 off-hub pinnings with (iv).
- **Ports.** A pinning that contains a port has access relative to that port exactly when the port is non-odd.

## 4. What the premise still needs (computation)

On the splices of check 2, at every near removal:

| Class of crossing knot | Plane near sides | Non-planar near sides | New |
| --- | --- | --- | --- |
| Separated by one port (ticket B) | 26,614 | 6,942 | 0 |
| Pinned by two near points, separated by one far point | 10,865 | 2,352 | 564 (all through the hub, six-pattern removals, non-planar near sides) |
| Residual: the far side pins a port pair | 4,862 | 1,540 | 0 |
| Residual: three near points pin | 990 | 1,364 | 0 |
| Residual: neither side pins alone | 2,814 | 532 | 0 |
| **All** | **46,145** | **12,730** | **564** |

- **The reduction holds on every splice.** All 58,875 crossing knots are generated by one-sided knots together with the knots pinned by two
  near points.
- **The premise holds in its original form.** Every new knot is pinned by two near points, passes through the hub, and is separated by one
  far point.
- **Not proved.** That the 12,102 residual knots always reduce to the two proved classes.
  - In every residual knot, one side pins a port pair in projection, or the pinning is spread over both sides.
  - The routes found for them pass through ports, near points or far points, with no single pattern.

## 5. The point-split side (computation)

- **The construction.** Split a point of a knot space into three ports, one on each line through it. This is the far side of every splice.
- **Plane spaces.** Every pinning of the port pattern by two non-port points has access: 552 on the plane census spaces and three grown
  plane spaces (528 of type (ii), 24 of type (i)).
- **Non-planar spaces.** On the Fano plane and census 58, no two non-port points pin the port pattern at all. Pinning there needs three
  far points.
- **What it suggests.** The residual class "the far side pins" is governed on the far side by the same access dichotomy.

## What this does not establish

- **The reduction lemma.** That every residual crossing knot reduces to one-port 2-sums and pinned three-point knots.
- **Access for larger pinnings.** That pinning triples, and pairs pinning only two ports, have access on plane sides.
- **The full planar theorem.** That a plane near side creates nothing, for any far side. It now rests on the reduction lemma alone, which
  holds on every splice tested.
- **Four-pattern removals.** These are outside the access lemma. No creation has been found there.

## Novelty

- **New here.** The extension of the access lemma to every pinning, by re-centring. The census of the remaining classes, and the
  point-split computation.
- **Classical.** L-convex sets and their sections (Murota).
