Verdict: **Confirmed with fixes.** The frozen **per-depth minimum** sample result survives independent recomputation. Its stronger reading as one bounded infinite path is **refuted**. Correct the uncertainty labels and construction claims below before accepting the exposition.

Fresh code was written from the frozen specification and Boolean-relation mathematics. No EVERY-RAY producer Python, parent-folder Python, or REACH DP was opened or imported. Work was offline, with all writes confined to this referee directory; there were no Git mutations or publication actions. At most three Python computations ran concurrently; the path programs used a 4 GiB address-space cap. This is an independent implementation within the same AI-assisted task, not external replication or human review.

## 1. Uncarried boundedness and explicit paths

**Not a block — the numerical per-depth statement.** I attempted all **204** families, all **50 mixed-path cases first**, then the rest by block size. All **200** originally labeled uncarried bounded have independent certificates. A further previously uncarried-unresolved family also has a certificate: **201/204** are now certified for the per-depth object; the other three have a port-map invariant forbidding an empty top-port set on any path.

The fresh DP repeats complete cost vectors after discarding costs above an explicit finite cap. This is exact for the bounded decision: nonnegative costs can never return below the cap. Rejected states with an already-impossible one-forgotten assignment cannot later accept. Every periodic residue is checked. There are **203** per-depth vector repeats, **200** positive; the remaining positive family is covered by its lasso. Comparing the repeated sequences against all 30 supplied depths gives **12,180** censored numerical comparisons, **zero disagreements**. Per-depth uncarried upper bounds are **3:26, 4:169, 5:6**.

**Narrowing — one infinite path needs a separate certificate.** I found **188** explicit uncarried lassos, including **37/50** mixed cases. **185** have finite bounds at every positive depth; three only have an eventual bound, with early missing bonds recorded. The selected lasso bounds are **3:10, 4:124, 5:41, 6:9, 7:1, 9:3**. Each certificate gives its entry, finite call prefix, repeated call word, top-port masks, cost vector, and every residue. The 16 families without a lasso are listed individually in `family_certificates.json`: three have no uncarried path; thirteen have bounded finite-path minima but no lasso found. Exhaustive finite-cap automata rule out an eventual bound of seven for twelve of those thirteen; eleven also exclude a bound of nine. These finite-cap exclusions alone do not exclude larger bounds.

**Block — an actual quantifier counterexample.** One sampled mixed family is

```json
[[3,2,[["K",[1,3,4]],["SELF",[2,0,4]],["SELF",[0,3,4]]]]]
```

Number the SELF calls 0 and 1. Its side relation is TOP. At depth `s`, `1^(s-1)0` gives a three-member bond; for `s>=3`, `1^(s-2)01` gives an uncarried four-member bond. Yet **every single infinite call word has bond size tending to infinity**. Each copy adds one NAE constraint on one old distinction and two fresh ones. Its least endpoint bond has size equal to its constraint ancestry height plus two; that height tends to infinity on every infinite word. The full symbolic proof, including arbitrary additional member choices, and direct checks of all 62 words through depth five are in [direct_brute_notes.md](direct_brute_notes.md). Thus `for every depth, some path` cannot become `one path, for every depth`.

**Block — the saved bound sentence.** The original plain `uniform_cost_bound` values span **2–14**, with **97**, not 100, equal to three. The value two is also present throughout its recorded sequence; fourteen is a loose certificate upper bound. The draft's “certified bounds 3–9” is not a faithful description of those fields. Keep plain, uncarried, single-lasso, and merely observed bounds distinct.

## 2. BRANCH-DEPTH comparison

**Narrowing — the proposed inequality changes the target.** BRANCH's `L_true` fixes a first-branch target and allows members anywhere. EVERY-RAY minimizes over target copies while restricting members to that target's path. Neither feasible set contains the other. The valid frozen comparisons are `L_any <= L_true` and `L_any <= L_path <= L_ray`; **`L_true <= L_path` is not generally valid**. The sampled counterexample above also proves this directly: in its full all-branches unfolding, the fixed all-call-0 target has `L_true(s)=floor(s/3)+3`, while `L_path(s)=3`; depth three already gives **4 > 3**. Off-path members cannot shorten the unique constraint ancestry, and all finite projections extend to the full limit. A BRANCH-linear label plus a bounded different-target path is consequently compatible, not automatically a contradiction.

There are **477 one-definition families in the 600-row sample**, but only **two** exactly match definitions in the permitted earlier inventory. Both are B, currently unresolved in EVERY-RAY, with BRANCH outcomes exactly-three and eventually-exactly-four. There is **no matched sample linear-growth contradiction**. Separately, all **224 G-last** definitions match that inventory; their structurally linked BRANCH outcomes are **65 linear, 143 linear-lower-bound-only, 10 exactly-three, 6 unresolved**. G-last supplies finite sequences, not eventual path classifications.

The raw BRANCH file/line-to-definition archive was outside the original read list and was not read. Independent port signatures match all 664 inventory entries, 640 uniquely and 24 to two candidates, whose outcome labels agree. These signatures omit some call structure; they corroborate coverage rather than proving raw identity. This is a limited cross-check, with exact sample coverage **2/477**, not a claimed validation of all one-definition sample rows. Details are in [branch_reading_notes.md](branch_reading_notes.md).

## 3. Direct enumeration, shared arguments, and repeated arguments

**Not a block.** A separate fresh implementation checked **18 additional several-definition families** outside the producing G-brute panel. Every family completed depths **1–3**; 17 also completed depth four: **71 complete depth cells, 1,564 paths, 20,573,984 complete assignments**, with **zero** disagreements under the stated seven-member censoring. All **63** available uncarried comparisons also agree. The panel includes two growers, duplicate calls, shared arguments, several entries, and inlined locals.

The sampled generator uses distinct arguments within each call. Duplicate calls and sharing between calls are different cases. A synthetic family with SELF arguments `(3,3,0)` explicitly tests repetition within one triple; both fresh implementations agree on all 14 paths through depth three. Independent direct enumeration also matches **40 values and 40 identity masks** from ten mixed lasso certificates.

**Narrowing.** One depth-four cell has 23 distinctions; all its 81 paths were explicitly skipped. The extra 18 families supplement the original 22 but do not retroactively satisfy the original frozen panel or its preperiod-plus-period depth requirement. Finite checks do not establish every eventual classification.

## 4. Unresolved cases, bands, and G-reg clarification

**Not a block — main P1.** The 26 unresolved G families stay outside the class numerators and enter the upper band: **204/296 to 230/296 = 68.919%–77.703%**. Applying the stated Wilson formula, with `z=1.959963984540054`, separately to those two counts gives the envelope **63.432%–82.072%**. The registered 75% decision remains **undecided**. The sample selection also reconstructs exactly; G is drawn from **6,701 after excluding 224 from 6,925**.

**Block — uncarried uncertainty.** The frozen 204 split is **200 bounded, 3 none, 1 uncarried unresolved**, not four proved carried-only. Before adding this referee's new certificate, the secondary band must include **27**, not 26, unknowns: **200/296 to 227/296**, Wilson envelope **62.039%–81.145%**. B is **55 uncarried bounded, 15 no uncarried bond, 30 unresolved**; five of its reported carried-only cases were unresolved. The spec's else-label explains the error but does not justify “only.” The new referee certificate resolves the extra G case independently; it does not silently rewrite the frozen rows.

**Narrowing — G-reg chronology.** All **486 single-entry** cases pass; the **nine** graph mismatches all have two or three entries; all 500 class and lambda comparisons agree. This fits the third clarification, explicitly frozen **after gate results but before class shares**, rather than a later post-share loosening. Preserve that chronology and the original mismatches. “One SELF call implies one path” also needs **one entry**.

**Block — equivalent calls.** All four excluded single-symmetry-class G families are bounded over paths despite their first-ray growth. Fresh finite calculations already disprove equality: one has `L_path(3)=3` versus `L_first(3)=4`. Local call symmetry does not imply `L_path=L_ray` or “grow by construction.” The frozen denominator can remain a declared estimand; remove that justification.

**Narrowing.** P3's reported upper Wilson endpoint 22.8% is the unresolved-aware envelope for **33/200 to 34/200**; an ordinary interval for 33 alone ends at 22.3%. Draw-weight summaries were not independently recomputed because draw records were outside the allowed inputs.

## 5. Two recorded code versions

**Not a block — observed consistency.** Every allowed same-key overlap has **zero resolved-versus-resolved scientific conflicts**. Differences involve incomplete information or newly obtained positive certificates. Phase two adds **three G bounded verdicts**: two completed runs and one timeout retaining a valid positive certificate. “Resolved two” must specify completed statuses rather than scientific verdicts.

**Narrowing — version equivalence remains untested by these overlaps.** B's 25 keys and B_resume's 75 are disjoint. Metadata assign G/N/B/phase2 the `a9cd74a7…` DP hash and B_resume/gates `164661c7…`; the 29 phase-two overlaps therefore do not provide a completed old/new same-input replay. The data show no contradiction, but disjointness cannot establish patch equivalence. The forbidden source files were not inspected to characterize the patch.

## 6. Wording and scope

**Block.** Replace “some descending path ... at every depth,” “that path,” and “only a mixed path does” where they assert one infinite witness with: **“For each sufficiently large depth, some finite path, possibly depending on that depth, has a bounded-size bond.”** A mixed flag excludes fixed entry-and-call pairs; it does not itself exhibit one periodic mixed witness.

**Narrowing.** Qualify prevalence claims such as “usually,” “about seven in ten,” and the decline with call count as statements about this frozen sample and its strata. The interpretation currently extends beyond that qualification. Small, differently capped call-count cells do not establish a general monotonic law.

“Grows along every path” is valid as a consequence of an independently justified positive asymptotic lower bound on the per-depth minimum. It is not the converse: the counterexample above grows along every single infinite path while its per-depth minimum is bounded. Complete finite-state certificates can justify statements beyond the 30 displayed depths; the direct enumeration alone supports only its read depths. No census-wide share, members-anywhere classification, or general law is established by these checks.

Files written, all in this directory:

- Report and evidence summaries: `codex_report.md`, `family_certificates.json`, `recomputation_summary.json`, `supplemental_checks.json`, `provenance.json`, `validation_results.json`.
- Fresh path code: `lasso_certify.py`, `min_path_certify.py`, `lasso_automaton.py`, `improve_lassos.py`, `higher_cap_lassos.py`, `summarize_referee.py`, `compact_evidence.py`, `validate_referee.py`.
- Full path evidence: `lasso_results.jsonl`, `min_path_results.jsonl.gz`, `lasso_automaton_results.jsonl.gz`, `lasso_automaton_controls.json`, `lasso_improvements.json`, `lasso_higher_cap.json`, `compression_receipt.json`. Compression was verified by round-trip SHA-256.
- Independent direct lane: `direct_brute.py`, `direct_brute_results.json`, `direct_brute_notes.md`.
- Independent reading lane: `branch_reading_check.py`, `branch_reading_results.json`, `branch_reading_notes.md`.

Reproduction uses `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B` on these scripts. `validate_referee.py` checks the saved certificates, controls, input hashes, and summary consistency. The original `brief_codex.md` and `codex_last_message.md` were left untouched.
