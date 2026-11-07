# Bond distance is a boundary

Status: Proved

Ticket `OPEN-END-GROWTH-20261107-001B`, 2026-11-07.

## Standard statement

Let G be a finite connected graph in which every ordinary vertex has degree 3, some edges ending at one
extra vertex ∞. Put a binary variable on each edge, and require the three variables at every ordinary
vertex to sum to 0 mod 2 (a Tseitin system with ∞ unconstrained). For a set U of ordinary vertices let
δ(U) be its edge boundary.

1. The minimal implied relations of size at least 3 that contain two given edges are the cuts δ(U)
   containing both, with U and (the other vertices plus ∞) both connected.
2. If δ(U) = {e} for a set U with no edge to ∞, then x_e = 0 in every solution. The solutions split as
   (edges inside U) × (edges outside U), so no minimal relation contains an edge on each side.
3. Every cut with both sides connected and at least 3 edges is a minimal relation. So any two of its
   edges lie in a minimal relation of that size.
4. Grow a graph from one vertex with three edges to ∞ by repeatedly choosing a vertex with at least two
   edges to ∞ and attaching a new vertex to one of them, giving the new vertex two edges to ∞.
   - The result is always a path: inner vertices keep one edge to ∞, and the two end vertices keep two.
   - The least minimal relation through two of the ∞-edges has (number of vertices on the path between
     them) + 2 edges.

## Nearest known result

- **Statements 1 and 3** are the bonds of a graph, the circuits of its cocycle matroid: minimal cuts are
  exactly the cuts whose two sides are connected (Whitney; Oxley, *Matroid Theory*, §2.3). For Tseitin
  systems the implied relations are the cuts.
- **Statement 2** is a bridge argument.
- **Statement 4** is an induction, plus the tree formula of `LOGIC-AXIS-20261107-001D` (Proposition 2).
- **Classification:** `known-with-delta`, at folklore level for the mathematics. The delta is the
  reading for growth rules:
  - bond distance is the least two-sided boundary, counting open ends inside;
  - sealing a region behind one seam freezes it off;
  - a long region with a short boundary is a shortcut;
  - one local rule grows exactly the two-way thread.

## Setting

As in `LOGIC-AXIS-20261107-001D`:
- **Hub-free parity laws.** In a hub-free parity law every knot (K1–K3) is a three-place parity check,
  and every distinction lies in at most two knots.
- **Its knot graph.**
  - knots are vertices;
  - a distinction held by two knots is an edge, a *seam*;
  - a distinction held by one knot is an edge to ∞, an *open end*.
- **Bond distance** δ(e, f) is the least size of a knot of the law containing e and f, minus one
  (NATIVE-NETWORK-20261021-001). It is ∞ when there is none.
- **Two-sided connected.** A set U of knots is two-sided connected when U is connected and the other knots
  together with ∞ are connected.

## 1. Bond distance is the least two-sided boundary

**Proposition 1.** δ(e, f) = min{|δ(U)| − 1 : U two-sided connected, e, f ∈ δ(U), |δ(U)| >= 3}, and ∞ if
there is no such U. Here δ(U) counts U's seams and the open ends held by U's knots.

*Proof.*
- **Implied checks.** The implied parity checks of the law are the sums of knot checks, which are the
  cuts δ(U) of the knot graph with ∞ ∉ U.
- **Knots.** The law's knots are the minimal nonempty ones with at least 3 elements. These are the bonds,
  and a cut of a connected graph is a bond iff both of its sides are connected. ∎

**Reading.** Bond distance is the size of the smallest two-sided region that has both distinctions on its
boundary. Seams count, and so do the open ends held inside. Open ends inside a region are part of its
boundary: they are its free distinctions, and any binding through the region must take them in.

## 2. One seam pins a sealed region

**Proposition 2.** Let U be a set of knots holding no open end, with exactly one seam e (δ(U) = {e}).
Then:
- x_e = 0 in every allowed state;
- the allowed states are the products of an allowed assignment to the distinctions inside U (both ends
  in U) and one to the distinctions outside (no end in U);
- no knot contains distinctions on both sides, and no knot contains e.

*Proof.*
1. **The pin.** δ(U) = {e} is an implied check, so x_e is constant 0, a pinned distinction.
2. **The split.** Every knot check involves only inside distinctions and e, or only outside distinctions
   and e. With x_e fixed, the two systems are independent, so allowed states are products.
3. **No knot crosses.** A set S meeting both sides, and not containing e, has X_S = X_{S∩inside} ×
   X_{S∩outside}. If S were a knot, both factors would be full by K2, so X_S would be full,
   contradicting K1.
4. **No knot contains e.** A set containing e has a constrained one-element projection, so it is not
   a knot. ∎

**Two seams do not decouple.** With δ(U) = {e, f} the two seams are tied (x_e = x_f), but knots can still
cross. Check 2 exhibits a sealed four-knot region whose inside and outside distinctions are all joined by
four-place knots.

**Consequence: closing every open end seals.** A growth rule that closes the last open ends of a region
leaves that region behind one seam. Such a rule breaks space into cells frozen apart, with infinite bond
distance between them.

## 3. A short boundary is a shortcut

**Proposition 3.** If U is two-sided connected and |δ(U)| = b >= 3, then δ(U) is a knot. Any two of its
distinctions are therefore at bond distance at most b − 1, however far apart their knots are.

*Proof.* δ(U) is a bond, by Proposition 1. ∎

**Consequence: closed strips collapse.** Take a strip whose consecutive pieces meet in c seams and whose
interior holds no open ends.
- **The region between two cross-sections** has boundary 2c, so the two cross-sections are at bond
  distance at most 2c − 1 at every length.
- **The three-seam strip of check 3.**
  - Its two-sided segments have boundaries of 6, as the proposition requires.
  - The exhaustive search finds more: seams any distance apart are joined by four-place knots, so
    bond distance stays 3 across all 31 beads. The bound 2c − 1 is an upper bound, and closed strips
    can collapse further.
- **The thread is the opposite.** It holds one open end per knot, so a region's boundary grows with its
  length, and so does its bond distance.

**What a ruler needs.** Bond distance grows with separation only if regions of large extent have large
boundaries, counting both seams and open ends inside.
- **On a lattice** the seams supply the growth: the perimeter grows with size (LOGIC-AXIS A).
- **On a line** only open ends inside can supply it, because a line's cross-sections stay bounded.

## 4. Two open ends grow the number line

**Proposition 4.** Start from one knot holding three open ends. Repeatedly choose any knot holding at
least two open ends and sprout at one of them: a new knot takes that distinction and two fresh open ends.
After n >= 2 knots:
- the knot graph is a path;
- the two end knots hold two open ends each, and every inner knot holds exactly one;
- the bond distance between open ends at knots u and v is |P(u, v)| + 1, the knots on the path plus one;
- consecutive seams are bonded at distance 1 + (the knots strictly between them) + 1.

*Proof.*
1. **Base.** After the first sprout the seed holds two open ends, the new knot holds two, and they share
   one seam.
2. **Induction.** If the graph is such a path, the knots holding two or more open ends are its two ends.
   Sprouting at an end leaves it with one open end and adds a new end knot holding two. Every choice of
   end and of open end gives a path of the same form.
3. **Distances.** The knot graph is a tree, so by `LOGIC-AXIS-20261107-001D`, Proposition 2, the bond
   distance between open ends at u and v is |P(u, v)| + 1. For seams, apply Proposition 1 to the path
   segment between them. ∎

**Reading.**
- **The rule.** "Grow where a knot holds two open ends" is a uniform local rule that reads only how many
  open ends a knot holds. It never chooses a direction, a lattice or a tip by age.
- **What it grows.** From one knot it grows the two-way thread: a logical number line extending in both
  directions, one open loop per unit.
- **Its ruler.** Bond distance along it counts the loops between two points. This is the parity version
  of the atom thread of `LOGIC-AXIS-20261107-001A`.

## Checks

`check.py` runs five checks, each with a rejected control (`result.json`):
- **Dependency digests.**
- **Proposition 1, by exhaustive search.** On 240 random pairs from 60 random grown knot graphs (4–9
  knots, mixed sprouting and closing), the least knot always equals the least two-sided boundary.
  Dropping the outside-connectivity condition changes the value on some pairs.
- **Proposition 2.** On random sealed one-seam clusters of 3, 5 and 7 knots, the seam is pinned and no
  knot crosses. The control is the two-seam example, where the seams are tied but knots cross.
- **Proposition 3.** On random two-sided regions the boundary is a knot. On the three-seam strip of 31
  beads:
  - segments of two or more beads have boundaries that are knots of 6;
  - cross-sections up to 29 beads apart are at bond distance 3.

  The control is a 31-knot thread, where links 8 apart are at bond distance at least 8.
- **Proposition 4.** 42 runs of the rule (n = 2..12, 40, 120 and 300, three seeds each) are all two-way
  threads. Bond distances agree by exhaustive search for n <= 10, and the whole-path cut is a knot of
  n + 2 for n up to 120. The control is random sprouting, which grows a knot joined to three others.

## Nonclaims

- These statements concern hub-free parity laws (every distinction in at most two knots).
- Proposition 4's rule gives dimension one. Nothing here grows a plane.
