# Three smallest even non-orientable choices and why the census misses them

> **Referee report R1, 28 November 2026: confirmed with fixes, one Block** ([the report](referee-R1/report.md)). The
> six-pair minimum, the three kinds and all 622,841 labelled structures reproduce; the census closures have no even
> non-orientable choice under either eligibility rule. Read this record with these corrections (logged in
> `docs/CORRECTIONS.md`):
> - **Block: P3 fails in its frozen scope.** The question says everything concerns choices covered twice. The declared
>   sample's one qualifying closure (draw 3) covers a pair of knots four times in all 32 of its choices, so under that
>   scope the sample had zero of 115. The all-coverage reading passed at one of 115; the second sample later found two
>   twice-covered positives among 1,168. The failed prediction is not rescued by the second sample.
> - **Narrowing: what the census misses, and why.** All three six-pair kinds need at least thirteen start distinctions
>   for connected growth that closes after a birth (the referee's proof by hand, which also closes the gap left at (a):
>   meetings with a newborn join consecutive rounds). The five-knot example attains thirteen for (c); the examples for
>   (a) and (b) also exceed the census's five knots. In (b) the marked holdings already exist at the start. That larger
>   kinds are absent from the census closures is a finite replay result.
> - **Narrowing: the join rule.** The common-knot veto applies to groups of three or more. Growth takes maximal
>   eligible groups, then uncovered compatible pairs, and gives each remaining loose distinction a one-parent birth.
>   Removing only the veto at census start 6830, with its twelve distinctions, closes it in one round holding four copies
>   of (c): a direct control of the rule. In B2 and B4 the values are start distinctions that acquire a newborn as their
>   second holder.
> - **Narrowing: two counts.** Of the 728 placements on (b)'s holding, 44 close, 20 in round one and 24 in round two,
>   while 571 stall and 113 reach the ten-round limit. Whole choices add two sampled closures beyond the three birth
>   positives: 5 of 1,283 at any coverage and 4 of 1,283 covered twice. The second sample's and the family's whole
>   choices were completed by the referee; the closing code had skipped them.
> - **Not a block.** The freeze: the scoring code and prediction text were frozen before the run, but the fixtures and
>   the abstract listing's counts had been seen. Scope words: the 622,841 are labelled by knot; the repeated cycle (an
>   orientable two-pair class) is left out; at seven pairs on seven knots, 18 of 144 classes are even and non-orientable;
>   the samples keep starts with at least three places at every knot. Credit: the six-vertex minimum is known, and the
>   seven-vertex bipartite example and a corrected catalogue holding both six-vertex kinds are published (Liu,
>   Ellingham and Ye; Matsumoto, Nakamoto and Yonekura; Fijavž and coauthors). This study adds the comparison with the
>   holdings and births that growth allows.


Epic `EVEN-ORIENT-20261127-001`, at the owner's go-ahead on direction 1 of the cross-pair study. Design, frozen
predictions, review and results: [README.md](README.md); code [evenorient.py](evenorient.py); outputs
[summary.json](summary.json), [gates.json](gates.json), [abstract.json](abstract.json), [built.json](built.json) and the
population rows. Every choice is listed exhaustively in each completed arm (the second sample's and the family's whole
choices were completed by the referee). Closures are one vote per draw or census start; choices are one
vote per labelled choice; abstract choices are one vote per class up to relabelling. Refereed (R1, confirmed with fixes,
one Block on P3's scope; [report](referee-R1/report.md)).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what keeps non-orientable even choices out of growth's census closures | **Status:** Partially successful | All gates hold; P1 and P2 hold; P3 holds only at all coverages, and fails in its frozen twice-covered scope (R1, a Block) |
| Local direction — why growth's census closures can be oriented | Retire | Answered for the six-pair kinds: each needs at least thirteen start distinctions (R1, by hand), more than any census start has; larger kinds are absent from the census closures by finite replay |
| Broader exploration — the readers' games as cells on grown closures | Continue | The minimal non-orientable even choices are now listed, three kinds at six pairs; what a closure's pattern carries with nothing chosen is the next question |
| Long-term goal — G18 Comparing growth laws | Capability gained | For the six-pair kinds the difference between growth's closures and the census types lies in the starts, and removing the common-knot veto at a census start lets growth make (c) (R1) |

A non-orientable even choice covered twice needs at least six failing pairs. There are three kinds at six:
- (a) a seven-knot projective plane;
- (b) a six-knot Klein bottle, found by hand here;
- (c) a second six-knot Klein bottle, found by the reviewer.

Every one below seven pairs puts two values on one pair of knots (P1, exhaustive through six knots and through six
pairs on seven). So the census types, which never do, start at seven.

Growth gives two knots two shared distinctions only between start knots, since a birth takes one distinction from each
parent. Its join rule vetoes a group of three or more live knots that one knot meets entirely; growth takes maximal
eligible groups, then uncovered compatible pairs, and gives each remaining loose distinction a one-parent birth (R1).
All three six-pair kinds need at least thirteen start distinctions for connected growth that closes after a birth (the
referee's proof by hand), while census starts have at most twelve, and five knots:
- (b) needs six start knots.
- (c)'s missing birth is vetoed. Census start 6830, which is (c) with one knot left out, stalls. Removing only the veto
  closes it in one round holding (c), a direct control of the rule (R1).
- (a) needs two newborns that meet, which takes consecutive rounds (R1).

Built starts past those bounds close into them in one round (P2). In B2 and B4 the values include start distinctions
that acquire a newborn as their second holder; in B1 the marked holdings already exist at the start. Under the
extension's weighting, sampled starts of six to eight knots have such a choice at 3 of 1,283 closures at any even
coverage and at 2 of 1,283 covered twice. The declared sample alone had one at all coverages and none covered twice, so
P3 fails in its frozen scope (R1). That larger kinds are absent from the census closures is a finite replay result.

The exactness on growth's census closures (a minimal strict choice is odd exactly when it cannot be oriented) belongs,
for the six-pair kinds, to the census starts' bounds rather than to growth.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Native carriers: sets of knots whose own candidate cells (every unheld pair held within the set) form exactly one closed choice, as four mutually meeting knots carry the projective plane with nothing chosen. Does growth's pattern carry these, and which surfaces? (The cross-pair study's direction 2, sharpened) | 3/3 — Barrier | 2/3 — Testable | List such sets at every grown closure and census type → a native carrier beyond four mutually meeting knots, or none | Selected · next |
| 2 | Why no seven- or eight-pair kind appears at the census closures, by hand | 1/3 — Incremental | 2/3 — Testable | Run the hand argument of item 4 on the 20 seven-pair classes and the census's eight-pair kinds → a rule that bars each, or a start that makes one | Alternative · deferred |
| 3 | The literature's minimal quadrangulations: are (a), (b), (c) and the six-knot one of Euler count −1 known? | 1/3 — Incremental | 3/3 — Ready | Read the quadrangulation literature cited in the README → credit, or a note | Alternative · deferred |
| 4 | A principle drawn from growth itself for the sign | 3/3 — Barrier | 1/3 — Stated | Name one quantity → a candidate, or none | Alternative · deferred |
| 5 | Back to a native line: G1 Space from a law, idle since 21 November | 3/3 — Barrier | 1/3 — Stated | Reread G1's open question → a bounded test | Alternative · deferred |

1. **Payoff 3/3:** the readers' contradiction is a closed non-orientable cell structure. If growth's own pattern carries
   one with nothing declared beyond the cells themselves, a surface comes from the law. That would tie G18 to G1.
   **Concreteness 2/3:** the candidate cells are defined, and the sets can be listed at every closure. Whether a carrier
   beyond four mutually meeting knots exists is the open risk. It continues the readers line at a STOP, by the owner's
   standing rule to take the next 3/3 direction.
2. **Payoff 1/3:** it would complete this study's explanation, which rests on the replay for these sizes.
   **Concreteness 2/3.**
3. **Payoff 1/3:** credit. **Concreteness 3/3.**
4. and 5. **Payoff 3/3**, **Concreteness 1/3**, as before.

**STOP** on the local direction: the question is answered within the tested scope. The census starts' bounds, through
two rules of growth, keep the non-orientable even choices out, and growth makes them once the bounds are passed.
**GO** on the readers line with direction 1. It stops when every grown closure and census type has its native carriers
listed, or when the first size that cannot be finished is reached.

**Corrections:** none. The reviewer's hand construction of (c) refuted the drafted P1's second clause before the
freeze, so nothing had left the session.

**Goals:** G18 gets a "capability gained" checkpoint row. No goal changed.

**Assumptions:** A319 (new, scaffold): the hand-built starts B1–B4 with loose distinctions placed by hand. A318 (the
cell reading) gets a history line.

**Scaffolds:**
- The built starts are hand-built (A319). The B1 family tested the placement of loose distinctions: 44 of 728 close,
  all holding (b). B2 and B4 are single starts. Their claim is existence ("growth can make these"), which one start
  suffices for. The sampled starts, under the extension's declared weighting, make the same point without a hand-built
  start.
- The second sample's seeds (20261200 + n) were chosen to avoid the extension's.
- The enumeration covers choices covered twice through seven knots (through seven pairs on seven). Eight knots were not
  listed.

**Basket:** `BOTH-LONG-20261126-001#1` (3/3, 3/3), `VALUE-CHANGE-20261126-001#1` (3/3, 3/3) and B239 (3/3, 2/3).
None was taken, for the reasons recorded at the earlier closes:
- the first belongs to the layer line;
- the second appears answered by the third-reader study;
- the third is an older selected study.

This study took `CELL-SIGN-20261127-001#1`. Direction 1 here takes `CELL-SIGN-20261127-001#2`.

**Advisor:** unavailable (Fable 5.2 returned an unrecognized model and Fable 5.1 a usage limit; logged). An independent
reviewer checked the design before the freeze and found two blocking problems:
- kind (c), which refuted the drafted second clause of P1;
- a disagreement between the README and the code on the seven-knot bound.

It also found these:
- the gaps at eight knots;
- an agreement check that was not independent;
- a gate that could pass on an empty list;
- scoring by size;
- overlapping seeds;
- wording problems.

All were fixed before the freeze.

## What was found

- **Gates.**
  - No non-orientable even choice covered twice has five pairs or fewer.
  - The sign equals the same-order parity on all 622,841 labelled structures.
  - Every doubled meeting at every grown closure joins two start knots.
  - The census-start closures reproduce the referee's replay: 6,534 even, all orientable; 4,803 odd, none.
- **The smallest non-orientable even choices** (P1). Exhaustive through six knots and through six pairs on seven:
  - On six knots: (b), (c), a pinched seven-pair one, and a seven-pair one of Euler count −1.
  - On seven knots through six pairs: (a).

  All five put two values on one pair of knots. At seven pairs on seven knots, 18 of 144 classes are even and
  non-orientable, three of them with at most one value on each pair of knots, which the census types can hold (R1).
- **Built starts** (P2). B1 and B2 close in one round, by one birth each, holding (b) and (a). B3, census start 6830,
  stalls before any birth: the join rule leaves three pairs, each knot short by one distinction. B4 (one more
  distinction) closes in one round by a four-parent birth and holds (c). Of the 728 placements of loose distinctions on
  (b)'s holding, 44 close, 20 in round one and 24 in round two; 571 stall and 113 reach the ten-round limit (R1).
- **Sampled larger starts** (P3, P4), under the extension's weighting, which is rare:
  - one closure of 115 in the declared sample (eight pairs, covered four times at some pair);
  - two of 1,168 in a second sample (a seven-pair Klein bottle using a newborn's values, and an eight-pair projective
    plane on start knots).

  Whole choices add two sampled closures beyond the three birth positives: 5 of 1,283 at any coverage, 4 of 1,283
  covered twice (R1). No census-start closure has any, under birth or whole choices.

## Intuitions (exact links, not evidence)

- **When the odd cycles are exactly the twisted ones, the sign is the Euler count's parity.** By the cross-pair study's
  item 3, the closing sign pairs the class of odd cycles of the cross pairs with the orientation class. The
  literature's Wu formula says the orientation class paired with itself is the Euler characteristic mod 2. So when a
  cycle is odd exactly when it reverses orientation, the sign is odd on the projective plane (the three-reader game)
  and even on the Klein bottles (b) and (c). The cheapest test is to compute, on the enumeration's classes, which have
  odd cycles exactly the reversing ones, and compare their sign with their Euler count's parity.
- **The join rule is the program's hub doctrine at work.** "No knot meets them all" refuses a newborn whose parents
  are already held together by one common knot: a hub, in the doctrine's sense, not a contact. Kind (c) needs exactly
  such a birth (its missing knot's partners all meet knot 4). Growth refuses it (B3 stalls) until the hub is itself a
  parent (B4). The cheapest test is to remove each knot of each seven-pair class in turn and check whether the same
  rule bars its birth.
- **One distinction per parent makes growth's later meetings single, as in the literature's simple graphs.** The small
  non-orientable even choices need values sharing a pair of knots, as quadrangulations with parallel values do. The
  census types are simple, so their floor is seven pairs; growth can place parallel values only among start knots.
