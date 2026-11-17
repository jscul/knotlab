**(a) Exactness.** A found bond is sound, but a null is weaker than it looks, and the mode-bond step has two gaps.

- **Soundness:** truncation is exact because F = all, and the same composite gives the same projection at s + 2k. Do confirm that L0 = 5 is on the periodic part and not the last transient length; if "threshold 5" means lengths > 5, use 6 and 7.
- **Missing type:** the incompatible pairs (U above, W below) for your composite are three, not two. The third is U = {0000, 1111}, W = non-constant: the part above forces only "X constant", and two unequal addresses sit in V. The generic search covers it, but any growth-side product test must include it.
- **Lower part too narrow:** restricting it to V misses members in V's children or side leaves that force z ∈ P or z non-constant more cheaply or differently. Keep one or two levels below V and admit members there.
- **Upper part too narrow:** excluding members on the path's side children and first few type-7 levels below X is the main hole, as (c) shows.
- **The "iff":** given the dichotomy, bounded ⇒ a long member-free window by pigeonhole ⇒ a type-7 crossing, since everything else is a product. That direction is right, but it inherits the unrefereed dichotomy, so label it conditional.

**(b) Expectation.** I expect no mode bond, at roughly 70–75%, with L = 3 + ⌈s/2⌉ continuing (8 at s = 9, 10).

- The certified L(7) = L(8) = 7 already excludes every mode bond of size ≤ 6 with a − 3 + L0 ∈ {7, 8}. So the new test only probes size ≥ 7 and a = 6.
- The stem null already covers the natural gadget: Y at level 3, on-path members, V.
- Structurally, product from parent to line means no parent state alone selects a class, so a gadget needs extra members that make the parent state and the class dependent.
- The residual risk is entirely off-path: X's type-6 sibling subtree and the side type-7 children.

**(c) Finite argument.** It is sound in spirit, but the framing "the top's reach to that block grows" is wrong, and yes, the bond's own members near X break the naive product step.

- **Where the question lives:** type 7 is entered only from types 4 and 5, and neither occurs below a type 7. Type 4 sits at level 3 and type 5 at level 4, so reaching Y costs nothing. Growth must come from there being no local gadget.
- **What the product covers:** only the undecorated composite. Members σ at X, its sibling, or side children can make the conditional relation between Y's state and the class non-product.
- **Exact criterion for Y at level 3:** the reach is bounded iff some σ strictly below Y, plus a lower part, is satisfiable yet excludes some Y-state. Then Y's addresses set to an excluded state complete the bond, and at least one of them is needed.
- **Making it finite:** saturate the set of decorated relations R_σ ⊆ states(Y) × states(X′) under composition of decorated segments. This is a finite monoid closure, since size is irrelevant to existence. Over-approximate the side subtrees by allowing arbitrary restrictions on each side orbit's state. If no saturated relation, composed with the long composite, is satisfiable and incompatible with some Y-state against any of the three (U, W) pairs, growth is proved, conditional on the dichotomy.
- **Type 5:** Y is at level 4, so additionally check whether the level-3 type-3 parent can force Y into the excluded set with a level-3 member needed. That is one more block.

**(d) What I would do differently.**

- Run the decorated saturation first. It is cheap on 88 states, decides both sides, and makes the a = 4, 5, 6 search a confirmation only.
- Freeze these predictions: no mode bond; L(9) = L(10) = 8; the saturation yields no dependent decorated relation for type 4. Type 5 is less certain, at about 60%.
- If a gadget does appear, expect type III with side-child members, of size 8–9.
