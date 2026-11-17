# Advisor review of the draft design

Epic `EARN-BUDGET-20261117-001`, 2026-11-17. The advisor model (`claude -p --model claude-fable-5-2 --tools "" --output-format
json`; the reply's `modelUsage` names `claude-fable-5-2`) was given SLOW-LOOP's results and the first draft cold. Its verdict was
"freeze with changes", with eight changes. Its points, checked here, and what changed:

| Point | Taken? | Change |
| --- | --- | --- |
| The "new" patterns were seen in calibration (w20, w10 at density 3.0, heavy), and batching was chosen from those runs | yes | two patterns never run before the freeze added: `local` w15 at density 3.5 (now the primary) and `rand` at density 3.0; the calibrated cells are labelled "seen in calibration" |
| The eager tie rule hands Erb its eagerness | yes | ErbL added (Erb with the most lazy setting within 0.01); Erb's result is read beside it |
| `block` is not structure-poor once rebuilds are batched | yes | `block` is no longer counted as structure-poor; Erb is described as tuned without a local pattern, not without structure |
| The mixture's mean log score is dominated by local w10, and E's 90 settings against Gb's 15 select on noise | partly | the per-cell oracle GbO (15 settings tuned on each test cell) gives the regret E/GbO; the scores and grids are kept as declared |
| The rule is not exhaustive; work wins and `embed` undefined | yes | readings applied in order, a win is a charged win, `embed` reported with no role |
| E/Gb as a structured-cell test returns "earning not shown" exactly when earning works (Gb eager loses on `rand`) | yes | the E/Gb condition is joint: E/Gb ≤ 0.9 (upper end below 1) somewhere, structured or not, and E/Gb's upper end below 1.1 everywhere |
| Add E/GO and E/ST to reading 1 | yes | reading 1 needs E/GO ≤ 1.5 on `local` w10 and E/ST's upper end below 1 in a cell where E wins |
| CPU is measured on a shared machine | noted | at most 5 workers, arms interleaved by case order; work does not depend on the machine |
| Predictions: raise P1 (then w20), P3, P6, P9; lower P5 as written, P11 | yes | w20 85%, w40 65%, Erb 70%, CDCL 95%; the joint earning test 50%; the new unseen primary 60%; P11 (E/Gm ≤ 1 everywhere) replaced by the regret prediction E/GbO ≤ 1.25 (50%) |
| Missing controls: per-cell oracle Gb; Erb's tie-rule sensitivity | yes | GbO and ErbL added |
| The "would and would not show" paragraph: add batching's effect, the calibration, and that only a win over Gb is evidence for monitoring | yes | added |
| Prior art closer than stated (Lingeling's per-technique penalties); "geometric delay" overstated for CaDiCaL | partly | rewritten to what the documented sources say (effort relative to search, rounds at growing intervals); the advisor's recollection of Lingeling's penalties is quoted as unverified |
| T2 comparators not re-tuned at 12,800 | yes | NOV and PS re-tuned at 12,800 over the 3,200 choice and its grid neighbours (a full grid would cost about six CPU-hours) |
| Dates | noted | the commit time is the only authority |

Not used after the results.
