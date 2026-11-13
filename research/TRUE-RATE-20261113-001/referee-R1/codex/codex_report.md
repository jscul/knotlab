**Verdict: Confirmed with fixes.**

The ten certificates, carriage counts and all 664 rule identities survive fresh recomputation. Three exact rates also reproduce. The fixes concern cyclic-port wording and the scope attributed to earlier work.

All scientific code here was written from the notes and mathematics. The prohibited TRUE-RATE implementation directory was never opened or imported. The permitted `families_one_def()` supplied an inventory, subsequently checked by independent reconstruction from the sample archives. All writes stayed here; no Git mutation or publication was performed. This is an independent implementation relative to the study (V2), with AI review, not external replication. Results concern the usual infinite allowed-state relation; finite-flip sources were not audited.

## 1. The certificate

**Not a block — confirmed.** I computed `G` by descending iteration of the existential one-copy port map from all eight states. For all ten families, **G = {0,…,7}**. Omitting the first SELF call, retaining the local NAE constraints and replacing every other call by G gives **R₁ = {0,…,7}**. A separately encoded one-copy SAT calculation agrees. The same holds for all 20 carried families.

Direct SAT on a subtree expanded through copy depth 3 found the following bonds. Slots and SELF-call indices are zero-based; a path such as `0/5` means first call, then sixth call, relative to C_s. Every `v` is created in C_s itself; every `w` is created off the first-call ray.

| Family | Carried port slot | Own slot v | Side path / own slot w |
| ---: | ---: | ---: | --- |
| 262 | 1 | 3 | 2 / 4 |
| 269 | 1 | 4 | 2 / 3 |
| 302 | 1 | 3 | 0/5 / 3 |
| 363 | 2 | 3 | 5 / 3 |
| 579 | 0 | 3 | 2/2 / 4 |
| 642 | 1 | 4 | 0/1 / 4 |
| 662 | 0 | 3 | 0/7 / 3 |
| 908 | 1 | 3 | 0/3 / 3 |
| 975 | 0 | 3 | 3 / 3 |
| 1144 | 2 | 3 | 5 / 3 |

Every triple has exactly the six NAE states; all three pair projections have all four states. Repeating with exact-G boundaries at depths 2 and 4 gives identical projections. `knotlab check` independently accepts this six-state relation under K1–K3.

The uniform argument is sound: the outside meets a subtree only through its ports, so its allowed assignments are restricted exactly by R_s. The same map F computes R_{s+1}=F(R_s). Since R₀ is full and F(full) is full, induction gives full R_s for every s. Exact G makes the finite SAT projection equal to the infinite subtree projection. Shifting the displayed bond therefore proves **L(s) ≤ 3 at every positive depth**, rather than merely extrapolating the checked depths. This alone is an upper bound, not a separate exclusion of every possible size-two tie.

**Narrowing — cycles change slots.** For f(j)=a_j and a cycle position p,
`C_s.port[p] = C_0.port[f^s(p)]`. Thus the shifted bond still contains *a* top port, as L(s) requires. It need not contain the same fixed top identity at every depth. A theorem about a prescribed fixed endpoint needs the relevant phases checked. All ten displayed certificates actually use fixed points, and all 20 selected carried families have only singleton cycles, so this wording fix changes none of their conclusions. The census code also handles genuine two-cycles and rejects tails into cycles.

## 2. The carried-port test

**Not a block — all requested counts reproduce.** A family is carried exactly when the partial argument map on slots 0–2 has a cycle.

| Population | Carried | Uncarried |
| --- | ---: | ---: |
| 226 complete, positive-rate ray families | 20 | 206 |
| BRANCH-DEPTH's 432 bounded rules | 320 | 112 |
| Of the bounded rules: exactly three | 320 | 73 |
| Of the bounded rules: eventually exactly four | 0 | 39 |

All 154 conditional-lower-bound rules are uncarried; 65 of the 69 linear rules are uncarried. The complete census contains 50 length-two argument cycles, so counting fixed points alone would be insufficient. Positive controls include cycles of length two and three; negative controls include a chain ending at a fresh local and a tail entering a cycle.

**Narrowing — interpretation.** “112 uncarried” establishes absence of this syntactic identity carry. It does not by itself exclude carrying enforced by constraints, or establish an independently qualified notion of reach.

## 3. Mapping to BRANCH-DEPTH

**Not a block — 664/664 are the same ordered rules.** I reconstructed the archived candidate order and the complete definitions, preserving call and argument order. The 1,341 unique candidates include 976 one-definition candidates; the independent usual-limit calculation excludes 312 and leaves the same 664. Their definition keys, allowed port relations and first-call transition relations all match BRANCH's records. All eight source-file hashes agree with BRANCH's recorded hashes and its outcome/port-table receipt bindings pass.

The `+1` offset converts zero-based archive enumeration to BRANCH's one-based lines; it is not the evidence for rule equality. Offset +1 recovers all 664 identical definitions; offsets 0 and +2 recover none. On the 226 selected rules the outcomes are exactly **66 linear, 144 linear-lower-bound-only, 10 exactly three, six unresolved**. The 66 constructive chain certificates connect ports, resolving the possible mismatch between BRANCH's wording “top distinction” and TRUE-RATE's narrower “top port.”

**Narrowing — “settled 220 of 226.”** Before TRUE-RATE, these were 76 complete qualitative verdicts and 144 conditional lower bounds, with existence still open in the latter group. Exact coefficients were also separate. Say “76 classified outright; another 144 have a proved conditional lower bound,” rather than implying 220 complete growth/existence solutions.

## 4. The 24 closed families

**Not a block — three fresh exact recomputations pass.** I independently implemented marked-assignment summaries, environment-level joins, uncapped least-cost closure, complete ray graphs, trimming and exact rational minimum cycle means.

| Family | Fresh λ_true | Recorded λ_ray | Exact L(s) from the live graph |
| ---: | ---: | ---: | --- |
| 105 | 1/3 | 1/3 | 3 + floor(s/3) |
| 429 | 1 | 1 | s + 3 |
| 874 | 2 | 2 | 2s + 3 |

All 36 available finite reference cells match. The fresh graphs also compute depths 1–30. A second AI reviewer checked the summary argument and the live graphs (three, two and one states respectively); no mathematical blocker was found. A separate replay of the saved graphs verifies exact cost-vector repeats from depth 1 with (period, gain) equal to (3,1), (1,1), (1,2), proving the displayed formulas for all s≥1 by the min-plus recurrence. Generic tables retain additional summaries that cannot reach acceptance, so raw table sizes differ. Controls cover marked-assignment joins and positive, fractional, zero and acyclic cycle-mean cases. In general minimum cycle mean gives the declared liminf rate.

The merged records contain exactly 24 closed/complete cases, with rates 1/3 in five, 1/2 in eight, 1 in ten and 2 in one; all recorded rates equal their ray rates, and all reached reference values are unshortened. **The remaining 21 exact-rate computations were not independently replayed here:** their claim rests on the study's closed-table/complete-graph records and its correctness argument, not on this spot check alone.

## 5. Prior work and TRUE-BOND

**Narrowing against TRUE-BOND.** [BRANCH-DEPTH's earlier note](../../../BRANCH-DEPTH-20261112-001/depth.md) explicitly allows arbitrary side support. Its results therefore change TRUE-BOND's novelty, “open” answer and four “candidate counter-examples”: those four belong to ten already certified bounded cases, and a carried-port example was already known. The checked finite shortening census remains a contribution. Exact true coefficients were not supplied by that earlier result.

The missing prior work should consequently be a **Narrowing**, not a new Block of TRUE-BOND's checked finite minima. A universal claim that positive ray growth forces true growth would be **Block**: the ten certificates refute it. TRUE-BOND already withdrew its growth extrapolation; its remaining stale “four candidate”/blanket “open” wording and explanation by side branches carrying the constraint down should be reconciled with its later addendum. The earlier study still left existence open in 144 selected cases and larger-size behavior unresolved in six. TRUE-RATE's new complete-rate records cover those six; that is a real addition, not a prior BRANCH conclusion.

## Files and reproduction

Written here: `codex_report.md`; `certificate_audit.py`, `certificate_audit.json`; `mapping_audit.py`, `mapping_audit.json`, `family_inventory.json`; `rate_recompute.py`, `rate_recompute.json`; `validate_audit.py`, `validation.json`; `knotlab_nae.json`. Existing brief/message files were preserved. JSONs retain per-family computations, controls, rule keys and input hashes.

From the repository root, with `P=/home/jscul/p-vs-np-contact-first/.venv/bin/python` and `R=research/TRUE-RATE-20261113-001/referee-R1/codex`:

```bash
$P -B $R/mapping_audit.py
$P -B $R/certificate_audit.py
$P -B $R/rate_recompute.py
PYTHONPATH=tools $P -B -m knotlab check --cnf 'u v w; ~u ~v ~w' --loops u v --contact w --json > $R/knotlab_nae.json
$P -B $R/validate_audit.py
```

The focused checks pass. Each computation took seconds, used one process, and stayed far below the requested memory ceiling; process concurrency stayed within three. No full project suite, lifecycle edit, commit or publication was run.
