# The same overlapping ternary knots with different SAT decisions

November 14, 2026 (Pacific). Goals G3 and G16.

## The question

Can two explicit Boolean systems have the same entire family of constrained triples of open choices, with seven allowed states apiece, while their completion questions admit an elementary algorithm on one family and encode all of strict 3-SAT on the other? How many choices suffice to read the relative signs?

## Prior work in the program

`scripts/track.py objects "constraint pinning" --until 2026-11-14 --exclude SIGNED-KNOT-OVERLAP-20261114-001 --limit 3`

`scripts/track.py objects "clause knot allowed states" --until 2026-11-14 --exclude SIGNED-KNOT-OVERLAP-20261114-001 --limit 3`

`scripts/track.py objects "overlap signs switch" --until 2026-11-14 --exclude SIGNED-KNOT-OVERLAP-20261114-001 --limit 3`

- `SUBST-NEST-20261112-001` studied Distinction substitution of finite not-all-equal blocks into knot patterns. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.
- `TOP-INFO-20261114-001` studied Which conditions at the root and the target bound the least bond to a covered copy at depth s: effective reading, bond-pinning, middle members. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.
- `PIN-RULE-20261112-001` studied Distinction substitution bound by the block's own knots in every order. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.
- `KNOTS-ALONE-20261111-001` studied Finite knot patterns under the uniform clause law. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.
- `HARMONY-ARITH-20261112-001` studied Allowed state periods and antiperiodicity of one-shift harmonies under four laws. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.
- `LEVEL-REACH-20261114-001` studied Least bonds from level 3 to level 3+s in addressed patterns with knots within and between levels. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.
- `PLACE-FLIP-20261110-001` studied Board-value knots read by flips in place in copies of finite boards. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.
- `BARE-NAMES-20261110-001` studied Boards on abstract names with neighbour distinctions and cell values. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.
- `OVERLAP-READ-20261111-001` studied Knot patterns with uniform overlap three. The present comparison fixes the carrier, all designated ternary scopes, all supports of the ternary K1–K3 relations, and the rule for later pins before comparing signs.

The strict-3-SAT completeness admission EVIDENCE-001D supplies the classical decision baseline. KNOT-FOUNDATION-20261019-001E supplies the canonical forgetting test and majority obstruction for strict 2-CNF. COMPRESSION-ROBUST-PROOF-COMPLEXITY-001T studies pinning and role sorts; KNOTS-ALONE-20261111-001 studies uniform monotone rules. Our proposed difference is the classification of all three-variable projections for a shared, partially readable system and the exact size-four relative sign test. The joint-braid predecessor distinguishes advance message size from online decision.

## Prior work outside the program

Fixed factor graphs for 3-SAT have been studied by Feige and Jozeph (https://arxiv.org/abs/1204.6484), and tractable Boolean constraint languages by Schaefer (https://doi.org/10.1145/800133.804350). These are primary comparisons. Our question fixes the entire signed rule system at each size before the input pins arrive, and asks additionally which global projections are actually constrained; the working proofs use direct reductions and local source evidence.

## Evidence and stopping rule

Give each possible signed three-variable clause a permanent slot. A slot has the rule w1 OR w2 OR w3 and three rules (NOT e_i) OR (NOT w_i) OR literal_i on distinct original variables. Each slot's guards and witnesses are private. Use all-positive literals as the aligned control. Test all one-, two- and three-variable assignments in a small genuine two-slot system and challenge four-coordinate demands. Compare with an XOR equation on each declared scope; state the reading at the unpinned prefix and the separate later pins. Stop at a counterexample or a uniform characterization and verified decision comparison. Do not infer an unconditional time lower bound from NP-completeness or from any restricted untangling model.
