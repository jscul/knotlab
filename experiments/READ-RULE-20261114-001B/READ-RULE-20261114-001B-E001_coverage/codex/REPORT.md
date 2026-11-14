# Reading-theorem census checks

Scope: `READ-RULE-20261114-001B`, experiment `E001_coverage`. This is computation
against the frozen preregistration and advisor answer. All authored files and
outputs are confined to this CODEX directory; source machinery and census
records are reused in place. No Git mutation, publication, tracker transition,
or change to a mathematical definition is authorized or performed.

## Computation contract

- Inputs: the frozen READ preregistration and advisor answer; CARRY's original
  per-family window records, syntax/window/direct machinery, and digest;
  FREE-TARGET's relation composition and rectangularity; the positive inequality
  gadget. No outside material or copied source datasets.
- Mapping: deterministic syntax checks, exact Boolean relation projections,
  complete bounded product length sets, and the unchanged finite direct search.
- Observables: residue coverage, exact tie flags, CARRY U values, least accepted
  product length through eight or a cap, and direct bond minima at depths 1–6.
- Controls: a separate raw-key implementation of R1, hand-calculated conditional
  product controls, exact reconstruction of CARRY Q sets and their recorded U,
  and the direct machinery's independent bond/deletion verification.
- Resources: `.venv/bin/python -B`, at most two computational processes and about
  8 GB total. Long computations are prepared for the existing shared runner,
  smoked with `--limit 20`, and left for the thread to launch.
- Stop: complete the requested computations where unambiguous and inexpensive;
  prepare expensive computations without launching them. Empirical checks do
  not discharge the preregistered proof obligations.

## Current evidence

Both counterexample variants are accepted by the unchanged machinery. The
verified direct minima are **2 at every requested depth 1–6**, rather than the
preregistered growth. A bond consists of the carried root `a` and target-own
`u`, which are opposite in every allowed state. Both complete windows have
U = 2 on their repeating part, and neither has a growth certificate. Q3 fails.

The original full window file has 5,964 final `ok` family records. The source
index records offsets, metadata, a streaming SHA-256, and source-file stability
checks without copying its allowed-state data. It contains 5,789 in-scope
families (draw weight 5,853) and 175 out-of-scope families (weight 175).

## Ambiguities

1. For R, does “every state” include Q states in which the proposed knot's
   position is not carried, or only the Q states in which it is carried? The
   code retains both predicates and leaves a disputed official flag null where
   they differ. It never interprets a semantic tie as identity carriage.
2. For Q1, must each reading meet the exception in every carried Q state, or is
   meeting it in some carried Q state sufficient? Exact state-wise tie evidence
   and both predicates are retained; a disputed official flag is skipped.
3. The preregistration mentions 83 undecided in-scope families. Applying CARRY's
   existing summary classification to the supplied full records gives 90:
   88 in stratum I and 2 in O. Which 83 were intended? No subset of 83 is
   selected. Tables use the supplied records' actual CARRY classifications;
   a statement about a distinct unspecified subset of 83 is skipped.
4. For conditional products, does the inherited 250,000-product storage cap
   count relation/carry pairs or distinct Boolean products? One family reaches
   the former cap while remaining below the latter. Its least-r computation is
   skipped and retained as capped/undecided; no cap interpretation is adopted.
5. What exact predicate defines which undecided families the counterexample's
   “shape describes”? No matching predicate is supplied. That descriptive
   match is skipped, without inventing a classifier.

The unchanged direct entry point stops at bond size six, so it cannot in
general confirm Q3's proposed values 7–9 at depths 4–6. This capacity limit
does not omit any observed counterexample cell: all returned exact minimum 2.

Counts, validation, timings, and execution disposition below come from the
completed computations.

<!-- generated-counts -->

## Computed census results

Completed: 5964 families. Independent R1 flags,
carried sequences and repeating-phase flags agree on 5964 families;
disagreements: 0.

| Population | Families | Draw weight | R1 every residue | R1 some residues only |
| --- | ---: | ---: | ---: | ---: |
| In scope | 5789 | 5853 | 471 | 1 |
| Out of scope | 175 | 175 | 10 | 0 |

Coverage shares among CARRY's bounded in-scope families (descriptive counts):

| Predicate | Covered families | Family share | Covered draw weight | Weight share | Unknown families |
| --- | ---: | ---: | ---: | ---: | ---: |
| R1_every | 469 | 9.2560% | 469 | 9.1441% | 0 |
| R1_some | 470 | 9.2757% | 470 | 9.1636% | 0 |
| R_every | 0 | undetermined | 0 | undetermined | 4479 |
| R_some | 0 | undetermined | 0 | undetermined | 4484 |

## Gates and predictions

- G: `inconclusive`. R gate unknown families: 68; R1 gate unknown families: 2.
- Q1: `fail`. Exception-only in-scope families: 9; unresolved: 73. The full key list and residue lists are in summary.json.
- Q2: `fail`. Conditional rectangularity succeeds for 2123 / 5789 families and 2180 / 5853 draw weight (37.2459%); capped counts as not.
- Q3: `fail`. Both variants give exact L(s) = 2 at s = 1–6 and a repeating window bound U = 2.

A gate with `null` is unavailable, rather than a pass or failure. Ambiguous
R coverage shares have explicit lower/upper count and weight bounds in
summary.json. No interpretation was chosen to complete a missing flag.

The R gate has zero observed violations and 68 unavailable families;
the R1 gate has zero observed violations and 2 unavailable families.
Those gates are unavailable because the reused Q_s sequences are capped,
so their repeating parts cannot be read. R1's separate syntax reproduction
passes in full. G is consequently inconclusive.

R's quantifiers disagree on 4598 families in at least one residue.
The official R flags affected by that question remain null; both alternatives
and exact per-state ties are retained. R1's every-residue flag does not
depend on that question.

Q1's definite exception-only list contains every identified family below;
the complete census keys are in summary.json. The unresolved list includes
both capped windows and the five families affected by its state quantifier.

| Family key SHA-256 prefix | Exception-only R residues |
| --- | --- |
| `018277ebab1de9a6` | [0] |
| `8e8c03006cbcc448` | [0] |
| `3fbe34294e00b1fa` | [0] |
| `c2850e10ae4f9743` | [0] |
| `33e3211faac70b6b` | [0] |
| `0235fe8965b7f432` | [1] |
| `8840b0164bc946d1` | [0] |
| `23df2a825b7b0e33` | [0] |
| `c6c99c623a5487a0` | [0] |

## Conditional rectangularity by CARRY classification

| Scope | Stratum | Verdict | Families | Successful | Count share | Weight | Successful weight | Weight share |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| out | I | bounded | 125 | 40 | 32.0000% | 125 | 40 | 32.0000% |
| out | I | undecided | 46 | 42 | 91.3043% | 46 | 42 | 91.3043% |
| out | O | bounded | 3 | 0 | 0.0000% | 3 | 0 | 0.0000% |
| out | T | bounded | 1 | 0 | 0.0000% | 1 | 0 | 0.0000% |
| in | I | bounded | 4967 | 1582 | 31.8502% | 5029 | 1638 | 32.5711% |
| in | I | growing | 632 | 538 | 85.1266% | 634 | 539 | 85.0158% |
| in | I | undecided | 88 | 3 | 3.4091% | 88 | 3 | 3.4091% |
| in | O | bounded | 91 | 0 | 0.0000% | 91 | 0 | 0.0000% |
| in | O | undecided | 2 | 0 | 0.0000% | 2 | 0 | 0.0000% |
| in | T | bounded | 5 | 0 | 0.0000% | 5 | 0 | 0.0000% |
| in | X | bounded | 4 | 0 | 0.0000% | 4 | 0 | 0.0000% |

Among the actual 90 undecided in-scope families, 3 are
conditionally rectangular through r ≤ 8. The separately mentioned subset
of 83 has no supplied membership list and is not selected.

One family reaches only the stricter pair-count storage cap; its least-r
answer remains skipped/undecided under Ambiguity 4. All uncapped results
are unaffected. Even if that family succeeded, Q2's draw-weight share
would be 37.2629%, still below 90%.

## Counterexample details

| Variant | U(1..6) | Exact L(1..6) | Direct bonds verified |
| --- | --- | --- | --- |
| a_repeated_argument | [2, 2, 2, 2, 2, 2] | [2, 2, 2, 2, 2, 2] | True |
| b_positive_gadget | [2, 2, 2, 2, 2, 2] | [2, 2, 2, 2, 2, 2] | True |

Both keys, complete window and growth records, exact direct witnesses, and
per-depth verification are retained in counterexample.json. The repeated
argument is accepted. The positive gadget uses its exact four positive NAE
constraints and adds its three own distinctions to S. In both variants
the direct witness is the carried top a and target-own u. The three
growth tests G, G2 and G2_live return no certificate.

## Validation and timings

- Streaming the original 3.5-GB records: 41.242 seconds; peak RSS 1155.18 MiB.
- Combined census: 575.054 summed case seconds; slowest case 7.774 seconds; maximum runner case RSS 1135.77 MiB.
- Foreground runner wall time: 601.019 seconds (about ten minutes); maximum parent-plus-worker memory 1153.30 MiB.
- R1's independent raw-key implementation has 17 hand-expected controls; conditional products have seven controls, including equal Boolean products with distinct identity maps.
- Fifteen focused tie/quantifier controls passed in 0.092 seconds.
- The independent exception audit confirmed all nine Q1 families: 1,956 eligible knot/state checks across 899 projected states, in 2.440 seconds. It reuses the producer's Q-state membership and independently recomputes candidates, pair projections and exception flags.
- For every complete source window, each reconstructed Q level agrees with CARRY's recorded cardinality, U, repeated phase, and the union of identity-carried positions.
- All requested direct bonds are checked independently by the reused CNF bond/deletion checker.

The shared runner used one worker plus its parent and a 4G configuration;
no service or tracker registration was launched. Preparation, the 20-case
foreground smoke, and the foreground computation are
recorded under census_run/. Reused source files were not modified.

## Outputs and replay

- [results.json](results.json): compact per-family flags, residues, tie histograms and conditional-product outcomes.
- [counterexample.json](counterexample.json): both raw census keys and all window, growth and direct results.
- [summary.json](summary.json): exact counts, draw-weight shares, gates, predictions, unresolved cases and ambiguity bounds.
- [validation.json](validation.json): focused output reconciliation, Python AST checks and source/code hashes.

The 20-case smoke completed in 0.549 summed case seconds. Its measured
cost supported the foreground census, which finished in about ten minutes.
All 5,964 runner cases are final and successful; no run awaits launch.

Commands used from the repository root (CODEX is this report's directory):

```bash
CODEX=experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex
.venv/bin/python -B scripts/longrun.py launch "$CODEX/job.py" --out "$CODEX/census_run" --unit read-rule-coverage --workers 1 --case-timeout 600 --case-mem 3G --mem-max 4G --cpu-quota 100% --param phase=combined --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$CODEX/census_run" --foreground --limit 20
.venv/bin/python -B scripts/longrun.py run --out "$CODEX/census_run" --foreground
.venv/bin/python -B "$CODEX/summarize.py"
.venv/bin/python -B "$CODEX/verify_outputs.py"
```

The preparation line records an already performed operation; it is not a
request to overwrite the retained configuration. The last two commands
rebuild and validate the requested outputs using the retained raw evidence.

Q3's disagreement with the frozen prediction is recorded here for the
owning thread. The write restriction prevents editing any external correction
log or research lifecycle record in this task.
