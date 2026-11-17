# Two-orbit bonds, forgetting on the values states take, and exposure

`KEEP-REACH-20261117-001A-P001`, epic `KEEP-REACH-20261117-001`, 2026-11-17. Written by Claude. The advisor model reviewed the design
and contributed the exposure lemma's idea (`research/KEEP-REACH-20261117-001/advisor_design_answer.md`). Refereed (KEEP-REACH-R1,
`research/KEEP-REACH-20261117-001/referee-R1/report.md`): confirmed with fixes, no Block. Checks:
`check.py`, with its result in `result.json`. The setting is that of Theorems W and F
([W](../../DIRECT-REACH-20261115-001B/DIRECT-REACH-20261115-001B-P001_every_depth/proof.md),
[F](../../BLOCK-REACH-20261116-001A/BLOCK-REACH-20261116-001A-P001_forgetting_blocks/proof.md)):
- addressed not-all-equal patterns, with blocks of orbits that meet only parent to child;
- with orbits of at most four addresses, finitely many types and exact projections;
- L_N(k, s) is the least bond of P_N meeting level k and level k + s.

The **pair projection** of two orbits is the projection of all states of P_N onto them; Theorem W computes it exactly.

*Words (checked with the advisor after the referee, `research/KEEP-REACH-20261117-001/advisor/words_answer.md`).* The **pair
projection** of two orbits is the projection of the allowed states onto them (first written "joint"). It is a **product** when every
pairing of the two projections' assignments is allowed. A **two-orbit bond** is a bond inside the union of two orbits containing a
distinction of each. An assignment of an orbit is **exposed** when some free set of the orbit's addresses takes its values in that
assignment only, and a dependence is **unexposed** when the pair projection is not a product but every missing pair has an unexposed
side (first written "hidden").

## Theorem K (two-orbit bonds of any size)

*For a top level k and every s ≥ 1 and N ≥ k + s, let b_N(k, s) be the least size of a set of addresses inside an orbit at level
k and an orbit at level k + s that meets both and is a bond in their pair projection. Then L_N(k, s) ≤ b_N(k, s), and b is decided for every
s and every N by a finite computation.*

*Proof.* The pair projection is the exact projection, so a set inside the two orbits is constrained, or free, in P_N exactly when it is in the
pair projection. A bond in the pair projection is therefore a bond of P_N meeting both levels. The computation is the refereed every-depth routine of
`DIRECT-REACH-20261115-001` (eventually periodic pair states, with every remaining depth below r₀ read separately). Only the property
read from each pair projection changes: the least such bond. ∎

## Theorem F′ (forgetting on actual values)

*Suppose that for some r, at every level j ≥ k and every remaining depth, the pair projection of every orbit and every descendant orbit r levels
below is a product of its two projections. Then L_N(k, s) ≥ 1 + ⌈s/r⌉.*

*Proof.* This is Theorem F's count with a weaker hypothesis. Splicing across the r groups between two such orbits O and O′ joins a
state α with a state β. It needs only that α's value on O and β's value on O′ are related by the window. Both values are taken by
states, so they lie in the projections of the pair projection J(O, O′), and J is their product. So the pair occurs in some state, and the
window can be filled as that state fills it. In Case 1 the windows between u's group and v's group start at levels ≥ k. In Case 2
the windows that start at levels ≥ k still number at least s − 1, so the count 2 + ⌊(s − 1)/r⌋ holds. ∎

F′ needs the products only on the values states actually take, where F needed them on all assignments. A pattern can never forget
on all assignments only through values no state takes, and then F′ still applies.

## Lemma E (exposure)

*Let J be the pair projection of orbits X and Y, with projections P_X and P_Y. Call an assignment x in P_X exposed when some set T of X's addresses
is free in P_X and x is the only assignment of P_X with its values on T. If some pair (x, y) in P_X × P_Y is missing from J, with x
exposed by T and y exposed by T′, then T ∪ T′ contains a bond of the pattern that meets both orbits, of at most |T| + |T′|
members.*

*Proof.* Fix x's values on T and y's values on T′. Every allowed state with these values takes x on X and y on Y, since both are exposed. That
pair is missing, so no state has these values, and T ∪ T′ is constrained. T and T′ are free, so a minimal constrained subset of
T ∪ T′ meets both. It is a bond, since all its proper subsets are free. ∎

A pair projection can depend on both orbits while every missing pair has an unexposed side. Then the dependence is hidden behind one orbit's
own constraint, and the pair projection holds no bond meeting both orbits (the advisor's example).

## Computed

**The census** (`run_census.py`, `census_keep.json`): 786 small-orbit descriptions, every depth tier.
- The 46 that never forget all have a two-orbit bond at every s and every depth. The 42 direct ones are at 2 or 3. The four others
  are bounded at 4, 4, 5 and 6 from s = 2 or 3 on: 8db5da810c00 at 5, a9a1c941de1a at 4, bace53f8f952 at 4, ca1efb37ad88 at 6.
- So forgetting decides bounded or growing for all 786, at every depth: 740 grow by Theorem F, 46 are bounded by Theorem K.

**A fresh sample** (`run_sample.py`, seed "KEEP-1117"): 1,016 draws until 40 small-orbit draws, alive at every depth, never forget.
**The mutations** (`run_sample.py mutants`): every one-slot change of one placement of the four.

| | Small orbits, alive | Forget on all assignments | Never forget, two-orbit bond at every s | Never forget, no two-orbit bond at some s |
| --- | ---: | ---: | ---: | ---: |
| Fresh sample | 670 | 630 | 38 | 2 |
| Mutations of the four | 1,710 | 451 | 1,222 | 37 |

*Narrowed after CARRIER's referee (CARRIER-R1, 2026-11-17):* the counts are of descriptions (keys), and many give the same pattern,
since a mutation can swap a word for one that acts the same. The 2,380 are 583 distinct patterns (244 forget), the 39 are 16 (6, 5
and 5 of the kinds below), and the census's 786 descriptions are 181 distinct (139 forget, 42 never do).

The 39 in the last column (`analyze_third.py`, `third_class.json`) fall into three kinds:
- **14 forget on actual values (6 patterns).** Theorem F′ applies with r = 2 or 3 from level 3, so they grow at every depth.
- **13 have top pair projections that become products (5 patterns).** From level 3, every two-orbit pair projection is a product from s = 5 on, while pair projections that
  start deeper never become products. All 13 are mutants of 8db5da810c00. For one of them, 8db5da810c00-73, the certified least bond
  at depth 11 is L₁₁(3, s) = 3, 4, 5, 5, 6, 6 for s = 1..6. That is past its parent's bound of 5, which holds at every depth by
  Theorem K. The parent's own certified values at depth 11 are 3, 4, 5, 5, 5, 5. At depth 13 (900 s per s) it reads 3, 4, 5, 5, 6, 6 again for s = 1..6; s = 7, 8 undecided.
- **12 keep an unexposed dependence (5 patterns).** From level 3 the pair projections stay non-product at every s checked (13 to 16, past every preperiod seen),
  but every missing pair has an unexposed side (Lemma E fails). So no two-orbit bond forms. The census search at 300 s per s decided
  none of their cells past s = 2 at depth 11.

*Checks* (`gate_two_orbit.py`):
- the least two-orbit bond agrees with an independent brute force on 3,000 random relations;
- it agrees with Theorem W's ties and three-member bonds on all 541 values of the 85 small-orbit population-D descriptions;
- no two-orbit bound lies below any of the 1,975 decided census cells at depth 9.

## What is proved, and the open converse

- **Proved.**
  - A two-orbit bond from the top at every distance bounds the reach (K).
  - Forgetting on actual values from the top's level forces growth (F′).
  - An exposed dependence between two orbits gives a two-orbit bond (E).
- **Consistent with everything computed, open.** *Conjecture C′:* L(k, s) is bounded exactly when a two-orbit bond from level k
  persists at every distance. It holds on all 786 census descriptions and on the 2,355 of the 2,380 fresh and mutated ones where the two tests decide.
  It is untested on the 25 of the last two kinds (13 and 12), and the one deep reading found agrees with it (8db5da810c00-73 grows
  past 5).
- **What the third class shows.** "Never forgets on all assignments" does not imply a bounded reach: the 14 forget on actual values and
  grow (F′). For the 25 that never forget even on actual values, boundedness is open (C′'s open direction); they hold no two-orbit bond
  from the top. *(Narrowed after the referee: it read "'Never forgets', even on actual values, does not imply a bounded reach".)*

## Dependencies

- `DIRECT-REACH-20261115-001B`: Theorem W and its every-depth routine.
- `BLOCK-REACH-20261116-001A`: Theorem F and its count.
- `BRANCH-DEPTH-20261112-001A`: the splicing lemma.
- `LEVEL-REACH-20261114-001`: the census and its search.
