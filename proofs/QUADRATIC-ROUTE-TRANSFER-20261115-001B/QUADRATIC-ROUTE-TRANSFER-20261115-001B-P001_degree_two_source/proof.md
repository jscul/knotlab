# The strict width-three source for degree-two deductions

Status: Proved

## Standard statement

Fix the field with two elements. From \(n\ge3\) Boolean variables, draw \(8n\) independent clauses with replacement, uniformly among the \(8\binom n3\) signed clauses using three different variables. With probability tending to one the formula is unsatisfiable and every refutation in syntactic \(\operatorname{Res}(\mathrm{PC}_2/\mathbb F_2)\) has at least \(\exp(cn)\) nodes for a fixed \(c>0\). Each node is counted even when several later deductions reuse it.

## Nearest known result

This is precisely Theorem 7.2(a) of Shuo Pang's v2 preprint at \(p=2,r=2,w=3,\Delta=8\). The introduction defines the rules and §7.1 specifies the probability law. The earlier route-source admission was explicitly restricted to \(r=1\). The new admission uses the same external-evidence policy with the exact higher-degree parameters. [Primary theorem](https://arxiv.org/html/2610.00837v2#S7) · [Rules](https://arxiv.org/html/2610.00837v2#S1) · [Admission](admission.json)

**Argument.** Substitute these four constants into the source theorem. Independently, a fixed assignment satisfies a random clause with probability \(7/8\). Thus the probability that a satisfying assignment exists is at most \([2(7/8)^8]^n\). The refutation lower bound comes from Pang. The local admission checks the statement and hypotheses. It does not reproduce Pang's degree–size argument. The identified October 24, 2026 PDF has SHA-256 `9f7eb894da07496b4cba14cbf7a4a109d64e994837fc0478be541cc4aaa57306`. [Versioned PDF](https://arxiv.org/pdf/2610.00837v2)

Lines are disjunctions of equations \(f=0\) for formal polynomials of total degree at most two. The rules are syntactic weakening, contraction, deletion of a nonzero constant equation, forming a linear combination of selected equations in two premises with their side disjuncts, and multiplying a selected polynomial by \(g\) when the displayed product stays within the degree cap. Default axioms are \([0=0]\) and the two-valued disjunction for a variable. An input literal is a degree-one equation. The previous one-premise *affine* semantic proof convention has a polynomial node simulation in the syntactic degree-one fragment. Thus the new system can simulate those earlier proofs at polynomial cost. The new feature is that both factors in a product may now be nonconstant affine polynomials. [Earlier convention bridge](../../ROUTE-PARITY-TRANSFER-20261115-001C/ROUTE-PARITY-TRANSFER-20261115-001C-P001_source_admission/proof.md)

## A genuinely new single line

From \([x=0]\) derive \([xy=0]\) by multiplication. Combining it with \([z=0]\) gives \([xy+z=0]\). The falsifying assignments of any disjunction of affine equations are a simultaneous affine linear system, hence an affine subspace, possibly empty. The falsifiers of \([xy+z=0]\), written in \(x,y,z\) order, contain \(001,011,101\). Their coordinatewise sum \(111\) satisfies the equation. Thus no single affine-disjunction line has this meaning. Allowing the multiplication adds expressiveness to a line. This example by itself gives no proof-length separation.

## Why the syntax of weakening matters

Checking arbitrary semantic weakening on quadratic lines is already coNP-complete, even for the fixed premise \([0=0]\). Given a strict 3-CNF, write \(u,v,w\) for the affine indicators that its three literals are false. For each clause introduce a fresh *input* coordinate \(t\) for this test and equations \(t+uv=0,\ tw=0\). Their joint solutions project exactly to assignments satisfying the CNF. For every polynomial \(p\) on this list form the disjunct \([p+1=0]\). Their disjunction is tautological exactly when the CNF is unsatisfiable. This construction has linear many terms and a falsifying assignment certifies non-tautology in polynomial time. Consequently the cheap test by affine elimination for the old lines does not generalize to arbitrary quadratic implication. This observation supplies no lower bound for the length of proofs in a calculus that grants such implications for free.

The verifier checks the admission against the repository schema. It enumerates all three-variable affine disjunctions, independently checks the new quadratic truth table, and compares the weakening reduction with SAT by enumeration. The asymptotic bound remains a versioned external preprint result. [Replay](check.py) · [Results](checks.json)
