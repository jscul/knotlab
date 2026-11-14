**Verdict:** claims 2 and 3 hold with caveats, claim 1 holds but will rarely be usable, and the design has two flaws to fix before freezing. All of this is hand reasoning; I ran nothing, and the citations are from memory.

## What I checked by hand

- **Claim 2 (ruler) holds.** The set {root, 1, 01, …, 0^(s-1)1, 0^s} has s+2 members and is a bond: setting root = 1 = 0 forces address 0 to 1, then alternately down the chain, and the last knot is violated. No member is spare.
- **A bond need not contain a whole knot.** {w, w0, w10, w11} is a bond: w = w0 = 0 and w10 = w11 = 1 force w1 both ways. So "members anywhere" does real work.
- **Claim 3 holds only for joint rigidity.** One state up to complement on the union of levels 0..N makes every pair tied. LEVEL-RETURN's rigidity was per level; rigid levels joined loosely can still have two free relative signs. Re-read the fate on the union.
- **Claim 1 (gap argument) is correct but nearly useless.** For the plain tree the projection onto (level k, level k+2) is already not a product: w00 = w01 = w10 = w11 = a forces w = a. Yet the tree's reach grows linearly. Forgetting is sufficient, not necessary, and a product across 2^k addresses is far more demanding than across 3 ports. Expect the test to fire almost never.

## Design flaws (E)

1. **The root is isolated in most descriptions.** Every word fixes the empty address, so letterless terms all give the root and letter terms give the single letters. The root is in a knot only when a placement has exactly one letterless term and two letter terms with letters 0 and 1. Otherwise there is no bond at all and L is infinite at every s. Use a top at level k0 = 2 or 3, taken over all its addresses, and add an explicit "no bond" outcome.
2. **Truncation is one-sided.** Raising N only adds knots, so a non-full projection stays non-full and L_N(s) is non-increasing in N. Upper bounds ("bounded", "rigid-like") are settled at finite N; "growing" never is. Freeze this as a gate (L at S+3 ≤ L at S+2) and word growth verdicts as "to depth N".
3. **A dead union pattern makes the empty set the bond.** Read satisfiability on the union first and record the death level.
4. **"Some address" is a minimum, driven by one lucky chain.** Report the minimum, the maximum, and the share of level-s addresses bound at each size.
5. **Record each least bond's deepest member minus s.** That overshoot is the direct reading of "parts depend on the whole"; L alone does not show it.

## A. Finite substitute

- **Exponential and polynomial classes: none.** Since g(uv) = g(u)·g|_u(v), knots at addresses in the cone below u land in three different cones g_i(u). The interface is the whole level. The stretch relation is a lift of the level-k knot pattern labelled by sections (finitely many labels, growing pattern), so there is no fixed semigroup. Say plainly that the test does not transfer.
- **Bounded class: probably yes.** Bounded automata have Schreier graphs built by finite inflation rules with finitely many glue points (Bondarenko; Nekrashevych's post-critically finite case). Those glue points are ports, which is the earlier setting. This is a lemma to prove before use; I have not checked that the three-term knots respect the inflation.

## B. Exact method

Use implicates. A set is non-full exactly when some assignment on it is forbidden, that is, a clause supported on it is implied. So bonds are the inclusion-minimal supports of implied clauses.

1. Run an implicit-hitting-set search, the smallest-unsatisfiable-subset method (Ignatiev et al., FORQES). The soft units are "x = 0" and "x = 1", the pattern is hard, and the candidate must contain a top unit and a level-s unit.
2. For each candidate, smallest first:
   - If it is satisfiable, add the correction set and continue.
   - If it is unsatisfiable, test whether each proper subset is full. That is at most m·2^(m-1) assumption calls, about 1,000 at m = 8, halved by complement symmetry.
   - If some subset T' is not full, block every superset of T'. This is sound because no superset of a non-full set is a bond.
3. The first candidate that survives is the exact least bond, with certificates on both sides.

Cheap first pass: width-bounded resolution closure gives upper bounds only, since narrow implied clauses can need wide derivations. Do not use a distance ball without a proved locality lemma; the four-member bond above shows bonds skip members.

## C. Predictions

Freeze numbers only after a pilot on a held-out seed split. What can be frozen now:

- **By construction:** no joining placement gives no bond across levels; tree-only gives s+2; joint rigidity gives 2; an isolated top gives no bond.
- **Theorem gate:** monotonicity in N.
- **Directional:**
  - The rigid-like share and the dead share both rise from bounded to exponential, since more cycles mean more ties and more contradictions.
  - Growth concentrates in the bounded class.
  - Overshoot is positive mostly in the exponential class.
- **Undecided rule:** the pilot decides whether s+2 bounds every finite L. I see no proof.

Report dead, no-bond, rigid-like, bounded and growing-to-N as five separate shares per activity class.

## D. Prior work to check

- **Tree reconstruction:** Mossel; Evans–Kenyon–Peres–Schulman.
- **Point-to-set correlations:** Montanari–Semerjian. At zero temperature this is the nearest probabilistic cousin of the bond reading.
- **Freezing and rigidity in random constraint problems:** Achlioptas–Ricci-Tersenghi; Semerjian; Zdeborová–Krzakala. This includes hypergraph 2-colouring, which is NAE.
- **Logical side:** prime implicates and backbones; shattering (Sauer–Shelah), since a bond is a minimal non-shattered set.
- **Schreier graphs:** D'Angeli–Donno–Matter–Nagnibeda; Bondarenko.

I know of no work on least implicate support as a function of depth on automaton-generated patterns, but treat that as unverified until a search is run.
