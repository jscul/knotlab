<!-- modelUsage: claude-fable-5-2 -->

# Advisor answer 1 (CLUSTER-ALL-20261119-001)

I had no file access in this session, so this rests on your message alone; I did not read RING-PAIR's cover model, the policy code or the pilot data. Everything below is reasoning to check, and none of it was run.

## The main finding: why the 38 fail, and a candidate exact rule (Q3)

Both of your examples are reproduced by one junction-level rule, which I reconstructed from them:

- **Candidates.** Two round-t objects are candidates when they touch a common earlier object (a knot they both touch at round 1; a shared parent later).
- **Valid sets.** A set of pairwise candidates is valid when it is a pair, or when no single object witnesses all its pairs (a clique that is not a star).
- **Junctions.** One junction for each maximal valid set; its cluster is the union.

Checks by hand:

| Start | Round 1 | Round 2 | Round 3 |
|---|---|---|---|
| Triangle 1-2-3 plus 0 touching 3 | {1,2,3} is not a star (witnesses 3, 2, 1) and supersedes pair 12; {0,1,2} is a star at 3, so 01 and 02 stay pairs: 3 junctions | J123, J01, J02 share 1, 2, 0 pairwise, so one junction: 1 | closes |
| Knot w with four untouching neighbours | 6 pairs (all stars at w) | {ab, ac, bc} share a, b, c, so one junction per triple: 4 | the four triples form one valid set: 1 |

The first row gives [4, 3, 1], as grown. The second gives every subset once, as your simplex rule says.

**Why the cover model is exact elsewhere.** If all round-t clusters in a block have the same size n, three sets pairwise meeting in n − 1 points either share a common core (a star, with different unions) or lie in one set of n + 1 points (equal unions). So "not a star" and "same union" coincide, and one junction per cluster follows. A hyperedge makes a cluster of size 3 or more at round 1, which breaks equal sizes. Cliques with unequal unions then appear, exactly when the hyperedge shares two knots with something else. Across a single shared knot no clique that is not a star can form, since its witnesses would make a cycle inside one block.

**Recommendation.** Keep them out of scope for the frozen test. A fix exists: run this set-level rule on the block alone and use its series as the block weight. I would not freeze it, for two reasons:
- It is a second fitted object.
- Rounds may no longer add across a shared knot for irregular blocks, so the product with pendants is unproved.

Instead, register the set-level rule as a separate secondary prediction on the out-of-scope starts, scored apart from the main one. If your policy code already states validity differently, that difference is the first thing to check.

**Scope warning.** If I read rule 2 correctly, a triangle hyperedge {1,2,3} goes out of scope as soon as any member has another neighbour 0: the simplex of that member contains the other two. So the scope at five knots may be far below the pilot's 98%. The scope fraction depends only on the starts, so compute it before the freeze; it does not unblind anything. If it is low, the hyperedge fix becomes the main result and deserves its own pilot first.

## Q1. The renewal derivation

I could not rederive the three cases (leaf, chain, two chains) or the floor max(d, 2) from the message, so I cannot confirm them. What I can say:

- **Rules 3 and 4 overlap.** A live knot with open = 1 and an offshoot has d = 0, so it is a one-point component. Rule 4 with m = 1 gives y²/(1 − y)², the same as y times the pendant y/(1 − y)². The exception "holds the only loose bit" is the same as "no other live knot". Merge them; that removes one fitted clause and one place for the two to disagree.
- **Offshoots of different knots.** Under the candidate rule above, an offshoot of k touches only k, so two offshoots of non-siblings never share a witness at round 1. They meet only through junctions containing both parents, which the product already counts. This fails if the policy's candidate relation reaches through two steps; check that in the code.
- **Where demand could differ from open − 1.** The likely place is a doubled pair: two knots with two common neighbours, merged into one edge. If the growth spends two of each knot's open places on it and the rule counts d once, both the stall test and the surplus s are off by one. Test with open exactly equal to d on such a knot.
- **Horizon.** Twenty rounds cannot tell an endless chain from one that closes later. Regrow a few of the smallest chain and relay starts to 40 or more rounds.

## Q2. The relay

- **Implied tops.** If "implied" is counted from open places, a top is implied exactly when its component contains every live knot. Freeze that wording rather than "other live knots exist", which reads ambiguously for live knots inside the same component. Any other live component keeps loose bits forever (its chains or its own relay), so no top elsewhere becomes implied later. If "implied" instead depends on the laws (a parity knot's open bit is forced by its other places), the answer can change, and the rule would then need the laws as input.
- **Tops of infinite components.** None in cluster terms: every finite cluster extends along a chain, so there is no maximal one.
- **Exponent.** y^(m+1) assumes the top forms at round m − 1. With a hyperedge in the component the top forms earlier, so the relay should carry the same y^(2 − |G|) factor. State whether leaves count in m.
- **Truncation.** A six-knot component with many leaves can top after round 20 or after the 20,000-junction cap. Report how many starts were cut off before their predicted relay or closure; those do not test rule 4.

## Q4. Likely breaks and falsifiers to add

1. **Two triangles sharing one knot** (1-2-3 and 3-4-5). The simplex of 3 is {1,2,4,5}; confirm the scope predicate puts it out, and score it with the secondary rule.
2. **Two triangles sharing two knots** (1-2-3 and 1-2-4). Is {1,2,3,4} one hyperedge of four, or two overlapping ones?
3. **Ring of six.** Candidates split into {1,3,5} and {2,4,6}, each a clique with three different witnesses. That predicts two hyperedges, two tops and two relays, [6, 2, ...]. Compare with RING-PAIR's record.
4. **Ring of five with unequal opens and pendants.** Tests the deck-orbit count where the symmetry is broken.
5. **Partly overlapping simplices** (w1 touching a, b, c; w2 touching b, c, e; six knots). The merged block lacks the edge a-e, and the pair bc arises twice. Set open(b) to 2 and to 3 to test the stall rule.
6. **A finite component beside a lone knot with open of 3 or more.** Both should relay, at different rounds.
7. **The same touch pattern through one shared distinction versus three.** A triangle on one common distinction against a triangle on three; the rule cannot tell them apart, the growth might.
8. **Later stalls.** Rule 1 tests round 1 only. If a junction's size is not set by the policy to fit its groups, a junction can stall later.

## On the freeze itself

- **T2 is not a prediction.** The chain and relay clauses came from JOIN-GROWTH and FIRST-KNOT, so label T2 a consistency check.
- **T3 needs a frozen sampler.** Uniform random six-knot arrangements will be mostly stalls and out-of-scope starts. Stratify by class, fix the seed, and report counts per class.
- **Freeze the scope predicate as code.** It was defined from the failures, so fix it by hash before the run, and treat any in-scope mismatch as a failure of the rule, not a new exclusion.
