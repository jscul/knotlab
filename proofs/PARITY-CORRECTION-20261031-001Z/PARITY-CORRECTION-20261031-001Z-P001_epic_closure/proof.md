# Closure of the parity correction

Status: Proved

Ticket `PARITY-CORRECTION-20261031-001Z`, 2026-10-31.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PARITY-CORRECTION-20261031-001/correction.md`.
- **The supersession record** is `research/PARITY-CORRECTION-20261031-001R/records.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Lane B's claim that parity's coupling family is polynomial everywhere is false. The Hadamard change makes the points parity checks, and the count is a code weight enumerator. | correction; elementary | A, Lemma 1 |
| 2 | Fan–Cai's Theorem 2.2 applies: [1, λ, 1, λ] is #P-hard for real λ > 0, λ ≠ 1 (on cubic bipartite graphs). Their gadget G4 is the theta substitution. | classical (Fan–Cai 2020) | A, Lemma 2 |
| 3 | Theta substitution: M_par(θH; λ) = (2λ(1 + λ))ⁿ M_nae(H; λ + 1/λ − 1). The even forms are related by squaring. | G4 read on cubic systems; the squaring link appears new | A, Theorem 3 |
| 4 | Counting parity's coupling on connected simple cubic systems is polynomial exactly at λ ∈ {0, 1, −1, i, −i, ∞} and #P-hard at every other complex λ. | λ > 0 Fan–Cai, rational λ Cai–Fan–Liu; complex λ not found (moderate folklore risk) | A, Theorem 4 |
| 5 | It stays #P-hard on connected simple systems where parity fails: certificates survive grafting, and two calls recover any count. | elementary | B |
| 6 | The uniqueness theorem (PINNING C) stands as stated. The scan's verdict on parity stands with a corrected reason. Seventeen dependent statements are located and marked. | documentation | R |

## Literature

- **Fan and Cai (2020, arXiv 2011.09110).** Theorem 2.2 and Lemma 4.2, case 3.
- **Cai, Fan and Liu (2021, arXiv 2110.01173).** Rational values with mixed signs.
- **No complex-valued dichotomy for Holant(f | =3)** was found in the abstracts checked.

## Recommendation

**Continue** (2/3): the value-free four-place scan, approved by the owner before this correction.
- **Guards.** Use two-sided transforms or dichotomies only, and test whether failures are local.
- **The question.** Does any value-free four-place knot have global, recognisable failures and a hard count?
- **Execution.** It resumes now. The decision note has the full assessment.
