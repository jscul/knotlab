# Encoded readers: does every minimal strict split decode to four mutually meeting knots or an odd ring around a knot?

Epic `ENCODED-READERS-20261127-001`, under G18 Comparing growth laws, at the owner's go-ahead ("Yes, continue with the
readers line") on direction 1 of the readers study (`READER-SPLIT-20261127-001#1`). Design and predictions frozen before
the code was run on any predicted case, after a review (section "Review before the freeze"; the advisor was
unavailable). Results follow in sections of their own; nothing above them changes except by a dated notice. The
canonical K1–K3 test, the growth law, the birth rule (A314) and the reading of readers (A316) are unchanged.

## The question

The readers study found a strict split at 692 of the 1,177 grown closures where birth choices attain odd. In a strict
split, readers hold two values that fail to commute, every other pair of values commutes, and each knot asks each
reader at most one value. The fewest strict readers is three exactly where four knots meet pairwise. It equals n where
the shortest odd ring around a knot has n knots. The prediction that such rings are the only source failed: 252 closures
split without one, and at 198 the readers' values form one pattern, which reads as one reader encoded into two (that
study's referee, `referee-R1/shapes.md`). This study defines the step that undoes such an encoding and asks whether every
minimal strict split decodes to one of the two known games.

## Merging and base games

Work on a closed pattern (every distinction held by two knots) with a strict odd choice F: disjoint failing pairs of
unheld distinctions, every two knots' checks commuting, closing odd.

- **Merge.** Take two failing pairs (x′, x) and (y′, y) where x′ and y′ are held by the same two knots p and q, and x
  and y share a knot w (x held by w and r, y by w and s). If r = s, remove both pairs: they are a **doubled pair**. If
  r ≠ s, replace them by one pair (x′, z), where z is a new distinction held by r and s. The knot w may hold other
  values of F. A merge is **forced** when w holds no other values; by item 1, a knot holding exactly two values always
  allows one.
- **Base games.**
  - The **three-reader game**: four mutually meeting knots with three failing pairs, one for each way of splitting the
    four into two pairs.
  - The **ring game** of odd n ≥ 5: a knot h meeting every knot of a ring r_1, …, r_n. The failing pairs join h's
    meeting with r_j to the ring meeting (n−1)/2 steps on.
- **Decodes.** Some sequence of merges turns F into exactly one base game. Merges are searched, since their order can
  matter (item 3).
- **Minimal.** No proper non-empty sub-collection of F commutes on its own. Equivalently, the pairs' patterns of met
  knot pairs have rank one less than their number.

## In standard terms

A strict split is a parity proof between separated parties, each holding one qubit read in one of two ways. A forced
merge undoes the literature's two-bit repetition code on one party; a merge through a knot holding other values undoes
an encoding whose parity check is shared with other parties (item 5). The question is whether every minimal such proof
on growth's closures is the GHZ argument on four knots or the ring argument (the literature's contradiction for graph
states of odd rings), with parties encoded.

## Population and weighting

- **Fewest strict splits.** Every fewest strict split at each of the 692 closures with one (all of them, listed by
  satisfiability up to 1,000 per closure), one vote per census start.
- **Minimal strict odd choices with at most eight failing pairs** at the same 692 closures, listed up to 2,000 per size
  per closure, one vote per choice.
- **Small codes.** Every strict odd choice at the closures and finished types whose code has at most 14 free choices
  (mostly closures of four to six knots), one vote per choice.
- **Finished census types**, a separate population: the 115 of the 173 types with a strict split, one vote per type.
- **The literature's planarity** (P4): all 1,177 closures and 173 types. Planar here means the pattern of which knots
  meet contains neither five mutually meeting knots nor three knots each meeting each of three others as a minor.
- **Fixtures**: census start 786 (the four-reader pattern), the ring of three's and the ring of five's closures, and the
  reviewer's constructions in items 3 and 6.

## Prior work in the program

`python3 -B scripts/track.py objects "contraction of encoded readers, repetition code, decode strict split to three-reader game" --until 2026-11-27 --exclude ENCODED-READERS-20261127-001`
`python3 -B scripts/track.py objects "planar meeting pattern magic game state-independent operator reading" --until 2026-11-27 --exclude ENCODED-READERS-20261127-001`

- `READER-SPLIT-20261127-001` — the same splits. Its referee classified every fewest strict split at the 252 closures
  without an odd ring into nine patterns (2,102 labelled words). It showed that passing a meeting through a new knot
  and doubling its mate cannot give the pattern at census start 6171. This study adds merges through knots that hold
  other values, minimal choices beyond the fewest, and a search for the family's limits.
- `FOUR-READINGS-20261120-001A` — which sharing patterns admit a signed operator reading with no ordinary state (the
  literature's non-planar ones); P4 sets splits against that line.
- `EVENTUAL-R-20261126-001` — its advisor named Arkhipov's arrangements (each value in exactly two contexts) as the
  literature's form of the two-holder condition.
- `SECOND-CHECK-20261126-001` — the literature's repetition code in another reading, with no readers.
- `TOY-PHASE-20261127-001`, `REVIEW-LEADS-20261123-001` and `ERASURE-AND-CLOSING-SIGNS-20261121-001` — relatives of
  P4. The first places the four-readings study's operator certificates against the toy reading. The second reads the
  operator test at every stage of growth. The third finds the least drawn whole admitting a signed closing reading (five
  knots on ten distinctions).
- `CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001` — unrelated objects matched on shared words.

## Settled by construction (stated, not tested)

1. **No knot holds exactly one value of a strict split; one holding two allows a forced merge.** At a knot, the partners
   of its values must meet every other knot an even number of times. One partner would meet its two holders once each.
   Two partners must therefore be held by the same two knots.
2. **A merge keeps the choice.** The two pairs meet the pairs of knots {p, q} × {w, r} and {p, q} × {w, s}. The new
   pair meets {p, q} × {r, s}, which is the same mod 2, since w is counted twice; w's other values play no part. The
   interleaving count is additive in the holders in the same way, so the closing sign is unchanged. The new pair is
   unheld and disjoint from the others. A doubled pair meets every pair of knots twice and closes even.
3. **Order.** Forced merges alone give the same remainder in every order (the reviewer's argument, by the cases of two
   merges sharing no pair, one pair or both, and the literature's lemma of Newman). With merges through knots holding
   other values the order can matter. The reviewer's example has three three-reader games sharing two knots p and q,
   with the meeting of p and q held five times and two meetings passed through one knot w. One choice of pairs at w
   restores the three games; the other leaves six pairs that no merge or partition decodes.
4. **Counting.** A forced merge removes one knot holding values and one pair; a merge through a knot holding other values
   removes one pair only. Both base games have one more knot holding values than pairs. So decoding a split whose knots
   holding values number c more than its pairs takes exactly 1 − c merges through knots holding other values, when it
   meets no doubled pair. A fewest split meets none: a doubled pair would come from two sub-collections that commute on
   their own, and a fewest split has no proper odd sub-choice.
5. **The encodings.** In operators, a forced merge undoes one reader in the literature's two-bit repetition code: both
   holders of the doubled meeting read X₁X₂, the knot w reads the parity Z₁Z₂, and either half of the passed meeting
   reads the encoded Z. Through a knot holding other values, w reads Z₁Z₂ times other readers' values, so the code's
   parity check is shared.
6. **Three pairs are the three-reader game** (the reviewer's argument). A strict odd choice of three pairs has no knot
   holding two values, since merging would leave two pairs, which never close odd. So every knot holding values holds
   three, which makes four knots. Two pairs splitting them the same way would leave a lone pair, which does not commute.
7. **The limit of the family.** On closed patterns, decoding does not always succeed. The reviewer's nine-knot choice
   is one example. Its knots fall in three classes ({0,1,2}, {3,4,5}, {6,7,8}), its failing pairs are ({0,4},{1,3}),
   ({1,5},{2,4}), ({2,3},{0,5}), ({3,7},{4,6}), ({4,8},{5,7}), ({5,6},{3,8}), ({2,6},{0,7}), ({1,7},{2,8}) and
   ({0,8},{1,6}), and every knot holds four values. It is strict, commuting, odd and minimal, and has no four mutually
   meeting knots and no odd ring around a knot. So the question is about growth's closures, not a theorem about all
   patterns.
8. **The literature's operator solutions.** Every distinction is held by two knots, so the closure's parity system with
   the closing law flipped is the literature's graph-incidence game. It has an operator solution, the literature's
   state-independent parity proof (Cleve and Mittal), exactly when the pattern of meetings is not planar (Arkhipov,
   arXiv:1209.3819). Parallel meetings and knot sizes do not change this. It concerns the pattern, not the birth
   choices. The strict splits here are state-dependent proofs, so P4 compares different things and only measures them.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates, including the hand results scored on the run: the readers study's fewest strict counts recomputed (3 at 423 closures, 4 at 198, 5 at 66, 6 at 5); the fewest-split listing reproduces the referee's count of fewest words at each of the 252 closures without an odd ring (2,102 in all); every listing reaches its end (any closure at the cap is reported, and the integer program's split must be among the listed where the listing is complete); every fewest split at the 692 closures decodes to exactly one base game, with no doubled pair met and with 1 − c merges through knots holding other values (item 4); every merge checked afresh (every two checks commute, the closing sign odd in index order and in a second seeded order, pairs disjoint and unheld); forced merges give the same remainder under three seeded orders; census start 786's fewest splits decode by one forced merge to four mutually meeting knots; the ring of five's and ring of three's closures are base games with no merge; the reviewer's nine-knot choice of item 7 is strict, commuting, odd, minimal and does not decode, and its example in item 3 decodes in one order of choices at w but not the other; no search unsettled. | any gate fails |
| P1 | Every minimal strict odd choice with at most eight failing pairs, at every one of the 692 closures, decodes to exactly one base game. | any one does not |
| P2 | Every minimal strict odd choice at the small codes (grown closures and census types, any number of pairs) decodes to exactly one base game. | any one does not |
| P3 | Measured: for every fewest split, the base game reached, the merges (forced, and through knots holding other values), c, and the sizes in the closure of the knots merged through; for the minimal choices of P1 and P2, the same by number of pairs; for strict odd choices that are not minimal, what remains after merging. | — |
| P4 | Measured: the literature's planarity of the pattern of meetings against the split kinds (strict, other only, none) at the 1,177 closures and the 173 types. | — |

P1 and P2 are judgments. Every known minimal strict odd choice on growth's closures decodes: the nine recorded
patterns, by hand, and the three-pair choices by item 6. The search for exceptions covers choices that are not fewest.
The open risk is a minimal choice like item 7's on a grown closure: knots holding four or more values and no knot
merging. Item 7 needs nine pairs, and on closures of four to six knots I expect none. The population of P1 extends past
the small codes, and that of P2 past eight pairs.

## Runs and stop rule

One script, `decode.py`, reusing the readers study's code (`readers.py`: the code of a closure, the integer program for
the fewest strict split) and the commutation-at-birth study's growth:

- **listing**: satisfiability (CaDiCaL through pysat): failing pairs disjoint, sign odd, exactly k pairs, each solution
  blocked in turn. The fewest splits are listed up to 1,000 per closure, and every strict odd choice of k = 3, …, 8
  pairs up to 2,000 per k per closure, each call with a time limit. A run that stops at the limit or the cap is reported.
- **minimal**: the rank of the pairs' patterns of met knot pairs, over GF(2), is one less than their number;
- **merging**: a search over merges (depth first, remainders remembered by their sorted holder pairs, at most 20,000
  states per choice), each merge checked afresh; forced merges also under three seeded orders;
- **base games**: recognized directly (four knots and their three ways of splitting; a knot of degree n in the choice, a
  ring of n knots, each pair (n−1)/2 steps on);
- **small codes**: enumeration of every birth choice where the code has at most 14 free choices, keeping the strict odd
  ones;
- **planarity**: networkx's planarity test on the pattern of which knots meet.

A prefix is timed first; if the whole would exceed an hour, the run is cut to a prefix in census order, recorded as a
deviation before it runs. A 4 GiB cap and one thread. The study stops when every prediction is scored.

## Scaffolds

- **A317, decoding by merges**: a split and its merges count as the same game, encoded. Another reading would count
  each encoding as a new game. Tested: P3 reports the encodings themselves.
- **The two base games**: the family is the two known games; a choice outside it shows a third.
- **The caps** (1,000 fewest splits, 2,000 choices per size, 20,000 search states, eight pairs for P1): reported where
  reached.
- Carried over: the census starts, four rounds and the 40-knot cap (A314's study), and A316.

## Review before the freeze

The advisor was unavailable (Fable 5.2 returned a usage limit; logged in `docs/ADVISOR_HIVEMIND.md`). An independent
reviewer (a separate session, read-only, reasoning by hand with no run) checked the first draft, and the design
changed in response:

1. **The first draft's merge was too narrow, and its P1 would have failed.** That draft merged only at knots holding
   exactly two values. The five-reader pattern at 16 to 18 closures (census start 6171) and two six-reader cases (starts
   4786 and 6131) would not have decoded under it. With merges through knots that hold other values, all nine recorded
   patterns decode by hand. The general merge is now the rule, and the old P1, now entailed, is a gate.
2. **Order.** Forced merges are confluent, but general merges are not (item 3's example). "Decodes" now means that some
   sequence succeeds, found by search.
3. **The first draft's P2 would have failed for reasons unrelated to encoding.** Its "an odd number of base games" was
   forced, and choices that are not minimal can carry even units that never merge. P1 and P2 now concern minimal
   choices.
4. **The nine-knot choice of item 7** shows decoding is not a theorem about closed patterns. The counting identity
   (item 4) and the three-pair argument (item 6) were added.
5. **Code.** The draft's order-free sign check equals the first sign check on every choice, so a second seeded knot
   order replaces it. An empty remainder no longer counts as odd. P3 is taken over every fewest split, the listing has
   time limits, and the cap case is handled.
6. **Words.** "Planar" is the literature's, defined once by minors. The record's "doubled sides" became doubled meetings.
   The 198-closure pattern is that of the readers' values, as its referee qualified.
