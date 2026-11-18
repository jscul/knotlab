<!-- modelUsage: claude-fable-5-2 -->

**Headline findings**

- T1, T2 and T3 are correct; T1 needs two small caveats.
- P2 is a theorem, for every matroid and not only binary ones (short proof in §4).
- R6 fails on four distinctions with two knots (explicit base in §5).
- R5 fails, but the smallest failure I can build has 8 distinctions and 6 knots; I expect none within 6 and 4, so P3 as frozen will probably score a miss on R5 even though the Consequence is true.
- "Five classes" is the wrong unit for the Consequence: switching values place by place is not a symmetry of base-building. There are 9 languages, and all 8 non-parity ones fail by explicit bases, so the Consequence can be settled by construction.

Everything below is hand derivation; nothing was run.

## 1. T1

Correct, with these notes.

- **Matroid claim.** Constrained is upward closed, so bonds are the minimal non-faces of the complex of free sets and form an antichain. With elimination they satisfy the circuit axioms, and the independent sets (those containing no circuit) are exactly the free sets. This is the standard circuit axiomatisation, so you do not need to cite `KNOT-CIRCUITS` for it.
- **Caveat: satisfiability.** The axiom "∅ is not a circuit" needs the base to have an allowed state. A parity base with mixed constants can be inconsistent; then ∅ is the only bond. P1's enumeration will meet such bases, so state whether they are excluded or pass vacuously.
- **Restriction step.** Circuits of M|(C₁∪C₂) are the circuits of M inside C₁∪C₂, and applying Oxley 4.1.2 to that restriction is legitimate. The bound |C₃| ≤ |C₁∪C₂| ≤ |C₁|+|C₂|−1 follows because y is shared.
- **Parity bases.** The projection of x₀+V onto S is full exactly when no nonzero vector of the row space of the checks is supported in S. So bonds are minimal supports of the row space, which are circuits of a binary matroid.
- **Caveat: degenerate triples.** By the definition, b(x,x) is the least bond through x minus one, which is not 0. Either restrict to three distinct distinctions or set b(x,x)=0. A forced distinction (singleton bond) lies in no other bond and is its own component, which is harmless.

## 2. T2 and T3

No gap in either.

- **T2.** The ten states are right (8 with a≠b, 2 with a=b). The "set a to differ from b" argument is right. The only candidate bond is {a,b,c,d}, which contains the knot. The correlation is E[cd] = 2/10 = 1/5 with zero means by the global flip.
- **T3.** Setting everything outside S to 0 proves "constrained iff contains a whole clause". The two-clauses-sharing-one case fails on five distinctions and meets at most once, which is worth stating since it bears on the meet-at-most-once theme.
- **Scope of T3.** It is for the clause "not all ones" (equivalently "not all zeros"). The mixed-sign clause x∧y→z is a different language; see §5.

## 3. Is "metric on every base" equivalent to "composes like cycles"?

For three-place laws passing K1–K3: yes, by the explicit failures in §5 (every non-affine language fails) together with T1.

For general languages: unclear. The obstacle is specific. A gadget base whose projection onto W imitates a failing relation reproduces the bonds inside W, but bonds running through the auxiliary distinctions can reconnect the pair. R5 shows this: the obvious gadgets (two knots sharing one or two distinctions, the triangle, Pasch) all gain a bond of size 3 or 4 through the long pair. The failure only appears once the gadget is one-way (the "diamond" in §5).

So an elimination failure in a base does not hand you a triangle failure in that base or a nearby one, and I have no uniform construction. I also found no counterexample language: implication, OR and NAND all fail on a path.

Cheapest discriminating computation: for each four-place law whose bonds fail elimination, search bases of at most 3 or 4 knots for a triangle failure and list the laws with none. Those are the only candidates for a counterexample.

## 4. P2 is a theorem

Let C₁ contain x,y and C₂ contain y,z, with x, y, z distinct, in any matroid.

- If C₁ = C₂ = C, then |C| ≤ 2|C|−2 since |C| ≥ 2.
- Otherwise T1 gives a circuit C₃ containing x,z inside C₁∪C₂. C₃ cannot equal C₁∪C₂, because that set properly contains the circuit C₁ and circuits form an antichain. So |C₃| ≤ |C₁∪C₂|−1 ≤ |C₁|+|C₂|−2. ∎

The constant is tight: two triangles sharing an edge give a 4-cycle. Note that b−1 is 0 between parallel elements, so it is a pseudometric, not a metric. Move P2 into T1 and keep the check as a gate.

## 5. R6, R5 and the class count

**R6 fails on four distinctions, two knots.** Write R6(s; u,v) for "s=1 ⇒ u=v", matching your allowed list. Your wording says the third place is the switch, but the list (forbidden 101, 110) makes the first place the switch; fix one.

- Base: R6(a; b,c), R6(d; b,c).
- Any set without b is free (set b:=c); likewise without c.
- So a bond holding a and d contains b and c, hence the knot {a,b,c}. No bond holds a and d, while b(a,b)=b(b,d)=2.
- A second failure meets at most once: R6(a; b,c), R6(a; d,e) on five distinctions. Sets without a are free (a:=0) and {a,b,d} is free, so b(b,d)=∞.

**R5 fails on 8 distinctions, 6 knots.** R5 is Horn: allowed states are the sets of ones closed under "two ones in a knot force the third". A set is free exactly when no member lies in the closure of the others.

- Knots: {a,b,f₁}, {a,b,g₁}, {f₁,g₁,c}, {a,b,f₂}, {a,b,g₂}, {f₂,g₂,d}. There are 34 allowed states.
- {a,c,f₁} is a bond: a=f₁=1 forces everything, so (1,1,0) is missing, and pairs are free. Likewise {a,d,f₂}. So b(c,a)=b(a,d)=2.
- No bond holds c and d. Let S contain c,d with S−c and S−d free, and T = S−{c,d}.
  - If T contains a or b, it is that singleton (anything more generates everything), and {a,c,d} is free.
  - Otherwise T ⊆ {f₁,g₁,f₂,g₂} with at most one of each pair (else c or d is forced). Then every subset of S is the trace of its own closure, so S is free.
- Hence ∞ > 2+2. Use this as a planted gate.

**Why I expect no R5 failure within 6 and 4.** A single R5 knot is two-way (any two force the third), so short bonds keep appearing. I checked by hand two knots sharing one or two distinctions, the triangle, Pasch, and several 5–7 distinction candidates; all are metric. The one-way implication needs the three-knot diamond. This is an expectation, not a proof.

**The class count.** Base-building permits reordering places and, by isomorphism, a global value switch. It does not permit switching one place. Under the permitted symmetries the 34 laws form 9 languages: parity 1, and two each for not-all-equal, the clause, R5 and R6. The twisted ones all fail by flipping individual distinctions in the bases above:

| Language | Failing base |
| --- | --- |
| Twisted not-all-equal | T2's base with c, d in the twisted place |
| Clause x∧y→z | (a,b,c), (a,b,d): sets without a are free (a:=0) |
| R6 with "s=1 ⇒ u≠v" | Same two-knot base, setting b:=¬c |
| Twisted R5 | The 8-distinction base with a, c, d in the twisted place (each knot contains exactly one of them) |

So all 32 non-parity laws fail, and the Consequence holds independently of P3's range.

## 6. P4 and P5: why 7 passes and 8 fails

I have no structural reason, and I did not recheck your 8-distinction example by hand. The one thing visible in it is that distinction 4 is pendant (only in (0,4,6)) on a four-knot cyclic core occupying the other seven points. Seven points leave no room for that core plus a pendant, but failures need not have this shape. Treat P4 as empirical. P5's boundary (four knots pass, five fail) is the sharper claim and has only exploration behind it.

## 7. P6

Plausible, but it is a claim of no exact cancellation, not a theorem. For not-all-equal, the only value-switch symmetry is the global flip, so no symmetry forces a zero. Across a cut distinction, correlations multiply, so tree-like routes never give zero. An exact zero would need positive and negative routes to cancel; I tried pendant gadgets with transfer weights (3ᵏ±1)/2 and could not balance them. So there is no easy counterexample, but nothing rules one out on the tori. Score it with exact integer counts (states with the pair equal versus unequal), not floats.

## 8. Literature

I know of no result on the triangle inequality or on transitivity of "lie in a common minimal non-shattered set" for general set families, and no name for this distance. The nearest work I can point to, from memory, so verify before citing:

- **Shattering-extremal (lopsided, ample) families:** Lawrence; Bandelt–Chepoi–Dress–Koolen; Anstee–Rónyai–Sali; Mészáros–Rónyai. Minimal non-shattered sets appear there through standard monomials.
- **Independence systems and clutters:** minimal non-faces are circuits of a matroid exactly under elimination.
- **Closure systems and antimatroids:** circuits and rooted circuits in Korte–Lovász–Schrader, and Dietrich's survey. This is the right home for R5 and the Horn clauses.

## 9. Changes before the freeze

1. **P3:** move R6 to "smallest failing base is two knots on four distinctions". For R5, predict no failure within 6 and 4 but failure by 8 and 6, with the base above as an exhibit, or record R5's smallest failure without prediction.
2. **Consequence:** state it over the 9 languages (34 laws) and add the four twisted exhibits to the gates.
3. **P2:** promote to a theorem for all matroids.
4. **Conventions:** fix triples to distinct distinctions (or b(x,x)=0) and say how inconsistent parity bases are handled.
5. **R6:** make the description and the allowed list agree.
6. **P6:** exact arithmetic, and add the R6 and R5 exhibits' long pairs to the record.
