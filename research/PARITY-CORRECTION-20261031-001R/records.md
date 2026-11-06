# What the parity error withdraws and what survives

Ticket `PARITY-CORRECTION-20261031-001R`, 2026-10-31. Documentation.

## The error

- **Where it was made.** `MUTUAL-SELECTION-20261031-001B` (lane B of the mutual-selection scan, closed 2026-10-31).
- **The claim.** Parity's whole coupling family [1, λ, 1, λ] is "a generalized equality, affine and polynomial on every graph".
- **Why it is false.**
  - The Hadamard change of basis does turn the lines' weights into generalized equalities. It also turns the points' equalities into
    even-parity checks, so the transformed count is a code weight enumerator.
  - Fan and Cai (2020, Theorem 2.2) prove [1, a, 1, a] #P-hard for a > 0, a ≠ 1.
  - Ticket A proves the full picture: counting parity's coupling on connected simple cubic systems is polynomial at λ ∈ {0, 1, −1, i, −i, ∞}
    and #P-hard at every other complex λ.
- **Who found it.** A peer session reported the error at the owner's request, 2026-10-31.

## Status of every dependent statement

Closed artifacts stay unedited, and this record supersedes them. `records_check.py` confirms that each quoted statement is at its listed
path (`records_check.log`: all 17 locations found).

| # | Where | What it says | Status | Replacement |
| --- | --- | --- | --- | --- |
| 1 | `research/MUTUAL-SELECTION-20261031-001B/report.md` (finding 1, reading) | the family is "a generalized equality, affine and polynomial on every graph"; "parity's family is easy everywhere"; "the selection is vacuous" | **withdrawn** | A (dichotomy); B (the failing systems carry every hard instance) |
| 2 | same lane, `parity_clause.py` docstring | the family is "a generalized equality, affine, polynomial on every graph" | **withdrawn** | A |
| 3 | same lane, `manifest.json` claim | "its whole coupling family [1, lam, 1, lam] is a generalized equality (affine) for every lam" | **withdrawn** (the other sentences stand) | A |
| 4 | `tickets/MUTUAL-SELECTION-20261031-001B.json` (objective, status) | "its whole coupling family … is affine, so parity selects nothing" | **reason withdrawn**; "selects nothing" survives | B |
| 5 | `tickets/MUTUAL-SELECTION-20261031-001.json` (status) | "parity fails recognisably but its whole family is affine" | **reason withdrawn**; the scan's verdict survives | A, B |
| 6 | `research/MUTUAL-SELECTION-20261031-001/decision.md` (lane B row, verdict) | "its whole coupling family is affine, so it selects nothing" | **reason withdrawn**; conclusion survives | B |
| 7 | `proofs/MUTUAL-SELECTION-20261031-001Z/…/proof.md` (conclusion 3) | "its whole coupling family is affine, so it selects nothing" | **reason withdrawn**; conclusion survives | B |
| 8 | `proofs/PINNING-20261031-001C/…/result.json` and `check.py` (table) | parity: "no (affine: its whole family is polynomial everywhere)" | **reason withdrawn**; the verdict "no" survives | parity's solution count is 2^{n−r} or 0 (Gaussian elimination), so it fails (M2) |
| 9 | same proof, `proof.md` (dependencies) | "Parity's family is affine" (citing lane B) | **withdrawn**; nothing in the theorem used it | A |
| 10 | same proof, `proof.md` (table row) | "no: affine, its counts are 2^{nullity} or 0" | **survives**: it concerns the solution count | — |
| 11 | `research/PINNING-20261031-001/discoveries/PINNING-20261031-001-D002.json` | "parity is affine, the clause never fails" | **survives**: the law is affine and its count polynomial; no family claim | — |
| 12 | `docs/KNOT_INTUITION.md` (mutual-selection and pinning entries) | "parity fails recognisably but makes nothing new easy"; "is affine" | **survive**; a dated note records the replaced reason | B |
| 13 | memory summaries outside the repository | "a generalized equality, so affine everywhere and nothing is selected" | **corrected** at closure | A, B |

## What survives

- **Parity's decision and solution count.** Both are polynomial by Gaussian elimination: 2^{n−r} solutions or none. Its failing systems
  are recognisable, and they exist exactly when the incidence matrix is singular over GF(2).
- **The uniqueness theorem (`PINNING-20261031-001C`), as stated.**
  - Mutual selection there is (M1), non-empty recognisable failures, plus (M2), the law's own solution count #P-hard in general.
  - Parity fails (M2), so not-all-equal remains the only three-place knot with mutual selection (unless NP-complete problems are
    polynomial; unconditionally on plain systems).
- **The scan's broader reading, now proved for parity.**
  - In that reading a law is selected back if its failing systems make some hard member of its coupling family easy.
  - Parity's failing systems make nothing easy: for every λ outside the six easy points, counting is #P-hard on connected simple systems
    where parity fails (B).
  - Fibonacci and x ∨ (y ≠ z) still fail (M1): recognising their failures is coNP-complete. The clause never fails. So the knot is unique
    in this reading too.
- **Unaffected work.**
  - KNOT-COUPLING-20261031-001 (the knot's coupling dichotomy).
  - The counting note COUNT-NOTE-20261031-001 and its sources PLAIN-COUNT / PLAIN-BRACE.
  - The pinning theorem, the five classes, and x ∨ (y ≠ z) NP-complete.
  - The scan's other lanes.
  - `records_check.py` finds no use of the withdrawn claim in those records.

## What is new

- **The dichotomy for parity's coupling family (A).**
  - It comes through the theta substitution, M_par(θH; λ) = (2λ(1 + λ))ⁿ M_nae(H; λ + 1/λ − 1), which is Fan–Cai's gadget G4.
  - In even-form variables, the knot's u is the square of parity's Hadamard ratio.
- **Hardness on parity's failing class (B).** A certificate in a small piece survives grafting into any host.
- **A sharper reading.** Recognisable failures select a law back only when they are global, as the knot's are: the Pfaffian property
  constrains the whole space. Parity's failures are local.

## The four-place continuation

- **Still justified.** Its target is whether three is the only arity with a mutually selecting law, under (M1) and (M2). The correction
  leaves that target intact.
- **Two guards added.**
  - Never infer that a weighted family is easy from a one-sided transform. Check both sides, or use a dichotomy or brute force.
  - For every candidate with recognisable failures, test whether its failures are local, i.e. whether a certificate survives grafting.
    Local failures cannot select.
- **Four-place parity.** Its count is polynomial, so it fails (M2) whatever its weighted family does.
