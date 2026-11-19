**Short answer:** I have no proof of Claim B for reached stages, and for all connected arrangements I believe it is false. Below is a 7-junction counterexample, checked by hand only and not run; it depends on one assumption about the law that you can check directly.

## Check of what you have

- **Lemma C** is correct. Two additions make it exact:
  - `δ(S)` is always a disjoint union of bonds of G. The complement of S is connected in G whenever it is in G′. S itself may split into parts `S_1..S_m` with no edge between them, joined only through T.
  - So a bond of G′ is a family of pairwise disjoint, non-touching bonds `B_i = δ(S_i)` of G plus a set T that connects them, with every complement part keeping a route to o.
- **Lemma O** is correct and extends to mixed rounds. An offshoot n ∈ T with parent u ∈ S can be removed from T, saving f−1 ≥ 1 and changing membership only among n's own edges. So offshoots can be stripped from any round, with `T'(fresh_n, y) = T''(x_{n,u}, y) + f(n) − 1`, and Claim B reduces to rounds of joins only.
- **Discount forms** are correct. One case to watch: k = 3, f = 1 with two of three parents held costs 0, so membership moves without paying.

## The quantity that matters

Since o ∉ S, a live junction u is in S exactly when its loose edges are in δ(S). Write `A(B)` for the set of live junctions a bond B holds. Then, for connected S and pairs not forced by membership:

`T'(x,y) + 1 = min over bonds B ∋ x,y of |B| − Σ_n max(0, 2|P(n) ∩ A(B)| − k(n) − f(n))`

The glued forms are the same over disjoint families. So T′ depends on bond sizes together with which live junctions each bond holds. T records only the minimum over all `A(B)`, and that is the gap.

For one join n (k = 2, f = 1, parents u, v) this is sharp:

- **Old pairs:** `T'(x,y) = T(x,y) − 1` exactly when some minimum bond through x, y holds both u and v (or a glued form does); otherwise T′ = T.
- **Pairs with n's fresh edge:** `T'(p, fresh_n) = min(W(p; ℓ_u, ℓ_v) − 2, μ + 1)` with `μ = min(T(p,ℓ_u), T(p,ℓ_v))`. Only whether W is μ+1, μ+2 or more matters.

So Claim B holds whenever "pairwise bonds of the right size imply one common bond" (a Helly property of minimum bonds) holds on both sides.

One piece is easy: if u and v each have a single parent j, then for p outside their edges `W(p; ℓ_u, ℓ_v) = T(p, ℓ_u) + f(v)`. A failure therefore needs a parent that is itself a join.

## Counterexample for general arrangements

**Arrangement.** Junctions a, b, c, u, v, u′, v′.

- a–b twice (p1, p2) and a–c twice (q1, q2).
- b–u twice and b–v twice; c–u′ twice and c–v′ twice.
- One loose edge on each of u, v, u′, v′.
- All junctions have at least 3 edges. Live = {u, v, u′, v′}; F = {{u,v}, {u′,v′}}.

**The map.** φ swaps p1 and q1 and fixes everything else.

- It keeps R: loose edges, live junctions' edge sets and F are all fixed.
- It is a table isometry:
  - Moving a across a bond that separates b from c swaps {p1,p2} for {q1,q2} and changes nothing else (not size, not other edges, not `A(B)`). So `T(p1,z) = T(q1,z)` for every other z.
  - Among the four edges every entry is 3. The cheapest bond through p1, p2 has size 4: a's own edges, or δ({b,u,v}) = {p1, p2, ℓ_u, ℓ_v}. δ({b}) = 6 and δ({b,u}) = 5. The only bond through q1 and p2 is a's own four edges.

**The round.** Assume the law joins {u,v} by n and {u′,v′} by n′ with f = 1.

- `T'(p1,p2) = 2`: δ′({b,u,v,n}) = {p1, p2, fresh_n}.
- `T'(q1,p2) = 3`: a must be separated from both b and c. Without a and o, the parts {b,u,v,n} and {c,u′,v′,n′} are not connected, so the only bond is a's four edges.
- So φ′ is not an isometry.

**What to check:** that the law really gives f(n) = 1 here. If it gives f(n) = 2, use triple edges a–b and a–c and three live junctions under b (each joined to b twice, one loose edge each). Then the tie is at 6 and the failure survives f ≤ 2.

**The mechanism** has three parts:

1. A junction whose edges split evenly between two holders, so swapping one edge across breaks holder classes for free.
2. A tie between a bond holding no live junction (a's edges) and a bond holding a full parent set.
3. The join discounts only the second, so the tie breaks.

This is your "static collision" failure, but with R kept. T and R cannot see `A(B)`, so the readings W are not functions of T and R in general.

## Answers

**1. Reached stages.** I have no proof. A proof cannot go through W being a function of T and R in general. It would need a reached-stage lemma of this form: if a bond holding no live junction ties with a bond holding more than (k+f)/2 of some parent set, no R-keeping isometry trades a pair read by both for a pair read only by one.
   - Bonds holding no live junction are exactly the previous stage's bonds, so this is a statement about ties between the old table and the new one.
   - The induction cannot run on T alone, because T is not self-propagating. The candidate invariant is the traced table: the minimum bond size through x, y for each prescribed set of live junctions held or not held.
   - Cheapest test: on the 1,746,752 symmetries, check whether each one preserves the traced table. If all do, prove that stronger claim by induction over layers. If some extend without preserving it, Claim B holds there by coincidence of minima and needs a different proof.

**2. Hunt target.** In a reached stage a failure needs all of:
   - a junction with no loose edge whose edges split evenly between two holders, with a class-breaking swap that is a table symmetry;
   - a connected part on one holder's side, cut off by exactly that holder's edges plus loose edges, holding a full parent set with k > f;
   - a tie in size with the junction's own edges;
   - a parent with k ≥ 2.

   That means at least three completed rounds plus two copies, so about 10 or more junctions. Your census reaches that size without a failure. I do not see why it must lie outside reached stages; the double edges b–u in my example are what reached stages forbid, and replacing them by two distinct backed parents is the thing to try.

**3. Holder-breaking symmetries.** The split formula never uses which junctions an edge joins. It uses bond sizes, which live junctions are held, and membership of the two read edges. A swap at an evenly split junction with no loose edge comes with a bijection on bonds (move that junction across) preserving all three, so it commutes with the round. That argument covers every entry except pairs inside the swapped classes, which is exactly where my example fails. Why those pairs survive in reached stages is the same open gap as Claim B.

**4. Bets.**
   - Claim B true for all reached stages: 60%.
   - Claim B true for all connected arrangements: 10%. The remaining doubt is whether the law forms those joins with f ≤ 2 on my example.
