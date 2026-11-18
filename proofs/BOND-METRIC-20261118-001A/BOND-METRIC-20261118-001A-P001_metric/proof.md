# Where bond distance is a metric: what is proved

Ticket `BOND-METRIC-20261118-001A`, 18 November 2026. Written before the frozen run; checked by ticket B's gates and census
(`experiments/BOND-METRIC-20261118-001B/BOND-METRIC-20261118-001B-E001_triangles/`). Referee pending. T1's second half, T4 and T5
are the advisor's (claude-fable-5-2), checked here by hand and by the gates; T1's first half, T2 and T3 are the thread's. Refereed:
report R1, confirmed with fixes, no Block (`research/BOND-METRIC-20261118-001/referee-R1/report.md`), folded in on 18 November.

## Terms

As in `FREE-READ-20261118-001A`: a set S of distinctions is **free** when the allowed states take all 2^|S| joint values on it, and
**constrained** otherwise; a **bond** is a constrained set every set of |S| − 1 of whose members is free; **bond distance** b(x, y) is
the size of the least bond holding x and y, minus one, and infinite when no bond holds them. A superset of a constrained set is
constrained (its projection onto the smaller set is the smaller set's), so the free sets are exactly the sets containing no bond,
and the bonds are the minimal constrained sets. b is a **metric** on a base when b(x, z) ≤ b(x, y) + b(y, z) for every three
distinctions, an infinite left side against a finite right side being a failure.

## T1. Where bonds compose like cycles, bond distance is a metric

Suppose the bonds of a base satisfy circuit elimination: for two different bonds C₁, C₂ and a distinction e in both, some bond lies
inside (C₁ ∪ C₂) − e. The bonds form an antichain (each is a minimal constrained set), so they are the circuits of a matroid on the
distinctions, and its independent sets, the sets containing no circuit, are the free sets (`KNOT-CIRCUITS-20261020-001`).

Let x, y lie on a least bond C₁ and y, z on a least bond C₂, x ≠ z. The restriction of the matroid to C₁ ∪ C₂ has as circuits the
bonds inside C₁ ∪ C₂; in it x and y lie on the circuit C₁, and y and z on C₂. In every matroid "equal or on a common circuit" is an
equivalence relation (Whitney; Oxley, *Matroid Theory*, Prop. 4.1.2), so x and z lie on a common circuit C₃ ⊆ C₁ ∪ C₂. Hence

b(x, z) ≤ |C₃| − 1 ≤ |C₁ ∪ C₂| − 1 ≤ |C₁| + |C₂| − 2 = b(x, y) + b(y, z).

The same equivalence shows that b is infinite exactly between different connected parts of the matroid, so no infinite left side
meets a finite right side.

Moreover, if C₁ ≠ C₂ then C₃ ≠ C₁ ∪ C₂, because C₁ ∪ C₂ properly contains the circuit C₁ and circuits form an antichain; so
|C₃| ≤ |C₁| + |C₂| − 2, that is, (b − 1)(x, z) ≤ (b − 1)(x, y) + (b − 1)(y, z). If C₁ = C₂ = C it reads |C| − 2 ≤ 2|C| − 4, true as
|C| ≥ 2. So b − 1 satisfies the triangle inequality too; it is zero between the two members of a bond of two (parallel elements),
so it is a pseudometric. ∎

**Parity bases.** On a base of parity knots (either constant) the allowed states are a coset of a linear code; a set is free exactly
when no nonzero sum of the parity checks has its support inside it, so the bonds are the minimal such supports, the circuits of a
binary matroid, and they satisfy elimination. So b is a metric on every parity base (the FREE-READ referee's argument, here in full).
∎

## T2. Two not-all-equal knots sharing two distinctions

Take the base {a, b, c}, {a, b, d} of not-all-equal knots. Each knot is a bond, so b(c, a) = b(a, d) = 2. A set holding c and d but
not a is free: given any values on it, give a the value opposite to b's, and both knots hold whatever c and d are; likewise without
b. So a bond holding c and d contains a and b, hence the knot {a, b, c}, a constrained proper subset, unless the bond is that knot,
which lacks d. So no bond holds c and d: b(c, d) is infinite and b(c, d) > b(c, a) + b(a, d). ∎

Their correlation is 1/5: the ten allowed states are the eight with a ≠ b (c and d free) and the two with a = b (c = d, opposite to
a). So c and d are tied, through the shared pair, but held by no bond. In the doctrine's words the shared pair is a common hub of
the two knots, and a hub is not one touch between c and d.

The argument uses only that each value of b has one value of a under which both knots leave their third distinction free. So it holds
for any two knots that each forbid a pattern and its complement (not-all-equal and the betweenness forms) when their forbidden
patterns agree, or are complementary, on the shared pair: then a must differ from b in both, or equal it in both. "Not exactly two
ones" (R5) lacks it: with b = 1, no value of a frees the third, and two R5 knots sharing two distinctions keep the bond {a, c, d}
(given a = 1, c = d).

## T3. The clause "not all ones"

On a base of such clauses a set is constrained exactly when it contains a whole clause (set every distinction outside it to 0;
`FREE-READ-20261118-001A`, C), so the bonds are the clauses. If two clauses share a distinction y, with x only in the first and z only in
the second and no clause holding x and z, then b(x, y) = b(y, z) = 2 and b(x, z) is infinite. Two clauses sharing two distinctions
(four distinctions in all) or one (five) already fail. ∎

## T4. R6, "if place 2 is 1, places 0 and 1 agree" (the advisor's bases)

Write R6(s; u, v) for the knot with s in place 2. On R6(a; b, c), R6(d; b, c), a set without b is free (given its values, set b equal
to c; both knots hold), and likewise without c. So a bond holding a and d contains b and c, hence the knot {a, b, c}, which is
constrained (a = 1, b ≠ c is missing): no bond holds a and d, while b(a, b) = b(b, d) = 2. On R6(a; b, c), R6(a; d, e), knots
meeting once on five distinctions, a set without a is free (set a = 0), and a set without c and e is free (set c equal to b and e
equal to d). So a bond holding b and d holds a and one of c, e, hence the knot {a, b, c} or {a, d, e}, a constrained proper subset:
none exists, while b(b, a) = b(a, d) = 2. Switching c in the first base turns both knots into copies of the twisted law "if place 2 is 1, places 0 and
1 differ", with the same bonds. ∎

## T5. R5, "not exactly two ones" (the advisor's base)

R5 allows the patterns of weight 0, 1 and 3, so the allowed states are the sets of ones closed under "two ones of a knot force the
third", and a set S is free exactly when no member of S lies in the closure of the others (each subset A of S is then the trace on S
of A's closure). Take a, b, f₁, g₁, c, f₂, g₂, d with knots {a, b, f₁}, {a, b, g₁}, {f₁, g₁, c}, {a, b, f₂}, {a, b, g₂},
{f₂, g₂, d}.
- {a, f₁, c} is a bond: a and f₁ close to everything (they force b, then g₁, f₂, g₂, c and d), so c lies in the closure of {a, f₁};
  and no member of a pair lies in the closure of the other. Likewise {a, f₂, d}. So b(c, a) = b(a, d) = 2.
- No bond holds c and d. Let S hold c and d with S − c and S − d free, and T = S − {c, d}. If T holds a (or b) and anything else, T
  closes to everything, against S − c free; so T = {a} (or {b}), and {a, c, d} is free (a with c or d closes to nothing new). If T
  avoids a and b, it holds at most one of f₁, g₁ (else c lies in the closure of f₁ and g₁, against S − d free) and at most one of
f₂, g₂ (likewise against S − c free); then the
  closure of any subset of S adds at most g₁ or f₁ (from f₁ with c, say) and g₂ or f₂, none of them in S, so every subset of S is its
  closure's trace and S is free.

So b(c, d) is infinite while b(c, a) + b(a, d) = 4. Switching a, c and d, each lying in exactly one place of each knot that holds it
and every knot holding exactly one of them, turns every knot into a copy of the twisted R5 with the same bonds. Two R5 knots sharing
two distinctions do not fail: given a = 1, c = d, so {a, c, d} is a bond. ∎

*Not the smallest (the referee):* R5 already fails on seven distinctions with six knots, for example {0, 1, 2}, {0, 1, 3}, {0, 1, 4},
{0, 2, 3}, {2, 4, 5}, {3, 4, 6}, where no bond holds 5 and 6 though each is two from every one of 0 to 4 (8,190 of 1,356,250 such
bases fail; none on six distinctions with five to eight knots, or on seven with five).

## The nine languages

The 34 three-place laws passing K1–K3 form nine languages under reordering places and switching every value at once: the operations
that carry a base of copies of one law to a base of copies of another with the same bonds (switching one place is not one of them,
since a distinction may sit in different places of different knots). They are parity, not-all-equal and betweenness, the clause and
the twisted clause (forbid a pattern with two ones), R5 and its twist, R6 and its twist. By T1 to T5:

**Theorem.** Bond distance is a metric on every base built from copies of one three-place law passing K1–K3 exactly when the law is
parity. ∎

This matches `KNOT-CIRCUITS-20261020-001`: a Boolean law composes like cycles exactly when it is affine. Whether "a metric on every
base" and "composes like cycles" coincide for laws of more places or values is open: T1 gives one direction; the other needs a
failing base built from any law whose bonds fail elimination, and R5 shows that small gadgets can reconnect the pair through other
bonds.

## What follows, and what is computed

- Parity: a metric on every base (T1). Not-all-equal and the clause: not a metric, on four distinctions (T2, T3).
- Ticket B's census (frozen): no failure of b or b − 1 on 439,652 parity bases; six languages fail on two knots on four
  distinctions; R5 has no failure on at most seven distinctions and four knots (it fails on seven with six, the referee), but its twist
  fails on four distinctions with three knots (12 of the 108 bases on distinct triples) (P3b missed), through two bonds of two that are one-way ties: {0, 1} forbids both being 1, {0, 3} forbids 0 = 1 with 3 = 0,
  and nothing then ties 1 to 3. One-way ties, unlike parity's equalities, do not compose.
- A failing pair need not be correlated (P6 missed): on the not-all-equal knots {0, 1, 2}, {0, 1, 3}, {0, 4, 5}, {2, 4, 5}, the pair
  3, 4 takes its four joint values equally often, though each is one knot from 0.
- On knot trees of parity, not-all-equal and betweenness knots, b = steps apart + 1, so b is a metric there
  (`FREE-READ-20261118-001A`).
- Open: whether "metric on every base" and "composes like cycles" coincide for every law.
