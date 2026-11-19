I am designing a study and want a colleague's check before I freeze it. Please be concrete and critical.

Setting. An arrangement is a set of junctions, each a set of distinctions (a parity constraint: XOR of its distinctions = 0). A
distinction held by one junction is loose; by two, shared (never more). Junction graph G: vertices = junctions plus an outside
vertex o; each distinction is an edge (shared: between its two junctions; loose: junction to o). The allowed states are the
solutions; their equation space is the span of the junction stars = the cut space of G. "Meet once": no two junctions share two
distinctions (G simple apart from parallel edges to o). Legal: every junction holds >= 3 distinctions, no cut vertex but o.
The bond-distance table: for distinctions x, y, the smallest bond (minimal cut with both sides connected) of G containing both, less
one. Two arrangements "collide" when non-isomorphic with isomorphic tables (up to renaming distinctions); "same states" when some
renaming carries one equation space onto the other (equivalently, by Whitney, the graphs' cycle matroids are isomorphic).

The growth law (complete rounds). Round 0 is a start (a few knots). In each round, the live junctions are those of the last round
that still hold loose distinctions. Two live junctions are candidates when they have a common neighbour in G - o (any junction,
"share a parent"). Every maximal set of >= 3 live junctions that pairwise are candidates and have no common neighbour all together
gets one new junction taking one loose distinction from each; every candidate pair not inside such a set gets one; every other
loose distinction gets a new junction of its own (an offshoot). Each new junction then receives some fresh (loose) distinctions,
possibly 0 only when its parity is implied (then it holds all loose distinctions and closes the stage). New junctions share nothing
with each other.

Findings so far. GROWN-PAIR: reached collisions with other states exist (152 groups, up to 14 junctions) but only when start knots
share two distinctions. MEET-ONCE: among 2,698 reached meet-once stages of 15 to 40 junctions, all 102 collisions have the same
states. UNIQUE-TABLE: six census stages (7-8 junctions, reached at round 1, meet once) have 11 static legal rivals with equal tables
and other states; none of the rivals is reachable (a referee checked every start).

Design-stage observation (disclosed; I looked before freezing). Define
- P1: for every junction holding a loose distinction, any two junctions it meets also meet some third junction in common;
- P2: no two junctions holding loose distinctions meet.
All six truths satisfy P1 and P2. All 11 rivals violate P1 (5 to 8 violating triples each); 10 of 11 violate P2.

Lemma I would prove: every stage of round >= 1 satisfies P1 and P2. Sketch: after round r the junctions with loose distinctions are
exactly the round-r junctions with fresh distinctions (round-(r-1) live junctions give all their loose distinctions in round r;
older ones have none). Such a junction meets exactly its parents. Its parents were pairwise candidates, i.e. had a common
neighbour w before it existed, so w is a third junction both meet. Round-r junctions share nothing with each other, giving P2.

Planned static test of sufficiency. Enumerate every legal meet-once arrangement with at most 7 junctions and at most 2 loose
distinctions per junction (and at most 3 for up to 6 junctions): every connected simple graph H from the graph atlas, every loose
count vector up to Aut(H). Exact tables by enumerating vertex subsets (<= 8 vertices). Group by table isomorphism; states by a
junction-graph isomorphism or a renaming of twin classes (distinctions with the same holders) checked by rank.
Predictions: S1 no other-states collision with both sides satisfying P1; S2 other-states collisions exist in the population (the
known pairs at 7 junctions among them); S3 the same with P1 and P2 together (implied by S1). If S1 holds it is a conjecture
(P1 + meet once => the table carries the states), which with the lemma would give "no reached meet-once collision with other
states" at every size.

Questions.
1. Is the lemma's proof right? Edge cases (round 1 from a start whose knots meet; closing junctions with 0 fresh; offshoots)?
2. Is the static enumeration a fair test of the sufficiency conjecture? Bounds, legality, what could make S1 hold vacuously or for
   the wrong reason (e.g. P1 being rare, or tables being too coarse at these sizes)?
3. Your bet on S1, and where a P1-P1 other-states collision would most likely appear.
4. If S1 holds, a proof route for "P1 + meet once => equal tables imply the same cycle matroid".
5. Naming: I would call P1 "the parent rule" (in a reached stage the junctions met are the parents; "parent" is the glossary's
   word) and P2 "loose junctions apart". Better names? No words from two- or three-dimensional space, please.
