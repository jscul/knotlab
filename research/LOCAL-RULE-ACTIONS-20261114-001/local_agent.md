# How far can a local agent see and act on logic?

On November 14, 2026 the owner recalled a reinforcement-learning agent sketched in the handwritten notebooks lost in the Palisades fire. The agent occupied a local context, saw atomic pieces of logic, and could act on a rule or a combination of nearby rules. The owner remembered trying to realize the idea spatially and suggested independently varying how many logical steps the agent sees and how many it can act across. November 14 dates this recollection. The original sketch's date is unknown. [Public timeline](https://prespatial.org/timeline)

## What survived

| Date | Source | What it establishes |
| --- | --- | --- |
| September 3, 2024 | Git `0deacb42e`. [Initial notebook](../../archive/dissonance/initial_research.ipynb) · [3-D Q learner](../../archive/dissonance/torch_qlearner_3d_space.ipynb) | The notebooks use coordinate vectors, learned movement and nearby stored vectors as memory. Nearness has a geometric meaning in this implementation. |
| January 2025 (approximate) | [October 30, 2026 historical account](../../docs/provenance/2026-10-30/sources/JOURNEY-RETROSPECTIVE.txt) | The two handwritten graph-paper notebooks were lost in the fire. Digital Jupyter notebooks survived in Git. The exact day of the personal loss is unverified. |
| March 10, 2026 | Git `2e616b2a3`. [Pair-graph PPO notebook](../../archive/p-vs-np/experiments/02_pair_graph_ppo.ipynb) · [Environment](../../archive/p-vs-np/experiments/pvsnp_mvp.py) | A reinforcement-learning agent edits a weighted Boolean formula, including literals and clauses. Its observation includes whole-formula statistics. |
| April 3, 2026 | Git `d92bb3f74`. [Pair versus variable notebook](../../archive/p-vs-np/experiments/30_cnf_pair_vs_variable_agents.ipynb) · [Routing implementation](../../archive/p-vs-np/experiments/cnf_agent_routing.py) · [Minimal loop agent](../../archive/p-vs-np/experiments/37_minimal_loop_agent_rl.ipynb) | A variable or a pair of variables shared by clauses can act as an agent. The action passes activation to a neighbor in a fixed graph. The policy can also observe the total mass at its goal. |
| November 14, 2026 | Owner's direct recollection, followed by the clarification about logical steps | The new experiment below combines a locally limited observation with an edit to the represented logic. This reconstruction makes operational choices that the surviving sources leave open. |

The three exact implementation dates come from the original commits, whose author and committer dates agree. All three fall on the same respective dates in Pacific time. The later archive import preserved the notebook code. [Archive provenance](../../archive/README.md)

## A step, a view and an action

In this reconstruction the agent stays at the first rule. Each rule takes three binary inputs and allows their parity, optionally flipped, at its output. That output is the next rule's first input. This family uses the parity read found in Lesson 4.7. The start and visible order of the rules are supplied. [Lesson 4.7](https://prespatial.org/intuitions/knots-alone) · [Source-search audit](../SEARCH-AUDIT-20261112-001/search_audit.md)

One step reaches a rule sharing a distinction with the current rule. Radius zero includes the focused rule. Radius one also includes its neighbor. The sight radius controls which rule signs are visible. The action radius controls which adjacent pairs can be combined. A third setting controls how many combinations are permitted before submission. A combination replaces the pair by all assignments to its outside distinctions that can be extended through the shared bit. Remaining steps are counted on the resulting rules. This supplied operation preserves the entire allowed outside relation and can bring a previously unseen sign into view.

The target tells the agent which overall parity is wanted. It can keep the current rules or flip the first sign and submit. It receives reward one exactly when the resulting relation on *all* outside inputs and the final output matches the target. The scorer actually joins the allowed rows, forgets internal bits, and compares the two whole relations. A complete matched relation counts as one successful start.

## The first comparison

Each policy trained by tabular Q-learning on 6,000 uniformly sampled three-rule starts per seed. We froze it and checked every possible set of signs and target at lengths three and four, for seeds 17, 31 and 53. The first family has 16 distinct starts and overlaps training. All 32 four-rule starts have an unseen length. At most one combination was allowed in this comparison. Each seed gave the displayed rate independently.

| Steps of sight | Steps of action reach | Trained agent, 3 rules | Trained agent, 4 rules | Hand-written local policy, 4 rules |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 50% | 50% | 50% |
| 0 | 1 | 50% | 50% | 50% |
| 0 | 2 | 50% | 50% | 50% |
| 1 | 0 | 50% | 50% | 50% |
| 1 | 1 | 100% | 50% | 50% |
| 1 | 2 | 100% | 50% | 50% |
| 2 | 0 | 100% | 50% | 50% |
| 2 | 1 | 100% | 50% | 100% |
| 2 | 2 | 100% | 50% | 100% |

At sight one and reach one, each trained policy first combined rules on all 16 three-rule starts. For example, suppose the signs are `0,1,0` or `0,1,1` and the target phase is zero. Initially both show `0,1`. Combining the first two leaves `1,0` or `1,1` in sight. The trained agent flips for the first and keeps for the second. At reach zero the original observations are identical and require opposite submissions. Each uniformly hidden sign pairs a correct guess with a wrong one, which accounts for the exact 50% in that setting.

The hand-written policy combines adjacent rules when it can and a sign is still hidden. It otherwise chooses from the visible parity. It matched the trained policy at length three. At length four with sight two and positive reach it solved all 32 starts. In that configuration three-rule training always initially exposed the end of the chain. The learned table had never seen a three-sign initial observation with a further rule beyond it. Uniform random actions and an unfitted Q table both scored 50% in every cell.

The semantic checks cover all 24 possible initial sign patterns across both lengths and all 64 possible first adjacent combinations thereof. Each combination preserved the entire outside relation. Flipping one sign changed that relation to its complement. Reading the wrong output changed 128 allowed boundary states in a three-rule case, and corrupting a local table entry while retaining its displayed sign changed 32. [Frozen design](preregistration.md) · [All runs and action histories](../../artifacts/LOCAL-RULE-ACTIONS-20261114-001/LOCAL-RULE-ACTIONS-20261114-001-E001_local_policy/results.jsonl)

From the research checkout, this command fits the three seeds and checks both lengths for the chosen radii. Change `--sight`, `--action` and `--preparations` independently.

```sh
.venv/bin/python -B experiments/LOCAL-RULE-ACTIONS-20261114-001/LOCAL-RULE-ACTIONS-20261114-001-E001_local_policy/job.py --sight 1 --action 1 --preparations 1
```

## Can the learned action repeat?

The first test limited the agent to one combination. A separate exploratory follow-up kept sight and action reach at one and replayed the **identical three fitted tables**. Every fit had 16 observed local states with 40 action values, trained exclusively on three-rule chains. At that length one allowed combination was sufficient. During training the remaining-action count was always 0 or 1.

For longer chains we changed two things independently. The environment could permit more combinations. The policy could see either the exact number remaining or a single bit saying whether another combination was available. Both ways of reporting the count addressed exactly the same table entries throughout training. The observation change was chosen by the investigator. All remaining signs, structural information, actions, rewards and learned values were held fixed. [Follow-up design](repeated_fold_design.md)

| Rules | Folds allowed | Learned, exact count | Same table, availability bit | Hand-written | Random |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 1 | 48/48 | 48/48 | 48/48 | 24/48 |
| 4 | 1 | 48/96 | 48/96 | 48/96 | 48/96 |
| 4 | 2 | 80/96 | 96/96 | 96/96 | 48/96 |
| 5 | 1 | 96/192 | 96/192 | 96/192 | 96/192 |
| 5 | 3 | 96/192 | 192/192 | 192/192 | 96/192 |

The denominators aggregate the same 16, 32 or 64 distinct starts over the three training seeds. With enough folds, every decision under the availability view reached a table entry already fitted on three rules. Each policy used two folds on every four-rule start and three folds on every five-rule start. No parameter or Q value changed during evaluation. The random and untrained policies gave identical results. The unchanged verifier checked 192 possible first pair combinations across lengths three through five and compared each submitted final relation against the target.

For example, on five rules with signs `0,1,0,1,1` and target zero, one trained policy saw `0,1`, folded the two rules, saw `1,0`, folded again, then saw `1,1` and folded a third time. Finally it saw `0,1` and the end of the chain and flipped the sign. Each fold kept every allowed assignment to the outside distinctions. What moved into sight on the next decision was the next rule together with the combined effect of all the rules already folded.

The exact-count runs encountered untrained entries for counts two and three. Ties there were resolved at random. A separate calculation averaged **all** ties as well as all starts, using the signed-parity law to check the outcome independently of the row-joining scorer. Every fitted policy with enough actions had exact success probability 2/3 at length four and 5/9 at length five with the numeric count. With the availability bit each had probability one at both lengths. With only one fold both had probability one half on both longer lengths. The difference between the sampled and averaged count-view rates reflects the shared random stream within each seed. [Exact tie calculation](check_reuse.py) · [All follow-up runs](../../artifacts/LOCAL-RULE-ACTIONS-20261114-001/LOCAL-RULE-ACTIONS-20261114-001-E002_repeated_fold/results.jsonl)

This isolates a transferable learned choice in a small family. The agent used the same local observations to decide when to fold again and when to submit. We supplied the parity family, a fixed starting point, the neighborhood, an indicator that the end was visible, the two budget encodings, the exact fold operation and the reward. Developing a suitable fold, moving the point of view, reasoning with a wider variety of rules, and improving the learning procedure itself are open questions. The hand-written local policy solved the same tasks with zero training. Exact folds here can increase the number of rows in a stored truth table. The measured gain concerns which information is within reach and which local policy entries can be reused. Compute savings would need their own comparison. [Related transfer test with two possible reads](../FOLD-TRANSFER-20261114-001/transfer.md)

The first command checks the fitted policies and integrates over all ties. The second recomputes one seed with the original relational scorer. The compact output includes every cell's score. Omitting `--smoke` also prints each action history.

```sh
.venv/bin/python -B research/LOCAL-RULE-ACTIONS-20261114-001/check_reuse.py
.venv/bin/python -B experiments/LOCAL-RULE-ACTIONS-20261114-001/LOCAL-RULE-ACTIONS-20261114-001-E002_repeated_fold/job.py --seed 17 --smoke
```
