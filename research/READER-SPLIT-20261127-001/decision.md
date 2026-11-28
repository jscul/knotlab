# Readers on grown closures: where the odd birth choices split into separated readers

Epic `READER-SPLIT-20261127-001`, at the owner's go-ahead on direction 1 of the most-failing study. Design, frozen
predictions, review and results: [README.md](README.md); code [readers.py](readers.py); outputs
[summary.json](summary.json), [gates.json](gates.json), [results.jsonl](results.jsonl),
[whole_only.jsonl](whole_only.jsonl), [fixtures.json](fixtures.json), [census_types.jsonl](census_types.jsonl). Exact
integer programs and satisfiability, enumeration of every code with at most 14 free choices, a certificate for every
split; one vote per census start unless marked; independent referee pending (brief in `referee-R1/`).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — splitting the odd birth choices into separated readers | **Status:** Successful | A strict split (two values per reader) at 692 of the 1,177 grown closures, a split of either kind at 731, none at 446; every split certified; P1 (odd rings only) refuted; referee pending |
| Local direction — where separated-reader games live in growth's closures | Continue | Beyond odd rings, 198 of the 252 other closures share one shape, one reader encoded into two; a classification is in reach |
| Broader exploration — the quantum part under the declared phase | Known alternatives | Separated readers at 62% of closures; the other 38% are odd only within a reader; the birth choice and the state stay supplied |
| Long-term goal — G18 Comparing growth laws | Capability gained | Under the declared phase, growth's own closures carry games of certainty between separated readers, the literature's GHZ argument among them |

At 692 of the 1,177 grown closures (59%, one vote per census start) some odd birth choice splits strictly into readers.
Each reader holds two values that fail to commute, and every other pair of values commutes, so each knot asks each
reader one value: a game of certainty between separated readers, which with three readers is the literature's GHZ
argument. At 39 more, readers must hold more than two values. At 446 (38%) no odd birth choice splits: those closes are
odd only within some reader. Strict splits with three readers appear exactly where four knots meet pairwise (423
closures), and a knot meeting every knot of a ring of five gives five (17). The frozen prediction that such odd rings are the only source
failed: 252 closures split without one, 198 of them in a single shape, in which one meeting of four mutually meeting
knots passes through a two-place knot and the meeting opposite it is doubled. That shape encodes one reader into two.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Encoded readers: is every strict split a game on four mutually meeting knots or on an odd ring around a knot, with readers encoded through two-place knots and doubled meetings? | 2/3 — Substantial | 3/3 — Ready | Define the encoding, prove it keeps commutation and the sign, and classify the fewest strict split at each of the 692 closures → a complete family, or the first split outside it | Selected · started |
| 2 | The 446 closures with no split: does another arrangement win them, such as readers who each receive a whole knot (the four-readings study's square), or none? | 2/3 — Substantial | 2/3 — Testable | State the arrangement and its classical bound, then search the 446 → a winning arrangement at each, or a closure none wins | Alternative · deferred |
| 3 | A principle drawn from growth itself for the sign, not imposed | 3/3 — Barrier | 1/3 — Stated | Name one such quantity at the closures → a candidate that fixes the sign on a stated class, or none | Alternative · deferred |
| 4 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Read G1's open question and its last record → a bounded next test, or a reason to keep it idle | Alternative · deferred |
| 5 | Intuition link: the fewest readers as the literature's fewest parties of an all-versus-nothing proof | 1/3 — Incremental | 3/3 — Ready | Compare the fewest readers with the literature's table for small stabilizer states → match or the first mismatch | Alternative · deferred |

1. **Payoff 2/3:** it would say exactly where separated-reader games live in growth's closures, replacing the refuted
   odd-ring rule with a family. **Concreteness 3/3:** the shapes are computed, and the encoding is checked by hand on
   the main one. The main uncertainty is the two five-reader shapes (16 and 13 closures), which may need a second
   encoding. Its bound is an exact search on the same codes, minutes of compute. It continues this line under the
   standing go-ahead, and the first step is under way.
2. **Payoff 2/3:** it says what the no-split closures carry, and whether some arrangement other than one value per
   reader per knot makes them games. **Concreteness 2/3:** the arrangement needs stating first.
3. **Payoff 3/3:** a native source of the sign. **Concreteness 1/3:** still no candidate.
4. **Payoff 3/3:** the program's central goal. **Concreteness 1/3** until its question is reread.
5. **Payoff 1/3:** a restatement. **Concreteness 3/3:** the literature's table exists (below).

**GO** on the readers line. The run answers where separated readers exist, and it refutes the odd-ring rule with a
structured family, the shape that encodes one reader into two. Classifying that family is a distinct test: a complete
family would state where growth's closures carry such games, and a split outside it would show the encoding is not the
whole story. The line stops when the classification closes or fails.

**Corrections:** none. The most-failing referee's narrowing (the separated form shown only at the ring of three's
closure) was right about what had been shown; this study shows more.

**Goals:** G18 gets a "capability gained" checkpoint row. No goal changed.

**Assumptions:** A316 (what a reader is) gets a history line: strict splits at 692 closures, splits of either kind at 731,
none at 446. The two forms differ at 39 closures. The other readings in its challenge (contextual readers, readers as
places) were not tested.

**Scaffolds:** A316 was tested in its strict and general forms, with the results reported apart. The certificate's
realization and its free knot are one choice that works; the certificate shows only that a realization exists. The state
and the signs of the values outside readers are a supplied preparation. The census starts, four rounds and the 40-knot
cap carry over from A314's study. The counts are about the model under A314 and A316, not the model alone.

**Basket:** `BOTH-LONG-20261126-001#1` (3/3, 3/3), `VALUE-CHANGE-20261126-001#1` (3/3, 3/3),
`TOY-PHASE-20261127-001#3` (3/3, 3/3) and B239 (3/3, 2/3). None was taken. The first and third (odd rings that meet,
class labels) belong to the layer line, the second was answered by the third-reader study, and the fourth is an older
selected study. This study took `MOST-FAILING-20261127-001#1`.

**Advisor:** unavailable. Fable 5.2 returned an unrecognized model and Fable 5.1 a usage limit (logged). An independent
reviewer checked the design by hand, read-only, before the freeze, and found:
- the first draft's ring of five stalls instead of growing; the start that does grow it is now a fixture;
- most predictions followed from the hand arguments, so they became gates (H) and P1 was added;
- two false steps in item 3, and a gap in the three-by-three argument;
- the grown closure F, which has no split.
Ten changes followed, listed in the README.

## What was found

- **Separated readers at most closures.** A strict split exists at 692 of 1,177 closures (675 of the 1,091 closing in
  round 1, 17 of the 86 later), a split of either kind at 731, and none at 446. Every split passes its certificate: the
  values are local to readers, the checks commute, and the readers alone play a game of certainty.
- **Four mutually meeting knots are the three-reader game.** All 423 closures with four mutually meeting knots split
  strictly with three readers, and strict splits with three readers occur nowhere else. Readers holding more values
  reach three at 10 more closures. At the 423, and only there, every odd birth choice with the fewest failing pairs is a
  strict split.
- **Odd rings around a knot give their length in readers.** The ring of five gives five readers, at 17 grown closures
  and in the fixtures, where it is the only strict odd choice. The ring of four's closure has no split.
- **Not only odd rings (P1 refuted).** 252 closures split strictly without an odd ring around a knot: four readers at
  198, five at 49, six at 5. 198 share one shape: one meeting of four mutually meeting knots passes through a two-place
  knot, and the meeting opposite it is doubled.
- **Readers of more values (P2).** At 39 closures only readers holding three or more values split the choice.
- **No split at 446.** Their odd closes put two values of one knot into one failing group in every odd birth choice.
  The three-by-three pattern and the grown five-knot closure F are the small cases.
- **The birth rule removes no split.** Whole choices at the 86 later closures give the same splits, and at the 10 where
  birth choices lose the odd close, whole choices have none.
- **Census types differ.** On the 173 finished types (one vote per type; knots of at least three distinctions): 115
  strict, all with an odd ring; 30 of the other kind only; 28 none.

## Intuitions (exact links, not evidence)

- **One reader encoded into two.** In the 198-closure shape the doubled meeting gives two values whose product acts as
  one reader's X, and the two-place knot's check is the parity Z⊗Z of the two new readers. The two halves of the passed
  meeting then read the same encoded Z. This is the three-reader game with one reader encoded in the literature's
  two-bit repetition code. The cheapest test is to check that the 198 splits' operators are exactly the encoded checks
  (direction 1).
- **The ring of five.** Its split matches the literature's paradox for the five-qubit code (DiVincenzo and Peres, Phys.
  Rev. A 55, 4089, 1997). The shift (n−1)/2 used on an odd ring is the inverse of 2 mod n, which exists exactly when n
  is odd. That is why even rings around a knot give no split.
- **The fewest readers.** This is the literature's fewest parties for an all-versus-nothing proof specific to a
  stabilizer state, tabulated for small states in Phys. Rev. A 81, 042110 (2010), arXiv:1004.4874 (direction 5).
- **No split.** These closes are the literature's contextuality without separated parties, like the magic square's six
  contexts, which are three knots each meeting each of three others.
