# What the far-pair sign decides, and where it stops

Status: Proved (L1 to L6 and Proposition 7); the equivalence on SEEDK's own fills is not proved here (see "Not proved")

Ticket `FAR-SIGN-20261118-001A`, 18 November 2026, by Claude, written before ticket B's freeze. It takes up
`COPY-CLASS-20261118-001`'s referee finding, "a crossing-making fill is a copy step exactly when its far end pair is separated by every
crossed split", and asks how much of it is a theorem.

## Setting

- A **base** is a set of distinctions with its allowed states (0/1 assignments, closed under complement, the two constant states
  included). A **split** is a nonconstant state taken with its complement. Two splits **cross** when all four of their quadrants hold
  a distinction. A split is **crossed** when it crosses some split of the base.
- A **fill** adds one distinction r, whose value on every old state is fixed by a set of knots on r (no state is added, and r is not a
  copy of an old distinction). Two old splits that did not cross **come to cross** when r lands in their empty quadrant.
- **SEED's clauses** (after its switch): (a) no two crossed splits come to cross; (b) every uncrossed split that gains crossings ends
  with exactly the crossers, after the fill, of some crossed split (its **model**). A **copy step** is a crossing-making fill that
  passes both.
- The knot sets in question have three knots on r, written as in `COPY-CLASS-20261118-001`:
  - a **middle knot** B(p, r, q), which pins r to p where p = q;
  - a **near end knot** B(a, p, r), whose pair {a, p} shares exactly p with the middle pair, and which pins r to p where a ≠ p;
  - a **far end knot** B(c, d, r), whose pair {c, d} is disjoint from the middle pair, and which pins r to d where c ≠ d.

  On SEEDK's runs every copy step has such a knot set, and every crossing-making knot set of this shape has its near knot pinning r to
  the shared distinction (computed; ticket B scores both). The other orientation of the near knot is not treated here.
- **The sign:** every crossed split separates c from d.
- For a split σ write P(σ) for its side holding p. Call σ **moved** when r lands off P(σ), and write M for the set of moved splits.

## L1. The moved splits

**Claim.** σ is moved exactly when a ∈ P(σ), q ∉ P(σ) and d ∉ P(σ). Zero cost forces two more facts:
- (i) every split σ with a ∈ P(σ) and q ∉ P(σ) separates c from d;
- (ii) every other split that separates c from d has d ∈ P(σ).

On a moved split, c ∈ P(σ).

**Proof.** Take the state s whose 1-side is P(σ), so s_p = 1.
- If q ∈ P(σ), the middle knot pins r to s_p = 1: unmoved.
- If a ∉ P(σ), the near knot pins r to s_p = 1: unmoved.
- Otherwise (a ∈ P(σ), q ∉ P(σ)) neither of those knots pins s. The knot set fixes r on every state, so the far knot must: s_c ≠ s_d,
  which is (i), and r takes s_d. So σ is moved exactly when s_d = 0, that is, d ∉ P(σ); then s_c = 1.
- For (ii): if σ separates c from d but is not of (i)'s kind, the far knot and the middle or near knot both pin s, to s_d and to 1.
  They agree, so s_d = 1. ∎

## L2. The new crossings

**Claim.** Two old splits σ, τ that did not cross come to cross exactly when one of them, say σ, is moved, the other is not, and
P(τ) ⊊ P(σ).

**Proof.** r lands in the quadrant cut out by its own sides of σ and τ.
- Neither moved: r lands in P(σ) ∩ P(τ), which holds p, so no new crossing.
- Both moved: r lands outside both, where q lies (L1: q ∉ P on a moved split), so no new crossing.
- σ moved, τ not: r lands in P(τ) minus P(σ), which is empty exactly when P(τ) ⊆ P(σ). Different splits with p on the same side
  cannot have equal sides there, so the inclusion is strict. Two splits with P(τ) ⊊ P(σ) do not cross before. ∎

## L3. Who gains

Let G be the set of uncrossed splits τ with a ∉ P(τ) and q ∉ P(τ).

**Claim.** Every split of G is unmoved and comes to cross every moved split. Every unmoved split that comes to cross something has
a, q and d off its p-side.

**Proof.**
- A split of G has a ∉ P(τ), so it is unmoved by L1.
- Take a moved σ. P(τ) ∩ P(σ) holds p. P(σ) minus P(τ) holds a. The outside of both holds q.
- τ crosses nothing, so the fourth quadrant, P(τ) minus P(σ), is empty: P(τ) ⊊ P(σ), and by L2 they come to cross.
- For the second sentence, L2 gives P(τ) ⊊ P(σ) for a moved σ, so q, d ∉ P(τ); and a ∉ P(τ), or τ would be moved by L1. ∎

## L4. What the sign does

Assume the sign.

**(a) holds** (the referee's half, restated).
- An unmoved split that separates c from d has d on p's side, by L1 (i) and (ii). A moved split has d off it.
- So by L2 an unmoved split separating c from d never comes to cross a moved one.
- Every crossed split separates c from d, so no unmoved crossed split comes to cross a moved split. Two moved splits, or two unmoved
  ones, never come to cross (L2). ∎

**The new crossings are exactly G × M.**
- An unmoved τ that comes to cross a moved σ has d ∉ P(τ) (L3). So it does not separate c from d, since otherwise d would be on its
  p-side.
- By the sign τ is then uncrossed, and by L3 it lies in G.
- Conversely every split of G comes to cross every moved split (L3). ∎

**r sides with d on every crossed split.**
- A moved crossed split has r and d both off P.
- An unmoved crossed split separates c from d, so it has d on P (L1), where r also is. ∎

## L5. The theorem under the sign

**Theorem.** Assume the sign, and that the fill makes a new crossing. Then it is a copy step exactly when:
- **(T1)** no uncrossed split is moved, and
- **(T2)** M equals the crossers of some unmoved crossed split.

On a base of two orders this reads: the moved splits are exactly one whole order. Here a base of two orders means that its crossed
splits fall into two classes, with no two of one class crossing and every split of one crossing every split of the other.

**Proof.**
- By L4 clause (a) holds, and the new crossings are G × M, with G and M nonempty.
- The splits that gain are G and the uncrossed moved splits.
  - A split of G ends with crossers M.
  - An uncrossed moved split u ends with crossers G, none of which crossed anything before the fill.
  - A crossed split ends with its old crossers, which are crossed, and perhaps more.
  - So u has no model, and (b) needs (T1).
- Under (T1), M holds only crossed splits.
  - A moved crossed split ends with crossers that include G, which holds uncrossed splits, while M holds none. So it is not a model.
  - An unmoved crossed split gains nothing (L4, (a)'s proof), so it ends with its old crossers.
  - Hence a split of G has a model exactly when (T2) holds.
- On a base of two orders, a crossed split's crossers are the other whole order.
  - If M is one whole order, every split of the other order is unmoved and is a model.
  - Conversely M = C(m) is the order not holding m. ∎

## L6. A pair pattern that gives the copy step

**Claim (base of two orders).** Suppose:
- every crossed split separates p from q;
- no crossed split separates a from p;
- some crossed split separates p from d, and some does not.

Then the sign holds and (T1) and (T2) hold. So the fill, if it makes a new crossing, is a copy step.

**Proof.**
- Every crossed split has a ∈ P and q ∉ P, so by L1 (i) it separates c from d: this is the sign.
- A crossed split is moved exactly when d ∉ P, that is, when it separates p from d.
- A moved crossed split σ and an unmoved crossed split τ cross. P(σ) holds p, a, c and not q, d; P(τ) holds p, a, d and not q, c.
  So their four quadrants hold p, c, d and q.
- So every moved crossed split crosses every unmoved crossed split, and both kinds occur.
  - Two moved splits in different orders would cross each other and both cross an unmoved one. That is three pairwise crossing splits,
    impossible in two orders.
  - So the moved crossed splits lie in one order, the unmoved in the other, and every crossed split is one or the other. The moved
    crossed splits are therefore one whole order.
- An uncrossed moved split u would have P(u) holding p, a, c and not q, d. The same four quadrants against an unmoved crossed split
  would make them cross. So there is none: (T1).
- L5 gives the copy step. ∎

**The sign in betweenness.** Say x lies between c and d over a set F of splits when no split of F has c and d on one side and x on
the other. Then the sign holds exactly when every distinction lies between c and d over the crossed splits.
- **Proof.** If a crossed split has c and d on one side, its other side holds some distinction (splits are nonconstant). ∎
- **What it means.** The betweenness the states imply is taken over all splits, crossed or not. COPY-READ's closure picture is that
  betweenness among the move's own distinctions. A reading of the sign must tell crossed splits from uncrossed ones, and the closure
  picture does not. Ticket B checks this both ways: the plain picture, and the picture with one mark for crossed per split.

## Proposition 7. Neither direction is a theorem of the fill and the base's two orders

**The base.** Take seven distinctions. Six of them are the product of a chain of two and a chain of three:
- 0 = (0, 0), 1 = (0, 1), 2 = (0, 2), 3 = (1, 0), 4 = (1, 1), 5 = (1, 2);
- 6 hangs on 1.

Its states are the constant states and both sides of four splits:
- σ_X = {3, 4, 5} | rest;
- σ_0 = {0, 3} | rest;
- σ_2 = {2, 5} | rest;
- τ = {6} | rest.

These are exactly the states allowed by the betweenness knots the base implies (ticket B's checks confirm it).
- σ_X crosses σ_0 and σ_2, and τ crosses nothing.
- So the crossed splits form two orders, {σ_X} and {σ_0, σ_2}.

**(A) The sign without the copy step.**
- Knot set: B(3, r, 6), B(1, 6, r), B(5, 0, r). Its roles are p = 6, q = 3, a = 1, c = 5, d = 0.
- The sign holds:
  - σ_X separates 5 from 0;
  - σ_0 separates 0 from 5;
  - σ_2 separates 5 from 0.
- Moved splits (L1: 1 ∈ P, 3 ∉ P, 0 ∉ P): only σ_0. So M = {σ_0}, which is not a whole order.
- So τ comes to cross σ_0 alone. No crossed split has crossers {σ_0}: σ_X has two, and σ_0 and σ_2 have {σ_X}.
- SEED refuses (clause (b), a strict subset).
- L5's (T2) fails, as the theorem says it must.

**(B) The copy step without the sign.**
- Knot set: B(3, r, 6), B(0, 6, r), B(0, 4, r). Its roles are p = 6, q = 3, a = 0, c = 0, d = 4.
- The moved splits are σ_X alone, a whole order.
- τ comes to cross σ_X. Then τ's crossers are {σ_X}, which are σ_0's crossers, so SEED accepts.
- But σ_2 = {2, 5} | rest has 0 and 4 on one side: the sign fails.
- No other knot set of this fill of the same shape has the sign (ticket B's checks list them all).
- This copy step also makes a third order. After it, τ, σ_0 and σ_2 each cross σ_X, but none of the three is nested in another, and
  the lattice dimension is 3 (computed in the checks). So off SEEDK's own bases, SEED's two clauses do not keep two orders either.

**So neither half of "sign ⟺ copy step" follows from the fill's knots and the base's two orders.**
- A's lemmas reduce the question to (T1) and (T2) under the sign, and to the converse: does every copy step have the sign?
- Both can fail when the three knots sit on pairs that SEEDK's growth would not have co-knotted.
- Any proof on SEEDK must therefore use which pairs its history has put in a common knot.

## Not proved

On SEEDK's knot-local fills, the following three statements; ticket B scores each on fresh runs.
- **F1:** a crossing-making fill that gives an uncrossed split a crossing has the sign.
  - It gives the converse. A copy step passes (a), so some uncrossed split gains.
- **T1** and **T2** under the sign.
  - They give "sign ⇒ copy step" through L5.

L6's pattern is a sufficient condition proved on any base of two orders. Whether it is also necessary on SEEDK is computed, not
proved.

## Sources

Split systems, compatibility and crossing are standard: Bandelt and Dress (1992), and Eppstein (2005) for the lattice dimension of
partial cubes. A base presented by all its implied betweenness knots, with half-spaces as states, is the half-space system of a median
graph. What this adds:
- L1 to L6, which reduce SEED's copy step under the sign to one set comparison: the moved splits against the crossers of one split,
  that is, against one whole order;
- the pair pattern that forces it;
- two seven-distinction counterexamples showing the equivalence is a property of SEEDK's knot-local growth, not of the fill's shape.

The advisor was consulted before this proof was frozen. It re-derived L1 to L3 and gave L4's "G × M" form and "r sides with d". It
also proposed scoring F1, T1 and T2 separately, and the marked five-distinction picture.
