# Scientific referee handoff · Learning a letter distinction at unseen turns

**Computed, external scientific referee pending.** A separate Astra Max review approved the proposed design before freeze. The independent execution audit passed the fit, blind decisions and scoring for a negative primary result. Both even parity and not-all-equal went through the same phases. The complete counts, sample images and study interpretation are in the decision. [Decision](decision.md) · [Astra design review](design_review/red_team_report.json) · [Run authorization](audit/R1/red_team_report.json) · [Independent replay review](audit/R2/red_team_report.json)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt · above-chance recognition in every blind held-turn cell | **Status: Failed** | Each law passed 4 of 16 cells |
| Local direction · choose the smallest equally best pixel groups | Retire this frozen rule | 32/128 on held turns for the new designs |
| Broader exploration · learn from shape variation | Known alternatives | Quarter-turn-preserved groups also fit the training data |
| Long-term goal · G15 Learning in a knot pattern | Obstruction learned | An exchange of the learned state reversed every decision |

## What to challenge

1. Recheck the pre-freeze sources and timestamps. The contract fixes all 768 new images, both keys, the 64-item training order, every selection and vote tie, and the 16-cell pass criterion. Check the 400 predecessor images and normalized supports for overlap. Design E or F must have no globally training-seen ancestor under a turn or a reflected turn. The blind files carry only digest and pixels to the adapter. Every fitted model receives only the 64 pixel bits plus correctness on its own training guess. The scorer reads its test key after checking the blind release.
2. Verify the budget and source of every experience-dependent value. Count one pass over the same 64 inputs for all eleven training arms. Check that receipts reside in 7,296 physical holdings during training and are erased at finalization. Inspect the frozen membership bits and the class counts they use. Project the executable holder onto an open mark, dock and read with the other holders fixed and apply K1–K3. Exercise the two distinct full laws, the prepared-codeword negative and the free-relation negative. Keep the sensor, grouping, arithmetic and write policy attributed to the adapter.
3. Reconstruct the two fitted singletons and the opposite and shifted conventions independently from the training receipts. Check the class means, all remaining ties, per-pattern votes and every blind guess. Confirm the ordinary twin agrees and the previous approach is the original implementation retrained under the same budget. The prior full-histogram reader got 16/128 on the primary held turns, the new reader 32/128, and fair chance expects 64/128. Recover the count for each letter, new design, position condition and held turn. Check all representative mistakes as well as successes. Translations of the same shape produce the same count signature.
4. Keep each queried bitmap and recipient fixed. Compare its own state, the opposite donor, the sham, clear and restored state, then the membership-only counterfactuals with class sizes and totals fixed. The donor should reverse each of 704 guesses in both directions for both laws. At 270° a single default guess for L could attain the entire observed class split, so distinguish the two unanimous, state-dependent votes from the cleared default. Reproduce the prior, shifted and all-singleton scores without fitting on any held image.
5. Evaluate the limit of the explanation. The evidence establishes that the learner selected orientation-specific cues from reward. An inspection made **after** the sealed score found 240 training-optimal partitions, including 12 preserved by a quarter-turn. The four-member clue seen in the earlier study tied before the smallest-side preference. Undoing a frozen arbitrary permutation of category IDs must recover the learned groups, means and individual votes. Keep the post-score inspection confined to training evidence and keep the sealed result as the endpoint.

## Releases and commands

The record below contains external-to-runner commitments taken before the next phase existed. The score binds both the blind guesses and the scorer key. Timing and resource metadata are recorded in each release. The clean producer replay matched all 16 deterministic payload files byte for byte, including the eleven fitted checkpoints, all receipts, all actions, per-rule votes and scores. [Phase commitments](phase_anchors.jsonl) · [Auditor receipts](audit/phase_anchor_checks.json) · [Fitted states](../../artifacts/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups/fit/release.json) · [Blind guesses](../../artifacts/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups/blind/release.json) · [Score release](../../artifacts/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups/scored/release.json)

| Release | SHA-256 |
| --- | --- |
| Reviewed frozen contract | `fb105cc7d5a938237460c580e4caf993a25a2c02a650b48c57782811616f3957` |
| Fitted states, before blind reads | `af13bf46249bb96f45b564e01f7417317ca93c16fa5b335fe7ebf7e6b93b8df8` |
| Blind guesses, before test labels | `b6cebe7c5b60440e1ae86d42159156e1c34b32c38a6e2c4046fdd67383484f02` |
| Scored outcomes | `1622bb1debf728900a3a13154c35b650c9beaf4420393d5561090e7d56493375` |

Run from the repository root. The independent replay reconstructs 704 training action/reward receipts, 512 per-presentation physical state checks and 21,824 blind actions. The optional example ID below is the 180° L shown first in the decision.

```bash
ticket=LEARNED-PATCH-GROUPS-20261122-001
family="${ticket}-E001_groups"
spec="experiments/$ticket/$family"
archive="artifacts/$ticket/$family"
record="research/$ticket"
prior="experiments/PIXEL-LETTERS-20261122-001/PIXEL-LETTERS-20261122-001-E001_letters"
python3 -B scripts/track.py objects-gate "$record/preregistration.md"
python3 -B "$spec/panel.py" --check
python3 -B "$spec/check_knots.py"
python3 -B "$record/audit/panel_census.py" "$spec/panel" "$prior/panel"
python3 -B "$record/audit/phase_io.py" "$spec"
python3 -B "$record/audit/replay.py" "$spec" "$archive" --anchors "$record/phase_anchors.jsonl" \
  --scored-sha 1622bb1debf728900a3a13154c35b650c9beaf4420393d5561090e7d56493375
python3 -B "$record/replay_guess.py" --id 00c159d8 --law nae
python3 -B "$record/inspect_training_ties.py"
```

Use a fresh directory for a check of the original producer. Original phase directories reject overwrites.

```bash
replay_dir=$(mktemp -d)
python3 -B "$spec/study.py" train --out "$replay_dir"
python3 -B "$spec/study.py" predict --out "$replay_dir"
python3 -B "$spec/study.py" score --out "$replay_dir"
cmp "$archive/fit/nae-ordinary.json" "$replay_dir/fit/nae-ordinary.json"
cmp "$archive/blind/predictions.jsonl" "$replay_dir/blind/predictions.jsonl"
cmp "$archive/scored/scores.json" "$replay_dir/scored/scores.json"
```

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Disambiguate equally good training clues | 2/3 | 2/3 | Vary the training drawings → check for surviving single-pattern shortcuts | Alternative · deferred |

**STOP.** Both laws reached the frozen test. More varied training drawings could supply a meaningful discriminator, but this finite study ends at the observed failure.

**Corrections:** None.  
**Goals:** G15 gained a bounded result on how a reward-selected clue can fail to transfer.  
**Assumptions:** A207 records the population and group ranking.  
**Scaffolds:** The common local sensor, search, size preference, write and vote were supplied. Opposite and shifted rewards, changed membership, independent arithmetic and both underlying laws were tested.
