# Can the reader remember another way to recognize a feeder?

A feeder is a grown knot with a permanent local signal and one consumable ration. The reader sees its energy, previous action and anonymous local movement controls. ON attempts to eat. OFF moves using the same drawn control used in the original game. This experiment starts with the [old keeper’s failed identifications](../FEEDER-MEMORY-20261121-001/histories.md) and asks what survives when two different physical feeders have exactly the same number of exits.

The [frozen design](preregistration.md) links the public histories, experience rule, and two-knot memory test. It distinguishes three questions. A physical decision can change on two histories even when public observations cannot certify both stocks. A useful decision on a pair can coexist with a shorter life. The [decision](decision.md) and [referee handoff](referee_handoff.md) give the findings under each law.

## Replay and recompute

Use the repository's Python environment at the root of the checkout. The archived resettable game supplies the ordinary growth and movement implementation. Inspect the [saved paired replay](causal_replay.json) for its founder seed, both movement tapes, exact preparation action turns, complete local observations, memory words, frozen games, original, sham, reciprocal, erased and selected-field reads, and actual subsequent energy.

The following command reproduces the complete physical panel and its deterministic seed example in an empty output directory.

~~~sh
.venv/bin/python -B research/SECOND-FEEDER-CUE-20261121-001/causal.py --output-dir /tmp/second-feeder-causal
~~~

Each branch starts from its own reset. The program regenerates the named records from the seed and the imposed past actions, checks them against the public prefix, then reads the four controls and the original before advancing any copy. Its worlds share the ordinary growth law. All other physical marks, including the trained selection marks, stay at their original values within each recipient of the second memory.

## Data boundaries

- The [archived example](panel_archive.json) uses the previous game's names and movement records. Its role is to establish the starting question.
- The bank separates training, the equal-exit paired comparison, and ordinary survival by exact founder key. Training uses only publicly observable meal outcomes. The [frozen physical weights](learning_weights.json) are loaded before either evaluation.
- The earned selection marks persist across training games. The second memory and transient route registers clear between games. The previous menu memory, the learned selector and the action distinction are all separate from the second memory. [Device and elementary guarded moves](device.py)
- The spectator uses the actual holdings and ration ledger to find and score pairs. Neither the device nor the current-only comparator receives these values. The measured survival includes every original held-out launch, including starts whose growth stalled.

## Two separately frozen comparisons

The [first fit](round_one.md) required every cue to agree with the last paying feeder's menu type. Its public training stream contained thirteen certain empty returns that the menu check barred. The [second freeze](return_cue/preregistration.md) removes that condition only from the strict return detector. It keeps the previous physical memory in place and uses three new structural folds. The [new weights](return_cue/learning_weights.json), [stock panel](return_cue/panel_results.json), [second-memory interventions](return_cue/causal_results.json), and [survival comparison](return_cue/survival_results.json) belong to this independently measured follow-up.

To replay the individual decisions, the following commands rebuild the saved episodes and check their public observations and physical interventions.

~~~sh
.venv/bin/python -B research/SECOND-FEEDER-CUE-20261121-001/replay.py
.venv/bin/python -B research/SECOND-FEEDER-CUE-20261121-001/return_cue/replay.py
~~~

Use the [first replay](replay.md) and [follow-up replay](return_cue/replay.md) for turn-by-turn spectator records. Names and stock labels are spectator-only. The [follow-up causal ledger](return_cue/menu_comparison.json) separates pairs that the old menu check would have admitted from pairs it would have excluded.

For a whole unattended game on the second held-out bank, the example below uses the first seed and replicate in candidate order where the trained reader outlived current-only. Use `--reader current` or `--reader old` for the two baselines and `--law nae` for not-all-equal. The ledger includes every held-out game.

~~~sh
.venv/bin/python -B research/SECOND-FEEDER-CUE-20261121-001/return_cue/play_seed.py --seed 12030535759847423040 --replicate 0 --law parity --reader learned
~~~
