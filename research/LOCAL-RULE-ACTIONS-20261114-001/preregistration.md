# A local agent with independent sight and action reach

Owner's recollection of 2026-11-14 and same-day clarification about looking several logical steps away. This exploratory ticket serves G15 and G16. Frozen before implementation or reward collection.

## Question

Can a reinforcement-learning agent choose a local logical edit from a bounded observation, and does being able to combine nearby rules substitute for seeing farther? One step is between two rules that share a distinction in the supplied chain. The agent is based at one end. Sight and action reach count steps independently on the *current* chain. Equal coordinates, names or labels play no role in defining the neighborhood.

## Prior work in the program

`python3 -B scripts/track.py objects "local rule actions" --until 2026-11-14 --exclude LOCAL-RULE-ACTIONS-20261114-001`

`python3 -B scripts/track.py objects "partially observed reinforcement learning" --until 2026-11-14 --exclude LOCAL-RULE-ACTIONS-20261114-001`

`python3 -B scripts/track.py objects "joined parity copies" --until 2026-11-14 --exclude LOCAL-RULE-ACTIONS-20261114-001`

`LEARN-PARITY-20261111-001` supplies the local parity read in either phase. `SHARED-COUNT-20261111-001` joins such reads through a common distinction. `SEARCH-AUDIT-20261112-001` corrects the interpretation of the earlier search that found and held the local map. `UNDRAWN-LEARN-20261111-001` changes bits and signs by prescribed proposals and repair; `CLAMP-LEARN-20261112-001` compares search against unguided baselines. `GROW-FACE-20261110-001` and `RIGID-WORLDS-20261110-001` concern growth or rigidity. `HIDDEN-COPY-20261112-001`, `ADDR-KNOTS-20261113-001`, `TRUE-RATE-20261113-001` and `PARITY-MIX-20261112-001` concern other copy observations or constraints. The historical CNF routing experiment moved activation on fixed unsigned incidence data. Here a policy receives reinforcement for an actual edit to a signed logical relation.

## Supplied environment and controls

A task gives a target binary phase and starts with three relations of the form `out = in XOR u XOR v XOR phase`. The outside read of one is the next rule's incoming distinction. Local signs and target phase are sampled uniformly. The initial chain, endpoint, visible rule order, action set, candidate relation and reward semantics are supplied. A rule's sign is visible inside sight radius; concealed signs, whole-world states, accumulated sign and a full target lookup are forbidden to the policy. Legal actions may expose the local unsigned structure. The verifier may examine the entire allowed relation.

A terminal action keeps the rules or toggles the phase at the focus, then submits. Toggling any reachable single phase would give the same terminal boundary relation. The only preparatory action combines a pair of adjacent rules when both lie within action reach, replacing them by the exact relation after forgetting their shared distinction. External distinctions are retained. The focus stays at the first surviving rule. At most one preparation is available in the primary comparison. Expose configurable sight, action reach and preparation budget for replay.

Train a tabular Q policy on the three-rule family with terminal correctness reward. Freeze it for assessment at lengths three and four; the latter is unseen in training. At each length exhaust all phase and target combinations. This measures exact rates over a finite panel, and training and assessment overlap at length three. Compare all nine sight/reach settings from zero through two with a random legal-action policy and a task-aware policy that fuses or uses visible phases. Include an untrained or reward-shuffled control. Preserve action choices and training seeds. The evaluator checks the joint allowed boundary relation independently of the policy. An inverted phase or a wrong observer boundary must change a check.

A uniformly hidden sign can reverse the right terminal choice while leaving a restricted observation unchanged. That gives a 50% benchmark wherever it remains hidden after all permitted actions. The primary observable is the fraction of completely correct boundary relations. A gain over blind behavior supports local action selection; equality with the task-aware rule limits the claim to acquiring behavior available to that rule. Nothing here tests autonomous choice of the observation language, the reward, the fusion operation or the task.

Classical background includes [tabular Q-learning](https://doi.org/10.1023/A:1022676722315) and [reinforcement learning with perceptual aliasing](https://cdn.aaai.org/AAAI/1992/AAAI92-029.pdf).
