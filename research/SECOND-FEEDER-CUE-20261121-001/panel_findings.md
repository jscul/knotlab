# Two actual feeders with equal numbers of exits

Both branches had already eaten at feeder A. One returned to empty A and the other reached still-full B. The two feeders had exactly the same number of exits at the decision. The current observations, old memory, founder, naming, movement tape, turn and total number of previous meals matched. We found 440 such pairs per law on fresh founders. The frozen history rule proved depletion on eight empty branches and availability on twelve full branches. These were 20 different pairs. The other 420 pairs kept both answers unresolved. [Matched histories](panel_pairs.json.gz) · [Public rule](../FEEDER-MEMORY-20261121-001/public_certificate.md)

## What the original confusion looked like

Among the preceding study's 2,354 same-memory nonflips, 688 per law involved a distinct previously paid feeder with the same exact number of exits as the query. Those earlier pairs queried the same physical target on both branches. Reassembling the archived terminal paths also gave 366 opposite-stock pairs at two physically distinct equal-exit feeders where both branches had eaten only at A. The frozen reader certified one side in 43 pairs and left both unresolved in 323. Its earlier positive memory-swap example used one versus several exits. [Reconstructed archive](panel_archive.json) · [Independent archive reproducer](panel_archive.py)

## What the complete local history supports

We evaluated 32 fresh founder structures with one held-out renaming, 16 movement tapes, both laws and all 56 scheduled preparations per cell. Fourteen founders funded a first formation and eighteen stalled. Per law, the 28,672 complete games accounted for 192,404 decision appearances and 36,734 distinct reached prefixes. Of 14,703 feeder visits, the public rules certified 5,140 full and 3,211 empty. Identical *complete* public histories had opposite stock in 25 visits. The other 6,327 remain unresolved. Parity and not-all-equal produced identical episode records on these starts. [Exact results and per-founder counts](panel_results.json)

In the finite bank, 40 of the 94 current views admitted opposite stock. The complete public records formed 13,822 classes, of which eleven admitted opposite stock and 13,465 occurred only once. Across the 440 primary pairs, both public records had a single stock value in this finite support on 438 pairs. The sound public rules certified both sides on zero pairs. That difference matters whenever a read occurred only once. The fixed current-only policy chose the stock-appropriate bit on 12,288 feeder visits and the frozen complete-history policy on 12,448. These are classifications of the same prepared paths. [Observation classes and weighting](panel_results.json)

| Per law | Distinct feeders, same tape | Distinct feeders, adjacent tapes | Same feeder queried, different feeder previously eaten |
| --- | ---: | ---: | ---: |
| Opposite-stock pairs | 440 | 425 | 639 |
| Distinct visits in those pairs | 576 | 497 | 793 |
| Visits after a prior meal outside those pairs | 12,134 | 12,213 | 11,917 |
| Both branches visited both matched feeders before the query | 75 | 49 | 247 |
| Last meal turn and pre-meal energy matched | 151 | 150 | 79 |
| Opposite order of first visiting the two feeders | 4 | 52 | 36 |
| Different numbers of moves on the two returns | 119 | 117 | 118 |
| Different intervening holders on the two returns | 172 | 173 | 174 |
| Public rule certified both stock values | 0 | 0 | 0 |
| Opposite first actions gave strictly higher energy on both branches after the common next ON | 50 | 38 | 21 |

Each pair receives one vote. The 576 visits in the primary comparison came from fourteen founders; the other eighteen had no qualifying pair. The mean fraction with both sides certified, giving each of the fourteen founders equal weight, was zero. The primary pairs included seven with two exits, 196 with three, 226 with four and eleven with five. In 298 the entire previously eaten set was the same and in 236 the branches had eaten only at A. All 440 took different sequences of departure holders even after omitting the different final endpoints; the 172 in the return comparison also visited different intervening holders between the previous and current visit to their own target. [Matched histories](panel_pairs.json.gz)

## What an earlier receipt can prove

On one turn-7 pair both current feeders had three exits. The empty-side bot had found A through a founder's first slot and eaten there. A then had one exit, which forced its return to that founder. The founder still had three exits after the last growth opportunity. Its first slot therefore still went to A. Taking it proved that the current feeder was empty even though A now had three exits of its own. The full-side history left its stock unresolved. On another pair the full-side bot had made a move directly from its only previously paid feeder to the current feeder. A move changes holders, so the new feeder had food despite having the same current degree as the old one. The other side remained unresolved. The first example is founder seed 7429920749878472752, tape 1497352126128417382; the second is founder seed 4151710084615049439, tape 17940527312967456023, turn 6. [Public actions and certificates](panel_pairs.json.gz)

## Two payoffs and one sensor reading

The short payoff comparison made two actual game copies at each query. One tried and one passed; both tried on the following turn if still alive. We counted energy after those two turns, including zero after death. In 50 of the 440 primary pairs, OFF gave higher energy at empty A and ON gave higher energy at full B. All 50 were among the 254 pairs with at least two energy at the decision. Across the other 390 pairs these strict inequalities did not both hold. [Counterfactual energy records](panel_pairs.json.gz)

One pair reached turn 8 with three energy. Both branches had eaten only at A on turn 4 and had seen both A and B before the decision. The empty branch returned after two moves. The full branch returned to B after four. A and B each offered three controls, with the same old memory. At A, passing left five energy after the following attempt and trying immediately left one. At B those two outcomes were reversed. The history rule left both sides unresolved. The source is founder seed 4151710084615049439 and the movement tape is 13733146636244823494. [Exact paths and four energy values](panel_pairs.json.gz)

## A fresh ambiguity any permitted reader faces

For one fresh founder, both branches ate only at feeder 7 on turn 2. Both had seen two controls there then. The move slots subsequently used, the feeder signals, previous actions and energy were identical at every turn. After the turn-5 formation, both queried feeders had three exits. One branch reached empty 7 and the other full 6. The visible records of the two turns after the meal were a pass via slot zero and a pass via slot one. The game concealed which slot the cursor had arrived through. [Complete witness, including both tapes](panel_results.json)

| Turn | 1 | 2 | 3 | 4 | 5, before action |
| --- | --- | --- | --- | --- | --- |
| Feeder signal | Off | On | On | Off | On |
| Energy | 6 | 5 | 8 | 7 | 6 |
| Exits | 3 | 2 | 2 | 3 | 3 |
| Action, zero-based outward slot | Pass via 0 | Try | Pass via 0 | Pass via 1 | Undecided |
| Actual holder, empty / full branch | 0 / 0 | 7 / 7 | 7 / 7 | 5 / 0 | 7 / 6 |

Because the entire public input is identical, a deterministic reader must issue the same bit on the two branches. Private randomness independent of the game can give at most one-half expected accuracy on the equally weighted pair. Among all sixteen tapes per founder there were seven such distinct-target pairs with A paid in both branches and B untouched. One belonged to the predefined adjacent-tape comparison. Their existence leaves the other unresolved cases open. [Public ambiguity witnesses](panel_results.json)

The independent checker rebuilt the actual movements from the owners of each shared distinction, the original movement draw, and the counters for energy and paid rations. It verified every scheduled path, regenerated all pairing conditions and both full-history class counts, and obtained the four two-turn energies for every pair directly from the physical state. The observed pair counts were 440, 425 and 639 under each law. [Independent verification](panel_verified.json) · [Verification code](panel_verify.py)
