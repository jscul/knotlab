# Exact replay for the eight signed holdings

The strict experiment has a named contradiction $0=1$. All sixteen launch questions receive two preparation refusals. One local reversal at holder 1 on distinction 0 yields the explicit calibrated device, with launch score 15/16. The independent finite derivation and the shared measurement agree on every launch and accepted-source cell. The uniform centralized comparison agrees with the archived fresh table and leaks the far setting in the held-reader sweep. [Scientific record](../../../research/TWO-KNOTS-ONE-DECISION-20261121-001B/results.md).

## Replay

From the repository root, run the following with Python 3 and its standard library. The independent derivation, measurement and archived comparison write to a fresh directory. The measurement never imports the archived reference.

~~~bash
lane_id=TWO-KNOTS-ONE-DECISION-20261121-001B
lane_exp="experiments/$lane_id/$lane_id-E001_eight_knots"
lane_ref="artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/games.json"
lane_dir=$(mktemp -d)
ulimit -v 4194304
python3 -B "$lane_exp/derive.py" --output "$lane_dir/predictions.json"
python3 -B "$lane_exp/run.py" --output "$lane_dir/run"
python3 -B "$lane_exp/compare.py" \
  --predictions "$lane_dir/predictions.json" \
  --fresh "$lane_dir/run/fresh.json.gz" \
  --archive "$lane_ref" \
  --output "$lane_dir/run/reference_comparison.json" \
  --check-histories
~~~

The frozen design digest is `83095b5467e30fb395e0005986fbb07fea14e3e8ad67a2e45fb94f7c7d3a41a2`. The independent derivation sealed `d65aa60b9e20625e641e5a5afee92da17d5c504fef6d38be21d13f7439203bf4` before reference comparison. It runs directly from the finite holding names and local charge vector. The common compiler fixture is also generated from those inputs. Every weighting is exact and no draws use a random seed. The independent derivation took under a second. The final clean-directory measurement used 43.43 seconds and peaked at 400,128 KiB on one CPU. The reference and history validation took 1.11 seconds. It rechecked 34,452 sparse table or witness rows across twelve principal, literal and independent source variants. The recorded history bytes reproduced exactly before and after the shared compiler added its complete equation provenance.

## Retained records

| File | Contents |
| --- | --- |
| [predictions.json](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001B/TWO-KNOTS-ONE-DECISION-20261121-001B-E001_eight_knots/predictions.json) | Named XOR certificate, all minimum calibrations, physical words, launch and accepted-source probabilities |
| [fresh.json.gz](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001B/TWO-KNOTS-ONE-DECISION-20261121-001B-E001_eight_knots/run/fresh.json.gz) | Exact cell and record laws, physical states, unilateral predictions, recodings, failed writing, first-mark tags and lawful two-holder control |
| [history_index.json](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001B/TWO-KNOTS-ONE-DECISION-20261121-001B-E001_eight_knots/run/history_index.json) | Full record decoder, script summaries, privacy witnesses and sweep bounds |
| [histories.jsonl.gz](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001B/TWO-KNOTS-ONE-DECISION-20261121-001B-E001_eight_knots/run/histories.jsonl.gz) | Sparse joint and private histories in exact integer numerators with a common denominator per table |
| [reference_comparison.json](../../../artifacts/TWO-KNOTS-ONE-DECISION-20261121-001B/TWO-KNOTS-ONE-DECISION-20261121-001B-E001_eight_knots/run/reference_comparison.json) | Post-seal equalities, per-setting distances and disagreements, independent archive and named-row checks |

An ordinary word in these tables is an integer with its low bit at the first listed distinction. The fresh displayed alphabet uses 8 for the refusal or missing-output row and column. The full records distinguish sources of missing output and idle slots. Unlisted cells have probability zero. Accepted-source tables are null when the readiness herald has zero mass. The historical comparator's listed word strings use lexical order. The replay maps its slots explicitly before comparing.

These results test the existing exploratory contract. The calibration and pointer are supplied operations. The finite replay is experiment evidence, and the certificates and proof supply the stated mathematical obstructions.
