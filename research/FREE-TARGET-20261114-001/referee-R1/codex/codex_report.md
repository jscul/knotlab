**Verdict: Confirmed with fixes.** The **43-family linear-growth conclusion survives**. All 161 port relations and all 66 semigroup decisions reproduce independently. However, the displayed lower bound needs a depth shift in seven families, and the added exact chain equality is false for the class actually counted. Those statements should be corrected before the report is relied on.

This is fresh, offline, same-task AI recomputation and mathematical review (V2), not human review or external replication. No producer Python under the prohibited FREE-TARGET directory was opened or imported. All writes are confined to this referee directory; no Git state changes or publication were performed. Inherited path-growth proofs are identified below rather than silently re-proved.

## 1. Direct attempt to break the lower bound

I searched the ten smallest certified flattened blocks: seven of size five and three of size six; seven have `r >= 4`. For each attempted `(s,h)`, every copy through depth `s+h` is explicit, every call below it has exact usual-limit boundary relation G, every depth-s own distinction is eligible as target, and members can come from **any explicit copy**, including side copies and copies below the target. Numeric helpers are freshly expanded. The search uses CNF satisfiability, increasing support sizes, and exhaustive satisfiability of every assignment after each one-member deletion. It uses **no port-relation composition or semigroup code**; only the permitted input-language module supplies G.

There are **70 exact minima across 92 attempted cutoff/depth points**, with **33 complete h=1/h=2 pairs**. Every exact value equals recorded `L_path`, satisfies both comparison bounds, and agrees between cutoffs wherever both finish. Two families complete both cutoffs through depth five. Full family keys, witnesses, forbidden states, completed lower-size exclusions and source records are in [direct_summary.json](direct_summary.json). The values, each sequence ordered by s=1..5, are:

| Family | Block | r | Claimed lower | L_path | h=1 minima | h=2 minima |
| --- | ---: | ---: | --- | --- | --- | --- |
| F01 | 5 | 4 | 2,2,2,3,3 | 3,4,4,5,5 | 3,4,4,5,T | 3,4,4,T,T |
| F02 | 5 | 4 | 2,2,2,3,3 | 3,4,4,5,5 | 3,4,4,5,T | 3,4,4,T,T |
| F03 | 5 | 5 | 2,2,2,2,3 | 3,4,4,5,5 | 3,4,4,5,T | 3,4,4,T,T |
| F04 | 5 | 5 | 2,2,2,2,3 | 3,4,4,5,5 | 3,4,4,T,T | 3,4,4,T,I |
| F05 | 5 | 6 | 2,2,2,2,2 | 3,3,4,4,4 | 3,3,4,4,4 | 3,3,4,4,4 |
| F06 | 5 | 4 | 2,2,2,3,3 | 3,3,4,4,5 | 3,3,4,4,5 | 3,3,4,4,T |
| F07 | 5 | 5 | 2,2,2,2,3 | 3,3,3,4,4 | 3,3,3,4,4 | 3,3,3,4,4 |
| F08 | 6 | 2 | 2,3,3,4,4 | 4,5,6,7,8 | 4,5,T,T,T | 4,5,T,T,T |
| F09 | 6 | 3 | 2,2,3,3,3 | 3,4,4,5,5 | 3,4,4,—,— | 3,4,4,—,— |
| F10 | 6 | 3 | 2,2,3,3,3 | 4,5,6,7,8 | 4,5,T,—,— | 4,5,T,—,— |

T means unfinished at the point budget; I means explicitly interrupted without a result; — means not attempted. None is an exact minimum. F06 and F07 use a wrapper main: their justified lower sequences are respectively `2,2,2,2,3` and `2,2,2,2,2`, as explained next. [direct_table.md](direct_table.md) preserves the same table separately.

**Not a block — finite scope of the recomputation.** G makes the allowed-state projection onto the explicit variables exact, so every returned bond is a bond of the infinite limit. Exhausting supports inside a cutoff proves its minimum only for that support universe. Agreement of two cutoffs does not prove that still deeper members cannot shorten it. The infinite lower bound depends on the proof in point 2.

Six targeted controls and 45 exhaustive full-state/subset oracle comparisons pass, including rejection of a constrained but nonminimal support. The generic helper-before-entry depth convention has its own regression control. I also rechecked the wrapper counterexample below directly in its full unfolded CNF: the displayed triple allows exactly NAE and every pair is unconstrained.

## 2. Gap argument and its actual scope

The necessary premises check out. Every own distinction is fresh at its introduction; copies share identities only through actual arguments. Fresh assignment enumeration reconstructs the usual-limit fixed point from TOP, including the pass-through NAE rule. Finite branching and compactness justify using that greatest fixed point as the exact projection of each infinite unmarked subtree.

For each selected call, R_i retains exactly the incoming and outgoing tuples. All other own variables, nonrecursive expansions, and other calls' subtrees are projected away, including calls to **other self-holding types with their own G**. Along a stretch with no selected member introduced in its groups, its required projection is exactly the product of these 8-by-8 relations. No extra identity state is needed: an identity carried between the two ends enforces equality of the corresponding bits. In a nonempty complement-invariant NAE system both bit values occur, making that relation nonrectangular.

Group each off-path branch with the ancestor where it leaves the chosen target's ancestral sequence, irrespective of how deep a member lies inside that branch. A rectangular, unmarked stretch permits independent assignments above and below to be spliced into an allowed global state. Each part of a bond is free; this would make the whole bond free, a contradiction. Thus each disjoint length-r stretch must introduce an additional member. Unique origins prevent counting one carried identity twice. This proves, for the **36 growers with main=S**,

```text
|B| >= 2 + floor(s/r).
```

**Narrowing — seven wrapper growers.** With `C0=main, C1=entry`, there are only `s-1` tested S transitions, so their certified bound is

```text
|B| >= 2 + floor((s-1)/r).
```

I checked the possible repair rather than merely inferring a problem from syntax: in **all seven**, the main-to-entry relation followed by all length-(r-1) S products is not uniformly rectangular. Their least initial all-rectangular length is r+1. The stronger numerical bound is therefore unproved for these seven actual fixtures; no direct violation in those fixtures is asserted. The shift leaves their linear lower rate `1/r` unchanged.

**Block — the general unshifted wrapper lemma is false.** An explicit three-definition NAE control, within the raw language caps, has the flattened rule

```text
S(a,b,c): fresh u,v,h,t; NAE(a,u,h), t=a; SELF(b,u,v).
main(a,b,c): S(a,b,c).
```

Here `t=a` is implemented by a finite NAE macro, not an extra primitive. Its port relation is `out0=in1`, with other outputs free; r=2 and G=TOP. The three-member set `{main.b, C2.h, C4.t}` is an NAE bond to depth four, contradicting the unshifted requirement of four. The shifted bound correctly requires three. Duplicating SELF gives two call choices with the same R_i, since the other call's G is TOP; direct full-copy SAT also confirms the same counterexample in that branching version. The raw NAE descriptions, macro enumeration and SAT verification are retained in `relations_audit.json` and `direct_validation.json`. These controls are not among the frozen 66.

There are **13 several-definition families among the 66, nine among the 43**. Four of the 43 also contain another self-holding type. Every such other type has **zero own distinctions even after finite inlining**, so it contributes no additional eligible own target. Their constraints are nevertheless included in G. Thus the S-based argument covers every eligible deep target in this population, including own variables introduced by finite helpers inside S. It does not extend automatically to a new recursive type that introduces its own variables.

Together with the inherited `L_path` existence/upper bounds, the shifted or unshifted certificate proves linear growth for all 43. The conclusions are asymptotic lower and upper bounds; they do not by themselves prove an exact limiting rate. Details are in [gap_audit.md](gap_audit.md).

## 3. Fresh rectangularity computation

The independent standard-library enumerator matches **all 161 R_i, every product-set orbit, all 43 least r values, and all 23 recurring nonrectangular words**, with **zero mismatches**. The r distribution is exactly `2:9, 3:14, 4:6, 5:9, 6:5`. The entire set-of-products sequence is followed to repetition; there is no arbitrary length cap.

Controls check all 256 products of two-state relations, rectangular-factor persistence, proper and empty rectangular relations, identity/permutation recurrence, mixed call choices, and false certificates that reject. Dropping side-call constraints changes independently derived relations in two population families. Stored cycle products use the state before each cycle step; their alignment is not an error.

**Not a block.** The finite certificate computation reproduces. Its interpretation still requires point 2's depth convention and target-type scope. See `relations_audit.py` and `relations_audit.json`.

## 4. Added chain claim and census recount

The **5,190 distinct keys / 5,633 draws** reproduce when numeric calls are expanded and both S and main have exactly the SELF-occurrence counter `{S:1}`. This permits finite helpers and wrappers. The literal condition **one definition, one SELF** gives only **4,035 keys / 4,478 draws**; 1,155 of the reported keys have several definitions.

The reported percentages are correctly rounded empirical fractions: `5633/223261 = 2.5231%` of recorded nested draws and `5633/13279 = 42.4204%` of first-ray-growth draws. **Narrowing:** state the actual structural filter and that these are recorded sample weights, not exact probabilities over all nested patterns.

**Block — exact `L_any=L_ray` for the counted class.** The inherited ray quantity restricts support to the prefix ending at the target. A counted family reduces to

```text
NAE(a,b,c), NAE(b,c,d), NAE(c,d,e), ...
```

where a is its only participating main port, b is a main own variable, and c,d,e are own variables of copies at depths 1,2,3. Its exact G is TOP. The projection onto `{a,b,d,e}` excludes exactly `0011` and `1100`; every deletion is unconstrained. Hence `L_any(2)<=4`, using e below the target d. No prefix bond contains both a and d through depth two; the census records an absence sentinel there. The complete counted family and fresh enumeration are in [chain_wording_audit.md](chain_wording_audit.md) and `chain_census_audit.json`. This refutes equality for the broader class actually counted, not an independently established theorem about the literal 4,035 one-definition cases.

A sufficient replacement follows by taking the greatest origin depth d of a finite bond B to depth s. The same B qualifies for prefix-only `L_ray(d)`, so

```text
inf_{d>=s} L_ray(d) <= L_any(s) <= L_ray(s).
```

An inherited uniform positive linear lower bound transfers to every finite `L_any(s)`. If `L_ray` is also eventually finite at every depth with `lambda*s+O(1)`, the same asymptotic rate transfers. **Narrowing:** all-depth existence is a separate premise: 15 counted rows have absence sentinels, 12 still beyond depth 20. Positive rate and complete-graph flags alone do not establish it.

The observation is honestly labelled **“added at the close.”** It should remain retrospective. On a single continuation, freeing the target adds no choice; this is a special-case transfer and census cross-tabulation of the program's existing chain-ruler work, rather than a new general ruler theorem. External novelty was not reassessed without network access.

## 5. Unresolved cases and wording

**Narrowing — no bounded certificate is not an unboundedness theorem.** The 21 completed unresolved searches found no certificate at k<=5 requiring one eventually periodic path. They do not decide boundedness with paths changing with depth, nor rule out larger bounds. The two other unresolved cases skipped bounded search. In fact **nine families skipped it because main!=S**: seven already certified growers plus those two unresolved cases. Bounded search ran on 57 families. Replace “None of the 66 has a bond ...” with **“No bounded certificate was produced; the eventual-path test ran on 57 families.”**

**Narrowing — population claims.** Remove “about 3% of all nested weight” from established conclusions. It combines the 5,633 counted draws with a `43/300` sample share applied to another stratum, contrary to the frozen no-extrapolation rule while cases remain unresolved. Calling it a sample estimate does not resolve that preregistration departure. Report the observed conditional certificate yields, 43/66 and 43/300, as lower counts of certified growers; do not infer typicality or rarity across all nested patterns. The latter Wilson upper endpoint rounds to **18.8%, not 18.7%**.

**Not a block — appropriately qualified “counts depth.”** With point 2's correction and inherited existence, the 43 do have proved linear lower growth, with `L_any<=L_path`. Keep “the other cases are unresolved” and the explicit exclusion of depth-dependent-path boundedness. Avoid an exact-rate claim or an unqualified population “often.”

## Files and execution

Scripts: `direct_bonds.py`, `validate_direct_search.py`, `direct_summary.py`, `finalize_audit.py`, `relations_audit.py`, `chain_census_audit.py`. Reports: this file, `direct_table.md`, `gap_audit.md`, `chain_wording_audit.md`. Results: `direct_summary.json`, `direct_controls.json`, `direct_validation.json`, `relations_audit.json`, `chain_census_audit.json`, `run_manifest.json`, and the retained `direct_*.jsonl` records. `direct_budget_interrupt.json` preserves the unfinished large run; `resource_deviation.json` records the brief fourth-process overlap, immediately stopped without a result. That execution-rule deviation does not change the exact checks and is not hidden as a passed resource gate.

All computations use the requested `.venv/bin/python -B`, with no network. Recorded peak RSS is 234 MiB per process. The original long SAT call was interrupted through its own session before the 15-minute command limit; subsequent meta searches have explicit timer interruption. No timeout is interpreted as a mathematical result beyond completed lower sizes. `run_manifest.json` records elapsed time, input/output hashes, final witness rechecks and the disclosed execution deviations. Research records outside this directory remain unchanged; the fixes above are recommendations, not published corrections.
