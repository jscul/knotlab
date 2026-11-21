# Independent scientific review of the funded and unguarded clock

The claims to adjudicate are the all-turn donor formula, the common-birth-70 comparison on the guarded clock, and two distinct finite counterfactuals under unguarded growth. The prospective advisor reviewed the design before observations. Independent scientific review of the results is pending. [Exact design and review disposition](preregistration.md) · [Statement and proof](../../proofs/TICK-BIRTHS-AND-SCARCITY-20261121-001B/TICK-BIRTHS-AND-SCARCITY-20261121-001B-P001_funded_ticks/proof.md) · [Results](results.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — competition at two clock parents | **Status:** Successful, pending referee | Each parent has exactly $j$ consumer children at turn $j$ |
| Local direction — raw loss | Two finite mechanisms | A required ancestor can exhaust both its parents, or an earlier larger child can exclude the pair |
| Broader exploration — clocks in ordinary growth | Known alternatives | Guarded and raw histories answer different questions |
| G5 Dynamics | Capability gained | Event-cost and funding can be tested separately |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Directly consume a raw turn's last required slot | 3/3 — identifies a cause of scarcity | 2/3 — funding controls available | Match initial supply from the originals → an outside last-slot loss or an obstruction | Selected · awaiting go-ahead |
| 2 | Additional funded turns | 1/3 — extends finite coverage | 3/3 — identified formula | Replay the next turn → agreement or a first exception | Alternative · deferred |

**Corrections:** None.  
**Goals:** B262 meets its stop for G5 Dynamics.  
**Assumptions:** A168 records the supplied originals, mark, orders, and serial readings.  
**Scaffolds:** Preparation, tie rule and observation boundary were varied as set out in the design. Both laws use physical input slots.

## Checks that could overturn the conclusion

1. Rebuild the marked parents at age $4j+2$ by the actual cluster deletions. Count all extensions which contain the attached holder; check the outside end positions and whether two positions could give the same child after identification. A duplicate or omitted extension would change the claimed $j$.
2. Independently sum the physical births at positive depths 1–10. Check that the bare clock always has one turn at event 70 and that the next level that could contain the other two first turns has yet to start at that event. Test separately the counts immediately before and after a selected tick. At the first and second tick, swap a consumer onto the same physical slot the tick could use; verify the residual slots and the incidences after both orders.
3. Replay the first 14 ascending unrestricted births from each original. Discard the proposed scorer labels and match true input sets. Determine whether the two parents of the blocked age-three role (events 10 and 12) can ever be replaced. The first turn's unique unary has exhausted its original and the remaining landed roles have at least two parents. A matching alternative lineage would defeat the loss result. Trace the 20-event same-continuation history and check whether any of it used the new holder. State separately whether the marked role was recognizable from the chronological writes.
4. On each reached restart apply the completely unguarded rule, recomputing groups and immutable demand at every individual write. Check the positive exact firing and all four steps to the prior-common-child certificate, at both turns, on both laws and under both policies. A temporarily absent candidate alone does not prove a permanent loss. A restart does not prove raw reachability of the prepared cut from the original. The three outcomes on historical priority choices carry no population weighting.
5. Challenge the input-projection, source-recognition and fairness hypotheses. The guard takes the supplied originals. Raw fairness of unrestricted runs and filtered fairness under joins-first have distinct continuation arguments. The proof of all-size expenditures uses the earlier identification theorem. The finite replays do not establish it.

The script below independently reads the physical receipts and reconstructs the current serial rosters without importing the original producer or either new replay. The prospective design and check scripts belong to the same study. External novelty was not assessed.

```sh
t=TICK-BIRTHS-AND-SCARCITY-20261121-001B
.venv/bin/python -B "proofs/$t/${t}-P001_funded_ticks/check.py"
set -o pipefail
PYTHONHASHSEED=7 .venv/bin/python -B "experiments/$t/${t}-E001_serial/replay.py" |
  cmp - "artifacts/$t/${t}-E001_serial/receipt.json"
PYTHONHASHSEED=7 .venv/bin/python -B "experiments/$t/${t}-E001_serial/raw.py" |
  cmp - "artifacts/$t/${t}-E001_serial/raw.json"
```

The guarded replay took 46 seconds with 56,348 KiB peak resident. The raw replay took 52 seconds with 122,796 KiB peak resident. Alternate hash-seed replays gave identical receipts. The checker validated 396 raw writes, 24 reached-cut positive firings, 24 reached-cut loss certificates, all 24 from-original outcomes and 40 independent complete-level counts per law. Its wrong-parent control rejects an attempted exact pair in place of the fourth, larger birth of the first attached loss. [Checker](../../proofs/TICK-BIRTHS-AND-SCARCITY-20261121-001B/TICK-BIRTHS-AND-SCARCITY-20261121-001B-P001_funded_ticks/check.py) · [Raw receipt](../../artifacts/TICK-BIRTHS-AND-SCARCITY-20261121-001B/TICK-BIRTHS-AND-SCARCITY-20261121-001B-E001_serial/raw.json) · [Guarded receipt](../../artifacts/TICK-BIRTHS-AND-SCARCITY-20261121-001B/TICK-BIRTHS-AND-SCARCITY-20261121-001B-E001_serial/receipt.json)
