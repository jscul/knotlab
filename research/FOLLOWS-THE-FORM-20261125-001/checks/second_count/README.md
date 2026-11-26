# The thread's second count

For ticket `FOLLOWS-THE-FORM-20261125-001A`. The drafter's own probe, second version (`ffp.py`, on the shared growth
engine; run `make_engine.py` first), was run on the families already seen before the freeze
([output](ffp_seen.jsonl.gz); its tables are in the frozen `disclosed.json`) and on the held-out material only after
the registered study's outputs were in ([output](ffp_held.jsonl.gz)). [The comparison](compare.py) sets the two side
by side, study by study.

**Result.** On all 360 studies of the held-out material (first seeds K to O: the family `fresh` linked, unlinked and
under parity, and the chains) the two programs agree exactly: R\*, the classes among the forms as sets of second
seeds, the classes by the wider record, the pairs told apart after the first round, the count profile and the fates,
90 of 90 in each group; and all 162 cells of the depth table. The second count also gives 37 studies with two or more
fates, 87 with three or more classes, and 90 and 41 for the two parts of the count profile.

The two programs share the growth engine. They do not share the starts, the descent or any reading.
