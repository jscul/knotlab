# Encoded readers: the fewest splits decode, and three more games appear

> **Referee report R1, 27 November 2026: confirmed with fixes, no Block** ([the report](referee-R1/report.md)). All 3,718
> fewest strict odd choices at the 692 closures reduce to exactly one base kind on every maximal route of merges, with
> the counting identity and no doubled pair. Read this record with these narrowings (logged in `docs/CORRECTIONS.md`):
> - **The headline is a convention (A317).** Under A317, every fewest strict odd birth choice at these 692 closures
>   reduces, on its marked reader values, to one of the two base kinds. A merge can change a list's best score: with
>   equal weight per knot, 4/5 at census start 786's four-reader word against 3/4 at its three-reader base. The readers
>   study's referee also found 39 closures with only wider splits.
> - **Paths and weighting.** The selected first paths merge through knots of two to six distinctions; across all paths
>   two to seven. At 18 closures every fewest word needs a merge through a knot holding other values; at 2 more (census
>   starts 6181 and 6185) some tied words do (240 of 3,718 words). The small codes are 213 of 397 with a strict word.
> - **P3 was only partly reported.** The 22 non-minimal five-pair words at 9 closures were not described; all reach the
>   three-reader game by deleting a doubled pair.
> - **The census games are counted through eight pairs** (one vote per labelled choice). At ten pairs the two largest
>   types (171 and 172) admit a minimal odd game on seven knots with no merge, a sixth kind, with count −3.
> - **The time limit was not enforced** (the solver's interrupt raised an exception); no listing reached a cap, and no
>   row was affected.
> - **The count is the Euler characteristic only when each covered pair of knots occurs twice.** At 240 fewest words a
>   pair of knots is covered four times; at census start 4786's six-reader word the count is 0 and the Euler
>   characteristic 1.
> - **The order fixture**: one pairing gives a partition into three base games and the other does not (zero routes
>   reach one base game).
> - **Credit (not a block).** The sign's link to orientation is the literature's parity of quadrangulations (Mohar,
>   Simonyi and Tardos, Lemma 6.1): for a holding covered twice, the sign is the number of covered pairs traversed twice
>   the same way, so a consistent orientation forces even.

Epic `ENCODED-READERS-20261127-001`, at the owner's go-ahead on direction 1 of the readers study. Design, frozen
predictions, review and results: [README.md](README.md); code [decode.py](decode.py); outputs [summary.json](summary.json),
[gates.json](gates.json), [results.jsonl](results.jsonl), [census_types.jsonl](census_types.jsonl),
[fixtures.json](fixtures.json). Satisfiability listings and exact merge searches with a fresh check at every step;
closures one vote per census start, choices one vote per choice; independent referee pending (brief in `referee-R1/`).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — decoding strict splits to the two known games | **Status:** Partially successful | Every fewest split at the 692 closures decodes (the referee's 2,102 words reproduced); P1 fails at 4 of 4,803 minimal choices, at two closures; P2 holds at all 1,139 of the small codes; referee pending |
| Local direction — the three-reader and ring games as the whole family | Retire | Three more irreducible games: one on grown closures, two on census types (at 46 of the 115 types) |
| Broader exploration — the readers' games on growth's closures | Known alternatives | Five irreducible games so far; read as cells, all five are closed and none is orientable, but the sign is not orientability alone |
| Long-term goal — G18 Comparing growth laws | Capability gained | Under A317, every fewest strict odd birth choice at the 692 closures reduces, on its marked values, to the three-reader or the ring-of-five kind (narrowed by R1) |

The fewest splits are now explained. Every fewest strict split at the 692 grown closures decodes by merges to the
three-reader game on four mutually meeting knots (675 closures) or the ring game of five (15; both kinds at 2). The
merges undo readers encoded through knots. Forced merges, through knots holding no other values, undo the literature's
two-bit repetition code; at 20 closures a merge passes through a knot that also holds other readers' values. The
prediction that every minimal split decodes failed. Four minimal choices of six pairs, at two closures, admit no merge
and are neither game. The census types hold two more such games through eight pairs, common there (3,726 of their 6,190 minimal choices,
one vote per labelled choice), and a sixth kind at ten pairs (R1).
So growth's closures carry separated-reader games of at least three irreducible kinds: the two known ones, and a
six-pair game on six knots.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The cell reading: is a strict commuting choice's sign decided by the complex its failing pairs make (each pair a cell on its four met pairs of knots), for example odd only when the complex cannot be oriented? | 3/3 — Barrier | 3/3 — Ready | Build the complex of every strict commuting choice, odd and even, at the small codes and the five irreducible games → a rule for the sign in terms of the complex, or a counterexample | Selected · awaiting go-ahead |
| 2 | The complete list of irreducible games on these populations: every strict odd choice with no merge, at every size, up to relabelling | 2/3 — Substantial | 2/3 — Testable | List them by satisfiability, size by size, with a time limit per type → the list, or the first size that cannot be finished | Alternative · deferred |
| 3 | The 446 closures with no split: 444 are planar in the literature's sense, so no state-independent game either; what do they carry? | 2/3 — Substantial | 2/3 — Testable | State the arrangement (readers receiving whole knots) and its bound, then search → a game at each, or a closure with none | Alternative · deferred |
| 4 | A principle drawn from growth itself for the sign | 3/3 — Barrier | 1/3 — Stated | Name one quantity at the closures → a candidate, or none | Alternative · deferred |
| 5 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Reread G1's open question → a bounded test, or a reason to keep it idle | Alternative · deferred |

1. **Payoff 3/3:** the five irreducible games all read as closed complexes that cannot be oriented, the base games as
   the literature's projective plane. A rule tying the readers' contradiction to such a property would be the first
   link between the quantum part and a shape the structure itself makes. **Concreteness 3/3:** the complex is built in
   a few lines, and seven cases were checked after the results. The main uncertainty is that the sign is not
   orientability alone, since the reviewer's even seven-knot unit cannot be oriented either. It needs your go-ahead.
   Its subject, the program's own objects read as complexes of cells, needs words from a space of two dimensions,
   which the standing rule reserves to you, and new words need the advisor.
2. **Payoff 2/3:** it closes the family on these populations. **Concreteness 2/3:** the census types' choices at large
   sizes may not finish.
3. **Payoff 2/3:** it says what the no-split closures carry. **Concreteness 2/3:** the arrangement needs stating.
4. **Payoff 3/3:** a native source of the sign. **Concreteness 1/3:** no candidate.
5. **Payoff 3/3:** the program's central goal. **Concreteness 1/3** until reread.

**STOP** on the two known games as the whole family: three irreducible games outside it, one on grown closures. Settled:
the fewest splits are those two games encoded, and every merge keeps the choice. The search for exceptions reopens only
with a larger population, such as more rounds or the census types at every size.

**Corrections:** none from this study. The readers study's referee (R1, confirmed with fixes, no Block) narrowed that
study's record:
- whole choices add splitting choices at 12 later closures;
- the game holds given the state, the outside signs and each reader's own setting, with at most one value per question;
- the 198-closure shape is a pattern of the readers' values, and the passing knot holds exactly two distinctions at
  only 25;
- denominators, the shortest ring, certificate coverage, and credit.

These are logged in `docs/CORRECTIONS.md`.

**Goals:** G18 gets a "capability gained" checkpoint row. No goal changed.

**Assumptions:** A317 (decoding by merges) gets a history line. Merges through knots that hold other values were needed
at 20 closures. Counting each encoding as a new game was not tested.

**Scaffolds:** A317 was tested by reporting the merges themselves (P3). Each cap was reported and none was reached. The
two base games are the family under test, and P1's failure shows it is not the whole. The census starts, four rounds,
the 40-knot cap and A316 carry over.

**Basket:** `BOTH-LONG-20261126-001#1`, `VALUE-CHANGE-20261126-001#1`, `TOY-PHASE-20261127-001#3` and B239. None was
taken, for the same reasons as in the readers study. This study took `READER-SPLIT-20261127-001#1`.

**Advisor:** unavailable (Fable 5.2 returned a usage limit; logged). An independent reviewer checked the design by hand
before the freeze. It found three problems:
- the first draft's merge (only at knots holding exactly two values) was too narrow, and its P1 would have failed;
- general merges are not confluent;
- P2 as drafted would have failed for reasons unrelated to encoding.

It supplied the nine-knot choice that no merge decodes, the counting identity and the three-pair argument. The design
became the general merge, with minimal choices tested.

## What was found

- **Every fewest split decodes.** At all 692 closures every fewest strict split, 2,102 labelled words at the 252
  closures without an odd ring and more elsewhere, decodes to exactly one base game. No decoding met a doubled pair, and
  every one took exactly 1 − c merges through knots holding other values, where c is the knots holding values minus the
  pairs.
- **The merges.** None at 440 closures (base games already), forced merges only at 236, and one merge through a knot
  holding other values at 20. A closure counts once for each pattern its fewest splits take. Knots merged through
  hold, in the closure, from two to six distinctions on the selected first paths, and two to seven across all paths
  (R1).
- **Minimal choices beyond the fewest (P1).** Of the 4,803 minimal strict odd choices with at most eight pairs, 4,799
  decode: all those of three and four pairs (to the three-reader game), those of five (816 to it, 88 to the ring game),
  and 46 of the 50 of six. The other 4 admit no merge.
- **Small codes (P2).** All 1,139 strict odd choices at the 213 small codes are minimal, and all decode.
- **Three more irreducible games.** All the failures admit no merge. On the grown closures they have one shape: six
  pairs on six knots. On the census types there are two through eight pairs: six pairs on seven knots, and eight
  pairs on seven knots, at 46 of the 115 types. R1 found a sixth at ten pairs (types 171 and 172, count −3).
- **The literature's planarity.** 1,157 of the 1,177 grown closures are planar, and so are 444 of the 446 with no split.
  The census types are mostly not planar (115 of 173).

## Intuitions (exact links, not evidence)

- **Cells.** A failing pair meets four pairs of knots, so it can be read as a cell with four corners, the reader's two
  values as its diagonals. In every one of the five irreducible games, each covered pair of knots is met by exactly two
  cells, and the knots holding values minus the pairs is the literature's Euler characteristic of the complex (only
  where every covered pair occurs twice, R1):
  - the three-reader game is the literature's hemi-cube, a projective plane, with 1;
  - the ring games are projective planes too;
  - the census six-pair game is a projective plane, and the grown six-pair game a Klein bottle, with 0;
  - the census eight-pair game is a pinched complex with −1.

  None can be oriented. A forced merge removes a knot in two cells, keeping the Euler characteristic, and the counting
  identity is that bookkeeping. The sign's link to orientation is the literature's parity of quadrangulations
  (Mohar, Simonyi and Tardos, Lemma 6.1; credited by R1): a consistent orientation forces even.
- **Repetition codes.** A forced merge undoes one reader in the literature's two-bit repetition code. A merge through a
  knot holding other values undoes a code whose parity check is shared with other readers.
- **Planarity.** By Arkhipov's theorem the 20 non-planar grown closures also carry the literature's state-independent
  game (two players receiving whole knots), and the 1,157 planar ones do not. The readers' games here are
  state-dependent, so the two lines cross rather than coincide.

## Final report as sent

2026-11-27 20:40 PST

Mostly yes, with three exceptions so far: every fewest separated-reader game on growth's closures is the three-reader game or the ring game of five, with readers encoded. The extra readers come from a step that merges two failing pairs: their partners are the same meeting held twice, and their other values share a knot. Undoing it (the literature's two-bit repetition code) takes every fewest split at the 692 closures down to the three-reader game (675 closures) or the ring game of five (15; both kinds at 2). At 20 closures the merge passes through a knot that also holds other readers' values.

**What we found**
- **My frozen prediction failed, narrowly.** Of the 4,803 minimal strict choices with up to eight failing pairs, 4,799 decode. The other 4, at two closures, admit no merge and are neither game: a third kind of game, six pairs on six knots.
- **The census types hold two more** such games (six pairs on seven knots, eight pairs on seven knots), and there they're common: 3,726 of 6,190 minimal choices.
- **The small codes all decode**, 1,139 of 1,139.
- **A pattern I noticed after the results:** read each failing pair as a cell with four corners, the reader's two values as its diagonals. All five irreducible games then close up into complexes that can't be oriented; the three-reader game is the literature's projective plane, and the new grown game is a Klein bottle. It isn't orientability alone, since an even example is also a projective plane. But no orientable example has closed odd so far.
- **Planarity** (the literature's): 1,157 of the 1,177 grown closures are planar, so the literature's state-independent two-player game exists at only 20. 444 of the 446 no-split closures are planar.
