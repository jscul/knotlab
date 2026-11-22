# Scientific referee handoff · Raw-pixel L and T

The formal scientific referee is pending. This is a single owner-assigned G15 ticket. A fresh-context design reviewer and a separate implementation auditor completed the before-data review, run approval and independent numerical replay. The [decision](decision.md) gives exact class counts, the observed failure, examples and block-by-block interpretation. [R0](design_review/red_team_report.json) · [R1](audit/R1/red_team_report.json) · [R2](audit/R2/red_team_report.json)

| Scope | Verdict | Decisive check |
| --- | --- | --- |
| Fresh images at familiar orientations | **Status** · Successful | 136/136, each image has a training-seen count signature |
| Untrained orientations | Failed | 50/200, including 0/100 T |
| Causal use of retained state | Successful | Both donor directions reverse all 336 actions in each law |
| G15 · Learning in a knot pattern | Capability gained | Same wiring, opposing rewards, different physical states and decisions |

## Checks requested

1. Read the prior-work section of the [preregistration](preregistration.md). Re-run its object-index searches and one independent search for earlier image studies. The predecessor allowed its reader two named clues. Here the only delivered stimulus is the 64 raw pixel bits.
2. Regenerate all 400 five-pixel images independently. Check each class has two styles and identical placement support. The held-out conditions are disjoint; bitmaps have no collisions. Check train and familiar have the other style at the exact same pose. Check placement invariance using the padded feature extractor and distinguish a new bitmap from a new pixel histogram. Audit the training-key and test-key paths separately. Neither ID nor position in the presentation order enters the learner.
3. Challenge both the preparation and the open holder law. At one actual register place, release the coding restriction and enumerate the allowed states with the other 415 places fixed. Verify the canonical checker on both projections, on the two-codeword negative and on the unconstrained relation. The learned holdings supply state to ordinary external arithmetic. Check the actual forced read before accepting the prediction.
4. Inspect the [phase anchors](phase_anchors.jsonl) and the independent auditor's [separate receipts](audit/phase_anchors.json). Refit both label conventions from neutral with each arm's own guess and correctness feedback, then release every state before prediction. Recompute the whole held-out panel and the class-specific scores. A round trip through the opposite learned word and back must leave every other property of a recipient fixed. Score the crossed word using the original recipient's meaning of its bit. Include failures, including wrong non-tied guesses.
5. Check the independent ordinary mean-histogram classifier and the raw-bitmap nearest-neighbor comparator on the same 64 training examples. Recompute class means from the learned marks and the single-example costs. Inspect the post-score three-lit-pixel sum as a descriptive check of retained information. It was absent from the sensor, credit rule, stage locks and deployed readout. A different future rule would need fresh letters.

From the repository root, these read-only commands reproduce the checks and one scored example. The independent replay compares all 448 training receipts and 7,728 blind actions against the frozen records.

```bash
ticket=PIXEL-LETTERS-20261122-001
family="${ticket}-E001_letters"
spec="experiments/$ticket/$family"
archive="artifacts/$ticket/$family"
record="research/$ticket"
python3 -B scripts/track.py objects-gate "$record/preregistration.md"
python3 -B "$spec/panel.py" --check
python3 -B "$spec/check_knots.py"
python3 -B "$record/audit/verify.py" "$spec/panel" --check-preparations --check-phase-io
python3 -B "$record/audit/replay.py" "$spec" "$archive" \
  --fit-anchor 1fba63dd4c28923c7e57a0176b7b003f7380e6d9ff667fa5aa45e4c52dfc8416 \
  --blind-anchor 6120eef599ad6811310448becda96c3abfdc30ab333fe4c3fa4d852a27d55fc4
python3 -B "$record/replay_guess.py" --id 038bf625 --law nae
```

For a clean run of the original producer, use a new directory for the three stages. The output contains the training receipts, individual physical words, blind actions and scored table. Timing fields vary on replay. Fitted words, blind predictions and the scores reproduce byte for byte.

```bash
replay_dir=$(mktemp -d)
python3 -B "$spec/study.py" train --out "$replay_dir"
python3 -B "$spec/study.py" predict --out "$replay_dir"
python3 -B "$spec/study.py" score --out "$replay_dir"
cmp "$archive/fit/parity-ordinary.json" "$replay_dir/fit/parity-ordinary.json"
cmp "$archive/blind/predictions.jsonl" "$replay_dir/blind/predictions.jsonl"
cmp "$archive/scored/scores.json" "$replay_dir/scored/scores.json"
```

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Learn which rotated patterns to count together | 2/3 | 2/3 | Fit on fresh shapes → score a held turn | Alternative · deferred |

**STOP.** The requested comparison is complete. The first failure was held-orientation readout despite a class distinction present in the measured counts.

**Corrections:** None.  
**Goals:** G15 gained a bounded demonstration of visual learning in retained knot state.  
**Assumptions:** A205 covers this weighting and supplied apparatus.  
**Scaffolds:** The sensor wiring, two class banks, credit and mean comparison were supplied. Opposite rewards and the two open laws were exercised.

