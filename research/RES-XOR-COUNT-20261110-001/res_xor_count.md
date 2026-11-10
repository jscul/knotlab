# Res(⊕) beyond tree-like on the sphere's count

Epic `RES-XOR-COUNT-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `PC-COUNT-20261110-001` settled tree-like Res(⊕) on the sphere's count (size 2^{Ω(n^{1/4}/log n)}) and left
  regular and dag-like Res(⊕) open, recorded as sub-goal B93. The coordinator selected B93 on 2026-11-10: do its first step with a frozen
  statement of what counts as a transfer, name the step that fails, and move to cutting planes (B82) if it stalls there.
- **The question.** Does a published regular, depth-restricted or dag-like Res(⊕) lower bound reach the count?
- **Frozen first.** `transfer_statement.md` beside this note (commit 2cb5de1ad): a transfer is an F2-affine substitution from a source
  with a published bound, with small Res(⊕) derivations of the substituted clauses (T1), or Braun's Theorem 9.1 verified for the count
  (T2); routes R1 (bit PHP and relatives), R2 (Braun's criterion), R3 (stifled lifting), R4 (the count's xor-lift).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Braun's criterion is capped by degree.** For any system with a polynomial-calculus refutation of degree d ≤ 2v/3, Braun's generic criterion certifies at most exp(d²/(6v)) nodes. The count's degree is at most its resolution width plus 1, O(√n), so on the count the criterion certifies only a constant (R2 stops). | proved | A |
| 2 | **Bit PHP would need a parity reduction.** Carrying Braun's bit-PHP bound to the count needs a reduction from PIGEON to the count with each point one parity. None by ordinary decision trees exists (PPP^dt ⊄ PPADS^dt, Beame et al. 1998), and none by parities is known (R1 stops there). | proved (from Beame et al.) | A |
| 3 | **Lifting enters through non-affine points.** No stifling gadget is affine, so the lifted sources of the Res(⊕) lifting theorems reach the count only through non-affine points (R3 stops); the theorems bound the lifted count instead. The count's xor-lift is the count again (R4 stops). | proved | A |

## Answer

No. Every route stops at its first step: the degree route cannot work for this formula at all, because algebra refutes the count in
degree √n along a tree decomposition of the sphere, and the other routes need a parity-preserving reduction that no known result
supplies. B93 stalls at its first step, so the epic moves to cutting planes (B82), as the coordinator directed.

## Reading

**Interpretation, not a theorem.**
- **Algebra sees the count only up to √n.** The count needs polynomial-calculus degree at least n^{1/4}/log n
  (`PC-COUNT-20261110-001A`) and at most O(√n). Any Res(⊕) method that works through degree needs degree above √(v log v) to say
  anything superpolynomial, so it is closed for the count; only a combinatorial method could bound Res(⊕) here, and Res(⊕) size is at
  most resolution's 2^{O(√n)}.
- **The count as a pigeonhole principle over corner parities.** In the corner agreements, which are F2-linear in the points, each face
  has at least one agreeing corner, each line at most one, and there are two more faces than lines: a graph pigeonhole principle whose
  edges are parities. That places the count beside the unary pigeonhole principles, for which no dag-like Res(⊕) bound is known.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** None: ticket A is a proof, with finite checks.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Lemma 1, the degree cap (1) | v = 20,000 and 100,000 (checked to 5,000) | pass: 805 cases, largest ratios 0.19 and 0.99 to the caps |
| Lemma 3, stifled gadgets are not affine (3) | 5 bits: all 64 affine functions and 20,000 random ones (checked to 4 bits) | pass: none both; Maj_5 2-stifled |
| The degree ceiling (1) | K_3: not refuted at resolution width 4, PC degree 4 (checked on K_2) | pass: width at least 5, degree 4 |

The script is `stress_test.py` beside this note, its output `stress_test.json`; registered before launch as RES-XOR-COUNT-S1, it ran
in 2 seconds.

## Literature and provenance

- **Sources.** Braun, arXiv 2609.23015 (Theorem 9.1, Remarks 9.3 and 9.4, §2's lemma on multiplying a completed line), audited in
  `BPHP-RES-PARITY-AUDIT-20261019-001` and extended in `HOLE-CRITERION-COLOURING-20261019-001B`; Beame, Cook, Edmonds, Impagliazzo and
  Pitassi (*JCSS* 57, 1998); Göös, Hollender, Jain, Maystre, Pires, Robere and Tao (*J. ACM* 2024) for the summary of separations;
  Chattopadhyay, Mande, Sanyal and Sherif (ITCS 2023) for stifling; Alekseev and Itsykson (ECCC TR24-128) and Bhattacharya, Chattopadhyay
  and Dvořák (CCC 2024) for Res(⊕) lifting; Efremenko, Garlík and Itsykson for regular Res(⊕) on bit PHP.
- **Classification.** Lemma 1 is new as far as found, and elementary; Lemmas 2 to 4 are routine; the delta is the obstruction map for
  this formula.
- **Correction made on the way.** `PC-COUNT-20261110-001`'s note and B93's entry had said that no dag-like Res(⊕) bound was known for any
  formula; the program had itself audited Braun's. Corrected in 249df4d87 (`docs/CORRECTIONS.md`, Not a block).

## Workspace assumptions

- **Relied on.** None of the register's entries.
- **Added.** None.
- **Scope.** The octahedral knot sphere's Kasteleyn-signed NAE formula; Res(⊕) and its fragments; Braun's criterion.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with its checks, one stress test, one correction.
- **Administrative.** The frozen statement, this note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`; whether to share `BPHP-MORE-PIGEONS-NOTE-20261019-001` with Braun.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — Res(⊕) beyond tree-like on the count | **Status:** Obstructed | Every route of the frozen statement stops at its first step; the degree route is closed for this formula |
| Local direction — Res(⊕) on the count | Research directions | Only a parity reduction from PIGEON, or a combinatorial method, remains |
| Broader exploration — G3 | Known alternatives | Cutting planes on the count (B82), taken next |
| Long-term goal — G3 Hardness at three places | Obstruction learned | Algebraic hardness of the count stops at degree √n; Res(⊕) beyond tree-like needs a non-algebraic argument |

**Corrections:** one, made on the way (no dag-like Res(⊕) bound "for any formula": Braun's exists; Not a block). **Goals:** a G3
checkpoint (obstruction learned); B93 taken; two sub-goals added. **Assumptions:** none added or changed.

- **What the attempt leaves open.** Any Res(⊕) bound beyond tree-like for the count; whether PIGEON reduces to SINK by parities.
- **The missing bridge to the program's composed topology.** None here; this line asks how hard the sphere's contradiction is.

**Next step:** Research directions — cutting planes (B82) taken next under the coordinator's standing instruction.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Cutting planes on the count (sub-goal B82, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Selected · next |
| 2 | Bit LeftPigeon as Braun's second family (G3) | 3/3 — Barrier | 2/3 — Testable | Compute, on small binary LeftPigeon instances, the polynomial-calculus consequences to degree B and the largest separated subspace of row-linear polynomials, as the audit proposed for other formulas → separated density that grows with size, or none | Alternative · deferred |
| 3 | Does PIGEON reduce to SINK by parities? (G3) | 3/3 — Barrier | 1/3 — Stated | Look for a parity-decision-tree reduction from bit PHP to SINK on small instances, or an F2 invariant that rules it out → a reduction (Braun's bound reaches the count), or the invariant | Alternative · deferred |

1. **Cutting planes.** As in `COUNT-SYSTEMS-20261110-001`.
2. **Bit LeftPigeon.** Payoff 3: a dense separated space for the binary PPADS-complete principle would answer Braun's Remark 9.3 and
   give the first dag-like Res(⊕) bound for a PPADS-complete principle; Lemma 1 does not block it, since its degree is near-linear in
   its holes (`PC-COUNT-20261110-001A`'s pigeonhole route). Concreteness 2: finite linear algebra with the existing solver. It does not
   reach the count, whose embedding costs the degree.
3. **The parity reduction.** Payoff 3: it would carry Braun's bound to the count; Concreteness 1: no method, and ordinary decision trees
   are ruled out.

**Recommendation.** Research directions: B82 is taken next (coordinator, 2026-11-10); directions 2 and 3 are recorded as sub-goals under
the owner's rule for untaken 3/3 directions.
