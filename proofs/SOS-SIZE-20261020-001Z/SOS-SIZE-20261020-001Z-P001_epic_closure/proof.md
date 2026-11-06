# Closure of the sum-of-squares epic

Status: Proved

Epic `SOS-SIZE-20261020-001` closed on 2026-10-20. This is a ledger: one line
per conclusion, with its novelty label and evidence. It makes no new claim.
The decision note is `research/SOS-SIZE-20261020-001/sos_size.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A tangle of order k of the cut function gives a pseudo-expectation for Tseitin up to degree k − 1 that defeats Sherali–Adams and sum-of-squares refutations. This holds in the clause and standard encodings, and in the balanced encoding when every degree is below k; a hub of degree cvw shows the condition is needed. | Grigoriev's construction with a tangle in place of expansion; the general-graph form was not found stated | `SOS-SIZE-20261020-001B-P001`, checked exactly on 15 graphs with controls |
| 2 | SoS degree lies between cvw and cvw + 4 once cvw ≥ 2Δ − 2; SA degree lies between cvw and ⌊3cvw/2⌋ + 1. | not found stated; Θ(tw) may be folklore | `…001B-P001` (Berkholz's simulation, Atserias–Dalmau, `PC-DEGREE-20261020-001B-P001`) |
| 3 | SoS and SA size is 2^{Θ(tw)} on graphs with cell systems: grids, d-dimensional grids, plane graphs with short faces, and walls. With twin variables the same holds on minor-free graphs, and 2^{Ω(tw^{1/9}/polylog)} holds on all graphs. | not found stated (targeted search) | `…001B-P001`, with the restriction lemmas of `CELL-SIZE-20261020-001B-P001` |

## Recommendation

**Continue, by converting.** Write one self-contained note on Tseitin
formulas beyond expanders:
- the degree characterizations for NS, PC, SoS and SA;
- size 2^{Θ(tw)} on cellular graphs for resolution, PCR, SoS and SA;
- the scrambled-wall barrier.

Interest 2/3. This is deferred to the owner, who asked that write-ups be kept
for novel results of real magnitude.
