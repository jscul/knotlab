# Can another lower bond determine the carried upper reading?

Across all **26,373** chain occurrences, every determining lower bond must contain both designated agreement carriers of the upper reading it determines. The two rival growth laws reach the same 1,325 ordered stages with a chain. Each chain supplies three pairs, each read as both or either, giving **158,238** upper-function occurrences per law. This search covers lower bonds which omit at least one of the two carriers. The companion check covers bonds containing both. [Stage occurrences](step_incidence.jsonl.gz) · [Counts](step_nonpaired.json)

| Weighting, once per upper-function occurrence per growth law | First three chains per stage | Every chain |
| --- | ---: | ---: |
| Chain occurrences | 3,932 | 26,373 |
| Upper-function occurrences | 23,592 | 158,238 |
| Single-distinction changes witnessed | 133,688 | 896,682 |
| Disjoint carrier triples containing every required raw distinction and omitting at least one designated carrier | 42,636,854,328 | 416,475,532,196 |
| Triples reaching the lower bond test with two carriers containing required distinctions | 0 | 0 |
| Triples reaching it with three carriers containing required distinctions | 7,930 | 53,098 |
| Eligible lower bonds among those triples | 0 | 0 |

Each row of the compressed record identifies one stage and the index of one chain in its complete ordered list. Entries give “both” then “either” for each of the three named pairs in order. The two counts for each reading correspond to two or three carriers containing required distinctions. A repeated choice in two different upper functions contributes twice. In the full run, 52,882 distinct stage-and-triple choices reached the lower bond test. [Per-chain counts](step_nonpaired_rows.jsonl.gz)

## Why the search covers every choice

Fix a carried pair of disjoint carriers X and Y. Their raw distinctions form D. For each member d of D, the search finds two allowed whole-stage states differing only at d that give different upper values. A determining triple must therefore contain every member of D. For each allowed triple of carrier sizes, the raw candidate count chooses the additional distinctions outside D and partitions the resulting set into disjoint carriers of those sizes. It then removes all choices containing X and Y together.

For each d in D and e outside D, the search asks whether every assignment to d and e is possible at the same fixed values elsewhere while changing d changes the upper reading. For a whole-stage not-all-equal law involving d or e, the other members must already include both raw values. The other members of d's designated carrier must agree. The opposite designated carrier must agree for “both” and disagree for “either”. These conditions characterize such a choice of four states. If they occur, a candidate carrier containing d and e cannot participate. With just d and e, changing both preserves agreement. With a third member f, choosing e opposite f makes the carrier disagree for either value of d. Each pair of states preserves every disjoint carrier.

The program then tests each remaining carrier that contains a member of D. A carrier contained in one source knot is readable there. For each other candidate, two whole-stage states with equal raw values outside the carrier, equal agreement on it and opposite upper readings rule it out. Such a pair witnesses failure for every triple of disjoint carriers that contains this carrier. A pool of 192 allowed states supplies direct witnesses when available. For questions still open, the program solves the whole-stage constraints exactly.

Between two and three disjoint carriers must cover D, since D contains five or six distinctions and a carrier has at most three. Choosing the carrier of the least uncovered distinction lists each possibility once. If two cover D, the search admits every possible disjoint third carrier except in the companion case where the first two are X and Y themselves. If three cover D, the triple is complete. The lower bond test requires a nonempty proper image with all three pair projections free, and two allowed states varying each agreement at some fixed value of each source knot. Any qualifying bond is then tested for determination by two copies of the stage with the same three agreements and opposite upper values. [Whole-stage check](step_nonpaired.py)

## Direct control

Four three-place knots on eight distinctions allow exactly 82 raw states. Directly listing those states gives 482 disjoint triples of individually unreadable agreements, of which 100 are lower bonds. The direct and reduced tests agree on the exact set of determining bonds for **966** choices of named pair and upper function with five or six single-change witnesses. They find **8** determining bond/function choices with two carriers containing named distinctions and **24** with three. Taking just one allowed state as the initial witness pool also gave the same answers on representatives of each positive kind and of the empty result. [Control counts and examples](step_nonpaired_controls.json) · [Direct enumeration](step_nonpaired_controls.py)

## Replay

Run from the repository root after creating the stage files. The 13 pilot stages supplied 228 chains. The two additional sizing stages had the most chains and the most distinctions, respectively, and supplied 352 chains. The two timings projected about 84 seconds and 216 seconds for the full run under their respective chain weightings. The completed check took 92.5 seconds and used 45.2 MiB at its peak. Each command uses a single process capped at 1.25 GiB. [Roster pilot](step_nonpaired_pilot.json) · [Largest stages](step_nonpaired_sizing.json)

```sh
ulimit -v 1310720
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ref=research/CHAIN-LAWS-20261127-001/referee-R1
.venv/bin/python -B "$ref/step_nonpaired_controls.py" --pilot
.venv/bin/python -B "$ref/step_nonpaired_controls.py"
.venv/bin/python -B "$ref/step_nonpaired.py" --pilot
.venv/bin/python -B "$ref/step_nonpaired.py" --ids 17,39 --output-prefix step_nonpaired_sizing
.venv/bin/python -B "$ref/step_nonpaired.py"
```
