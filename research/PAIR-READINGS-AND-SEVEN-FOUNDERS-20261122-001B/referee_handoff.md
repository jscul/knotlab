# Scientific referee handoff for the seven-founder census

**Independent scientific referee pending.** The principal claim is an actual three-parent parity closure at the second cut of a seven-founder, eight-meeting source. Its matched not-all-equal birth receives one fresh distinction. A complete finite census also supplies a cut-three ternary closure and a cut-four two-place ordinary exception. A separate deduction classifies the 11 parity types still connected and funded at the four-cut stop. [Result and population accounting](result.md) · [Named source, exact payments, all 11 survivors and induction](seven_founders.md)

## Prospective authority

The independent GPT-6.2 Astra Max reviewer required a common physical witness for each uncovered pair, a complete old-row-span test for zero, and an explicit control where a child exhausts only its own component. The revised design also required a complete accounting before reporting probabilities or minimum ages. The reviewer inspected no target outcome. Candidate 2 and the preregistration are byte-identical, SHA-256 `52190e0f89817a4df0187fe8ce26a0cb0f74cf49ce71b41a29ff8376b634dbe9`. The receipt has SHA-256 `c2ae564f135d421abecc5054be919fc2e0bb412446fab7083dec1415e94636bf`. The coordinator verified the object gate, contract and dependencies, and activated the study before observations. [First candidate](design_candidate_1.md) · [Approved second candidate](design_candidate_2.md) · [Written freeze](preregistration.md) · [Independent prospective receipt](advisor_receipt.json) · [Frozen contract](../../experiments/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/contract.json)

## Suggested scientific checks

1. **Reconstruct the shortest closing whole from its seven original rows.** Verify the three distinct original physical witnesses, including the one covering (3,4,6), all seven loose payments of cut one, the three actual shared-parent witnesses at cut two, and the absence of another birth. Confirm the old rank, preservation of 256 even words and the zero scalar count after changing only the final sign. Verify the not-all-equal child receives exactly one new distinction. The other two terminal examples and one-flag controls are separately identifiable. [Full named events](../../artifacts/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/physical_events.json.gz)
2. **Check lawfulness and the closing convention.** The deletion-pivot proof from the six-founder study applies to all 67 seven-founder patterns. Match its global projection and erasure claims to the named SAT or direct controls. Local arities 3–7 pass the canonical CLI under both laws. Preserve the cut-four two-place implied exception as a separate ordinary endpoint. The two ternary closings meet the stricter convention directly. Also repeat the earlier fourth-cut six-founder positive. [Canonical and physical checks](../../artifacts/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/physical_summary.json)
3. **Test the physical whole against proper live components.** Recompute the four-founder comparison on the same three old names. Their parity projection changes from four to eight legal words when two unrelated openings survive, and the target's grant changes from zero to one. Across the seven-founder ledger, directly count the input's membership in the row span and the full loose-name complement. There are 1,001 proper-component sole births in each law. There are 3 whole-paying parity events and 5 whole-paying not-all-equal events across the same three founding types. [Control rows and conditional word lists](../../artifacts/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/physical_controls.json)
4. **Verify every denominator and refusal.** Check the 5,594 decorated symmetry classes, all founder relabellings, tree origin counts and all 128 flag patterns per shape. The two integer denominators with independent 1/4 flags are 2,564,997,120 and 28,913,418,240. Initial stalls have positive mass under both. For the 11,188 source/law records, reconcile complete parent groups, actual rather than assumed disjoint payments, grants, live components and the shortages. Confirm that at most four successful cuts are present and no target was censored. [Per-source end ledger](../../artifacts/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/census.json.gz) · [Exact-weight totals](../../artifacts/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/census_totals.json)
5. **Review the later deduction separately.** A repeating end must preserve every effective witnessed subset as well as opening counts. For each finite-tree case check that the four initial holders have supplies 3,2,2,3, that each of the four unary births has two possible next additions, and that the maximal unheld families at later sizes are precisely all leaf deletions of their unions. This checks its inductive funding and the four-parent final birth at paid age seven. The earlier rank calculations and all four-cut frequency claims stand independently of this deduction. [Measured end isomorphisms and subset certificates](../../artifacts/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/surviving_ends.json)

## Exact replay

From the workspace root, use the research virtual environment, with its NetworkX, PySAT and canonical knot CLI. The first script generates the catalogue and complete end ledger. A separate GPT-6.2 Sol Max implementation reconstructs all named physical holdings from the registered founder list and compares its compressed and uncompressed outputs byte-for-byte in verification mode. The third script binds the old controls, alternative counting method and survivor certificates. The last script matches each native cut and builds the merged result. These runs use one thread and fit under a six-GiB address-space cap. [End census](../../experiments/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/census.py) · [Independent named replay](../../experiments/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/physical_replay.py) · [Matched controls](../../experiments/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/checks.py) · [Full reconciliation](../../experiments/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/reconcile.py)

```sh
leaf=PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B
runner="experiments/$leaf/${leaf}-E001_seven_founders"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
.venv/bin/python -B "$runner/census.py" --phase all
.venv/bin/python -B "$runner/physical_replay.py" --verify
.venv/bin/python -B "$runner/checks.py"
.venv/bin/python -B "$runner/reconcile.py"
```

For an empty output directory omit `--verify` on the first physical run to materialize the named ledger. The merged output has SHA-256 `204cb1a0c0539695f9891af6ce709f0472ae6370a2574b680f72ade8fffae14b` and identifies the individual evidence digests. Two implementations agreed on every registered input, 10,028 refusals, 4,637 paid cuts and 35,100 births. Scientific review and reproduction are separate. [Merged results and digests](../../artifacts/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001B-E001_seven_founders/result.json)

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — seven founders under two knot laws | **Status: Successful** | Two measured canonical whole closures |
| Local direction — minimum extra meetings at seven | Settled at two | Earlier lower bound and funded second-cut witness |
| Broader exploration — G17 meeting patterns and G18 comparing growth laws | Known alternatives | Measured and inferred ages separately accounted |
| Long-term goal — G5 Dynamics | Capability gained | Exact funding can preserve the whole earlier scalar state |

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Independent scientific referee of the seven-founder result | 2/3 — verify physical and later-age claims | 3/3 — named payments and cohort maps available | Test complete original holdings and the induction → referee verdict | Alternative · deferred |

**Round recommendation — STOP.** The selected size has both a traced canonical positive and exhaustive four-cut evidence under both laws. Other founder counts and signed operator readings are outside this study.

**Corrections:** None to the preceding six-founder record or the tree and one-addition obstructions.

**Goals:** B293 addresses G17 Typical and rare meeting patterns, G5 Dynamics and G18 Comparing growth laws.

**Assumptions:** At seven founders the study applies the A179 choice of simple additions, capped private supply, two declared source weightings and the four-cut observation limit.

**Scaffolds:** Named physical founders, supplied funding and knot laws, and the opposite final scalar sign control. The payments, relabellings and alternative law expose their individual roles.
