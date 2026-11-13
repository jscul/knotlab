# Referee R1: mathematical scope and row arithmetic, points 2–6

Scope: `TRUE-BOND-20261113-001`. This lane read the three admitted study notes, the admitted true-bond rows and summary, and the prior rate rows. It did not open, import, or list the implementation directory. It makes no judgment about unseen code or the original validation files. Mathematical arguments below concern the stated method; arithmetic below concerns the recorded values.

## Required fixes

| Severity | Finding | Exact source |
| --- | --- | --- |
| **Block** | The four-family rate example is a misreading of the recorded values. Families **269, 302, 642, 908** have `L=[3,3,3,3,3,3,3]` and `L_ray=[3,4,4,5,5,6,6]` at depths 1–7. Their deficits are indeed `[0,1,1,2,2,3,3]`. These records show a constant true value through depth 7, with later values missing. They do not show a change from one member per level to one per two, or any positive true rate. Replace that example with the actual finite profiles. | `research/TRUE-BOND-20261113-001/true_bond.md:28`; `artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl:39,48,104,151` |
| **Narrowing** | Remove the claims that side branches lower a true rate or that no level skipping implies continued true growth. Report the finite endpoint comparisons and leave unbounded growth, asymptotic rates, and general census behavior unresolved. In particular, the statement “No rate is claimed” must also govern the earlier conclusions and answer. | `research/TRUE-BOND-20261113-001/true_bond.md:28,33–41,45–46,88`; `research/TRUE-BOND-20261113-001/preregistration.md:20–27` |
| **Narrowing** | P3 is **undecided on its registered denominator of 226**, with 37 observed successes and 189 unknown outcomes. “P3 held on the 37 reached” describes a complete-case observation, not the preregistered prediction. The depth-at-least-8 comparison is a separate descriptive comparison. | `research/TRUE-BOND-20261113-001/preregistration.md:34–36`; `research/TRUE-BOND-20261113-001/true_bond.md:28,85` |
| **Narrowing** | State the completion-group composition alongside the positive growth comparisons: only **2/37** depth-12 completions and **9/75** families reaching at least 8 are observed shorteners, versus **60/189** and **53/151** in the respective complements. No representativeness of the completed families is established. | `research/TRUE-BOND-20261113-001/true_bond.md:27–29,33–36`; independently recalculated in `research/TRUE-BOND-20261113-001/referee-R1/codex/audit_claims.json`, keys `groups` and `shortened_evidence` |
| **Not a block** | P1 has already failed: at least 62/226 = 27.43% shorten, exceeding the registered 20%, irrespective of the missing outcomes. P2 is correctly left undecided: only 2 of the 62 known shorteners have both endpoints, and additional shorteners may remain unidentified. | `research/TRUE-BOND-20261113-001/preregistration.md:34–36`; `research/TRUE-BOND-20261113-001/true_bond.md:27,29`; true rows `:41,222` for the two P2 cases |
| **Not a block** | Status counts, reached-depth counts, every supplied summary field, and the exact 226-ID study selection reproduce. Eleven families have no recorded true value; the summary’s maximum-deficit class `0` includes those eleven, so it means “no observed positive deficit,” not a proved zero deficit in every such family. | `research/TRUE-BOND-20261113-001/true_bond.md:29,45–47`; `artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/summary.json:2–13`; audit JSON keys `computed_summary`, `no_observed_true_values`, `study_selection`, `summary_fields_equal` |

“Block” here blocks accepting the prose unchanged; this lane found no mathematical obstruction to the stated finite-support method. The method argument is conditional on using the declared exact infinite port relation `G` and implementing the specified summaries correctly.

## 2. Arbitrary finite chosen-member depth, truncations, pruning, and cap

**Not a block — least fixed point.** Every candidate bond is a finite set of distinctions, so its creators occur at some finite maximum copy depth. Below that finite selection, a child containing no chosen distinction is replaced by the exact infinite port relation `G` (spec `codex_spec.md:20–24,34–44`). Conversely, each finite derivation of a generic summary constructs a finite chosen set. Iterating the combination over all heights therefore covers exactly arbitrary finite chosen-member depths; it does not assert that a bond contains infinitely many distinctions. For a fixed cap, a summary is a pair of subsets of the 256 possible 8-bit masks, and its stored cost is an integer from 0 through the cap. There are finitely many such states and finitely many possible cost decreases. At closure, induction on finite selection height gives completeness, and induction on each derivation gives realizability. Replacing a witness by a cheaper witness with the same `(F,G)` preserves its behavior in every parent context; the required top and depth-s members lie outside generic children.

**Not a block — uniform truncation.** Fix root copy depth 0 and an inclusive last retained copy depth `D=s+h`. Let generic table `T_0` be the empty choice, while `T_1` permits choices among the current copy’s own distinctions. A side child of ray copy `C_j` starts at depth `j+1`, and must therefore use **`T_(D-j)`**: it has own distinctions at depths `j+1` through `D`. In particular, children of `C_s` use `T_h`; side children higher on the ray need larger tables. This is the precise convention for the requested `D-j` rule. Giving every side child the same `T_h` would describe different global terminal depths and is not the same uniform truncation (spec `codex_spec.md:47–58`; study acknowledgment `true_bond.md:26,53–54`). Even a correctly matched truncation restricts where members may be chosen. Agreement there does not by itself prove the arbitrary-depth minimum; that requires closure of the generic table. Exteriors remain infinite and exact through `G` in both comparisons.

**Not a block — pruning.** The three rules in `codex_spec.md:44–46` are sound for a generic child in a bond containing a top port outside that child:

- An empty mask in `F` means that some assignment to the child’s chosen set has no extension for any port state. That chosen set is already constrained without the top member, contradicting global minimality.
- An empty mask in the one-forgotten set `G_S` makes a still smaller selected set constrained without the top member, also contradicting minimality.
- With positive cost and `F={G}`, every assignment to the selected distinctions leaves exactly the empty-choice port relation. Forgetting those distinctions changes no feasible parent state, so they cannot be essential to the global bond.

These are logical exclusions, not empirical observations. They depend on `G_S` representing the specified one-forgotten masks, not an arbitrary union generated from `F` alone.

**Not a block — cap.** A ray candidate gives `L(s) <= L_ray(s)`. For `s>=1`, any admissible global bond contains at least two distinct distinctions: a top port and a fresh own distinction of `C_s`. Both are outside every generic side child and outside every generic child below `C_s`. Consequently, any such generic child contributes at most `L_ray(s)-2` members to a minimizing candidate. Discarding larger generic costs cannot remove an optimum (spec `codex_spec.md:16–21,27–30,43–50`). This proves soundness of the cap separately at each s; it supplies no cap independent of s and no asymptotic rate theorem.

## 3. The inequality is by construction

**Not a block.** Let `R` be the one infinite relation in the specification. For any finite set `W` of distinctions on the ray, its projected relation is `pi_W(R)` regardless of whether the optimization later permits other finite sets containing side members. Non-shattering of `W` and shattering of its proper subsets depend only on those projections. Thus a ray bond remains the same bond when more candidate sets are admitted, and the minimization domain only grows: `L(s) <= L_ray(s)` (spec `codex_spec.md:20–30`; preregistration `preregistration.md:17–25`). This reasoning would not apply to a different system obtained by deleting side constraints. The specification instead quantifies their unchosen interiors into the same exact `G` relation. The zero observed negative deficits are a consistency check, not a scientific discovery of this inequality.

## 4. Independently recomputed subgroups and predictions

| Reached-depth group | Families | Observed shorteners | Recorded growth comparison |
| --- | ---: | ---: | --- |
| Depth 12 | 37 | 2 (5.41%) | 37/37 have `L(12)>L(6)`; among shorteners, 2/2 |
| Less than 12 | 189 | 60 (31.75%) | Registered endpoints unavailable |
| At least 8 | 75 | 9 (12.00%) | 75/75 have `L(last)>L(4)`; among shorteners, 9/9 |
| Less than 8 | 151 | 53 (35.10%) | Not part of that comparison |

The depth-12 shorteners are **273 and 1332** (true rows `:41,222`); each has `L(6)=3`, `L(12)=4`, and `D(6)=D(12)=0`, with its positive deficit occurring earlier at depth 8. The at-least-8 shorteners are **230, 273, 296, 332, 382, 660, 1128, 1287, 1332** (true rows `:33,41,46,53,62,107,184,211,222`). Their respective `(L(4),L(last))` pairs are `(3,4),(3,4),(4,5),(3,4),(4,5),(4,5),(3,4),(4,5),(3,4)`. These are finite endpoint increases, not rates.

The registered P1 denominator is all 226. There are 62 known successes of shortening, 35 complete non-shorteners through 12, and 129 unresolved shortening outcomes. This already falsifies “at most 20%.” The 164 rows in the supplied maximum-deficit `0` category contain both the 35 complete non-shorteners and the 129 unresolved cases.

P2 is conditional on all families shortening somewhere through 12. Only the two shorteners above have the required depths 6 and 12; the other **60 known shorteners lack the final endpoint**, and some unresolved families may yet enter the conditional set. The observed `2/2` satisfying `D(12)-D(6)<=1` therefore leaves the registered 80% claim undecided.

P3 requires at least **204 of 226** families to satisfy `L(12)>L(6)`. There are **37 recorded successes, no recorded endpoint failures, and 189 unknown outcomes**. Reporting `37/37` is accurate only with that complete-case qualification; it does not decide P3. The at-least-8 comparison uses another depth interval and was not the registered P3 test (preregistration `preregistration.md:34–37`).

## 5. Status, exact errors, and selected IDs

The 226 true rows have 226 unique IDs and match exactly the 226 prior rows with `complete=true` and `lambda_float>0`, out of 664 prior rows. There are **no duplicates, missing selected IDs, or extra IDs**; exact rational positivity agrees with the float-based selection. Nonconsecutive numerical IDs are expected and are not missing study rows. All 226 `L` and `L_ray` arrays have length 12; recorded true values are contiguous prefixes, and no recorded true value lacks its ray comparator.

Statuses reproduce as **163 timeout, 37 done, 18 memory_limit, 6 incomplete_ray_reference, 2 error**. The `done` IDs are exactly the 37 depth-12 IDs. Reached-depth counts are `{0:11,2:13,3:26,4:17,5:45,6:18,7:21,8:15,9:7,10:1,11:15,12:37}`; 112 have depth at most 5. Every supplied summary field, including all 62 deficit profiles, matches independent arithmetic.

The two exact error records are:

| ID | Row line | Last recorded depth | Active depth | Exact error |
| --- | ---: | ---: | ---: | --- |
| 248 | 35 | 2 | 3 | `SystemError: error return without exception set` |
| 1288 | 212 | 5 | 6 | `SystemError: error return without exception set` |

Both errors occur at recorded stage `true_minimum`. Their cause cannot be identified from the permitted rows. The active or later depths are not observations. The six incomplete-reference IDs are **170,397,692,847,923,935**, all with no true value. Together with timeout IDs **264,436,724,910,1329**, they make the eleven wholly unobserved true profiles. No missing value is treated as a confirmed non-shortener or a P2/P3 failure.

## 6. Claim boundary and validation

A defensible replacement for the answer is: “Side members shorten the minimum in at least 62 of the 226 selected positive-ray-rate families at observed depths. All 37 families reaching depth 12 satisfy `L(12)>L(6)`, and all 75 reaching at least depth 8 satisfy `L(last)>L(4)`. Only two and nine of those families, respectively, are observed shorteners. P2, P3 on their registered denominators, and unbounded true growth remain unresolved.” The four flat prefixes must be stated as flat prefixes, with no inference that they remain bounded forever. These selected families establish no typical behavior for a general census, and an experiment does not discharge a theorem.

Reproduce the arithmetic with:

```sh
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/TRUE-BOND-20261113-001/referee-R1/codex/audit_claims.py
```

All **20 controls pass**: exact total and study set; no duplicates or malformed prefixes; status, depth, and subgroup partitions; every supplied summary field; explicit errors and missing values; and negative controls that detect a changed total, changed deficit profile, duplicate row, and omitted study ID. The JSON contains the raw subgroup IDs, all shortened profiles with source line numbers, errors, missing-data cases, and independently computed summary. No implementation files, original validation code, or prohibited directory contents were accessed.
