# Replaying the original-stage recount

All 1,452 archived stage records agreed on funding, distinction count and knot count. The 1,241 stages originally read had 1,687,769 lower bonds in total. Every one excluded exactly one triple. The unrestricted signed matching search found one four-clause family in the held-out sample, on the second grown round of the five-knot census entry numbered 5,260. All three choices of the pair read as “both” gave seven upper words. On the separate four-knot census control numbered 420, the second round had four families and twelve such readings. Its named earlier witness also agreed on the four signed clauses, seven upper words and the ten law-deletion counts. [Totals](read_counts.json) · [Stage rows](read_stages_0.json) · [Positive controls](read_pilot.json) · [Direct checks](read_bond_controls.json)

At round zero, 322 starts had twelve distinctions, the only size in the sample large enough for six disjoint carriers. Of those starts, 201 had at least four single-word lower bonds. None of the 43,486 lower bonds at round zero used three two-place carriers. With only twelve distinctions, all six carriers would have to have two places. The round-zero prediction thus had zero sampled starts with even one eligible lower clause. [Counts by round](read_counts.json)

## Search and controls

The original-stage recount uses the earlier independent ordinary-growth rule and the archived census starts. It compares the funded rounds, raw distinction counts and knot counts to each held-out row. The earlier positive control also gives the actual supports for a direct identity-by-identity check. [Growth rule](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py) · [Control witness](../../UPPER-GROWN-20261127-001/referee-R1/upper_sample.json)

For every two- and three-distinction carrier, the search evaluates its agreement on allowed source assignments. A global complement preserves every source law and reading. Fixing one source bit therefore keeps all relevant words. For determination at a source knot, it groups the knot's assignments together with their complements. This is equivalent to fixing the knot's raw values, because any complementary pair of knot assignments can be made identical by complementing one whole state. A reading is eligible exactly when it is open and varies somewhere at fixed values of each single source knot.

For each eligible pair of disjoint carriers and each of their four joint values, the engine observes up to 48 allowed states to find third readings that take both values. Every possible exclusion left by this shortcut is checked on every allowed state in that pair's cell. A bond must still have every pair free. The direct control on six small stages enumerates all raw states, all three-carrier choices and all eight words. All 724 lower bonds, including their signs, match. [Lower enumeration](read_engine.cpp) · [Small direct controls](read_bond_controls.json)

The search for four clauses joins different partitions of the same four signed readings around two disjoint carriers. Each qualifying four-clause family has three descriptions this way. Keeping the one for which a shared signed reading is the least of all six gives one record per clause set. The search allows both parities on one set of paired, signed carriers. All three choices of “both” are checked on the full source with each of its laws deleted individually. The controls cover all 15 pairings, both parities and all 64 assignments of signs. A 32-clause control yielded 64 distinct families. A separate direct oracle checked 347,386 four-clause choices across 135 inputs. The original sample had at most one family per stage. [Pattern enumeration](read_pattern.hpp) · [Pattern controls](read_pattern_controls.json)

## Commands

Run from the repository root. Each command uses one compute worker at a time. The per-process limit is under two GiB. Temporary compilation files for these checks are directed into the referee folder.

```sh
ulimit -v 1992294
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
R="$PWD/research/FOUR-CLAUSE-20261127-001/referee-R1"
PY="$PWD/.venv/bin/python"
TMPDIR="$R" g++ -pipe -std=c++17 -O3 -march=native -Wall -Wextra "$R/read_engine.cpp" -o "$R/read_engine"

"$PY" -B "$R/read_recount.py" --pilot 206/0,15/1,5260/2,2485/2,420/2 --out read_pilot.json
"$PY" -B "$R/read_recount.py" --chunk 0/100 --signed-spool --timing
"$PY" -B "$R/read_recount.py" --chunk 0/1 --signed-spool
"$PY" -B "$R/read_recount.py" --summarize 1
"$PY" -B "$R/read_recount.py" --pilot 426/2 --export-pilot-bonds --out read_positive_426.json

"$PY" -B "$R/read_bond_controls.py" --small
"$PY" -B "$R/read_bond_controls.py"
"$PY" -B "$R/read_pattern_checks.py" --smoke --benchmark 2000
"$PY" -B "$R/read_pattern_checks.py" --benchmark 2000 10000 41256 > "$R/read_pattern_controls.json"
```

The first full run with signed-clause export took 48.5 seconds and its largest child process used 49,404 KiB. A second full run took 47.4 seconds, reached 48,964 KiB and reproduced every archived field. The timing slice used the first start of each successive group of 100 starts in the ordered sample, six starts in all. Its first run took 0.457 seconds, about 46 seconds at full size. The separate size trials took under 0.4 seconds apiece. The full run writes a compressed list of each stage's single-word clauses for the separate reading comparison. The pilot writes compressed lists of all bonds, their precise excluded words and upper roles on the two positive stages. With an input of the form 5260/2, the number before the slash is the census entry and the number after it is the ordinary growth round. [Timing slice](read_stage_timing.json) · [Size trials](read_pilot.json)
