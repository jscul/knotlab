# Closure of F2 polynomial calculus on the sphere's count

Status: Proved

Ticket `PC-COUNT-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PC-COUNT-20261110-001/pc_count.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Over every field, every polynomial-calculus refutation of the sphere's count has degree at least c n^{1/4}/log n (the functional pigeonhole principle on an expander, Miksa and Nordstrom, through LeftPigeon and the program's chain). | known-with-delta, folklore risk high; proved (from published bounds) | A |
| 2 | Over F2, tree-like Res(xor) refutations of the count have size at least 2^{c n^{1/4}/log n}, and parity decision trees for it depth at least c n^{1/4}/log n. | known-with-delta; proved | A, with TREE-XOR-20261110-001B |
| 3 | The count's F2 polynomial-calculus degree is 3 on K_2, 4 on K_3 and at least 5 on K_4; its Nullstellensatz degree is 6 on K_2 and at least 6 on K_3; the two-sided control has degree 3. | new as numbers; computed (pre-registered, exact) | B |

## Answer

Algebra over any field cannot refute the count in low degree, so tree-like Res(xor) needs exponential size on it; the small spheres
already climb one degree per step.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Recommendation

**Research directions**, none selected, for the coordinator. The table is in the decision note.
