I'd freeze it only after four fixes. I answered from your description alone and did not open the code, so the points about the law's tie-breaking and what it reads are things to check, not findings.

## 1. Design flaws

- **The likeliest counterexample is not targeted.** If the law reads only what the table determines, the two sides of a start-level other-states collision grow in parallel and may keep both the table isomorphism and the other states. Grow both sides of every start-level other-states collision first (the 242 backed pairs and the rest), one and two rounds, and compare directly. If all stall at once, record it, because that is the real reason G1 would hold.
- **No positive control.** Run the known other-states pairs among the 503,039 through the same key and pairing code and require that all are recovered. Otherwise a zero cannot be told from a blind pipeline.
- **The states test can produce a false failure.** "Other states" is concluded when no pooled-table isomorphism carries one equation space to the other, but a renaming need not be a table isomorphism. Treat that verdict as "candidate" only. Hitting the 5,000 cap or the alarm must count as unresolved, and G1 passes only with zero unresolved.
- **Twins.** A twin swap fixes the table but may move the equation space. Either the rank test quantifies over within-class permutations, or you prove invariance.
- **Cross-start and cross-round collisions.** Use one global pool keyed on the hash, never per start or per round. Dedupe by exact arrangement class and keep the multiplicity, since the same class will arrive from many starts and at different round indices.
- **Isomorphic starts.** If the 503,039 are classes, growth must not depend on labels. "Cheapest counts" suggests ties, so regrow relabelled copies of a sample and require isomorphic stages. If that fails, G1 is about one representative's growth and should say so.
- **Stalls.** These bias the population towards small starts. Report stages by start size and the stall counts, and treat G2 as the power measure: state how many same-table non-isomorphic class pairs were examined. If that number is small, G1 is near-vacuous; fix a floor before the run.
- **Meet once.** "Each new junction meets each parent once" is not the property. Assert it pairwise over all junctions, including new against new and new against non-parent.
- **Key soundness.** It is fine: pooling is a function of the full table, so isomorphic full tables give equal keys. Do log the table diameters, because if none exceeds 8 the escalation ladder is never exercised.

## 2. Population

Score the rounds separately, but not by round index, which depends on the start. A class can be round 1 from one start and round 2 from another. Give each class an intrinsic depth: peel while one round of the law from the peel gives it back, and count the peels.

Report G1 in cells (1,1), (1,2+) and (2+,2+), and keep the overall statement as the registered one. Your earlier numbers (38 both peel once, 0 both peel twice) make "fails at depth 1, holds at depth 2" a live outcome, and a pooled verdict would hide it. Run the self-grown control on every stage rather than a sample, since it is one peel and one round each.

## 3. Bet

| Outcome | Probability |
|---|---|
| G1 holds overall | 80% |
| G1 fails only among depth-1 pairs | 14% |
| G1 fails with a depth-2 stage involved | 6% |
| G2 holds | 95% |

The earlier zeros (77 and 85 arrangements) are too small to move this much. Most of my confidence comes from the census record to 40–50 junctions.

## 4. Where a failure would be, and how to check it

I'd expect the first pair to be two round-1 stages whose starts are themselves a table-isomorphic other-states pair, or share such a core. It would be at the small end, about 10–14 junctions, after a short round that added few junctions, with twins present.

Check it outside the pipeline:

1. **Non-isomorphism:** canonical forms of the two arrangements from a second tool, such as nauty or bliss on the incidence graph.
2. **Table isomorphism:** recompute the full tables with separate code, write the isomorphism down as an explicit permutation and verify it entry by entry.
3. **Other states:** prove it by an invariant, not by exhausting isomorphisms. Use the rank, the weight enumerator of the equation space and its dual, or a canonical form of the low-weight words.
4. **Provenance:** regrow both stages from their starts with relabelled inputs and re-assert pairwise meet-once.
5. **Persistence:** grow a third round and record whether the pair survives.
