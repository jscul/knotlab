# Eight lower clauses on open stages under the two cuts

## A formed witness under both laws

The constructed ten-knot start from the independent check of agreement readings one layer up forms the same two births under the one-fewer cut (A129), the arity-floor cut (A130) and ordinary growth. Each birth takes two inputs and receives the one fresh distinction required for three places. The first round therefore has twelve knots, nineteen distinctions, and two loose distinctions, 17 and 18. The constructed start is outside the census of starts with three to five knots. [Earlier construction](../../UPPER-GROWN-20261127-001/referee-R1/open_witness.json) · [Rival-law replay and direct tables](open_eight_control.jsonl)

One witness reads agreement on the six disjoint carriers below, in the order A0, A1, B0, B1, C0, C1.

```
(0,9,17) (2,3,16) (1,5,18) (7,10,13) (4,6,8) (11,12,14)
```

All 524,288 assignments were enumerated under each law's common resulting stage. Its 14,554 allowed states give 34 six-reading words. Each of the eight triples taking one reading per pair has the seven words other than 111. For each of the 72 source-knot and lower-reading choices, there is a fixing of the source knot that permits both values of the reading. For each of the 24 lower-triple and upper-reading choices, there is a fixing of the lower triple that permits both upper values.

The upper readings compare the two members of each pair for disagreement. Their image is exactly 000 through 110, so every pair is free. If all three pairs disagree, each pair has exactly one 1, and the triple of those 1s is forbidden. In the eight-clause conjunction, deleting any clause allows the orientation with 1s on just that clause's three readings. On the source stage, erasing either birth law individually restores 90 or 50 assignments giving upper 111, respectively, with the carrier distinctions still available. Erasing both birth laws gives 172. Each of the ten starting laws is also individually essential to this exclusion. The witness uses both newborn distinctions, and the law deletions establish dependence while preserving the size of the declared reading.

The complete search verifies zero boxes before the first round and 18 after it under both laws. Each of the 18 has a seven-word upper image and needs each of the twelve source laws individually. The start and the first round together took 12.58 seconds and peaked at 124,420 KiB. [Search timing prefix](open_eight_screen_pilot.jsonl) · [Full control](open_eight_control.jsonl)

## Bounded census search

The replay uses the earlier independent ordinary growth rule to obtain each set of births and then applies the two fresh-distinction cuts. Through round six it forms 16,168 open stage occurrences under the one-fewer cut and 16,264 under the arity-floor cut. Under each law 264 have fewer than twelve distinctions, so they cannot supply six disjoint carriers of at least two. The counts treat every census start and formed round once per law.

The main search first limits the roster to at most twelve knots and 22 distinctions, retaining 10,542 occurrences of the one-fewer cut and 10,549 of the arity-floor cut. Together these give 10,548 systems after renaming distinction identities while leaving knot indices fixed. The search took the first 220 of these systems, in descending knot count, then descending distinction count, then archived entry and round. It covers 222 occurrences per law, in rounds two through four. Its sizes are 133 systems at twelve knots and 22 distinctions, 33 at twelve and 21, three at twelve and 20, and 51 at eleven and 22.

All 220 have zero structural eight-clause candidates. On 209 systems, 139,969 signed triple incidences survive the iterative requirement of a disjoint replacement for each reading. None can be assembled into the required eight triples. The 15-system timing prefix took 8.75 seconds, peaking at 105,460 KiB. The 220-system search took 137.64 seconds, peaking at 117,460 KiB. [Timing](open_eight_pilot.jsonl) · [Per-system census checks](open_eight_census.jsonl)

A separate search raised the limits to fourteen knots and 24 distinctions and used the same order. Its first 36 systems have no overlap with the 220. There are 24 systems with fourteen knots and 24 distinctions, three with fourteen and 23, and nine with thirteen and 24. They cover 36 occurrences per law, in rounds two through five. All 36 retain at least one signed triple after pruning, with 82,916 total incidences and no eight-clause candidate. The first five systems took 12.78 seconds at 137,916 KiB. Later systems took longer per case, and the full prefix took 244.51 seconds at 150,784 KiB. [Timing](open_eight_larger_pilot.jsonl) · [Larger systems](open_eight_larger.jsonl)

### Why the bound is exhaustive within a searched system

The earlier independent analysis gives a complete list of candidates by retaining every assignment exclusion with a suitable minimal subset of source laws, allowing a positive two-place carrier to acquire a third place. Each qualifying lower clause is in that list, with its sign. Some candidates may exclude several words or be determined at one source knot. Keeping them can only enlarge the candidate list. Iterating the disjoint-replacement requirement preserves every triple in an eight-clause witness because its paired carrier supplies a disjoint replacement. [Completeness proof for the prior signed-triple screen](../../UPPER-GROWN-20261127-001/referee-R1/large_notes.md)

Every eight-clause witness has two opposite lower triples that use all six of its disjoint carriers. The join here tests every pair of remaining triples with disjoint carrier unions, all six matchings between their readings, and membership of all eight resulting triples. A surviving candidate receives a separate literal enumeration of the lower images, single-source-knot non-determination, upper image, lower-triple non-determination and source-law deletions.

### Checks at the stages carrying the four-clause alternatives

| Census stage | Knot and distinction counts | Loose distinctions | Signed candidates before and after disjoint-replacement pruning | Eight-clause candidates |
| --- | --- | ---: | ---: | ---: |
| Second round of a four-knot start with three three-place knots and one four-place knot, entry 420 under both cuts | 10 knots, 18 distinctions | 5 | 41,500 and 422 | 0 |
| Fourth round of the five-knot start whose cut birth is essential to the four-clause witness, entry 5246 under both cuts | 12 knots, 22 distinctions | 5 | 88,466 and 344 | 0 |

The first row is a separate targeted check. The second is search order 118 within the main census prefix. [First stage](open_eight_sample_420_pilot.jsonl) · [Main census prefix](open_eight_census.jsonl)

### Two later stages with the same knot and distinction counts

Two of the census stages passing the prior witness's width, connectedness and cycle-count filters have fifteen knots and 24 distinctions. These are round six of the three-knot start in entry 2 and round five of the five-knot start in entry 2030. Each has three loose distinctions and the two stages are isomorphic upon renaming both knots and distinctions. For each, there are 325,560 signed triple candidates, 10,210 after pruning, and zero eight-clause candidates. Each search covers the same stage under both cuts. The individual runs took 77.64 and 31.55 seconds. [Prior-witness filter](trace_strict_example.json) · [Three-knot start](open_eight_target_2.jsonl) · [Five-knot start](open_eight_target_2030.jsonl)

The searches cover 261 open occurrences with at least twelve distinctions under each law. The remaining 15,643 occurrences under the one-fewer cut and 15,739 under the arity-floor cut were not run. The search concerns six disjoint two- or three-place carriers and the eight lower clauses.

## Rerun

From the repository root, run the commands in order. The small runs use the same single-process path and memory cap as the corresponding full runs.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ref=research/CLOSED-BY-CUTS-20261127-001/referee-R1
.venv/bin/python -B "$ref/open_eight.py" --control --assignment-prefix 65536 --out "$ref/open_eight_control_pilot.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --control --screen-control --limit 3 --out "$ref/open_eight_screen_pilot.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --control --screen-control --out "$ref/open_eight_control.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --limit 15 --stop-on-success --out "$ref/open_eight_pilot.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --limit 220 --stop-on-success --out "$ref/open_eight_census.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --case 420 2 --limit 1 --out "$ref/open_eight_sample_420_pilot.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --max-knots 14 --max-distinctions 24 --limit 5 --stop-on-success --out "$ref/open_eight_larger_pilot.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --max-knots 14 --max-distinctions 24 --limit 36 --stop-on-success --out "$ref/open_eight_larger.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --max-knots 15 --max-distinctions 24 --case 2 6 --limit 1 --out "$ref/open_eight_target_2.jsonl"
.venv/bin/python -B "$ref/open_eight.py" --max-knots 15 --max-distinctions 24 --case 2030 5 --limit 1 --out "$ref/open_eight_target_2030.jsonl"
PYTHONPATH=tools .venv/bin/python -B -m knotlab check --cnf '~P ~Q ~R' --loops Q R --contact P --json
PYTHONPATH=tools .venv/bin/python -B -m knotlab check --cnf '~P ~Q ~R' --loops P R --contact Q --json
PYTHONPATH=tools .venv/bin/python -B -m knotlab check --cnf '~P ~Q ~R' --loops P Q --contact R --json
```
