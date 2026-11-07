# Hidden points and the two-bit screening lemma

Status: Proved (items 1 to 3: the closure as a tetrahedron rule, the Fano side's facts by exhaustion, and the no-loss theorem; the
reduction in item 4); items 4 and 5 are otherwise exact computations, and the pendant-line statement is a conjecture

Ticket `TWO-BIT-SCREEN-20261105-001A`, 2026-11-05.

## Question

- **Background.**
  - **One bit (HANDLE-LOCALITY B).** A side that forces its three ports onto one antipodal pair acts as a point for creation. This is
    proved.
  - **Two bits.** A side split from a knot space at a point passes its line's six patterns. It acts as that line for solutions, and
    HANDLE-LOCALITY found that it seemed to act as the line for creation too. This was left unexplained.
  - **Why it matters.** BRACE-TREE needs it to turn its dictionary into theorems. Every receiving atom met on the way to a line is a
    side of this kind.
- **The question.** Does an intact side attached at a line act as that line for creation?

## Dependencies

- **`HANDLE-LOCALITY-20261103-001B`.** The join method, the creation map and the one-bit screening lemma.
- **`HANDLE-EMERGENCE-20261102-001B`.** Port sets, the join lemma, and the locality of three-point knots.
- **`SPLICE-TREE-20261102-001C`.** Tie classes, the elimination closure and the size lemma (`elim_lib.py`).
- **`NATIVE-GENUS-20261104-001A`.** Spaces, atoms and splices (`genus_lib.py`).
- **`BRACE-TREE-20261105-001Z`.** The dictionary this ticket serves.

## Setting

- **Near side.** A complement-closed set of assignments on the near points: the solutions of a space minus the removal M. The gluing
  line ℓ is kept; its points are Y.
- **Splice.** ℓ is spliced into one of the four census far sides (K4^(3), census 6, the Fano plane, census 58). The far side is split at
  a point and admits exactly ℓ's six patterns.
- **Knots.**
  - **Ties and knots.** Minimal constrained sets of at most three points are computed. Two-point ones are ties, points are replaced by
    their tie classes, and knots are triples of classes.
  - **Crossing knots.** A knot is crossing when it meets the far points and a near point off ℓ.
  - **Base and new knots.** The base is the set of non-crossing knots. A crossing knot is new when it lies outside the elimination
    closure of the base.
- **Creation.** Creation at (M, ℓ) means some new knot exists for some far side.
- **The receiving side.**
  - **The Fano side.** R is the Fano plane split at a point. Its three cut lines carry the ports X instead of the point, and its
    hidden points B are the other six points.
  - **The two spaces.** S is a space with an intact Fano side at its line L0 = X. N̂ is the same space with L0 restored.
  - **W.** W is every point that is not hidden.
- **The two-bit screening lemma (strong form).** For every removal and gluing line outside R and every far side:
  - **(i) Off the side.** The new knots that avoid the hidden points are those of N̂.
  - **(ii) Through the side.** A new knot through a hidden point occurs only where N̂ has a new knot.

  Together, (i) and (ii) make creation in S the same as creation in N̂.

## 1. The closure is a tetrahedron rule (proved)

**The elimination closure of the base is the least set of class triples containing the base in which every four classes with two
triples in the set have every knot triple in the set.**

*Proof.*
- **The closure's rule is a four-set rule.**
  - The closure adds a triple T when two members A, B through a class h ∉ T satisfy A ∪ B = T ∪ {h}.
  - Knots have three classes, so A and B are triples of the four-set Q = T ∪ {h} through h, and T is Q's triple avoiding h.
- **Each step of the rule is a closure step.** Two triples of a four-set always share two classes, a and b.
  - Each of the other triples avoids one of them.
  - The triple avoiding a is produced with h = a, and the triple avoiding b with h = b. ∎

**Check 1.** The two closures agree on all 512 census splices.

## 2. The Fano side (exhaustive)

The Fano plane was split at each of its seven points.
- **(a) The ports.** They show the six non-constant patterns.
- **(b) One hidden point.** Each hidden point b is forced on exactly two patterns, a complementary pair whose odd port is the port on
  b's cut line. On them, b takes the ports' majority value. It is free on the other four.
  - **Notation.** ξ_b(β) is the one pattern that forbids b = β.
  - **The cut line's class.** κ(b) is the antipodal class of patterns whose odd port is on b's cut line.
- **(c) Two hidden points.** Each value pair of two hidden points forbids one of these:
  - a subcube (one port fixed: 3 patterns; or two ports fixed unequal: 2 patterns);
  - the antipodal class κ, and only when the two points lie on one cut line;
  - nothing.

**Check 2.** Observed exclusion types over the 7 × 15 pairs and 4 value pairs:

| Exclusion type | Points on one cut line | Other pairs |
| --- | --- | --- |
| Antipodal class | 42 | 0 |
| Subcube of 3 patterns | 42 | 168 |
| Subcube of 2 patterns | 0 | 168 |

## 3. No loss (proved)

**Theorem.** For every removal M and gluing line ℓ outside R, and every far side, the following hold.
- **(i) Off the side.** A triple of classes that avoids the hidden classes is generated in S iff it is generated in N̂. So the new
  knots off the side are exactly those of N̂.
- **(ii) Shadows.** If a crossing knot {b, p, q} through one hidden class is generated in S, then each of its port shadows {x, p, q}
  is generated in N̂. A port shadow takes x to be a port class other than the classes of p and q, and it must be a knot.
- **(iii) Two hidden classes.** No crossing knot meets two hidden classes.
- **Consequence.** Creation in N̂ implies creation in S: an intact Fano side never removes creation.

*Hidden classes.*
- **Definition.** A hidden class is a tie class made only of hidden points. Hidden points tied to a point of W are counted with W.
- **Same knots off the side.** The solutions of S project onto those of N̂, because R shows exactly L0's six patterns. So S and N̂ have
  the same ties and knots among W.

*Lemma A (knots through hidden classes).*
- **The join.** Write m_W(u) for the port patterns that solutions of N̂ show together with u, and m_R(v) for those that R's solutions
  show together with v. Then an assignment (u, v) occurs in S iff m_W(u) ∩ m_R(v) ≠ ∅.
- **(a) One hidden class.** A triple {b, p, q}, with b hidden and p, q in W, is a knot iff some values π, κ satisfy
  m_W(π, κ) = {ξ_b(β)}.
  - Indeed, b = β is excluded iff m_W(π, κ) ⊆ {ξ_b(β)}, by 2(b), and m_W(π, κ) ≠ ∅ because the pair {p, q} is free.
  - Then each port x is forced by (π, κ). So {x, p, q} is a knot whenever x's class differs from p's and q's.
- **(b) Two hidden classes.** Let K = {b, b', w} be a knot with two hidden classes. If w's class holds a near point, K has a
  non-crossing representative and lies in the base. Otherwise w's class is far only. Let E be the set that K's excluded value pair
  forbids. By complement symmetry, m_W(w = ω) ⊆ E and m_W(w = ¬ω) ⊆ ¬E.
  - **E a subcube.** It fixes a port x_m, so w is tied to x_m. That contradicts "far only".
  - **E the class κ of b and b''s cut line.** Then the ports show only κ, so b equals the ports' majority and is tied to a port. That
    contradicts "hidden".
  - **Three hidden classes.** Such a knot holds no far point, so it is in the base.

*Proof of the theorem.*
- **The candidate set 𝒮.** Let 𝒮 be the union of three sets:
  - the closure of N̂ (on W);
  - every base triple of S through a hidden class;
  - every knot {b, p, q} through one hidden class whose port shadows (Lemma A(a)) are all in N̂'s closure.
- **What remains.** 𝒮 contains S's base. It is enough to show that 𝒮 is closed under the tetrahedron rule. Then S's closure lies in
  𝒮, which gives (i) and (ii); and (iii) is Lemma A(b).
- **The cases.** Let Q be four classes with two triples G1, G2 in 𝒮, and F a knot triple of Q outside S's base.
  - **No hidden class.** The rule in N̂ applies directly.
  - **One hidden class b, Q = {b, w1, w2, w3}.**
    - **F = {w1, w2, w3}, from G1 = {b, w1, w2} and G2 = {b, w1, w3}.** Both pin the ports to one pattern (Lemma A(a)). Take a port
      class x outside the classes of w1, w2, w3. The shadows {x, w1, w2} and {x, w1, w3} are knots of N̂'s closure. So the
      four-set {x, w1, w2, w3} gives F in N̂.
      - **No port class outside.** If the ports form three classes, F is the class set of L0, which is in the base. If they form two
        classes, one of G1, G2 has the remaining port class as a shadow port, and that shadow is F. They cannot form a single class:
        then every hidden point is tied to a port or free of the ports, so no G1 exists.
    - **F = {b, w2, w3}, from the same G1 and G2.** Each shadow {x, w2, w3} comes from the four-set {x, w1, w2, w3} in N̂. When x is
      w1's class, the shadow is {w1, w2, w3}, which the previous case gives.
    - **F = {b, w1, w2}, from G1 = {b, w1, w3} and G2 = {w1, w2, w3}.** Each shadow {x, w1, w2} comes from the four-set
      {x, w1, w2, w3}, using G1's shadow {x, w1, w3} and G2. When x is w3's class, the shadow is G2 itself.
  - **Two hidden classes b, b', Q = {b, b', w1, w2}.**
    - **Shadows depend only on the visible pair.** A knot {b', w1, w2} has the same port shadows {x, w1, w2} as {b, w1, w2}. So it is
      in 𝒮 whenever {b, w1, w2} is.
    - **The other triples.** Triples with two hidden classes are in the base (Lemma A(b)). If both G's are such triples, w1 and w2 are
      near and F is in the base.
  - **Three or four hidden classes.** Every knot triple of Q has two hidden classes and is in the base. ∎

**The same proof for a pendant line.** Take one new point b on one new not-all-equal line through two near points s and u. Then b is
forced exactly when s and u agree, as literals, on the line's value. That is one pattern of (s, u). Lemma A(a) and the proof hold with
the ports replaced by {s, u}. There is one hidden class, so Lemma A(b) is not needed.

**Checks.**
- **Check 3.** On every census near side, at every line L0 and every port permutation, and on larger near sides (28,288 cases):
  - the new knots off the side equal N̂'s;
  - all 189,540 generated crossing knots through a hidden class have every shadow generated;
  - no crossing class meets two hidden classes.
- **Check 4.** The pendant half holds on all 117,344 cases.

## 4. The lifting half (computed; stated as a conjecture)

**Conjecture (lifting).** If a crossing knot through a hidden class of an intact Fano side is new, then N̂ has a new knot. In fact
every one of its port shadows is new.
- **For pendant lines.** The same is conjectured.
- **What it would give.** With the theorem above, it would make creation in S exactly creation in N̂: the two-bit screening lemma.

**Reduction (proved): the lemma for Fano sides follows from the pendant-line statement.** That statement is: one new point on one
new not-all-equal line through two near points never adds creation.

*Proof.*
- **The hidden point alone is a pendant point.** Keep one hidden point b of the Fano side and project the others away. By 2(b), b is
  forbidden a value exactly when the two ports off its cut line are equal; L0 then fixes the third port. So the projection of S onto
  W ∪ {b} is N̂ with one new point on one new line through those two ports.
- **Suppose N̂ creates nothing.**
  - By the theorem, every crossing knot of S off the side is generated.
  - By Lemma A(b), every crossing knot through the side meets one hidden class, say {b, p, q}.
  - If the pendant-line statement holds, the pendant system creates nothing. So {b, p, q} is generated there.
- **That derivation is one in S.** The pendant system's knots and base are S's knots and base among W ∪ {b}. ∎

**The bound is sharp.** One new line is the most a hidden point may carry:
- **Two lines.** A point forced on two of a line's antipodal classes to the same side is a point on two new lines through pairs of
  the line's points. This is the profile (majority, majority, free).
- **Three lines.** The ports' majority is a point on three such lines.
- **Both create where the space without them does not** (check 5).

**Evidence.**

| Family | Cases | Creation unchanged | Notes |
| --- | --- | --- | --- |
| Fano sides on census and larger near sides (check 3b) | 28,288 | all | All 10,882 new knots through a hidden class have every shadow new. |
| Census 58, 14 and 38 split at a point (check 3c) | 3,360 | all | 10,591 crossing classes meet two hidden classes, yet nothing changes. |
| Pendant lines: census near sides, every pendant (check 4) | 39,744 | all | |
| Pendant lines: larger near sides, sampled | 13,200 | all | |
| Pendant lines: 1,500 random signed systems of 7–10 points | 64,400 | all | |

**What lifting is not.**
- **Not local (check 6).**
  - **Generated knots are local.** Every generated crossing knot through a hidden Fano point (11,384) is derived inside the knot, the
    ports and the gluing line.
  - **Some new ones are not.** 320 new ones are not derived there even when every other knot there is seeded.
  - **So a proof must use more than the neighbourhood.** Such a configuration inside a space without creation would need help from
    elsewhere.
- **Not a consequence of the knots alone (check 6b).**
  - **The test.** Seed every knot off a pendant point, and every knot through it without a far point. The closure still misses 42
    crossing knots through the point.
  - **Each miss sits where the side without the point creates.**
  - **So the conjecture is a statement about which knots the base generates, not about the knot hypergraph.**
- **Not the twin statement (check 6c).** Take an assignment to two classes that forces two other classes. The two knots it makes do
  not always share their status: 434 of 67,702 such pairs differ. So the shadows of a knot are not interchangeable in general.
- **The gluing line suffices (check 7, computed).** Eliminating only through classes of ℓ's points generates every crossing class that
  the full closure generates: 9,225 of 9,225.

## 5. What a side must not encode (computed)

- **One hidden point, all 27 profiles (check 5).**
  - **The profiles.** On each antipodal class of a line's patterns, the point is free, equal to the majority, or equal to the
    minority. Each profile was tested on four bases at two lines.
  - **Which change creation.** Creation changes for exactly the 8 profiles whose exclusion sets are not subcubes. These are the
    majority and minority of the ports, and copies of one port that are free on that port's own class.
  - **The 19 subcube profiles never change it.**
  - **New knots off the point never change, in any profile.**
- **Two hidden points (check 5b).** Up to symmetry, there are 390 gadgets per base whose single points have subcube exclusions.
  - **Some change creation.** 89 do on census 58 and 126 on census 38.
  - **None of the Fano side's kind does.** Of the gadgets whose value pairs forbid only subcubes or antipodal classes, none changes
    creation (196 tested).
- **Knot-space sides (check 8).** Every knot space tried, split at any point, gives every hidden point subcube exclusions. The spaces
  tried are the census, three prisms, and every three-fold space up to 22 points. None encodes a majority or a parity of its ports.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Elimination closure = tetrahedron rule | 512 splices equal |
| 2 | The Fano side's facts | as in item 2 |
| 3 | No-loss theorem, checked | 28,288 cases |
| 3b | Lifting for Fano sides (computed) | 28,288 cases, creation unchanged |
| 3c | Other receiving sides (computed) | 3,360 cases, unchanged |
| 4 | Pendant lines | 117,344 cases unchanged |
| 5, 5b | Gadgets that encode | 8 of 27 one-point profiles change creation; two-point condition |
| 6, 6b, 6c | What lifting is not | 320 non-local; 42 misses, all where the closed side creates; 434 twin pairs differ |
| 7 | The gluing line suffices | 9,225 of 9,225 |
| 8 | Knot-space sides have subcube exclusions | census, three prisms and the 32 three-fold classes up to 22 points: no other kind (three-fold: 11,544 one-pattern, 204 two-pattern, 702 tied, 10,854 free) |

## What this does not establish

- **The lifting half.** It is a conjecture, reduced to the pendant-line statement. Without it, an intact Fano side is known not to
  remove creation, but not known not to add it.
- **Other sides.**
  - **Census 58.** Its side has crossing classes through two hidden classes. The theorem is proved only for sides whose hidden points
    each exclude one pattern and whose pairs forbid only subcubes or one cut line's class.
  - **Plane pieces.** Sides whose points fix two ports are not covered by the proof as written.
- **Larger knots.** Everything concerns knots of at most three points, as the creation map does.

## Novelty

- **New here.**
  - The tetrahedron form of the closure, used as a proof tool.
  - The no-loss theorem and its shadow argument.
  - The classification of what a hidden point may encode.
  - The pendant-line statement, the reduction of the side's lemma to it, and its sharpness (two new lines can create).
  - The reformulations of the conjecture.
- **Classical analogue.**
  - The tetrahedron rule is a bootstrap closure on a 3-uniform hypergraph.
  - The no-loss argument resembles extending a matroid by an element in the closure of others, where circuits through the new element
    reduce to circuits through the old ones.
  - Neither is known to us in this form.
