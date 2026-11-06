# Polynomial calculus degree of Tseitin formulas: half the carving width

Epic `PC-DEGREE-20261020-001`, closed 2026-10-20.

## What was found

Over any field of characteristic other than 2, take a connected graph G with
an odd charge and its Tseitin system.
- **Balanced encoding.** Write each vertex as one balanced ±1 binomial. Then
  the polynomial calculus degree, measured modulo y² = 1, lies between
  ⌈cvw/2⌉ and ⌊cvw/2⌋ + 1, where cvw is the carving width. When cvw is odd it
  equals ⌈cvw/2⌉ exactly.
- **Standard encodings.** The standard binomial and clause encodings need
  max(maxdegree, that value). Counting degree before reduction adds at most
  one.
- **Charge placement.** None of this depends on where the charge sits
  ([proof](../../proofs/PC-DEGREE-20261020-001B/PC-DEGREE-20261020-001B-P001_half_carving_width/proof.md)).

So the four algebraic measures we now have for Tseitin read off graph
layouts:

| Measure | Governing layout | Value |
| --- | --- | --- |
| Nullstellensatz, clause encoding | linear (toggle width) | cutwidth + 1 at degree ≤ 3 |
| Nullstellensatz, ±1, reduced | linear | cutwidth exactly |
| Polynomial calculus, ±1 balanced, reduced | tree (carving) | ⌈cvw/2⌉ or ⌊cvw/2⌋ + 1 |
| Polynomial calculus, clause encoding | tree | max(maxdegree, the above), up to + 1 |

## Why it works

A polynomial calculus derivation from binomial axioms is a closure of signed
relations y_A ≈ ±y_B. Each relation is labelled by the vertex set U whose
cut is A △ B.
- **Upper bound.** A relation can sit at half its cut, and below 2d it can
  move freely. Composing two relations needs a common center for three cuts,
  so a carving of width w gives degree ⌊w/2⌋ + 1.
- **Lower bound.** A tangle of order 2d + 1 keeps every label on its small
  side, so no relation is ever labelled V. The tangle–branch-width duality of
  Robertson and Seymour turns this into ⌈cvw/2⌉.
- **Even width.** At exactly 2d a relation is rigid. That is where the
  remaining ±1 lives.

## Evidence

- **Proof.** `PC-DEGREE-20261020-001B-P001`, in prose. Executable checks
  cover:
  - the closure model, against plain linear algebra;
  - every tangle on small graphs, which also confirms the duality there;
  - explicit carving derivations replayed on 155 graphs, including K₅,₅.
- **Census.** `PC-DEGREE-20261020-001A-E001` is a frozen, confirmatory census
  of 1,253 graphs, including 300 held-out graphs.
  - All five predictions hold.
  - Graphs of even width split 191 at cvw/2 and 628 at cvw/2 + 1.
  - In the standard clause encoding the degree exceeds the maximum degree
    when the graph is wide enough: 6 against 4 on the 4-cube, and 7 against
    5 on K₅,₅.

## Open

- **The exact rule for even carving width.** A vertex of degree cvw does not
  decide it.
- **Tseitin modulo p and other groups.** These need labels that are
  ℤ_p-labellings.
- **Size.** In the ±1 basis these derivations are small: polynomially many
  binomial lines. In the usual 0/1 basis the size–degree relation gives
  nothing below √n, so the size of polynomial calculus proofs of grid
  Tseitin formulas is not settled by this.

## Recommendation

**Research directions**, rated by barrier potential.

| | A. PC size of grid Tseitin, 0/1 basis | B. Sum-of-squares degree of Tseitin | C. Back to the foundations (question 9) |
| --- | --- | --- | --- |
| Interest | 2/3. An exponential bound would beat the size–degree barrier for a natural family. The exact degree theory is the tool. | 1/3. It likely completes the dictionary: the tangle gives a pseudo-expectation whose moment matrix splits into rank-one blocks, so SoS degree ≈ cvw ± 2. A clean result, but a refinement. | 1/3, as before. |
| Execution | First a literature check. Then design a charge-preserving random restriction, setting whole cycles, that kills large monomials. Stop if the bound is known, or if no restriction family keeps the contradiction global. | One short epic: proof plus an exact PSD check on small graphs. | A fresh epic. |

Execution is the owner's decision.
