# Referee hand-off: which receivers switch

Epic `SWITCH-RECEIVERS-20261126-001`, closed 26 November 2026, referee pending. [What stands](decision.md).

**What to recheck, in order of what rests on it.**

1. **The census** (`receivers.py`, `drive.py`, `receivers_runs.jsonl.gz`, `tally.py`): six of 646 receivers switch
   under the cap of three, one kind (the same own births with every sender), at round 2d + 1, d = 2 to 5; the counts
   under caps of four and five, the record's one fewer and the ordinary count. Check "reads the far end" (first
   difference between two senders, up to the last round both were read) and the "no own knot short before" filter.
2. **The rule's test** (`rule.py`, `rule_runs.jsonl.gz`): the starts built by hand holding four and five loose
   distinctions under caps of six and seven, and the caps one smaller and one larger; the rule was written in the
   note before this run (README, "A rule read from the first pass").
3. **The controls** (`controls.py`, `controls_runs.jsonl.gz`): the far site changed after round t₀ (heard for
   t₀ ≤ 2, not for t₀ ≥ 3, at d = 3), 22 rounds, both ends.
4. **The advisor's reading checked** (`senders.py`, `senders_runs.jsonl.gz`; `reflect.py`, `reflect.json`): 3d + 2
   under a cap of four on the switch receiver, the cap of five's failure, and the far site's slack not sorting the
   senders.

The growth engine and the joins are those of `research/SHORT-AGAIN-20261126-001` (`jam.py`, `ring_line.py`,
`switch.py`), whose own referee job is SHORT-AGAIN-R1.
