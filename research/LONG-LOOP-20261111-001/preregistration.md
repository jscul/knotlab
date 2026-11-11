# The long-loop regime: pre-registration

Epic `LONG-LOOP-20261111-001` (NAE-SURFACE-20261111-001 direction 1, with KNOTS-ALONE-20261111-001 direction 2; G1, question 9;
program topology, group spacing), 2026-11-11, at the coordinator's go-ahead. Frozen before any law is run on any world of the list
below; nothing changes after results. Under challenge: A63, with the surface count given (A64; NAE-SURFACE showed the count is an
input). The canonical K1–K3 test is unchanged.

## The question

On 6-regular surface worlds of three-place knots alone, the not-all-equal law (NAE) was faithful on every world in
`KNOTS-ALONE-20261111-001`'s range whose short loops have length at least 5, and its bond distance was graph distance + 1 out to
distance 2, with distance 3 shortened on some thin tori. Both readings came after the run. This epic freezes them one size range up.

## Definitions (frozen)

- **Worlds.** Every 6-regular triangulated torus with 49 to 80 distinctions (the triangular lattice modulo a sublattice of index V;
  complete by Altshuler), and every 6-regular triangulated Klein bottle with 19 to 40 (the lattice modulo a group of translations
  and one glide reflection; complete because a flat triangulation's deck group is translations and glides). One per isomorphism
  class. Before freezing, the glide construction gave exactly the exhaustive SAT Klein bottles of `KNOTS-ALONE-20261111-001` at
  every V from 7 to 18 (no law run); the frozen code checks this again at 7 to 16 by isomorphism class.
- **Edge-width.** The least length of a non-contractible closed walk: the least lattice distance from a point to its image under a
  non-identity deck element.
- **Faithful, bond, bond distance.** As in `KNOTS-ALONE-20261111-001`, by its frozen `read_law_sat` (hash checked). Bond distance
  β(u, v) is the least size of a bond through u and v, minus one.
- **The distance-3 reading.** On each torus of edge-width at least 6 that NAE reads faithfully, from distinction 0 (tori are
  vertex-transitive): for every v at graph distance 3, (i) no bond of four elements contains 0 and v, searched over every pair of
  other distinctions; (ii) some bond of five elements contains 0 and v, searched among the distinctions within distance 2 of 0 or v.
  Pattern extension by a seeded sample of 4,000 states, then SAT for every pattern not seen, so each answer is exact.

## Settled before the run (said up front)

- **Distance 1, by definition.** In a faithful world every knot is a bond, so β = 2 between co-knotted distinctions.
- **Distance 2, by a short lemma (proved; to be refereed).** Let W be a surface world, every distinction in d ≥ 4 knots, with no
  non-facial triangle, and let NAE read it faithfully. If u and v are at graph distance 2, then β(u, v) = 3.
  - *Lower bound.* Bonds have at least three elements, and in a faithful world the three-element bonds are the knots; u and v are in
    no common knot.
  - *Upper bound.* A common neighbour h has u and v in its link, a d-cycle, at cycle distance at least 2. Choose link neighbours u′ of
    u and v′ of v with the edges uu′ and vv′ disjoint. The pattern u = u′ = 0, v = v′ = 1 forces h = 1 through the knot {h, u, u′}
    and h = 0 through {h, v, v′}, so S = {u, u′, v, v′} is constrained. No three of S form a knot: that would make two link
    vertices of h adjacent that are not consecutive in its link, a non-facial triangle. So every 3-subset of S is free, by
    faithfulness, and S is a bond.
  The frozen code checks this lemma on every torus it measures (a four-element bond through 0 and each v at distance 2, found among
  nearby distinctions).
- **States exist on large tori (known).** Eulerian triangulations of orientable surfaces with large edge-width are 4-colourable
  (Hutchinson, Richter and Seymour), so NAE has states there. Faithfulness is not known, and nothing was found on the least
  non-shattered sets of the solution set; P1 and P2 at distance 3 are computational.

## Predictions (frozen)

- **P1.** NAE is faithful on every torus and every Klein bottle in the list of edge-width at least 5. *Fails* if one is not.
- **P2.** On every torus in the list of edge-width at least 6 that NAE reads faithfully, β(0, v) = δ(0, v) + 1 for every v with
  δ(0, v) ≤ 3: at distance 3, no four-element bond through 0 and v, and a five-element bond through them nearby. *Fails* if a
  four-element bond is found at distance 3, or no five-element bond is found in the region searched (counted as a failure, not as
  undecided).
- Worlds of edge-width 3 and 4 (and distance 3 on tori of edge-width 5) are reported, with no prediction.

## Decision rules

- **P1 and P2 hold.** Within the surface count, NAE reads every long-loop flat world in range faithfully and spaces it as graph
  distance + 1 to distance 3 (computed; distance 2 proved given faithfulness). A63 is then overturned in the knots-alone setting, with
  the surface count given and the evidence computed in range, as its history line anticipated.
- **Either fails.** A63 stands; the failing worlds or distances are reported.

## Disclosed before freezing

- The world list was generated and counted, with no law run: 562 tori (edge-width 3 to 10; 434 of at least 5, 349 of at least 6) and
  66 Klein bottles (edge-width 3 to 6; 15 of at least 5).
- Controls outside the list ran the whole pipeline on six tori with 21 distinctions: the global four-element search finds bonds at
  distance 3 on the edge-width-4 tori (the shortcuts `KNOTS-ALONE-20261111-001` saw), finds none on the edge-width-5 one, and the
  distance-2 lemma check passes on all faithful ones; so the distance-3 test can fail.
- Expected runtime: about half an hour on 12 workers; registered in `docs/LONG_RUNNING.md`, run under `systemd-run --user -p
  MemoryMax=16G -p MemorySwapMax=0`.

## Stop rule

One run on the frozen list; then report and hold for a go-ahead.
