# Referee hand-off: free edits under joins that forbid

Epic `FORBID-EDITS-20261126-001`, closed 26 November 2026, referee pending. [What stands](decision.md) ·
[the note](README.md).

1. **A2, the parity bound** (README, part A; `linear_two.py`, `linear_three.py`): when a structure's equations split
   into the old ones and each reader's own, and each reader's complete record has the same support for either far
   setting, CHSH ≤ 2. Check the proof; the three-reader case is only checked by exhaustion on small sizes.
2. **A3 and A4** (`pr_example.py`, `pr_three.py`): forbidding by settings can reach CHSH 4 and the Mermin game's
   certainty with every record unchanged; and where nothing depends on both settings, the tables are a local model with
   local rejection. Check both, and whether A4's hypothesis is what the census's "splits" flag tests.
3. **The census and its extension** (`forbid.py` on the earlier studies' growth and counting code; `census_count.md`,
   `census_tables.md`, `extension_count.md`, `extension_tables.md`; the runs as `.jsonl.gz`): forbidding never answers
   both readers' settings; no CHSH above 2 and no Mermin win above 3/4 anywhere. Check the kept preparation (the start's
   knots beside the edited ones), the two weightings, the complete record, and the flags, on a seeded sample with code
   of your own (for instance by enumerating allowed states directly on small structures).
4. **The built starts** (`built.py`, `built_tables.md`): two-sided forbidding in all 81, CHSH below 0.001, because the
   join carries almost no correlation.
5. **The contact addendum** (`--shared`; `shared_tables.md`): placements where a newborn knot holds distinctions of two
   readers.
