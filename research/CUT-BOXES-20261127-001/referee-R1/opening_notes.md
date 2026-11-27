# What a cut does to a box

The original readings and readings chosen again after opening answer different questions.

## Original readings

Split any nonempty set of shared distinctions. For each original distinction named in a carrier, choose which copy to keep in that carrier. When every carrier omits a distinction, choose either copy as its representative. Let $D$ consist of the knots holding the *other* copies. The projection of the opened system onto the representative copies and the unsplit distinctions equals the original system with the laws in $D$ erased.

For the forward inclusion, each law outside $D$ holds on the projected state. For the reverse inclusion, start with any state of the original distinctions satisfying those laws. Every knot in $D$ has an unread loose copy of its own. Its three-place not-all-equal rule admits an extension for every fixing of the other two places. Fill its private places to satisfy the rule. The choices for different knots in $D$ are independent. This also covers several cuts incident to one knot.

If each single source-law deletion restores an excluded upper word of a closed box, any such transport restores that word after any nonempty set of cuts. Every source state satisfying all the laws still lifts, so any previously present upper word still occurs. The same holds for the lower projections of the transported readings. This argument concerns a box whose carriers follow their original distinctions. New readings can use both loose copies, and identifying these copies can make two carriers overlap or make a carrier smaller. A full absence claim must include these choices.

The original closed census checked the upper deletion condition directly on 681 of its 801 boxes. The independent full closed audit checks the condition on all 801, each with eighteen named distinctions in six disjoint triples. The projection calculation therefore covers 801 × 18 × 2 = 28,836 one-cut transports and 801 × 153 × 4 = 490,212 two-cut transports. Each number counts choices of an original box, the distinctions to split, and the retained copy of each. [Closed deletion counts](upper_counts.json)

## A different cut of the same source

The first archived source in `cubic_12_3.jsonl` has sixteen closed boxes. It is the sixth entry in the cut study's order, where its seeded choice split distinction 16. Split distinction 0 instead, leaving its copy at knot 0 and giving the other copy, 18, to knot 1. Read agreement on these carriers in the order A0, A1, B0, B1, C0, C1.

```
(0,1,10)   (3,4,17)   (2,6,18)   (8,11,14)   (5,7,9)   (12,13,15)
```

Every one of the eight lower triples has exactly seven words, missing 111. For all 72 choices of a reading and a source knot, some fixing of the knot permits both values of the reading. All eighteen carrier places admit a single allowed change that changes the reading. On the three pairwise disagreements the upper words are exactly 000 through 110. Removing any of the twelve source laws restores 111. Direct enumeration uses all 524,288 assignments, of which 14,554 obey the twelve laws. The two loose distinctions occur in different lower carriers. Identifying both as 0 makes the first and third carriers overlap. The two ordinary transports of the archived closed example instead each retain six of its eight lower clauses and admit upper 111 in 20 and 60 assignments. [Truth table](opening_witness.json)

## Complete finite search

For each source, the unordered set of cuts is marked. Two markings related by a renaming of the source knots give isomorphic open systems, including the loose distinctions. At each split either copy may be called fresh. A renaming of the source knots induces a renaming of the opened distinctions by their incident knots, including when the chosen fresh names are reversed. Every box, its signs, and its source-law deletions are invariant under such a renaming. The census runs one representative for each class of markings and records all equivalent labelled choices. [Cut populations](opening_census.json)

One class represented by the earlier closed twelve-knot witness and the distinct class containing the explicit alternative cut above supply the two-cut populations. The earlier witness is identified by an isomorphism on knots and their shared distinctions. The positive-source class is specified by its archived labelled links. The two populations contain 19 and 123 inequivalent two-cut markings, respectively, each accounting for all 153 labelled choices on that source. The remaining 47 parent systems were outside this two-cut census.

The search considers every eligible two- or three-place agreement carrier, all eight forbidden-word signs and every six-carrier box satisfying the disjointness rule. Each source is treated once for a question about sources. Each of its eighteen marks is treated once for a question about a random link with a uniform weighting of the links. The six-case timing run at two workers measured about 0.76 worker-seconds per one-cut case and 1.42 per two-cut case. This gave a combined estimate of about four minutes for 371 one-cut and 142 two-cut representatives. [Timing](opening_census_pilot.json)

| Closed sources | Number cut | Labelled choices | Choices up to renaming | Positive labelled choices | Boxes on the positive choices |
| --- | ---: | ---: | ---: | ---: | ---: |
| All 49 carrying a closed box | 1 | 882 | 371 | 1 | 18 |
| The source carrying the open box above | 2 | 153 | 123 | 0 | 0 |
| The original twelve-knot witness | 2 | 153 | 19 | 0 | 0 |

The 18 one-cut boxes all occur at the same cut on the same source. Across the 18 there are 86 distinct lower triples. The direct projection confirmed the seven words of every one. Every upper image misses only 111 and every one of the 216 source-law deletions restores it. Each box uses eighteen distinctions, and the two loose distinctions lie in different lower readings and different upper pairs in all eighteen boxes. The seven-word image passes the canonical knot test with each of its three distinctions designated as contact. [Positive checks](opening_positive.json)

The other 881 one-cut choices have zero boxes. Under the hypothetical weighting that picks one of the eighteen links uniformly and independently on each source, the chance of observing zero positives on all 49 sources is 17/18. Forty-eight sources contribute no opportunity to find a box and one contributes a single favourable link. The reported 49 seeded choices are fixed. The 882 systems have 130,984 to 237,298 lower bonds each. At two cuts, 7,191 labelled choices on the remaining 47 sources were not run.

## Rerun

From the repository root, after generating `archive_counts.json`, use the commands below. The shared program reads one system per line and writes one result per system. `opening_census.py` records all equivalent labelled choices for each representative. The temporary executable can be removed after the run.

```bash
folder=research/CUT-BOXES-20261127-001/referee-R1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 1250000
TMPDIR="$PWD/$folder" g++ -std=c++20 -O3 -march=native "$folder/recount_engine.cpp" -o "$folder/opening_census_run"
.venv/bin/python -B "$folder/opening_witness.py" --prefix 65536 --out "$folder/opening_witness_pilot.json"
.venv/bin/python -B "$folder/opening_witness.py" --out "$folder/opening_witness.json"
.venv/bin/python -B "$folder/opening_census.py" --engine "$folder/opening_census_run" --pilot --out "$folder/opening_census_pilot.json"
.venv/bin/python -B "$folder/opening_census.py" --engine "$folder/opening_census_run" --out "$folder/opening_census.json"
.venv/bin/python -B "$folder/opening_positive.py" --census "$folder/opening_census_pilot.json" --out "$folder/opening_positive_pilot.json"
.venv/bin/python -B "$folder/opening_positive.py" --census "$folder/opening_census.json" --out "$folder/opening_positive.json"
```
