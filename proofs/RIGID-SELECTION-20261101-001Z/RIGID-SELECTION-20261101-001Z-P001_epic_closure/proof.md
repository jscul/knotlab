# Closure of the rigid-selection epic

Status: Proved

Ticket `RIGID-SELECTION-20261101-001Z`, 2026-11-01.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RIGID-SELECTION-20261101-001/rigid_selection.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Over a field every global failure has corank 1 and is rigid, at every arity. Blurring keeps rigidity. S3 and D_p have only blurred-parity knots on full ranges. Simple non-affine three-value Mal'tsev algebras have no full-range knots. | new as stated; classical parts (linear algebra, Goursat, skew-free) | A, items 1 and 3 |
| 2 | Over Z_(p^k) a failure is global exactly when its class is a nonzero element of every ⟨g_L⟩. After removing L, the solutions are a coset of order \|M\| · \|ann(g_L)\|. Cyclic groups leave only ties. | new as stated; elementary | A, item 2 |
| 3 | Signed Z4 has global failures that keep knots: after every removal on a 6-point 4-regular substrate, and after one removal on a 9-point cubic substrate. Nine points is the minimum at three places. Unit-weighted Z8, Z9, Z25 and Z27 do the same on many substrates. | new | B |
| 4 | Selection spends the top layer. Over any finite chain ring, a global failure has m ≤ n + 1 and leaves top layers of dimension n − m + 1. A kept knot has at most one full-range variable and hides at most k − 1 digits; the bound is attained. | new; elementary (moderate folklore risk) | D |
| 5 | Blurred signed Z4 on five values composes like cycles, selects globally and recognisably, counts #P-complete, and keeps knots inside its selected spaces, below its top layer. | new | C, items 1–6 |
| 6 | At two values, composing like cycles and keeping emergence inside selected spaces exclude each other. The knot keeps emergence there. | new as stated; from KNOT-CIRCUITS Theorem 2 and D | C, consequence |
| 7 | Precision note: the census holds 73 substrates (60 incidence graphs read both ways). BEYOND-TWO C's statements hold under both readings. | check | B, check 3a; decision note |

## Pending the owner

- **Still open.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): test whether every law that composes like cycles keeps the top layer of its selected spaces rigid.
- **The top layer.** The image in (A/θ)^n, where θ is the algebra's unique maximal congruence.
- **First test.** Non-abelian groups that compose like cycles, of order at most 24, and the 1020 non-simple three-value Mal'tsev
  algebras, on regular substrates.
- **Then.** A proof from ticket D and commutator theory.

The table is in the decision note.
