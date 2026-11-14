# R1: chain claim, census recount, and conclusion wording

Scope: `FREE-TARGET-20261114-001`, referee points 4–5. This lane read the four supplied study documents, permitted JSON/JSONL data, the allowed dlang/LIMIT-STATE input semantics, and the required vocabulary/proof guidance. It did not read or import producer Python from the FREE-TARGET or census implementations. It writes only this note and `chain_census_audit.py` / `chain_census_audit.json` beside it. No network, tickets, publication, or Git mutations were used.

**Verdict: the numerical census count reproduces for a broader condition than the prose states. Exact `L_any = L_ray` is false for that counted class when the ray support stops at the target. Positive growth has a weaker surviving argument.** The 43/66 result counts reproduce; the unresolved cases and population extrapolation need the qualifications below. Mathematical validity of the 43 forgetting certificates is outside this lane.

## 1. Exact counts and filter

The census has **124,572 distinct description-family keys**, matched exactly by the distinct keys in **223,261 recorded nested samples**. Its `class == "grows"` rows contain 12,772 keys and 13,279 sample records.

The filter reproducing **5,190 keys / 5,633 sample records** is:

1. Require census `class == "grows"`.
2. Expand every numeric call to an earlier definition, counting occurrences separately; retain each `SELF` with the index of its definition. Knots contribute no `SELF` occurrence.
3. For the census ray definition `S`, require the resulting counter to be exactly `{S: 1}`.
4. Require the counter of main to be exactly `{S: 1}` too.

Thus the used expansion has one recursive continuation at every level and one entry from main. Finite helper definitions are allowed. Unused definitions create no copies. The counter condition excludes both other recursive definitions within the used bodies and multiple entries from main.

The literal condition **`n_defs == 1` and one `SELF`** gives only **4,035 keys / 4,478 sample records**. Of the counted 5,190, **1,155 have more than one definition**. Consequently, “a family with one definition” cannot be the stated filter for that count. “No side copies” also needs to refer to recursive continuations after expanding finite helpers; finite helper copies can occur.

The precise reported fractions are:

| Recorded quantity | Exact fraction | Percent |
| --- | --- | --- |
| Counted single-continuation sample records / all nested sample records | 5,633 / 223,261 | 2.5230559748% |
| Counted single-continuation sample records / first-ray-growth sample records | 5,633 / 13,279 | 42.4203629791% |

Therefore **2.5%** and **42%** are accurate rounding of empirical sample weight. They are not exact probabilities over all nested patterns. “Distinct families” means distinct description-family keys here, not a count modulo semantic equivalence or isomorphism.

Classification: **Narrowing required** for the filter and population words; **not a block** to the arithmetic.

## 2. Algebra: equality fails; a growth implication survives

If “members on the ray” meant members anywhere on the entire infinite unique sequence, equality of candidate support sets would be immediate. It is not immediate for support confined to the initial segment ending at the target. Members below the target remain available to `L_any`.

Here is a counterexample **inside the actual 5,190-key count**, with census `lambda = 1/2`:

```json
[[3,0,[["K",[0,1,2]]]],[3,1,[["SELF",[1,3,0]],["K",[3,1,0]]]],[3,1,[["K",[2,0,3]]]],[3,2,[[1,[2,4,1]]]]]
```

Main calls definition 1 on `(root port 2, main own variable 4, root port 1)`. Write these first two relevant variables as `a,b`. Let `c,d,e` be the fresh own variables in its first, second and third recursive copies. The three copies impose exactly

```text
NAE(a,b,c), NAE(b,c,d), NAE(c,d,e).
```

The other main ports and its unused own variable have no constraint involving them. The exact limit port relation of this definition is `TOP`: any assignment of its ports can be extended by choosing its next fresh own variable to make the newest NAE triple hold, repeatedly. Thus these finite projections are also projections of the full infinite pattern.

The projection onto **`{a,b,d,e}`** excludes exactly **`0011` and `1100`** in that order. It is nonempty, non-full, and forgetting any member gives all eight states of the other three. It is therefore a size-four bond containing root port `a` and the depth-two own distinction `d`, with `e` at depth three.

In contrast, with support restricted to the first two copies, no bond contains both `a` and `d`. Fresh enumeration checks every candidate subset of `{a,b,c,d}`; adding unused variables cannot make a minimal constrained set. The census records `L_ray = [3, 1000000000, 4, ...]`, consistent with this absence at depth two. Consequently **`L_any(2) <= 4` while prefix-only `L_ray(2)` has no finite value**. Depth here is the flattened-entry convention: the first entered recursive copy is depth one.

This refutes equality for the *broader class actually counted*. It does not by itself refute an equality theorem restricted to the literal 4,035 one-definition families; such a theorem has not been supplied or proved in this lane.

The following weaker statement does hold for any one continuing sequence. Let `B` be a finite bond reaching depth `s`, and let `d >= s` be the greatest origin depth of any member of `B`. A member of `B` is an own distinction at depth `d`; all its members lie in the prefix through `d`. The same `B` therefore qualifies for `L_ray(d)`. Hence, with absence treated as no finite candidate,

```text
inf_{d >= s} L_ray(d) <= L_any(s) <= L_ray(s).
```

If the inherited finite-graph theorem gives `L_ray(d) >= lambda*d - C`, with `lambda > 0`, at every finite value, this transfers the same lower bound to every finite `L_any(s)`. If `L_ray` is also eventually finite at every depth and equals `lambda*s + O(1)`, the two inequalities give `L_any(s) = lambda*s + O(1)`. Neither inference requires exact equality.

**Existence needs separate care.** In the first 30 recorded depths, 15 of the 5,190 have a `10^9` absence sentinel; 12 still have such values after depth 20. All 5,190 source rows carry `complete=true`, `status=done`, positive complete `lambda`, and `eventually_bounded=false`, so those flags alone do not supply existence at every large depth. There are 17 recorded declines, including two finite-to-finite declines; one of those belongs to a literal one-definition family. Monotonicity cannot silently repair the equality argument. A decline alone is not a counterexample; the five-variable construction above is.

Classification: **Block the exact equality claim for the counted class. Narrow the chain conclusion** to the lower-bound transfer, with all-depth existence stated only where separately justified. The positive-slope argument and the numerical count remain useful.

## 3. Sample result wording

Replacing the rows of `G.jsonl` by matching `phase2.jsonl` rows replaces 28 entries and leaves 300 distinct sample keys: **208 path-bounded, 66 path-growing, 26 unresolved**. The FREE-TARGET frozen population matches exactly those 66 path-growing keys.

The full results reproduce **43 `grows`, zero bounded certificates, 23 unresolved**, with least forgetting lengths `r=2:9`, `3:14`, `4:6`, `5:9`, `6:5`. All 66 inherited path-growth rows have `complete=true` and a complete path-rate record. This is the recorded source for the claimed upper bound and existence; a finite displayed sequence alone would not establish eventual existence.

The unresolved split is exactly:

- **21:** the eventually-periodic-path bounded-certificate searches completed for budgets 3, 4 and 5 without a certificate. This is not a decision that `L_any` is unbounded, nor a decision about depth-dependent changing paths.
- **2:** bounded search was skipped because `main != S`, despite the pre-run clarification selecting a depth convention. They remain unresolved.

There are actually **nine `main != S` cases in the 66**, all with no bounded-search attempts: seven already have growth certificates and two are unresolved. Thus “the two skipped cases” is accurate only when it means the two *unresolved* skipped cases. In total, bounded search ran on 57 families. Replace “None of the 66 has a bond of at most 5 ...” by **“No bounded certificate was produced; the bounded search ran on 57 families, and its 21 unresolved completed cases found none within the specified eventual-path test.”**

“43 of 66 (65.2%) are certified to grow” is an exact sample description. **At least** is needed if it is read as the share that truly grows: some of the other 23 may grow too. The same qualification applies to 43/300 = 14.3333%. The Wilson calculation gives 53.1122–75.5241% for 43/66 and 10.8185–18.7501% for 43/300; the latter rounds to **10.8–18.8%**, so the note's 18.7% upper endpoint needs correction. These intervals concern certificate yield under a sampling model, not proof bounds on the true growth fraction. The allowed rows alone do not recover the sample inclusion law.

For the 43, assuming the separately audited lower-bound theorem, existence from `L_path` plus the lower and upper linear bounds justifies “grows at least linearly.” “A rate between `1/r` and `lambda_path`” should mean asymptotic lower/upper bounds, or explicitly `liminf >= 1/r` and `limsup <= lambda_path`; the bounds do not prove that an exact limiting rate exists.

Classification: **Narrowing required**; the 43/66 and unresolved counts themselves are **not a block**.

## 4. “About 3%,” typicality, and novelty

The reported extra exclusions reproduce: **224** one-definition limit-only growth keys/sample records and **657** one-SELF non-chain growth keys/sample records. The remaining reconstructed G stratum contains **6,701 keys / 6,765 sample records**. The reported 3% is the arithmetic

```text
(5633 + 6765 * 43/300) / 223261 = 2.9573682820%.
```

That combines an empirical census component with an extrapolated sample component. It is not an established census share of true depth counters. The frozen preregistration explicitly adopts “no extrapolation beyond the sample while some cases are unresolved,” and the advisor asks for this restriction too. Calling the number a sample estimate acknowledges uncertainty but does not satisfy that preregistered restriction. **Remove it from the study's established conclusions.** If retained as retrospective exploratory arithmetic, label its departure from the preregistration, its conditional sampling assumptions, and the unresolved false-negative issue. No unqualified “typical,” “rare,” or “often” follows for all nested patterns. The defensible frequency is the stated conditional sample frequency for a named process/stratum.

The close-added chain observation is honestly labelled “added at the close”; it was not a frozen prediction and should remain a separate retrospective result. The permitted preregistration already identifies fixed-branch unrestricted-support bonds, existing first-ray rulers and complete-graph growth methods as prior work. On a single continuation, changing from a fixed target sequence to a free target creates no new choice. The structural transfer/count is therefore a special-case observation plus a new census cross-tabulation, **not a new general chain ruler theorem**. The study's broader every-call/free-target delta is separate and was not reviewed for external novelty in this lane. External novelty remains unassessed; no network literature search was authorized.

Classification: **Narrowing required** for extrapolation, typicality and novelty. This is **not a block** to reporting the new per-family certificate results and the exact cross-tabulation.

## Validation

Executed:

```text
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/FREE-TARGET-20261114-001/referee-R1/codex/chain_census_audit.py
```

The script completed in under two seconds, one compute process, with a 2 GiB address-space ceiling. It checks source key equality, structural occurrence counts, all reported denominators, G/phase2 population replacement, verdicts, the counterexample's projected relation and every one-forgotten projection. Input SHA-256 values and the full decline/skip records are in the JSON. This is independently authored same-task reimplementation (**V2**), not human review or external replication. It recounts inherited census classifications rather than independently proving the original complete-graph algorithm.
