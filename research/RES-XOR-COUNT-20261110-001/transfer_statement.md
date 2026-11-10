# What counts as a transfer (frozen before the routes are worked)

Epic `RES-XOR-COUNT-20261110-001`, sub-goal B93, 2026-11-10. Written and committed before any route below was worked out in detail.

## A transfer

A proof, from a published lower bound, that every refutation of NAE(K_k) (the sphere's count, n = 4k² points) in **regular** Res(⊕), in
**depth-restricted** Res(⊕) (any published depth regime), or in **dag-like** Res(⊕) has size n^{ω(1)}, in one of two forms:

- **T1, a reduction.** A source CNF S with such a published bound, and a substitution sending every point variable of the count to an
  F2-affine form in S's variables, such that each substituted clause of the count has a Res(⊕) derivation from S's clauses of size
  poly(|S|), regular or within the depth regime when the source bound is for that fragment. A refutation of the count of size s then
  gives one of S of size s·poly(|S|).
- **T2, a criterion.** A published general sufficient condition, Braun's Theorem 9.1 (arXiv 2609.23015, "Generic criterion"),
  verified for the count with parameters that give n^{ω(1)}.

## Not a transfer

- A bound for a **lifted count**, the count composed with a gadget (recorded separately, as a bound for that formula).
- A width, rank or depth bound without a size bound.
- Tree-like bounds (`PC-COUNT-20261110-001` has them).

## Routes, each to a transfer or to the step that fails

- **R1.** The bit pigeonhole family: Braun's dag-like bound for bit PHP, its extension to more pigeons and bit-colouring
  (`HOLE-CRITERION-COLOURING-20261019-001B`), and Efremenko, Garlík and Itsykson's regular bounds, as sources for T1.
- **R2.** Braun's Theorem 9.1 on the count itself (T2).
- **R3.** Lifted formulas with stifling gadgets (Alekseev and Itsykson; Bhattacharya, Chattopadhyay and Dvořák; Efremenko and
  Itsykson) as sources for T1.
- **R4.** The count's own xor-lift, as a source for T1.

**Stop.** At a transfer, or when every route has its failing step named. If every route stops at its first step, move to cutting planes
(sub-goal B82), as the coordinator directed on 2026-11-10.
