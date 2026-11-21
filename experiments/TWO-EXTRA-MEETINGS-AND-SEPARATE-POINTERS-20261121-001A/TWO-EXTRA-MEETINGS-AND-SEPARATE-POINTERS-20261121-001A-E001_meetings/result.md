# Reproduce the six-knot, seven-meeting study

Run from the repository root with the installed research environment.

~~~sh
ulimit -v 6291456
export OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1
case_dir=experiments/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A-E001_meetings
.venv/bin/python -B "$case_dir/catalog.py"
.venv/bin/python -B "$case_dir/physical_population.py"
.venv/bin/python -B "$case_dir/reconcile.py"
~~~

The catalogue visits every connected labelled seven-pair subset, tree, choice of two absent meetings and flag vector. The separate physical enumerator uses the unlabelled meeting catalogue, decorated symmetries, projection and erasure gates, literal growth, the witnessed-end computation and the named signed-operator criterion. The reconciliation checks both weighted denominators and each founder's four-cut course, executes the matched single-meeting deletions and local knot checker, and compares witnessed ends already present in the archive. Each step stops after the fourth cut at latest on every new six-knot founder.

The verified archive contains 751 decorated sources. Parity closed on one type at cut four with positive operator admission. Of the seven still-connected parity survivors, four return to an observed end and one retains a growing path. Two map at cut four to the measured closer's cut-three end. The latter implication proves later ordinary closure without generating more physical cuts. [Results](../../../research/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/results.md) · [Referee handoff](../../../research/TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A/referee_handoff.md)
