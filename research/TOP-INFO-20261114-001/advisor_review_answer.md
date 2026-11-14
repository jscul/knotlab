<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

**Verdict:** Theorem P's sketch is unsound, the "maximal shattered subset" repair fails too, and the converse fails as stated. The rule worth freezing is the one in your Q2, with shattered sets. All of this is hand-checked, not machine-run.

**1. Counterexample to the sketch (and to the repair).**
Take V = {p,q,r,t}, X_c = {x}, and R = NAE4(p,q,r,t) × {0,1} minus the two states (0011, x=1) and (1100, x=0).

- R is complement-closed, with 26 of the 28 product states, so V and x are correlated and s is "pinned".
- Every triple of V together with x is full. A triple's assignment τ has two completions differing in one place; if τ is constant its one NAE completion has weight 1 or 3, otherwise at most one completion is 0011 or 1100.
- So no bond inside V ∪ X_c contains x: such a bond is T ∪ {x} with T shattered, hence |T| ≤ 3, and then T ∪ {x} is full.
- The only correlated set is V ∪ {x}, and forgetting x leaves NAE4, so K2 fails.
- Maximal shattered subsets of V are the triples, and each is independent of x, so that repair fails as well.

This is also your parity-like hiding done by a positive complement-closed relation: x is independent of every three ports. It is pp-definable from NAE3 with witnesses (complement-closed is the whole co-clone).

What it does not show: whether some family in scope realises it, or that P's bound itself fails, since with members anywhere a witness may complete a bond. P is unproved, not refuted.

**2. Repair that is provable.**
Call s *bond-pinned* when some shattered T ⊆ V and shattered D ⊆ X_c have T ∪ D not full.

Theorem P′: then L(s) ≤ |T| + |D|. Proof: a minimal non-full subset of T ∪ D is a bond, and it meets both sides because each side alone is full.

**3. Converse fails as stated.**
NAE(p, y, x) with y an own distinction of a shallow copy, or any top non-port, gives L = 3 with V independent of X_c. Nothing in scope as you state it excludes a shallow y.

**Q1.** Pumping gives only U and D, not V and X_c. A bounded bond B across a member-free stretch splits as U above and D below; both are shattered as proper subsets of a bond, and U ∪ D = B is not full. U may contain non-ports.

**Q2.** Yes, with shattered sets. The exact form is: there are shattered U in the top block and shattered D in the target block with U ∪ D not full, while (U∖V) ∪ D and U ∪ (D∖X_c) are full. The last two conditions force a minimal non-full subset to contain a port and an own distinction.

This is not the same as "not trimmed-rectangular":
- A bond across the stretch implies non-product, so non-rectangular.
- Non-rectangular does not imply a bond: the example in 1 is non-product with no cross bond.

So G2's negation is necessary and not sufficient, unless you prove hiding cannot survive the stretch's finite state. That is the real open lemma.

**Q3.** The Q2 rule is decidable, provided the top and target blocks are bounded. The stretch's transfer relations form a finite monoid, so their powers are eventually periodic; compute the periodic part per residue and enumerate U and D. Plain pinning and rectangularity are decidable the same way, but they are the wrong predicates.

**Cheap refuting checks.**
- **P itself:** in the 632 growers, test V–X_c correlation at two depths per residue. Any pinned depth refutes P.
- **Converse:** among the 5,074 bounded, look for a family where every window certificate has a non-port top member and the V ∪ X_c projection is a product. The 93 order-label families are the first place to look.
- **Hiding:** among the 83 undecided, look for non-rectangular families with no shattered cross pair.

**Freeze:** P′, the Q2 rule as the characterisation of the bounded case, its decidability, and the example in 1 as the reason plain pinning is not the rule.