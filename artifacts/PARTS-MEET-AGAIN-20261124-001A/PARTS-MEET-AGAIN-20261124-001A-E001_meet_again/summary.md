# PARTS-MEET-AGAIN-20261124-001A-E001: summary

Engine written from the frozen texts by a helper that did not see the drafter's prototype. Every reading taken is an item of `deviations.md` (experiment folder). Files named below are in this artifact folder.

## Predictions

| # | Verdict | The numbers |
| --- | --- | --- |
| P0 | holds | ring engine: 728 registered + 112 extra runs of G, 6720 rounds compared, 0 mismatches; IMPLIED = LITERAL on 420 parity runs (0 differ); rule R / rule Q engines: 3256 runs, 16149 rounds compared, 0 mismatches; brute force: 600 structures, 5344 knot verdicts (1953 failing), ranks/kernel/NAE mismatches 0/0/0; birth method: 600 grown structures, 4862 knots (609 failing), against direct 0 and brute 0 mismatches; birth vs direct on run G: 135314 knots compared, 0 disagree |
| P1 | holds | 504 runs (run 1 arm A, CARRY both readings): no wholly-apart pair one part again, no joint birth, every pair checked; run 2: 285 enumerations, 1939866 histories, no violation |
| P2 | holds | arm A pairs at s >= 1: 1396 under not-all-equal, none differs; 1168 under parity, 0 differ (none by another way). The two-knot start's own pair at s = 0 (an addition, not wholly apart) differs under Q by a group or owing / fresh: outside argument 4 |
| P3 | holds | ring returns under arm A from round 1: 0 (control without a taking rule: RING-LAW returns at rounds 2, 4, 6, 8 on all three ring starts); two-knot parts after round 1 besides the exception: 0; exception N(1) = 2 on the two-knot start under SHORT-TAKES (every COPY-LAW, both knot laws) |
| P4 | holds | three-knot start, COPY-LAW(t), both knot laws: Q(OLDEST/NEWEST) round 2 has the group {3, 4, 5} and one part at every round; SHORT-TAKES: knot 3 short in round 2, its second join takes a shared distinction, one part through round 8 (24 of 24 runs) |
| P5 | holds | late Q(NEWEST): 387 pairs that came apart, 0 one part again; late Q(OLDEST): 355 pairs that came apart, 0 one part again; late SHORT-TAKES(NEWEST): 438 pairs that came apart, 0 one part again; late SHORT-TAKES(OLDEST): 438 pairs that came apart, 0 one part again |
| P6 | holds | RECORD-2: 270 pairs that came apart, 0 one part again; RECORD-3: 174, 0; ALL-JOINABLE, CARRY (both readings): at most one class at every round |
| P7 | holds | round 1: [[3, 'join', [1, 2], [4, 6]], [4, 'offshoot', [1], [5, 2]], [5, 'offshoot', [2], [7, 0]]]; round 2 under RETIRE: groups [[3, 4], [3, 5], [4, 5]], retired [3, 4, 5], 6 knots at the end; under WAIT jammed in round 2: True |
| P8 | holds | one part again 3 (through start knot 0, no recorded ancestor of both); course differs 4 in B(i), 4 in B(ii); demand line 3; way a group or owing; through a meeting; joint birth None; verdict through a start knot; 12-15 take {'12': [0], '13': [0], '14': [2], '15': [2]}; 20 knots after round 5; knot failures through round 8: 0 (not-all-equal), 0 (parity) |
| P9 | holds | BY-COUNT: vanishes; CAP-3: vanishes; HOLD: stands; NEWEST: vanishes; UP-TO-2: vanishes; demand before the takes: stands; fresh by parents: stands; names reversed: stands; order reversed: stands; parity: stands; names reversed through ['through a knot the growth made'] |
| P10 | holds | one part again 3 through {'3': 'a knot made by the growth that is no ancestor of both'}; course differs 4; verdict through a knot the growth made; BY-COUNT: vanishes; CAP-3: vanishes; HOLD: stands ['through a knot the growth made']; NEWEST: vanishes; UP-TO-2: vanishes; demand before the takes: stands ['through a knot the growth made']; fresh by parents: stands ['through a knot the growth made']; names reversed: stands ['through a start knot']; order reversed: vanishes; parity: stands ['through a knot the growth made'] |
| P11 | holds under the three-component reading per ration group; fails under the four-component reading | pairs that came apart, minimal (three components): base laws ['STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)'], CAP-3 swap ['MET(BY-COUNT)', 'MET(NEWEST)']; four components: base ['STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)', 'STEPS-2(BY-COUNT)', 'UP-TO-2(BY-COUNT)'], CAP-3 ['MET(BY-COUNT)', 'MET(NEWEST)', 'STEPS-2(IN-TURN)']. Halves (first time): base ['MET(BY-COUNT)'], CAP-3 ['MET(BY-COUNT)', 'MET(IN-TURN)', 'MET(NEWEST)', 'MET(OLDEST)']. No law of arm A, RECORD-k, ALL-JOINABLE or CARRY has the mark |
| P12 | holds | came apart: 33 cases; vanish under {'HOLD': 24, 'STEPS-k/UP-TO-k': 28, 'demand before the takes': 9, 'fresh by parents': 4, 'names reversed': 12, 'order reversed': 5, 'ration': 33}; survive the ration swap: 0; STEPS-2 surviving UP-TO-2: 0; vanish under the knot law: 0. Halves: 47 cases; vanish under {'STEPS-k/UP-TO-k': 10, 'demand before the takes': 10, 'fresh by parents': 1, 'names reversed': 39, 'ration': 21}; survive every swap: [['MET(BY-COUNT)', 'COPY-LAW(OFFSHOOT)', 'two-knot', ['through a start knot']]] |
| P13 | holds | smallest case, first copy only: {'BY-COUNT': None, 'BY-RECEIVED': None, 'IN-TURN': 4, 'NEWEST': None, 'OLDEST': 4}; Ring(5,3), X a given-off part, Y the ring part: [{"X": [15, 16], "by_choice": {"BY-COUNT": 4, "BY-RECEIVED": 4, "IN-TURN": null, "NEWEST": null, "OLDEST": null}, "s": 2}, {"X": [17, 18], "by_choice": {"BY-COUNT": null, "BY-RECEIVED": null, "IN-TURN": null, "NEWEST": null, "OLDEST": null}, "s": 2}, {"X": [19, 20], "by_choice": {"BY-COUNT": 4, "BY- ... |
| P14 | reported (open) | run 4: [["smallest case", "nae", "same", 6], ["smallest case", "parity", "same", 6], ["through the retired join", "nae", "same", 6], ["through the retired join", "parity", "same", 6]]; supplement: 54 three-knot pairs with a mark, 16 applicable (six laws: ['COPY-LAW(OFFSHOOT) / STEPS-2(IN-TURN)', 'COPY-LAW(OFFSHOOT) / STEPS-2(OLDEST)', 'COPY-LAW(RETIRE) / STEPS-2(IN-TURN)', 'COPY-LAW(RETIRE) / STEPS-2(OLDEST)', 'COPY-LAW(WAIT) / STEPS-2(IN-TURN)', 'COPY-LAW(WAIT) / STEPS-2(OLDEST)']), differing: none |
| P15 | fails | [["COPY-LAW(RETIRE)", "three-knot", "nae", "one part at s with the placed knot: True", "vs Y barred: None", "vs no placed knot: None"], ["COPY-LAW(RETIRE)", "three-knot", "parity", "one part at s with the placed knot: True", "vs Y barred: None", "vs no placed knot: None"], ["COPY-LAW(WAIT)", "three-knot", "nae", "one part at s with the placed knot: True", "vs Y barred: 5", "vs no placed knot: None"], ["COPY-LAW(WAIT)", "three-knot", "parity", "one part at s with the placed knot: True", "vs Y barred: 5", "vs no placed knot: None"], ["RING-LAW", "Ring(5,3)", "nae", "one part at s with the placed knot: True", "vs Y barred: None", "vs no placed knot: 3"], ["RING-LAW", "Ring(5,3)", "parity", "one ... |
| P16 | fails | COPY-LAW(WAIT)+HOLD: 26 pairs not wholly apart, 26 one part again, course differs: 0; Q with HOLD, runs with parts that come apart: [['COPY-LAW(OFFSHOOT)+HOLD', 'two-knot', 'Q(NEWEST)', 'nae', 1], ['COPY-LAW(OFFSHOOT)+HOLD', 'two-knot', 'Q(NEWEST)', 'parity', 1], ['COPY-LAW(OFFSHOOT)+HOLD', 'Ring(5,3)', 'Q(NEWEST)', 'nae', 4], ['COPY-LAW(OFFSHOOT)+HOLD', 'Ring(5,3)', 'Q(NEWEST)', 'parity', 4]] |
| P17 | reported (open) | {"run3 / came apart / FIRST(PARTS)(OLDEST) / RING-LAW": 2, "run3 / came apart / MET(NEWEST) / CAP-3(RETIRE)": 2, "run3 / came apart / STEPS-2(BY-COUNT) / RING-LAW": 4, "run3 / came apart / STEPS-2(IN-TURN) / RING-LAW": 12, "run3 / came apart / STEPS-2(NEWEST) / CAP-3(WAIT)": 4, "run3 / came apart / STEPS-2(NEWEST) / RING-LAW": 34, "run3 / came apart / STEPS-2(OLDEST) / RING-LAW": 10, "run3 / came apart / UP-TO-2(BY-COUNT) / COPY-LAW(OFFSHOOT)": 6, "run3 / first time / MET(BY-COUNT) / CAP-3(WAIT)": 2, "run3 / first time / MET(NEWEST) / CAP-3(WAIT)": 2, "run3 / first time / STEPS-1(IN-TURN) / CAP-3(OFFSHOOT)": 2, "run3 / first time / STEPS-1(IN-TURN) / CAP-3(RETIRE)": 2, "run3 / first time / STEPS-1(IN-TURN) / CAP-3(WAIT)": 2, "run3 / first time / STEPS-1(OLDEST) / CAP-3(OFFSHOOT)": 2, "run3 / first time / STEPS-1(OLDEST) / CAP-3(RETIRE)": 2, "run3 / first time / STEPS-1(OLDEST) / CAP-3(WA ... |
| P18 | holds | run A verdicts 517822, comparison-run verdicts 1842292, run 2 verdicts 231300591; method disagreements 0; untested 0; birth vs direct compared 259841. Not-all-equal failures outside CARRY: 0; parity failures not at a join of 3+ parents (FLOOR0/ONE-FEWER excepted): 0 |

## Differences from the numbers disclosed before the freeze

| What | Disclosed | Found here | Verdict | Listing |
| --- | --- | --- | --- | --- |
| Pairs tested in runs 1 and 3 (s >= 1) | 7,039 (5,703 that came apart, 1,336 for the first time) | see summary_core.json run1_pairs/run3_pairs | every disclosed per-law count of pairs that came apart is equal (Q 24/178/22/182, late start 355/387/438/438, RECORD 270/174, UP-TO-2(NEWEST) 244); so are the 302 and 116 marks, their ways, demand lines, reading (ii) and verdicts. The difference lies in laws whose pair counts were not disclosed. No verdict differs. | summary_core.json |
| CARRY, the round-2 join of ten parents on Ring(5,3) | 21 places (ten given, ten carried, one fresh), failing under both knot laws | 15 places under reading 10 (a parent whose oldest distinction the birth already takes adds nothing): fails under parity, passes under not-all-equal. Under the other reading (oldest not already taken) 21 places, failing under both: the disclosed knot | P18 holds under either reading (CARRY is the permitted place); P1 and P6 hold under either | replays.json (carry), carry-alt.jsonl.gz |
| Q with HOLD | nothing comes apart | under COPY-LAW(OFFSHOOT)+HOLD with Q(NEWEST): on the two-knot start the round-1 part {2, 3, 4, 5} comes apart at round 2; on Ring(5, 3) the round-0 and round-1 parts come apart at round 2 (every member is short in round 2, so HOLD keeps nothing and the round is the RELEASE round) | P16 fails on this clause | replays.json (hold_q_newest) |
| HOLD arm counts | COPY-LAW(WAIT)+HOLD: "6 of 20 and 6 of 6 pairs" not wholly apart one part again; STEPS-2 with HOLD: 3 pairs one part again | per knot law, two-knot start: 12 pairs, 4 not wholly apart, all 4 one part again; three-knot start: 6 of 6. STEPS-2(OLDEST)+HOLD: pairs not wholly apart one part again: 7 per knot law (and wholly-apart pairs with marks) | P16's first clause holds; counts differ; the cap of four pairs per round was kept (reading 20); without it the two-knot count is 12 of 34 | run7.jsonl.gz |
| STEPS-2 with HOLD (run 7) | "under STEPS-2 with HOLD, 3 pairs are one part again, no course differs" | STEPS-2(OLDEST) with HOLD: 14 "course differs" marks per knot law at s >= 1 (COPY-LAW(OFFSHOOT): three-knot 5, one of them on a pair not wholly apart, two-knot 3; COPY-LAW(RETIRE): three-knot 2, the smallest case under HOLD as P9 says, two-knot 2; RING-LAW: two-knot 2); none under COPY-LAW(WAIT) | P16 judges no course under COPY-LAW(WAIT) only, and that holds; P9 (the smallest case stands under HOLD) holds | run7.jsonl.gz |
| A225 control under COPY-LAW(WAIT) | the first copy's course differs at round 3 | with X, Y the two copies {6, 7}, {8, 9}: round 5 (way: a group or owing; the placed knot is short only while the second copy is there, so the first copy's join 11 makes an offshoot instead of a join with it). Round 3 is what X = the waiting join {3}, Y = {6, 7} gives (my first run 6, reading 38) | P15 fails on this clause (round 5, not 3) | replays.json (a225_wait), run6.jsonl |
| Swap battery, HOLD | HOLD removes 27 of 33 cases that came apart | 24; two cases survive only through a pair not wholly apart, one only through marks confirmed by the mask that are never one part again (verdict unconfirmed); counting only wholly-apart pairs with a made or start-knot verdict gives 27 | P12 does not judge HOLD; no verdict differs | run5.jsonl |
| The smallest case under HOLD | three pairs show it | two confirmed pairs (any pair, wholly apart or not) | P9 holds (it stands) | run4.jsonl |
| Q runs with pairs that came apart | 8, 14, 2 and 14 of the 42 runs | equal when counting runs in which a part comes apart (every part); 2, 14, 2, 14 runs with a sampled pair that came apart | none | summary_core.json |

## The cost of the laws (definitions 3.3)

| Law | Holder steps | Record steps | Whole roster | Choice supplied by |
| --- | --- | --- | --- | --- |
| ALL-JOINABLE | 0 | 0 | yes | none |
| CARRY | 1 | 1 | no | names |
| FIRST(PARTS)(OLDEST) | any | any | yes | names |
| MET(BY-COUNT) | 2 | 0 | no | structure |
| MET(IN-TURN) | 2 | 0 | no | order of births |
| MET(NEWEST) | 2 | 0 | no | names |
| MET(OLDEST) | 2 | 0 | no | names |
| Q(BY-COUNT) | 1 | 0 | no | structure |
| Q(IN-TURN) | 1 | 0 | no | order of births |
| Q(NEWEST) | 1 | 0 | no | names |
| Q(OLDEST) | 1 | 0 | no | names |
| RECORD-2 | 0 | 2 | no | none |
| RECORD-3 | 0 | 3 | no | none |
| SHORT-TAKES(NEWEST) | 1 | 0 | no | names |
| SHORT-TAKES(OLDEST) | 1 | 0 | no | names |
| STEPS-1(BY-COUNT) | 2 | 1 | no | structure |
| STEPS-1(IN-TURN) | 2 | 1 | no | order of births |
| STEPS-1(NEWEST) | 2 | 1 | no | names |
| STEPS-1(OLDEST) | 2 | 1 | no | names |
| STEPS-2(BY-COUNT) | 3 | 2 | no | structure |
| STEPS-2(IN-TURN) | 3 | 2 | no | order of births |
| STEPS-2(NEWEST) | 3 | 2 | no | names |
| STEPS-2(OLDEST) | 3 | 2 | no | names |
| UP-TO-2(BY-COUNT) | 3 | 2 | no | structure |
| UP-TO-2(IN-TURN) | 3 | 2 | no | order of births |
| UP-TO-2(NEWEST) | 3 | 2 | no | names |
| UP-TO-2(OLDEST) | 3 | 2 | no | names |
| late Q(NEWEST) | 1 | 0 | no | names |
| late Q(OLDEST) | 1 | 0 | no | names |
| late SHORT-TAKES(NEWEST) | 1 | 0 | no | names |
| late SHORT-TAKES(OLDEST) | 1 | 0 | no | names |
| none | 0 | 0 | no | none |

## Minimal laws with a confirmed "course differs" mark

- pairs that came apart, CAP-3 swap: laws with the mark ['MET(BY-COUNT)', 'MET(NEWEST)', 'STEPS-2(BY-COUNT)', 'STEPS-2(IN-TURN)', 'STEPS-2(NEWEST)', 'STEPS-2(OLDEST)']; minimal (three components) ['MET(BY-COUNT)', 'MET(NEWEST)']; minimal (four components, the choice compared by equality) ['MET(BY-COUNT)', 'MET(NEWEST)', 'STEPS-2(IN-TURN)']
- pairs that came apart, base laws: laws with the mark ['FIRST(PARTS)(OLDEST)', 'STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)', 'STEPS-2(BY-COUNT)', 'STEPS-2(IN-TURN)', 'STEPS-2(NEWEST)', 'STEPS-2(OLDEST)', 'UP-TO-2(BY-COUNT)']; minimal (three components) ['STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)']; minimal (four components, the choice compared by equality) ['STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)', 'STEPS-2(BY-COUNT)', 'UP-TO-2(BY-COUNT)']
- pairs that came apart, pooled: laws with the mark ['FIRST(PARTS)(OLDEST)', 'MET(BY-COUNT)', 'MET(NEWEST)', 'STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)', 'STEPS-2(BY-COUNT)', 'STEPS-2(IN-TURN)', 'STEPS-2(NEWEST)', 'STEPS-2(OLDEST)', 'UP-TO-2(BY-COUNT)']; minimal (three components) ['MET(BY-COUNT)', 'MET(NEWEST)']; minimal (four components, the choice compared by equality) ['MET(BY-COUNT)', 'MET(NEWEST)', 'STEPS-1(IN-TURN)']
- the two-knot start's halves, CAP-3 swap: laws with the mark ['MET(BY-COUNT)', 'MET(IN-TURN)', 'MET(NEWEST)', 'MET(OLDEST)', 'STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)', 'STEPS-2(BY-COUNT)', 'STEPS-2(IN-TURN)', 'STEPS-2(OLDEST)', 'UP-TO-2(IN-TURN)', 'UP-TO-2(OLDEST)']; minimal (three components) ['MET(BY-COUNT)', 'MET(IN-TURN)', 'MET(NEWEST)', 'MET(OLDEST)']; minimal (four components, the choice compared by equality) ['MET(BY-COUNT)', 'MET(IN-TURN)', 'MET(NEWEST)', 'MET(OLDEST)']
- the two-knot start's halves, base laws: laws with the mark ['MET(BY-COUNT)', 'STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)', 'UP-TO-2(BY-COUNT)', 'UP-TO-2(IN-TURN)', 'UP-TO-2(OLDEST)']; minimal (three components) ['MET(BY-COUNT)']; minimal (four components, the choice compared by equality) ['MET(BY-COUNT)', 'STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)']
- the two-knot start's halves, pooled: laws with the mark ['MET(BY-COUNT)', 'MET(IN-TURN)', 'MET(NEWEST)', 'MET(OLDEST)', 'STEPS-1(IN-TURN)', 'STEPS-1(OLDEST)', 'STEPS-2(BY-COUNT)', 'STEPS-2(IN-TURN)', 'STEPS-2(OLDEST)', 'UP-TO-2(BY-COUNT)', 'UP-TO-2(IN-TURN)', 'UP-TO-2(OLDEST)']; minimal (three components) ['MET(BY-COUNT)', 'MET(IN-TURN)', 'MET(NEWEST)', 'MET(OLDEST)']; minimal (four components, the choice compared by equality) ['MET(BY-COUNT)', 'MET(IN-TURN)', 'MET(NEWEST)', 'MET(OLDEST)']

## The swap battery (run 5): which swaps each case survives

| Case (law, base law, start, kind) | names rev. | order rev. | demand first | fresh by parents | HOLD | ration | STEPS/UP-TO | knot law |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MET(BY-COUNT), CAP-3(OFFSHOOT), Ring(5,3), came apart | vanishes | vanishes | vanishes | survives | vanishes | vanishes | n/a | survives |
| MET(BY-COUNT), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| MET(IN-TURN), CAP-3(OFFSHOOT), two-knot, first time | survives | survives | vanishes | survives | survives | vanishes | n/a | survives |
| MET(NEWEST), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | vanishes | survives | survives | vanishes | n/a | survives |
| MET(OLDEST), CAP-3(OFFSHOOT), two-knot, first time | survives | survives | vanishes | survives | survives | vanishes | n/a | survives |
| STEPS-1(IN-TURN), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-1(OLDEST), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-2(BY-COUNT), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | vanishes | vanishes | survives |
| STEPS-2(IN-TURN), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | vanishes | survives | survives |
| STEPS-2(OLDEST), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | vanishes | survives | survives |
| UP-TO-2(IN-TURN), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | survives | survives |
| UP-TO-2(OLDEST), CAP-3(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | survives | survives |
| MET(NEWEST), CAP-3(RETIRE), Ring(5,3), came apart | vanishes | vanishes | vanishes | survives | vanishes | vanishes | n/a | survives |
| STEPS-2(IN-TURN), CAP-3(RETIRE), Ring(5,3), came apart | survives | survives | vanishes | survives | survives | vanishes | vanishes | survives |
| STEPS-2(OLDEST), CAP-3(RETIRE), Ring(5,3), came apart | survives | survives | vanishes | survives | survives | vanishes | vanishes | survives |
| MET(BY-COUNT), CAP-3(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | vanishes | n/a | survives |
| MET(IN-TURN), CAP-3(RETIRE), two-knot, first time | survives | survives | survives | survives | survives | vanishes | n/a | survives |
| MET(NEWEST), CAP-3(RETIRE), two-knot, first time | vanishes | survives | vanishes | survives | survives | vanishes | n/a | survives |
| MET(OLDEST), CAP-3(RETIRE), two-knot, first time | survives | survives | survives | survives | survives | vanishes | n/a | survives |
| STEPS-1(IN-TURN), CAP-3(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-1(OLDEST), CAP-3(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-2(BY-COUNT), CAP-3(RETIRE), two-knot, first time | vanishes | survives | vanishes | survives | survives | vanishes | vanishes | survives |
| STEPS-2(IN-TURN), CAP-3(RETIRE), two-knot, first time | vanishes | survives | vanishes | survives | survives | vanishes | survives | survives |
| STEPS-2(OLDEST), CAP-3(RETIRE), two-knot, first time | vanishes | survives | vanishes | survives | survives | vanishes | survives | survives |
| UP-TO-2(IN-TURN), CAP-3(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | survives | survives | survives |
| UP-TO-2(OLDEST), CAP-3(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | survives | survives | survives |
| STEPS-2(BY-COUNT), CAP-3(WAIT), Ring(5,3), came apart | vanishes | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(IN-TURN), CAP-3(WAIT), Ring(5,3), came apart | survives | survives | vanishes | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(NEWEST), CAP-3(WAIT), Ring(5,3), came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| MET(BY-COUNT), CAP-3(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | vanishes | n/a | survives |
| MET(IN-TURN), CAP-3(WAIT), two-knot, first time | survives | survives | survives | survives | survives | vanishes | n/a | survives |
| MET(NEWEST), CAP-3(WAIT), two-knot, first time | vanishes | survives | vanishes | survives | survives | vanishes | n/a | survives |
| MET(OLDEST), CAP-3(WAIT), two-knot, first time | survives | survives | survives | survives | survives | vanishes | n/a | survives |
| STEPS-1(IN-TURN), CAP-3(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-1(OLDEST), CAP-3(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-2(BY-COUNT), CAP-3(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | vanishes | vanishes | survives |
| STEPS-2(IN-TURN), CAP-3(WAIT), two-knot, first time | vanishes | survives | vanishes | survives | survives | vanishes | survives | survives |
| STEPS-2(OLDEST), CAP-3(WAIT), two-knot, first time | vanishes | survives | vanishes | survives | survives | vanishes | survives | survives |
| UP-TO-2(IN-TURN), CAP-3(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | survives | survives |
| UP-TO-2(OLDEST), CAP-3(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | survives | survives |
| STEPS-2(BY-COUNT), COPY-LAW(OFFSHOOT), three-knot, came apart | survives | survives | survives | survives | survives | vanishes | vanishes | survives |
| STEPS-2(IN-TURN), COPY-LAW(OFFSHOOT), three-knot, came apart | survives | survives | survives | vanishes | survives | vanishes | vanishes | survives |
| STEPS-2(NEWEST), COPY-LAW(OFFSHOOT), three-knot, came apart | vanishes | vanishes | survives | survives | survives | vanishes | vanishes | survives |
| STEPS-2(OLDEST), COPY-LAW(OFFSHOOT), three-knot, came apart | survives | survives | survives | vanishes | survives | vanishes | vanishes | survives |
| MET(BY-COUNT), COPY-LAW(OFFSHOOT), two-knot, first time | survives | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-1(IN-TURN), COPY-LAW(OFFSHOOT), two-knot, came apart | vanishes | survives | survives | vanishes | vanishes | vanishes | n/a | survives |
| STEPS-1(IN-TURN), COPY-LAW(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-1(OLDEST), COPY-LAW(OFFSHOOT), two-knot, came apart | vanishes | survives | survives | survives | vanishes | vanishes | n/a | survives |
| STEPS-1(OLDEST), COPY-LAW(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| UP-TO-2(BY-COUNT), COPY-LAW(OFFSHOOT), two-knot, came apart | survives | survives | survives | vanishes | survives | vanishes | vanishes | survives |
| UP-TO-2(BY-COUNT), COPY-LAW(OFFSHOOT), two-knot, first time | survives | survives | survives | vanishes | survives | vanishes | vanishes | survives |
| UP-TO-2(IN-TURN), COPY-LAW(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | vanishes | survives |
| UP-TO-2(OLDEST), COPY-LAW(OFFSHOOT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | vanishes | survives |
| STEPS-2(IN-TURN), COPY-LAW(RETIRE), three-knot, came apart | survives | survives | survives | survives | survives | vanishes | vanishes | survives |
| STEPS-2(OLDEST), COPY-LAW(RETIRE), three-knot, came apart | survives | survives | survives | survives | survives | vanishes | vanishes | survives |
| STEPS-1(IN-TURN), COPY-LAW(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-1(OLDEST), COPY-LAW(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| UP-TO-2(IN-TURN), COPY-LAW(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | survives | vanishes | survives |
| UP-TO-2(OLDEST), COPY-LAW(RETIRE), two-knot, first time | vanishes | survives | survives | survives | survives | survives | vanishes | survives |
| STEPS-2(IN-TURN), COPY-LAW(WAIT), three-knot, came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(NEWEST), COPY-LAW(WAIT), three-knot, came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(OLDEST), COPY-LAW(WAIT), three-knot, came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-1(IN-TURN), COPY-LAW(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-1(OLDEST), COPY-LAW(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | n/a | survives |
| STEPS-2(BY-COUNT), COPY-LAW(WAIT), two-knot, came apart | vanishes | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(OLDEST), COPY-LAW(WAIT), two-knot, came apart | vanishes | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| UP-TO-2(IN-TURN), COPY-LAW(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | vanishes | survives |
| UP-TO-2(OLDEST), COPY-LAW(WAIT), two-knot, first time | vanishes | survives | survives | survives | survives | survives | vanishes | survives |
| FIRST(PARTS)(OLDEST), RING-LAW, D2(5,3), came apart | vanishes | survives | vanishes | survives | vanishes | vanishes | n/a | survives |
| STEPS-2(BY-COUNT), RING-LAW, D2(5,3), came apart | vanishes | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(IN-TURN), RING-LAW, D2(5,3), came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(NEWEST), RING-LAW, D2(5,3), came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(OLDEST), RING-LAW, D2(5,3), came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(BY-COUNT), RING-LAW, Ring(5,3), came apart | vanishes | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(IN-TURN), RING-LAW, Ring(5,3), came apart | survives | survives | vanishes | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(NEWEST), RING-LAW, Ring(5,3), came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(BY-COUNT), RING-LAW, Ring(7,3), came apart | survives | survives | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(IN-TURN), RING-LAW, Ring(7,3), came apart | survives | survives | vanishes | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(NEWEST), RING-LAW, Ring(7,3), came apart | survives | vanishes | survives | survives | vanishes | vanishes | vanishes | survives |
| STEPS-2(OLDEST), RING-LAW, Ring(7,3), came apart | vanishes | vanishes | vanishes | survives | vanishes | vanishes | vanishes | survives |

## Knot tests

- Numbers: {"birth vs direct compared": 259841, "comparison-run verdicts": 1842292, "disagreements": 0, "run 2 verdicts": 231300591, "untested": 0, "verdicts": 517822}
- Failing knots of the registered runs (distinct rows: run, knot law, law, base, start, kind, parents, places, round made; run-2 rows give the enumeration): [["run2", "parity", "COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|ONE-FEWER|parity", "", "", "see examples", null, null, null], ["run2", "parity", "COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|ONE-FEWER|parity", "", "", "see examples", null, null, null], ["run2", "parity", "COPY-LAW(OFFSHOOT)|three-knot|Q|r1|FLOOR0|parity", "", "", "see examples", null, null, null], ["run2", "parity", "COPY-LAW(OFFSHOOT)|three-knot|Q|r1|ONE-FEWER|parity", "", "", "see examples", null, null, null], ["run2", "parity", "COPY-LAW(RETIRE)|three-knot|Q|r1|FLOOR0|parity", "", "", "see examples", null, null, null], ["run2", "parity", "COPY-LAW(RETIRE)|three-knot|Q|r1|ONE-FEWER|parity", "", "", "see examples", null, null, null], ["run2", "parity", "COPY-LAW(WAIT)|three-knot|Q|r1|FLOOR0|parity", "", "", "see examples", null, null, null], ["run2", "parity", "COPY-LAW(WAIT)|three-knot|Q|r1|ONE-FEWER|parity", "", "", "see examples", null, null, null], ["run3 kt_B1 s=0", "parity", "MET(BY-COUNT)", "COPY-LAW(OFFSHOOT)", "two-knot", "join", 3, 4, 4], ["run3 kt_B1 s=6", "parity", "MET(NEWEST)", "CAP-3(WAIT)", "two-knot", "join", 12, 14, 5], ["run3 kt_B2 s=1", "parity", "MET(BY-COUNT)", "COPY-LAW(OFFSHOOT)", "two-knot", "join", 3, 4, 4], ["run3", "parity", "CARRY", "CAP-3(OFFSHOOT)", "Ring(5,3)", "join", 10, 15, 2], ["run3", "parity", "CARRY", "CAP-3(RETIRE)", "Ring(5,3)", "join", 10, 15, 2], ["run3", "parity", "CARRY", "CAP-3(WAIT)", "Ring(5,3)", "join", 10, 15, 2], ["run3", "parity", "CARRY", "COPY-LAW(OFFSHOOT)", "Ring(5,3)", "join", 10, 15, 2], ["run3", "parity", "CARRY", "COPY-LAW(RETIRE)", "Ring(5,3)", "join", 10, 15, 2], ["run3", "parity", "CARRY", "COPY-LAW(WAIT)", "Ring(5,3)", "join", 10, 15, 2], ["run3", "parity", "CARRY", "RING-LAW", "Ring(5,3)", "join", 10, 15, 2], ["run3", "parity", "MET(NEWEST)", "CAP-3(WAIT)", "two-knot", "join", 12, 14, 5]]
- Run 2 failure examples: [{"examples": [{"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}], "id": "COPY-LAW(RETIRE)|three-knot|Q|r1|FLOOR0|parity"}, {"examples": [{"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}], "id": "COPY-LAW(RETIRE)|three-knot|Q|r1|ONE-FEWER|parity"}, {"examples": [{"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}], "id": "COPY-LAW(OFFSHOOT)|three-knot|Q|r1|FLOOR0|parity"}, {"examples": [{"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fail", "knots": [0], "round": 4}, {"kind": "parity fail", "knots": [0], "round": 2}, {"kind": "parity fail", "knots": [0], "round": 3}, {"kind": "parity fai ...
- Supplementary CARRY run (other reading, not registered): [["carry-alt (supplementary) kt_B1 s=0", "nae", "CARRY(oldest not taken)", "CAP-3(OFFSHOOT)", "two-knot", "join", 2, 5, 2], ["carry-alt (supplementary) kt_B1 s=0", "nae", "CARRY(oldest not taken)", "CAP-3(RETIRE)", "two-knot", "join", 2, 5, 2], ["carry-alt (supplementary) kt_B1 s=0", "nae", "CARRY(oldest not taken)", "CAP-3(WAIT)", "two-knot", "join", 2, 5, 2], ["carry-alt (supplementary) kt_B1 s=0", "nae", "CARRY(oldest not taken)", "COPY-LAW(OFFSHOOT)", "two-knot", "join", 2, 5, 2], ["carry-alt (supplementary) kt_B1 s=0", "nae", "CARRY(oldest not taken)", "COPY-LAW(RETIRE)", "two-knot", "joi ...

## The most-held distinction within the run, per law

{"ALL-JOINABLE": 2, "CARRY": 246, "CARRY(oldest not taken)": 246, "FIRST(PARTS)(OLDEST)": 48, "MET(BY-COUNT)": 56, "MET(IN-TURN)": 68, "MET(NEWEST)": 161, "MET(OLDEST)": 182, "Q(BY-COUNT)": 8, "Q(IN-TURN)": 34, "Q(NEWEST)": 6, "Q(OLDEST)": 128, "RECORD-2": 2, "RECORD-3": 2, "SHORT-TAKES(NEWEST)": 3, "SHORT-TAKES(OLDEST)": 9, "STEPS-1(BY-COUNT)": 14, "STEPS-1(IN-TURN)": 26, "STEPS-1(NEWEST)": 8, "STEPS-1(OLDEST)": 162, "STEPS-2(BY-COUNT)": 60, "STEPS-2(IN-TURN)": 42, "STEPS-2(NEWEST)": 19, "STEPS-2(OLDEST)": 114, "UP-TO-2(BY-COUNT)": 29, "UP-TO-2(IN-TURN)": 36, "UP-TO-2(NEWEST)": 8, "UP-TO-2(OLDEST)": 162, "late Q(NEWEST)": 5, "late Q(OLDEST)": 12, "late SHORT-TAKES(NEWEST)": 4, "late SHORT-TAKES(OLDEST)": 7, "none": 2}

## Run 2 (every choice)

- COPY-LAW(RETIRE)|two-knot|Q|r1|base|parity: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|r1|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|r1|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|r1|base|nae: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 6, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|r1|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|r1|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|r1|fresh by parents|parity: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|r1|fresh by parents|nae: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 6, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|late|base|nae: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 32, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|late|base|parity: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|late|fresh by parents|nae: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 32, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|Q|late|fresh by parents|parity: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|r1|FLOOR0|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|r1|ONE-FEWER|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|r1|base|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|late|base|nae: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 32, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|late|base|parity: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|r1|base|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 684, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|late|fresh by parents|nae: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 32, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|late|fresh by parents|parity: every choice, 1 histories, pairs wholly apart 8 (came apart 2), one part again 0, joint births 0, knot verdicts 72, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|r1|FLOOR0|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|r1|ONE-FEWER|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|r1|FLOOR0|parity: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 12
- COPY-LAW(RETIRE)|three-knot|Q|r1|FLOOR0|nae: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|r1|fresh by parents|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|r1|ONE-FEWER|parity: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 12
- COPY-LAW(RETIRE)|three-knot|Q|r1|ONE-FEWER|nae: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|r1|base|nae: every choice, 24 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 55, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|r1|base|parity: every choice, 24 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 367, failures 0
- COPY-LAW(RETIRE)|two-knot|SHORT-TAKES|r1|fresh by parents|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 684, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|late|base|parity: every choice, 1 histories, pairs wholly apart 2 (came apart 2), one part again 0, joint births 0, knot verdicts 53, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|late|base|nae: every choice, 1 histories, pairs wholly apart 2 (came apart 2), one part again 0, joint births 0, knot verdicts 18, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 2 (came apart 2), one part again 0, joint births 0, knot verdicts 53, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 2 (came apart 2), one part again 0, joint births 0, knot verdicts 53, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 2 (came apart 2), one part again 0, joint births 0, knot verdicts 53, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 2 (came apart 2), one part again 0, joint births 0, knot verdicts 53, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|late|fresh by parents|nae: every choice, 16 histories, pairs wholly apart 32 (came apart 32), one part again 0, joint births 0, knot verdicts 112, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|late|fresh by parents|parity: every choice, 16 histories, pairs wholly apart 32 (came apart 32), one part again 0, joint births 0, knot verdicts 387, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|r1|base|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 382, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|r1|base|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|r1|FLOOR0|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|r1|FLOOR0|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|r1|ONE-FEWER|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|late|base|nae: every choice, 4 histories, pairs wholly apart 8 (came apart 8), one part again 0, joint births 0, knot verdicts 48, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|late|base|parity: every choice, 4 histories, pairs wholly apart 8 (came apart 8), one part again 0, joint births 0, knot verdicts 131, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|late|FLOOR0|nae: every choice, 4 histories, pairs wholly apart 8 (came apart 8), one part again 0, joint births 0, knot verdicts 131, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|r1|fresh by parents|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 382, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|late|FLOOR0|parity: every choice, 4 histories, pairs wholly apart 8 (came apart 8), one part again 0, joint births 0, knot verdicts 131, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 4 histories, pairs wholly apart 8 (came apart 8), one part again 0, joint births 0, knot verdicts 131, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 4 histories, pairs wholly apart 8 (came apart 8), one part again 0, joint births 0, knot verdicts 131, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|late|fresh by parents|nae: every choice, 4 histories, pairs wholly apart 8 (came apart 8), one part again 0, joint births 0, knot verdicts 48, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|late|fresh by parents|parity: every choice, 4 histories, pairs wholly apart 8 (came apart 8), one part again 0, joint births 0, knot verdicts 131, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|r1|ONE-FEWER|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(RETIRE)|three-knot|SHORT-TAKES|r1|fresh by parents|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|r1|base|nae: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 325, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|r1|base|parity: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|r1|FLOOR0|parity: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|r1|ONE-FEWER|parity: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|r1|ONE-FEWER|nae: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|late|base|nae: every choice, 1 histories, pairs wholly apart 20 (came apart 20), one part again 0, joint births 0, knot verdicts 45, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|r1|FLOOR0|nae: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|late|base|parity: every choice, 1 histories, pairs wholly apart 20 (came apart 20), one part again 0, joint births 0, knot verdicts 130, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 20 (came apart 20), one part again 0, joint births 0, knot verdicts 130, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 20 (came apart 20), one part again 0, joint births 0, knot verdicts 130, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|r1|fresh by parents|parity: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 20 (came apart 20), one part again 0, joint births 0, knot verdicts 130, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 20 (came apart 20), one part again 0, joint births 0, knot verdicts 130, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|base|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 15, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|base|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|r1|fresh by parents|nae: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 325, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|FLOOR0|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|FLOOR0|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|late|fresh by parents|nae: every choice, 1024 histories, pairs wholly apart 20480 (came apart 20480), one part again 0, joint births 0, knot verdicts 15400, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|fresh by parents|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 15, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|fresh by parents|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|late|base|nae: every choice, 32 histories, pairs wholly apart 640 (came apart 640), one part again 0, joint births 0, knot verdicts 680, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|late|base|parity: every choice, 32 histories, pairs wholly apart 640 (came apart 640), one part again 0, joint births 0, knot verdicts 2005, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|late|FLOOR0|nae: every choice, 32 histories, pairs wholly apart 640 (came apart 640), one part again 0, joint births 0, knot verdicts 2005, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|late|FLOOR0|parity: every choice, 32 histories, pairs wholly apart 640 (came apart 640), one part again 0, joint births 0, knot verdicts 2005, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|Q|late|fresh by parents|parity: every choice, 1024 histories, pairs wholly apart 20480 (came apart 20480), one part again 0, joint births 0, knot verdicts 56405, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 32 histories, pairs wholly apart 640 (came apart 640), one part again 0, joint births 0, knot verdicts 2005, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 32 histories, pairs wholly apart 640 (came apart 640), one part again 0, joint births 0, knot verdicts 2005, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|late|fresh by parents|nae: every choice, 32 histories, pairs wholly apart 640 (came apart 640), one part again 0, joint births 0, knot verdicts 680, failures 0
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|late|fresh by parents|parity: every choice, 32 histories, pairs wholly apart 640 (came apart 640), one part again 0, joint births 0, knot verdicts 2005, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|r1|fresh by parents|parity: every choice, 3280 histories, pairs wholly apart 3072 (came apart 3072), one part again 0, joint births 0, knot verdicts 64539, failures 0
- COPY-LAW(RETIRE)|three-knot|Q|r1|fresh by parents|nae: every choice, 3280 histories, pairs wholly apart 3072 (came apart 3072), one part again 0, joint births 0, knot verdicts 20127, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|r1|base|nae: every choice, 3724 histories, pairs wholly apart 5408 (came apart 5408), one part again 0, joint births 0, knot verdicts 15880, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|r1|base|parity: every choice, 3721 histories, pairs wholly apart 5401 (came apart 5401), one part again 0, joint births 0, knot verdicts 70472, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|r1|FLOOR0|parity: every choice, 3721 histories, pairs wholly apart 5401 (came apart 5401), one part again 0, joint births 0, knot verdicts 70472, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|r1|FLOOR0|nae: every choice, 3724 histories, pairs wholly apart 5408 (came apart 5408), one part again 0, joint births 0, knot verdicts 70516, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|r1|fresh by parents|parity: drawn, 100000 histories, pairs wholly apart 5554 (came apart 5554), one part again 0, joint births 0, knot verdicts 11400000, failures 0, distinct final structures 100000
- COPY-LAW(OFFSHOOT)|two-knot|Q|late|base|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 38, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|late|base|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|late|fresh by parents|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 38, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|late|fresh by parents|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|r1|base|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 684, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|r1|base|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|r1|FLOOR0|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|r1|FLOOR0|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|r1|ONE-FEWER|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|r1|ONE-FEWER|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|r1|fresh by parents|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 684, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|r1|fresh by parents|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|late|base|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 38, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|late|base|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|late|fresh by parents|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 38, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|SHORT-TAKES|late|fresh by parents|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 80, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|r1|base|nae: every choice, 24 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 55, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|r1|base|parity: every choice, 24 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 367, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|r1|FLOOR0|nae: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|r1|FLOOR0|parity: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 12
- COPY-LAW(OFFSHOOT)|three-knot|Q|r1|ONE-FEWER|nae: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|r1|ONE-FEWER|parity: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 12
- COPY-LAW(OFFSHOOT)|three-knot|Q|r1|fresh by parents|nae: every choice, 14416 histories, pairs wholly apart 38400 (came apart 38400), one part again 0, joint births 0, knot verdicts 113439, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|r1|fresh by parents|parity: every choice, 14416 histories, pairs wholly apart 38400 (came apart 38400), one part again 0, joint births 0, knot verdicts 319515, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|late|base|nae: every choice, 1 histories, pairs wholly apart 6 (came apart 6), one part again 0, joint births 0, knot verdicts 22, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|late|base|parity: every choice, 1 histories, pairs wholly apart 6 (came apart 6), one part again 0, joint births 0, knot verdicts 61, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 6 (came apart 6), one part again 0, joint births 0, knot verdicts 61, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 6 (came apart 6), one part again 0, joint births 0, knot verdicts 61, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 6 (came apart 6), one part again 0, joint births 0, knot verdicts 61, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 6 (came apart 6), one part again 0, joint births 0, knot verdicts 61, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|late|fresh by parents|nae: every choice, 64 histories, pairs wholly apart 384 (came apart 384), one part again 0, joint births 0, knot verdicts 595, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|Q|late|fresh by parents|parity: every choice, 64 histories, pairs wholly apart 384 (came apart 384), one part again 0, joint births 0, knot verdicts 1831, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|r1|base|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 382, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|r1|base|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|r1|FLOOR0|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|r1|FLOOR0|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|r1|ONE-FEWER|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|r1|ONE-FEWER|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|r1|fresh by parents|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 382, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|r1|fresh by parents|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|late|base|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 63, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|late|base|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 159, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|late|FLOOR0|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 159, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|late|FLOOR0|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 159, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 159, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 159, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|late|fresh by parents|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 63, failures 0
- COPY-LAW(OFFSHOOT)|three-knot|SHORT-TAKES|late|fresh by parents|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 159, failures 0
- COPY-LAW(OFFSHOOT)|two-knot|Q|r1|fresh by parents|nae: drawn, 100000 histories, pairs wholly apart 5541 (came apart 5541), one part again 0, joint births 0, knot verdicts 6200000, failures 0, distinct final structures 100000
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|r1|base|nae: drawn, 100000 histories, pairs wholly apart 2448715 (came apart 2448715), one part again 0, joint births 0, knot verdicts 4292937, failures 0, distinct final structures 99971
- COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|parity: drawn, 100000 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 19390390, failures 0, distinct final structures 100000
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|r1|base|parity: drawn, 100000 histories, pairs wholly apart 2453209 (came apart 2453209), one part again 0, joint births 0, knot verdicts 12216707, failures 0, distinct final structures 99978
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|r1|FLOOR0|parity: drawn, 100000 histories, pairs wholly apart 2445782 (came apart 2445782), one part again 0, joint births 0, knot verdicts 12218614, failures 0, distinct final structures 99976
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|r1|FLOOR0|nae: drawn, 100000 histories, pairs wholly apart 2441733 (came apart 2441733), one part again 0, joint births 0, knot verdicts 12216985, failures 0, distinct final structures 99969
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|base|nae: every choice, 1 histories, pairs wholly apart 90 (came apart 90), one part again 0, joint births 0, knot verdicts 65, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|base|parity: every choice, 1 histories, pairs wholly apart 90 (came apart 90), one part again 0, joint births 0, knot verdicts 170, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 90 (came apart 90), one part again 0, joint births 0, knot verdicts 170, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 90 (came apart 90), one part again 0, joint births 0, knot verdicts 170, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 90 (came apart 90), one part again 0, joint births 0, knot verdicts 210, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 90 (came apart 90), one part again 0, joint births 0, knot verdicts 210, failures 5
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|fresh by parents|nae: drawn, 100000 histories, pairs wholly apart 9000000 (came apart 9000000), one part again 0, joint births 0, knot verdicts 8500000, failures 0, distinct final structures 95384
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|r1|fresh by parents|parity: drawn, 100000 histories, pairs wholly apart 691070 (came apart 691070), one part again 0, joint births 0, knot verdicts 22064456, failures 0, distinct final structures 100000
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|base|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 15, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|base|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|FLOOR0|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|FLOOR0|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|late|fresh by parents|parity: drawn, 100000 histories, pairs wholly apart 9000000 (came apart 9000000), one part again 0, joint births 0, knot verdicts 19000000, failures 0, distinct final structures 95395
- COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|r1|fresh by parents|nae: drawn, 100000 histories, pairs wholly apart 688118 (came apart 688118), one part again 0, joint births 0, knot verdicts 11210107, failures 0, distinct final structures 99999
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|fresh by parents|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 15, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|fresh by parents|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|base|nae: every choice, 32 histories, pairs wholly apart 2880 (came apart 2880), one part again 0, joint births 0, knot verdicts 1175, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|base|parity: every choice, 32 histories, pairs wholly apart 2880 (came apart 2880), one part again 0, joint births 0, knot verdicts 2985, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|FLOOR0|nae: every choice, 32 histories, pairs wholly apart 2880 (came apart 2880), one part again 0, joint births 0, knot verdicts 2985, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|FLOOR0|parity: every choice, 32 histories, pairs wholly apart 2880 (came apart 2880), one part again 0, joint births 0, knot verdicts 2985, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 32 histories, pairs wholly apart 2880 (came apart 2880), one part again 0, joint births 0, knot verdicts 3170, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 32 histories, pairs wholly apart 2880 (came apart 2880), one part again 0, joint births 0, knot verdicts 3170, failures 160
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|fresh by parents|nae: every choice, 32 histories, pairs wholly apart 2880 (came apart 2880), one part again 0, joint births 0, knot verdicts 1175, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|late|fresh by parents|parity: every choice, 32 histories, pairs wholly apart 2880 (came apart 2880), one part again 0, joint births 0, knot verdicts 2985, failures 0
- COPY-LAW(WAIT)|two-knot|Q|r1|base|nae: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 6, failures 0
- COPY-LAW(WAIT)|two-knot|Q|r1|base|parity: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(WAIT)|two-knot|Q|r1|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(WAIT)|two-knot|Q|r1|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(WAIT)|two-knot|Q|r1|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(WAIT)|two-knot|Q|r1|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(WAIT)|two-knot|Q|r1|fresh by parents|nae: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 6, failures 0
- COPY-LAW(WAIT)|two-knot|Q|r1|fresh by parents|parity: every choice, 1 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 26, failures 0
- COPY-LAW(WAIT)|two-knot|Q|late|base|nae: every choice, 4 histories, pairs wholly apart 68 (came apart 24), one part again 0, joint births 0, knot verdicts 76, failures 0
- COPY-LAW(WAIT)|two-knot|Q|late|base|parity: every choice, 4 histories, pairs wholly apart 68 (came apart 24), one part again 0, joint births 0, knot verdicts 176, failures 0
- COPY-LAW(WAIT)|two-knot|Q|late|FLOOR0|nae: every choice, 4 histories, pairs wholly apart 68 (came apart 24), one part again 0, joint births 0, knot verdicts 176, failures 0
- COPY-LAW(WAIT)|two-knot|Q|late|FLOOR0|parity: every choice, 4 histories, pairs wholly apart 68 (came apart 24), one part again 0, joint births 0, knot verdicts 176, failures 0
- COPY-LAW(WAIT)|two-knot|Q|late|ONE-FEWER|nae: every choice, 4 histories, pairs wholly apart 68 (came apart 24), one part again 0, joint births 0, knot verdicts 176, failures 0
- COPY-LAW(WAIT)|two-knot|Q|late|ONE-FEWER|parity: every choice, 4 histories, pairs wholly apart 68 (came apart 24), one part again 0, joint births 0, knot verdicts 176, failures 0
- COPY-LAW(WAIT)|two-knot|Q|late|fresh by parents|nae: every choice, 4 histories, pairs wholly apart 68 (came apart 24), one part again 0, joint births 0, knot verdicts 76, failures 0
- COPY-LAW(WAIT)|two-knot|Q|late|fresh by parents|parity: every choice, 4 histories, pairs wholly apart 68 (came apart 24), one part again 0, joint births 0, knot verdicts 176, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|r1|base|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 684, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|r1|base|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|r1|FLOOR0|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|r1|FLOOR0|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|r1|ONE-FEWER|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|r1|ONE-FEWER|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|r1|fresh by parents|nae: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 684, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|r1|fresh by parents|parity: every choice, 64 histories, pairs wholly apart 192 (came apart 0), one part again 0, joint births 0, knot verdicts 2020, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|late|base|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 34, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|late|base|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 74, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 74, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 74, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 74, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 74, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|late|fresh by parents|nae: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 34, failures 0
- COPY-LAW(WAIT)|two-knot|SHORT-TAKES|late|fresh by parents|parity: every choice, 1 histories, pairs wholly apart 17 (came apart 6), one part again 0, joint births 0, knot verdicts 74, failures 0
- COPY-LAW(WAIT)|three-knot|Q|r1|base|nae: every choice, 24 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 55, failures 0
- COPY-LAW(WAIT)|three-knot|Q|r1|base|parity: every choice, 24 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 367, failures 0
- COPY-LAW(WAIT)|three-knot|Q|r1|FLOOR0|nae: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 0
- COPY-LAW(WAIT)|three-knot|Q|r1|FLOOR0|parity: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 12
- COPY-LAW(WAIT)|three-knot|Q|r1|ONE-FEWER|nae: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 0
- COPY-LAW(WAIT)|three-knot|Q|r1|ONE-FEWER|parity: every choice, 4 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 111, failures 12
- COPY-LAW(WAIT)|three-knot|Q|r1|fresh by parents|nae: every choice, 3280 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 20127, failures 0
- COPY-LAW(WAIT)|three-knot|Q|r1|fresh by parents|parity: every choice, 3280 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 64539, failures 0
- COPY-LAW(WAIT)|three-knot|Q|late|base|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 36, failures 0
- COPY-LAW(WAIT)|three-knot|Q|late|base|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 133, failures 0
- COPY-LAW(WAIT)|three-knot|Q|late|FLOOR0|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 133, failures 0
- COPY-LAW(WAIT)|three-knot|Q|late|FLOOR0|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 133, failures 0
- COPY-LAW(WAIT)|three-knot|Q|late|ONE-FEWER|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 133, failures 0
- COPY-LAW(WAIT)|three-knot|Q|late|ONE-FEWER|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 133, failures 0
- COPY-LAW(WAIT)|three-knot|Q|late|fresh by parents|nae: every choice, 128 histories, pairs wholly apart 768 (came apart 768), one part again 0, joint births 0, knot verdicts 1048, failures 0
- COPY-LAW(WAIT)|three-knot|Q|late|fresh by parents|parity: every choice, 128 histories, pairs wholly apart 768 (came apart 768), one part again 0, joint births 0, knot verdicts 3253, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|r1|base|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 382, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|r1|base|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|r1|FLOOR0|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|r1|FLOOR0|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|r1|ONE-FEWER|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|r1|ONE-FEWER|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|r1|fresh by parents|nae: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 382, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|r1|fresh by parents|parity: every choice, 56 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1317, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|late|base|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 57, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|late|base|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 144, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|late|FLOOR0|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 144, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|late|FLOOR0|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 144, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 144, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 144, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|late|fresh by parents|nae: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 57, failures 0
- COPY-LAW(WAIT)|three-knot|SHORT-TAKES|late|fresh by parents|parity: every choice, 4 histories, pairs wholly apart 24 (came apart 24), one part again 0, joint births 0, knot verdicts 144, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|r1|base|nae: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 325, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|r1|base|parity: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|r1|FLOOR0|nae: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|r1|FLOOR0|parity: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|r1|ONE-FEWER|nae: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|r1|ONE-FEWER|parity: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|r1|fresh by parents|nae: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 325, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|r1|fresh by parents|parity: every choice, 32 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 1925, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|late|base|nae: every choice, 1 histories, pairs wholly apart 30 (came apart 30), one part again 0, joint births 0, knot verdicts 45, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|late|base|parity: every choice, 1 histories, pairs wholly apart 30 (came apart 30), one part again 0, joint births 0, knot verdicts 130, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|late|FLOOR0|nae: every choice, 1 histories, pairs wholly apart 30 (came apart 30), one part again 0, joint births 0, knot verdicts 130, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|late|FLOOR0|parity: every choice, 1 histories, pairs wholly apart 30 (came apart 30), one part again 0, joint births 0, knot verdicts 130, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|late|ONE-FEWER|nae: every choice, 32 histories, pairs wholly apart 960 (came apart 960), one part again 0, joint births 0, knot verdicts 3405, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|late|ONE-FEWER|parity: every choice, 32 histories, pairs wholly apart 960 (came apart 960), one part again 0, joint births 0, knot verdicts 3405, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|late|fresh by parents|nae: every choice, 1024 histories, pairs wholly apart 30720 (came apart 30720), one part again 0, joint births 0, knot verdicts 15400, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|Q|late|fresh by parents|parity: every choice, 1024 histories, pairs wholly apart 30720 (came apart 30720), one part again 0, joint births 0, knot verdicts 56405, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|base|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 15, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|base|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|FLOOR0|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|FLOOR0|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|parity: drawn, 100000 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 19395325, failures 0, distinct final structures 100000
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|parity: drawn, 100000 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 19393872, failures 0, distinct final structures 100000
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|late|ONE-FEWER|nae: every choice, 1024 histories, pairs wholly apart 30720 (came apart 30720), one part again 0, joint births 0, knot verdicts 87135, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|late|ONE-FEWER|parity: every choice, 1024 histories, pairs wholly apart 30720 (came apart 30720), one part again 0, joint births 0, knot verdicts 87135, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|fresh by parents|nae: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 15, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|fresh by parents|parity: every choice, 2 histories, pairs wholly apart 0 (came apart 0), one part again 0, joint births 0, knot verdicts 50, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|late|base|nae: every choice, 28672 histories, pairs wholly apart 860160 (came apart 860160), one part again 0, joint births 0, knot verdicts 713369, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|late|base|parity: every choice, 28672 histories, pairs wholly apart 860160 (came apart 860160), one part again 0, joint births 0, knot verdicts 2004429, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|late|FLOOR0|nae: every choice, 28672 histories, pairs wholly apart 860160 (came apart 860160), one part again 0, joint births 0, knot verdicts 2004429, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|late|FLOOR0|parity: every choice, 28672 histories, pairs wholly apart 860160 (came apart 860160), one part again 0, joint births 0, knot verdicts 2004429, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|late|fresh by parents|nae: every choice, 28672 histories, pairs wholly apart 860160 (came apart 860160), one part again 0, joint births 0, knot verdicts 713369, failures 0
- COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|late|fresh by parents|parity: every choice, 28672 histories, pairs wholly apart 860160 (came apart 860160), one part again 0, joint births 0, knot verdicts 2004429, failures 0
- RING-LAW|Ring(5,3)|Q|r1|base|nae: drawn, 100000 histories, pairs wholly apart 388 (came apart 388), one part again 0, joint births 0, knot verdicts 5495872, failures 0, distinct final structures 93750
- RING-LAW|Ring(5,3)|Q|r1|base|parity: drawn, 100000 histories, pairs wholly apart 378 (came apart 378), one part again 0, joint births 0, knot verdicts 14431566, failures 0, distinct final structures 93835
- COPY-LAW(OFFSHOOT)|two-knot|Q|r1|ONE-FEWER|parity: drawn, 100000 histories, pairs wholly apart 1073 (came apart 1073), one part again 0, joint births 0, knot verdicts 8710208, failures 0, distinct final structures 100000
- RING-LAW|Ring(5,3)|Q|r1|FILLERS|parity: drawn, 100000 histories, pairs wholly apart 408 (came apart 408), one part again 0, joint births 0, knot verdicts 14418850, failures 0, distinct final structures 93704

Not finished when this summary was written: ["COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|nae", "COPY-LAW(OFFSHOOT)|two-knot|Q|r1|ONE-FEWER|nae", "COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|r1|ONE-FEWER|nae", "COPY-LAW(OFFSHOOT)|Ring(5,3)|Q|r1|ONE-FEWER|parity", "COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|nae", "COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|nae", "RING-LAW|two-knot|Q|r1|base|nae", "RING-LAW|two-knot|Q|r1|base|parity", "RING-LAW|two-knot|Q|r1|FILLERS|nae", "RING-LAW|two-knot|Q|r1|FILLERS|parity", "RING-LAW|two-knot|Q|r1|fresh by parents|nae", "RING-LAW|two-knot|Q|r1|fresh by parents|parity", "RING-LAW|two-knot|Q|late|base|nae", "RING-LAW|two-knot|Q|late|base|parity", "RING-LAW|two-knot|Q|late|FILLERS|nae", "RING-LAW|two-knot|Q|late|FILLERS|parity", "RING-LAW|two-knot|Q|late|fresh by parents|nae", "RING-LAW|two-knot|Q|late|fresh by parents|parity", "RING-LAW|two-knot|SHORT-TAKES|r1|base|nae", "RING-LAW|two-knot|SHORT-TAKES|r1|base|parity", "RING-LAW|two-knot|SHORT-TAKES|r1|FILLERS|nae", "RING-LAW|two-knot|SHORT-TAKES|r1|FILLERS|parity", "RING-LAW|two-knot|SHORT-TAKES|r1|fresh by parents|nae", "RING-LAW|two-knot|SHORT-TAKES|r1|fresh by parents|parity", "RING-LAW|two-knot|SHORT-TAKES|late|base|nae", "RING-LAW|two-knot|SHORT-TAKES|late|base|parity", "RING-LAW|two-knot|SHORT-TAKES|late|FILLERS|nae", "RING-LAW|two-knot|SHORT-TAKES|late|FILLERS|parity", "RING-LAW|two-knot|SHORT-TAKES|late|fresh by parents|nae", "RING-LAW|two-knot|SHORT-TAKES|late|fresh by parents|parity", "RING-LAW|three-knot|Q|r1|base|nae", "RING-LAW|three-knot|Q|r1|base|parity", "RING-LAW|three-knot|Q|r1|FILLERS|nae", "RING-LAW|three-knot|Q|r1|FILLERS|parity", "RING-LAW|three-knot|Q|r1|fresh by parents|nae", "RING-LAW|three-knot|Q|r1|fresh by parents|parity", "RING-LAW|three-knot|Q|late|base|nae", "RING-LAW|three-knot|Q|late|base|parity", "RING-LAW|three-knot|Q|late|FILLERS|nae", "RING-LAW|three-knot|Q|late|FILLERS|parity", "RING-LAW|three-knot|Q|late|fresh by parents|nae", "RING-LAW|three-knot|Q|late|fresh by parents|parity", "RING-LAW|three-knot|SHORT-TAKES|r1|base|nae", "RING-LAW|three-knot|SHORT-TAKES|r1|base|parity", "RING-LAW|three-knot|SHORT-TAKES|r1|FILLERS|nae", "RING-LAW|three-knot|SHORT-TAKES|r1|FILLERS|parity", "RING-LAW|three-knot|SHORT-TAKES|r1|fresh by parents|nae", "RING-LAW|three-knot|SHORT-TAKES|r1|fresh by parents|parity", "RING-LAW|three-knot|SHORT-TAKES|late|base|nae", "RING-LAW|three-knot|SHORT-TAKES|late|base|parity", "RING-LAW|three-knot|SHORT-TAKES|late|FILLERS|nae", "RING-LAW|three-knot|SHORT-TAKES|late|FILLERS|parity", "RING-LAW|three-knot|SHORT-TAKES|late|fresh by parents|nae", "RING-LAW|three-knot|SHORT-TAKES|late|fresh by parents|parity", "RING-LAW|Ring(5,3)|Q|r1|FILLERS|nae", "RING-LAW|Ring(5,3)|Q|r1|fresh by parents|nae", "RING-LAW|Ring(5,3)|Q|r1|fresh by parents|parity", "RING-LAW|Ring(5,3)|Q|late|base|nae", "RING-LAW|Ring(5,3)|Q|late|base|parity", "RING-LAW|Ring(5,3)|Q|late|FILLERS|nae", "RING-LAW|Ring(5,3)|Q|late|FILLERS|parity", "RING-LAW|Ring(5,3)|Q|late|fresh by p ...

Their progress (last progress line): {"COPY-LAW(OFFSHOOT)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|nae": {"histories_so_far": 60000, "joint_births_so_far": 0, "knot_fails_so_far": 0, "mode": "drawn", "one_part_again_so_far": 0, "pairs_wholly_apart_so_far": 0, "seconds": 4929.8}, "COPY-LAW(OFFSHOOT)|two-knot|Q|r1|ONE-FEWER|nae": {"histories_so_far": 15000, "joint_births_so_far": 0, "knot_fails_so_far": 0, "mode": "drawn", "one_part_again_so_far": 0, "pairs_wholly_apart_so_far": 147, "seconds": 4172.5}, "COPY-LAW(RETIRE)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|nae": {"histories_so_far": 60000, "joint_births_so_far": 0, "knot_fails_so_far": 0, "mode": "drawn", "one_part_again_so_far": 0, "pairs_wholly_apart_so_far": 0, "seconds": 4939.8}, "COPY-LAW(WAIT)|Ring(5,3)|SHORT-TAKES|r1|ONE-FEWER|nae": {"histories_so_far": 55000, "joint_births_so_far": 0, "knot_fails_so_far": 0, "mode": "drawn", "one_part_again_so_far": 0, "pairs_wholly_apart_so_far": 0, "seconds": 4544.1}, "RING-LAW|Ring(5,3)|Q|r1|FILLERS|nae": {"histories_so_far": 95000, "joint_births_so_far": 0, "knot_fails_so_far": 0, "mode": "drawn", "one_part_again_so_far": 0, "pairs_wholly_apart_so_far": 357, "seconds": 1365.7}, "RING-LAW|Ring(5,3)|Q|r1|fresh by parents|nae": {"histories_so_far": 10000, "joint_births_so_far": 0, "knot_fails_so_far": 0, "mode": "drawn", "one_part_again_so_far": 0, "pairs_wholly_apart_so_far": 36, "seconds": 314.5}}

## Stops

{"carry-alt None": 36, "carry-alt guard": 6, "run1 None": 402, "run1 guard": 4, "run1 knots": 4, "run1 residual_stall": 52, "run3 None": 830, "run3 guard": 46, "run3 knots": 6, "run7 None": 96}

Errors: []
