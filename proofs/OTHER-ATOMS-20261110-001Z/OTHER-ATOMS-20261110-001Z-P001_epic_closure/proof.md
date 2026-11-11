# Closure of other pieces, a challenge of A48

Status: Proved

Ticket `OTHER-ATOMS-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/OTHER-ATOMS-20261110-001/other_atoms.md`.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, and an atom (a Fano or torus atom) a piece (Intuitions guide, Glossary). The mathematics is
unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A torus piece acts as its replaced knot exactly where its torus is unsatisfiable and is transparent where it is satisfiable, if the torus is free at the removed distinction; where it acts it holds a unit; so the piece rule holds for such pieces on any Kasteleyn host, pieces adjacent or not. | proved by hand, given two facts per torus | A |
| 2 | On 29 named piece types, 60 splices each: the 8 class-forced ones act in exactly their torus's unsatisfiable class, the 21 all-satisfiable ones are transparent. | exhaustive computation | A |
| 3 | R-a and R-b on 960 classes of two- and three-piece patterns on K_3 for four piece types. | exact (SAT over every state) | B |
| 4 | 72 of 72 addresses written in sequence and held, with the Fano piece and three thin-torus pieces. | computed | C |
| 5 | All 157 lattice-torus types to 30 distinctions (thin of even index to 40) are free in every class; the class-forced ones are the Fano torus and one thin torus per even index, each with one unsatisfiable class. | exhaustive computation | D |

## Answer

The learned memory does not need the Fano pattern: it needs a torus with a class no state satisfies. A48 overturned as a limit, replaced
by A52.

## Recommendation

**Research directions:** pieces within pieces (backlog B104), awaiting a go-ahead.
