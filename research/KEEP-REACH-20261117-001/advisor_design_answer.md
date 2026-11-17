**What I checked:** the logic of the plan and the two lemmas in question (1), by hand. I did not open the repository, the refereed routine or the census, and ran nothing.

**(1) Conjecture C has two gaps, and one has a counterexample.**

- **Non-product does not imply a bond meeting both.** Take X = {x1, x2} with allowed states {00, 11, 01}, Y = {y}, and forbid only (01, y=1). The joint is non-product. But {x1, y} and {x2, y} are free and {x1, x2} is constrained, so no minimal constrained set meets both. The dependency is hidden behind X's own constraint.
- **Realisation is not automatic.** The actual joint is e ∩ (Up × Down), and a non-rectangular idempotent can be cut to a rectangle (e = equality, Up a single state).
- **States versus values.** If Q carries more than the orbit's address values, a relation non-rectangular on Q can still project to a product on values. Say which one K uses.

**Proof idea (exposure lemma).** Call a marginal state x of an orbit *exposed* if some internally free subset T ⊆ X has x as the only marginal state with that restriction to T.

- If a missing pair (x, y) has x exposed by T and y exposed by T′, then T ∪ T′ is constrained while T and T′ are free.
- So a minimal constrained subset of T ∪ T′ meets both orbits, and the bond has size ≤ |T| + |T′|.
- Free orbits, ties (take one representative per tie) and an NAE triple (every allowed state has an equal pair, which determines it) are all fully exposed.
- C then reduces to a finite check: are all marginal states of the actual orbit types, at each depth tier, exposed? Orbits with four addresses and trimmed marginals are where it could fail.

**(2) Read forgetting on trimmed states.** Use states extendable both up and down, per depth tier, projected to values.

- Theorem F's proof should only use states that occur, so a trimmed F′ is stronger and probably free; check this against the proof.
- The dichotomy is then clean: either trimmed r-windows are all rectangular, or non-product actual joints exist at every s.
- With rectangularity on all of Q, a description can "never forget" only through unreachable states. That is a place where C fails for the wrong reason.

**(3) Sharpening the sample.**

- **Power.** Only 46 of 786 census descriptions never forget, so a fair-coin sample may contain almost none and P2 would pass vacuously. Freeze a minimum count of never-forgetting, non-direct descriptions (rejection-sample until reached) and report it.
- **Where a counterexample lives.** Look at orbits with an unexposed marginal state (four addresses, an internal constraint that is neither a tie nor an NAE triple), at cross-dependency conditional on one internal state, and at Up/Down pruning that differs by tier. Add one-placement mutations of the four non-direct cases.
- **Every s.** Decide it by the proved preperiod and period, not a cap such as 24; freeze that bound.
- **Third outcome.** Record "never forgets on trimmed states, non-product joint, no two-orbit bond" as its own class. It refutes C but not necessarily boundedness, since a bond may pass through a third orbit.
- **Gates.** The gate "forgetting with r implies no bond for s ≥ r" is true by construction and has no power. Replace it with the exposure check and a brute-force comparison of trimmed against untrimmed rectangularity.
- **P1.** The "partly undecided" profiles need deciding before the freeze, or P1 should exclude them explicitly.
