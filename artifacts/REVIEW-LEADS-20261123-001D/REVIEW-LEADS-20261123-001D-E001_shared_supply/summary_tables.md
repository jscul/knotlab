### Joint starts

| start | class | X + Y | knots | donor | loose s=0 / s=1 | demand X + Y | first asks in the sources' own histories | first parent step of the joint plan that asks it |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| S1 | same-step | R0 + R0 | 15 | 4 | 4 / 3 | 2 + 2 | 1 / 1 | 1 / 1 |
| S2 | same-step | R5 + R5 | 125 | 57 | 6 / 5 | 3 + 3 | 6 / 6 | 1 / 1 |
| T1 | staggered | R0 + R5 | 70 | 4 | 5 / 4 | 2 + 3 | 1 / 6 | 1 / 1 |
| T2 | staggered | R5 + R9 | 197 | 57 | 7 / 6 | 3 + 4 | 6 / 10 | 1 / 1 |
| T3 | staggered | R0m + R5 | 70 | 0 | 6 / 5 | 3 + 3 | 1 / 6 | 1 / 1 |

### Branches by outcome (counts of choice sequences; a source is `lost` if any registered tick has a loss certificate)

| start | s | rule | choice sequences | X keeps, Y keeps | X lost, Y keeps | X keeps, Y lost | both lost | stalled |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 | 0 | guarded | 1 | 1 | 0 | 0 | 0 | 0 |
| S1 | 0 | recompute unrestricted | 1 | 1 | 0 | 0 | 0 | 0 |
| S1 | 0 | recompute joins_first | 1 | 1 | 0 | 0 | 0 | 0 |
| S1 | 1 | guarded | 1 | 0 | 0 | 0 | 0 | 1 |
| S1 | 1 | recompute unrestricted | 24 | 0 | 12 | 12 | 0 | 0 |
| S1 | 1 | recompute joins_first | 24 | 0 | 12 | 12 | 0 | 0 |
| S2 | 0 | guarded | 1 | 1 | 0 | 0 | 0 | 0 |
| S2 | 0 | recompute unrestricted | 1 | 1 | 0 | 0 | 0 | 0 |
| S2 | 0 | recompute joins_first | 1 | 1 | 0 | 0 | 0 | 0 |
| S2 | 1 | guarded | 1 | 0 | 0 | 0 | 0 | 1 |
| S2 | 1 | recompute unrestricted | 720 | 240 | 240 | 240 | 0 | 0 |
| S2 | 1 | recompute joins_first | 720 | 240 | 240 | 240 | 0 | 0 |
| T1 | 0 | guarded | 1 | 1 | 0 | 0 | 0 | 0 |
| T1 | 0 | recompute unrestricted | 1 | 1 | 0 | 0 | 0 | 0 |
| T1 | 0 | recompute joins_first | 1 | 1 | 0 | 0 | 0 | 0 |
| T1 | 1 | guarded | 1 | 0 | 0 | 0 | 0 | 1 |
| T1 | 1 | recompute unrestricted | 120 | 24 | 48 | 48 | 0 | 0 |
| T1 | 1 | recompute joins_first | 120 | 24 | 48 | 48 | 0 | 0 |
| T2 | 0 | guarded | 1 | 1 | 0 | 0 | 0 | 0 |
| T2 | 0 | recompute unrestricted | 1 | 1 | 0 | 0 | 0 | 0 |
| T2 | 0 | recompute joins_first | 1 | 1 | 0 | 0 | 0 | 0 |
| T2 | 1 | guarded | 1 | 0 | 0 | 0 | 0 | 1 |
| T2 | 1 | recompute unrestricted | 5040 | 2880 | 1440 | 720 | 0 | 0 |
| T2 | 1 | recompute joins_first | 5040 | 2880 | 1440 | 720 | 0 | 0 |
| T3 | 0 | guarded | 1 | 1 | 0 | 0 | 0 | 0 |
| T3 | 0 | recompute unrestricted | 1 | 1 | 0 | 0 | 0 | 0 |
| T3 | 0 | recompute joins_first | 1 | 1 | 0 | 0 | 0 | 0 |
| T3 | 1 | guarded | 1 | 0 | 1 | 0 | 0 | 0 |
| T3 | 1 | recompute unrestricted | 1 | 0 | 1 | 0 | 0 | 0 |
| T3 | 1 | recompute joins_first | 1 | 0 | 1 | 0 | 0 | 0 |

### Predictions

P1 (s = 0, no source loses a tick in any branch): guarded: 0 of 5 branches with a loss or stall; recompute unrestricted: 0 of 5 branches with a loss or stall; recompute joins_first: 0 of 5 branches with a loss or stall.

P2 (s = 1, staggered starts T1, T2, T3: the earlier asker X keeps ticking in every branch):

| start | rule | branches | X lost | X lost and Y keeps (the failing clause) | X keeps in every branch |
| --- | --- | ---: | ---: | ---: | --- |
| T1 | guarded | 1 | 1 | 0 | no |
| T1 | recompute unrestricted | 120 | 48 | 48 | no |
| T1 | recompute joins_first | 120 | 48 | 48 | no |
| T2 | guarded | 1 | 1 | 0 | no |
| T2 | recompute unrestricted | 5040 | 1440 | 1440 | no |
| T2 | recompute joins_first | 5040 | 1440 | 1440 | no |
| T3 | guarded | 1 | 1 | 1 | no |
| T3 | recompute unrestricted | 1 | 1 | 1 | no |
| T3 | recompute joins_first | 1 | 1 | 1 | no |

P3 (s = 1, same-step starts S1, S2: both outcomes occur among the branches):

| start | rule | branches | X lost, Y keeps | Y lost, X keeps | both keep | both outcomes occur | every branch ends the same source |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| S1 | guarded | 1 | 0 | 0 | 0 | no | no |
| S1 | recompute unrestricted | 24 | 12 | 12 | 0 | yes | no |
| S1 | recompute joins_first | 24 | 12 | 12 | 0 | yes | no |
| S2 | guarded | 1 | 0 | 0 | 0 | no | no |
| S2 | recompute unrestricted | 720 | 240 | 240 | 240 | yes | no |
| S2 | recompute joins_first | 720 | 240 | 240 | 240 | yes | no |

### Guarded rule, shortfall 0: births at which each registered tick is made (cap 400)

| start | X tick 6 | X tick 10 | Y tick 6 | Y tick 10 |
| --- | --- | --- | --- | --- |
| S1 | birth 395 (step 6) | not reached within the caps | birth 396 (step 6) | not reached within the caps |
| S2 | birth 1 (step 1) | birth 251 (step 5) | birth 2 (step 1) | birth 252 (step 5) |
| T1 | birth 320 (step 6) | not reached within the caps | birth 1 (step 1) | birth 193 (step 5) |
| T2 | birth 1 (step 1) | birth 353 (step 5) | none registered | birth 7 (step 1) |
| T3 | birth 382 (step 6) | not reached within the caps | birth 1 (step 1) | birth 227 (step 5) |


