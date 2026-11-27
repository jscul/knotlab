# Independent enumeration of the closed systems and seeded cuts

All 85 closed rows and all 49 seeded cuts agree with the archived counts of bonds and boxes. The closed systems have 13,990,187 bonds and 801 boxes. All 49 closed examples saved in the archive are among the enumerated boxes. Every box reads all eighteen distinctions. The seeded cuts have 7,634,271 bonds, between 131,578 and 223,829 per cut, and no box. The bond count is higher after the cut on 16 systems and lower on 33. Every bond in both panels misses exactly one of eight lower words.

All 49 cuts keep their meeting patterns connected. The cut census found 2,184,391,527 triples of eligible disjoint readings with all pair images free. On each cut there were 11 to 1,108 choices of the first two signed reading pairs having at least two choices for the third pair. In each of the 6,981 choices, every third pair overlapped within itself.

The source saved at line 1 of `cubic_12_3.jsonl` gives a positive control under a different cut. The seeded split at distinction 16 gives no box. Splitting distinction 0 gives 18 boxes. Each reads both loose distinctions, and each uses eighteen of the nineteen distinctions. Both open systems allow 14,554 source states, so the number of allowed states alone cannot distinguish them. A permutation of all nineteen names with the knot order reversed preserves all 18 boxes, their signs and the bond counts.

## Coverage and checks

The recount engine enumerates assignments with one distinction fixed. Global complement preserves the source laws and all agreements, so each omitted assignment has the same reading values as a retained one. It excludes an agreement if a single knot's fixed values determine it. It then enumerates every triple of disjoint eligible carriers whose pair images are free. For each pair of readings it separates all retained assignments by their two values, then checks whether each value of the third reading occurs in each part. Every proposed absence is checked over the whole part. The search order affects only how soon a presence can be witnessed.

For each missing single word, the engine records the three signed readings. It finds boxes by choosing the pair with the least signed reading, then constructing the signed reading pairs that complete a lower bond with either member. The other two pairs of a box give four such pairs, one for each choice of one member of each. Intersecting the choices and testing carrier disjointness enumerates each box once. A planted pattern with both signs gives one box and loses it under each of eight individual deletions and under a carrier overlap within one pair. An independent scalar search on five small systems agrees on eligible readings, candidate triples, bonds and missing-word counts without using global complement. The open three-knot chain gives 16 bonds and a split four-knot system gives 14.

The numbered source laws and cuts were reconstructed from the archived draws without importing the study programs. The 3,000 draws rediscover exactly 85 connected isomorphism classes, with the first representative of each matching the archive. A separate exhaustive generator fills forward adjacencies in breadth-first discovery order. Every connected simple cubic meeting pattern admits such a labelling. The independently relabelled archive and that generator give equal sets of 9,609 labelled meeting patterns. No two archive rows share a label.

This recount covers the 85 twelve-knot closed systems and the 49 archived cuts. The alternate cut and relabelling serve as positive controls. Upper word images and source-law necessity are separate from this enumeration. No growth simulation or other carrier sizes were run in the recount.

## Replay

From the repository root:

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1
recount_dir="$PWD/research/CUT-BOXES-20261127-001/referee-R1"
export TMPDIR="$recount_dir"
g++ -O3 -std=c++20 -march=native -Wall -Wextra -Wpedantic \
  "$recount_dir/recount_engine.cpp" -o "$recount_dir/recount_engine"
.venv/bin/python -B "$recount_dir/recount_run.py" --binary "$recount_dir/recount_engine" \
  --limit 1 --output "$recount_dir/recount_pilot.json"
.venv/bin/python -B "$recount_dir/recount_run.py" --binary "$recount_dir/recount_engine" \
  --output "$recount_dir/recount_run.json"
.venv/bin/python -B "$recount_dir/recount_coverage.py" --limit 256
.venv/bin/python -B "$recount_dir/recount_coverage.py" --output "$recount_dir/recount_coverage.json"
```

The first row in each panel and all controls took 5.97 seconds together, with peak RSS 72,068 KiB. The full recount took 77.13 seconds with peak RSS 74,460 KiB. The coverage prefix and full coverage each took less than 0.31 seconds, with full peak RSS 35,272 KiB. [Per-system counts and all boxes](recount_run.json) · [Coverage](recount_coverage.json)
