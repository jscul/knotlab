# Referee report SUBST-NEST-R1: nesting by substitution

**Verdict: Confirmed with fixes.** Every census number reproduces with new code. The pinning rule, which the record reports as proved one
way and exact the other, is a theorem in both directions. I proved it independently by a different argument from the one in
`PIN-RULE-20261112-001`. The influence is real, but its reach across the whole pattern is the pattern's connectivity and adds no
information beyond one knot. Three wording fixes and one arithmetic slip are listed in section 4.

Referee: the background referee thread, 2026-11-12. The handoff is in `brief.md`. The code (`ref_subst.py`, `ref_pin` checks in the
PIN-RULE referee folder) was written for this job and imports neither `subst_lib.py` nor `check.py`. It differs from the author's in
three ways:
- it uses Glucose 4, not CaDiCaL;
- it computes the whole tie relation of every substituted pattern, not only the roots' tie classes;
- it builds the three-copy nesting from integer points.

Validation: V2, an independent reimplementation by a separate session. The advisor model was consulted once, cold, on my proof (section
2). It found the proof correct and gave a simpler reading of "spare". Its view was checked here, not taken as a result.

## 1. The census, rebuilt (exact, on the frozen range)

| Item | Record | Referee |
| --- | --- | --- |
| Living connected blocks (3, 4, 5 distinctions; 6 with up to 5 knots) | 87 (1, 3, 28, 55) | 87 (1, 3, 28, 55) |
| Diagonal: ties between different copies | none in 87 | none in 87 |
| Block's knots: every distinction spare / some / none | 40 / 42 / 5 | 40 / 42 / 5; the 5 rigid templates are exactly the 5 blocks with no spare distinction |
| Every distinct triple: none / rigid / empty | 1 / 3 (on 4) / 83 (on 5 and 6) | 1 / 3 / 83 |
| Cells meeting the frozen criterion | 50 | 50 (47 with the block's knots, 3 with every distinct triple) |
| Roots tied outside their copy; short of the farthest distinction | 1,090; 0 | 1,090; 0 |
| Ties only after two substitutions | none | none |
| K4 with its knots | rigid, share 1/4 once and twice, 6 states | the same; σ(chain of 4) has exactly 6 states |
| Three-copy gadget, levels 0 to 5 | no ties | no tied pair anywhere |
| Fano gadget, levels 0 to 4: tied to a terminal | 1, 3, 7, 31, 175 | 1, 3, 7, 31, 175, of 3, 7, 31, 175 and **1,039** distinctions |

The whole tie relation also has a closed form, checked against the computed relation on all 870 living tests with the block's knots.
In σ(P), for a connected P with a knot, (v, p) and (w, q) are tied exactly when both of these hold:
- p = q, or p and q are tied in the block;
- v = w, or p is not spare.

The tied-pair count predicted by this form equals the computed count in all 870 tests. Ties between copies of the same distinction
are always equalities. Ties between different distinctions in different copies carry the block's own relation; 150 of them are
inequalities, the block's opposite ties carried across copies.

## 2. The pinning rule is a theorem (the referee's proof)

**Theorem.** B is a living block, T is B's knots in every order, and P is connected and has a knot. Then p's part is tied across
all of P, by equality, exactly when p is not spare. A spare p's part is tied to nothing (N6).

**Proof of the hard direction.**
- **Setup.** Take a state, and let a, b and c be the B-states of the three copies at a knot of P. Suppose a, b and c do not agree
  at p. For every other distinction q, set u(q) to the majority of a(q), b(q), c(q).
- **A knot e of B without p.** Suppose u takes one value β on all of e. Then each member of e takes β in at least two of the three
  copies. If some copy misses all three members, that copy's state is constant on e, which no state of B is. Otherwise Hall's
  condition holds, so each member of e can be sent to a different copy where it takes β. That gives a between-copy knot of T whose
  three values are equal, and it is violated.
- **A knot e = {p, b', c'}.** Suppose u(b') = u(c') = β. Then p takes β in at least one copy, because it takes both values. The same
  dichotomy applies: either one copy is constant on e, or Hall's condition gives a violated between-copy knot.
- **Conclusion.** u gives every knot of B both values among its members other than p, so p is spare. Contrapositive: a non-spare p
  is equal in the three copies of every knot of P, and so equal on the whole connected pattern.

PIN-RULE's proof is shorter: it takes the third copy itself as the spare witness. Both are correct, and I checked theirs line by
line.

**Corollaries.**
- A template is rigid exactly when no distinction is spare.
- The advisor's restatement: p is spare exactly when some state of B stays a state when p alone is flipped.
- With T = B's knots in every order, pins on a part never vary from copy to copy.

**Checks.**
- On all 87 templates, a template triple differs at a distinction exactly when that distinction is spare.
- On 500 random living blocks of 6 to 10 distinctions (seed 20261113), the same holds by SAT on one substituted knot, and on the
  chain of 8 knots for some of them. See `result_random.json` once it is written.

## 3. The coordinator's points

**(a) Is the global influence real, or an artefact of the stitching rule?**

It is real, and it is a theorem. But two parts of it are close to the construction, and the write-up should say so plainly.

- **The reach is connectivity.** Once one knot of P forces p equal in its three copies, ties chain along P. So "fixing one distinction
  forces that block distinction in every copy, at every distance", "tie extent 16 steps on the chain of 16" and "tie extent equals
  the farthest distinction in all 1,090 roots" follow from the local fact and the pattern's connectivity. They are not separate
  findings. The frozen criterion "influence growing with the pattern" is met by every block with a local pin, whatever the pattern.
- **The pin is not stated by any knot.** No between-copy knot holds (x, p) and (y, p) together: each one holds three different
  distinctions of the block. So the equality is forced, and which distinctions it reaches (the non-spare ones) is a property of the
  block alone.
- **The plain statement.** A non-spare distinction is pinned because, in every state of B, it cannot flip alone. The block's knots,
  laid across three copies in every order, carry that rigidity across copies, which makes the copies agree there.
- **It is global in reach, local in cause, and uniform.** PIN-RULE's account says the same, and it is fair.

**(b) Is "pinned iff not spare" proved in either direction, and is it worded accordingly?**

N6 proves "spare ⇒ free", and the record calls the converse "exact, descriptive". That was the right wording when written. Both
directions are now proved (section 2, and PIN-RULE). The decision note's table and "What this establishes" can point to the
theorem.

**(c) Are the three corrections logged with the right verdicts?**

- **N5 narrowed.** Narrowing is right. The narrowed proof is correct: with m ≥ 5, two of three states share their majority value at
  three or more places; the third state is not constant, so it has that value somewhere; three distinct places then carry one value.
  The verdict is Narrowing (Wrong step) in a frozen lemma, and it does not touch the main result, which uses the block's knots.
- **BASES-WITHIN's "nesting spreads no influence".** Narrowing is right. Its "Stands: every lemma and count of BASES-WITHIN" should
  now point to BASES-WITHIN-R1, which replaces that epic's sampled count of lagged stitches (17 of 45 harmonies becomes 37 of 45).
- **"Bond distance" for steps apart.** Not a block is right.

**(d) The count wording.** "47 of 87 blocks" in the chat note and "5 rigid plus 42 intermediate" in the handoff agree: 47 is the
number of blocks with at least one non-spare distinction. "Most of these blocks hold no ties of their own" is right: 30 of the 47 hold
none and 17 hold some.

## 4. Fixes for the thread

1. **Fano gadget, level 4.** The share is 175/1,039, not 175/1,051. The run computed 1,039 distinctions: d_k = d_(k−1) + 4 · 6^(k−1).
   The pre-registration's N3 and the proof's arm-K table carry 1,051. **Not a block** (arithmetic slip in a frozen text).
2. **N2's last clause.** "No distinction is tied to any other at any level" does not follow from "level 1 allows all eight on the
   terminals". That fact fixes only the terminals' relation. The clause is computed: no tied pair at levels 0 to 5 here, and 0 to 7
   in BASES-WITHIN-R1. **Not a block** (wording).
3. **Reach.** Say in the answer that the whole-pattern reach is the pattern's connectivity once one knot pins. **Not a block**
   (emphasis).
4. **The pinning rule.** Update "proved one way; exact the other" to point to the theorem now proved in both directions. This is not a
   correction: the record was right when written.

## 5. The lemmas

- **N1 holds.** The relations on three distinctions closed under the mirror and under every order are exactly none, all equal,
  not-all-equal and all eight. The next level fixes each one except not-all-equal; all equal needs a connected gadget.
- **N2 holds,** as far as all eight on the terminals.
- **N3 holds,** with the share fix above.
- **N4 holds:** the diagonal gives the Cartesian product, and ties are products.
- **N5 holds as narrowed.**
- **N6 holds.**
- **N7 holds:** each knot of P forces its three copies into one state, and connectivity spreads that to the whole pattern.
