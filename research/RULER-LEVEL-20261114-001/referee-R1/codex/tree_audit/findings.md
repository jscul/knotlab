# Independent referee: Theorem A's one-placement construction

Scope: `RULER-LEVEL-20261114-001`, tree-audit lane. Codex, 2026-11-15.

**Verdict: no block in Theorem A's structural argument.** Its application of Theorem A** is sound conditional on the cited T1 having the advertised all-support least-bond statement; T1's original authority record is assigned to the other referee lane and was not inspected here. The overview contains a stronger statement that needs narrowing. Finite checks below support implementation agreement; they do not prove the uniform theorem.

The objects here are the distinction-and-knot meeting pattern; its classical incidence graph (the literature's bipartite graph on the distinctions and knots) is used solely as a finite structural test. A cycle of co-knotted pairs inside one three-place knot is not a Berge cycle. No contact, metric or complexity authority is inferred from these checks. Vocabulary follows the [program glossary](../../../../../publication/knotlab/INTUITIONS.md#glossary).

## Proof inspected line by line

Source: `proofs/RULER-LEVEL-20261114-001A/RULER-LEVEL-20261114-001A-P001_forest_ruler/proof.md`, original inspected lines 29–42.

| Source lines | Claim and audit |
| --- | --- |
| 31 | A binary rooted-address-tree automorphism is length preserving and bijective on each level. This is enough for the argument. In fact only levelwise bijectivity of the three maps is needed; prefix preservation is a sufficient extra hypothesis. |
| 31–33 | The plain term remains at level n; the two appended terms are at n+1. Thus there are no within-level knots. At n=N the placement is omitted by the finite pattern definition, rather than introducing addresses past N. |
| 33, 37–38 | Each source word w at n<N makes three distinct addresses: the upper address has a different level, while the two lower addresses have different last letters. Two source words at the same n have different upper addresses because g is injective; knots from different n have different pairs of levels. Thus no knots are lost by duplicate-image filtering or knot deduplication. There are exactly 2^N−1 knots. |
| 33, 38 | Each address u at n<N is the upper member of exactly one knot, namely the source w=g⁻¹(u). At level N it is upper in none. This is a statement about the construction's upper role, rather than its general incidence degree. |
| 33–34, 38–39 | Each non-root address parses uniquely as v0 or v1. In the first case the unique source is h₁⁻¹(v); in the second it is h₂⁻¹(v). Knots at other source levels cannot make the same lower address. The root is lower in none. Correct even when the three automorphisms coincide. |
| 39–41 | The deepest-address argument is valid. In a hypothetical Berge cycle choose a cycle address z of largest level. It must be incident to two distinct cycle knots. Any incident knot in which z is upper has its other two addresses at a strictly deeper level; whichever other address that knot uses on the cycle contradicts maximality. Consequently z is lower in both cycle knots, contrary to lower uniqueness. The argument handles the two-knot cycle with a shared pair as well as longer cycles. Merely bounding the incidence degree by two would not have sufficed, but the repaired proof uses the stronger property. |
| 41 | Connectedness is established: repeatedly taking the unique upper member of the unique parent knot lowers the address level by exactly one. Every address reaches the unique level-zero address, and every knot contains addresses. This also handles the root and terminal-level addresses of incidence degree one. N=0 has one address, no knots, and a vacuous reach statement. |
| 41–42 | Starting at any address at level k<N, its unique upper knot supplies two addresses one level deeper. Iteration reaches every requested depth ≤N. The successive knots are distinct by their upper levels, so this is a descending chain, not repeated use of one knot. |
| 42 | The warning about prefix descendants is essential and correct: the upper parent of v0 is g(h₁⁻¹(v)), and need not be the word prefix v. The tests include examples where many parents differ from word prefixes. |
| 34–35, 42 | For k+s≤N and s≥1, the descending chain supplies a pair joined by s knots. Every knot changes the level by at most one, so no pair at the two designated levels has a shorter route through knots. The minimum over pairs is s. Subject to T1 as quoted in lines 22–24, the least crossing bond size is s+2 even when supports anywhere in 0..N are eligible. No extra monotonicity assumption is used. |

The requested pair-sharing check also follows directly, independently of the deepest-address argument. Two knots with the same upper level have disjoint upper members and disjoint lower members. Knots whose upper levels differ by one can meet only at the deeper knot's unique upper member. With a larger level difference they are disjoint. Therefore two distinct knots never share two distinctions.

## Registered words and action semantics

The allowed written specification is `research/LEVEL-REACH-20261114-001/codex_spec.md:22–30`: addresses are length-tagged binary words, terms append **after** the word action, and duplicate-image triples are discarded. The inherited independent referee source is `research/ADDR-KNOTS-20261113-001/referee-R1/codex/fresh_patterns.py`:

- Lines 12–13 register the identity, single-state maps and two-state compositions.
- Lines 16–30 give the action `bu ↦ (b xor swap[q]) action_successor(u)`. By induction on suffix length, each state map is a permutation on every level: the two first-letter outputs are disjoint, and each suffix action is bijective. It also preserves every prefix and emits exactly the input length.
- Lines 33–41 implement the same action letter by letter. Composition, including the empty word, preserves the automorphism property.
- `fresh_pattern.py:25–32,34–38` applies the composed action before appending a last letter and implements finite truncation and duplicate filtering. No producer source was read.

The array and letterwise action implementations agreed on 415,140 word/address images, checking **every registered word**, levels 0..7, on the 120 sampled automata. Every checked word was a level permutation and preserved prefixes. This confirms the finite implementation surface; the preceding induction supplies the mathematical explanation for all lengths.

## Fresh checks and controls

The seed and bounds were recorded in `interface.md`. The sample is a structural audit, not an estimate under the census weighting.

- **Structure:** 120 generated descriptions, 116 distinct keys, each at N=0,1,2,4,6,7,9: 840 patterns. All state counts 1..5 occur. Every property in the proof table passed, including explicit root ascent and 169,320 descending-chain continuation checks. Largest pattern: 1,023 distinctions and 511 knots. All patterns agreed among the inherited `fresh_pattern.build`, `fresh_pattern.direct_build`, and `brute_supports.placement_pattern` constructions.
- **Exact reach:** four fresh descriptions at both N=6 and N=7, k=1 or 2, s=1,2,3: **24/24 exact values [3,4,5]**, no undecided search. Two descriptions realize the plain tree; two have non-prefix knot parents. The same prior independent search was used without any forest/ruler shortcut and with all 0..N distinctions eligible. Its elimination width was 2. Each returned bond was rechecked for a forbidden assignment and full projections on all maximal proper subsets with the separate `brute_supports.ProjectionOracle`.
- **Scaling smoke:** one non-prefix-parent description at N=4,5,6, k=1, s=1..3: nine exact matches. This is separate from the N=6,7 count.
- **Malformed controls:** two knots sharing a pair; a three-knot Berge cycle with only single overlaps; deletion of the root knot leaving missing parents and disconnected pieces; an extra knot repeating lower membership; and a within-level knot. All five were rejected by the specified structural gates. In particular the longer-cycle control demonstrates that the incidence test does more than reject shared pairs.
- **Exact semantic controls:** every state and every support were enumerated on a single knot, a two-step tree, two knots sharing a pair whose endpoint pair lies in no bond, and two disconnected knots. Independent search matched all four truth-table results: 3,4,none,none.

Measured final phase runs took about 0.01 seconds for controls, 1.06 seconds for structure, 0.12 seconds for smoke, and 1.15 seconds for the 24-search exact set. Peak reported RSS was below 32 MiB. Each invocation used one Python process with a 2,300 MiB address-space limit, in-process solvers and no subprocess. All commands used the required `.venv/bin/python -B`.

## Findings to integrate

1. **Narrowing — overview overstatement.** `research/RULER-LEVEL-20261114-001/ruler_level.md:14–16` says “Exactly where the knots form no cycle” and “there is no bond otherwise.” The first suggests necessity contradicted by its own cyclic-ruler examples; the second is stronger than `proof.md:18–20`, which asserts no bond only when there is **no path**. Replace the overview with the two actual sufficient clauses. An acyclic pattern can connect the levels by a longer route with a within-level knot, so failure to have a descending chain does not itself remove all bonds. A concrete abstract layered-forest control is `{(1,3,4),(4,5,6),(6,7,8)}` on addresses through level 3, k=1,s=2: it has no two-knot descending chain, yet both independent search and exhaustive support enumeration give L=5. This control is **not claimed to be generated by a registered description**. Its full evidence is in `controls.json`.
2. **Not a block — no stronger hypothesis needed in A.** Upper/lower uniqueness and the level argument establish acyclicity and connectedness; no prefix-parent condition, faithfulness, fullness assumption beyond what A constructs, or monotonicity in N needs to be added.
3. **Not a block — 117 is sufficient syntactic coverage, not sharp uniform coverage.** `proof.md:58–59` and `ruler_level.md:18–19` can correctly say those 117 descriptions are covered at every N by Theorem A. Do not infer that they are the only descriptions covered at every N. The root supplied the registered key `[1,[0],[0],[0],[[1,3,5],[3,6,7]]]`. All its state words are identity: the first placement is `{w0,w,w1}`, while the second is `{w,w,w0}` and is always discarded. Thus two nominal placements generate the bare tree at every N. The fresh builders confirm this at N=0,1,3,6,7. This is an exact symbolic reason, not an all-depth extrapolation from those checks.
4. **Not a block — evidence and scope.** Original producer `check.py`, exploratory Python and LEVEL-REACH producer Python were neither read nor run. The producer's reported 2,000 checks and 20 searches were not audited here. The new machine evidence is V2 relative to the producer, reusing previously independent referee code; it remains a same-task AI referee, not human review or external replication. This lane did not recount census classifications or review T1's original manifest.

No block was found in Theorem A itself. The summary narrowing should be integrated before approval of the overall text.

## Prior-work flags and artifacts

Own-knowledge flags, **unverified**: rooted binary tree automorphisms from invertible binary Mealy automata, the equivalence between Berge acyclicity and acyclicity of the classical incidence graph, and the uniqueness-of-parent level argument are standard mathematical observations. No network or literature lookup was performed, and external novelty remains unassessed. The new reach conclusion is an application of the program's cited T1, not an independent proof of T1.

Artifacts owned by this lane:

- `tree_audit.py`: test script, no producer imports.
- `interface.md`: audit question, inputs, controls, bounds and nonclaims.
- `structural.json`: every sampled key/depth and structural/action checks.
- `exact.json`: 24 N=6,7 exact searches and independent bond checks.
- `smoke.json`: nine smaller scaling/search checks.
- `controls.json`: five rejecting structural controls, four exhaustive truth-table controls, the non-A redundant-placement positive control, and the layered-forest overview control.
- `audit_summary.json`: compact machine-readable findings, source and artifact hashes.

Reproduction, one command at a time from the repository root:

```sh
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/RULER-LEVEL-20261114-001/referee-R1/codex/tree_audit/tree_audit.py controls
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/RULER-LEVEL-20261114-001/referee-R1/codex/tree_audit/tree_audit.py structural --count 120
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/RULER-LEVEL-20261114-001/referee-R1/codex/tree_audit/tree_audit.py smoke
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/RULER-LEVEL-20261114-001/referee-R1/codex/tree_audit/tree_audit.py exact
```
