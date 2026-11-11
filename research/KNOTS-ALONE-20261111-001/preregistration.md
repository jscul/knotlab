# Knots alone: pre-registration

Epic `KNOTS-ALONE-20261111-001` (backlog B144, G1, question 9; program topology, group spacing), 2026-11-11, at the owner's
go-ahead ("Yes, please continue on with this", relayed by the coordinator). Frozen before any law is run on any world of the family
below. Under challenge: A62 (a law gives a shape only by forcing it) and A63 (a named face is put in, not native). The canonical
K1–K3 test is unchanged.

## The question

A world is a finite set of distinctions and a set of three-element subsets of it, its knots. Nothing else is given: no board, no
names (everything is read up to isomorphism), no declared faces, no infinite set. A uniform law puts one symmetric three-place
relation on every knot. The symmetric three-place relations that pass K1–K3 (`knotlab check`, run 2026-11-11: all four are knots)
fall into four classes up to complementing every distinction:

| Law | Weights allowed | Note |
| --- | --- | --- |
| PAR | {1, 3} | parity; complement {0, 2} |
| NAE | {1, 2} | not all equal; its own complement |
| OR | {1, 2, 3} | the clause; complement NAND {0, 1, 2} |
| NOL | {0, 2, 3} | not exactly one 1; complement {0, 1, 3} |

Uniformity of the world: every distinction lies in d knots. The surface condition: every co-knotted pair lies in exactly two knots
and every link is one cycle, so the knots span a closed triangulated surface. This condition counts how knots meet at a distinction;
a stricter reading in the spirit of A61 would call the link's fixed length a named dual face, and P3 asks whether any law supplies
the condition by itself.

**Readings**, all from the world's allowed states with every other distinction quantified away: *allowed* (some state); *frozen*
(a distinction with one value); *tie* (a pair of unfrozen distinctions missing a value pair); *3-bond* (a triple whose pairs are
free and whose eight patterns are not all allowed: a three-place knot of the world); *native* (allowed, and every knot of the world
is a 3-bond); *faithful* (native, no frozen distinction, no tie, and the 3-bonds are exactly the world's knots, so the world is
recovered from its allowed states); *bond distance* β(u, v): the least size of a bond through u and v, minus one (a bond: a
constrained set of three or more whose every co-1 subset is free; `knotlab.space.bonds`). δ(u, v) is the drawn complex's graph
distance, used only to compare.

## The question in standard terms

For a closed triangulated surface (or a d-regular 3-uniform hypergraph), consider the Boolean constraint satisfaction problem with
one symmetric constraint on each triangle. Which instances are satisfiable without frozen variables; when is the triangulation the
set of minimal non-shattered triples of the solution set (the shatter complex of the solution set recovers the surface); what is
the least non-shattered set with shattered facets containing two given vertices; and which surfaces are excluded by each constraint?

## What is settled before the run (said up front)

These hold by definition or by short arguments, which the referee checks; the census reproduces them as controls of the code.

- **D1, curvature is counting.** On a surface world with every distinction in d knots, the Euler characteristic is
  V − dV/2 + dV/3 = V(6 − d)/6. The curvature sign, flat exactly at d = 6, follows by double counting and has no knot content:
  B144's old P1 is settled by definition.
- **D2, covers.** If p: W′ → W is a covering of worlds (a surjection that is a bijection from the knots at each distinction onto
  the knots at its image), allowed states lift by composition, and nativeness lifts too: each knot's projection in W′ contains
  that of its image and lies inside the relation. Flat and hyperbolic surfaces have connected covers of every degree, so at d ≥ 6
  no law fixes size. B144's old P2 said that no law fixes size or global shape; that was too general, since a world can have no
  proper cover (correction of 2026-11-11, `docs/CORRECTIONS.md`, Narrowing).
- **D3, classical lists.** At d ≤ 5, D1 gives χ > 0, so the world is a sphere or a projective plane with at most 12 distinctions:
  exactly the tetrahedron (d = 3), octahedron (4), icosahedron and hemi-icosahedron (5). At d = 6 the tori are the triangular
  lattice modulo a sublattice (Altshuler 1973, T(r, s, t)), and there are Klein bottles. At d ≥ 7 there are worlds of every
  higher genus.
- **D4, the clause reads every world faithfully and spaces nothing.** Under OR, set every distinction outside a set S to 1: any
  pattern on S extends unless S contains a knot. So the free sets are exactly the sets containing no knot, the bonds are exactly
  the knots, every world is allowed, native and faithful, and β is 2 between co-knotted distinctions and undefined otherwise. Under
  A39 a shared distinction of two OR knots is a gate (its value 1 satisfies both), so OR's worlds are hubs, not spaced.
- **D5, parity collapses.** Under PAR, two knots sharing a pair force their other two distinctions equal (subtract the two
  equations): a tie across every edge. On a connected surface world these equalities make the distinctions constant on the classes
  of a proper 3-colouring when one exists (every knot rainbow), leaving 4 states, ties inside each class, and every rainbow triple a
  3-bond: native, never faithful. When none exists, some knot has two distinctions in one class and its third is frozen. The flat
  plane is read as one three-place knot copied over the world.
- **D6, not-exactly-one is the hard-core law with a hub state.** Under NOL, two co-knotted zeros force the third distinction of
  each of their knots to zero, and on a connected surface world this spreads everywhere. So the states are the all-zero state and
  the states whose zeros are pairwise non-co-knotted (independent sets of the 1-skeleton). Every surface world is native; the
  3-bonds are exactly the triples containing a co-knotted pair; there are no larger bonds; β = 2 between every two distinctions.
  Faithful only on the tetrahedron.

So three of the four laws are settled by short arguments. **NAE is the open case**, and the census's content is NAE's readings,
together with the non-surface family and the controls. What the K1–K3 reading adds beyond the classical facts: whether the drawn
surface is recovered from allowed states alone (faithful), whether its knots compose into a ruler (bond distance), and which global
features a law fixes by excluding worlds.

## Frozen family and method

- **Surface worlds.** d = 3, 4, 5: every V (complete by D1), enumerated by SAT to V = 12. d = 6: every surface with 7 ≤ V ≤ 16
  (exhaustive SAT: tori and Klein bottles), and every lattice torus with 17 ≤ V ≤ 48 (complete for tori by Altshuler). d = 7, V = 12:
  the classes the SAT search finds within 600 seconds, a sample. The SAT search fixes distinction 0's link and breaks label
  symmetry by breadth-first order (sound); isomorphism classes by flag codes.
- **Non-surface worlds.** For d = 3 to 7 and 6 ≤ V ≤ 12 with 3 | dV, a seeded SAT sample (random phases) of at most 60 connected
  d-regular triple systems per (d, V), surfaces removed; biased, for existence only.
- **Laws.** NAE by SAT on every world; PAR by GF(2) elimination on every world; OR and NOL by SAT where V ≤ 20. Independent paths:
  brute force over all states for V ≤ 16 (all four laws), SAT against GF(2) for PAR where V ≤ 20, and complements for V ≤ 12.
- **Bond distance.** Every lattice torus with 12 ≤ V ≤ 24, from distinction 0 (lattice tori are vertex-transitive), all bonds of
  size at most 6 (so β ≤ 5 is measured, larger reported as none), from the full list of allowed states; NAE on all of them, and OR,
  NOL and PAR as lemma controls on 12 ≤ V ≤ 16. Cross-checked against `knotlab.space` on the smallest torus.
- **Code.** `experiments/KNOTS-ALONE-20261111-001A/KNOTS-ALONE-20261111-001A-E001_knots_alone_census/` (`knots_alone.py`,
  `census.py`), hashes in `contract.json`.

## Predictions (frozen)

- **P1, positive curvature (A62).** NAE is faithful on the tetrahedron, the octahedron and the icosahedron and allows no state on
  the hemi-icosahedron. With D3, NAE at d = 5 then fixes one world, the icosahedron: a uniform knot law fixing global shape and size.
  *Fails* if any of the four outcomes differs.
- **P2, flat worlds are read faithfully (A63, part one).** NAE is faithful on every flat world in range without a non-facial
  triangle (three mutually co-knotted distinctions that are not a knot; in a flat world, a non-contractible 3-cycle), and allows no
  state on the 7-vertex torus K7 (known: its face hypergraph has no 2-colouring without a monochromatic face). *Fails* if some flat
  world without a non-facial triangle is not read faithfully. Flat worlds with a non-facial triangle are reported, with no
  prediction.
- **P3, the law does not supply the surface condition.** For each law and each d = 3 to 7, the sample has a native world that is
  not a surface, and for NAE a faithful one. *Fails* for a (law, d) whose sampled worlds include no such world (reported as not
  found, which a sample cannot turn into an absence).
- **P4, orientability among flat worlds.** NAE allows states on some Klein bottle and on some torus in range, so it does not fix
  orientability; PAR allows exactly the 3-colourable flat worlds (D5), which are reported by orientability. *Fails* if NAE allows no
  Klein bottle in range.
- **P5, NAE's knots compose into a ruler (A63, part two).** On every lattice torus with 12 ≤ V ≤ 24 that NAE reads faithfully,
  β(0, v) = δ(0, v) + 1 for every v with δ(0, v) ∈ {1, 2, 3}: a bond of three around one knot, of four around a hidden distinction
  (two of its link's edges forcing it both ways), of five around a hidden edge. *Fails* at any v where β ≠ δ + 1, none found
  included.

## Decision rules

- **A63.** If P2 and P5 hold, the not-all-equal knot alone, with the surface count, reads the flat world from its allowed states
  and spaces it as a ruler: flat local geometry is native with nothing named but the knot and how many knots meet. A63 is then
  overturned in this setting, with the caveat about the surface condition and with P3 saying whether a law supplies it. If P2 holds
  and P5 fails with finite β, the world is spaced but not as δ + 1, and the measured law is reported. If β is mostly undefined
  beyond adjacency, A63 is narrowed (faces recovered, not spaced, as under OR). If P2 fails, A63 stands for NAE on flat worlds.
- **A62.** If P1 holds, a uniform knot law fixes global shape and size at positive curvature, and by D2 none fixes size at d ≥ 6:
  forcing reads global shape only where a world has no cover, and the co-real reading (what every allowed world shares) covers the
  rest. A62 is then narrowed accordingly.

## Disclosed before freezing

- The world enumerator was run on d = 3, 4, 5 (the classical list reproduced), on d = 6 to V = 16 to time it (lattice tori agree
  with the SAT tori at every V), and on d = 7, V = 12 for 120 seconds (34 classes, incomplete). No law was run on any world of the
  family.
- Controls outside the family (one knot, two knots on an edge, the pentagonal bipyramid, a 6-regular triple system on 15
  distinctions): SAT, brute force, GF(2) and `knotlab.space` agree; the lemma checks pass on them. Mutations are rejected: a wrong
  law against brute force, a dropped knot under GF(2), NAND under the D6 count, shifted bond distances against knotlab, one torus
  dropped from the lattice comparison, a pinched vertex under the surface check.
- A timing control (a random 6-regular triple system on 48 distinctions) reads in under a second.
- Expected runtime: under an hour, registered in `docs/LONG_RUNNING.md` and run under `systemd-run --user -p MemoryMax=16G -p
  MemorySwapMax=0`.

## Stop rule

One run on the frozen family; a stress test one size past (lattice tori to 30 distinctions for P5, Klein bottles at V = 17 and 18
for P4 and P2) after the run. No extension of the laws, the readings or the ranges in this epic.

## Corrections after freezing (2026-11-11)

Found by the referee, logged in `docs/CORRECTIONS.md` (Not a block); the text above is left as frozen.
- D3's "at d ≥ 7 there are worlds of every higher genus" fails for χ = −1 (no surface world has it).
- P4's "PAR allows exactly the 3-colourable flat worlds" should read "is native on": PAR allows the all-ones state everywhere.
- The A62 rule's "a uniform knot law fixing global shape and size" credits the law with what the surface condition and d do; NAE
  only removes the projective plane at d = 5.
- The frozen code's filter d ≤ V − 1 dropped the registered cells (6, 6) and (7, 6); they were run afterwards
  (`omitted_cells.py`), with P3 unchanged.
