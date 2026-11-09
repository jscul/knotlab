# The S6 exception is a three-way tie between lifts

Status: Proved by exact reading. The finite claims are checked in `check.py`.

Ticket `GROW-PLAIN-20261109-001A`, 2026-11-09.

## Standard statement

- **The map.** The one orientably regular map of genus at least 2, among the 1,762 read by `RESCUE-GENUS-20261109-001A-E001`, that is
  on time although some ring has no closest contact reached by a single shortest route: a map of S6 of type (6, 6), genus 61, 120 rings
  and 360 contacts (two generating pairs, with identical readings), equally spaced rule-60 rings with law-(12, 12) contacts.
- **Homology mod 2.** Two shortest routes with common ends close a loop on the map's surface; its edges, mod 2, are a cycle of the ring
  graph, null-homologous mod 2 when it lies in the span of the face boundaries.

**Proposition.** Two rings of the map are rescued only by odd counts of several routes. Each has three closest contacts, at distance 9 from
the target, reached by 2, 3 and 2 shortest routes. Every pair of shortest routes to any of them closes a loop that is not null-homologous
mod 2: the routes run round different handles, so each comes from a different lift of the target in the universal cover, one route per
lift. The count 3 is three lifts at one distance, an odd tie between lifts. The half-turn about the target exchanges the two rings.

## Proof

Check 1 finds the map and the two rings by breadth-first search from the target, with exact route counts. Check 2 confirms that the 120
face boundaries span a space of dimension 119 and that the genus is (360 − 119 − 119)/2 = 61. Check 3 lists every shortest route to the
six closest contacts, forms the loop of each pair and reduces it against the face boundaries: none reduces to 0. Distinct classes in
homology mod 2 are distinct classes in homotopy, so the routes end at distinct lifts of the target. Check 4 applies left multiplication by
y, the half-turn of the target contact, to the rings. ∎

## Remarks

- **Why tori never do this.** On a torus the lifts of a ring nearest the target lie one on each side of a tube or are finitely many in a
  small torus (`RESCUE-MAP-20261109-001A`), and no on-time torus uses an odd tie. On a surface of genus 61, a ball of radius 9 already wraps
  round several handles, and three lifts can arrive at once.
- **It is parity, not a single fastest way.** No route to the ring is the unique fastest one; the ring is on time only because 3 is odd.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The map (six generating pairs of S6 of type (6, 6) and genus 61 read; two give it, with identical readings) and its two rings | pass |
| 2 | The face boundaries span 119 dimensions; genus 61 | pass |
| 3 | Every pair of shortest routes to each of the six closest contacts runs round a handle | pass |
| 4 | The half-turn about the target exchanges the two rings | pass |

## Nonclaims

- **One map.** No second such map is known; `RESCUE-GENUS-20261109-001A-E001` found none among 1,762.
- **Homology mod 2** separates the routes; finer classes are not computed.
- **Two-time knots only** (A30).
