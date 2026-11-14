# CARRY-BOUND R1: scope, census split, frozen rule and wording

**Verdict: the scope and advertised census arithmetic reproduce. Narrowing is needed in the exposition and in the distinction between frozen trial classifications and mathematical certificates. No Block was found by this lane.** The certificate-validity arguments themselves belong to the other referee lanes; this recount does not establish their soundness.

Enclosing scope: `epic CARRY-BOUND-20261114-001`; R1 points 3–6 only. The fresh calculation is `scope_audit.py`, its machine-readable evidence is `scope_audit.json`. Run:

```text
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/CARRY-BOUND-20261114-001/referee-R1/codex/scope_audit.py
```

The final replay took 1.61 seconds, peak RSS 188,820 KiB, with a 768 MiB address-space limit. No network, state-changing Git command, forbidden study Python, or outside scientific source was used. Scope predicates, occurrence-counted chain membership, identity cycles, carried-position iteration, knot-meeting positions and liveness were reimplemented. The permitted earlier referee supplied the explicit usual-limit language convention; its study implementations were not imported. This is V2 same-task independent recomputation, not external replication.

## 3. Structural scope and denominators

The fresh structural predicates agree with **every one of the 5,964** CARRY digest scope flags. They also reproduce the other-own predicate and exact inlined-own counts in **all 657** earlier `target_inventory.json` rows, including the 119 rows overlapping CARRY. Checking the second predicate independently gives the following exclusions:

| CARRY population | Families | Draw weight |
| --- | ---: | ---: |
| All | 5,964 | 6,028 |
| In scope | 5,789 | 5,853 |
| Other own distinctions, no delayed S | 167 | 167 |
| Delayed S, no other own distinctions | 4 | 4 |
| Both exclusions | 4 | 4 |
| Total out of scope | 175 | 175 |

Reachability is from **main or S**. A different reachable self-holding definition excludes a lower-bound claim if its finite expansion introduces own distinctions, or if it can later reach S. Counting only other raw own distinctions, or checking reachability only from S, would be insufficient.

| In-scope label | Families | Draws | Window bounded: families / draws | Growing: families / draws | Window-stage undecided |
| --- | ---: | ---: | ---: | ---: | ---: |
| I | 5,687 | 5,751 | 4,967 / 5,029 | 632 / 634 | 88 |
| T | 5 | 5 | 5 / 5 | 0 / 0 | 0 |
| O | 93 | 93 | 91 / 91 | 0 / 0 | 2 |
| X | 4 | 4 | 4 / 4 | 0 / 0 | 0 |
| Total | 5,789 | 5,853 | 5,067 / 5,129 | 632 / 634 | 90 |

Identity-cycle membership was rederived. T/O/X labels were inherited, not reclassified. P1 is **5,029 / 5,751 = 87.4457%**, with sensitivity **5,029 / 5,663 = 88.8045%**. P3's stricter every-unbounded-residue reading is **648 / 722 = 89.7507%**, with 74 unknown draws and sensitivity **648 / 648**. The I-minus-O window gap is **−10.4038 percentage points**. P5 is **634 / 5,853 = 10.8321%**. These reproduce the advertised prediction outcomes without using path rescues to change a frozen window prediction.

The earlier conservative growth tally can also be reconstructed structurally. Among the 12,772 first-ray-growth families, 5,190 are occurrence-counted chains; 5,964 are in CARRY; the remaining 1,618 are earlier certified nonchains. Exactly **188** of those 1,618 fail the corrected scope predicates: the union of the earlier inventory's 186 other-own exclusions and eight delayed-S records, with overlap. Thus 1,430 earlier nonchains remain eligible. With the earlier referee's chain draw weight 5,633, the earlier eligible growth tally is **5,633 + 1,430 = 7,063**.

With the seven advertised primary path certificates, the weighted split is:

| Outcome | Numerator | Denominator | Share |
| --- | ---: | ---: | ---: |
| Growing | 7,063 + 634 = 7,697 | 13,279 | 57.9637% |
| Bounded | 5,129 in-scope window + 7 paths + 129 out-of-scope upper certificates = 5,265 | 13,279 | 39.6491% |
| Undecided | 83 in scope + 46 out of scope + 188 earlier exclusions = 317 | 13,279 | 2.3872% |

This is a split of the **first-ray-growth draw weight**, not of all 223,261 nested draws and not a population prevalence theorem. Out-of-scope upper certificates can be used because a covered target is still an admissible target; a lower bound confined to covered targets cannot exclude a cheaper other-type or delayed target. The earlier 7,063 growth conclusion is inherited subject to its corrected chain and S-only-ancestry arguments.

**Weight limitation:** the allowed family archive has no per-key draw multiplicities. This lane independently sums the CARRY digest weights and reconciles them with the permitted earlier referee's 13,279 total and 5,633 chain weight. It does not re-read the raw draw file, which was outside the assigned input scope.

Negative controls reject a total of 13,280, reject substituting 5,687 families for P1's 5,751-draw denominator, and reject a lower-bound promotion for a structurally excluded earlier family. The latter checks eligibility, not the truth or falsity of that family's all-target growth.

## 4. The two complete-window but frozen-undecided families

Both are in-scope I wrappers, weight one, with `status="ok"`, `window_complete=true`, `window_verdict="bounded"`, all recorded U values equal to 3, and all recorded a/b/e gates true:

| Family SHA-256 | SELF calls | Window preperiod | Period | Caps |
| --- | ---: | ---: | ---: | --- |
| `432127c418b021d1f7ad899a4a6c3dd27932aab291c45c754346bfdfec35ae20` | 4 | 19 | 12 | inherited census semigroup length-set; P_n product 250,000 |
| `981fdc202826982cf81896e9f6ff3c6109dcede2824048c15c92a963ad702ba8` | 6 | 14 | 4 | inherited census semigroup length-set; P_n product 250,000 |

Their exact keys and complete digest records are preserved in `scope_audit.json` under `capped_but_window_bounded`. The frozen pre-registration, lines 134–136, explicitly treats any cap/timeout and a capped length set as undecided in P1–P4 and not growing in P5. The summary's `rules.uncertainty` repeats that caps override local certificates. Thus their conservative **trial classification** is supported by the frozen wording. The cap does not logically invalidate an independently complete window upper certificate: a failed growth test is not evidence against a bound.

The final 83 reported in-scope undecided families reproduce as 70 incomplete capped windows, 11 complete windows without either certificate, and these two complete-window/capped families.

### Path rescues need an explicit classification distinction

The input is `experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/paths_full/results.jsonl`. All seven rows have `result.path_class="bounded"`, `result.eventually_bounded=true`, an `exact_eventual_boundedness` record covering all residues, and no missing residues:

| JSONL line | Family prefix | Label | Certified upper bound | Onset depth | Result completeness |
| --- | --- | --- | ---: | ---: | --- |
| 43 | `ad4255ad1474` | I | 5 | 4 | complete, done |
| 48 | `b47bcba2eb6c` | I | 4 | 6 | incomplete, timeout in uncarried calculation |
| 50 | `530dbea3fe7b` | I | 4 | 6 | incomplete, done; uncarried calculation partial |
| 60 | `5ceea39607cb` | O | 4 | 12 | complete, done |
| 61 | `f8a2d53b04c6` | I | 4 | 5 | complete, done |
| 62 | `fea4933ecaf1` | O | 3 | 3 | complete, done |
| 63 | `992270e6afcd` | I | 5 | 4 | complete, done |

Only lines 48 and 50 have inherited window caps. Line 48 has `result.status="timeout"`, `result.stage="uncarried_trim_scc_karp_exact_bound"`, and `result.complete=false`; its primary `exact_eventual_boundedness` records period 6, residues 0–5, threshold 6, bound 4. Line 50 has `result.status="done"`, `result.complete=false`, and `result.uncarried_result.complete=false` / `lambda_status="partial"`; its primary bound certificate likewise covers all six residues with threshold 6 and bound 4. These data distinguish completed primary boundedness work from incomplete further analysis; they do not independently verify the primary certificate's mathematics.

The frozen cap sentence explicitly governs P1–P5, which remain unchanged. It need not prohibit reporting a later independent mathematical upper certificate. The report should nevertheless name its final classification policy, because it currently excludes two complete capped window certificates while including two capped, partly incomplete path rows:

| Reading | In-scope bounded / growing / undecided families | Whole-census bounded / undecided draws |
| --- | --- | --- |
| Frozen window stage | 5,067 / 632 / 90 | 5,258 / 324 |
| Advertised primary path rescue policy | 5,074 / 632 / 83 | 5,265 / 317 |
| Require complete whole path rows, retaining frozen window exclusions | 5,072 / 632 / 85 | 5,263 / 319 |
| Count every valid primary upper certificate, including both capped complete windows | 5,076 / 632 / 81 | 5,267 / 315 |

All rows keep 7,697 growing draws. **Narrowing, administrative classification:** identify the advertised row as the frozen window classification plus separately admitted primary path rescues, or report trial classification and mathematical certification separately. A timeout in an uncarried diagnostic does not itself falsify a previously complete primary bound. Counting every available mathematical certificate would also admit the two complete capped windows. This is a reporting distinction, not a discovered counterexample to boundedness.

## 5. Exact eventual scope and wording

For valid uncapped window-bounded families, the repeated Q state-set certifies the bound for all word lengths **s ≥ the family's preperiod**. Absolute target depth adds one for a wrapper. The maximum recorded word preperiod is 36, attained by a nonwrapper; the maximum uncapped wrapper preperiod is 17, so the maximum absolute threshold remains 36. These are sufficient certificate thresholds, not proofs of the earliest possible thresholds.

The seven path certificates have their own onsets, shown above, at most 12. Their uniform bound reaches **5**, whereas the window's bound reaches **4**. The two bound-5 certificates do not prove that the free bond ever exceeds 4; they establish only a bound of 5. The note must not use them as evidence for a universal bound of 4.

All 632 growth records use Lemma G, with r distribution **318, 163, 55, 96** at r = 1, 2, 3, 4. The independent liveness calculation confirms that every eventually carried position in these families is unread. There are **101 wrappers**, so the lower-bound formula needs the frozen wrapper shift: `2 + floor((d-1)/r)` at absolute depth d for wrappers, versus `2 + floor(d/r)` without a wrapper. The unshifted formula in conclusion 6 should be qualified accordingly.

The following prose fixes are **Narrowing**, not evidence that a certified family is unbounded or that a bound is false:

- `carry_bound.md:47–48` and `:60–63`: replace “every depth” with “every sufficiently large depth”, or give the certificate thresholds. A concrete bounded-window record, `2ea108b5457837b093d6bf1748a9823323cf6f3140eefe3fefe9353635bf2e2a`, has U values `["> 6", "> 6", 3]` and preperiod 2. Failure of that early window to find a bond does not prove failure of the free bond, but the eventual certificate does not establish the stronger early-depth sentence.
- `carry_bound.md:47` and `:63`: attach “at most four” to the window-certified part. Two additional path certificates supply only ≤5. An approximately 40% statement can still describe the ≤4-certified weight after a cutoff, but it must use that subset and qualification.
- `carry_bound.md:38`: 55 size-3 and 36 size-4 certificates account for the **91 window-bounded O families**. Including both path additions gives certified upper bounds ≤3 for 56 families and ≤4 for 37. These are bounds/certificate sizes, not established exact values of L.
- `carry_bound.md:27` and the question's “do not forget”: the population includes capped census families. There are 66 inherited length-set caps in the digest. “Non-forgetting or capped first-ray growers” states the frozen population without assigning a non-rectangular-idempotent theorem to every capped family.
- `carry_bound.md:39`: “the window leaves without a bound” avoids treating absence of a size-at-most-six window certificate as proved unboundedness.
- `carry_bound.md:93`: “5,964 exact window decisions” should distinguish attempted families from completed decisions: 72 windows are incomplete, and two further complete windows are excluded by the frozen cap rule.

The meaning of “proved per family” can survive these qualifications: a valid finite automaton/semigroup certificate may imply infinitely many depths **through the relevant proved lemma**. A finite direct replay does not supply that implication. The prevalence, label comparisons and shares are computed census facts. The proposed general theorem “a read carried value bounds the bond” remains a proposed theorem, including its opposite-tie obligation; the interpretation paragraphs must not silently claim it has already been proved for every family.

## 6. Reported correction verdicts

The global correction log was outside the permitted read scope. This lane therefore checks only the descriptions in `carry_bound.md:98–102`; it cannot attest the exact logged wording, dates or whether the global entries match the note.

- **Narrowing of the earlier carrying interpretation:** supported by the permitted evidence. A carried value alone is insufficient: 632 certified-growth families have only unread eventual carrying. This does not refute the surviving certificate-based results or prove the stronger converse that any read value always bounds the bond.
- **Not a block for the misstated fixed point:** appropriate for the corrected current protocol, conditional on the main proof audit. The pre-registration's original least-dead formulation cannot identify a self-carried unread position when started from no dead positions. Addendum A2, lines 162–166, replaces it with the least fixed point of liveness seeded by knots and propagated through calls, then takes the complement. `codex_spec2.md:10–11` explicitly orders that repair before the full run. This is a substantive correction to the rule, not merely a word substitution; the corrected rule was frozen before the population run, and it does not alter K1–K3.

The assigned evidence supports no new **Block** verdict. The missing global-log comparison is an access limitation, not evidence of a missing correction. Neither this finite recount nor agreement among AI referee lanes establishes a general read-memory theorem.
