# Fresh sampled relation and semigroup audit

**The sampled relation computations and completed semigroup verdicts reproduce.**
The deterministic base sample has 120 families; five additional families selected
by the main referee's direct counterexample search and two with a zero-own
delaying type bring the audit to 127.
Every one of the **318 per-call relations R_i** matches the recorded result.
The **103 completed source verdicts**, including every least r, reproduce.
The remaining 24 source rows are capped computations; fresh nonrectangular
recurrence certificates decide all 24 as non-forgetting. This says nothing about
whether their members-anywhere bond sizes grow or stay bounded.

This is V2 same-task independently authored AI recomputation, not external
replication or a proof of the claimed growth interpretation. No Python under
either prohibited FREE-TARGET or CENSUS-FORGET experiment tree was opened or
imported. No network, Git mutation, publication, or writes outside this lane's
`sample_*` files occurred.

## Sample and scope

| Structural stratum | Recorded verdict | Census families | Base sample |
| --- | --- | ---: | ---: |
| c >= 2 | certified | 1,080 | 24 |
| c >= 2 | non-forgetting | 5,779 | 24 |
| c >= 2 | capped | 66 | 24 |
| c = 1 and non-chain | certified | 538 | 12 |
| c = 1 and non-chain | non-forgetting | 119 | 12 |
| chain | certified | 4,223 | 12 |
| chain | non-forgetting | 967 | 12 |

The 657 stratum means `c == 1 and not chain`. The auxiliary flag
`other_holding_calls` concerns other types in **main or S** and is not this
stratum's definition. The structural counters, this flag, c, definition counts,
flattened block sizes, and limit-alive flags all match independently.

Selection uses SHA256 with seed
`CENSUS-FORGET-R1-independent-sample-v1`. Within each certified cell, one minimum
hash key at every available r is selected before filling the quota by the
remaining minimum hashes. Other cells use minimum hashes directly. This covers
every recorded r from 1 through 12. It is a deterministic audit sample, not a
sample used to estimate a population share. The exact ranking expression, keys,
selection reasons, relations, and source hashes are in `sample_audit.json`.

All five requested direct-counterexample families are additional to the base
sample. Their relation certificates reproduce:

| SHA256 of family key, prefix | Fresh least r |
| --- | ---: |
| f25a8e17968d | 3 |
| 3fe70047c198 | 3 |
| f3c4843e45fa | 3 |
| ec647c80edb0 | 3 |
| c6cbc657bedb | 5 |

Two further targeted families have another self-holding type with zero own
variables that can delay before calling S. Both fresh relation certificates
match the source: **e8ce853eb78a has r=2**, and **6227f3d37d32 has r=3**.
They were appended after the original 120+5 selection, which is preserved.

These are certificates for the selected S-call relations. They do not certify
the main referee's broader claim about targets in another self-holding type.
The sample contains 32 families with another self-holding type and 15 such types
with positive own counts after finite expansion; those counts and each type's
limit relation are retained for the main referee's interpretation audit.

## Independent reconstruction

The code enumerates the assignments of each raw definition directly, starting
every SELF relation at TOP and iterating monotonically to a fixed point. It adds
the specified pass-through NAE rule and expands every finite numeric helper
with fresh own variables. It imports only the permitted input-language
`dlang.py` to compare the independently computed final relations. All **127
greatest fixed points and all definition port relations match**. In 51 families
at least one SELF relation is strictly smaller than TOP, so this comparison
does not reduce to using TOP everywhere.

For each selected call, a fresh CNF includes every other call's independently
computed limit relation and leaves the selected call open. Exactly 64 SAT
queries recover its incoming/outgoing relation. All **20,352 SAT queries** are
covered by an additional assignment-enumeration comparison for each of the 318
relations; these sampled flattened blocks have at most 12 variables. No shared
preparation output is used to derive G or R_i.

There are two distinct fresh semigroup computations. A search of the reachable
nonrectangular products either supplies an explicitly checked repeated product
or exhausts an acyclic automaton; in the latter case its longest path gives the
least r. A separate construction follows the complete sets of length-n products
to set repetition or its declared 250,000-entry cap. For all 103 completed
source rows, the exact set sizes, rectangularity flags, first repeating length,
period, stored-entry count, and r match. Every stored source non-forgetting
word also validates through independent set-based composition.

## Capped rows are separate

All 24 sampled capped rows have a fresh, exactly verified nonrectangular lasso.
That is new finite evidence deciding their semigroup question; the original
finite cap itself was only an undecided computation.

For 23 of them, the separate length-set construction still reaches its resource
cap. One family, key SHA256 prefix **a86b73d872cc**, instead completes: the sets
at lengths 33, 34, 35 repeat with period 3, every repeating set contains a
nonrectangular product, and 247,445 entries were retained before repetition.
Charging the next 10,419-entry set would exceed 250,000. A different placement
of the repetition/cap check could explain the recorded cap, but its producer
code was intentionally not consulted. This is a procedural difference within
a capped row, not a contradictory mathematical verdict.

No sampled R_i is empty. No empty product appears in any completed length of
the separately retained orbits, including their completed prefixes when capped.
No claim is made about omitted levels after a cap.

## Controls, limits, and replay

Controls pass all 256 two-state relation compositions, rectangular-factor
persistence, and all 136 unordered pairs of two-state generators, comparing
the nonrectangular-product decision to complete length-set exhaustion. Named
controls include empty and proper rectangular relations, identity and
permutation recurrence, a mixed non-forgetting choice, first rectangular power
two, and rejection of a false lasso. A capped fixture whose exact answer is
finite r verifies that a cap is not a non-forgetting certificate. Separate
controls distinguish greatest from least fixed points and detect removal of an
unselected other-type call's constraint.

The final audit has **zero relation, fixed-point, structural, completed-orbit,
or completed-verdict mismatches**. It does not audit the entire census and does
not validate the growth argument's depth convention, target-type coverage,
chain transfer, or the census weighting. Those are separate referee duties.

Replay from the repository root:

```sh
timeout 840 /home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/CENSUS-FORGET-20261114-001/referee-R1/codex/sample_audit.py
```

The run uses one single-thread Python process under a 2 GiB address-space limit.
Exact final runtime, peak RSS, source/input hashes, interpreter, and thread
identity are recorded in `sample_audit.json`; `sample_run.log` retains its row
progress and final summary.
