**Verdict: Confirmed with fixes.** Theorem I, the tie/forgetting implication on living families, the six ties beyond identity, and the chain counts reproduce. The asserted exhaustive label/order classification does not: the reported 44/45 includes a family that conserves parity. All 66 census caps, rather than only the reported 53, have identity cycles.

This is an offline referee audit of `TIE-CYCLE-20261114-001`, not a closure or publication operation. The earlier permitted referee engine supplies greatest-limit semantics, per-call SAT projection, and exact forgetting decisions; the tie search, core/label classification, split, and occurrence counters are fresh. All 12,772 families and 26,243 call relations were recomputed. A second, set-based implementation independently regenerated all 100 residual semigroups and their 159 non-rectangular idempotents. This is same-task AI independent-code checking (V2), not external replication. No Python under the prohibited study directory was opened or imported; no network or Git mutation was used. All writes stayed here.

## 1. Theorem I

**Not a block — the proof is correct and classical.** Put `S = <R_i>+`, using nonempty call words, and `I = S ∩ Rect`, including the empty relation when generated. Relational composition sends `U(A×B)V` to a rectangle, so `I` is a two-sided ideal. Color intervals of a long word by their product in finite S. A Ramsey monochromatic triple gives `e = e·e`, hence a contiguous idempotent factor; the ideal absorbs it. Conversely, powers of a nonempty word representing a non-rectangular idempotent stay non-rectangular. This proves the equivalence. Simon factorisation is another route.

For nonempty I this is exactly the classical Rees-quotient criterion: `S/I` is nilpotent iff every idempotent of S lies in I. If `I=S`, the quotient is the one-element zero semigroup. If I is empty, both forgetting and the all-idempotents condition fail; use an adjoined zero if a quotient is wanted. Do not test an identity supplied only by the empty word. [proof_review.md](proof_review.md) gives the details.

**Narrowing — “0 violations on 12,759” is a theorem consequence / implementation-consistency check, not an independent empirical prediction.** If forgetting is assigned from those same idempotents, agreement is settled by code construction. The allowed `heldout.json` cannot establish whether the unread Python literally did that, so I do not claim to have inspected that implementation. Here the earlier exact graph decision was compared with independently evaluated non-rectangular idempotent witnesses for **all 6,931 non-forgetting families**; all 5,841 forgetting automata are acyclic. There are no mismatches, and all 12,772 are independently decided.

## 2. Ties, fresh

A tie in a positive-word product R means `end[k] = start[j] xor sign` on **every pair of R**, with both bit values present. A tie cycle requires `j=k`. I searched all reachable non-rectangular products where an identity cycle did not already provide a witness. Rectangles may be discarded because they form an ideal and cannot acquire a nonconstant tie. Every positive witness was rechecked by set-based composition.

| Recomputed quantity | Training | Held out |
| --- | ---: | ---: |
| Families | 6,321 | 6,451 |
| Identity cycle | 3,355 | 3,470 |
| Tie cycle | 3,360 | 3,471 |
| Tie cycle beyond identity | **5** | **1** |
| Tie cycle and forgetting | **0** | **0** |
| Original census caps with a tie cycle | **33** | **33** |

**Not a block — the six exceptional ties reproduce.** None has a syntactic identity cycle or a directly unchanged same-numbered port. Some do pass a port to a different position, so “no port passed unchanged” must not mean that no port identity is reused anywhere. Their full keys, call arguments, signs, and witness words are in [ties_beyond_identity.json](ties_beyond_identity.json).

**Narrowing — make livingness explicit in the tie theorem.** Every recomputed generator is serial on the same nonempty greatest support `G_S`: for every x in `G_S`, some y in `G_S` satisfies `x R_i y`. Therefore every word and power is nonempty. Complement closure then supplies both bit values, and a self-tie prevents rectangularity in every power. Complement closure alone is insufficient: `{(000,001),(111,110)}` has self-ties but its square is empty. Syntactic permission to repeat a word does not replace this hypothesis.

**Narrowing — the 53 are a subset, not the full capped count.** The report's 26+27 omit the 7+6 cases recorded as “semigroup cap.” All **66** original census caps have syntactic identity cycles and fresh non-forgetting certificates, agreeing with the earlier referee. Also replace “0 of 6,445 held out” as a tie denominator: 6,445 is the original decided-semigroup total; there are **3,471** held-out tied families including the six omitted caps (3,465 excluding them).

## 3. Orders and labels

For each non-rectangular idempotent E, I formed the core `{x:xEx}`, its mutual-reachability classes, and the one-way comparabilities between distinct classes. Independently, a **conserved endpoint quantity** means a nonconstant `f(start)=g(end)` on the full active supports of E. It exists exactly when the classical bipartite incidence relation has multiple connected components. The second checker exhausts all 256 Boolean functions f; any nonconstant multivalued quantity has a nonconstant Boolean coarsening. Coordinate and parity labels were also checked directly.

| “Only order” means every non-rectangular idempotent passes | Training | Held out |
| --- | ---: | ---: |
| Some distinct core classes are comparable (published proxy) | **52/55** | **44/45** |
| That proxy, and no nonconstant endpoint quantity is conserved | **52/55** | **43/45** |
| Additionally, every endpoint has a unique class in that core quotient | **51/55** | **43/45** |

**Block — comparability does not imply “nothing is carried.”** Held-out family `4f5934b2e118` has sole non-rectangular idempotent `E=0x0058a01008051a00`, reached by word `[1,1]` (zero-based call labels). Its distinct core classes have one-way comparabilities, **and** every pair satisfies `start[0] xor start[2] = end[0] xor end[2]`. This is the reported **one** tie-free parity family, not a separate family outside the published 44. It has no coordinate tie cycle. Thus 43/45, not 44/45, support the full “order and nothing carried” interpretation. The frozen ≥80% H4 still passes under either reading.

**Block — an antichain core does not by itself conserve an endpoint label.** The source's residual-type unions reproduce exactly: training `order:52`, `nonlinear label|order|tie:1`, `order|tie:1`, `tie:1`; held out `order:44`, `order|tie:1`. These are **core-only labels**. In the full endpoint relations, none of the 159 residual idempotents has a coordinate tie. Ten idempotents (six training, four held out) have incomparable core classes and **no** nonconstant conserved endpoint quantity. For example training `9ef44064b996`, `E=0x7e4c32324c4c327e`, is labelled “tie” by its core, but its rows at states 000 and 111 reach every core state, forcing every global endpoint label to be constant. A label after restriction to the core is a different claim from a tie along the original word.

**Narrowing — endpoint classes need qualification.** Five additional idempotents have some comparable core classes and no conserved quantity, but transient endpoints do not each belong to a unique core class. Two are in training family `0274a8f97ce5`, explaining the optional stronger 51/55 count; three are in the already mixed held-out family `65ac0ef5e85c`. One may retain the core-only order definition, but cannot silently assign its classes to every endpoint. These maps are role-specific: a state can have different start and end classes. The JSON records all class maps and failures.

Mixed families are counted once, by the union of their non-rectangular idempotents' types. “Only order” is universal over those idempotents; a family with both order and core-tie idempotents does not count as only order. A **single idempotent** can also mix order and a conserved parity, as above. The 159 idempotents comprise 148 with a core comparability and no endpoint label, 10 with neither property, and one with both order and a parity. These are complete **data checks**, not a uniform classification theorem. The claimed exhaustive label/order dichotomy is false in general, with explicit complement-closed counterexamples in [proof_review.md](proof_review.md).

## 4. Chains and splits

**Not a block — 2,097/2,097 reproduces, as do training 2,126/2,126.** The corrected chain filter counts recursive **occurrences** after numeric calls are expanded: the counter in S and the counter in main must both be exactly `{S:1}`. A repeated helper call contributes twice. Finite helpers, wrappers, and unused definitions are allowed; “one-definition chain” is narrower.

| Corrected-chain population | Training | Held out |
| --- | ---: | ---: |
| All chains | 2,606 | 2,584 |
| One definition | 2,007 | 2,028 |
| Multiple definitions | 599 | 556 |
| No tie cycle, all forgetting | **2,126** | **2,097** |

The total is 5,190 chains: 4,035 with one definition and 1,155 with several. The study's `sha256("TIE:"+key)` split gives **6,321/6,451** families. Reapplying FORGET-RULE's unsalted split reproduces its **2,096/2,096** held-out identity-acyclic chains, so the change by one is a split difference. The old full-family split is separately recorded in the permitted earlier recount; no producer Python was used.

**Not a block — H2's nonchain numbers also reproduce:** 780/835 training and 838/883 held out forget without a tie cycle; the held-out share is 94.90%, inside the frozen 91.5–95.5% band. All-chain forgetting without a tie remains a census observation here, not a proved general chain theorem.

## 5. Wording and growth scope

**Not a block — “almost always by identity” is supported as census description.** Among the independently decided 6,931 non-forgetting families, 6,825 (98.47%) have an identity cycle; six more have a tie cycle beyond identity and 100 have none. State this population and keep the identity-cycle mechanism distinct from native-contact claims.

**Block — replace the exhaustive “only other way is an order” and “nothing is carried” prose.** Say instead: “Most residual families have only idempotents with one-way core comparabilities. A conserved parity can coexist with order, and core labels need not extend to full endpoint labels.” This retains the observed predominance without asserting the refuted dichotomy.

**Narrowing — preserve the earlier referees' growth scope.** The forgetting theorem concerns rectangularity of call-word relations. Its free-bond growth reading covers depth-s own targets in copies of S reached through S calls after main's finite expansion. It does not automatically cover targets in other recursive definitions or S reached after delays in another recurrence. For a wrapper main retain the one-level loss, `2+floor((s-1)/r)`, unless separately strengthened. Non-forgetting itself establishes neither bounded free bonds nor failure of growth. The study's initial scope sentence is correct; keep that scope attached to its informal answer too.

## Files written and validation

- Scripts: [recompute.py](recompute.py), [validate_and_summarize.py](validate_and_summarize.py), [write_report.py](write_report.py).
- Full data: [families_fresh.jsonl](families_fresh.jsonl), [residual_idempotents.json](residual_idempotents.json), [ties_beyond_identity.json](ties_beyond_identity.json), [capped_decisions.json](capped_decisions.json), [classification_counterexamples.json](classification_counterexamples.json).
- Receipts: [recomputation.json](recomputation.json), [validation.json](validation.json), [run_manifest.json](run_manifest.json).
- Proof review: [proof_review.md](proof_review.md), [proof_review.json](proof_review.json); this report is `codex_report.md`.

Every positive tie witness and all 6,931 non-rectangular idempotent witnesses were checked by a separate set-composition implementation. All 100 residual closures (13,208 non-rectangular products), all 159 residual idempotents, and all Boolean endpoint-label possibilities were rechecked; all controls passed. JSON/JSONL files parse. The complete main recomputation took about 18 seconds at about 209 MiB peak RSS; the second check took about three seconds at about 84 MiB. Commands used the requested `.venv/bin/python -B`; no compute cap was hit. Input/output hashes and exact invocations are in the manifest. Only this task's smoke outputs were removed. Shared correction logs and public records were left untouched under the write restriction.
