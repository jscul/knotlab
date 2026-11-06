# Do ends count as native loops?

Status: adopted on 2026-10-20 by the repository owner: the source-aware reading (B), kept reopenable
Raised: 2026-10-20
Commitment: First emergence needs "two independently witnessed native recurrences" (AGENTS.md; docs/FOUNDATIONAL_THESIS.md), decided by the canonical K1–K3 test on allowed states; open question 1 of docs/KNOT_INTUITION.md ("which structures the program should count as native loops")
Decision: Whether an open distinction supplied by the ends of an infinite system, rather than by any finite recurrence of its law, counts as a native loop for the knot test
Implementation: AGENTS.md (the canonical knot test paragraph); docs/FOUNDATIONAL_THESIS.md ("Source condition for infinite systems"); docs/KNOT_INTUITION.md (open question 1); docs/FOUNDATION_READING.md ("What remains open")
Reopen: set Status back to open and rebuild the program views; every knot claim about an infinite system records both the K1–K3 verdict and the source label, so nothing has to be re-derived

## Adoption

On 2026-10-20 the owner asked which reading gives more interesting results.
`FROZEN-WORLDS-20261020-001`
([decision note](../FROZEN-WORLDS-20261020-001/frozen_worlds.md)) compared
them.
- **Under the source-aware reading, emergence becomes a property of the law
  and of the world:**
  - a linear law has native knots at every world or at none, on Z^d exactly
    when it has positive entropy;
  - proper 3-colourings have frozen worlds without native knots and dense
    flexible worlds with them.
- **The source-blind reading** calls all of these knots everywhere.

The owner answered: "We can do source-aware, but let's make it so we can open
it up again if needed." So the reading is adopted with three safeguards:
- the source condition applies to infinite systems only, and finite verdicts
  are unchanged;
- every infinite-system knot claim keeps its source-blind K1–K3 verdict next
  to its source label;
- reopening is the Status change above.

## Evidence

Epic `HOLES-AT-INFINITY-20261020-001`
([decision note](holes_at_infinity.md)):
- **Two sources of openness.** In an infinite parity system, an open
  distinction comes either from a finite loop or from the system's ends.
  Closed finite systems have only the first kind
  (`HOLES-AT-INFINITY-20261020-001B-P001`, Theorem 1).
- **Knots without loops.** The 3-regular tree has no loop of any kind, yet
  every vertex carries a K1–K3 knot. All of its openness comes from the
  tree's ends (Theorem 2).
- **The test cannot tell the two apart.** Adding one far edge turns an
  end-supplied distinction into a loop-supplied one without changing anything
  that a finite ball, or a K1–K3 verdict, can see (Theorem 3).
- **The law decides what a loop is.** On the square grid:
  - Tseitin's vertex law gets all its openness from finite loops.
  - Ledrappier's triangle law has no finite loop at all: no finitely supported
    homogeneous solution. Yet every triangle carries a parity knot, and all of
    its openness comes from infinity (`HOLES-AT-INFINITY-20261020-001C-P001`,
    Theorem 2(d)).

## The two readings

**A. Source-blind: keep the canonical test as adopted.** A loop is any
structure with an open distinction, as open question 1 already says. Ends
count.
- The 3-regular tree and Ledrappier's grid contain knots.
- First emergence can have an infinite source. INFINITE-CNF-001 said such a
  source would be needed for a knot that infinity originates.
- Verdicts stay functions of the projected allowed states.
- Proposed wording for AGENTS.md: "two independently witnessed native open
  distinctions, each supplied by a finite recurrence of the law or by its
  ends".

**B. Source-aware: require finite recurrence.** Add to K1–K3 that each loop's
distinction must be loop-supplied: some change of the whole system's
solutions in finitely many variables flips it.
- The tree and Ledrappier's grid contain no knots. The Tseitin grid still
  does.
- Verdicts then depend on how the whole system's solutions are connected by
  finite changes, not only on the projected relation.
- In closed finite systems both readings agree, because there every open
  distinction is loop-supplied.
- Proposed wording for docs/FOUNDATIONAL_THESIS.md, "Canonical knot test": "…
  and each loop's distinction is changed by some change of finitely many of
  the system's variables".

## What neither reading changes

- **Finite stages.** Every relation among finitely many variables, and so
  every knot, is already the relation of a finite stage (`…001C-P001`,
  Proposition 3; INFINITE-CNF-001A1-P001). Infinity supplies where the
  openness comes from, not new relations.
- **Trends.** Trends are invariants that no readable function sees, such as a
  circle through an end or the slope of a colouring's height function. They
  are invisible to both readings (`…001C-P001`, Theorem 5).
- **Interpretation.** Nothing here bears on the modal-plurality
  interpretation. A system with many completions and no computable one is a
  fact about one base, not evidence for co-reality.

The decision is the owner's.
