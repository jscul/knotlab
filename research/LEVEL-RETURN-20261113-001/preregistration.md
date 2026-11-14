# Pre-registration: returns across levels

Epic `LEVEL-RETURN-20261113-001` (`ADDR-KNOTS-20261113-001#1`; G17, with G8; program topology, group spacing), 2026-11-13, at the
coordinator's go-ahead (22:22 UTC). Written before the registered run, after the exploration and the smoke test disclosed below. The
canonical K1–K3 test is unchanged. Words as in `ADDR-KNOTS-20261113-001` (address, level, address map, placement, tail class; the
fates; "within level 16").

## The question

`ADDR-KNOTS-20261113-001`'s census found 48 knot patterns placed by address maps that are dead at some level and alive at a later
one, 7 alternating with the level's parity from level 5 to 12. Do the returns and the alternation persist to level 16 when every
verdict is certified, and why do the seven alternate: can it be proved at every level, through the two-to-one map between levels?

## The question in standard terms

For the 48 NAE-3-SAT instance families {g₁x, g₂x, g₃x} on {0,1}ⁿ (n = 1..16) from the census: certified satisfiability (a checked
model, or an LRAT refutation checked independently), and for the seven period-2 families an all-n proof of satisfiability at one
parity of n and unsatisfiability at the other.

## Certification (frozen)

- **Patterns** built by the thread's generator (`certify.py`) and, independently, by the census's `addr.py` (Codex's); the two must
  agree at every case, or the case is invalid.
- **Alive:** CaDiCaL 2.1.2 (the binary shipped with the Lean toolchain, on this machine; no download) returns a model, checked
  against every knot. **Dead:** CaDiCaL writes an LRAT proof, checked by `lrat_check` (the thread's C checker, RUP steps only; the
  proof file deleted after the check, its size and SHA-256 kept). Anything else is **undecided**, its own cell. Gates
  (`gates.json`): the Fano pattern dead; 8 of 8 corrupted proofs and a truncated proof rejected; 400 of 400 random small patterns agree
  with brute force.
- **Run:** the shared runner (`scripts/longrun.py`), 48 × 16 level cases and 7 R4 cases, 6 workers, 2,400 s per case, 2 GB per case.

## Settled before the run (proved)

The all-level product check (`proofs/LEVEL-RETURN-20261113-001B/LEVEL-RETURN-20261113-001B-P001_alternation/prover.py`) reads a
state computed by a finite automaton on the address, and decides by finite reachability whether it is a state at every level of a
given parity from a given level on. It proved: for description #2 (swap [1,0,1], d0 [0,2,2], d1 [2,1,1]), the address's parity is a
state at every odd level n ≥ 3, and it fails at every even level from 4 (the first failing address 0010 in placement [0, 8, 10]); for
#3 (swap [1,0,1], d0 [0,2,1], d1 [0,1,1]), the first letter XOR the last is a state at every even level n ≥ 2. So the living half of
the alternation is proved at every level for two of the seven. Exploration found no state of this kind (up to the feature automata
tried) for the other five.

## Predictions and failure criteria (frozen)

| # | Prediction | Fails if |
| --- | --- | --- |
| R1 | The seven keep alternating at levels 13 to 16: alive exactly at their living parity. | A certified verdict at levels 13 to 16 against it (undecided levels are reported and do not count either way). |
| R2 | (a replay of the proof) #2's parity and #3's first-XOR-last are states at their living levels 13 to 16. | Any violated knot: the proof or the code is wrong. |
| R3 | Of the 41 other returning patterns, those alive at all of levels 10 to 12 (18) stay alive at every level 13 to 16, and those dead at all of 10 to 12 (16) stay dead, each in at least 75% of the decided. (Calibration on the census: from levels 7 to 9 to levels 10 to 12, 9 of 10 and 13 of 16 kept their fate.) | Below 75% in either group. |
| R4 | (the advisor's) For #2 at every even level 4 to 16, the parity state fails on exactly the two knots of placement [0, 8, 10] at x = 0ⁿ⁻²10 and 0ⁿ⁻²11, and the pattern without them is alive (certified). So every dead core at even levels holds one of the two. | More or other violated knots, or the reduced pattern not alive, at any even level to 16. |

Descriptive: each pattern's fates at levels 1 to 16; the smallest period p ≤ 4 of its fates on levels 5 to 16, if any; certificate
sizes; where a return happens in the 41.

## The proof attempt (ticket B)

The living half for the other five: wider feature automata, or a direct construction. The dying half: for #2, R4 reduces each even
level's death to the rest of the pattern forcing the two special knots' addresses equal; the attempt is to show that forcing at every
even level (a chain of knots that grows with the level, read from the certified refutations and forced equalities at levels 6 to 12),
and to look for the same few-knot reduction in #3. A proof, a partial proof, or a level where it fails is reported as found.

## Stop rule

One registered run, the proof attempt, its summary, a referee hand-off; report and hold. Nothing is claimed past level 16 except
what is proved at every level.

## Prior work in the program

`python3 -B scripts/track.py objects "patterns that die and come back across levels" --until 2026-11-13 --exclude LEVEL-RETURN-20261113-001`
`python3 -B scripts/track.py objects "satisfiability alternating with parity of the level two-fold lift covering" --until 2026-11-13 --exclude LEVEL-RETURN-20261113-001`
`python3 -B scripts/track.py objects "returning addressed patterns" --until 2026-11-13 --exclude LEVEL-RETURN-20261113-001`

The first is the object in the program's words, the second in standard terms, the third the population.

- `ADDR-KNOTS-20261113-001` — the same population (its rows 2 and 3): this study's source; it read levels 1 to 12 with an uncertified
  budgeted solver.
- `SHORT-DESC-20261112-001`, `NEST-READ-20261112-001` — relatives (nested fates); monotone fates in depth there, no returns.
- `PARITY-SURVIVE-20261112-001`, `KNOTS-ALONE-20261111-001` — unrelated objects found by the word parity.
- `BASES-WITHIN-20261112-001` (row 2, "ending and revival of outer knot patterns under lagged stitches") — a relative: revival under
  lagged stitches of harmonies, a different construction; this study's returns come from the two-to-one lift between levels.
- `BASES-WITHIN-20261112-001/1`, `SHIFT-COUNT-20261112-001/3` — unrelated.

None found on fates that alternate with the level.

## Prior work outside the program

Lamplighter-type automata with affine maps (Grigorchuk and Żuk) and their de Bruijn-like Schreier graphs; parity of the Gray code is
its last bit (classical; the computation behind #2's state); voltage graphs for two-fold covers (Gross and Tucker); the classification
of three-state two-letter automata (Bondarenko et al. 2008). Nothing found on two-colourings of these patterns by level parity (the
advisor's search from memory; to check at close).

## Advisor

Consulted before freezing ([advisor_design_question.md](advisor_design_question.md),
[advisor_design_answer.md](advisor_design_answer.md)): its hand proof of #2's parity state (confirmed by the product check), R4, the
calibration of R3, the second generator, the treatment of undecided levels and the negative controls on the checker are its.

## Exploration and smoke test disclosed

- Before this file, on levels already read by the census (to 12): dead cores (`exploratory/look.py`), linear states
  (`exploratory/mech.py`), automatic states with up to three states (`exploratory/auto_states.py`) and feature automata
  (`exploratory/feature_states.py`); the all-level proofs above.
- The runner's smoke test (`smoke/`, 20 cases) ran levels 1 to 16 of one alternating pattern (key 03702b84…, #6 or #7 in the census's
  order) and levels 1 to 4 of another: the first alternated through level 16 (alive at 13 and 15, dead at 14 and 16, all certified).
  Its R1 outcome is therefore seen before this file and is not prospective; the registered run recomputes it.

## Addendum R5: rigidity (added 2026-11-13 before any registered result was read)

Exploration at levels already read (to 12; `exploratory/rigid.py`, `exploratory/rigid_all.py`) found that five of the seven (#2 from
level 7, #3, #4, #5, #7) have exactly one state up to complement at every living level read, and that #2's pattern without its two
special knots has exactly the parity state and its complement at every level from 6. Since a part's states include the whole's, this
gives a proof of #2's death at an even level n from two facts: the reduced pattern is rigid at n, and the parity state violates the
two knots (R4). Registered as R5, computed by a second job of the shared runner (`job_rigid.py`; rigidity certified by a checked
model and a checked LRAT refutation of any second state):

| # | Prediction | Fails if |
| --- | --- | --- |
| R5a | The five stay rigid at their living levels to 16; #1 and #6 are not rigid at any living level to 16. | A certified verdict against it. |
| R5b | #2's reduced pattern is rigid at every even level 6 to 16, so with R4 its death there is certified by this reduction. | A certified second state. |

`certify.py` gained the function `certify_rigid` while the main run was in progress; the functions the main run uses are unchanged.

## Procedure fix (2026-11-13, before any registered result was used)

The first registered run (`run/`, kept as evidence) finished 375 of 775 cases; the other 400 were killed (signal 9) once refutation
proofs left in the memory-backed `/tmp` by cases stopped mid-proof had filled the run's memory allowance (23 GB of leaked proof
files, removed). Its 375 verdicts agreed with the census at every level both decided and with the second generator at every case;
they were tallied once to find the failure and are not used. The rigidity run (`run_rigid/`) was stopped for the same reason.
Fix, with no change to any prediction or decision rule: CaDiCaL now writes its LRAT proof into a pipe that the checker reads as it is
written, so no proof is stored (proof sizes are no longer kept; the checker reports its step count); the checker frees deleted
clauses; each case works in its own directory on disk, removed at the case's start and end. Gates rerun and passed. Both runs restart
from scratch in `run2/` and `run_rigid2/`.

Second fix (2026-11-14 about 01:40 UTC, again before any registered result was used): streaming the proof through a pipe let the
checker's pace throttle the solver, and run2 left many cases undecided at the 1,800-second limit that run 1 had decided in seconds;
it was stopped (kept as evidence, not used). Now each case first solves without a proof (a model is checked as before); a refuted
formula is solved again with its LRAT proof written to a file in the case's own work directory on disk, checked, and deleted. Gates
rerun and passed. Both runs restart from scratch in `run3/` and `run_rigid3/`.
