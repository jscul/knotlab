# Moving the ends' pair carries KF3

Ticket `MEET-TWIST-20261118-001A`, 18 November 2026, by Claude; checked by the advisor model (Fable 5.2: holds with fixes, all
folded in before the freeze). Words as in `MEET-ORDERS-20261118-001` (bracketing, odd set) and
the glossary. The map was found by computation (the advisor's twist made exact, see the decision note); the proof below was written
before the frozen check of ticket B.

## Setting

- **The cycle of a presentation.** A fewest-knot presentation of a line of n distinctions is a bracketing, the literature's
  triangulation of the n-gon with the distinctions in the line's order as its vertices and the pair of the line's two ends as its
  marked side (`MEET-ORDERS-20261118-001`, Lemma 0). Put the distinctions 0, …, m on a cycle (m = n − 1); its **steps** are the
  consecutive pairs h_0 = {m, 0} and h_k = {k − 1, k}, all co-knotted. Cutting the cycle at any step g, as the ends' pair (the **mark**), gives a
  presentation P_g of a line: the same knots (as sets of distinctions), the line running from the distinction after g round to the
  one before g. Every step works, since a triangulation with any marked side is a bracketing.
- **States.** For a step h let run_g(h) be the distinctions passed going forward round the cycle from g to h (empty when h = g).
  The states of P_g are the pairs (h, ε), h a step and ε ∈ {0, 1}, with distinction v taking ε ⊕ [v ∈ run_g(h)]: h = g gives the
  two constant states, and the other steps the cuts, with both orientations. So the states of every P_g are indexed by the same 2n
  pairs.
- **Odd sets.** While no new distinction has added a state, each distinction d (old or new) is the parity of its odd set O_d of
  old distinctions (`MEET-ORDERS-20261118-001`, parity form): d takes ε ⊕ π_g(O_d, h) at (h, ε), where π_g(X, h) = |X ∩ run_g(h)| mod 2.
  An old distinction v has O_v = {v}. For two distinctions u, v put E_uv = O_u △ O_v (an even set): they differ at (h, ε)
  exactly when π_g(E_uv, h) = 1, whatever ε. Call D_g(u, v) the steps where they differ and A_g(u, v) the others; A_g ∋ g.
- **Knots on a new distinction r and a co-knotted pair {u, v}**, for a target odd set O_r:
  - β = B(u, r, v) pins every state on the steps of A_g(u, v), and is right for O_r when π_g(O_r △ O_u, h) = 0 there;
  - γ_v = B(u, v, r) pins every state on D_g(u, v), right when π_g(O_r △ O_v, h) = 0 there;
  - γ_u = B(v, u, r) pins every state on D_g(u, v), right when π_g(O_r △ O_u, h) = 0 there.

  A knot is right for O_r exactly when its pins agree with the parity of O_r. A KF3 option that adds no state pins every state, so
  it fixes r to a function of the state, and that function is the parity of one odd set O_r: on the constant states only β knots
  pin, and they set r = u, so r is 0 on the constant state 0; every pin reads r = u or r = v, so r respects complements; so r's
  value changes along the cuts at a set of distinctions which, with the odd-size convention fixing whether the distinction just
  before g belongs (it lies in no run), is one odd set. Every knot of the option is right for that O_r. KF3 judges irredundancy on
  states (a knot is redundant when the others already pin every state it pins), so it is a statement about pinned steps. No two
  distinctions are copies (KF3 never adds one), so every E_uv is nonempty; a nonempty even set has odd
  parity on the steps between its first two members along the runs, so D_g(u, v) is nonempty for every pair.

## Lemma 1 (moving the ends' pair one step)

Let g⁺ be the step after g and w the distinction they share. For every even set E and every step h,
π_{g⁺}(E, h) = π_g(E, h) ⊕ [w ∈ E].

*Proof.* For h ∉ {g, g⁺}, run_g(h) = {w} ∪ run_{g⁺}(h). For h = g⁺, run_g(g⁺) = {w} and run_{g⁺}(g⁺) = ∅. For h = g,
run_g(g) = ∅ and run_{g⁺}(g) is every distinction but w, which meets E in |E| − [w ∈ E] ≡ [w ∈ E] distinctions, |E| being even. ∎

So D_{g⁺}(u, v) = D_g(u, v) when w ∉ E_uv, and the two swap (D_{g⁺} = A_g, A_{g⁺} = D_g) when w ∈ E_uv; and a knot's rightness
condition on a set F = O_r △ O_x flips on every step exactly when w ∈ F.

## Lemma 2 (knot by knot)

Fix O_r and a co-knotted pair {u, v}. The knots on {u, v} right for O_r under the mark g correspond one to one to those right for
O_r under g⁺, by the table below, and each knot's image pins exactly the same steps.

| Case | Knot under g | Its image under g⁺ |
| --- | --- | --- |
| w ∉ E_uv | β | β (and then w ∉ O_r △ O_u) |
| w ∉ E_uv | γ_v | γ_v if w ∉ O_r △ O_v, else γ_u |
| w ∉ E_uv | γ_u | γ_u if w ∉ O_r △ O_u, else γ_v |
| w ∈ E_uv | β | γ_u if w ∉ O_r △ O_u, else γ_v |
| w ∈ E_uv | γ_v or γ_u | β |

*Proof.*
- *w ∉ E_uv.* The pinned steps stay. β pins A_g, which holds g⁺ (π_g(E_uv, g⁺) = [w ∈ E_uv] = 0), so rightness at g⁺ under g
  gives [w ∈ O_r △ O_u] = 0, and by Lemma 1 the condition is unchanged under g⁺. A γ knot's condition on F flips exactly when
  w ∈ F; flipped, "r = v on D" becomes "r ≠ v on D", which is "r = u on D" since u ≠ v there. As w ∉ E_uv, w ∈ O_r △ O_v exactly
  when w ∈ O_r △ O_u, so the image is well defined.
- *w ∈ E_uv.* The steps A_g become the disagreement steps under g⁺ and D_g the agreement steps. β's condition "r = u on A_g"
  under g⁺ reads "r = u on D_{g⁺}" (γ_u) if w ∉ O_r △ O_u and "r ≠ u, so r = v, on D_{g⁺}" (γ_v) otherwise. A right γ_v pins
  D_g, which holds g⁺ (π_g(E_uv, g⁺) = 1), and rightness there gives w ∉ O_r △ O_v, so under g⁺ the condition "r = v on A_{g⁺}"
  is unchanged: that is β, since u = v on A_{g⁺}. The same for γ_u. At most one of γ_u, γ_v is right for O_r, since they pin
  the nonempty D_g to different values, so the map is one to one.
- *The inverse.* Moving the mark back, from g⁺ to g, past the same w, uses g as the step that witnesses rightness: π_{g⁺}(F, g) =
  [w ∈ F] by Lemma 1, and g lies in A_{g⁺} when w ∉ E_uv and in D_{g⁺} when w ∈ E_uv. The same argument then sends every right
  knot under g⁺ to a right knot under g, and the two maps undo each other. ∎

## Theorem 2 (the meeting pattern grows on its own)

For a bracketing T of the cycle and steps g, g⁺ of it, the KF3 chains from P_g and P_{g⁺}, each with its new distinctions numbered in order,
have the same law on (the family of odd sets, the co-knotted pairs) under the coupling of Lemma 2, until the first new distinction
that adds a state, and that step comes at the same point in both.

*Proof.* By induction on new distinctions. Both start from O_v = {v} and T's pairs. At a reached state described by the odd sets
and the pairs G, an option of P_g that adds no state is an irredundant set of one to three knots on co-knotted pairs, all right
for one O_r, covering every step, with O_r none of the existing odd sets. Lemma 2 sends it, knot by knot, to a set on the same
pairs with the same pinned steps, all right for O_r under g⁺: it covers every step, is irredundant (each knot pins the same steps
as before), adds no state, and makes the same new distinction O_r, not a copy. So the options that add no state correspond one to
one, with the same new pairs and the same O_r, and the inverse does the same. KF3 takes them uniformly when any exist, in both
chains at once; when none exist, both take a step that adds a state at that point. ∎

**Corollary (every pair of presentations with one meeting pattern).** A presentation is fixed by its knots as sets of
distinctions together with its ends' pair: the middles follow from the line (Lemma 0 of `MEET-ORDERS-20261118-001`). Two
presentations of a line whose knots are the same pattern up to renaming φ are P_g and P_{g′} of one bracketing of the cycle up to renaming: the co-knotted pairs form a maximal outerplanar graph (the
literature's), which has one Hamiltonian cycle (classical), so φ maps the cycle to itself, a rotation or reflection, and the presentations differ by which step is the ends' pair (a reflection needs nothing more: a line and its reverse are the same presentation, and in
the indexing reversal sends (h, ε) to (h, 1 − ε) with the odd sets unchanged). Moving the ends' pair one step at a time carries
KF3 from one to the other. So, until the first state is added, the labelled law of the co-knotted pairs is carried by one
renaming (MEET-GROW's P1), the labelled base counts agree (P3), and the joint law with every state's options (all of which add no
state in that range) is carried (P4), for every n. The states correspond by their index (h, ε), not by the renaming: the values
differ, which is why the number of orders is not carried.

**What the mark still decides: the number of orders.** The states are read from the odd sets with the mark: the line is the cycle
cut at the ends' pair. For new distinctions that are fills of triples, a fill's middle is the distinction of its triple that does not lie next to
the ends' pair along the cycle's runs between the three (the one opposite the run holding it), and Lemma C of `MEET-ORDERS-20261118-001` reads two orders from which middles lie strictly inside which fills' ends. So
the same odd sets give different numbers of orders under different marks.

## What this does not prove

- Anything after the first new distinction that adds a state. Ticket B records when that is reached in the cases it runs.
- That different meeting patterns grow differently (MEET-GROW's P2, computed).
- Other knot kinds, rules, or presentations with more knots than needed (A99, A100).

## Known mathematics, labelled

Polygon triangulations and bracketings (Catalan); the unique Hamiltonian cycle of a maximal outerplanar graph (classical); parity
(odd sets) of GF(2)-valued functions. Local: Lemmas 1 and 2 and Theorem 2 for KF3.
