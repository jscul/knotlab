# The parity-growth line: where a growth's dimension comes from

Line summary, 18 November 2026, by Claude, for the owner. It covers the six studies `FRESH-COUNT-20261118-001`,
`FIRST-KNOT-20261118-001`, `TOUCH-CENSUS-20261118-001`, `RING-GROWTH-20261118-001`, `PLUS-ONE-20261118-001` and
`RING-FORMULA-20261118-001`. Each study's decision note holds the evidence; this page adds no new result. Referee verdicts: five
in (all confirmed, no Block; three with fixes), and `PLUS-ONE-20261118-001`'s pending. "Dimension" here always counts junctions by round: the junctions up to round t
grow like t^d. Bond balls, the program's own measure, are proved only for the d-fold counting pattern.

## Why the line exists

G2 asks whether native logic builds three dimensions, and A97 says distance is the only information. The line took the parity law,
where knots always compose, and grew from it: every junction is a parity knot, the joining rule is the cubic study's complete round
(A104), and a count rule decides how many fresh distinctions each junction takes. The question was what fixes the dimension of what
grows: the law, the count, the first knot, or how the first knots meet.

## The answer in one paragraph

Not the law and not the count: the start. Whatever the counts, the growth always builds one kind of object, the down-closed sets of
the order in which its one-parent junctions (offshoots) descend, so a count rule only decides where offshoots begin (proved). One
count for every join is then forced to the start's number of open distinctions; from the smallest knot that number is three, and
the growth is three-dimensional (proved). The cheapest count closes a lone knot and stops, and on knots that touch it grows one
independent chain per birth, adding the chains whose partners share a neighbour (proved for the basic cases; 99.9% of small
arrangements that grow with a birth). Over every small arrangement of touching knots, nothing chosen, two dimensions are typical (about four in five that
grow), three and four rare (computed). Rings are the exception: a ring of an odd number of knots with spare distinctions winds back
over its own start each lap and grows exponentially, at a rate fixed by its length and its spares (proved). So
three is not the law's own number: it is the foundation's first knot under one count, or a rare arrangement.

## The six studies

1. **Can the count settle the dimension?** (`FRESH-COUNT`.) No. The growth is Birkhoff's construction; one count must equal the
   first knot's size or stall by round 4; the earlier "three" came from the old rule's cap of three per join; the fewest counts
   close a knot of a places into its 2^a pattern and stop; blind counts stall, random surplus fixes no number.
2. **Why the smallest first knot?** (`FIRST-KNOT`.) Nothing in the law or the rule prefers it: the rule reads open distinctions,
   never sizes. A three-place and a four-place first knot cannot grow together under one count. The same relation grows four- or
   two-dimensionally depending on how it is split into knots, so the dimension belongs to the presentation. The three of a lone
   knot is the foundation's first emergence (A105, a reading).
3. **What is typical?** (`TOUCH-CENSUS`.) All 26,441 connected arrangements of up to five knots of three to five places (A106):
   41.6% cannot start, 14.1% close, 7.9% grow one-, 36.2% two-, 0.15% three- and 0.03% four-dimensionally, 0.05% faster than any
   power. Two is typical under both weights and at six knots (the referee). Chains born together predict 98.7% of those that grow.
4. **Why do some rings grow faster than any power?** (`RING-GROWTH`.) The spare distinction of a five-place knot opens one more way
   to grow; on a ring that way comes back over its start every lap and is kept as a new way, not merged. The ring of four
   four-place knots and one five-place knot makes c(t) = c(t − 5) + c(t − 6) junctions in round t. This is the folded, overlapping
   structure in the owner's words, literally; a "logic based fractal" only loosely (no likeness at every scale).
5. **When do chains born apart combine?** (`PLUS-ONE`.) When the junctions they are each asked to join share a neighbour; then
   their dimensions add. Right in 11,649 of 11,658 census arrangements and 148 of 149 six-knot ones, never too high; ten combine
   through a second link not yet found.
6. **One formula for every ring?** (`RING-FORMULA`.) Yes for odd rings of five or more: n knots with j spares grow at the root of
   x^(n+j) = (1 + x)^j; a spare at every knot gives n times the Fibonacci numbers in every round. Rings of three, four and six
   join their knots in groups instead of round the ring and grow polynomially.

## Where the dimension comes from

| Start | Count | What grows | Dimension | Evidence |
| --- | --- | --- | --- | --- |
| one knot of a places | one count c | the a-fold counting pattern exactly when c = a; else a stall by round 4 | a | proved |
| the same, groups of at most three | one count | survives only at a = 3 | 3 | proved |
| one knot of a places | fewest | its 2^a pattern, then stops | closes | proved |
| two knots touching at one distinction | fewest | two two-way patterns, forever, any sizes | 2 | proved |
| m knots of m + 1 places, each touching every other | fewest | m chains born together | m | proved; checked m = 3 to 6 |
| every arrangement of up to five knots | fewest | stall, close, or chains | 2 typical; 3 and 4 rare | computed (census) |
| arrangements with births | fewest | linked chains add | the largest linked sum | computed: 11,649 of 11,658 (fitting), 148 of 149 (test) |
| odd ring of n ≥ 5 knots, j spares | fewest | a winding whose laps add ways | none: rate the root of x^(n+j) = (1 + x)^j | proved; matched on 17 rings here, and on the 13 census rings and five more by the referee |
| odd ring, a spare at every knot | fewest | n F(t + 2) junctions in round t | none: the golden ratio | proved |
| odd ring, q spares at every knot | fewest | n Σ_h C(q(h + 1), t − h) junctions in round t | none: the root of x^(q+1) = (1 + x)^q | proved (the referee's addition); computed for q = 2 |
| rings of three, four, six; even rings of eight or more | fewest | groups, not windings; two windings of half the length | 3 / polynomial / polynomial; per winding | computed (even rings at 8, 10 and 12) |

## Proved against computed

- **Proved:** the Birkhoff structure for every count rule; the one-count and capped-count theorems; the fewest counts on one knot,
  on any hand-over and on touching pairs; the pieces lemma and the presentation result; m mutually touching knots; stalls only in
  round 1 and where chains start (census lemmas); that every odd ring's growth is the model (its group step by the referee's exact
  argument), the count and the recurrence from round n + j for any odd n ≥ 5 and j spares, and the Fibonacci ring in every round.
  Checked by graph isomorphism to round 20 for one ring, by counts on 17, and by the referee's histograms on ten.
- **Computed only:** the census shares and the typical two; the link rule; even rings; rings of four and six; bond balls anywhere
  but the a-fold pattern.
- **Readings, not theorems:** the three as the foundation's (A105); "a rule can only copy its number from its start".

## Referee verdicts and corrections

| Study | Verdict | What changed |
| --- | --- | --- |
| FRESH-COUNT | Confirmed with fixes, no Block: one Narrowing, two Not a block | the "cannot" claim scoped to the complete round and the three rules proved; distance-only proved for the uniform count only |
| FIRST-KNOT | Confirmed with fixes, no Block: one Narrowing, one Not a block | dimension is junctions by round; bond balls proved only for the a-fold pattern |
| TOUCH-CENSUS | Confirmed with fixes, no Block: three Narrowings | the 200 arrangements unread at the close held the rare growth (40 three-dimensional, not 36; 13 fast rings, not 7); the fast rings' rates 1.13 to 1.62; 1,746 starts force a distinction, not 1,713 |
| RING-GROWTH | Confirmed, no Block: one Narrowing, one Not a block | the formula is for odd rings; the ring of eight follows it at half its length (rate 1.1673), not at n = 8; the group step's "product" was not a product, and the referee's exact argument replaces it, so the growth is the model is proved |
| RING-FORMULA | Confirmed, no Block: two Not a block | the transient is exactly n + j, not "about 3n + j", with two slips in its proof fixed; the proof's pointer to its check corrected |
| PLUS-ONE | pending | — |

Each is in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`. The lessons: state a "cannot" for the rules actually proved; name the
measure behind "dimension" every time; never treat the tail of a sorted run as a sample; state a formula's range next to every
case it is checked on.

## Known mathematics, and what the line adds

Known, each cited once in its study: Birkhoff's representation of distributive lattices by ideals (Stanley, *Enumerative
Combinatorics* I, 3.4.3); prime event structures (Nielsen, Plotkin and Winskel); the cube condition of median graphs; Dilworth's
theorem; Whitney's 2-isomorphism and the rank of a graph's incidence matrix over two values; Burnside counting of small multigraphs;
Pascal's rule, Vandermonde's identity and the Fibonacci numbers as diagonal sums of Pascal's triangle. What the line adds, with no
literature search beyond these, so parts may be folklore: the program's parity growth law is Birkhoff's construction, so a count
rule chooses only an order; one count is forced to the start's open distinctions; the joining rule reads open distinctions, never
sizes, and the dimension belongs to the presentation; the first census of the cheapest growth over unchosen arrangements, with two
typical; the link rule for chains born apart; and the exact exponential rate of every odd ring.

## What it means for the goals

- **G2, dimension three:** an obstruction learned. Three is not selected by the law, the count or the rule; it comes from the
  foundation's three-place first knot under one count, or from a rare arrangement. The cheapest growth's typical number is two.
- **G1 and A97:** only the uniform count is proved to read nothing but bond distances; the others read demands from the pattern of
  junctions. Whether a rule reading distances alone behaves the same is the basket's first item.
- **G17, typical and rare meeting patterns:** capability gained. Typical and rare growth are both predicted: two from the chain
  rule, exponential from a ring's length and spares.
- **What is solid to build on:** any count rule is an order of offshoots (Birkhoff), so every later growth question reduces to
  which order a rule builds. Everything here rests on one assumption, the complete round (A104).

## The open basket

| Scope | Verdict | Why |
| --- | --- | --- |
| This line: where a parity growth's dimension comes from | Settled under the complete round | the start sets it; two typical, three rare, rings exponential |
| Long-term goal: G2 | Obstruction learned | three is the foundation's first knot, not the law's |

**Next step:** Research directions; none selected (the line is paused for this summary).

| # | Open item | Payoff | Concreteness | First step → stop when |
| --- | --- | --- | --- | --- |
| 1 | Serial growth read from distances: one junction at a time, joins preferred (`FRESH-COUNT-20261118-001#1`), testing A104 | 2/3 | 2/3 | its descent orders against the complete round's on seeds of three to five → a proof they agree, or a seed where they differ |
| 2 | A dimension that belongs to the relation, not its presentation (B202) | 3/3 | 1/3 | one canonical presentation, tested on the four-place relation's three → one that grows alike, or a proof none can |
| 3 | Bond balls on descent orders with tied chains (`FRESH-COUNT-20261118-001#3`) | 1/3 | 3/3 | "exponent = chains eventually untied" → a proof or a refutation |
| 4 | Bond balls on the rings' winding (`RING-GROWTH-20261118-001#3`) | 1/3 | 2/3 | bond distances on the first rounds → a rate or an obstruction |
| 5 | The second link of the chain rule (`PLUS-ONE-20261118-001#1`) | 1/3 | 3/3 | the ten misses against the 889 overshoots of the naive repair → a separating link, or a proof none local exists |
| 6 | Even rings: prove the split into two windings (`RING-FORMULA-20261118-001#2`) | 1/3 | 3/3 | the model for even n ≥ 8 → a proof or a ring that breaks it |
| 7 | A short note: the parity growth law is Birkhoff's construction (`FRESH-COUNT-20261118-001#4`) | 1/3 | 3/3 | the two theorems written self-contained → checked |

Two ring studies run in other threads and are not in this basket: composing rings with other pieces, and regrowing a ring from its
distance table.

**Corrections:** none new; those folded in are listed above. **Goals:** no change. **Assumptions:** A104, A105 and A106 carry
the line; no status changed. **Advisor:** not consulted for this summary; each study's use is in its note.
