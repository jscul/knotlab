I need a colleague's judgement, early, on whether a proof route is clear. If it is not, I will switch to another direction rather than
grind. Please be concrete and brief (under 600 words).

Setting (as in earlier questions): addressed not-all-equal patterns with orbits of at most 4 addresses, a tree of blocks with finitely
many orbit types; P_N the depth-N pattern; L_N(3, s) the least bond with a member at level 3 and one at level 3 + s. Proved tools:
Lemma S (finite (type, composite) path states, ultimately periodic lengths); Theorem D (per depth tier r and residue of s: eventually
constant or linear, by pumping a member-free window of T+Q+1 saturated levels with no special orbit, i.e. no member and no branch
point of the bond's skeleton S); Lemma R (depth pumping); Theorem G (if every l0-step composite on the top's component is a product,
linear growth); Lemma J (a bond lies in one component); the carriers (two-orbit, orbit-and-block, stem bonds) and forgetting tests.
On 627 + 583 + 181 distinct small-orbit patterns these decide everything.

Goal: a decision procedure for "L bounded over all (s, N)" for small orbits.

What I have: (1) L_N(k, s) = min |D| over sets D that are constrained while D minus its level-k members and D minus its level-(k+s)
members are both free (a minimal constrained subset of such a D is a bond meeting both levels). (2) By D, a bounded residue has, for
large s, least bonds with a long saturated member-free window. (3) The skeleton is a tree, so the window is crossed by k disjoint
paths; below the window the k crossing bottoms carry k independent subtrees, one holding the level-(k+s) members. Product crossings
carry nothing, so a minimal set has only non-product crossings, whose composites are periodic. (4) For fixed k, the upper part's
"profile" (for each assignment of its members, the compatible k-tuples of crossing-top states, with and without its level-k members)
ranges over a finite family closed under the tree's block steps with arbitrary decorations (a fixpoint, like a decorated closure), and
similarly each lower subtree's condition. So "a gadget with k crossings exists" is decidable for each k, and "L <= c" for each c.

The gap: nothing bounds k. Boundedness is semi-decidable (search c), but growth needs "no gadget for any k", an infinite check, unless a
gadget with many crossings can be compressed to one with at most K0 crossings.

Questions: (a) Is there a compression argument (e.g. two crossings of the same periodic composite type with the same lower condition
can be merged or one dropped; or a Ramsey/pumping argument on the upper tree's branching) that bounds k, making the procedure total? (b)
If not, is there a different route to totality (e.g. treat the upper part as a tree automaton over decorations and decide emptiness of a
"gadget language", which would handle all k at once)? (c) Is a restricted theorem worth having: decidable when the non-product
periodic composites have some property (e.g. each is "functional" in one direction)? (d) Your honest estimate: is this a few-day proof
or an open-ended project? If open-ended, say so and I will switch to growing orbits.
