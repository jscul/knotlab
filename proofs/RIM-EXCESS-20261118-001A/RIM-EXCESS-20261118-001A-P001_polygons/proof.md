# Bond polygons and the excess at the weave's rim

Ticket `RIM-EXCESS-20261118-001A`, 18 November 2026. Written before the frozen census of ticket B
(`experiments/RIM-EXCESS-20261118-001B/RIM-EXCESS-20261118-001B-E001_excess/`). Refereed: report R1, confirmed with fixes, no Block
(`research/RIM-EXCESS-20261118-001/referee-R1/report.md`); its fixes folded in on 18 November. Uses `WEAVE-HEIGHTS-20261118-001A`
(refereed): D, Lemma 2(i), Proposition 3, Lemma 6 and Theorem 7, on a weave patch without holes. Lemma P, the corollary and Lemma C are
the thread's, checked by the advisor (claude-fable-5-2), whose sharpenings are folded in; the figure-eight statement is the advisor's
sketch.

## Lemma P (bond polygons)

Let B be a bond of m ≥ 3 members. Then B has a cyclic order of all its members with D-sum at most 3(m − 2) (Corollary 4 of
`WEAVE-HEIGHTS-20261118-001A`), and every such cyclic order has D-sum exactly 3(m − 2), each member s lying on a D-geodesic between its
two neighbours p, n: D(p, s) + D(s, n) = D(p, n).

*Proof.* D-sums of cyclic orders are multiples of 3 (Lemma 2(i): each closed walk weighs ≡ 0). Removing a member s from the cyclic order
lowers its D-sum by δ_s = D(p, s) + D(s, n) − D(p, n), which is ≥ 0 (triangle inequality) and ≡ 0 (mod 3) (Lemma 2(i) on the three
terms). For m ≥ 4, B − s is free (every proper subset of a bond is free), so by Proposition 3 its induced order is not tight:
L − δ_s > 3(m − 3), where L is the D-sum. With L ≤ 3(m − 2) this gives δ_s < 3, hence δ_s = 0; and taking δ_s = 0, L > 3(m − 3), so
L = 3(m − 2). For m = 3 the pair B − s has D-sum L − δ_s = D(p, n) + D(n, p) = 3 s(p, n) ≥ 3 (Lemma 6), while L ≤ 3, so again δ_s = 0
and L = 3. ∎ (The case m = 3 uses Lemma 6, which rests on the bridged-graph theorems cited for Lemma 5 of `WEAVE-HEIGHTS-20261118-001A`;
the case m ≥ 4 uses only Proposition 3.)

More generally, removing any r members (leaving at least three) lowers the D-sum by at most 3(r − 1).

## Corollary (the excess)

For x ≠ y held by a bond, write b(x, y) = s(x, y) + 1 + e, e ≥ 0 the **excess** (Theorem 7). If B is a least bond holding x and y, its
polygon (any tight cyclic order of B) has D-sum W = 3(|B| − 2) = 3(s + e), and the round trip costs D(x, y) + D(y, x) = 3s (Lemma 6). So

e = (W − D(x, y) − D(y, x)) / 3:

the excess is how much longer the least bond's polygon is than the round trip between the pair, in units of 3.

## Lemma C (where a least bond's members lie)

Split the polygon at x and y into the arc from x to y, of D-sum a₁, and the arc back, of D-sum a₂. Then (a₁ − D(x, y)) + (a₂ − D(y, x))
= 3e, with both terms non-negative multiples of 3. Every member p on the first arc has D(x, p) + D(p, y) − D(x, y) ≤ a₁ − D(x, y), and
likewise on the second. So every member lies within detour 3e of one of the two round-trip routes, and at e = 0 every member lies on a
D-geodesic from x to y or from y to x. ∎

## The polygon search

For e = 0, 1, …: enumerate cyclic sequences through x and y of s + 2 + e distinct distinctions, drawn from those within detour 3e
(Lemma C), with D-sum exactly 3(s + e) and every member on a D-geodesic between its neighbours (Lemma P); return the first whose set has
no constrained proper subset, tested by Proposition 3 over every sub-collection and every cyclic order of it (not only the induced one).
By Proposition 3 and Lemma P this returns exactly b(x, y) when b(x, y) ≤ s + 1 + emax; a pair with no polygon up to emax has no bond of
excess ≤ emax. No bond has more than |V| members, so run to emax = |V| − 2 − s the search exhausts every possible bond and certifies,
without listing the states, that no bond holds the pair (the referee's addition). (Gates and R2 check it at excess 0 and on unbonded
pairs; the referee checks excess 1 and 2.)

## The figure-eight (the advisor's sketch, not claimed proved)

A geodesic walk passes a lone distinction of one class with the patch on one side and a lone distinction of the other class with the
patch on the other side (Lemma 8 of `WEAVE-HEIGHTS-20261118-001A`). So, in a disc, the polygon of a bond through a lone pair of opposite
classes crosses itself at some distinction y outside the bond, and the bond is (C₁ ∪ C₂) − y for two tight sets C₁ ∋ x, y and C₂ ∋ y, z
meeting only in y; its excess is then e = e₁ + e₂ + (s(x, y) + s(y, z) − s(x, z)). Not checked here.

## Open

Whether the excess grows without limit with patch size (to fourteen knots its largest value on facing pairs is 2, the referee); why
excess lives only on lone pairs of opposite classes facing each other (computed in ticket B).

## Computed in ticket B (frozen)

Lemma P held on all 116,932 bonds of the 2,907 discs to nine knots; the polygon search matched brute force on all 142,413 pairs there. On
every disc of eleven and twelve knots (13,746 and 37,901), every pair carrying an excess (48 and 198) and every unbonded pair is a lone
pair of opposite classes facing each other; the largest excess is 1 at eleven knots and 2 at twelve (6 pairs). Random patches of 20 to 40
knots gave excess 0 on 253 facing pairs, 1 on one, and 20 searches ran out of time; eight shape climbs reached 2 at most.

*Corrected after the referee (Narrowing, wording):* R2 compared the search with brute force only where no bonded pair has an excess (to
nine knots), so it validated excess 0 and unbonded pairs. The 20 random searches that ran out of time are settled by the referee except
three: 9 at excess 0, 8 certified unbonded, 3 with no bond up to excess 8, 8 and 9.

## Checked by the referee (R1)

Lemma P with every tight order enumerated on every disc of ten knots (319,114 bonds, 319,117 tight orders, each of D-sum 3(m − 2) and
geodesic at every member); the search against brute force at excess 1 and 2 (60 and 24 pairs at excess 1, 6 at excess 2, 13,370 unbonded
pairs, every such pair at ten and eleven knots and on 3,000 random discs each of twelve and thirteen, by the referee's search, and by this one
on the 10,620 pairs of ten and eleven knots; no mismatch); on the lone opposite facing pairs of every disc of thirteen knots (104,902 discs) and fourteen (291,312), the largest excess is
2 (24 and 102 pairs), with no 3.
