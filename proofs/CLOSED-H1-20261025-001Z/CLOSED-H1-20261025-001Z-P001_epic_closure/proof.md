# Closure of the closed-manifold epic

Status: Proved

Epic `CLOSED-H1-20261025-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/CLOSED-H1-20261025-001/closed_manifolds.md`, and the literature scan is
`research/CLOSED-H1-20261025-001/scan.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | An independent code path confirms the S₄ knot hardness of `BOUNDED-H1-20261025-001A`: diagrams, the bicycle law, the Potts identity, gadget knots and interpolation. An audit of its written proof finds no gap. | Verification (V1, same session) | `CLOSED-H1-20261025-001A-P001` |
| 2 | Every transposition colouring of a knot by S₄ has trivial longitude. Lifts to GL(2, 3) of a transposition and of its commuting double transposition anticommute. | Folklore risk high (Johnson–Livingston theory) | `CLOSED-H1-20261025-001B-P001`, (a) |
| 3 | Over every S₃ colouring of a knot, the lifts with a fixed transposition meridian and with a fixed 4-cycle meridian are equinumerous, and the 4-cycle lifts share one longitude. The proof uses half-lives-half-dies for the self-dual module V₄. | `candidate-local-delta`; overlap risk medium (Ishikawa 2025, abstract only) | `…001B-P001`, (b) |
| 4 | The connected quandles C[6,1] and C[6,2] colour every classical knot equally, which proves the 2013 conjecture of Clark, Elhamdadi, Hou, Saito and Yeatman for this pair. Every 3-colourable knot has a non-trivial C[6,2] colouring (Carter, Oshiro and Saito, 2009). A virtual knot shows the 3-manifold input is needed. | `candidate-local-delta`; no proof found in the bounded scan | `…001B-P001`, (c) |
| 5 | For every knot, C₂ + C₄ = 8 + 3T and 3·C₂(K) + C₂(K # 3₁) = 16 + 12T. So counting homomorphisms to S₄ is #P-hard on closed orientable 3-manifolds with H₁ = Z/2, with two queries per knot. Metabelian targets are polynomial there. | `candidate-local-delta`; folklore risk low to medium | `CLOSED-H1-20261025-001C-P001` |
| 6 | The 4-cycle longitude over an S₃ colouring is c^{2h}, where 2^h is the number of transposition lifts. | Observed on 230 of 230 colourings; not proved | Decision note (scratch) |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- **Closing up needs gluing gadgets that control the 4-cycle colourings.** Unnecessary: those colourings are already as many as the
  transposition colourings.
- **A transposition colouring with longitude z might exist.** Impossible, by the GL(2, 3) lift. The search was stopped.
- **The equal colouring counts of the order-6 quandles are only empirical.** Proved for classical knots.

## Recommendation

**Research directions: SL(2, 3) with bounded homology.**
- **First discriminator:** does the quadratic lifting obstruction of SL(2, 3) over A₄ keep the count polynomial with bounded H₁, or do
  knot gadgets make it hard? The answer decides whether the line is "abelian-by-nilpotent" or "Fitting height 2".
- **Interest:** 2/3.
- **Alternatives:**
  - a short note on the 2013 conjecture and the closed hardness, after reading Ishikawa's full text (2/3);
  - the parity law for 4-cycle longitudes (1/3);
  - the other Galkin pairs (1/3);
  - return to the core intuitions (1/3).
- **Execution:** deferred to the owner.
