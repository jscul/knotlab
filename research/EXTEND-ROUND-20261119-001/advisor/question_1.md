I want a colleague's analysis before freezing a proof attempt plus a counterexample search. Be rigorous and concrete; bet.

Setting. Parity arrangements: junctions = sets of distinctions; a distinction is held by one junction (loose) or two (shared).
Junction graph G: junctions + outside vertex o, distinctions as edges (loose ones to o). Equations = cut space of G. Table T(x,y)
= smallest bond (minimal cut with both sides connected) containing x and y, less one. A junction is live when it holds a loose
distinction.

One complete round of the law (census's): live junctions L; two live junctions are candidates when some junction meets both;
every maximal set of >= 3 pairwise candidates with no junction meeting all of them gets a new junction taking one loose distinction
from each member; every candidate pair in no such set gets one; every other loose distinction gets its own new junction
(offshoot); stall if a junction is in more sets than it has loose distinctions. Fresh counts: max(d, 3 - p, 1), d = number of the
next round's sets the new junction will be in, p = its parent count; 0 only if its parity is implied (connected arrangement: it
holds every loose distinction).

What the round reads (my statement). R(a) = (L, each live junction's loose count, which live junctions meet each other, the family
F of sets of live junctions met all by one junction). Lemma A: the round's output (new junctions' parent sets and fresh counts) is
a function of R up to relabelling. A table isometry phi: a -> b "keeps the reading" when it carries loose distinctions onto loose
distinctions and each live junction's distinctions onto a live junction's (giving psi: L_a -> L_b), and psi carries F_a onto F_b.

Claim B (to prove or refute): if phi keeps the reading, its extension phi' (new junctions matched by psi of their parent sets;
taken and fresh distinctions matched; loose distinctions of one junction re-paired, since they are twins in the table) is an
isometry of the next tables T(a'), T(b').

Context: GROW-SMALL found 86 reached meet-once pairs with isometric tables and other states that stay isometric (full tables) one
round further, and one created pair that parts; CREATED-PAIR found every small carried pair (63) has isometries keeping the loose
distinctions, 57 of 63 keep the "growing end" (loose kept and every live junction carried onto a junction), 6 smallest (9
junctions) do not, yet persist. In a 10-case smoke test (disclosed), three of those 9-junction carried pairs have no isometry
keeping R, yet their next tables are isometric; the static pairs looked at have none keeping R.

Questions:
1. Is Lemma A right as stated, or does the round read more (for example the junctions met by no live junction, or the equations)?
2. Claim B: proof idea or counterexample idea? Note the table is only pairwise minimal bond sizes, while the next table depends on
   all bonds of the split graph (o replaced by the new junctions). Is there a reason minimal sizes after the split are determined
   by the old table plus R? If not, what extra invariant would make it true (for example the three-way readings, or the sizes of
   all bonds through each pair)?
3. Since persistence also happens without keeping R (the 6), what is the honest form of the statement the coordinator wants: "distance
   plus the growing end carries what grows"?
4. Bets: Claim B holds on every pair with an R-keeping isometry among the 63 carried + 1,034 static pairs? 
