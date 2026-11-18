# Can three new distinctions inherit a trace of the erased knots?

Ticket `FRESH-THREE-20261117-001`, 17 November 2026, serves G1 and G16. The owner selected the three-distinction projection after the eight-cut study. This exploratory plan fixes the observable and its interpretation before collecting its endpoint.

## Question

The previous study found that the entire state table of ten distinguishes the two starts after erasure at eight. It introduced a distinction at each subsequent step. The last two distinctions alone allow every binary assignment under either start. Here growth gets one more step. The evaluator then hides every distinction present at erasure. Does the three-distinction relation that remains have different probabilities for the two starts?

## In standard terms

Each source gives a known distribution over the same space of signed isomorphism classes of binary relations. Their union of supports at eight has 13 members. For each input class compute one transition law on three new binary coordinates by composing three conservative extensions that minimize the number of rows. Grow without consulting any distinguished subset. Project the resulting relation onto the three new coordinates, forget all column names and signs, and compare the two mixtures with equal prior odds. The [contract](../../experiments/FRESH-THREE-20261117-001/FRESH-THREE-20261117-001-E001_projection/contract.json) pins the source and complete move rule.

Every projected row occurs with its bitwise complement. Each new column takes both values and cannot equal another column or its complement. Thus each pair allows four assignments. If a ternary projection had at most two complementary pairs of rows, choose one row per pair. Across at most two chosen rows there are at most two possible column patterns up to complementation. Three different columns cannot fit. The projection must therefore contain six or eight rows. In the six-row case the missing complementary pair can be renamed to 000 and 111. Counting rows identifies the entire anonymous allowed-state relation in this particular test.

The earlier cut and whole-table results are known. The three-new probabilities and the direction of any difference are open. Compare the exact probability of a six-row projection for each start. Equality gives chance recognition. Otherwise report the optimal guessing probability and its gain over one half. The score concerns the ensemble from each start and a single observation drawn with equal prior odds. The full cut-table score of 26/35 is a ceiling. Keep exact weights for each incoming class and for every step, including when the same new triple is available by different routes. The old distinctions remain available to the grower through the third addition.

## Prior work in the program

`python3 -B scripts/track.py objects "matched starts" --until 2026-11-17 --exclude FRESH-THREE-20261117-001`

`python3 -B scripts/track.py objects "ternary projection of allowed states" --until 2026-11-17 --exclude FRESH-THREE-20261117-001`

`python3 -B scripts/track.py objects "betweenness growth, fan and non-fan" --until 2026-11-17 --exclude FRESH-THREE-20261117-001`

- `ERASE-SEPARATELY-20261117-001` supplies the signed eight-cut input laws, the exact anonymous transition rule, and the one- and two-distinction controls.
- `STATE-RULES-20261117-001` gives the original matched starts. `KNOT-CAP-20261117-001` registered a shared-value erasure and reads the entire later table. This test reads only the three new distinctions under the signed rule.
- `KNOT-ORDER-20261117-001` and `GRID-GROW-20261117-001` count attachments to supplied orders. `SIGNED-KNOT-OVERLAP-20261114-001` studies projections of fixed clause templates. `HARMONY-ARITH-20261112-001` concerns periods of state patterns. `CLAMP-LEARN-20261112-001` changes the start of a learning walk and `ACROSS-FOLD-20261112-001` measures a bond across a fold.

## Comparison and checks

There are 32 distinct columns up to value exchange on the six complementary row pairs. Eight are occupied at the cut. As a comparison, draw three uniformly from the 24 unused columns with no further attachment law. This keeps the no-copy rule and the same inherited rows, and isolates the source information available simply because different inputs leave different columns unused. Count how often the resulting triple has six allowed states under each cut law and compare the effect size with the specified growth rule.

Track which coordinates to project solely in the evaluator. The grower sees the current relation and the same transition at every class. Give each achievable literal extension the same weight at that step. A fixed fresh-column flip pairs two equally weighted extensions. Every reached parent must have a minimizing move, and every cut-class conditional law and each source mixture must sum to one. Verify the classifications for all ternary relations, a recoded control and at least one direct reconstruction using the published growth rule. The advisor identified conditional independence within a cut class as the principal check. Its warning that complement closure alone would allow smaller projections is resolved here by the no-copy condition. Stop at eleven.
