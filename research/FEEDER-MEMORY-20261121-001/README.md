# Play the feeder-memory game

A feeder is a knot born during ordinary growth. It starts with one ration and continues to signal after that ration is eaten. The bot receives one action bit. ON attempts a meal. OFF moves through an actual shared distinction using the original uniform movement control. Founders never signal. The energy charge, two growth opportunities, source weighting, movement and death at zero come from the [previous resettable game](../KNOT-RATION-GAME-20261121-001/README.md). The [design](preregistration.md) lists every addition.

## Replay the reciprocal experiment

Run the following from the repository root using its Python environment. It rebuilds the two histories from their founder seed and movement tape under each law. At the decision it executes the original and sham reads and the reciprocal memory exchanges before any cloned game advances. It checks the prepared knots, local observations, physical actions and post-action consequences against the saved record.

~~~sh
.venv/bin/python -B research/FEEDER-MEMORY-20261121-001/interventions.py --verify research/FEEDER-MEMORY-20261121-001/decisive_replays.json
~~~

The decisive record has one pair per law. Each `pair` contains both public histories, its source seed, tape and scheduled eat turns. All unspecified earlier actions were passes. Each `branches` entry separates the actual game state reserved for the spectator from what the bot saw. The `arms` give both action marks and the actual next move or eat on each unchanged game. Raw guard offers and refusals are included for the decisive reads. The rest of the paired interventions have a [compact ledger](intervention_rows.json.gz).

Watch the [animated paired replay](media/feeder-memory.gif) or the [seekable movie](media/feeder-memory.mp4). Each shows the same decisions under parity and not-all-equal. To play the full-stock preparation from its original seed, use the command below. Use `000001100` in place of `001001000` for the depleted preparation. Drop `--prefix` and its value to let the keeper play from turn one, or change the seed for a fresh start.

~~~sh
.venv/bin/python -B research/FEEDER-MEMORY-20261121-001/play_feeder.py --seed 15776084479232194445 --tape 7224311483179669286 --law nae --reader keeper --prefix 001001000
~~~

The full held-out comparison can also be regenerated in a new directory.

~~~sh
.venv/bin/python -B research/FEEDER-MEMORY-20261121-001/survival_eval.py --output-dir /tmp/feeder-scores
~~~

## What each reader has

The current reader sees feeder membership, its energy, last actual action and the local menu. Complete local history adds the outgoing anonymous slot of every previous move and the observable energy change on each attempt. The [public certificate](public_certificate.md) recognizes some definite returns and excludes some previous meal holders. It returns unknown when its own rules leave possible aliases. The offline comparison may inspect the true holdings to score the decision. No policy receives these holdings.

The keeper is a prepared bot-side memory knot, a coupling knot and a separate action knot. The writer accepts only the same public inputs and consequences. It stores whether the most recent successful meal was paid at a one-control or multiple-control feeder. Its fixed decision turns ON at a feeder whose menu type differs from the last paid type or when memory is ready. It passes matches. Different feeders can have the same type. Every emit comes from the same actual distinction in the action knot. [Device design](keeper_design.md) · [Local exchange implementation](keeper.py)

Remembering a sequence of observations and actions is standard in partially observable decisions. The contribution here is a concrete pair of lawful game histories, a locally written memory, and reciprocal interventions on that memory with an unchanged one-bit readout. [Kaelbling, Littman and Cassandra, 1998](https://www.cassandra.org/arc/papers/aij98.pdf)

## Check the finite history panel

The [results](history_results.json) give every denominator, including incompletely distinguished visits. The [unique-prefix pairs](history_pairs.json.gz) are indexed by source, gameplay tape, renaming, decision and the earlier eat attempts. The [direct replay](history_verify.py) reconstructs the original action schedules. The [separate source checks](source_checks.json) verify local projections of the actual grown network under the declared law. See the [scientific decision](decision.md) and [referee handoff](referee_handoff.md).
