Colleague check on a proof-plus-search design, before I freeze it. Under 600 words. Be concrete about what is sound.

Setting. A parity arrangement is a graph G whose edges are distinctions; each vertex but one (the outside vertex o, which ends
every loose distinction) is a junction, whose star is a parity equation; the equations span the cut space C of G. The table T gives,
for every pair of edges, (size of the smallest bond = circuit of C containing both) - 1. Population: 522 census stages with 3 to 10
junctions and 9 to 29 edges, no two junctions sharing two edges, where an exhaustive VF2 search found that every permutation of
edges preserving T also preserves the set of junction stars (no table symmetry moves a junction), and where my reader failed
(mostly a tie it could not break). 330 have a 2-vertex separation (with o), 176 are 3-connected, 15 have nothing loose (o isolated).

Question: is G the only "legal" arrangement with table T? Rival space (my proposed bound): incidences on the same edges where every
edge is in one or two junctions, every junction has at least 3 edges, two junctions share at most one edge, and every junction's
star is a bond of the rival (no cut vertex), sizes unbounded.

Plan, per stage:
(1) Forcing. For each pair p with T(p) = d and d + 1 <= K (K = largest junction), list the (d+1)-sets containing p all of whose
pairs have T <= d (they are the only possible circuits of size d+1 through p in any rival code). If exactly one, it lies in every
rival code. F = span of forced sets. If F = C, every rival code C' contains C.
(2) Excluding C' strictly larger than C. Idea: a rival with C' > C has more vertices on the same edges; I believe it must be a
vertex-splitting of (a 2-isomorph of) G, so some rival star is a proper subset P of a true star (or of the loose set) with
3 <= |P|, and P being a bond forces all pairs of P to have T <= |P| - 1. So if no such proper subset is a clique at its size, C' = C.
(3) Same code, different junctions. Enumerate the Whitney 2-isomorphism class of G (twists at 2-separations) and every choice of
outside vertex; each legal incidence other than G there has the same table.
Stages where F != C go to a bounded SAT search (rival junctions = cliques of size <= K, multiplicities 1-2, lazy table check).

Questions: (a) Is (1) sound as stated? (b) Is the claim in (2) true (C' a superspace of C forces a refinement of a 2-isomorph of G),
and if not, what is the right sound test? (c) Is (3) complete for same-code rivals (twists + outside choice), including when o is
isolated? (d) What fraction of the 522 do you expect to come out unique, same-states-ambiguous, or undecided, and which prediction
would you bet against? (e) Anything to separate cleanly the three kinds of non-uniqueness: table symmetry, same allowed states with
different junctions, and different allowed states with one table?
