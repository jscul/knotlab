# Knots placed by address maps

Epic `ADDR-KNOTS-20261113-001` (G17 Typical and rare meeting patterns, with G1; program topology, group spacing), 2026-11-13, at the
coordinator's go-ahead after John confirmed the direction. Pre-registered in commit 02b35eb5f ([preregistration.md](preregistration.md)),
with the prior work in the program added (f21c6f33e) and the summary's units fixed by an addendum (d2231b8ce,
[codex_spec_addendum.md](codex_spec_addendum.md)), all before any registered result was read. Code by Codex from
[codex_spec.md](codex_spec.md), run by the thread (systemd unit ak-run, 8 workers, 18:00 to 21:38 UTC). Proof note
`ADDR-KNOTS-20261113-001B`: [proof.md](../../proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces/proof.md).
The canonical K1–K3 test is unchanged. **Refereed** (ADDR-KNOTS-R1, `referee-R1/report.md`, commit 8c76eef9a): **confirmed with
fixes**, folded in below; one Block (a sentence on tail classes, withdrawn) and six Narrowings, logged in `docs/CORRECTIONS.md`.

## Words

As in the pre-registration: **address** (a binary word), **level** n (the addresses of length n), **address map** (the map an
automaton state defines, the literature's "state", or a product of two), **placement** (a triple of address maps, placing the knot
{g₁x, g₂x, g₃x} at every address x where the three differ), **tail class** (the addresses sharing their last letters, the literature's
tile), **joining knots** (knots holding addresses inside and outside a tail class), **activity** (the literature's term, Sidki 2000).
The fates: F1 **resolves to nothing** (dead at its first level with knots), F2 **ends** (alive at some level, dead at a later one), F3
**alive at every level read**, F0 no knot, FU undecided by the solver's budget; all "within level 12".

## The question

Every nested study before this one let a copy meet the rest through a fixed number of distinctions. Here the knots are placed by a
small automaton on addresses, so each map acts on a tail class's free letters the same way whatever the tail, while which knots stay
inside it and which join it to the rest depend on the tail (*corrected after the referee*), and the number of joining knots may grow
with the level (the owner's "nested structures depend on the larger structures to
know where they are ... it can hop around"). Under a description weighting of A79's kind: how common is each fate, and does how fast
the joining can grow change the fates once knot density is matched?

## The question in standard terms

Two-colourability (NAE-3-SAT) of the 3-uniform hypergraphs {g₁x, g₂x, g₃x} on {0,1}ⁿ, n = 1..12, with the g's words of length at most
2 in the states of a random invertible binary Mealy automaton (s ≤ 5 states), by the Sidki activity class of the relative maps gⱼgᵢ⁻¹,
at matched hyperedge density, under prefix-code sampling (W, 40,000 fair-coin draws) and an exhaustive sweep of the automata with
s = 2 and 3 (E, 19,416 placement lists).

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Shared lists stay finite-state.** A copy that meets every distinction its ancestors put on a shared list, a number growing without bound, still depends on them only through capped counts of values, so life is eventually periodic in depth and decided in the limit (Lemma A). Growing interfaces are not enough to escape finite state; the parts must tell the shared distinctions apart. | proved (known in kind) | the Narrowing of NEST-COUNT's reading |
| 2 | **One placement on two letters always lives** (B0), and so does any description whose placements each mix root swaps (first-letter settled); one placement on seven letters can die at every level (the Fano difference set). | proved; checked | P1 held: 9,731 descriptions with a knot checked, none failed |
| 3 | **Typical: alive at every level read, mostly by construction.** Of the 28,770 accepted W draws, 61.8% have one state map and place no knot, and 18.2% more place none within level 12. Of the 5,759 with a knot, 94.3% are alive at every level read, 5.5% end, 0.3% are undecided; 74.8% are settled by construction (B0 or first letter) under each draw's own flags (79.9% under the addendum's inherited settlement, where a pattern is settled if any description forming it is; *narrowed after the referee: say which*). Of the 1,452 unsettled, 21.6% end within level 12. | computed, frozen | descriptive |
| 4 | **Nothing resolves to nothing.** No pattern in either population is dead at its first level with knots; first deaths fall at levels 3 to 12. | computed, frozen | descriptive |
| 5 | **Death rises with density (an association).** By knots per address (ρ_max, E's distinct patterns), the death share is 0 below 1.5, 0.24% in [1.5, 2.1), 7.4% in [2.1, 3), 23% in [3, 4.5) and 66% from 4.5 on, where a third still live through level 12. | computed, frozen | descriptive |
| 6 | **Joining that can grow is the usual class; bounded joining is a minority and sparse.** By the relative maps' activity, 92% of W's (pattern, class) units (3,669 of 3,997 memberships over 3,990 patterns) and 94% of E's (8,444 of 8,952) are exponential; among W draws with a knot, 88% by weight are exponential, 7.9% bounded, 2.7% polynomial, 1.4% finitary. Bounded and polynomial patterns are sparse (mean ρ_max 1.1 and 1.2 in W, 1.5 and 2.0 in E). The measured joining averages by class at levels 10, 11, 12 (W): bounded 6.7, 6.7, 6.7; polynomial 58, 70, 83; exponential 1,169, 2,303, 4,558. Activity bounds joining only from above: one exponential-class pattern joins with a constant 4 knots. *(Narrowed after the referee from "rare", "doubling" and "typical".)* | exact class; computed joining | check |
| 7 | **Late ends occurred only in the exponential class (an association within level 12).** Bounded patterns die only at level 3 (2 of E's 293); polynomial ones by level 6 (11 of 196); exponential ones first die at every level from 3 to 12 (15 of E's at levels 9 to 12). | computed, frozen | P4 held (21 qualifying descriptions) |
| 8 | **Patterns can die and come back.** 48 descriptions (48 distinct patterns, all exponential, 2.6% of the 1,812 that die) are dead at a level and alive at a later one; 7 alternate with the parity of the level from level 5 on (one is alive at levels 1 to 3, 5, 7, 9 and 11 and dead at 4, 6, 8, 10 and 12). A level is not a growth: level n + 1 lies over level n two to one, and a two-fold lift of a dead pattern can live. | computed, frozen; **certified by the referee** (a checked refutation of a dead level and a verified state of a later live one, for all 48; all 84 levels of the seven, 53 live and 31 dead); the thread's Glucose recheck agreed but left 26 levels undecided. A return is an observed dead-then-live pair within level 12, not a permanent pattern (*narrowed after the referee*) | **P2 failed** |
| 9 | **The matched comparison is testable only where nothing dies.** With settled patterns excluded, one cell is eligible ([1.5, 2.1), bounded against exponential, 36 against 1,092 decided): Δ = −0.007 with undecided read as alive, −0.022 as dead, both "same". So H-dens shows no failure and H-bound fails by its frozen rule. But few die there (0 of 36; 8 of 1,092), and where deaths happen (ρ_max ≥ 2.1) no bounded or polynomial cell reaches 30 patterns. Descriptively, not tested: bounded patterns at ρ_max ≥ 2.1 end in 2 of 27, against about 9 expected at the exponential rates of the same bins; polynomial ones in 11 of 33, against about 12. | computed, frozen | H-dens: no failure observed; H-bound: fails (frozen rule); the question is open where deaths occur |
| 10 | **Checks.** Seven gates passed (V-act, V-rel, V-sat, V-B0, V-act-class, V-code, V-resume); the summary's units passed 37 checks; 287 level verdicts in 125 descriptions were undecided, 47 descriptions are FU; no two descriptions of one pattern gave conflicting decided verdicts. | computed | gates |

## Answer

When nested parts know where they are through an automaton, joining that can grow is the usual case: under a weighting by short
descriptions most patterns are in the exponential activity class, whose tail classes were joined by about 1,169, 2,303 and 4,558
knots on average at levels 10, 11 and 12 (W's patterns; activity bounds joining only from above), and the bounded class, where every
earlier nested result of the program lives, is a minority (7.9% of the W draws with a knot, 3.7% of W's pattern-and-class units, 3.3%
of E's). *(Narrowed after the referee from "almost every pattern ... doubles" and "a few percent".)* Most patterns live at every level
read, three quarters of them for reasons settled by construction. Of the rest about one in five ends, never at once and sometimes
late, and within level 12 the late ends occurred only in the exponential class (an association). Death rises with density (an
association). Whether the growth of
joining matters once density is matched could be tested only where nothing dies, and there it changes nothing; where patterns do
die, bounded ones are too few to test, though they died less often. A fourth fate appears that growth cannot have: a pattern can die
at one level and live again at a later one, in seven cases alternating with the level's parity.

## Reading

**Interpretation, not a theorem.**
- **For the owner's three fates.** "Resolves to nothing" does not occur here, because the first levels place too few knots to die.
  "Goes for a while then dies" is real and uncommon (5.5% of the weight with a knot, a fifth of what construction leaves open).
  "Goes on forever" can only be read as "alive at every level read", and is typical, mostly by construction. The returns are a
  fourth fate that A72's growth excludes: across levels nothing is added; each level is a new pattern lying two to one over the last.
- **For the owner's harmonies.** The parity-alternating patterns are a harmony in the level: whether the pattern lives depends on
  the level's residue modulo 2, within level 12. They are not counters; whether they alternate at every level is open.
- **For "parts that know where they are".** The automaton reading (A82) makes the owner's picture concrete and finitely described,
  and under it the excluded case of the nested line, joining that can grow, is the usual class. The finitely ramified case that the
  program studied before is a minority under this weighting (frequencies above).
- **Growth of joining against density.** The frozen test could not separate them where it matters. The descriptive excess of bounded
  survival at high density fits the expected finite-state behaviour of bounded patterns (die early or never), but it is 27 patterns
  from few automata; it is not evidence that bounded patterns are typically more robust.

## Lag cutoffs and census-only claims

Levels 1 to 12, two letters, at most five state maps, words of length at most 2, placements as frozen, the stated weighting; a SAT
conflict budget of 2,000,000 per level. Nothing is claimed beyond level 12: "alive at every level read" is not "goes on forever", and a
return or an alternation seen to level 12 is not known to persist.

## Literature and provenance

Known: self-similar groups and their Schreier graphs, activity (Sidki 2000), the domino problem and monadic second-order logic on
self-similar graphs (Bartholdi 2022: decidable in the bounded case, undecidable on a linear-activity example; conjecture for contracting
groups), groups of three-state two-letter automata (Bondarenko et al. 2008), rank-width and decidability (Courcelle and Oum 2007),
minimal non-two-colourable hypergraphs (Seymour 1974), the random NAE-3-SAT threshold near 2.1. Not found: the not-all-equal law on
these patterns, a description weighting over automata, the fate census, returns across levels. Ours: everything in the conclusions
table except the classical inputs; Lemma A and the finite-types remark are known in kind, B0 known-with-delta. Classification:
known-with-delta.

## Review

Refereed (ADDR-KNOTS-R1, confirmed with fixes; the referee thread with Codex, fresh code: fresh patterns, recomputed census cells, replayed certificates, relative classes recomputed on 80 units in agreement, a joining check; `referee-R1/`). The advisor model was consulted twice before the freeze (design and spec,
`advisor_design_*.md`, `advisor_review_*.md`): B0's second proof, the rival prediction H-dens, the relative-map class, the settled
exclusion and the expectation of returns are its; its view that higher-order recursion schemes give non-periodic fates is disputed in
the proof note's §3 (unchecked).

## Workspace assumptions

A82 added (the automaton reading of the owner's recursion picture). A79's kind of weighting used; A71 (a census states its result for
its own process only) applies.

## Ratio

Substantive: the proof note and the census. Administrative: the pre-registration, two addenda, this note, the closure.

## Corrections

One, logged at the freeze commit (`docs/CORRECTIONS.md`, 2026-11-13, **Narrowing**): NEST-COUNT's reading "the size of the interface
separates decidable from undecidable nesting" narrowed to the number of ways a copy can be met. P2's failure is a failed prediction,
not a correction.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — fates of knots placed by address maps | **Status:** Partially successful | Fates and classes read within level 12; returns found; the matched comparison testable only where nothing dies |
| Local direction — address maps | Continue | Returns and late ends are new; bounded patterns too sparse in this language to test |
| Broader exploration — G17 nested line | Known alternatives | Bartholdi's decidability side known; growing joining now read under a weighting |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Joining that can grow is the usual class under this weighting, and fates can return across levels |

The attempt leaves open whether the growth of joining changes fates at matched density where patterns die, whether any return or
alternation persists past level 12, and influence across levels, which this census did not read.

**Corrections:** one, Narrowing (above). **Goals:** a G17 checkpoint (with G1), capability gained; no goal change. **Assumptions:** A82
added at the freeze. **Basket:** `BOND-BALLS-20261111-001#2` (2/3 Payoff, 3/3 Concreteness), `ACROSS-FOLD-20261112-001#3` (2/3, 3/3),
`FAR-BOUND-20261112-001#2` (2/3, 3/3), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `PREFIX-END-20261112-001#2` (2/3, 3/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Returns across levels | 2/3 — Substantial | 3/3 — Ready | Read the 48 returning patterns to level 16 and seek a proof for the seven alternating ones through the two-to-one lift → a proved harmony in the level, or alternation that stops | Selected · awaiting go-ahead |
| 2 | Dense bounded patterns | 2/3 — Substantial | 3/3 — Ready | Every bounded automaton with four states, more placements and words of length 3, the frozen matched comparison at ρ_max ≥ 2.1 → bounded patterns die less at matched density, or the same | Alternative · deferred |
| 3 | Reach across levels | 2/3 — Substantial | 2/3 — Testable | Addresses of every length with knots on an address and its extensions plus the placements; exact least bond from the top address to level s ≤ 8, on bounded and polynomial patterns against exponential ones → joining knots bound the reach, or the ruler along levels survives | Alternative · deferred |
| 4 | The law's growth exponent on bounded patterns | 2/3 — Substantial | 2/3 — Testable | Bond balls on finitely ramified patterns (three letters, the Hanoi-type) → a fractional exponent read natively, or only the known graph growth | Alternative · deferred |
| 5 | Finite types | 1/3 — Incremental | 2/3 — Testable | Prove or refute the proof note's §3 for higher-order definitions, depth counted two ways → periodic in unfoldings and not in chain length, or periodic in both | Alternative · deferred |

1. Payoff 2: a fate fixed by the level's residue would be the owner's harmony read in depth, and the first fate in the nested line
   that is not monotone. Concreteness 3: the 48 patterns and the code exist; level 16 has 65,536 addresses, within the solver's reach
   for most; a proof would go through the two-to-one map between levels. Resource: one background run under an hour, then by hand.
   The connection to G17 is the fourth fate; the main uncertainty is whether the alternation is a low-level accident.
2. Payoff 2: it would answer the question this census could not. Concreteness 3: the census code takes a new population.
3. Payoff 2: influence across levels in the owner's sense. Concreteness 2: exact bonds are costly beyond level 8. This census makes it
   more targeted, not less worth doing: typical patterns have exponentially many joining knots, so the informative cases are the rare
   bounded and polynomial ones, where Bartholdi's undecidable example lives.
4. Payoff 2, Concreteness 2: a native fractional exponent would serve G1, but faithfulness probably makes it the known graph growth.
5. Payoff 1, Concreteness 2: settles the disagreement with the advisor.

**Recommendation.** Research directions, #1, awaiting the go-ahead.

## Hand-off to the referee

Folder: this one, the proof family `proofs/ADDR-KNOTS-20261113-001B/`, the code and gates in
`experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/`, the per-description records and
draws in `artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/`. Proved: Lemma A, B0, first-letter
settled, the Fano placement. Computed: everything in the census. Least sure: (a) Lemma A's profile for list knots whose members are
also ports, and (b) the finite-types remark; (c) the relative-class computation through product automata with inverses (*the referee: V-rel checks actions and V-act-class the letter maps, so neither gate validates the class computation; its own recomputation agreed on 80 units*; V-rel checks
the action, not the class); (d) the returns rest on decided solver verdicts; the thread rechecked all 48 with Glucose and its own pattern code (knot
counts equal at every level, every return confirmed), but a refutation is a solver's word, not a certificate;
(e) the descriptive bounded excess in conclusion 9, from few automata.

## Final report as sent

2026-11-13, about 22:25 UTC, to the owner in the project thread:

> The census is done and published; the referee check is still pending. Under the short-description weighting, 94% of patterns
> with a knot live through level 12, three quarters of them for reasons fixed by construction. Parts whose ties to the rest grow
> every level are the typical case. One surprise: 48 patterns die at one level and come back at a later one, and seven of them
> switch between alive and dead with the level's parity, a harmony in depth. I recommend chasing those next.

The same hour, to the coordinator: the result list, both tables and the referee hand-off above, verbatim in substance (the
coordinator's copy carries the five least-sure points of "Hand-off to the referee").
