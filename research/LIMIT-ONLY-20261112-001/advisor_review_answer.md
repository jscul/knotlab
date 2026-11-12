**Verdict:** L1 is correct but is a one-line monotonicity corollary; L2 (⇒) is false in general, and not only because of periodic orbits. This is reasoned from your description alone; I ran nothing.

**(1) L1.** It is correct and is the special case X = G of L2 (⇐), i.e. Park's coinduction principle. Present it as a gate or remark, not a result. Its hypothesis is sufficient only, so don't suggest the converse.

**(2) L2 (⇒).**
- **Equivalent form:** L2's criterion is main(P) ≠ ∅, where P = gfp of X ↦ N ∧ Phi(X) is the largest post-fixed point below the seed N = NAE. Compute P by iteration; this removes the 4096 cap.
- **Abstract counterexample:** on the subsets of {1,2}, let Phi(S) = {2} if S ≠ ∅, else ∅, with N = {1} and main = identity. The orbit is {1}, {2}, {2}, …, alive forever, but P = ∅. No cycle is needed; the orbit only has to leave ↓N.
- **Likely concrete counterexample:** D(a,b,c) = [a=b=c] ∧ SELF(x,y,z) with x, y, z local. The orbit is NAE → {000,111} → {000,111}, yet any X ⊆ NAE with X ⊆ Phi(X) is empty. Forcing port equality from K-calls probably exceeds class E's budget, so a pass on E is weak evidence; W with helper definitions should hit it.
- **"Not all empty" clause:** drop it. It breaks (⇒) when main is alive without using SELF.
- **Where L2 does hold:** when N is comparable with Phi(N). If Phi(N) ⊆ N the orbit descends to P. If N ⊆ Phi(N), X = N works.
- **Exact criterion:** the orbit is eventually periodic, and the family is alive at every depth iff main is non-empty on every element of the tail plus cycle. Decide this by cycle detection, never by a depth cap.

**(3) Prior work.**
- Knaster–Tarski, and Park for coinduction.
- Cousot & Cousot 1979, "Constructive versions of Tarski's fixed point theorems" (iteration from seeds; only pre/post-fixed seeds give chains).
- Kozen's mu-calculus for the lfp/gfp contrast.
- Lengauer & Wanke on hierarchical graph descriptions (bottom-up port tables).
- Courcelle, and Habel–Kreowski–Vogler, on HR grammars and compatible/finite-state properties.
- Schaefer and the co-clone lattice for complement-closed relations.

**(4) Settled by definition.**
- "Alive at every finite depth ⇒ limit alive" (you already flag this).
- L1 and its "all-equal state" corollary.
- Eventual periodicity of the orbit.
- The 0.63% and 58% figures are properties of your sampling distribution, not of the families; report them as such.

**Failure criteria.** The L1 gate is fine. For L2, a counterexample is the expected outcome, so reframe the test as measurements:
- how often N is comparable with Phi(N);
- the L2 failure rate among incomparable cases, split into "fixed point outside ↓N" and "period > 1";
- whether E can express a failure at all.
