# Closure of the re-querying epic

Status: Proved

Epic `URQUHART-TSEITIN-20261020-001` closed on 2026-10-20. This is a ledger:
one line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/URQUHART-TSEITIN-20261020-001/urquhart_tseitin.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For bounded degree, Urquhart's conjecture on a family is equivalent to general resolution 2^{Ω(tw)}/poly(n) on it. It therefore holds on graphs with cell systems, minor-free graphs (planar included), linear-treewidth families and families with compact topological minors. | short consequence of known results and earlier epics | `URQUHART-TSEITIN-20261020-001B-P001` |
| 2 | Read-2 branching programs of size 2m + 2 compute satisfiable Tseitin formulas, so branching-program size arguments stop at regular resolution. | likely folklore | `…001B-P001` (checked on all assignments) |
| 3 | Hole-faithful refutations need 2^{Ω(tw)}. Hole-faithful means no step forgets a variable touching the hole's region after the pivot. Davis–Putnam refutations are regular and hole-faithful. | not found stated; Haken–Urquhart counting with a faithfulness condition | `…001B-P001` (exact posteriors on seven graphs) |
| 4 | A refutation of size 2^{o(tw)} must both re-read variables and forget at the hole's region. One such forgetting step already biases the hole's posterior on every checked graph. | diagnosis | `…001B-P001` (non-faithful control on four graphs) |

## Recommendation

**Continue, by converting.** Write one self-contained note on Tseitin formulas
beyond expanders:
- degrees;
- sizes on cellular graphs;
- the Urquhart equivalence;
- the two barriers.

Interest 2/3, deferred to the owner. The alternative is a full pivot to a new
barrier.
