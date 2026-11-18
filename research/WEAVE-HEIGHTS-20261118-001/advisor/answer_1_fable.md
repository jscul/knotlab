<!-- modelUsage: claude-fable-5-2 -->

**Verdict:** I found no wrong step in the chain Lemma 0 → Theorem 7 or in Lemma 8. The one statement I would not let stand is the unnumbered remark after Lemma 8. The rest are small gaps and citation tightening.

## 1. Lemma 0: complete, with small additions
- **Fan or wheel:** this needs one line. Two distinct knots at v that share a pair share a pair containing v, so "connected through double meetings" means a connected subset of the 6-cycle of knots around v.
- **Embedding:** say explicitly that (V, E, T) is a subcomplex of the lattice triangulation, so the union of knots is its geometric realisation. "Simply connected" is later used for the complex.
- **One boundary curve and flagness:** both are correct. Flagness uses that three pairwise adjacent lattice points are the corners of a lattice knot; state it.
- **Convention:** s(x, x) = 0 conflicts with "number of knots of a least chain" (which gives 1). Fix the convention.

## 2. Lemmas 1 and 2: correct
- **Lemma 1:** the cochain argument and the mod 2 / mod 3 bookkeeping check out. State that values lie in {0, 1} and that G is connected.
- **Lemma 2:** (iii) needs D finite, so G connected. Either state the lemma for discs or add that hypothesis.

## 3. Proposition 3: correct
- **Parity bookkeeping:** I checked each piece.
  - aᵢ ≡ 0 (mod 3).
  - The floor identity holds, including for negative aᵢ (aᵢ = −3 gives −1).
  - Σεᵢ ≡ Σ/3 (mod 2).
  - Changing σ(sᵢ) flips εᵢ and εᵢ₋₁, also when m = 2.
  - Adjacent double flips reach every vector of the fixed parity.
  - Both case analyses are right.
- **m = 2 exclusion:** correct. D(s, t) + D(t, s) is positive and ≡ 0 (mod 3), so it is at least 3.
- **Missing sentence:** the reduction "σ occurs iff g exists" should say that it uses Lemma 1 (extension ⇔ height function with h ≡ r mod 6 on S), then Lemma 2(ii) for necessity and 2(iii) for sufficiency.
- **Loops:** say the digraph has no loops, so there is no m = 1 cycle.
- **Notation:** Σ is used both as a number and as the summation sign. Rename the number.
- **Corollary 4:** "every proper subset of a bond is free" is not the definition, which only covers (|S|−1)-subsets. Add "subsets of free sets are free". "The case m ≤ 2 of Proposition 3" should read "Proposition 3 requires three distinct members".

## 4. Lemma 5: correct, but hypotheses need verifying in the text
The cited facts are right as stated, and the argument is sound: a′ and b′ are distinct and non-adjacent (for a = (0,0), b = (1,0), c = (0,1) they are (1,1) and (−1,1)), and t = 1 is covered.

Before invoking Chepoi, the text must establish three things it currently skips:
- **No 4-clique:** G has none, so the clique complex is 2-dimensional and equals (V, E, T) by Lemma 0.
- **Link is induced:** the link of v is the induced graph on its neighbours, and two neighbours of v are adjacent in G only if they form a knot of T with v (Lemma 0).
- **5-fan case:** without flagness, the two end neighbours could be adjacent through the outer knot, closing an induced 6-cycle that is not a wheel. That is harmless for the 4-/5-cycle condition but contradicts "path". Say flagness is what excludes it.

References, from memory with no lookup, so verify theorem numbers before freezing:
- **Characterisation:** Chepoi, "Graphs of some CAT(0) complexes", Adv. Appl. Math. 24 (2000), 125–179, Theorem 8.1 as I recall. It says bridged ⇔ flag, simply connected, links without induced 4- or 5-cycles.
- **Independent second source:** Januszkiewicz and Świątkowski, "Simplicial nonpositive curvature", Publ. Math. IHÉS 104 (2006). It gives locally 6-large and simply connected ⇒ systolic, and convexity of balls (§7).
- **Convex balls:** Farber and Jamison, "On local convexity in graphs", Discrete Math. 66 (1987), 231–247. Also Soltan and Chepoi, Cybernetics 19 (1983), 750–756.
- **Triangle condition:** Chepoi 1989 (Metody Diskret. Analiz. 49, in Russian) is hard to obtain. Cite instead Chalopin, Chepoi, Hirai and Osajda, "Weakly modular graphs and nonpositive curvature", Mem. AMS 268 (2020), which states that bridged graphs are the weakly modular graphs without induced C₄ and C₅.

I do not have a self-contained proof that I have verified and that is shorter than reproving these results. I would keep the citations and have ticket B check "no level knot" exhaustively on the census discs as corroboration.

## 5. Lemma 6, Theorem 7, Lemma 8
- **Lemma 6:** correct, in both directions.
- **Theorem 7:** correct. It needs x ≠ y stated. It actually proves that every bond holding x and y has at least s(x, y) + 2 members, so "least" is unnecessary. State the convention for b when no bond holds the pair.
- **Lemma 8:** correct, but "lone distinction" is never defined (presumably: lies in exactly one knot of T). The proof uses D(s, x) = min over neighbours n of D(s, n) + w(n → x), valid for s ≠ x; say so.
- **Remark after Lemma 8: wrong as written.** A bond through x need not contain u or v, so "x sits between v and u in the cyclic order" is unjustified. "The cyclic order" also presumes uniqueness, which Corollary 4 does not give.
  - What Lemma 8 does give: if x sits between s and t, its contribution is D(s, x) + D(x, t) = D(s, v) + 2 + D(u, t).
  - That is the cost of routing s → v, then the backward step v → u, then u → t.
  - Weaken the remark to this, and justify D(v, u) = 2 (it is ≡ 2 mod 3 and positive).

## 6. Required before this is refereeable
1. Rewrite the remark after Lemma 8 as above, or delete it.
2. Add the three hypothesis checks in Lemma 5 and replace the 1989 citation with the 2020 one. Add theorem numbers after checking them against the sources.
3. Define "lone distinction" and b(x, y), fix s(x, x), and state G connected where D is used.
4. Patch Corollary 4's "proper subset" step and the reduction sentence in Proposition 3.
5. In the closing section, "Not proved: the upper bound b ≤ s + 1 (false on 64 bonded pairs…)" should say the upper bound is refuted by the census, and not list it as unproved.

**Statements to weaken:** only the post-Lemma 8 remark. Theorem 7 can be strengthened to all bonds at no cost.
