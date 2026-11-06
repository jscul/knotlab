# Closure of the equal-acyclic-counts epic

Status: Proved

Epic `ACYCLIC-COINCIDENCE-20261023-001` closed on 2026-10-23. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/ACYCLIC-COINCIDENCE-20261023-001/acyclic_coincidence.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In a signed graph, flipping the sign of a path through vertices of degree 2 whose ends are also joined by a positive and a negative link keeps the chromatic polynomial (equal to that of the rest times ((λ − 1)^k − (−1)^k)/λ), the zero-free chromatic polynomial, T(x, 0) and so the number of acyclic orientations. It can change the Tutte polynomial. | A gluing along the doubled edge in Zaslavsky's colouring framework; high folklore risk; not found stated in a short search | `ACYCLIC-COINCIDENCE-20261023-001A-P001`, Lemma 1 and Theorem 2 |
| 2 | Each of the 48 skeletons behind the six residual twist relations on L(3,1,3,1) is explained by one such flip followed by an isomorphism of frame matroids. With the earlier mechanisms, every exact twist relation found on the four fresh genus-2 surfaces now holds skeleton by skeleton. | A recorded computation; new to the program | `…001A-P001`, Corollary 3 and its check |
| 3 | The residue was not a coincidence of one value: the whole chromatic polynomial agrees in all 48 pairs. | A recorded computation | `…001A-P001`, check |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- that the six relations had no structure behind them;
- that isomorphic reduced pieces are the right notion of "same piece" for the acyclic factor;
- that series paths outside clusters always matter (their sign does not next to a doubled link);
- that the equality might hold only at λ = −1.

## Recommendation

**Full pivot back to the main route.**
- **This side route is settled.** The identity was found, so the stop rule is met, and refining it on more surfaces would only
  re-map known mechanisms.
- **The next step.** The dual-pair test for three-place lines (`TRIPLE-SHIELD-20261023-001`), already running. Interest: 2/3.
- **Reopen this line** if a three-place relation turns on acyclic or chromatic counts.
- **Execution:** started (the frozen experiment of `TRIPLE-SHIELD-20261023-001A`).
