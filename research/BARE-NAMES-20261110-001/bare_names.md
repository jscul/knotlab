# Abstract names

Epic `BARE-NAMES-20261110-001` (program topology, group `spacing`, `WEAK-APER-20261110-001` direction 1, G1, the challenge of
A54), 2026-11-10. Pre-registered in commit eed41814b, with ticket B's census and A54's failure criteria frozen there.

## The question

- **Where it comes from.** Since `BOARD-DIST-20261110-001`, places have been named by the words in x, y and their inverses (A54).
  Every name then has four neighbour names, and every board is a quotient of the tree of names. The board line's four epics rest on
  that naming. Its challenge, taken at the coordinator's go-ahead of 2026-11-10: name places without letters.
- **The question.** With a countable set of names that carry no structure, a neighbour distinction for each pair and a value for
  each name, what can a uniform law force about the board? Does the unfolding theorem still hold, what do the letters draw that a
  law cannot say, and are boards still frozen to finite changes?

## The question in standard terms

Universal, and universal-existential, first-order theories of vertex-coloured graphs on a countable set: which structures they can
force, how they behave under Ramsey's theorem, covers and compactness, and whether finitely many changes connect their models.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Finitary laws cannot shape a board.** Every finitary law that allows a state allows one in which all names are neighbours or none are, with one value; with identity distinctions, possibly all names one place. So a finitary law can bound the degree but never force a neighbour, and it forces no finite board other than one place. | proved; classical (Ramsey) | A (T1) |
| 2 | **What the letters draw.** Four neighbour names per name, a labelling the law can read, and one connected world. Without letters an existence clause can supply a degree 2k, and then a labelling exists (every board splits into k permutations), but no clause can read it; and no law of bounded degree forces a connected board. | proved; classical ingredients | A (T2, T4) |
| 3 | **The unfolding theorem for count laws.** A count law allows the cover of every board, so it allows a tree whenever it allows a board with a cycle. A finitary clause that reads a walk of distinct names can exclude the tree: distinct names tell a closed walk from an open one, which plays the part of a named relation. | proved; classical | A (T3) |
| 4 | **One named face still gives the plane, componentwise.** A law that names the square, with coordinates mod 3 and an aperiodic tile set, has exactly the disjoint unions of tiled planes as its boards. | proved | A (T4) |
| 5 | **Without letters the board is not frozen.** In a count law, two edges with the same pair of values can exchange partners, a change of four distinctions. When the edge lies on a cycle of a finite component, the board changes up to isomorphism; on copies of a tree the switch only exchanges names. With letters, two boards differ in infinitely many distinctions. | proved | A (T5) |
| 6 | **The board knots with the values in 90 one-bit laws.** Of the 1,024 one-bit count laws of degree four, 31 have no state. In 90 of the other 993, one neighbour distinction and its two endpoint values form a knot (K1–K3, a clause of width three): 29 never put two 0s side by side, 29 never two 1s, 31 never a 0 beside a 1, and 1 only a 0 beside a 1. Source label: each passes the source-aware condition at a state of infinitely many copies of a board, by T5's moves (through renamings, A59). | computed, exact, frozen | B |
| 7 | **Under abstract names the source-aware condition excludes nothing.** A knot is native only when each of its variables is flipped by a finite change, and renaming finitely many names is one, flipping every distinction, for any uniform law of finite degree with two values. So the condition carries no information about the board. A count that ignored renamings would keep the switch's flips on cycles of finite components. | proved; a reading (A59) | A (T5) |

## Answer

The obstruction does not depend on the naming, for finitary laws and for count laws: without letters a finitary law cannot even
make places touch, and a count law always allows the tree. What the letters draw is four neighbour names per name, a labelling the
law can read, and one connected world. They also freeze the board. Without letters the board changes by four distinctions, and in
90 one-bit laws it knots with the values. Renaming names is then a finite change too, so the source-aware condition excludes
nothing, and whether renamings should count is now an open reading.

## Reading

**Interpretation, not a theorem.**
- **The naming works both ways.** It supplies what a law cannot say for itself, neighbours it can address and one connected
  world, and it freezes the board. Abstract names lose the first and gain a board that changes like the values do.
- **Distinct names can name a relation.** Without letters, a clause that reads a walk through distinct names can tell a walk that
  closes from one that does not, and so force cycles, as the square does. Naming no relation then has to exclude such clauses.
- **For the owner's idea.** Without letters the board's distinctions behave like values: they take part in knots, and finite
  changes flip them. Shape still does not follow, unless the law names a face, and then only one plane per component.
- **Renaming is a gauge.** Two states that differ by a renaming are the same world with different names. A reading of nativeness
  that ignores renamings would keep the switch's flips on cycles of finite components, lose those on trees, and have to find value
  flips by other moves. It is recorded as assumption A59.
- **Nothing here is a length.**

## Lag cutoffs and census-only claims

- **Exact.** Conclusions 1 to 5 and 7 are proved. The census is exact: each law's pairs and edges follow from a pruning that a
  greedy tree realizes, and each knot verdict is knotlab's.
- **Census-only.** The counts of conclusion 6.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusions 1 to 5 and 7 (proved) | — (proofs) | read by an independent referee before publication (see "Review") |
| Conclusion 6 (census) | every allowed colouring of all 34 frozen boards, for all 1,024 laws, checked against the census's pairs and edges | passed: no colouring uses a pair or an edge outside the census's lists |

## Predictions

- **C1 held.** No law is undecided.
- **C2 held.** knotlab finds a knot exactly when both values occur and some pair of values never shares an edge.
- **C3 held.** The switch and both exchanges succeed for the three knot shapes that have a two-valued board in the frozen list. The
  fourth shape, never a 0 beside a 1, has no connected board with both values, and the frozen boards are all connected. By the
  contract's rule it is not certified on an explicit board, and T5 covers it with two monochromatic boards side by side.

## Review

An independent referee, a fresh Claude agent given only ticket A's proof, read it before publication on 2026-11-10.
- **Verdict.** No error in T1 to T4's main statements or in T2; its own exhaustive search of the square law on tori agreed with
  the check.
- **Changes asked for and made.**
  - T5's switch changes the board only when the edge lies on a cycle of a finite component; on copies of a tree it only exchanges
    names. The earlier wording said it always changes the board.
  - The source-aware condition is a necessary one ("native only when"), so under abstract names it excludes nothing rather than
    making everything native.
  - T1's first corollary needed the one-place case with identity distinctions; its second was sharpened (the one-place board is
    always allowed), and "the unfolding theorem in its strongest form" was renamed restriction, since its board can be the
    collapse.
  - Connectedness cannot be forced only for laws of bounded degree: "every two names are neighbours" forces the complete board.
  - What the letters draw includes a labelling the law can read, which an existing but unreadable labelling does not replace.
  - A finitary clause reading a walk of distinct names can exclude the tree (the referee's example, now in T3), so T3's
    statement stays with count laws.
  - Hypotheses written out (countably infinite names, symmetric neighbour distinctions, degree at least 1), and the period lemma
    for Wang tiles cited in T4.

## Literature and provenance

- **Sources.** Ramsey (1930); Petersen (1891); Hall's theorem and its infinite form (M. Hall 1948); Mendelsohn and Dulmage (1958);
  Tychonoff, compactness and Löwenheim–Skolem; covering graphs; Berger (1966), Robinson (1971) and Jeandel and Rao (2015) for
  aperiodic Wang tiles; related, Benjamini and Ellis (2016) on graphs locally like a lattice.
- **Classification.** Every ingredient is classical and each statement a short consequence; folklore risk is high for conclusions 1
  to 4. The reading for the board line, what the letters draw and what freezes a board, is this epic's.

## Workspace assumptions

- **Challenged.** A54, by design. By the frozen rule, with T1, T3 and T5 proved, it is **Confirmed for the obstruction**, and its
  statement and "Rests on it" are split: the frozen boards of `BOARD-DIST-20261110-001` (its conclusion 6) and A53's reading rest
  on the naming.
- **Bearing on A53.** Without letters, places are names, and the board changes by finite switches. A53's challenge, counting changes
  per place, gives way to a sharper question: whether renamings count.
- **Added.** A59, renamings count as finite changes under abstract names (a reading, Assumed).

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (T1 to T5 and the check) and ticket B (the census).
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (**Not a block**). Ticket A's proof and the closure ledger, both closed, cite the reading
"renamings count as finite changes" as A58. A58 had been taken by another thread first; the reading is A59, as this note, the knot
intuition entry and the goals doc now say. `BOARD-DIST-20261110-001`'s frozen boards were proved within A54's scope, which the
register now records; that is not a correction.

**Correction (2026-11-10, found by `PLACE-FLIP-20261110-001`).** Ticket B's frozen contract says no law of the family was run
before freezing, but its control, law 63, is in the family. The control's run and result were disclosed there, and the frozen
run agreed, so no result changes (`docs/CORRECTIONS.md`, Not a block).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — abstract names | **Status:** Successful | A54's challenge answered by proof, by the frozen rule: the obstruction holds without letters and the frozen boards do not; 90 one-bit laws knot the board with the values |
| Local direction — boards made of distinctions | Obstruction confirmed | With or without letters, no finitary law and no count law forces the plane; a named face gives it, and without letters only componentwise |
| Broader exploration — question 9 | Sharpened | Letters give a degree and one world and freeze the board; abstract names give a board that changes like the values and no shape |
| Long-term goal — G1 Space from a law | Obstruction learned | Space still needs a named face, whatever the naming, and one connected world needs the naming |

**Corrections:** none. **Goals:** a G1 checkpoint (obstruction learned); WEAK-APER-20261110-001#1 taken.
**Assumptions:** A54 Confirmed for the obstruction, its "Rests on it" split (the frozen boards rest on the naming); A59 added
(renamings count as finite changes); A51's and A53's histories record the bearing.

- **What the attempt leaves open.** Whether the board's knots with the values stay native when renamings do not count, and what
  Leibniz's rule does with abstract names.

**Next step:** Research directions — selected: #1, unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Nativeness up to renaming (A59) | 2/3 — Substantial | 3/3 — Ready | For the 90 knotted laws, search two copies of a finite board for value flips by local moves that are not renamings (value changes with switches) → each law's knot native or not under the stricter count | Selected · not started |
| 2 | Leibniz's rule with abstract names | 2/3 — Substantial | 2/3 — Testable | Under "places with isomorphic views are one place", isomorphic components merge; ask whether a law of finitary and existence clauses then forces one connected board → such a law, or an obstruction | Alternative · not started |
| 3 | Every accretion law (WEAK-APER-20261110-001#2) | 2/3 — Substantial | 2/3 — Testable | As recorded there | Alternative · not started |

1. **Nativeness up to renaming.** Payoff 2: it decides whether a board made of distinctions carries knots that no renaming can fake,
   where the owner's idea and the source-aware reading meet. Concreteness 3: the boards and the moves are in hand, and the search is
   local.
2. **Leibniz's rule with abstract names.** Payoff 2: the one route by which a law over abstract names might force a single connected
   world. Concreteness 2: the identification of places by their views has to be set up without letters first.
3. **Accretion laws.** As rated there.

**Recommendation.** Research directions, selected #1: the cheapest step, and it settles the reading this epic opened, which bears on
the foundation's source-aware reading.

## Final report as sent

Sent to the owner on 2026-11-10 at 18:44 UTC and copied here verbatim.

I've closed and published abstract names. The obstruction holds without letters. A law that reads finitely many names at a time can't make two places touch, and a law that reads a place and its neighbours always allows the tree, so the obstruction doesn't depend on the naming. Theorem W is now described as "proved here, not found in the literature so far". Piantadosi and Cohen only give points with a nontrivial stabilizer, so they don't imply it.

**What the letters were doing.** They gave every place four neighbours a law can address, and they kept the world connected. Without letters, an infinite clause can supply the degree. But no law of bounded degree can force one connected world, and a named square with aperiodic tiles gives only one plane per component. The letters also froze the board. Without them, two edges joining the same pair of values can swap partners. In 90 of the 1,024 one-bit laws, a neighbour distinction knots with the values at its two ends.

**A catch for the foundation.** Swapping two names also counts as a finite change, so under abstract names the source-aware condition excludes nothing. I've recorded this as assumption A59 and haven't proposed any change to the canonical reading. Tell me if you'd rather have a correction request.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: abstract names | **Status:** Successful | Under the frozen rule, the obstruction holds without letters; the frozen boards don't |
| Local direction: boards made of distinctions | Obstruction confirmed | With or without letters, no finitary law or count law forces the plane |
| Broader exploration: question 9 | Sharpened | Letters give shape and freeze the board; abstract names give a board that changes, and no shape |
| Long-term goal: G1 | Obstruction learned | Space still needs a named face |

**Next step:** Research directions. My pick is #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | Nativeness up to renaming (A59) | 2/3 | 3/3 | For the 90 knotted laws, look for value flips that aren't renamings | Selected |
| 2 | Leibniz's rule with abstract names | 2/3 | 2/3 | Ask whether merging isomorphic components forces one connected world | Alternative |
| 3 | Every accretion law | 2/3 | 2/3 | As recorded | Alternative |

**Corrections:** one, Not a block. The epic's proof and ledger cite the new assumption as A58, a number another thread had already taken; it is A59 ([history](https://github.com/jscul/knotlab/blob/main/HISTORY.md)).
**Goals:** G1 checkpoint (obstruction learned). **Assumptions:** A54 is confirmed for the obstruction, with the frozen boards recorded as resting on the naming; A59 is added; the A51 and A53 histories are updated.
**Basket:** spacing's BARE-NAMES-20261110-001#1 (nativeness up to renaming), #2 (Leibniz's rule with abstract names) and WEAK-APER-20261110-001#2 (every accretion law). Taken: none yet; #1 is selected and waiting for a go-ahead.

Commits: eed41814b (pre-registration), 2ebe30869 (epic), 04b3fdc8b (shared docs), 3e4b06ad7 (correction), fb3c86f52 (assumptions).
