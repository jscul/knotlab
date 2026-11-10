# Bit LeftPigeon as Braun's second family

Epic `SEP-LEFT-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `RES-XOR-COUNT-20261110-001` closed the degree route to Res(⊕) bounds for the knot sphere's count and
  recorded sub-goal B100: the binary left-pigeon principle, PPADS-complete with near-linear polynomial-calculus degree, is not blocked
  by that degree cap. The coordinator moved B100 ahead of cutting planes (B82) on 2026-11-10, asking for a frozen statement of what
  "density that grows" means and the sizes.
- **The question.** Does bit LeftPigeon have a separated space of useful density for Braun's Res(⊕) criterion, as bit PHP does (his
  Remark 9.3 knows no second formula)?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **One statement decides it.** Braun's generic criterion applies to bit LeftPigeon with its own clauses: if its row-linear space over all rows, pigeon and hole, is separated at degree k(12l + 2), every dag-like Res(⊕) refutation has 3S + n(n + 1)(l + 1) ≥ exp(k²/(3n) − 2). Superpolynomial needs that for some k = ω(√(n log n)). | proved (from Braun's theorems) | A |
| 2 | **The pigeon rows transfer, but are too thin.** Substituting g(h) := Σ_x [f_x = h]·x turns LeftPigeon's axioms into bit-PHP collisions, so pigeon-row separation follows from Braun's at l times the degree; but the pigeon rows alone make the criterion's bound fall below 1. The hole rows are needed, and the hole sums Σ_h g_h,j lie in the substitution's kernel. | proved | A |
| 3 | **The hole rows keep pace at small sizes.** On n = 2, 4, 8 holes, bit LeftPigeon's row-linear spaces over all rows stay separated at least as far as bit PHP's (degree 2, 3, at least 4 against none, 2, 4 for k = 1; 3 and at least 4 for k = 2), and the reach grows from n = 4 to 8: density that grows, by the frozen rule. | computed (pre-registered, exact) | B |

## Answer

Probably, but it is not proved. Everything in Braun's argument except one step transfers to bit LeftPigeon, and that step, separating
row-linear polynomials over the hole rows from the polynomial calculus's consequences, holds on every instance small enough to compute,
as far as bit PHP's does. If it holds at degree √n·polylog, bit LeftPigeon needs superpolynomial dag-like Res(⊕) proofs, the first such
bound for a PPADS-complete principle.

## Reading

**Interpretation, not a theorem.**
- **A left inverse costs the prover nothing visible.** The left-pigeon principle is easier than the pigeonhole principle in TFNP (its
  clauses imply bit PHP's), yet at every size read its row-linear spaces survive at least as long and its PC degree is at least bit
  PHP's (3, 4, at least 5 against 1, 3, 5). The extra structure, a hole that names its pigeon, gives the algebra more to keep separate,
  not less.
- **Where the difficulty sits.** Under Braun's decoder a hole-row bit becomes a weighted sum over the pigeons that could sit in that hole.
  Bit PHP's proof isolates products of pigeon sums; LeftPigeon needs the same for hole sums.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** Conclusion 3 is exact on n = 2, 4, 8 holes and degrees up to 4 (LP_8 at degree 5 passes the memory cap). An analysis
  bug in the frozen run.py (degree-2 horizons read from B = 1) is disclosed in `interpretation.md`; the verdict is read from the
  contract's definition on the same readings.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusion 3's readings | BPHP_4 and LP_4 recomputed by an independent pure-Python solver (pcsep.c was cross-checked on at most 8 variables) | pass: every reading agrees |
| The control (3) | bit PHP with 16 holes and 16 pigeons (64 variables, the solver's limit) at B = 2 to 5, inside Braun's range (checked at n = 8); LP_16 has 148 variables, past the solver, so the comparison has no size past n = 8 | pass: L1 and L2 fully separated |
| Lemmas 1 and 3 and Theorem 2 (1, 2) | n = 32 (checked to 16); l = 21 to 24 (checked to 20) | pass: margin 2 |

The script is `stress_test.py` beside this note, its output `stress_test.json`; registered before launch as SEP-LEFT-S1, it ran in
63 seconds. Its first run read the control with 17 pigeons, 68 variables, past the solver's 64-bit masks; that reading was invalid,
not a failure of separation, and the rerun uses 16 pigeons, which Braun's separation also covers.

## Literature and provenance

- **Sources.** Braun, arXiv 2609.23015 (Theorem 9.1, Corollary 9.2, Remark 9.3, the row-linear separation theorem and decoder of §4,
  the lemma on multiplying a completed line in §2), audited in `BPHP-RES-PARITY-AUDIT-20261019-001`; Göös, Hollender, Jain, Maystre,
  Pires, Robere and Tao (*J. ACM* 2024) for LeftPigeon and PPADS^dt.
- **Classification.** Ticket A: new as far as found, elementary given Braun's paper. Ticket B: new as computed numbers.

## Workspace assumptions

- **Relied on.** None of the register's entries.
- **Added.** None.
- **Scope.** The binary left-pigeon principle and bit PHP in Braun's compact encoding; F2 polynomial calculus; Res(⊕) through Braun's
  criterion.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A), one pre-registered computation (B) with its probe solver, one stress test.
- **Administrative.** This note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`; whether to share `BPHP-MORE-PIGEONS-NOTE-20261019-001` with Braun.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — bit LeftPigeon as Braun's second family | **Status:** Partially successful | Reduced to one separation statement, which small instances support |
| Local direction — the hole-row separation | Continue | A defined statement with Braun's machinery to adapt, and evidence for it |
| Broader exploration — G3 | Known alternatives | Cutting planes on the count (B82); the parity reduction from PIGEON (B101) |
| Long-term goal — G3 Hardness at three places | Capability gained | A route to the first dag-like Res(⊕) bound for a PPADS-complete principle, short of the knot sphere |

**Corrections:** none. **Goals:** a G3 checkpoint (capability gained); B100 taken; sub-goal B102 added. **Assumptions:** none added or
changed.

- **What the attempt leaves open.** Row-linear separation over the hole rows at degree beyond the sizes computed.
- **The missing bridge to the program's composed topology.** None here; this line asks about proof systems for PPADS principles.

**Next step:** Continue — prove row-linear separation for bit LeftPigeon's hole rows, starting from Braun's cube argument.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Hole-row separation for bit LeftPigeon (G3) | 3/3 — Barrier | 2/3 — Testable | Adapt Braun's cube argument and matching moments to products of weighted hole sums Σ_x x_j X_x,h in the unary pigeonhole principle; test the needed moment functionals on unary instances with 4 to 8 holes by linear algebra → a separating functional for every hole-row monomial, or a hole-row combination that every moment functional kills | Recommended |
| 2 | Cutting planes on the count (sub-goal B82, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |
| 3 | A parity reduction from PIGEON to SINK (sub-goal B101, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |

1. **Hole-row separation.** Payoff 3: with Theorem 2 it gives the first dag-like Res(⊕) lower bound for a PPADS-complete principle and
   answers Braun's Remark 9.3. Concreteness 2: the statement is exact and the moment test is finite linear algebra; the proof may need
   new chessboard-type homology.
2. **Cutting planes.** As in `COUNT-SYSTEMS-20261110-001`.
3. **The parity reduction.** As in `RES-XOR-COUNT-20261110-001`.

**Recommendation.** Continue with direction 1, recorded as sub-goal B102 under the owner's rule for untaken 3/3 directions, for the
coordinator to confirm.
