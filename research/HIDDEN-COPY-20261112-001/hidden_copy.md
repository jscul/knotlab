# Influence through hidden copies

Epic `HIDDEN-COPY-20261112-001` (the open route of `LINE-LOCK-R1`; G17 with G8; program mathematics, group arithmetic), 2026-11-12.
Pre-registered in [preregistration.md](preregistration.md), frozen in commit `44e339263`. Proof family:
`proofs/HIDDEN-COPY-20261112-001A/`. **Refereed: confirmed, one wording note** ([referee R1](referee-R1/report.md); folded in below
and logged in `docs/CORRECTIONS.md`). The last epic of this line for now: the owner asked to curb token use, and the
coordinator asked this thread to close and stop.

## The question

Can a gadget of harmony copies joined by not-all-equal stitches, some copies hidden, give an additive relation on the copies it shows,
the kind of law behind Ledrappier-type influence, and how common is that?

## The answer

**In principle yes, for some harmonies; in practice not found. By the frozen criterion, no.**

- **Settled by definition.** A gadget of stitched copies always allows all its copies equal, so it can never make flip-blind parity. A78's
  parity gadget is built from bare not-all-equal knots on single distinctions, which is a different object.
- **Frozen census.** The cap stopped it after 17 of the 40 harmonies, in the order run, over 1,001 kind sets; the other 23 are
  unclassified. Among the 17 reached, for the single-orbit harmonies the only self-maps of the states keeping the stitch are
  symmetries and constants (E-small); most multi-orbit ones have more (E-large).
  No E-small case has the three symmetry orbits the frozen construction needed. None of 486,000 small gadgets (at most two hidden
  copies, at most three stitches) gives an additive readout, while 2 of 54 random relations of the same size do. **The frozen failure
  criterion is met.**
- **After the run (the advisor's second check; known theorems, labelled).** Every E-small case reached is essentially unary, by Pálfy's
  theorem and a cycle argument, with no search needed. A gadget relation is then exactly a relation that contains every all-equal
  triple and keeps the symmetries. So any split of the states into three symmetric classes gives one: "the three copies' classes are
  all equal or all different", Ledrappier's law over Z₃.
  - 102 of 318 E-small kind sets have such a split.
  - Six harmonies have it under every kind set reached: 000111, 000000111111, 001010110101, 000111 + 01, 0000011111 + 01 and
    0010011011 + 01.
  - The gadget this argument gives is astronomically large (about 6^11 copies for 000111), and none appeared among the small ones.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Stitched-copy gadgets never give flip-blind parity | proved (definitional) |
| Among the 17 harmonies the cap reached (in run order; 1,001 kind sets), E-small for the single-orbit ones, E-large mostly for the multi-orbit ones | exact (frozen; capped) |
| No factor-permutive relation among 486,000 small gadgets; 2 of 54 random baselines have one | exact (frozen) |
| Every E-small case essentially unary; three invariant classes give a mod-3 factor-permutive gadget relation (102 of 318) | after the run, by known theorems (Pálfy; Jablonskij; Geiger; Bodnarchuk and co-authors); confirmed by the referee (102 exact on the full lattice) |

## Against the pre-registration

Essentially unary in every E-small case (95%): met (136 by search, all 318 by the argument after the run). Affine never above 4 states
(90%): met (never). Aut equal to the shifts and flips for most pairs (70%): met (69 of 1,001 have more). Most harmonies E-small (55%):
10 of the 16 whose census kind set was reached (the alternation among them), met on the range reached. Some pair admits factor-permutive influence (75%): not by the
frozen construction; yes by the wider one after the run. A gadget with at most two hidden copies shows it (20%): not met. The endo part
stopped at its cap (1,001 of 1,267 pairs), the binary part was relaunched once after a failed start, and the after-run check was cut
down once after a run that was too slow; all disclosed in the proof.

## Known mathematics

Pálfy (1984) on permutational algebras; Jablonskij's lemma (with constants, an essential operation of two or more variables gives
an essential binary one), the referee's credit for the elementary step; Geiger (1968) and Bodnarchuk, Kaluzhnin, Kotov and Romov (1969) on the Galois correspondence;
Ledrappier's three-dot law and its mod-3 analogue; Schaefer for bare not-all-equal. The algebra is not new; the classification of the
harmonies and the census are new data.

## What it changes

- **For the owner's "globally influential".** Patterns of copies tied the not-all-equal way can, in principle, build a mod-3 adding
  law out of hidden copies when their states split into three symmetric classes. But the gadgets that do it are far too large to
  appear in small arrangements, so as a mechanism for influence that actually arises in patterns, it stays theoretical.
- **The line.** Across the last six epics, stitched harmonies carry influence through cycles, rarely through parity mixtures, and only
  in principle through hidden copies. That is a reasonable place to stop, as asked.

## Assumptions

A70 and A78 used (A78's scope is noted in its history); none added.

## Corrections

After the referee (R1, confirmed), one entry, Not a block, logged in `docs/CORRECTIONS.md` and knotlab's HISTORY.md: "E-small is
common for single-orbit harmonies and rare for multi-orbit ones" holds for the 17 harmonies the capped census reached, in the order
run, not for the 40; the note now says so, and the same sentence in the proof's "What this establishes" (immutable) is read with
that scope. The referee also confirmed that all 318 E-small pairs are certified without the binary search (145 by |W| not a prime
power, 140 by a single |W|-cycle, 33 by an intransitive Aut), so the binary part's relaunch does not bear on the result. Before it:
none.

## In the owner's words

Copies of a pattern tied the not-all-equal way can never build a parity tie, because making everything equal always fits. But for
patterns whose states fall into three symmetric groups, hidden copies can in principle build an "all the same or all different" rule,
which is arithmetic mod 3. The construction is enormous, though, and no small one exists in what I searched. So it's possible in
theory, not something that shows up in practice.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — influence through hidden copies | **Status:** Successful, referee pending | frozen criterion met (no); a wider existence after the run |
| Local direction — stitched harmonies | Stop (as asked) | cycles, rare parity mixtures, theoretical hidden copies |
| Broader exploration — G17's census | Known alternatives | the travelling bases (the other thread) |
| Long-term goal — G17 Typical and rare meeting patterns | Obstruction learned | additive influence from stitched harmonies is rare or only theoretical |

**Next step:** Research directions — none selected (the owner and coordinator asked to stop; recorded in the basket for later).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A practical mod-3 gadget | 2/3 — Substantial | 1/3 — Exploratory | search gadgets with Z₃ class readouts for 000111 beyond two hidden copies → the smallest gadget, or none to a bound | Basket · deferred |
| 2 | Finish the self-map classification | 1/3 — Incremental | 3/3 — Ready | the 23 harmonies the cap did not reach | Basket · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (obstruction learned, with G8; no goal change). **Assumptions:** none added.
**Basket:** #1, #2 recorded; the mean-step proof stays there. **Advisor:** consulted twice: before the freeze (the self-map test, the
targets) and after the run (the mod-3 construction, the certificate for the unsettled cases).

## Final report as sent

**Influence through hidden copies is closed (referee pending), and with it this line stops, as you asked.** In principle yes for some harmonies, in practice not found; by the frozen criterion, no.

- Copies tied by not-all-equal stitches can never build a parity tie, since all copies equal always fits.
- By known algebra (Pálfy; the Galois correspondence), the 102 of 318 cases whose states split into three symmetric classes can build "all equal or all different", Ledrappier's law mod 3, but only with gadgets of impractical size (about 6^11 copies). None of 486,000 small gadgets gives an additive readout, while 2 of 54 random baselines do.
- The self-map census stopped at its cap with 17 of the 40 harmonies; disclosed.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: influence through hidden copies | Successful, referee pending | frozen criterion met (no); mod 3 exists after the run |
| Local direction: stitched harmonies | Stop (as asked) | cycles, rare parity mixtures, theoretical hidden copies |
| Broader exploration: G17's census | Known alternatives | the travelling bases (the other thread) |
| Long-term goal: G17 | Obstruction learned | additive influence from stitched harmonies is rare or only theoretical |

**Next step:** none selected; both directions wait in the basket.

| # | Direction | Payoff | Concreteness | Status |
| --- | --- | --- | --- | --- |
| 1 | A practical mod-3 gadget | 2/3 | 1/3 | Basket · deferred |
| 2 | Finish the self-map classification | 1/3 | 3/3 | Basket · deferred |

**Corrections:** none. **Goals:** G17 checkpoint, no goal change. **Assumptions:** none added. **Basket:** #1, #2. **Advisor:** consulted twice. Note: `research/HIDDEN-COPY-20261112-001/hidden_copy.md`.
