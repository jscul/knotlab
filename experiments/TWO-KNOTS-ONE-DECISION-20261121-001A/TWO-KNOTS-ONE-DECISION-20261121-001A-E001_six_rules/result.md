# Six signed rules and lawful controls

Exact exploratory code analysis. The signed compiler accepts every preparation. The eight positive binary cells on each of nine settings have mass 1/8. All 576 ordinary cells match the earlier benchmark. The coherent reader maintains complete local transcript privacy and loses later agreements. The central matcher preserves agreements at a cost detectable in a three-slot sweep. [Scientific report](../../../research/TWO-KNOTS-ONE-DECISION-20261121-001A/results.md) · [Frozen design](../../../research/TWO-KNOTS-ONE-DECISION-20261121-001/preregistration.md)

[Saved prospective prediction](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001A/TWO-KNOTS-ONE-DECISION-20261121-001A-E001_six_rules/prospective.json) · [Pre-comparison timestamp and digest](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001A/TWO-KNOTS-ONE-DECISION-20261121-001A-E001_six_rules/prediction_receipt.json) · [Subsequent archive comparison](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001A/TWO-KNOTS-ONE-DECISION-20261121-001A-E001_six_rules/archive_comparison.json) · [Complete computed evidence](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001A/TWO-KNOTS-ONE-DECISION-20261121-001A-E001_six_rules/results.json.gz) · [Runtime](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001A/TWO-KNOTS-ONE-DECISION-20261121-001A-E001_six_rules/replay_runtime.txt)

## Reproduction

Run from the repository root with standard Python 3.11 or later. The committed evidence is write-once by the producer. The exact runner uses a single process and a 4 GiB address-space cap.

~~~bash
six=TWO-KNOTS-ONE-DECISION-20261121-001A
experiment=experiments/$six/$six-E001_six_rules
evidence=artifacts/$six/$six-E001_six_rules
replay=$(mktemp -d "${TMPDIR:-/tmp}/six-rules-replay-XXXXXX")
python3 -B "$experiment/predict.py" --output "$replay/prospective.json"
cmp "$evidence/prospective.json" "$replay/prospective.json"
python3 -B "$experiment/run.py" --output "$replay/results.json.gz"
cmp "$evidence/results.json.gz" "$replay/results.json.gz"
python3 -B "$experiment/verify.py" "$evidence"
~~~

The prediction producer uses standard-library finite arithmetic and its own mask equations. The main replay reads the shared exact compiler, physical-word reader and literal reader. It checks their first tables against the standalone calculation and expands joint pointer amplitudes for the tagged checks. Archive access is isolated in [compare.py](compare.py). Its output has a separate comparison timestamp.

For an exact joint trace with every visible field and each branch's calculation state, use a selected fixed pair of scripts. Each list gives one request per slot, with `null` for idle. The optional final tag pair accepts `none`, `held`, `ignored` or `uncomputed` for each role. Use `--allow-all-addresses` for the non-game controls with the same address on both wings or a one-reader sequence through all holders.

~~~bash
python3 -B "$experiment/run.py" --case '["signed","coherent",[0,1,0],[3,3,3]]' --output "$replay/trace.json"
python3 -B "$experiment/run.py" --case '["signed","coherent",[0],[3],["held","held"]]' --output "$replay/marked.json"
~~~

## Evidence layout

- Each fresh table has 64 ordered binary entries, nine entries in the left failure row and eight in the extra right failure column. The failure corner appears once. When preparation always refuses, the accepted-source table is `null`.
- A sparse law lists its numerators, common denominator, number of positive entries and available dimension and zero count. It includes the shared pre-question herald. A positive accepted-source law is recovered from launch by retaining `source_ready` and dividing by the reported acceptance mass. Fixed two-slot settings retain metrics and denominators for all conditions, full joint laws on immediate repetitions and all nonzero private TV comparisons with their first differing prefixes. The fixed script replay gives every complete joint history including its latent conditional states. Sweep, adaptive and one-reader laws retain their complete local records.
- Each local code gives requested holder, status, raw word, displayed word and readable tag. Answers are slot-indexed bit masks, with the first displayed place at bit 0. [The decoder](replay.py) supplies the remaining observable fields from the already declared local schedule and the history of the corresponding reader. This includes its own role's address bank, ordered marks, receipt, capacity, successful or missing write, physical exchanges and unchanged earlier keeper contents. Private laws include no calculated data state or remote diagnostic trace. The common proof establishes the trace-preservation argument for arbitrary finite adaptive local protocols of the specified kind.
- The relaxed compiler reaches the strict device with no reversals on every catalogue here. Its certificate is retained and its measured distributions reference the identical strict measurements. The separately named nonminimal calibration checks raw versus displayed scores on an intentional one-incidence change.
- The [shared mechanism audit](../../../research/TWO-KNOTS-ONE-DECISION-20261121-001/mechanism.md) supplies the native funded birth, actual guard, ternary exchanges, earlier switch and lost clock tick. This lane supplies the finite six-rule, both six-holder lawful and both two-holder lawful replays. Scientific referee pending.
