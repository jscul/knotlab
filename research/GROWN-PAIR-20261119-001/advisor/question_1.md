Colleague check before I freeze a small study. Under 400 words.

Previous result (UNIQUE-TABLE-20261119-001): on 6 of 527 symmetry-free census stages of parity growth under the cheapest counts
(complete rounds), a second arrangement, legal as a static arrangement (each distinction in one or two junctions, junctions of at
least 3 distinctions, no two sharing two, no junction at a cut vertex, same junction count), has the same exact bond-distance table
on the same named distinctions and different allowed states; in five of six the rival stalls at its next round; none is shown
reachable by growth.

Now: do two arrangements the growth actually reaches share a table? Design: every stage (rounds 0 to 8) of all 26,441 census
arrangements with at most 14 junctions (about 52,000 stages; round 0 is the start, marked); for each, the exact full table (every
pair, all bonds); a canonical form of the table up to renaming (Weisfeiler-Leman hash of the complete graph on distinctions with
the distance as edge label, then VF2 for exact isomorphism within a hash bucket); within a bucket, discard pairs whose arrangements
are isomorphic (incidence graphs with loose distinctions marked); report every remaining pair (two non-isomorphic reached
arrangements whose tables are isomorphic), whether their allowed states differ under the table isomorphism, and their next joins
and growth. If none, widen to stages of 15 to 24 junctions, or to Codex's serial mixed law's reachable census.

Questions: (1) Is this sound and complete for "two reached arrangements with one table, up to renaming"? Any pitfall (several
table isomorphisms; same arrangement reached by different starts; starts versus grown stages)? (2) Predictions: how likely is at
least one pair at up to 14 junctions, and among stages where junctions meet once? (3) Is "states differ under the isomorphism"
well defined when the table has many automorphisms; how should I state it?
