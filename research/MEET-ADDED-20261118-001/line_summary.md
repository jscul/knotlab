# How the knots meet, read against the line: the MEET line's closing summary

2026-11-18. Six studies, run in one thread on the coordinator's picks, from `KNOT-CAP-20261117-001`'s second direction (why the
line of five's placements of a shared distinction grow different numbers of orders): `MEET-ORDERS-20261118-001`,
`MEET-GROW-20261118-001`, `MEET-TWIST-20261118-001`, `MEET-DIST-20261118-001`, `MEET-HIST-20261118-001` and
`MEET-ADDED-20261118-001`. All six are refereed and folded in. The coordinator closed the line here as practically exhausted at
these sizes.

**Scope throughout.** Fewest-knot presentations of a line by betweenness knots (A100), the growth rule KF3 of
`STATE-RULES-20261117-001` (A99), exact laws (no sampling), prior uniform over labelled presentations where a share is given.

## The question

The line's states are the same for every presentation, yet KF3 grows different numbers of orders from different presentations.
What is it about how the knots meet that the states do not carry, and how far is it a distance (A97, the owner's founding
premise)?

## What is proved

| Result | Where |
| --- | --- |
| **Lemma 0.** The fewest-knot presentations of a line of n are exactly its bracketings (n − 2 knots, Catalan(n − 2) per labelling): every knot has its middle between its ends, and each knot but the ends' knot lies directly within one half of another. | `MEET-ORDERS-20261118-001` |
| **Lemma C.** On a line with fills of triples, two orders exactly when some fill exists and no fill's middle lies strictly between another fill's ends without being its middle. | `MEET-ORDERS-20261118-001` |
| **Theorem 1.** Under KF3 the chance of two orders after the second new distinction is (1/(n − 2)) Σ_κ [s + 2p + c] / [(n − 3) + 2(p + c)], a function of the bare bracketing: 5/12 for chains (shared distinction at an end or next to an end), 11/18 for the middle, 51/140 for both six-starts. (Lemma B by compression and a finite check on all 6,916 bracketings to eleven.) | `MEET-ORDERS-20261118-001` |
| **Theorem 2.** Moving the ends' pair one step round the cycle of a presentation's knots, keeping every distinction's odd set, carries KF3's options knot by knot (knots change role but pin the same states and add the same pairs). So every two presentations with one meeting pattern grow their co-knotted pairs by one law, for every line length, through the steps before the first added state, which comes within 2^(n0 − 1) distinctions. | `MEET-TWIST-20261118-001` |

**Known results, and what this view adds.**
- *Triangulations, bracketings and binary trees* (Catalan); *rotations* and the Tamari lattice (Sleator, Tarjan and Thurston 1988);
  the *dihedral symmetry* of triangulations, which re-roots the binary tree; the *unique Hamiltonian cycle* of a maximal outerplanar
  graph. What this view adds: the line's states hold the line, and how its knots meet is a triangulation that the states do not
  show, which the growth reads through its co-knotted pairs.
- *Minimal defining sets.* In phylogenetics every rooted binary tree on n leaves is defined by n − 2 rooted triples, and all minimal
  defining sets have that size (Steel; Grünewald, Steel and Swenson 2007). Lemma 0 has the same count for a different object: there
  one tree has many minimal triple sets, here one line has many minimal presentations, exactly its triangulations. It also differs
  from order-theoretic betweenness (Opatrny 1979), where the consecutive triples fix the order: here they do not present the
  line's states.
- *Lattice dimension* by chain covers of splits (Eppstein 2005). Lemma C reads it for fills of triples.
- *The program's own:* the disagreement table with the state count determines these bases (`DISTANCE-ORDER-20261117-001`, 3(a)),
  so here "what the distances hold" equals "what the states hold".

## What is computed

- **The bare bracketing decides the number of orders through the third new distinction**, and separates bare bracketings, for
  every presentation of 5 to 9 distinctions; at the fourth the halves' order (same way, other way) enters, with ties from eight
  (one pair at eight, 24 of 217 at nine). Next to an end equals the end through n = 8 and parts at n = 9; the six-starts agree
  through n = 9 and part at n = 10. (`MEET-ORDERS-20261118-001`)
- **The meeting pattern grows by one law wherever it sits.** For all 1,049 pairs of presentations of 5 to 9 distinctions with one
  meeting pattern, one renaming carries the labelled law of the grown co-knotted pairs, state by state; different patterns grow
  differently; the number of orders differs within every pattern with several presentations. The pairs are not a process by
  themselves: the states steer which come next. (`MEET-GROW-20261118-001`; proved by Theorem 2 in its range)
- **How much of the nesting the grown distances hold.** One grown base's disagreement counts, read on unnamed distinctions, carry
  about 0.4 to 0.7 of the information about the bare bracketing (peaking and then falling for five to seven, still rising at eight
  and nine); read with the distinctions' names, all of it at five and 0.91 at six; in law, all of it from the first new
  distinction. (`MEET-DIST-20261118-001`)
- **Where the rest sits.** It is a small part of the order of growth (0.22 to 0.36 bits), which the states do not determine even
  with the line's distinctions named (the order is 85 to 90% undetermined); knowing which distinctions are the line's adds little.
  (`MEET-HIST-20261118-001`)
- **Told which knots the growth added**, a reader of the grown states recovers what the full names give, exactly at five and six
  and within 0.0002 at seven, where the order of three fills carries a real sliver (44 merged classes). Neither the states nor the
  added knots suffice alone, and given every knot, old and new mixed, the nesting is read at once. (`MEET-ADDED-20261118-001`)

## Corrections in the line

All logged in `docs/CORRECTIONS.md` with knotlab's `HISTORY.md`:
- `KNOT-CAP-20261117-001`: the five-starts differ from the second new distinction, not "from the first fill" (Not a block).
- `MEET-ORDERS-20261118-001` (R1): the meeting pattern's counts do not tell every pattern apart (Narrowing); the bracketing account
  is about fewest-knot presentations, one redundant knot changing the chances in 21 of 21 cases (Not a block, material, A100).
- `MEET-GROW-20261118-001` (R1): "grows by the same law wherever it sits", not "grows on its own" (Narrowing).
- `MEET-TWIST-20261118-001` (R1): "for every line length, before the first added state", not "for every n" (Not a block).
- `MEET-DIST-20261118-001` (R1): **Block on a reading.** "The rest is lost, not hidden" was false: the names, chiefly the order of
  growth, hold it. Two Narrowings (one sample, one prior; the fall only unnamed and only for five to seven).
- `MEET-HIST-20261118-001` (R1): "mostly undetermined" and "a small part of the order", not "unreadable" (Not a block).
- `MEET-ADDED-20261118-001` (R1): "told which knots were added", not "the knots carry it, not the distances" (Narrowing).

## What is open

| Direction | Payoff | Concreteness | Where to start |
| --- | --- | --- | --- |
| Beyond fewest knots (A100's challenge): with redundant knots the chances change and the placements mix; what replaces the bracketing? | 2/3 | 2/3 | `MEET-ORDERS-20261118-001`'s referee, `referee-R1/referee_meet.py extra` |
| Past the first added state: does Theorem 2's coupling extend once KF3 must add states (the cube full), and what do the shares do in long growth? | 2/3 | 2/3 | `MEET-TWIST-20261118-001` (the range bound); sampling from `MEET-DIST-20261118-001`'s engine |
| Other rules and bases: other knot kinds and weightings, presentations of the 2 × 2 pattern or of branching trees | 2/3 | 2/3 | A99; `melib.py` |
| Proofs of the computed parts: the third-step blindness, the reading of the order of growth from the added knots (and the cause of the sliver at seven) | 2/3 | 2/3 | `MEET-ORDERS-20261118-001`, `MEET-ADDED-20261118-001` (its referee's 44 classes) |

No untaken direction of the line rates 3/3 for payoff, so no new sub-goal is filed; B197 (a rule that never nests its fills) was
passed to the LOCAL-ROOM thread, and B198 and B199 were taken by `MEET-DIST-20261118-001` and `MEET-ADDED-20261118-001`.

## What the line says about A97

The owner's premise is that distance is the only form of information. This line found a piece of information that is not in the
distances to begin with: presentations of one line share every state and every distance, yet differ in how their knots nest, and
that nesting decides how many orders grow (proved at the second new distinction). The growth itself does not depend on where the
pattern sits along the line (proved), so the difference in orders comes from reading one growth against different placements.
After growth the distances hold part of the nesting: over many growths all of it, but in one grown base, read without names, only
about half to two thirds. The rest is not lost; it sits in the names, and chiefly in a small part of the order of growth, which the
states do not record. A reader who is told which knots the growth made recovers it, and a reader who has the knots themselves has
the nesting outright. So in this setting the knots and the history carry information the distances of a single base do not: the
premise holds in law and fails for one base read on its own.

## Records

Decision notes: [MEET-ORDERS](../MEET-ORDERS-20261118-001/meet_orders.md), [MEET-GROW](../MEET-GROW-20261118-001/meet_grow.md),
[MEET-TWIST](../MEET-TWIST-20261118-001/meet_twist.md), [MEET-DIST](../MEET-DIST-20261118-001/meet_dist.md),
[MEET-HIST](../MEET-HIST-20261118-001/meet_hist.md), [MEET-ADDED](meet_added.md). The advisor model (Fable 5.2) was consulted
before every freeze and shaped two designs (MEET-DIST's null and ablation, MEET-HIST's sanity row); every study has its referee
report in its `referee-R1/` directory.
