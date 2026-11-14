<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

**Lemma W: sound, with three repairs** (pen-and-paper review, nothing run)

- **Exactness.** The copy tree separates c's block from the rest through c's ports only, so context × inside is exact provided "usual limit" is the decreasing limit from "everything allowed". Compactness then makes it the true projection of an infinite subtree; a limit from below is not.
- **Merges.** Merge c-port with c-port too, not only c with main. Two ports of c carrying one own distinction of an ancestor otherwise show a spurious size-2 "bond" (equality of two coordinates). The automaton state must carry this partition.
- **Living.** Require a living family; an empty J_w makes every set non-shattered.
- **Wrapper main.** Fine once merged: Start is an identity relation, and a port in no constraint is in no bond.
- **R_i.** Either choice gives the same state set, since the next step re-imposes c's limit relation and conjunction is idempotent. Leaving it out is cleaner, and J_w is then truly the context.
- **Caps.** Capped length sets do not certify "every large depth". Iterate the reachable-state set Q_s = step(Q_{s−1}) instead; it is deterministic, so the first repeat proves periodicity. No repeat before the cap means undecided.

**Negative control: weak where the risk is**

Forgetting families have rectangular products and probably no identity passing, so the merge code is never exercised. Two additions:
- Check U(s) ≥ 2 + ⌊s/r⌋ at every s, not only large s.
- Compare U(s) with brute force on explicit truncations (leaf limits substituted) for s ≤ 3 on stratum I families.

**Live quotient: sound**

If a non-shattered X contains a free x, then X∖{x} is non-shattered, so no bond contains x and L is unchanged. "Free" must be a least fixed point over port positions across all definitions, and a distinction is free only if every position it occupies is dead.

**Stronger growth arguments** (sketches, to be checked)

- **Conditional gap.** Let T be the distinctions passed through the r-gap. If for every T′ ⊆ T the product with T∖T′ projected out is rectangular given each value of T′, a crossing bond X₁ ∪ T′ ∪ X₂ forces X₁ ∪ T′ or T′ ∪ X₂ non-shattered. Minimality then empties one side, and the gap count survives.
- **Trimmed rectangularity.** For conserved labels or orders, restrict the gap product's upper tuples to those the context realises and its lower tuples to the limit relation, then test rectangularity. A label one side cannot read drops out: J = ∪_λ P_λ × Q_λ with trimmed P_λ independent of λ is rectangular.

**Predictions**

- **P3** is settled by construction. Knots have three places, so a bond through an identity-carried port and one knot of c has size at most 3.
- **P1 and P5** are nearly one measurement. A cycled identity that is live gives a window bound; one that is free gives the quotient. Only the residue is informative: an identity that never reaches a main port, or one that sits only in port-only knots.
- **P4** is all-or-nothing at n = 5.
- **P2** is informative but underpowered: at n = 91 the Wilson half-width is about 10 points.
- **Undecided rule.** Counting undecided as not bounded biases P1 down, so the sensitivity figure is needed.