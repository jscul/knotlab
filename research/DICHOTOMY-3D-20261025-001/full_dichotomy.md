# Toward the full dichotomy for counting in three dimensions

Epic `DICHOTOMY-3D-20261025-001`, closed 2026-10-25.

## The question

The owner approved the recommendation made at the close of `HARD-3D-20261025-001`:
- **First.** Separate the collision of growth rates that left the dihedral group of order 16 open (256 · 16 = 64²).
- **Then.** Ask whether counting homomorphisms from closed 3-manifold groups is #P-hard for every finite non-abelian group.

**Intuitions this epic targets.**
- The complexity side: is the abelian/non-abelian line the line of hardness in three dimensions?
- Patterns of patterns: group laws as the patterns that survive the moves.

**The evidence:**
- [Root fillings separate the order-16 collision](../../proofs/DICHOTOMY-3D-20261025-001A/DICHOTOMY-3D-20261025-001A-P001_root_fillings_separate_the_order_16_collision/proof.md)
  (A, proof);
- [bounded scan](scan.md), which found the question already answered;
- **scoping (scratch, not evidence):**
  - sector identities;
  - extraction by faces of growth-rate polytopes;
  - a sector map over 39 non-abelian groups and 8 abelian controls.

## Outcome in one paragraph

**The second gadget works, but the full dichotomy was already a theorem.**
- **The gadget.** Dehn-fill a parallel copy of each edge curve by a square root (slope λμ⁻²) and another by its mirror. This multiplies
  each anyon channel by |Σ_{τ² = λ} ψ(τ)|²/ψ(1)², which kills every reflection channel of the order-16 dihedral group, since no
  reflection is a square.
- **The coefficient.** Interpolating in the number of fins then recovers 4^m·8·P(G, 4)/2^|V|.
- **The general theorem.** Ticket A proves this as one case of an index-p theorem. It covers:
  - every group with an abelian normal subgroup of prime index, except one 2-group case;
  - every 2-power dihedral, semidihedral and generalized quaternion group.
- **The literature.** The bounded scan then found César Galindo's
  [*A Complexity Dichotomy for Quantum Invariants of 3-Manifolds*](https://arxiv.org/abs/2605.06984) (arXiv, May 2026, revised June
  2026).
  - Its Turaev–Viro dichotomy, applied to Vec_Γ, makes |Hom(π₁(M), Γ)| #P-hard for every non-abelian Γ and polynomial for abelian Γ.
  - So the full dichotomy, including S₃ and the order-16 dihedral group, predates both this epic and `HARD-3D-20261025-001`.
- **What remains ours** is an elementary, explicit route: planar chromatic polynomials hidden in explicit closed manifolds.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Survey of growth-rate classes with fins and root filters, 27 groups | Every group has a chromatic class with q ≥ 3; the order-16 dihedral group needs square roots (q = 4) | Scratch |
| Consistency of mirror labels | Equal to per-edge commutation, which makes the counts tensor networks | Proved (A, Lemma 1.2) |
| Index-p analysis | Root fillings work when the group acts nontrivially on pA; two trivial-action cases work with fins alone | Proved (A) |
| Five chromatic sector families; extraction by faces | Every non-abelian group surveyed (orders 6–48) has an extractable sector; no abelian control does | Scratch |
| Extraspecial groups | p odd: the top-dimension class is "charge nontrivial on the centre", q = p. p = 2: square roots isolate the abelian anyons with nontrivial charge, q = 16 | Scratch |
| Bounded literature scan | Galindo (2026) already implies the full dichotomy | Recorded |

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1(a) | If A ◁ Γ is abelian of prime index p and Γ acts nontrivially on pA, the top coefficient is \|A[p]\|^{2m}\|Γ:pA\|\|A[p]\|(\|L′\|/\|A\|)ⁿ P(G, \|[pA, σ]\|²). |
| A, Theorem 1(b1) | Trivial action on pA and \|[A, σ]\| = p: every non-abelian anyon has dimension p, and fins alone give (\|Z\|/\|Γ′\|)ⁿ P(G, \|Γ:Z\|\|Γ′\|). |
| A, Theorem 1(b2) | Trivial action on pA, \|[A, σ]\| ≥ p², p ≥ 3: the fluxes outside A give \|A\|ⁿ P(G, p). |
| A, Corollary 2 | #P-hardness by an elementary route for these groups. This includes the order-16 dihedral group, every 2-power dihedral, semidihedral and generalized quaternion group, every non-abelian group of order p³, A₄, the dicyclic groups and Z_ℓ ⋊ Z_p. The hardness itself is not new: it follows from Galindo (2026). |

## What this changes

- **For the complexity side of the thesis.**
  - The three-dimensional line is exactly abelian/non-abelian, for every finite group, once homology may grow.
  - This is the program's affine/non-affine line, in the form "pointed versus non-pointed Drinfeld centre".
  - The confirmation is external (Galindo), not ours.
- **For `HARD-3D-20261025-001`.**
  - Its identities and constructions stand.
  - Its claims to settle a named open case (S₃) and to show the bounded-H² hypothesis necessary were already implied by Galindo's
    May 2026 preprint.
  - Its novelty labels should read "independent elementary route", not "frontier change". That epic is closed, so its records are
    not edited here. Annotating its discovery record is left to the owner.
- **A relational reading.**
  - Each recoverable sector pairs a flux colouring with a charge colouring: the double still "counts pairs of colourings".
  - The non-abelian structure matters only through which sectors the gadgets can isolate.
  - Abelian groups have the same sector identities, but no gadget can isolate them. That is why abelian counting stays easy.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| S₃ and the order-16 dihedral group were open for closed 3-manifolds in late 2026 | `HARD-3D-20261025-001` scan and closure | **False.** Settled by Galindo's Turaev–Viro dichotomy in May 2026. The scan missed it. |
| Fins alone cannot reach the order-16 dihedral group, so a new kind of instance is needed | `HARD-3D-20261025-001`, Section 5 | **Partly false.** The same doubles work once parallel copies are Dehn-filled by square roots. |
| A literature scan of the named open problem suffices | Practice in recent epics | **False here.** The decisive result was phrased for quantum invariants and fusion categories, not for homomorphism counts. Future scans should search the TQFT phrasing too. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Root-filling gadget; index-p coefficients | Anyon channels of the doubles (`HARD-3D-20261025-001B`) plus Clifford theory | `candidate-local-delta`; folklore risk medium |
| Hardness for these groups | A | Not new: implied by Galindo (2026) |
| Sector families and sector map | Scratch | Not recorded as evidence. A natural companion to Galindo's matrix S_ij/(d_i d_j); folklore risk medium |

**Did the perspective do real work?**
- **What it supplied.** The question and the tools: counting laws, sectors and colourings.
- **What it did not do.** It did not find anything the field lacked. The full dichotomy was proved first by a more general method.
- **What is lasting.** The explicit colouring content of the counts, and the lesson that scans must search TQFT phrasings.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the full dichotomy | **Status:** Partially successful | The order-16 collision was separated and the index-p theorem proved (A). The full dichotomy was already a theorem (Galindo 2026). |
| Local direction: hardness through doubles of fin handlebodies | Retire: practically exhausted | Every hardness conclusion it can reach is implied by Galindo. More sectors would only add explicit identities. Retained: the gadget and the identities. |
| Broader exploration: complexity of counting in three dimensions | Known alternatives | Settled with growing homology. Open: bounded first homology, approximate counting for non-simple groups, and parsimony. |
| Long-term goal: the complexity side of the thesis | Capability confirmed, not created | Abelian/non-abelian is pointed/non-pointed is affine/non-affine, in three dimensions; the proof is external. |
| Next recommendation: bounded first homology | **Next step:** Full pivot, from hardness with growing homology to hardness with bounded first homology | First discriminator: is counting maps into S₄, of derived length 3, #P-hard on closed 3-manifolds whose H₁ has bounded order, while every metabelian target is polynomial there? |
| Interest: that recommendation | **2/3: Promising** | See below. |
| Execution | Deferred to the owner | Bound: one epic. Stop if a polynomial algorithm for S₄ on bounded H₁ appears, or if no instance family with bounded H₁ encodes a hard sum. |

**Why 2/3.**
- **The evidence.**
  - Metabelian targets reduce to a bounded number of twisted-cohomology computations, in the spirit of Matei and Suciu, so they are
    polynomial.
  - S₄ requires summing over exponentially many maps into S₃. That is the first place hardness can live.
  - A bounded search found no prior result. Kuperberg and Samperton cover only simple groups on homology spheres.
- **The uncertainty.** Building bounded-H₁ instances with controlled twisted homology may be hard. Deeper obstruction theory may also
  make S₄ polynomial.

**Alternatives:**
- **Return to the program's core intuitions (1/3).** For example, 2-clauses against 3-clauses for emergence. The three-dimensional
  chain has now run three epics, and its newest question was answered externally.
- **Approximate counting for solvable targets (1/3).** Kuperberg and Samperton's hardness of approximation uses simple groups.
- **Result conversion (1/3).** A short companion note to Galindo with the explicit colouring identities. It is low priority, since the
  hardness is known.
