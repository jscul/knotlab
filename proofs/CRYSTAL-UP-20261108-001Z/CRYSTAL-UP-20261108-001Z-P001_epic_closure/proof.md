# Closure of the crystal one level up

Status: Proved

Ticket `CRYSTAL-UP-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/CRYSTAL-UP-20261108-001/crystal_up.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Growing tori from the 203 off-law parent collars of s = 10101 / 00110 on lattices spanned by periods from their own patches, 7 non-pinwheel collars complete 26 periodic parent tilings of 8 to 40 tiles per period, half their tiles turned by arctan(4/3) from the other half, whose cuts obey the decoration's law (E002; E001 stopped). | exploratory experiment | A |
| 2 | Every one of the 1,024 one-bit decorated substitutions of the pinwheel admits a crystal at every radius; the sixteen the exact census left open are settled by certificates checked with independent code. | no-overlap-found; proved | B |
| 3 | Correction to `LAST-BIT-20261108-001` (not a block): its forcing route needed every off-law parent collar to die, the 50 pinwheel collars with off-law labels included. | correction | `docs/CORRECTIONS.md` |

## Answer

One hidden bit per tile, placed by a decorated substitution, never forces the pinwheel: the last decoration falls to crystals that
mix two tile orientations a turn of arctan(4/3) apart.

## Stress test

At tile distance 3 the extension test reaches a fixed point with 109 non-pinwheel and 39 off-law pinwheel parent collars alive (two
rounds removed 26, then 24); the run was stopped at the start of distance 4 once the crystals settled the question, and every
labelled parent collar of the 26 crystals is among the survivors (`research/CRYSTAL-UP-20261108-001/stress_crosscheck.py`).

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions**, selected: bond distance against chain distance, a challenge of A12 (backlog B4). Rated Payoff 2/3
(Substantial), Concreteness 3/3 (Ready). The table is in the decision note.
