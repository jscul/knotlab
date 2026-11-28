# Whole-choice sets: two cell patterns account for all 1,028 odd minimal sets in the four populations

> **Referee report R1, 28 November 2026: confirmed with fixes, one Block** ([the report](referee-R1/report.md)). The
> 1,028 odd minimal sets and their two kinds reproduce, every subset of the 24 cut closures was read (none added), and
> no odd minimal set exists on exactly eight knots. Read this record with these corrections (logged in
> `docs/CORRECTIONS.md`):
> - **Block: "the other 1,025 attain odd only through a selection" is false.** Minimality was tested against subsets of
>   either sign, so an odd whole-choice set whose smaller sets are all even was never listed. Of the 1,177 census starts
>   whose closures admit an odd birth choice, 152 have an odd minimal whole-choice set, 39 more have only nonminimal odd
>   whole-choice sets, and 986 have no odd whole-choice set. Every one of the 191 positives has a birth-legal witness.
>   If "nothing selected" requires the entire closure, the split is 53 against 1,124. Census start 643's five-knot
>   closure, for example, has 18 cells that close odd in every order, while its only minimal sets close even.
> - **Narrowing: the classification's scope.** The abstract enumeration covered simple patterns through seven knots and
>   patterns with doubled meetings on four and five knots; the referee excluded odd minimal sets on exactly eight knots;
>   the Petersen graph gives a different kind on ten.
> - **Narrowing: readers.** A whole choice that splits into separated readers is always the three-reader game (the
>   referee's proof). K_{2,3}'s six distinctions fall in one reader, which would have to read three of them at one knot.
>   So where a count is meant, "the readers' contradiction" should read "an odd product of commuting checks". Of the 152
>   closures, 119 have a splitting odd minimum and 33 have only nonsplitting ones.
> - **Narrowing: whole choice and birth.** Here the whole choice declares all internal candidate pairs to fail; the
>   records' earlier whole choices range over selections. At the later closures 8 of 65 odd sets use pairs not decidable
>   at birth; 257 of the 258 odd minima in the grown populations are birth choices.
> - **Narrowing: parity.** Coverage parities and the sign depend only on multiplicities mod 2, but cell existence, cell
>   counts and minimality need the unreduced pattern; the definition needs at least one candidate cell.
> - **Not a block.** Counts and weightings were stated more exactly (1,761 census closures have a minimal set of either
>   sign, 1,717 an even minimal one), and the gates were narrower than worded (205 atlas patterns with an isolated knot
>   were skipped in the formula check; nonminimal subsets were not order-checked). Credit: for simple patterns a
>   whole-choice set is the literature's convex parity graph (Burger and Harborth), and the program's whole-state study
>   already tested the simple criterion on the census types (21 whole patterns commuting, 14 odd). Conway–Gordon counts
>   pairs with odd linking number.


Epic `NATIVE-CARRY-20261128-001`, direction 1 of the even-orientation study (the cross-pair study's direction 2,
sharpened), taken at a STOP under the owner's standing rule. Design, frozen predictions, review and results:
[README.md](README.md); code [nativecarry.py](nativecarry.py); outputs [summary.json](summary.json),
[gates.json](gates.json), [abstract.json](abstract.json) and [rows.jsonl.gz](rows.jsonl.gz). Exhaustive over every subset
of knots at closures of at most twelve knots, and over subsets of at most eight at the 24 larger ones. Closures and types
are one vote each; sets are one vote per set of knots. Refereed (R1, confirmed with fixes, one Block; [report](referee-R1/report.md)).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which sets of knots commute with nothing selected, and where growth's closures have them | **Status:** Successful | The parity conclusions hold (gates narrower than worded, R1); P1 and P2 hold; refereed, one Block on the reading of the remaining closures |
| Local direction — whether growth's pattern alone carries an odd product of commuting checks | Retire | Answered: of the 1,177 census closures where birth choices attain odd, 152 have an odd minimal set (always four mutually meeting knots or K_{2,3}), 39 more an odd nonminimal one, and 986 none (R1) |
| Broader exploration — the readers' games on growth's closures | Continue | Where the pattern does not carry the sign, what in growth could select it is the open question this line keeps returning to |
| Long-term goal — G18 Comparing growth laws | Capability gained | Growth's odd closures split into those with an odd whole-choice set (191) and those that need a selection of pairs (986), with the two minimal kinds named; only four mutually meeting knots split into separated readers (R1) |

Place the knots on a circle and draw each distinction as a chord between its holders. The closing sign of any choice is
then the parity of crossing chords among its failing pairs, and commutation is exactly what keeps that parity the same
in every order (the literature's parity-invariance argument). A **whole-choice set** (provisional word) is a set of
knots with at least one candidate cell whose whole choice commutes with nothing selected: every unheld pair held within
it fails. Through seven knots (simple patterns, and four or five knots with doubled meetings), the only odd minimal ones
are four mutually meeting knots and K_{2,3}, two knots meeting the same three others. These
are the literature's two obstructions to outerplanarity, here as sets of knots (P1). The literature's Petersen graph,
on ten knots, shows larger ones exist; none occurs in the populations (P2).

Of the 1,177 census starts whose closures admit an odd birth choice (one vote per start), 152 have an odd minimal
whole-choice set, 39 more have only nonminimal odd whole-choice sets, and 986 have no odd whole-choice set (R1). At the
986, the ring games among them, an odd product of commuting checks needs a selection of pairs. The census
types carry it at 149 of 173. Sampled larger starts carry it at 10 of 115 and 44 of 1,168 closures under the extension's
weighting.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A selection drawn from growth itself: at the 986 odd-attaining census closures with no odd whole-choice set (R1), does anything growth records (its births, their parents, the round a pair is decided) single out the failing pairs, and with which sign? | 3/3 — Barrier | 2/3 — Testable | List each such closure's odd choices against one growth-recorded selection (each birth's parents and newborn, read as a set) → a recorded selection that commutes and closes odd at some closure, or none | Selected · next |
| 2 | Petersen-like sets in growth: read the 24 closures above twelve knots with every subset, and grow starts large enough to hold ten knots of three distinctions each | 1/3 — Incremental | 2/3 — Testable | Read the 24 closures fully → a larger odd set, or none at that size | Alternative · deferred |
| 3 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Reread G1's open question → a bounded test | Alternative · deferred |
| 4 | Credit: check the crossing-parity and outerplanarity credits (Kleitman; Conway–Gordon and Sachs; Chartrand–Harary) and whether whole-choice sets have a literature name | 1/3 — Incremental | 3/3 — Ready | Read the cited works → credit, or a note | Alternative · deferred |

1. **Payoff 3/3:** where the pattern does not carry the sign, a selection is supplied (A314). A selection that growth
   itself records would make the readers' contradiction native at those closures. **Concreteness 2/3:** each birth's
   parents and newborn are recorded, so the first candidate is defined, and the odd choices are already listed. It
   continues the line the owner chose, at the question its last three studies deferred (the readers study's direction
   3, the most-failing study's direction 2).
2. **Payoff 1/3:** it would close P2's gap at the largest closures. **Concreteness 2/3.**
3. **Payoff 3/3**, **Concreteness 1/3**, as before.
4. **Payoff 1/3**, **Concreteness 3/3.**

**STOP** on the local direction: answered within the tested sizes. **GO** on the readers line with direction 1. It
stops when the first growth-recorded selection is scored at every odd closure the pattern does not carry.

**Corrections:** none from this study; the reviewer's two blocking findings were fixed before the freeze. The
even-orientation study's referee (R1, confirmed with fixes, one Block on P3's scope) was folded in and logged in
`docs/CORRECTIONS.md`.

**Goals:** G18 gets a "capability gained" checkpoint row. No goal changed.

**Assumptions:** none new. A318 (the cell reading) gets a history line. The provisional glossary word **whole-choice
set** was added at the freeze, chosen without the advisor.

**Scaffolds:** the subset cut at eight knots above twelve (24 closures, "not run" beyond it); the fixtures are the
literature's or hand-built and were seen before the freeze. No hand-built start is used.

**Basket:** `BOTH-LONG-20261126-001#1` (3/3, 3/3), `VALUE-CHANGE-20261126-001#1` (3/3, 3/3) and B239 (3/3, 2/3).
None was taken, for the reasons recorded before:
- the first belongs to the layer line;
- the second appears answered by the third-reader study;
- the third is an older selected study.

This study took `EVEN-ORIENT-20261127-001#1` and `CELL-SIGN-20261127-001#2`.

**Advisor:** unavailable (both Fable versions returned a usage limit; logged). An independent reviewer checked the
design before the freeze. Its blocking findings:
- the odd-attaining closures had been read from the wrong population;
- the draft P2 could not fail.

It also found the Petersen graph, the minor and credit corrections, weaker gates than needed, and the collision of
"carrier" and "native" with the foundation's words. All were fixed before the freeze.

## What was found

- **Gates.**
  - Every fixture is as item 3 says. The Petersen graph is an odd minimal set with 75 cells.
  - The formula equals a direct count at every pair of every pattern examined.
  - Every set's sign is the same in every order tried.
  - Outerplanar patterns give only even sets.
  - The commutation-at-birth study's 145 round-1 closures with a state, 53 odd, reproduce.
- **P1 (abstract).** Of 36 minimal sets, 4 are odd: four mutually meeting knots, K_{2,3}, K_{2,3} with an inert meeting,
  and K_{2,3} with an inert doubled meeting. The 32 even ones are a ring of three with a separate meeting and 31
  four-knot patterns with doubled meetings.
- **P2 (populations).** All 1,028 odd minimal sets found have the cells of four mutually meeting knots or of K_{2,3}.
- **P3 (measured).**

  | Population | With an odd set | Of |
  | --- | --- | --- |
  | Census-start closures | 152 | 1,819 |
  | Census types | 149 | 173 |
  | Extension closures | 10 | 115 |
  | Second-sample closures | 44 | 1,168 |

  - Every census closure with an odd set attains odd under birth choices. Of the others, 39 have a nonminimal odd
    whole-choice set and 986 have none (R1).
  - Even sets are everywhere: four knots with doubled meetings, and rings of three with a separate meeting.

## Intuitions (exact links, not evidence)

- **The contradiction carried with nothing selected is an unavoidable crossing.**
  - A set of knots carries an odd product of commuting checks exactly when its meeting pattern, drawn with the knots on a
    circle, has an odd number of crossing chord pairs in every order.
  - The literature's Conway–Gordon theorem has the same shape: K6 placed in space always has an odd number of linked
    pairs of disjoint triangles with odd linking number (the literature's words), and the count is free of the placement
    for the same parity reason.
  - Here the unavoidable crossing is the outerplanarity obstruction, as K4 or K_{2,3}.
  - The cheapest test is to compute, on the 1,028 odd sets, the crossing count of the natural circular order of their
    meeting patterns.
- **A selection is what an ordinary drawing would need: a choice of which chords to draw.**
  - At the 986 closures with no odd whole-choice set, the odd sign appears only for chosen pairs of distinctions. The
    ring game selects n of the closure's candidate cells, each pairing a meeting of the hub with the ring meeting
    opposite it.
  - Whether growth records such a choice is direction 1.
