# Whole-stage knot certification

The input is the complete ordered supports of each independently grown not-all-equal and parity trajectory. Each support lists the distinctions held by one knot. Every retired support stays in the relation. The checker reads each birth round and verifies the input digest, distinction names, cumulative totals, and the scheduled stage counts. The verified prefix includes round zero and every reached round, including the first complete round exceeding the post-round knot bound. A discarded guard round and any later rounds are outside that prefix.

The tested relation for each knot is the projection of the conjunction of all rules present at that stage onto its own places. All other distinctions are existentially quantified. The verdict checks K1 binding, K2 freedom after each forgetting, and K3 coexistence. For example, a stricter not-all-equal relation can still pass all three tests. The checker does not use equality to the written rule as a general definition of a knot.

## Two ways to recover the exact relations

The first calculation uses the terminal stage and checks every support. If its projection equals the support's own rule, then every earlier projection equals that same rule. The earlier projection contains the terminal one by deletion of whole later rules, and the earlier support's own rule still bounds it from above. When that argument does not give equality, the checker computes the earlier relations separately.

- **Not-all-equal.** The terminal test verifies that every distinction has at most two holders, all supports have at least three places, and every other support retains at least two unpinned places after fixing the target's places. Pin an arbitrary word allowed by the target and remove its rule. Use the incidence graph of the remaining free distinctions to find components for this argument. In a component with an unpinned loose distinction, choose a spanning tree rooted at that distinction's holder. Set the remaining variables arbitrarily. Then satisfy each support in order from the leaves by setting its parent distinction, and satisfy the root by setting its loose distinction. This proves extension for every pinned word.
- **Closed not-all-equal components.** Each knot now has at least two free places. Pair odd-degree vertices by adding temporary edges. Alternate the values along an Euler circuit starting with one of these temporary edges. At most one pair of incident edges in the circuit receives the same value, at the start and finish. That pair contains a temporary edge. Every odd-degree vertex had degree at least three before the added edge, so it has at least one alternating pair of original edges. If there were no odd degrees and some degree is at least four, start there and an alternating pair survives there too. The remaining case is a cycle. An even cycle can alternate. In an odd cycle each knot has two free places and at least one pinned place, since its original arity was at least three. Put the two equal values at one pinned knot and set them opposite to one of its pins. All its rules are then satisfied. The temporary edges serve only in this existence argument.
- **Parity.** For this calculation, represent each distinction with two holders by an edge between them, and connect every loose distinction to one extra vertex through a separate edge. The extra parity equation follows by summing all original equations. Delete the target vertex. Each remaining component requires an even sum of its incident pinned distinctions, by summing its equations. These are the only restrictions. A spanning tree sets all its equations from the leaves inwards, and the even boundary sum settles the root. An iterative depth-first search computes all of these partitions by the intervals it separates at each target. For each target, the exact allowed relation requires even parity separately on each group of the partition.

The second calculation processes the supports in birth order. It independently maintains connected components joined by shared distinctions and counts their loose distinctions. It verifies sole use of each old input and checks that each same-round fresh distinction is held privately. This calculation does not use the terminal overlap condition or terminal cut test.

- The start projections are checked by a SAT solver on their complete initial relation.
- An old component still holding an unpinned loose distinction accepts all assignments to its pins, by the tree construction above. A private fresh distinction in each birth extends any old joint state through that round. Other births cannot restrict the target birth's projection. Under not-all-equal, a birth that fixes all the loose distinctions in an old component instead gets an exhaustive SAT projection at its birth stage. The proof that later rounds preserve it still applies.
- For parity, an old component with every loose distinction fixed imposes one even sum on those pins. A birth with a fresh distinction contributes one sum on the remaining places. A birth without a fresh distinction preserves old states exactly when its inputs are a union of whole old loose sets, under the verified sole-use loose-input condition. This checks implied closing from the actual supports.

If a sufficient condition is unavailable, exhaustive SAT queries determine the exact exceptional projections. The terminal method uses CaDiCaL and the birth method uses MiniSat. Each solver query fixes one whole candidate word and asks whether it extends. The targeted controls independently enumerate all joint states of small systems, including successful and failed implied-closing controls, an odd closed not-all-equal component, extra not-all-equal exclusions that preserve K2 or break K2, and distinctions with more than two holders. A resource stop or a disagreement leaves the affected trajectory unclassified.

## Canonical allowed-state receipts

The exact relations are grouped only by an explicit renaming of places. The canonical tool receives the exact relation as CNF and compares its complete allowed table and K1–K3 verdict to the certificate. Grouping identical relations saves repeated CLI work and leaves the stage count unchanged. The last renamed place is supplied as the contact to the checker. Every place is forgotten in turn under the canonical reading.

Use the stock command `PYTHONPATH=tools python3 -B -m knotlab check --cnf CNF --loops d0 d1 --contact d2 --json`, extending the loop list for a wider relation. The stock receipt run covers widths 3 through 12 under both laws. On this host, a width-12 control took 257 seconds under not-all-equal and 215 seconds under parity before concurrent batch load. The stock checker also calculates minimum clause width by enumerating candidate clauses. At the observed width 15, projecting the stock search cost from the measured width-10, width-11, and width-12 times exceeds the run budget. Stock receipts for those wider relations are outside the timed prefix.

The wide adapter runs the same canonical CLI and knot test on the full allowed table. For a visible CNF it constructs that identical table by enumerating each clause's falsifying assignments and taking their complement. Clauses with existential witnesses use the stock code. The adapter returns minimum width zero for a full relation. For a constrained relation with every single-forgetting projection full, every proper subset is free, so no clause on a proper subset can be implied. A clause per excluded state then gives the exact full width. The remaining minimum-width cases use the stock method. K1, K2, K3 and the other reported fields still run in the original checker. All fields of the wide-adapter receipts are compared to stock at each affordable relation width.

## Replay

From the repository root, run the focused controls with the project virtual environment.

```sh
.venv/bin/python -B experiments/WIDENING-ROSTERS-20261125-001C/WIDENING-ROSTERS-20261125-001C-E001_recount/knot_test/test_certify.py
```

`job.py` uses `scripts/longrun.py` with the producer results and digest-addressed raw supports. `canonical.py` runs the stock receipts. `canonical_wide.py` runs the full allowed-table receipts. The output directories' `job.json` files record source digests, configuration and resource limits. `summarize.py` checks stage totals against both growth implementations and reconciles the exact certificates with both canonical receipt streams.

## Recount result

| Scope | Not-all-equal | Parity |
| --- | ---: | ---: |
| Complete trajectories | 154 | 154 |
| Scheduled stages with totals matching both growth programs | 2,137 | 2,137 |
| Knot verdicts in those scheduled stages | 8,889,286 | 8,889,286 |
| All reached stages, including intermediate stages | 5,843 | 5,843 |
| Knot verdicts in all reached stages | 26,668,466 | 26,668,466 |
| Knots in the terminal stages | 2,682,727 | 2,682,727 |
| Failed, unclassified or discordant verdicts | 0 | 0 |

Intermediate stages have their own cumulative count reconstructed from the support stream and their exact projections checked by both relation methods. For the scheduled stages and the terminal stage of every run, the whole-stage knot totals also agree with the independent growth program. No parity trajectory closed. No birth fixed all the loose distinctions of an old component. Twenty requested stages under each knot law lay past an actual growth stop.

The canonical receipts cover each law at widths 3 through 12 and 15. All reported fields agree with stock for the 20 relations of widths 3 through 12. The width-15 relation occurs eight times under each law. Its complete allowed-state receipt uses the wide adapter. A projected stock cost of at least seven hours per width-15 law from a fivefold growth estimate per extra place exceeds the allowed run budget. The wide receipt run's longest case took 1.36 seconds. The longest complete history certificate took 2.00 seconds with 177.12 MiB peak case memory. [Summary with exact relation classes](../../../../artifacts/WIDENING-ROSTERS-20261125-001C/WIDENING-ROSTERS-20261125-001C-E001_recount/knot_test/summary.json)
