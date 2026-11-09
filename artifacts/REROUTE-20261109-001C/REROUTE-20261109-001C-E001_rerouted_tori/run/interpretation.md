# Re-routed lattice tori, a census: interpretation

Experiment `REROUTE-20261109-001C-E001` (exploratory), run once on 2026-11-09 under the frozen contract (pre-registered in 8291ad565),
in 8.5 s on 16 workers. Exact: persistence through the unchanged contact graph (and directly on the 80 networks of at most 300
contacts), flips built from one dart, and the plain first need of every ring for every target by shortest routes. Every row is in
`result.json`.

## Control

Every one of the 120 networks has its torus's contact graph, so every contact persists (REROUTE-20261109-001B, Theorem 1); read
directly, every contact of the 80 networks of at most 300 contacts persists. All 120 are non-degenerate: rings and faces of at least
three contacts and no doubled pair. On the 8 × 8 tori every contact sends and hears, a property of the contact graph.

## Primary observable

| Start | Networks | Face toggles kept | Contacts with a flip | On time | Rings of at most 12 contacts late for some target (n ≥ 12) |
| --- | --- | --- | --- | --- | --- |
| the torus | 60 | 39 to 398 per network | none | none (34% to 48% of (ring, target) pairs late, by lattice) | 4,006 of 4,006 |
| its line network | 60 | none: every toggle made a contact join a ring to itself | every contact | all 60 | none (rings of 2n or 3n contacts) |

- **H1 fails, but only on the line networks.** The 60 random re-routings from the torus have no flip at any contact, with rings of 3 to
  69 contacts and genus 15 to 189: large, non-degenerate, non-periodic networks persistent without flips are what a random re-routing
  gives. From the line network not one of the 4n² face toggles could be kept, so those 60 networks are the line networks themselves,
  with a flip at every contact.
- **H2 fails the same way.** The 60 line networks are on time, as REROUTE-20261109-001B, Theorem 2, proves (square) and computes
  (triangular, honeycomb). Every random re-routing is late; 6,538 of their 6,540 rings are late for some target.
- **H3 holds.** On tori of n ≥ 12 every ring of at most 12 contacts is late for some target, 4,006 of 4,006, on all three lattices: the
  mechanism of Theorem 3, proved for the square contact graph, is seen on the triangular and honeycomb ones too.
- **Ring balls.** The random re-routings' ring graphs grow faster than linearly (at n = 16 a ball of radius 4 holds 47 to 126 of 166 to
  352 rings); the line networks' grow by 2 rings per step.

## Reading against the decision rule

H2 fails only on the line networks, whose ring balls grow linearly, so no plane read plainly appears. The census answers B42's first
question: large networks persistent without flips are generic among re-routings of a torus. None reads its distance plainly; the ones
that do are the line networks, isolated under face toggles, and small rings are late on every lattice read.

## Nonclaims

- **Exploratory and finite:** the roster only; face toggles reach only part of the re-routings.
- **Two-time knots only** (A30); equally spaced rings only; each network read as fixed (A42).
