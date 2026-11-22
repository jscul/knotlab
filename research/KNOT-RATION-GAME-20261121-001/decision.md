# How long can a bot survive on knot-grown rations?

The one-bit script lived longest on unseen starts. A bot that eats on a positive food bit and otherwise follows a shared distinction lived 4.82 turns longer on average than the blind move-then-eat script and 5.02 turns longer than the fitted learner. These are empirical comparisons of named policies in a supplied game. The actual births and available shared distinctions follow from unchanged ordinary growth. [Play from a seed](README.md) · [Watch the movie](media/208304-nae-sensing.mp4)

## Design and checkpoints

The owner selected movement between actual holders from B208 and one-bit observation from B304. Founders have three through seven holders with the labelled-tree weighting, private counts, optional first funding, name recoding and exact exclusion rule described in the prospective design. Excluding repeated structures and reserved folds changes the weighting from raw independent source seeds. Each evaluation founder counts equally and uses four movement tapes. Bot, law and movement tape never change the source draw. The B208 distance-reading experiment and the B304 hidden-law calibration remain open. [Frozen rules](preregistration.md) · [Independent Astra Max objection and resolution](design_review.json)

Before learning, seven distinct fresh founders under both laws and both scripted policies produced 28 whole games. All 468 turns were verified to use actual holders, to lose an eaten ration, to charge for a failed eat, and to end at zero. This passed the GO condition for learning. Training made 27,980 Q updates in 3,072 episodes. Only the frozen final checkpoint played the 2,048 evaluation games. There were 35 first-funded starts and 29 stalls under each law. Across the 64 starts each law supplied 612 rations. Every paired full growth record agreed across laws, including paid and fresh distinctions. Other lawful starts or longer ordinary growth can differ. [Scripted check](smoke.json) · [World controls](test_world.py) · [Canonical finite knot checks, widths 3–9](law_checks.json)

The primary measure counts each completed turn including death. A failed eat costs one. A present meal grants four with a capacity of ten. Consequently an episode with (m) meals lasts exactly six plus four times (m), less energy discarded at capacity. No trial was censored. Median lifetimes were 14 turns for sensing and 6 for each other policy. On each law the sensing bot outlasted the move-then-eat bot in 98 of 256 games, tied in 132 and lost in 26. The learner outlasted the sensing script in 27, tied in 131 and lost in 98. A 2,000-draw paired bootstrap resampled the 64 whole starts including all four tapes. For sensing minus blind the intervals were [3.32, 6.54] turns under parity and [3.29, 6.58] under not-all-equal. For learner minus sensing they were [−6.82, −3.34] and [−6.79, −3.30]. The differing endpoints arise from the frozen independent bootstrap streams. Duplicated law copies were never pooled as independent evidence. [Full results](results.json) · [Every episode](per_episode.csv)

On the learner's own 3,288 turns per law, it agreed with the script on 2,337 actions. Its 878 empty eats and 73 departures with a ration present account for all disagreements. These descriptions of its visited states illustrate policy behaviour. Choosing a different learner or a different price can change the ranking. Isolating the causal effect of enabling its own sensor would require a matched, separately trained blind learner. B304 supplied access to a local bit. The ration ledger and its coupling to each funded birth are extra game rules. The food bit contains no law label.

Exact global projection checks recovered the full canonical local relation at every holder of all 193 sources used for training, evaluation and the spectator. That covered 371 reached stages and 4,632 holder projections per law. [Projection checks](global_law_checks.json)

The complete training repeat regenerated the same checkpoint and the exact same episode ledger. The independent turn check recovered all 2,048 evaluation event hashes, 26,650 individual turn ledgers and 1,024 matched law pairs from seed. It rebuilt physical ownership and the food and energy ledgers independently of the game's scoring function. A simultaneous name recoding with the same actual moves preserved movement and depletion. In the reserved spectator example the game grew first six, then five new knots. All 28 decisions are visible. The visual layout stays outside the bot. [Verification code](verify_scores.py) · [Machine checks](validation.json) · [Full spectator events](replays/208304-nae-sensing.json)

The first checkpoint authorized training. The second closes the bounded comparison and the handoff for independent scientific review. [Referee handoff](referee_handoff.md)

## Final report as sent

2026-11-21, 22:06 PST

The food-sensing bot lived longest. On fresh held-out starts it averaged **17.87 turns**, compared with **13.05** for the blind move-then-eat bot and **12.84** for the reinforcement learner. Every bot played unattended until its energy reached zero.

![Spectator replay showing ordinary knot growth, the food sensor, actual moves, consumed rations and energy through death](/home/jscul/p-vs-np-contact-first/research/KNOT-RATION-GAME-20261121-001/media/208304-nae-sensing.gif)

In this replay, five founders grow six new knots before turn 1 and five more before turn 5. On turn 3 the bot senses food at K6, eats its ration, and goes from 4 to 7 energy. It eats six rations in total and dies on turn 28. On independent resets of the same seed, the learner lives 22 turns and the blind bot lives 6. [Seekable movie](/home/jscul/p-vs-np-contact-first/research/KNOT-RATION-GAME-20261121-001/media/208304-nae-sensing.mp4) · [Turn-by-turn record](/home/jscul/p-vs-np-contact-first/research/KNOT-RATION-GAME-20261121-001/replays/208304-nae-sensing.json)

| Scope | Verdict | Held-out result under each law |
| --- | --- | --- |
| Autonomous game | **Successful** | All 2,048 evaluation games reached death |
| Sense food, eat if present, otherwise move | Best mean survival | **17.87 turns** |
| Blind, move then try one meal | Stronger blind baseline | 13.05 turns |
| Reinforcement learner with the food bit | Behind the sensing script | 12.84 turns |
| Blind, choose eat or move at random | Random baseline | 8.29 turns |
| G15 · Learning in a knot pattern | Capability gained | A supplied controller can act on a local read |

The learner trained for 3,072 games on 128 founder structures. Testing used 64 different structures, four matched runs per structure and **256 games per bot per law**. Both laws produced identical growth and play on these starts, including 29 where growth stalled. The sensing script gained 4.82 turns over the stronger blind bot. The learner trailed the sensing script by 5.02 turns. In its 256 parity games it tried to eat on empty knots 878 times and moved away from available food 73 times. [Paired results and 95% intervals](/home/jscul/p-vs-np-contact-first/research/KNOT-RATION-GAME-20261121-001/results.json)

**Replay from a seed** with this command. Change `--seed` for a fresh start, `--law` to `parity` for the other law, or `--bot` to `learner` to play the saved policy. [Game and replay instructions](/home/jscul/p-vs-np-contact-first/research/KNOT-RATION-GAME-20261121-001/README.md)

```sh
.venv/bin/python -B research/KNOT-RATION-GAME-20261121-001/play.py --seed 208304 --law nae --bot sensing --tape 0
```

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Preserve a resettable benchmark | 2/3 | 3/3 | Replay every held-out game → all turns match | Selected · started |
| 2 | Test remembered moves (B159) | 2/3 | 2/3 | Compare matched histories → memory changes a useful action | Alternative · deferred |

**STOP on this comparison.** Replaying all 26,650 held-out turns and retraining from scratch reproduced the game records and model. A memory experiment would need a task where a previous visit changes which move pays. [Verification](/home/jscul/p-vs-np-contact-first/research/KNOT-RATION-GAME-20261121-001/validation.json) · [Scientific referee handoff](/home/jscul/p-vs-np-contact-first/research/KNOT-RATION-GAME-20261121-001/referee_handoff.md)

**Corrections:** None. Scientific referee pending. A repository check still flags an unrelated wording change in the research-directions instructions.  
**Goals:** G15 gained a working moving reader. Learning a hidden knot law from one bit remains open.  
**Assumptions:** A198 fixes the start weighting and growth opportunities before turns 1 and 5. Founders start empty. Energy starts at 6, caps at 10, falls by 1 per turn and gains 4 per meal. All bots choose uniformly among available moves when they move.  
**Scaffolds:** Food, hunger, the sensor, the cursor, its controls, reward and policies are supplied game rules. Ordinary growth supplies the new knots and the shared distinctions the bots actually follow.  
**Basket:** B208 movement and B304 one-bit sensing were used here. B155 and B154 remain open.
