# Scientific referee handoff · Matched narrow and varied letter drawings

**Computed. External scientific referee pending.** The fixed physical reader scored 304/512 after narrow training and 256/512 after varied training on the same unseen-turn images, under each law. The external-to-runner fit and blind commitments preceded their successor phases. The prospectively reviewed design and independent release replay are complete. [Decision and counts](decision.md) · [Astra Max design review](design_review/red_team_report.json) · [Run authorization](audit/R1/red_team_report.json) · [Execution audit](audit/R2/red_team_report.json)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt · transfer from varied familiar-angle drawings | **Status: Failed** | 32/64 varied and 38/64 narrow cells passed |
| Local direction · hold the existing count sensor fixed | Retire for the strict gate | One L and T have the same full observation |
| Broader exploration · learn useful pixel relations | Known alternative | The raw witness bitmaps differ |
| Long-term goal · G15 Learning in a knot pattern | Obstruction learned | A change of learned group flags accounted for all between-arm changes |

## Evidence to test independently

1. Establish what changed between arms. Verify all 64 previous narrow bitmaps and their order. Independently reconstruct the A–D training allocations before the E/F catalogue is used. Recover the same 16 varied design pairs at both shown turns, with the common 16 straight bitmaps and 48 same-slot replacements. Check the digital pen-stroke continuity, bounding boxes, ink, true labels, turns, coordinates and matched reward strings. Count the classes separately. Recover the geometry-only quota change for base E, where two individually valid compound designs share a drawing orbit. Check all eight reserved designs against both training arms and all 1,168 previously examined images up to translation, rotation and reflection. The new pen shapes come from two basic dimension families with disclosed earlier template ancestry. [Independent reconstruction](audit/panel_audit.json)
2. Verify the contract sources and three releases against the digests below. Trace the source file imports to the exact predecessor physical and integer reader. The trainer passes 64 raw bits and then one correctness bit following its own output. Check all 768 emitted actions and rewards, together with the before/after physical checkpoint hashes. The receipts are erased after fitting. The new fitted class totals and flags are actual words in 40,494 holdings per physical reader. Rerun the archived K1–K3 open-holder tests and their negative controls. Examine what the software supplies before attributing an advantage to either underlying relation.
3. Recompute all 32,767 partition ranks per training arm and verify both physical fits and integer twins. The narrow fit must reproduce 240 infinite-rank partitions and its two singleton votes. The varied fit must reproduce two finite co-winners of rank 121/31. Its smaller group counts raw patterns 0111 and 1101. The other also counts 1111, absent throughout these data. Verify their respective memberships, class means and actual decisions, including at ties. A diagnostic of the earlier four-pattern clue belongs to the training-only interpretation. [Group census](../../artifacts/VARIED-LETTER-DRAWINGS-20261122-001/VARIED-LETTER-DRAWINGS-20261122-001-E001_drawings/group_diagnostics.json)
4. Replay all 45,056 decisions. Check the two ordinary donors, both directions of opposite-label exchange, flag-only exchanges, calibration contrasts, clearing, sham and restore on the same pixels. The narrow and varied teaching schedules are matched within each convention. Do not count a shared default at a narrow split vote as a failed state transplant. Recompute the paired gains and losses per true class/held turn/design and for the two sets of anchors. Sixteen translations of one design at one angle are one underlying case. [Independent outputs](audit/replay_result.json)
5. Separate the claim about the particular fitted learner from the observation limit. Reconstruct the 270° L from the second square design and the 180° T from the first square design at (1,1), count all 81 padded two-by-two windows directly, and verify their entire vectors agree. They differ in raw pixels. Across the held turns the mixed signature contains 16 images of each label. This rules out passing the strict gate even with an arbitrary deterministic rule on that fixed sensor. The empirical ceilings of 496/512 for the full counts and 336/512 for each retained representation are explanatory, label-aware bounds. No additional trained predictor received a held outcome. [Independent collision proof by enumeration](audit/sensor_obstruction.json) · [One same-position collision](show_sensor_collision.py)

## Seals and reproduction

| Stage | SHA-256 |
| --- | --- |
| Proposed contract reviewed by Astra Max | `1d11141dd5ee6396b464fd45604055ebe867eed85a30b4bac292258cfa9366a6` |
| Detached frozen contract | `6c2bcbd04d566b8d15905c7845c08a257f4419e6b8aa2fa020160d2436dba365` |
| Fitted states, before opening the blind stream | `63e79cdff679e2a3d58207cb51aed37a92c66315ac7b6197e178189219563c98` |
| Blind decisions, before opening the test answer key for scoring | `f646cec745d0d1cc645524291e97704dd5adf51ba8fdb0a30f8b3f1981155701` |
| Scored results | `07635ca02bc204f5a045286976fd3e7768943cbe2a85e8ddf6e3ae64a29679a9` |

The main runner measured 1.22 seconds for fitting, 8.13 for blind inference and 0.19 for scoring on CPU. The peak among the three was 34,540 KiB. The supplementary advisor returned an account quota limit. Astra Max completed the requested prospective review and supplied the matched-order and flag-versus-calibration checks. [Advisor record](advisor.json) · [Anchors](phase_anchors.jsonl) · [Fitted release](../../artifacts/VARIED-LETTER-DRAWINGS-20261122-001/VARIED-LETTER-DRAWINGS-20261122-001-E001_drawings/fit/release.json) · [Blind release](../../artifacts/VARIED-LETTER-DRAWINGS-20261122-001/VARIED-LETTER-DRAWINGS-20261122-001-E001_drawings/blind/release.json) · [Score release](../../artifacts/VARIED-LETTER-DRAWINGS-20261122-001/VARIED-LETTER-DRAWINGS-20261122-001-E001_drawings/scored/release.json)

The following commands run from the repository root.

```bash
ticket=VARIED-LETTER-DRAWINGS-20261122-001
family="${ticket}-E001_drawings"
spec="experiments/$ticket/$family"
record="research/$ticket"
archive="artifacts/$ticket/$family"
previous="experiments/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups"
first="experiments/PIXEL-LETTERS-20261122-001/PIXEL-LETTERS-20261122-001-E001_letters"
python3 -B scripts/track.py objects-gate "$record/preregistration.md"
python3 -B "$spec/panel.py" --check
python3 -B "$record/audit/panel_audit.py" "$spec/panel" "$previous/panel" "$first/panel"
python3 -B "$previous/check_knots.py"
python3 -B "$record/audit/phase_io.py" "$spec" "$previous/learner.py"
python3 -B "$record/audit/outcome_replay.py" "$spec" "$archive" --anchors "$record/phase_anchors.jsonl" \
  --scored-sha 07635ca02bc204f5a045286976fd3e7768943cbe2a85e8ddf6e3ae64a29679a9
python3 -B "$record/inspect_held_groups.py"
python3 -B "$record/audit/signature_obstruction.py" "$spec/panel"
python3 -B "$record/show_sensor_collision.py"
python3 -B "$record/replay_examples.py" --id 01700eb7 --law nae
python3 -B "$record/reproduce.py"
```

The first post-score wrapper, preserved as reviewed, gave the frozen group diagnostic all four turns. It rejected that input before emitting results. The replacement invocation above passes only the intended 512 held-turn cases and compares to the same archived narrow reference. Both the frozen scorer and the independent audit had already defined the primary population correctly. The final command creates fresh temporary phase directories, records new anchors and compares all 18 deterministic payload files byte for byte with the original releases.

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Retain the arrangement that distinguishes the witness pair | 2/3 | 3/3 | Separate the pair with generic pixel wiring → test on new blind drawings | Alternative · deferred |

**STOP.** Training variation alone cannot make the unchanged sensor distinguish the exhibited pair. An arrangement-sensitive observation would define a new comparison.

**Corrections:** No earlier scientific claim changed. The supplementary invocation and its correction are documented above.

**Goals:** G15 gained a measured change in learned membership and a finite sensing obstruction.

**Assumptions:** A208 records the fixed treatment and weighting.

**Scaffolds:** Shared local wiring, stroke generation, ranking and writing and reading the chosen pattern groups are supplied. The donor and integer controls delimit the result.
