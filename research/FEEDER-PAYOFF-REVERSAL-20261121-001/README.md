# Learning which arrival opens a feeder

Two versions of the resettable game give each grown feeder the same single ration. On an eligible three-exit feeder, a bite pays only after the privately accepted approach. A and B are paired even and odd outward control labels from the bot's own preceding move. A version favors one approach and its paired version favors the other. A declined bite at a stocked feeder costs one turn and preserves the ration. Every turn uses the existing one-bit eat/pass control and movement among actual holders. The public player receives its energy, previous action, permanent feeder signal, anonymous controls and the outward slot actually used.

The [joint report](decision.md) and [scientific referee handoff](referee_handoff.md) distinguish learned preference, causal memory and whole-game survival. The [first feeder study](../FEEDER-MEMORY-20261121-001/decision.md) and [previous cue study](../SECOND-FEEDER-CUE-20261121-001/decision.md) use their own original game and openings.

## Read the evidence

- [Rules, train/test separation and stop](preregistration.md), [independent prospective review](advisor.json) and [source bank](source_bank.json).
- [Actual training exposures, payoffs and controls](acquisition.md), [all charged training probes](training_receipts.csv), [frozen physical words](learned_words.json) and [independent refit](training_replay_repeat.json).
- [Exchange, clear and restore the learned part at a fixed decision](seed_replay.md), [all held decisions](mechanism_results.json) and [fresh matched real bites](opportunity_results.json).
- [Complete survival by law, version and comparison](survival_results.json), [paired founder means](survival_founders.csv) and [unattended episode ledger](survival_episodes.csv). The scientific results depend on the supplied access rule and the persistence of a training regime across fresh starts.

## Replay from the repository root

Use the repository Python environment. These checks regenerate results into a scratch directory. The weights digest comes from the [pre-evaluation release](release.json).

~~~sh
study=research/FEEDER-PAYOFF-REVERSAL-20261121-001
results_dir=$(mktemp -d)
weights=bec02cabdf000ba2e68655cc7ea533c9fbd9464f95bd6746e0c3abbca49c424b
.venv/bin/python -B "$study/reader_check.py" --check
.venv/bin/python -B "$study/training.py" --output "$results_dir"
cmp "$study/learned_words.json" "$results_dir/learned_words.json"
.venv/bin/python -B "$study/opportunities.py" --weights-sha "$weights" --out "$results_dir/fresh_bites.json"
.venv/bin/python -B "$study/survival.py" --weights-sha256 "$weights" --output-dir "$results_dir"
.venv/bin/python -B "$study/audit.py" --weights-sha "$weights" --output "$results_dir/audit.json"
.venv/bin/python -B "$study/replay.py" --weights-sha "$weights" --write "$results_dir/seed_replay.md"
cmp "$study/seed_replay.md" "$results_dir/seed_replay.md"
~~~

One natural episode can be played with the [seed CLI](seed_play.py). Use the [mechanism replay](replay.py) for the fixed-history intervention. The intervention route is imposed and terminates at the tested decision. The survival policies choose every turn themselves through death.

For example, the following two runs use the first ordinary-label, majority-A held-out game in candidate order on which the counter outlived the learner. This is an illustration selected from the complete ledger. They reproduce 22 and 29 turns respectively. The prespecified mechanism witness uses a different seed, selected by having both eligible clues before its outcomes were inspected.

~~~sh
.venv/bin/python -B "$study/seed_play.py" --weights-sha256 "$weights" --seed 18218318156473285168 --replicate 1 --law parity --version 0 --arm outcome
.venv/bin/python -B "$study/seed_play.py" --weights-sha256 "$weights" --seed 18218318156473285168 --replicate 1 --law parity --version 0 --arm count
~~~
