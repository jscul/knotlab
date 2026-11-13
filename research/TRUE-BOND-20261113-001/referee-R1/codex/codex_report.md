Verdict: **Confirmed with fixes**.

The requested recomputation supports the recorded small-case minima and the stated fixed-point mathematics. The conclusions require a factual correction and narrower growth claims. **Block** below blocks accepting the prose unchanged, not the stated mathematical method.

## 1. Fresh direct satisfiability recomputation

Fresh code constructs `G`, expands the copies, generates CNF and searches supports by direct SAT assumptions; it uses no summary DP. The permitted BOND-DEPTH `census.py` supplies definitions and a cross-check on independently computed `G`. No TRUE-BOND implementation, logs or validation outputs were opened or imported.

Selection: the seven smallest study families by `(own distinctions, SELF calls, ID)`, plus 911. All have two own distinctions. Copies at depths **0..D inclusive**, D=s+h, are retained; lower SELF calls receive `G`. Members may occur **anywhere** in the truncation. Every smaller support size is exhausted before declaring a minimum. SAT tests constraint and single-deletion freedom; cached genuine satisfying states only skip already answered satisfiable queries.

Each triple gives minima for **s=1,2,3**:

| Family | SELF | h=1 | h=2 | h=3 | Study L | Study L_ray |
| --- | ---: | --- | --- | --- | --- | --- |
| 709 | 2 | 3,3,4 | 3,3,4 | 3,3,4 | 3,3,4 | 3,3,4 |
| 914 | 2 | 3,4,4 | 3,4,4 | 3,4,4 | 3,4,4 | 3,4,4 |
| 22 | 3 | 3,4,4 | 3,4,4 | 3,4,4 | 3,4,4 | 3,4,4 |
| 53 | 3 | 3,3,4 | 3,3,4 | 3,3,4 | 3,3,4 | 3,4,4 |
| 112 | 3 | **3,4,4** | **3,3,4** | **3,3,4** | 3,3,4 | 3,4,4 |
| 137 | 3 | 3,3,4 | 3,3,4 | 3,3,4 | 3,3,4 | 3,3,4 |
| 212 | 3 | 3,3,4 | 3,3,4 | 3,3,4 | 3,3,4 | 3,3,4 |
| 911 | 3 | 3,3,4 | 3,3,4 | 3,3,4 | 3,3,4 | 3,4,5 |

**Not a block:** All **72/72** minima were obtained; all **48/48 h≥2** values match the recorded `L`. Family 112, s=2, falls from 4 at h=1 to 3 at h=2: its witness contains a depth-4 side member absent at D=3. Family **911, s=2**, gives **3 versus L_ray=4**. Its witness is top port 2, own distinction 1 of `C_2`, and own distinction 1 of side copy `(0,0,2)`; its projection forbids exactly 000 and 111. SELF children are numbered from zero, with child zero continuing the ray.

Separately written depth-first expansion and **Glucose 4** verified all 72 retained projections and deletion checks. Sixteen small cells also received raw SAT lower-bound searches without cached-state or complement shortcuts. Exhaustive smaller-size support counts agree combinatorially; four final controls pass. Two searches exceeding a 10-second cap were retried with retested witnesses from our own earlier computations and fresh smaller-size exhaustion. Total measured computation was about **35 seconds**, peak RSS **182.5 MiB**, maximum truncation **2,189 distinctions**, with at most two concurrent processes.

**Narrowing:** This checks neither the original 33 bond-count validations nor the unseen mutant/ray-check implementation. Stabilization through h=3 does not prove an arbitrary-depth lower bound for size-four answers. Size-three answers additionally decide the unrestricted minimum: their witnesses and six free top/target pairs suffice, since exact `G` exteriors preserve those projections.

## 2. Objects, uniform truncation and cap

**Not a block — fixed point:** Every bond has finite member depth. Below its members, exact `G` replaces unchosen subtrees; conversely, every finite summary derivation realizes a finite chosen set. Closure over all heights therefore covers arbitrary finite member depths. Identical summaries behave identically in every parent context, so retaining their least costs is sound. The one-forgotten summary must use paired masks as specified, not `F_S` alone.

**Not a block — finite object:** With `T_0` allowing no internal members and `T_1` allowing current-copy own members, a side child of `C_j` needs **`T_(D-j)`** for inclusive terminal depth D. Children of `C_s` use `T_h`. A common `T_h` at every ray level is a different truncation. The settled uniform-depth convention is correct.

**Not a block — pruning/cap:** An empty full or one-forgotten mask identifies an internally constrained proper subset, excluding a global bond with a top member outside that subtree. Positive-cost `F_S={G}` contributes only inessential members. A minimizer has size ≤L_ray; every generic child excludes the two mandatory distinct members, a top port and a fresh `C_s` own distinction. Its contribution is therefore ≤**L_ray(s)−2**. The cap hides no optimum of size ≤L_ray; it is s-specific and supplies no rate theorem.

## 3. Settled by construction

**Not a block:** **L≤L_ray** follows from enlarging the permitted locations of members. A ray bond remains a bond of the **same infinite relation**: its constraint and minimality depend only on its projections. Side constraints already enter through exact `G`; they are not removed. The absence of negative deficits is a consistency check, not a finding.

## 4. Selection and growth denominators

| Group | Families | Any observed shortening | Observed endpoint increase |
| --- | ---: | ---: | --- |
| Reached 12 | 37 | **2/37 (5.4%)** | L(12)>L(6): 37/37; **2/2 shorteners** |
| Did not reach 12 | 189 | **60/189 (31.7%)** | Registered endpoints missing |
| Reached ≥8 | 75 | **9/75 (12.0%)** | L(last)>L(4): 75/75; **9/9 shorteners** |
| Did not reach 8 | 151 | **53/151 (35.1%)** | Outside that comparison |

The depth-12 shorteners are **273, 1332**: both have L(6)=3, L(12)=4 and D(6)=D(12)=0; their shortening occurs at depth 8. The nine reaching ≥8 are **230,273,296,332,382,660,1128,1287,1332**. Thus the headline comparisons directly cover only **2 and 9 of the 62 known shorteners**, respectively; these groups overlap.

**Narrowing:** Completion is not established as representative. Registered **P3 remains undecided**: it requires ≥204 successes among 226, but there are 37 observed successes and 189 unknowns. The ≥8 comparison is descriptive and uses different endpoints. **P2 remains undecided**: two known shorteners have its endpoints, 60 do not, and further shorteners may remain unidentified.

**Not a block:** **P1 is falsified** already: at least 62/226=27.43% shorten, exceeding 20%. The remaining 164 mean “no observed shortening,” not confirmed absence: only 35 completed depth 12 without shortening; 129 remain unresolved, including 11 with no true values.

## 5. Run status and coverage

**Not a block:** The **226 selected families each appear exactly once**, with no duplicate, missing or extra IDs against the prior complete positive-rate selection. Arrays have length 12 and observed true values form contiguous prefixes. Every supplied summary field reproduces.

| Status | Count |
| --- | ---: |
| done | 37 |
| timeout | 163 |
| memory_limit | 18 |
| incomplete_ray_reference | 6 |
| error | 2 |

Errors: **248**, JSONL line 35, last depth 2/active 3; **1288**, line 212, last depth 5/active 6. Both record stage `true_minimum` and **`SystemError: error return without exception set`**. The permitted rows do not diagnose their causes. Eleven families have no true values; 112 reached depth ≤5. Active/missing depths are not observations.

## 6. Wording and required fixes

**Block:** `true_bond.md:28` misreads families **269,302,642,908**:

```text
s       = 1,2,3,4,5,6,7
L       = 3,3,3,3,3,3,3
L_ray   = 3,4,4,5,5,6,6
deficit = 0,1,1,2,2,3,3
```

Their true values are **flat through depth 7**, with later values missing. Replace the claimed change “from one member per level to one per two” with these profiles, and remove “in a few it lowers the rate of growth” from the answer. These prefixes establish neither a positive true rate nor permanent boundedness.

**Narrowing:** “No route skips a level ... so the reach still lengthens” (`true_bond.md:38–41`) is unsupported: passing through successive levels does not force additional chosen members. Restrict “growth survives,” “not an artefact,” and the G17 capability statement to the explicit observed intervals and groups. No unbounded true growth, true asymptotic rate, or typical behavior beyond the selected families is established. “No rate is claimed” must govern the earlier conclusions too.

A defensible answer: **Side members shorten the minimum in at least 62 selected families at observed depths. All 37 reaching depth 12 increase from depth 6, and all 75 reaching ≥8 increase from depth 4 to their last observation; only two and nine, respectively, are observed shorteners. P2, P3 on their registered denominators, unbounded growth and true rates remain unresolved.**

**Not a block — files written:** All are in this `codex/` directory:

- `codex_report.md`: this report.
- `recompute_sat.py`, `selected_families.json`: fresh computation and definitions.
- `recomputed.jsonl`, `recomputed_retries.jsonl`, `recomputation_summary.json`: attempts, witnesses and joined results.
- `verify_recomputation.py`, `verification.json`: separate expansion/solver verification.
- `controls.json`, `controls_initial.json`: final controls and preserved fixture calibration, explained in the manifest.
- `audit_claims.py`, `audit_claims.json`, `audit_claims.md`: independent arithmetic, 20 passing controls and detailed arguments.
- `summarize_recomputation.py`, `run_manifest.json`: joiner, input/code hashes, commands, versions and limits.

The manifest records commands using `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No Git state changes, publishing, or writes outside the requested directory occurred.
