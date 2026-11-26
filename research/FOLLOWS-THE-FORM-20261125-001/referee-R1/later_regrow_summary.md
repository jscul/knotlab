# Regrowth of selected later studies

Six complete studies agree with the archived results. Each includes 345 second
seeds and the bare start. All six reach common round 9, and each round's
partition of the second seeds agrees. The regrowth also reproduces the pair
totals and all 16 profile tallies in each study.

| First seed | Ration | Short knots | Taking | Classes | Pairs sharing the registered count profile | Of those, told apart |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Ring of four (O) | Cap of three | Retire | None | 3 | 252 | 0 |
| Ring of four (O) | Ordinary count | Retire | None | 3 | 249 | 0 |
| Ring of three (C) | Cap of three | Retire | Sole candidate | 6 | 226 | 0 |
| Single knot (K) | Just enough for three places | Retire | None | 4 | 158 | 42 |
| Ring of three (C) | Cap of three | Wait | None | 11 | 109 | 15 |
| Three-knot chain held at an end (D) | Cap of three | Wait | None | 21 | 98 | 15 |

These studies were selected after reading the archive. They include all three
studies whose registered count profile decides the class, both no-take studies
with an exception among the 141 pairs agreeing out to two steps, and a
contrasting retirement study. The waiting studies reproduce those 19
exceptions in full. For the ring of three, 16 of 141 pairs are first told apart
in round 4, including 4 of the 16 pairs agreeing out to three steps. For the
three-knot chain, 3 of 141 pairs are first told apart in round 3. Eleven of
the 19 differences occur between chains of the same length, and eight
between chains of different lengths. None of the 141 pairs is told apart
in any of the four other replayed studies.

The single-knot retirement study reproduces the author's round-1 example.
The second seed is a four-knot chain held at an end. Changing its loose counts
from 1, 1, 2, 2 to 1, 2, 1, 2 changes the first seed's own births from four
offshoots to three, while adding one join of both descents.

## Counterexamples to the registered count profile

For each of the 264 completed studies with a recorded counterexample, the
replay takes the first such pair in the archive.
It regrows both starts at the archive's law, nine-round bound and 3,000-knot
bound. In every pair the held-knot triple agrees and the two second seeds'
own birth counts agree in every round through the recorded common round.
The first seeds' own births differ first in round 1 for 225 pairs, round 2
for 28 and round 3 for 11, exactly as recorded. Twenty-five starts reached
a growth guard and one reached the knot limit, in each case after
completing the common window.

Together with the three complete positive replays, this confirms the
count of 3 of 267 at the recorded common rounds. The one-pair checks use
the archived common round for each study. Only the six complete replays
recompute it across every start. [Witness rows and pilot timings](later_regrow_witness_evidence.json)

## Five-knot swaps

Each pair is a five-knot chain held at its middle knot. The two end knots have
different loose counts and exchange partners. Each replay verifies that the
counts of knots by steps, loose count and number of partners coincide, and
that the patterns of which knots are partners differ even up to renaming.
Brackets mark the held knot in the following loose-count lists.

| First seed | Ration, treatment and taking | The two second seeds | First difference, recorded and regrown |
| --- | --- | --- | ---: |
| Ring of four (O) | Just enough for three places, wait, none | 2,1,[0],2,3 and 3,1,[0],2,2 | 3 |
| Ring of four (O) | Just enough for three places, wait, none | 2,1,[0],3,3 and 3,1,[0],3,2 | 3 |
| Three-knot chain held at an end (M) | Cap of three, wait, none | 3,1,[2],2,4 and 4,1,[2],2,3 | 4 |
| Two knots (L) | Ordinary count, wait, sole candidate | 3,1,[0],2,4 and 4,1,[0],2,3 | 2 |
| Two knots (L) | Ordinary count, wait, sole candidate | 3,1,[0],3,4 and 4,1,[0],3,3 | 2 |

These five distinct pairs were selected from the recorded positives. All have
the same wider record in round 1 within the pair. Waiting is changed to
retirement for the first three controls and the taking rule is removed for the
last two controls. All five controls agree through round 9, as recorded.
Comparisons cover every archived common round. The ordinary-count positives
complete two rounds in each regrowth.

The 345-seed roster contains no two seeds with the same knot counts by steps
over the whole seed. The swap replay supplies a direct contrast: in these
cases what the first seed's own descent makes changes when the pairing changes
and those counts are held fixed. Of the 141 pairs sharing the two-step
profile in the 345-seed roster, 77 vary only in farther loose counts and
64 compare four- and five-knot chains. The profile retains each included
knot's number of partners in the whole seed, even when some partners are
beyond the cutoff. These comparisons support statements about those pairs
under the reported laws.

## Method and coverage

The replay uses the regrowth implementation written from the frozen
definitions in [growth_engine.py](growth_engine.py). It reads explicit seed
knots from the registered seed file when available and reconstructs the other
knots from the archive's names, which give the loose counts and which knot is
held. It checks that all 345 second seeds differ up to renaming. It groups
second seeds by the first seed's own births through each common round and
compares the resulting sets of members to the archive, independent of class
labels. Profile totals come from the regrown birth counts and second-seed
knots. Pair counts weight each unordered pair in the named study once.

Each run was preceded by a pilot at the same law, round bound and knot bound,
with one process and an address-space cap of 2 GiB. Per-case times and
resource use are in the [replay and pilot evidence](later_regrow_evidence.json).
The largest full-study projection was
1.58 seconds and the largest measured study took 0.92 seconds. Peak resident
memory across the recorded runs was under 30 MiB.

The other 264 of the 270 later studies are **not run in full** in this replay.
Three were also stopped in the author's run and have no witness replay. The
other 7,280 swap pair comparisons are **not run** in this replay. The
all-row tabulation is a separate check of the archive.

The witness replay first timed one pair per law, selecting a pair from the
study with the smallest recorded common round under that law and breaking
ties by archive order. The pilot projected 20.6 seconds, and the full
uncut witness replay used 15.3 seconds including its own fresh pilot. Its
peak resident memory was 59.4 MiB, under the 2 GiB address-space cap.

## Rerun from the repository root

```bash
dir=research/FOLLOWS-THE-FORM-20261125-001/referee-R1
.venv/bin/python -B "$dir/later_regrow_check.py" all > "$dir/later_regrow_evidence.json"
.venv/bin/python -B "$dir/later_regrow_witnesses.py" > "$dir/later_regrow_witness_evidence.json"
```

Both commands run their own pilots and keep the timings in the evidence.
