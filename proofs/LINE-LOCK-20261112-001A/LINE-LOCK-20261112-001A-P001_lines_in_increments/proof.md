# No permutive sub-stitch in a harmony's stitch, and the coset census

Status: Proved (the theorem by hand: the advisor model's lemma, rechecked here) with an exact census; **referee pending** (the
background referee thread). Ticket A of `research/LINE-LOCK-20261112-001/preregistration.md`, frozen with the code in commit
`023a3da46`.

Words as in the pre-registration, renamed after the advisor model's word check (`research/LINE-LOCK-20261112-001/line_lock.md`,
Words): harmony (every state on the integers repeats), the one-order stitch R ⊆ W³, an orbit O of the harmony's shift σ and flip κ
with its group Q, the **stitch pairs** A ⊆ Q² (the pre-registration's increments), a **permutive sub-stitch** (its Latin sub-law:
triples inside R in which, for every two entries from its set of states, exactly one third completes a triple), a **ratio subgroup**
(its line: a cyclic subgroup of Q² inside A whose order-q part, q an odd prime, is ⟨(g, λg)⟩ with ratio λ not 0 or 1 modulo q; the
literature's line through the origin), the **additive** automaton it gives, and the three degenerate subgroups {(a, 0)}, {(a, a)},
{(0, b)}.

## 1. The theorem (proved)

**If H is a harmony, its one-order stitch R holds no permutive sub-stitch on a set S of at least two states whose three entries all
range over S.**

*Proof.* Fix a kind (0, a, b) of H and a place i, and let x, y, z be the bits of each state of S at i, i + a and i + b, read as three
functions (fibres) on S. Every triple (j, k, l) of the permutive set T satisfies not-all-equal on (x_j, y_k, z_l).

- *At most one fibre is not constant.* Suppose x and y are not constant; let X₀ = {x = 0} have r members and Y₀ = {y = 0} have c, with
  n = |S|. The triples with j in X₀ and k in Y₀ need z = 1, those with j in X₁ and k in Y₁ need z = 0. A Latin r × c rectangle holds at
  least max(r, c) distinct third entries, so max(r, c) + max(n − r, n − c) ≤ n, which forces r = c and makes X₀ × Y₀ a Latin subsquare on
  the set Σ = {z = 1}. Then each row of X₀ already uses all of Σ inside Y₀, so a column k of Y₁ meets the rows of X₀ in entries outside
  Σ; and the rows of X₁ meet it in entries with z = 0, also outside Σ. The column misses Σ, which a Latin column cannot. The same holds
  for any two of the three fibres.
- *The other two are then constant and opposite.* If x is not constant and y ≡ y₀, z ≡ z₀, a triple with x_j = y₀ needs z₀ ≠ y₀.
- *A free site.* Two distinct states of S differ at some place i, so the fibre at i is not constant in each of its three roles (first
  member at i, second member of the knot starting at i − a, third of the knot starting at i − b). So in every state of S, every knot of
  H through i has its other two members opposite. Flip place i of one state's repeating extension at a single place on the integers:
  every knot through it still holds, every other knot is unchanged, and the result is a state that does not repeat. H is then not a
  harmony. ∎

**Corollaries.** (a) No orbit's stitch pairs hold a ratio subgroup: on the coset of the order-q subgroup through u, ⟨(g, λg)⟩ inside A
gives a permutive sub-stitch, since λ ≠ 0 makes the first two entries fix the third, λ invertible makes the first and third fix the second,
and λ ≠ 1 makes the last two fix the first. (b) Nor the advisor's Z₂ × Z₂ block (the graph of a fixed-point-free automorphism of
order 3). (c) Nor a free pair H' × H' inside A (it holds the permutive law z = x + y on two states). This holds for every harmony at every
period, for every knot shape across two shifts and every slot order, and so for the odd harmonies of periods 61, 73 and 193, which the
coordinator named. A ratio subgroup is what puts an additive automaton t(x + q) = (1 − λ) t(x) + λ t(x + p) over F_q inside a
stitched arrangement (the advisor's convention), the source of Ledrappier-type arithmetic; the unlagged stitch of a harmony never has
one. The theorem is not true by definition: it uses that every state repeats, through the free site.

**What it leaves open.** Cosets d + Λ inside A with d outside Λ, realised by lagged stitches when d has no flip part: their three
entries range over different sets of states, so the free site is only for lagged kinds; permutive sub-stitches with entries in
different orbits; laws seen only after blocking copies; and functional but not permutive sub-stitches.

## 2. The census (exact; frozen; `result_census.json`, `result.json`)

Every orbit of the 66 harmonies of span at most 8 (periods 2 to 240) and of the 7 odd step sets (periods 61, 73, 193): 73 harmonies,
187 orbits, 101 of them with a period that has an odd prime factor.

| Item | Found |
| --- | --- |
| Harmonies with a free site (the theorem's premise) | 0 |
| Ratio subgroups, Z₂ × Z₂ blocks, free pairs (the theorem) | 0, 0, 0 |
| Cyclic subgroups inside an orbit's stitch pairs | 22, all degenerate |
| Cosets of a cyclic subgroup inside the stitch pairs | 2, both degenerate |
| Cosets with a ratio part (any, and those a lag can give) | 0 and 0 |

The odd harmonies' stitch pairs are {(0, 0)} on every orbit: stitched in one order, a knot whose three copies lie in one orbit of an odd
harmony forces them equal, so nothing moves inside an orbit at all, let alone additively.

## 3. One size past (after the run; labelled; `stress_one_size_past.py`, `result_stress.json`)

The 32 harmonies of span exactly 9 that the frozen census did not hold (periods 12 to 252): no free site, no ratio subgroup, block or
free pair, no coset with a ratio part.

## What this establishes

- Proved: a harmony's one-order stitch holds no permutive sub-stitch on one set of states, so no additive automaton in any orbit, for every
  harmony, period, two-way knot shape and slot order.
- Exact on the range (73 harmonies, 187 orbits; and 32 more one size past): no coset with a ratio part either, so lagged stitches hold
  none.
- So two-way influence of Ledrappier's kind cannot come from stitched harmonies in range: the obstruction the coordinator asked to state
  if everything reduced to cycles, now with a proof for the unlagged case.
- Not established: permutive sub-stitches across orbits, after blocking, or in laws other than stitched harmonies (other binding modes, other
  laws on bits); the full cyclic structure of the lagged arrangements.
