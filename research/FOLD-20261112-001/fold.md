# A direction the knot law does not lengthen

Epic `FOLD-20261112-001` (`BOND-BALLS-20261111-001` direction 1; G1, question 9; program topology, group spacing), 2026-11-12, at the
coordinator's go-ahead under the owner's standing mandate. Pre-registered in commit 66a30a06f; ticket A's exact check was run before
freezing and is disclosed as such; ticket B's census ran after. The canonical K1–K3 test is unchanged.

## Words

As in the guide's glossary, `BOND-BALLS-20261111-001` and the pre-registration: steps apart, bond, bond distance, ball, shortcut, base
16, the sheared frame, the travelling triple, and a base that folds to six steps.

## The question

On base 16 the not-all-equal law (NAE) kept distinctions twelve steps away at bond distance 3. Is that so at every distance, is it
settled by how the base was supplied, how does it square with the faithful reading, what is the law's ball there, and which other
shortcut bases fold?

## The question in standard terms

For the proper 2-colourings of the periodic 3-uniform hypergraph with edges {z, z+(0,1), z+(1,−1)} and {z, z+(0,2), z+(1,1)}, are the
four-sets made of a translated column triple and the origin minimal non-shattered at every distance; and which of 42 related periodic
hypergraphs have such four-sets at distances 5 and 6?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The fold holds at every distance (Theorem F).** For every k ≥ 3 (and k = 2) the origin's own triple with any distinction k columns on, and the triple k columns back with the origin (a translate), are bonds of four; every pair of the origin with one of those far distinctions is free. So the law keeps a whole line through the origin, in both directions, at bond distance at most 3 though it lies k steps away. | proved (a hand proof of the forcing; an exact finite check of the freeness, valid for every k); refereed | A |
| 2 | **Not an artefact of the supply.** Steps apart depend only on which pairs are co-knotted, bond distance only on the states, and both are unchanged by any re-presentation of the base, so the gap between them is intrinsic; the step metric is genuinely two-dimensional (shells 10, 26, 40, 54) and the far distinctions are k steps away. The fold runs along the pair class that lies in two knots: it is the law's "two equal force the third opposite", iterated. | proved | A |
| 3 | **The faithful reading stands.** The law ties the origin to no single far distinction; it binds the origin only jointly with a whole triple, and only when that triple is all equal. | proved | A |
| 4 | **The law's radius-3 ball is infinite.** By translation it contains ten distinctions for every k ≥ 3, all exactly k steps away, on a line both ways: at least linear growth in steps at a fixed bond radius. Their bond distance is exactly 3 at k = 4 to 6 (computed). What else the ball contains, and the balls of larger radius, are not claimed. | proved (lower bound) | A |
| 5 | **Which shortcut bases fold.** With the bond's two other distinctions within one step of the far one, 16 of BOND-BALLS's 42 shortcut bases fold to six steps, all among the 18 with a four-step shortcut (prediction G held); none of the 24 others does. Up to change of lattice basis that is 14 of 16 classes, none of the 22 others; the two four-step classes that do not fold (81, 88) showed no bond of four at five or six steps in the referee's broader search either. Only base 16 (≅ 40) is proved to fold at every distance. | computed, frozen; refereed | B |

## Answer

Yes, at every distance: on base 16 a triple of equal distinctions forces the next triple over, column after column, so the law binds
the origin to distinctions arbitrarily many steps away at bond distance 3, along a whole line in both directions. It is the law doing
this, not the way the base was supplied: steps apart and bond distance are both intrinsic, the step metric is two-dimensional, and the
line runs along the one pair class that two knots share. The faithful reading is untouched, since no single far distinction is tied to
the origin. Of the 38 classes of bases with shortcuts, 14 fold this way to six steps, exactly among those whose shortcuts already
reached four steps.

## Reading

**Interpretation, not a theorem.**
- **A space the law makes.** The meeting pattern gives base 16 two shifts and a step distance growing along both. Read by the law alone,
  one direction has no length: the law sees a base compressed along that line, which the owner's "folded, compressed" structure names.
- **Where the fold comes from.** The direction is the pair class covered twice. Overlap, a pair in two knots, is what lets a whole
  triple push its values one column on; without the second knot kind it stops at once.
- **For question 9.** Dimension read natively by balls is not defined here in the usual way, since a ball of bond radius 3 is already
  infinite; the law's geometry is degenerate along the fold. Whether the base reads as a line across the fold (one dimension left) is
  the next measurement.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic. **Proved.** Theorem F, its reconciliations, and the ball's lower bound, for base 16 only.
  **Computed.** The classification of the 42 shortcut bases, to six steps, with bonds of four sought within one step of the far
  distinction.

## Stress test

The theorem holds at every k by the transfer graphs' eventual periodicity (periods 2 from k = 9 for m = 3 to 8); the reproduction in
`BOND-BALLS-20261111-001` found the same bonds at k = 3 to 12 with independent bounds. The classification agrees with that epic's
referee, who found the same 14 of 16 tested four-step bases folding.

## Review

An independent referee (its own code in the original frame: window SAT for constraint; doubly periodic states from 822 finite repeats
and an exact transfer computation for freeness) found Theorem F true and every recorded fold bond sound, and:
- **corrected the shear's image of B_k** (rows −2 to 0, not 0 to 2): B_k is a translate of F_k^2, so the statement stands and C2 repeats
  a translate of F_k^0; verified freeness and the two refuted patterns (0000/1111 at odd k, 0001/1110 at even k) at k = 2 to 12, 20,
  37, 100, 101, and at k = 50 that the forcing is the only constraint;
- **found the ball understated**: ten distinctions per k, exactly k steps away (k = 2 to 25), bond distance exactly 3 at k = 4 to 6;
- **replaced the pair-count argument** for "not an artefact" by invariance (the pair-count claim was unproved and not needed);
- **found a range slip in ticket B's bounds**: the one-shift repeats' window is exact only within span + 7 of the origin along its free
  coordinate, and 32 part-patterns (on ten bases) were settled beyond it; its own exact transfer computation realizes every one, so no
  verdict changes. Patterns that force a travelling triple cannot be carried by any doubly periodic state, so torus-only witnesses would
  misjudge them;
- **counted classes**: 14 of 16 four-step classes fold, none of the 22 others; and pointed to Ledrappier's three-dot shift (1978) and
  Kitchens and Schmidt's non-mixing shapes (1993) as the nearest precedent.

## Literature and provenance

- **Known.** The nearest precedent is Ledrappier's three-dot shift (1978; its states are the Newman–Moore ground states): parity on the
  same up-triangle meeting pattern as base 16's first knot kind, where every pair is free but a set of three at 2^n steps is
  constrained for every n, the non-mixing shapes of Kitchens and Schmidt (1993). Related: failures of strong irreducibility and block
  gluing where pairs mix (Boyle, Pavlov and Schraudner 2010), signals in two-dimensional shifts of finite type, expansive subdynamics
  (Boyle and Lind 1997), transfer matrices of one-dimensional shifts.
- **Not found** (bounded search): the same for not-all-equal, with four-element bonds at every distance along a line, read as bond
  distance.
- **Classification.** Known-with-delta, folklore risk moderate to high for the mechanism.

## Workspace assumptions

- **Relied on.** A64, A67. **Changed.** None.

## Ratio

- **Substantive.** The proof and its exact check, the classification census, one referee pass.
- **Administrative.** The pre-registration, this note, the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (**Not a block**), on the published pre-registration and proof draft: the proof gave the shear's
image of B_k with the wrong rows (the statement stands, as a translate); the pre-registration argued from pair counts that no base with
the same counts repeats along one shift only, which is unproved and not needed; and its definition of folding (any bond of four at five
and six steps) is broader than the census's search (the bond's other two distinctions within one step of the far one). Ticket B's
frozen bounds also settled 32 part-patterns beyond their exact range; every one was confirmed exactly by the referee, so no verdict
changed (recorded here, not a correction).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a direction the knot law does not lengthen | **Status:** Successful | Proved on base 16 at every distance; 14 folding classes found |
| Local direction — the law's geometry on folding bases | Continue | Across the fold, does the law read a line? The other 26 shortcut bases need a rule |
| Broader exploration — G1 on bases of knots alone | Known alternatives | Rigid periodic states; reading by pair counts |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A law can read its own lower-dimensional geometry off a two-shift meeting pattern (proved, one base) |

**Corrections:** one, Not a block (the proof's shear image, the pre-registration's pair-count argument and its fold definition). **Goals:** a G1 checkpoint (capability gained), no goal change. **Assumptions:** none changed.
**Basket:** `BOND-BALLS-20261111-001#2` (the other shortcuts, 2/3, 3/3), `PERIODIC-READ-20261111-001#2` (rigid periodic states, 2/3,
2/3), `OVERLAP-READ-20261111-001#4` (reading by pair counts, 2/3, 1/3); taken: none yet; direction 1 below is the first.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Across the fold: is it a line? | 3/3 — Major | 2/3 — Testable | On base 16, bound bond distance between distinctions on different lines of the fold (quotient by the fold) → the law reads one dimension across, or the quotient is degenerate too | Selected · awaiting go-ahead |
| 2 | The other shortcuts (was `BOND-BALLS-20261111-001#2`) | 2/3 — Substantial | 3/3 — Ready | For the 24 classes that do not fold, find the law's distance as steps under other moves → a rule, or none | Alternative · deferred |
| 3 | All fourteen folding classes, proved | 1/3 — Modest | 3/3 — Ready | Run ticket A's transfer proof on each (with exact ranges) → fourteen theorems, or a class where the fold stops past six steps | Alternative · deferred |

1. **Across the fold.** Payoff 3: dimension read natively on the first base where the law makes its own geometry. Concreteness 2.
2. **Other shortcuts.** Payoff 2, concreteness 3.
3. **Fourteen proofs.** Payoff 1, concreteness 3.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
