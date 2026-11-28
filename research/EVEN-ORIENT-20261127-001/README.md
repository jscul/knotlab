# Why growth's minimal even choices can be oriented: the smallest non-orientable even choices and the births they need

Epic `EVEN-ORIENT-20261127-001`, under G18 Comparing growth laws, at the owner's go-ahead ("Yes continue") on direction
1 of the cross-pair study (`CELL-SIGN-20261127-001#1`). Design and predictions were frozen before the code was run on any
predicted case, after a review (section "Review before the freeze"). Results follow in sections of their own; nothing
above them changes except by a dated notice. The canonical K1–K3 test, the growth law, the birth rule (A314) and the
reading of failing pairs as cells (A318) are unchanged.

## The question

On the closures grown from the census starts, every minimal strict even birth choice can be oriented. That is the
cross-pair study's P3, and its referee's exhaustive replay found 6,534 of 6,534. So there a minimal strict choice closes
odd exactly when its cycles admit no balanced orders. At the 115 census types with a strict split, 20,029 of 35,300
minimal strict even choices through eight pairs cannot be oriented.

The referee found that the difference disappears at matched size. Every minimal even choice of five or six pairs is
orientable in both populations. The census's non-orientable ones have seven or eight pairs, and growth's even choices
have at most six. This study asks why: what the smallest non-orientable even choices need, and whether growth can make
them. Everything here concerns choices **covered twice** (every cross pair in exactly two failing pairs). The 236
minimal even grown choices with a cross pair covered four times are outside it; all are orientable.

## Seen while designing (before the freeze; not predicted)

- **Growth makes no further closures.** Ordinary parity growth of the 7,075 census starts to ten rounds and 3,000
  knots closes the same 1,819 as at four rounds and forty knots:
  - 1,713 in round 1, with four to six knots;
  - 105 in round 2, with seven to nine;
  - 1 in round 3, with eleven.

  The rest stall or keep growing.
- **Whole choices at the larger closures.** At the 106 closures with seven or more knots, whole choices give no
  minimal strict even choice of more than two pairs. A whole choice takes every unheld pair, not only those decidable
  at birth.
- **The census types hold at most one distinction on each pair of knots.** None of the 173 has a **doubled meeting**,
  two knots sharing two distinctions (the readers study's term). The 41 types with a strict split that also have a
  non-orientable even choice all have seven knots and 14 to 21 distinctions (the referee's listings).
- **The extension's starts.** FORBID-EDITS's 3,000 sampled starts of six to eight knots close 115 times:
  - 75 in round 1, with seven to nine knots;
  - 35 in round 2;
  - 5 in round 3.

  Each closure has two to seven doubled meetings.
- **Three six-pair kinds by hand** (item 1), each checked singly with the study's code: (a) and (b) by this thread,
  (c) and a pinched seven-pair one by the reviewer. Each closes even and cannot be oriented. The reviewer also found a
  seven-pair one on eight knots, which the enumeration does not reach.

## Argued by hand (each checked in the run)

- **Separation.** A choice is separated when each knot whose failing pairs make several cycles is split into one knot
  per cycle. This keeps the sign, orientability and the cross pairs, which stay distinct (the cross-pair study and its
  referee).
- **Counts.** For a choice covered twice with F failing pairs and V knots after separation, there are 2F cross pairs
  and the Euler count is V − F.
- **The literature's surfaces.** The projective plane, the Klein bottle, the torus and the sphere are the
  literature's names for the separated structures. The program's objects are the choices.

1. **A non-orientable even choice covered twice has at least six failing pairs, and three kinds at six exist.**
   - **The bound.** Not orientable means Euler count at most 1. A count of −1 or less needs 2F ≤ (F − 1)(F − 2)/2
     cross pairs on F − 1 knots, so F ≥ 7. So with F ≤ 6 the choice is one of two:
     - a projective plane on F + 1 ≤ 7 knots;
     - a Klein bottle on F ≤ 6 knots, which needs at least five, since 2V cross pairs need V(V − 1)/2 ≥ 2V.
   - **On the projective plane**, even means two-colourable cross pairs after separation (the cross-pair study, item
     3). But 2(V − 1) cross pairs between two classes of knots number at most V²/4, so V ≥ 7. With F ≤ 6 that leaves
     V = 7 and F = 6, and the cross pairs are all twelve pairs between a class of three and a class of four: the
     literature's K_{3,4}.
   - **On the Klein bottle**, the same item, read through the literature's intersection form, says even holds
     exactly in two cases: the cross pairs are two-colourable, or a cycle of cross pairs is odd exactly when it
     reverses orientation. Two-colourable needs 2V ≤ V²/4, so V ≥ 8.
   - **On five knots** all ten pairs are cross pairs. Each of the five failing pairs leaves out one knot, and their
     values take each pair of knots once. Every such choice is the literature's torus (the reviewer's listing; gate
     G(i)).
   - So the fewest pairs is six, and there are three kinds at six:
     - **(a) The seven-knot projective plane.** This is the encoded-readers referee's even control. Every pair of a
       class of three knots holds two of its values; every pair of the class of four holds one. Each failing pair
       joins one value of a doubled pair with the value of a single pair. The three doubled pairs take the three ways
       of splitting the class of four into two pairs.
     - **(b) A six-knot Klein bottle on the literature's K_{2,2,2}.** Two rings of three knots, each knot sharing two
       distinctions with one knot of the other ring. Each failing pair joins one value of such a doubled meeting with
       the value of a ring meeting that avoids both its knots. Its orientation double cover is a two-colourable
       quadrangulation of the literature's torus on twelve vertices (a twisted one), and the deck map exchanges the
       colour classes.
     - **(c) A second six-knot Klein bottle**, the reviewer's. It has one doubled meeting; its cross pairs are every
       pair of knots except a path of three pairs. Both (b) and (c) are of the second Klein-bottle case.
2. **What each kind needs.**
   - (a) needs three doubled meetings, on the class of three.
   - (b) needs three, one at every knot.
   - (c) needs one. But each of its other four knots has partners (the knots it shares the choice's values with) that
     all meet one further knot of (c).
3. **A birth takes at most one distinction from each parent.** The engine checks that a newborn's parents are distinct,
   and a newborn's fresh distinctions go one to each later birth. So at a grown closure two knots share two
   distinctions only if both are start knots. (Checked at every closure, gate G(ii).)
4. **The join rule** (the guide, lesson 8.1). Live knots are joined by one newborn only when every two of them meet a
   common knot and no knot meets them all. For the census starts, which have at most five knots and twelve
   distinctions, this gives:
   - **(b)** needs six start knots, so it is at no closure grown from a census start.
   - **(a)** needs its class of three among the start knots and its class of four meeting pairwise. With at most two
     more start knots, two newborns would have to meet each other, which takes a second round. This is not excluded by
     hand; the referee's replay found none.
   - **(c)'s** two knots on the doubled meeting are start knots. Each other knot, born holding exactly its values of
     the choice, would be joined from partners that one knot meets all of, which the rule forbids. Born with one more
     parent, it holds one more distinction.
     - B3 is (c) with one such knot left out and its three distinctions loose. It has twelve distinctions on five
       knots, and it is census start 6830.
     - B4 adds one loose distinction at the knot that meets the three, making thirteen, one more than the census
       allows.

**The explanation under test.** The census closures can be oriented because each six-pair kind needs one of three
things:
- six start knots, for (b);
- two newborns that meet, which takes a second round, for (a);
- a birth that the join rule forbids unless it takes one more distinction than the census starts have, for (c).

The seven-pair and larger kinds need more knots holding the choice's values than the census closures of seven or more
knots offer; there whole choices give no even choice beyond two pairs (seen while designing). If this is right, growth
makes non-orientable even choices from starts with more knots or more distinctions.

## Population and weighting

- **E, abstract choices.** Every labelled minimal choice covered twice whose failing pairs use exactly V knots:
  - V = 4, 5 and 6, at any size;
  - V = 7, through seven pairs.

  Each failing pair is a cycle of four distinct knots with its own two values. Every pair of knots is a cross pair of
  zero or two failing pairs, and the cycles are joined through shared cross pairs. Pinched knots are allowed. The
  choices are counted labelled and up to relabelling (one vote per class). Two failing pairs on one cycle (a repeated
  cycle, the literature's sphere of two cells) are left out, since they are orientable. Not listed: eight or more knots.
  So seven-pair choices on eight knots, such as the reviewer's projective plane, are missing.
- **B, built starts.** Each is grown by ordinary parity growth to ten rounds and 3,000 knots, and each birth's parents
  are recorded.
  - **B1:** the holding of (b), with one loose distinction at each knot of one ring.
  - **B2:** three knots each pair of which shares two distinctions, plus a ring of three more knots, each with one
    loose distinction, and one meeting between the two groups. If the closing birth joins the ring's three loose
    distinctions, the closure holds (a), with the newborn in the class of four.
  - **B3 and B4:** as in item 4.
  - **The B1 family:** the holding of (b) with zero to two loose distinctions at each knot, 728 starts (not all zero),
    one vote per start. It tests the scaffold "which knots carry loose distinctions". The values of (b) are start
    values, so (b) is present at every closure of the family. The family therefore measures which placements close.
- **X, larger starts.** FORBID-EDITS's extension: 1,000 labelled draws each of six, seven and eight start knots, seeds
  20261126 + n.
  - The weighting: each pair meets with probability 1/3, with multiplicity one or two equally, and loose counts 0, 1
    and 2 equally. A draw is kept when connected, with three places at every knot and at most 18 distinctions.
  - Growth runs to ten rounds and 3,000 knots, giving 115 closures, one vote per draw.
- **X2.** A second sample under the same weighting, 10,000 draws per size, seeds 20261200 + n (not overlapping the
  extension's); measured.
- **C, census-start closures.** The 1,819 closures of the 7,075 census starts at four rounds and forty knots, as the
  referee had them, under birth choices and whole choices.
- **Census types.** The referee's counts; no new computation.
- **Words.** At every closure, every minimal strict choice among the eligible pairs is listed exhaustively, one vote
  per labelled choice. The cap is 200,000 per closure and is reported if reached. Two-colourability of a grown choice
  is read before separation.

## Prior work in the program

`python3 -B scripts/track.py objects "non-orientable even commuting choice doubled meetings founders smallest Klein bottle projective plane" --until 2026-11-27 --exclude EVEN-ORIENT-20261127-001`
`python3 -B scripts/track.py objects "larger starts six seven eight knots extension sampled starts closures grown" --until 2026-11-27 --exclude EVEN-ORIENT-20261127-001`

- `CELL-SIGN-20261127-001` and its referee — the question, the counts and the size comparison. This is the referee's
  direction 2, "distinguish size from the growth rule".
- `ENCODED-READERS-20261127-001`, referee — the even seven-knot control, kind (a).
- `READER-SPLIT-20261127-001` and `LOCAL-COMMUTE-20261127-001` — birth choices (A314) and the doubled meetings at the
  closures.
- `FORBID-EDITS-20261126-001` — the extension's starts and weighting, and the engine wrapper.
- The join rule and groups of three — the guide, lesson 8.1, and the growth studies it cites.
- `UPPER-GROWN-20261127-001` — the same move. A built start shows what one round of growth makes when sampled stages
  show none.
- `RULER-FLAT-20261111-001`, `LONG-LOOP-20261111-001` and `KNOTS-ALONE-20261111-001` — non-orientable two-fold weaves of
  three-place knots, a different object, matched on words.

## In standard terms

The choices covered twice are quadrangulations of closed surfaces. By the cross-pair study's item 3, the closing sign is
the pairing of the class of odd cycles of the cross pairs with the orientation class. The literature on the parity and
colouring of quadrangulations includes:
- Youngs, "4-chromatic projective graphs" (J. Graph Theory 21, 1996): on the projective plane the non-bipartite
  quadrangulations are 4-chromatic;
- Archdeacon, Hutchinson, Nakamoto, Negami and Ota, "Chromatic numbers of quadrangulations on closed surfaces" (J. Graph
  Theory 37, 2001);
- Mohar, Simonyi and Tardos, "Local chromatic number of quadrangulations of surfaces" (Combinatorica, 2013).

The minimal sizes here are presumably known there: bipartite quadrangulations of the projective plane need seven
vertices, and the Klein bottle has quadrangulations on six. That will be checked before any claim of novelty. This
study adds the comparison with growth: which of these the birth and join rules let a grown closure hold.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates:<br>(i) the enumeration finds no non-orientable even choice with at most five pairs; it finds kinds (a), (b) and (c); Euler count 0 on five knots occurs and is always orientable; the sign equals the same-order parity on every structure; the general machinery and an independent brute-force orientation test agree with the fast one on every non-orientable even class;<br>(ii) item 3 holds at every closure examined;<br>(iii) the census-start closures reproduce the referee's replay: 1,819 closures, 6,534 minimal strict even birth choices, all orientable, and 4,803 odd, none orientable;<br>(iv) every listing finishes below its cap, and every orientation is decided. | any gate fails |
| P1 | Every non-orientable even choice of E on at most six knots, or with at most six pairs on seven knots, puts two of its values on one pair of knots. With at most one value on each pair of knots (as at every census type), there is then none with fewer than seven pairs. | a choice with at most one value on every pair of knots |
| P2 | B1 and B2 close. B1's closure holds kind (b), and B2's holds kind (a) with a newborn's distinction among its values. No birth of B3 has parents exactly its knots 0, 1 and 3, all of which meet knot 4. | either start does not close, either kind is missing, or B3 has such a birth |
| P3 | Some closure grown from the extension's 3,000 starts has a minimal strict even birth choice that cannot be oriented. | none has |
| P4 | Measured, not predicted:<br>• for each grown population (B1 family, X, X2, C), the closures by knots and the minimal strict birth and whole choices by size, sign and orientability;<br>• for each non-orientable even choice: its start knots, newborns, doubled pairs, separated Euler count and kind, and whether it uses a newborn's value;<br>• for E, the classes by knots, pairs, kind, separated Euler count and two-colourability;<br>• B4: whether it closes and holds (c) with a newborn's values. | — |

**Why these predictions.**
- P1 is a judgment.
  - By the reviewer's cases at six pairs, every kind has a doubled meeting.
  - Not excluded by hand: a choice of Euler count −1 on six knots (seven pairs on fourteen of the fifteen pairs of
    knots) with no pair holding two values.
- P2 is a judgment about the engine.
  - B1's and B2's closing births are groups of three on rings, with no knot meeting all three. With one loose
    distinction at each of three knots, the closing birth has so far joined them (the readers study's ring fixtures).
  - B3's bar is the join rule as the guide states it.
- P3 is a judgment.
  - The extension's closures have seven to thirteen knots and two to seven doubled meetings. Kind (c) needs only one
    doubled meeting.
  - Under this weighting, though, the exact holdings of the six-pair kinds are rare.
- Reading the outcomes:
  - If P3 fails while P2 holds, growth can make these choices but this weighting rarely gives it the starts.
  - If B3 has the barred birth, the join rule is not what keeps (c) out.

## Compute

Timed on a prefix before the freeze:
- E takes about 4 s on six knots (8,547 labelled structures) and 22 s to list seven knots through seven pairs (614,232).
  Eight knots through six pairs took 145 s, and seven pairs on eight knots was cut as too long for its value.
- Growth takes 15 s for the extension's 3,000 starts; listing is under a second per closure.
- The B1 family's 728 starts grow in seconds. The second sample's 30,000 draws take a few minutes.

The whole run is estimated at 10 to 20 minutes. It runs as one systemd unit under a 4 GiB cap with one thread,
registered in `docs/LONG_RUNNING.md`.

## Review before the freeze

The advisor was unavailable (Fable 5.2 returned an unrecognized model and Fable 5.1 a usage limit; logged in the
hivemind). An independent reviewer read the design and code and reasoned by hand. Its own small listings covered five
knots or fewer only, and it ran no predicted case. Its findings and what changed:

1. **Blocking.**
   - **P1's second clause was false by a hand construction.** The reviewer's kind (c) is a six-knot Klein bottle with
     one doubled meeting. The clause, that every knot lies on a doubled pair, is dropped. (c) is now in item 1, in gate
     G(i) and among the built starts. Item 4 and the explanation were rewritten around the join rule: in (c), each knot
     off the doubled meeting has partners that one knot meets all of (the reviewer's suggestion, tested by B3 and B4).
   - **The seven-knot bound disagreed** between the README (seven pairs) and the code (eight). Both now say seven.
2. **Should fix.**
   - **E misses seven-pair choices on eight knots** (the reviewer's projective plane on eight knots). This is stated
     as a gap; eight knots were too costly. "About four values per knot" was wrong (it is 4F/V) and is no longer used.
   - **The agreement check was not independent** (both called the same orientation code). An independent brute-force
     orientation test was added.
   - **The five-knot gate passed on an empty list.** It now requires the case to occur.
   - **P2 and the family were scored by size**, so any six-pair choice would pass. They are now scored by structure
     (isomorphism to (a), (b) and (c)). The family's limit is stated: (b) sits on start values, so the family measures
     which placements close.
   - **The double-cover description was wrong.** No plain grid works, so it now reads as above.
   - **The scope is choices covered twice**, now stated in the question.
   - **The second sample's seeds overlapped the extension's** (20261128 + 6 = 20261126 + 8). They are now
     20261200 + n.
   - **Words.** The literature's surface names are marked at first use. "Side" became "class". The two-cell sphere is
     a "repeated cycle", leaving "doubled" for pairs of knots. "Doubled meeting" is defined where first used, and K_{3,4}
     is written as such.
   - **Overclaims.**
     - The title and question now say "minimal even choices", since the cross-pair referee found two non-minimal strict
       even choices that cannot be oriented.
     - "Settled by hand" became "Argued by hand".
     - The census types are those with a strict split.
3. **Notes.**
   - Items 1–3 were otherwise confirmed: the bounds, K_{3,4}'s forced value pattern, and the engine's rule (`freelib`
     groups are distinct live knots, `rival_growth` asserts distinct parents, old holdings never change).
   - Gate G(iii) can match: the growth limits, the eligibility by dates and the circuit listing agree with the
     referee's.
   - The enumeration is complete without repeats.
   - The literature was named with confidence for the three works cited above; K_{2,2,2} on the Klein bottle could not
     be cited.
   - The Klein-bottle case split in item 1 was added at the reviewer's suggestion.
