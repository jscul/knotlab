# Which listening contacts bind two processes

Status: Proved by hand. The finite claims are checked by exhaustive computation with controls (`check.py`), against
`GROWTH-LAW-20261107-001A`'s generic K1–K3 enumerator and `knotlab check`.

Ticket `PROCESS-CONTACT-20261108-001A`, 2026-11-08.

## Standard statement

- **The setting.** Two rings, A with m cells and B with n cells (m, n ≥ 3), each running an elementary cellular automaton and
  closed on itself. One contact cell c reads cell a_0 of A, cell b_0 of B and possibly itself:
  c(t + 1) = g(a_0(t), c(t), b_0(t)). It feeds nothing back. The whole is one space-time law, with one variable per cell and time
  step. The first row (X for ring A, Y for ring B, and c(0)) is free, and every later value is a function of it.
- **The two-time law.** The contact's value after T steps is c(T) = F(X, Y, c(0)). By `TIME-KNOTS-20261107-001A`'s Theorem 1 the
  knots of the law that contain c(T) and otherwise only first-row cells are c(T) with a minimally decisive set of F of two or more
  cells, and a decisive single cell gives a tie.
- **Binding.** The contact *binds both rings at lag T* when F is nonconstant and every minimally decisive set of F meets both X and
  Y.

The results:

1. **Theorem 1.** These are equivalent: the contact binds both rings at lag T; neither X with c(0) nor Y with c(0) is decisive for
   c(T); forgetting either ring leaves c(T) free over the other ring's first row and c(0); every knot through c(T) and the first row
   meets both rings, and there is no tie.
2. **Theorem 2.** The contact sees each ring only through the set of histories that ring can show at its contact cell.
3. **Theorem 3.** A contact that reads only the two rings, c(t + 1) = g(a_0(t), b_0(t)), binds both rings at lag T exactly when g
   is XOR or XNOR and both rings' contact cells at lag T − 1 depend on their first rows. Its minimally decisive sets are then the
   unions of one minimally decisive set from each ring.
4. **Theorem 4.** A contact law that may read itself binds both rings at lag 1 exactly when it is one of the four parities a + b,
   a + b + 1, a + b + c and a + b + c + 1.
5. **Theorem 5.** For linear rings the contact of Theorem 3 binds at every lag exactly when neither ring polynomial is nilpotent
   modulo X^m − 1. Among the elementary rules this fails only for rules 0 and 255 on every ring, and for rules 60, 102 and 90 and
   their negations on rings of 2^k cells, which forget after 2^k, 2^k and 2^(k−1) steps.

## Nearest known result

- **Canalizing functions.** A Boolean function is canalizing when some value of one input fixes the output (Kauffman, 1969).
  Every two-input function except XOR and XNOR is canalizing. Theorem 3's case analysis is this classical fact.
- **Composition of certificates.** A setting that fixes a composed function f(g_1, …, g_k) of disjoint inputs fixes enough of the
  g_i to make a certificate of f. Composition of certificate complexity is classical (for example Tal, 2013).
- **Linear automata on rings.** Martin, Odlyzko and Wolfram (1984) analyzed additive automata on rings through polynomials
  modulo X^m − 1. Rule 90 on a ring of 2^k cells reaches the zero configuration from every start, which is the nilpotency of
  Theorem 5.
- **Classification.** Known-with-delta. The pieces are classical. The delta is their reading under K1–K3: a contact between two
  processes binds both of them, in the sense of the contact gate's two-sided essentiality and loss under erasure read across time,
  exactly in these cases.

## Setting

- **Rings.** Ring A has cells a_0, …, a_{m−1}, and cell i's neighbours are cells i − 1 and i + 1 modulo m. Its rule f_A gives
  a_i(t + 1) = f_A(a_{i−1}(t), a_i(t), a_{i+1}(t)). The same holds for ring B.
- **The contact.** c(t + 1) = g(a_0(t), c(t), b_0(t)), g a table of eight values indexed by 4a + 2c + b.
- **Histories.** Ring A's *contact history* over T steps is h_A(X) = (a_0(0), …, a_0(T − 1)), and H_A ⊆ {0, 1}^T is the set of all
  of them. G_T(c0, h, k) is the contact's value after iterating g on histories h and k from c(0) = c0.
- **The test.** K1–K3 on allowed states, with erasure as forgetting. Every claim is about the two-time law of c(T), the
  projection of the space-time law on X, Y, c(0) and c(T) (assumption A30 of `docs/ASSUMPTIONS.md`).

## Theorem 1 (binding is two-sided essentiality and loss under erasure)

For T ≥ 1 the following are equivalent.
- (a) The contact binds both rings at lag T.
- (b) Neither X + {c(0)} nor Y + {c(0)} is decisive for c(T).
- (c) The two-time law's projection on Y + {c(0), c(T)} is free, and so is its projection on X + {c(0), c(T)}.
- (d) c(T) is nonconstant, every knot through c(T) and first-row cells meets both X and Y, and no first-row cell is tied to c(T).

*Proof.*
- **Decisiveness is monotone.** A setting that fixes c(T) extends to every superset, so supersets of decisive sets are decisive.
- **(a) ⇔ (b).** If X + {c(0)} contains a decisive set, it contains a minimally decisive one, which misses Y. Conversely, a
  minimally decisive set that misses Y lies in X + {c(0)}, which is then decisive. The empty set lies in X + {c(0)}, so (b) also
  gives that c(T) is nonconstant.
- **(b) ⇔ (c).** The projection on Y + {c(0), c(T)} misses (y, c0, v) exactly when every completion of the setting (y, c0) gives
  c(T) ≠ v, that is, when that full setting of Y + {c(0)} fixes c(T). By monotonicity some full setting fixes c(T) exactly when Y +
  {c(0)} is decisive. Forgetting ring A means projecting it out, at every time, and the later values of ring B and of c are
  functions of the remaining first row, so this projection is what remains.
- **(a) ⇔ (d).** By `TIME-KNOTS-20261107-001A`'s Theorem 1, the minimally decisive sets of two or more cells, with c(T), are the
  knots, and the single ones are ties. A single cell cannot meet both rings. ∎

**Computed (check 1).** On ten ring rules with both rings alike, rings of 3 + 3 and 3 + 4 cells, all 256 contact laws and T = 1 to
3, the readings (b), (d) and (c) agree on all 15,360 maps. Reading (c) is computed by the generic enumerator's freeness test.

## Theorem 2 (the contact sees each ring through its histories)

c(T) = G_T(c(0), h_A(X), h_B(Y)). The contact binds both rings at lag T exactly when:
- for every c0 and every h in H_A, the map k ↦ G_T(c0, h, k) is nonconstant on H_B;
- for every c0 and every k in H_B, the map h ↦ G_T(c0, h, k) is nonconstant on H_A.

So two pairs of rings with the same history sets are bound by the same contact laws.

*Proof.*
- **What c reads.** Its update reads only a_0, b_0 and itself, and nothing reads c. So c(T) depends on the first row only through
  c(0) and the two contact histories.
- **The test.** A full setting of X + {c(0)} fixes c0 and h = h_A(X), while Y still ranges over all of {0, 1}^n, so h_B(Y) ranges
  over all of H_B. So X + {c(0)} is decisive exactly when some (c0, h) makes G_T constant on H_B. Theorem 1 (b) finishes. ∎

**Computed (check 2).** On all 88 rule classes with both rings alike, 3 + 4 cells, all 256 laws and T = 1 to 6, binding read from
the first rows equals binding read from the history sets, on 135,168 maps. The rule classes that share both history sets at T = 4
are bound by exactly the same laws.

## Theorem 3 (a contact that reads only the rings binds exactly when it is a parity)

Let c(t + 1) = g(a_0(t), b_0(t)), g one of the 16 two-input functions, T ≥ 1. Write α = a_0(T − 1), a function of X, and
β = b_0(T − 1), a function of Y. Then c(T) = g(α, β), and:
- the contact binds both rings at lag T exactly when g is XOR or XNOR and α and β are both nonconstant;
- the minimally decisive sets of c(T) are then exactly S_A + S_B, for S_A a minimally decisive set of α and S_B one of β. So its
  knots are S_A + S_B + {c(T)}, with at least three places, and there are no ties.

*Proof.*
- **Parities bind.** Let g be a parity with α and β nonconstant.
  - **Both parts must be fixed.** A setting of S fixes α + β exactly when it fixes both α and β. X and Y are disjoint, so if α
    were left unfixed, two completions on X with different α and one completion on Y would give two values.
  - **The sets.** So S is decisive exactly when S ∩ X is decisive for α and S ∩ Y for β, and the minimally decisive sets are the
    unions S_A + S_B.
  - **Both rings.** α is nonconstant, so the empty set does not decide it and S_A is not empty. Likewise S_B is not empty, so every
    minimally decisive set meets both rings, and c(0), which c(T) ignores, is in none.
- **Nothing else binds.**
  - **A forgetting ring.** If α is constant, c(T) = g(α, β(Y)) depends only on Y, and a full setting of Y decides it. So binding
    needs α and β nonconstant.
  - **A canalizing law.** If g is not a parity it is canalizing: some value v of one input, say the first, fixes g (the 14 cases
    are checked). Since α is nonconstant, some setting of X gives α = v, and that setting decides c(T) inside X. ∎

**Computed (check 3).**
- **Both rings alike.** All 16 laws, all 88 classes, rings of 3 + 4, 4 + 5 and 5 + 5 cells and T = 1 to 8: 33,792 maps, no
  mismatch.
- **Mixed rings.** All 7,744 ordered pairs of classes with five laws (XOR, AND, OR, the first input alone, and the first input
  and not the second), 3 + 4 cells and T = 1 to 6: 232,320 maps, no mismatch.
- **Composition.** Under XOR, the minimally decisive sets equal the unions of the rings' own, with no tie, on every map tested.

## Theorem 4 (binding from the first step needs a parity)

A contact law g(a, c, b) binds both rings at lag 1 exactly when it is one of a + b, a + b + 1, a + b + c and a + b + c + 1 (laws
90, 165, 150 and 105).

*Proof.*
- **The histories at lag 1.** h_A = a_0(0) is a free cell, so H_A = H_B = {0, 1}.
- **The condition.** By Theorem 2, the contact binds exactly when, for each c0, the two-input map (a, b) ↦ g(a, c0, b) is
  nonconstant in b for each a and in a for each b. That is, it is canalizing in neither input, which leaves XOR or XNOR.
- **The four laws.** So g(a, c, b) = a + b + φ(c), with φ one of 0, 1, c and c + 1. ∎

**Computed (check 4).**
- **Lag 1.** Exactly these four of the 256 laws bind at lag 1.
- **Later lags.** With memory, binding can begin later. Iterating the 2^8-state dynamics of 3 + 4 cells until its maps repeat,
  which makes the verdict exact at every lag, some non-parity laws bind at every lag from 2 on for some rule. Check 4's output lists
  them. Between negation rings (rule 51), whose contact cell alternates, a contact sees only two histories per ring, so laws that
  are not parities can act as one.

## Theorem 5 (linear rings stop binding only when they forget)

- **The rule's polynomial.** A linear rule acts on a ring's state S(X) = Σ s_i X^i as multiplication by a polynomial p modulo
  X^m − 1. Over GF(2) the left neighbour is X and the right neighbour X^(−1), so:
  - p = 0 for rule 0, 1 for rule 204, X for rule 240 and X^(−1) for rule 170;
  - p = 1 + X for rule 60, 1 + X^(−1) for rule 102, X + X^(−1) for rule 90, and X^(−1) + 1 + X for rule 150.
  - The negations 255, 51, 15, 85, 195, 153, 165 and 105 add the all-ones state at each step. The contact cell then gains a
    constant, which does not change whether it is constant.
- **The contact cell.** a_0(t) is the parity of the coefficients of p^t mod X^m − 1, reflected, applied to X. It is nonconstant
  exactly when p^t ≢ 0.
- **Binding.** By Theorem 3, the parity contact binds at lag T exactly when p_A^(T−1) ≢ 0 modulo X^m − 1 and p_B^(T−1) ≢ 0
  modulo X^n − 1. It binds at every lag exactly when neither polynomial is nilpotent.
- **Nilpotency.**
  - Write m = 2^k m', with m' odd. Over GF(2), X^m − 1 = (X^(m') − 1)^(2^k), and X^(m') − 1 is squarefree. So p is nilpotent
    exactly when X^(m') − 1 divides p, X being a unit.
  - 1 + X divides X^(m') − 1, and when m' > 1 the quotient 1 + X + … + X^(m'−1) is nonconstant and is not divisible by 1 + X (its
    value at 1 is m', odd). So X^(m') − 1 divides a power of 1 + X only when m' = 1.
  - So rules 60, 102 and 90, whose polynomials are units times (1 + X) or (1 + X)², are nilpotent exactly on rings of 2^k cells.
    Rule 150's polynomial is a unit times 1 + X + X², which 1 + X does not divide, so it is never nilpotent. Units are never
    nilpotent, and 0 always is.
- **The index.** On m = 2^k cells, X^m − 1 = (1 + X)^m. So (1 + X)^t vanishes first at t = m, and (1 + X)^(2t) at t = m / 2. ∎

**Computed (check 5).**
- **Nilpotency.** For all 16 linear and affine rules, the index is as stated on rings of 3 to 16 cells, by exact iteration of p^t
  until it cycles. The radical criterion agrees to 128 cells.
- **Polynomials.** Each polynomial is the rule's one-step action.
- **Simulation.** The parity contact between two such rings binds at lag T exactly when neither p^(T−1) vanishes, on rings of 3
  to 8 cells.

## The canonical check

Check 6 runs `knotlab check` on the CNF of the space-time law. The rings run rule 128 on 3 cells, T = 2, and every cell other
than the three named is a witness.
- **Under XOR.** {a_0(0), b_1(0), c(2)} is a knot: c(2) = AND(X) + AND(Y), and the only excluded setting is (0, 0, 1). It is
  constrained as a whole, free in every part, and not definable by a 2-CNF with witnesses.
- **Under AND.** The same set is not a knot: one ring's zero fixes c(2), a tie.
- **The generic enumerator.** It finds exactly nine knots under XOR, each one cell of each ring with c(2).

## Reading

**Interpretation, not a theorem.**
- **For the program's first emergence.** The contact gate asks for one contact, shared by identity, irreducibly joint,
  two-sided essential, persistent, and lost when either loop is erased. Read across time, with loops as processes and a contact
  that listens to both:
  - irreducibility is a knot through c(T);
  - two-sided essentiality and loss under erasure are one property, binding (Theorem 1);
  - binding is exactly a parity contact (Theorems 3 and 4);
  - persistence asks that neither ring forget at its contact cell (Theorem 5).
- **An XOR of fixed values is a classifier.** The doctrine says that an XOR applied to values fixed elsewhere is a classifier, not
  a contact, because its inputs are not open. A ring that forgets fixes its contact value, and then the parity contact stops
  binding.
- **Each ring's knots, joined.** Under a parity contact, a knot between processes is one knot of each ring, or a tie, joined
  through the contact into one knot.

## Checks

`check.py`, with `process_contact_lib.py`, reproduces `result.json` on the repository's `.venv`.

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | Theorem 1: three readings agree on 15,360 maps | pass |
| 2 | Theorem 2: binding through histories, 135,168 maps; equal histories, equal laws | pass |
| 3 | Theorem 3: parities exactly, rings alike and mixed; composition of decisive sets | pass |
| 4 | Theorem 4: the four lag-1 laws; later binding with memory, exact at every lag | pass |
| 5 | Theorem 5: nilpotency on rings of 3 to 16 cells, radical criterion to 128, simulation | pass |
| 6 | knotlab check and the generic enumerator on the rule-128 example | pass |

## Nonclaims

- **Listening contacts only.** The contact reads the rings and feeds nothing back. Rings that share their contact cell are ticket
  B.
- **Two-time knots only.** Binding is read from the contact's knots with the first row (A30). Knots of the whole space-time law are
  not counted.
- **No physics.** No physical time or dynamics is claimed.
