# Rerun the referee checks

Run from the repository root. The commands below use one compute process at a time. The timing runs precede the corresponding full runs. The compiler output and all result files go in this referee folder.

```sh
ulimit -v 2621440
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ref=research/CLOSED-BY-CUTS-20261127-001/referee-R1
py=.venv/bin/python

"$py" -B "$ref/census_membership.py" --pilot
"$py" -B "$ref/census_membership.py"
"$py" -B "$ref/growth_audit.py" pilot
"$py" -B "$ref/growth_audit.py" census
"$py" -B "$ref/closure_supports.py" --pilot
"$py" -B "$ref/closure_supports.py"

c++ -O3 -std=c++17 -shared -fPIC "$ref/closed_bonds.cpp" -o "$ref/closed_bonds.so"
"$py" -B "$ref/closed_forms.py" --cases 17 61 1348 --output closed_pilot.json
"$py" -B "$ref/closed_forms.py" --output closed_counts.json
"$py" -B "$ref/closed_controls.py" --pilot
"$py" -B "$ref/closed_controls.py"
"$py" -B "$ref/closed_supports.py" --cases 17 61 1348 --output closed_supports_pilot.json
"$py" -B "$ref/closed_supports.py" --output closed_support_counts.json

"$py" -B "$ref/trace_strict_example.py" --pilot
"$py" -B "$ref/trace_strict_example.py"
"$py" -B "$ref/verify_readings.py" --pilot
"$py" -B "$ref/verify_readings.py"
```

- `census_membership.py` enumerates connected starts of three to five knots with at most twelve distinctions. A knot has at least three places and at most two loose distinctions. Two knots can share at most two distinctions. Relabelling the knots first classifies the shared distinctions and then the loose counts. The resulting classes match the archive individually.
- `growth_replay.py` uses the earlier independent [ordinary rule](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py) for funding, inputs and the fresh allotment. A129 retains the greater of the arity floor and the ordinary allotment minus one. A130 retains the arity floor. Both use the ordinary labels of the retained distinctions. `growth_audit.py` checks the seven growth fields of each raw closure row, all chunk tallies, the frozen pilot, and funding just after round six. The [growth tables](growth_census.json) include the first differing grant and shortage on the 48 diverging starts.
- `closed_bonds.cpp` enumerates allowed assignments and every pair or triple agreement that varies at a fixed value of each individual source knot. It tests the exact images of triples on disjoint carriers. `closed_forms.py` joins the signed clauses into every eligible box or four-clause choice. A box requires two clauses on six disjoint carriers. The alternating four-clause form can have no such pair, so it gets a separate search for two clauses sharing one reading and the two clauses which would complete them. The saved [positive and deletion controls](closed_controls.json) recover known four- and eight-clause examples and test all 256 subsets of the eight possible clauses in each of two sign conventions.
- `closure_supports.py` projects the full allowed states onto each imposed law and checks the resulting relation with the canonical knot test. It also counts entire closed systems up to renaming, respecting how many distinctions each pair of knots shares. `trace_strict_example.py` tests all open census stages for an exact copy of the earlier twelve-law example as a subfamily of their laws. A carrier is unrestricted in the main closed search.
- `verify_readings.py` independently enumerates all raw assignments using one bit per assignment. It checks the six-reading and upper images, single-law deletions, mixed fixes and individual carrier-member changes. It runs the canonical test on each upper role, including from the conjunction with six witnesses. The same file cross-checks the earlier closed-class and split archives and reproduces all 49 examples in the [earlier post-run tables](../../UPPER-GROWN-20261127-001/post/replay_box.json).

Run the commands in the [open four-clause notes](open_four_notes.md) and the [open eight-clause notes](open_eight_notes.md) next, each in a fresh repository-root shell so its memory limit applies to that block. The former rebuilds the two census witnesses and their matched ordinary histories. The latter rebuilds the constructed positive control, ordered prefixes and targeted census checks. Each note records the selection order, timing and memory. Finish with the following commands in the first shell.

```sh
"$py" -B "$ref/verify_readings.py" --changed --pilot
"$py" -B "$ref/verify_readings.py" --changed
"$py" -B "$ref/open_four.py" --task different --law arity_floor --start-limit 100 --candidate-limit 50 --output "$ref/open_four_different_pilot.json"
"$py" -B "$ref/open_four.py" --task different --law arity_floor --output "$ref/open_four_different.json"
"$py" -B "$ref/check_coverage.py" --pilot
"$py" -B "$ref/check_coverage.py"
sha256sum -c research/CLOSED-BY-CUTS-20261127-001/frozen.sha256
```

The last two numerical checks compare the changed birth under all three laws, assert the individual closure rows' box, birth and example fields, and deduplicate the open start-round records across searches. The 150-start growth timing took 0.075 seconds and the census took 2.0 seconds. The closed pattern search took about five seconds. The two open eight-clause prefixes took 138 and 245 seconds. The four-clause shortened-birth search took 14 seconds. The largest recorded open-prefix peak was below 151 MiB. Timing fields can vary on replay.

The read-only index queries, freeze history, wording and credit are recorded in [sources.json](sources.json). For example, rerun the first search with

```sh
"$py" -B scripts/track.py objects 'closed growth box' --json --deep --limit 5 \
  --until 2026-11-27 --exclude CLOSED-BY-CUTS-20261127-001
```
