# Independent R/R1 coverage audit

**Verdict: Confirmed with fixes.** The local exception of Theorem R is exact, R1's proof and frozen syntactic condition are sound, and the reported R1 counts reproduce. The theorem-correct existential R reading raises bounded draw-weight coverage from **87.463443%** to **87.560928%**. The five quantifier-affected cases are resolved positively; exactly nine exception-only families remain, and 68 capped cases remain unknown.

This is the assigned points 2 and 3 lane within `READ-RULE-20261114-001`. No READ producer Python was opened or imported, no network was used, and only `coverage_*` files in this referee directory were written. No Git mutation, publication, lifecycle edit, foundational change, or new terminology was made. Earlier permitted CARRY referee algorithms are reused transparently. Validation is V2, independent same-task recomputation and SAT, without external replication.

## 2. Theorem R

For three distinct positions, positive NAE has three antipodal pairs of allowed states. Exhausting their seven nonempty unions exhausts every nonempty complement-closed triple projection satisfying NAE. A separate generic support enumerator checks all inclusion-minimal non-shattered subsets, rather than assuming the pair/triple case split. Exactly two projections lack a bond through both p and x:

- allowed integer rows `[1,3,4,6]` (bit order p, x, z): p and x are free, z is opposite to p;
- allowed rows `[2,3,4,5]`: p and x are free, z is opposite to x.

The other five projections contain the required bond. An opposite tie to both p and x instead ties p to x and is a positive two-member case. Empty/dead relations are explicitly outside the living hypothesis and rejected by the generic reference checker. A signed-NAE control shows why the positive sign hypothesis matters. The identity case z = p yields the p-x opposite pair; it does not supply a third distinct member.

**Not a block — scope of exactness.** This equivalence concerns bonds inside W. The exception does not assert that the whole family lacks another small bond. All nine census exception families have other bonds of size at most three.

The Q-state sets are independently reconstructed from raw family keys using the earlier CARRY referee's greatest-limit, call-projection and identity-partition algorithms. All **5,717 complete in-scope Q orbits** reproduce the digest's preperiod and period. Candidate enumeration, pendant syntax, carried masks, local projections, tie tests, and both state quantifiers are fresh READ code. There are **2,152** cross-checks against the earlier referee's separate whole-window enumerator. No official R/R1 flag supplies the recomputed result; those flags are read only for comparison.

For every exact Q phase, the correct predicate is: some eligible carried q and some reading candidate survive. Every repeating Q phase must satisfy that predicate for every-large-depth coverage. The stricter predicate fixes a candidate and requires it to survive every eligible carried state, as grouped in the study's R residue. Pooling Q phases before asking for one survivor would be an invalid general replacement; a deliberately constructed control rejects it. The two readings happen to agree on that pooling issue in this census.

| Coverage predicate, original window-bounded in-scope population | Families | Draw weight / 5,129 | Weight share |
| --- | ---: | ---: | ---: |
| Stronger every eligible carried-state reading | 4,479 | 4,486 | 87.463443% |
| Theorem-correct some-state reading, in every exact Q phase | 4,484 | 4,491 | 87.560928% |

The denominator is **5,067 families**, weight **5,129**. The difference is five weight-one families, or **0.0974849 percentage points**. Asking only for some successful Q phase would wrongly count 4,489 families and weight 4,496 as every-depth coverage. All recomputed successful phases have recorded U ≤ 3; no gate violation occurs. The stricter recount agrees with every supplied study carried-state flag.

**Not a block — quantitative completion.** The stated 87.5% is the correctly rounded stronger lower bound. It is not the exact coverage under the theorem's existential quantifier.

The five additional cases are also exactly the five complete-window Q1 ambiguities. Each is an original CARRY stratum-I bounded wrapper, weight one; none remains exception-only:

| Key SHA-256 prefix | Q preperiod | Q period | Every exact phase has a surviving reading |
| --- | ---: | ---: | --- |
| `5dd5ab5a117eb660` | 6 | 1 | yes |
| `52997167e985b8f4` | 8 | 2 | yes |
| `7ecf57750d7d2775` | 7 | 1 | yes |
| `63577d9cf381049f` | 10 | 2 | yes |
| `39f7b334062ac725` | 12 | 4 | yes |

All ten phase witnesses have independently unfolded CNF/SAT certificates. Full keys, original classifications and caps are retained in `coverage_reconciliation.json`.

The exact exception-only list remains:

| Key SHA-256 prefix | Independently checked Q states | Eligible readings | Other bond in representative word |
| --- | ---: | ---: | ---: |
| `018277ebab1de9a6` | 34 | 68 | 3 |
| `8e8c03006cbcc448` | 88 | 176 | 3 |
| `3fbe34294e00b1fa` | 486 | 1,044 | 3 |
| `c2850e10ae4f9743` | 16 | 34 | 3 |
| `33e3211faac70b6b` | 174 | 400 | 3 |
| `0235fe8965b7f432` | 1 | 2 | 3 |
| `8840b0164bc946d1` | 16 | 40 | 3 |
| `23df2a825b7b0e33` | 82 | 188 | 3 |
| `c6c99c623a5487a0` | 2 | 4 | 3 |

The nine contribute **899 Q states / 1,956 reading checks**. Each projected triple is recomputed by exact SAT on its concrete word, with exact off-word subtree limits, and matches the independent Q reconstruction. The relation-free support search also checks twenty nonexception controls, including nine controls matched to exceptions, all five quantifier rescues, and longer-period examples: **919 Q states / 1,996 candidate checks** in total. All twenty have a bond of at most three, and every candidate marked surviving has the required bond inside W. Search uses no per-call relation or composition code; those algorithms are used only to reconstruct the concrete-word roster. Every reported support is rechecked using a second SAT solver, including every one-member deletion.

A further per-phase search supplies other bonds of at most three in **all twenty repeating Q phases** of the nine exception families. These witnesses establish the claimed upper bounds. Their least sizes are exact over the explicitly unfolded word's member universe; this audit does not infer a global lower bound of three by excluding members elsewhere.

The updated Q1 status is nine exact exception-only, **68 unknown**, and **5,712 definitely not exception-only** among 5,789 in-scope families. There are 72 incomplete in-scope Q windows, but four have no reading candidate and therefore cannot be exception-only. The study's 73 unresolved cases were these 68 capped cases plus the five now-resolved quantifier cases. Capped evidence remains unknown.

## 3. Theorem R1

When z is own, in exactly one constraint and in no call argument, any allowed state of the rest extends with exactly the z-values satisfying its NAE constraint. Hence the triple projection is P(p,x) conjoined with NAE. The three nonempty complement-closed P relations are the equal pair, opposite pair and full pair; direct enumeration confirms the required two- or three-member bond in all three cases. This verifies the proof's substantive step.

The frozen syntax excludes arguments of finite helper calls as well as SELF calls. The fresh implementation retains those arguments before inlining, so an occurrence cannot disappear from the call-argument guard during flattening. Ten hand-specified controls check this guard, a repeated constraint, both own-role choices, a non-own third member, an unread carried position, automatic port-only knots, and wrapper carriage. All 5,964 family candidate rosters, carried sequences and R1 flags agree with the study.

| R1 population | Families | Draw weight |
| --- | ---: | ---: |
| Every residue, all in-scope | 471 | 471 |
| Every residue, window-bounded in-scope | 469 | 469 |
| Some residues only, in-scope | 1 | 1 |

Thus **469 / 5,067 = 9.255970% of families**, and **469 / 5,129 = 9.1440827% of bounded draw weight**, reproducing the stated 9.1441%.

**Not a block — 471 versus 469.** The two additional all-in-scope cases are `d5ac8dc038ae968e` and `ce083ff8262fab67`. Both are original CARRY stratum I, undecided, weight one, without a complete Q window. Their recorded caps are the inherited census semigroup length-set cap, Q stored-state cap, and P_n product cap. Their syntactic R1 predicates are proved independently of those caps, while the stated bounded-population denominator preserves CARRY's frozen classification. They are not missing bounded rows.

This lane uses the window-stage population, before path-DP rescues. It does not replace the historical 83-versus-90 discussion with an invented roster.

## Evidence and replay

All commands ran sequentially with the workspace interpreter and no network:

```text
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/READ-RULE-20261114-001/referee-R1/codex/coverage_run.py --limit 20
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/READ-RULE-20261114-001/referee-R1/codex/coverage_run.py
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/READ-RULE-20261114-001/referee-R1/codex/coverage_controls.py
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/READ-RULE-20261114-001/referee-R1/codex/coverage_direct.py
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/READ-RULE-20261114-001/referee-R1/codex/coverage_reconcile.py
```

The complete coverage pass took **339.19 s**, peak RSS **289,592 KiB**. The 29-family direct audit took **12.86 s**, peak RSS **248,836 KiB**. The thirty per-phase certificates took **7.28 s**. Each invocation stayed below fourteen minutes and used one computational process with a 2 GiB address-space ceiling.

Principal files: `coverage_run.py`, `coverage_results.jsonl`, `coverage_summary.json`, `coverage_triples.json`, `coverage_controls.py`, `coverage_controls.json`, `coverage_direct.py`, `coverage_direct.json`, `coverage_direct_states.jsonl`, `coverage_reconcile.py`, `coverage_reconciliation.json`, and this report. Final outputs subsume the smoke and progress records; those duplicate scratch files were removed. The manifest binds current scripts, inputs and outputs.

Limitations: family draw weights and original CARRY classification are inherited data, not a fresh sampling run. Exact finite projections rely on the admitted greatest-limit and off-word separation semantics. No finite census or direct-word sample establishes the infinite-system dichotomy, a generic complexity claim, or any foundational reinterpretation.
