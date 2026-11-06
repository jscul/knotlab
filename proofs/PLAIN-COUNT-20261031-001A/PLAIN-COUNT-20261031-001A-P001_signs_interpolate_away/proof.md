# Signs interpolate away: plain Pfaffian triple systems are #P-hard to count

Status: Proved

Ticket `PLAIN-COUNT-20261031-001A`, 2026-10-31.

**What it uses:**
- **`SOFT-CROSS-20261031-001B`, Theorem 4:** counting colourings of cubic bipartite Pfaffian graphs under signings is #P-hard. The oracle
  instances are those of `SOFT-CROSS-20261031-001A`: planar hosts carrying junctions of twisted pages, with a Pfaffian certificate.
- **`SOFT-CROSS-20261031-001A`:**
  - Lemma 1: the dead cap;
  - Lemma 4: a long edge with k capped pairs acts by 3^k M^k = 9^k P₊ + (−3)^k P₋;
  - Corollary 6: 9·#col(K₃,₃) from four snake instances.
- **`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4:** a connected cubic signed system is non-colourable iff its signing is Pfaffian.
- **External, not replayed:** Kasteleyn's theorem; Vandermonde systems with distinct nodes are invertible.

## Why this ticket exists

`SOFT-CROSS-20261031-001` proved counting hard on the knot's graphs, but with the signs supplied as part of the input. The program's native
objects carry no signs: a triple system is a 3-regular 3-uniform hypergraph, and its colourings are its proper 2-colourings. This ticket
trades every sign for the length of a path, and so proves the hardness for plain triple systems.

## Standard statement

**Setting.**
- **Plain triple systems.** A *plain triple system* is a 3-regular 3-uniform hypergraph, with points and lines. Its *incidence graph* is
  cubic bipartite, and #col counts its proper 2-colourings.
- **Long edges.** A *long edge with k pairs* replaces an incidence (p, ℓ) by a path p − ℓ₁ − p₁ − … − ℓ_k − p_k − ℓ. Each pair (ℓ_i, p_i) is
  closed by a dead cap.
- **Notation.** For a signed system G with L negated incidences, G_k is the plain system in which each negated incidence is replaced by a
  long edge with k pairs. Write t = (−1/3)^k.

**Results.**
- **Lemma 1 (signs by interpolation).** #col(G_k) = 9^{kL} q(t) for a polynomial q of degree at most L.
  - q(−1) = #col(G), the signed count.
  - q(1) is the count with the signs dropped.
  - The counts at k = 1, …, L + 1 determine q.
- **Lemma 2 (certificates survive).** Let G be an instance of `SOFT-CROSS-20261031-001A`: a planar host and planar pages glued at junction
  squares, with a glued Kasteleyn signing that is non-colourable. Then G_k has the same certificate.
  - Its pieces are the components left once the square vertices are removed.
  - A long edge goes with the piece of the edge it replaces.
- **Lemma 3 (switching).** Switching at vertices inside the pages leaves the soft crossing with 2 negations on its page Q and 4 on its page
  R, instead of 4 and 7. This is the minimum over all switchings inside each page (exhaustive). Counts are unchanged.
- **Theorem 4.** Counting the proper 2-colourings of 3-regular 3-uniform hypergraphs whose incidence graphs are Pfaffian is #P-hard under
  polynomial-time Turing reductions.
- **Corollary 5 (end to end).** 9·#col(K₃,₃) = 54 is recovered from counts of plain triple systems with Pfaffian incidence graphs alone:
  - 100 plain counts, the largest system with 18504 vertices;
  - snakes with k_S = 1, 3, 5, 7 junctions and L = 6k_S long edges, at L + 1 lengths each.

  Every plain instance checked (lengths 1 and 2, all k_S) is certified Pfaffian and non-planar, and has three twisted branches at every
  junction.

## Nearest known result

- **Fan and Cai** (arXiv 2011.09110, 2020) prove Holant([0, 1, 1, 0] | =3) #P-hard; this is counting 2-colourings of 3-regular 3-uniform
  hypergraphs. They also note that its planar restriction is in FP.
- **Interpolation.** Replacing weights by paths and interpolating is standard (Valiant; Dyer, Goldberg and Jerrum; Cai, Lu and Xia).
- **What is new** (no overlap found, candidate local delta, folklore risk moderate): the hardness survives on hypergraphs whose incidence
  graphs are Pfaffian, where perfect matchings still count in polynomial time.

## Proof of Lemma 1

**The expansion.**
- By `SOFT-CROSS-20261031-001A`, Lemma 4, each long edge acts between p and p_k by 9^k(P₊ + tP₋), and p_k − ℓ is a plain incidence.
- Expand every long edge into its two parts. Then #col(G_k) = 9^{kL} Σ_J c_J t^{|J|}, where J runs over the sets of long edges taking their
  P₋ part.
- c_J is the count with P₋ on J and P₊ elsewhere. It does not depend on k, so q(t) = Σ_J c_J t^{|J|} has degree at most L.

**The two values.**
- At t = 1 every long edge acts by P₊ + P₋ = I, a plain incidence.
- At t = −1 it acts by P₊ − P₋ = [[0, 1], [1, 0]]: ℓ sees the complement of p's colour, which is the negated incidence. So q(−1) = #col(G).

**Solving.** The nodes (−1/3)^k for k = 1, …, L + 1 are distinct, so the Vandermonde system determines q. ∎

## Proof of Lemma 2

- **Drawing.** A long edge and its caps are drawn inside a face of the piece next to the edge it replaces. So every piece stays planar, and
  every junction square stays a face of the pieces that contain it.
- **The argument.** It is that of `SOFT-CROSS-20261031-001A`, Theorem 5. Kasteleyn signings of the pieces, switched to one odd pattern on
  every square, glue to a non-colourable signing (`SEYMOUR-COUNT-20261030-001A`, Lemma 1(iii)). That signing is Pfaffian
  (`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4).
- **Check.** Section 4 verifies the certificate on the plain instances at lengths 1 and 2 for k_S = 1, 3, 5, 7. Section 5 verifies it with
  signed host edges as well. ∎

## Proof of Lemma 3

- **Invariance.** Switching at a point renames its colour. Switching at a line complements all three values it sees, and not-all-equal is
  invariant under that. So counts are unchanged.
- **The minimum.** Section 2 searches all 2²⁰ switchings inside each page, meeting in the middle. The minimum is 2 for Q and 4 for R. One of
  R's four is the incidence of the square point c₀ into R; the original c₃ negation is switched away. ∎

## Proof of Theorem 4

**The reduction.**
- Take an oracle instance G of `SOFT-CROSS-20261031-001B`, Theorem 4. It has polynomially many negated incidences, L.
- Build G_k for k = 1, …, L + 1. Each is a plain triple system of polynomial size: a long edge adds 10k vertices.
- By Lemma 2 their incidence graphs are Pfaffian.
- Query their counts, and evaluate q(−1) = #col(G) (Lemma 1).

**Composition.** Composing with `SOFT-CROSS-20261031-001B`'s Turing reduction from #NAE-3SAT gives the theorem. ∎

## Proof of Corollary 5

By computation (section 3):
- for each k_S, the plain counts at L + 1 lengths give q(−1), equal to the directly counted signed instance;
- the four signed values give 9·#col(K₃,₃) = 54 through `SOFT-CROSS-20261031-001A`'s system. ∎

## What the computation checks

`check.py` (about four minutes, mostly the 43 plain counts for k_S = 7):
- **1, Lemma 1 on K₃,₃** with 2 and 5 negations: q(−1) = 2 (signed) and q(1) = 6 (signs dropped).
- **2, Lemma 3.** 11 → 6 negations per junction, for k_S = 1, 3, 5, 7, with counts unchanged.
- **3, Corollary 5.** The plain series of 7, 19, 31 and 43 counts, the largest system 18504 vertices, then 54.
- **4, the plain instances** at lengths 1 and 2:
  - no signs, cubic bipartite, certified Pfaffian and non-planar;
  - three twisted branches at every junction, and no good root.
- **5, signed hosts.** K₃,₃ signings with 2 and 5 negations at k_S = 1: L = 8 and 11, recovered exactly and certified.
- **6, controls:**
  - q(1) is the count with the signs dropped, and differs from the signed count;
  - L counts leave q(−1) undetermined.

## Reading

- **The knot's graphs are hard to count without any supplied sign.** A sign is a short path in disguise: a long edge read at t = −1 is a
  negation.
- **What the hard instances are.** Hypergraphs whose incidence graphs are Pfaffian, the graphs on which perfect matchings, and with them the
  knot's own counts, stay polynomial.
- **What their hardness comes from.** Their plain signs differ from the Pfaffian class, and the difference branches at every junction.
  Ticket B shows that plain pages are always twisted, so in the plain world twisting is the default.

## Nonclaims

- **No claim about braces.** The instances have 2-edge cuts (caps, long edges), so they are not braces.
- **The gadget still needs signs inside its pages.** They are removed by interpolation, not by a plain gadget. During scoping, no pair of
  plain pages among 50 page tensors gave a soft crossing with nonzero double entry. That scan is scoping, not evidence of this ticket.
- **External results.** Kasteleyn's theorem and Vandermonde invertibility are not replayed.
