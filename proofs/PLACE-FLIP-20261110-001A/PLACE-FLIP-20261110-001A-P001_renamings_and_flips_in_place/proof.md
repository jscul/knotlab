# Renamings, transplants and flips in place

Status: Partial (pre-registered 2026-11-10, before any run of ticket B's census)

Ticket `PLACE-FLIP-20261110-001A`, the challenge of A59.

## Setting

As in `BARE-NAMES-20261110-001A`: a countably infinite set of names with no letters, a symmetric neighbour distinction for each pair
of names, a value for each name, and count laws of degree four. A **renaming** is a change from x to x ∘ π for a permutation π that
moves finitely many names.

## Definitions (frozen in the pre-registration)

- **A value flipped in place.** s(u) is flipped in place at x by a finite change of values alone, every neighbour distinction kept,
  that is allowed, flips s(u), is not a renaming, and is minimal: no allowed change of a proper subset of its values flips s(u).
- **A neighbour distinction flipped in place.** The same, with neighbour distinctions alone changed and every value kept.
- **Native in place.** A knot of one neighbour distinction n(u, v) and its endpoint values s(u), s(v) is native in place at x when
  all three are flipped in place there.

## Targets

1. **L1, renamings in a world of finite components.** A finite change is a renaming exactly when it keeps the multiset of
   isomorphism types of the components it touches. So a change of values on one copy of (B, c) is a renaming exactly when its new
   colouring is an automorphic image of c.
2. **L2, no renamings on trees.** In a world whose components are infinite trees, no change of values alone is a renaming.
3. **L3, the switch in place.** The switch of `BARE-NAMES-20261110-001A` (T5) flips a neighbour distinction in place when the edge
   lies on a cycle of a finite component, or in a tree world.
4. **L4, transplants.** When values and neighbour distinctions may change together, a place can be moved from one region to another
   by a finite rewiring that is not a renaming. So a count that excludes only renamings still excludes little, which is why the
   operative count holds the board fixed for values and the values fixed for neighbour distinctions.
5. **L5, cascades.** In the laws that never put a 0 beside a 1, and in law 48 (a 0 has four neighbours of value 1, a 1 none), no
   finite change of values alone flips a value in a tree world.

## Known before registration (disclosed)

L1 to L5 were sketched by hand while the registration was written, and ticket B's code was run on its control, the full law 1023.
