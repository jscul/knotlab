# Braun's bound for more pigeons, and bit-colouring through a proper colouring

Status: Proved

Ticket `HOLE-CRITERION-COLOURING-20261019-001B`, 2026-10-19. The Lean file
`MorePigeonsColouring.lean` is checked by `check.py` against Braun's formal
development at commit `8904bf09a5376f48a00d1c25d079bf0c6441502a` of
`https://github.com/kbr-/math-research`:
- `BPHP-RES-PARITY-AUDIT-20261019-001A` replayed that development;
- `BPHP-RES-PARITY-AUDIT-20261019-001B` audited its definitions.

## Standard statement

Resolution over parities, Res(⊕), is as in the audit: linear clauses over F₂,
DAG-like refutations, and size equal to the number of lines. With n = 2^ℓ
holes, the bit pigeonhole principle BPHPₙᵐ has variables b_{it} for
i ∈ [m] and t ∈ [ℓ]. For every two pigeons i < i' and every label
z ∈ {0,1}^ℓ, it has the clause ⋁_t [b_{it} ≠ z_t] ∨ ⋁_t [b_{i't} ≠ z_t].
The bit encoding of n-colouring a graph G = (V, E) has the variables b_{vt}.
For every edge {u, w} and every label z, it has the same clause for u and w.
It is satisfiable exactly when G is n-colourable.

**Theorem 1 (more pigeons).** Let ℓ ≥ 32 and n = 2^ℓ. For every m with
n < m and 8192·m·ℓ²·(2ℓ+5) ≤ n², every refutation of BPHPₙᵐ has more than
exp(n²/(8192·m·ℓ²)) lines.

**Theorem 2 (transfer).** Let f : V → [m] be a proper colouring of G.
Replace each variable b_{vt} by b_{f(v)t}. This maps every refutation of the
bit encoding of n-colouring G, line by line, to a refutation of BPHPₙᵐ with
the same number of lines.

**Corollary 3.** Suppose 2^ℓ < χ(G) and 8192·χ(G)·ℓ²·(2ℓ+5) ≤ 4^ℓ. Then
every refutation of the bit encoding of 2^ℓ-colouring G has more than
exp(4^ℓ/(8192·χ(G)·ℓ²)) lines.

Some instances of Theorem 1, once ℓ is large enough for m to be in the range (ℓ ≥ 32 for m = 2n, ℓ ≥ 66 for m = n^{3/2}):

| Pigeons | Bound |
| --- | --- |
| m = 2n | exp(n/(16384 ℓ²)) |
| m = n^{3/2} | exp(√n/(8192 ℓ²)) |
| m = n + 1 | exp(n²/(8192 (n+1) ℓ²)), the same form as Braun's exp(n/(32768 ℓ²)) |

The bound stays superpolynomial while m = o(n²/log³ n). At ℓ = 32 the range
of m runs from 2^32+1 to about 7.4·2^32. It widens as ℓ grows, to about
n²/(16384 ℓ³).

## Nearest known result

- **Braun (2026), arXiv:2609.23015:** the case m = n+1. His moment
  construction (Section 3) notes that "no hypothesis m ≥ B is required". The
  formal lemmas take the number of pigeons as a parameter. Only the final
  calibration in `BitPHPExponential.lean` fixes m = 2^ℓ+1.
- **Efremenko, Garlík and Itsykson (2025):**
  - regular Res(⊕) lower bounds for BPHPₙⁿ⁺¹;
  - tree-like Res(⊕) size bounds of 2^{Ω(n)} for weak bit-PHP;
  - a DAG-like width bound for weak bit-PHP.
- **Lauria and Nordström (CCC 2017); Conneryd, de Rezende, Nordström, Pang and
  Risse (FOCS 2023):** linear polynomial-calculus degree for colouring in the
  unary encoding.

**Novelty: corollary level.**
- Theorem 1 is Braun's own argument with the number of pigeons kept general
  in the last step.
- Theorem 2 is the standard substitution argument.
- Neither is stated in Braun's preprint. A brief search found no earlier
  DAG-like Res(⊕) size bound for weak bit-PHP, or for bit-colouring beyond
  complete graphs.
- This is not a novelty claim, and no thorough literature review was made.

## Proof

**Theorem 1.** Follow Braun's proof of `bitPHP_exponential` with m in place of
n+1.
1. His transfer lemma turns a refutation with S lines into a degree-(12ℓ+1)
   polynomial-calculus derivation of one over at most M = 3S + C(m,2) blocks.
2. His exclusion lemma rules such a derivation out under these conditions:
   - m·ln(4M) ≤ k²;
   - k ≤ m;
   - 4(k−1) < n;
   - 2k(12ℓ+2) − 1 ≤ n.
3. Only the first two conditions mention m. Take k = ⌊n/(32ℓ)⌋, as Braun
   does.
4. Suppose S ≤ eˣ with x = n²/(8192·m·ℓ²). The hypothesis gives x ≥ 2ℓ+5,
   so eˣ ≥ 32n². It also gives m ≤ n².
5. Then 4M ≤ 12eˣ + 2m² ≤ e^{2x}.
6. So m·ln(4M) ≤ 2mx = n²/(4096 ℓ²) ≤ k², because n ≤ 64ℓk.
7. The exclusion lemma now contradicts the derivation, so S > eˣ.

**Theorem 2.** Map each affine form g over the vertex bits to the form y ↦ g(y∘f̂),
where f̂(v, t) = (f(v), t), and map each clause to its image.
- A clause's image holds at y exactly when the clause holds at y∘f̂.
- An initial clause for an edge {u, w} and a label z maps to the bit-PHP
  clause for the pigeons f(u) and f(w) and the same label. This uses
  f(u) ≠ f(w); the clause is symmetric in the two pigeons.
- Weakening steps and two-premise semantic steps map to the same steps.
- A resolution step maps to a two-premise semantic step, since resolution is
  sound.
- The empty clause maps to the empty clause.

**Witnesses against vacuity.** These are Lean theorems:
- the range of m is nonempty at ℓ = 32 (`range_nonempty`);
- BPHPₙᵐ is unsatisfiable when m > 2^ℓ (`usualBitPHP_unsat_more`);
- the bit-colouring clause set is unsatisfiable when G has no 2^ℓ-colouring
  (`bitColouring_unsat`), and every proper colouring satisfies it
  (`bitColouring_sat`);
- on the complete graph it is exactly BPHP (`complete_graph_is_bitPHP`).

Refutations exist whenever the clause sets are unsatisfiable, since Res(⊕)
contains resolution. That step is argued in prose.

## What is checked

| Check | Result |
| --- | --- |
| Checkout at the pinned commit, no tracked changes, SHA-256 of the 11 files whose declarations the proof uses plus the build pins | pass; the digests agree with the audit's on every shared file |
| No `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by` or `unsafe` in the proof file | pass |
| All eight stated theorems compile and depend only on `propext`, `Classical.choice` and `Quot.sound` | pass |
| Control: constant 8192 lowered to 2048 throughout the proof of Theorem 1 | rejected, first error exactly at the step that calibrates the kernel degree |
| Control: transfer without the properness hypothesis | rejected |
| Control: unsatisfiability with as many pigeons as labels | rejected |
| Control: colouring unsatisfiability without a monochromatic edge | rejected |

## Scope

- **Trust.** The theorems rest on:
  - Braun's formal development, which is kernel-checked and was replayed from
    source by the audit;
  - Lean's kernel, Mathlib at the pinned revision, and the release-candidate
    toolchain `v4.34.0-rc2`.

  This artifact does not admit Braun's theorem as local evidence. Its
  conclusions are Lean theorems, stated relative to that development.
- **Proof system.** The proof system is Braun's. It contains standard DAG-like
  Res(⊕), as audited in `BPHP-RES-PARITY-AUDIT-20261019-001B`, so the bounds
  hold for standard Res(⊕).
- **Not claimed.** Nothing here concerns the unary encoding, polynomial-calculus
  degree, Frege systems, or a contact-first object.
