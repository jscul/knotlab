# The board as distinctions

Epic `BOARD-DIST-20261110-001` (program topology, group `spacing`, backlog B92, G1), 2026-11-10. A challenge of A51, pre-registered in
commit c3b6a0bde with ticket B's census frozen there.

## The question

- **Where it comes from.** In Life, and in every law the program has measured for space, the board comes first: which places exist and
  which are neighbours is fixed before the rules are read (A51, lesson 4.6). The owner's idea, stated on 2026-11-07 and asked about
  again on 2026-11-10, is that the axes themselves follow rules, as Life's cells do, governed by an essentially infinite CNF. Backlog
  B92 recorded the first test, and the coordinator assigned it on 2026-11-10.
- **The question.** Make "these two names are one place" a distinction of the same infinite CNF as the values, constrained by one
  uniform clause pattern. Which boards do the rules then allow or force, and can they force a plane?

## The question in standard terms

Names are the elements of the free group F2 = ⟨x, y⟩; an identity distinction e(u, v) for each pair, under transitivity, letter closure
e(u, v) → e(ug, vg) and constancy e(u, v) → s(u) = s(v), with a finitary uniform law over a finite alphabet. The boards are then
subgroups of F2. Which subgroups (Schreier graphs) can such a law force, and which do the 1,024 Life-like one-bit laws allow?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Boards are Schreier graphs.** The boards are exactly the subgroups of F2 with their Schreier graphs, and on a finite ball of names exactly the restrictions of these. | proved; classical | A |
| 2 | **Refinement.** With no positive identity literal besides the board axioms, refining an allowed board keeps it allowed: the tree (no two names one place) is allowed whenever any board is. | proved | A |
| 3 | **Unfolding.** If a law names no relation (each identity literal relates the same offset of two names) and allows an infinite board, it allows the tree. So no such law forces the plane, or any infinite board; it can force only finite ones. | proved; new as far as found | A |
| 4 | **Finite boards can be forced.** Every finite board is the only board of some law that names no relation (a Cayley-type law with one value per place, and identity of indiscernibles at radius 0). Identity of indiscernibles at any radius makes every board finite. | proved | A |
| 5 | **One named relation suffices.** The commutator rule e(u, uxyXY), a face of size four, with an aperiodic tile law, forces exactly the plane. | proved; classical ingredients | A |
| 6 | **Boards made of names are frozen to finite changes.** Two different boards differ in infinitely many identity distinctions, and off the tree every place holds infinitely many names. So no distinction of a state off the tree, and no identity distinction anywhere, is flipped by a finite change. | proved | A |
| 7 | **The census.** All four frozen predictions hold with no violation over the 1,024 Life-like laws: every allowed board brings its covers (P1, P3), the collapse comes with every board (P2), and at radius 1 every plane-like abelian identity board has a non-abelian sibling (P4). 768 laws allow every board, 31 none, and the other 225 allow the tree; 2 of those allow the tree but not the plane. | computed, exact, frozen | B |
| 8 | **The board bound to the values, beyond constancy.** In 60 laws the square's identity distinction e(1, xyXY) is knotted with values it does not identify. Closing the square makes 1 and xyX neighbours. In 56 laws this gives a single clause of three, the atom's shape: e → s(1) ∨ s(xyX) (as in 26 of the 32 laws in which a 0 has only 1s around it), or its complement e → ¬s(1) ∨ ¬s(xyX). In 4 it gives e → s(1) ≠ s(xyX). All are knots by K1–K3 (knotlab). | computed, exact | B |
| 9 | **The second code agrees.** The truncated CNF on the ball of names, read by a SAT solver written apart, agrees for parity 0, parity 1 and the atom (P5). | computed, exact | B |

## Answer

No law that names no relation chooses the plane. Whenever such a law allows an infinite board it also allows the tree, the board in
which no two names are one place, so the plane is never forced: a board made of distinctions stays free in the direction of the tree.
What such laws can force is a finite board, and the natural rule that makes names one place (two names that look alike are one place)
always does so. The plane follows as soon as one relation is named: the square, with an aperiodic law. In the census of the 1,024
Life-like laws every allowed board brings all its covers, exactly as the proofs say, and the values can forbid a square from closing,
the one way the board is bound to the values beyond "one place, one value". That binding is never native: a board made of names cannot
change by finitely many distinctions.

## Reading

**Interpretation, not a theorem.**
- **Shapes have rules, and the plane's rule is a shape.** The owner's hint was that lines and functions are shapes and shapes have
  rules. The theorems say the plane follows from rules exactly when a rule names a shape, the closing square. Rules that only say which
  names are one place never name which words close, and cannot choose it.
- **Why the tree survives.** Without a named relation, a law can identify names only by how they look. On an infinite board only
  finitely many places look unique, and far from them every local view repeats; the tree is the board on which every repeated view is a
  different place.
- **The free board is hyperbolic.** The board a relation-free law always leaves open grows exponentially; flat boards need a named
  relation, as uniform laws of lines and co-lines needed their co-lines (`UNIFORM-SPHERES-20261107-001`).
- **Frozen at infinity.** Boards made of names are frozen to finite changes, so under the source-aware reading no knot that involves the
  board is native. If dimensions are to follow rules as distinctions, either nativeness is read per place rather than per name, or the
  board comes from a process.
- **Identity is not contact.** The knots of conclusion 8 involve an identity distinction; they are bindings of the law, not contacts
  (A51; equality is not a binding).
- **Nothing here is a length.** Board growth counts places within a number of letter steps; no distance is read from values.

## Truncations and census-only claims

- **Exact.** The tree, the lines and every finite board are decided exactly; the plane by tori to index 16 and boxes to 8 × 8, which
  decided all 1,024 laws.
- **Truncations.** Ticket B's B4 reads the CNF on finite balls of names. There the atom's identity-of-indiscernibles tree query is a
  pigeonhole instance (53 inner names into 28 views), which the solver did not finish; it is decided by the count.
- **Census-only.** Conclusions 7 to 9.

## Deviations from the frozen contract

- **Stress S2.** Its first run stalled on parity 0 before printing a result: parity laws on tori are Tseitin-like systems that a
  clause solver can take exponentially long to refute. It was stopped and rerun with parity decided by linear algebra over GF(2) and
  the atom's solver calls under a conflict budget (none was reached). The laws, the boards, the notion of an identity board and the
  prediction are unchanged.
- **B4 and S3, the atom.** The identity-of-indiscernibles tree query is a pigeonhole instance (53 or 161 inner names into 28
  views). The solver did not finish it in 28.7 and 7 minutes, and both runs were stopped. The atom's other queries were rerun with
  the frozen functions (`supplement_atom.py`), and the two identity queries were decided by a certificate (the collapse state) and by
  the count.
- **S1's output** (583 MB, regenerable) is kept in compact form.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusions 2 and 3 (proved; P1, P3 to 6 places) | every finite board with 7 and 8 places | passed: P1 to P4 with no violation over all 39,391 finite boards to 8 places (41,088 covering pairs). The four laws that allowed the tree but no finite board to 6 places allow boards with 7 places (L40 and L80, 187 each, none abelian, so not the plane) or with 8 (L66 and L264) |
| Conclusion 7, P4 (radius 1, proved and computed) | radius 2 for parity 0, parity 1 and the atom | passed, after a disclosed fix (the first run stalled on parity's Tseitin-like tori, so parity was decided by linear algebra over GF(2)): parity 0 and 1 have radius-2 identity boards on 4 of the 28 tori listed and on 90 of the 166 non-abelian boards, the atom on all 28 and all 166. None of the three forces a two-dimensional board at radius 2 |
| Conclusion 9 (truncations L = 6 and 4) | L = 7 and 5 | passed: all three laws agree with the census. The atom's identity queries were decided by certificate and by count, and its solver run was stopped on the pigeonhole instance |

## Literature and provenance

- **Sources.** Schreier coset graphs and Stallings foldings (1983); compactness (Tychonoff; König); aperiodic tilings (Berger 1966,
  Robinson 1971, Jeandel and Rao 2015); Leibniz's identity of indiscernibles, read as a rule; shifts of finite type on free groups
  (Piantadosi 2008) and tree shifts (Aubrun and Béal).
- **Names elsewhere.** Graph subshifts (Arrighi, Durbec and Guillon, arXiv 2302.07249, 2023) ask the same question in another
  formalism: sets of graphs defined by forbidding finitely many local patterns, which extend both shifts of finite type and finitely
  presented groups, and the question whether such local conditions can enforce a specific support graph. Their abstract proves that
  subshifts containing only infinite graphs are aperiodic or have a period group that is not residually finite; no statement like
  conclusion 3 was found there. Quantum graphity (Konopka, Markopoulou and Smolin 2006) and the Wolfram model (2020) make adjacency
  dynamical; Gromov's growth of groups (1981) reads dimension from ball growth. Free groups carry no strongly aperiodic shift of
  finite type (Piantadosi 2008), which bears on the identity rule in the limit (sub-goal B111).
- **Where the ideas came from.** The owner's idea and B92's design. The reading of these boards as subgroups is classical in itself;
  the unfolding theorem, the freezing of boards made of names and the census are this epic's.
- **Classification.** New as far as found for conclusions 3, 6 and 8 (bounded searches on 2026-11-10, the second at the coordinator's
  request, not a priority claim), within the known framework of graph subshifts. Known-with-delta for conclusion 5: finitely
  presented groups are graph subshifts, and aperiodic tilings exclude the periodic quotients. Folklore risk moderate for 1, 2 and 4.

## Workspace assumptions

- **Challenged.** A51, by design. It is confirmed for planes within laws that name no relation.
- **Relied on.** The source-aware reading (2026-10-20), applied as written in conclusion 6.
- **Added.**
  - A53: nativeness of a board made of names is counted per name, the reading behind conclusion 6.
  - A54: places are named by words in two letters, the naming behind every result here.
- **Scope.** Names from the free group on two letters, so the naming supplies four neighbour names per name; finitary templates over
  finite alphabets.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (eight theorems, six checks) and ticket B (the census, the second code, the stress tests).
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the board as distinctions | **Status:** Successful | Answered by proof: a law that names no relation never forces the plane (Theorem 3). The frozen census held all four predictions, and the plane follows from one named relation (Theorem 8) |
| Local direction — boards made of distinctions | Obstruction proved | Static, finitary laws that name no relation leave the tree open; what remains is the infinitary limit of identity of indiscernibles, finite worlds at radius 2, and other namings |
| Broader exploration — question 9, space with nothing drawn | Sharpened | The barrier of `LOGIC-AXIS-20261107-001` extends from drawn boards to boards made of distinctions: the plane needs a named shape or a process |
| Long-term goal — G1 Space from a law | Obstruction learned | Dimension two cannot follow from rules that name no relation in a static CNF; it follows from one rule that names the square |

**Corrections:** none. **Goals:** a G1 checkpoint (obstruction learned); B92 taken; sub-goal B111 recorded (Leibniz boards, selected).
**Assumptions:** A51 confirmed for planes within laws that name no relation (under challenge here); A53 (nativeness of a board made of
names is counted per name) and A54 (places are named by words in two letters) added.
**Basket:** spacing's HARD-FLAT-20261107-001#3 (every accretion law, 2/3, 2/3) and B16 (edge labels, as in Radin's rules, 2/3,
1/3); the recommendation stays in this line, whose next step rates higher and starts where the obstruction stops.

- **What the attempt leaves open.**
  - Whether identity of indiscernibles in the limit, an infinitary rule, can choose the plane.
  - Whether a one-bit law with indiscernibles at radius 2 forces a finite two-dimensional world.
  - Namings other than words in two letters.

**Next step:** Continue — selected: #1, unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Leibniz boards (B111) | 3/3 — Barrier | 2/3 — Testable | Prove or refute the Leibniz dichotomy: every tree shift of a star law has a point with trivial stabilizer, or only points with finite-index stabilizers. Compute the identity boards of parity and the atom at radius 2 and 3 → the dichotomy proved, or a law whose limit boards are all planes | Selected · not started |
| 2 | Rigid worlds at radius 2 | 2/3 — Substantial | 3/3 — Ready | Search the Life-like laws for one whose radius-2 identity boards are all abelian and plane-like (room only below 256 places) → such a law, or none in the family | Alternative · not started |
| 3 | Abstract names (A54) | 2/3 — Substantial | 2/3 — Testable | Names without letters, a neighbour distinction per pair, laws that name no degree → whether a finitary law can force bounded degree at all, and the unfolding theorem there | Alternative · not started |
| 4 | Nativeness per place (A53) | 1/3 — Incremental | 3/3 — Ready | Re-read the census's 60 square knots with changes counted per place → which become native | Alternative · not started |

1. **Leibniz boards.**
   - **Payoff 3.** It is the one route left that names no relation and needs no history. Two names that agree at every radius are one
     place; under that rule the boards are the stabilizer quotients of the law's solutions on the tree. A value law that this rule
     turns into the plane would put dimension in the rules.
   - **Concreteness 2.** The objects are standard. The main uncertainty is that free choices on branches seem to give trivial
     stabilizers, which would prove the dichotomy and close the static question instead.
2. **Rigid worlds.**
   - **Payoff 2.** A finite two-dimensional world chosen by the rules, bounded in size.
   - **Concreteness 3.** SAT over view boards, as at radius 1. Parity and the atom are already not rigid at radius 2 (the stress test).
3. **Abstract names.**
   - **Payoff 2.** It would make the obstruction independent of the naming, or show that the naming is the hidden drawing.
   - **Concreteness 2.** It needs the formalism.
4. **Nativeness per place.**
   - **Payoff 1.** A reading.
   - **Concreteness 3.** The knots are in hand.

**Recommendation.** Continue with #1. The finitary question is closed by proof; the infinitary limit of identity is where the owner's
idea still has room without naming a shape.

## Final report as sent

Sent to the owner on 2026-11-10 at 05:24 UTC and copied here verbatim.

I've closed and published the board-as-distinctions epic. I proved an obstruction: when "these two names are one place" is a distinction of the CNF, no uniform law that names no relation can choose the plane.

**What I proved.** Names are the words in x, y and their inverses. With that naming, the boards are exactly the Schreier graphs of subgroups of the free group: the tree, the plane, lines, tori and the rest. Suppose a law only says which names are one place, never that a word comes back to where it started. If it allows any infinite board, it also allows the tree, so it never forces the plane. Such laws can force finite boards, and "names that look alike are one place" always makes the board finite. One named relation is enough, though: a closing square at every name, together with an aperiodic tile law, forces exactly the plane. Your hint fits here: shapes have rules, and the plane's rule is a shape.

**The census.** I froze an exact census of all 1,024 Life-like one-bit laws plus the atom, and every prediction held with no violation, including one size past. The values can stop a square from closing. In 60 laws the square's identity distinction is knotted with two values that the square makes neighbours, and in 56 of those the knot is a single clause of three. Nothing that involves the board is native, though, because a board made of names can't change by finitely many distinctions.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the board as distinctions | **Status:** Successful | Answered by proof; the frozen census held every prediction |
| Local direction: boards made of distinctions | Obstruction proved | Finitary relation-free laws leave the tree open; the infinitary limit is what remains |
| Broader exploration: question 9 | Sharpened | LOGIC-AXIS's barrier now covers boards made of distinctions too |
| Long-term goal: G1 Space from a law | Obstruction learned | The plane needs a named shape or a process |

**Next step:** Continue with #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | Leibniz boards (B111) | 3/3 | 2/3 | Prove or refute "tree or finite" when names that agree at every radius are one place | Selected |
| 2 | Rigid worlds at radius 2 | 2/3 | 3/3 | Search for a law that forces a finite 2D torus | Alternative |
| 3 | Abstract names (A54) | 2/3 | 2/3 | Names without letters: does the theorem survive? | Alternative |
| 4 | Nativeness per place (A53) | 1/3 | 3/3 | Re-read the 60 square knots per place | Alternative |

**Corrections:** none. **Goals:** G1 checkpoint (obstruction learned), B92 taken, sub-goal B111 recorded. **Assumptions:** A51 is now confirmed for planes within relation-free laws. I added A53 (nativeness counted per name) and A54 (two-letter naming).
**Basket:** spacing's HARD-FLAT-20261107-001#3 and B16. I didn't take either, because #1 rates higher and picks up where the obstruction stops.

Two deviations are disclosed in the record. A stress script stalled on parity, so I switched it to linear algebra over GF(2). One pigeonhole query was decided by counting after the solver ran for 28 minutes. Commits: c3b6a0bde, 9248d6929, 2e638b79b. My tracking rows went in with another thread's tracking commit, b812d2965.
