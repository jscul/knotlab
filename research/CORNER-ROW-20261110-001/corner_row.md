# A closed form for the corner's row of the block inverse

Epic `CORNER-ROW-20261110-001` (program foundations, groups `collapse` and `reach`, B140), 2026-11-11. Pre-registered in commit
c53bb2861, before any exact row was computed; the training verdict and the held-out predictions were committed in 128b2e30d, before
any entry at side 64 was computed.

## The question

- **Where it comes from.** `RETURN-LAW-20261110-001` wrote the corner's walks in the box as one block operator K_n of size 2(n − 1)
  (ticket C, Theorem 7), explicit at a power of two. Its corner entry is the return law, proved at each power of two to 512 by exact
  computation; its corner row carries the count that decides the failure of full reach (B137) by Corollary 10. A closed form for that
  row, proved for every m, would settle both. The coordinator gave the go-ahead on 2026-11-11 at 00:33 UTC and asked that "closed form"
  and "no pattern" be frozen in advance, and that the line stop at side 64 if no pattern appears.
- **The question.** Does the corner row have a closed form in a declared alphabet at every power of two, found on the sides 4, 8, 16, 32
  and confirmed on the held-out side 64?

## The question in standard terms

For the n × n grid's alternating medial digraph with the outer face's arcs removed, A over GF(2), and n = 2^m, the walk series from the
corner vertex c = (0, 1) to the vertices (0, 2b + 1) and (2n − 2, 2b + 1) of the two side walls, b = 0, …, n − 2, are rational functions
of s = w². A closed form is one uniform rule in the frozen alphabet (path and looped-path determinants over GF(2), truncated Catalan and
trace polynomials, monomial substitutions, finite sums and products, one quotient) giving every entry at every m, stated before side 64
and reproducing side 64 exactly.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **A partial rule only.** Rules in the frozen alphabet hold for the six entries next to the corners, all known or derivable before registration, and none was found for the other 2(n − 1) − 6 entries, so the row has no closed form of the kind looked for. The training verdict was committed before side 64; its label "no pattern" is corrected to this partial rule. | frozen outcome | A |
| 2 | **The row's denominators sit on the Kloosterman classes.** Their irreducible factors are exactly the minimal polynomials of the classes a ∈ GF(2n)* with Kloosterman sum K(a) ≠ 0, the a for which the curve y² + xy = x³ + a over GF(2n) does not have 2n points, and every such class appears (17 of 17 at side 64). That only these classes occur follows from the spectrum; that all of them appear is the row's own. | computed, exact, 4 to 64 (64 held out) | A |
| 3 | **Squares and exponents.** Every reduced denominator is a perfect square, and a class's largest exponent over the row is 2⌈\|K(a)\|/8⌉ (6 for \|K\| = 20 at side 64), not the spectrum's \|K(a)\|/2. | computed, exact, 4 to 64 (64 held out) | A |
| 4 | **No structure along the walls.** Along each wall the entries have linear complexity exactly n/2 over GF(2)(s), the generic value. | computed, exact (Hankel certificate), 4 to 64 | A |
| 5 | **The row is the walk to the side walls.** The corner row of K_n^(−1) is exactly the walk series from c to the side walls' v contacts. | proved | A |
| 6 | **The line is parked.** No rule appeared beyond the corners by side 64; the search was not extended, as frozen, and ticket B, conditional on a full rule, is retired. | the gap | A, B |

## Answer

The corner row has no closed form of the kind B140 looked for. After the training sides 4 to 32, rules in the frozen alphabet were
found only for the six entries next to the corners, all known or derivable before registration, and for none of the rest. That was
committed before side 64 was computed, and side 64 changed nothing. By the letter of the frozen criteria the outcome is a partial rule,
not the "no pattern" the training commit wrote; it ends the line the same way. What the rows do show, exactly and with side 64 held out:
their denominators sit on the classes of GF(2n) with nonzero Kloosterman sum and every such class appears, every denominator is a
perfect square, and a class's largest exponent is 2⌈|K|/8⌉. That only those classes occur is the spectrum's, since every walk series in
the box has it; the rest is the row's own. The line is parked as frozen.

## Reading

**Interpretation, not a theorem.**
- **Why no rule.** If the support law holds at every m, a rule giving the denominators in factored form would locate the Kloosterman
  zeros of GF(2n) at every power of two, and no such description is known. This is a heuristic and may not be the reason: a rule could
  carry the zeros implicitly, as a product or a determinant.
- **Two lines meet, partly.** The reduction of `REACH-HALVES-20261110-001A` took the failure of full reach away from the spectrum, to one
  walk count. Read through the corner row, that count meets the spectrum again, since the row's denominators carry every class of the
  collapse line's Kloosterman law (`LINEAR-ROOTS-20261109-001`). Whether the count itself needs the spectrum is open: the reduction does
  not show that it avoids it, and this route does not show that it needs it.
- **What would reopen it.** A closed form for the Kloosterman zeros of binary fields; a proof of the count that does not pass through the
  row's rational functions, for instance a pairing of the walks; or a reason for the exponents 2⌈|K|/8⌉.

## Timing (the protocol)

Commit times are in git; the file times below are modification times, recorded here because later edits move them. All in UTC on
2026-11-11.
- 00:35:59, c53bb2861: the registration (tickets, proof stubs, scope state) and nothing else.
- 00:36:30: the first exact rows, in the scratch work; `rows.py` refuses n ≥ 64.
- 00:41:38, 128b2e30d: the training verdict and P1 to P5, with no side-64 file.
- 00:41:54 to 00:41:56: `heldout64.py`, whose docstring cites 128b2e30d, and `rows_heldout64.json` (the run takes about 1.6 s).
- 00:42:21 to 00:42:23: `test64.py` and `heldout64_tests.json`. The test was written after the side-64 rows; the referee's independent
  test confirms P1 to P5 as worded.

Before registration the exploration in `RETURN-LAW-20261110-001` had truncated series to s^64 at sides 4, 8 and 16; at side 4 that is
more than the 24 terms that fix a row, so the side-4 row was determined before registration. It is a training side, so this could not
bias the held-out test. The training search took about six minutes between the two commits and tested only monomial relations between
entries; it missed the affine rule for ρ_(R,0), which the referee found.

## Literature and provenance

- Kloosterman sums over binary fields and the curves y² + xy = x³ + a (Lachaud and Wolfmann 1990; Katz and Livné 1989); a deterministic
  test for a single zero by point halving (Ahmadi and Granger, Math. Comp. 83 (2014)); values and zeros (Lisoněk 2008 and later). No
  closed form for the set of zeros was found.
- Bounded web search on 2026-11-11 (Kloosterman zeros of binary fields, their characterization by elliptic curves);
  `LINEAR-ROOTS-20261109-001`'s search (2026-11-09) found no link between Kloosterman sums and the spectra of walks over GF(2).

## Referee pass

An independent referee, a fresh agent that did not see the author's reasoning, read ticket A, its scripts, its data and the protocol on
2026-11-11. It recomputed every row at 4 to 64 by another method (the Krylov minimal polynomial of e_c under A² on the v contacts, on its
own walk), every Kloosterman sum and factorization with its own field, and Proposition 1 with its own block operator. Every computation
stands, and nothing was fitted to side 64. Its findings, all folded in:
1. **Six entries, not four** (error). ρ_(R,0) = s^(n−1) + s^(3n−1)/(1 + L(s²)) is in the alphabet and exact at 4 to 64, and with
   ρ_(L,n−3) = ρ_(R,0) it gives six entries; at side 4 they are the whole row. The verdict now says "no rule was found" and lists all
   six (ticket A, check 6).
2. **Wrong source** (error). The four-corner formula does not give ρ_(R,1) or ρ_(L,n−3); those are relations of the powers of two, seen on
   truncated series before registration, which fail at every side 3, 5 to 7 and 9 to 12. Corrected, with the failure checked.
3. **The letter of the frozen criteria** (gap). C1 and the corner relations, stated before side 64 and passing there, make the outcome a
   partial rule, not no pattern, and 128b2e30d's "cannot change the verdict" was wrong for P5. Relabelled as a partial rule, with a
   correction note under the committed text and an entry in `docs/CORRECTIONS.md`.
4. **Timing** (fine). The timeline checks out; it is recorded above.
5. **What was held out** (gap). The support half of K1 follows from the spectrum, two of P5's relations had been computed at side 64,
   and P4 predicted the generic outcome. The held-out bullet now says which tests were real (ticket A, check 8 for the spectrum).
6. **Novelty** (overclaim). The support is inherited and the exponents differ from the spectrum's (|K|/2 in the minimal polynomial of
   A² on the v contacts). The classification now claims only that the row sees every class, the squares and the exponents.
7. **K4 was random points** (overclaim). Now certified exactly by Hankel determinants (check 7).
8. **"Governed by"** and 9. **"Would have to"** (overclaims). Narrowed to "supported exactly on"; the Kloosterman-zero argument is marked
   as a heuristic and kept out of the Answer.
10. **Status wording.** Ticket A's class is closed-null; this attempt's verdict is Failed (below).
11. to 17. **Minor.** The s-bound n(n − 1) is explained, a dead comment in `rows.py` removed, check labels fixed (check 3 now reads the
   file from 128b2e30d), citations completed (Katz and Livné; "counting the point at infinity"; "through the curve's 2-Sylow
   subgroup"), nonclaims added and the manifest updated.

## Corrections

Two, both **Not a block** (`docs/CORRECTIONS.md`, 2026-11-11):
- `CORNER-ROW-20261110-001A`'s training verdict (128b2e30d) named four entries next to the corners with rules where six have them,
  credited two of them to the wrong source, and called the outcome "no pattern" where the frozen criteria give a partial rule.
- `REACH-HALVES-20261110-001` said the failure of full reach does not need the spectrum; only its reduction is shown not to need it.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a closed form for the corner row (B140) | **Status:** Failed | Rules only for six corner entries known before; none for the rest by side 64 |
| Local direction — the corner route to the full-reach count | Practically exhausted (parked) | No rule beyond the corners; frozen stop at side 64 |
| Broader exploration — the cut-open torus line (G5) | Known alternatives | Other tori (B66), the least solution's degree (B74), the other half (B139) |
| Long-term goal — G5 Dynamics (question 4) | No demonstrated advance | The corner route meets the spectrum's Kloosterman classes; the count stays open |

**Corrections:** two, both Not a block (above). **Goals:** a G5 checkpoint (no demonstrated advance), no goal change; B140 taken, B142
added; the corner line parked. **Assumptions:** none added or changed.
**Basket:** B137 (3/3, 1/3), B74 (3/3, 1/3), B66 (2/3, 3/3); none taken: the corner line is parked by its frozen stop, and which line
comes next is the coordinator's call.

- **What the attempt leaves open.** The count of B137, the return law for every m, and the row's laws K1 to K4 as theorems.
- **What it keeps.** The decompositions of `RETURN-LAW-20261110-001`, the exact law at each power of two to 512, the six corner rules
  exact to 64, and the row's Kloosterman structure as a held-out computed law.

**Next step:** Full pivot — No next action selected. This leaves the corner route to the full-reach count (B140, with B137 and B141
behind it), parked by its frozen stop; what comes next is another line, among the candidates below, for the coordinator to choose.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other tori (B66) | 2/3 — Substantial | 3/3 — Ready | The spectrum of the cut-open 2^m × 2^(m′) torus for small m ≠ m′, matched against Kloosterman-type sums → a two-parameter law, or where it breaks | Alternative · deferred |
| 2 | The degree of the least solution (B74) | 3/3 — Barrier | 1/3 — Stated | Bound deg G from its identity with the overflow R at the roots of Δ → the eigenvector half of the Kloosterman law, or why the identity cannot see K | Alternative · deferred |
| 3 | A short-time certificate for the other half (B139) | 2/3 — Substantial | 1/3 — Stated | Odd counts within 6.4n for every contact and ring, sides to 40 → a rule, or sides with none | Alternative · deferred |
| 4 | The corner row's squares and exponents (B142) | 1/3 — Modest | 1/3 — Stated | Derive the row's exponents 2⌈\|K\|/8⌉ from the Jordan chains of A² at 8 and 16 → a proof at those sides, or the step that needs the collapse line's chains (B73) | Alternative · deferred |

1. **Other tori.** Payoff 2: whether the Kloosterman law belongs to the square torus only, the question the collapse line left first.
   Concreteness 3: the cone's tools compute it directly. It leaves the corner route for its neighbour on the collapse line.
2. **The least solution's degree.** Payoff 3 and concreteness 1, unchanged: it would give the eigenvector half of the Kloosterman law,
   but its method stalled (B73, B74).
3. **The other half.** Payoff 2 and concreteness 1, unchanged.
4. **The row's squares and exponents.** Payoff 1: it would say which part of each Jordan chain the corner's walk to the walls reaches,
   which bears on B137 only indirectly. Concreteness 1: the law is exact and held out to 64, but no derivation is in hand.

**Recommendation.** Stop the corner line here, as frozen; the coordinator picks the next line.

## Final report as sent

Sent to the owner on 2026-11-11 at 01:41 UTC and copied here verbatim.

**Corner row (B140): there's no closed form, so I've parked the corner line as frozen.**

I stopped at side 64 as agreed. Rules in the frozen alphabet exist only for the six entries next to the corners, all known or derivable before registration. I found none for the rest of the row. The training verdict was committed before side 64 was computed, and nothing was fitted afterwards.

What the exact rows show instead, with side 64 held out:
- The denominators vanish exactly at the elements of GF(2n) whose Kloosterman sum is nonzero, and every one of them appears.
- Every denominator is a perfect square, and the largest exponent is 2⌈|K|/8⌉.

That only those elements occur was automatic: every walk series in the box inherits it from the spectrum. That all of them appear, the squares and the exponents are new as far as I found.

The independent referee reproduced every computation by another method and caught a real slip. One more corner entry has an affine rule that my training search missed, because it only tried monomial relations. By the letter of the frozen criteria that makes the outcome a "partial rule", not the "no pattern" I had written. I relabelled it and logged the correction. Nothing changes in substance.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a closed form for the corner row (B140) | **Status:** Failed | Rules only for six corner entries known before; none for the rest by side 64 |
| Local direction — the corner route to the full-reach count | Practically exhausted (parked) | No rule beyond the corners; frozen stop at side 64 |
| Broader exploration — the cut-open torus line (G5) | Known alternatives | Other tori (B66), the least solution's degree (B74), the other half (B139) |
| Long-term goal — G5 Dynamics (question 4) | No demonstrated advance | The corner route meets the spectrum's Kloosterman classes; the count stays open |

**Corrections:** two, both Not a block.
1. The corner row's training verdict named four entries with rules where six have them, credited two of them to the wrong source, and called the outcome "no pattern" where the frozen criteria give a partial rule ([decision note](https://github.com/jscul/knotlab/blob/main/research/CORNER-ROW-20261110-001/corner_row.md)).
2. REACH-HALVES said the failure of full reach "is not spectral". Only its reduction avoids the spectrum, and whether the count needs it is open ([note](https://github.com/jscul/knotlab/blob/main/research/REACH-HALVES-20261110-001/reach_halves.md)).

**Goals:** a G5 checkpoint (no demonstrated advance), no goal change; B140 taken, B142 added, B137 parked.
**Assumptions:** none added or changed.
**Basket:** B137 (3/3, 1/3), B74 (3/3, 1/3), B66 (2/3, 3/3). I took none of them: the line is parked, and picking the next line is the coordinator's call.

**Next step:** Full pivot — No next action selected. This leaves the corner route to the full-reach count. The next line should come from these:

(The direction table is the one under "Next steps" above.)

Everything is committed and published. I'll hold here until you or the coordinator pick the next line.
