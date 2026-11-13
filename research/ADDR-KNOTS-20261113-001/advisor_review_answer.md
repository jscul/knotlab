# Review of the frozen ADDR-KNOTS design

Nothing below was run; all of it is by hand from the three texts. The design needs four fixes before it runs: the class label, the by-construction survivors, the sampling unit and two validation gates that fail on correct code.

## Holes that change the result

1. **The class label is the wrong variable.** Activity is computed over the letters used, but the knots {g₁x, g₂x, g₃x} depend only on the relative maps gᵢ⁻¹gⱼ. Products cancel (q·q = e for an involution) and co-active words leave no joining, so an "exponential" description can have J_n = 0. "Grows otherwise" is therefore false: J_n is bounded above by activity, not below. Classify by the relative words (product automaton, same cycle criterion) and keep the letter class as secondary.

2. **Survival by construction beyond B0.** If every rule's three words have root swaps that are not all equal, value = first letter is a state at every level, for any r and any density. That is about (3/4)^r of rule lists, and it correlates with swap bits, hence with activity. More generally, a level-k state under which no triple collapses lifts to every later level. Flag these (k = 1 at least) and run the matched comparison without them.

3. **s = 1 has no knot.** The single relabeling is the identity or the all-flip, so e, q, qq never give three distinct images. Half of W is F0, and E's 60 s = 1 lists are wasted. The pre-registration's "every s = 1 description lives" is vacuous.

4. **P5 nearly cannot fail.** Among W's draws with a knot, about half have r = 1 (B0) and more are first-letter-settled. Restate P5 on the unsettled draws.

## Q1: matched density

- **Units are not independent.** Descriptions cluster by automaton (3 lists each) and by automaton class (renaming × letter swap). Bounded cells may come from a handful of classes, and many keys give identical patterns (all 729 sw = 000 automata are F0). Deduplicate by pattern, and bootstrap or cluster by automaton class.
- **"Same" is unreachable at the eligibility floor.** At n = 30 per arm even 0/30 against 0/30 has an interval wider than ±0.10; it needs roughly 200 per arm. The likely outcome is "unclear" everywhere, with both hypotheses surviving, so state the power or widen the bins.
- **"Bounded higher"** in H-bound is undefined (point estimate or "differs"?).
- **Undecided is not ignorable.** Hard refutations sit in the exponential arm, and up to 10% exclusion is allowed against a 0.10 effect. Report each cell with undecided counted as dead and as alive, and require the verdict under both.
- **Censoring at level 12.** Exponential patterns near the threshold die late, so "death within 12" favours them. Report death-by-level curves.
- **Matching variable.** Deaths happen at levels 3 to 12, so match on the largest ρ_n over n, or on ρ at first death, with ρ₁₂ as secondary. Add a logistic fit on ρ and class, clustered, as a sensitivity check; keep the bins primary but report mean ρ per arm, since [2, 2.5) straddles 2.1.

## Q2: which hypothesis

H-bound is a fair rival, but I expect it to fail by direction. Bounded patterns are near-copies joined by few knots, so they die early from a small dead core or live forever. Exponential ones behave like random patterns: alive below about 2.1 and dying late above it. Within level 12 at ρ in [1.5, 2.5), bounded should die at least as often; at ρ ≥ 2.5, with the settled survivors removed, both die. H-dens probably fails in a middle bin if power allows.

## Q3: P2 to P4

- **P3:** level 8 is arbitrary without a preperiod bound, so report it as descriptive.
- **P4:** fine, though it is an existence claim.
- **P2:** returns are genuinely possible. Level n + 1 is a two-fold lift of level n, and a lift of a dead pattern can live (as a double cover of an odd cycle does). I expect a few.

## Q4: Lemma A

It is sound, with three repairs:

- Siblings do not see the same profile: a child's profile excludes its own ports, so it depends on the call's binding. It is still a finite function of the parent's data; fix (ii) and (iii).
- If a call can bind one distinction to two ports, the equality pattern among ports must be recorded.
- Say whether c = c′ is allowed in the list forms; the cap of 3 covers it.

In the advisor's second proof of B0, the fixed points are odd cycles; they are harmless only because those triples are dropped.

## Q5: parts

The corrected statement is right: g(uv) = g(u)·g|ᵤ(v), so tail classes are the tiles. A knot joins when the three tails differ, not when a section is non-identity. J_n covers only the tail of length 1.

## Q6: spec errors

- **V-act-class fails on correct code, twice.**
  - Bounded θ_n is periodic, not constant: a 2-cycle with a one-step exit alternates 1, 2 at s = 4. Test θ_n = θ_{n+60} instead.
  - The slowest exponential at s ≤ 5 is a 4-cycle with one chord plus a trivial relabeling, x⁴ = x + 1, rate 1.2207, below 1.25. Use θ₈₀/θ₄₀ ≥ 100; polynomial gives at most about 16.
- **The smoke run is vacuous.** The first 150 E keys are all sw = (0,0,0) and half of W is s = 1, so no SAT call is made and the timing and V-resume are empty. Use a stratified random sample with dense s ≥ 3, r ≥ 4 keys.
- **Seed collision.** Automaton number a is not defined across s; number globally or put s in the seed.
- **Budgets.** Give Glucose4 a budget, and add a gate that `conf_budget` binds on Cadical195 (a tiny budget must return None).
- **`first_death`** is ambiguous when a null precedes a death; add a flag.
- **"x1.6"** misses the rates between 1.22 and 1.6.
- The unit clause and the phase hint are fine.

## Words

- **address, activity, joining knots:** fine.
- **level:** already used for subdivision steps of the Sierpinski patterns; say "address length n", or check the glossary.
- **relabeling:** names two things (an automaton state and a map) and reads like the admitted recodings. Use "address map" for the map and its products, and give the literature's "state" once.
- **knot rule:** "rule" against "law" is already a flagged confusion; "placement" is safer.
- **part:** already means any sub-pattern in the nesting notes; use "tail class".
