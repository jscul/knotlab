# Can a local agent reuse the same action twice?

This exploratory design was recorded after the nine-cell sight and action comparison and before running the new comparison. The first experiment found that a learned policy with sight one and action reach one could fuse once and solve every three-rule start. Four-rule starts under that same one-fold budget retained a hidden sign. At sight two and positive reach the hand-written local policy could solve the four-rule starts in one fold, while the fitted table still gave 50%.

Keep sight and reach at one. Replay the three original training seeds at length three and verify the fitted Q digests against E001. After training, keep the same table and give it either the remaining preparation count or one bit saying whether any preparation is available. These views are identical on every training state. This bit is a representation chosen for the experiment. The environment still enforces the full count. Compare one allowed fold with up to two folds at length four and three folds at length five. All three- through five-rule phase and target settings are evaluated, with seeds coupled across comparators. The chain length and hidden phases are absent from the policy.

Record whether a reached table key was present in training and how many folds the policy actually took. Check the projected allowed relation using the unchanged join-and-forget scorer. Compare both learned views with the same hand-written and blind controls as the first experiment. A gain confined to the bit view would distinguish failure to reuse the same local state when a counter changes from having too few allowed steps. A tie or reversal is an equally valid outcome. Training on a new logic, learning a new operation, and improving the learning procedure require separate tests.

## Prior work in the program

`python3 -B scripts/track.py objects "repeated local rule" --until 2026-11-14 --exclude LOCAL-RULE-ACTIONS-20261114-001`

`python3 -B scripts/track.py objects "policy length generalization" --until 2026-11-14 --exclude LOCAL-RULE-ACTIONS-20261114-001`

The direct comparison is this ticket's E001 agent, trained to take a single local action. The first search also found `NEST-COUNT-20261112-001` on repeated local constraints, `RIGID-WORLDS-20261110-001` on radius-limited views and `GROW-FACE-20261110-001` on rules for extending a pattern. The second matched length studies `LOOP-LOCK-20261112-001` and `CHEAP-COUNT-20261112-001`. The present question concerns reuse of the identical fitted policy table under a change in chain length.
