# Independent exhaustive-support audit

The least-bond monotonicity assertion is false, including for an actual alive
description in the registered population. The finite census numbers are not
thereby disproved; their interpretation as upper bounds that deeper levels
can only lower must be removed or replaced by a separately proved condition.

This lane wrote only this directory. It did not open, import, or execute the
study's Python/C sources or `summarize.py`, use the network, mutate Git, or
publish. It reused the old ADDR referee's actions and words read-only, as
authorized. The primary pattern placement, support enumeration, and
projection checks are new. Parent referee `fresh_pattern.py` and
`fresh_search.py` were imported read-only for a separate comparison after
their implementation was available.

## Larger exhaustive checks

The core panel contains 29 descriptions: 26 actual registered-population
keys and three controls. Selection used two random keys per N9 outcome
stratum, with a frozen seed, then four each from actual `[3,3,4,4]` profiles,
dense undecided descriptions, and rigid-like descriptions. N9 outcomes were
used only to select keys; no equality between the changed N4/N5 observables
and the study's N9 numbers is assumed.

There are 82 queries at top level 2 and spans 1 and 2:

| Truncation | Queries | Support cap |
| --- | ---: | ---: |
| N4, 31 distinctions | 58 | 7 |
| N5, 63 distinctions | 24 | 4 |

The primary method enumerates crossing supports in increasing size and
checks their projections by SAT, over every assignment modulo NAE's global
complement symmetry. A non-full support is accepted only if every maximal
proper support is full, testing all its assignments. It stops at the first
bond in the smallest size, or exhausts every candidate through the cap.
The only reduction is exact separation into independent constraint
components: a minimal non-full support cannot span two product factors.
It does not infer bonds from connectedness or impose a ruler formula.

Across these queries it examined 4,344,938 candidate supports and made
6,355,842 SAT projection calls. This includes a connected 31-distinction
description for which both spans exhaust through 7 without finding a bond,
so coverage is not confined to disconnected or tiny patterns.

The separate bucket-elimination existence-circuit search returned an exact
answer on 62 queries: 50 numeric/bounded answers and 12 `none` answers. Every
one agrees. Its other 20 answers hit an elimination-width limit and are
excluded, not counted as passes. The two independent placement
implementations and the parent's placement implementation agree on the
constructed patterns. All seven source controls pass: identity and
nonidentity tree actions, N0 append boundary, term order, double-flip
cancellation, duplicate-image rejection, and a deliberately corrupted tree.

Three additional targeted queries also agree exactly between exhaustive
supports and the separate solver: N4/top2/span1 is `>7`, N4/top3/span1 is 3,
and N5/top3/span1 is `>4` for the counterexample below.

## Actual fixed-top monotonicity counterexample

Key `a0ce47179bf2fb205295a4415dbda9c6d19c17c6ebaaf506331718c8b15300e4`
is actual W_R draw 1185, seed `20261121-1185`:

```text
[1,[1],[0],[0],
 [[0,1,3],[0,6,7],[1,2,4],[2,5,6],[3,4,8],[4,5,8],[4,7,8]]]
```

It has one state that flips every bit. It is alive at the study's N9, whose
stored profile is `[">10",">10",">10",">10"]` (spaces in the stored display
are immaterial). Both tested truncations below are alive.

At the study's fixed top level 3, span 1:

| Truncation | Exact result | Evidence |
| --- | --- | --- |
| N4 | L = 3 | Bond ids `[7,15,16]`, forbidden values `[0,0,1]`; every proper projection is full; all 128 crossing pairs exhausted |
| N5 | L > 4 | All 128 crossing pairs, 6,400 triples and 158,496 quadruples exhausted; separate search gives the same exact bounded result |

This directly falsifies non-increase in N at the study's top level. It does
not claim that this key violates non-increase specifically at N9 to N10.

The same key at top level 2, span 1 gives a stronger unrestricted example:
N3 has L = 3 and N4 has **no crossing bond at any size**. Complete model
enumeration gives 72 and 2,592 states, respectively. Equal/complementary
model columns determine binary-bond classes. A bond of size at least 3 can
use at most one member of each class, since two such members already form a
non-full pair. Exhausting every support of the resulting finite relation
therefore determines all larger bonds, not just those under an arbitrary
cap. At N4 none crosses the chosen levels. This is a calculation on allowed
states; no new native identity/contact claim is made by the reduction.

For a second actual description, key `162021bb42750e56a80c86c6eca97216d8d598a76c0a8a5cb9a4d4fb0428b8d8`,
top level 1 and span 2 give L = 3 at N3 and L = 4 at N4. Complete state
counts are 40 and 36. The old bond `[1,7,9]` becomes nonminimal because its
target pair `[7,9]` becomes non-full. A new least bond is `[1,4,5,7]`, with
forbidden values `[0,1,1,0]`. Both the exhaustive support method and the
separate existence-circuit search establish the increase. This second key
eventually dies before the study's N9; the first key does not.

The mathematical error is that fewer allowed states preserve non-fullness
but do not preserve **minimal** non-fullness. A smaller forbidden support
may lose the top or target member, and every crossing support may then
contain an already constrained proper part. Relevant assertions occur in
`design.md:15`, `preregistration.md:37-38`, and `level_reach.md:15`.

## Adjacent-level composition needs hypotheses

The adjacent-level condition alone does not imply a bond of size span+2.
For two knots NAE(a,u,v) and NAE(u,v,b), with levels `{a}`, `{u,v}`, `{b}`,
all 16 assignments were checked. There are 10 allowed states. The only
bonds are the two displayed triples; none holds both a and b. The two
knots share both intermediate distinctions. The actual top2 counterexample
above also has one connected 31-distinction constraint component and no
crossing bond. A precise overlap/composition condition is required before
the ruler explanation can serve as a theorem or settled premise.

`countermodels.json` additionally contains a six-distinction exact example:
start with NAE(a,b,c), then add NAE(a,c,d), NAE(a,c,e), NAE(a,c,f),
NAE(d,e,f). The added knots force a != c, making the first knot redundant.
L(a,b) changes from 3 to none. Every state and every support was directly
enumerated for this small example.

## Evidence, limits, and replay

`summary.json` records coverage, source/input SHA-256 hashes, actual
population membership, and the three targeted solver comparisons.
`brute_N4_cap7.jsonl`, `enriched_results.jsonl`, and `comparison_N4.json`
retain per-query counts, results, and exclusions. The three
`actual_*monotonicity*` families retain keys, witnesses, knots, and complete
state tables where available. The N5 state-table attempt stops after
8,193 states and is explicitly incomplete; it supports no unrestricted
absence conclusion. `source_controls.json` records control outcomes.

Replay the core work from the repository root:

```bash
.venv/bin/python -B research/LEVEL-REACH-20261114-001/referee-R1/codex/brute_audit/brute_supports.py --N 4 --k0 2 --cap 7 --per-stratum 2 --output research/LEVEL-REACH-20261114-001/referee-R1/codex/brute_audit/brute_N4_cap7.jsonl
.venv/bin/python -B research/LEVEL-REACH-20261114-001/referee-R1/codex/brute_audit/compare_and_extend.py compare
.venv/bin/python -B research/LEVEL-REACH-20261114-001/referee-R1/codex/brute_audit/compare_and_extend.py extend
```

Each executable used one compute process; every command was below twenty
minutes. The completed larger panel took seconds apart from one approximately
19-second primary cap7 case. The additional top2 absence check through 7
took approximately 42 seconds and made 20,268,365 SAT calls. The bounded
top2 search considered 383 descriptions and 800 finite-before comparisons
before finding its first counterexample. The fixed-top search stopped
after its two prioritized keys. There is no further search pending.

These are exact finite calculations with separately authored same-task
algorithms, not external replication. The independent searches share the
installed SAT solver, and this lane did not create LRAT certificates.
Complete small direct truth tables and the explicit minimality mechanism
provide additional checks on the substantive counterclaim.

Recommended referee action: retain supported finite census results subject
to the other referee lanes; correct the monotonicity interpretation; require
explicit conditions for adjacent-level composition. No canonical knot-test
change is proposed.
