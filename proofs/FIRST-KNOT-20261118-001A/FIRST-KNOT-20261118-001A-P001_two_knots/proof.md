# Two first knots under one count and under the fewest counts

## Standard statement

For the complete-round joining policy on even-parity constraints, a start of constraints whose neighbour graph is a matching grows
as independent pieces, one per start constraint, each the growth of a single seed with that constraint's loose variables. Hence a
constant count c survives exactly when every start constraint has 0, 1 or c loose variables, and the least count rule closes separate
seeds but grows two copies of the quadrant ℕ² from two seeds sharing one variable, for every pair of arities; the arities themselves
never enter.

## Nearest known result

`FRESH-COUNT-20261118-001A` (one seed: the descent order, the uniform count forced to the seed's size, the fewest counts closing the
seed), which this extends to starts of two knots.
[Proof](../../FRESH-COUNT-20261118-001A/FRESH-COUNT-20261118-001A-P001_free_count/proof.md) ·
[design](../../../research/FIRST-KNOT-20261118-001/preregistration.md).

## 0. Setting

As in `FRESH-COUNT-20261118-001A` §0: junctions (even-parity knots), loose and shared distinctions, the complete-round joining rule
with groups of any size, offshoots, demand, count rules. A **start** is a set of junctions forming round 0. A start junction's
**open distinctions** are its loose ones. Old allowed states are kept: a count of 0 only where the new junction's parity is implied
by the old equations, tested here by elimination over GF(2), since a start may have several components. The **fewest** rule gives
0 fresh distinctions where the demand is 0 and the parity is implied, and otherwise max(d, 3 − p, 1). Counts are at least 2, so that
every offshoot holds at least three distinctions (the program's smallest knot).

## 1. Pieces (S1)

**Lemma 1.** Let the start be junctions J_1, …, J_m no two of which have a common neighbour (the neighbour graph of the start is
a matching: lone knots and touching pairs, sharing any number of distinctions). Call the **piece** of J_i the junctions
descending from J_i. Then no junction outside the start has parents in two pieces, and the growth of each piece, including every
group, demand and stall, is exactly the growth from a single seed on ℓ_i = (open distinctions of J_i) distinctions, except that the
implied-parity test reads the whole pattern.

*Proof.* The start junctions are live only in round 1: they give all their open distinctions then. In round 1 the live junctions are the start junctions; two of them are candidates only through a common neighbour, which
there is none of, so every open distinction becomes an offshoot of its own start junction. Suppose that up to round t every non-start
junction lies in exactly one piece. A live junction of round t ≥ 1 has as neighbours only its parents (its own distinctions are
loose), all in its piece, or, in round 1, its start junction. Two live junctions of different pieces would need a common neighbour,
which would lie in both pieces or be a start junction that is a parent of both, and a start junction's children are in its own
piece. So all candidates, groups and new junctions stay within pieces. Inside a piece, the start junction's shared distinctions take
no part: they are never loose, so the start junction contributes only its ℓ_i open distinctions, exactly as a seed on ℓ_i
distinctions would. ∎

Two knots placed apart, or sharing any number of distinctions, satisfy the hypothesis (two junctions sharing distinctions are
neighbours of each other, not neighbours in common). The growth sees only each start junction's number of open distinctions ℓ,
never its size (the advisor's formulation).

## 2. One count (S2)

**Theorem 2.** Under the hypothesis of Lemma 1 and one count c ≥ 2 for every join (the floor: an offshoot holds at least three
distinctions), the growth runs every round exactly when every start junction has ℓ ∈ {0, 1, c} open distinctions. Otherwise it stalls
at the earliest of the rounds r(ℓ, c) over its start junctions: 2 if c ≤ ℓ − 2; 4 if c = ℓ − 1 and ℓ ≥ 3; 3 if c ≥ ℓ + 1 and ℓ ≥ 2.
When it runs, each start junction with ℓ = c is a copy of the c-fold counting pattern (the literature's orthant ℕ^c), with
C(t + c − 1, c − 1) junctions in round t ≥ 1, and each with ℓ = 1 is one offshoot in round 1 followed by a copy of ℕ^c one round
late.

*Proof.* By Lemma 1 each piece is a single seed on ℓ distinctions. By `FRESH-COUNT-20261118-001A` Theorem 2, a seed on ℓ ≥ 3
distinctions runs under one count exactly when c = ℓ and otherwise stalls at round 2, 3 or 4 as stated. Its proof covers ℓ = 2:
round 1 makes two offshoots of demand 1; with s = c − 1 surplus distinctions each, the round-2 pair has demand 2s and needs
2s ≤ c = 1 + s, so s ≤ 1; c = 2 gives ℕ², and c ≥ 3 stalls at round 3. A seed on one distinction makes one offshoot of demand 0,
which takes c fresh distinctions and from then on is a seed on c distinctions, so it runs for every c. A seed on none makes nothing.
The whole runs exactly when every piece does. ∎

**Two first knots of a and b places** (3 ≤ a ≤ b), sharing s distinctions, have ℓ = a − s and b − s.
- Apart (s = 0): they grow together exactly when c = a = b.
- Sharing one: exactly when c = a − 1 = b − 1.
- In general the condition is on open counts, not sizes. A three-place and a four-place knot sharing two distinctions (ℓ = 1, 2) grow
  together at c = 2; knots of a < b places sharing a − 1 distinctions grow together at c = b − a + 1.
- So the coordinator's first step has a definite answer. A three-place and a four-place first knot, apart or sharing one
  distinction, cannot grow under one count at all, and neither wins. Under one count nothing about a knot's size matters, only how
  many of its distinctions are open.

**Corollary 2.1 (presentations).** The four-place parity knot on x_1, …, x_4 is the projection of two three-place knots
A: x_1 + x_2 + h = 0 and B: h + x_3 + x_4 = 0 sharing a distinction h that is forgotten. As one junction it grows only at c = 4, into
ℕ⁴. As A and B it grows only at c = 2, into two copies of ℕ². As A and A + B (the same distinctions and the same allowed states as A
and B, ℓ = 1 and 2) it grows only at c = 2, with one copy of ℕ² a round late. The growth is a property of the presentation, the
chosen junctions, not of the relation that the knot test reads. A first knot's size is not defined for the growth until a
presentation is fixed.

## 3. The fewest counts for two first knots (S3)

**Lemma 3 (the advisor's form of Lemma 0).** A new junction of demand 0 has implied parity exactly when its old distinctions are all
the loose distinctions of its component of the old pattern. *Proof.* A set of old equations sums to its cut. If the cut equals the
new junction's old distinctions, the set contains the junctions those distinctions leave, and, since a cut made only of loose
distinctions avoids every shared one, it is a union of components; its cut is all their loose distinctions. ∎

**Theorem 3.** Let the start be knots of a and b ≥ 3 places. Apart, the fewest counts close each into its 2^a and 2^b patterns
and stop. Sharing one distinction h, they grow forever, and each piece makes exactly these junctions in round t ≥ 1:
- a piece with ℓ = 2 open distinctions (a three-place knot): t + 1;
- a piece with ℓ ≥ 3: C(ℓ, t) for t ≤ ℓ, then 1 at t = ℓ + 1, then t − ℓ for t ≥ ℓ + 2.

Every piece ends as a copy of ℕ² (after the 2^ℓ pattern when ℓ ≥ 3), whatever a and b are. In each piece with ℓ ≥ 3, the top's one
fresh distinction equals h in every allowed state.

*Proof.* Apart: each component is a single seed whose top takes every loose distinction of its component, so by Lemma 3 its parity is
implied, and `FRESH-COUNT-20261118-001A` Theorem 4(a) applies to each.

Sharing one distinction, by Lemma 1 the pieces are single seeds on ℓ = a − 1 and b − 1.
- *ℓ = 2.* The two offshoots have demand 1 (each other). The fewest rule gives each max(1, 3 − 1, 1) = 2 fresh distinctions, one
  surplus, and by `FRESH-COUNT-20261118-001A` Theorem 4(b) each starts a chain that never ends: ℕ², t + 1 junctions in round t.
- *ℓ ≥ 3.* As in Theorem 4(a) there, every junction below the top has demand at least 1 and at least three distinctions, so no surplus
  is given: C(ℓ, t) junctions in round t ≤ ℓ. The top, formed at round ℓ, has demand 0. The old pattern is one component (the pieces
  are joined through h), and in that round the other piece holds loose distinctions too (it either grows forever or, if a = b,
  forms its own top in the same round), so by Lemma 3 the top's parity is not implied. The rule gives it max(0, 3 − p, 1) = 1 fresh
  distinction u. The piece's equations, with its start knot, sum to the top's old distinctions plus h, so u = h in every allowed
  state: the 2^ℓ pattern relays h. Next round u makes a lone offshoot U, whose only neighbour is the top; its demand is 0 and, by the
  same argument, its parity is not implied, so it gets max(0, 3 − 1, 1) = 2 fresh distinctions (one junction at t = ℓ + 1). Their two
  offshoots have demand 1 and continue forever, a copy of ℕ² with t − ℓ junctions in round t ≥ ℓ + 2. If a = b, neither top is
  implied alone though their sum is, and each follows this path. ∎

So the fewest counts grow two touching knots two-dimensionally for every pair of sizes, and every one-distinction touch reduces to
the three-and-three case through the relay. **The two is the rule's floor, not a finding.** Surplus arises only from the floor terms
(3 − p and 1), that is only at demand at most 1; with a floor of m distinctions per junction in place of three, the lone offshoot
would get m − 1 fresh distinctions and the tail would change with m (ticket B's control, floors 2 and 4). The fewest rule writes the
knot's smallest size into its floor, and touching knots then grow in 3 − 1 = 2 dimensions.

## 3b. Mutually touching knots under the fewest counts (added after the census)

Ticket B's Q4 failed on the ring of three four-place knots, which the fewest counts grow three-dimensionally. This section, written
after the read-out, explains it.

**Proposition 4.** Let m ≥ 3 knots of m + 1 places touch pairwise, each pair sharing one distinction of its own (so each knot has
m − 1 shared and 2 open distinctions). Under the fewest counts the growth runs forever and, from round 2 on, is the crossed start of
`FRESH-COUNT-20261118-001A` Theorem 4(c) with a = m: m chains of offshoots that never end, and the junctions up to round t grow like
t^m.

*Proof.* In round 1 every start knot is live. Two of them have the other m − 2 as common neighbours, so all pairs are candidates. A
set of at least three of them that misses some knot R_k has R_k as a common neighbour, and the whole set has none, so the only
group is the whole set: one junction T taking one distinction from each knot. Each knot's other open distinction becomes an offshoot
c_i. Next round the live junctions are T and the c_i. Each c_i has the single neighbour R_i, whose live children are T and c_i, so its
only candidate is T and its demand is 1; the fewest rule gives it max(1, 3 − 1, 1) = 2, one surplus, and by
`FRESH-COUNT-20261118-001A` Theorem 4(b) its chain never ends. T has demand m. From round 2 on, candidates are read only through
junctions of round 1 or later, whose neighbour pattern is that of the crossed start at its round a = m (its top and its m offshoots
above the level-(a − 1) junctions), so the growth from there is the crossed growth, whose ideal count grows like t^m. ∎ (Computed
for m = 3, 4, 5: the per-round counts match the crossed start's exactly through 14 rounds. Three mutually touching knots of five
places, or four of four, close instead: the single group then takes every open distinction or leaves offshoots of demand two.)

So the fewest counts single out no number either: two touching knots give two, and m mutually touching knots of m + 1 places give
m. The number is the start's arrangement.

## 4. Cheapness (S4)

Each junction of a one-count growth adds c fresh distinctions under one parity, so it multiplies the allowed states by 2^(c − 1)
(`FRESH-COUNT-20261118-001A` Corollary 2.1): least at the least admissible count. For a lone first knot that is a = 3; for touching
knots it is c = 2, two smallest knots sharing a distinction. Cheapness prefers small, but only through the floor of three places.

## 5. What this answers

- **Nothing in the parity law or the joining rule prefers the smallest first knot.** The law accepts parity knots of every size; the
  rule never sees a size, only how many of a knot's distinctions are open (Lemma 1). Under one count a three-place and a four-place
  first knot, apart or sharing one distinction, cannot grow at all, and neither wins (Theorem 2).
- **What does fix the three of a lone knot.** The foundation's first emergence is two native recurrences joined by one contact: a
  relation on two loops' distinctions and the contact, three variables, whose parity form is the three-place knot with three open
  distinctions (A2). That is a definition of the foundation, not a consequence of the law (a reading).
- **Touching lowers the count, and the fewest counts give whatever the arrangement holds.** Two touching knots of any sizes grow
  two-dimensionally (Theorem 3, through the floor of three places less the shared distinction); m mutually touching knots of m + 1
  places grow m-dimensionally (Proposition 4).
- **The growth belongs to the presentation.** The same relation grows four- or two-dimensionally depending on the chosen junctions
  (Corollary 2.1).

## Verification and evidence

Ticket B (`experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/`) replays Theorems 2 and 3 on every pair
of sizes three to six, apart and sharing one or two distinctions, counts 2 to 8, and on small starts of up to four knots, with the
floor control. Written by the thread before the census and corrected after the advisor (Fable 5.2), who found that the first form of
Theorem 2 ("different sizes never grow together") was false beyond one shared distinction and repaired the proof of Theorem 3. No
independent referee verdict yet.
