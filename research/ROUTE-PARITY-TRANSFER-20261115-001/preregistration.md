# Proof length after encoding strict 3-SAT as two-use routes

2026-11-15 (Pacific). Goals G3 and G16.

## The question

Does every parity-resolution refutation of the actual guarded two-use route encoding project to a short refutation of the source, and which quantitative lower bounds result for satisfiability switches chosen by the compiler?

## Prior work in the program

`scripts/track.py objects "two-use guarded strict routes" --until 2026-11-15 --exclude ROUTE-PARITY-TRANSFER-20261115-001 --limit 3`

`scripts/track.py objects "common restriction semantic parity proof" --until 2026-11-15 --exclude ROUTE-PARITY-TRANSFER-20261115-001 --limit 3`

`scripts/track.py objects "random 3-CNF degree size parity proof" --until 2026-11-15 --exclude ROUTE-PARITY-TRANSFER-20261115-001 --limit 3`

`scripts/track.py objects "exponential proof length lower bound transfer" --until 2026-11-15 --exclude ROUTE-PARITY-TRANSFER-20261115-001 --limit 3`

- `ROUTE-FRONTIER-MEMORY-20261115-001` studied Tight deterministic stage-order memory and exact residual count on one fixed guarded route schedule. Compare the exact axiom image, proof rules, and size on the two-use route compiler.
- `TWO-RELAY-PADDING-20261115-001` studied Exact linear regrouping and minimal clause obstructions for two-use pads on disjoint guarded implication paths. Compare the exact axiom image, proof rules, and size on the two-use route compiler.
- `ONE-RELAY-PADDING-20261115-001` studied Linear ordinary SAT and full witness construction with one repeated middle and arbitrary pad reuse. Compare the exact axiom image, proof rules, and size on the two-use route compiler.
- `KNOTS-ALONE-20261111-001` studied Connected two-fold weaves under the uniform parity knot. Compare the exact axiom image, proof rules, and size on the two-use route compiler.
- `LOOP-LOCK-20261112-001` studied Ring lengths that lock one-order stitched harmony copies. Compare the exact axiom image, proof rules, and size on the two-use route compiler.
- `HARMONY-ARITH-20261112-001` studied Periods and surviving offsets of stitched orbit pairs, including mirror pairing. Compare the exact axiom image, proof rules, and size on the two-use route compiler.
- `SIGNED-KNOT-OVERLAP-20261114-001` studied Exponential common-core switch obstructions versus exact decision work and CNF size. Compare the exact axiom image, proof rules, and size on the two-use route compiler.
- `NAE-SURFACE-20261111-001` studied Random regular knot patterns outside the two-fold-weave condition. Compare the exact axiom image, proof rules, and size on the two-use route compiler.
- `CHEAP-COUNT-20261112-001` studied Description length and code mass of the counting descriptions found. Compare the exact axiom image, proof rules, and size on the two-use route compiler.

The two-use compiler fixes the guarded formula and the switch menu. Whole-proof affine substitution is already local for a different majority encoding. The random strict width-three lower bound needs a dedicated admission.

## Prior work outside the program

Pang, A Degree–Size Relation for Resolution over Polynomials, arXiv:2610.00837v2, Theorem 7.2(a) and the discussion of semantic weakening near Corollary 1.3 (https://arxiv.org/html/2610.00837v2). Admit only the necessary degree-one characteristic-two, fixed-width-three and fixed-density specialization through EVIDENCE-001.

## Evidence and stopping rule

Fix each target guard by the compiler. Check literal images of every raw axiom and pin, plus an inactive and a wrong-sign control. Back-translate all types of DAG proof steps, including tautological parents, shared references and weakening; compare checked proof steps and explicit bits. Independently match the source's sampling, quantifiers, weakening and line convention. Keep formal source intake separate. Finish with both sparse and fixed wiring bounds; stop at the named proof system. The separate branch-swap direction is independently authorized.
