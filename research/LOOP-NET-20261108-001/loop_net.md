# Networks of loops

Epic `LOOP-NET-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `LOOP-ANY-20261108-001` proved that a balanced loop of any number of rings keeps every contact binding both
  of its rings at every lag, at every ring size. The coordinator relayed its direction 1 on 2026-11-08: networks of loops, rings with
  three or more contacts. Give one ring a third contact so that two loops share it, find the balance condition for each loop, and stop
  at persistence of every contact at every size or at the obstruction where the loops meet.
- **The question.** When loops share rings, can the influence returning to each contact still cancel, and what decides it?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **A contact keeps its witnesses exactly when its returns cancel.** In any network of rule-60 rings joined by left-reading contacts, the two cells a contact reads last on its rings have coefficient D_cc · z/(1 + z) in its value, D = (I + K)^(−1) for the weighted contact graph. They hold at every lag exactly when the closed walks returning to the contact cancel. | proved; checked on 400 random networks | A |
| 2 | **Positions make a surface.** The order of the contacts round each ring embeds the ring graph in an oriented surface. The contact graph is its directed medial graph: walks that keep to one ring go round rings, walks that change ring at every contact go round faces. | proved | A |
| 3 | **Balance is equal density.** The balance condition for a network of loops is per face: every ring and every face carries the same number of cells per contact. Then the network is uniform, and a contact's returns cancel exactly when the number of returns of each length is even. | proved | A |
| 4 | **Symmetry cancels returns.** A symmetry that fixes a contact and exchanges its two rings pairs its returns. So every orientably regular network persists at every lag at every size: loops of any length, two rings sharing any number of contacts, the five Platonic networks, and square, triangular and honeycomb lattices of rings on a torus. | proved; checked on 84 networks and on full state spaces | A |
| 5 | **Where a loop meets a larger ring, one return is unpaired.** At a contact joining a ring of two contacts to a ring of three or more, the only short return goes back and forth across the two-contact ring, and nothing cancels it. In a uniform network the witnesses there lapse, first at lag 2κ + 1. Every figure-eight with a loop of three or more rings, and every chord across a loop of three or more rings, has such contacts. | proved; checked on 264 networks | A |
| 6 | **At equal ring sizes nothing else cancels them.** Of 170,502 figure-eights and chords with every ring of the same size 5 to 9, none cancels every return except 20 degenerate ones. 500 persist to lag 300 through other cells, none of them a figure-eight of two three-ring loops or a theta (2, 2, 2). | exploratory census, exact | B |
| 7 | **Even returns need no symmetry.** Of 395 plane ring graphs of 2 to 7 rings, 8 have every return count even: the 7 with a symmetry at every contact and one six-ring graph without. | exploratory census, exact | B |
| 8 | **Other cells rescue some, never at every size.** Equally spaced, eight figure-eights and chords all miss a ring by lag 600 at spacings 2, 3, 4, 8 and 16. At spacings 5, 6, 7 and 9 some persist at every lag through other cells; the flat figure-eight of two three-ring loops misses a ring as late as lag 1,143. | computed | A, check 9 |

## Answer

The stop rule's two outcomes both occur, in different networks. Where loops share rings symmetrically, every contact persists at every
size: two rings sharing three contacts, the Platonic networks, and lattices of rings on a torus, the honeycomb lattice having three
contacts on every ring. Where a loop of two-contact rings meets a shared ring with more contacts, the returns cannot cancel. That is the
construction the go-ahead named: giving one ring of a loop a third contact makes such meeting contacts, and there the witnesses lapse.
At equal ring sizes no other placement cancels the returns either, and no equally spaced figure-eight or chord persists at every size.

## Reading

**Interpretation, not a theorem.**
- **What balance means for a network.** For a single loop, balance was a sum of positions. For a network it is a density: every ring
  and every face carries the same number of cells per contact. A ring shared by more loops must then be larger, in proportion to its
  contacts.
- **Why the meeting contacts fail.** A contact on a two-contact ring has a short return: across that ring and back. In a single loop
  the ring on the other side has one of the same length, and the two cancel. At a ring with more contacts the other side's shortest
  return is longer, so the short one stays.
- **What the symmetric networks have in common.** Every contact looks the same from both of its rings, so its returns pair up. That
  rules out a ring that differs from its neighbours, which is exactly what a shared ring in a figure-eight or a chord is.
- **For composed topology across time.** The lattices of rings on a torus are the first two-dimensional arrangements of contacts that
  all persist at every size, by proof. The lattice is given, not grown from a law, so this is not G1's space from a law. Whether
  contacts far apart in the lattice compose, and whether cuts separate it, is the next question.
- **Not a metric.** Density is used only in an equality, as the sum of positions was for loops. Nothing here is a length or distance.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Regular networks persist (4) | square torus of side 7, triangular and honeycomb of side 6, the Platonic networks at spacings 5 and 6, a loop of 9 rings, two rings sharing 7 contacts | pass: 22 networks, every return count even, persistent to lag 300 |
| The meeting contacts (5) | figure-eights with a loop of 7 rings, chords with a path of 5 contacts, both embeddings, spacings 2, 3 and 6 | pass: 36 networks, N_2 = 1 and the lapse at 2g + 1 |
| No other cancellation (6) | four families at ring size 10 | pass: 73,920 placements, none non-degenerate cancels every return; 72 persist to lag 300 |

## Literature and provenance

- **Sources.** Generating functions over GF(2); determinants as sums over disjoint cycles; rotation systems and medial graphs;
  orientably regular maps, whose rotations act transitively on darts (Coxeter and Moser; Jones and Singerman 1978); the regular maps
  {4,4}, {3,6} and {6,3} on the torus. Boolean automata networks of intersecting cycles have been studied for their dynamics (Demongeot,
  Noual, Sené and coauthors), not for this cancellation.
- **Classification.** Ticket A: known-with-delta. The delta is reading persistence across time as the cancellation of returns in the
  medial graph, the cancellation by edge-reversing symmetry, and the local obstruction at a two-contact ring. Ticket B: new as far as
  found, a census.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Scope.** Rule-60 rings (rule 102 by mirror symmetry) with law (12, 12) at every contact.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with ten checks, and one census (B).
- **Administrative.** This note and the closure.

## Pending the owner

- **Counted length as a native magnitude**, which gates distance across time; put to the owner by the coordinator.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — networks of loops | **Status:** Successful | Symmetric networks persist at every size, by proof; where a two-contact loop meets a shared ring the returns cannot cancel |
| Local direction — composed topology across time | Continue | Lattices of rings now persist; composition and separation across them come next |
| Broader exploration — G5 with G1 | Known alternatives | Why other cells rescue some chords; even returns without symmetry; the rule-90 mechanism (B13); restrictions (B14); distance, once the owner rules |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Networks of loops sharing rings, lattices of rings on a torus among them, keep every contact at every size, by proof |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - Whether contacts far apart in a lattice of rings compose, and whether a ring of cuts separates the lattice.
  - Why other cells keep some chords persistent at most spacings, and never at powers of two.
  - Which networks have even return counts without a symmetry.
- **The missing bridge to the program's composed topology.** Native paths and separation across a lattice of rings, the
  two-dimensional version of what `RECUR-PROOF-20261108-001` and `SEPARATE-20261108-001` did for paths and cycles.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Composition and separation across a lattice of rings (G5, with G1) | 3/3 — Major | 2/3 — Testable | On the equally spaced square torus, find which contacts each contact needs and at which lags (the support of D's row), prove its shape, then test whether cutting a ring of contacts separates the torus → a theorem for the square lattice, or the size where composition stops reaching | Selected · not started |
| 2 | Why other cells rescue figure-eights and chords (G5) | 2/3 — Substantial | 2/3 — Testable | Find the cells that bind the chord (1, 1, 2) at spacings 5 to 15 and prove why they fail at powers of two → a second mechanism, or its failure | Alternative · deferred |
| 3 | Even returns without symmetry (G5) | 2/3 — Substantial | 1/3 — Stated | Explain the six-ring exception and search plane graphs of 8 to 10 rings → a criterion, or more exceptions | Alternative · deferred |
| 4 | Distance across time | 3/3 — Major | 1/3 — Stated | Waits on the owner's ruling on counted length | Alternative · deferred |

1. **Across the lattice.**
   - **Payoff 3.** Native paths and separation across a two-dimensional arrangement of persistent contacts would bring the program's
     order (adjacency, paths, separation) to a lattice across time.
   - **Concreteness 2.** D's rows are computable exactly and cuts act as in `SEPARATE-20261108-001`; the shape of D's support is the
     open part.
   - **Uncertainty.** In some lattices the feedback is finite and influence may reach only part of the torus.
2. **Other cells.** Narrower; it explains exceptions rather than a structure.
3. **Even returns.** One example so far; the criterion is unknown.
4. **Distance.** Waits on the owner.

**Recommendation.** Continue with direction 1. The process line has run fifteen epics today, so if the coordinator prefers to pause it
until the owner rules on distance, the network results stand as a complete stage.
