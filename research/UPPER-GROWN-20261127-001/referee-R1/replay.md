# Replaying the referee checks

Run these blocks sequentially from the repository root in the same shell. The closed recount and its direct checks accept new output filenames. The other commands write their own named referee outputs. The first runs on the small configurations support the estimates for the corresponding larger runs. Raw evidence is in the study's `out/` and `post/` directories.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ref=research/UPPER-GROWN-20261127-001/referee-R1
py=.venv/bin/python
export TMPDIR="$PWD/$ref"
```

## Every closed class

The first command checks one twelve-knot system with the full algorithm. The second prints the class and count summaries and writes each reconstructed system to a fresh file. The third and fourth check the actual six-reading and upper images by direct enumeration, first on one positive class and then on all 49. The saved [records](closed_boxes.jsonl), [recount](closed_recount.json) and [direct checks](closed_upper_controls.json) are available for comparison. Use fresh replay filenames on another run.

```sh
"$py" -B "$ref/closed_recount.py" --size 12 --indices 3
"$py" -B "$ref/closed_recount.py" --records "$ref/closed_replay.jsonl" --output "$ref/closed_replay.json"
"$py" -B "$ref/closed_upper_controls.py" "$ref/closed_replay.jsonl" --limit 1
"$py" -B "$ref/closed_upper_controls.py" "$ref/closed_replay.jsonl" --output "$ref/closed_replay_upper.json"
```

## The census, local search and ring

The census driver compiles the finite-state scan in a temporary directory under this referee folder. Its 16-stage timing run took about five seconds, and its archived-search replay took 133 seconds. The six larger full truth tables also check 47,356 lower words against the unrestricted large-stage filter. The archived run counted 1,000 starts. The standalone ring is counted from the start through the fourth round.

```sh
"$py" -B "$ref/census_recount.py" --ranks 32 1290 1703 4080 5282 5420 --controls --out "$ref/census_pilot.json"
"$py" -B "$ref/census_recount.py" --controls --out "$ref/census_recount.json"
"$py" -B "$ref/census_recount.py" --mode denominators --out "$ref/census_denominators.json"
"$py" -B "$ref/census_recount.py" --mode ring --rounds 1 --out "$ref/census_ring_pilot.json"
"$py" -B "$ref/census_recount.py" --mode ring --rounds 4 --out "$ref/census_ring.json"
"$py" -B "$ref/census_recount.py" --mode superset --minimum 20 --maximum 22 --ranks 1316 947 399 1290 6788 6353 --out "$ref/census_superset_controls.json"
```

Use the [large-stage commands](large_notes.md#rerun) to rerun the independent exclusion of boxes on all 351 locally searched stages and the two corrected opportunity counts.

## Counterexamples

The [open-system commands](open_notes.md) reconstruct the ten-knot start, all births, the complete split census, its comparison with the 49 seeded choices, and the lower and upper canonical checks. The [other-arity commands](arity_notes.md#replay) reproduce the multiple-meeting and four-place checks. The [alternative agreement commands](alternative_notes.md) cover the larger carriers and signed clauses at the abstract lower level.

The following separate search uses four lower clauses to bind three upper readings. On ten-knot closed systems it visits archive order and stops at the first witness. On the grown sample the first exploratory run used the 80 highest archived bond counts among post-birth stages with 12–15 distinctions. A second search admits signs and includes all fully searched post-birth stages with at least twelve distinctions and four archived bonds, in decreasing order of bond count with ties broken by census rank and round. It stops at the first success or the first 80 stages. That search found its witness on the first stage. Each search's one-stage timing run uses the same settings.

```sh
for pattern in four pairs
do
    for target in closed grown
    do
        "$py" -B "$ref/upper_readings.py" "$target" --pattern "$pattern" --limit 1 --pilot
    done
    "$py" -B "$ref/upper_readings.py" closed --pattern "$pattern" --limit 19
    "$py" -B "$ref/upper_readings.py" grown --pattern "$pattern" --limit 80
done
"$py" -B "$ref/upper_sample.py" --limit 2 --pilot
"$py" -B "$ref/upper_sample.py" --limit 80
```

## Record checks

These commands verify the frozen hashes, saved pilot exclusions, two weightings, prior-work searches, and the canonical roles on the referee's closed and sampled examples. They check all 18 birth-deletion results independently from the allowed states and determine how the symmetries of the ten-knot start act on the boxes. The last two commands check the construction based on pairing source knots against the actual 801-box list.

```sh
"$py" -B "$ref/record_checks.py" --pilot
"$py" -B "$ref/record_checks.py"
"$py" -B "$ref/pairing.py" --pilot
"$py" -B "$ref/pairing.py"
```
