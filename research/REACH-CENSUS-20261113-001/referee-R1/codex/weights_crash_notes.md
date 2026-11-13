# Weights, crash, and unresolved audit — points 3, 4, 7

**Verdict: Confirmed with fixes.** No arithmetic Block found. Class/graph correctness is handled by the other audit lanes.

Fresh aggregation and bootstrap code read the archived data and the permitted input language; the reach-census implementation was never opened or imported. The archived draw file is absent from the permitted directory, so its stored bits and fates could not be compared directly (G0 is not independently re-certified here). Draw multiplicities were recovered by replaying dlang.sample: eight SHA256(LO:w) seeds, 150,000 attempts each, retaining defs with t not None; each canonical JSON key receives one count per retained draw. Finite fates were recomputed with the permitted input's finite-orbit definition. No extra 2^-bits weighting was applied.

## 3. Crash recovery — Narrowing

Recovery was a **resume**, not a fresh run of all families. run_info records 110,262 resumed and 14,310 written. The crashed log stops at 110,262; the resumed log begins at 110,287. The partial snapshot's 14,310 missing keys are exactly the final file's suffix. The retained prefix represents 206,980 draws; the added suffix represents 16,281.

The final prefix reproduces all 1,830 partial class-count/point-band comparisons and all 366 recorded rate/bounded-cost/onset histograms, including cell and definition-count/S-own-count strata. There are zero mismatches. This supports aggregate stability and continuation of the same key coverage. It cannot establish per-family equality: exchanged class/rate changes preserving all aggregates, or changes to per-key nodes, completeness, trimmed nodes, exact-test period/residues, L_ray values, status or performance fields, cannot be ruled out without raw pre-patch records or their per-record hashes. No such change is demonstrated. Correct the brief's from-scratch wording and narrow any all-fields unchanged claim to the evidence available.

## 4. Draw shares and headline arithmetic — Not a block

The replay recovers **223,261 draws and 124,572 unique canonical family keys**, with no missing keys. All 2,145 final point-count/band comparisons and 429 recorded histograms match. All primary 2,000-resample class/P1 bootstrap intervals reproduce exactly; P3's 2.5% lower quantile is 0.12752854775543002, with limit-only sampled before forever in its independent-cell draws. The other within-P3 order gives 0.12786807700599154 and does not alter the prediction verdict. Intervals use linear quantiles and the frozen shared stream.

| First-ray class | Draws | Distinct sampled families | Share of all draws | Unresolved-assignment band |
| --- | ---: | ---: | ---: | ---: |
| S1 limit dead | 1,487 | 1,487 | 0.66604% | settled observed share |
| S2 no copy | 13,019 | 12,491 | 5.83129% | settled observed share |
| S3 no own distinctions | 117,360 | 48,974 | 52.56628% | settled observed share |
| S4 free own distinctions | 5,293 | 1,539 | 2.37077% | settled observed share |
| bounded | 30,979 | 29,460 | 13.87569% | 13.87569–14.23984% |
| grows | 13,279 | 12,772 | 5.94775% | 5.94775–6.31190% |
| lost at large depths | 970 | 970 | 0.43447% | 0.43447–0.79862% |
| mixed by residue | 8 | 8 | 0.00358% | 0.00358–0.36773% |
| none at any depth | 40,053 | 16,058 | 17.93999% | 17.93999–18.30414% |
| unresolved | 813 | 813 | 0.36415% | exact unresolved share |

No depth (S2+S3) is 130,379/223,261 = 58.39757%; settled no bond (S1+S4) is 6,780/223,261 = 3.03680%. Absence at large depths, counting settled classes plus none/lost, is 178,182–178,995/223,261 = 79.80883–80.17298%. These reproduce Conclusions 2–3. The raw all-weight bounded and grows point shares are 13.87569% and 5.94775%; assigning all unresolved to each separately gives upper shares 14.23984% and 6.31190%.

| Computed cell | Draws | None | Lost | Bounded | Grows | Mixed | Unresolved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forever | 85,240 | 40,046 (46.98029%) | 958 (1.12389%) | 30,431 (35.70038%) | 13,002 (15.25340%) | 8 (0.00939%) | 795 (0.93266%) |
| alive_only_in_limit | 862 | 7 (0.81206%) | 12 (1.39211%) | 548 (63.57309%) | 277 (32.13457%) | 0 (0.00000%) | 18 (2.08817%) |

P1 uses 44,236 computed forever draws in bounded/grows/mixed/unresolved: bounded is 30,431–31,226/44,236 = 68.79239–70.58957%, bootstrap 68.34223–71.02954%. Name this forever denominator when quoting 68.8–70.6%. Across both live cells the corresponding share is 30,979–31,792/45,079 = 68.72158–70.52508%. P2's forever growth interval is 15.00466–16.43947%. P3's adverse point difference is 15.94851 percentage points, with its lower bootstrap quantile 12.75285 points; both frozen requirements pass.

**Narrowing:** Conclusion 4's only-because reading is not established. Conditional growth bands are 29.39235–31.18953% (forever) and 32.85884–34.99407% (limit-only). Comparing the same unresolved assignment gives a 3.46649–3.80454 point gap; allowing opposing assignments gives 1.66931–5.60172 points. The data show that differing absence rates explain much of the unconditioned contrast, while conditional point shares still differ. A causal or equal-probability claim does not follow.

**Narrowing:** The Reading's about-6%-of-weight and about-half-on-both-rays statements have different sampling units. The former is 13,279/223,261 draws. The latter is 297/645 distinct panel keys among first-ray growers in a uniformly selected eligible-key panel of 3,000. Report them separately; their product is not an established two-ray share of all description weight.

## 7. Unresolved — Not a block

All **813 unresolved draws are 813 distinct singleton keys**: block-size 746, timeout 38, incomplete graphs 27, worker errors 2. Each of the 27 has exactly 300,000 nodes and complete=false; no unresolved record has a positive boundedness certificate. Unresolved enters each computed denominator; each resolved class band's low numerator excludes it and high numerator adds it. P1 includes it in its four-class denominator, and P3 assigns it against/for the difference as specified. Unresolved itself is reported as an exact observed share, without a band.

Unresolved is 795/85,240 = 0.93266% of computed forever draws and 18/862 = 2.08817% of computed limit-only draws; neither exceeds the 5% undecided threshold. The two error records, final lines 81,994 and 110,262, remain unresolved rather than disappearing on resume. Both lack usual-limit/stratum fields; independently replayed finite fates place both in forever. Their definition counts are six and one, reconstructible from their keys. The JSON retains every unresolved key, status, cap/certificate field and exact counts by inferred definition count.

**Narrowing:** mixed below 0.01% is only the classified point share, 8/223,261 = 0.00358325%. The adverse unresolved bound is 821/223,261 = 0.36773104%, so below 0.01% is not unresolved-robust. The frozen word rare is still justified: even this upper bound is below 1%.

Reproduce with:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/weights_crash.py
```

Outputs: weights_crash.py, weights_crash.json, weights_crash_notes.md. The JSON contains input hashes, replay digests, exact count/band tables for every reported stratum, both P3 bootstrap orders, all discrepancies (none after mathematical normalization), crash coverage and residual limitations. One process; no subprocesses or Git mutations.
