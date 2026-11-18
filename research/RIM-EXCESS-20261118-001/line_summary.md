# The bond-distance line: where the program's distance is a true distance

Line summary, 18 November 2026, by Claude, for the owner. It covers the five studies `BOND-METRIC-20261118-001`,
`NAE-METRIC-20261118-001`, `DOUBLE-MEET-20261118-001`, `WEAVE-HEIGHTS-20261118-001` and `RIM-EXCESS-20261118-001`, with
`FREE-READ-20261118-001` as their starting point. Each study's decision note holds the evidence; this page adds no new result. Referee
verdicts: five in (FREE-READ and the first four studies), `RIM-EXCESS-20261118-001`'s pending.

## Why the line exists

Your premise is that distance is the only form of information (A97). The program's own distance is **bond distance**: take the least
set of distinctions holding the two on which the allowed states, everything else forgotten, form a knot, and count its size minus one.
It is read from which joint values occur and nothing else. `FREE-READ-20261118-001` proved that on every tree of knots it is exactly the
steps apart plus one. The line then asked the question any distance must answer: does it add up? Is the way from x to z never longer
than the way from x to y and on to z (the triangle inequality, counting a pair that no knot holds as infinitely far)? Where it fails,
bond distance reads something, but not yet a distance.

## The answer in one paragraph

Bond distance adds up on every base for exactly one three-place law, parity, the law whose knots always compose. Under not-all-equal,
your case, it adds up wherever the knots meet like a tree of single knots and rings (proved), on the endless weave (proved earlier) and
the closed weaves checked, and on patches of the weave without holes everywhere except at their rim. Elsewhere it can fail: two knots
meeting twice with nothing else around break it, and so can single meetings in a dense pattern (from eight distinctions). On the weave's patches the only trouble is a pair of
lone distinctions (each in a single knot) of opposite classes facing each other across the patch: no knot holds them, or only one that
is too large. There bond distance is never less than the steps apart plus one (proved) and equals it everywhere except on those facing
rim pairs (computed, to twelve knots). So distance read from freedom is a true ruler in the weave away from its rim; at the rim it
overcounts, never undercounts, and how far it can overcount is open.

## The five studies

1. **Is bond distance a true distance at all?** (`BOND-METRIC-20261118-001`.) Not on every base. Among all 34 three-place laws that pass
   the knot test, it is one on every base built from copies of one law exactly when the law is parity (proved). The reason is
   composition: two parity knots that meet always contain a knot holding their far ends (two circuits of a matroid sharing an element).
   Two not-all-equal knots sharing two distinctions do not: no knot of the allowed states holds their two outer distinctions, because the
   shared pair is a hub, not one touch.
2. **Where, under not-all-equal?** (`NAE-METRIC-20261118-001`.) The question splits along the knots' blocks. Across a joint (a
   distinction whose removal splits the knots into two groups meeting nowhere else) bond distance minus one adds exactly, so a base is a
   true distance exactly when each block is (proved, for every base of not-all-equal and betweenness knots of any arity, and for parity
   bases). Single knots and rings of knots are good blocks, with bond distance the steps apart plus one, so every tree of knots and rings
   is a true distance (proved). Tonight's grown lines and grids pass, but trivially: at every step of the runs every pair but one lies in
   a knot of three, so bond distance is at most 2 and gives them no spacing.
3. **Inside the weave?** (`DOUBLE-MEET-20261118-001`.) The weave is made of knots meeting twice, yet those meetings are harmless, because
   other knots hold the outer distinctions. On every patch without holes to eleven knots (and 480 random ones to sixteen distinctions), every pair that no
   knot holds is a lone pair of opposite classes facing each other; the smallest case is the two knots meeting twice. From twelve knots
   such a pair can also break the triangle inequality while held, by a knot that is too large (the referee).
4. **Why never less than the steps apart?** (`WEAVE-HEIGHTS-20261118-001`.) Every state of a weave patch without holes is a height: a
   whole number at each distinction that steps up by one or down by two along each pair. A set is constrained exactly when a few of its
   distinctions close a route too short for the heights to fit, and going between two distinctions and back always costs three times
   their steps apart. So every knot holding two distinctions has at least the steps apart plus two members (proved).
5. **How much more, at the rim?** (`RIM-EXCESS-20261118-001`, referee pending.) A knot of the states, visited in the right order, is a
   closed route exactly as short as the heights allow. So bond distance is the steps apart plus one plus the **excess**: how much longer
   the least knot's route is than the plain round trip, in units of three (proved). The excess lives only on facing rim pairs and is at
   most 2 up to twelve knots (computed). Whether it grows without limit is open.

## Where bond distance is a true distance

| Base | True distance? | Relation to steps apart | Evidence |
| --- | --- | --- | --- |
| Trees of knots: parity, not-all-equal, betweenness, any mixture | yes | exactly steps + 1 | proved (FREE-READ) |
| Any parity base | yes, and bond distance − 1 too | — | proved (BOND-METRIC T1); 439,652 bases checked |
| Copies of any other three-place law | not on every base | — | proved (a failing base for each of the eight other kinds) |
| Not-all-equal or betweenness, any base | exactly when every block is | adds across joints | proved (NAE-METRIC C1, C2) |
| Not-all-equal blocks that are knots or rings | yes | exactly steps + 1 | proved (NAE-METRIC C3) |
| Plain not-all-equal knots meeting at most once, each distinction in at most two, no K4 in their pattern of meetings | yes in all 296 checked | — | computed; a conjecture, false with one betweenness knot |
| Small not-all-equal blocks with two knots meeting twice | often not | — | computed (420,202 failing of 1,589,656 to seven distinctions and six knots, every one with a double meeting) |
| Weave patches without holes, pairs other than facing rim pairs | yes | exactly steps + 1 | at least steps + 1 proved; equality computed to twelve knots |
| Weave patches without holes, facing rim pairs | sometimes not | unbonded, or steps + 2 (from ten knots), steps + 3 (from twelve) | at least steps + 1 proved; the rest computed |
| The endless weave | yes | exactly steps + 1 | proved (`RULER-20261111-001`) |
| Woven tori 3 × 3 to 4 × 5 | yes | — | computed (BOND-METRIC) |
| Tonight's grown lines and grids | yes, trivially | at most 2 (one pair at 3 at one step) | proved for split lines and full grids (NAE-METRIC C4); the runs computed |

## Proved against computed

- **Proved:** the triangle inequality on every parity base, for bond distance and bond distance minus one; the classification of all 34
  three-place laws; additivity across joints and the block reduction for not-all-equal, betweenness and parity bases; rings, and trees
  of knots and rings; flatness of split lines and grids; the weave's height criterion for constrained sets; the round-trip identity; the
  lower bound b ≥ steps + 1 on weave patches without holes; a least knot as a closed route of the heights' length, and the excess formula.
- **Computed only:** that every unbonded or over-long pair of a weave patch is a facing rim pair (to twelve knots); that the excess is at
  most 2 there (and at most 1 on random patches of 20 to 40 knots); that small not-all-equal failures need a double meeting (to seven distinctions); the
  series-parallel conjecture for plain not-all-equal; that the woven tori checked are true distances.
- **Resting on citations:** one step of the lower bound (no knot of a patch without holes is level as seen from any distinction) uses
  standard theorems on bridged graphs; the referee confirmed the statements from secondary sources, but not the theorem numbers. The
  step's conclusion was checked on every patch to twelve knots and 6,000 random ones of thirteen and fourteen.

## Every referee verdict and correction

| Study | Verdict | What changed |
| --- | --- | --- |
| FREE-READ | Narrowing, and Not a block (two small fixes) | The triangle inequality was claimed for bond distance off trees, from a check that skipped pairs held by no knot; counting them as infinitely far, it fails on 106 of the 400 bases. It is claimed now on trees and parity bases, and where it fails became BOND-METRIC's question. The small fixes: every three distinctions form a knot on the split line only, not the grid; the switching step is argued knot by knot. |
| BOND-METRIC | Narrowing | "Not exactly two ones" first fails at seven distinctions with six knots, not eight; "a true distance exactly where knots compose" holds law by law, not base by base (not-all-equal trees are true distances though their knots do not compose). |
| NAE-METRIC | Narrowing, and Not a block | The series-parallel conjecture holds for plain not-all-equal only: one betweenness knot breaks it on eleven distinctions. The joint lemma now excludes blocks mixing parity with not-all-equal or betweenness. |
| DOUBLE-MEET | **Block** on one reading, and Not a block | "A weave patch fails exactly when some pair is unbonded" is false from twelve knots, where a facing pair can fail while bonded. The rim is still the only cause; nothing had been built on the blocked reading. The lower bound was marked sketched until WEAVE-HEIGHTS proved it. |
| WEAVE-HEIGHTS | Confirmed, no Block, no entry | Lemma 5's citation caveat; one sentence reworded; two stale phrases from DOUBLE-MEET's fold-in fixed. |
| RIM-EXCESS | pending | — |

Each entry is in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`. The lessons the line taught: count a pair with no reading as
infinitely far; search one size past an advisor's smallest example; test every twisted variant of a pattern; when an excess over a ruler
grows with size, run the census past the first size where it appears.

## Known mathematics, and what the program's view adds

Known, each cited once in its study: "equal or on a common circuit" is an equivalence in every matroid (Whitney; Oxley); the parallel
connection of matroids (Brylawski); lossless joins of acyclic schemes (Beeri, Fagin, Maier and Yannakakis); block-cut trees and
series-parallel graphs; bonds as the minimal non-shattered sets of the allowed states; Horn closure systems; the triangular
antiferromagnet's height function (Blöte and Hilhorst; Nienhuis, Hilhorst and Blöte); heights as difference constraints (Thurston);
bridged graphs, their convex balls and triangle condition (Soltan and Chepoi; Farber and Jamison; Chepoi; Januszkiewicz and Świątkowski;
Chalopin, Chepoi, Hirai and Osajda). In the program: `KNOT-CIRCUITS-20261020-001` (a law composes like cycles exactly when it is
affine, which for three-place laws on bits is parity) and `BOND-CHAIN-20261108-001` (chains add nothing where knots compose; A39).

What this line adds, with no literature search run and none of it known to the advisor, though parts may be folklore: the triangle
inequality as the test of whether knots compose, settled for all three-place laws; additivity across joints for bases closed under
switching every value, and the block reduction; the exact criterion for constrained sets on weave patches and the lower bound; a least
knot as a closed route and the excess as its extra length; the census placing every failure on the weave at lone facing rim pairs.

## What it means for the premise

Read from freedom alone, distance is a true ruler where knots compose: everywhere under parity, and under not-all-equal on tree-like patterns and in the weave away from its rim. That is where the
program's spacing results (rulers, circles, ball growth) were measured, so none of them changes (A39). At the rim of a not-all-equal
patch the reading overcounts: two lone distinctions facing each other can look farther apart than the steps between them, or unrelated.
The overcount is exactly the extra length of a route the heights force around the rim. So the premise holds away from the rim and
meets a boundary effect at the rim, which is where the line stands.

## The open basket

| Scope | Verdict | Why |
| --- | --- | --- |
| This line: is bond distance a true distance | Settled away from the rim, open at it | Proved where knots compose, on trees of knots and rings, and as a lower bound on the weave; the rim excess's growth is open |
| One distance for both laws (B200) | Promising | Bond distance reads both laws on trees and on the weave away from the rim; grown split bases stay flat |
| Long-term goal: G1 | Capability gained | A proved ruler on trees of knots and rings, a proved lower bound on the weave, and an exact meaning for the rim excess |

**Next step:** Research directions; none selected (the line is paused for this summary).

| # | Direction | Payoff | Concreteness | First step → stop when |
| --- | --- | --- | --- | --- |
| 1 | Does the rim excess grow without limit? Check the advisor's split of every excess knot (a closed route crossing itself once, the advisor's figure-eight) to twelve knots and build a family from it | 2/3 | 2/3 | the split on all 198 excess pairs → a family with excess 3, or a reason the loops cannot grow |
| 2 | Prove the plain not-all-equal series-parallel conjecture through two-distinction separations | 2/3 | 2/3 | a two-joint formula on rings with one knot replaced by a small block → a proof or a counterexample |
| 3 | Is "a true distance on every base" the same as "composes like cycles" for laws of four places or three values? | 2/3 | 2/3 | four-place laws whose knots fail to compose, bases of up to four knots → a law with no failure, or a proof |
| 4 | Prove that every pair other than a facing rim pair has b = steps + 1 on weave patches | 2/3 | 1/3 | a closed route of steps + 2 members for a pair with a non-lone end → a proof or a counterexample |
| 5 | Closed weaves beyond the cutoff `RULER-FLAT-20261111-001` found | 2/3 | 1/3 | tori 5 × 5 to 6 × 6 with the route search → a failing torus or a proof route |
| 6 | Exhaustive excess at thirteen knots with the route search | 1/3 | 3/3 | the largest excess at thirteen knots → 3, or 2 |
| 7 | One-way ties as orders (the twisted "not exactly two ones" failures) | 1/3 | 3/3 | the ties of two in every failing base and their directions → the list |
| 8 | Patches with holes: heights that wind, and whether a hole acts like a rim | 1/3 | 2/3 | annuli of the weave → the first failure or a pattern |
| 9 | A citation-free proof that no knot of a weave patch is level | 1/3 | 2/3 | an argument by the rim's turning → a proof or a gap |

**Corrections:** listed above; none new in this summary. **Goals:** no change. **Assumptions:** A39 and A97 carry the line's history;
no status changed. **Advisor:** not consulted for this summary; each study's use is in its note.
