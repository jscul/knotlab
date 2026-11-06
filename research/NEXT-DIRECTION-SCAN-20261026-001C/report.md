# Lane C: the Borromean bridge back to the core program

Ticket `NEXT-DIRECTION-SCAN-20261026-001C`, 2026-10-26. A bounded scouting pass (documentation, no theorem activated). The
scouting agent's harness refused to write this file, so the top-level task wrote it from the agent's final report and reran
its scan: `scan_c.py` reproduces `results.json` exactly (timing aside) in a temporary copy, with 0 mismatches in 15.9 s.

## Question

Do the relations behind the twisted-triple-product hardness pass the canonical knot test K1–K3? Does "pairwise versus
three-way" (Gauss sums versus Potts hardness) match "not a knot versus knot"? Which native systems carry free three-way forms
whose pairwise data stays invariant?

## Findings

Labels: **[computed]** by `scan_c.py` or the knotlab CLI; **[proved]** with a short argument; **[literature]** cited.

1. **Controls** [computed]. Through `python3 -B -m knotlab check`: parity x + y + z = 0 is a knot; x = y with z free, and
   c = A ⊕ B with A fixed, are not.
2. **Vector reading**, where each slot vector is one many-valued distinction [computed, proved].
   - Every nonzero trilinear zero set {T(a, b, c) = 0} is a knot: the zero vector meets every line, so forgetting any slot
     frees the rest (K2), and T ≠ 0 constrains the whole (K1).
   - Tested on det = 0 over F₂, F₃ and F₄; tr det = 0 over F₄; e1∧e2∧e3, e123 + e145 and e123 + e456; all 4,432 nonzero forms
     over F₂ in six dimension patterns. This includes the countable bounded-slot form B(a, b)·c = 0 with one-bit c.
   - Not knots: the kernel tie {T(a, b, ·) = 0} and bilinear zero sets (each has a free contact), and the graphs B(a, b) = c
     and det = s.
3. **Bit reading** over F₂ [computed, proved].
   - A trilinear zero set is a knot exactly when the form is σ(a)σ(b)σ(c), the atom on the parities of the three slots.
   - No alternating (Borromean) form passes: det on 9 bits fails K2 and contains 36 six-bit atoms.
   - The bilinear controls (dot product, 2×2 minor, kernel a × b = 0) are not pairwise systems either; they need width 3 and
     contain three-bit atoms.
4. **Group laws** [computed, proved]. Every group's multiplication relation is a Latin knot, including UT₃(F₄) ⋊ C₃ with the
   hard pair (ω, ω, ω²) and without it (ω, ω², 1). So K1–K3 does not see the hard pair.
5. **Verdict on the bridge.** Pairwise versus three-way does **not** match not-a-knot versus knot. Only the number of places
   matches, and no reading tested lets K1–K3 distinguish a hard pair from an easy one.
6. **What does connect** [proved, computed].
   - #Z(T) = q^(d₁+d₂+d₃−1) + (q − 1) q^(d₃−1) N(T) (checked on 21 random forms; a one-line count over c). So the #P-hard
     kernel count N(T) is, up to a known affine map, the number of states the vector-level three-loop knot allows.
   - Summing a three-way phase over one slot leaves the counted pairwise tie: Σ_w (−1)^det(u,v,w) is nonzero on exactly the 22
     pairs with u ∥ v. Existential forgetting frees (K2); summation ties.
7. **The signed reading** [proved; literature].
   - Weight each state by (−1)^(number of violated clauses). A width-k clause becomes a degree-k phase, and the atom becomes
     (−1)^xyz, the CCZ phase.
   - Signed pairwise sums are quadratic Gauss sums, computable in polynomial time (60 random cases). Signed width-three sums
     are #P-hard (Ehrenfeucht–Karpinski; text not fetched, attribution through arXiv:1607.08473).
   - Over F₂, (−1)^T is a signed tripartite monotone width-three system; a Borromean move adds the six signed atoms of a 3 × 3
     determinant. "Three-way" here means three places of a phase.
   - K1–K3 does not certify the signed atom: as a weight it has full support, and written as a relation s = xyz it fails K2.
8. **"Three nontrivial characters" means "no bounded place", not "three places"** [proved, computed]. A trivial-character slot
   is a bounded hub that meets every cubic term; enumerating it leaves Gauss sums (60 cases). A hard pair needs α, β and αβ all
   ≠ 1, impossible over F₂ or F₃, so bits cannot carry it natively.
9. **Is the Borromean move a knot?** [computed; literature] Only in the vector reading, where every nonzero trilinear zero set
   is one. Its exact content is Matveev's theorem: Borromean surgery changes nothing pairwise (H₁ and the linking pairing). A
   native carrier is three bit layers with a type-III signed atom per tetrahedron (Dijkgraaf–Witten, ≅ D₄): 22 =
   |Hom(Z³, D₄)|/8 on T³ and 64 on #³(S¹ × S²), where type-I/II phases give 64 on both. No such carrier exists in dimension
   ≤ 2. The F₂ edge gadget gives N = 2^(2m−n) Z_Potts(G; 8, 3), #P-hard by Jaeger–Vertigan–Welsh.

## Evidence

- `PYTHONPATH=tools python3 -B research/NEXT-DIRECTION-SCAN-20261026-001C/scan_c.py` (16 s, 0 mismatches) writes
  `results.json`, `cli_log.txt` and `relations/*.cnf`.
- Bit-level verdicts replay with `PYTHONPATH=tools python3 -B -m knotlab check --cnf "$(cat …/relations/<name>.cnf)" --loops …
  --contact … --json`; `cli_log.txt` has the 12 exact commands.
- Vector-level verdicts use `mv_check` in `scan_c.py` (knotlab's checker is Boolean only). It has the same definition and agrees
  with `knotlab.check_knot` on all 256 three-bit and 3,000 random four-bit relations.

## Literature

- Matveev's theorem, through Moussard: [arXiv:1412.4627](https://arxiv.org/abs/1412.4627)
- Cai–Lu–Xia, the affine class: [arXiv:1212.2284](https://arxiv.org/abs/1212.2284)
- Ehrenfeucht–Karpinski: [report](https://theory.cs.uni-bonn.de/Zope/csreports/report_1990/paper_8543/abstract.html),
  attributed in [arXiv:1607.08473](https://arxiv.org/abs/1607.08473)
- Quadratic gaps: [arXiv:cs/0111052](https://arxiv.org/abs/cs/0111052)
- Type-III Z₂³ ≅ D₄: [Error Correction Zoo](https://errorcorrectionzoo.org/c/tqd_abelian)
- Jaeger–Vertigan–Welsh: [doi:10.1017/S0305004100068936](https://doi.org/10.1017/S0305004100068936)

## Gaps

- The cases are small, and the uniform claims rest on one-line proofs.
- The D₄ check is cohomological; the Ehrenfeucht–Karpinski text was not fetched.
- Nothing here is new mathematics.

## Cheapest next discriminator (one day at most)

- **Question.** Are native signed-atom networks, where each distinction lies in exactly two terms, countable in polynomial
  time?
- **Method.** Holant([1, 1, 1, −1]) on cubic graphs and parity networks dressed with signed atoms, through the Cai–Guo–Williams
  Holant dichotomy, then exact small counts.
- **Gate.** If polynomial, the native restriction does real work and a signed-knots epic would be justified. If #P-hard or
  already classified, stop.

## Assessment

- **Interest: 1/3 (Exploratory).** The main uncertainty is whether any phase extension of K1–K3 says anything beyond
  Cai–Lu–Xia, Ehrenfeucht–Karpinski and type-III Dijkgraaf–Witten.
- **Recommendation: against** making this the next epic. The K1–K3 bridge is negative, and the positive bridge (in the signed
  reading, emergence equals the count) is classical. Whether phases count as distinctions is the owner's decision; if pursued,
  map both readings, gated by the discriminator above.
