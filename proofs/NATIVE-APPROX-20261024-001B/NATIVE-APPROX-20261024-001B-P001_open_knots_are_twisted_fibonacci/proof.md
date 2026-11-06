# The open knots are twisted Fibonacci knots

Status: Proved

Ticket `NATIVE-APPROX-20261024-001B`, 2026-10-24.

**What it uses:**
- from `NATIVE-APPROX-20261024-001A-P001`:
  - the eight non-windable knots are those excluding three tuples;
  - the six non-symmetric ones are the only knots without an efficient counting algorithm;
- from `NATIVE-COUNTING-20261024-001A-P001`: the Fibonacci knot Fib, allowing 0, 2 or 3 ones, is λ₀ v₀^⊗3 + λ₁ v₁^⊗3 with
  orthonormal vᵢ = (S₀ⱼ, S₁ⱼ) and λⱼ = 1/S₀ⱼ;
- background, cited: McQuillan's closure theorem for windable functions (arXiv:1301.2880, Theorem 4); the holographic algorithm for
  Fibonacci gates (Cai, Lu and Xia); weighted Fibonacci gates (Lu, Wang and Zhang, arXiv:1402.4370), whose edge weights are unary
  activities.

## Standard statement

**Setting.**
- **The knots.** S is the knot excluding 000, 011 and 101. X is the disequality [0, 1, 0] on two places.
- **Twisted networks.** A *twisted Fibonacci network* is a native network of Fib in which some edges carry X instead of equality.

**Theorem 1 (one orbit).**
- **The orbit.** The six non-symmetric knots excluding three tuples form a single orbit under permutations of places and global
  complement.
- **The twists.** Each equals Fib with one or two of its places negated.
- **The extremes.** Fib with no negation and with all three negated gives the two no-lone-value knots.
- **The example.** In particular, S(x, y, z) = Fib(x, y, ¬z).

**Theorem 2 (networks).** Every native network of S with pins and free legs has the same count as a twisted Fibonacci network:
- every knot becomes Fib;
- an edge with exactly one end at a negated place (the z-place of an S knot) carries a twist;
- an edge with both ends at negated places is plain;
- a pin at a negated place is complemented.

**Proposition 3 (a twist is a signed reflection).**
- **The matrix.** In the Fibonacci eigenbasis, a twist becomes
  C = [vⱼ · X vₖ] = (1/D²) [[2φ, φ], [φ, −2φ]],
  a symmetric orthogonal reflection with one negative entry.
- **The signed sum.** So the count of a twisted Fibonacci network is a signed two-spin sum over knot spins sᵥ ∈ {0, 1}:
  Σ_s ∏ᵥ λ_{sᵥ} ∏ over plain edges δ(s_u, sᵥ) ∏ over twisted edges C(s_u, sᵥ) ∏ over legs u_{sᵥ}(leg).
  Here u_s(a) = v_s(a) for a pin a, and v_s(0) + v_s(1) for a free leg.

**Proposition 4 (why the known tools stop).**
- **(a) Winding.** S is not windable (ticket A). The strictly terraced windable functions are closed under connected circuits, so no
  circuit of windable functions realizes S, and McQuillan's scheme does not apply.
- **(b) Holography.** The Fibonacci holographic algorithm diagonalizes every knot with the same orthonormal change of basis. That makes
  every untwisted edge an identity, but a twist becomes C, which is not diagonal.
- **(c) Weighted Fibonacci gates.** Lu, Wang and Zhang allow edge activities, unary weights [λ(0), λ(1)] on edges. A twist is the
  binary function X, not an activity, and X is not diagonal in the Fibonacci basis, so no activity reproduces it.
- **(d) Exact counting** is #P-hard, given Backens's dichotomy (`NATIVE-COUNTING-20261024-001A`).

**Reading.**
- **The open frontier.** It is exactly where the Fibonacci knot meets a twist. In the knot's own basis a twist is a reflection with a
  negative entry.
- **The same sign twice.** This is the same sign that made the Fibonacci rule need a negative weight in three dimensions
  (`HUB-DIMENSION-20261024-001B`). Both open problems are signs, while every unsigned case is settled.

## Nearest known result

- **Twisted Fibonacci networks are a natural generalization.** Fibonacci gates with disequality edges are Holant problems not covered
  by the cited approximation schemes. No treatment of their approximate counting was found in the bounded scan.
- **The local contribution** is the identification of the open six with twisted Fibonacci knots, and of the twist with a signed
  reflection. Novelty: `candidate-local-delta`; folklore risk medium.

## Proof

### Theorem 1

- **The orbit.** The check enumerates the images of S under the six permutations and the complement: there are six, and they are
  exactly the non-symmetric knots excluding three tuples.
- **The twists.** It also enumerates Fib with each of the eight negation patterns. One or two negations give these six, and zero or
  three give the no-lone-value knots.
- **The example.** Directly, negating z maps the allowed set {000, 011, 101, 110, 111} of Fib to {001, 010, 100, 111, 110}, which is S.
  ∎

### Theorem 2

- **Rewrite the knots.** Write each S knot as Fib with its z-place negated.
- **Edges.** An internal edge e meets two places.
  - If neither is negated, both knots see e.
  - If exactly one is, the two knots see e and ¬e. That is a twisted edge.
  - If both are, both see ¬e. Renaming e to ¬e leaves the sum over e unchanged and makes the edge plain.
- **Legs.** A pin p at a negated place is seen as ¬p. A free leg is summed over both values either way. ∎

### Proposition 3

- **The decomposition.** With Fib = Σⱼ λⱼ vⱼ^⊗3, contracting the network inserts, on each edge, the matrix [vⱼ · M vₖ]. Here M is the
  identity for plain edges and X for twisted ones.
  - Orthonormality makes the identity δ.
  - Direct computation gives C, which satisfies C² = I since X² = I, and has the single negative entry −2φ/D².
- **Legs.** Each leg contributes the component of vⱼ, or their sum for a free leg. ∎

### Proposition 4

- **(a)** By McQuillan's Theorem 4 and ticket A.
- **(b)** By Proposition 3: C is not diagonal.
- **(c)** An edge activity is a diagonal binary function diag(λ(0), λ(1)) in the standard basis, which X is not. In the Fibonacci
  basis an activity becomes VᵀΛV, and the twist becomes C. Λ = VCVᵀ = X would be needed, and X is not diagonal.
- **(d)** By the cited dichotomy. ∎

## Checks

`check.py` uses the standard library only (seed 20261024). It confirms:
- **Theorem 1** by enumeration.
- **Theorem 2 and Proposition 3** on 1,000 random native networks of S with up to seven knots, eleven internal edges, and pinned and
  unpinned legs: the direct count, the twisted Fibonacci count and the signed two-spin sum agree on every network. 779 of the networks
  contain a twisted edge.
- **The matrix C.** It is the stated reflection, orthogonal, with one negative entry.

**Controls.**
- **Not every knot is a twisted Fibonacci knot.** Not-all-equal is not Fib with any negations and permutation of places.
- **Twists matter.** Treating twisted edges as plain changes the count on some network.
- **Signs matter.** Replacing C by its entrywise absolute value changes the signed sum on some network.

## What this does not show

- **Whether twisted Fibonacci networks can be approximated.** That is the open question; ticket C gathers evidence.
- **A positive representation where a known scheme applies.** None is excluded by this ticket, beyond the three tools examined.
