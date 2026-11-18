<!-- modelUsage: claude-fable-5-2 -->

Not ready to freeze as worded: the pilot cannot tell the sum form from its two rivals, and the counts are off by two (11,621 − 11,476 = 145, not 147), which needs reconciling first. I reasoned from your summary only and did not open the census files.

**(1) Form.** Sum is the right one to freeze, but it is so far untested against the alternatives.

- **Three forms fit every observed case** (1+1→2, 2+1→3, [[1,1],[1]]→2):
  - (a) the sum of the class sizes in a component;
  - (b) largest + (number of linked classes − 1);
  - (c) largest + 1 if any link exists.
- **Where they differ:** (a) and (b) differ only when a non-largest class has size ≥ 2 (linked 2+2 gives 4 against 3). (b) and (c) differ only at three or more linked classes.
- **Why sum mechanically:** a sibling class of two is already "two births whose partners are candidates of each other". So class and link are one relation on births: partners equal or mutually candidates. The dimension is then the largest set of births related this way, and each birth contributes one chain direction. Chains through related partners join each other, so counts multiply and degrees add; unrelated chains add, giving the max.
- **Suggested restatement:** freeze it as a rule on births rather than on classes. Forms (b) and (c) have no such reading.
- **Fix one wording:** "partners are candidates of each other" and "share a neighbour" may not be the same thing (live or not, same round or not).

**(2) Where it could fail.**

- **Component against clique.** Commuting is pairwise, so a path A–B–C with A and C unlinked may give 2, not 3. This is the likeliest failure.
- **Linked 2+2 or 3+1.** A cap could apply; did anything in the census exceed dimension 3? The sum would overshoot, and so would any case where a link is used up by the first joining under the complete-round rule, which would favour (c).
- **Cross-round links.** A one-round stagger should not change the degree of a product, so I expect the same-round restriction to undercount. That only 147 exceptions exist suggests such cases are rare at five knots, not that they are absent.
- **False positives.** Eight matches out of 11,476 is thin. A linked pair with dimension equal to the largest class kills the rule.
- **Exponential rings.** Exclude them explicitly; they have no dimension.

**Before freezing** (this is fitting, so label it that way): run the link test over all growing arrangements at up to five knots, and report three things.

1. Any linked match (a false positive).
2. Any unlinked exception.
3. Any component of shape 2+2, of three or more classes, or a path. If one exists with only +1, the sum is already dead.

**(3) Predictions to freeze.**

- **P1, six-knot sample.** Among settled polynomial arrangements with a birth, dimension = largest related set of births, with zero false positives. The excess over the largest class is ≥ 2 exactly when a component has three or more classes or a non-largest class of size ≥ 2.
- **P2, constructed.** The sample may contain neither shape, so build them by hand:
  - a linked 2+2, predicted 4 (forms (b) and (c) say 3);
  - three mutually linked single classes, predicted 3 (form (c) says 2);
  - a path of three, frozen with a stated guess. Mine is 2, which makes the rule clique, not component.
- **P3, separate clause.** Cross-round candidate partners do not add. I would bet against this, so keep it separable, so that its failure narrows the rule without overturning it.