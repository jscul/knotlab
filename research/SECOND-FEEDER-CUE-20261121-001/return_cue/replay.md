# Certified return replay

The repaired device removes the old menu-match guard from the strict-return offer. The other three detectors keep their guards. The prepared action still uses mark 6.

Frozen weights SHA-256 `60767f960e50d2dbe499502a81c4605ca8480d61d5ad8b53b07b3d52fa777979`.

| Law | Strict training receipts | Paid | Score from count | Final fitted scores | Fitted cue | Count-only cue |
|---|---:|---:|---:|---|---|---|
| parity | 9 | 0 | 7 | `[7, -5, -5, -3]` | `strict_return` | `strict_return` |
| not-all-equal | 9 | 0 | 7 | `[7, -5, -5, -3]` | `strict_return` | `strict_return` |

A certified return has already paid its ration. Seven charged strict vetoes saturate the strict score at 7, and its first tie priority forces selection there.
For these training receipts the supplied count threshold reproduces the deployed selector. Actual feedback updates the score words. The certified-opportunity count suffices to select the deployed rule.

| Law | Count-only matches of full histories | Lifetime ties | Count-only matches of common-path decisions |
|---|---:|---:|---:|
| parity | 512/512 | 512/512 | 2964/2964 |
| not-all-equal | 512/512 | 512/512 | 2964/2964 |

## Frozen fitted reader under both laws

The parity and not-all-equal seed replays were checked separately and have the same displayed trace.

Seed `942994390279659641`, tapes `6240676702441903461, 6240676702441903461`, primary comparison. Prefix actions were supplied.

| Turn | History ending at the empty feeder | History ending at the full feeder |
|---:|---|---|
| 1 | PASS K4 → K3 via d9 (port 0), energy 6→5 | PASS K4 → K3 via d9 (port 0), energy 6→5 |
| 2 | PASS K3 → K15 via d8 (port 2), energy 5→4 | PASS K3 → K15 via d8 (port 2), energy 5→4 |
| 3 | EAT at K15, ration consumed, energy 4→7 | EAT at K15, ration consumed, energy 4→7 |
| 4 | EAT at K15, no ration, energy 7→6 | PASS K15 → K3 via d8 (port 0), energy 7→6 |
| 5 | PASS K15 → K26 via d35 (port 1), energy 6→5 | EAT at K3, no ration, energy 6→5 |
| 6 | PASS K26 → K15 via d35 (port 0), energy 5→4 | PASS K3 → K14 via d1 (port 1), energy 5→4 |

On turn 7, the bot sees feeder on, energy 4, previous action move and ports 0, 1, 2 in both histories. Spectators see K15 empty and K14 full.

Both preparations hold first memory `101` (one port at the last paid meal), active cue `strict_return`, and ready action `100`.
The empty side’s last paid EAT was at K15 on turn 3. The receipt stored the pre-action arrival menu `0001` in `x_paid_menu`, which had held `1000`.
The full side’s last paid EAT was at K15 on turn 3. The receipt stored the pre-action arrival menu `0001` in `x_paid_menu`, which had held `1000`.

| Differing word | Empty history | Full history |
|---|---|---|
| `x_here` | `01` (paid-site certificate present) | `10` (certificate absent) |
| `arr_from` | `001` (feeder origin) | `010` (nonfeeder origin) |
| `arr_menu` | `0010` (one port) | `0001` (multiple ports) |
| `arr_slot` | `010` | `001` |

The X differences are `x_here`.
The physical action mark was read for both histories in every arm before any forked game advanced.

| Arm | Recorded empty-side bit and game result | Recorded full-side bit and game result |
|---|---|---|
| original | 0 · PASS K15 → K3 via d8 (port 2), energy 4→3 | 1 · EAT at K14, ration consumed, energy 4→7 |
| sham | 0 · PASS K15 → K3 via d8 (port 2), energy 4→3 | 1 · EAT at K14, ration consumed, energy 4→7 |
| swap | 1 · EAT at K15, no ration, energy 4→3 | 0 · PASS K14 → K25 via d2 (port 2), energy 4→3 |
| erased | 1 · EAT at K15, no ration, energy 4→3 | 1 · EAT at K14, ration consumed, energy 4→7 |
| selected field | 1 · EAT at K15, no ration, energy 4→3 | 0 · PASS K14 → K25 via d2 (port 2), energy 4→3 |

Public-history verdicts were `empty` and `unknown`.
In the separate two-charged-turn control, PASS first versus EAT first leaves 2 versus 2 energy on the empty side and 6 versus 6 on the full side.

The empty history keeps M=`101` while the current menu would match `011`. Its certified return has `x_here=01`. Reading the same prepared words gives bit 1 under the old guard and bit 0 under the repaired guard.

The independently verified preset strict-return control has the same displayed trace.

The independently verified old-menu-mismatch decision has the same displayed trace.
