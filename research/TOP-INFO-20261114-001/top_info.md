# Is reading the whole rule for the bond

Epic `TOP-INFO-20261114-001` (`READ-RULE-20261114-001#2`; G17, with G1), 2026-11-14. Started at the coordinator's go-ahead, which
put it before B173. Pre-registered in c01a7a833 (objects gate passed; advisor consulted), with addenda before the run (815313957) and
after READ-RULE's referee (356669fb1), both before any result was read. The proofs were written in 055654987 and checked by the
advisor. Census code by Codex, run by the thread on the shared runner. The canonical K1–K3 test is unchanged. **Referee pending.
Stress test pending:** the brute-force gate.

## Words

As in `READ-RULE-20261114-001`: L(s), covered targets, carried ports, Theorem R and its exception, the dichotomy. **Bond-pinned** at
depth s: some shattered set T of main's ports and some shattered set D of a covered copy's own distinctions have T ∪ D not full.
**Pinned** (plainly): main's ports and the copy's own distinctions are correlated.

## The question

Is the bond bounded on a residue exactly when some carried value is read there, outside Theorem R's exception, and linear otherwise?
If not, what else bounds it?

## The question in standard terms

For iterated hyperedge-replacement NAE instances, which finite conditions at the root and at the target decide whether the least
minimal non-shattered set through a root vertex and a depth-s vertex stays bounded.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The rule is false, in both directions.** Bounded without an effective reading: the 93 order-label families (nothing is carried to large depths), READ-RULE's 9 exception families, and 486 others, mostly identity families (588 in scope with such a residue). Growing with a reading: READ-RULE's referee's family, whose carried values are read only inside the exception. What holds is one direction, a theorem: an effective reading at infinitely many depths of a residue bounds the bond there. | computed; known before the run | — |
| 2 | **Bond-pinning is a second sufficient condition, proved (Theorem P′).** Shattered sets of main's ports and of the target copy's own distinctions that are jointly non-full contain a bond of at most their total size. No grower is bond-pinned or plainly pinned at a large depth (0 of 632), as the theorem requires. | proved; computed | T1 held; gate held |
| 3 | **Reading or pinning explains almost all of the bounded half.** Of the 5,074 bounded in-scope families: 4,484 have an effective reading on every residue (3,515 of them also bond-pinned), and 523 more are bond-pinned on every residue without one. Only **65 (1.3% of the bounded weight)** have neither on every residue: 50 identity families and 15 order-label families. Their bonds use members between the top and the target. In the census, plain pinning and bond-pinning never differ, so the advisor's hiding relation does not occur. | computed | — |
| 4 | **Not every order family is bond-pinned.** 78 of the 93 are bond-pinned on every residue; 15 are not, and they are bounded through middle members. | computed | **T2 failed** (15 of 93) |
| 5 | **The two-block window decides a few more.** With main's whole block in the window, 9 of the 83 undecided in-scope families are bounded on every residue. Two more undecided families, 432127c418b0 and 981fdc202826, have an effective reading on every residue of a complete window, so Theorem R and the dichotomy bound them too: 11 newly bounded in all, 72 undecided. | proved per family | **T3 failed** (9 by the frozen count, threshold 10) |
| 6 | **Localisation, proved; decidability open.** If L is bounded on a residue, some bond of bounded size lies within a computable number of levels of the root and of the target, apart from one long member-free stretch. A search over growing windows therefore finds every bounded case, but without an a priori size bound a "no" is never certified. | proved | — |
| 7 | **Gates.** Theorem R and bond-pinning never apply to a grower. The two-block window never undercuts the gap bound on 100 forgetting families, and never exceeds the one-block window where both bound (0 violations; 84 families unavailable through caps). **Stress test pending:** the brute-force gate on 30 identity families (registered as TOP-INFO-brute30) is still running and will be folded in. | computed | G: no violation so far (brute force pending) |

## Answer

Reading is not the whole rule. The law keeps the top within reach of a deep copy in three ways:
- **Effective reading.** A value carried down is read by a knot next to the copy's own, and no tie splits that knot (88% of the
  bounded families, on every residue).
- **Pinning.** The top's ports and the copy's own distinctions are directly correlated, with nothing carried, as in the order
  families (another 10%).
- **Middle members.** In 1.3% the bond needs members between the top and the target.

Each of the first two is a proved sufficient condition, and neither alone is necessary. The converse of the whole, that every bounded
case shows up in a bounded window at the top and at the target, is proved. Whether that can be decided in advance, family by family,
is open.

## Reading

**Interpretation, not a theorem.**
- **Information, not carrying.** What keeps the top within reach is information about the top in the deep copy's own distinctions:
  carried and read, or pinned by an order, and rarely relayed through the middle. A value carried but unread, or read only inside a
  tie, keeps no information the bond can use.
- **The open edge.** The 72 undecided families and the 65 middle-member families are where a rule beyond reading and pinning would
  have to be found.

## Lag cutoffs and census-only claims

Theorem P′, the two-block bound and localisation hold for every living in-scope family. The shares are census facts.

## Review

**Referee pending.** The advisor model was consulted before the freeze (`advisor_review_answer.md`: plain pinning refuted by its
hiding relation, the bond-pinning repair, the two-block form) and on the proofs (`advisor_proof_answer.md`: no error in P′ or the
two-block bound; three fixes to localisation, adopted; a route to decidability, not checked).

## Literature and provenance

Known: minimal non-shattered sets inside correlated sets, finite-monoid pumping. Ours: the census split of the bounded half into
reading, pinning and middle members, and the two-block window. Classification: known-with-delta.

## Workspace assumptions

A79 and A81 used.

## Ratio

Substantive: 5,964 families checked, 961 two-block windows, three proofs. Administrative: the freeze, two addenda, this note.

## Corrections

None. T2 and T3 are frozen predictions that failed.

## Data

`experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/`: Codex's `codex/` (`checks.py`, `two_block.py`,
`two_block_brute.py`, `job.py`, `summarize.py`, `summary.json`, `results.json`, `REPORT.md`, the run in `census_full/`), and the
thread's `brute30.py` with `brute30.json`, the frozen brute-force gate. Proofs: `proofs/TOP-INFO-20261114-001B/`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the whole rule | **Status:** Successful (referee pending) | The stated rule refuted both ways; two proved sufficient conditions explain 98.7% of the bounded weight; localisation proved |
| Local direction — counting inside | Continue | 72 undecided and 65 middle-member families remain |
| Broader exploration — G17 | Searching | The bounded half explained by information about the top in the deep copy |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Three mechanisms of bounded reach, two proved |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1; no goal change. **Assumptions:** A79 and A81 used.
**Basket:** `B173` (2/3 Payoff, 2/3 Concreteness; next in line), `CARRY-BOUND-20261114-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other recursive definitions as targets (B173) | 2/3 — Substantial | 2/3 — Testable | The coordinator's next in line: the typed window on the 175 out-of-scope families and CENSUS-FORGET's 188 → bounded or growing with every recursive target | Selected · next in line |
| 2 | Decide boundedness | 2/3 — Substantial | 1/3 — Exploratory | Check the advisor's finite-type route to an a priori bound on the least bounded value → boundedness decidable per family, or a gap | Alternative |
| 3 | The middle-member bonds | 1/3 — Minor | 2/3 — Testable | The 65 families' least bonds: what the middle members relay → a third sufficient condition | Alternative |

1. Payoff 2: removes the covered-target caveat. Concreteness 2.
2. Payoff 2: would make the bounded-or-linear split computable. Concreteness 1: an unchecked sketch.
3. Payoff 1: 1.3% of the bounded weight. Concreteness 2.

**Recommendation.** Research directions, #1, as the coordinator set.
