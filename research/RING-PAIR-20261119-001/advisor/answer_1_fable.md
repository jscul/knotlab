<!-- modelUsage: claude-fable-5-2 -->

# Advisor answer 1 (RING-PAIR-20261119-001)

I worked only from your statement, not from the growth code, so every claim about the rule itself is my reading and needs your check. The citations are from memory.

## 1. Is H a theorem, and which step is weakest

H is plausible as a theorem. The counting half already is one; the half that maps the growth onto vertex sets is where the work is.

**Counting half (sound).**
- Condition 4 says two blocks share at most one vertex, so the vertex–block incidence graph has a tree as universal cover, and the deck group is free and acts freely.
- No deck element fixes a finite set: it would permute finitely many vertices, a power would fix one, and the group is torsion-free. So orbits of rooted sets are counted once per base vertex and your formula is right.
- A cheaper identity follows: Σ_x y Π Φ(B, x) = y C′(y), up to the knot-free singletons. So c(t) = [y^(t+1)] R / (t + 1), where R is the rooted sum. This checks the dissymmetry code independently, and (t + 1) must divide every rooted coefficient.
- It also gives −5/2 directly: R has a square-root singularity, so C has a 3/2-power one.
- The system is aperiodic, since U = y Π(1 + U) has y and y² terms. It is not strongly connected when X has pendant parts, so cite the non-irreducible case, not plain Drmota–Lalley–Woods.

**Growth half.** Your four steps, strongest first:
- **Round = size − 1** is immediate by induction.
- **Parents = sets less a non-cut vertex** is a clean lemma. For |S| ≥ 3, any two parents S − u and S − v share a connected grandparent S − {u, v}; otherwise u and v would both touch two components and close a cycle through distinct blocks. For |S| = 2 the "through" object is the knot w, not a subset, so start the induction at round 2 and do rounds 0–1 by hand.
- **Groups (weakest).** You need the rule's groups to be exactly the full parent set of each connected S, and I read that as three sub-claims:
  - *Upstairs there are no false groups.* Pairwise-candidate sets through distinct intermediates lie in a common (t + 2)-set; this is the two-types-of-clique fact for Johnson graphs.
  - *Downstairs a false group needs a triangle of candidates that does not lift closed*, meaning three exchange steps that carry S to γS with γ ≠ 1. For a path along γ's axis, |S ∖ γS| is the translation length, so this needs a closed non-contractible walk of length ≤ 3 in X. I sketched this only for paths; the general case is the lemma to prove.
  - *Conditions 3 and 4 are then exactly "every deck element translates by ≥ 4".* If my reading is right, they say the knot–bit graph G has no cycle of length 3, 4 or 6. Check that a ring of six fails condition 3, a ring of four fails condition 4, and any three knots pairwise sharing bits fail condition 3.
- **Bit invariant.** State explicitly what bits the junction for S carries. If it is one per parent plus one per outside neighbour of S, then conditions 1–2 give ≥ 4 for every |S| ≥ 2, so the floor never returns. Condition 4 forces every knot to have ≥ 2 neighbours in X, and condition 2 covers surplus vertices. If the invariant is anything else, this is where H breaks late.

## 2. Falsifiers

First compute the shortest non-ring cycle of G for each of the fifteen; any 6-cycle puts a start out of scope. The risk is "5–5 by two paths of one", depending on where the paths attach.

The edge of the lemma is translation length 4, a G-cycle of eight. Only "7–7 joined twice" has one, so it is the planned start most likely to fail. I would add:

- **A ring of eight with a lone knot on each of knots 1, 3, 5, 7.** G is bipartite, so X has two components: a 4-cycle of three-vertex blocks and a bare 4-cycle. H predicts two rational series that never interact. This tests both the shortest allowed translation and whether the two classes stay apart. Skip it if even rings are already among the 36.
- **5–5 sharing a knot c, plus a path of three lone knots from a2 to b2.** This gives a G-cycle of eight through c: a 4-cycle of blocks of sizes 4, 3, 2, 3 inside an X with several independent cycles. It tests groups of three and four on a shortest axis.

## 3. Mathematics to cite

- **Closest match:** lattice animals on the Bethe lattice, whose mean-field exponent is θ = 5/2. Fisher and Essam 1961 (J. Math. Phys. 2); Lubensky and Isaacson 1979 (Phys. Rev. A 20). Your t^(−5/2) is this exponent.
- **Sanity formula:** the d-regular tree has d/((d−1)n + 1) · C((d−1)n + 1, n − 1) connected n-sets through a vertex. I checked d = 2, and d = 3 for n ≤ 3.
- **Animals on non-amenable graphs:** Madras and Wu 2010, "Trees, animals, and percolation on hyperbolic lattices".
- **Block trees and dissymmetry:** Otter 1948; Harary and Uhlenbeck 1953 (Husimi trees); Bergeron, Labelle and Leroux, *Combinatorial Species and Tree-like Structures*, ch. 4.
- **Asymptotics:** Drmota 1997, Lalley 1993, Woods 1997; Flajolet and Sedgewick VII.5–VII.6; Banderier and Drmota 2015 for systems that are not strongly connected.
- **Free groups:** I know nothing closer than the Bass–Serre picture (a free group acting freely on a tree of blocks). Counting subgroups by Stallings graph size (Bassino, Nicaud and Weil 2008) is adjacent, not the same count.

What you add is the identification of a joining rule with this count, not the count.

## 4. "A rule that refers to itself", and "fractal"

Plain version: each round the rule is applied to the junctions the same rule made in the round before, and to nothing else. So the count of what it makes satisfies an equation in which the unknown appears on both sides, U = y Π(1 + U). That is all "self-reference" means here; it is recursion, not a statement about itself.

"Fractal" is defensible in one precise sense. With two or more independent cycles, the cover has finitely many branch types, and each branch contains copies of every type. That is exact self-similarity, and the fixed-point equation is its count. With one cycle it is merely periodic.

It is not defensible as a dimension claim. A dimension needs a metric on the ends of the cover, and that metric would be chosen, not native. I would write "self-similar (finitely many branch types)" in claims and keep "fractal" in quotation. The count does not show emergence either.
