# Does retaining a complete candidate help?

Post-E001 exploratory follow-up, specified before the new runs. The first reward-fitted method returned an exact answer in 2/18 chosen context and seed combinations and its blind comparator in 5/18. Ordinary size-ordered enumeration found all six exact minimal-width encoders. One possible obstacle in the first policy search is that it resamples instruction positions independently and its elite tie rule favors small live programs. This comparison tests a different search procedure. An observed change cannot by itself attribute the cause to either feature.

Reuse E001's signed source hash, gate tokens, two widths, scoring, decoder, frozen seeds, train and held-out rows, and best-program reporting rule. Each method gets 96 candidates for each of 128 generations. The initial population must be identical to E001. Divide it into 12 groups of eight. Retain one parent per group. At each subsequent generation propose eight new programs per group. With probability 1/8 draw a fresh uniform program. Otherwise mutate one of the four token positions (probability 3/4) or two distinct positions (1/4). At a mutated position, choose with equal probabilities a fresh token or one changed field of that token (gate operation, operand, or emitted register). All programs execute only the same elementary gates. No target-dependent operator, example, gate reward, pair label or pretrained fragment is introduced.

Reward-guided groups choose a parent from the old parent and current offspring by maximum terminal training correctness, resolving ties uniformly. Neutral groups choose a parent uniformly from the identical kind of pool. Both use the same retention rule from E001 to report the best among every scored proposal and to select the emitted width from training. The neutral control can find and keep a correct answer by chance. Match initial populations, proposal counts, alphabets, perturbation probabilities, and budgets. Record the selected programs and decoder for each width and context, all search trajectories, first exact samples, and final exhaustive results. Freeze before scoring the 32 withheld worlds.

Compare exact and exact-minimal-width counts against this matched control, along with the two earlier methods. All results remain exploratory. Stop here even if the follow-up fails. The earlier six contexts are familiar in both studies. A further independent question is whether one policy learns to choose a pair from a visible change of connections to a new consumer.

## Prior work in the program

`python3 -B scripts/track.py objects "learning logical variable elimination order" --until 2026-11-14 --exclude ATOMIC-FOLD-20261114-001`

The direct evidence is this ticket's E001. `SEARCH-AUDIT-20261112-001` calls for a matched blind search. `PIN-RULE-20261112-001` and `HIDDEN-COPY-20261112-001` concern different substitution and observation tasks.
