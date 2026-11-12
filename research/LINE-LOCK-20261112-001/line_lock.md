# Lines in the increments

Epic `LINE-LOCK-20261112-001` (`SHIFT-LOCK-20261112-001` direction 1, influence beyond cycles; G17 with G8; program mathematics,
group arithmetic), 2026-11-12, at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in
commit `023a3da46`. Proof family: `proofs/LINE-LOCK-20261112-001A/`. **Referee pending.**

## Words

Changed after the freeze on the advisor model's word check, with the same meanings as in the pre-registration: the increments are now
the **stitch pairs** of an orbit; a Latin sub-law is a **permutive sub-stitch** (a set of triples inside the stitch in which, for every
two entries from its set of states, exactly one third completes a triple; the literature's quasigroup or permutive law); a line is a
**ratio subgroup** ⟨(g, λg)⟩ of the stitch pairs with ratio λ not 0 or 1 at an odd prime (the literature's line through the origin),
and the automaton it gives is **additive**. "Line", "linear" and "Latin" are words for drawn space or lean on one.

## The question

`SHIFT-LOCK-20261112-001` found states of copies along two shifts that repeat along no step but carry no influence; locks at every size
came from cycles. Influence of Ledrappier's kind, lock arithmetic that is not eventually periodic, would need an additive automaton
inside the stitch. Does any harmony's stitch hold one? The coordinator named the odd harmonies of periods 61, 73 and 193.

## The answer

**No harmony's stitch holds one: proved for the unlagged stitch of every harmony, and checked for lagged stitches on all 105 harmonies
in range.**

- **The theorem (proved).** A harmony's one-order stitch holds no permutive sub-stitch on a set of two or more states. Read the bits at
  the three members' places as three functions on the states: a permutive set of triples forces at most one of them to vary, and the
  other two to be constant and opposite. Two states differ somewhere, so at that place every knot of the harmony has its other two
  members opposite, and the place can be flipped once on the integers: a state that does not repeat, which a harmony does not have. So
  no orbit holds a ratio subgroup, which is what an additive automaton needs, at any period, for any knot shape across two shifts and
  any slot order. The odd harmonies are covered; they never needed a run.
- **The census (exact; 73 harmonies, 187 orbits).** Every orbit of the 66 harmonies of span at most 8 (periods 2 to 240) and of the 7
  odd step sets: no free site anywhere (the theorem's premise), no ratio subgroup or other permutive block, 22 cyclic subgroups and 2
  cosets inside the stitch pairs, all degenerate (states constant along a direction), and **no coset with a ratio part**, so no lagged
  stitch holds an additive automaton either. On the odd harmonies' orbits the stitch pairs are {(0, 0)} alone: stitched in one order,
  three copies in one orbit of an odd harmony that share a knot are equal.
- **One size past (after the run).** The 32 further harmonies of span 9 (periods 12 to 252): the same.
- **So** two-way influence of Ledrappier's kind cannot come from stitched harmonies in range. The obstruction the coordinator asked for
  if everything reduced to cycles is now part proof, part census. Ledrappier's law itself is a parity law on the mixed shape, and parity
  is permutive, so the program's own parity knots do carry it; not-all-equal on a harmony's states does not.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| No permutive sub-stitch on one set of states in a harmony's one-order stitch; so no ratio subgroup, Z₂ × Z₂ block or free pair in any orbit | proved by hand (the advisor model's lemma, rechecked) |
| No free site in 73 harmonies; no ratio subgroup, block or free pair; 22 + 2 degenerate subgroups and cosets; no coset with a ratio part | exact on the range (frozen) |
| The same on the 32 harmonies of span 9 | after the run, exact |

## Against the pre-registration

Theorem checks all passed (99%); no free site (99%); no coset with a ratio part that a lag can give (mine, 55%: met); some coset with a
ratio part and a flip (mine, 40%: not met, none at all). The census took 7 seconds of processor time, inside its cap. Words changed
after the freeze (above), meanings unchanged.

## Known mathematics

Ledrappier's shift (1978); Markov subgroups and algebraic actions of ℤ² (Kitchens and Schmidt; Schmidt's book); permutive and
additive automata (Hedlund; Ito, Osato and Nasu; Martin, Odlyzko and Wolfram); three-member permutive shapes, the totally extremally
permutive subshifts with Ledrappier's as the prime example (Salo, "Cutting corners", 2022); not-all-equal has only trivial polymorphisms
(Schaefer). The theorem, the advisor's two-constant-fibres lemma, is not one the advisor or I have seen stated; novelty is claimed for
it only with that caveat, pending the referee's search.

## What it changes

- **For the owner's "globally influential".** Patterns that fold in two directions out of copies of a harmony can make two-way states,
  but never an additive one, so their reach stays tied to cycles; reach of the kind Ledrappier's law has, a pattern's influence set by
  the arithmetic of polynomials, needs a permutive knot, and the not-all-equal law on repeating patterns cannot supply one.
- **What would be new next.** Mixing laws: a permutive (parity) knot among stitched not-all-equal copies. Whether the not-all-equal
  copies freeze its arithmetic or carry it is open.

## Assumptions

A70 (the theorem's premise, every state repeats), A75 and A77 used; none added.

## Corrections

One, logged in `docs/CORRECTIONS.md` and knotlab's HISTORY.md: words for a drawn space in `SHIFT-LOCK-20261112-001`'s record (tilings,
cell types, slope polygon, slope rule) and in this epic's pre-registration (line, linear), replaced by lifted phases, step pairs, the
mean-step bounds, ratio subgroups and additive automata, with the literature's names given once. Not a block.

## In the owner's words

Copies of a repeating pattern, tied across two directions, can make two-dimensional patterns, but never ones that behave like
arithmetic on a grid of numbers, where one value spreads its influence by adding. That kind of influence needs a knot where any two
members decide the third, and the not-all-equal law on repeating patterns can't make one: if it could, some pattern would have a single
place free to flip, and repeating patterns have none. Parity knots can, which is why Ledrappier's law does it.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — lines in the increments | **Status:** Successful, referee pending | proved for unlagged stitches; none for lagged ones on 105 harmonies |
| Local direction — two-shift arrangements of harmonies | Exhausted for additive influence | the theorem closes it; the mean-step rule is still unproved |
| Broader exploration — G17's census | Known alternatives | mixed laws (parity among not-all-equal); the knots-alone thread's travelling bases |
| Long-term goal — G17 Typical and rare meeting patterns | Obstruction learned | stitched harmonies' influence stays tied to cycles |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the mean-step rule (`SHIFT-LOCK-20261112-001` #2) | 2/3 — Substantial | 3/3 — Ready | for 0011 + 01: every non-constant state is a lifted phase on the orbit of 0011, and every pair of total steps the bounds allow is realised → its lock set at every size | Selected · awaiting go-ahead |
| 2 | A parity knot among stitched copies | 2/3 — Substantial | 2/3 — Testable | put one permutive (parity) knot shape into a two-shift arrangement of not-all-equal stitched copies → square lock sets against Ledrappier's arithmetic, or frozen | Alternative · deferred |
| 3 | Permutive sub-stitches across orbits or after blocking | 1/3 — Incremental | 3/3 — Ready | extend the census to triples across orbits and to pairs of copies as one symbol → none, or one | Alternative · deferred |

**Corrections:** one (words for a drawn space; Not a block). **Goals:** G17 checkpoint (obstruction learned, with G8; no goal change).
**Assumptions:** A70, A75, A77 used; none added. **Basket:** #2, #3 recorded; #1 is `SHIFT-LOCK-20261112-001` #2. **Advisor:** consulted
twice: before the freeze (it repaired the criterion, gave the two-constant-fibres lemma and designed the base-16 test) and on the new
words.

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 12:30 UTC, verbatim:

> Done: lines in the increments. The write-up is research/LINE-LOCK-20261112-001/line_lock.md. The referee is pending.
>
> • **The theorem (proved).** A harmony's stitch can't contain a permutive sub-stitch, that is, triples where any two members decide the third. If it did, the members' bits would be forced constant and opposite at some place. That place could then be flipped once, giving a state that never repeats, and a harmony has none. So no harmony at any period carries the additive automaton that Ledrappier-type influence needs. The odd harmonies 61, 73 and 193 are covered by the proof without a run.
> • **Lagged stitches too (exact).** I checked all 187 orbits of 73 harmonies (span up to 8 at every period, plus the 7 odd step sets). None holds a coset with a ratio part, so no lagged stitch carries one either. One size past, 32 more harmonies of span 9 show the same.
> • **What it means.** The two-way patterns these harmonies make never spread influence the way Ledrappier's law does. That needs a permutive knot like parity, and the not-all-equal law on repeating patterns can't supply one. Prior work: Ledrappier, Kitchens–Schmidt, and Salo's three-point permutive subshifts. Neither the advisor nor I has seen the lemma stated before, so novelty is pending the referee's search.
> • **Test for the knots-alone thread (frozen, theirs to run).** On base 16, for each travelling pattern not certified up to period 8, list the repeats up to 24 × 24 (sheared ones included) that certify it. My reading predicts the list is non-empty and fixed by a divisibility rule, the same for every pattern with the same travel vector. It also predicts that some local feature has an equal count on parallel rows. It's refuted if nothing certifies to 24 × 24, if every size past a threshold works, or if the counts vary. A wrap-around overlap check is the rival.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — lines in the increments | **Status:** Successful, referee pending | proved for unlagged stitches; none for lagged ones on 105 harmonies |
> | Local direction — two-shift arrangements of harmonies | Exhausted for additive influence | the theorem closes it; the mean-step rule is still unproved |
> | Broader exploration — G17's census | Known alternatives | a parity knot among not-all-equal copies; the travelling bases |
> | Long-term goal — G17 Typical and rare meeting patterns | Obstruction learned | stitched harmonies' influence stays tied to cycles |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Prove the mean-step rule (last epic's #2) | 2/3 — Substantial | 3/3 — Ready | for 0011 + 01, every state is a lifted phase and every allowed pair of total steps is realised → its lock set at every size | Selected · awaiting go-ahead |
> | 2 | A parity knot among stitched copies | 2/3 — Substantial | 2/3 — Testable | one parity knot shape in a two-shift arrangement of not-all-equal copies → Ledrappier's arithmetic, or frozen | Alternative · deferred |
> | 3 | Permutive sub-stitches across orbits or after blocking | 1/3 — Incremental | 3/3 — Ready | extend the census → none, or one | Alternative · deferred |
>
> **Corrections:** one, Not a block. I replaced words for a drawn space in the last epic's record ("tilings", "slope polygon") with "lifted phases" and "mean-step bounds", and the literature's names are given once. **Goals:** G17 checkpoint (obstruction learned), no goal change. **Assumptions:** none added. **Basket:** #2 and #3 recorded; #1 is the last epic's #2. **Advisor:** consulted twice. Before the freeze it repaired my criterion, supplied the lemma, and designed the base-16 test. Then it checked the new words.
