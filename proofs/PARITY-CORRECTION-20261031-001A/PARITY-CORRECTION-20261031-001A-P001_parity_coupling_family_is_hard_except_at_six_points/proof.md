# Parity's coupling family is #P-hard except at six points

Status: Proved

Ticket `PARITY-CORRECTION-20261031-001A`, 2026-10-31.

## What this corrects

`MUTUAL-SELECTION-20261031-001B` (lane B of the mutual-selection scan) claimed:

> The whole coupling family f_λ = [1, λ, 1, λ] has Hadamard transform supported on {000, 111} for every λ: 4(λ + 1) and −4(λ − 1).
> It is a generalized equality, affine and polynomial on every graph. So parity's family is easy everywhere.

- **What was right.** The transform of the line weight.
- **What was wrong.** The conclusion. A change of basis acts on both ends of every incidence: the lines' weights become generalized
  equalities, but the points' equalities become even-parity checks. The transformed count is a code weight enumerator, and it is #P-hard
  at most couplings.
- **Who found it.** A peer session flagged the error on 2026-10-31, citing Fan and Cai (2020), Theorem 2.2.
- **Where the dependents are handled.** The statements that relied on the claim are listed in ticket R. Ticket B treats the failing
  systems.

## Dependencies

- **`KNOT-COUPLING-20261031-001` (B, C).** On the knot's spaces (non-2-colourable cubic triple systems), the knot's coupling M_nae(H; λ)
  is #P-hard (Turing) at every complex λ outside {0, 1, −1, −3, ∞}. It is polynomial at those five points.
- **`PLAIN-COUNT-20261031-001A`.** Counting 2-colourings, M_nae(H; 0), of cubic triple systems with Pfaffian incidence graphs is
  #P-hard (Turing).
- **External, used as a cross-check and not needed for the theorem.**
  - Fan and Cai (2020, arXiv 2011.09110): Theorem 2.2 (PDF p. 5), Lemma 4.1 and Lemma 4.2, case 3 (PDF p. 8).
  - Cai, Fan and Liu (2021, arXiv 2110.01173): the same problem for integer and rational values, mixed signs allowed.
- **Affine tractability (λ = ±i).** Classical (Cai–Lu–Xia; Cai–Chen). Here it is also implemented as an explicit polynomial Gauss sum.

## Setting

- **A cubic system H.** It has n points and n lines, with every point on three lines. N is its point–line incidence matrix over GF(2).
- **A signing b in GF(2)^L.** It gives each line the parity of its negated incidences.
- **Parity's coupling.** M(H, b; λ) = Σ_c λ^{m(c)}, where m(c) is the number of lines whose colour sum differs from b_ℓ mod 2. Plain
  systems have b = 0.
- **The knot's coupling.** M_nae(H; λ) = Σ_c λ^{(number of monochromatic lines)}.
- **The codes.** D is the span of the points' line sets (the row space of N), of dimension r. ker N is the set of line sets covering
  every point an even number of times. Parity's law is solvable iff b ∈ D.

## Lemma 1 (what the transform gives)

M(H, b; λ) = 2^{n−r} Σ_{d ∈ b + D} λ^{|d|} = Σ_{s ∈ ker N} (−1)^{b·s} (1 + λ)^{n−|s|} (1 − λ)^{|s|}.

**Proof.**
- **First form.** c ↦ Nᵀc maps onto D with fibres of size 2^{n−r}, and m(c) = |Nᵀc + b|.
- **Second form.** Write each line weight as ((1 + λ) + (1 − λ)(−1)^t)/2, where t is the line's colour sum plus b_ℓ. Expand the product
  over lines and sum over c. The term of a line set s survives iff s covers every point an even number of times. ∎

**In Holant terms.**
- The Hadamard basis change sends the lines' [1, λ, 1, λ] to the generalized equality [4(1 + λ), 0, 0, 4(1 − λ)].
- It sends each point's equality to the even-parity check ¼[1, 0, 1, 0].
- So the transformed problem sums over the code ker N, not over two global states.

**Where lane B went wrong.**
- It transformed the lines only. That implicitly gives a count proportional to (1 + λ)ⁿ + (1 − λ)ⁿ on a connected system.
- This prediction is wrong on every census graph (check 2c).
- Fano: the true count is (1 + λ)⁷ + 7(1 + λ)³(1 − λ)⁴, because ker N is the 8 complements of point pencils.

## Lemma 2 (Fan–Cai applies)

**Their theorem.** Fan–Cai, Theorem 2.2: for nonnegative [x0, x1, x2, x3], Holant([x0, x1, x2, x3] | =3) is #P-hard except in three
cases:
1. the signature is degenerate;
2. x1 = x2 = 0;
3. (x1 = x3 = 0 and x0 = x2), or (x0 = x2 = 0 and x1 = x3).

**The translation.** On the incidence graph, Holant([1, λ, 1, λ] | =3) is exactly M(H, 0; λ): lines carry the line weight, points the
equality.

**The cases at λ ≥ 0.**
- The signature is degenerate iff λ = 1.
- Case 2 never holds.
- Case 3 holds iff λ = 0.

So the count is #P-hard at every real λ > 0 with λ ≠ 1.

**Their proof of this case.** It treats [1, a, 1, a] explicitly (Lemma 4.2, case 3).
- Gadget G4 has two (=3) circles, each joined to all three squares, and one dangling edge per square. Its signature is
  [2 + 2a³, 2a + 2a², 2a + 2a², 2 + 2a³].
- This reduces to [1, a′, a′, 1] with a′ = a/(a² − a + 1), which is hard unless a′ ∈ {0, 1}, i.e. a ∈ {0, 1} (Lemma 4.1).
- Read on cubic systems, G4 is the theta substitution below (check 3b).

**Caveat.** Holant problems are posed on graphs that may have parallel edges. The dichotomy below does not use Fan–Cai and holds on simple
systems.

## Theorem 3 (theta substitution)

**The construction.** θH replaces each line {x, y, z} by three lines {x, u, v}, {y, u, v}, {z, u, v}, with two new points u, v per line.
θH is a cubic system with a simple incidence graph and no repeated lines, and it is connected iff H is.

**The identity.** M(θH, 0; λ) = (2λ(1 + λ))ⁿ M_nae(H; λ′), with λ′ = λ + 1/λ − 1.

**Proof.** Put t = u + v. Each line of H contributes Σ_{u,v} Π_i w(x_i + t) = 2[Π_i w(x_i) + Π_i w(x_i + 1)]:
- 2(1 + λ³) if the line is monochromatic;
- 2(λ + λ²) otherwise.

Their ratio is (1 + λ³)/(λ(1 + λ)) = (λ² − λ + 1)/λ = λ′. ∎

**The even forms.** In the knot's even-form variable, u = (λ′ − 1)/(λ′ + 3) = ((λ − 1)/(λ + 1))². This is the square of the Hadamard
ratio of parity's line weight, so the two even forms are linked by squaring.

## Theorem 4 (dichotomy)

**Statement.** Count M(H, 0; λ) on connected cubic systems with simple incidence graphs and no repeated lines.
- It is polynomial at λ ∈ {0, 1, −1, i, −i, ∞}.
- It is #P-hard (Turing) at every other complex λ.

With signs the hard cases stay hard, since plain systems are a special case, and the six points stay polynomial.

**Proof: the easy points.**
- **λ = 0.** The count is 2^{n−r}[b ∈ D] (Gaussian elimination).
- **λ = ∞.** This is the top coefficient, the weight [0, 1, 0, 1]: 2^{n−r}[b + 1 ∈ D].
- **λ = 1.** The count is 2ⁿ.
- **λ = −1.** The count is 0, since each point meets three factors (−1)^{c_p}.
- **λ = ±i.** [1, ±i, 1, ±i] = (±i)^{x+y+z} (−1)^{xy+xz+yz} is affine. The dual form of Lemma 1 is a quadratic Gauss sum over a basis
  of ker N. It is summed one variable at a time in polynomial time: each step either fixes a linear constraint or adds a quadratic term
  (`parity_lib.gauss_sum`, check 5).

**Proof: hardness.**
1. **The reduction.** For λ ∉ {0, −1} the factor 2λ(1 + λ) is nonzero, so M_nae(H; λ′) reduces to one parity count on θH.
2. **The main case.** If λ′ ∉ {0, 1, −1, −3, ∞}, KNOT-COUPLING says M_nae(·; λ′) is #P-hard on the knot's spaces. θ of a knot's space is a
   simple system without repeated lines.
3. **The exceptional values of λ′** (check 6):
   - λ′ = 1 iff λ = 1;
   - λ′ = −1 iff λ = ±i;
   - λ′ = −3 iff λ = −1;
   - λ′ = ∞ iff λ ∈ {0, ∞};
   - λ′ = 0 iff λ = e^{±iπ/3}.
4. **λ = e^{±iπ/3}.** Here M_nae(·; 0) counts 2-colourings, which is #P-hard on cubic systems with Pfaffian incidence graphs
   (PLAIN-COUNT A). Their θ images are simple, with no repeated lines.
5. **Connectivity.** The count is multiplicative over components, so hardness on all instances gives hardness on connected ones. ∎

**Remarks.**
- The model of computation is that of KNOT-COUPLING: algebraic λ, Turing reductions.
- For real λ > 0 this re-derives Fan–Cai on simple systems. For rational λ it agrees with Cai–Fan–Liu.

## Checks

`check.py` (`result.json`, about 2 s):

| # | Check | Result |
| --- | --- | --- |
| 0–1 | Hash bindings; upstream proofs Proved; lane B's manifest contains the withdrawn sentence. | pass |
| 2a | Symbolic transform of both sides: the lines become [4(1 + λ), 0, 0, 4(1 − λ)], the points ¼[1, 0, 1, 0]. | pass |
| 2b | Lemma 1's two forms against brute-force distributions on all 60 census graphs (n ≤ 8), with four signings each. | 240/240 |
| 2c | Lane B's implicit two-term count is wrong on every census graph. | 60/60 |
| 3a–b | Fan–Cai's exceptional cases at [1, λ, 1, λ]; G4's signature; G4 is the theta substitution; Lemma 4.1's parameter. | pass |
| 4a | The per-line identity and the even-form squaring, symbolically. | pass |
| 4b | θ yields connected simple cubic systems without repeated lines (census, Fano, the 13-point splice). | pass |
| 4c | Theorem 3 exact on 24 hosts (census n ≤ 7, Fano, splice), at λ ∈ {2, 1/3, −2, 5/7, 1 + i, −3/2 + i/2}. | 144/144 |
| 5 | Six easy points on 240 signed systems, with the Gauss sum at ±i; the Gauss sum against brute force on 300 random forms. | pass |
| 6 | The values of λ where λ′ is exceptional, and the zeros of 2λ(1 + λ). | pass |
| 7 | Control: the theta identity fails with λ′ = λ. | pass |

## What this does not establish

- **The failing systems.** Hardness restricted to parity's failing systems is ticket B.
- **Knot claims.** Parity is a knot (K1–K3) with the same standing as any other knot. This ticket is about counting, not about whether
  anything is a knot.
- **Approximate counting.** Not addressed.

## Novelty

- **Real λ > 0.** Fan–Cai (2020).
- **Rational λ.** Cai–Fan–Liu (2021).
- **The theta substitution.** It is Fan–Cai's gadget G4.
- **Complex λ for this family.** It is obtained from the knot's coupling dichotomy, and was not found in the literature checked: the two
  abstracts cover only nonnegative and rational values. A complex-valued dichotomy for Holant(f | =3) may exist beyond what was checked,
  so folklore risk is moderate.

## Reading

- **Two sides, not one.** Parity's decision and count are easy, by linear algebra. Its weighted family is not: through the theta
  substitution it contains the knot's coupling, with the even forms related by squaring.
- **The error, in the owner's terms.** It came from transforming one side of a two-sided relation. A basis change acts on every
  incidence at once.

## Files

- `parity_lib.py`: systems, θ, exact evaluation (variable elimination, over Q and Q(i)), GF(2) codes, and the Gauss sum at ±i.
- `check.py`, `result.json`: the checks.
