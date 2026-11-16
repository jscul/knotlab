# Exact reach at every depth from blocks of orbits

Epic `BLOCK-REACH-20261116-001` (`DIRECT-REACH-20261115-001#1`, at the coordinator's go-ahead, 2026-11-16 20:30 UTC; G17, with G1),
2026-11-16. Proof note: [proof.md](../../proofs/BLOCK-REACH-20261116-001A/BLOCK-REACH-20261116-001A-P001_forgetting_blocks/proof.md).
Code by the thread. The canonical K1–K3 test is unchanged. **Refereed** (BLOCK-REACH-R1, [report](referee-R1/report.md), commit
68f92ea96): **confirmed with fixes**, no Block; Theorem F (both cases), the block step and Lemma U hold, and the forgetting lengths
recompute on all 786. Folded in below and logged in `docs/CORRECTIONS.md`: an index in the proof, the predictions' time, and an exact
result the study missed.

## The question

`DIRECT-REACH-20261115-001` proved, with blocks of orbits, that direct reach stays bounded at every depth wherever the maps' orbits
stay small. Can blocks also say, at every depth, how the reach grows where it grows: the census's rulers (one member more per level,
including the cyclic ones that the hypertree theorem does not cover, backlog B180), its half-rate profile and its undecided
descriptions? Population: the 786 alive descriptions of the `LEVEL-REACH-20261114-001` census whose orbits have at most four
addresses.

## Answer

**Every small-orbit ruler and half-rate description provably keeps growing at every depth, at least linearly, and the census's
depth-9 values bound them from above at every depth; the exact rate is open, and cyclic rulers forget more slowly than acyclic ones.**

The tool is the nested line's forgetting bound (`BRANCH-DEPTH-20261112-001A`), moved onto blocks. Follow the orbits from the top
orbit down to the target's orbit, and treat each block step (an orbit's assignment to its child orbit's assignment, the block's
knots holding and the other children's subtrees feasible) as one group. If every run of r consecutive steps forgets, meaning that any
value that can enter it combines with any value that can leave it, then a bond cannot skip r levels in a row, so it needs at least
1 + ⌈s/r⌉ members to reach s levels down (**Theorem F**, proved). Separately, the projection onto addresses at levels at most m
does not depend on the depth once the depth is r₀ past m (**Lemma U**, proved), so every least bond the census found at
depth 9 stays a bond at every depth.

| Census profile (depth 9) | Small orbits | Forget (r = 1 / 2 / 3) | Never forget | At every depth N ≥ 3 + s |
| --- | ---: | --- | ---: | --- |
| ruler, no cycle of knots | 245 | 197 / 47 / 1 | 0 | grows; 1 + ⌈s/r⌉ ≤ L ≤ depth-9 value (s ≤ 4) |
| ruler, with cycles | 154 | 31 / 105 / 18 | 0 | grows, mostly at rate at least 1/2 |
| half-rate [3, 3, 4, 4] | 43 | 0 / 19 / 24 | 0 | grows, rate at least 1/2 or 1/3 |
| undecided | 8 | 0 / 0 / 6 | 2 | 6 grow |
| other (13 with no bond of at most 10 members past s = 1; [3, 4, 4, 5], [3, 4, 4, 4], [3, 4, 5, 5]) | 16 | 5 / 8 / 1 | 2 | 14 grow |
| no bond at depth 9 | 278 | 278 / 0 / 0 | 0 | — |
| direct | 42 | — | 42 | bounded (`DIRECT-REACH-20261115-001`) |

So among small orbits, forgetting decides growth: every description that forgets grows at every depth (740 of 786), and of the 46
that never forget, 42 are proved bounded and 4 are open ([3, 4, 4, 4], [3, 4, 5, 5] and two partly undecided). None is known to
never forget and grow. The bound is one below the census's values for most rulers (s + 1 against s + 2 when r = 1) and half-rate
descriptions. Where Theorem W shows no tie at any depth (all 43 half-rate and all 399 rulers) the bound is max(3, 1 + ⌈s/r⌉), and
then **the reach is exact at the first levels**: L_N(3, s) = 3 at every depth N ≥ 9 for s = 1 and 2 in every half-rate description
(found by the referee, SAT-confirmed at N = 12) and for s = 1 in every ruler (the same argument, not refereed separately). The gap is
then 0 in 86 and 1 in 86 of the 172 half-rate cells, and 0 / 1 / 2 / 3 in 399 / 855 / 171 / 171 of the 1,596 ruler cells. *(Corrected
after the referee: the gap had been measured against the bare bound, "1 in 1,083 of the 1,596 ruler cells and 148 of the 172
half-rate cells".)*

**B180, the cyclic rulers.** 154 of the census's 158 cyclic rulers have small orbits, and all grow at every depth. But they forget
more slowly: r = 1 for 20% of them against 80% of the acyclic rulers, so for most the theorem proves a rate of at least 1/2 where the
census reads 1 per level. Why the cyclic ones still read as rulers is the same open question, now sharper: their two-level stretches
forget, their one-level stretches mostly do not.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Theorem F: forgetting windows of r block steps give L ≥ 1 + ⌈s/r⌉ at every depth and every s | proved (from the splicing lemma of `BRANCH-DEPTH-20261112-001A`) |
| 2 | Lemma U: projections onto addresses at level ≤ m are the same at every depth ≥ m + r₀ | proved |
| 3 | 740 of 786 small-orbit descriptions forget (r ≤ 3, the same at every remaining depth); every ruler, half-rate and 6 of 8 undecided grow at every depth | computed; 100 window relations equal SAT, no census value below the bound |
| 4 | Every depth-9 least bond of the 786 holds at every depth: L_N ≤ L_9 for s ≤ 4 and N ≥ 9; exact L = 3 at s = 1, 2 for the 43 half-rate (the referee) and at s = 1 for the 399 rulers | computed; 158 bonds' projections equal by SAT at depths 9, 10, 11 (the referee: 132 at 9, 12, 13) |
| 5 | Cyclic rulers forget more slowly (r = 1 in 20% against 80%) | computed |

## Predictions

Frozen in [predictions.md](predictions.md) (committed in 169c0d53f at 20:45 UTC, before the census output first appeared in 6c9ce0f8a at
20:50 UTC; the exploratory stable-depth lengths had been seen; the file's own stamp, 21:00, was corrected after the referee).

- **P1 holds.** The forgetting length at every remaining depth equals the stable one in all 786 (needed: 40 of 43 half-rate, 90% of
  the rulers).
- **P2 holds.** The closure confirms that the 42 direct and the 4 others never forget.
- **P3 fails.** r = 1 for 20.1% of the small-orbit cyclic rulers against 80.4% of the acyclic ones, 60 points apart (predicted within 15).
- **P4 holds.** All 1,596 decided ruler cells (and every decided cell of the 786) have their depth-9 bond within levels 9 − r₀.

## Lessons

- The nested line's theorems transfer to addressed patterns once orbits are small: a block step is a group with a finite interface.
  Reusing it gave the lower bound quickly; the upper bounds for every s still need the nested line's other tool, fixed-size reachability
  over marked tables.
- A bound that holds at every depth can still be weak at every depth: forgetting proves growth but not the ruler's rate for cyclic
  rulers.

## Advisor

Used once, on the design before freezing (`advisor_design_answer.md`): the transfer is sound; it asked for the closure deciding
"never forgets" (done), counting empty windows (none), the two depth tiers (both agree), a falsifiable third prediction (the cyclic
split, which failed), and it proposed Lemma U for upper bounds at every depth (done).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — growth at every depth from blocks | **Status:** Successful | Every small-orbit ruler and half-rate grows at every depth; exact rates open |
| Local direction — blocks of orbits | Continue | Exact rates need a marked window or marked tables |
| Broader exploration — G17 nested line | Known alternatives | The nested line's fixed-size tool is the next to transfer |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Small orbits: forgetting decides bounded or growing, 782 of 786 |

The bridge to G1 is the ruler's rate: a reach of one member per level is the program's bond distance, and for cyclic rulers it is
read only to depth 9.

**Corrections:** none. **Goals:** a G17 checkpoint (with G1), capability gained. **Assumptions:** A83 and A82 used; none added.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Exact rates from marked windows | 2/3 — Substantial | 2/3 — Testable | Test whether one-step windows of the cyclic rulers forget once one member is pinned in them, which would give s + 2 → a ruler at every depth for those, or the pinned windows that still remember | Selected · awaiting go-ahead |
| 2 | Upper bounds for every s by marked block tables | 2/3 — Substantial | 2/3 — Testable | Adapt `BRANCH-DEPTH-20261112-001D`'s fixed-size reachability to blocks for sizes up to 6 → exact L at every s where L ≤ 6, or tables too large | Alternative · deferred |
| 3 | The four that never forget | 1/3 — Incremental | 2/3 — Testable | Decide boundedness of [3, 4, 4, 4] and [3, 4, 5, 5] with direction 2's tables at size 5 → bounded, or a growth certificate | Alternative · deferred |
| 4 | Growing orbits | 2/3 — Substantial | 1/3 — Stated | Find a finite interface for descents where orbits grow (502 census descriptions) → one family with a forgetting bound, or none | Alternative · deferred |

1. Payoff 2: would answer B180 for cyclic rulers at every depth and make the rate exact where the theorem is one short. Concreteness 2:
   the census's rulers have exact depth-9 values to test against, and pinning one member is a small change to the gate-checked
   window code; the main uncertainty is whether pinned windows forget at all.
2. Payoff 2: exact reach at every s, not only s ≤ 4. Concreteness 2: the method is proved in the nested line; the table sizes for
   orbits of four addresses are unknown.
3. Payoff 1: would close the small-orbit dichotomy. Concreteness 2: four cases, needs direction 2's tool.
4. Payoff 2: most of the census. Concreteness 1: no finite interface is known when orbits are whole levels.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead.

## Hand-off to the referee

Folder: this one (note, predictions, advisor Q/A, `forget.py`, `gate_forget.py`, `gate_upper.py`, `run_census.py`, `census_forget.json`,
`exploratory/`); the proof family `proofs/BLOCK-REACH-20261116-001A/` (`proof.md`, `check.py`, `result.json`). Proved: Theorem F and
Lemma U. Computed: Corollary F and the upper bounds. Least sure: (a) the group bookkeeping in Theorem F's Case 2 (the top member in a
side subtree of the first step); (b) that a block step leaves the child orbit unrestricted by its own subtree, as the splicing lemma's
groups require; (c) Lemma U's use of F at the boundary level, checked by SAT only to depth 11.
