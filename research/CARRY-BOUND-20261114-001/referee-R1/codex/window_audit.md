# Lemma W and bounded-window audit

**Verdict: Confirmed with fixes.** Lemma W's separation argument is sound with the frozen greatest-limit semantics and complete identity partition. All 16 sampled positive window certificates reproduce: 15 families classified bounded and one left undecided by the frozen cap rule. A concrete **Narrowing** is required wherever `> 6` is interpreted as absence of a finite window bond: eight sampled states actually have minimum eligible window bond size 7.

This is point 2 of the independent referee task for `CARRY-BOUND-20261114-001`. The sample is purposive: seven identity families, four order families, all five in-scope tie families, seven wrappers, and eventual bounds 2, 3, and 4. It estimates no population rate.

## What was checked

The fresh standard-library implementation reconstructs the usual greatest fixed point from all port states, finite-call flattening, every per-call relation, and the full root/target-port identity partition. It then iterates the complete reachable-state sets to their first repeat. It independently recomputes every sampled state's eligible bond search through size 6 by explicit finite relations and shattering checks.

All **21,805 distinct states**, per-call relations, state-set cardinalities, first-repeat parameters, and reported `U(s)` values agree with the supplied JSON certificates. A separate CNF calculation retains the intervening blocks on a concrete call word and replaces off-word subtrees by the independently reconstructed exact port limits. This checked **135 bonds** at word lengths 1, 2, 3, 6 and every residue of each first repeating interval. At lengths 1, 2, 3, **48 further checks** expand all S-copy calls, keep the target's children, and apply exact usual-limit relations only below that frontier. These 183 checks compare all **58,752 whole-window assignments**, in addition to checking non-shattering and every one-member deletion of each support. Every comparison passes.

The longest directly checked word has length **40**. The largest explicit finite truncation has **6,255 distinct variables**. This is a finite audit and a review of the stated argument; it is not external replication or a new uniform theorem. Validation independence is **V2**: separately authored same-task algorithms and SAT checks, with no producer Python opened or imported.

## Exact thresholds

Here `mu` is the independently reproduced preperiod of the complete state-set sequence, `p` its period, and `C` the largest least window bond size over its first repeating interval. Thus the certificate proves `L(s) <= C` at every word length `s >= mu`. For a wrapper, absolute target-copy depth is `s + 1`; for main = S it is `s`. The last column records the earliest word length from which this same bound C already holds, which can precede the complete state-set repeat.

| Family key prefix | Label | Wrapper | C | mu | p | Absolute periodic threshold | Earliest word length for C |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| e35d907e41c9 | I | no | 2 | 30 | 6 | 30 | 2 |
| 277e4af88ffd | I | yes | 2 | 14 | 4 | 15 | 0 |
| ce444059ece1 | I | no | 3 | 29 | 12 | 29 | 0 |
| 432127c418b0 | I | yes | 3 | 19 | 12 | 20 | 0 |
| 0d0a849308d9 | I | yes | 4 | 2 | 3 | 3 | 0 |
| 4a89d24d95e9 | I | yes | 4 | 3 | 2 | 4 | 0 |
| 0274a8f97ce5 | O | no | 3 | 17 | 4 | 17 | 0 |
| 17f842211d02 | O | yes | 3 | 8 | 4 | 9 | 0 |
| 7aac0c3bf98b | O | no | 4 | 15 | 4 | 15 | 0 |
| 3b96dcc4045a | O | yes | 4 | 12 | 2 | 13 | 0 |
| 3e479a23fc49 | T | no | 2 | 36 | 4 | 36 | 5 |
| 4c743f6f3c29 | T | no | 2 | 10 | 4 | 10 | 0 |
| 6840b65fda90 | T | no | 3 | 16 | 4 | 16 | 0 |
| 43d056083445 | T | no | 2 | 3 | 4 | 3 | 0 |
| d2942bac0424 | T | no | 2 | 5 | 2 | 5 | 0 |
| 057b385094fd | I | yes | 3 | 11 | 6 | 12 | 0 |

Every first-cycle residue has a concrete word and directly verified support in `window_results.jsonl`; no capped length set was used as a periodic certificate. Some first-cycle values alternate below C, so C is an eventual upper bound, not an assertion that every depth has the same minimum. The exact window minimum is an upper bound on the global minimum L; this audit does not identify L with U.

`432127c418b0` is the retained frozen-rule undecided case: the mathematical positive window certificate is complete, with mu = 19, p = 12, and bound 3, but an inherited census cap blocks its final bounded verdict under the frozen rule. The other 15 panel members have final verdict bounded. This audit does not override that rule.

**Not a block — threshold wording.** State thresholds in the declared word-length convention, adding one for wrapper absolute depth. The preperiod certifies the full state-set repetition and need not be the earliest onset of the numerical bound. For example, `3e479a23fc49` has mu = 36, p = 4, while its bound 2 already holds from word length 5.

## Why Lemma W is exact

With fresh local distinctions per copy, the target subtree and its context share only the target ports, including any repeated identities among them. The exact relation on those ports is obtained by decreasing iteration from all tuples: every allowed infinite subtree restricts into every iterate, and a surviving fixed-point tuple has compatible finite completions at every finite expansion. Finite Boolean constraints and compactness then give an infinite completion. A living main relation supplies a nonempty whole pattern.

At an intervening copy, the selected child's subtree is omitted; all other subtrees can be replaced by their exact port projections. Existentially forgetting that copy's other distinctions therefore gives the stated per-call relation. Successive conjunction and existential forgetting give relational composition. The target's own block is then conjoined once, so a tuple in the resulting window extends exactly when the original whole pattern permits it. No scheduler, execution order, or outside input enters this relation.

The state must retain syntactic identity separately from semantic equality or opposite ties. Root/target aliases and target-port/target-port aliases count as one distinction. Distinct variables tied by constraints stay distinct and can form a genuine size-2 bond. The sampled census states have root/target aliases but no target-internal identity repetition; that latter branch is exercised by a matched synthetic control.

The control uses `S(a,b,c)` with an own distinction x, rule `NAE(a,b,x)`, and call `SELF(a,x,x)`. After that call, the child has actual ports `(a,x,x)` and partition `[0,1,2,0,3,3]`. Treating the last two positions as separate variables gives the apparent equality relation `{00,11}`. Merging their one identity leaves a free singleton `{0,1}`. The checker explicitly rejects the duplicated-identity support as a purported two-member bond. SAT and exhaustive enumeration of all 32 actual assignments agree; the merged whole-window relation also matches direct SAT. This validates the mathematical need for the full partition.

An actual window bond lifts to the whole pattern because its projection and every proper projection are identical in both relations. Repetition of the complete reachable-state set then repeats those finite relations up to the retained identities, proving the positive bound at every subsequent depth.

## Narrowing: the size-six sentinel is censored

The frozen implementation defines a search through size 6 and records `> 6` when it finds no eligible bond there. The notes also use “exact U” and “window leaves unbounded.” The latter wording is too strong unless the search exhausts every possible support size or a separate obstruction is supplied.

This is a substantive counterexample to treating the sentinel as infinity, rather than a merely hypothetical concern. The sampled windows have **5 to 10 distinct variables**. Among **243 states** with reported `g = "> 6"`, a fresh exhaustive search of the remaining support sizes finds **eight states with exact minimum g = 7**: four in `0274a8f97ce5` and four in `7aac0c3bf98b`. All eight size-7 supports are also verified by direct SAT, comparing their entire window projections and all seven six-member deletions. In each case the bond permits 126 of its 128 states and every deletion permits all 64 states.

One concrete example is `7aac0c3bf98b`, SELF-label word `[0,0,1,1,0,0]` of length 6, state `J = 0x7ffffffffffffffe`, partition `[0,1,2,3,4,5]`. Its window has eight distinctions. The support with labels `[0,1,2,3,5,6,7]` is a bond of size 7, excluding exactly states 31 and 96 in the listed support order. Labels 0–2 are main ports, 3–5 are target-port identities, and 6–7 are target own distinctions. The full JSON gives the actual distinction IDs, word, clauses/variable counts, and every deletion count.

SELF labels are zero-based among S calls in flattened-block order. The eight additional size-7 checks bring the total to **191 concrete bond checks** and **63,872 whole-window assignment comparisons**, apart from the synthetic control.

**Required wording:** call a failed size-six search “no window bond of size at most 6 found” or “no bound certified by this search.” Keep `> 6` distinct from “no finite bond,” “unbounded,” and infinity. Exact finite g-values at or below 6, successful bounded certificates, and the sample's exact U(s) minima survive: each sampled level has a least witness of size at most 4, so an omitted bond of size 7 cannot improve it. No sampled family-level bound changes. The probe did not exhaust other census families, and it does not establish how many family classifications a search beyond size 6 would change.

## Files and replay

- `window_contract.md`: audit interface and limits.
- `window_prepare.py`, `window_inputs.json`: deterministic sample and compact permitted source data; source-file hashes are included.
- `window_audit.py`, `window_results.jsonl`, `window_results.json`: reconstruction, concrete words/supports, raw SAT checks, summary, and source/code hashes.
- `window_censor_probe.py`, `window_censor_probe.json`: exhaustive remaining-size search and direct checks for the eight size-7 counterexamples.
- `window_manifest.json`: hashes of the notes and principal audit artifacts.

Replay from the repository root with `.venv/bin/python -B research/CARRY-BOUND-20261114-001/referee-R1/codex/window_audit.py`, then the same command ending in `window_censor_probe.py`. The final main run took **11.624 seconds**, with peak RSS **81,628 KiB**; the censor probe took **0.426 seconds**. Each invocation used one computational process and a 2 GiB address-space limit. No Git mutation, publication, network call, or forbidden Python access occurred.
