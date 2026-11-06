# Definitional fidelity of the formal bit-PHP lower bound

Status: Proved

Ticket `BPHP-RES-PARITY-AUDIT-20261019-001B`, 2026-10-19. This is an
independent audit of the formal statement behind Braun's preprint "An
exponential lower bound for the bit pigeonhole principle in resolution over
parities" (arXiv:2609.23015v1, preprint revision 2). It covers the Lean
declaration `MathResearch.bitPHP_exponential` at commit
`8904bf09a5376f48a00d1c25d079bf0c6441502a` of
`https://github.com/kbr-/math-research`. The author states that the fidelity of
the formal definitions to the standard proof system is not covered by his
formalization. This audit addresses exactly that gap. Ticket A replays the
formal proof itself.

## Standard statement

Resolution over parities, Res(⊕), works with linear clauses: disjunctions of
affine equations over F₂. A refutation is a sequence of linear clauses ending
in the empty clause. Each line is an initial clause or follows from earlier
lines by an inference rule, and earlier lines may be reused. Its size is the
number of lines.

The bit pigeonhole principle BPHPₙⁿ⁺¹ with n = 2^ℓ uses variables b_{it} for
i ∈ [n+1] and t ∈ [ℓ]. For every two pigeons i < i' and every label
z ∈ {0,1}^ℓ, it has the clause ⋁_t [b_{it} ≠ z_t] ∨ ⋁_t [b_{i't} ≠ z_t].

The audit establishes:
- **(i)** The declaration `MathResearch.bitPHP_exponential` states, for every
  ℓ ≥ 32, that every refutation of the BPHPₙⁿ⁺¹ clause set has more than
  exp(n/(32768 ℓ²)) lines. It does so in a proof system whose rules include
  complementary-parity resolution on any affine form, semantic weakening, and
  every sound inference from at most two earlier lines.
- **(ii)** Every standard rule set for DAG-like Res(⊕) consists of sound rules
  with at most two premises over linear clauses. So the formal theorem implies
  the same bound for each of them, with the same size measure.
- **(iii)** The formal clause set is unsatisfiable for every ℓ, and the formal
  proof system refutes the instance ℓ = 1, so the theorem is not vacuous for
  lack of refutations.

## Nearest known result

- **The claim itself:** Braun (2026), arXiv:2609.23015. Prior lower bounds for
  Res(⊕) were for tree-like refutations (Itsykson and Sokolov 2014, 2020),
  regular ones (Efremenko, Garlík and Itsykson 2025), and bounded or
  nearly quadratic depth (Bhattacharya and Chattopadhyay 2025; Byramji and
  Impagliazzo 2025; Bhattacharya, Byramji, Chattopadhyay and Impagliazzo
  2026; Alekseev and Gaevoy 2026).
- **The proof system:** Itsykson and Sokolov, "Resolution over linear
  equations modulo two", Annals of Pure and Applied Logic 171 (2020); Raz
  and Tzameret (2008) for the integer version.

Novelty: `known-overlap-found`. The theorem is Braun's. This artifact adds an
independent check of what the formal statement means, plus witnesses against
vacuity.

## What the formal objects are

Each row cites the pinned source file and its SHA-256 recorded in
`manifest.json`.

| Formal object | Definition at the pinned commit | Standard meaning | Verdict |
| --- | --- | --- | --- |
| Linear clause | `ParityClause V := Finset (V →ᵃ[ZMod 2] ZMod 2)` with `V = BitVar m ℓ → ZMod 2` (`BinaryAffineZeroCover.lean`, `AffineClauseRegistry.lean`) | a finite set of affine forms over F₂ in the m·ℓ variables | faithful |
| Truth of a clause | `clauseHolds C x := ∃ g ∈ C, g x = 1` | a disjunction of equations, each written through its true-indicator, as in the paper's Section 2.1 | faithful |
| Entailment | `clauseEntails C D := ∀ x, clauseHolds C x → clauseHolds D x` | semantic consequence | faithful |
| Complementary form | `oppositeParity u := 1 − u` (`BinarySemanticAffineCover.lean`) | the equation with the other parity | faithful |
| Steps | `AffineDAGStep` (`AffineDAGRegistry.lean`), exactly four constructors: `initial` (the line is an initial clause); `weaken` (semantic consequence of one earlier line); `resolve` (from earlier lines `{u} ∪ A` and `{1 − u} ∪ B` with any affine `u`, derive `A ∪ B`); `binary` (any line implied by two earlier lines) | rules (1.2) of the paper, plus the paper's stronger two-premise convention | faithful, and stronger |
| Refutation and size | `C : Fin S → FiniteParityClause`, `AffineDAG I C` (a step for every line), and some `finish` with `C finish = ∅`; premises are any earlier indices, with no reuse restriction; size is `S`, every line counted | DAG-like refutation; size is the number of nodes, initial ones included | faithful |
| Variables and labels | `BitVar m ℓ := Fin m × Fin ℓ`; `BitLabel ℓ := Fin ℓ → ZMod 2`, all 2^ℓ labels (`BitPHPInitialBridge.lean`, `CompactBitDecoder.lean`) | b_{it}; labels in {0,1}^ℓ | faithful |
| Literal | `labelBitLiteral i z t = x(i,t) + z_t`, which is 1 exactly when x(i,t) ≠ z_t | [b_{it} ≠ z_t] | faithful |
| Initial clauses | `usualBitPHPInitials m ℓ := {usualCNFClause i i' z ∣ i < i', z}`, where `usualCNFClause i i' z` collects the literals of pigeon i and of pigeon i' for label z (`BitPHPClauseTransfer.lean`) | the clauses of (1.1) | faithful |
| Statement | `∀ ℓ ≥ 32, ∀ S C (dag : AffineDAG (usualBitPHPInitials (2^ℓ+1) ℓ) C) finish, C finish = ∅ → exp(2^ℓ/(32768 ℓ²)) < S` (`BitPHPExponential.lean`) | Theorem 1.1 with n+1 = 2^ℓ+1 pigeons | faithful |

Meaning-changing constructs were also checked. The `claims` and
`third-party-claims` sources contain:
- no `set_option` other than resource limits, and nothing that skips kernel
  checking;
- no `notation`, `macro`, `syntax` or `elab`, and no metaprogramming beyond
  importing the `omega` tactic;
- no `axiom`, `sorry`, `admit`, `native_decide`, `unsafe`, `extern` or
  `implemented_by`;
- one ordinary instance (`rowLinearSpace_finite`).

## Why a stronger system is harmless

A lower bound for a system that has more rules is a lower bound for every
system with fewer rules. Every standard Res(⊕) rule is a sound inference over
linear clauses from at most two premises: resolution, weakening, and the
simplification that deletes a false equation. Each such rule is an instance of
`weaken` or `binary`. So any standard refutation, written line by line, is an
`AffineDAG` refutation of the same size. Whether size counts initial lines
changes the bound by at most the number of initial clauses, which is
polynomial in n. That is far below exp(n/(32768 ℓ²)) for every ℓ ≥ 32.

## Why the theorem is not vacuous

If no refutation existed, "every refutation is long" would hold trivially.
Two witnesses rule this out (`AuditWitnesses.lean`):
- `usualBitPHP_unsat`: for every ℓ and every assignment, some initial clause
  is false. Map each pigeon to its row of bits. There are 2^ℓ + 1 pigeons and
  2^ℓ labels, so two pigeons share a label z, and their clause for z is false.
- `smallest_instance_refuted`: an explicit 11-line refutation for ℓ = 1, with
  three pigeons and two holes. Two-premise steps turn each pair's two clauses
  into "these two differ". "0 ≠ 1" and "0 ≠ 2" give "1 = 2", and resolution
  with "1 ≠ 2" gives the empty clause. It uses `initial`, `binary` and
  `resolve`.

Together with the completeness of resolution, which Res(⊕) contains with
variable pivots, these show that refutations exist for every ℓ. The
completeness step is argued in prose.

## Scope

- This audit checks what the formal statement means. Ticket A checks that its
  proof replays. Neither checks the prose proof line by line or assesses
  novelty.
- Trust rests on Lean's kernel, Mathlib at the pinned revision, and the
  release-candidate toolchain `v4.34.0-rc2`.
