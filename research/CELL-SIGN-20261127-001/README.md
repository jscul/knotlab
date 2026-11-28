# Cross pairs and the closing sign: is the readers' sign decided by the cycles its failing pairs make?

Epic `CELL-SIGN-20261127-001`, under G18 Comparing growth laws, at the owner's go-ahead ("Let's do 1") on direction 1 of
the encoded-readers study (`ENCODED-READERS-20261127-001#1`). Design and predictions frozen before the code was run on
any predicted case, after a review (section "Review before the freeze"; the advisor was unavailable). Results follow in
sections of their own; nothing above them changes except by a dated notice. The canonical K1–K3 test, the growth law,
the birth rule (A314), A316 and A317 are unchanged.

## The question

The encoded-readers study found six irreducible separated-reader games, five of them through eight failing pairs and
one at ten. Read in the literature's way, each failing pair a cell with four corners, the five closed up into complexes
that could not be oriented. That study's referee credited the link to the literature's parity of quadrangulations. It
also asked, as its direction 2, what happens where a pair of knots is covered four times. This study states the rule in
the program's words, for every commuting choice, strict or not, at any even coverage. It checks the rule on every
choice, and measures which structures growth's closures and the census types make.

## Cross pairs and orders

A **commuting choice** is a set of failing pairs (x, y) of unheld values, with every two knots' checks commuting (A314;
any birth choice).

- A **cross pair** of a failing pair (x, y) is a pair of knots, one holding x and the other holding y. With x held by a
  and b and y by c and d, the failing pair has four, {a, c}, {c, b}, {b, d} and {d, a}. They make its **cycle**
  a, c, b, d, along which the holders of x and of y alternate. Commutation says exactly that every pair of knots is a
  cross pair of an even number of failing pairs. Earlier records called these the holder pairs (the readers study's
  item 4), met pairs (the encoded-readers study) and covered pairs (its referee).
- A cycle can be listed in two cyclic orders. Two failing pairs sharing a cross pair list it in the **same order** or in
  **opposite orders**.
- A choice is **orientable** (the glossary's word, extended from two-fold weaves) when its cycles can be given cyclic
  orders that list every pair of knots equally often in each of its two orders. When every cross pair belongs to exactly
  two failing pairs, this means every shared cross pair is listed in opposite orders.
- Its **Euler count** (the glossary's word, extended) is knots on its cycles − cross pairs + failing pairs.
- Two further properties: whether every cross pair belongs to exactly two failing pairs, and whether the failing pairs
  through each knot form **one cycle at the knot**, consecutive ones sharing a cross pair there.
- The cross pairs are **two-colourable** when the knots split into two classes with every cross pair joining them.

"Cross pair" is a new word, entered in the glossary as provisional since the advisor was unavailable to check it. It
already occurs in other records in the generic sense of a pair across two sets, and this sense is a narrow case of it.

## In standard terms

A failing pair is the literature's four-sided cell, with its cross pairs as sides and its two values as diagonals.
When every cross pair belongs to exactly two failing pairs and every knot has one cycle, the choice is the literature's
quadrangulation of a closed surface. Orientable and the Euler count are then the literature's orientability and Euler
characteristic. The closing sign is the parity that defines the literature's odd quadrangulations: Mohar, Simonyi and
Tardos, Lemma 6.1, after Archdeacon, Hutchinson, Nakamoto, Negami and Ota, and Mohar and Seymour. Their lemma says a
quadrangulation is odd exactly when an odd number of its cells, with sides and cells oriented arbitrarily, list an odd
number of sides in the chosen direction. With the encoded-readers referee's identity (a failing pair's two values
interleave exactly when its cycle has an odd number of descents in index order), this is item 1 below at coverage two.
What this study adds is item 1 at any even coverage, so failing pairs may share values and pairs of knots may be covered
four or more times. It adds the closing sign as that parity, and a census of what growth's choices make.

## Settled by construction (stated, not tested)

1. **The order count.** Give each failing pair's cycle a cyclic order, and each pair of knots a reference order. Let L(s)
   be the number of failing pairs whose cyclic order lists the pair of knots s in its reference order. Then the closing
   sign is the sum of L(s) over all pairs of knots, mod 2, whatever orders are chosen.
   - *Proof.* A failing pair's two values interleave in index order exactly when its cycle has an odd number of
     descents, steps from a later knot to an earlier one; in either cyclic order, the four steps alternate between the
     holders of x and of y. With every reference order "earlier knot first", the closing sign, the number of
     interleaving failing pairs mod 2, is the sum over cycles of their descents. That is the number of cycle listings
     against the reference, which is Σ (m(s) − L(s)) ≡ Σ L(s), since each m(s), the number of failing pairs at s, is
     even.
   - Reversing a cycle changes L on its four cross pairs by one each. Reversing a reference changes L(s) to m(s) − L(s).
     Neither changes the parity. ∎
2. **Consequences.**
   - **(a)** An orientable choice closes even: L(s) is then half of m(s), and the halves sum to twice the number of
     failing pairs. More weakly, a choice closes even whenever its cycles can be given orders with L(s) ≡ m(s)/2 mod 2 at
     every s.
   - **(b)** When every cross pair belongs to exactly two failing pairs, L(s) is 1 exactly when the two list s in
     opposite orders. So the sign is the parity of the number of opposite-order cross pairs, and since there are twice
     as many cross pairs as failing pairs, also of the same-order ones, whatever orders are chosen.
   - **(c)** The sign depends only on the multiset of cycles mod 2: two failing pairs with one cycle contribute nothing
     together.
   - **(d)** Two-colourable cross pairs close even: reference every cross pair from the first class, and each cycle,
     alternating between the classes, lists exactly two of its four in that order.
3. **The literature's terms.** When every cross pair belongs to exactly two failing pairs and every knot has one cycle,
   2(b) is the literature's first Stiefel–Whitney class evaluated on the literature's dual cycle crossing every cross
   pair once. The dual cells of a set A of knots have as boundary exactly the dual edges of the cross pairs with one end
   in A, so that cycle bounds exactly when the cross pairs are two-colourable. On the literature's projective plane, the
   sign is therefore odd exactly when the cross pairs are not two-colourable. For a knot with several cycles (a pinched
   knot), separate it into one knot per cycle first. The sign is unchanged, and two-colourability is then read on the
   separated pattern: on the original, two-colourable still forces even, but the converse can fail.
4. **Forced merges.** A forced merge of the encoded-readers study, at a knot holding exactly two values, removes that
   knot and two cross pairs and joins two cycles into one. It keeps the Euler count, orientability, the one cycle at
   every knot, coverage exactly two, two-colourability and the sign.

## Population and weighting

- **Fewest strict splits**: every fewest strict split at the 692 grown closures with one, listed as in the
  encoded-readers study, one vote per census start.
- **Minimal strict choices** with at most eight failing pairs, odd and even, at the 692 closures and at the 115 census
  types with a strict split, listed up to 2,000 per size, sign and closure. A choice is minimal when no proper non-empty
  sub-collection commutes on its own. One vote per choice.
- **All commuting choices** at the codes with at most 14 free choices (grown closures and census types), odd and even,
  strict or not, and so at the 446 closures with no split where their codes are small. One vote per choice.
- **Fixtures**, constructed choices, each from cycles with the two values of each cycle as new distinctions:
  - the three-reader game (the literature's hemi-cube) and ring games of five, seven and nine;
  - the literature's cube;
  - grids of the literature's torus and Klein bottle, n × m for n, m in {3, 4, 5};
  - grids of the literature's projective plane: N × N squares with the boundary glued antipodally, N = 3, 4;
  - the literature's cube subdivided k × k on each face and taken modulo the antipodal map, k = 1, 2, 3, where k = 1 is
    the hemi-cube;
  - the six irreducible games (the ten-pair one from the encoded-readers referee's record);
  - the census start 4786 witness with a pair of knots covered four times, and the reviewer's five-pair one;
  - that referee's even seven-knot control and the nine-knot choice of the encoded-readers study's item 7;
  - random closed patterns (as in the earlier self-tests) with all their commuting choices.

## Prior work in the program

`python3 -B scripts/track.py objects "cross pairs cycle of a failing pair closing sign order count orientable" --until 2026-11-27 --exclude CELL-SIGN-20261127-001`
`python3 -B scripts/track.py objects "projective plane Klein bottle surface cells sign twist readers" --until 2026-11-27 --exclude CELL-SIGN-20261127-001`

- `ENCODED-READERS-20261127-001` and its referee:
  - the six irreducible games and the cell reading;
  - the descent identity, and the credit to the literature's parity of quadrangulations;
  - the coverage table: pairs of knots covered four times at 240 fewest words at 20 closures, at 136 further minimal
    words at 13, and none at census types through eight pairs;
  - its direction 2 (the sign at fourfold coverage), which item 1 answers.
- `READER-SPLIT-20261127-001` — its item 4 (the order-free count) and its referee's exchange check, the order
  independence of the sign.
- `LOCAL-COMMUTE-20261127-001` — the birth choices, and its criterion that whole choices close odd exactly off
  outerplanar patterns. That criterion is a statement about patterns; this one is about choices.
- `DISTANCE-ORDER-20261117-001`, `FAR-SIGN-20261118-001`, `KNOTS-ALONE-20261111-001`, `LONG-LOOP-20261111-001`,
  `LOOP-LOCK-20261112-001` — unrelated objects (orders of a base, a far pair's sign in growth, loops) matched on shared
  words.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: the closing sign by interleaving equals Σ L(s) mod 2 for two seeded random settings of cyclic and reference orders, on every choice examined; every orientable choice, every choice meeting 2(a)'s weaker condition, and every choice with two-colourable cross pairs closes even; where every cross pair is in two failing pairs, the sign equals the same-order parity of 2(b). The fixtures as items 1–3 say: <br>• the hemi-cube and the ring games odd, not orientable, Euler count 1, not two-colourable; <br>• the cube orientable with Euler count 2, and every torus grid orientable with 0, both even; <br>• every Klein grid not orientable with 0, odd exactly when n is odd; <br>• the projective grids not orientable with 1, two-colourable and even; <br>• the subdivided cube mod the antipodal map not orientable with 1, odd exactly when k is odd; <br>• the six games odd with Euler counts 1, 1, 0, 1, −1 and −3; <br>• the 4786 and five-pair witnesses odd with a pair of knots covered four times; <br>• the seven-knot control even, two-colourable, Euler count 1; <br>• the nine-knot choice odd with 0. <br>The referee's coverage table reproduced at the closures and types. No search unsettled, a search not finished within its limit counting as unsettled. | any gate fails |
| P1 | Every minimal strict odd choice in the populations with every cross pair in exactly two failing pairs, after its pinched knots are separated, has Euler count 1 or 0 (the literature's projective plane or Klein bottle). | any has another Euler count |
| P2 | Measured, not predicted: for each population and by sign, strict and not, how many choices have every cross pair in exactly two failing pairs, one cycle at every knot, orientability and two-colourable cross pairs, and the distribution of Euler counts (before and after separation); the same at the closures with no split. | — |
| P3 | Measured: among the even minimal strict choices, how many are orientable, with their Euler counts. | — |

P1 is a judgment. All five irreducible games through eight pairs have separated Euler count 1 or 0, and the encoded
games covered twice inherit the count of their base game, since forced merges keep it. The open risk is a minimal
choice like the census ten-pair game (−3) at eight pairs or fewer.

## Runs and stop rule

One script, `cellsign.py`. It reuses the encoded-readers study's listing and minimality test (`decode.py`), the readers
study's code (`readers.py`) and the commutation-at-birth study's growth. For each choice it builds the cycles and cross
pairs, computes the order count twice under seeded orders, and computes:
- coverage exactly two;
- the cycles at each knot, and the separated Euler count;
- orientability: by propagation over shared cross pairs where every cross pair is in two failing pairs, otherwise by an
  exact search;
- 2(a)'s weaker condition, as a linear system over GF(2);
- two-colourability and the Euler count.

Satisfiability calls carry a conflict budget, and an exhausted budget counts as unsettled. A prefix is timed first; if
the whole would exceed an hour, the run is cut to a prefix in census order, recorded as a deviation before it runs. A 4
GiB cap and one thread. The study stops when every prediction is scored.

## Scaffolds

- **A318, a failing pair as a cell on its cross pairs**: each failing pair read as the cycle of its four cross pairs, the
  cells attached along them. Another reading would keep only the pair of values, as two chords; the closing sign is
  defined from those, and item 1 shows it is a property of the cells. Tested: P2 measures which cells occur.
- **The constructed fixtures** are the literature's examples, chosen by hand: the theorem is general, and the fixtures
  test the code.
- The caps (2,000 choices per size, sign and closure; eight pairs; the conflict budget) are reported where reached.
  Carried over: the census starts, four rounds and the 40-knot cap (A314's study), and A316 and A317.

## Review before the freeze

The advisor was unavailable (Fable 5.2 returned a usage limit; logged in `docs/ADVISOR_HIVEMIND.md`), so the new word was
chosen by the vocabulary skill's steps alone and marked provisional. An independent reviewer (read-only, reasoning by
hand) checked the first draft, and the design changed in response:

1. **The first draft's P1 was already refuted by the record.** It predicted that every minimal strict odd choice has
   every cross pair in two failing pairs. The encoded-readers referee lists 376 minimal words with a pair of knots
   covered four times, from merges through knots that hold other values. That table is now a gate, and P1 is a
   judgment about separated Euler counts.
2. **The theorem is known at coverage two**: the literature's odd quadrangulations (Mohar, Simonyi and Tardos, Lemma
   6.1). It is credited, and the proof now uses descents. Item 2(b) gained its missing step. Item 2(c) was restated:
   different failing pairs can share a cycle. Item 3's argument was replaced by the dual-cell one, with the pinched case
   stated.
3. **Fixtures.** The draft's 2 × 2 projective grid was two doubled pairs, and every antipodal grid is two-colourable,
   hence even. So an odd projective family was added (the subdivided cube mod the antipodal map, odd exactly when k is
   odd), and Klein grids are scored as odd exactly when n is odd. The sixth game, the fourfold witnesses, the seven-knot
   control and the nine-knot choice were added.
4. **Code.** Orientability no longer stops above 22 cycles. Propagation is used where coverage is two, and a "not
   computed" result counts as unsettled. Satisfiability calls carry a conflict budget, since the earlier timer was not
   enforced. The same-order count and the missing gates were added, and the start-786 gate made robust.
5. **Words.** "Order-consistent" duplicated the glossary's Orientable, which is extended instead. The count is the
   glossary's Euler count. The order count's L(s) no longer clashes with G. Spatial words are marked as the
   literature's, and the earlier names of cross pairs are recorded.

## Results (27 November)

The run took 1,799 seconds under a 4 GiB cap with one thread, unit `cell-sign-run`, no cut ([summary](summary.json),
[gates](gates.json), [rows](results.jsonl), [census types](census_types.jsonl), [fixtures](fixtures.json)). Two census
types (171 and 172, the largest) reached the cap of 2,000 even choices at seven or eight pairs. Their even counts are
therefore incomplete; nothing else reached a cap. Closures are one vote per census start, choices one vote per choice.

| # | Verdict | Count |
| --- | --- | --- |
| G | holds | The order count gives the closing sign on all 2,499,769 choices of the populations and on 80,005 choices of random patterns, and the same-order parity agrees wherever every cross pair is in two failing pairs. No orientable, weakly even or two-colourable choice closes odd. Every fixture is as items 1–3 say: the hemi-cube and the ring games of five, seven and nine are odd with Euler count 1; the cube and every torus grid are orientable and even; every Klein grid is odd exactly when n is odd; the projective grids are two-colourable and even; the subdivided cube modulo the antipodal map is odd exactly when k is odd; the six games are odd and minimal, with Euler counts 1, 1, 0, 1, −1 and −3; the fourfold witnesses are odd with a pair of knots covered four times; the seven-knot control is even and two-colourable with count 1; and the nine-knot choice is odd with 0. The referee's coverage table is reproduced exactly: 240 fewest words at 20 closures and 136 further minimal words at 13 have a pair of knots covered four times, and no census type has one through eight pairs. No search was left unsettled. |
| P1 | holds | Every minimal strict odd choice covered twice has separated Euler count 1 or 0. At the grown closures that is 4,423 with 1 and 4 with 0 (of 4,427 covered twice among 4,803). At the census types it is 4,464 with 1 and 1,726 with 0 (all 6,190 covered twice). At the small codes all 1,131 have 1. |

**P2, measured** (one vote per choice; the full tables are in the summary):

- **Strict odd choices** are never orientable, as item 2(a) requires. Covered twice, they are the literature's projective
  plane or Klein bottle after separation. Their pinched knots are at the census eight-pair game, which separates to a
  Klein bottle.
- **Choices that are not strict** (a value in two failing pairs) at the small codes number about 2.4 million, half odd
  and half even. Pairs of knots covered four to eighteen times are the rule there: at the grown closures only
  23,490 of them are covered exactly twice. 1,210,317 of the 1,216,401 even ones at the grown closures are
  orientable, and none of the odd ones.
- **At the 446 closures with no split**, the 633 odd choices covered twice are all projective planes after separation.

**P3, measured.** At the grown closures every one of the 1,846 minimal strict even choices is orientable. After
separation they are 1,504 with Euler count 2 (the literature's sphere) and 106 with 0 (the torus), and the rest are
covered four times at some pair. So on growth's own closures, for minimal strict choices, **the sign is odd exactly when
the cycles cannot be oriented.** The census types differ: 6,694 of their 15,620 minimal strict even choices are
orientable and 8,926 are not, the latter with separated Euler counts 0 and −1.

**After the results (not frozen).** The difference is not the literature's planarity of the meeting pattern. Planar
census types have 21 non-orientable even choices against 30 orientable. On the grown closures both the 1,730 even
choices on planar closures and the 116 on non-planar ones are all orientable.
