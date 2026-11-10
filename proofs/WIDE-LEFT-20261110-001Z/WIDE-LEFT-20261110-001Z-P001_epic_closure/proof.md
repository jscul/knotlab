# Closure of the decoder route for the 2n-pigeon principle

Status: Proved

Ticket `WIDE-LEFT-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/WIDE-LEFT-20261110-001/wide_left.md`; the novelty and transfer check and the frozen target are beside it.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every dag-like Res(xor) refutation of the binary left-pigeon principle with 2n pigeons, and so of the PPADS-complete one with n + 1 pigeons, has exp(Omega(n / log^5 n)) lines (3S + 2n^2(l + 1) >= exp(0.005 k / l^2 - 1), k = floor(n/(64 l^3)), l >= 20). | new as far as found; known-with-delta in technique; proved (V1, from Braun's lemmas, assumption A55) | A |
| 2 | The spare-row space meets the decoder's kernel only in zero at (4, 1), (8, 1), (16, 2), and the cube identities hold where checked. | computed (pre-registered) | B |

## Answer

The decoder route gives a dag-like Res(xor) lower bound for the binary left-pigeon principle; nothing transfers to the knot sphere's count.

## Pending the owner

- Whether and how to share the result.

## Recommendation

**Full pivot** from the decoder route (finished in this program), with a note for review recommended first, for the coordinator to
confirm. The table is in the decision note.
