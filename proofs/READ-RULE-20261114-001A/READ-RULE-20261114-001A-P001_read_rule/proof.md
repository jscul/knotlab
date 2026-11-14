# The reading theorems

Status: Proved

Ticket `READ-RULE-20261114-001A`, 2026-11-14. Statements as frozen in `research/READ-RULE-20261114-001/preregistration.md`.
Theorems R and R1, Claim 1′, the first part of Claim 2′, and the dichotomy are proved below. The dichotomy is proved by pumping, the
advisor's suggestion on checking the first draft (`research/READ-RULE-20261114-001/advisor_proof_answer.md`), and needs no
rectangularity. Claim 2′'s second part is open.

## Setting and two facts

The pattern is the infinite usual-limit system of a living, complement-closed NAE family. Every knot is NAE on three distinct
positions of its block; two positions may hold the same distinction (a port passed down by identity), and the allowed set Ω is nonempty and closed under complementing every distinction. "Free" and "non-shattered" refer to
the projection of Ω.

**Fact 1 (singletons).** Every distinction takes both values: Ω is nonempty and closed under complement.

**Fact 2 (pairs).** A pair {u, v} is non-shattered exactly when it is tied. Its projection is a nonempty, complement-closed subset of
{0,1}², and the proper ones are {00, 11} and {01, 10}.

So every bond has at least two members, and a two-member bond is a tie.

## Theorem R

*Statement.* At depth s, let a covered copy c hold the main port p at position k, and let S's block have a knot {k, x, z} with x own.
Write x and z also for the distinctions of c at those places. Then L(s) ≤ 3 unless {p, x} is free and z is tied opposite to p or to
x; in that exception the proof gives no bound. (The frozen clause "L(s) ≤ 2 when {p, x} is tied" holds by Fact 2 and adds nothing.)

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

*What Claim 1′ gives.* A bond that holds every main port carried through a member-free stretch has its other members on one side of
that stretch. That needs T ⊆ W for each stretch's own T. It says nothing about how far a group of members spreads, or about side
subtrees, since rectangularity is assumed only along the target's word. (A caveat from the check: if c_a passes c_b by identity a port
that is not a main port, M_t can be a product only when that coordinate is constant on the slice.)

## The dichotomy (pumping)

*Statement.* For every living in-scope family there is a period Π such that, on each residue of s modulo Π, either L is bounded
(L(s) ≤ L(s₀) for every s ≥ s₀ in the residue, for some s₀), or L(s) ≥ s/(m + 1) − 1 for every s in the residue, with m below.
Nothing grows between bounded and linear.

*Proof.* Take the state of a word u of SELF calls to be the pair (the product of its per-call relations, its carry map from the
first copy's port positions to the last copy's). There are finitely many states, say m, counting the empty word. Let Π = m!.

Take a least bond W at depth s, with target x in copy c_s along the word v. Call a level i of v occupied when W has a member in the
block of the copy at level i or in that copy's side subtrees. A member-free stretch is a run of unoccupied levels.
- **No long stretch.** If every member-free stretch has at most m levels, then at least one level in every m + 1 is occupied, so
  |W| ≥ s/(m + 1) − 1.
- **A long stretch.** Otherwise some stretch, from copy c_a to copy c_b, has more than m levels. Among the words from c_a to the copies
  at its levels, two, ending at levels i < j, have the same state. Write the stretch's word as t₁ y t₃, with y the levels i + 1 to j,
  of length ℓ ≤ m. Since P(t₁y) = P(t₁), induction gives P(t₁yᵏ) = P(t₁) for every k, and likewise for the carry map. So the
  stretch's product P(t₁yᵏt₃) and its carry map are unchanged by pumping y.
  - Insert y another Π/ℓ times: the new word v′ is an S-word of length s + Π, so its end copy is a covered copy at depth s + Π.
  - Move each member of W to the corresponding place: the same place above the stretch, or the same place in the copies below it,
    which are copies of S with the same subtrees.
  - The realisable relation across the lengthened stretch is unchanged: it is the stretch's product, with c_a's context and c_b's
    usual limit, as in CARRY-BOUND's Lemma G2. The outside and the inside are unchanged too, and they meet the stretch only through
    its end ports. So the projection of the moved set equals W's projection, and it is a bond of the same size.
  - Hence L(s + Π) ≤ L(s), and by repetition L(s + kΠ) ≤ L(s) for every k.
- **Per residue.** On a residue of s modulo Π, if some s₀ has a least bond with a long stretch, then L(s) ≤ L(s₀) for every later s in
  the residue. Otherwise every least bond there has only short stretches, and L(s) ≥ s/(m + 1) − 1. ∎

*Remarks.*
- The members moved below the stretch stay in copies of S. Their identity with main's ports is preserved, because the carry map is
  part of the state.
- m can be large, so the linear rate this gives is weak. The gap argument gives the sharp rate where it applies.
- The same proof works for any covered target, and needs neither forgetting nor rectangularity.

## Use

Theorems R and R1 and the dichotomy hold for every living in-scope family, with no census input. So every bond to a covered
target is, per residue, eventually bounded or at least linear: the census's undecided families cannot grow slowly. The census checks of
`READ-RULE-20261114-001B` measure their coverage, and the advisor's family tests the converse.
