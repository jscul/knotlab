# Closure of other atoms, a challenge of A48

Status: Proved

Ticket `OTHER-ATOMS-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/OTHER-ATOMS-20261110-001/other_atoms.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A torus atom acts as its replaced line exactly where its torus is unsatisfiable and is transparent where it is satisfiable, if the torus is free at the removed point; where it acts it holds a unit; so the atom rule holds for such atoms on any Kasteleyn host, atoms adjacent or not. | proved by hand, given two facts per torus | A |
| 2 | On 29 named atom types, 60 splices each: the 8 class-forced ones act in exactly their torus's unsatisfiable class, the 21 all-satisfiable ones are transparent. | exhaustive computation | A |
| 3 | R-a and R-b on 960 classes of two- and three-atom spaces on K_3 for four atom types. | exact (SAT over every state) | B |
| 4 | 72 of 72 addresses written in sequence and held, with the Fano atom and three thin-torus atoms. | computed | C |
| 5 | All 157 lattice-torus types to 30 points (thin of even index to 40) are free in every class; the class-forced ones are the Fano torus and one thin torus per even index, each with one unsatisfiable class. | exhaustive computation | D |

## Answer

The learned memory does not need the Fano plane: it needs a torus with a class no state satisfies. A48 overturned as a limit, replaced
by A52.

## Recommendation

**Research directions:** atoms within atoms (backlog B104), awaiting a go-ahead.
