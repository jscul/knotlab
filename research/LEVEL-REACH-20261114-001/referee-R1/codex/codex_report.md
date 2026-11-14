**Verdict: Confirmed with fixes.** The sampled depth-9 least-bond values survive fresh exact recomputation. The general depth-monotonicity claim is refuted, and the literal Q3 membership claim is false. These corrections matter to the proposed ruler proof.

This report concerns finite NAE relations, not a uniform ruler theorem. All new files are in this referee directory. No forbidden study Python/C source or study summarizer was opened, imported, or executed; no network, Git mutation, or publication was used. The previous ADDR referee's action routines and hint-free RUP checker were reused read-only. Other construction, search, classification, and projection code is fresh. The independent lanes are same-task AI checks, not external replication.

## 1. Optimality, freshly

The fixed sample contains 12 chained descriptions, eight direct (four each of `[3,3,3,3]` and `[2,2,2,2]`), six other (three `[3,3,4,4]`, three containing `>10`), four undecided, and two additional Q3 cases. The chained selection deliberately balances six cyclic and six acyclic incidence graphs, restricted to independently measured elimination width at most eight. This is a feasible stratified audit, not a random estimate of census error. Exact keys and selection seed are in [sample_plan.json](sample_plan.json).

All **26 selected decided profiles** agree at all four separations: **104 exact comparisons**. The two additional Q3 profiles also agree, making **112 exact depth-9 cells across 28 complete profiles**, with **zero numerical disagreements**. In particular, all twelve s=4 ruler values are independently 6, excluding every smaller bond, and all nine sampled `>10` cells are independently exhausted through size 10. Complete per-cell results and remaining exclusions are in [audit_summary.json](audit_summary.json).

The main search builds the pattern from the key, then eliminates state variables from the NAE relation, compiling *existence of a completing state* into a Boolean circuit on assumption selectors. A SAT query sets existence false, requires top and target membership, and bounds support cardinality. Each returned forbidden support is tested by projecting **every assignment of every maximal proper subset**, using complement symmetry. A nonminimal support is discarded using an explicitly nonfull proper subset: strict supersets cannot be bonds. The blocked subset itself must also be safe to exclude; cardinality-first exhaustion rules out a smaller crossing bond, and a final audit explicitly verified that **all 56,971 recorded blocked subsets miss at least one required level**. Unsatisfiability after these sound exclusions proves there is no smaller bond; it is not inferred from a successful witness. No forest theorem or ruler formula is assumed. See [fresh_search.py](fresh_search.py) and [search review](cert_audit/search_review.md).

The circuit code is fresh and derived from quantifier elimination. Admitted output metadata, read before implementation, also describes an elimination-circuit route in the study: this is an independent implementation of a related method, not a claim of blind algorithm selection. A separate exhaustive support method supplies the different-method comparison in point 2. Broad direct profiles additionally use Glucose4: the reported support supplies only an upper-bound candidate, while all cross-level pairs supply the fresh lower bound. Width failures are retained as undecided, never converted into `>10`.

The four undecided profiles remain unresolved. Fresh exhaustive checks establish **L(s) ≥ 3** at every separation and **L(4) ≥ 4** for each, with no size-three crossing bond at s=4. These are useful bounds, not exact profiles. See [undecided audit](outcomes/undecided_pair_audit.json).

**Not a block:** the sampled numerical optimality claims survive. **Narrowing:** this is sampled finite computational validation; master-query UNSAT proofs are replayable computations, not retained LRAT lower-bound certificates. The fresh compiler was checked on 61,568 complete selector assignments, 712 finite-relation/search comparisons, 128 builder comparisons, and rejecting mutations.

## 2. Beyond G-brute's tiny patterns

The independent brute panel has **29 descriptions** (26 actual population keys plus three controls), **82 queries** at k0=2: 58 at N=4 through support size 7, and 24 at N=5 through size 4. It enumerated **4,344,938 crossing supports** and made **6,355,842 SAT projection calls**, including a connected 31-distinction pattern exhausted through size 7.

The separate fresh search decided 62 queries and agreed on all 62; 20 elimination-width exclusions remain explicit. Three additional targeted comparisons also agree. Placement builders agree. N=4/5 results are not equated to the study's N=9 values: changing truncation changes the observable. Keys drawn from the study provide shared descriptions, not a same-depth study comparator. [Full findings, controls and replay commands](brute_audit/findings.md); [machine summary](brute_audit/summary.json).

**Not a block:** no optimality mismatch was found in this larger exhaustive panel. These checks exercise the implemented finite search rather than establish a uniform theorem.

## 3. Depth sensitivity and G-mono

The depth panel uses all twelve chained descriptions, plus two direct-3 and two `[3,3,4,4]` descriptions, at **all four separations and both N=10 and N=11**: 128 requested cells. The unchanged baseline decided 119; audited resolution pruning resolved five forest timeouts. **All 124 exact results equal their N=9 values.** Ten chained descriptions retain `[3,4,5,6]` at both deeper truncations; both direct controls retain `[3,3,3,3]`, and both slow controls retain `[3,3,4,4]`. This supports the finite ruler in these cases, with no observed shortening or increase.

The four unresolved cells are:

| Full case | N | s | N=9 value |
| --- | ---: | ---: | ---: |
| `67fdb8d79e16c83f33a68530c2f8b6eb6b8db3c363bee85785379d5659dceacc` | 10 | 4 | 6 |
| same case | 11 | 4 | 6 |
| `db28d1adef8096080a333c57f21faa06430c6c01606617fadaf0fdb630ee4df0` | 11 | 3 | 5 |
| same case | 11 | 4 | 6 |

These are projection-deadline exclusions, not confirmations. [Baseline and depth findings](cert_audit/depth_findings.md), [successful retries](depth_retries.jsonl), and [reconciled results](audit_summary.json) retain the full evidence. A separate 120-second pruning probe on the first unresolved N=11 cell also remained undecided.

**Block — general monotonicity is false.** An actual alive registered description, W_R draw 1185, case
`a0ce47179bf2fb205295a4415dbda9c6d19c17c6ebaaf506331718c8b15300e4`, has key

```text
[1,[1],[0],[0],
 [[0,1,3],[0,6,7],[1,2,4],[2,5,6],[3,4,8],[4,5,8],[4,7,8]]]
```

At the study's fixed **k0=3, s=1**, both truncations are alive, but **L₄(1)=3 and L₅(1)>4**. At N=4, `[7,15,16]` with forbidden values `[0,0,1]` is a bond, and every crossing pair is full. At N=5, all 128 crossing pairs, 6,400 triples, and 158,496 quadruples were exhausted; the separate circuit search agrees. The same key at k0=2, s=1 changes from L₃=3 to **no crossing bond of any size** at N=4, checked using complete state tables. This key's study N=9 union is alive and its recorded profile is `[>10,>10,>10,>10]`. [Exact witnesses and evidence](brute_audit/findings.md).

The error is minimality: adding constraints preserves nonfullness, but can make a proper subset nonfull, destroying an old bond. In a second actual description, the old bond `[1,7,9]` loses minimality when `[7,9]` becomes constrained, and the least crossing bond rises from 3 to 4. Thus “more knots, fewer states” does not prove the asserted inequality. These examples do not claim a violation specifically between N=9 and N=10.

**Block — adjacent-level joining alone is insufficient for composition.** For NAE(a,u,v) and NAE(u,v,b), with levels `{a}`, `{u,v}`, `{b}`, the complete 16-state truth table has ten allowed states and only the two native triples as bonds. No bond holds both a and b. A ruler theorem needs explicit overlap/composition hypotheses and an independent lower bound.

G-mono's data contain **49 of 50 successful keys** and **108 numeric comparisons; all are equal**. There was no recorded L₁₀<L₉, and no increase. The missing case is `0758783d31dde76fe9f2f1e3f17d2f8c077710f5fdd6a8d478363a186001d00b`, which failed memory in the original run and three retries. Two other original memory failures later succeeded. **Block** any claim that the required 50-key gate was completed; retain it as a disclosed incomplete empirical check. [Attempts and comparisons](outcomes/monotonicity.json).

## 4. Certificates

All sampled bond certificates passed: **20 (key,s) cells, 237 nested bond claims, 184 distinct retained CNF/LRAT pairs**. The rebuilt CNF plus forbidden-assignment units equals each stored CNF as a clause multiset, allowing clause reordering; filename and recorded hashes agree. A fresh adapter discarded LRAT hints and used the earlier referee's RUP checker for **3,619 additions**, retaining already proved clauses across deletions. Every proof reaches the empty clause.

Every one of **3,236 state-pool entries** satisfies the rebuilt pattern, and all **4,028 maximal-proper-subset assignment references** cover their declared assignments. Invalid-state, changed-CNF, malformed-proof, and false-refutation controls reject. Hint mutation is intentionally irrelevant to a hint-free checker. [Detailed checks and controls](cert_audit/findings.md).

The complete numeric-certificate inventory has 36,213 claims using 12,644 distinct retained pairs, with no missing referenced numeric pair. This inventory is not a full proof replay. **Block — an unqualified universal-retention claim:** all 23 dead-union records lack a CNF hash, proof hash, or retained name; their textual checker-success assertions do not bind a retrievable proof. Three deterministic weighted-dead cases were independently rebuilt and refuted with Glucose4, and their new DRUP proofs passed hint-free RUP checks ([fresh evidence](dead_recomputation.json)); that does not repair the original 23 records' provenance.

For `>10`, a bond's LRAT proof is not an optimality certificate. The evidence must be complete exhaustion of the bounded candidate search with sound minimality exclusions. The study records describe that exhaustion; the nine sampled cells were independently reconstructed and exhausted. No existence of a larger bond follows from `>10`.

## 5. Outcome rule and frozen verdicts

The full-record recount reproduces all primary labels and weights exactly. Weights count W_R memberships with index <2000; 436 attached later memberships are excluded. There are 1,423 represented accepted W_R draws, 1,412 alive. [Full recount](outcomes/independent_summary.json).

| Outcome | Descriptions | W_R weight |
| --- | ---: | ---: |
| no join | 183 | 234 |
| no bond: disconnected | 188 | 285 |
| chained | 457 | 605 |
| direct | 100 | 71 |
| other | 73 | 67 |
| undecided | 264 | 150 |
| dead | 23 | 11 |

**(a) Direct — Narrowing.** Constant over the four measured separations, including 3, is faithful to the frozen explicit wording “one constant value ≥3.” It supports the operational label **constant for s=1..4 at N=9**. It does not distinguish persistent bounded reach from delayed growth: `[3,3,4,4]` and `[3,3,3,4]` demonstrate why four observations cannot establish an asymptotic distinction. This is not a post hoc classification error, but the unqualified bounded interpretation is too strong.

**(b) Undecided bands — Narrowing.** Only 126 of the 150 undecided W weight are compatible with the ruler; only 91 are compatible with a constant direct profile. Already decided values rule out the others.

| Frozen quantity | Compatibility-tightened bound |
| --- | ---: |
| Q0 operational none / 1,412 alive | **36.76% exactly** |
| Q0 chained / alive | **42.85–51.77%** |
| Q0 direct / alive | **5.03–11.47%** |
| Q1 ruler / frozen denominator 893 | **67.75–81.86%** |
| Q2 direct / frozen denominator 893 | **7.95–18.14%** |

Q0 passes both thresholds even at these bounds. Q1 and Q2 are **not falsified under their asymmetric frozen rules**, but their uncertainty bands do not establish the stated 70% and 10% predictions. “Held” needs that qualification. The denominator 893 actually contains 730 numeric-every-s draws, 150 undecided, and 13 with `>10`; existence of a bond at every s is unproved for the last two groups.

**(c) None — Narrowing.** The frozen no-join/disconnected label is decided: every undecided profile is connected at every s, so adding all undecided weight to that label's upper bound is unnecessary. Mathematical absence of any bond is a different question: connectedness is insufficient, as point 3 shows. Under that semantic reading, even `>10` cases can contribute additional absence; do not call 36.76% the exact share of all mathematically bond-free cases.

**(d) Other.** Its 67 W weight comprises 54 nonconstant numeric profiles and 13 bounded-exhaustion profiles:

| Profile | W weight |
| --- | ---: |
| `[3,3,4,4]` | 45 |
| `[3,3,3,4]` | 3 |
| `[3,3,4,5]` | 3 |
| `[3,4,4,5]`, `[3,4,4,4]`, `[3,4,5,5]` | 1 each |
| `[3,>10,>10,>10]` | 10 |
| `[>10,>10,>10,>10]` | 3 |

Two further numeric profiles, `[2,3,3,3]` and `[2,2,2,3]`, occur only in unweighted E_R.

**Block — Q3 wording/verdict.** Of 2,894 returned numeric anywhere bonds, **26 across 16 descriptions contain a member deeper than the target** (counts by s: 13,2,9,2). All 26 have equal-size in-target alternatives. For example, `58480a08...`, s=1 returns `[7,15,1002]` at levels `[3,4,9]`, with alternative `[7,29,30]`. Both are genuine certified bonds; the fresh optimum is 3. The complete discrepancy list, including full keys, supports, levels, weights, and alternatives, is [q3_membership.json](outcomes/q3_membership.json). The literal “every least bond found lies within target” fails; the weaker “a least bond can be chosen within target” survives in the reported data. The frozen prediction's membership wording and its “needs” failure wording are not equivalent, and should not be collapsed into an unqualified pass.

**Narrowing — Q4/Q5.** Q4's point difference reproduces: 27.33% versus 4.59% non-ruler, difference 22.74 percentage points. The reported 99/40 clusters identify automata under state relabeling and global binary-letter conjugation. A fresh 100,000-replicate independent-by-activity cluster bootstrap gives 95% interval **[-6.57,40.00] percentage points**, retaining the failed verdict. Seven canonical automata occur in both groups; jointly resampling them gives **[0.24,39.63]**, showing sensitivity to unspecified bootstrap choices. Do not promote that post hoc variant to confirmation. Q5 reproduces: bounded 29/45 direct and 10/45 ruler, but 88/165 undecided; polynomial has only one decided bond profile. Exponential W_R is 57/450 direct and 327/450 ruler. The same Wilson convention gives the omitted exponential intervals **9.91–16.06% direct**, **68.37–76.58% ruler**; these descriptive intervals do not handle automaton clustering or undecided censoring. [Details](outcomes/findings.md).

## 6. Thread additions, from provenance JSON only

| Addition | Effect on a correctly decided per-key result |
| --- | --- |
| Budget parameterization; final records all use 300 seconds per (key,s), shared by L_N, L_target and per-target work | Can change completion, timing and undecided outcomes; should not alter an exact value decided by sound search. |
| W_R cut from 4,000 to first 2,000; E_R filtered to bounded/polynomial, frozen before the registered run in the documentary record | Changes the population and aggregate shares; does not change the relation or L for a retained key. The specification permits a pre-run cut. |
| Gzip CNF/LRAT retention named by CNF SHA-256 instead of deletion | Changes auditability and possibly timing; no mathematical change. Numeric retention is present; union-death binding remains the gap above. |
| Memoization caps: 20,000 SAT entries, 1,024 projection entries, 512 retained models | Eviction should change timing, chosen witnesses and undecided cells only. JSON records small-cap controls; they do not by themselves prove source equivalence. |
| Presence auxiliaries replace exponential expansions of support blockers | Intended logically equivalent SAT-query encoding, with unchanged original pattern and state witnesses; 1,620 finite equivalence checks are recorded. No decided value should change if equivalence is correct. |
| Breaking closed-engine lifecycle references | Intended post-computation memory cleanup; no scientific change. |

**Not a block at the documentary scope:** budgets, job hashes, raw-result hashes and numeric retention metadata reconcile. **Narrowing:** JSON declarations cannot establish the semantic equivalence or execution chronology of source versions that this audit was forbidden to inspect. Independent recomputation tests their outputs, rather than certifying unseen edits. [Provenance reconciliation](outcomes/provenance_audit.json).

## Files written and reproducibility

The main implementation is [fresh_pattern.py](fresh_pattern.py), [fresh_search.py](fresh_search.py), and [run_fresh.py](run_fresh.py). [assemble_audit.py](assemble_audit.py) reconciles lane results and validates syntax/JSON. The three audit directories contain their own scripts, JSON outputs, controls, and findings. The optional [resolution pruning](resolution_accel.py) resolves already proved clauses and excludes only nonfull supports missing a required level; it preserves every crossing bond. Its review checked 384 comparisons with complete truth tables and 1,025 derived nonfull supports. Both its failed cyclic benchmark and successful forest retries are retained; it supplements the unchanged baseline.

[validation_manifest.json](validation_manifest.json) enumerates every newly written file with size and SHA-256, excluding the two pre-existing handoff files. It includes complete counterexample tables, compressed checked-state pools, three new dead-union proof pairs, and all exclusions. Commands use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`; replay commands are in the lane findings. No full repository test suite was run. No changes were made to the study, tickets, canonical definitions, or public records.

The downstream proof should retain the verified finite ruler examples, remove general N-monotonicity as a premise, and state a precise composition class before claiming `L_N(s)=s+2`. Census frequencies and sampled optimality checks cannot discharge that theorem.
