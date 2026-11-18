# Can the ring be regrown from its bond distances past six? Pre-registration

Epic `RING-READ-20261118-001` (the coordinator's go-ahead on the scouting probe's idea 2, "a system that carries no description of
itself"; goals G1 and G17, assumption A97), 2026-11-18. Code by the thread. Frozen before `check.py` is run. The canonical K1–K3
test is unchanged.

## The question

The ring of four four-place knots and one five-place knot grows under the cheapest counts (`RING-GROWTH-20261118-001`). Keep only
its bond-distance table: anonymous distinctions, no rounds, no parents, no names. Can the junctions, and with them the next round,
be read back? `BOND-NEXT-JOIN-20261117-001` proved a reader for the pure parity growth when every junction has at most six
distinctions. The ring passes that bound at round 10, when its first seven-distinction junction appears, and the reader then
returns junctions that do not exist (scouting, below). At rounds 10 to 20 (largest junctions of 7, 8 and 9 distinctions) this
study stops at a reader that works there, or at two different incidences or histories with one table. It tests A97 ("distance is
the only form of information") on a growth law whose junctions keep getting larger.

Scope against Codex's newest reader, `VARIABLE-OUTPUT-READER-20261118-001G` (decision note, not yet refereed): that reader is
all-size for the law with two or three fresh distinctions per join when every junction has at most four distinctions, at
horizons 3, 4 and 5. The ring's junctions have 4 to 9 distinctions and up to six or seven parents under a different joining law
(complete rounds, cheapest counts), so the ring lies outside it from round 0 (the five-place seed knot) and far outside it from
round 5. This study does not repeat its proof; it is computational, on one growth, at finite rounds.

## In standard terms

The junction graph G has one vertex per junction and one more, o, that ends every loose distinction; distinctions are its edges.
The parity consequences of the junctions are the cut space of G, its circuits are the bonds (minimal edge cuts, both sides
connected), and the bond distance of two edges is the size of the smallest bond containing both, minus one. The question: does
the matrix of these sizes determine G, as a graph with o marked, among the graphs the growth law can make? Classical facts: the cut
space determines G up to Whitney's 2-isomorphism (Whitney 1933), and up to isomorphism when G is 3-connected; it never marks a
vertex, so it cannot say which vertex is o.

## Prior work in the program

`python3 -B scripts/track.py objects "bond distance table reader junctions recovered" --until 2026-11-18 --exclude RING-READ-20261118-001`

- `FRESH-COUNT-20261118-001`: a relative. Its threshold reader is exact on one count, reads the last junction one round early on
  the 2^a pattern (the loose distinctions already form a knot: the outside-vertex ambiguity below), and misreads 47 of 247
  mixed-count stages of at most 21 junctions. The ring is mixed-count growth at far larger stages; this study asks whether a
  different reader recovers it.
- `BRAID-COUNTS-20261114-001`: unrelated (answer classes of crossing tests).
- `ROW-ARRANGE-20261118-001`: a relative on another base (grown split bases): which readings of a disagreement-count table recover
  the number of orders; it proves that number not computable from the table in polynomial time unless P = NP. Nothing here reads
  orders.
- Also `DISTANCE-INFO-20261117-001` (pair bond distance does not determine not-all-equal relations; parity is this study's law).

`python3 -B scripts/track.py objects "graph reconstruction from minimum cut containing two edges cographic matroid" --until 2026-11-18 --exclude RING-READ-20261118-001`

- `NAE-METRIC-20261118-001` and `CUMULANT-DIST-20261118-001`: relatives (bond distance as a metric, steps apart plus one on trees
  and rings of knots; delta = bond distance - 1 on parity bases). They measure the distance, not reading the base back from it.
- `TERNARY-REPORT-JOINS-20261115-001`: unrelated (affine covers of pair products).
- `KNOT-SPACE-20261020-001` (other epics): a relative and the program's own Whitney-type fact: a law's allowed states carry a graph
  exactly when its knot matroid is graphic. Used here through Whitney's theorem for the step from allowed states to junctions.

`python3 -B scripts/track.py objects "ring of four four-place knots and one five-place knot cheapest counts" --until 2026-11-18 --exclude RING-READ-20261118-001`

- `RING-GROWTH-20261118-001`: the same population; its ring code and counts are reused (closed record).
- `FIRST-KNOT-20261118-001`: a relative (the joining rule reads open distinctions; the same relation grows differently by
  presentation, so the presentation matters, which is why this study reads junctions and not only allowed states).
- `TOUCH-CENSUS-20261118-001`: the census in which the ring was found; same population family, never read from distances.

Dependencies read for what is proved: `BOND-NEXT-JOIN-20261117-001` (the reader to six, and its key lemma: a sum of three or more
junctions has support at least seven, which the ring breaks), `VARIABLE-OUTPUT-READER-20261118-001D`, `-001E`, `-001F` (the full
table versus the allowed states; a width-32 table with two parity spaces; three-parent joins read through width 26),
`VARIABLE-OUTPUT-READER-20261118-001G` (scope above), and `-001A` (identical allowed states with different one- and two-parent
menus at width 18, under the other law).

## Prior work outside the program

Whitney's 2-isomorphism theorem (1933): two graphs with the same cycle (equivalently cut) space on the same edges are related by
vertex identifications, splittings and twists at 2-separations; a 3-connected graph is fixed by it. Reconstructing a graph from
the sizes of the smallest bonds through pairs of edges is not a problem I know in the literature; the closest standard object is the
matroid's pairwise circuit sizes. Not searched further for a scouting-scale study; the referee may.

## Disclosed before the freeze

The scouting probe (2026-11-18, provisional, scripts outside the repository) computed tables at m = 3 and 4 at rounds 3 to 16 and
found: the reader to six exact at rounds 3, 6 and 9 with the regrown round matching (Weisfeiler–Leman hash and sizes); at round 10
the reader run on to support 7 returns three spurious junctions (sizes 5, 5, 4; none missed), all near the round-1 one-parent
junction of three distinctions and the five-place seed knot, from bonds of three junctions with support 7; an explain-away variant
(drop pairs explained by sums of two or three read junctions) misses a true junction and fails at rounds 10 to 16. The scouting
also saw one-parent junctions only in round 1, to round 24. Timing of the enumeration was measured (m = 4 at round 20: one second).

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage` names
claude-fable-5-2). Its points and what I took:
- The m-bounded enumeration only finds upper bounds; long chains of three-distinction junctions or a belt round the ring could hide
  a smaller bond with both sides large. Taken: m raised to 6 and 7 (8 where it runs), and the facts that rule out its two shapes
  are computed (F1, F3). Its max-flow certificate was considered and not used: a minimum cut containing two edges may be two
  separate junctions (two four-distinction junctions undercut a nine-distinction one), so it does not bound the bonds the reader
  needs.
- A principled prune is linear: discard a clique lying in the span of the junctions already read. Taken as reader R1′ with the
  advisor's prediction; my own expectation is that it fails, since the scouting's spurious cliques have pairs at distance 6 and are
  not themselves parity consequences.
- P5 fails by construction where a live one-parent junction hangs on one parent. Taken as a check (F1 says none is live after round
  1); the uniqueness claim P3 is stated among incidences legal for the law, as advised.
- Whitney twists at 2-separations could give a second legal incidence with the same table; the 2-separations are enumerated if P5
  fails.

## Settled by construction (stated, not tested)

- The table is a function of the allowed states (the cut space), so any two incidences with the same cut space have the same table.
- Choosing any other vertex of G as the outside gives the same cut space: its junctions are the old ones less that vertex's star,
  plus one junction made of all the old loose distinctions. So no table says which junction holds the loose distinctions; the law
  does, because that junction would have as many distinctions as there are loose ones (far above the ring's largest junction at
  every round checked). FRESH-COUNT's "one round early" is this ambiguity at its smallest.
- A reader with horizon H (distances above H pooled) runs stages to support H + 1, so it cannot read a junction of more than H + 1
  distinctions as a clique unless all its pairs lie in smaller bonds.

## Definitions

- Table: `bond_table(stars, m, K)` in `ringread.py`: exact distances up to K = largest junction size over every bond with a side
  of at most m junctions (o excluded) and a connected complement; other pairs pooled at K + 1.
- R0: BOND-NEXT-JOIN's `read_stages` to support 6, imported unchanged from the closed proof file.
- R1: the same stages run on to support K (the largest junction size), same pairwise prune.
- R1′: R1, and at each stage discard every clique lying in the GF(2) span of the junctions kept at the previous stage.
- R2: R1's final junctions; remove candidates (every inclusion-minimal removal of at most six, fewer if the count of removals to
  try passes 200,000, which is then reported) until the incidence is legal for the law:
  every distinction in one or two junctions, every junction at least three distinctions, two junctions sharing at most one
  distinction; keep each legal repair whose own table (same m and K) equals the given table. "Works" = exactly one survivor and it
  is the true junction set.
- Regrown round: one round of the cheapest counts grown from R2's junctions alone, compared with the true next round as the
  multiset of (parent junctions, fresh count).
- G: the junction graph with o (multiple shared distinctions merged).

## Predictions (frozen)

Rounds T = 10, 12, 14, 15, 16, 18, 20; tables at m = 6 (main) and 7, and 8 at T ≤ 14.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: at rounds 1 and 2 the m = 6 table equals the brute-force bond table over every side; R0 recovers the ring exactly at round 9; R2 given the round-10 table with one entry changed returns no survivor equal to the true junctions | any fails |
| F1 | No one-parent junction after round 1 (so no chain of three-distinction junctions longer than one) | one exists |
| F2 | G has no triangle and no two junctions share two distinctions | either occurs |
| F3 | Every layer cut (junctions of rounds at most s against the rest, o included) has at least 11 distinctions | one is smaller |
| P1 | The tables at m = 6, 7 (and 8) agree entry for entry at every T | any entry differs |
| P2 | R1 returns at least one spurious junction at every T | some T is exact |
| P3′ | R1′ returns exactly the true junctions at every T (the advisor's prediction; mine is that it fails) | some T differs |
| P3 | R2 has exactly one survivor, the true junction set, at every T | none, two or more, or a wrong one |
| P4 | The regrown round equals the true next round at every T | some T differs |
| P5 | G is 3-connected at every T | a 2-vertex cut exists |
| P6 | The least horizon H at which R2 still works is (largest junction size) − 1 at every T | H is smaller, or R2 needs more |

## Runs and stop rule

`check.py` runs every T in one process (minutes; under ten, so not registered as long-running) and writes
`artifacts/RING-READ-20261118-001A/RING-READ-20261118-001A-E001_tables/results.json`. If P3 holds, the study closes with a reader
that works at rounds 10 to 20 (computed, not an all-size proof). If P3 fails with two or more survivors, those incidences are two
answers with one table, checked for legality against the law and history; if it fails with none, the failure is diagnosed and the
study closes with the obstruction. Either way: referee hand-off, two-table report.

## Amendment 1: ticket B, frozen before it runs (2026-11-18)

Ticket A's frozen run has been read (`artifacts/RING-READ-20261118-001A/.../results.json`): the gate, F1–F3, P1, P2, P5 held;
P3′ failed (the linear prune changed nothing); P3, P4 and P6 held at rounds 10, 12 and 14 and failed at 15, 16, 18 and 20, where
R1 misses junctions and makes 104 to 148 spurious ones near the seed, and R2 finds no legal repair. Diagnosis (`diagnose.py`, after
the run): at round 15 the missed junction is the round-1 three-distinction junction, one of whose pairs the pairwise prune removes
at stage 8 (R1 recomputes every junction each stage); the spurious cliques come from bonds of size at most 8 that are sums of three
or more small junctions near the seed. The advisor was asked again ([question](advisor/question_2.md),
[answer](advisor/answer_2_fable.md)): it judged three junctions too few (chains and closed rings of small junctions sum to small
bonds; a 2-by-2 block of four-place junctions has support 8), proposed the closure below, warned that kept wrong junctions can
poison later stages, and bet against Q1.

Reader R3 (`experiments/RING-READ-20261118-001B/.../reader3.py`): keep every junction read at an earlier stage; at stage s remove
a short pair lying in the support (at most s) of the sum of a connected set of known junctions, at most s of them, grown only while
the running support stays at most s + 2, unless one known junction holds both; new junctions are the maximal cliques of at most s
distinctions that are not known, not in the span of the known ones, and share at most one distinction with each known junction (F2
used as a filter, declared). R3+ = R3 followed by ticket A's legality repair and own-table check. Same tables (m = 6), same rounds.

| # | Prediction | Fails when |
| --- | --- | --- |
| Q0 | Gate: R3 exact at rounds 3 to 9; R3+ on the mutated round-10 table does not return the true junctions | either fails |
| Q1 | R3 alone returns exactly the true junctions at every round 10 to 20 (the advisor bets against) | some round differs |
| Q2 | R3+ has exactly one survivor, the true junctions, at every round | none, two or more, or a wrong one |
| Q3 | The round regrown from R3+'s junctions equals the true next round at every round | some round differs |
| Q4 | The least horizon at which R3+ works is (largest junction size) − 1 at every round | smaller, or R3+ needs more |

Stop rule: one run per round. If Q2 holds, the study closes with a reader that works at rounds 10 to 20; if it fails, it closes
with the obstruction found, a reader that works to round 14, and the diagnosis. No third reader in this study.
