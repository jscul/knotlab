# What the arrangement of the count's rows holds: pre-registration

Epic `ROW-ARRANGE-20261118-001` (`COUNT-BALLS-20261118-001#1`; G16 and G1; tests A97), 18 November 2026. Frozen before the run.
Code by the thread (Claude), run by the thread through the shared runner; no Codex. The canonical K1–K3 test is unchanged.

## The question

`COUNT-BALLS-20261118-001` found that every start's sorted row of disagreement counts, read without names, merges grown split
bases with two and three orders from seven distinctions, while the full table of counts keeps the orders (it determines these
bases). So the orders sit in how the rows are arranged: which start's row lies at which count from which. This study climbs from
the sorted rows to the full table and asks where the number of orders k (and the lattice dimension λ) is first recovered, and
whether a reading that looks only near each start (a local one) is enough.

## In standard terms

A grown base is the solution set of betweenness constraints; its count table D is twice the split metric. Readings, each a
multiset over starts x, invariant under renaming:
- **a**: the sorted row of D at x (the distance-degree sequence);
- **N1**: x's row with the rows of the distinctions nearest x (one step of refinement along the nearest pairs);
- **W2**: x's row with every other row tagged by its count from x (two rounds of colour refinement, 1-WL, on the complete
  count-weighted graph);
- **WL**: 1-WL run 2n rounds (the stable colouring's histogram);
- **B_r**: the table restricted to the distinctions within count r of x, with x marked, up to renaming (a purely local view; no
  rows), r = 2, 4, …, 14.
Targets: k, the chromatic number of the splits' crossing graph; λ, Eppstein's lattice dimension.

## Prior work in the program

`python3 -B scripts/track.py objects "what the arrangement of the disagreement count's rows holds, readings that recover the number of orders" --until 2026-11-18 --exclude ROW-ARRANGE-20261118-001`
`python3 -B scripts/track.py objects "colour refinement Weisfeiler-Leman distance-degree sequence local views Hanf locality split metric partial cube" --until 2026-11-18 --exclude ROW-ARRANGE-20261118-001`
`python3 -B scripts/track.py objects "grown split bases one-split population cheapest growth orders lattice dimension census" --until 2026-11-18 --exclude ROW-ARRANGE-20261118-001`

- `COUNT-BALLS-20261118-001` — same object and population: reading a fails from n = 7; the state side is blind to translation.
  Taken: the populations (its `census.py`, unchanged) and the first failing pair.
- `DISTANCE-ORDER-20261117-001` — same object: the table with N determines every base of complement-closed three-place
  constraints, so the full table determines k and λ here.
- `WEAVE-MIX-20261117-001` — unrelated (knot arrangements on the weave; matched on words).
- `MEET-DIST-20261118-001` — a relative: how much of a grown base's nesting its unnamed table carries.
- `OVERLAP-READ-20261111-001` — a relative in word only (locality of hollow triples on overlapping bases).
- `STATE-RULES-20261117-001` — the growth engine (`rules.py`, unchanged) and the readings k and λ.
- `CUBE-DOUBLING-20261118-001` — the cheapest population.
- `MEET-HIST-20261118-001` — a relative: names that carry what unnamed states miss.
- `REFINE-READ-20261107-001` (found by its ticket) — colour refinement on another object (the native creation map): 1-WL merges
  only where symmetry forces it, pair refinement fixes the atoms. A relative; here the object is the count table.

## Prior work outside the program

Colour refinement (1-WL) and its failure on regular graphs such as one cycle of length 2m against two of length m (Weisfeiler and
Leman 1968; Cai, Fürer and Immerman 1992); Hanf's and Gaifman's locality theorems (bounded-radius views cannot express
connectivity or two-colourability); the Djoković–Winkler relation and median graphs, in which two splits cross exactly when a
square carries both (Mulder; Chepoi); lattice dimension by a matching (Eppstein 2005); distance-degree sequences of graphs.

## Settled by construction (stated, not tested)

- The readings are ordered: a is a function of N1 and of W2; N1 and W2 are functions of WL; every B_r is a function of the full
  table; B_r for r at least the largest count is the full table, which determines k and λ.
- **Every partial cube is a base** (the advisor's lemma, checked by hand): in a connected bipartite graph, a set A whose
  members and non-members are both closed under lying on a shortest path, crossed by a pair ab, equals W_ab = {x : d(x, a) <
  d(x, b)}; so the solution set of the betweenness constraints along shortest paths is exactly the halfspaces with the two
  all-equal states, and the count is twice the graph distance.
- **No reading that sees each start only within a fixed count determines k** (Hanf–Gaifman locality, here by the advisor's
  family): F(a, b), two rings of 2a and 2b points sharing one point, is a partial cube with k = λ = max(a, b) (each ring's splits
  cross each other and nest with the other ring's). F(a, b) and F(c, d) with a + b = c + d, all long against the radius, have the
  same views within that count from every start, with the same n and N. Smallest: F(2, 4) against F(3, 3), n = 11, k = 4 against 3,
  equal B_2.
- **Colour refinement does not determine k either**: the simplex graph κ(G) of a graph G without triangles is a median graph
  (a base) whose splits are G's vertices, crossing exactly when adjacent, so k = χ(G). κ(C₁₀) and κ(C₅ ⊔ C₅), n = 21, have the same
  three-part equitable structure (one point for the empty set, ten for the vertices, ten for the pairs), so a, N1, W2 and WL agree,
  while k = 2 against 3 (λ = 5 for both). B_4 tells them apart. So local views and colour refinement are incomparable.
- **Computing k from the full table is hard** (classical): k is the least number of trees whose product holds a median graph
  (Bandelt and van de Vel 1989), NP-complete already for three; through κ, three-colouring graphs without triangles reduces to it.
  λ is a maximum matching (Eppstein 2005), polynomial.
- **W2 determines the table when every start's row is distinct** (the advisor): the rows name the starts, and W2 gives each start's
  count to each named start.
- Rings of arcs (found before the advisor's families, kept as a remark): on a ring of L points take as splits all arcs of w
  consecutive points; the crossing graph is the (w − 1)-th power of a cycle of length L, the count is 4·min(d, w) at ring distance
  d, and one ring of 2M against two of M (M ≡ w/2 mod w, w even; or w = 2, M odd) gives equal views within count below 4w, equal
  1-WL colourings, and k = w against w + 1 (checked at L = 10 against 5 + 5, w = 2, and 20 against 10 + 10, w = 4). These are
  split systems but not solution sets of their betweenness constraints, so they are not bases; the families above are.

## Exploration disclosed

Before the freeze I ran every reading of the ladder on the 101 one-split classes at n = 6: a, N1, W2, WL and B6 separate all 101;
B2 merges them into 22 groups (16 mixing k) and B4 into 92 (3 mixing k). At n = 7 I timed the run (24 s) without printing any
result, and timed the family sampling on two parents (239 children) without reading it. The checks of the two families
(F(2,4)/F(3,3), κ(C₁₀)/κ(C₅ ⊔ C₅)) and the rings were run before the freeze; they are proofs' checks, not the census.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): the readings reproduce COUNT-BALLS's reading a counts at n = 7 (1,651 groups, 3 mixing k); every reading is invariant under renaming (random relabellings of 200 classes give the same names); the view canonical form agrees with a brute-force canonical form on 300 random small views; the two families check (k, equal readings, betweenness solution set); the ladder's order holds on every class (a function of N1 and of W2, and those of WL) | any fails |
| P1 | N1 (each start's row with its nearest starts' rows) determines k and λ on the one-split population at n = 7 | a group mixing k or λ |
| P2 | W2 separates every one-split class at n = 7 | a merged group |
| P3 | WL separates every class at n = 7, every cheapest class to n = 12, and determines k and λ at n = 8 | a merged group at 7 or cheapest; a group mixing k or λ at 8 |
| P4 | N1 does not determine k at n = 8 | no group mixing k |
| P5 | The least count r at which B_r (local views, no rows) determines k is 6 at n = 7 and 8 at n = 8 | other values |
| P6 | BW4 (refinement started from B_4 views) separates every one-split class at n = 7 and at n = 8 | a merged group |
| P7 | Calibration: the families at n = 8 (300 parents' children) contain at least one of reading a's k-mixing groups | none |
| P8 | One size past: on the families at n = 9, WL determines k and λ, and reading a mixes k in at least one group | WL mixes, or a does not |

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 4 shards at n = 7, 48 at n = 8, one per n for the cheapest population (4 to 12), and 12 family
shards at each of n = 8 and 9 (25 random parents each, every one-split child; setup enumerates the populations once). A plain
random sample at n = 9 was dropped on the advisor's point that among millions of classes almost no merge would be sampled. Then `merge.py` scores the predictions.
Expected well under an hour with 8 workers; registered as ROW-ARRANGE-B1. One run; no change to cases, readings, predictions or
decision rules after seeing results; later looks labelled post hoc. Stop at the read-out, the proofs, the referee hand-off and the
report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` was asked before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2). It gave the partial-cube lemma, both families, the
hardness of k, the remark on distinct rows, the family design for n = 9, the BW4 reading and its predictions, which P1 to P6
follow (my own guesses agreed on P2, P3 and P5). Its answer also described a shell session, files and processes that do not exist
(it had no tools; checked, nothing of the kind on the machine); those parts were disregarded.
