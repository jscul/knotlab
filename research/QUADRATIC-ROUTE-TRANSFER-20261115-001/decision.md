# When proofs can multiply linear expressions

Allow a proof over Boolean variables to multiply two linear expressions modulo two, keeping total formal degree at most two. A single line can now express, for example, \(xy+z=0\). No disjunction of affine equations has that same truth table. The signed-literal substitution for the raw compiler still preserves the proof rules, since substituting into a polynomial product gives the product of its substituted factors. A guarded contradiction proof with \(S\) nodes gives an original-clause proof with at most \(2S\) nodes, even with repeated use of earlier steps and arbitrary equation lists. For \(m\) strict source clauses on \(n\) variables the more precise cap is \(\min(2S,S+m+n+1)\). [Proof translation](../../proofs/QUADRATIC-ROUTE-TRANSFER-20261115-001A/QUADRATIC-ROUTE-TRANSFER-20261115-001A-P001_quadratic_substitution/proof.md) · [Rule and expressiveness comparison](../../proofs/QUADRATIC-ROUTE-TRANSFER-20261115-001B/QUADRATIC-ROUTE-TRANSFER-20261115-001B-P001_degree_two_source/proof.md)

Pang's v2 preprint proves an exponential lower bound for this very degree-two syntactic system on random strict ternary clauses at density eight. After compilation, with probability tending to one over the source draw, every contradiction proof in that system requires exponentially many nodes in \(r\) on wiring built from the list, and exponentially many in \(r^{1/3}\) on one catalogue fixed for each source width. Both estimates are superpolynomial in the respective route input lengths. Two end-to-end checks used live quadratic deductions on two distinct surviving original variables. We independently checked every source line against every assignment. The source theorem supplies the asymptotic conclusion. [External admission](../../proofs/QUADRATIC-ROUTE-TRANSFER-20261115-001B/QUADRATIC-ROUTE-TRANSFER-20261115-001B-P001_degree_two_source/admission.json) · [Encoding and replays](../../proofs/QUADRATIC-ROUTE-TRANSFER-20261115-001C/QUADRATIC-ROUTE-TRANSFER-20261115-001C-P001_encoded_products/proof.md) · [Primary preprint, Theorem 7.2(a)](https://arxiv.org/html/2610.00837v2#S7)

This result concerns explicit proofs in the named rules. It takes a particular possible shortcut seriously by granting it to every proof. To derive a bound on all SAT algorithms would also require a justified connection from those algorithms to proofs with controlled size, or a different argument that applies to those algorithms directly. Checking an arbitrary semantic implication between quadratic lines is already coNP-complete. Granting such implications freely would define a different model. [Weakening comparison](../../proofs/QUADRATIC-ROUTE-TRANSFER-20261115-001B/QUADRATIC-ROUTE-TRANSFER-20261115-001B-P001_degree_two_source/proof.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — quadratic proof transfer | **Status:** Successful | The signed map preserves the new deduction |
| Local direction — transport explicit proofs | Continue | The source theorem matches the formal rules and input law |
| Broader exploration — lower bounds on SAT decisions | Known alternatives | Other proof rules and decision algorithms can use different shortcuts |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | A second proof model has a superpolynomial output bound |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Test reuse of a newly named product | 2/3 — a different algebraic shortcut | 2/3 — explicit definition chain | Substitute through two product definitions → identify where the degree-two argument stops | Selected · started |
| 2 | Locate a certificate simulation for unrestricted decision algorithms (B181) | 3/3 — all-solver work | 1/3 — no general size bridge | Name an uncovered solver and state its exact simulation obligation → reassess if a size bound is available | Alternative · deferred |

For #1 the first bounded check is decisive for straightforward expansion. A proof that could introduce \(u=xy\) and then \(v=uz\) could keep the written equations quadratic, while expanding both definitions gives \(v=xyz\). Every Boolean polynomial of degree at most two on three bits has an even number of ones in its truth table. Each of its monomials is independent of at least one input. The function \(xyz\) has one. Thus the new name cannot be erased by substituting a degree-two polynomial for \(v\) directly in the original three variables. A source theorem or different simulation for systems with such extension axioms remains to be found. For #2 the potential payoff is a result about decision work. Even the sign and constant map proved here supplies no size bridge from arbitrary decisions. The existing B181 records that missing step.

**Basis:** One local substitution theorem, a version- and parameter-specific external source, and a local route corollary with two checked nonlinear proofs. The finite replays are V1 internal validation. The external preprint supplies the source lower bound and was not independently reproved. The additional outside design advisor was unavailable at its weekly quota.

**Corrections:** None to the earlier degree-one transfer. **Goals:** G3 and G16 gain a stronger proof-model bound and a concrete obstruction to erasing successively defined products within degree two. B181 already records the broader untaken 3/3-payoff direction. **Assumptions:** Characteristic two, formal degree two, syntactic deductions, explicit node count, density eight and both route encodings are stated parameters. The degree-two result has its own source admission. No standing assumption changed.

**Basket:** Taken B183 and the matching earlier ROUTE-PARITY-TRANSFER-20261115-001#2. B181 remains the broader high-payoff missing simulation. SIGNED-KNOT-OVERLAP-20261114-001#1 is the alternative on representation.

## Final report as sent

2026-11-15 17:42:31 UTC

The extra rule survived. A guarded proof that can multiply two linear expressions still gives a proof of the original clauses with at most twice as many steps. Pang's degree-two source bound therefore transfers to the guarded formulas. This limits everything that produces proofs in these rules and leaves algorithms using other methods open.
