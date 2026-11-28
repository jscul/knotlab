# Readers on grown closures: where the odd birth choices split into separated readers

> **Referee report R1, 27 November 2026: confirmed with fixes, no Block** ([the report](referee-R1/report.md)). All 1,177
> birth-choice verdicts and both reader minima reproduced closure by closure with the referee's own search. Read this
> record with these narrowings (logged in `docs/CORRECTIONS.md`):
> - **The birth rule.** Whole choices keep which later closures split and their fewest strict readers. They add 567
>   splitting odd choices at 12 later closures (four strict ones at one) and lower the fewest readers of either kind at
>   two: six to five at the eight-knot closure grown from census start 289, and six to four at the one from start 608.
>   "The birth rule removes no split" is withdrawn.
> - **What the game establishes.** Given the shared state, compatible signs for the values outside readers, and only
>   its own setting as each reader's input, the reader parts meet every knot's value with certainty. Each knot asks each
>   reader at most one value. A reader's settings need a system of their own, not always one qubit. At the eight-knot
>   closure from start 4308, one setting commutes with two that fail with each other, yet fails with a third. Counting
>   idle knots as questions raises a list's score (7/8 against 3/4 at the eight-knot closure from start 168). "Odd only
>   within a reader" means that every odd choice forces two distinctions of one knot into a single failing group.
>   "Only readers holding three or more values" means that each split needs at least one such reader.
> - **Denominators and rings.** The 731 are of the 1,177 closures where birth choices attain odd (40.2% of all 1,819
>   grown closures). "Three readers exactly where four knots meet pairwise" concerns the fewest strict readers. "Five
>   around a ring of five (17)" counts closures whose shortest odd ring has five knots. 34 closures have a ring of five
>   and 17 of them also a ring of three. Among the 17, the fewest readers of either kind is three at ten, four at six
>   and five at one, and one has a single strict odd choice.
> - **The 198-closure shape belongs to the readers' values.** At 198 closures every fewest strict choice has the same
>   pattern of reader values, holders and pairings, and that pattern admits the two-bit repetition encoding. The 198
>   full closures are pairwise different. The knot the passed meeting goes through holds two reader values everywhere,
>   but exactly two distinctions at only 25 (three at 82, four at 71, five at 19, six at 1). Counting each shape a
>   closure admits, the five-reader shapes number 20, 18 and 13. Passing a meeting through a new knot and doubling its
>   mate cannot give the shape at census start 6171 (five knots holding reader values, five readers).
> - **Which certificates ran.** Each reported minimum has a certified representative, and every legal split admits a
>   realization by construction. Some secondary witnesses had combinatorial checks only.
> - **Hand items.** On an odd ring, twice the shift is −1 mod n, for the stated orientation. "Even rings give no split"
>   is a statement about the fixed-shift construction. For a bare ring with every unheld pair available it holds by a
>   separate argument. Item 3's connectedness step needs a component using all three places at each of its knots. The
>   joined rings have one partition into three readers, with two choices of failing pairs. A316: at most one value per
>   question.
> - **Credit (not a block).** The ring split is the literature's contradiction for graph states of odd rings (Anshu and
>   Mhalla, arXiv:1207.2276), relabelled since (n−1)/2 is coprime to n. DiVincenzo and Peres give the five-reader checks
>   up to exchanging X and Z. The fewest readers is related to the literature's minimum-party question (Cabello and
>   Moreno), but is not the same.

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
| Broader exploration — the quantum part under the declared phase | Known alternatives | Separated readers at 731 of the 1,177 closures where birth choices attain odd; at the other 446 every odd choice forces two values of one knot into one failing group; the birth choice and the state stay supplied (narrowed by R1) |
| Long-term goal — G18 Comparing growth laws | Capability gained | Under the declared phase, growth's own closures carry games of certainty between separated readers, the literature's GHZ argument among them |

At 692 of the 1,177 grown closures (59%, one vote per census start) some odd birth choice splits strictly into readers.
Each reader holds two values that fail to commute, and every other pair of values commutes, so each knot asks each
reader at most one value: a game of certainty between separated readers, which with three readers is the literature's GHZ
argument. At 39 more, each split needs a reader holding three or more values. At 446 (38%) no odd birth choice splits: every
odd choice forces two values of one knot into one failing group. Strict splits with three readers appear exactly where four knots meet pairwise (423
closures), and where the shortest odd ring around a knot has five knots the fewest strict readers is five (17). The frozen prediction that such odd rings are the only source
failed: 252 closures split without one, 198 of them with one pattern of reader values, in which one meeting of four
mutually meeting knots passes through a knot holding two reader values and the meeting opposite it is doubled. That
pattern encodes one reader into two (narrowed by R1: the knot holds exactly two distinctions at only 25 of the 198).

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Encoded readers: is every strict split a game on four mutually meeting knots or on an odd ring around a knot, with readers encoded through knots and doubled meetings? | 2/3 — Substantial | 3/3 — Ready | Define the encoding, prove it keeps commutation and the sign, and classify the fewest strict split at each of the 692 closures → a complete family, or the first split outside it | Selected · started |
| 2 | The 446 closures with no split: does another arrangement win them, such as readers who each receive a whole knot (the four-readings study's square), or none? | 2/3 — Substantial | 2/3 — Testable | State the arrangement and its classical bound, then search the 446 → a winning arrangement at each, or a closure none wins | Alternative · deferred |
| 3 | A principle drawn from growth itself for the sign, not imposed | 3/3 — Barrier | 1/3 — Stated | Name one such quantity at the closures → a candidate that fixes the sign on a stated class, or none | Alternative · deferred |
| 4 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Read G1's open question and its last record → a bounded next test, or a reason to keep it idle | Alternative · deferred |
| 5 | Intuition link: the fewest readers as the literature's fewest parties of an all-versus-nothing proof | 1/3 — Incremental | 3/3 — Ready | Compare the fewest readers with the literature's table for small stabilizer states → match or the first mismatch | Alternative · deferred |

1. **Payoff 2/3:** it would say exactly where separated-reader games live in growth's closures, replacing the refuted
   odd-ring rule with a family (R1: the passing knot need not be a two-place knot, and passing through a new knot alone
   misses the shape at census start 6171). **Concreteness 3/3:** the shapes are computed, and the encoding is checked by hand on
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

- **Separated readers at most of these closures.** A strict split exists at 692 of the 1,177 closures where birth
  choices attain odd (675 of the 1,091 closing in round 1, 17 of the 86 later), a split of either kind at 731, and none
  at 446. Each reported minimum has a certified representative: the values are local to readers, the checks commute,
  and, given the state, the outside signs and only its own setting as each reader's input, the readers meet every
  knot's value with certainty (narrowed by R1).
- **Four mutually meeting knots are the three-reader game.** All 423 closures with four mutually meeting knots split
  strictly with three readers, and strict splits with three readers occur nowhere else. Readers holding more values
  reach three at 10 more closures. At the 423, and only there, every odd birth choice with the fewest failing pairs is a
  strict split.
- **Odd rings around a knot give their length in readers.** Where the shortest odd ring around a knot has n knots, the
  fewest strict readers is n (five at 17 grown closures); in the fixtures the ring of five's construction is the only
  strict odd choice. The ring of four's closure has no split.
- **Not only odd rings (P1 refuted).** 252 closures split strictly without an odd ring around a knot: four readers at
  198, five at 49, six at 5. At 198 every fewest strict choice has one pattern of reader values: one meeting of four
  mutually meeting knots passes through a knot holding two reader values, and the meeting opposite it is doubled.
- **Readers of more values (P2).** At 39 closures each split needs at least one reader holding three or more values.
- **No split at 446.** Their odd closes put two values of one knot into one failing group in every odd birth choice.
  The three-by-three pattern and the grown five-knot closure F are the small cases.
- **The birth rule keeps which closures split.** Whole choices at the 86 later closures split at the same closures with
  the same fewest strict readers, but add 567 splitting choices at 12 of them and lower the fewest readers of either
  kind at two (narrowed by R1); at the 10 where birth choices lose the odd close, whole choices have no split.
- **Census types differ.** On the 173 finished types (one vote per type; knots of at least three distinctions): 115
  strict, all with an odd ring; 30 of the other kind only; 28 none.

## Intuitions (exact links, not evidence)

- **One reader encoded into two.** In the 198-closure shape the doubled meeting gives two values whose product acts as
  one reader's X, and the knot the meeting passes through reads the parity Z⊗Z of the two new readers. The two halves of the passed
  meeting then read the same encoded Z. This is the three-reader game with one reader encoded in the literature's
  two-bit repetition code. The cheapest test is to check that the 198 splits' operators are exactly the encoded checks
  (direction 1).
- **The ring of five.** Its split is the literature's contradiction for graph states of odd rings (Anshu and Mhalla,
  arXiv:1207.2276), and DiVincenzo and Peres (Phys. Rev. A 55, 4089, 1997) give its five-reader checks up to
  exchanging X and Z. For the stated orientation twice the shift is −1 mod n, which needs n odd, so the fixed-shift
  construction gives no split on even rings (narrowed by R1).
- **The fewest readers.** This is related to the literature's fewest parties for an all-versus-nothing proof specific
  to a stabilizer state (Cabello and Moreno, Phys. Rev. A 81, 042110, 2010, arXiv:1004.4874), which fixes the state
  and the measurements, while here the minimum ranges over birth choices and partitions (direction 5; narrowed by R1).
- **No split.** These closes are the literature's contextuality without separated parties, like the magic square's six
  contexts, which are three knots each meeting each of three others.

## Final report as sent

2026-11-27 19:20 PST

**Yes, mostly: growth's closures do carry games between separated readers.** At 731 of the 1,177 grown closures (one vote per census start), some odd birth choice splits into readers: different readers' values commute, and each knot asks each reader one value. At 692 the split is strict, each reader holding two values that fail to commute. The odd close is then a game of certainty between separated readers: the readers win it every time, and any list of values loses. With three readers it's the literature's GHZ argument. At 446 there's no split; those closes are odd only within a single reader. Every split was certified with explicit operators local to each reader and a state in which every knot's answer is certain.

**What we found**
- **Three readers occur exactly where four knots all meet each other** (423 closures). There, and only there, the cheapest odd choice is the three-reader game.
- **A knot meeting every knot of a ring of five gives five readers** (17 closures). Odd rings of any length work; even rings never do.
- **My frozen prediction failed.** I predicted odd rings like these were the only source of strict splits. 252 closures split without one, 198 of them in a single shape: one meeting of four mutually meeting knots passes through a two-place knot, and the meeting opposite it is doubled. That's the three-reader game with one reader re-encoded into two (the literature's repetition code).
- **39 closures** split only if readers hold three or more values.
- **The birth rule removes no split**: whole choices give the same splits at the later closures.
- **The finished census types** (one vote per type) give 115 strict, 30 other kind only, 28 none, and there every strict split comes from an odd ring. The new shape needs growth's two-place knots.

What's still supplied: which values fail to commute (the birth choice), the state, and the reading of what a reader is (A316). Nothing in the model selects the odd choice.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — splitting the odd birth choices into separated readers | **Status:** Successful | Strict split at 692 of 1,177 closures, a split of either kind at 731, none at 446; every split certified; P1 refuted; referee pending |
| Local direction — where separated-reader games live in growth's closures | Continue | 198 of the 252 splits outside odd rings share one shape that encodes one reader into two; a classification is in reach |
| Broader exploration — the quantum part under the declared phase | Known alternatives | Separated readers at 62% of closures; the other 38% are odd only within a reader; the choice and the state stay supplied |
| Long-term goal — G18 Comparing growth laws | Capability gained | Growth's own closures carry games of certainty between separated readers, the GHZ argument among them |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Encoded readers: is every strict split a game on four mutually meeting knots or on an odd ring around a knot, with readers encoded through two-place knots and doubled meetings? | 2/3 — Substantial | 3/3 — Ready | Define the encoding, prove it keeps commutation and the sign, classify all 692 → a complete family, or the first split outside it | Selected · started |
| 2 | The 446 closures with no split: does another arrangement win them, such as readers who each receive a whole knot? | 2/3 — Substantial | 2/3 — Testable | State the arrangement and its classical bound, search the 446 → a winner at each, or a closure none wins | Alternative · deferred |
| 3 | A principle drawn from growth itself for the sign | 3/3 — Barrier | 1/3 — Stated | Name one quantity at the closures → a candidate, or none | Alternative · deferred |
| 4 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Reread G1's open question → a bounded test, or a reason to keep it idle | Alternative · deferred |
| 5 | Intuition link: the fewest readers as the literature's fewest parties of an all-versus-nothing proof | 1/3 — Incremental | 3/3 — Ready | Compare with the published table for small stabilizer states → match or first mismatch | Alternative · deferred |

1. This replaces the refuted odd-ring rule with an exact family. The main shape is already checked by hand; two five-reader shapes (16 and 13 closures) may need a second encoding. Minutes of exact search.
2. This says what the no-split closures carry; the arrangement needs stating first.
3. This would make the sign native, but there's still no candidate.
4. The program's central goal, idle for six days.
5. A restatement; cheap.

**GO** on the readers line. The classification is a distinct test: either a complete family, which says exactly where these games live, or a split outside it. Stops when the classification closes or fails.

**Corrections:** none. The earlier narrowing (separated readers shown only at the ring of three's closure) was right about what had been shown then; this study shows more.

**Goals:** G18 gets a "capability gained" checkpoint row. No goal changed.

**Assumptions:** New A316 (what a reader is), tested in its strict and general forms, which differ at 39 closures; its other readings were not tested.

**Scaffolds:** The certificate's realization (one that works, not the only one) and the state are supplied and recorded. The census starts and the four-round cap carry over.

**Basket:** none of the line's top four was taken, for the same reasons as before.

The advisor was unavailable again (Fable 5.2 "unrecognized model", 5.1 usage limit). The independent reviewer made a real difference before the freeze: my first ring-of-five start doesn't grow (they found one that does); most of my predictions were already settled by the hand arguments, so they became gates and I added P1; and they found two false steps in a lemma, a gap in the K3,3 argument, and a grown closure that never splits. The referee is running now in the background.

Sources for the two literature links: [DiVincenzo & Peres, "Quantum codewords contradict local realism"](https://arxiv.org/abs/quant-ph/9611011) · [All-versus-nothing proofs with n qubits distributed between m parties](https://arxiv.org/abs/1004.4874)
