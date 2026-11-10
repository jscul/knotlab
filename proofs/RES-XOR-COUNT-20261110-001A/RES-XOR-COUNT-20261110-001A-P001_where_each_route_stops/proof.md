# Where each Res(⊕) route to the sphere's count stops

Status: Proved by hand. Lemmas 1, 3 and 4 are elementary and checked in `check.py`; Lemma 2 rests on Beame et al.'s separations.

Ticket `RES-XOR-COUNT-20261110-001A`, 2026-11-10. The routes and what counts as a transfer were frozen first, in
`research/RES-XOR-COUNT-20261110-001/transfer_statement.md` (commit 2cb5de1ad).

## Standard statement

- **The count.** NAE(K_k), n = 4k² points, two 3-clauses per line (`COUNT-NOTE-20261107-001`).
- **Res(⊕).** Lines are disjunctions of F2-linear equations; regular, depth-restricted and dag-like refutations as in the literature.
  Substituting an F2-affine form for each variable turns a Res(⊕) refutation into one of the same size and shape.
- **Polynomial calculus (PC)** over F2, standard rule: a line of degree at most D − 1 may be multiplied by a variable, every line has
  degree at most D (Braun's convention, §2 of arXiv 2609.23015).
- **Braun's generic criterion** (Theorem 9.1 of arXiv 2609.23015). For a set of linear clauses in v variables, a covering family of
  linear clauses A_j (j ∈ J) of width at most w, a polynomial system F containing the Boolean equations and the A_j's clause
  polynomials, integers h, k ≥ 1 with h(k + 1) + 1 ≤ v, D = max(2h + w, 4h + 1) and B = k(D + 1), and a space U of polynomials of degree
  at most k with U ∩ Cons_B(F) = {0}: every Res(⊕) refutation with S nodes has dim U ≤ (3S + |J|)·C(v − h(k + 1) − 1 + k, k).

**Theorem.** None of the four routes of the frozen statement yields a transfer of a regular, depth-restricted or dag-like Res(⊕) size
bound to the count. R2 cannot; R1, R3 and R4 stop at steps that no known result supplies:
- **R2 (Braun's criterion)** certifies at most a constant number of nodes for the count (Lemmas 1 and 5);
- **R1 (the bit pigeonhole family)** needs a reduction from PIGEON to the count in which every point is one parity; for bit PHP no
  reduction by ordinary decision trees of polylogarithmic depth exists, and none by parities is known (Lemma 2);
- **R3 (lifted formulas)** enter the count only through points that are not affine, because no stifling gadget is affine (Lemma 3);
- **R4 (the count's xor-lift)** is the count again under affine maps (Lemma 4).

## Nearest known result

- **Braun's Remark 9.3** says that no formula other than bit PHP is known to have a separated space of useful density, and his
  Remark 9.4 notes that a system deriving one at low degree, as for Tseitin formulas, has no separated space at higher degree. Lemma 1
  is a quantitative form of that remark from the criterion's own parameters: a refutation of degree d caps the criterion at
  exp(d²/(6v)).
- **Beame, Cook, Edmonds, Impagliazzo and Pitassi** (*JCSS* 57, 1998) proved every black-box separation among PPA, PPAD, PPADS and PPP
  (as summarized by Göös et al., *J. ACM* 2024), PPP ⊄ PPADS among them.
- **Stifling** (Chattopadhyay, Mande, Sanyal and Sherif, ITCS 2023) and the lifting theorems for Res(⊕) that use it (Alekseev and
  Itsykson, ECCC TR24-128: Maj_3 lifts resolution width to Res(⊕)-rank, and Maj_5 with mixing lifts resolution depth to exponential
  regular Res(⊕) size; Bhattacharya, Chattopadhyay and Dvořák, CCC 2024).
- **Classification.** Lemma 1 is new as far as found, and elementary. Lemmas 2 to 4 are routine. The delta is the obstruction map for
  this formula.

## Proof

**Lemma 1 (the criterion is capped by degree).** Let F have a PC refutation of degree d ≤ 2v/3. Then for every admissible h, k, w and
every U ≠ {0} separated at degree B, the criterion's inequality gives no more than 3S + |J| ≥ exp(d²/(6v)), and its density form no
more than exp(d²/(36v)).
- If B ≥ d then 1 ∈ Cons_B(F), and every polynomial q of degree at most B is derived from it (Braun's lemma on multiplying a completed line, §2), so U ⊆ Cons_B(F)
  forces U = {0}. Hence B < d, and since D + 1 ≥ 4h + 2, k < d/(4h + 2).
- Put r = h(k + 1) + 1 ≤ 3hk. Then hk < d/4, so r < 3d/4 ≤ v/2. The best the inequality can give, with dim U ≤ C(v + k, k), is
  C(v + k, k)/C(v − r + k, k) = Π_{j ≤ k} (1 + r/(v − r + j)) ≤ exp(kr/(v − r)) ≤ exp(2kr/v) ≤ exp(6hk²/v).
- And hk² < h d²/(4h + 2)² ≤ d²/36 for h ≥ 1. So the bound is at most exp(d²/(6v)); the density form's exponent hk²/(v + k) is below
  d²/(36v). ∎

Check 1 confirms both on 27,255 admissible parameter choices (v from 60 to 5,000): the largest ratios to the caps are 0.37 and 0.98.

**Lemma 5 (the count's degree ceiling).** F2 PC simulates resolution of width W in degree W + 1: for a resolution step from C ∨ x and
C′ ∨ ¬x, multiply J_{C∨x} = J_C(1 − x) and J_{C′∨¬x} = J_{C′}x by the missing literal factors of the resolvent, one variable at a time,
and add; every line has degree at most |C ∪ C′| + 1. The count's resolution width is O(k) (`SPHERE-WIDTH-20261107-001A`, by treewidth),
so its PC degree d_count is O(√n). A system F that Braun's criterion admits for the count contains the clause polynomials of a
covering family A_j of width w, and these derive the count's own in degree w + 3 (J_C = J_C·J_{A_j} when A_j implies C), so F has a
refutation of degree d_F ≤ max(d_count, w + 3). If d_F ≤ w + 3 then B ≥ k(2h + w + 1) ≥ w + 3 ≥ d_F and U = {0}. Otherwise
d_F ≤ d_count = O(√n) ≤ 2n/3 and Lemma 1 caps the criterion at exp(d_count²/(6n)) = exp(O(1)). So **R2 stops**: Braun's criterion cannot certify more than a constant number of nodes for the count. On K_2 (check 3):
resolution width 4, PC degree 3.

**Lemma 2 (R1).** A T1 transfer from bit PHP, its weak form or bit-colouring (`HOLE-CRITERION-COLOURING-20261019-001B`) to the count
sends each point to an F2-affine form, one parity query, and decodes each violated line by a small Res(⊕) derivation, a search that
walks down the derivation reading parities; it is a reduction of the source's search problem (PIGEON for bit PHP) to the count in a
parity model. For bit PHP, with ordinary decision trees of polylogarithmic depth no such reduction exists, since the count is in
PPADS^dt (`COUNT-TFNP-20261107-001B`) and PIGEON is not (PPP^dt ⊄ PPADS^dt, Beame et al. 1998). A single parity may read polynomially
many bits, so that separation does not reach the parity model, and no reduction from PIGEON to SINK or Sperner by parities is known;
the weak and colouring forms are not settled here. So **R1 stops** at that reduction, which would itself be a new reduction between
TFNP classes.

**Lemma 3 (R3).** A gadget g on m bits is 1-stifled if for every position i and value b some setting of the other bits makes g = b
whatever bit i is. An affine g = c ⊕ ⊕_{i∈T} x_i is not: if T is empty g is constant and misses one value; if i ∈ T, every setting of
the other bits leaves g depending on x_i. ∎ (Check 2: none of the 65,812 functions on at most 4 bits is both; Maj_3 is 1-stifled and
Maj_5 2-stifled.) The lifted sources F∘g of the Res(⊕) lifting theorems use stifled gadgets, and the only reductions of their search
problems to the count go through F's reduction, which makes each point a function of gadget outputs; with g not affine the points are
not affine, and no other reduction is known. So **R3 stops** at affineness. What the lifting theorems do give is a bound for the
lifted count, not the count: by Alekseev and Itsykson, the count composed with Maj_3 needs Res(⊕)-rank at least its resolution width,
Ω(√n), and their mixing with Maj_5 turns the count, of resolution depth Ω(√n), into a formula that needs exponential regular Res(⊕)
size. Neither is a transfer under the frozen statement.

**Lemma 4 (R4).** Let count∘⊕ replace each point y_p by the parity of a block of b fresh variables. Substituting y_p = ⊕ block sends a
refutation of the count to one of count∘⊕, and setting all but one variable of each block to 0 sends a refutation of count∘⊕ to one of
the count, both affine and size-preserving. So the xor-lift has the count's Res(⊕) complexity and is no new source; **R4 stops**
there. ∎

## Remarks

- **Why the degree route is closed.** The count is hard for algebra only up to degree √n: its contradiction has a refutation of
  degree O(√n) along a tree decomposition of the sphere, and every degree-based method for Res(⊕) size, Braun's included, needs degree
  above √(v log v) to say anything superpolynomial (Lemma 1). Res(⊕) size for the count is at most 2^{O(√n)} (resolution's), so any
  bound must come from a method that does not pass through degree.
- **The count as a pigeonhole principle over corner parities.** In the corner agreements e_c = 1 + y_a + y_b, which are F2-linear, each
  face has at least one agreeing corner and each line at most one (every corner lies on one face and one line), and there are two more
  faces than lines: a graph pigeonhole principle on the face–line incidence graph whose edge variables are parities. Res(⊕) works
  directly with such parities, which is why the count resembles unary pigeonhole principles, for which no dag-like Res(⊕) bound is
  known (Braun's §9: his bound does not transfer to unary PHP). This is a reading, not a reduction.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Lemma 1 on 27,255 admissible parameter choices, v from 60 to 5,000, d ≤ 2v/3 | pass: largest ratios 0.37 and 0.98 to the caps |
| 2 | Lemma 3 on every function of at most 4 bits; Maj_3 and Maj_5 | pass: 60 affine, none 1-stifled |
| 3 | Lemma 5 on K_2: resolution width 4 (not 3), PC degree 3 | pass |

## Nonclaims

- **No impossibility of a transfer** is claimed for R1 or R3: each route stops at a step that no known result supplies.
- **No upper bound for Res(⊕)** on the count beyond resolution's 2^{O(√n)} is claimed, and no lower bound beyond tree-like.
- **The lifted-count statements** restate Alekseev and Itsykson's theorems for this formula; their exact exponents are theirs.
