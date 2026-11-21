# Scientific referee handoff for the last-slot comparison

Please adjudicate the finite two-history witness and the accompanying first-outside-birth exclusion. The positive claim concerns the first marked turn read from its complete chronological ancestry. The losing payment uses the attached original as a direct parent and strikes an original needed by an ancestor of the mark. The prospective advisor has already reviewed the experimental design. Independent scientific referee review of the result is pending. [Main statement and proof](../../proofs/LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001A/LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001A-P001_outside_spend/proof.md) · [Design and objection](preregistration.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — matched last-slot spending | **Status:** Successful, referee pending | The same named slot funds mutually exclusive births |
| Local direction — raw clock ancestry | One marked ancestor is obligatory | Every realization requires the unmade pair on originals 4 and 6 |
| Broader exploration — outside spending | Known alternatives | A two-slot comparison permits both the expense and the turn |
| G5 Dynamics | Capability gained | A true outside parent causes a permanent clock loss |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | An outside descendant spends directly at a born tick parent | 3/3 — tests the established clock at its own turn | 2/3 — roles known, common prefix to find | Reach both tick parents raw → direct last-slot fork or class obstruction | Selected · awaiting go-ahead |
| 2 | Other source placements with a source-pair loss | 1/3 — checks robustness | 3/3 — concrete variants available | Alter placement → first change or confirmation | Alternative · deferred |

**Corrections:** None.  
**Goals:** B282's direct stop for G5 is reached.  
**Assumptions:** A170 records the identical-source fork and reader.  
**Scaffolds:** The earlier eight-original clock, one prepared attachment, the extra pure expense, and the chosen raw orders. Slot renaming and omitting the expense were checked.

## Questions for independent reconstruction

1. Construct the first marked ancestry from the original eight-knot clock. Verify that every candidate realization, including reversal and a different source-0 unary, needs an exact child on the named originals 4 and 6. Check every previous child of 4 and the rival itself. A preexisting payment or an admissible physical substitute defeats the permanence argument.
2. Reconstruct the raw candidate and priority pools before each of the nine common events and both branches. Check both source projections, current true parents, named inputs, immutable fresh outputs and allowed-state extension. Show that both birth-10 choices are allowed, that the losing birth is genuinely funded by the attached original, and that it leaves no earlier child containing both 4 and 6.
3. Reconstruct the entire twenty-role directed ancestry at comparison birth 21. Replay a treatment suffix through the same count. Repeat without the common ninth expense, using the same outside parents and the same named inputs. Confirm that the remaining slot then pays for the necessary child and the same twelve subsequent parent choices complete the turn.
4. Check the alternative disjoint expense and state exactly what its unfinished clock-role enumeration permits. The previous reached-cut larger child with slots remaining should reject as a last-slot witness. An outside expense at a donor with two remaining slots should also reject. The raw source, current loose budgets and marked ancestry are shared across the main fork.
5. Audit the uniqueness and nonvacuity of the first-outside-spend theorem. Identify the attached original's only witness, every source clock donor it can reach through that witness, the two paid clock children at each, and the absence of a positive-age pure donor meeting original 3. Verify at least one actual outside expenditure is admitted in this class.
6. Compare unrestricted fairness with filtered fairness under joins-first. Trace the common initial unary separately from the two equal-priority fork actions. The witness proves the possibility of a last-slot loss without introducing a frequency over fair histories.

```sh
t=LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001A
set -o pipefail
PYTHONHASHSEED=7 .venv/bin/python -B "experiments/$t/${t}-E001_last_slot/search.py" |
  cmp - "artifacts/$t/${t}-E001_last_slot/witness.json"
.venv/bin/python -B "proofs/$t/${t}-P001_outside_spend/check.py" |
  cmp - "artifacts/$t/${t}-E001_last_slot/counterfactuals.json"
```

The search took under a second and peaked at 61,844 KiB. It visited the twenty historical prefixes before trying common preparations. The witness turned up after 41 of the one-preparation options had been tried. These counts describe the executed search. The mathematical scope comes from the physical certificate and the separate all-order argument. [Full result](results.md)
