**Verdict: Refuted — Rule A as written.** The version that excludes **every selected-call argument from peeling, including ports in F**, survives this audit and exactly reproduces the reported census results. The forbidden implementation was neither opened nor imported; this is a defect in the written rule/proof, not a finding about that unread code.

Scope: `epic FORGET-RULE-20261114-001`, independent referee recomputation. All writes are in this directory. No network, publication, Git mutation, or shared-record edit. Rule A/N are fresh implementations from stage 2; per-call SAT projection and the exact nonrectangular-product automaton reuse the expressly permitted CENSUS-FORGET referee engine. A separate pure-set implementation verifies the decisive witness without that engine.

## 1. Rule A: counterexample search

**Block — retained outputs cannot be existentially peeled.** The written alternative “an own distinction not among call i's arguments, or a port in F” protects outputs only in its first arm. The literal second arm is false. Required repair:

```text
eligible(v) = v not in arguments(i)
              and (v is an own distinction or v is a port in F).
```

If the intended meaning of “remaining constraint” already counts the selected continuation's argument occurrences, state that explicitly; it supplies this same guard. The numerical results below support the guarded reading, but do not identify the unread implementation.

A small complete witness, with own distinctions u,v, is:

```text
S(p0,p1,p2):
  NAE(p0,p1,p2)
  NAE(p0,p2,v)
  SELF(p1,u,v)
```

Its raw A79 description is `[[3,2,[["K",[0,1,2]],["K",[0,2,4]],["SELF",[1,3,4]]]]]`. Its usual greatest support is NAE, so it is living. No pass-through correction is added. N has only the arc `1 → 0` and is acyclic.

The literal generic-start automaton reaches M empty after **3** calls. At its second step it peels through current port 1 in F even though that port is the next argument 0. The exact removed-continuation relation, with no final child-support constraint, is

```text
R((a,b,c),(d,e,f)) ⇔ NAE(a,b,c) ∧ d=b ∧ NAE(a,c,f).
```

It has 20 pairs, mask `0x00aa0555aaa05500`. For every n≥1,

```text
R^n[010] = {101,111} at odd n, {000,010} at even n;
R^n[101] = the opposite row.
```

Only 101 in the first row and 010 in the second can continue, since constant intermediate triples violate the next block's first NAE. This proves the displayed rows for all n. Crossed pairs are absent, so no power is rectangular. Independently, `R²=0x00ffa0ffff05ff00`, `R³=0x00ff05ffffa0ff00`, and `R⁴=R²` give an exact period-two certificate. The guarded automaton rejects the family. See [counterexample.json](counterexample.json).

This minimal key is absent from the full 124,572-record census, but nine isomorphic presentations occur there, all classified bounded and outside the 12,772-family first-ray-grower study. I therefore also verified a stronger holdout with **no isomorphic presentation** under any port/own renaming, NAE argument reorder, or call reorder:

```text
S(p0,p1,p2), own u,v,w,x:
  NAE(u,w,x)
  NAE(p0,p2,v)
  NAE(p0,p1,u)
  NAE(p0,p1,p2)
  SELF(v,w,p1)
```

All four own distinctions are used. Its raw description and complete lasso are in [structural_and_boundary_controls.json](structural_and_boundary_controls.json). Literal A again certifies r≤3; its exact products are nonrectangular and periodic; guarded A rejects it.

Both search pools stayed within raw language caps, used only living greatest-limit families for the theorem tests, and exactly decided every tested family; **no search case was capped**.

| Search pool | Distinct keys outside full census | Living/exactly tested | Literal A false certificates | Guarded A certificates | Guarded false certificates / bound failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Exhaustive grids plus random one/two definitions | 198,424 | 192,332 | 60 | 18,125 | 0 / 0 |
| Additional two-definition helpers, 3–6 ports | 49,996 | 46,117 | 3 | 7,017 | 0 / 0 |

The first pool includes two completed exhaustive grids, 1def: 10,584 outside-census descriptions, 10,578 living; 2def: 7,091 outside-census descriptions, 7,091 living. Grid 1 covers own counts 0–2, every ordered distinct SELF triple, and every set of 0–3 unordered NAE triples. Grid 2 covers the same own counts and continuations, every placement of a ternary NAE helper, and 0–1 additional NAE triples. Random searches add own counts through 6, multiple continuation/side calls, recursive side definitions, and two-definition helpers with 3–6 ports. Literal A also gave **1,502** incorrect finite bounds in the first pool and **266** in the second. Counts are distinct description keys within each pool; the pools are reported separately, without asserting structural uniqueness or adding potentially overlapping pools. No guarded-rule failure was found; finite search alone does not prove its theorem.

## 2. Rule N

**Confirmed on living families.** No identity-cyclic family forgot in either search pool or among all 12,772 recomputed census families. The proof needs nonemptiness: on the nonempty powers of a cycle word, identity forces equality of an endpoint coordinate; complement closure supplies both diagonal values, and a rectangle would contain the missing crossed values. Rectangularity persists under further composition, so arbitrarily long nonrectangular cycle-word powers exclude every uniform r.

**Narrowing — state the living/nonempty-word hypothesis.** Complement closure alone does not imply either value occurs. An A79 negative-domain control uses all ten NAE triples on five distinctions plus `SELF(p0,p1,p2)`: it is unsatisfiable, identity-cyclic, and has empty (hence rectangular) R. For a living greatest-limit S, every word has a nonempty realization with endpoints in its support, which supplies the missing premise. See [structural_and_boundary_controls.json](structural_and_boundary_controls.json).

## 3. Proof of Rule A

**(a) Block — the F output guard above is necessary.** After that repair, preserve two invariants: F contains no identity of an original top port and no variable touched by a retained upper constraint; every eliminated variable is absent from the next frontier. An eligible own distinction is fresh above and absent below. An eligible F port is absent above and absent below. Degree one is then degree one in the whole composite, and its full two-coordinate projection justifies exact existential elimination. Not revisiting older layers can miss additional eliminations, which only makes the guarded test conservative.

**(b) Not a block — frontier partitions retain climb-back paths.** Joining the old frontier partition with the new block and restricting to its arguments computes connectivity in the entire retained prefix. Every excursion into an older prefix enters and leaves through its frontier, whose connectivity is already recorded. A prefix component missing that frontier cannot reconnect later. Complete-prefix checks matched **34,764** guarded transitions on **5,794** six-layer words, including the advisor's inequality gadget; **22,740** transitions had a nontrivial upper partition. See [prefix_invariant.json](prefix_invariant.json). The advisor's 22-state count excludes F; use the actual augmented automaton's longest-live-path bound.

**(c) Not a block — the generic start is necessary and fixes the reconstructed eight training errors.** A main-conditioned entry can already be a product even though generic S products are not. I reconstructed main-entry states without reading the first implementation: it produces **8** nonforgetting false certificates in training, and **9** in held out. All 17 are rejected by the generic guarded start. This reproduces the reported training count, not the unavailable historical identities. See [guarded_recount_and_starts.json](guarded_recount_and_starts.json).

**(d) Narrowing — rectangularity and bond growth have different premises.** Rules N and guarded A, H1–H3, and the forgetting fractions in H4 are relational statements; they do not need the gap argument. Interpreting forgetting as a growing free-bond lower bound does: it covers copies of S whose ancestry after main consists of S calls. Other recursive own targets and delayed routes to S are not automatically covered. For wrappers use `2 + floor((s−1)/r)`, as specified by the [earlier referee](../../../CENSUS-FORGET-20261114-001/referee-R1/report.md). Saying only “copies of S” misses delayed S. The identity/forced-equality-only explanation remains a hypothesis; N plus a sufficient rule do not prove a characterization. See [proof_critique.md](proof_critique.md) for the full invariant argument.

## 4. Held-out read

I freshly rebuilt all **12,772** greatest-limit blocks, all **26,243** per-call relations, and every exact forgetting decision. Every R_i and all previously completed verdicts/least r values match the permitted CENSUS-FORGET data. The graph method also resolves all **66** previously capped cases as nonforgetting. The guarded implementation reproduces **every field** of both train and held-out tables in `heldout.json`.

- **H1:** 0 held-out N violations.
- **H2, guarded A:** 1,051 certificates; 0 false certificates; all exact r are within the guarded bounds.
- **H3, guarded A:** 1,051/2,861 = **36.7354%**, within the frozen band; training is 1,107/2,980 = 37.1477%. Each stratum is within eight percentage points.
- **H4:** all **2,096/2,096** N-acyclic chains forget; **765/817 = 93.6353%** N-acyclic non-chains forget.

| Stratum | Training guarded A / forgetting | Held-out guarded A / forgetting |
| --- | ---: | ---: |
| chain/1def | 694/1,659 (41.83%) | 662/1,623 (40.79%) |
| chain/multi | 190/468 (40.60%) | 186/473 (39.32%) |
| nonchain/1def | 117/439 (26.65%) | 95/399 (23.81%) |
| nonchain/multi | 106/414 (25.60%) | 108/366 (29.51%) |

**Block — these numerical confirmations require the guarded reading.** Literal A instead certifies **1,372** held-out families (47.96% of forgetting families), with **273 incorrect r bounds**; training gives 1,421 certificates and 277 incorrect bounds. It has no nonforgetting false certificate *in this selected study population*, but the outside-population witnesses above refute general sufficiency. Therefore literal H2 fails its frozen bound clause and literal H3 fails its 30–42% band. See [heldout_recount.json](heldout_recount.json), [heldout_fresh.jsonl](heldout_fresh.jsonl), and [guarded_recount_and_starts.json](guarded_recount_and_starts.json).

## Files written and reproduction

- Fresh rules/engine adapter: [independent_rules.py](independent_rules.py); controls: [controls.json](controls.json).
- Search: [search_counterexamples.py](search_counterexamples.py), [wide_search.py](wide_search.py); `first_search.*`, `extended_search.*`, `final_search.*`, `wide_search.*` JSON/JSONL. First/extended runs preserve discovery history; final search adds explicit guarded-bound checks over the same deterministic pool, not additional independent families.
- Decisive verification: [validate_counterexample.py](validate_counterexample.py), [counterexample.json](counterexample.json), [structural_and_boundary_controls.py](structural_and_boundary_controls.py), its JSON.
- Census/start audit: [recount_heldout.py](recount_heldout.py), [audit_starts_and_counts.py](audit_starts_and_counts.py), and the three result files linked above.
- Whole-prefix audit: [check_prefix_invariant.py](check_prefix_invariant.py), [prefix_invariant.json](prefix_invariant.json).
- Delegated proof audit: [proof_critique.md](proof_critique.md), [proof_critique.json](proof_critique.json).
- Assembly/provenance: [write_report.py](write_report.py), [summary.json](summary.json), [run_manifest.json](run_manifest.json), [validation.json](validation.json), this report.

All Python runs use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. Reproduction commands and content hashes are in `run_manifest.json`. At most three research jobs ran concurrently; each used a 2 GiB address-space ceiling once the referee adapter loaded. The largest measured job RSS was 142.2 MiB. Every substantive command completed below 15 minutes. No theorem is inferred from the number of tests, and no shared correction/publication/lifecycle file was edited under this task's write restriction.
