# Exact weighted census through eight starting knots

The complete enumeration covered 3,739 decorated founder classes at both laws, representing 69,347,360 distinct labelled tree/mask pairs. In the registered equal-size, quarter-extra law, parity closure has probability **591/16,000**, admitting closure **339/64,000**, and admission conditional on closure **113/788**. The unsigned law has zero closure probability. No mass was censored. Independent scientific referee pending. [Results](../../../research/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/results.md) · [Referee handoff](../../../research/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/referee_handoff.md)

Run these commands from the repository root. The two small-size commands preserve the registered first physical and independent comparison signal. The full run recomputes all ordinary inputs, so the previous sample never supplies census mass.

```sh
study=experiments/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 6291456
.venv/bin/python -B "$study/job.py" --n 4
.venv/bin/python -B "$study/job.py"
.venv/bin/python -B "$study/representatives_audit.py"
.venv/bin/python -B "$study/multiplicities.py"
.venv/bin/python -B "$study/literal_inputs.py" --sizes 4 5 --sample
.venv/bin/python -B "$study/census_audit.py" --small-size 4
.venv/bin/python -B "$study/census_audit.py"
```

The four-knot first signal identified two negative closing patterns and one admitting pattern at cuts two, three and four. The uncapped physical run then classified every size through eight. The independent enumeration generated every uncoloured tree by successive leaf attachment and decoded all 280,388 labelled Prüfer words. It counted every extra-opening mask by its recursive rooted-tree description, checked every labelled multiplicity, grew all 4,256 literal inputs at sizes four and five under both laws and reconciled all 256 previous named trees. A separate formula derived from the four allowed closing configurations checked the resulting probabilities under each of four opening weightings. Every earlier size cap would have retained every trajectory. [Complete ledgers and operator certificates](../../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/representatives.json.gz) · [Per-size and mixture fractions](../../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/census_audit.json) · [Replay fingerprints](../../../artifacts/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B-E001_trees/replay_receipt.json)

The physical component of each result is a finite exhaustive calculation. The all-size impossibility for at least six starting knots is a separate consequence of the stated source and growth laws. It also explains why growing larger trees in the same family cannot discover a later closure. [Proof](../../../research/IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B/tree_count.md)
