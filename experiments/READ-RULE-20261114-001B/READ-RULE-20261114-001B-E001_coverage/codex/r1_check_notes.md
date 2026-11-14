# Separate R1 syntax check

Owned implementation: `r1_check.py`. This checker computes the frozen R1
syntax predicate and the repeating carried sets directly from raw census
keys. It imports only the Python standard library. It imports no primary
READ-RULE code and no CARRY parser, inliner, predicate or computed flag.

Interface: `check_family(raw_key)` returns the independently recomputed scope,
S and main, the usual-rule additions, R1 positions and their syntax witnesses,
pendant distinctions and every recorded call-argument use, the carried-set
preperiod and period, one flag per repeating phase, and `R1_every_residue`,
`R1_some_residue`, `R1_progressions_only`. `aligned_residues(result, t, p)`
compares those phases with another declared repeating period by absolute depth
congruence. It does not consume the other computation's coverage flags.

The checker validates local argument indices and downward definition calls.
It appends exactly the existing census usual-rule constraint: one
`K(0,1,2)` for a definition with a SELF call permuting those three ports.
Inlining uses symbolic variable identities formed from invocation call words
and local variable indices. Separate calls introduce separate own
distinctions. Non-K call arguments are recorded before inlining, including
arguments passed to a helper that contributes no constraint.

For a candidate triple `{k,x,z}`, the three distinctions must differ, `k`
must be a port of S, both other distinctions must be own distinctions of S's
inlined block, and at least one can serve as `z`: it belongs to exactly one
constraint occurrence and to no non-K call argument at any inlined definition.
The other own distinction `x` need not be pendant. Repeated constraint
occurrences remain repeated syntax. The predicate does not inspect ties or
allowed states and does not establish a bond-size bound on its own.

The carried sets include every direct S entry of main after inlining.
When main is S, depth zero carries all three ports. Each transition takes
the union over every onward S call; a child's position is carried exactly
when the actual argument is a currently carried parent port. The resulting
subset sequence has at most eight distinct states. The booleans refer only
to its repeating part, including when the initial part has coverage.

## Controls and execution

The `--controls` command has 17 hand-specified checks: one pendant is enough;
both pendants; SELF argument exclusion; a second constraint occurrence;
helper-call argument exclusion; exclusion even for an unconstraining helper;
own distinctions introduced inside a helper; distinct own identities for two
helper invocations; coverage on only one of two phases; all wrapper entries;
coverage confined to the initial part; a third member that is a port;
usual-rule port-only constraints; the other-own scope exclusion; the delayed-S
scope exclusion; and two absolute-depth residue-alignment checks.

Suggested first command, when scheduled by the lead:

```sh
.venv/bin/python -B experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex/r1_check.py --controls
```

For the specified population, pass the authorized CENSUS-FORGET JSONL to
`--census`. The CLI selects each key's final successful record, filters
`chain == false` and verdict in `{non-forgetting,capped}`, and uses the CARRY
hash order. Alternatively `--keys-jsonl` accepts one JSON key string or an
object with `key` or `case` per line. Both forms emit one result per family
to stdout and perform no file writes. The caller owns output capture.

No Python process was run while implementing this checker. After the lead
granted one process slot, all 17 controls passed, followed by a full pass over
the 5,964 distinct keys in `source_index.json`. Only `rows[].key` was consumed;
no primary R1 output or code was opened for this pass. The first 20 families
took 0.0137 seconds; all families, metrics and output writing took 0.389
seconds. Peak resident memory was 61,540 KiB. The process slot was released
immediately after completion. No subprocesses, workers, numerical-library
threads or SAT calls were created.

`r1_independent.json` contains all per-family results keyed by raw key, source
and code SHA256 digests, the control results and metrics. The independent
scope predicates give 5,789 in-scope and 175 out-of-scope families. Among the
in-scope families, 471 have R1 syntax coverage on every repeating residue,
one on some repeating residues only, and 5,317 on none. Among the out-of-scope
families, 10 have all-residue syntax coverage and 165 have none. These are
syntax counts, pending the lead's separate reconciliation and semantic
gates; they do not discharge R1's proof obligation.

## Ambiguities

No unresolved ambiguity was identified under the delegated interpretation:
"own" includes own distinctions created by inlined nonholding definitions,
and "no call argument in any definition" includes uses at every inlined
call boundary. Out-of-scope families receive syntax flags plus an explicit
scope flag; those syntax flags do not extend R1's scientific applicability.

Native worker identity, obtained from `CODEX_THREAD_ID` without deriving it
from a task name: `01a1d912-407d-7f41-a887-d4ec9fc026d3`.
