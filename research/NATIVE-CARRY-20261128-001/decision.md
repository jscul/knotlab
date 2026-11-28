# Whole-choice sets: the pattern alone carries the readers' contradiction only as K4 or K_{2,3}, at 13% of growth's odd closures

Epic `NATIVE-CARRY-20261128-001`, direction 1 of the even-orientation study (the cross-pair study's direction 2,
sharpened), taken at a STOP under the owner's standing rule. Design, frozen predictions, review and results:
[README.md](README.md); code [nativecarry.py](nativecarry.py); outputs [summary.json](summary.json),
[gates.json](gates.json), [abstract.json](abstract.json) and [rows.jsonl.gz](rows.jsonl.gz). Exhaustive over every subset
of knots at closures of at most twelve knots, and over subsets of at most eight at the 24 larger ones. Closures and types
are one vote each; sets are one vote per set of knots. Independent referee pending (brief in `referee-R1/`).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which sets of knots commute with nothing selected, and where growth's closures have them | **Status:** Successful | All gates hold; P1 and P2 hold; referee pending |
| Local direction — whether growth's pattern alone carries the readers' contradiction | Retire | Answered: at 152 of the 1,177 census closures where birth choices attain odd, only as four mutually meeting knots or K_{2,3}; elsewhere a selection is needed |
| Broader exploration — the readers' games on growth's closures | Continue | Where the pattern does not carry the sign, what in growth could select it is the open question this line keeps returning to |
| Long-term goal — G18 Comparing growth laws | Capability gained | Growth's odd closures split into those whose pattern carries the contradiction with nothing selected and those that need a selection, with the two carrying kinds named |

Place the knots on a circle and draw each distinction as a chord between its holders. The closing sign of any choice is
then the parity of crossing chords among its failing pairs, and commutation is exactly what keeps that parity the same
in every order (the literature's parity-invariance argument). A **whole-choice set** (provisional word) is a set of
knots whose whole choice commutes with nothing selected: every unheld pair held within it fails. Through seven knots,
the only odd minimal ones are four mutually meeting knots and K_{2,3}, two knots meeting the same three others. These
are the literature's two obstructions to outerplanarity, here as sets of knots (P1). The literature's Petersen graph,
on ten knots, shows larger ones exist; none occurs in the populations (P2).

Growth's census closures carry the contradiction this way at 152 of the 1,177 where birth choices attain odd (13%, one
vote per census start). The other 1,025, the ring games among them, attain odd only through a selection. The census
types carry it at 149 of 173. Sampled larger starts carry it at 10 of 115 and 44 of 1,168 closures under the extension's
weighting.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A selection drawn from growth itself: at the 1,025 odd closures the pattern does not carry, does anything growth records (its births, their parents, the round a pair is decided) single out the failing pairs, and with which sign? | 3/3 — Barrier | 2/3 — Testable | List each such closure's odd choices against one growth-recorded selection (each birth's parents and newborn, read as a set) → a recorded selection that commutes and closes odd at some closure, or none | Selected · next |
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

  - Every census closure with an odd set attains odd under birth choices. 1,025 attain odd only through a selection.
  - Even sets are everywhere: four knots with doubled meetings, and rings of three with a separate meeting.

## Intuitions (exact links, not evidence)

- **The contradiction carried with nothing selected is an unavoidable crossing.**
  - A set of knots carries the readers' contradiction exactly when its meeting pattern, drawn with the knots on a
    circle, has an odd number of crossing chord pairs in every order.
  - The literature's Conway–Gordon theorem has the same shape: K6 placed in space always has an odd number of linked
    pairs of disjoint triangles (the literature's words), and the count is free of the placement for the same parity
    reason.
  - Here the unavoidable crossing is the outerplanarity obstruction, as K4 or K_{2,3}.
  - The cheapest test is to compute, on the 1,028 odd sets, the crossing count of the natural circular order of their
    meeting patterns.
- **A selection is what an ordinary drawing would need: a choice of which chords to draw.**
  - At the 1,025 closures the pattern does not carry, the odd sign appears only for chosen subsets of the chords. The
    ring game selects n of the closure's candidate cells, each pairing a meeting of the hub with the ring meeting
    opposite it.
  - Whether growth records such a choice is direction 1.
