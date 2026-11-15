# When switch settings let two blocks forget a shared choice

2026-11-15 (Pacific). Goals G3 and G16.

## The question

On fixed positive two-route wiring, when does splitting a name across a cut preserve every externally visible boundary assignment, what can a solver certify locally, and how difficult is universal recognition?

## Prior work in the program

`scripts/track.py objects "guard-dependent cut shared middle boundary valuations" --until 2026-11-15 --exclude GUARD-CHOICE-SEPARATION-20261115-001 --limit 3`

`scripts/track.py objects "splitting a shared choice preserves boundary triples" --until 2026-11-15 --exclude GUARD-CHOICE-SEPARATION-20261115-001 --limit 3`

`scripts/track.py objects "private padding reachability independent boundary" --until 2026-11-15 --exclude GUARD-CHOICE-SEPARATION-20261115-001 --limit 3`

`scripts/track.py objects "lossless joins fixed guarded routes" --until 2026-11-15 --exclude GUARD-CHOICE-SEPARATION-20261115-001 --limit 3`

- `ONE-RELAY-PADDING-20261115-001` studied Linear ordinary SAT and full witness construction with one repeated middle and arbitrary pad reuse. Compare the chosen joint-versus-split boundary relation on the unchanged raw wiring under different switch settings.
- `ROUTE-FRONTIER-MEMORY-20261115-001` studied Tight deterministic stage-order memory and exact residual count on one fixed guarded route schedule. Compare the chosen joint-versus-split boundary relation on the unchanged raw wiring under different switch settings.
- `TWO-RELAY-PADDING-20261115-001` studied NP-completeness with at most two uses in both middle and pad roles, and a complementary sign-parameter solver. Compare the chosen joint-versus-split boundary relation on the unchanged raw wiring under different switch settings.
- `SUBST-NEST-20261112-001` studied Distinction substitution of finite not-all-equal blocks into knot patterns. Compare the chosen joint-versus-split boundary relation on the unchanged raw wiring under different switch settings.
- `UNSIGNED-ROUTE-JOINS-20261115-001` studied All-input correctness of the original stage scan and linear decision after arbitrary positive middle joins. Compare the chosen joint-versus-split boundary relation on the unchanged raw wiring under different switch settings.
- `SWAPPED-ROUTE-GROUPING-20261115-001` studied Linear mixed block readers with both global k and q large. Compare the chosen joint-versus-split boundary relation on the unchanged raw wiring under different switch settings.
- `ROUTE-PARITY-TRANSFER-20261115-001` studied Exact signed-literal projection of the pinned raw two-use route compiler. Compare the chosen joint-versus-split boundary relation on the unchanged raw wiring under different switch settings.

The previous optimal-order and block result applies to cuts across which no name repeats. The fixed two-use compiler realizes any strict CNF by its guard values. Those are the baselines.

## Prior work outside the program

Existential variable elimination and lossless joins in the sense of Fagin, Multivalued Dependencies and a New Normal Form for Relational Databases (https://doi.org/10.1145/320557.320571), are comparisons only. All mathematical claims here are proved directly.

## Evidence and stopping rule

Keep the same raw clause skeleton and physical wiring across switch changes, and use splitting only as the comparison. Measure triples (left endpoint, cut bit, right endpoint) before external pins, and separately project away the cut bit. Check table equality and original raw witnesses independently. Seek active cases, adversarial splits, a recognition lower bound, and distinguish it from a solver lower bound.
