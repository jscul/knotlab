# Play the knot ration game

Every controller plays its own episode to death. Use the repository Python environment from the checkout root. The growth engine needs NetworkX and python-sat. The command-line game itself adds no package dependency. Pillow renders images and the local ffmpeg executable writes MP4.

~~~sh
.venv/bin/python -B research/KNOT-RATION-GAME-20261121-001/play.py --seed 208304 --law nae --bot sensing
~~~

Change the seed to draw another founder tree. Use `--law parity` for even parity. The available bots are `blind` (move first, then try food after every arrival), `random` (blind, balanced eat/move), `sensing` (eat on a positive food bit), and `learner` (the saved greedy Q policy). The optional `--tape 0` controls movement ties and policy randomness independently of the source seed. The same arguments restore the same episode from scratch.

~~~sh
.venv/bin/python -B research/KNOT-RATION-GAME-20261121-001/play.py --seed 208304 --law nae --bot learner --out /tmp/knot-game.json --quiet
.venv/bin/python -B research/KNOT-RATION-GAME-20261121-001/play.py --verify /tmp/knot-game.json --render /tmp/knot-game.mp4 --quiet
~~~

The game starts its cursor on a founder. Founders start empty. There are two opportunities for ordinary growth, before game turns 1 and 5. A funded newborn receives one ration. A single continuously held shared distinction permits one move to its other actual holder. The game supplies anonymous local controls for these moves. The observer has its own energy, previous action and legal controls. The sensing and learned bots also receive the one-bit answer to “food here?” before acting. All global labels and growth records are reserved for the spectator.

A bot starts with 6 energy and capacity 10. Moving, eating and trying to eat on an empty holder each cost 1. Eating a present ration also grants 4 before the final capacity limit. The ration stays gone. Zero energy ends play including the last turn. With a total supply of R newborn rations, every episode ends within 6 + 4R turns. The exact ledger is turns = 6 + 4 × meals − energy discarded at capacity.

The spectator records the actual shared name paid by each parent, every funded birth, both ends of each move, the bit available to the bot, the spent ration and energy before and after every action. A stall stays in the results, with no new food. A supplied game turn is independent of the order in which parent holdings appear.

The learner receives one reward per completed turn. Its training uses the actions it took and the consequences it experienced. It chooses between eating and moving, with a uniform tie among exchangeable movement controls. Tabular Q-learning evaluates actions from their consequences. This experiment adds a matched benchmark on actual knot-grown holdings, with independent initial food ledgers, a founder-isomorphism holdout and seed replay. [Watkins and Dayan, 1992](https://doi.org/10.1007/BF00992698)

For the experimental rules, tested weighting and independent checks, see the [frozen design](preregistration.md) and [scientific decision](decision.md).

## Watch and reproduce the comparison

The [spectator movie](media/208304-nae-sensing.mp4) and [animated replay](media/208304-nae-sensing.gif) follow the same sensing bot through all 28 turns. The view shows all reached knots and actual shared distinctions. Its drawing is available to the spectator alone. Each [turn record](replays/208304-nae-sensing.json) gives the holdings, food bit, action and energy change. The [blind](replays/208304-nae-blind.json) and [learned](replays/208304-nae-learner.json) runs start from independent resets of the same game.

The [held-out results](results.json) give mean and median lifetimes, paired differences and intervals. The [episode ledger](per_episode.csv) records every training and held-out game. The source seed, movement tape, law and policy in any **evaluation** row reproduce it with `play.py`. Training rows used the policy as it learned. To reproduce those, rerun the whole training sequence in a fresh output directory.

~~~sh
.venv/bin/python -B research/KNOT-RATION-GAME-20261121-001/train_eval.py --output-dir /tmp/knot-ration-run
.venv/bin/python -B research/KNOT-RATION-GAME-20261121-001/verify_scores.py
~~~
