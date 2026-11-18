# The cube at every doubling

Status: Proved

Ticket `CUBE-DOUBLING-20261118-001A`, 18 November 2026, by Claude. Epic `CUBE-DOUBLING-20261118-001`. This proves
`STATE-RULES-20261117-001A`'s conjecture S6. Ticket B's frozen check verifies every certificate below for s = 2 to 7, and the
exact distribution to n = 20.

## Words

- **Base and moves.** As in A99:
  - a base of betweenness knots B(x, y, z) (y between x and z) is complement-closed, and its non-constant states up to flipping are
    its splits;
  - a step adds a distinction p with one to three knots, each on p and two old distinctions;
  - every old state extends, and p is constrained and not a copy.
- **The cheapest rule.** It takes an extension with the fewest states N′. Ties may be broken in any way; the theorem holds for every
  tie rule.
- **Orientations.** Fix a side of each of the s splits. A distinction's orientation is the vector in {0, 1}^s saying which side of
  each split it lies on.
  - Two distinctions are copies exactly when their orientations are equal (the constants agree on both).
  - An orientation is occupied when some distinction has it.
- **The cube Q_s.** The base whose 2^s distinctions occupy every orientation of s splits: the cut system of the product of s
  two-point lines, with 2s + 2 states.
- **The differing set.** For a target orientation o and a distinction x, A(x) is the set of splits on which x's orientation
  differs from o.

## Lemmas

**L1. Zero-cost steps are fills of unoccupied orientations.** A step with N′ = N forces p on every old state, so p has an
orientation o and is the base's new point at o. It is admitted exactly when o is unoccupied. Such a step adds no split. Every old
distinction keeps its orientation, and every later point's orientation is read against the same s splits.

**L2. When three knots force an orientation.** A knot set forces p to o, every old state kept, exactly when:
- every knot is consistent with o;
- the knots together cover every split and the constants;
- at least one knot is a middle knot, since only middle knots cover the constants.

For a single knot:
- **Middle knot B(u, p, v).** It forces p to u's side on every split not separating u and v, and on the constants. It is consistent
  with o iff A(u) ∩ A(v) = ∅, and then it covers the constants and every split outside A(u) ∪ A(v).
- **End knot B(u, v, p).** It forces p to v's side on every split separating u and v. It is consistent iff A(v) ⊆ A(u), and then it
  covers A(u) \ A(v).

*Proof.*
- The forcing rules are `STATE-RULES-20261117-001A`, S1.
- A knot inconsistent with o forbids o on some state, and since p's only value there is o, the state dies. So inconsistent knots are
  out.
- A split left uncovered leaves p free there, so the step is not zero-cost.
- Covering a split forces p's value on both of its states, a complementary pair, so the split cannot double. A middle knot whose u
  and v differ on a split does not block its doubling, which is why uncovered splits are free.
- For the middle knot, on a split not separating u and v, u and v agree. They differ from o there either both or neither, so
  consistency is A(u) ∩ A(v) = ∅, and the uncovered splits are those separating them, A(u) Δ A(v) = A(u) ∪ A(v).
- For the end knot, on the splits A(u) Δ A(v) it forces v's side, which agrees with o iff those splits miss A(v), that is
  A(v) ⊆ A(u). ∎

**L3. Certificates survive fills.** If three knots on old distinctions force o, they still force it after any number of zero-cost
steps fill other orientations. By L1 the splits and the orientations of those distinctions do not change. ∎

**L4. The cheapest steps from Q_s.**
- No step from Q_s costs nothing: every orientation is occupied, so a zero-cost step would be a copy (L1).
- The steps with N′ = N + 2 are exactly the s·2^(s−1) **subdivisions** and the 2^s **pendants**:
  - a subdivision puts p between the two points of a cube pair differing on one split, by one knot B(u, p, v);
  - a pendant copies a point v and adds the trivial split {p}, by one knot B(v̄, v, p), where v̄ is v's opposite point.

*Proof.*
- A99 keeps every old state and adds no state that is not an old state with a value of p, so the new base restricted to the old
  distinctions is exactly the old base. Hence N′ − N counts the old states that allow both values of p.
- Those come in complementary pairs, so N′ − N is even, and N′ = N + 2 means exactly one pair allows both.
- **The pair is a split's two states.** That split doubles, and p's side on every other split is forced. So p lies between the two
  points that differ only on that split: a subdivision, realised by B(u, p, v) with those two points.
- **The pair is the constants.** p's side on every split is forced: p copies some v, plus {p}. That is realised by B(v̄, v, p),
  which forces p = v wherever v̄ ≠ v, which is every split.
- Both kinds are admitted: p is constrained, and it is not a copy, since it is free on a split or on the constants. ∎

**L5. Every missing combination has a certificate after either cheapest step.**
- **Subdivision.** Coordinates: the doubled split becomes two splits a (x₁ > 0) and b (x₁ ≥ 1) of the first coordinate, and the
  others are w ∈ {0, 1}^(s−1). The old points have (a, b) = (0, 0) or (1, 1) with every w, and the new point is (1, 0, w₀).
  - **The unoccupied (1, 0, w), w ≠ w₀.** Certified by:
    - middle B((0,0,w), p, (1,1,w)), with A sets {a} and {b}, disjoint, covering all but a and b;
    - end B((0,0,w₀), (1,0,w₀), p), covering {a};
    - end B((1,1,w₀), (1,0,w₀), p), covering {b}.

    The end knots are consistent, since A((1,0,w₀)) = D ⊆ D ∪ {a} = A((0,0,w₀)), and likewise with b, where D is the set of splits
    on which w₀ and w differ.
  - **The unoccupied (0, 1, w), for every w.** Certified by:
    - middle B((0,0,w), p, (1,1,w)), with A sets {b} and {a};
    - end B((1,0,w₀), (0,0,w), p), covering {a} ∪ D, consistent since {b} ⊆ {a, b} ∪ D;
    - end B((1,0,w₀), (1,1,w), p), covering {b} ∪ D.
- **Pendant.** Coordinates: the s old splits and the trivial split t. The old points are (x, 0) for every x, and the new point is
  (c, 1).
  - **The unoccupied (x, 1), x ≠ c.** Let D be the set of splits on which c and x differ. Certified by:
    - middle B((c,1), p, (x,0)), with A sets D and {t}, disjoint, covering all but D and t;
    - end B((c,0), (c,1), p), covering {t}, consistent since D ⊆ D ∪ {t};
    - end B((c,0), (x,0), p), covering D, consistent since {t} ⊆ D ∪ {t}.

So every unoccupied orientation of the s + 1 splits is forceable by three knots on distinctions present right after the cheapest
step. ∎

## Theorem

**Under the cheapest rule with up to three knots per step, from one knot, the base at n = 2^d is the cube Q_d for every d ≥ 2, in
every run and for every tie rule.**

For 2^d < n < 2^(d+1) it has d + 1 splits (2d + 4 states). So the number of orders λ is d at n = 2^d, and it grows by one at each
doubling.

*Proof.* Induction on d. Only the existence of an admitted zero-cost step is used at each fill step: the cheapest rule then takes
some zero-cost step, and by L1 every such step is a fill.
- **d = 2.** One knot, the line of three, is Q₁ (two points, one split) after a subdivision. So L5 with s = 1 gives Q₂ at n = 4,
  as `STATE-RULES-20261117-001A`, S5 found.
- **From Q_d at n = 2^d.**
  - By L4 the next step adds one split, n = 2^d + 1, in one of two classes.
  - By L5 every unoccupied orientation of the d + 1 splits then has a three-knot certificate, and by L3 it keeps it while other
    orientations fill.
  - So at every later step a zero-cost step exists. The cheapest rule takes one, filling one more orientation (L1) and adding no
    split.
  - After 2^(d+1) − 2^d − 1 such steps every orientation is occupied: Q_(d+1) at n = 2^(d+1).
- **The number of orders.** λ(Q_d) = d: d crossing splits need d chains, and the d coordinates are d chains. ∎

## Provenance

- **Classical.** The cube's cut system and its lattice dimension.
- **Related, from the advisor's memory and not checked:**
  - Mulder's convex expansion theorem for median graphs, with hypercubes as a special case;
  - Chepoi's isometric expansions of partial cubes;
  - Buneman graphs and split systems;
  - median betweenness axiomatics (Sholander; Bandelt and Hedlíková).

  These characterise expansions. They do not describe a cheapest growth under three-place betweenness constraints.
- **Local.**
  - The step analysis and the certificates are new as far as I know. Any part that proves to be folklore is cited, and what this
    adds is the reading: the cube growth as space built from knots alone, with the certificates in knot terms.
  - The certificate construction follows the advisor's restatement of forcing (`KNOT-CAP-20261117-001`'s consultation).
  - The forceability of every orientation was the advisor's claim; this proof makes it explicit.
  - The advisor checked the proof before the freeze and asked for three lines, now added: L4's use of A99, L2's no-doubling line,
    and the theorem's use of existence only, together with the base case from Q₁.
