# Why the parity comes out even

Status: Theorems 1 and 2 proved by hand, their finite claims checked in `check.py`; the six-contact example is an exact reading; the
classification by mechanism is computed (exhaustive to six contacts, sampled from seven to ten).

Ticket `REROUTE-20261109-001A`, 2026-11-09.

## Standard statement

- **Maps and networks.** As in `FLIP-RULE-20261109-001B`: a map on E contacts is a permutation σ of the darts 0 … 2E − 1, the next dart
  counterclockwise at a ring, with α(d) = d xor 1 and contact(d) = d >> 1; rings are the cycles of σ and faces the cycles of σα. As a
  network of equally spaced rule-60 rings with law-(12, 12) contacts, its **contact graph** has an arc contact(d) → contact(σd) for every
  dart d, two out of every contact and two into it, and a contact c **persists** exactly when every count (A^k)_cc of closed walks at c
  is even (`LOOP-NET-20261108-001A`, Theorem 2 (a), at equal spacing). A **flip** at c is an automorphism of the map fixing c and
  exchanging its two rings (Theorem 3 there).
- **Odd arcs.** N is the contact graph mod 2, a 0/1 matrix: an arc a → b survives when exactly one dart of a leads to b.
- **Doubled pair.** Contacts (a, b) with both darts of a leading to b: b follows a on both of their rings, in the same order. Then row a of
  N vanishes.
- **Contact-graph flip.** An automorphism of the contact graph, arcs counted with multiplicity, that fixes c and exchanges the heads of
  its two out-arcs, or the tails of its two in-arcs (neither an arc c → c). A flip of the map induces one.
- **Non-degenerate.** As in `FLIP-RULE-20261109-001B-E002`: every ring and every face has at least three contacts. A contact **sends and
  hears** when some walk from it, and some walk into it, has an odd count.

**Theorem 1 (the criterion).** Over GF(2), c persists exactly when det(I + tN) = det(I + tN₋c), where N₋c deletes c's row and column.
Equivalently, for every m the number of families of disjoint cycles of the odd-arc graph, of total length m, that pass through c is even.

**Theorem 2 (two pairings).** (a) If every closed walk at c leaves the first contact of some doubled pair, equivalently c lies on no
cycle of the odd-arc graph, then exchanging the dart at the first such step is a fixed-point-free involution on closed walks at c of
each length, and c persists. (b) If c has a contact-graph flip, its closed walks of each length split into two equal halves by their first
(or last) arc, and c persists.

**The six-contact example.** `FLIP-RULE-20261109-001B`'s smallest non-degenerate map persistent without a flip, σ = (5, 7, 11, 10, 8, 9,
3, 4, 2, 0, 6, 1) with rings of 3, 3 and 6 contacts and one face, genus 2, has two doubled pairs, contact 1 to 5 and contact 2 to 4, and
every closed walk at its contact 0 passes one: Theorem 2 (a). Its counts 2, 4, 4, 8, 24, 48, … at lengths 3, 4, 5, … pair up that way.

**Computed (check 4).** Persistent contacts that send and hear, by mechanism (a map flip first, then doubled pairs, then a contact-graph
flip, else none found):

| Maps | Read | Map flip | Doubled pairs | Contact-graph flip | None found |
| --- | --- | --- | --- | --- | --- |
| every non-degenerate map, E ≤ 5 | 8,888 maps | 3,840 | 0 | 0 | 0 |
| every non-degenerate map, E = 6 (normalised σ(0) = 2) | 89,472 | 18,432 | 36,864 | 13,824 | 0 |
| random non-degenerate maps, E = 7 | 5,839 | 505 | 2,211 | 838 | 5,438 |
| E = 8 | 4,481 | 123 | 1,359 | 328 | 2,192 |
| E = 9 | 3,469 | 30 | 828 | 145 | 1,437 |
| E = 10 | 2,557 | 5 | 546 | 76 | 951 |

So up to six contacts every persistent contact of a non-degenerate map that sends and hears is explained by a flip, a doubled pair or a
contact-graph flip; from seven contacts on, most are explained by none of them. Among degenerate maps (a ring or face of one or two
contacts) unexplained ones occur already at five.

## Nearest known result

- **Sources.** Cramer's rule and the expansion of det(I + tN) over GF(2) by cycle covers (the permanent mod 2); involutions on closed walks;
  `LOOP-NET-20261108-001A`, Theorem 3, of which Theorem 2 (b) is the contact-graph version.
- **Classification.** Known-with-delta for Theorem 1 (standard linear algebra applied to persistence); new as far as found for the two
  pairings as a reading of persistence and for the classification.

## Proof of Theorem 1

Mod 2, (A^k)_cc = (N^k)_cc, and Σ_k (N^k)_cc t^k is the (c, c) entry of (I + tN)⁻¹ in GF(2)[[t]], which by Cramer's rule is
det(I + tN₋c) / det(I + tN) (signs vanish mod 2). Persistence says the entry is 1, so the two determinants are equal. Over GF(2)
det(I + tN) = Σ_S t^|S| det N[S], and det N[S] is the permanent mod 2, the number of covers of S by disjoint cycles of the odd-arc graph;
the difference of the two determinants counts exactly the covers whose support contains c. Check 2 confirms the criterion on every contact
of every map of up to five contacts, every non-degenerate map of six and the samples to ten (1,977,637 contacts read). ∎

## Proof of Theorem 2

(a) A closed walk at c is a sequence of darts d₁ … d_k with contact(σd_i) = contact(d_{i+1}) and contact(σd_k) = c. If it is at the
first contact a of a doubled pair at step i, both darts of a lead to b, so replacing d_i by d_i xor 1 gives another closed walk; doing it
at the first such step is an involution with no fixed point. Every arc that does not leave such a contact has multiplicity 1 and survives
in N, and the arcs out of such a contact all vanish, so "every closed walk at c passes one" is "c lies on no cycle of N".

(b) (A^k)_cc = (A^(k−1))_{h₀c} + (A^(k−1))_{h₁c}, summing over c's two out-arcs with heads h₀ ≠ h₁; an automorphism π of the contact
graph with π(c) = c and π(h₀) = h₁ carries walks h₀ → c bijectively onto walks h₁ → c, so the two terms are equal. The in-arc version is
the same with the last arc. If an arc c → c is one of them the exchange cannot fix c, which is why such arcs are excluded.

Check 3 confirms both on the same maps: 593,692 contacts are blocked by doubled pairs and 147,534 have a contact-graph flip, and all of
them persist. ∎

## Remarks

- **Arithmetic starts at seven contacts.** `FLIP-RULE-20261109-001` read its smallest non-degenerate example as parity that "just comes
  out even". It does not: two doubled pairs pair its walks, and at six contacts every case has a doubled pair or a symmetry of the contact
  graph. Persistence with no pairing found starts at seven contacts, and there it is the majority. For those, Theorem 1 is the reason: the
  cycle families through the contact cancel in pairs by size, with no pairing of walks found.
- **Doubled pairs are not faces.** `LATTICE-REACH-20261109-001A`, Theorem 1, calls the configuration "two contacts consecutive on a ring
  are also consecutive on the other ring they share" a digon face. On those tori every face keeps the lattice's size (4 on the square, 6
  on the honeycomb; check 5, 57 and 87 tori to index 30), and the configuration is a doubled pair: the two rings run side by side from one
  contact to the next in the same order, which no face does. Its theorem stands as stated; only the name is wrong.
- **Persistence is a fact about the contact graph.** Both pairings, and the criterion, read only the contact graph, which forgets how
  each ring continues through a contact. `REROUTE-20261109-001B` uses that.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The six-contact example: two doubled pairs, every closed walk at contact 0 to length 12 passes one, the exchange is a fixed-point-free involution, no flip of either kind | pass |
| 2 | Theorem 1 on 1,977,637 contacts (every map to five contacts, every non-degenerate map of six, samples to ten) | pass |
| 3 | Theorem 2: every blocked contact (593,692) and every contact with a contact-graph flip (147,534) persists | pass |
| 4 | Computed: the classification above; none found first at seven contacts on non-degenerate maps | pass |
| 5 | `LATTICE-REACH-20261109-001A`'s digon tori to index 30: every face of 4 or 6 sides, and a doubled pair on each | pass: 57 square, 87 honeycomb |

## Nonclaims

- **No pairing is claimed for the unexplained cases** from seven contacts; that none of the three mechanisms applies is computed, and other
  pairings may exist.
- **Shares are of labelled maps**, exhaustive (normalised at six) or sampled, not of isomorphism classes.
- **Two-time knots only** (A30); equally spaced rings only.
