# Carrying distinctions together: pre-registration

Epic `CARRY-STRANDS-20261116-001` (takes `SEQUENTIAL-WALL-20261116-001#1`, the owner's braid made exact for forcing; goal G3),
16 November 2026. Frozen before any read-out. The code (`strands.py`, `gates.py`, `job.py` in
`experiments/CARRY-STRANDS-20261116-001A/CARRY-STRANDS-20261116-001A-E001_carried/`, using the atom library of
`SEQUENTIAL-WALL-20261116-001A`) was written first and run only on its gates and on smoke cases with unregistered seeds, whose
timings and state counts were read but not their phases. Code and run by this thread with the shared runner. The canonical K1–K3
test is unchanged.

## The question

`SEQUENTIAL-WALL-20261116-001` found that order in atom patterns is forced only at open uses: an atom both of whose demanders are
first forced in the same phase waits for the next phase, and a distinction's phase is its Strahler number σ. The owner's picture
is of strands that can be braided and untangled. Made exact for forcing: instead of waiting, a law can **carry** several open
distinctions at once and take an open use while carrying both demanders. The **w-carry law** carries at most w distinctions;
in a phase it may *begin* (carry what an atom over two forced demanders demands), *follow a rule* (an atom with one forced
demander), take an *open use while carried* (both demanders carried), and *release*. In the **spend-only law** every use spends
what it uses, so a distinction needed twice is derived twice; the **keep law** may keep a carried distinction after a use, which
is what lets one strand split into two that rejoin. w = 1 is the forcing law.

Questions: how many phases P_w and doubling rounds T_w each law needs as w grows (the curve w ↦ P_w, and the least w giving one
phase); how much keeping gains over spending; and whether the braid picture explains anything that the classical statements
(register allocation, pebbling) do not.

## The record-size measure, and why

The measure is **w, the number of distinctions carried at once**. For forcing, the joint record of open distinctions carries no
correlation, since the forced set is one state: all a carried record holds is which distinctions are carried, so a phase searches
the about n^w carried sets, and w is the logarithm of its work in base n. Table size (2^w) and states visited (up to n^w) are
functions of w, and reachable-state counts mostly count independent beginnings, so they add nothing (advisor). w is the pebble
count of the classical pebble games.

## In standard terms

The spend-only law is register allocation for expression trees (Ershov 1958; Nakata 1967; Sethi and Ullman 1970): registers equal
the Strahler number. The keep law is the black pebble game with sliding on the derivation DAG, the forced distinctions free (Cook
1974; Paterson and Hewitt 1970; Gilbert, Lengauer and Tarjan 1980). A phase is a reachability search over carried sets (NL in
n^w states). Phases as Newton iterates: Esparza, Kiefer and Luttenberger 2010.

## Prior work in the program

`python3 -B scripts/track.py objects "carried distinctions keep spend phases w-carry law" --until 2026-11-16 --exclude CARRY-STRANDS-20261116-001`

`python3 -B scripts/track.py objects "black pebbling sliding register allocation Strahler number phases" --until 2026-11-16 --exclude CARRY-STRANDS-20261116-001`

`python3 -B scripts/track.py objects "random atom patterns layered circuits ladder pyramid" --until 2026-11-16 --exclude CARRY-STRANDS-20261116-001`

- `SEQUENTIAL-WALL-20261116-001`: the predecessor (same patterns, the forcing law w = 1); this study reuses its library and its
  random families at small sizes and adds w ≥ 2.
- `REACH-CENSUS-20261113-001`: unrelated (nested not-all-equal families read along rays; matched on "carried").
- `SHIFT-COUNT-20261112-001`: unrelated (travelling patterns; matched on general words).
- `HARMONY-ARITH-20261112-001`: unrelated (periods of stitched orbits).
- `FORGET-RULE-20261114-001`: unrelated (forgetting in nested families; matched on "layered").
- `COMMON-FOLD-20261112-001`: unrelated (travelling patterns among random periodic bases).
- The braid studies `BRAID-READOUT-20261114-001`, `BRAID-COUNTS-20261114-001`, `JOINT-BRAID-READS-20261114-001` and
  `STRAND-RETURN-20261114-001` are the owner's line this study makes exact for forcing; they measured reversible crossings, which
  forcing does not have.

## Prior work outside the program

Strahler number = registers for trees (Ershov 1958; Flajolet, Raoult and Vuillemin 1979); pebbling of pyramids (Cook 1974);
pebbling price is PSPACE-complete to compute (Gilbert, Lengauer and Tarjan 1980); parallel time and pebble games (Dymond and Tompa
1985; Paterson and Valiant 1976), which the advisor judged a misfit here: they are theorems for arbitrary DAGs, while any cone of
height d needs about d/w phases. Not found: the phase count of w-pebble closure (phases of the keep law) as a two-parameter curve,
and measurements of it on random Horn systems or random circuits.

## Settled by construction (stated, proved in ticket B, checked by the gates)

- w = 1 is the forcing law (G1). Every law ends in the closure (G2). Keeping and more carried distinctions never add phases (G5).
- Spend-only: phase = ⌈σ/w⌉ for every forced distinction (G3), and T_w ≥ max σ (G4): spend-only carrying shortens the count of
  phases but never lowers the doubling rounds below the Strahler number.
- Keep: the ladder's top is forced in one phase with two carried distinctions at every length (G6); a layered circuit of width W
  is forced in one phase with 2W carried distinctions at any depth (carry one layer while deriving the next).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | `gates.py` passes; in every case every law ends in the closure. | any fails |
| Q1 | Random atom patterns at the jump: keeping rarely saves a phase: P_2(keep) = ⌈P_1/2⌉ in at least 75% of the samples at each n ≥ 256 (advisor: about 65% likely). | below 75% at some n ≥ 256 |
| Q1b | Per distinction: the median over samples of the fraction of forced, unheld distinctions whose keep-law phase at w = 2 is below ⌈σ/2⌉ is at most 0.10 at every n; and at n ≥ 512 the median fraction after the phase where the forcing law forces fewest exceeds the median fraction before it. | either fails |
| Q2 | Random patterns, rounds: T_2(spend) ≤ T_1 in at least 90% of the samples at each n ≥ 256, and the median T_2(spend)/T_1 lies in [0.8, 0.95] at n ≥ 1024 (advisor; the saving comes from merging the per-phase ceilings). | either fails |
| Q3 | Layered random circuits: keeping gains more where the circuit is narrower: at depth 32, the median relative gain (⌈σ/2⌉ − P_2(keep))/⌈σ/2⌉ at width 4 exceeds that at width 32, and width 16 is at least width 32. | either fails |
| Q3b | Narrow circuits: P_(2W)(keep) = 1 on every sample of width 2 (depths 4 to 16) and width 3 (depths 4 to 8). | any sample needs more |
| Q4 | Pyramids (advisor's derivation): P_w(keep) = P_w(spend) = ⌈h/w⌉ for every measured h (4 to 12) and w (1 to 4), and T_w(keep) = T_w(spend): keeping buys no phase and no round on pyramids at w ≤ 4. | any differs |
| Q5 | Subdivided trees (each edge of a complete binary tree a chain of ℓ rules), advisor's example: with ℓ = 16, T_2(spend) < T_1 at heights 4 and 6, and T_3(spend) < T_2(spend) at height 4: spend-only carrying can turn the per-phase logarithm into an additive one. | any fails |

The curve w ↦ P_w and the copy gain ⌈σ/w⌉ − P_w(keep) are reported for every family without a further prediction.

## Runs and stop rule

One shared-runner job (`job.py`, 305 cases): random atom patterns at the jump, n = 64 to 1024 (20 samples) and 2048, 4096 (10),
w = 1, 2 (and 3 for n ≤ 256), both laws; layered random circuits of width 4, 16, 32 and depth 8 to 64 (10 samples), w = 1, 2 (and 3
when n ≤ 140); narrow circuits of width 2 and 3 (5 samples) at w = 2W with keeping; unlayered circuits of 256 and 1,024 gates on
32 inputs; ladders, pyramids and subdivided trees. Two workers, 3G per case, a state cap of 4,000,000 per phase search (a capped
case is recorded as capped). Expected under an hour; registered in `docs/LONG_RUNNING.md` if over ten minutes. The study stops
after this run; then the decision note, referee hand-off and report.

The advisor model (`claude -p --model claude-fable-5-2`) was consulted once, before this freeze. Its corrections, all adopted: a
law that copies a carried distinction is off from black pebbling with sliding by up to two, so the keep law replaces copying by
keeping (a use may keep either demander or both); the spend-only rounds bound is correct but only says carrying cannot beat the
forcing law's trivial floor, while it can beat its actual cost on some trees (Q5); my guess for pyramids was wrong, and with the
bottom row forced its derivation gives ⌈h/w⌉ phases with or without keeping (Q4); "how many to save a phase" is always two, so the
study reports the curve and the least w for one phase instead; Q1–Q3 were sharpened as above. Words chosen with it: carried
distinction, w-carry law, keep and spend (spend-only law, keep law), begin, follow a rule, open use taken while carried, release,
and "step" for one step of a law (move is reserved for growth). Braid and strand stay in the owner's words. Its blunt view, to be
tested in the report: "your strands are pebbles; the picture explains nothing new, but it isolates one dichotomy cleanly".
