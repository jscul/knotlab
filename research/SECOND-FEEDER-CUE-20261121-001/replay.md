# Second feeder cue replay

## Frozen training check

Pinned weights SHA-256 `40a5466895f942a194cd8eb97f02bb70965ac2e9b6da3c223556611ad105753c`.

| Law | Charged veto opportunities | Receipts that changed scores | Final scores | Active cue |
|---|---:|---:|---|---|
| parity | 713 | 602 | `[0, -3, -3, -5]` | `none` |
| not-all-equal | 713 | 602 | `[0, -3, -3, -5]` | `none` |

The scores are in the fixed order strict return, approach feeder, approach menu and approach slot. Ordered public receipts reproduced every packet and final word, with one eligible episode per law also replayed physically. A final selector of `none` leaves the current-only action in force.

Permuted feedback ended at `[0, -5, -5, -6]` under parity and `[0, -7, -7, -5]` under not-all-equal, with selector `none` under both.

The replay uses the archived game and the frozen device with separate checks for public receipts, physical offers and credit arithmetic. On game copies, changing private stock, cursor and tape while preserving the public observation preserved the prepared read.

## Frozen fitted reader under both laws

The parity and not-all-equal seed replays were checked separately and have the same displayed trace.

Seed `4151710084615049439`, tapes `13733146636244823494, 13733146636244823494`, primary comparison. Prefix actions were supplied.

| Turn | History ending at the empty feeder | History ending at the full feeder |
|---:|---|---|
| 1 | PASS K0 → K7 via d35 (port 0), energy 6→5 | PASS K0 → K7 via d35 (port 0), energy 6→5 |
| 2 | PASS K7 → K0 via d35 (port 1), energy 5→4 | PASS K7 → K0 via d35 (port 1), energy 5→4 |
| 3 | PASS K0 → K6 via d7 (port 1), energy 4→3 | PASS K0 → K6 via d7 (port 1), energy 4→3 |
| 4 | EAT at K6, ration consumed, energy 3→6 | EAT at K6, ration consumed, energy 3→6 |
| 5 | PASS K6 → K4 via d29 (port 1), energy 6→5 | EAT at K6, no ration, energy 6→5 |
| 6 | EAT at K4, no ration, energy 5→4 | PASS K6 → K14 via d28 (port 2), energy 5→4 |
| 7 | PASS K4 → K6 via d29 (port 4), energy 4→3 | PASS K14 → K7 via d46 (port 2), energy 4→3 |

On turn 8, the bot sees feeder on, energy 3, previous action move and ports 0, 1, 2 in both histories. Spectators see K6 empty and K7 full.

Both preparations hold first memory `011` (multiple ports at the last paid meal), active cue `none`, and ready action `100`.
The empty side’s last paid EAT was at K6 on turn 4. The receipt stored the pre-action arrival menu `0001` in `x_paid_menu`, which had held `1000`.
The full side’s last paid EAT was at K6 on turn 4. The receipt stored the pre-action arrival menu `0001` in `x_paid_menu`, which had held `1000`.

| Differing word | Empty history | Full history |
|---|---|---|
| `arr_from` | `010` (nonfeeder origin) | `001` (feeder origin) |

The two X words agree before the interventions.
The physical action mark was read for both histories in every arm before any forked game advanced.

| Arm | Recorded empty-side bit and game result | Recorded full-side bit and game result |
|---|---|---|
| original | 1 · EAT at K6, no ration, energy 3→2 | 1 · EAT at K7, ration consumed, energy 3→6 |
| sham | 1 · EAT at K6, no ration, energy 3→2 | 1 · EAT at K7, ration consumed, energy 3→6 |
| swap | 1 · EAT at K6, no ration, energy 3→2 | 1 · EAT at K7, ration consumed, energy 3→6 |
| erased | 1 · EAT at K6, no ration, energy 3→2 | 1 · EAT at K7, ration consumed, energy 3→6 |
| selected field | 1 · EAT at K6, no ration, energy 3→2 | 1 · EAT at K7, ration consumed, energy 3→6 |

Public-history verdicts were `unknown` and `unknown`.
In the separate two-charged-turn control, PASS first versus EAT first leaves 5 versus 1 energy on the empty side and 1 versus 5 on the full side.

## Preset strict-return control under both laws

The parity and not-all-equal seed replays were checked separately and have the same displayed trace.

Seed `5383868181617845372`, tapes `412991864232508913, 412991864232508913`, primary comparison. Prefix actions were supplied.

| Turn | History ending at the empty feeder | History ending at the full feeder |
|---:|---|---|
| 1 | PASS K2 → K6 via d54 (port 1), energy 6→5 | PASS K2 → K6 via d54 (port 1), energy 6→5 |
| 2 | EAT at K6, ration consumed, energy 5→8 | EAT at K6, ration consumed, energy 5→8 |
| 3 | PASS K6 → K2 via d54 (port 0), energy 8→7 | PASS K6 → K2 via d54 (port 0), energy 8→7 |
| 4 | PASS K2 → K6 via d54 (port 1), energy 7→6 | PASS K2 → K6 via d54 (port 1), energy 7→6 |
| 5 | PASS K6 → K15 via d26 (port 2), energy 6→5 | PASS K6 → K15 via d26 (port 2), energy 6→5 |
| 6 | PASS K15 → K11 via d52 (port 0), energy 5→4 | PASS K15 → K11 via d52 (port 0), energy 5→4 |
| 7 | PASS K11 → K23 via d4 (port 0), energy 4→3 | EAT at K11, ration consumed, energy 4→7 |
| 8 | PASS K23 → K11 via d4 (port 0), energy 3→2 | PASS K11 → K2 via d20 (port 2), energy 7→6 |
| 9 | EAT at K11, ration consumed, energy 2→5 | PASS K2 → K5 via d3 (port 2), energy 6→5 |
| 10 | PASS K11 → K23 via d4 (port 0), energy 5→4 | PASS K5 → K0 via d7 (port 0), energy 5→4 |
| 11 | PASS K23 → K11 via d4 (port 0), energy 4→3 | PASS K0 → K8 via d10 (port 2), energy 4→3 |

On turn 12, the bot sees feeder on, energy 3, previous action move and ports 0, 1, 2 in both histories. Spectators see K11 empty and K8 full.

Both preparations hold first memory `011` (multiple ports at the last paid meal), active cue `strict_return`, and ready action `100`.
The empty side’s last paid EAT was at K11 on turn 9. The receipt stored the pre-action arrival menu `0010` in `x_paid_menu`, which had held `0001`.
The full side’s last paid EAT was at K11 on turn 7. The receipt stored the pre-action arrival menu `0001` in `x_paid_menu`, which had held `0001`.

| Differing word | Empty history | Full history |
|---|---|---|
| `x_here` | `01` (paid-site certificate present) | `10` (certificate absent) |
| `x_paid_menu` | `0010` (one port) | `0001` (multiple ports) |
| `arr_from` | `001` (feeder origin) | `010` (nonfeeder origin) |
| `arr_menu` | `0010` (one port) | `0001` (multiple ports) |

The X differences are `x_here`, `x_paid_menu`.
The physical action mark was read for both histories in every arm before any forked game advanced.

| Arm | Recorded empty-side bit and game result | Recorded full-side bit and game result |
|---|---|---|
| original | 0 · PASS K11 → K23 via d4 (port 0), energy 3→2 | 1 · EAT at K8, ration consumed, energy 3→6 |
| sham | 0 · PASS K11 → K23 via d4 (port 0), energy 3→2 | 1 · EAT at K8, ration consumed, energy 3→6 |
| swap | 1 · EAT at K11, no ration, energy 3→2 | 0 · PASS K8 → K22 via d2 (port 0), energy 3→2 |
| erased | 1 · EAT at K11, no ration, energy 3→2 | 1 · EAT at K8, ration consumed, energy 3→6 |
| selected field | 1 · EAT at K11, no ration, energy 3→2 | 0 · PASS K8 → K22 via d2 (port 0), energy 3→2 |

Public-history verdicts were `empty` and `unknown`.
In the separate two-charged-turn control, PASS first versus EAT first leaves 5 versus 1 energy on the empty side and 5 versus 5 on the full side.

With these same prepared histories, the fitted reader retains differences in `x_here`, `x_paid_menu` and has selector `none`. Its original bits are `1/1`, and exchanging X gives `1/1`. Neutralizing X gives `1/1`.
