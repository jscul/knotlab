Confirmed with fixes

## 1. Fresh recomputation

Independently rebuilt **95 complete families**, selected by increasing `(reported node count, idx)`: the 40 smallest, the 10 smallest in each requested stratum, and all 46 disputed “flat” families, deduplicating overlaps. [sample_selection.json](sample_selection.json) freezes their identities and input/source hashes. This is a targeted sample, not an independent rerun of all 655 complete graphs.

[recompute.py](recompute.py) uses integer bitsets for the sets of interface masks, direct assignment enumeration for block relations and their greatest fixed point, breadth-first graph construction, reverse trimming, iterative SCC decomposition, and exact rational Karp calculations. Its sole scientific import is the permitted BOND-DEPTH family enumerator; it never calls that file's DP or table helpers. The forbidden implementation and logs were neither opened nor imported. The owner's merge was read as text, never executed.

**All 2,375 comparisons across 25 mathematical/graph/gate fields agree.** This includes reachable and trimmed node counts, transitions, SCC diagnostics, exact and floating rates, all empty-cycle diagnostics, `bounded_all`, `zero_mean`, and recomputed recorded-depth values. There are **0 mismatches in 1,885 depth values across 94 families**. Family 1222 has no prior `L`, and its gate remains unchecked rather than being counted as a pass. Timing fields are not equality targets; record classes and all-row summary counters were separately audited.

Controls passed: 210 synthetic weighted graphs compared with explicit simple-cycle enumeration, 369 block operations compared with direct set semantics, exact 1/2 and 1/7 controls, and matched counterexamples rejecting stronger boundedness claims. A separate source review found no demonstrated semantic defect. This is V2 independent reimplementation within one AI-assisted task, not human or external replication.

The 95-family run took 10.36 seconds; its longest family took 1.30 seconds, and peak RSS was 53,296 KiB (52.1 MiB). Each command used one process and the required `.venv/bin/python -B`; the fresh runner imposed 7 GiB address-space and 540-second per-family limits. No computation approached the requested resource ceiling. Raw comparisons are in [recomputed.jsonl](recomputed.jsonl); reconciliation is in [referee_summary.json](referee_summary.json).

## 2. Lower bound and asymptotic meaning

Let `T` be the complete reachable and acceptance-co-reachable state set, with `t = |T|`. An accepting depth-`s` walk has `s−1` middle transitions. Removing cycles leaves a simple walk with at most `t−1` transitions. Removed cycles cost at least their length times λ; all remaining costs are nonnegative. Therefore

`L_ray(s) ≥ λ((s−1)−(t−1)) = λ(s−t)`.

Thus **the trimmed count is valid and stronger**; using all reachable nodes is also valid. A minimum-mean cycle has fixed reachable entry and accepting exit walks. Repeating it gives depths `h+kd` and cost at most `A+k·d·λ`. Together with the lower bound, this proves **`liminf L_ray(s)/s = λ`**.

For λ > 0 this is a linear **lower bound**, with an additive constant. It neither guarantees a finite ray bond at every depth nor a common limiting slope across residues. The theorem interprets absent bonds as genuine `+∞`; `10^9` is only the finite-file sentinel. With no productive cycle, `L_ray(s)=+∞` for all `s>t`, not zero. Full arguments and counterexamples are in [math_review.md](math_review.md).

## 3. `bounded_all` and exact boundedness

**Sufficient, not necessary.** After a fixed walk reaches an empty-`W` cycle on which every state closes, arbitrarily many zero-cost steps can be followed by a closing of uniformly bounded cost. This proves boundedness at every **sufficiently large** depth. It alone says nothing about earlier depths. Nonnecessity already occurs in family **130**: the cycle states need not close directly when a fixed positive-cost exit leads to acceptance.

For an exact test, collect all productive zero-cost cycles and let `P` be the least common multiple of their lengths. Exhaustively explore `(state, middle length mod P, has visited a zero-cycle state)`, retaining every middle transition before and after that visit. Accept when the flag is true and closing is finite. Eventual uniform boundedness holds **iff all P residues accept**. Each residue witness can be extended by P zero-cost steps at its cycle visit. Conversely a cost bound C permits at most `floor(C)` positive transitions; a sufficiently long such walk must contain a zero cycle. This proves necessity as well as sufficiency.

| Independently checked group | Families | Eventually bounded | Certificate onset | Uniform cost bound |
| --- | ---: | ---: | ---: | ---: |
| All disputed flat, zero-mean, `bounded_all=false` | 46 | **46** | s ≤ 3 | ≤ 4 |
| Ten smallest other zero-mean-only families | 10 | **10** | s ≤ 3 | ≤ 3 |

The 46 use period P=1 in 43 cases and P=2 in three cases. Twenty-nine have certified upper bound 3 and seventeen upper bound 4. Fresh finite-prefix replay also verifies the depths before onset, so these **46 are bounded over every depth s≥1**. The ten other cases likewise pass their finite-prefix checks. These are upper bounds, not assertions that each bound is the exact least eventual value.

Consequently the original 305 complete-graph sufficient positives plus these 56 additional, disjoint positives establish **at least 361 eventually bounded complete families**. This combines the submitted 305 certificates with the 56 fresh certificates; it is not a fresh reconstruction of all 305. The remaining 56 complete zero-mean-only families were not classified here. All 163 flat families are now covered by the original 117 positives plus these 46. The preregistered P3 still fails: it specifically tested the original sufficient predicate, not this later stronger test.

## 4. Capped graphs

For an authentic retained subgraph H, accepting walks are a subset of the full graph's: `L_H(s) ≥ L_full(s)`. When H has a productive cycle, **`λ_H ≥ λ_full`**. A positive partial mean therefore supplies **no positive lower bound** on the full ray-bond rate. A missing cycle in H also proves no eventual nonexistence in the full graph. Agreement through depth 30 cannot repair this gap; the controls give a partial positive mean and full zero mean despite an agreeing finite prefix.

Positive witnesses do transfer. A verified reachable zero cycle with an accepting exit proves progression boundedness and liminf zero, since weights are nonnegative. An authentic all-closing zero cycle proves eventual every-depth boundedness even if other parts remain unexplored. Global negative classifications require completed exploration. No capped graph was substituted into the independent complete-family sample.

## 5. Roster, summary, and run history

The permitted enumerator yields **664 families**, and `rates_all.jsonl` contains exactly that roster once each, with no loss, extra index, or duplicate in the final file. Every scientific summary counter follows from the rows. Separately, all **14,000 submitted** depth values equal their BOND-DEPTH records; this all-row array comparison is distinct from the fresh 1,885-value DP replay above.

| Complete-graph result | Count |
| --- | ---: |
| Complete | 655 |
| λ > 0 | 226 |
| λ = 0 | 417 |
| λ undefined / no productive cycle | 12 |
| Original `bounded_all=true` | 305 |
| λ=0 and original `bounded_all=false` | 112 |

P1 is **644/653 = 98.62%** among prior records with `L`; overall completion is **655/664 = 98.64%**. The eleven other complete families have no prior `L`. P2 is **214/240 = 89.17%**, and P3 is **117/163 = 71.78%**: both fail their registered 90% thresholds.

**The detailed three-batch history is unverified under the required read boundary.** The permitted merge text names the 508/92/64 batches, but their files and logs are forbidden. Its `setdefault` silently keeps an earlier duplicate, so final uniqueness cannot prove source disjointness, source counts, agreement of duplicate source rows, or the claimed out-of-memory stop. No evidence of a faulty final roster was found. Likewise the runner's unchanged identity and termination causes remain owner-reported. Summary metadata `wall_seconds=0` and `workers=7` are supplied constants in the merge, not recovered runtime measurements. See [history_review.md](history_review.md) and [history_audit.json](history_audit.json).

## 6. Wording and construction

The explicit ray/true-bond caveats are correct: **`L_true(s) ≤ L_ray(s)`**. Bounded ray witnesses transfer as upper bounds; positive ray lower bounds do not transfer through minimization over side branches. Preserve this qualification in the “shortest chain”/“ruler” interpretation too: the cost counts distinctions in a ray-supported bond, not constraint rules or a proved unrestricted metric.

Replace “vanishes” with **“no ray bond exists at sufficiently large depths”** for λ=None. Two such families have no ray bond at any recorded depth; ten lose it after finite early depths. None belongs to the current specification's bounded record class. Replace “one to six levels” with **“positive liminf rates from 1/7 to 2 distinctions per level”**, retaining the full fraction distribution. “The 26 rose early and then stopped” should remain the verified zero-mean result and depth-20–30 plateau unless stronger eventual evidence is cited; zero mean alone does not imply eventual constancy.

Finite-state closure in principle is built in: each of F and G is a subset of 256 masks, so there are at most `2^512` pairs. What the census establishes is closure **below the two-million-node cap** in 655 families. Likewise nonnegative weights and the equivalence between zero-cost cycles and empty-`W` cycles follow from construction. The minimum-cycle-mean and boundedness implications are mathematics of the recurrence; family-specific rates and counts are the substantive census outcomes. The note broadly makes this attribution correctly.

## Fixes

- **Block — detailed run-history certification only:** mark the 508/92/64 source counts/disjointness, OOM, unchanged runner, and timings as unverified owner-reported history. Independently certifying them needs evidence outside the currently permitted inputs. This does not block the final roster or sampled computations.
- **Narrowing — boundedness:** use “every sufficiently large depth” for the sufficient theorem and identify 305 as the original predicate's count. Do not label its 112 failures as bounded *only* on progressions. Cite the 46+10 new certificates and the resulting lower count 361; keep the frozen P3 outcome unchanged.
- **Narrowing — growth and absence:** state a ray-only linear lower bound with additive constant and liminf rate, permitting absent depths. Interpret `INF` as no witness, not zero size or a finite bounded bond. Do not infer eventual constancy from a finite plateau plus λ=0.
- **Not a block — presentation:** distinguish 644/653 from 655/664, include the 1/7 rate, and separate old BOND-DEPTH labels from current record classes. Of 135 short nonempty records, 121 remain ambiguous and 14 are already capped; “all shorter than eight are unclassified” is inaccurate. The summary arithmetic itself is consistent.

No canonical definition, study result, correction register, ticket, Git state, or publication was changed. The requested fixes are recorded here for the owner; all writes stayed in this referee directory.

## Files written

- [recompute.py](recompute.py), [sample_selection.json](sample_selection.json), [recomputed.jsonl](recomputed.jsonl), [smoke.jsonl](smoke.jsonl): fresh reconstruction, frozen selection, per-family comparisons, and retained smoke evidence.
- [controls.py](controls.py), [controls.json](controls.json): independent small-cycle, direct-set, and boundedness controls.
- [summarize_referee.py](summarize_referee.py), [referee_summary.json](referee_summary.json): reconciliation and compact results. Its initial validation assumed every sampled family had a prior `L`; correcting that audit-only assumption retained family 1222 as unchecked and changed no computation.
- [math_review.md](math_review.md), [math_controls.json](math_controls.json): separate mathematical proofs and twelve explicit counterexample/control models.
- [history_audit.py](history_audit.py), [history_audit.json](history_audit.json), [history_review.md](history_review.md): independent roster, counter, provenance, and wording audit, including preserved earlier auditor-pass evidence.
- [code_review.md](code_review.md): separate review of the fresh implementation.
- [codex_report.md](codex_report.md): this report. The supplied `brief_codex.md` was left unchanged.
