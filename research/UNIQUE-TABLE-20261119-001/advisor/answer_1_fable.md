**Verdict: (1) is sound; (2) is false as stated, so swap in the test below; (3) has two gaps. I have not run anything; this is from memory and hand argument.**

**(a) Sound.** A size-(d+1) circuit through p in any rival code has all pairs at T ≤ d, so a unique candidate lies in every rival code. G is itself a rival, so F ⊆ C comes free, and F = C gives C ⊆ C'. The cap d+1 ≤ K only limits compute. But K does not bound rival star sizes, so the SAT fallback's "cliques of size ≤ K" is unsound: twists and re-rooting make larger stars (old o becomes a junction). Bound by incidence count instead.

**(b) False in general.** C ⊂ C' at codimension 1 is the setting of Shih's theorem (1982 thesis; restated in Pivotto's thesis and Guenin–Pivotto–Wollan). Vertex splitting is only one of several cases; the others re-glue pieces at small separations. This is from memory, so check it. At higher codimension the intermediate codes need not be graphic at all.

A sound test needing no structure theory:
- Stars span C', so if C' ⊋ C, some rival star S lies outside C.
- S is a C' circuit, so all its pairs have T ≤ |S| − 1.
- Every edge e has m(e) = 1 + min_f T(e,f), its smallest circuit size, which is fixed by T. So no word of the coset S + C through e may weigh less than m(e).
- The coset has at most 2^10 words, so this is cheap. If no S ∉ C passes, then C' = C.
- At codimension 1 it is exact: compute the table of C + S and compare. Do not assume tables are monotone under enlarging the code; only m(e) is.

**(c) Complete only with two repairs.**
- **Outside choice is per block.** o may be a cut vertex, in G and in rivals. Legality forces every cut vertex to be the outside, so all blocks meet at o', but each block picks its own attachment vertex independently. A single global choice misses rivals.
- **Twists need closure.** Take the closure under twists (or use the Tutte decomposition, including reordering of series nodes with ≥ 3 virtual edges), not single twists from G. Filter for degree ≥ 3 and no shared pairs afterwards.
- **o isolated.** Each block may independently stay closed or take any of its vertices as outside (its star becomes the loose set). These are always legal, since each neighbour gains one loose edge and the other stars are unchanged bonds.

**(d) Predictions (rough guesses).**
- **o isolated (15):** all same-states-ambiguous.
- **3-connected (176):** Whitney leaves only re-rooting. Re-rooting at any junction is legal exactly when deg(o) ≥ 3 and no junction has two loose edges. So these are decided by a one-line criterion, and are unique otherwise, provided the coset test passes.
- **Overall:** unique 55–70%, same-states-ambiguous 25–35%, undecided 5–15%, concentrated in 2-separation stages with F ≠ C. Different-states rivals: at most a handful, none among the 3-connected.
- **Bet against:** "nearly all unique". Reader ties suggest twist or re-root freedom.

**(e) Separation.** Label each rival R with two bits:
1. Is span(stars of R) = C? This is a rank check.
2. Is R = π(G) for some edge permutation π?

In your population the table-symmetry kind is provably empty. If R = π(G) has table T, then π ∈ Aut(T), which preserves the stars, so R = G. State that as a lemma rather than searching for it.

Every rival is therefore non-isomorphic to G, and bit 1 alone splits same-states from different-states. Sub-label same-states rivals as re-root, twist, or both, and report rivals up to Aut(T) orbits so counts are not inflated.