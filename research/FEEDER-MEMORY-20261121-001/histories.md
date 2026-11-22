# What a moving reader can know about a feeder

On 3,332 pairs of visits with opposite ration states and identical current observations, the complete local history proved which feeder had been emptied on both sides of 234 pairs. Other histories left the answer open. On one fresh start the bot made the same attempts, used exactly the same outward slot numbers, received the same energy after every action and reached the same actual feeder with opposite ration states under two presentations. These counts held separately under parity and not-all-equal. The two laws produced identical episode records on these starts. [Matched pairs](history_pairs.json.gz) · [Results](history_results.json)

## The saved game

On turns 15 and 21 the cursor reached the same actual feeder. With the persistent feeder sensor, both views have the signal on, energy eight, a preceding move and two anonymous exits. The archived bot ate there on turn 15 and passed on turn 21. The scorer found a ration on the former visit and an empty feeder on the latter. The frozen public reader returns unresolved on both. Its history leaves open a possible match to an earlier meal on turn 3. This is a reading of the recorded action sequence with the new signal on every turn. [Recorded game](../KNOT-RATION-GAME-20261121-001/replays/208304-nae-sensing.json) · [Public reader](history_reader.py)

## All fresh visits, including uncertainty

We used 16 distinct founder structures excluded from earlier play and from the survival comparison. Eight funded a first birth and eight stalled under each law. For every founder we used 16 movement tapes, original and consistently renamed distinctions with newly ranked local slots, and every one of the 56 schedules that attempts up to two eats on turns 1–10. All other decisions passed with the game's ordinary movement draw. Each game ended by turn 14. Counts give equal weight to each distinct reached action prefix in a cell. Schedules with identical past actions have the same visit until their actions diverge. The 28,672 complete schedules per law account for 197,060 individual decision appearances, including 26,755 charged empty attempts. [Registration](preregistration.md) · [Terminal paths and multiplicities](history_runs.json.gz)

| Per law | Original names | Renamed, newly ranked slots | Both presentations |
| --- | ---: | ---: | ---: |
| Distinct reached visits | 20,082 | 20,208 | 40,290 |
| Feeder visits | 8,976 | 9,176 | 18,152 |
| Ration present, certified using only public history | 3,061 | 3,219 | 6,280 |
| Ration gone, certified using only public history | 2,102 | 2,108 | 4,210 |
| Same entire public history, opposite stock witnessed in this support | 4 | 2 | 61 |
| Remaining unresolved visits | 3,809 | 3,847 | 7,601 |
| Correct decisions using the current feeder bit and previous action | 7,375 | 7,465 | 14,840 |
| Correct decisions using the whole public record, eating on unresolved feeders | 7,609 | 7,681 | 15,290 |

The four certainty rows partition all feeder visits in each column. Combining presentations admits additional matches between original and renamed histories. The other 22,138 visits across presentations were to founders. On every feeder visit the last two rows score the issued bit against the presence of a ration. The whole-history policy made 450 additional correct decisions over these paths. Actual survival on the separate founder sample is a different measurement. [Counts by law and presentation](history_results.json)

The complete finite support lets us calculate how well any lookup on this support could score. Among 95 current observations, 40 had opposite outcomes, covering 14,344 visits. A majority choice for each observation would score 14,865 of 18,152. Among 16,192 entire public histories, 28 had opposite outcomes, covering 61 visits. A majority choice for each history would score 18,124. Of the 16,164 histories with one observed outcome, 15,289 occurred only once. The public reader credits certainty only when the observations and rules force it. Its proof follows each paid attempt, carries identities across actually witnessed stays and forced returns, and respects the possible insertion of new controls before turn 5. [Exact classes](history_results.json) · [Certificate rules](public_certificate.md)

## A return that settles the question

The preregistered choice of example reaches turn 10 on founder seed 15776084479232194445, with original names and tape 7224311483179669286. The two branches had each visited both distinct feeders before the query. Each had obtained its only meal on turn 6 at energy one. At the query, both saw the feeder bit on, energy one, a previous move and three exits. The route includes a one-exit feeder. After the last growth opportunity, leaving a holder for that feeder and taking its sole exit must return to the holder just left. This argument needs no report of the arrival slot. [Selected prefixes and public actions](history_results.json)

| Prior evidence | Branch that emptied the queried feeder | Branch that emptied the other feeder |
| --- | --- | --- |
| First attempt | Ate the three-exit feeder on turn 6 | Tried at a founder on turn 3 |
| Second attempt | Tried again at the same three-exit feeder on turn 7 and lost one energy | Ate the one-exit feeder on turn 6 |
| Subsequent moves since the meal | Two, through the one-exit feeder and back | Three, including another forced return |
| Public conclusion on turn 10 | Empty, a verified return to the feeder where the attempt on turn 7 failed | Full, the only previously paid feeder had one exit and the current feeder has three in the same stable period |
| Useful bit | OFF passes and moves | ON attempts the available ration |

The shortest pair with both conclusions and opposite useful last-meal-type outputs reached a decision on turn 8. Both branches visited the same two distinct feeders. One ate the three-exit feeder, visited the one-exit feeder and returned. The other ate the one-exit feeder and returned to the three-exit feeder. In the longer selected example, earlier meal turn and pre-meal energy also match. Three pairs per law met all three selection preferences as well as both public certificates and the two useful predicted outputs. [Shortest and selected pairs](history_results.json)

## A return no permitted reader can settle

On founder seed 2170504463124764764 and tape 10366267210353236488, both games tried to eat on turns 2 and 3. The first attempt took energy from five to eight. The second took energy from eight to seven. The original presentation reached the same feeder again on turn 6. The renamed presentation first reached that same physical target on turn 6 after emptying a different feeder. The target held a ration in the renamed game. The names in the last row are available only to the scorer. [Witness and complete public records](history_results.json)

| Turn | 1 | 2 | 3 | 4 | 5 | 6, before action |
| --- | --- | --- | --- | --- | --- | --- |
| Feeder signal, both | Off | On | On | On | Off | On |
| Energy, both | 6 | 5 | 8 | 7 | 6 | 5 |
| Number of controls, both | 4 | 2 | 2 | 2 | 4 | 4 |
| Action, both, with outward slots numbered from zero | Pass via 2 | Try | Try | Pass via 1 | Pass via 1 | Undecided |
| Actual holder, original / renamed | 0 / 0 | 5 / 7 | 5 / 7 | 5 / 7 | 1 / 0 | 5 / 5 |

Both traces have the same previous actual action at every visit. Consequently any deterministic reader confined to these observations must give the same answer to both histories. A randomized reader with the same private randomness has the same limitation. With equal weight on these two cases the maximum correct fraction is one half. The observed identity of the queried target strengthens the witness. The bot never received it. [Verified witness](history_verification.json)

## What changed across return routes and visit orders

The matched-pair gate compared the very same founder, tape, presentation, current physical feeder, decision turn, current public observation and number of earlier paid meals. The earlier spent sets differed and stock at the current feeder was opposite. Of 12,084 arrivals after a prior meal, 3,509 distinct visits belonged to at least one such pair. The other 8,575 remain in the visit results. The 3,332 overlapping pairs are a comparison of possible histories, each pair counted once. [Paired alternatives](history_pairs.json.gz)

| Per law | Original names | Renamed | Total |
| --- | ---: | ---: | ---: |
| All opposite-stock pairs | 1,574 | 1,758 | 3,332 |
| Complete public history proves both answers | 128 | 106 | 234 |
| Both branches visited the same two feeders by the decision | 1,055 | 1,076 | 2,131 |
| Both branches visited both feeders before the decision | 791 | 784 | 1,575 |
| Equal last-meal turn and pre-meal energy | 153 | 189 | 342 |
| Both branches had at least two moves since the last meal | 1,237 | 1,390 | 2,627 |
| The last paid feeders had the same one-or-many control count | 1,034 | 1,320 | 2,354 |
| Certified answers and a useful opposite choice from the last-meal-type rule | 78 | 40 | 118 |

In 183 pairs both branches visited both feeders in opposite first-visit orders. None of these 183 yielded two public certificates under the frozen rule. In 491 pairs the two branches returned to the target by different numbers of moves. Across the full matched set there were 2,572 patterns of holder revisits after erasing physical names. On a renamed start, one branch returned after eight moves, the other after two, and the first-visit order of the queried and other feeder reversed. Both branches had last eaten on turn 7 at energy four and made six more moves before the turn-14 probe. Their last paid feeders each had multiple exits. The public rule left both unresolved and the type-only memory predicted the same bit on both. The full record also includes two-return versus ten-return moves with the same visit order. [Detailed route and order examples](history_results.json)

Reversing distinction names while transporting the original numbering of the anonymous controls reproduced every physical path and receipt in all 56 schedules on the first tape of each founder and each law. These 1,792 repeated schedules were excluded from the main counts. An independent program reconstructed the original and renamed movement menus directly from distinction ownership, recomputed each ordinary port draw and energy change, then recovered every one of the 3,332 pairs and the full-history classes for each law. The complete primary bank supplied both required kinds of witness and met the stopping rule. [Independent verification](history_verification.json) · [Verification code](history_verify.py) · [Enumerator](history_panel.py)
