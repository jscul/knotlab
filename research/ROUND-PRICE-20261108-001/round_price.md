# The price of roundness in the plane

Epic `ROUND-PRICE-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it comes from.** The selected next step of `COLLAR-PLANE-20261108-001`, started at the coordinator's go-ahead on
  2026-11-08 (G1, space from a law; A25).
- **What was known.** No undecorated local law of the pinwheel forces roundness: a cut crystal obeys every one. Decorated matching
  rules do force the pinwheel (Radin 1994), with large alphabets. So roundness in the plane costs hidden information, as on the
  sphere, where one hidden bit per incidence suffices.
- **The question.** How much? Start with one hidden bit per tile, in the form every known construction uses: a decorated
  substitution, in which Conway's cut gives each child a label fixed by its parent's label and its child index.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Labels read from the tiling add nothing.** If each hidden label is a function of a bounded window of the undecorated tiling, the cut rhombus crystal, labelled by the same function, obeys the labelled law at every radius after enough cuts. Child indices, and any finite part of a tile's address in the hierarchy, are such labels. Forcing information must be non-local. | proved | A |
| 2 | **For decorations the radius does not matter.** If a decorated substitution's collar law admits a crystal, its law of every radius admits a crystal after more cuts. | proved | A |
| 3 | **Most one-bit decorations fail.** Of the 1,024 decorated substitutions on two labels, 172 admit the rhombus crystal after one cut, 792 after two and 30 after three; of the other 30, 4 admit it after four and 8 admit the brick crystal after two to four cuts. So 1,006 admit a periodic plane at every radius. The other 18 exclude both crystals at every level tested. | proved (exact census) | A |
| 4 | **Parent labels come free.** For the 18 survivors, in every arc-consistent level-one collar the central tile's five children carry s(0) or s(1), so every parent's label is forced. If, besides, every surviving labelled parent collar obeyed the law, composition would be forced at every level, and the decoration would force the pinwheel. | proved | B |
| 5 | **The second half is not settled.** For each survivor, arc consistency leaves labelled parent collars outside the law: 30 to 250 non-key collars and 50 to 125 pinwheel collars with labellings the law does not list. One survivor and its relabelling admit a third crystal family, brick rows with diagonals of period 4, after three cuts. Sixteen one-bit decorations, eight up to relabelling, remain candidates. | proved (exact computation) | B |

## Answer

- **Lower bound.** Roundness in the plane costs hidden information that no bounded window of the tiling determines.
- **One bit.** One bit per tile, used as a decorated substitution, fails in 1,008 of 1,024 cases: the decoration's law, at every
  radius, allows a periodic plane.
- **Sixteen candidates.** In the other sixteen the bit already forces every parent's label, and the three crystal families tried do
  not get through. Whether one of them forces the pinwheel, which would make the plane's price one bit per tile, is open: the
  pairwise test leaves off-pinwheel parent collars for each.

## Reading

**Interpretation, not a theorem.**
- **Where the information lives.** A forcing decoration has to carry, at each tile, something about levels arbitrarily far up the
  hierarchy. A bit set by a decorated substitution does: it depends on the whole chain of ancestors' labels. Most choices still
  leave a crystal room, because the bit can be set consistently on a crystal's own hierarchy.
- **The surviving sixteen.** In each, the labels of children 0 and 4, at the parent's corners Q and P, differ between the two
  parent labels. A bit at the corners that remembers the parent is the shape a working decoration would take.
- **Beside the sphere.** On spheres one hidden bit per incidence forces roundness (`SPHERE-GROWTH-20261107-001`). In the plane the
  same price, one bit per tile, is not excluded, and for most ways of placing that bit it fails.

## Stress test

One size past each computed claim, in the epic itself.

| Claim | One size past | Result |
| --- | --- | --- |
| The 18 exclude the rhombus crystal at levels 1 to 3 (A) | Level 4 for every survivor of levels 1 to 3 | 26 of 30 still exclude it; 4 admit it (counted in conclusion 3) |
| The 18 exclude the two crystals tested (A) | A third family: the 16 brick-row planes with period-4 diagonals found by `COLLAR-PLANE-C1` | One of the nine, with its relabelling, admits one after three cuts; eight do not within three cuts (B) |

## Literature and provenance

- **Sources.**
  - **Decorated matching rules.** Radin (Annals of Mathematics 139, 1994) for the pinwheel; Mozes (1989) and Goodman-Strauss
    (Annals of Mathematics 147, 1998) for substitution tilings.
  - **Small aperiodic sets.** Jeandel and Rao (2021): 11 Wang tiles, and no fewer.
  - **Recognizability.** Solomyak (1998).
- **Classification.** Lemma 1 is the standard reason decorations are needed (known-with-delta). The one-bit census and the forcing
  test on the pinwheel: no-overlap-found, not a novelty claim.

## Workspace assumptions

- **Relied on.** A33 (a local law is read up to congruence) and A25, now confirmed in the plane.
- **Taken by default.** Hidden information is counted as labels per tile assigned by a decorated substitution (new entry A35). Labels
  on edges, as in Radin's rules, or labels a child takes from more than its parent, are not counted here.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions (A and B), and the in-epic stress tests.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — one hidden bit per tile | **Status:** Partially successful | 1,008 of 1,024 fail; 16 open |
| Local direction — decorated one-bit laws | Continue | Sixteen candidates, parent labels forced |
| Broader exploration — G1 lines | Known alternatives | Edge labels; spheres; growth |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | The plane's price is bounded below and probed at one bit |

**Corrections:** one, from folding in `COLLAR-PLANE-C1` (not a block: more crystals pass after one cut), and a wording fix to it
(the new crystals are brick rows, not grids), both logged in `docs/CORRECTIONS.md`. **Goals:** a G1 checkpoint (capability gained);
no goal change. **Assumptions:** A35 added; a history line on A25 (hidden information counted as labels per tile of a decorated substitution).

- **What is left open.** Whether any of the sixteen forces the pinwheel.
- **The missing bridge to G1.** An exact price: a decorated law, with its alphabet counted, that provably forces a round plane.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Settle the sixteen (G1) | 2/3 — Substantial | 2/3 — Testable | Radius-2 joint consistency on each candidate's surviving parent collars, then a search for a periodic plane built from them → a decoration that forces the pinwheel, or an escape for each | Selected · awaiting go-ahead |
| 2 | Two bits per tile | 1/3 — Incremental | 1/3 — Stated | Sampled two-bit decorations against the three crystal families → a rate of survival, or none | Alternative · deferred |
| 3 | A note: the pinwheel has no undecorated local rules, and one bit mostly fails | 1/3 — Incremental | 3/3 — Ready | The witness, the lemmas and the census for outside readers → a note that passes review | Alternative · deferred |

1. **Settle the sixteen.**
   - **Payoff 2.** A forcing decoration would set the plane's price of roundness at one bit per tile, beside the sphere's one bit
     per incidence; an escape for each would push it above one bit.
   - **Concreteness 2.** The survivors, their laws and both tests exist. The radius-2 test is slow in pure Python and needs a faster
     compatibility check.
   - **Uncertainty.** Whether deeper consistency closes the gap, or the survivors build a plane.
   - **Status.** Bound: one epic. Not started: the coordinator decides whether this thread takes it.
2. **Two bits.**
   - **Payoff 1.** It refines the census; it matters only if all sixteen fail.
   - **Concreteness 1.** 4^20 decorations; only samples or a structured family are feasible.
3. **A note.**
   - **Payoff 1.** It makes both epics checkable by outside readers.
   - **Concreteness 3.** Everything is in hand.
