# Whole-choice sets: sets of knots whose own candidate cells commute with nothing selected

Epic `NATIVE-CARRY-20261128-001` (the label predates the choice of word; see "Words"), under G18 Comparing growth
laws, toward G1. It takes direction 1 of the even-orientation study (`EVEN-ORIENT-20261127-001#1`), which sharpens the
cross-pair study's direction 2 (`CELL-SIGN-20261127-001#2`). The direction was taken at a STOP under the owner's
standing rule to take the next 3/3 direction. Design and predictions were frozen before the run, after a review
(section "Review before the freeze"). The fixtures named in it, single patterns checked by hand, had been seen. Results
follow in sections of their own; nothing above them changes except by a dated notice. The canonical K1–K3 test, the
growth law and the birth rule (A314) are unchanged.

## The question

The readers' contradiction is a commuting choice that closes odd. Read as cells on its cross pairs (A318), it is a
closed cell structure that cannot be oriented. So far every such choice at a grown closure has been a **selection**: a
birth choice declares which unheld pairs fail (A314). The ring games, for example, use some of a closure's unheld
pairs and not others. The cross-pair study asked whether growth's pattern alone carries these cycles; four mutually
meeting knots are the example, since all their candidate cells together are the three-reader game.

This study asks which sets of knots commute with nothing selected, whether they close odd, and where growth's closures
have them.

## The objects and words

- The **candidate cells** of a set S of knots are every unheld pair of distinctions (x, y) whose four holders are
  distinct and all in S. Together they are S's **whole choice**, the records' word for every unheld pair failing.
- S is a **whole-choice set** (provisional) when it has a candidate cell and every pair of knots is a cross pair of an
  even number of its cells. Then S's whole choice commutes, and only the uniform declaration that unheld pairs fail is
  supplied.
- A whole-choice set is **minimal** when no proper subset of its knots is one. Its **sign** is the closing sign of its
  whole choice.
- **Words.** "Carrier" was considered and set aside, because the foundation uses it for other things (finite carriers,
  the index carrier, a formed set). "Native" was set aside too: it has a defined meaning, the source-aware reading.
  The epic's label keeps the first draft's name. The new word was chosen without the advisor, which was unavailable,
  and is marked provisional; its glossary entry is added with the freeze.

## Argued by hand (each checked in the run)

1. **The sign as crossings.** Place the knots on a circle in an order, and draw each distinction as a chord between
   its two holders. A failing pair's two values interleave exactly when their two chords cross. So the closing sign of
   any choice is the parity of crossing pairs among its cells.
   - Exchanging two knots that are next to each other in the order changes that parity by the number of cells at
     their pair of knots.
   - So a choice's sign is the same in every order exactly when every such number is even. This is the
     commutation-at-birth study's A4, which the cross-pair study's order count implies, read as the literature's
     parity of crossings.
   - Doubled meetings leave no gap: parallel chords share both holders, so they never make a cell together, and each
     copy is counted separately.
2. **The test.** For knots u and v of S, write m_uw for the number of distinctions u and w share within S, and m_u for
   u's total within S. The number of S's cells at the pair {u, v} is

   (m_u − m_uv)(m_v − m_uv) − Σ over w ≠ u, v of m_uw·m_vw.

   S is a whole-choice set exactly when this is even for every pair and S has a cell. Mod 2 the test and the sign depend
   only on the multiplicities mod 2 (the reviewer's reduction), so a doubled meeting adds nothing a single one cannot.
3. **Small cases.**
   - **Odd sets.** Four mutually meeting knots are one: three cells, the three-reader game, closing odd. So is the
     literature's K_{2,3}, two knots meeting the same three others: six cells, closing odd.
   - **Not sets:** a knot meeting every knot of a ring of five (the ring of five's closure), and a ring of four. So a ring
     game needs a selection.
   - **Even sets:** a ring of three with a separate meeting (three cells, the literature's sphere), and a doubled
     meeting with a separate meeting (the repeated cycle).
4. **Outerplanar patterns give only even sets.** If S's meeting pattern can be placed on a circle with no two chords
   crossing (the literature's outerplanar), its sign is 0 in that order, hence in every order (item 1).
   - So an odd set is not outerplanar.
   - The literature's obstructions to outerplanarity are K4 and K_{2,3} as minors (Chartrand and Harary, 1967).
   - Only this direction holds. The ring of five's closure is not outerplanar and has no whole-choice set at all.
   - In the subset order that minimality uses, the minimal non-outerplanar patterns are infinitely many. The
     literature's Petersen graph is a minimal odd whole-choice set on ten knots, as the reviewer found.

## Seen while designing (before the freeze; not predicted)

- The fixtures of item 3, each checked singly.
- **Census start 17's closure** (four knots, each pair meeting once) has an odd minimal set. **Census start 5088's
  closure** (the ring of five's) has none. Both closures attain odd under birth choices. These are now gates, since
  they settle the draft's P2.
- **The Petersen graph** (ten knots, three distinctions each) is a minimal odd whole-choice set with 75 cells. It
  contains neither four mutually meeting knots nor K_{2,3}. It is now a gate.
- The timing probe printed only that the abstract classification has 36 minimal sets. Their signs and kinds were not
  printed.

## Population and weighting

- **A, abstract.**
  - Every graph on four to seven knots in the literature's atlas, each pair of knots sharing at most one distinction
    (one vote per graph up to relabelling).
  - Every pattern on four or five knots with zero, one or two shared distinctions on each pair, at least one pair
    holding two and every knot holding one (up to relabelling).

  A pattern is kept when its whole set of knots is a minimal whole-choice set.
- **P, populations.**
  - the 1,819 census-start closures (four rounds, forty knots);
  - the 173 census types;
  - the extension's 115 closures;
  - the second sample's 1,168 closures, the same as in the even-orientation study.

  Each is one vote per closure or type. Every subset of knots is tested at closures of at most twelve knots, and
  subsets of at most eight knots at larger ones. Larger subsets there are "not run": a ten-knot set like the Petersen
  graph would be missed at those closures, and the count of such closures is reported. Cells are all unheld pairs,
  the pattern alone. Whether birth choices attain odd at each census-start closure is read from the commutation-at-birth
  study's rows (any birth choice, 1,177 closures).

## Prior work in the program

`python3 -B scripts/track.py objects "carrier candidate cells every unheld pair closes with nothing selected four mutually meeting knots" --until 2026-11-28 --exclude NATIVE-CARRY-20261128-001`
`python3 -B scripts/track.py objects "outerplanar whole choices close odd crossing parity Hanani Tutte" --until 2026-11-28 --exclude NATIVE-CARRY-20261128-001`

- `CELL-SIGN-20261127-001` — the cell reading, the order count and the question (its direction 2).
- `EVEN-ORIENT-20261127-001` — the sharpened direction and the sampled closures.
- `LOCAL-COMMUTE-20261127-001`:
  - its criterion that whole choices close odd exactly off outerplanar patterns, a statement about selections;
  - its argument A4, order independence;
  - its natural birth rule, under which every pair decidable at birth fails. At round 1 every unheld pair is
    decidable, so its "keeps a state at 145 of the 1,713 round-1 closures, odd at 53" is exactly "the whole closure is
    a whole-choice set". Gate G(v) must reproduce it.
  - This study adds the minimal sets inside the closures, their classification and the crossing reading.
- `READER-SPLIT-20261127-001` — four mutually meeting knots, with any multiplicity, at 423 of its 1,177 closures; and
  the ring games, which select.
- `MOST-FAILING-20261127-001` — a selection by a score (the most failing pairs). Here nothing is selected.

## In standard terms

A choice's closing sign is the literature's parity of crossings of chords with the vertices on a circle. The order
count is the literature's parity-invariance argument: a change of order alters an even number of disjoint pairs when
every cross pair is covered evenly. That is the mechanism behind Kleitman's parity theorem for crossings (J. Combin.
Theory B 21, 1976) and the Conway–Gordon and Sachs linking counts (1983). The outerplanarity obstructions are Chartrand
and Harary's. This study adds which sets of knots in growth's closures have an order-invariant whole choice, and
whether it closes odd.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates:<br>(i) the fixtures: four mutually meeting knots and K_{2,3} are odd minimal sets; a knot meeting every knot of a ring of five is not a set, nor is a ring of four; a ring of three with a separate meeting, and a doubled meeting with a separate meeting, are even sets; the Petersen graph is an odd minimal set with 75 cells; census start 17's closure has an odd minimal set of four mutually meeting knots; census start 5088's closure has no minimal set;<br>(ii) item 2's formula equals a direct count at every pair of every whole pattern examined (every abstract pattern and every population row);<br>(iii) every set's sign is the same under every neighbouring exchange and two random orders;<br>(iv) every minimal set on an outerplanar graph of the atlas closes even;<br>(v) at the 1,713 round-1 census closures the whole closure is a set at 145, closing odd at 53 (the commutation-at-birth study's natural rule). | any gate fails |
| P1 | Every minimal odd whole-choice set of A, in either source, has the cells of four mutually meeting knots or of K_{2,3} (distinctions in no cell left out). | an odd minimal set of another kind |
| P2 | Every minimal odd whole-choice set found at the census-start closures, the census types, the extension's closures and the second sample's closures has the cells of four mutually meeting knots or of K_{2,3}. | one of another kind (a Petersen-like set, for example) |
| P3 | Measured, not predicted, for each population:<br>• closures with a minimal set, and with an odd one;<br>• the kinds of odd and even minimal sets;<br>• closures whose whole set of knots is a set, and odd;<br>• at the census-start closures, how many of the 1,177 odd-attaining closures have an odd minimal set;<br>• odd minimal sets where birth choices never close odd, at the 106 later closures (zero by construction at round 1);<br>• closures read with subsets of at most eight knots only. | — |

**Why these predictions.**
- P1 is a judgment.
  - By item 4 an odd set is not outerplanar.
  - The reviewer's hand attempts on six and seven knots found none other than K4 and K_{2,3}.
  - The Petersen graph shows that larger ones exist, beyond A's seven knots.
  - By item 2's reduction, the doubled half of P1 follows from the simple half.
- P2 is a judgment.
  - The populations reach thirteen to seventeen knots and have many doubled meetings.
  - A Petersen-like set needs ten knots of three distinctions each, meeting in a specific way.
  - I expect growth's and the census's minimal odd sets to be K4 and K_{2,3} only.

## Compute

Timed on a prefix before the freeze: the abstract classification takes 8 s, and growth of all populations takes about
two minutes. Every closure read so far took under a second. The whole run is estimated at about five minutes, under a
4 GiB cap with one thread.

## Review before the freeze

The advisor was unavailable: both Fable versions returned a usage limit, which is logged in the hivemind. An
independent reviewer read the design and code, reasoned by hand and checked single patterns. It ran no predicted case.
Its findings and what changed:

1. **Blocking.**
   - **The odd-attaining closures came from the wrong population.** The draft read the even-orientation study's minimal
     strict tallies (692 closures), not "birth choices attain odd" (1,177). It now reads the commutation-at-birth
     study's rows, asserting a verdict for every closure.
   - **The draft's P2 could not fail.** Census starts 17 and 5088 already settle it. Both are now gates. The new P2 is
     the reviewer's suggestion, at risk from Petersen-like sets.
2. **Should fix.**
   - **"Exactly where these obstructions occur" was false beyond seven knots** (the Petersen graph). The claim is
     limited to the sizes checked, the Petersen graph is a gate, and the eight-knot subset cut at larger closures is
     stated as not run.
   - **Item 4** now says "as minors", citing Chartrand and Harary, and states that the converse fails.
   - **The Hanani–Tutte credit was off.** That theorem concerns pairwise-even drawings, so the credit is replaced by
     Kleitman's parity argument and the Conway–Gordon and Sachs counts.
   - **Item 1** names A4, and its wording on interleaving was corrected.
   - **The 423 closures** count four mutually meeting knots with any multiplicity, out of 1,177.
   - **Gates (ii) and (iii) were too weak.** The formula is now checked at every pair of every whole pattern, and the
     sign under every neighbouring exchange, whole closures included.
   - **P1 was split by a field** that saw only doubled meetings used in cells. It is now split by source.
   - **Words.** "Carrier" and "native" collided with the foundation's words and were replaced. See "The objects and
     words".
   - **P2's verdict is now computed**, using sets of indices.
   - **A's scope** is stated exactly.
3. **Notes adopted.**
   - The reduction mod 2 (item 2).
   - Its hand checks on six and seven knots (P1's rationale).
   - The points it checked and found correct: the superset skip, the canonical keys, the outerplanarity test, gate (v)
     against the records, and the formula on four doubled patterns.
