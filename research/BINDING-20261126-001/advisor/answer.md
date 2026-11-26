# The advisor's answer

A colleague's view, checked before use; read in the repository. Model: claude-fable-5-2. [Question](question.md)

Everything below is a hand argument and `unverified` unless marked. I read the referee report, the decision and `binding.py`. I did not read the growth engine, and the witness file is one line too long to open, so I worked from the referee's description of the nine-knot start.

**(a) Is (1) right, and is (2) the right line?**

(1) is right, and it reaches further than you use it. At round 1 every fresh distinction has one holder (the referee: "distinct births have disjoint fresh distinctions"). So every cycle at round 1, including one "through births", is made only of old distinctions: old shared ones and old loose ones that are now parent-child. By (1), no relation among cycle parities at round 1 is new in values. What growth changes at round 1 is which old functionals are closed and are labels.

The same lag holds at every round. A birth law made at round t has loose fresh distinctions, so a relation using it can close into cycles only at round t + 1. The first relations that are new in values should appear at round 2, with K containing round-1 births.

(2) does not draw the line, because it depends on the representative:

- Suppose C1 + C2 + C3 = cut(K) with K free of loose distinctions.
- Then C3′ = C3 + cut(K) = C1 + C2 is again a sum of cycles and is the same function on every allowed state.
- With C3′ in place of C3 the relation is an identity.

Over two values, any three functions with a + b + c = 0 on the allowed states have c equal to a + b as a function; a layer-one parity knot is no different. What makes its three distinctions exist "on their own account" is that they are three different distinctions, so the criterion has to be about supports.

A cleaner criterion: a circuit of three or more carriers counts when

- the carriers have pairwise disjoint supports;
- none is read by one knot;
- no proper sub-sum lies in the span of the knot laws;
- the set K of laws summing to it contains a knot born after the start.

This amounts to: cut(K), for K with no loose distinction, splits into three or more distinction-disjoint cycles. In words, what crosses the edge of a spent set of knots sums to zero.

Two cautions:

- **Holder counts.** The cycle and cut wording needs every distinction to have at most two holders after growth. I did not check this; assert it.
- **The draft cannot show a binding.** In `binding.py`, `joint rank` (line 63) is k by construction, since a basis independent modulo the laws takes free values. The triple test (line 78) compares label codes, where `a ^ b == c` is always the defined sum.

**(b) Do I expect forced circuits after growth, and are they identities in disguise?**

Yes, I expect them, and at round 1 they are old relations re-read.

- **All old knots.** The cut of all spent old knots is the set of parent-child distinctions. It is a sum of cycles exactly when every birth holds an even number of inputs. Its relation is "the old loose distinctions sum to zero", which is the sum of all start laws and was true at the start.
- **The nine-knot witness.** For r1 + r2 + C3 to be forced, K must alternate around each ring of four (knots 0 and 2 of each), and every outside knot and birth must meet K evenly. The ninth knot meets two opposite members of ring 1 (even either way) and one member of ring 2 (odd unless the ninth is in K or that member is out). The two births with inputs from both rings decide it. I could not settle it by hand.
- **Check.** Enumerate the 512 subsets K of old knots and list those whose cut meets every knot evenly.

**(c) What goes wrong with every cycle up to a length?**

- With more cycles than the dimension of the cycle space, almost every minimal dependent set is an identity.
- The forced sets differ from identities only by an element of B, defined below.
- The length cutoff is a second scaffold on top of the move rule.

A principled replacement is one rank computation per round: B = (span of the laws) ∩ (its orthogonal) ∩ (zero on loose distinctions).

- If B = 0, there are no forced relations among cycle parities, whatever the carrier set.
- If B ≠ 0, the carriers are the distinction-disjoint cycles that elements of B split into. Keep those that are labels and not read by one knot.

A second principled set is the minimal-support representative of each label class, the reading-side twin of shortest changes. For unread labels a and b, test whether a, b and a + b have pairwise disjoint representatives.

**(d) What is the analogue under not-all-equal?**

- **Check (1) first.** I expect it to hold (one fresh distinction satisfies a not-all-equal birth for any inputs), but that is unverified.
- **Count classes before anything else.** The decision says the record read no classes under this law. If there is one class, there is nothing to bind, and the analogue is forced equalities of pairs.
- **Carrier.** A function of the values on a support set A, constant on classes and unchanged by flipping every value. That means a function of pairwise agreements, not a cycle parity.
- **Forced relation.** Carriers with pairwise disjoint supports whose joint image is smaller than the product of their images, while every sub-family is free, and which was not so at the start. Your SAT call per value tuple decides it. Run K1 to K3 on the image relation itself; it may be not-all-equal instead of parity.

**What a referee would press first:** the representative-dependence in (a), and that round 1 cannot show a growth-made relation.

One entry is added to the hivemind, marked `unverified`.
