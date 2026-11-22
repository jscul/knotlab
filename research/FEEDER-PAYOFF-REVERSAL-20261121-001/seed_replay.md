# Feeder payoff reversal seed replay

Released learned word hash `bec02cabdf000ba2e68655cc7ea533c9fbd9464f95bd6746e0c3abbca49c424b`.

## Actual acquisition receipts

| Law | Version | Charged A | A paid | Charged B | B paid |
|---|---:|---:|---:|---:|---:|
| parity | 0 | 64 | 48 | 64 | 16 |
| parity | 1 | 64 | 16 | 64 | 48 |
| not-all-equal | 0 | 64 | 48 | 64 | 16 |
| not-all-equal | 1 | 64 | 16 | 64 | 48 |

| Version | Credit condition | Signed score | 32 learned pairs, least significant first |
|---|---|---:|---|
| 0 | outcome | +32 | `1010101010011010101010101010101010101010101010101010101010101010` |
| 0 | count | +0 | `1010101010101010101010101010101010101010101010101010101010101010` |
| 0 | shuffled | +0 | `1010101010101010101010101010101010101010101010101010101010101010` |
| 1 | outcome | -32 | `1010101010010101010101010101010101010101010101010101010101010101` |
| 1 | count | +0 | `1010101010101010101010101010101010101010101010101010101010101010` |
| 1 | shuffled | +0 | `1010101010101010101010101010101010101010101010101010101010101010` |

The first matched pair was also rerun through the physical writer for each fitted arm. The two entries below are the actual charged bites in recorded order.

| Version | Credit condition | First actual bite and score update | Second actual bite and score update |
|---|---|---|---|
| 0 | outcome | B denied 1→0, score +0→+0 | A paid 1→4, score +0→+1 |
| 0 | count | B denied 1→0, score +0→-1 | A paid 1→4, score -1→+0 |
| 0 | shuffled | B denied 1→0, score +0→-1 | A paid 1→4, score -1→-1 |
| 1 | outcome | B paid 1→4, score +0→-1 | A denied 1→0, score -1→-1 |
| 1 | count | B paid 1→4, score +0→-1 | A denied 1→0, score -1→+0 |
| 1 | shuffled | B paid 1→4, score +0→-1 | A denied 1→0, score -1→-1 |

## Frozen mechanism comparison

The prospectively first founder with both matched arrival clues was selected from public pass-only paths. Each intervention was read on the same ready action mark before any fork advanced.

Founder seed `5152685336963129192`, replicate 6, decision turn 6.

Parity and not-all-equal were replayed separately and give this same displayed trace.

### Ordinary cue A on tape 15017661208506867840

Both versions follow these physical passes. The mirrored code retains every move and exchanges the paired public slot names.

| Turn | Growth | Charged pass | Ordinary slot | Mirrored slot | Arrival clue in the ordinary code |
|---:|---|---|---:|---:|---|
| 1 | Formation 1 adds K7–K18 | PASS K3 → K18 via d2, energy 6→5 | 0 | 1 | A |
| 2 | — | PASS K18 → K3 via d2, energy 5→4 | 0 | 0 | — |
| 3 | — | PASS K3 → K17 via d73, energy 4→3 | 1 | 0 | B |
| 4 | — | PASS K17 → K3 via d73, energy 3→2 | 0 | 0 | — |
| 5 | Formation 2 adds K19–K31 | PASS K3 → K18 via d2, energy 2→1 | 0 | 1 | A |

**Ordinary code**

Turn 6 is at stocked K18. Both readers see the feeder on, energy 1, previous move and anonymous ports 0, 1, 2. The preceding real movement wrote clue A into route word `010`. First receipt `110` and prepared action `100` are fixed. The spectator’s opening is A in version 0 and B in version 1.

| Prepared arm | Version 0 learned score, bit and game result | Version 1 learned score, bit and game result |
|---|---|---|
| Resident word | `+32` · bit 1 · EAT at K18, ration consumed, energy 1→4 | `-32` · bit 0 · PASS K18 → K31 via d29, energy 1→0, died |
| Sham | `+32` · bit 1 · EAT at K18, ration consumed, energy 1→4 | `-32` · bit 0 · PASS K18 → K31 via d29, energy 1→0, died |
| Other version’s word | `-32` · bit 0 · PASS K18 → K31 via d29, energy 1→0, died | `+32` · bit 1 · EAT denied at K18, stock retained, energy 1→0, died |
| Neutral erase | `+0` · bit 1 · EAT at K18, ration consumed, energy 1→4 | `+0` · bit 1 · EAT denied at K18, stock retained, energy 1→0, died |
| Restored word | `+32` · bit 1 · EAT at K18, ration consumed, energy 1→4 | `-32` · bit 0 · PASS K18 → K31 via d29, energy 1→0, died |
| Count-trained word | `+0` · bit 1 · EAT at K18, ration consumed, energy 1→4 | `+0` · bit 1 · EAT denied at K18, stock retained, energy 1→0, died |
| Re-paired-credit word | `+0` · bit 1 · EAT at K18, ration consumed, energy 1→4 | `+0` · bit 1 · EAT denied at K18, stock retained, energy 1→0, died |

**Mirrored code**

Turn 6 is at stocked K18. Both readers see the feeder on, energy 1, previous move and anonymous ports 0, 1, 2. The preceding real movement wrote clue B into route word `001`. First receipt `110` and prepared action `100` are fixed. The spectator’s opening is A in version 0 and B in version 1.

| Prepared arm | Version 0 learned score, bit and game result | Version 1 learned score, bit and game result |
|---|---|---|
| Resident word | `+32` · bit 0 · PASS K18 → K31 via d29, energy 1→0, died | `-32` · bit 1 · EAT at K18, ration consumed, energy 1→4 |
| Sham | `+32` · bit 0 · PASS K18 → K31 via d29, energy 1→0, died | `-32` · bit 1 · EAT at K18, ration consumed, energy 1→4 |
| Other version’s word | `-32` · bit 1 · EAT denied at K18, stock retained, energy 1→0, died | `+32` · bit 0 · PASS K18 → K31 via d29, energy 1→0, died |
| Neutral erase | `+0` · bit 1 · EAT denied at K18, stock retained, energy 1→0, died | `+0` · bit 1 · EAT at K18, ration consumed, energy 1→4 |
| Restored word | `+32` · bit 0 · PASS K18 → K31 via d29, energy 1→0, died | `-32` · bit 1 · EAT at K18, ration consumed, energy 1→4 |
| Count-trained word | `+0` · bit 1 · EAT denied at K18, stock retained, energy 1→0, died | `+0` · bit 1 · EAT at K18, ration consumed, energy 1→4 |
| Re-paired-credit word | `+0` · bit 1 · EAT denied at K18, stock retained, energy 1→0, died | `+0` · bit 1 · EAT at K18, ration consumed, energy 1→4 |

Founder seed `5152685336963129192`, replicate 2, decision turn 6.

Parity and not-all-equal were replayed separately and give this same displayed trace.

### Ordinary cue B on tape 9701403267683456919

Both versions follow these physical passes. The mirrored code retains every move and exchanges the paired public slot names.

| Turn | Growth | Charged pass | Ordinary slot | Mirrored slot | Arrival clue in the ordinary code |
|---:|---|---|---:|---:|---|
| 1 | Formation 1 adds K7–K18 | PASS K3 → K1 via d62, energy 6→5 | 2 | 2 | — |
| 2 | — | PASS K1 → K13 via d58, energy 5→4 | 1 | 0 | B |
| 3 | — | PASS K13 → K1 via d58, energy 4→3 | 0 | 1 | A |
| 4 | — | PASS K1 → K12 via d56, energy 3→2 | 5 | 4 | B |
| 5 | Formation 2 adds K19–K31 | PASS K12 → K20 via d5, energy 2→1 | 1 | 0 | B |

**Ordinary code**

Turn 6 is at stocked K20. Both readers see the feeder on, energy 1, previous move and anonymous ports 0, 1, 2. The preceding real movement wrote clue B into route word `001`. First receipt `110` and prepared action `100` are fixed. The spectator’s opening is A in version 0 and B in version 1.

| Prepared arm | Version 0 learned score, bit and game result | Version 1 learned score, bit and game result |
|---|---|---|
| Resident word | `+32` · bit 0 · PASS K20 → K9 via d10, energy 1→0, died | `-32` · bit 1 · EAT at K20, ration consumed, energy 1→4 |
| Sham | `+32` · bit 0 · PASS K20 → K9 via d10, energy 1→0, died | `-32` · bit 1 · EAT at K20, ration consumed, energy 1→4 |
| Other version’s word | `-32` · bit 1 · EAT denied at K20, stock retained, energy 1→0, died | `+32` · bit 0 · PASS K20 → K9 via d10, energy 1→0, died |
| Neutral erase | `+0` · bit 1 · EAT denied at K20, stock retained, energy 1→0, died | `+0` · bit 1 · EAT at K20, ration consumed, energy 1→4 |
| Restored word | `+32` · bit 0 · PASS K20 → K9 via d10, energy 1→0, died | `-32` · bit 1 · EAT at K20, ration consumed, energy 1→4 |
| Count-trained word | `+0` · bit 1 · EAT denied at K20, stock retained, energy 1→0, died | `+0` · bit 1 · EAT at K20, ration consumed, energy 1→4 |
| Re-paired-credit word | `+0` · bit 1 · EAT denied at K20, stock retained, energy 1→0, died | `+0` · bit 1 · EAT at K20, ration consumed, energy 1→4 |

**Mirrored code**

Turn 6 is at stocked K20. Both readers see the feeder on, energy 1, previous move and anonymous ports 0, 1, 2. The preceding real movement wrote clue A into route word `010`. First receipt `110` and prepared action `100` are fixed. The spectator’s opening is A in version 0 and B in version 1.

| Prepared arm | Version 0 learned score, bit and game result | Version 1 learned score, bit and game result |
|---|---|---|
| Resident word | `+32` · bit 1 · EAT at K20, ration consumed, energy 1→4 | `-32` · bit 0 · PASS K20 → K9 via d10, energy 1→0, died |
| Sham | `+32` · bit 1 · EAT at K20, ration consumed, energy 1→4 | `-32` · bit 0 · PASS K20 → K9 via d10, energy 1→0, died |
| Other version’s word | `-32` · bit 0 · PASS K20 → K9 via d10, energy 1→0, died | `+32` · bit 1 · EAT denied at K20, stock retained, energy 1→0, died |
| Neutral erase | `+0` · bit 1 · EAT at K20, ration consumed, energy 1→4 | `+0` · bit 1 · EAT denied at K20, stock retained, energy 1→0, died |
| Restored word | `+32` · bit 1 · EAT at K20, ration consumed, energy 1→4 | `-32` · bit 0 · PASS K20 → K9 via d10, energy 1→0, died |
| Count-trained word | `+0` · bit 1 · EAT at K20, ration consumed, energy 1→4 | `+0` · bit 1 · EAT denied at K20, stock retained, energy 1→0, died |
| Re-paired-credit word | `+0` · bit 1 · EAT at K20, ration consumed, energy 1→4 | `+0` · bit 1 · EAT denied at K20, stock retained, energy 1→0, died |
