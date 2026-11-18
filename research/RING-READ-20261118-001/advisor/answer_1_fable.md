**Verdict:** I would not freeze this yet. The table is only an upper bound as designed, and P5 fails by construction, which takes P3 with it.

**(1) Table soundness**

The m-bounded enumeration only ever finds bonds, so it gives upper bounds on distance. For connected J (o ∉ J) with cycle rank b(J):

|δ(J)| = Σ(deg − 2) + 2 − 2·b(J)

- **Chains:** a path of k three-distinction junctions is a bond of size k + 2. A bond of size 9 (needed at T = 20) can therefore have 7 junctions on its small side. One-parent chains of length 5 look likely given the 5–6 round period, and m = 4 misses them.
- **Belts:** a layer cut is a bond (both sides are connected), so it matters whenever its size is ≤ H + 1. Only the earliest layers could qualify.
- **Completeness proof:** bound b(J) ≤ β|J| from the join structure (a p-parent join adds p − 1 to cycle rank). That gives |J| ≤ (s − 2)/(1 − 2β) when the minimum size is 3.
- **Sharper check:** certify each entry with a max-flow lower bound. For e = (a,b), f = (c,d), take the min cut separating {a,c} from {b,d} and {a,d} from {b,c}. Where flow equals the enumeration value, the entry is exact with no m needed.

**(2) Reader**

Stars are a basis of the cut space, so the principled prune is linear. At stage s, discard a clique if it lies in the GF(2) span of the junctions already read; this covers every k at once.

It needs one lemma: a non-star bond of support s is a sum of stars each smaller than s. By the formula this holds for tree-like J with minimum size 3. With cycles it needs girth: a triangle with two 3-junctions ties (s + 3 + 3 − 6 = s), while a 4-cycle gives s + 1. Verify "no triangles, no doubly shared pairs" per T and the lemma follows. I would run this as R1′ alongside R2.

**(3) Bets against**

- **P5 (certain).** A live one-parent junction N has only P and o as neighbours, so {P, o} is a 2-vertex cut. Every cut vertex of G − o gives one.
- **P3 (likely).** The twists in (4) give other legal incidences with the same table, and P + N is a bond, so it is a candidate clique unless the prune already removed it. Say whether R2 takes pre-prune or post-prune candidates.
- **P1 (as evidence).** Agreement of m = 4 and m = 5 does not show the table is right, since both miss the same long chains. I expect actual disagreement by T ≈ 15–20 if five-long chains of 3-junctions occur. Use m ≥ (largest size) − 2, or the flow certificate.
- **P6 (mild).** Two distinctions of a large junction N can lie in a smaller bond around N's neighbours (for example two join-siblings plus their common lower neighbour). Within-junction distances can then be below size − 1, so H may come out lower. No H removes twist ambiguity, because twists preserve the whole table.
- **P2 and P4.** P2 should hold. P4 holds only if P3 does.

**(4) Two incidences, one table**

Yes. Take a component C of G − {P, o} attached to P by a single distinction e. The Whitney twist replaces star(P) with star(P) + Σ stars(C) and leaves every other star unchanged. Then e becomes loose on its old junction, and C's loose distinctions become shared with P′.

- If C is a single live N with two or more loose ends, P′ and N share two distinctions. A "one shared distinction per pair" rule excludes this.
- If C has two live junctions with one loose end each, there is no double sharing. The incidence is fully legal, and only history excludes it (a loose distinction on a non-newest junction).

So uniqueness has to be argued from the law, not from Whitney. Enumerate the 2-separations {v, o} and show each twist breaks a stated legality rule. Then make that rule part of R2's survivor filter, and state P3 as "unique among round-legal incidences".

I checked none of this against the repo's growth code. The chain lengths, the girth and the layer-cut sizes are the three facts to compute first.