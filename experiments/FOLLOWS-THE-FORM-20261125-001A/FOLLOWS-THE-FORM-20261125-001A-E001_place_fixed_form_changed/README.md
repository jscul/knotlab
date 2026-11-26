# FOLLOWS-THE-FORM-20261125-001A-E001: the place held fixed, the form changed

An independent reading on a shared growth engine (FF 1), written from the frozen texts alone: the claim and
definitions of `research/FOLLOWS-THE-FORM-20261125-001/`, the pre-registration, `seeds.json` and `disclosed.json` of
`research/FOLLOWS-THE-FORM-20261125-001A/`, and, for the growth only, BD2
(`research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions_b.md`). The drafter's probe programs were not seen. The
growth is ticket B's engine `eng.py` (`experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/...`), imported unchanged and
read-only; R0's second growth is the fold engine `pm.py` (`experiments/PARTS-MEET-AGAIN-20261124-001A/...`), and the
knot test is `knots.test_run` from the same folder, both unchanged and read-only. Every frozen file is checked by hash
at start (`ff_core.FROZEN`). Readings chosen where the texts leave a choice, timings, estimates and cuts are in
[deviations.md](deviations.md), each written before the run it affects.

## Files

- `ff_core.py`: the starts (FF 2: start, bare start, unlinked start), the 18 laws and the registered order of runs,
  the descent (FF 4), what the first seed's descent makes (FF 5), the wider record (FF 5b), the second seed's own
  births (FF 11), start knots in the roster (FF 8); one run grown and read.
- `ff_run.py`: one chunk of a run set (R1, R2, R2u, R3, R4) per process; a timing mode.
- `ff_gate.py`: R0, the gate.
- `ff_read.py`: the study readings (FF 6, 7, 9, 11) from the per-run records, and the tables in `disclosed.json`'s form.
- `ff_controls.py`: R5, renumbering (FF 10) and the knot test.
- `ff_judge.py`: the replication comparisons (PR1, PR2, PR3, PR5).
- `ff_summary.py`: every prediction judged; `summary.json` and `summary.md`.
- `ff_launch.sh`: launches the 8 chunks of one command and logs the wall time.

## Rerun

From this folder, with `PY=/home/jscul/p-vs-np-contact-first/.venv/bin/python`:

```sh
$PY -B ff_gate.py starts                 # the three starts of FF 2, the run counts
./ff_launch.sh R0 ff_gate.py run          # R0 on 8 processes
$PY -B ff_gate.py summary                 # gate.json (a failed gate stops the ticket)
./ff_launch.sh R1 ff_run.py run --runset R1
./ff_launch.sh R2 ff_run.py run --runset R2
./ff_launch.sh R2u ff_run.py run --runset R2u
./ff_launch.sh R3 ff_run.py run --runset R3
./ff_launch.sh R4 ff_run.py run --runset R4
./ff_launch.sh R5 ff_controls.py run
$PY -B ff_controls.py summary             # controls.json
for R in R1 R2 R2u R3 R4; do $PY -B ff_read.py --runset $R; done
$PY -B ff_judge.py replication            # PR1, PR2, PR3, PR5 against disclosed.json
$PY -B ff_summary.py                      # summary.json, summary.md
```

Each process caps its address space at 6 GB (`resource.setrlimit(RLIMIT_AS)`). Timing a small part before a run:
`$PY -B ff_run.py time --runset R2 --every 25`, `$PY -B ff_controls.py time`, `$PY -B ff_gate.py time`.

## Outputs

In `artifacts/FOLLOWS-THE-FORM-20261125-001A/FOLLOWS-THE-FORM-20261125-001A-E001_place_fixed_form_changed/`:

- `runs_<R>_<i>of8.jsonl.gz`: one line a run: its study key (run set, knot law, family, first seed, take, ration,
  treatment), the second seed's name (`null` for the bare start), linked or unlinked, rounds read, stop, guard, final
  knots, and by round: what the first seed's descent makes (`make`, entries [kind, parents, places, f, takes, count]),
  the wider record (`wider`, entries with a sixth item 1 when in the own descent, then the count), the births of the
  second only (`sec_only`), the counts of own-descent births (`n_own`), of births of the first (`n_of_first`), of
  births of both (`n_both`); the last round a start knot is a member (`last_member_round`) and whether one holds a
  usable loose distinction in the final structure (`start_member_final`); seconds. Every table can be recounted from
  these without growing anything.
- `studies_<R>.jsonl.gz`: per study: R\*, L, runs read by round, the classes (own descent, with the bare start
  "(none)"; and by the wider record), the pairs of forms with the round first told apart and whether told apart at
  R\*, fates, the count profile verdicts.
- `tables_<R>.json`: the tables of each run set in the form of `disclosed.json`'s.
- `gate.json` and `gate_<i>of8.jsonl.gz` (R0); `controls.json`, `controls_<i>of8.jsonl.gz` and
  `controls_rest_<i>of7.jsonl.gz` (R5). R5's knot test was cut to half during the run (deviations 35, 36): the rest of
  the half was run by `ff_controls.py rest --chunk i/7 --exclude 941 --deadline <epoch>`; files of stopped processes
  are read up to their last complete line, and a job finished twice is counted once.
- `summary.json` (one entry per prediction: id, verdict, numbers, first failing case) and `summary.md`.
- `logs/`: each process's log and `walltime.log`.
