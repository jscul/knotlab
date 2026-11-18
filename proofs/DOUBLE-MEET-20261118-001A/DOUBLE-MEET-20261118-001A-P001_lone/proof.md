# Lone distinctions in the weave: what is proved, and what is sketched

Ticket `DOUBLE-MEET-20261118-001A`, 18 November 2026. Written before the frozen run; checked by ticket B's gates and census
(`experiments/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches/`). Referee pending. Sections H and L are the advisor's
(claude-fable-5-2) sketches, not machine-checked, and are tested computationally in P0; T is the thread's (from
`BOND-METRIC-20261118-001A`).

## Terms

As in the pre-registration: the weave's knots u(i, j) and d(i, j), all not-all-equal; classes u and d; patches, discs, lone
distinctions (in one knot of the patch), facing pairs. Steps apart counts the knots of a least chain.

## T. The smallest case (proved)

On the two knots u(0, 0) = {(0,0), (1,0), (0,1)} and d(0, 0) = {(1,0), (0,1), (1,1)}, the distinctions (0, 0) and (1, 1) are lone,
of opposite classes and face each other (p = q = 1). No bond holds them: a set holding both but missing (1, 0) or (0, 1) is free (set
the missing one opposite to the other, and both knots hold), and a set holding all four contains a knot (`BOND-METRIC-20261118-001A`,
T2). ∎

## H. Heights and the cyclic criterion (the advisor's sketch)

Orient each pair forward along e1 = (1, 0), e2 = (−1, 1) or e3 = (0, −1), so that every knot of class u is a forward cycle. On a disc
every state, up to switching every value, is a height function h with h(v) ≡ i + 2j (mod 3) that rises by 1 or falls by 2 along each
forward pair, the value of v being the parity of h(v); a knot then has exactly one equal pair, the one where h falls by 2. Let D(s, t)
be the least weight of a route from s to t inside the patch, a forward step costing 1 and a backward step 2. Then h(t) − h(s) takes
exactly the values of the right residue in [−D(t, s), D(s, t)], and values on a set S respecting these bounds extend to a state. Fixing
values on S fixes h mod 6 there; writing h = r + 6k gives difference constraints on k, infeasible exactly when a cycle is negative,
which after rounding reads: **S is constrained exactly when it holds m ≥ 3 distinctions with a cyclic order whose D-sum is at most
3(m − 2).** (P0 checks this on every disc to seven knots, set by set.)

## L. D(x, y) + D(y, x) = 3 · steps apart on every disc (the advisor's sketch)

"≤": go out along a least chain and back along it; each pair costs 1 + 2. "≥": let δ be steps apart from x. Discs are systolic, so no
knot has δ constant on it; each knot then has one forward pair where δ falls and one where it rises. Putting the fall of 2 on the
falling pairs gives one height function h₁, on the rising pairs another, h₂; then (h₁ − h₂)(y) − (h₁ − h₂)(x) = 3δ(y), while
D(x, y) ≥ h₁(y) − h₁(x) and D(y, x) ≥ h₂(x) − h₂(y). (P0 checks the identity on every pair of every disc of the census.)

**Corollary (sketch): b ≥ steps apart + 1 on every disc.** A bond of m members is a minimal constrained set, so by H its members have a
cyclic order of D-sum at most 3(m − 2); the route from x to y and back along that order weighs at least D(x, y) + D(y, x) = 3·steps by
L. So 3(m − 2) ≥ 3·steps, that is b = m − 1 ≥ steps + 1.

## Open

The upper bound b ≤ steps + 1 when a bond exists; that only lone pairs of opposite classes facing each other can be unbonded; and an
exact rule for which facing pairs are (ticket B measures all three).

## Computed in ticket B (frozen)

- H's criterion gave exactly the constrained sets of every disc to seven knots (156,160 sets of 405 discs), and L's identity held on
  all 1,564,004 pairs of the 22,143 discs of the census; no bonded pair had b below steps + 1.
- The upper bound is false: 64 bonded pairs have b = steps + 2 (at steps 4), first on discs of ten knots.
- Every unbonded pair (12,318) is two lone distinctions of opposite classes facing each other; a disc is a true distance exactly when
  it has none (all 22,143).
