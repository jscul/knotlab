# Cross pairs and the closing sign: the sign belongs to the cycles, and on growth's closures it is non-orientability

Epic `CELL-SIGN-20261127-001`, at the owner's go-ahead on direction 1 of the encoded-readers study. Design, frozen
predictions, review and results: [README.md](README.md); code [cellsign.py](cellsign.py); outputs
[summary.json](summary.json), [gates.json](gates.json), [results.jsonl](results.jsonl),
[census_types.jsonl](census_types.jsonl), [fixtures.json](fixtures.json). A theorem by hand (item 1), checked on 2.5
million choices; closures one vote per census start, choices one vote per choice; independent referee pending (brief in
`referee-R1/`).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the closing sign as a property of the failing pairs' cycles | **Status:** Successful | The order count holds on all 2,499,769 choices; orientable and two-colourable choices close even; P1 holds; referee pending |
| Local direction — the sign read through cross pairs | Continue | On growth's closures the converse holds for minimal strict choices (all 1,846 even ones orientable), but not on the census types (8,926 not) and not because of planarity |
| Broader exploration — the quantum part under the declared phase | Known alternatives | The separated-reader games are the literature's odd quadrangulations: after separation, projective planes and Klein bottles |
| Long-term goal — G18 Comparing growth laws | Capability gained | The closing sign of every commuting choice is a parity of the cycles its failing pairs make; on growth's closures a minimal strict choice is odd exactly when they cannot be oriented |

Read each failing pair through its four cross pairs, the pairs of knots holding one value each. They make a cycle along
which the two values' holders alternate. The closing sign is then the parity of how those cycles list their shared cross
pairs, whatever orders are chosen (item 1). This is the literature's parity of odd quadrangulations, extended here to
pairs of knots covered four or more times and to failing pairs that share values. It follows that a choice whose cycles
can be oriented always closes even, and so does one whose cross pairs are two-colourable. The check held on every one of
2,499,769 choices. On growth's closures the converse holds too for minimal strict choices. Every odd one is, after
separating pinched knots, a projective plane (4,423) or a Klein bottle (4), and every even one is orientable, a sphere
(1,504) or a torus (106). There, the readers' contradiction is exactly the impossibility of orienting the cycles. The
census types break the converse: 8,926 of their even minimal choices are non-orientable. Planarity does not explain the
difference.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why growth's even choices are orientable: compare the census types' non-orientable even choices with growth's, by the knots they use, the closing birth and how their knots meet | 2/3 — Substantial | 2/3 — Testable | Tabulate those features for both populations → a property that forces orientability on growth's closures, or a grown closure where it fails (one more round, or a larger cap) | Selected · started |
| 2 | Space from the readers' contradiction: does growth's pattern alone, before any failing pair is declared, carry these cycles? Four mutually meeting knots carry the projective plane, for instance | 3/3 — Barrier | 1/3 — Stated | List the cycles that a closure's meetings determine without a birth choice → a native carrier of the projective plane, or none | Alternative · deferred |
| 3 | The ten-pair census game and larger: the irreducible games at every size on the census types | 2/3 — Substantial | 2/3 — Testable | List them size by size with a conflict budget → the list, or the first size that cannot be finished | Alternative · deferred |
| 4 | A principle drawn from growth itself for the sign | 3/3 — Barrier | 1/3 — Stated | Name one quantity → a candidate, or none | Alternative · deferred |
| 5 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Reread G1's open question → a bounded test | Alternative · deferred |

1. **Payoff 2/3:** growth's own closures make the topological reading exact, and the census types do not; the reason
   would say what growth contributes. **Concreteness 2/3:** the features are measurable from the stored rows. The main
   uncertainty is whether size alone explains it, which is itself a useful answer. It continues the readers line under
   the owner's go-ahead.
2. **Payoff 3/3:** a shape the structure makes before anything is declared would connect G18 to G1. **Concreteness
   1/3:** which cycles a pattern determines is not yet defined.
3. **Payoff 2/3:** it closes the census family. **Concreteness 2/3:** the largest types may not finish.
4. **Payoff 3/3:** a native source of the sign. **Concreteness 1/3:** no candidate.
5. **Payoff 3/3:** the central goal. **Concreteness 1/3** until reread.

**GO** on the readers line. The sign question is settled (item 1, known at coverage two), and the run found the converse
on growth's closures but not on the census types. Why growth's closures behave this way is a distinct test whose answer
says what growth adds to the readers' games. It stops when a property that forces orientability is found or refuted.

**Corrections:** none from this study. The encoded-readers study's referee (R1, confirmed with fixes, no Block) narrowed
that record:
- the reduction to the two base kinds holds under A317 on marked values, a convention, since a merge can change a list's
  best score;
- the census games were counted through eight pairs, and a sixth kind appears at ten;
- the count of knots minus pairs is the Euler characteristic only where every pair of knots is covered twice;
- smaller points: paths, the unenforced time limit, the order fixture, and credit.

These are logged in `docs/CORRECTIONS.md`.

**Goals:** G18 gets a "capability gained" checkpoint row. No goal changed.

**Assumptions:** A318 (a failing pair as a cell on its cross pairs) gets a history line. The provisional glossary word
cross pair, and the glossary's Orientable and Euler count extended to failing pairs, are reported here.

**Scaffolds:**
- A318's attachment of cells along cross pairs, and the separation of pinched knots, were used as stated. At pairs of
  knots covered four times the attachment is not determined, and those choices are reported apart.
- The fixtures are the literature's examples.
- Two census types reached the cap on even choices.

**Basket:** `BOTH-LONG-20261126-001#1`, `VALUE-CHANGE-20261126-001#1`, `TOY-PHASE-20261127-001#3` and B239. None was
taken, for the same reasons as before. This study took `ENCODED-READERS-20261127-001#1`.

**Advisor:** unavailable (Fable 5.2 returned a usage limit; logged), so the new word was chosen by the vocabulary
skill's steps alone and marked provisional. An independent reviewer checked the design by hand before the freeze:
- the first P1 was already refuted by the record (pairs of knots covered four times);
- the theorem is known at coverage two, in the literature's odd quadrangulations;
- the draft's projective grids were even;
- "order-consistent" duplicated the glossary's Orientable;
- several code fixes.

## What was found

- **The order count holds everywhere checked**, on 2,499,769 choices of the populations and 80,005 of random patterns,
  strict or not, at any coverage.
- **Odd choices are never orientable, never weakly even, and their cross pairs are never two-colourable** (item 2).
- **Minimal strict odd choices, after separation**, are projective planes (4,423 at grown closures, 4,464 at census
  types, all 1,131 at small codes) or Klein bottles (4 at grown closures, 1,726 at census types) (P1).
- **Even minimal strict choices are orientable on growth's closures** (1,846 of 1,846), but not on the census types
  (6,694 of 15,620).
- **Choices that are not strict are mostly covered many times.** 1,210,317 of the 1,216,401 even ones at the grown
  closures are orientable, and none of the odd ones.
- **The literature's examples behave as the theorem says.** Klein grids are odd exactly when n is odd, and the
  subdivided cube modulo the antipodal map exactly when k is odd. The projective grids are two-colourable and even.

## Intuitions (exact links, not evidence)

- **The readers' contradiction is a failure of orientation.** A separated-reader game is a parity proof whose cells
  cannot be oriented consistently. The three-reader game is the hemi-cube, the smallest cell structure on the
  projective plane, and the GHZ argument of the literature lives there. The ring games are larger projective planes,
  and the grown six-pair game is a Klein bottle.
- **On growth's closures this is exact.** There, even choices can always be oriented. A cheap test of why is
  direction 1: compare the knots and meetings that the census types' non-orientable even choices use.
