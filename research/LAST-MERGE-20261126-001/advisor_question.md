You are advising on a small computational check before its prediction is frozen. Be concrete and critical; at most
450 words; a numbered list. Do not praise.

Setting. A deterministic growth law builds knots in rounds from a finite start (the cheapest growth: inside a proved
class, the knots made in round t are exactly the connected clusters of t + 1 members of an infinite cover of a finite
"map of joins", whose members are the start's live knots plus one member per leftover loose distinction). Read each
round's births by local type (kind, number of parents, fresh distinctions, places). A start of dimension D "settles" at
round K when, from K on, every local type's count per round is a polynomial of degree at most D - 1 in the round,
through round 24.

Data. On all 1,556 five-knot starts of a dimension and 387 sampled six-knot starts, under two knot laws:
- A bound K <= M + 5 (M = largest block: largest set of live start knots sharing a neighbour, or largest fresh count of a
  round-1 birth) failed on 47 starts.
- On those 47, K = T + 3 exactly (and K = T + 5 in a reading that adds parents' types), where T is the first round of
  the final trough of the count (the first round from which the total count never falls again). 34 of them first narrow
  to a single birth a round (one join of everything), then grow like a lone knot.
- The combined bound K <= max(M + 5, T + 3) (and max(M + 7, T + 5)) holds on every start of all four runs, but it was
  fitted on them.

Plan. Freeze the combined bound and test it on a fresh seeded sample of 2,000 six-knot starts (disjoint from the first
1,000) under both knot laws; also freeze a static prediction of T: T = (size of the largest part of the map of joins
with no endless chain) - 1, where it narrows to one birth.

Questions.
1. Is the combined bound a real claim or nearly circular, since T is read from the counts? What must it predict to be
   worth testing?
2. Is "first round of the final trough" well defined and robust (ties, plateaus, a dip after round 16)? Suggest a sharper
   definition.
3. Is the static T (largest finite part of the map, minus one) the right prediction of the merge round in the cluster
   picture? What would you freeze instead, and what is the cheapest discriminating test?
4. Any failure mode that would make a held-out pass uninformative?
