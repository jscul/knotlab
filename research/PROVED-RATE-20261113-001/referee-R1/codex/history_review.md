# History, summary, and wording audit

**Verdict: Confirmed with fixes for the merged roster and counters.** The
508/92/64 batch history is consistent with the permitted merge description;
the actual batch merge and causes of termination cannot be independently
verified because the original batches and logs are forbidden inputs.

This is the independent lane for points 5 and 6 of the referee brief, within
epic `PROVED-RATE-20261113-001`, referee `referee-R1`. It does not independently
recompute reachable graphs, cycle means, or the sufficient boundedness test.
No other referee's artifacts were used.

## 5. Roster, counters, and run history

The permitted BOND-DEPTH `families_one_def()` generator, with its permitted
LIMIT-STATE and dlang dependencies, enumerated exactly 664 families. The
merged `rates_all.jsonl` has exactly those indices, once each, in increasing
order. There are no missing, extra, or duplicate family rows. The output JSON
retains the complete expected definitions and index roster, their hash, and
source hashes, including the underlying sampled-description files.

All top-level and nested scientific counters in `summary.json` follow from
the submitted rows. Exact fraction strings agree with their float fields;
`zero_mean` agrees with the exact fractions.

| Counter | All 664 rows | Complete graphs only |
| --- | ---: | ---: |
| Complete graphs | 655 | 655 |
| Positive minimum cycle mean | 227 | 226 |
| Zero minimum cycle mean | 425 | 417 |
| No accepting cyclic component (`lambda = None`) | 12 | 12 |
| Pass original `bounded_all` sufficient test | 309 | 305 |
| Zero mean and `bounded_all = false` | 112 | 112 |

Five partial rows have uncomputed `bounded_all`; four of them have zero mean.
The nine partial indices are 206, 277, 392, 619, 820, 1018, 1048, 1061, and
1231. Partial results must remain distinct from complete-graph results.

Every one of the 14,000 submitted `L_recomputed` entries agrees with the
corresponding permitted BOND-DEPTH record. There are 653 records with `L`:
644 have complete graphs and nine have partial graphs with their gate marked
`checked_partial_graph`. Eleven complete families have no prior `L`, so their
gates are correctly marked unchecked. This comparison verifies the submitted
arrays against prior records; it is not an independent DP computation.

The registered P1 numerator is **644/653 = 98.62%**. The overall completion
share is **655/664 = 98.64%**. P2 is **214/240 = 89.17%**, below its registered
90% threshold. P3, as the original sufficient-test frequency, is
**117/163 = 71.78%**, below its registered 90% threshold. No subsequent stronger
test should silently change the frozen P3 decision rule.

The operational record classes reproduce exactly: bounded 97, rising 240,
flat 163, capped 43, and unclassified 121. There are actually 135 nonempty
records shorter than eight depths. Fourteen already have unequal finite
values and are capped; the remaining 121 retain the stated short-record
ambiguity. Thus “unclassified when a record has fewer than eight depths” is
too broad. Explicitly excluding `INF` from a constant finite tail, permitting
`INF` in that tail, or first filtering finite values gives the same counts on
these data; this agreement does not resolve the specification in general.

The merge script was read strictly as text and was never imported or run.
It names `rates_first_508.jsonl`, `rates_next_92.jsonl`, and
`rates_last_64.jsonl`, then uses `rows.setdefault(r["idx"], r)`. That operation
silently retains the earliest row when a family appears twice. Therefore:

- The merged result proves final roster coverage and uniqueness.
- It does not prove that the source files contain 508, 92, and 64 distinct,
  disjoint families, or that duplicate source rows agree.
- It cannot establish the session's termination cause, the second run's
  out-of-memory stop, an unchanged runner, actual worker counts, or timings.

The summary's `wall_seconds = 0` and `workers = 7` are supplied constants in
the visible `make_summary(rows, 0, 7)` call, rather than reconstructed run
history. The 11-minute, 20-minute, 50-GB, “right first time,” independent
cycle-enumerator, and effort-saved statements remain owner-reported history
under this boundary. None is independently confirmed by the allowed rows.

Read-only Git inspection confirms that the specification and preregistration
were committed in `43bc81620` at 2026-11-12 19:39:16 −0800, unchanged through
the current HEAD; the result-bearing commit is `c3c951269` at 20:11:20 −0800.
This establishes repository ordering, not the forbidden runtime history.

## 6. Wording and what the construction already settles

The ray restriction is handled correctly in the explicit caveats in
`proved_rate.md`: every finite ray-supported bond is admissible for the true
minimum, so **true least bond ≤ least ray bond**. Bounded ray witnesses
therefore provide upper bounds for the true minimum. A positive ray rate
supplies no lower bound for the true minimum, which could use side branches.
Retain that qualification in the interpretation paragraph as well: “the
shortest chain of constraint” and “as on a ruler” can otherwise suggest an
unrestricted bond-distance theorem. The measured cost counts distinctions
in a ray-supported bond; it does not count constraint rules or force a member
at every intervening depth.

Use **“every sufficiently large depth”** for the `bounded_all` consequence,
as the preregistration itself says “from the empty-W cycle's start on.” A
reachable accepting empty-W cycle controls all later depths after its finite
prefix. The test alone does not check earlier depths. The number 305 is the
count passing this sufficient test on complete graphs, not the number proved
to fail every other boundedness criterion. Likewise, 112 further complete
families have zero mean and fail the sufficient test; that does not prove
they are bounded only on a progression.

The 26 rising-record families with zero mean are indeed exactly the 26 whose
recorded values are constant from depths 20 through 30. Sixteen pass the
original `bounded_all` test. The wording “they rose early and then stopped”
asserts eventual behavior not implied by a finite plateau plus zero liminf
alone; use those two verified statements unless additional evidence is cited.

The exact positive complete-graph rate distribution is:

| λ | Families |
| --- | ---: |
| 1/7 | 1 |
| 1/6 | 7 |
| 1/4 | 8 |
| 2/7 | 1 |
| 1/3 | 40 |
| 3/8 | 1 |
| 2/5 | 1 |
| 1/2 | 95 |
| 2/3 | 3 |
| 1 | 64 |
| 3/2 | 1 |
| 2 | 4 |

The answer's “one member per one to six levels (or two per level)” omits
1/7 and the intermediate fractions. Say “positive liminf rates between 1/7
and 2 distinctions per level,” retain the distribution, and keep the
all-depth lower-bound statement separate from an exact rate per length
residue. No rate-per-residue result was requested or supplied.

For the 12 complete families with no accepting cyclic component, sufficiently
long accepting walks do not exist: **there is no ray bond**, represented by
`INF`, at those depths. “The ray bond vanishes” must mean disappearance of
the witness, never a bond of cardinality zero. Two families, 580 and 762,
have no ray bond at any recorded depth; ten have finite early values and
then `INF`. All 12 lie in the current capped or unclassified classes, not
in the current bounded class. The current “bounded includes the 10 families”
sentence mixes the older BOND-DEPTH label with the specification's new
operational classes. Every finite submitted bond size is at least two.

Finite-state closure in principle is supplied by the construction: both F
and G are subsets of the 256 possible interface masks, giving at most
2^512 pairs. The measured P1 result is closure below the two-million-node
resource cap in the reported number of families. It is not discovery that
the state space is finite. Similarly, all transition costs are nonnegative
cardinalities, and a middle transition has cost zero exactly when W is empty.
Therefore every zero-mean cycle consists entirely of empty-W transitions.
The resulting implications of zero mean and the accepting-cycle test are
mathematical consequences of the construction; the family counts and
which accepting components survive trimming are the census results. The
visible note's attribution to established minimum-cycle-mean methods keeps
that distinction broadly clear, subject to the wording fixes above.

## Required fixes and limits

- **Block, for certification of the detailed run history only:** the source
  batches and logs are outside the permitted evidence boundary. Mark their
  counts, merge disjointness, OOM, runner identity, and timings as unverified
  owner-reported history. This is not evidence of a bad merge and does not
  block the verified final roster or counter arithmetic.
- **Narrowing:** replace unqualified every-depth boundedness with eventual
  boundedness, and identify 305 as a sufficient-test count. Preserve P3 as
  the preregistered test's outcome.
- **Narrowing:** avoid interpreting positive ray lower-bound rates as growth
  of the true minimum or as a full bond-distance ruler. Retain “liminf” and
  the unresolved length-residue qualification.
- **Narrowing:** replace “rose early and then stopped” with the verified
  finite plateau and zero-mean statements unless a stronger certificate is
  cited.
- **Narrowing:** say no ray bond exists eventually for the 12 `lambda=None`
  cases; do not identify `INF` with zero size or finite boundedness.
- **Not a block:** clarify 644/653 versus 655/664; correct the rate range;
  separate the older bounded label from the new classes; state the 135/121
  short-record distinction. The submitted arithmetic itself is consistent.

## Reproducibility and files

The corrected comparison script was frozen at SHA-256
`2f46c0b0388007fc73710ca5d4e067e58a03367e02ab5c26e39235b34081e510`
before execution. Its comparison found zero roster, class, gate-field,
top-level-summary, or nested-counter discrepancies. It ran in one Python
3.13 process in less than one second and used under 47 MiB peak RSS, with
7 GiB address-space, 550-second CPU, and 580-second wall limits.

The first audit pass conservatively treated every short record as ambiguous
and initially accepted only the complete-graph gate-status label. Its
diagnostics reflected those two auditor assumptions. The exact first-pass
script and raw output are preserved inside `history_audit.json`; the
corrected rules and their reason are explicit. This correction changes no
study inputs and no submitted rows.

Only these three owned files were written:

- `history_audit.py` — independent enumeration and counter comparison, with
  a runtime guard against opening the forbidden producer subtree.
- `history_audit.json` — full roster, raw per-family comparisons, hashes,
  summary calculations, resource metadata, provenance limits, and preserved
  earlier auditor pass.
- `history_review.md` — this review.

Actual `CODEX_THREAD_ID`: `01a1d31d-baed-7ca0-8715-998dad46593e`.
