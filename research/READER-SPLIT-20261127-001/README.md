# Readers on grown closures: do the odd birth choices split into separated readers?

Epic `READER-SPLIT-20261127-001`, under G18 Comparing growth laws, at the owner's go-ahead ("Let's take on 1") on
direction 1 of the most-failing study (`MOST-FAILING-20261127-001#1`). Design and predictions frozen before the code was
run on any predicted case, after a review (section "Review before the freeze"; the advisor was unavailable). Results
follow in sections of their own; nothing above them changes except by a dated notice. The canonical K1–K3 test, the
growth law and the birth rule (A314) are unchanged.

## The question

With which values commute declared at birth (A314), birth choices attain an odd close at 1,177 grown closures: the
knots' checks commute, and their product closes with the sign opposite to what any list of values gives. The
most-failing study's referee narrowed what this shows: an odd product of commuting checks, with the form between
separated readers shown only at the ring of three's closure. This study asks, closure by closure, whether some odd birth
choice splits into readers.

## Readers and splits

A birth choice is its set of failing pairs (A314), with every two knots' checks commuting.

- A **split** of an odd birth choice is a set of disjoint **readers** (sets of distinctions) such that (i) every failing
  pair lies inside one reader, so the values of different readers commute; and (ii) no knot holds two distinctions of
  one reader, so in every knot each reader reads at most one of its values (its setting there). A distinction in no
  failing pair belongs to no reader.
- A split is **strict** when every reader holds exactly two values and they fail to commute: the failing pairs are
  disjoint. Condition (ii) then holds by itself, since no knot holds a failing pair.
- The **number of readers** at a closure is the fewest readers over all splits of all its odd birth choices (one reader
  may hold several groups of failing pairs, when (ii) allows).
- **Separated**, in this study, means only this: different readers' values commute and can act on separate qubits, and
  each knot asks each reader at most one value. Knots are questions here, not channels between readers; that each
  reader answers from its own setting alone is the literature's assumption for such games, supplied (A316). It is not
  the third-reader study's sense, readers whom no knot joins: here knots join readers, as questions.
- **What a split gives** (settled by construction, item 6 below): a state in which every knot's check has a definite
  value, the closing knot's opposite to what the other knots imply for any list of values, with the values outside the
  readers fixed. Every knot is then a question, each reader answers with its value in that knot, and the answers must
  multiply to the knot's value. The readers win with certainty; a list of values cannot, since every value is held by
  two knots. The state and the signs of the values outside readers are a supplied preparation.
- An odd close with **no split** has, in every odd birth choice, a group of failing pairs that reaches some knot twice:
  some reader would have to read two values of one knot.

## In standard terms

The checks are commuting Pauli operators and the odd close is a parity proof that no assignment of values exists. A
strict split with three readers is the literature's argument of Greenberger, Horne and Zeilinger in Mermin's form
(GHZ): three parties, two settings each, four contexts. The ring-of-n construction below may be the literature's
GHZ-type argument for graph states of odd rings (to be checked before it is cited). An odd close with no split cannot be
placed among readers in this sense. On three knots each meeting each of three others (the literature's magic square of
Mermin and Peres, in another arrangement), two readers who each receive a whole knot do win with certainty (the
four-readings study), but each then reads three values in one question.

## Population and weighting

- **Grown closures.** The 1,177 closures where birth choices attain odd (the commutation-at-birth study, as refereed),
  one vote per census start: 1,091 closing in round 1, where every unheld pair is decidable, 85 in round 2 and 1 in
  round 3. Birth choices throughout. Whole choices (every unheld pair) at all 96 later closures that are not outerplanar,
  the 86 above and the 10 where birth choices lose the odd close, to measure what the birth rule removes.
- **Described before the freeze** (a population description, not the measured quantity): the closures have 4 knots (4
  closures), 5 (97), 6 (990), 8 (80), 9 (5) or 11 (1); the largest knot holds 3 distinctions at 4 closures, 4 at 79, 5
  at 463, 6 at 475, 7 at 139, 8 at 16 and 9 at 1; 1,135 have a doubled meeting; 423 contain four mutually meeting knots.
- **Finished census types**, a separate population: the 173 types of the earlier census, read as finished closed
  patterns (every unheld pair decidable), one vote per type.
- **Fixtures.** Grown (birth choices): the ring of three's closure; the ring of five's closure, grown from a start knot
  meeting four knots in a chain, with one loose distinction at it and at the chain's two ends (the closing knot then
  meets three of them, and the start knot meets all five others); and a five-knot closure F, grown from four knots
  meeting pairwise except one pair, each of that pair with one loose distinction (one two-place birth joins them).
  Closed patterns (whole choices), which growth never makes: the ring of four's and the ring of five's closures, each a
  ring closed by one knot meeting every ring knot once (the literature's wheels); two rings of three joined knot to knot
  (six knots, three distinctions each); three knots each meeting each of three others.

## Prior work in the program

`python3 -B scripts/track.py objects "readers each holding two values that fail to commute, separated readers, split of the failing pairs" --until 2026-11-27 --exclude READER-SPLIT-20261127-001`
`python3 -B scripts/track.py objects "GHZ Mermin game of certainty four mutually meeting knots closure" --until 2026-11-27 --exclude READER-SPLIT-20261127-001`

- `NO-WHOLE-STATE-20261126-001` — proposed this study's direction (its direction 3: a reader game with roles from the
  pairs no knot holds together, defined by the advisor's R4, which is condition (i) here).
- `LOCAL-COMMUTE-20261127-001` — same population and birth choices; its argument A4 gives the order independence that
  item 4 restates as a count; its referee's construction realizes the odd close where three parents of the closing knot
  lie in one block, with values spread over several readers' bits.
- `MOST-FAILING-20261127-001` — at the ring of three's closure the maximum is the readers' matching; its referee's
  exchange check covers order independence, and its narrowing that the separated-reader form is shown only there is
  the question here.
- `TOY-PHASE-20261127-001` — the four-knot closure with readers the pairs no knot holds together: with one qubit per
  reader and two distinct Paulis the knots' operators multiply to −1; 7 of its 15 pairings into readers pass the toy
  theory. Placing that case inside larger closures (item 1) is immediate.
- `ENTANGLEMENT-READ-20261120-001` — the four mutually meeting knots as the holder pattern of the GHZ argument; the GHZ
  and Mermin–Peres requirements as the literature's.
- `FOUR-READINGS-20261120-001A` — operator readings of the census types after one sign is supplied (115 certificates),
  with no condition that operators be local to readers; the six-knot pattern (the literature's magic square) won by two
  readers who each receive a whole knot.
- `ERASURE-AND-CLOSING-SIGNS-20261121-001B` — a relative: closing laws on four mutually meeting founders.
- `THIRD-READER-20261126-001` — with values that commute, readers whom no knot joins share nothing a list cannot give.
  Here values fail to commute by declaration, and knots join the readers.
- `BIRTH-SIGN-WEIGHT-20261127-001` — a relative: a sign at birth and a joint weighting for separated readers, with a
  coherent preparation and fixed questions supplied (CHSH 2.1078 on a sibling pair); here the readers' values and
  their commutation come from the birth choices, and the game is one of certainty.
- `UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001` — unrelated objects (a sign meter on a split knot, weightings
  that every reveal order keeps), matched on shared words.
- This study adds the census of splits on the grown closures, the construction on every odd ring, which odd closes
  split and which do not, and a certificate for each split.

## Settled by construction (stated, not tested)

1. **A knot meeting every knot of an odd ring gives a strict split.** Let a knot h meet each knot of a ring r_1, …, r_n
   (n odd, each r_i meeting r_{i+1}, chords allowed), and pick meetings s_j of h with r_j and e_i of r_i with r_{i+1}.
   The failing pairs (s_j, e_{j+(n−1)/2}) (indices mod n) are disjoint and unheld. Each pair of h with a ring knot is
   met by exactly two of them, as is each pair of ring knots (n−1)/2 steps apart, and no other pair of knots by any, so
   every two checks commute. In the order h, r_1, …, r_n exactly one pair interleaves (the one whose ring meeting joins
   r_n to r_1), so the choice closes odd. It is a strict split with n readers, and a birth choice when its pairs are
   decidable (always at a round-1 closure). For n = 3 it is four mutually meeting knots: the three ways of splitting
   them into two pairs. For even n no pairing of this form (a fixed shift) commutes. The converse for three readers (a strict split with three
   readers only on four mutually meeting knots) is argued by the reviewer, not proved here.
2. **No split has fewer than three readers.** In a split each knot holds at most one value per reader, and the values
   outside readers commute with everything and are held twice, so they cancel. With one or two readers, each knot's
   reader part has at most two values, one per reader, and each value is held by two knots, so the knots fall into
   chains in which successive knots share a value. Multiplying the commuting reader parts along each chain cancels each
   value against its neighbour, so the checks multiply to +1. Two failing pairs never close odd: if they share a value,
   (x, y) and (x, z), commutation makes y and z a doubled meeting, and they interleave with x together; if disjoint,
   commutation makes their holders the same.
3. **Knots holding at most three distinctions** (the reviewer's classification, checked by hand). Each knot has 0, 2 or
   3 failing values, and the failing pairs of a strict commuting choice fall into units that commute on their own: two
   doubled meetings whose pairs interleave together; a six-knot unit (two knots meeting twice and each meeting a third,
   joined through it to a like three); four mutually meeting knots, which are then the whole closure; or two separate
   copies of these. The first two cost 0 (each splits into two halves listed apart), and connectedness excludes the
   last. So in a connected closure a strict odd split exists only on four knots meeting once each.
4. **The order-free sign.** Take each failing pair (x, y) in one orientation, and count for two knots u, v the failing
   pairs with x held by u and y by v. On birth choices this count has the same parity both ways, and the closing sign is
   the number of pairs of knots with an odd count, taken mod 2. (A pair interleaves exactly when the number of its
   holder pairs in increasing order is odd.) This restates A4 of the commutation-at-birth study as a count.
5. **The certificate.** Give each distinction its own qubit. A value inside a reader is X on its qubit times Z on the
   qubit of each earlier value of the same reader that fails with it; a value outside the readers is X on its qubit. The
   values are then local to their readers, fail to commute exactly on the failing pairs, and the checks (each knot's
   values multiplied in order) commute; in a connected closure their only dependency is the whole product.
6. **The readers' game.** Leave any one knot's check free (the certificate takes the last knot), fix the others at +1,
   and each value outside the readers at a sign to be found. A product of these operators is ±1 only if it holds every
   reader value an even number of times. Two such products with the same values outside readers would multiply to a
   product of checks alone holding every distinction an even number of times, and with one knot left out of a connected
   closure there is none but the empty one. So each such product is fixed by its values outside readers, the signs can
   be chosen so that none equals −1, and the state exists. In it the free check is −1, each knot's reader part has a
   definite value, and the reader parts multiply to −1, while a list of values gives +1.
7. **The fixtures by hand** (the reviewer's and the author's): the ring of five's closure has the construction of item
   1 as its only strict odd choice, so its fewest strict readers is five; the ring of four's closure has no split of
   either kind; the two joined rings of three have no strict split and exactly two odd splits, each of three readers
   holding three values (the classes of the colourings of the nine meetings by three colours, the literature's Latin
   squares, one meeting in each class failing with the other two); on three knots each meeting each of three others,
   condition (ii) puts each failing group inside one transversal of the three-by-three pattern, the parity checks then
   exclude splits that use transversals of both colourings (the reviewer's step), and inside one colouring every
   commuting choice closes even, so there is no split of either kind though whole choices close odd; the grown closure F
   has a three-dimensional space of commuting choices, and each of its four odd choices puts two values of one knot into
   one failing group, so it has no split.

## Predictions (frozen)

All counts are under one vote per census start unless marked.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: at the ring of three's closure the only odd birth choice is the readers' matching, a strict split with three readers, and the general search finds it; every split found is a birth choice, closes odd by the interleaving cost, by the order-free count and by the product of its certificate's checks, and passes items 5 and 6 (values local to readers, failing exactly on the failing pairs, commuting checks, only the whole product as a dependency, signs found, reader parts multiplying to −1 with at most one value per reader in each knot); at every code with at most 14 free choices, enumerating every birth choice agrees with the solvers on strict existence, the fewest strict readers, existence of a split of either kind and its fewest readers; the integer program and the satisfiability check agree on strict existence everywhere; no search is left unsettled (one that is goes to "not run"). | any gate fails |
| H | The hand results, checked on the run: every closure with a knot meeting every knot of an odd ring, with the split's pairs decidable, has a strict split with at most that many readers; no split anywhere has fewer than three readers; among closures whose knots all hold at most three distinctions, a strict split exists only on four knots meeting once each; every fixture as in item 7, and the grown ring of five's closure has no four mutually meeting knots and fewest strict readers five. | any differs |
| P1 | Odd rings only: every grown closure with a strict split has a knot meeting every knot of an odd ring with the split's pairs decidable, and its fewest strict readers is the length of the shortest such ring. | a strict split at a closure without one, or a different fewest number |
| P2 | Some grown closure has a split of either kind but no strict split. | none has |
| P3 | Measured, not predicted: closures with a strict split, with only a split of the other kind, and with neither, by closing round, by four mutually meeting knots, by the shortest odd ring around a knot and by the largest knot; the fewest readers, strict and of either kind; whole against birth choices at the 96 later closures; the same counts on the 173 finished census types, one vote per type. | — |
| P4 | Measured: the fewest failing pairs among odd birth choices against the fewest in a strict split, and whether every odd birth choice with the fewest failing pairs is a strict split. | — |

P1 is a judgment: item 1 gives the odd rings, and nothing found so far gives a strict odd split without one, but large
knots allow units that small ones do not (item 3's six-knot unit is one, and it closes even). P2 is a guess: the one
known pattern with readers holding three values (the joined rings of three) is not a grown closure, but readers of three
values only need three disjoint meetings, which the six-knot closures with large knots have. Neither was checked
against the run's rows. The fixtures were worked by hand.

## Runs and stop rule

One script, `readers.py`. Each closure is regrown and its code rebuilt with the commutation-at-birth study's code
(`local_commute.py`: holders, decidable pairs, one parity check per pair of knots, the interleaving cost). Then:

- **strict**: an exact integer program (scipy's `milp`, HiGHS, zero gap, 60 seconds) for the fewest failing pairs in an
  odd birth choice whose failing pairs are disjoint, and a satisfiability check of the same existence (CaDiCaL through
  pysat; parity checks as chains of exclusive-or clauses);
- **either kind**: satisfiability with a same-reader relation on unheld pairs (symmetric, transitive, never relating two
  distinctions a knot holds, containing every failing pair) for existence; for the fewest readers, satisfiability with
  r reader labels for r = 1, 2, … up to 12 (beyond 12: reported unsettled);
- **P4**: two integer programs, the fewest failing pairs in an odd birth choice, and the same with some distinction in
  two failing pairs;
- **odd rings**: for each knot, the odd rings among the knots it meets (up to nine knots) whose split pairs are
  decidable, and the shortest;
- **enumeration** of every birth choice where the code has at most 14 free choices, recording every strict odd choice's
  size and, for each odd choice with a split, its fewest readers (an exact colouring of its failing groups);
- **the certificate** of items 5 and 6 for each split found, with exact Pauli arithmetic.

A prefix of 50 closures in census order is timed first; if the whole would exceed an hour, the run is cut to a prefix in
census order, recorded as a deviation before it runs. A 4 GiB cap and one thread. The study stops when every prediction
is scored.

## Scaffolds

- **A316, what a reader is**: conditions (i) and (ii), with the strict form as the main case, and each reader answering
  from its own setting alone. Others are possible: a reader reading two commuting values of one knot jointly (which
  admits contextual readers), or readers as places in the structure (the third-reader study's). Tested by reporting
  strict splits and splits of either kind separately.
- **The certificate's realization** (one qubit per distinction), the knot left free (the last), and the state with the
  signs of the values outside readers (a supplied preparation): any other realization local to the readers would do;
  the certificate only shows one exists.
- Carried over from A314's study: the census starts, four rounds and the 40-knot cap.

## Review before the freeze

The advisor was unavailable (Fable 5.2 returned an unrecognized model, Fable 5.1 a usage limit; logged in
`docs/ADVISOR_HIVEMIND.md`). An independent reviewer (a separate session, read-only, reasoning by hand with no run)
checked the first draft. Changed before the freeze in response:

1. The first draft's basis for its prediction P3 was false: a ring of five with one loose distinction per knot stalls at
   round 0 (two knots are candidates only with a common neighbour). The ring of five's closure grows instead from the
   start named under Fixtures, which makes that prediction a hand result; it moved into H.
2. Most of the first draft's predictions followed from the hand arguments. They are now gates (H), and a prediction that
   can fail replaces them (P1, odd rings only). The joined rings of three and the three-by-three pattern are census
   types, not grown closures, so P2 is labelled a guess.
3. Item 3's sketch had two false steps (a six-knot pattern with knots of three distinctions has a strict commuting
   choice with three partners on three mutually meeting knots, and its doubled-meeting pairs cancel only across
   knots); its conclusion stands by the reviewer's classification, with connectedness stated.
4. The three-by-three argument skipped the step that excludes splits mixing both colourings; the reviewer supplied it.
5. "Separated" is now defined for this study, knots as questions, and the state and outside signs are scaffolds; the
   magic-square sentence is corrected.
6. The ring-of-five clause now says the construction is the only strict odd choice, and the enumeration records every
   strict size; "two steps on" is replaced by the exact index.
7. Whole choices are scored on all 96 later closures that are not outerplanar.
8. Added: the grown closure F with no split, the construction on every odd ring (the author's, generalizing the
   reviewer's note), and the reviewer's converse for three readers as an argument.
9. Prior work: the no-whole-state study's direction 3, the toy-phase pairings, A4 and the referee's exchange check, and
   the closing laws on four mutually meeting founders; the novelty line narrowed.
10. The reader-label search starts at one reader (so "fewer than three" is tested), and the enumeration now checks the
   fewest readers of either kind.

## Results (27 November)

> **Refereed (R1, confirmed with fixes, no Block; [report](referee-R1/report.md)).** Narrowings in full at the top of
> [the decision](decision.md): whole choices add splitting choices at 12 later closures; the game holds given the
> state, the outside signs and only each reader's own setting; the G row's certificates cover a certified
> representative of each reported minimum; the 198-closure shape is a pattern of the readers' values.

The run took 162 seconds under a 4 GiB cap with one thread, unit `readers-split-run`, no cut ([summary](summary.json),
[gates](gates.json), [rows](results.jsonl), [whole choices where birth choices lose the odd close](whole_only.jsonl),
[fixtures](fixtures.json), [census types](census_types.jsonl)). Counts are one vote per census start unless marked.

| # | Verdict | Count |
| --- | --- | --- |
| G | holds | At the ring of three's closure the only odd birth choice is the readers' matching, a strict split with three readers, and both searches find it. Every split found (at the 1,177 closures, the 173 types and the fixtures) passes its certificate. Enumeration agrees with the solvers at all 403 codes with at most 14 free choices. The integer program and the satisfiability check agree on strict existence everywhere. No search was left unsettled. |
| H | holds | 440 closures have a knot meeting every knot of an odd ring with decidable split pairs (423 rings of three, 17 of five), and each has a strict split with that many readers. No split anywhere has fewer than three readers. Of the 4 closures whose knots hold at most three distinctions, only the four-knot one has a strict split. The fixtures are as in item 7: the ring of five's closure, closed and grown (it closes in round 1, with no four mutually meeting knots), has fewest strict readers five and the construction as its only strict odd choice; the ring of four's closure has no split; the joined rings of three have no strict split and exactly two odd splits, each of three readers holding three values; the three-by-three pattern has no split; the grown closure F has no split. |
| P1 | fails | 252 of the 692 closures with a strict split have no odd ring around a knot: fewest strict readers 4 at 198, 5 at 49, 6 at 5. At the 440 with one, the fewest is the shortest ring's length. |
| P2 | holds | 39 closures have a split of either kind but no strict split: fewest readers 4 at 31, 5 at 6, 6 at 2. |

**P3, measured.**

| Population | Strict split | Only a split of the other kind | No split |
| --- | ---: | ---: | ---: |
| All 1,177 grown closures | 692 | 39 | 446 |
| — closing in round 1 (1,091) / round 2 (85) / round 3 (1) | 675 / 17 / 0 | 20 / 19 / 0 | 396 / 49 / 1 |
| — with four mutually meeting knots (423) | 423 | 0 | 0 |
| — with an odd ring of five around a knot and no four (17) | 17 | 0 | 0 |
| — with no odd ring around a knot (737) | 252 | 39 | 446 |
| One vote per finished census type (173) | 115 | 30 | 28 |

- By the largest knot (3, 4, 5, 6, 7, 8, 9 distinctions): strict 1, 21, 254, 326, 85, 5, 0; other kind only 0, 0, 22, 17,
  0, 0, 0; no split 3, 58, 187, 132, 54, 11, 1.
- Fewest readers in a strict split: 3 at 423 closures (exactly those with four mutually meeting knots), 4 at 198, 5 at
  66, 6 at 5. In a split of either kind: 3 at 433, 4 at 242, 5 at 51, 6 at 5; at 25 closures with a strict split, readers
  holding more values need fewer readers.
- Whole choices at the 86 later closures split at the same closures as birth choices (strict 17, either kind 36, in
  both), with the same fewest strict readers; R1 found that they add 567 splitting choices at 12 of them and lower the
  fewest readers of either kind at two. At the 10 later closures where birth choices lose the odd close, whole
  choices have no split of either kind.
- Finished census types: all 173 attain odd. Strict splits at 115, all with an odd ring around a knot (109 rings of three,
  6 of five), fewest strict readers 3 or 5; splits of the other kind only at 30; none at 28.

**P4, measured.** The fewest failing pairs among odd birth choices is 3 at 423 closures, 4 at 422, 5 at 127, 6 at 157, 7
at 9 and 8 at 39. Every odd birth choice with the fewest failing pairs is a strict split at 423 closures, exactly those
with four mutually meeting knots; at 37 closures with a strict split, some odd choice has fewer failing pairs than any
strict split.

**After the results (not frozen): the shapes beyond odd rings.** Grouping the fewest strict split at each of the 252
closures without an odd ring by the holders of its readers (up to relabelling) gives nine shapes. 198 have one shape:
four knots meeting pairwise except one pair, whose connection passes through a knot holding two reader values, with
the meeting opposite it doubled; the two copies of that meeting fail with the two halves of the passed connection.
(Narrowed by R1: the shape is of the readers' values and holders; the 198 full closures differ, and the passing knot
holds exactly two distinctions at only 25.) 20 have two such
passes, 16 and 13 have two other five-reader shapes, and 5 are single cases. In census types, whose knots all hold at
least three distinctions, every strict split has an odd ring.
