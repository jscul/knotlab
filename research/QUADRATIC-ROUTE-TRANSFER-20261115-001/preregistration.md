# Transferring route proof length when proofs can multiply two linear expressions

2026-11-15 (Pacific). Goals G3 and G16.

## The question

Does the literal map of the guarded two-use compiler still transport refutations when multiplication can introduce formal degree-two terms, and is there a strict width-three source lower bound for exactly that system?

## Prior work in the program

`scripts/track.py objects "quadratic polynomial resolution signed substitution literal projection" --until 2026-11-15 --exclude QUADRATIC-ROUTE-TRANSFER-20261115-001 --limit 3`

`scripts/track.py objects "degree two proof size random strict clause width three" --until 2026-11-15 --exclude QUADRATIC-ROUTE-TRANSFER-20261115-001 --limit 3`

`scripts/track.py objects "degree bounded multiplication route proofs" --until 2026-11-15 --exclude QUADRATIC-ROUTE-TRANSFER-20261115-001 --limit 3`

`scripts/track.py objects "affine axiom projection DAG rule transport" --until 2026-11-15 --exclude QUADRATIC-ROUTE-TRANSFER-20261115-001 --limit 3`

- `SIGNED-KNOT-OVERLAP-20261114-001` studied Ternary supports and private four-bit sign observations of fixed guarded clause templates. Check the specific formal polynomial, axiom and node conventions on the same compiler and an actual refutation with a mixed quadratic term.
- `ROUTE-PARITY-TRANSFER-20261115-001` studied Admitted density-eight random strict-CNF parity lower bound with semantic-weakening convention conversion. Check the specific formal polynomial, axiom and node conventions on the same compiler and an actual refutation with a mixed quadratic term.
- `ROUTE-FRONTIER-MEMORY-20261115-001` studied Tight deterministic stage-order memory and exact residual count on one fixed guarded route schedule. Check the specific formal polynomial, axiom and node conventions on the same compiler and an actual refutation with a mixed quadratic term.
- `TRUE-RATE-20261113-001` studied Carried top ports among certified bounded and growing nested rules. Check the specific formal polynomial, axiom and node conventions on the same compiler and an actual refutation with a mixed quadratic term.

The predecessor implements signed literal and constant projection of every guarded compiler axiom. It admits only the degree-one characteristic-two source. It separately gives a polynomial node simulation for the earlier affine semantic weakening convention.

## Prior work outside the program

Shuo Pang, A Degree–Size Relation for Resolution over Polynomials, v2 (2026-10-24), introductory syntactic rules, §7.1 and Theorem 7.2(a), at p=2, r=2, w=3, Δ=8 (https://arxiv.org/html/2610.00837v2). This specialization must be admitted in its own scope. No unrestricted semantic weakening on quadratic lines is supplied.

## Evidence and stopping rule

Substitute in the formal polynomial ring including squares and complemented aliases, track DAG references, axioms and syntactic line size. Stress variable collisions, false constants, source-image tautologies, arbitrary input line width, and a degree-three negative. Instantiate an actual nonlinear proof in the strict guarded system, compare source/target truth and distinct-variable quadratic monomials, and state both size conversions. The inherited degree-one semantic comparison and the degree-two syntactic system must be distinguished.
