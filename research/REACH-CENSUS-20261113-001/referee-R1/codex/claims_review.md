# REACH-CENSUS-R1: construction, bounds, and the ray reading

**Verdict for this lane: Confirmed with fixes — Block against the broad
depth/counting reading; Not a block to the first-ray equations.** The S1–S4
implications and the distinction between a first-ray result and an
unrestricted least-bond result are sound as stated in the frozen design. The
roughly 70/30 split is measured, not settled by construction. The last-call
stress test blocks the ray-independent reading, while a chosen-ray
replacement is a Narrowing. Exact-value wording for bounded certificates and
the assertion that all validation gates passed need qualification.

Scope: `epic REACH-CENSUS-20261113-001`, referee lane for points 5 and 6 and
validation coverage. This is a prose/mathematical claim audit with aggregation
of permitted data, not an independently reimplemented DP or a new theorem.
The enclosing task independently checks sample last-ray results. No file in
the prohibited experiment `codex/` directory was opened or imported. Only the
two `claims_review.*` files are written by this lane.

## 5. What follows by construction

The exact definitions are in `codex_spec.md:46–82`. In the frozen order:

- **S1:** the usual limit allows no state, so no bond meeting the stated
  endpoint condition exists.
- **S2:** the flattened main has no self-holding call, so the required copy
  sequence does not exist.
- **S3:** S has no own distinctions, so there is no own distinction of its
  depth-s copy available as the required endpoint.
- **S4:** every own distinction of S is free and independent of the ray's
  constraints. A set containing one cannot be minimally constrained: its
  other members already account for any constraint.

These implications are definitional or one-line arguments. Their **shares**
are still measured properties of the sampled descriptions. The preregistration
correctly says, “properties of the definition of L_ray and of the code, not
findings” (`preregistration.md:46–48`). The measured counts of which
descriptions satisfy those conditions are not uniform theorems about other
description languages, weights, or caps.

Finite state, nonnegative costs, the graph-class implications, and the
existence of a residue-sensitive eventual description are likewise inherited
method facts. They do not force a majority into either bounded or growing.
The predecessor referee explicitly separates “Settled by construction” from
“The rates and counts per family are the substance”
(`research/PROVED-RATE-20261113-001/referee-R1/report.md:76–77`).
Thus neither the roughly 70/30 split, its similarity across the two fate
cells, nor the frequencies of rates and bound certificates is settled by
construction. They require the measured classes and sample weighting.

**Narrowing — the no-depth wording.** “Nothing below the top three
distinctions” (`reach_census.md:46–47`) is stronger than S2/S3. In a
multi-definition family main can have more than three ports or additional
own distinctions even when S adds none. For example the permitted
`families.jsonl.gz` decompressed line 12 is S3 with `n_defs=2`, `k_main=5`,
`main_block_size=5`, `s_own=0`. The correct statement is that the specified
ray has no new own-distinction endpoint at increasing copy depth. Keep
no-depth weight, construction-absent weight, and computed absence separate,
as the advisor requested (`advisor_review_answer.md:5`). “Absence is typical”
as a combined label includes the no-depth cases; it must not be read as a
majority finding of computed absence among families with eligible endpoints.

## Which typical claims use a one-sided bound

P1's majority claim is valid with its frozen denominator and conservative
treatment of unresolved cases. The exact predicate is eventual boundedness
of the **first-ray** least-bond size, not merely zero liminf. The
preregistration defines “Typical” by the lower interval endpoint exceeding
one half (`preregistration.md:63–66`), and P1 explicitly counts mixed and
unresolved against bounded (`preregistration.md:78`).

The supplied summary reports, for P1's forever-cell denominator, 30,431
certified bounded draws among 44,236 draws in bounded/grows/mixed/unresolved:
the conservative share is 0.6879238629, the optimistic share 0.7058956506,
and the bootstrap interval is [0.6834222797, 0.7102954330]. These values are
read from `summary.json`, JSON pointer
`/cells/forever/computed/p1_bounded_conditional_share`; this lane did not
replay the bootstrap. A lower bound already above one half is sufficient to
establish that majority under the registered rule. This is not the error of
calling a phenomenon rare from a lower bound alone.

There are two separate one-sided transfers that the report must retain:

1. A ray bond is an available candidate in the full relation, assuming the
   exact side-limit projection in the specification. Consequently bounded
   first-ray size certifies an upper bound on unrestricted least-bond size.
   The unrestricted bond can be smaller. First-ray growth and absence do
   not supply a lower bound on unrestricted size or prove its absence.
2. A positive bounded certificate found in an incomplete graph remains a
   witness; a positive cycle mean in an incomplete graph cannot certify
   growth. The frozen class rules already make this distinction
   (`codex_spec.md:96–103`).

The design states the appropriate conclusion: “A bounded ray bond bounds the
true least bond … from above; growth and absence are ray-only”
(`preregistration.md:52–53`). The advisor requires “only as an upper bound”
(`advisor_review_answer.md:17`). Therefore a majority upper-bound conclusion
survives for the broader bond in that same conditioned sample; an exact
70/30 bounded-versus-growing split for unrestricted bonds does not.

**Narrowing — certificate size and onset are upper bounds.** Conclusion 5's
“bounded reach settles at 3 members … from depth 1 to 12”
(`reach_census.md:40`) reads as an exact eventual value and exact onset. The
permitted predecessor `exact_eventual_bound` uses the first BFS representative
for each residue and takes the maxima of their cost and depth
(`research/PROVED-RATE-20261113-001/referee-R1/codex/recompute.py:345–366`).
It establishes a sufficient uniform cost bound and sufficient onset, not an
optimal uniform bound, minimal onset, or constant eventual value.

The data demonstrate the distinction. In `families.jsonl.gz`, decompressed
line 262 has `uniform_cost_bound=5`, `onset_depth=3`, but every reported
`L_ray(1..30)` is 3. Across the 29,460 bounded family records, 6,795 have a
reported value after the certificate onset below the certificate bound. In
`alt_growing664_families.jsonl.gz`, line 8 has bound 3 and onset 2 while its
reported values alternate 2,3 through depth 30. Replace “settles at” by
“has a certified upper bound of … from a sufficient onset …”. The
distribution of certificate values remains a valid measured result.

## 6. What the last-call stress test corrects

Aggregating the permitted stress-test file gives exactly 224 distinct rows:
131 bounded, 87 grows, 2 lost at large depths, 1 none at any depth, and 3
unresolved. All 131 bounded rows carry `eventually_bounded=true`; their
certificate bounds are 3 (96), 4 (32), or 5 (3), with sufficient onsets
between 1 and 11. Their 30 recorded values are finite. Of these bounded
rows, 125 graphs are complete and six incomplete; the latter are admissible
positive certificates under the frozen rule. This aggregation confirms the
reported counts, not the independently recomputed validity of each graph.

Thus, subject to sample certificate validation, for these 131 families there
is an eligible copy at every sufficiently large depth with a ray-supported
bond of at most five members. This defeats the inference that growth of the
first-ray quantity establishes growth of the least bond to **any** copy at
that depth. It says neither that all other rays are bounded nor that the
first-ray target's unrestricted least bond has been computed. The report's
phrase “the distance to one copy” (`reach_census.md:42`) should instead say
“the least size with members restricted to the first ray and a target in
its chosen copy”; the unrestricted size to that same copy can also be smaller.

**Not a block to the earlier first-ray equations.** Their technical objects
and scope were explicitly first-ray:

- PROVED-RATE asks for behavior “along a ray”
  (`proved_rate.md:17–18`). Its growth conclusion says “for ray bonds only”
  (`proved_rate.md:30`), its answer leaves side-branch shortening open
  (`proved_rate.md:40`), and its cutoff excludes “other rays”
  (`proved_rate.md:53–54`). Its interpretation is headed “Counting inside,
  proved along a ray” (`proved_rate.md:45`).
- BOND-DEPTH defines the first-SELF ray (`bond_depth.md:11–13`), its standard
  question is “along one derivation ray” (`bond_depth.md:21–22`), and its
  interpretation explicitly says “along one ray; side branches could
  shorten the true bond” (`bond_depth.md:51–52`).

The stress test does not falsify those mathematical statements. These scope
limits were present before this stress-test correction: in the original
PROVED-RATE note at commit `c3c951269`, the Answer leaves side-branch
shortening open (line 39), the Reading is headed “proved along a ray”
(line 44), and the cutoff excludes other rays (lines 50–51). Original
BOND-DEPTH at `559be58a8` says “within depth 30 and along one ray” (line 45).
They are not qualifications invented after the stress test.

**Block against the broad published depth/counting reading.** The actual
overreading is the move from the restricted object to “the law's reach
measures depth there, as on a ruler” (`proved_rate.md:46`; original
`c3c951269:45`) and “counting inside … appears in more than a third”
(`bond_depth.md:39–40`). Read as a ray-independent count of copy depth, that
claim is contradicted for the 131 certified countercases: the whole-depth
least bond is bounded above, even though the first-ray quantity grows. No
first-ray lower bound establishes the stronger reading. Against that claim
under test, the correction rubric's Block applies
(`docs/CORRECTIONS.md:40–48`); this is more than a stylistic change to an
interpretation. Dependent claims using this unrestricted inference must stop
or replace it with the restricted result.

**Narrowing describes the surviving replacement.** A statement about the
members restricted to one chosen ray remains valid, and preserves all the
first-ray rates and bounds. That replacement is scientifically useful, but
the fact that it survives does not make the broad reading true. Thus the
existing entry's single “Narrowing” label (`docs/CORRECTIONS.md:203–217`)
should distinguish **Block to the broad reading** from **Narrowing to its
chosen-ray replacement**, while explicitly preserving the equations. The
evidence does not justify declaring the entire earlier numerical studies
refuted.

## Validation coverage

**Not a block — clarified G1 comparisons.** The preregistered C2 amendment
limits G1 comparisons to graphs complete in both runs and lists the rest as
not comparable (`preregistration.md:108–109`). The permitted gate file has
664 distinct keys, each present twice; selecting the last record gives 644
`passed=true`, 20 `passed=null`, and zero mismatches. The top-level gate JSON
still has `passed=null` with 40 pending field comparisons. These do not
contradict the amended 644-family statement, but the machine status should
be described as reconciled against C2, not as an unqualified original-G1
pass. Duplicate rows are not 1,328 independent comparisons.

**Narrowing — G3 remains incomplete.** The frozen specification requires
150 independent brute-force panel families (`codex_spec.md:124–131`), and
the preregistration says “Any G0–G3 failure invalidates the run”
(`preregistration.md:89`). The note reports 139 finished and 11 largest
cases unfinished (`reach_census.md:36,77`). No disagreement among the 139 is
valid evidence; 65 several-definition families exceed the numerical minimum
of 40. It does not cover the unfinished larger cases or complete the
frozen 150-family gate. Say “G3 incomplete; no disagreements in the 139
finished cases”, rather than “gates passed”. This is a coverage restriction,
not evidence that the computed values are false. It **blocks an unqualified
assertion of full frozen-gate completion** until the missing coverage is
supplied or an explicitly post-run acceptance change is disclosed. Whether
the enclosing task's additional independent large-block checks close the
material scientific gap is for the lead referee to reconcile.

## Strongest supportable conclusion

Under the registered capped description sampling, many descriptions cannot
supply the required fresh endpoint by construction. Among the registered
forever-cell draws with potentially persistent first-ray bonds, more than
half have certified bounded first-ray least-bond size even with all
unresolved counted against bounded. The approximate 70/30 split is a
sample-weighted first-ray result, not a construction theorem or a split for
unrestricted least bonds. In 131 of the 224 complete-at-census-cap first-ray
growers in the stress-test domain, a last-call positive certificate supplies
a bond of at most five members at every sufficiently large depth. Therefore
first-ray growth cannot by itself establish a choice-independent count of
copy depth. Certificate values and onset depths are sufficient upper bounds.

Lead with the Block against the broad depth/counting reading, then preserve
the valid first-ray results and make the Narrowings above. Gate completion
and stronger dependent whole-depth claims require their own explicit closure.
