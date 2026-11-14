Cold check, about 300 words: find any error in these proofs (Theorems R, R1, Claim 1', Claim 2' first part) and say whether the dichotomy's stated gap is the real one. Be concrete; I will check your answer.

# The reading theorems

Status: Partial

Ticket `READ-RULE-20261114-001A`, 2026-11-14. Statements as frozen in `research/READ-RULE-20261114-001/preregistration.md`.
Theorems R and R1 and Claim 1′ are proved below. Claim 2′ is proved for its first part. The dichotomy is left as a conjecture, with
its gap stated.

## Setting and two facts

The pattern is the infinite usual-limit system of a living, complement-closed NAE family: every knot is NAE on three distinct
distinctions, and the allowed set Ω is nonempty and closed under complementing every distinction. "Free" and "non-shattered" refer to
the projection of Ω.

**Fact 1 (singletons).** Every distinction takes both values: Ω is nonempty and closed under complement.

**Fact 2 (pairs).** A pair {u, v} is non-shattered exactly when it is tied. Its projection is a nonempty, complement-closed subset of
{0,1}², and the proper ones are {00, 11} and {01, 10}.

So every bond has at least two members, and a two-member bond is a tie.

## Theorem R

*Statement.* At depth s, let a covered copy c hold the main port p at position k, and let S's block have a knot {k, x, z} with x own.
Write x and z also for the distinctions of c at those places. Then L(s) ≤ 3, and L(s) ≤ 2 when {p, x} is tied, unless {p, x} is free
and z is tied opposite to p or to x.

*Proof.* The constraint at c is NAE(p, x, z), since c's distinction at k is p. Here x is an own distinction of c, hence distinct from
p (a port of main) and from z.
- If z is p itself, the knot forces x = ¬p in every allowed state. By Fact 2, {p, x} is a 2-bond.
- Otherwise W = {p, x, z} has three distinct members. NAE excludes 000 and 111, so W is non-shattered and contains a bond B. By
  Fact 1, |B| ≥ 2.
- If B = W or B = {p, x}, it is a bond containing p and the covered target x, of size at most 3.
- Otherwise B is {p, z} or {x, z}, which is a tie by Fact 2:
  - z equal to p forces x ≠ p, so {p, x} is tied;
  - z equal to x forces p ≠ x, so {p, x} is tied;
  - z opposite to both gives p = x, so {p, x} is tied.

In each of these sub-cases {p, x} is a 2-bond. What remains is exactly the exception: {p, x} free, and z tied opposite to one of p
and x. Then W contains a tie but no bond holding both p and x. ∎

## Theorem R1

*Statement.* If in Theorem R the third member z is an own distinction of S that occurs in no other constraint and in no call's
arguments, then L(s) ≤ 3 with no exception.

*Proof.* z occurs in one constraint only, so the projection of Ω on {p, x, z} is
{(a, b, e) : (a, b) ∈ P, NAE(a, b, e)}, where P is the projection on {p, x}. Given any allowed state of the rest, the values of z
allowed with it are exactly those satisfying the knot.
- If P is a tie, {p, x} is a 2-bond.
- Otherwise P is all four pairs, by Fact 2. The projection is then the six NAE triples. Every pair inside it takes all four values,
  for example (p, z) = (0, 0) from (0, 1, 0) and (0, 1) from (0, 0, 1), with the rest by complement. So W is a bond of size 3. ∎

*Every large depth.* The carried sets R_s, and the copies realising them, are eventually periodic. If every residue of R_s's repeating
part has a carried position with such a knot, then L(s) ≤ 3 at every large s.

## Lemma C′

*Setting.* Let a member-free stretch of a bond W run from copy c_a to copy c_b along the target's word v: no member lies in the
blocks of c_{a+1}, …, c_b or their side subtrees. Let U be the members outside c_a's subtree and D those inside c_b's subtree. Let M
be the realisable relation of (α, β), the port states of c_a and c_b, as in Lemma G2 of CARRY-BOUND. Let T be the main ports carried
from c_a to c_b by identity, so that α and β agree on T's coordinates. **Conditional rectangularity** of v: for every value t of T,
the slice M_t = {(α, β) ∈ M : α|T = t} is a product A_t × B_t.

**Claim 1′.** If T ⊆ W, then U = T or D = ∅.

*Proof.* T ⊆ U, since main's ports lie outside every subtree. For each value t of T, the projection of W restricted to t is
U_t × D_t. Here U_t is the set of states of U with T = t that extend to some α ∈ A_t, and D_t is the set of states of D compatible
with some β ∈ B_t; both are read through c_a's and c_b's ports, and the slice is a product. Suppose U ≠ T and D ≠ ∅.
- T ∪ D is a proper subset of W, so it is shattered. Hence D_t is everything for each t.
- Then the projection of W is ∪_t U_t × everything, which is (projection of U) × everything. U is a proper subset, so it is
  shattered, and W is shattered: a contradiction. ∎

**Claim 2′ (first part).** If W hides the carried coordinates T∖W, h of them, then for each value of T ∩ W the projection of W is a
union of at most 2^h products across the stretch. *Proof:* split M by the 2^h values of the hidden coordinates and apply the
slice product to each. ∎

*Claim 2′ (second part), not proved here.* The advisor's further claim, that W then has at most 2^h clusters separated by
member-free stretches, needs an argument for three or more clusters reading the same hidden values. It is left open.

## The dichotomy: a conjecture

*Conjecture.* Under C′'s hypothesis, on each residue of s, L(s) is bounded or at least linear in s.

*What is proved.* By Claim 1′, a bond holding every carried top port that crosses a long member-free stretch has all its other
members on one side of it. So such a bond is p's carried set plus one local cluster.

*The gap.* A bond hiding some carried coordinates may combine several clusters through the hidden values. A cluster's span in depth,
and the stretches between clusters, are not bounded by the argument above. So sublinear growth, with a slowly widening cluster, is
not excluded. Closing it needs either the cluster bound (Claim 2′'s second part) together with a bound on a cluster's span by its
finite state, or a counterexample.

## Use

Theorems R and R1 hold for every living census-grammar family, with no census input. The census checks of
`READ-RULE-20261114-001B` measure their coverage, and the advisor's family tests the converse.
