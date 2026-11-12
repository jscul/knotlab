# Which parity placements survive

Epic `PARITY-SURVIVE-20261112-001` (`PARITY-MIX-20261112-001` direction 1, reshaped by the coordinator; G17 with G8; program
mathematics, group arithmetic), 2026-11-12. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `d4d3c753b`.
Proof family: `proofs/PARITY-SURVIVE-20261112-001A/`. **Refereed: confirmed, three small fixes** ([referee R1](referee-R1/report.md);
folded in below and logged in `docs/CORRECTIONS.md`).

## The question

Flip-blind parity knots and not-all-equal stitches rarely coexist among harmony copies (`PARITY-MIX-20261112-001`). Which placements
survive, how common is survival as size grows under one stated weighting, and does fixing pass through the not-all-equal stitches, or
is it parity's own arithmetic inside the copies it surrounds (the coordinator's worry, with "fixed but unreached" nearly automatic
when propagation can only use parity)?

## The answer

**For one kind set per harmony (the census's), survival is rare and decays with size; where it happens, most of the influence goes
through the not-all-equal stitches, not through parity's arithmetic. The rarity is a property of that kind set, not of the harmony
(PARITY-MIX's referee, after this epic closed).**

- **Lemma A (a census, for the census's kind sets).** In all 8 harmonies that have flip-blind triples, the stitch allows none of them
  under the kind set used. It is false in general: under 12 of the 96 kind sets of span at most 8 that present the 8 harmonies, the
  stitch does allow flip-blind triples, and there survival is 21.8% on 3 × 3 and, for 0011 + 01 with kinds (1, 3) and (5, 6), 12.6% on
  4 × 4 at every k (PARITY-MIX's referee).
- **Rare for one kind set (exact per sample).** With each cell parity independently with probability ρ, under 1% of placements survive
  at every ρ from 1/8 to 7/8 for every n ≥ 6, and none of 11,997 samples at 7 × 7 to 9 × 9 (the referee ran the cell cut by the cap: 0 of 500), for the census's kind set of
  each harmony.
  A claim about the harmony would need the kind set drawn as part of the weighting (uniformly among the kind sets that present it);
  with 12 of 96 such kind sets mixing freely, that claim is not established and may fail. Sizes divisible by 3 do best. The annealed first-moment
  rate (each cell's triple treated as independent) is negative for almost every harmony and ρ; it suggests survival falling like
  e^{λ n²}, but that is unproved: the exact first moment is a sum over the repeat's states.
- **No simple rule (exact on 3 × 3 and 4 × 4).** Neither frozen rule holds. Knowing only which class each copy is in is not enough: on
  705 placements the classes fit but no choice of states does. And one placement class survives with an isolated parity cell.
- **Where the fixing comes from (the coordinator's question).** Over every surviving placement on 3 × 3 and 4 × 4, fixing from every
  base count:
  - 10% comes from the parity equations alone;
  - 14% needs the harmony's states as well;
  - 76% needs the not-all-equal stitches;
  - 37.7% is beyond arc consistency (the referee, with no cap on count-r₀ assignments; 36% with the cap of 30).

  On the sampled survivors at larger sizes the split is 38%, 25% and 37%, with 27.7% beyond arc consistency (25% with the cap). The
  pair totals (9,598; 347) count each placement's pairs once per base count, n times, so they are shares, not placement counts. So the worry does not
  hold. "Fixed but unreached" was partly automatic in the earlier epic, but against the fair baseline a quarter to a third of the
  fixing is still non-local, and most of it passes through the stitches.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Lemma A: no flip-blind triple is a stitch triple (8 of 8 harmonies) | exact census (frozen) |
| Survival under 1% at every ρ for n ≥ 6; none in 11,997 samples at 7 × 7 to 9 × 9 | exact per sample (frozen; 55 of 56 cells, cap; the last cell by the referee) |
| Class-level fit not enough (705 placements); one survivor with an isolated parity cell | exact on 3 × 3 and 4 × 4 (frozen) |
| Fixing split: L 10%, P not L 14%, stitches 76%, beyond arc consistency 37.7% (small); 38 / 25 / 37 / 27.7% (samples) | exact (frozen; refereed, uncapped) |

## Against the pre-registration

Lemma A (99%): met. Lifting never binds (mine, 55%): **not met**. Isolated parity cells fatal (80%): **not met** (one class of 8
placements). Survival decays with n; order 3, 6, 9 ≫ 7 > 5 ≫ 4, 8 (70%): partly (divisible by 3 best; 9 and 7 had no survivor). Rare
(mine, 80%): met. Fixing beyond arc consistency (85%): met. Almost all fixing in L (75%): **not met** (10% and 38%). Stitches' share
under a tenth (60%): **not met** (76% and 37%). The scale part hit its one-hour cap with 55 of 56 cells saved (the seven-orbit
harmony at 9 × 9 missing) and is reported with the cells reached, as frozen (`assemble_after_cap.py`); the small part finished in
58 minutes, near its cap.

## Known mathematics

The triangular plaquette model (Newman and Moore); linear cellular automata on rings (Martin, Odlyzko and Wolfram); mixed hypergraph
colouring with C- and D-edges (Voloshin; Kündgen, Mendelsohn and Voloshin), which the class-level system of 0011 + 01 is; uniquely
extendible constraints (Connamacher and Molloy); (2 + p)-SAT and locked problems; Schaefer. No mechanism is claimed new; the survival
rates under one weighting and the split of fixing are new data.

## What it changes

- **For the owner's "globally influential".** Mixing an additive knot into patterns of not-all-equal copies does let influence travel
  further than any knot passes it, and most of that influence runs through the not-all-equal ties themselves. But such mixtures almost
  never exist once the pattern is bigger than a few copies across: as a way to make influence global, it is rare, and rarer with size.
- **The window-bond test (the knots-alone thread, `SHIFT-COUNT-20261112-001` ticket C).** The repeat-size test frozen in
  `LINE-LOCK-20261112-001`'s pre-registration refuted the lifted-phase reading for base 16's patterns. 9 of 21 uncertified travelling
  patterns, base 16's two among them, have no certifying repeat up to 24 × 24. 4 are carried at every size past a threshold, and 8
  survive weakly. The reading was proposed, not asserted, in `SHIFT-LOCK-20261112-001`'s note, so this is an outcome recorded, not a
  correction.

## Assumptions

A70, A75, A77, A78 used; none added.

## Corrections

After this epic's referee (R1), one entry, Not a block, logged in `docs/CORRECTIONS.md` and knotlab's HISTORY.md: the share beyond arc
consistency without the cap (37.7% and 27.7%), the pair totals as shares counted per base count, and the first-moment decay marked
unproved. After PARITY-MIX's referee (R1), one here, logged in `docs/CORRECTIONS.md`: the rarity and lemma A hold for one kind set per harmony,
not for the harmony (Narrowing). Before it: none in this epic's claims. The word "star" for a copy's three knots, used in `PARITY-MIX-20261112-001`'s record, is the literature's
word for a vertex's neighbourhood; replaced there by "a copy's three knots" and logged in `docs/CORRECTIONS.md` (Not a block).

## In the owner's words

A parity tie dropped among not-all-equal ties almost always breaks the pattern, and the bigger the pattern, the surer that is. In
the rare mixtures that survive, though, one line of copies does decide others, and three quarters of that deciding runs through the
not-all-equal ties, not through parity's own arithmetic. A third of it can't be seen by checking ties one at a time.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which parity placements survive | **Status:** Successful, referee pending | rare and decaying; fixing mostly through the stitches where it survives |
| Local direction — mixed laws on stitched copies | Exhausted for typical influence | rare at every density; no simple survival rule |
| Broader exploration — G17's census | Known alternatives | lagged free pairs; the travelling bases' own line |
| Long-term goal — G17 Typical and rare meeting patterns | Obstruction learned | additive mixtures make global influence only rarely |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Lagged free pairs (`LINE-LOCK-20261112-001` #R1) | 2/3 — Substantial | 2/3 — Testable | on the 20 harmonies whose lagged stitches hold free pairs, lagged mixed-knot arrangements at those lags: lock sets and copies tied to copy 0 against the unlagged ones → a new influence route, or none | Selected · awaiting go-ahead |
| 2 | Why flip-blind triples are never stitch triples | 1/3 — Incremental | 3/3 — Ready | a proof for every harmony, or one where they meet | Dropped: false in general (12 of 96 kind sets) |

**Corrections:** one word correction in `PARITY-MIX-20261112-001`'s record (Not a block). **Goals:** G17 checkpoint (obstruction
learned, with G8; no goal change). **Assumptions:** A70, A75, A77, A78 used; none added. **Basket:** #2 recorded; #1 is
`LINE-LOCK-20261112-001` #R1. **Advisor:** consulted once before the freeze (it confirmed the class-level reading for three classes,
gave the fair baseline and the tiers, and the first-moment rate).
