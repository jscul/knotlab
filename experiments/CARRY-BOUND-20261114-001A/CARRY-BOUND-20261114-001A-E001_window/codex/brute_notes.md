# Independent projection and direct-search implementation

This is an implementation handoff, with no population results or predictions
computed. The [glossary](../../../../publication/knotlab/INTUITIONS.md#glossary)
supplies the meanings of distinction, projection and bond.

## Inputs and independence

`brute.py` reads raw definitions from `prep.defs`, a row's `key` or `defs`, a
canonical key string, or a raw definition list. It recomputes the usual-limit
relations from TOP using only the permitted description-language module. It
does its own finite inlining and full CNF unfolding. It never imports
`window.py`, per-call relation code, relation composition, or path DP code.

`direct.py` reuses only the read-only `DirectSearch` from the FREE-TARGET
independent referee. Its CNF, covered-target inventory and witness recheck come
from `brute.py`. Search uses the referee's cadical195 instance solver;
projection and support-minimality rechecks use glucose42. The latter enumerates
every extendible state of the support and checks every one-variable deletion.

## Projection API and identity map

`project_word(prep, word, *, entry_index=None, cutoff_depth=None, ...)` returns
`status`, `labels`, `allowed`, `main_aliases`, `end_aliases`, `root_labels`,
`own_labels`, depth and cutoff records, counts, and resource limits.
`allowed` is a sorted exact list of integers. Its bit j is the value of
`labels[j]`; all remaining CNF variables are forgotten by SAT projection.

For k main ports and V end-block distinctions, main port p has symbolic label
p, and end-block index v has symbolic label k+v. Scan the main ports and then
the end block, and keep only the first symbolic label of each actual unfolded
variable. Thus end-port/main-port identity and end-port/end-port identity
produce one variable. Own distinctions of finite inlined helpers belong to
the end block, in raw-call inlining order.

Letters of `word` are ordinals among the S block's retained S calls, starting
at zero. They are not indices in the block's full call list. A wrapper's
`entry_index` is separately an ordinal among its direct retained S calls.
Multiple direct wrapper S entries require an explicit entry index; no first
entry is silently selected.

`recheck_bond(prep, word, support, ...)` accepts canonical unique labels,
rebuilds the independent full CNF, and reports the complete support projection,
every deletion's fullness, and separate flags for a bond and for a bond that
contains both a main port and an end own distinction.

`bond_check_cnf(clauses, n, support)` is the same independent support test on
explicit unfolded variable indices. `unfold_pattern` exposes the full CNF,
copies, origins, covered targets and selected end copy for the direct runner.

## Depth convention and questions left open

The implemented absolute depth convention follows the prior direct referee:
a self-holding main is at depth 0, while a nonholding wrapper's direct
self-holding entries are at depth 1. SELF increments depth. A numeric
self-holding call within an already self-holding copy keeps that depth.
Finite nonholding helpers are inlined without a depth increment.

1. The frozen text uses both a SELF word of length s from the top S copy and
   FREE-TARGET's absolute target depth s. They agree for main=S. For a wrapper
   the selected end has absolute depth `len(word)+1`. No scalar convention is
   chosen here. Default wrapper projection comparisons return `not_computed`
   unless the caller supplies `cutoff_depth` explicitly.
2. In this implementation, all blocks at depths through `cutoff_depth` are
   explicit, inclusive; calls below it receive their usual-limit relations.
   Main=S therefore defaults to cutoff `len(word)+1`. A wrapper comparison
   needs the lead's explicit cutoff and, where necessary, entry choice.
3. The sample's direct targets are unambiguous under the stated absolute
   convention: every S copy directly entered from main and thereafter reached
   through S calls only, at absolute depth s. Other recursive copies are
   still unfolded and their distinctions remain eligible members, but their
   own distinctions are not covered targets. No other target definition is
   silently added.

The lead owns any frozen-text resolution. Ambiguous projection comparisons
are skipped individually; the direct runner's explicitly specified absolute
depth calculations remain available.

## Direct job and cap outcomes

`direct.run_case(row, s)` accepts s=1..6 and unfolds through absolute depth
s+2 inclusive, with usual-limit relations below. Members range over all
unfolded distinctions and targets over every covered S copy's flattened own
distinctions at depth s. The returned minimum is an integer at most 6 after a
successful independent witness recheck. A completed exclusion of all sizes
through 6 is the literal `"> 6"`. A deadline, construction cap, unresolved
input convention or failed verification has a null minimum and an explicit
status; none receives a growth verdict.

Construction caps are checked during finite inlining and unfolding, before
allocating an oversized block or whole pattern. Defaults are 15,000 variables,
100,000 clauses/flattened calls and 25,000 copies. Exact projection retains at
most 2^20 rows; direct support rechecks retain at most 2^6. The reused direct
search has a 480-second deadline and 30 model-seeding attempts by default.
Every result records the requested limits. The shared runner separately owns
worker memory, outer timeout, retries and durable outputs.

`job_direct.py` has only `setup(params)`, `cases()` and `run(case_id,payload)`.
It consumes a post-path `sample.json` with `direct_ready: true` and a `direct`
list of keys or rows, at most 60 distinct families in the frozen CARRY hash
order. Archive raw definitions and S take precedence over sample metadata.
One case is one family and one depth; all six depths are produced. No job is
launched by importing these modules. Setup rejects unknown job parameters and
calls `inputs.verify_sources()` before accepting the sample.

## Suggested lead-driven controls

- A carried port with one NAE rule on that port and two pendant own
  distinctions, plus at least two pass-through SELF calls, exercises a
  positive size-three witness and main/end port aliases. Using a permuted
  second call checks that identity is independent of port position.
- A deliberately repeated child-port argument exercises end/end identity
  merging. This is a mapping mutation control, outside the generator's
  distinct-argument sampling rule. It must produce one canonical variable,
  not a spurious equality bond between two coordinates.
- One NAE relation with an extra unconstrained distinction rejects its
  four-variable supersupport, because a deletion retains a non-shattered
  triple. Two independent NAE relations reject a support requiring unrelated
  endpoints. The reused referee also exposes its existing controls without
  writing them unless its CLI is invoked.
- A wrapper with two direct S entries must be skipped without an explicit
  entry index. A wrapper with no explicit cutoff must also be skipped.
- Tiny construction/row limits must return `cap` and no complete relation;
  a tiny direct deadline must return `timeout` and no `"> 6"` minimum.

## Validation performed

The four Python files passed in-memory `ast.parse` and import checks under
`.venv/bin/python -B`. The permitted description-language module and the
read-only referee search module also imported successfully. No family,
control, experiment, shared-runner job, population prediction or sample result
was computed in this lane.

## Companion summary interface

`summarize.py --window OUT [--paths OUT] [--direct OUT]` is for the thread to
run after the frozen population finishes. It refuses a missing or foreign
window case, reads archive draw weights, and writes `CODEX/summary.json`.
`--check-gates` accepts smoke records and reads recorded gates a/b/e without
computing P1--P5. The separate lead-owned gate report retains authority for
the other controls.

The full summary keeps count and draw-weight shares, descriptive Wilson95
intervals, and sensitivity excluding undecided cases. Caps, invalid gates and
runner failures override recorded local certificates. A valid full window
bound is resolved bounded; an uncapped valid in-scope G/G2 certificate is
resolved growing; partial window bounds alone remain undecided for either
global claim. Unknown scope/stratum blocks the affected prediction and
sensitivity denominators. Threshold comparisons use exact rational values.

P3's scalar is skipped: the phrase "on that residue" does not select a
quantifier when a family has several residues without a bound. Its per-residue
flags remain in the summary. B/widened-B/tie readings are nonexclusive,
retaining some/every minimum witness and some/every residue separately. Old
records missing the lead's optional per-residue readings are skipped for those
shares; no phase is inferred from an unphased union of saved states.
Readings, bond-size records and the four explicit window-verdict shares are
also retained separately for each in-scope stratum I/T/O/X.
