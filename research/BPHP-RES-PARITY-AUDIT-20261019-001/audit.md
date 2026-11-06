# Audit of the claimed exponential bit-PHP lower bound for Res(⊕)

Epic `BPHP-RES-PARITY-AUDIT-20261019-001`, 2026-10-19, run at the repository
owner's request. This is the epic's decision note.

## The claim

Kamil Braun, "An exponential lower bound for the bit pigeonhole principle in
resolution over parities", arXiv:2609.23015v1 (19 September 2026, preprint
revision 2). The claim: every DAG-like Res(⊕) refutation of BPHPₙⁿ⁺¹ with
n = 2^ℓ has more than exp(n/(32768 ℓ²)) lines for ℓ ≥ 32, with no restriction
on depth or regularity. Earlier lower bounds needed tree-like, regular or
depth-restricted refutations.

The paper credits its mathematics and formalization to AI models working
under the author's direction. The author states that he cannot check the
mathematics, that his confidence rests on the Lean formalization, and that the
fidelity of the formal definitions to the standard proof system is not covered
by it.

## What was checked

| Check | Result | Evidence |
| --- | --- | --- |
| Replay of the published procedure at commit `8904bf09`, Lean `v4.34.0-rc2`, Mathlib `67248ba` | The author's cache command fetched nothing, so Mathlib was compiled from source. The project built with warnings as errors, and `verify.py` passed on all 7 declarations the paper cites, each depending only on `propext`, `Classical.choice` and `Quot.sound`. | `BPHP-RES-PARITY-AUDIT-20261019-001A-E001` |
| Fresh kernel replay (`leanchecker --fresh`) | Passed: the aggregate and every imported declaration replayed in a fresh kernel (206 s) | `…001A-E001` |
| Controls on the replay | A `sorry` placed in a probe is reported as `sorryAx`. The main proof with 32768 replaced by 1 is rejected. A supplementary control changes the constant everywhere; the proof then fails only at the inequality that calibrates the bound (line 125), so the constant is load-bearing | `…001A-E001` |
| What the formal statement means | Faithful to the paper's (1.1) and (1.2). The rules contain every standard Res(⊕) rule set (any sound inference from at most two earlier lines), reuse is unrestricted, and size counts every line. | `BPHP-RES-PARITY-AUDIT-20261019-001B-P001` |
| Meaning-changing constructs | None: no `sorry`, custom axiom, kernel-skipping option, notation, macro or metaprogram in the claim sources | `…001B-P001` |
| Vacuity | Not vacuous. The formal clause set is unsatisfiable for every ℓ (Lean), and the formal system refutes ℓ = 1 in 11 lines (Lean); both are rejected when the mathematics is altered | `…001B-P001` |

## Conclusion

No gap was found. The Lean declaration states the paper's Theorem 1.1 for a
proof system that contains standard DAG-like Res(⊕), and the statement is not
vacuous. With the replay, the theorem follows in Lean's kernel from Mathlib at
the pinned revision. As far as a definitional audit and a from-source replay
can establish, the claimed exponential lower bound for unrestricted Res(⊕) is
correct.

What this audit does not cover:
- the prose proof, which was not checked line by line;
- novelty and the literature comparison;
- residual trust in Lean's kernel, Mathlib and the release-candidate
  toolchain.

## What it means for this repository

- **The depth-restricted Res(⊕) line is superseded for bit PHP.** The affine
  erosion programme (`AFFINE-SUBSPACE-EROSION-001`, `AFFINE-EROSION-SHARPNESS-001`)
  was a route to polynomial-depth bounds in the style of ECCC TR26-007. An
  unrestricted bound makes that route moot for this formula. The
  counterexample to TR26-007's Conjecture 1.4 remains a correct and separate
  result.
- **The paper names the next open problem itself.** Its Theorem 9.1 gives a
  Res(⊕) size bound for any clause set with a dense "separated" space of
  low-degree polynomials: a space meeting the low-degree polynomial-calculus
  consequences of the clauses only in zero. Remark 9.3 says no formula other
  than bit PHP is known to have one. The criterion is already formalized.
  Finding a second family would give new Res(⊕) lower bounds through a
  machine-checked pipeline.

## Recommendation

**Continue** in a fresh proof-complexity epic: search for a second formula
family with a separated space of useful density (Theorem 9.1). The cheapest
discriminator is finite linear algebra on small instances: compute the
polynomial-calculus consequences up to degree B and the largest separated
subspace, for candidates such as unary and functional PHP, the ordering
principle, and random 3-CNF. Stop if no candidate shows separated density
that grows with size at small n.

Communicating this audit to the author or posting it publicly is the
owner's decision.
