I did this by hand and ran nothing. The short version: Lemma A is right with one caveat, Claim B as stated has no reason to hold, and a stronger version with "same equations" in place of "same table" has a three-line proof and persists for every later round.

## 1. Lemma A

It is right, provided connectedness is a standing assumption.

- **Only parents matter after the round.** Every loose distinction is taken, so the next live junctions are exactly the new ones, and a new junction meets only its parents. The next round's candidates are therefore "share a parent" and its excluded sets are "have a common parent". So d, and hence the fresh counts, depend only on the parent sets, including offshoots (an offshoot of u is a candidate with every other new junction of u).
- **Parent sets depend only on (L, loose counts, F).** Candidates are the pairs in F, the sets are the maximal candidate cliques not in F, and the stall test uses the loose counts. "Maximal among sets with no common junction" and "maximal clique, then filtered" agree, because a common junction of a superset is one of the subset.
- **Junctions met by no live junction, and multiplicities of shared distinctions, are not read.**
- **"Which live junctions meet each other" is redundant** for the output, unless your convention lets a junction meet itself when building F. Fix that convention in the statement.
- **The caveat is the fresh-0 rule.** "Holds every loose distinction" is a function of R only if the arrangement is connected. Without that, the correct test is "every loose distinction of its component", which R does not contain. Either assume connectedness or add components to R.

## 2. Claim B

**What is provable (Claim B*).** If phi is an isomorphism of the equations (cut spaces) and matches the round's output, then phi' is an isomorphism of the next equations, hence an isometry of T'.

- Each old junction's distinction set is unchanged by the round, so the old junction equations are the same sets in a'.
- The equations of a' are therefore the equations of a plus the new junctions' sets (taken plus fresh).
- phi carries the first part by hypothesis and the second by Lemma A. Re-pairing twins is harmless because they are parallel in G.
- Bonds are the minimal nonempty cuts, so every bond size is carried, not only the pairwise minima.
- phi' again keeps the next reading, since that is a function of the parent sets. So the pair stays together in every later round, by induction.

**Why the table alone should not suffice.** Bonds of G are the bonds of G' that avoid fresh distinctions, so T' ≤ T on old pairs. The new bonds put new junctions on the inside:

- **Discounts.** Moving a new junction n inside changes the cost from |P(n) ∩ A| to fresh(n) + |P(n) \ A|. A pair-junction with fresh 1 and both parents inside saves 1; a three-parent junction with fresh 1 and all parents inside saves 2; offshoots never save.
- **Gluing.** An inside A that is disconnected in G can be connected through n, giving sizes like |B1| + |B2| − 2 + fresh(n).

So T'(x,y) is the minimum over old bonds through x, y of size minus discounts, and a larger bond that swallows candidate pairs can beat the minimal one.

The smallest exposed reading is three-way. For a pair-junction n of (u,v) with fresh 1 and fresh distinction f, writing ℓ_u, ℓ_v for the taken loose distinctions:

T'(x,f) + 1 = min( c3(x; u,v) − 1, c(x; u in, v out) + 1, c(x; v in, u out) + 1, glued terms )

Here c3 is the smallest bond through x with both u and v inside. The old table gives only min(c3, c(u in, v out)) = T(x,ℓ_u) + 1. So if c3 exceeds that minimum by exactly 1 in a and by 2 or more in b, the next tables differ at (x,f). Nothing in "isometry + R" forbids this.

**What extra invariant works.** Three-way readings cover T'(old, fresh). T'(old, old) needs a (2+2j)-way reading for j discounted junctions inside, so no fixed order is enough in general, and "sizes of all bonds through each pair" does not record who is inside. The invariant that closes the argument is the equations themselves.

**Counterexample search.** Look for R-keeping isometries that are not equation isomorphisms (rank test: do images of a's junction sets lie in b's cut space?). Among those, look for a candidate pair with fresh 1 and a c3 mismatch within 1 of the pairwise minimum.

## 3. The honest statement

- **Proved:** same equations plus same growing end carries everything that grows, forever.
- **Not proved and probably false in general:** distance plus growing end carries the next table. The table is the pairwise shadow of the equations, and growth reads the many-way part through the discounts.
- **Sufficient, not necessary:** the 6 pairs and the 3 smoke-test pairs persist with no R-keeping isometry. Record for each whether the next isometry extends an old one at all, or maps new distinctions onto old ones. Those are different phenomena.

Before freezing, I would split every pair into three classes:

| Class | What it tests |
|---|---|
| Equation isomorphism + R | Nothing new: the theorem applies and it must persist |
| R kept, not an equation isomorphism | The only real test of Claim B |
| Neither | Persistence here is unexplained |

If the second class is empty, the data cannot test Claim B, and the real open question is whether "isometry + R implies same equations" at these sizes.

## 4. Bets

| Statement | Probability |
|---|---|
| Claim B* (equations + R) is true | about 99%; it is a proof |
| Claim B is true in general | 25% |
| No counterexample in the dataset, "some R-keeping phi extends" form | 80% |
| No counterexample in the dataset, "every R-keeping phi extends" form | 60% |
| Most R-keeping isometries among the carried pairs are equation isomorphisms | 55% |

The static 1,034 are likely near-vacuous, since the ones you looked at have no R-keeping isometry; the test's power is in the carried pairs. If a counterexample exists, I expect it at the three-way mismatch above, in a pair where two live junctions with one loose distinction each get a fresh-1 pair-junction.
