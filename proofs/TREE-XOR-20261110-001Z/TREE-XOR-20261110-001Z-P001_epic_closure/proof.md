# Closure of tree-like Res(xor) on the sphere's count

Status: Proved

Ticket `TREE-XOR-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/TREE-XOR-20261110-001/tree_xor.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every parity decision tree for the sphere's count, hence every tree-like Res(xor) refutation, has depth at least c n^{1/8} / log n. | known-with-delta; proved (from Beame et al.'s degree bound) | A |
| 2 | A parity tree with s leaves gives an F2 polynomial-calculus refutation of degree log2 s + w, so tree-like Res(xor) size on the count is at least 2^(deg_PC - 3). | known-with-delta; proved | B |

## Answer

Polynomial height for tree-like Res(xor) on the count; its size is decided by the count's F2 polynomial-calculus degree (B84).

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Recommendation

**Research directions**, none selected, for the coordinator. The table is in the decision note.
