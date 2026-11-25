# Independent roster recount

`recount.py` reads the frozen case list and the raw census starts. It builds a
mutually sharing start of size m with a separate shared distinction for each pair
and two loose distinctions held by each start knot. The complete-round engine
comes from the [one-birth-at-a-time study](../../../LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/lr_core.py).
The recount applies the cap to the engine's ordinary fresh count. When there is
only a closing birth, the fresh count is zero under parity and has its ordinary
value under not-all-equal. A completed stalled or zero-birth attempt gets the
round number the engine assigned. A roster already empty at the end of a round
stops there. The 75,000-knot rule keeps the first completed round that crosses
the bound. The one-birth-at-a-time engine lacks the earlier study's other
per-round guards. Compare completed common stages when a guard changes a run's
end.

The recount reads membership and meeting directly from holders at each measured
stage. Each common knot supplies the unordered pairs among the members it meets.
The union gives the exact witnessed relation and includes each pair once even
when several common knots supply it. `read_roster` returns that full relation
with its member IDs. `reach.cpp` walks it once from each member to the registered
step bound or to saturation of that member's part. The reported hash is of the
compact sorted list of cumulative counts including multiplicities. The hash
compares spectra. Identification of the witnessed relation is a separate proof
obligation.

From the repository root, set `REFEREE` to this directory and `RUN_DIR` to a fresh
scratch directory. Build the helper and time one frozen configuration with a
64-source traversal assay. The assay records timings and consumes the same growth
path, stage preparation and search bound as a full run.

```sh
g++ -std=c++17 -O3 -Wall -Wextra -Wpedantic -Werror \
  "$REFEREE/reach.cpp" -o "$RUN_DIR/reach"
python3 -B "$REFEREE/recount.py" --reach-bin "$RUN_DIR/reach" \
  --case census-177-L0 --kl nae --assay
```

The shared-runner entry point is `recount.py`. Pass `--param reach_bin=` with
the absolute binary path. Pass `--param assay=1` for a timed rehearsal. Omit that
parameter to traverse from every member and retain the counts. After a run,
`collect.py RUN_DIR/results.jsonl OUTPUT_DIR` validates and writes the scheduled
stage rows and terminal rows in the frozen case order. Terminal rows include
each omitted round and the whole-history knot count when a run reached a
terminal stage.
