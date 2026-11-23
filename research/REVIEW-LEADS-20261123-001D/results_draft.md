# Sources that share one supply: draft result

Ticket `REVIEW-LEADS-20261123-001D`, experiment `REVIEW-LEADS-20261123-001D-E001`, 23 November 2026. Draft by the implementing sub-agent; analysis and verdict belong to the thread. Referee pending. Code: `experiments/REVIEW-LEADS-20261123-001D/REVIEW-LEADS-20261123-001D-E001_shared_supply/`. Outputs: `artifacts/REVIEW-LEADS-20261123-001D/REVIEW-LEADS-20261123-001D-E001_shared_supply/`. Readings and omissions: `deviations.md` in the code folder. The construction addendum was hashed (sha256 `245a07ebaf79ee6dcc3ef88f6fdc54f5efe61d00aba290283192e067894f3be1`) before any joint start was grown, apart from one scratch ordinary growth disclosed in the addendum.

## What the study found

Only the clock of the scarcity study has a recorded tick inside the frozen horizon, so every joint start joins two copies of that clock (the eight-knot ring with one spare; ticks at parent steps 6 and 10), sharing one donor knot. Merging two original ring knots leaves four cross proposals unfunded and the first parent step stalls; merging at a knot whose neighbours on one side are spent creates no cross proposal. With the donor short by one loose distinction, the guarded rule stalls the whole start (nothing is written) except where the shortage is the donor's unary birth, which the ordinary plan drops silently; the recompute-after-every-birth rule starves exactly one proposal through the donor, and every proposal is starved in the same number of choice sequences. The earlier asker in the sources' own histories loses in 48 of 120, 1,440 of 5,040 and 1 of 1 recompute branches (starts T1, T2, T3 below), so asking first does not protect a source in these starts. The one start in which every branch ends the same source (T3) is the one whose tick needs a unary birth of the donor.

## Population and gates

| source | start | alone, ordinary growth | alone, guarded rule | alone, recompute rule (`unrestricted` pool) |
| --- | --- | --- | --- | --- |
| R0: the ring clock from its original knots | 8 knots | ticks at steps 6 and 10 (70 and 151 births at those cuts, as recorded) | ticks at births 56 and 128 | first tick made (20 births, 1,797 states, replayed through the archived `apply` under both laws); second tick undecided at 20,000 states |
| R5: the ring after 5 parent steps | 63 knots | ticks at steps 1 and 5 from the stage | births 1 and 73 | first tick made (1 birth); second tick: no firing order among births that are roles of its ancestry (193 states) |
| R9: the ring after 9 parent steps | 135 knots | tick at step 1 | birth 1 | tick made (1 birth) |
| seven-knot source | 7 knots | first recorded tick at step 15; cumulative births 413 at step 7 | not reached in the horizon | not reached in the horizon |
| nine-knot drawn source | 9 knots | first recorded tick at step 17; 588 cumulative at step 5 | not reached | not reached |
| two clocks of the 21-knot structure | 21 knots | first ticks at steps 31 and 47; 613 cumulative at step 5 | not reached | not reached |

Gate 1: passes for ordinary growth and the guarded rule on the ring; passes for the first tick only under the recompute rule; fails by horizon for the other four sources (left out). The archived implementation and the count-level engine agree at 360 states per ring and pool policy and 60 per policy under not-all-equal. Under the `joins_first` pool the original ring's first tick is not reproduced alone (exhausted at 745 states). Gate 2 (s = 0, ordinary growth through the latest registered tick age, 100,000-birth limit): passes for all five starts; every recorded role of each source is written at the same step as alone, ticks come at the recorded steps, the first three steps agree with the archived `literal_turn`, and the first tick is found under the recompute rule. Cumulative ordinary births at the end: S1 8,654 (10 steps), S2 422 (5), T1 6,110 (10), T2 617 (5), T3 7,835 (10).

## Joint starts built

R0 = original ring, donor knot 4 (opposite the spare). R0m = original ring, donor knot 0 (the marked original with the spare; one of its three distinctions pays a unary birth). R5, R9 = ring after 5 or 9 parent steps, donor the first parent of tick 6 (knot 57) or of tick 10 (knot 126). X is the first source, Y the second. Demand = the births that the source's own ordinary plan takes from the donor. First ask = the donor's birth depth + 1 in the source's own history; in the joint growth every start asks the donor at parent step 1.

| start | class | X + Y | knots | donor | loose at the donor s = 0 / s = 1 | demand X + Y | first asks in the sources' own histories | first ask in the joint plan |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| S1 | same-step, original donors, repaired | R0 + R0 | 15 | 4 | 4 / 3 | 2 + 2 | 1 / 1 | 1 / 1 |
| S2 | same-step | R5 + R5 | 125 | 57 | 6 / 5 | 3 + 3 | 6 / 6 | 1 / 1 |
| T1 | staggered | R0 + R5 | 70 | 4 | 5 / 4 | 2 + 3 | 1 / 6 | 1 / 1 |
| T2 | staggered | R5 + R9 | 197 | 57 | 7 / 6 | 3 + 4 | 6 / 10 | 1 / 1 |
| T3 | staggered, X's tick needs a unary birth of the donor | R0m + R5 | 70 | 0 | 6 / 5 | 3 + 3 | 1 / 6 | 1 / 1 |

First missing construction: the unfunded merge of two original ring donors (S1 without repair) stalls at step 1 with shortages (knot, missing) (3, 2), (5, 2), (11, 2), (12, 2), the four neighbours of the merged knot, because the merged knot becomes a common witness of the neighbours on both sides. S1 is run with those four shortages repaired by extra loose slots (a changed definition, both versions reported). A start staggered in the joint growth does not exist for one shared knot: each knot pays all its loose distinctions in the one parent step after its birth.

## Branches by outcome

Counts are choice sequences at the contested births (equal states merged; no sampling). A source is `lost` when any registered tick has a loss certificate. `stalled`: the first parent step is unfunded and nothing is written. Tick 10 of a source whose first tick is the only one searched, and ticks not reached within 400 births, are not counted as lost.

| start | s | rule | choice sequences | both keep | X lost, Y keeps | X keeps, Y lost | stalled |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| S1 | 0 | guarded; recompute (both pools) | 1 each | 1 | 0 | 0 | 0 |
| S1 | 1 | guarded | 1 | 0 | 0 | 0 | 1 |
| S1 | 1 | recompute `unrestricted` and `joins_first` | 24 | 0 | 12 | 12 | 0 |
| S2 | 0 | guarded; recompute (both pools) | 1 each | 1 | 0 | 0 | 0 |
| S2 | 1 | guarded | 1 | 0 | 0 | 0 | 1 |
| S2 | 1 | recompute (both pools) | 720 (360 distinct leaves) | 240 | 240 | 240 | 0 |
| T1 | 0 | guarded; recompute (both pools) | 1 each | 1 | 0 | 0 | 0 |
| T1 | 1 | guarded | 1 | 0 | 0 | 0 | 1 |
| T1 | 1 | recompute (both pools) | 120 | 24 | 48 | 48 | 0 |
| T2 | 0 | guarded; recompute (both pools) | 1 each | 1 | 0 | 0 | 0 |
| T2 | 1 | guarded | 1 | 0 | 0 | 0 | 1 |
| T2 | 1 | recompute (both pools) | 5,040 (2,520 distinct leaves) | 2,880 | 1,440 | 720 | 0 |
| T3 | 0 | guarded; recompute (both pools) | 1 each | 1 | 0 | 0 | 0 |
| T3 | 1 | guarded | 1 | 0 | 1 | 0 | 0 |
| T3 | 1 | recompute (both pools) | 1 | 0 | 1 | 0 | 0 |

Which proposal is starved at s = 1 (recompute, `unrestricted`; each row is the same number of choice sequences, (m - 1)! for m proposals through the donor): S1 four proposals, 6 sequences each: X's (2, 4), X's (4, 6), Y's (4, 10), Y's (4, 13), all needed for both ticks of their source. S2 six proposals, 120 each: for each source its tick-6 pair (loses tick 6), its tick-10 pair (loses tick 10) and its triple (loses nothing). T1 five proposals, 24 each: X's two pairs (X loses both ticks), Y's tick-6 pair (loses tick 6), Y's tick-10 pair (loses tick 10), Y's triple (nothing). T2 seven proposals, 720 each: X's tick-6 and tick-10 pairs and triple, Y's tick-10 pair (loses its only registered tick) and three others (nothing). T3: the shortfall removes the unary birth of the donor and X's tick needs it.

Certificates (`grow_<start>.json`, `certificates_by_choice_sequences`): every loss certificate in every start names the shared donor as the parent that holds no loose distinction (S1 48, S2 480, T1 144, T2 2,160, T3 2 certificates across the sequences) and the birth that spent its last distinction, which is one of the other proposals through the donor. Examples. S1, s = 1, X lost: donor knot 4 holds no loose distinction; its last was spent by the birth of parents (4, 10) (Y's proposal), and the required birth of parents (2, 4) is unmade. T3, s = 1, guarded and recompute: donor knot 0 holds none; its last was spent by birth (0, 59, 63) (guarded, event 11) or (0, 65) (recompute), and X's required unary birth of knot 0 is unmade; the first parent step is funded with 23 births, one fewer than at s = 0.

## Predictions

| # | Verdict | Counts |
| --- | --- | --- |
| G | Fails in part, passes for what is registered | Four sources have no tick inside the horizon; the recompute rule does not reproduce a second tick alone (R0 undecided at 20,000 states, R5 no firing order); `joins_first` does not reproduce R0's first tick. For the five joint starts gate 2 passes at s = 0. |
| P1 | Holds on the registered ticks, under both rules and both pools | 0 of 5 starts have a loss or stall at s = 0 under the guarded rule and 0 of 5 under the recompute rule (one branch each). Second ticks of the original ring are not reached within 400 births under the guarded rule (S1, T1, T3) and are `open` under the recompute rule. |
| P2 | Fails | Earlier asker X loses in 48 of 120 (T1), 1,440 of 5,040 (T2), 1 of 1 (T3) recompute branches, and in each of them Y keeps ticking (the failing clause). Guarded: T1 and T2 stall (neither source ticks), T3 X lost with Y keeping. |
| P3 | Holds under the recompute rule, fails under the guarded rule | S1: X lost 12, Y lost 12 of 24. S2: X lost 240, Y lost 240, both keep 240 of 720. Guarded: the start stalls, no branch ends one source only. |

Literal reading of the preregistration (branch only when the donor has one loose distinction and two or more proposals need it; earlier slots written in ascending order of parent lists; added after the primary results, `grow_strict_*.json`): S1, S2, T1 end Y in both of their 2 branches; T2 has 2 branches (Y lost 1, both keep 1); T3 as before. The result there is fixed by which source's knots carry the lower numbers.

Pair in which every branch ends the same source: T3 at s = 1 (X, in every rule and pool). What distinguishes it: X's tick needs the unary birth of the marked donor, and the recompute rule offers a unary birth only while the donor holds more loose distinctions than it has enabled multi-parent proposals. At s = 1 these are equal, so the unary is never offered; the ordinary plan simply omits it and the step is funded. In S1, S2, T1, T2 no source is fixed: the starved proposal is each of the donor's proposals in equal numbers of choice sequences, so a source loses in as many sequences as it has proposals that are roles of its ticks' ancestry (S1 2 of 4 each; S2 2 of 6 each; T1 2 of 5 each for X and Y; T2 2 of 7 for X, 1 of 7 for Y).

## Scaffolds

The clock (ring of eight, spare at one original, tick of the scarcity study); the stage cuts at 5 and 9 parent steps; the first parent of a tick as donor (the second parent not tried); the merged donor (both supports, less one loose distinction of Y's part); the repair of S1; shortfall 0 and 1 only; the two ticks per source and the recorded tick ages; the recompute rule's pool policies; the reading of a contested birth (exhaustive at the donor; the literal reading reported alongside); the ascending order of the fair continuation at the donor; the 20,000-state completion search and its restriction to the first tick; the tick-first order inside a guarded step; the 400-birth and 12-step horizon.

## Commands (repository root; every run under 10 minutes and 12 GB)

Run in this order. Each prefix is `timeout 600 prlimit --as=12884901888 .venv/bin/python -B`.

1. `... experiments/REVIEW-LEADS-20261123-001D/REVIEW-LEADS-20261123-001D-E001_shared_supply/gate.py 1` (8.5 s)
2. `... .../addendum.py` (writes `construction_addendum.md/.json` and, in the artifacts folder, `construction_addendum.sha256`; before any joint growth)
3. `... .../gate.py 2` (7.5 s, 108 MB)
4. `... .../grow.py` (32 s, 538 MB) and `... .../grow.py --strict` (3 s)
5. `... .../verify.py S1 T3`, `... .../verify.py S2 T1`, `... .../verify.py T2` (11 s, 46 s, 74 s and 907 MB): the contest trees recounted with the archived functions (identical in all 30 runs), leaves checked, loss certificates re-read from the archived holdings, completions replayed under both laws.
6. `.venv/bin/python -B .../summarize.py > .../summary_tables.md` and `... summarize.py --strict > .../summary_tables_strict.md`.

Logs and timings: `artifacts/.../logs/`. Files: `gate1.json`, `gate2.json`, `grow_{S1,S2,T1,T2,T3}.json`, `grow_strict_*.json`, `verify_*.json`, `summary_tables*.md`, `construction_addendum.sha256`.

## Not done

Pairs with the seven-knot, nine-knot and 21-knot sources (no tick inside the horizon); a staggered pair in the joint growth (none exists for one knot); outside spends by births that are not roles of a tick; the second parent of a tick as donor; a second tick of the recompute rule (not reproduced alone); more than one shared donor; weighting over branches (counts of choice sequences only).
