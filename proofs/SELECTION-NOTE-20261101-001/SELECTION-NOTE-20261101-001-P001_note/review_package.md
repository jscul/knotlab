# Review package: "Native selection on regular systems"

## Claims and evidence

| Note | Claim | Proved in | Novelty and folklore risk |
| --- | --- | --- | --- |
| Theorem 1 | On the knot's spaces, the coupling with weight λ per monochromatic line is easy exactly at λ ∈ {0, 1, −1, −3, ∞}; #P-hard elsewhere over ℂ. | `KNOT-COUPLING-20261031-001` A, B, C | No dichotomy restricted to these spaces found; tools classical (gadgets, interpolation, Beukers–Smyth). Moderate. |
| Theorem 2 | 34 three-place knots, 5 classes; only not-all-equal excludes both constants and is flip-invariant. | `PINNING-20261031-001A` | Elementary census; no source found. Low novelty, low risk. |
| Theorem 3 | Pinning theorem on cubic systems. | `PINNING-20261031-001A` | Close to Dalmau–Ford (2003), who use constants. Moderate to high folklore risk. |
| Theorem 4 | Unless P = NP, not-all-equal is the only mutually selecting three-place knot. | `PINNING-20261031-001C` | New statement from classical parts. |
| Remark (corrected claim) | Parity's weighted family is not easy everywhere; the earlier claim is withdrawn. | `PARITY-CORRECTION-20261031-001` (A, R) | Fan–Cai (2020) Theorem 2.2. |
| Theorem 5 | Parity's coupling is #P-hard except at six points (theta substitution). | `PARITY-CORRECTION-20261031-001A` | Fan–Cai for real λ > 0; Cai–Fan–Liu for rational; complex case not found. Moderate. |
| Theorem 6 | Parity's failing class carries every hard instance (two calls). | `PARITY-CORRECTION-20261031-001B` | Elementary (certificate-preserving splice, Cayley–Hamilton). |
| Theorem 7 | Signed not-all-equal never fails on k-regular systems for k ≥ 4. | `FOUR-PLACE-20261031-001B` | Plain case Thomassen (1992); signed case via Seymour's argument, not found stated. Moderate. |
| Theorem 8 | Four-place knots = independent sets of the 4-cube; 742 in 20 classes; the clause never fails. | `FOUR-PREFER-20261101-001A`, `FOUR-PLACE-20261031-001A` | Elementary; no source found. |
| Theorem 9 | Twelve four-place classes build links and are NP-complete on 4-regular systems. | `FOUR-PLACE-20261031-001C`, `FOUR-PREFER-20261101-001B` | Explicit pieces new; techniques classical. |
| Corollary 10 | A mutually selecting four-place knot would lie in five weak classes. | `FOUR-PREFER-20261101-001D` (with C, documentation) | New statement; the five classes are open. |
| Lemma 11, Theorem 12 | Complementarity; the knot's spaces compose only through hubs. | `KNOT-COMPOSE-20261101-001A` | Lemma elementary; the hub reading found in no source. |

## Replay

```bash
.venv/bin/python -B replay.py --write        # reruns the sixteen cited checks in a temporary copy (about an hour)
.venv/bin/python -B independent.py --write   # nine claims in fresh code
.venv/bin/python -B check.py --write         # ties the quoted numbers, compiles the note, controls
```

## Questions for a reviewer

1. Is the coupling dichotomy on non-2-colourable cubic systems (Theorem 1) known, perhaps as a corollary of a complex-valued Holant
   dichotomy?
2. Is the signed form of Thomassen's theorem (Theorem 7) stated anywhere?
3. Does the definition of mutual selection, recognisable failures plus a hard count, have a precedent? Is the local/global distinction
   the right refinement?
4. Do the five weak four-place classes (Corollary 10) never fail? A Hall-type or Thomassen-type argument for them would close the
   four-place picture.
5. Are the hub results (Theorem 12) consequences of known tight-cut theory?

## Status

- **Review.** Not externally reviewed.
- **Sharing.** Nothing has been sent; sharing is the owner's decision.
