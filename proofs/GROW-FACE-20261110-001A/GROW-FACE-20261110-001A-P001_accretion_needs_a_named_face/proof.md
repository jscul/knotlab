# Accretion needs a named face

Status: Partial (pre-registered 2026-11-10, before any computation)

Ticket `GROW-FACE-20261110-001A`, the board line's deciding epic.

## Setting (frozen)

- **Accretion laws.** Over abstract names (`BARE-NAMES-20261110-001A`): a board grows from a finite seed. A step picks a site and
  applies the law's action for the site's radius-r view (its graph and values, with no names): add one new place with a value, joined
  to the site and possibly to places of the view, or join the site to a place of the view. Values come from a finite alphabet. Places
  are never removed or merged.
- **Orders.** A growth order is fair when every action that stays enabled is eventually taken. A result belongs to the law only if it
  holds in every fair order (`GROWTH-LAW-20261107-001`). The limit of an order is the union of its boards.
- **Naming a face.** An action names a face when it closes a cycle: it joins a new place to two or more existing places, or joins two
  existing places. The cycle has length at most 2r + 2 and is fixed by the action's view.
- **Forcing the plane.** A law forces the plane when every fair order's limit is the square grid of Z².

## Targets

1. **G1, no named face, no plane.** A law none of whose actions names a face grows only forests: every limit is a tree. So it never
   grows the plane, nor anything of dimension two.
2. **G2, a named face and a carried marker.** A law that names the square and carries one moving marker grows the square grid in its
   only order: a spiral.
3. **G3, no marker, no plane in every order.** For every radius r, the square-closing law (coordinates mod 3 in the values, each place
   at most one neighbour at each unit offset, every visible square closed) has a fair order whose limit is not the square grid: a
   slit grown longer than the view and filled from both sides leaves two sheets.
