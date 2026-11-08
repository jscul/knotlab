# Bands grow, single rings do not

Status: Proved by hand. The finite claims are checked exactly in `check.py`.

Ticket `GROW-NET-20261108-001A`, 2026-11-08.

## Standard statement

- **Networks.** Rule-60 rings joined by contacts with law (12, 12), as in `LOOP-NET-20261108-001A`, given by a rotation system: each ring
  lists its contacts in cyclic order. Contacts are **equally spaced**, every ring of m contacts having m·g cells (g ≥ 2), so every corner
  has the same weight ω = z a^(g−1) and a contact persists at every lag exactly when every count of returns to it is even
  (`LOOP-NET-20261108-001A`, Theorems 1 and 2). A network is **balanced** when every contact persists. Every ring has at least two
  contacts.
- **Growth.** A growth step changes the rotation system locally. **Attaching a ring** adds a new ring R with m contacts, each shared with
  an existing ring and inserted somewhere in that ring's cyclic order. A **bubble** is the attachment of a two-contact ring at two
  consecutive places of one ring X, between X's consecutive contacts p and q. **Inserting a band** turns the n × m square torus into the
  n × (m + 1) one; **splitting into blocks** turns it into the kn × lm one.

**Theorem 1 (the rectangular tori persist).** For n, m ≥ 3, the half-turn of the n × m torus about the midpoint of any contact is an
orientation-preserving automorphism that fixes the contact and exchanges its two rings. So every contact of every n × m torus of rings
persists at every lag at every ring size, and growth by inserting bands or by splitting every ring into k × l blocks keeps every contact
persistent at every stage.

**Theorem 2 (one ring at a time breaks persistence).** Attach a new ring R to a balanced network.
1. **One contact.** R's only corner runs from its contact c back to c, a return of length 1, so c does not persist.
2. **Two contacts, not a bubble.** The contact c1 joins R, a ring of two contacts, to a ring of at least three contacts, and neither face
   at c1 has two contacts. So exactly one return of length 2 reaches c1, and c1 does not persist (`LOOP-NET-20261108-001A`, Theorem 4).
3. **A bubble.** The two corners from c1 to c2, one on X and one on R, have equal weight and cancel, so c1 receives but sends nothing and
   c2 sends but receives nothing. The other contacts see X's corner p → q deleted, and for each of them
   D′_cc = 1 + ω D_cq D_pc / (1 + ω D_pq), with D the old network's. So the network stays balanced exactly when no old contact c is both
   reached from q and reaches p, an odd number of walks each way at some lengths.

**Remark (where the flip criterion can carry growth).** Networks with a flip at every contact are orientably regular maps, up to the
choice of spacing. On the sphere these are the five Platonic networks, the loops and the two-ring hosohedra; on each surface of genus at
least 2 there are finitely many (Hurwitz's bound). Only the torus has them at every size. Ticket B finds that one-ring growth keeps
persistence only from seeds of at most four rings, and that truncating or rectifying the Platonic networks loses it.

## Nearest known result

- **Maps.** Regular and chiral maps on the torus, {4,4}_(b,c) and their relatives (Coxeter and Moser, ch. 8), and the finiteness of
  regular maps of genus at least 2 (Hurwitz 1893).
- **Linear algebra.** The Sherman–Morrison formula for a rank-one update of an inverse.
- **Classification.** Known-with-delta. The delta is reading growth of a network of persistent contacts through these: bands and blocks
  keep the flips, single rings break the pairing of returns.

## Proof of Theorem 1

Index the rings by Z_n × Z_m with h(p) joining p to p + e1 and v(p) joining p to p + e2, each ring listing E, N, W, S counterclockwise.
The half-turn about the midpoint of h(p) is x ↦ 2p + e1 − x on Z_n × Z_m. It maps the lattice to itself and every horizontal contact to a
horizontal contact, and as a rotation by 180° it preserves the counterclockwise order at every ring, so it is an automorphism of the
rotation system and hence of the contact graph. It fixes h(p) and exchanges p and p + e1. The half-turn x ↦ 2p + e2 − x does the same for
v(p). With n, m ≥ 3 no two contacts join the same pair of rings in parallel. Contacts are equally spaced, so every corner weighs ω and the
automorphism preserves weights. By `LOOP-NET-20261108-001A`, Theorem 3, every contact persists at every lag. Inserting a band and
splitting into blocks both produce rectangular tori with sides at least 3, so every stage persists. ∎

## Proof of Theorem 2

**Part 1.** R has the single contact c, so its only corner leads from c to c: an arc c → c of the contact graph. That is one return of
length 1 (the other ring of c has at least three contacts after the insertion, so its corner from c goes elsewhere). Under equal spacing
D_cc = 1 + N_1(c)ω + ..., and N_1(c) = 1, so c's witnesses lapse at lag g + 1 (`LOOP-NET-20261108-001A`, Theorem 1).

**Part 2.** R has two contacts c1 on X and c2 on Y. X had at least two contacts, so it has at least three. A face at c1 with only two
contacts would consist of c1 and the contact next to it on R or on X, which is c2 only when c2 lies next to c1 on X: a bubble. So
neither face at c1 has two contacts, and by `LOOP-NET-20261108-001A`, Theorem 4, exactly one return of length 2 reaches c1.

**Part 3.** On X the order is p, c1, c2, q (or with c1 and c2 exchanged, which is the same up to names). X's corner from c1 to c2 and R's
corner from c1 to c2 both weigh ω and cancel in K; R's other corner runs c2 → c1, and X's corners run p → c1 and c2 → q. So c1 has no arc
out and c2 no arc in, no closed walk passes through either, and each has even return counts. The old contacts keep every arc except
X's corner p → q, which is gone. In K over the old contacts this adds ω at entry (q, p) over GF(2), and by Sherman–Morrison,
D′ = D + ω (D e_q)(e_p^T D) / (1 + ω D_pq). With D_cc = 1 this gives D′_cc = 1 + ω D_cq D_pc / (1 + ω D_pq). The power series D_cq and D_pc are
nonzero exactly when an odd number of walks of some length lead from q to c and from c to p, and their product vanishes only if one of
them does. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The seeds are balanced: loops of 3 to 5 rings, two rings sharing 3 and 4 contacts, tetrahedron, cube, octahedron, the 3 × 3 torus, the genus-2 network of 16 rings | pass |
| 2 | Theorem 1: every n × m torus with 3 ≤ n ≤ 8 and 3 ≤ m ≤ 12 has a half-turn at every contact and is balanced | pass: 60 tori |
| 3 | Theorem 1: growth by bands (3 × 3 to 3 × 12, 4 × 4 to 4 × 12) and by blocks (3 × 3 to 6 × 6, 9 × 9, 12 × 12; 4 × 4 to 8 × 8 and 12 × 12) balanced at every stage | pass: 26 stages |
| 4 | Theorem 2, part 1: every one-contact attachment on every seed has its return of length 1 and is unbalanced | pass: 182 attachments |
| 5 | Theorem 2, part 2: every two-contact attachment that is not a bubble has an odd number of returns of length 2 at its first contact and is unbalanced | pass: 2,588 attachments |
| 6 | Theorem 2, part 3: every bubble on every seed is balanced exactly when no old contact is reached from q and reaches p | pass: 182 bubbles, none balanced |
| 7 | Theorem 2, part 3, exact over GF(2)(z): D′_cc = 1 + ω D_cq D_pc / (1 + ω D_pq) for every old contact, on six bubbles | pass |
| 8 | Cell level, exact: the contact predicted to fail loses a witness at some lag (bubbles on a loop and the tetrahedron, two-contact attachments on the tetrahedron and the 3 × 3 torus) | pass: first lapses at lags 5 and 7 |

## Nonclaims

- **Equally spaced networks**, law (12, 12) and rule-60 rings; other spacings change the weights and are not covered.
- **One growth step** for Theorem 2; Theorem 1 covers every stage of band and block growth.
- **The networks are given a surface.** Growth here never changes the surface; growing a surface is not addressed.
- **No distance.** **Two-time knots only** (A30).
