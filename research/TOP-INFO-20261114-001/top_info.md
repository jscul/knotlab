# Is reading the whole rule for the bond

Epic `TOP-INFO-20261114-001` (`READ-RULE-20261114-001#2`; G17, with G1), 2026-11-14. Started at the coordinator's go-ahead, which
put it before B173. Pre-registered in c01a7a833 (objects gate passed; advisor consulted), with addenda before the run (815313957) and
after READ-RULE's referee (356669fb1), both before any result was read. The proofs were written in 055654987 and checked by the
advisor. Census code by Codex, run by the thread on the shared runner. The canonical K1–K3 test is unchanged. Refereed by the referee thread with Codex (TOP-INFO-R1, `referee-R1/report.md`, commit
94befcf5c): **confirmed with fixes, one Block on "middle members"**. The three theorems stand, localisation with proof repairs; the
counts are restated below. **Stress test pending:** the brute-force gate.

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
| 1 | **The rule is false.** *Narrowed after the referee:* for the rule as asked (with R's exception), only "bounded ⇒ effective reading" fails; the referee's growing family refutes only the syntactic rule. Bounded without an effective reading: the 93 order-label families (nothing is carried to large depths), READ-RULE's 9 exception families, and 486 others, mostly identity families (588 in scope with such a residue). Growing with a syntactic reading: READ-RULE's referee's family, whose carried values are read only inside the exception. What holds is one direction, a theorem: an effective reading at infinitely many depths of a residue bounds the bond there. | computed; known before the run | — |
| 2 | **Bond-pinning is a second sufficient condition, proved (Theorem P′).** Shattered sets of main's ports and of the target copy's own distinctions that are jointly non-full contain a bond of at most their total size. No grower is bond-pinned or plainly pinned at a large depth (0 of 632), as the theorem requires. | proved; computed | T1 held; gate held |
| 3 | **Reading or pinning explains almost all of the bounded half.** Of the 5,072 bounded in-scope families of CARRY-BOUND's strict count (*corrected after the referee*: the advertised 5,074 includes b47bcba2eb6c and 530dbea3fe7b, whose flags are unavailable), 4,484 have an effective reading on every residue (3,515 of them also bond-pinned), and 523 more are bond-pinned on every residue without one (436 identity, 78 order-label, 5 tie, 4 other). **65 are not explained on every residue by reading or bond-pinning** (50 identity, 15 order-label). By family that is 88.37%, 10.31% and 1.28%; by weight 87.44%, 11.25% and 1.27%, with 0.04% unavailable. *Corrected after the referee (Block):* ~~their bonds use members between the top and the target~~. In three of the 65 (fea4933ecaf1 and 5ceea39607cb, order-label; fd60333c5872), complete certificates find eventual bonds using only main's block and the target copy: for fea4933ecaf1, {main port 1, main's own distinction 8, an own distinction of the target} at depth 4, with bound 3. P′ misses them because one top member is main's own distinction, not a port. The 65 are a residue, not a mechanism. *Narrowed after the referee:* ~~the advisor's hiding relation does not occur~~. Plain pinning and bond-pinning agree on every family's flags, but hiding occurs in word states (order-label aab77be157e5: 24 plainly pinned states, 22 bond-pinned, no cross bond). | computed | — |
| 4 | **Not every order family is bond-pinned.** 78 of the 93 are bond-pinned on every residue; 15 are not, and they are bounded through middle members. | computed | **T2 failed** (15 of 93) |
| 5 | **The two-block window decides a few more.** With main's whole block in the window, 9 of the 83 undecided in-scope families, all wrappers, are bounded on every residue; their bounds (at most 4) are upper bounds, not exact values. Two more undecided families, 432127c418b0 and 981fdc202826, have an effective reading on every residue of a complete window, so Theorem R and the dichotomy bound them too. *Narrowed after the referee:* they already had complete window certificates of 3, so this is a second proof, not a new bound. In scope the census now stands at **5,085 bounded, 632 growing, 72 undecided** (weights 5,147, 634 and 72). | proved per family | **T3 failed** (9 by the frozen count, threshold 10) |
| 6 | **Localisation, proved; decidability open.** If L ≤ C eventually on a residue, then at every large depth on it **some** least bond lies within a number of levels of the root and of the target that is computable *given C*, apart from one long member-free stretch (*narrowed after the referee*: not every least bond, as a synthetic family with a member 23 levels below the target shows; the proof is repaired as the referee set out). It is a normal form for witnesses. Semi-decision of boundedness already followed from the dichotomy, and without an a priori bound on C a "no" is never certified. | proved | — |
| 7 | **Gates.** Theorem R and bond-pinning never apply to a grower. The two-block window never undercuts the gap bound on 100 forgetting families, and never exceeds the one-block window where both bound (0 violations; 84 families unavailable through caps). **Stress test pending:** the brute-force gate on 30 identity families (registered as TOP-INFO-brute30) is still running and will be folded in. | computed | G: no violation so far (brute force pending) |

## Answer

Reading is not the whole rule. The law keeps the top within reach of a deep copy in two proved ways:
- **Effective reading.** A value carried down is read by a knot next to the copy's own, and no tie splits that knot (88.4% of the
  bounded families, on every residue).
- **Pinning.** Some of the top's ports and the copy's own distinctions are jointly constrained (another 10.3%: 436 identity
  families, 78 of the order families, 9 others).

The remaining 1.3% are a residue, not a mechanism. In three of them, a form of pinning that also uses main's own distinctions finds
the bond (*corrected after the referee*; the first version called them bonds through middle members). Every bounded case has some
least bond in a window at the top and at the target, whose size is computable once the bound is known. Whether boundedness can be
decided in advance, family by family, is open.

## Reading

**Interpretation, not a theorem.**
- **Information, not carrying** (interpretation). What keeps the top within reach is information about the top in the deep copy's own distinctions:
  carried and read, or pinned by an order, and in a few cases by distinctions of the top's own block. A value carried but unread, or read only inside a
  tie, keeps no information the bond can use.
- **The open edge.** The 72 undecided families and the 65 unexplained families are where a rule beyond reading and pinning would
  have to be found.

## Lag cutoffs and census-only claims

Theorem P′, the two-block bound and localisation hold for every living in-scope family. The shares are census facts.

## Review

**TOP-INFO-R1**: confirmed with fixes, one Block (above). The advisor model was consulted before the freeze (`advisor_review_answer.md`: plain pinning refuted by its
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

From the referee (`docs/CORRECTIONS.md`, 2026-11-14):
- **Block.** "Middle members" is withdrawn: the 65 are a residue, and three are explained by main's block and the target copy.
- **Narrowing.** Hiding occurs in word states. Localisation holds for some least bond, with a window computable given C. The
  two-block start convention is stated, and its 9 new bounds are upper bounds. The counts: 5,072 strict, 2 unavailable, the two R
  families a second proof, 5,085 / 632 / 72 final. "False in both directions" applies to the syntactic rule only. The 523 are
  mostly identity families. Family and weight shares are kept apart.
- **Not a block.** The localisation proof's repairs.

T2 and T3 are frozen predictions that failed.

## Data

`experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/`: Codex's `codex/` (`checks.py`, `two_block.py`,
`two_block_brute.py`, `job.py`, `summarize.py`, `summary.json`, `results.json`, `REPORT.md`, the run in `census_full/`), and the
thread's `brute30.py` with `brute30.json`, the frozen brute-force gate. Proofs: `proofs/TOP-INFO-20261114-001B/`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the whole rule | **Status:** Successful (refereed, confirmed with fixes, one Block) | The stated rule refuted; two proved sufficient conditions explain 98.7% of the bounded families; localisation proved |
| Local direction — counting inside | Wrap up (the coordinator's call) | 72 undecided and 65 unexplained families remain; recorded as backlog |
| Broader exploration — G17 | Searching | The bounded half explained by information about the top in the deep copy |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Three mechanisms of bounded reach, two proved |

**Corrections:** from the referee, one Block, several Narrowing and a proof repair. **Goals:** a checkpoint for G17 and G1; no goal change. **Assumptions:** A79 and A81 used.
**Basket:** `B173` (2/3 Payoff, 2/3 Concreteness; next in line), `CARRY-BOUND-20261114-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other recursive definitions as targets (B173) | 2/3 — Substantial | 2/3 — Testable | The coordinator's next in line: the typed window on the 175 out-of-scope families and CENSUS-FORGET's 188 → bounded or growing with every recursive target | Selected · next in line |
| 2 | Decide boundedness | 2/3 — Substantial | 1/3 — Exploratory | Check the advisor's finite-type route to an a priori bound on the least bounded value → boundedness decidable per family, or a gap | Alternative |
| 3 | Pinning with main's whole block | 1/3 — Minor | 3/3 — Ready | P′ with T drawn from main's whole block, on the 65 unexplained families → how many it covers (at least 3) | Alternative · backlog |

1. Payoff 2: removes the covered-target caveat. Concreteness 2.
2. Payoff 2: would make the bounded-or-linear split computable. Concreteness 1: an unchecked sketch.
3. Payoff 1: 1.3% of the bounded families. Concreteness 3: the proof is P′'s, and the window exists.

**Recommendation.** The coordinator has wrapped up this line. The directions are recorded as backlog, and the line's summary is in
`research/TOP-INFO-20261114-001/line_summary.md`.
