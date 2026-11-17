# Does space force order: pre-registration

Epic `SPACE-ORDER-20261117-001` (takes B185; goal G3, with G1), 17 November 2026. Frozen before any read-out. The code
(`weaves.py`, `gates.py`, `job.py`, `summarize.py` in
`experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/`, with the atom library of
`SEQUENTIAL-WALL-20261116-001A`) was written first and run only on its gates and on smoke cases with unregistered seeds, whose
timings and in-run checks were read but not their readings. Code and run by this thread with the shared runner. The canonical
K1–K3 test is unchanged.

## The question

On random atom patterns, untangling beat step-by-step propagation by a wide margin at the jump of the forced set
(`SEQUENTIAL-WALL-20261116-001`: 12 phases against 312 rounds at n = 2^20). The owner's question, reopened on 17 November: does the
knot picture see space? On the program's own six-regular weaves, does untangling still beat propagation, or does distance force
nested open uses?

## A lemma that frames it (proved here; settled by construction)

**Each phase extends the forced set by at most one step.** A distinction added in a phase is reached along a two-place rule that
comes from an atom (or a not-all-equal knot) one of whose members was already set at the phase's start, or it begins from a knot
two of whose members were set; either way it shares a knot with a distinction set earlier. So after t phases every set distinction
is within t steps of the held set, and **the phase count is at least the largest steps apart D from the held set to a set
distinction**. Within a phase rule chains run any distance, but only through what is already set. (The advisor pointed this out.)

So phases see space exactly through steps apart: on a random pattern every distinction is within about log n steps, and the bound
does not bind; on a weave, a set region that has to grow far from every held distinction costs one phase per step.

## Design (revised with the advisor before freezing)

The advisor computed that the first design could not answer the question: with each knot demanding one member, the twin has no
jump at all (the forced share is smooth in the held share, half reached at 0.222), and not-all-equal propagation from a planted
state is an atom law in which each knot forces only its odd member, which does not percolate. So the frozen design has three laws,
each on the weave W(L) (L × L distinctions, 2L² knots, every distinction in six) and on its **twin** R6, the same pattern after 5m
degree- and role-preserving knot swaps (members exchanged only between slots of the same role, so every distinction keeps how many
knots it has in each role, and steps apart are destroyed):

- **two** (the arm with a jump): each knot demands two members, the third (chosen uniformly) acting with either one to demand the
  other: atoms (f, y → x) and (f, x → y).
- **one** (control): each knot demands one uniformly chosen member.
- **nae**: not-all-equal from a planted state (30 zero-energy sweeps from the three-class state; the twin swaps only members of equal
  value and equal role, odd member or pair).

Held = first k of a uniform order (with planted values for nae); k* = the least k setting half the distinctions. L = 24, 48, 96,
192, 384 with 20, 20, 15, 10, 6 samples. Readings at k* and k* − 1 and at held fractions 0.05, 0.1, 0.2: rounds R, phases P, the
largest steps apart D, the avalanche (set share at k* minus at k* − 1); Strahler number = phase checked at L ≤ 48.

## Prior work in the program

`python3 -B scripts/track.py objects "six-regular weave propagation forced values held fraction" --until 2026-11-17 --exclude SPACE-ORDER-20261117-001`

`python3 -B scripts/track.py objects "bootstrap percolation triangular lattice rounds" --until 2026-11-17 --exclude SPACE-ORDER-20261117-001`

`python3 -B scripts/track.py objects "not-all-equal propagation planted state ground state triangular" --until 2026-11-17 --exclude SPACE-ORDER-20261117-001`

`python3 -B scripts/track.py objects "random six-regular three-uniform pattern control" --until 2026-11-17 --exclude SPACE-ORDER-20261117-001`

- `COMMON-FOLD-20261112-001`: a relative (forced share of a growing not-all-equal base from a pair); not rounds or phases, not
  weaves.
- `RULER-FLAT-20261111-001`: a relative (orientable six-regular weaves read by the winding margin; states exist when M ≥ 0); it fixes
  which weaves have not-all-equal states, which the planted state here relies on.
- `LONG-LOOP-20261111-001`: unrelated (faithful reading of non-orientable weaves).
- `SEQUENTIAL-WALL-20261116-001`: the predecessor (rounds against phases on random atom patterns); same laws, no space.
- `RULER-20261111-001`: a relative (on the endless six-regular weave bond distance is steps apart plus one; the three-class state):
  the reason steps apart is the program's distance on weaves, and the start of the planted state.
- `SLOW-LOOP-20261117-001`: unrelated (charged work of solver loops; matched on "propagation").
- `NAE-SURFACE-20261111-001`: a relative (degree-preserving knot swaps of six-regular weaves, the same kind of twin); this study's
  swaps also preserve roles.
- `KNOTS-ALONE-20261111-001`: a relative (regular weaves under not-all-equal); faithfulness, not propagation.

## Prior work outside the program

Polluted bootstrap percolation (Gravner and McDonald 1997; Gravner and Holroyd 2019); two-neighbour bootstrap thresholds
(Aizenman and Lebowitz 1988; Holroyd 2003, π²/(18 log L)); finite-size behaviour (Gravner, Holroyd and Morris 2012); rounds at a
mean-field discontinuous jump, n^(1/3) (Iwata and Sasa 2009; Baxter et al. 2015); Horn transitions (Moore, Istrate, Demopoulos and
Vardi 2007); forcing in perfect matchings (Harary, Klein and Živković; Pachter and Kim 1998); triangular antiferromagnet ground
states and height functions (Wannier 1950; Blöte and Hilhorst 1982), single-flip mixing (Caputo, Martinelli and Toninelli 2012;
Laslier and Toninelli 2015). Parallel complexity: planar monotone circuit value is in NC for acyclic planar circuits (Yang 1991;
Delcher and Kosaraju 1995); bootstrap prediction is in NC at degree ≤ 4 and P-complete at degree ≥ 5 on general graphs (Goles,
Montealegre and Todinca 2013); Eden growth in NC (Machta and Greenlaw). Not found: the one-step-per-phase lemma for Newton-type
phases, and phase counts of propagation on weaves against their twins.

## Predictions (frozen)

Medians over samples. Local slopes between successive sizes, not one global power law (advisor).

| # | Prediction | Fails when |
| --- | --- | --- |
| G | gates pass; P ≥ D in every reading; Strahler number = phase wherever checked | any fails |
| T1 | **two on W: a growing kernel, one phase per step.** Local slopes of log P* and of log R* against log L at 96→192 and 192→384 are both ≥ 0.7; P*/R* at L = 384 in [0.3, 1]; k*/n at 384 ≤ half of k*/n at 48 | any fails |
| T2 | two on R6: a mean-field jump. k*/n in [0.06, 0.11] at every L; R*(384)/R*(96) ≥ 2; P*(384) − P*(24) in [1, 8] and P*(384) ≤ 20 | any fails |
| T3 | **space forces order:** P*(W)/P*(R6) ≥ 5 at L = 384 for the two-demand law | below |
| T4 | the lemma's bound is nearly tight on W for two: median P*/D* in [1, 1.5] at L = 96, 192, 384 | any outside |
| O1 | one: no jump: median avalanche at L = 384 ≤ 0.05 on W and on R6 | either above |
| O2 | one: flat phases: P*(384) − P*(24) ≤ 4 on R6; local slope of log P* on W at 192→384 < 0.2 | either fails |
| O3 | one on R6: k*/n in [0.20, 0.245] at L = 96, 192, 384 (advisor: 0.222) | any outside |
| N1 | nae: no jump: median avalanche at L = 384 ≤ 0.05 on W and on R6 | either above |
| N2 | nae: P* ≤ 8 at every size on W and on R6 | any above |
| N3 | nae planted state: free share on W in [0.27, 0.31] at L ≥ 48 (advisor's Kasteleyn value 0.290); 300 sweeps change it by ≤ 0.01 (L = 48) | either fails |

The advisor put about 30% on the one-demand law having a real jump on W; if it does, O1 and O2 fail on W and that is a reading,
not an error. No prediction is changed after this freeze.

## Runs and stop rule

One shared-runner job, 431 cases, three workers, 3G per case, MemoryMax 12G; expected under an hour; registered in
`docs/LONG_RUNNING.md`. The study stops after this run and its read-out; then the decision note, the referee hand-off and the report.

The advisor model (`claude -p --model claude-fable-5-2`) was consulted once, before this freeze, and reshaped the design as above:
the no-jump computations for the first design, the planted not-all-equal law as a fixed-choice atom law, role-preserving twins in
place of plain swaps, the two-demand arm, the lemma and the three regimes (no tangency: log log n phases; a mean-field tangency:
log n; a growing kernel: one phase per step), and the predictions T1–T4, O1–O3, N1–N3. Words chosen with it: kernel (a set
region that keeps growing with no further held distinctions), and steps apart for every distance; the literature's lattice, torus,
droplet and front are named only as the literature's.
