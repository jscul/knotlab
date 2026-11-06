# The trisum law

Status: Proved

Ticket `SEYMOUR-COUNT-20261030-001A`, 2026-10-30.

**What it uses:**
- **`THREEFOLD-AMPLITUDE-20261030-001C`:**
  - Theorem 3: a connected cubic signed system that is not colourable has one amplitude, the same at every line (corner independence);
  - Lemma 4: such a system is not colourable iff its signing is Pfaffian, and then it is minimally so.
- **`THREEFOLD-AMPLITUDE-20261030-001A`:**
  - Lemma 1: the Pfaffian signings of a matching covered bipartite graph form one switching class, and switching preserves colouring counts;
  - Lemma 3: the point lemma (context only).
- **External, not replayed:** Plummer's characterization of braces: every matching of size at most two extends to a perfect matching. It
  is used only to see that a brace's square is a nice cycle.

## Why this ticket exists

The knot's three-fold spaces factor into braces. Heawood braces and planar braces have known amplitudes: 5, and Tutte's number. The
remaining braces are non-planar Pfaffian braces, which Robertson, Seymour and Thomas build from smaller ones by *trisums*: three pieces
glued along a common square.

A probe found that every trisum's amplitude is determined by two numbers per piece, in a not-all-equal form. This ticket proves it.

## Standard statement

**Setting.**
- **Squares and pieces.** A *square* is a 4-cycle (c0, c1, c2, c3) with c0, c2 points and c1, c3 lines.
  - A *piece* is a connected cubic signed system containing the square's four edges, with a Pfaffian signing in which the square carries
    an odd number of negated edges. This holds when the square is a nice cycle, as it is in every brace.
  - So a piece is not colourable (`THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4), and has one amplitude ρ.
- **Trisums.** The *trisum* T of three pieces P₁, P₂, P₃ with a common square identifies the squares and deletes the square's four edges.
  Then c0 and c2 each have one incidence into each piece, and c1 and c3 each have one incidence from each piece.
- **Leaning split.** In a piece P, the lines c1 and c3 see c0 and c2. Since the square's sign parity is odd, for any colours of c0 and c2
  exactly one of the two lines sees them equal (Lemma 1). In a colouring of P − c1:
  - c1 sees c0 and c2 equal, so c3 sees them different;
  - the third point u₃ of c3 agrees, as seen by c3, with exactly one of c0 and c2.

  The *leaning split* (α, β) is half the number of colourings of P − c1 in which u₃ agrees with c0, respectively with c2. So α + β = ρ.
  - Switching changes no seen-value comparison, so the split does not depend on the Pfaffian signing chosen.
  - The *split seen from c3*, (α′, β′), is defined the same way from P − c3 and the third point u₁ of c1.
  - *Reversing a piece* means gluing it with c0 and c2 exchanged. That exchanges the roles of α and β.
- **Uniform gauge.** Switch so that the twelve incidences at the square's vertices are positive, and every piece carries the same odd
  pattern of signs on its square edges. Lemma 1 shows this is always possible.

**Results.**
- **Lemma 1 (gauge).**
  - (i) In a piece, exactly one of c1, c3 sees c0 and c2 equal, for every colouring of c0 and c2.
  - (ii) Any three pieces can be put in the uniform gauge.
  - (iii) Their trisum in the uniform gauge is not colourable, hence Pfaffian. Any Pfaffian signing of the same trisum graph is a switching of
    it, so has the same counts.
- **Lemma 2 (support).** Fix the colours of c0 and c2, and let P be a piece of a trisum, with its square edges removed. Count the colourings
  of P's own points that make P's own lines proper. Such a colouring is nonzero only if the square line of P that sees c0 = c2 is improper
  in P, that is, its third point takes the value seen on c0 and c2.
  - The other square line is then automatically proper, and its third point leans to c0 or to c2.
  - The counts are α and β in the case where c1 sees c0 = c2, and α′ and β′ in the case where c3 does.
- **Theorem 3 (the trisum law).** Glue the pieces in the uniform gauge, each with a given orientation, and let (αᵢ, βᵢ) be their splits in
  that orientation. Then the trisum T has, at every line,

  A(T) = ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃.

  That is the number of choices of leanings, weighted by the splits, in which the three leanings are not all equal.
- **Proposition 4 (the other view is swapped).** For every piece, (α′, β′) = (β, α).
- **Proposition 5 (children as weights).** Let a piece P be glued at a square D to two pieces Q and R, in the uniform gauge, and let L be a
  line of P not on D. Then the colourings of the glued system minus L correspond to colourings of P − L in which both of D's lines are
  proper. Each such colouring is weighted by:
  - ρ_Qρ_R − α_Qα_R or ρ_Qρ_R − β_Qβ_R, if P's line d1 sees d0 = d2 and the third point of d3 leans to d0, respectively to d2;
  - ρ_Qρ_R − β_Qβ_R or ρ_Qρ_R − α_Qα_R, if d3 sees d0 = d2 and the third point of d1 leans to d0, respectively to d2.

  The same holds with the count further restricted at another square of P, for instance by a leaning there.

## Nearest known result

- **Trisums.** They are Robertson, Seymour and Thomas's (Annals 1999), in their structure theorem for Pfaffian braces.
- **What is new here** (no overlap found, candidate local delta):
  - the leaning split;
  - the trisum law and its not-all-equal form;
  - the swapped second view;
  - the weights lemma.

## Proof of Lemma 1

- **(i)** c1 sees c0 and c2 equal iff x₀ ⊕ s(c1, c0) = x₂ ⊕ s(c1, c2), and c3 does iff x₀ ⊕ s(c3, c0) = x₂ ⊕ s(c3, c2). The two conditions
  differ by the square's sign parity, which is odd.
- **(ii) Positive incidences.** Switching at a piece's own vertices next to the square makes the twelve incidences at the square's vertices
  positive.
- **(ii) A common square pattern.**
  - Switching at a square vertex, then switching back that vertex's own incidence through its piece-side neighbour, flips the two square
    edges at that vertex.
  - These four moves generate all even changes of the four square signs. So any odd pattern can be turned into any other.
- **(iii) Non-colourable.** In the uniform gauge, take any colours of c0 and c2, say in the case where c1 sees them equal.
  - In each piece, by Lemma 2 the third point of c1 takes the same value v, since the pattern is common.
  - So the shared line c1 sees v, v, v and is improper. The other case is symmetric.
  - Hence T is not colourable, so its signing is Pfaffian (Lemma 4 of `THREEFOLD-AMPLITUDE-20261030-001C`). Pfaffian signings form one
    switching class. ∎

## Proof of Lemma 2

- **Non-vanishing forces the case.** If both square lines were proper, restoring the square edges would colour the piece, which is
  impossible. Exactly one line sees c0 = c2 (Lemma 1), so that line must be improper.
- **The other line.** It sees c0 ≠ c2 and is proper whatever its third point does.
- **The counts.**
  - Restoring the square edges identifies these colourings with colourings of P − c1 (in the case where c1 sees c0 = c2), counted by α and β
    according to the leaning.
  - In the other case they are colourings of P − c3, counted by α′ and β′. ∎

## Proof of Theorem 3

- **Opening at c1.** By corner independence, A(T) = A(T, c1).
  - All three pieces are closed, so Lemma 2 applies to each. Fix the colours of c0 and c2.
- **The case where c1 sees c0 = c2.**
  - Each piece's third point of c1 is forced, but c1 is removed, so this does not matter.
  - Each third point of c3 leans freely, with weights αᵢ and βᵢ.
  - In the uniform gauge a given leaning gives the same value on the shared line c3 for every piece. So c3 is proper iff the leanings are not
    all equal.
  - Summing gives ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃.
- **The case where c3 sees c0 = c2.** Each third point of c3 is forced to the common value, so the shared c3 is improper: no colourings.
- **Halving.** Both colourings of c0 with x₂ fixed by the case contribute alike, and halving gives the amplitude. ∎

## Proof of Proposition 4

- **Both openings.** Opening T at c3 instead gives, by the same argument, A(T) = ρ₁ρ₂ρ₃ − α′₁α′₂α′₃ − β′₁β′₂β′₃. Corner independence makes
  the two expressions equal for every triple of pieces.
- **Three copies of one piece.** α³ + β³ = α′³ + β′³, with α + β = α′ + β′. So the products agree, and {α′, β′} = {α, β}.
- **One piece against a reference.** Take an asymmetric piece P and an asymmetric reference R, with α_R ≠ β_R.
  - If R is swapped and P is not, the trisum P, R, R gives (α_P − β_P)(α_R² − β_R²) = 0. That is a contradiction.
  - So all asymmetric pieces follow one rule. For symmetric pieces the two rules coincide.
- **Which rule.** The 6-prism has (α, β) = (2, 1) and (α′, β′) = (1, 2) (computed). So the rule is the swap. ∎

## Proof of Proposition 5

- **The other two pieces are closed.** Q and R are not opened, so Lemma 2 applies to them at D.
- **The case where d1 sees d0 = d2.**
  - Their third points of d1 are forced to a common value v, so the shared d1 is proper iff P's third point of d1 differs from v. That is,
    iff P's own d1 is proper.
  - The third points of d3 of Q and R lean freely. The shared d3 is proper iff the three leanings are not all equal. Given P's leaning,
    this is ρ_Qρ_R minus the product of Q's and R's weights on that same leaning.
- **The case where d3 sees d0 = d2.** The roles of the lines are exchanged. By Proposition 4, the weights on d1's leanings are (β, α).
- **What remains.** P's own lines are all proper except L, and its colourings with both D-lines proper are exactly its colourings with the
  square edges of D restored. ∎

## What the computation checks

`check.py` (about fifteen seconds):
- **Splits** of the 4- to 10-prisms ((k − 1, 1)) and of the truncated octahedron ((8, 8)), in both orientations, from both lines.
- **Theorem 3:**
  - on all 44 trisums of prisms, 11 triples in 4 orientations, with amplitudes 6 to 52, against direct counts with a Pfaffian signing from
    a minimal map;
  - on 20 random trisums including truncated octahedra.
- **Lemma 2:** boundary tensors inside four trisums each have 8 nonzero entries, carrying the split.
- **Proposition 5:** on seven nested trisums, the weighted count of the host equals the nested trisum's split computed directly.
- **Controls:** neither the product of the amplitudes, nor the unswapped law, nor the sum of the amplitudes gives the trisum's amplitude.

## Reading

- **The knot reappears one level up.** Three non-colourable pieces glued along a square contribute their colourings, each leaning to one of
  the square's two points. The trisum keeps exactly the triples whose leanings are not all equal: the knot's own rule, applied to pieces.
- **What it gives.** Non-planar glue is no harder than its pieces. Its amplitude is determined by two numbers per piece, and a piece glued
  to others sees them only as weights on its own two leanings. Ticket B turns this into a polynomial algorithm.

## Nonclaims

- **Other compositions.** Only trisums are treated; 4-sums and other compositions are not.
- **The swap's base case.** Proposition 4 uses one computed asymmetric piece to decide between the two possible rules.
