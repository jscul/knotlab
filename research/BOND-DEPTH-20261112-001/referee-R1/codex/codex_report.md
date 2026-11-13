**Refuted** — the asymptotic classification and “204 bounded” headline. The independently checked finite-depth DP values survive.

## 1. Repeat detector

`mn = min(layer.values())` includes **every** DP state, including states incapable of closing a bond. It is identically **1**:
an initial singleton top selection costs 1, empty middle selections preserve a cost-1 state indefinitely, and costs never decrease
below 1. Thus positive gain is impossible; “growing exactly 0” is a structural consequence of the detector. Saved independent
unpruned replays confirm this through 40 levels.

A repeated complete vector is nevertheless sound: deterministic min-plus transition and fixed closing costs give
`L(s+p)=L(s)+gain` thereafter, including absent values (`INF`). It certifies finite boundedness only when every recurring closing
value is finite. Of the **204** bounded labels, **194** meet that requirement; **10 become permanently bondless**:
256, 370, 493, 547, 555, 761, 764, 909, 954, 1289. All ten were independently recomputed; e.g. 256 has `3,4,∞,∞,…`.
The finite tails comprise **167 constant 3, 17 constant 2, 3 constant 4, and 7 periodic between 2 and 3**. All seven periodic cases
were independently checked. The reported 173/30/1 counts are observed minima, not settled values.

The detector can miss periodic scalar outputs because irrelevant coordinates keep increasing while `mn` remains 1. Even a
productive graph can contain coordinates with different rates. The depth/state caps impose further incompleteness; the frozen
code also exits at depth 30 before checking that layer for repetition.

## 2. Rising and flat samples

Independently rebuilt block tables, forgetting maps and the weighted graph. Removed states with zero in F or G (they cannot
complete a minimal bond), then states unable to reach an accepting closing step. Sampled the **20 smallest `(states,idx)`** from
each full-depth undetermined group, reconstructed as `L(30)>L(1)` and equality.

| Sample | Exact result |
| --- | --- |
| 20 rising | All eventually linear plus periodic: **13 rate 1, 6 rate 1/2, 1 rate 2** |
| 20 flat | All bounded for every depth: **19 identically 3, one identically 2** |

Positive rates have complete-vector translation certificates. For flat cases, nonnegative costs permit discarding prefix costs
above a bound B; repeated truncated vectors with finite closing values throughout their period certify boundedness. All recorded
prefixes agree. A separate graph replay recomputed depths **1–512** without extrapolation and checked the certificates.

The population wording is wrong: **240 means endpoint increase**, not steady late growth. Only **214** rise between depths 20 and
30; **26** are constant throughout that interval. Independently checking the five smallest of those 26 (295, 422, 918, 805, 60)
proves eventual constant **4** in all five. Consequently the 240 are not all genuinely linear. The other flat families remain
unclassified by this audit; these deliberately small samples do not estimate population shares.

## 3. Validation

Independent complete-relation enumeration and support search, without a support-size cutoff, matched **24/24** cells: families
103, 156, 480, 311, 737, 124, 1307, 104 at depths 1–3, from the reconstructed seeded validation sample. Both chains gave
**4,5,6,7,8,9** at depths 1–6, matching independently counted `steps + 2`. Every support passed SAT shattering/deletion checks;
four controls passed, including rejection of a nonminimal NAE superset.

The original 120/120 record lacks per-case values; only this subset was reproduced. The exhaustive validator imports no producer
code. `independent_dp.py` reuses only `census.families_one_def()` and `census.L` (`dlang` fixed-point evaluation);
`audit_records.py` uses `dlang` for cohort reconstruction only. All other computations are new code. This is independent
implementation within one AI-assisted task, not external replication.

## 4. Helpers and merge

**831 raw rows → 653 completed family indices**, plus **11 explicit unfinished placeholders = 664**. There are **150 duplicated
indices**, including **136 original/helper overlaps**, with **178 extra rows**. All scientific fields agree exactly. Full records
are not identical: `seconds` and `helper` metadata differ. Every merged completed record equals a raw source record, with no
scientific omission or alteration; winners match first-by-index in ascending filename order.

The unfinished indices are **485, 751, 840, 869, 933, 1113, 1186, 1222, 1296, 1315, 1329**; exactly these are absent from raw results.
The **447 undetermined = 403 full-depth + 44 capped**. Stored summary counts reproduce independently. The supplied `summarize()`
itself is insufficient: it neither deduplicates nor handles empty unfinished rows correctly (`all([])` is true; `states=None`
also breaks cap aggregation). Preserve an executable merge/summary procedure. Raw files do not verify the claimed stopping time.

## 5. Construction versus class

Given exact side-branch projection, a ray bond is a true bond, so **L_true(s) ≤ L_ray(s)** wherever the ray value is finite. A finite
ray bound transfers; rising ray values provide upper bounds and no true-growth lower bound. An absent ray bond supplies no bound.
Endpoint minimisation means **some top port and some own distinction at each depth**; it neither fixes that port across depths nor
covers every target. These are definitional consequences, not census discoveries. Bond cardinality is not a constructed metric.

The finite graph supplies eventual affine behaviour **per length residue**, possibly with different rates or absent residues;
it excludes unbounded sublinear growth on each feasible residue. It does not alone prove one common rate. Counterexample:
zero-cost arcs `q→a,q→b,a→c,c→a`, a cost-1 loop at b, start q,
accept a or b. Fixed-length cost is 0 at odd lengths and `n−1` at even lengths despite global minimum cycle mean 0; the saved
verification checks this example.

An exact general rate method must respect length residues: for example, take P divisible by all simple-cycle lengths, form the
graph recording length modulo P, and for each accepting residue compute minimum cycle means after accessibility/coaccessibility
restriction. Residues with no productive cycle are eventually absent. This finite method can be impractical; a bare global Karp
minimum is insufficient without a common-rate argument. The much smaller exact recurrence certificates above settle the samples.

## 6. Reporting and P1

The below-half certification yield is openly reported, but it **does not falsify bounded-majority P1**: undetermined families are
not proved nonbounded. Correct wording: “the preregistered certification target was not reached; the bounded fraction remains
unresolved.” The original records establish 194 finite bounded tails with 458 unresolved families. Adding this audit's 25 new
bounded certificates and 20 positive-rate certificates still leaves the possible bounded count between **219 and 632 of 664**.

“No positive repeat found” accurately describes the run, but conceals an unreachable detection outcome unless the defect is stated.
“Rising steadily in 240” is incorrect even within the observed range. The existing caution against extrapolating finite readings
and the disclosed helper/unfinished counts are appropriate.

Fixes:

- **Block:** repair or retire the positive-gain detector before using it to assess growth.
- **Block:** remove the ten eventually bondless cases from finite boundedness; report recurring values instead of observed minima.
- **Narrowing:** report P1 as unresolved mathematically, and distinguish 240 endpoint rises from 214 late rises and proven rates.
- **Narrowing:** qualify the common-rate claim by length residues and keep ray, endpoint and true-bond claims separate.
- **Not a block:** helpers preserve scientific results; qualify metadata identity and provide the merge/summary procedure.
- **Not a block:** sampled independent validation succeeds; retain its finite coverage and implementation-sharing disclosures.

Files written, all in this directory:

- `codex_report.md`
- `independent_dp.py`; `dp_smoke.json`, `dp_samples.json`, `dp_controls.json`, `dp_plateaus.json`
- `verify_results.py`; `verification.json`
- `independent_validation.py`; `independent_validation.json`
- `audit_records.py`; `record_audit.json`

All computations used the specified `.venv/bin/python -B`; each completed in seconds with peak RSS below 50 MiB. No publication or
Git mutation was performed. Source/data hashes checked by the record audit remained unchanged.
