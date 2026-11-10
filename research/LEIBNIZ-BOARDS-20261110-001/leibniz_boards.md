# Leibniz boards

Epic `LEIBNIZ-BOARDS-20261110-001` (program topology, group `spacing`, sub-goal B111, G1), 2026-11-10. Pre-registered in commit
3592c5641, with ticket B's census frozen there (its code revised before any run in ec1664143, as its contract records).

## The question

- **Where it comes from.** `BOARD-DIST-20261110-001` proved that, with the board made of identity distinctions, a law that names no
  relation and allows an infinite board allows the tree. The theorem needs finitary clauses. The coordinator's go-ahead of 2026-11-10
  took its direction 1: Leibniz's rule in full, "names whose views agree at every radius are one place", one infinitary rule the
  theorem does not reach.
- **The question.** Under that rule, does an infinite board always bring the tree (W), and can a law make every board a plane (P)?

## The question in standard terms

For a shift of finite type X on F2, are there points with trivial stabilizer whenever some point has an infinite orbit? And can every
stabilizer have a Schreier graph of quadratic growth?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The boards are stabilizer quotients.** Under Leibniz's rule a law's boards are exactly Sch(Stab(s)) for its solutions s on the tree. | proved | A |
| 2 | **Not every board is the tree or finite (S false).** The horofunction law on Z/3 (one neighbour one lower, three one higher) has, for the end x^∞, the stabilizer ⟨x³⟩: a 3-cycle with trees attached is a board. Found by hand before registration and disclosed. | proved | A |
| 3 | **Lemma A.** A periodic solution that uses a branching pattern gives, by independent choices on disjoint half-trees and the Baire category theorem, a solution with trivial stabilizer (the tree) and one with infinite cyclic stabilizer. | proved | A |
| 4 | **Lemma B.** If no solution has trivial stabilizer, an open set of solutions is fixed by one h ≠ 1, uniquely completed off h's axis, finite, and made of isolated points. | proved | A |
| 5 | **W and P for every one-bit Life-like law and the atom.** Of the 1,024 Life-like laws, 31 have no solution, 97 are deterministic (every board finite) and 896 have a periodic branching solution; so does the atom. None is undecided (C1). So under Leibniz's rule no law of the family forces the plane, and each of the 897 has the tree and an infinite cyclic board. | proved, from a computed exact census | A, B |
| 6 | **W in general is reduced, not proved.** It is equivalent to excluding a non-isolated solution in a shift with no free solution. Such a solution would be fixed by some h ≠ 1, rigid away from one end of h's axis, and have only isolated far alternatives. | the gap | A |
| 7 | **The plane is often a board.** 891 of the 896 class-A laws have an aperiodic solution on the plane, certified by a refill on a torus, so the plane is a board without being forced. | computed | B |

## Answer

Leibniz's rule does not choose the plane for any one-bit Life-like law, or for the atom. Every such law either has finitely many
solutions, so every board is finite, or has a periodic solution with a free choice in it. Free choices made independently on
infinitely many interchangeable half-trees leave the tree as a board, and choices repeated along one element leave a cycle with
trees attached. The coordinator's strong form, "every board is the tree or finite", is false, already for a three-value law. For
arbitrary finite alphabets the dichotomy "an infinite board brings the tree" is reduced to excluding one rigid kind of solution, and
is not proved. Free groups carry laws with no finite board (Piantadosi), and those are the only possible exceptions.

## Reading

**Interpretation, not a theorem.**
- **Why the tree keeps coming back.** On a tree, choices in disjoint branches are independent. Wherever a law leaves a choice and
  has a periodic solution, the choices can be spread out so that nothing repeats, and Leibniz's rule then keeps every name a
  separate place.
- **What a counterexample would need.** A law whose freedom runs along a single end and is fixed elsewhere. Every point would be a
  rigid world with one open direction, like a number line attached to a tree. That is a weakly aperiodic shift without free points;
  none was found or excluded.
- **For the owner's idea.** With the identity rule taken to its infinitary limit, the plane is still not chosen by a value law in
  the family studied. It is often allowed, though, 891 times out of 896: the board can be a plane, but the rules never make it one.
- **Nothing here is a length.**

## Lag cutoffs and census-only claims

- **Exact.** Classes D and A are decided exactly, A by certificates on boards to 8 places (re-verified by ticket A's check).
- **Census-only.** Conclusions 5 (through the census) and 7.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusion 5 (boards to 8 places decided every law) | — (the census decided every law; a larger board cannot change a decided class) | not run |
| Conclusions 1 to 4 (proved) | — | proofs by hand; T2 checked on the ball of radius 9, every class-A certificate re-verified |

## Literature and provenance

- **Sources.** Busemann functions and ends of trees; the Baire category theorem; shifts of finite type on free groups (Piantadosi
  2008: no strongly aperiodic SFT, while weakly aperiodic ones exist; Carroll and Penland on weak and strong periodicity; Bitar,
  arXiv 2406.04132, on stabilizers of SFT points); graph subshifts (Arrighi, Durbec and Guillon 2023).
- **Classification.** Conclusions 2 to 4 are elementary and close to folklore. W was not found stated for free groups (bounded
  search, 2026-11-10, not a priority claim).

## Workspace assumptions

- **Relied on.** A53 (nativeness counted per name) and A54 (two-letter naming), from `BOARD-DIST-20261110-001`.
- **Bearing on A51.** Leibniz's rule is infinitary, so A51's confirmation for finitary laws that name no relation stands, and is
  extended to the one-bit Life-like family under the infinitary rule.
- **Added.** None.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (T1 to T6, two checks) and ticket B (the census).
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — Leibniz boards | **Status:** Partially successful | W and P proved for every one-bit Life-like law and the atom; S refuted; W in general reduced to one rigid kind of solution, not proved |
| Local direction — the identity rule in the limit | Paused by the stop rule | W was not settled in one epic; no new route is named |
| Broader exploration — question 9, boards made of distinctions | Known alternatives | Rigid finite worlds at radius 2, other namings, growth |
| Long-term goal — G1 Space from a law | Obstruction learned | Even Leibniz's rule leaves the tree open in the family studied: the plane is allowed, never forced |

**Corrections:** none. **Goals:** a G1 checkpoint (obstruction learned); B111 taken. **Assumptions:** none added or changed (A51 is
extended in scope, and its history records it).
**Basket:** spacing's BOARD-DIST-20261110-001#2 (rigid worlds at radius 2, 2/3, 3/3), HARD-FLAT-20261107-001#3 (every accretion law,
2/3, 2/3) and BOARD-DIST-20261110-001#3 (abstract names, 2/3, 2/3); taken: BOARD-DIST-20261110-001#2.

- **What the attempt leaves open.** W for arbitrary finite alphabets, the weakly aperiodic laws in particular, and with it P in
  general.

**Next step:** Research directions — selected: #1 (BOARD-DIST-20261110-001#2), unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Rigid worlds at radius 2 (BOARD-DIST-20261110-001#2) | 2/3 — Substantial | 3/3 — Ready | Search the Life-like laws for one whose radius-2 identity boards are all abelian and plane-like, room only below 256 places → such a law, or none in the family | Selected · not started |
| 2 | Weakly aperiodic laws under Leibniz's rule | 2/3 — Substantial | 2/3 — Testable | Build an explicit weakly aperiodic shift of finite type on F2 and decide whether it has a free point → a free point, or a counterexample to W | Alternative · not started |
| 3 | W in general | 2/3 — Substantial | 1/3 — Stated | Exclude the rigid one-ended solution of conclusion 6 → W proved, or the obstruction located | Alternative · not started (paused by the stop rule) |
| 4 | Abstract names (BOARD-DIST-20261110-001#3, A54) | 2/3 — Substantial | 2/3 — Testable | As recorded there | Alternative · not started |

1. **Rigid worlds.** Payoff 2: a finite two-dimensional world chosen by the rules would be the strongest positive answer this setting
   leaves room for. Concreteness 3: SAT over view boards, as at radius 1. Parity and the atom are already not rigid at radius 2.
2. **Weakly aperiodic laws.** Payoff 2: the only place W can fail. Concreteness 2: such shifts are known to exist, but none is in hand
   here.
3. **W in general.** Payoff 2: it would close the infinitary limit. Concreteness 1: the gap is located, and the argument that should
   close it fails in one case.
4. **Abstract names.** As rated by `BOARD-DIST-20261110-001`.

**Recommendation.** Research directions, selected #1: the most concrete open question about boards made of distinctions, and the
spacing basket's top item. The Leibniz line pauses by its stop rule.
