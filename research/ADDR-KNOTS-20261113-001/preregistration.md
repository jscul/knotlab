# Pre-registration: knots placed by address maps

Epic `ADDR-KNOTS-20261113-001` (G17 Typical and rare meeting patterns, with G1; program topology, group spacing), 2026-11-13, at the
coordinator's go-ahead after John confirmed the direction ("Yes, let's proceed with that", 16:39 UTC). Written before any registered
run and revised once after the advisor model's review of the frozen draft (see "Advisor"). The census `ADDR-KNOTS-20261113-001A` is
computed by code Codex writes from [codex_spec.md](codex_spec.md) and run by the thread; the proof note `ADDR-KNOTS-20261113-001B` is
[proof.md](../../proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces/proof.md). The canonical K1–K3
test is unchanged.

## The question

Every nested study so far let a copy meet the rest through a fixed number of distinctions, and `NEST-COUNT-20261112-001` proved such
patterns finite-state. The owner's recursion picture is the excluded case: "the nested structures depend on the larger structures to
know where they are ... for logic, it can hop around." Under a description weighting in the spirit of A79, among not-all-equal
patterns whose knots are placed by a small automaton on addresses, so that tail classes are joined to the rest by a number of knots
that may grow with the level: how common is each fate (resolves to nothing, lives a while and ends, lives at every level read), and
does how fast the joining can grow change the fates once knot density is matched?

## The question in standard terms

For two-colourability (NAE-3-SAT) of the 3-uniform hypergraphs {g₁x, g₂x, g₃x} on {0,1}ⁿ, with g's words of length at most 2 in the
states of a random invertible binary Mealy automaton: the satisfiability profile over n = 1..12, by the Sidki activity class of the
relative maps gⱼgᵢ⁻¹ (finitary, bounded, polynomial, exponential) at matched hyperedge density, under a prefix-code sampling.

## Words

From the proof note: **address**, **level** n (addresses of length n), **address map** (the map defined by an automaton state, the
literature's "state", or a product of such maps), **placement** (a triple of address maps), **tail class** (the addresses sharing
their last letters; the literature's tile), **joining knots** (knots holding addresses in a tail class and outside it), **activity**
(the literature's term, Sidki 2000). "Level" is used instead of "depth", which the guide's glossary gives to holes. A level is not a
growth: level n + 1 is a new pattern lying over level n, so A72's "adding knots never brings a state back" does not apply, and a
return is possible in principle (P2).

## The object and the weighting (frozen; details in the spec)

- **Automaton:** s state maps, each a swap bit and two successors; two letters.
- **Words:** e and the words of length 1 and 2 in the state maps (1 + s + s² words; `q r` means r first, then q).
- **Description:** an automaton and a list of r placements, each an unordered triple of distinct words. The level-n pattern is the
  union over placements of the knots {g₁x, g₂x, g₃x}, x of length n, kept when the three addresses are distinct.
- **Weighting (A79's kind):** fair coins; s by Elias gamma (s ≤ 5, else rejected and counted), each swap bit 1 bit, each successor
  uniform, r by Elias gamma (r ≤ 8), each placement uniform among the C(1 + s + s², 3) triples; weight 2^−length.
- **Populations.** **W:** 40,000 fair-coin draws (seed 20261113). **E:** every automaton with s = 3 (5,832) with 3 placement lists
  each, and every automaton with s = 2 (64) with 30 lists each; lists drawn by the placement code with r = 1 + Elias gamma (r ≥ 2,
  capped at 9), seeds naming s. E exists for power in the matched-density comparison; W gives the weights.

## Settled by construction (before the run)

- **s = 1 places no knot** (the one map is the identity or the flip of every letter, so e, q, qq never give three distinct images):
  F0 by construction, about half of W's weight.
- **B0** (proved): one distinct placement lives at every level.
- **First-letter settled** (proved, the proof note's remark (a)): if in every placement the three root permutations are not all
  equal, the first letter is a state at every level, whatever the density.
- The run reports the weight settled each way. The primary comparison excludes B0 and first-letter-settled descriptions.
- **Lemma A** (proved): the other way to let a copy meet a growing number of distinctions, uniform shared lists, stays finite-state;
  it is not censused.
- **Expected, not proved:** bounded activity of the relative maps gives tail classes joined by a bounded number of knots, finite-state
  by Bartholdi 2022's construction applied to knots. Activity bounds joining from above only: maps can cancel.

## Measures

Per description and level n = 1..12: the knot set (deduplicated), its size, the verdict (alive, dead, or **undecided** when the
solver's conflict budget runs out), and the joining count J_n (knots holding addresses ending in 0 and in 1). Then:

- **Fate within level 12:** F0 no knot at any level read; F1 resolves to nothing (dead at its first level with knots); F2 ends
  (alive at some level, dead at a later one); F3 alive at every level read; FU undecided (a level with no verdict leaves the class
  open). Undecided is its own cell, never folded into alive. A return (dead, then alive at a later level) is flagged.
- **Density:** ρ_max = the largest knots_n / 2ⁿ over n = 1..12 (primary matching variable); ρ₁₂ (secondary); the mean of each per arm
  is reported.
- **Activity class** (primary): the largest exact class (finitary < bounded < polynomial by degree < exponential) of the relative maps
  gⱼgᵢ⁻¹, i ≠ j, over all placements, by Sidki's cycle criterion on their product automata. The class of the state maps used (the
  letter class) is secondary. The measured joining growth (J_10, J_11, J_12) is reported beside them as a check, never used to
  classify.
- **Unit:** a distinct level pattern (all twelve knot sets equal ⇒ one unit), carrying its automaton's class under renaming the state
  maps and swapping the two letters (the **automaton class**, the cluster for intervals).

## Predictions and failure criteria (frozen)

Shares are reported raw, given s ≥ 2, given s ≥ 3, and given density bin, by count (distinct patterns) and by weight (W's draws).

| # | Prediction | Fails if |
| --- | --- | --- |
| P1 | Every description with one distinct placement, and every first-letter-settled one, is F3. | Any is not: a bug; the run is invalid until fixed. |
| P2 | No return: no description is dead at a level and alive at a later one. (The advisor expects a few: a two-fold lift of a dead pattern can live.) | Any return (reported as a finding). |
| P4 | Late ends exist: some unsettled description whose relative class is exponential first dies at level 9 or later. | None does. |
| H-dens | (the advisor's first view) At matched density, the relative class adds nothing to the death share. | Some eligible cell "differs". |
| H-bound | (the thread's) At matched density ρ_max ≥ 1.5, bounded descriptions die less often than exponential ones. | Some eligible bounded-against-exponential cell with ρ_max ≥ 1.5 is "same", or "differs" with bounded higher. |

Descriptive, not predictions: the first-death level by class (the draft's P3, a level-8 cut with no preperiod bound behind it); the
weight settled by construction and the fates of the rest (the draft's P5, which could hardly fail); death-by-level curves per class
and bin (deaths after level 12 are censored, which favours late-dying classes). The advisor's revised expectation, recorded before
the run: H-bound fails by direction, bounded descriptions dying at least as often as exponential ones in [1.5, 2.5).

**Matched-density design (the study's core, frozen).** Population E, distinct patterns, B0- and first-letter-settled excluded (also
reported included), F0 excluded, FU counted. Bins of ρ_max: [0, 1), [1, 1.5), [1.5, 2.1), [2.1, 3), [3, 4.5), [4.5, ∞). A class's
death share in a bin is the share of F1 or F2. A comparison of class C against exponential is **eligible** in a bin when each arm has
at least 30 decided patterns from at least 5 automaton classes and under 10% undecided. Δ = share(C) − share(exponential); its
interval is a cluster bootstrap over automaton classes within each arm (2,000 resamples, percentile), at 95% and at 1 − 0.05/m with
m the number of eligible cells (Bonferroni). A cell **differs** when the corrected interval excludes 0 and |Δ| ≥ 0.10; is **same**
when the 95% interval lies within [−0.10, 0.10]; else **unclear**. Each verdict is computed twice, undecided counted as dead and as
alive, and holds only when the two agree (else unclear). H-dens and H-bound are rivals; both can fail. If no bounded-against-
exponential cell with ρ_max ≥ 1.5 is eligible, H-bound is **not testable at s ≤ 3**, reported as such. **Power:** "same" needs
roughly 200 patterns per arm; thin cells will read "unclear", and that is reported, not upgraded. Sensitivity: a logistic fit of
death on class and bin with cluster-robust errors by automaton class; W read the same way by weight, as a secondary that never
overrides E.

## Validation gates (in the spec; any failure invalidates the run)

V-act (the action against a recursive reference), V-sat (verdicts against brute force at levels ≤ 4; two budgeted solvers agree at
levels 9 and 10; a tiny conflict budget returns undecided), V-B0 (the proof note's check), V-act-class (exact classes against counted
active sections to length 160), V-rel (relative maps: the product automaton's action equals composing the actions), V-code (s and r
frequencies against Elias gamma), V-resume (a killed and restarted run gives identical records).

## Stop rule

One Codex hand-off, one registered run by the thread, its frozen summary, a referee hand-off; report and hold. Nothing is claimed
beyond level 12, two letters, five state maps, words of length 2, or the stated weighting. A finite census proves no all-level
statement.

## Prior work and what is ours

Known: Bartholdi 2022 (domino and monadic second-order logic on self-similar graphs: decidable when bounded, undecidable on a
linear-activity example; conjecture for contracting groups); Sidki 2000 (activity); Bondarenko et al. 2008 (three-state two-letter
automata); D'Angeli, Donno and Nagnibeda (Ising and dimers on Schreier graphs); Seymour 1974; random NAE-3-SAT's threshold near 2.1
knots per distinction. Ours: the not-all-equal law on these patterns, the description weighting over automata and placements, the
fate census within level 12 and the matched-density comparison. Novelty to be checked again at close.

## Advisor

Consulted twice before freezing: on the design ([advisor_design_question.md](advisor_design_question.md),
[advisor_design_answer.md](advisor_design_answer.md): B0 and H-dens are its), and on the frozen draft and spec
([advisor_review_question.md](advisor_review_question.md), [advisor_review_answer.md](advisor_review_answer.md)). The second review
changed: the class to the relative maps (activity of the state maps does not bound joining from below); the first-letter-settled
exclusion; s = 1 is F0 by construction; P3 and P5 made descriptive; units deduplicated by pattern with cluster intervals; undecided
read both ways; ρ_max as the matching variable and the bin edge at 2.1; two validation thresholds (bounded activity is periodic, the
slowest exponential rate at s ≤ 5 is about 1.22); a stratified smoke run; seeds naming s; budgets on both solvers; the words address
map, placement and tail class.

## Exploratory runs disclosed

Before this file: the four scripts in [exploratory/](exploratory/) (single placements on two and three letters; all four single-map
triples at s = 3 to level 10; the activity split), reported to the coordinator. Their populations and placements differ from the
registered ones (no products of maps, no weighting).
