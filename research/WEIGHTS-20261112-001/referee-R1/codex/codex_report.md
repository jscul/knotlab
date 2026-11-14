Verdict: **Confirmed with fixes.**

The frozen numerical W1 rule passes for all three new-kind strata. All four completion directions and both directions on ten main-arm bases were reconstructed. The diameter headline requires narrowing; the calibration has no completed observations.

## 1. Four completion certificates

All four listed patterns work, **with polarity `sigma = 1`**: `p` on A forces `p XOR 1` on A + k·d. For each, a 61 × 61 window is satisfiable with p and rejects every image-bit violation, using Glucose4 and the earlier referee's CaDiCaL forcing check. Explicit infinite states carry the image and every pattern on A. I also independently certified an existing main-arm direction independent of the completion direction.

| β/sample/r | completion d | k | image P, Q | main d also rechecked | free patterns checked |
| --- | --- | --- | --- | --- | --- |
| 0/38/4 | (-1, 1) | 1 | 12, 12 | (1, 0) | 8 + complements |
| 1/18/4 | (-1, -1) | 1 | 4, 2 | (-1, 0) | 4 + complements |
| 1/28/4 | (-1, 0) | 2 | 4, 4 | (0, -1) | 4 + complements |
| 1/41/3 | (1, 0) | 2 | 4, 4 | (1, 1) | 4 + complements |

**What certified means.** Every infinite state restricts to a model of the finite window, so UNSAT of each image violation proves forcing on the infinite base; a window SAT result alone would not prove existence. Existence and freeness are supplied by legal states repeating along and across outside a finite central rectangle. Two copies of each tail block are equated across the entire orthogonal extent, including corners. If the periods are at least the transformed kind spans, every translated kind has a checked representative inside the rectangle. More generally, our encoder explicitly includes every constraint after folding coordinates into their central interval or periodic tail; the verifier checks all boundary positions and one full period in each pure tail, which covers every infinite translate. Thus the recorded model extends to a legal state everywhere. A model for each first-bit-zero pattern, together with complement symmetry, proves A free. This separates universal forcing from nonvacuity and freeness.

**Not a block — certificate metadata.** Store `sigma = 1`, frame, central bounds and witness data. Uncomplemented translation (`sigma = 0`) fails for all four. Every reported P,Q pair was reproduced; no substitute pattern was needed. For β1/18, P=4,Q=2 are below the spans 5,7 in the earlier referee's frame, so the sufficient two-copy span argument alone would not justify them. Complete folded-constraint coverage and direct infinite-extension verification do justify our reconstructed witness at those same periods. Models and bounds are in [completion_checks.json](completion_checks.json).

## 2. Ten main-arm spot checks

The earlier independent COMMON-FOLD reader recomputed **travels** on all ten, and found no tie in either its original or enlarged window. I searched fresh patterns in the declared main family to certify two recorded, linearly independent directions per base; the data contain direction lists rather than pattern witnesses. All 20 checks passed, with explicit states witnessing the image and freeness. Six bases are from before the pause and four from resumption; both strata are covered. β0 has no resumed main-rank-two base to select.

| β/sample/r | record source | stratum | two recorded directions re-certified | class + certificates |
| --- | --- | --- | --- | --- |
| 0/4/5 | before pause | new kinds | (-1, 0); (0, -1) | agrees |
| 0/33/4 | before pause | new kinds | (0, -1); (1, -2) | agrees |
| 0/35/4 | before pause | new kinds | (-1, 0); (0, 1) | agrees |
| 1/4/4 | before pause | new kinds | (-1, 0); (0, -1) | agrees |
| 1/7/5 | before pause | old box | (-1, 0); (0, -1) | agrees |
| 1/14/4 | before pause | new kinds | (-1, 0); (0, -1) | agrees |
| 1/50/4 | resumed | new kinds | (-1, 0); (0, -1) | agrees |
| 2/0/3 | resumed | old box | (0, -1); (-1, -1) | agrees |
| 2/1/3 | resumed | new kinds | (0, -1); (1, 0) | agrees |
| 2/6/4 | resumed | new kinds | (-1, 0); (0, -1) | agrees |

No disagreement. This is a spot check, not a revalidation of every main-arm positive. Full patterns and models: [spot_checks.json](spot_checks.json).

## 3. Fresh raw-data recount

I independently regenerated the 171- and 738-kind universes, checked all 1,044 base readings for kind membership, nested prefixes, diameters and stratum, and recomputed direction ranks. A **base** denominator requires `outcome = base`; a **travelling** numerator requires `class = travels`. The additional `travels, uncertified` and unsettled readings are excluded from that numerator. These are rates for the identified class within the search.

The first whole-sample prefixes with at least 40 travelling new-kind bases end at **101, 55, 89** (zero-based), containing 102, 56, 90 samples. All three W1 verdicts pass, both for these prefixes and under the alternative all-completed reading.

| selection | β | samples | new: two / travelling (Wilson) | new: travelling / bases (rate) | old: two / travelling (Wilson) | old: travelling / bases (rate) |
| --- | --- | --- | --- | --- | --- | --- |
| prefix | 0 | 102 | 39/40 (87.1–99.6%) | 40/296 (13.5%) | 0/0 (no estimate) | 0/1 (0.0%) |
| prefix | 1 | 56 | 35/40 (73.9–94.5%) | 40/146 (27.4%) | 4/4 (51.0–100.0%) | 4/18 (22.2%) |
| prefix | 2 | 90 | 38/41 (80.6–97.5%) | 41/121 (33.9%) | 46/54 (73.4–92.3%) | 54/141 (38.3%) |
| all completed | 0 | 122 | 47/48 (89.1–99.6%) | 48/353 (13.6%) | 0/0 (no estimate) | 0/1 (0.0%) |
| all completed | 1 | 130 | 73/82 (80.4–94.1%) | 82/344 (23.8%) | 10/14 (45.4–88.3%) | 14/41 (34.1%) |
| all completed | 2 | 96 | 41/45 (79.3–96.5%) | 45/130 (34.6%) | 46/57 (68.7–88.9%) | 57/150 (38.0%) |

Wilson entries are nominal 95% intervals. The prefixes reproduce **39/40, 35/40, 38/41**, old-box β2 **46/54**, and travelling rates **13.5%, 27.4%, 33.9%, 38.3%**. The all-completed selection includes indices through 121,129,96; β2/sample94 has no completed record and is excluded. It is a sensitivity recount, not the frozen endpoint.

**Narrowing — uncertainty.** The numerical Wilson rule is reproduced. Nested r-readings from one sampled order are dependent, and sampling stops on observed travel; an ordinary binomial Wilson calculation has not been shown to deliver calibrated 95% coverage for this design. Treat these intervals as descriptive, and condition the share on the identified travelling class.

Seven samples have explicit pre-pause capped records. Three further indices, β1/33,41,50, have no row inside the pre-pause observed range 0…57; the permitted data do not say whether they had started. All ten now have completed rerun records:

| β/sample | original record | r=3 | r=4 | r=5 |
| --- | --- | --- | --- | --- |
| 0/38 | logged capped | none found | 2C* | tied |
| 0/98 | logged capped | none found | 1C | tied |
| 1/2 | logged capped | none found | 1C | 2C |
| 1/10 | logged capped | 1C | 2C | 2C |
| 1/18 | logged capped | none found | 2C* | tied |
| 1/20 | logged capped | none found | none found | 1C |
| 1/28 | logged capped | none found | 2C* | tied |
| 1/33 | no row before pause | none found | 1C | 2C |
| 1/41 | no row before pause | 2C* | 2C | none found |
| 1/50 | no row before pause | 1C | 2C | tied |

Here 1C/2C give the rerun's certified-direction rank after completion; `*` marks one of the four independently checked completions. **Not a block — missing-sample bookkeeping.** The note's “9 missing (2 + 7)” omits β1/50 if it means holes in the original observed index ranges: there are ten (2 + 8), of which seven were logged capped. The primary counts already include β1/50 and remain unchanged. [recount.json](recount.json) retains every outcome.

## 4. “Big knots travel less”

These prefix tables give travelling / base counts. Every cell's nominal Wilson interval, exact rational mean-diameter tables, and both sizes crossed with r are in [diameter_tables.md](diameter_tables.md) and [diameter_tables.json](diameter_tables.json), for both prefix and all-completed selections. The mean bins below are descriptive, not new frozen tests.

Largest kind diameter:

| β, stratum | D=1 | D=2 | D=3 | D=4 | D=5 | D=6 |
| --- | --- | --- | --- | --- | --- | --- |
| 0, new kinds | — | — | 0/6 | 1/4 | 13/85 | 26/201 |
| 0, old box | — | — | — | 0/1 | — | — |
| 1, new kinds | — | — | 20/64 | 11/32 | 5/34 | 4/16 |
| 1, old box | — | 1/4 | 1/6 | 2/8 | — | — |
| 2, new kinds | — | — | 38/108 | 2/10 | 1/3 | — |
| 2, old box | 0/2 | 39/93 | 15/44 | 0/2 | — | — |

Mean kind diameter:

| β, stratum | [1,2) | [2,3) | [3,4) | [4,5) | [5,6] |
| --- | --- | --- | --- | --- | --- |
| 0, new kinds | — | 0/1 | 15/75 | 21/150 | 4/70 |
| 0, old box | — | — | 0/1 | — | — |
| 1, new kinds | — | 25/79 | 15/63 | 0/4 | — |
| 1, old box | 1/3 | 3/13 | 0/2 | — | — |
| 2, new kinds | 10/22 | 30/93 | 1/6 | — | — |
| 2, old box | 40/98 | 14/43 | — | — | — |

By number of kinds:

| β, stratum | r=3 | r=4 | r=5 |
| --- | --- | --- | --- |
| 0, new kinds | 2/101 (2.0%) | 15/102 (14.7%) | 23/93 (24.7%) |
| 0, old box | 0/1 (0.0%) | — | — |
| 1, new kinds | 5/44 (11.4%) | 19/52 (36.5%) | 16/50 (32.0%) |
| 1, old box | 2/12 (16.7%) | 0/4 (0.0%) | 2/2 (100.0%) |
| 2, new kinds | 12/37 (32.4%) | 18/40 (45.0%) | 11/44 (25.0%) |
| 2, old box | 23/53 (43.4%) | 20/48 (41.7%) | 11/40 (27.5%) |

There is a descriptive downward association with **mean** diameter in the well-populated new-kind bins, but no consistent monotonicity by **largest** diameter. At β0, travelling and other new-kind bases even have the same pooled mean largest diameter, 5.625. Fixing r exposes reversals: at β1,r5 the mean bins [2,3) and [3,4) give 7/27 = 25.9% versus 9/22 = 40.9%; their intervals are 13.2–44.7% and 23.3–61.3%. Small cells are weak evidence: β0,D4 is 1/4 (4.6–69.9%), and β2,new,D5 is 1/3 (6.1–79.2%).

The across-β ranking is **not solely an r-mixture effect**: equally weighting r=3,4,5 within new kinds gives 13.8%,26.6%,34.1%. It is not uniform across r either: at r5 the new-kind rates are 24.7%,32.0%,25.0%. The old-box comparison changes both the distribution of kinds and the stratum; at β2 its r mix is 53/48/40 bases, versus 37/40/44 in new kinds. The weighting changes the whole kind composition and which readings certify as bases or travelling, so it does not isolate a causal effect of diameter.

**Narrowing — size claim.** Replace “big knots make it rarer” with “the identified travelling rate is lower under weightings favouring larger kinds; within-weighting diameter associations vary with r and size measure.” The data support that descriptive statement, not a universal or isolated size effect.

## 5. Wording

- **Not a block — independence.** Replace “share kinds and seeding” with “share the kind universe and pipeline, using distinct per-weighting seeds `70000 + 1000*w + i`.” Common kinds or a seeding formula do not themselves prove correlated draws. Nested r-prefixes do share a draw; shared methods are also a reason not to call this three independent methodological replications.
- **Not a block — “at 88 to 98%”.** Correct rounded point estimates for the prefix new-kind strata: 97.5%,87.5%,92.7%. Say “among travelling bases identified by this search”; this is neither an interval nor an unconditional population guarantee.
- **Narrowing — “under four declared weightings”.** Acceptable as a descriptive umbrella for COMMON-FOLD's old-box census plus these three new-kind strata. State that the original has r=3…6 and these have r=3…5, with different strata and certificate limits. Suggested wording: “Two certified independent directions occur on a majority of the identified travelling bases in the original old-box census and in each of the three new-kind weighting strata.”
- **Narrowing — calibration.** The four calibration records are **all capped**, for 11/5,17/4,9/4,17/5. There are **four attempts, zero completed outcomes, out of 23 planned**. Replace “4 of 23 done; none gained” with that statement. **W3 is undecided**; there is no observed 0/4 calibration result.
- **Not a block — old box.** β0's old-box stratum contains one base and zero travellers, rather than being empty. W2 has no travelling denominator. β2's 46/54 is a useful comparison under another weighting, not the frozen β0 replication check.

## Files and validation

Written in this directory only:

- [audit_certificates.py](audit_certificates.py), [completion_checks.json](completion_checks.json), [spot_checks.json](spot_checks.json), [validation_checks.json](validation_checks.json), [run_metrics.json](run_metrics.json).
- [audit_data.py](audit_data.py), [recount.json](recount.json), [diameter_tables.json](diameter_tables.json), [diameter_tables.md](diameter_tables.md), [provenance.json](provenance.json).
- [write_report.py](write_report.py), this [codex_report.md](codex_report.md).

All 160 stored infinite-state witnesses passed model replay; wrong pattern, wrong polarity, monochromatic kind, unforced singleton, reversed bounds, nonbinary model and zero-period controls rejected. Certificate commands used one Python process, a 5 GiB address-space ceiling and an 840-second command ceiling. The final completion and ten-base runs took 6.7 and 15.6 seconds; their peak RSS was at most 48.3 MiB. No network, producer-code access, Git state changes or publication. Earlier referee window/frame/classification primitives were reused; new witness construction, model checking, searching and recounting are supplied here. Relative to the study producer this is **V2 — independent reimplementation**, using the expressly permitted earlier referee code. Internal model replay does not add an external replication. This is AI-assisted recomputation with trusted SAT solvers, not human review or a proof-kernel-checked UNSAT derivation. A same-task read-only reviewer inspected the certificate argument.

Reproduce with `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B` followed by, in order: `audit_certificates.py completion`, `audit_certificates.py spots`, `audit_certificates.py replay`, `audit_data.py`, `write_report.py` (script paths relative to this directory).
