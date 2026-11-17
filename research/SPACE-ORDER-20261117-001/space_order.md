# Does space force order

Epic `SPACE-ORDER-20261117-001`, 17 November 2026, by Claude; takes B185. Goals G3, with G1. Referee pending. Pre-registration:
[preregistration.md](preregistration.md), frozen in commit `6995ef26a` at 17:09:44 UTC; the run was created at 17:09:52 UTC and
ended at 17:14:24 UTC. Experiment: [code and contract](../../experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/),
[summary](../../artifacts/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/summary.json).

## The answer

Yes: space forces order, and only through steps apart. Untangling travels along what is already settled. A two-place rule exists
only where a knot already has a settled member, so the long chains of a phase run along the rim of the settled region and never
into the open. Each phase therefore moves the settled region at most one step (proved, below).

On a weave the law that can grow a set region from one place (each knot demanding two members) does exactly that. A kernel starts
near one held distinction and grows one step per phase until it covers the weave:

- 256 phases at L = 384, which is the weave's largest steps apart (2L/3);
- each distinction's phase is its steps apart from where the kernel began (correlation 0.99, 0.99 phases per step at L = 384);
- phases and rounds both grow like L, local slopes 0.95 to 1.01 and 0.91 to 0.94.

The same law on the weave's shuffled twin (every distinction in the same number of knots in each role, steps apart destroyed)
jumps the mean-field way. It needs 9.5 phases at the same size against 174 rounds, logarithmic in n, as random atom patterns did.
That is a ratio of 27 between pattern and twin.

Laws that cannot grow a kernel see no space at all: one demand per knot, and not-all-equal from a planted state. They have no
jump on either pattern and need 3 to 7.5 phases at every size.

So in the knot picture, space is what untangling cannot shortcut, and the price is exactly steps apart. The program's ruler
(`RULER-20261111-001`: on the six-regular weave bond distance is steps apart + 1) makes that price the law's own distance. The
classical counterpart is a light cone: local Newton iterates move information one step at a time. This identifies nothing new in
complexity theory: planar or bootstrap-type questions can be in NC by methods that are not phases. What the knot picture explains
is why the random patterns of `SEQUENTIAL-WALL-20261116-001` were easy for untangling: everything there is within about log n steps.
It also explains why weaves are not: a kernel must travel the weave's whole span, one settled step at a time.

## The lemma (proved)

**Each phase extends the settled set by at most one step.** A distinction settled in a phase is reached along a two-place rule from
an atom (or a not-all-equal knot) one of whose members was settled at the phase's start, or it begins from a knot two of whose
members were settled; either way it shares a knot with a distinction settled earlier. So after t phases every settled distinction
is within t steps of the held set: **P ≥ D**, the largest steps apart from the held set to a settled distinction. It held in all
2,130 readings.

The bound is in terms of the held set; the kernel's growth makes the count far larger. P*/D* was 3.7, 5.5 and 6.3 at L = 96, 192
and 384, because held distinctions are scattered and the kernel reaches regions near some held distinction only by growing from
its own start. Measured from the trigger (the held distinction whose addition sets off the leap), the phases are the steps apart
(post hoc, `posthoc.py`).

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gates; P ≥ D everywhere; Strahler number = phase where checked | held | 431 of 431 cases; P ≥ D in all readings; Strahler = phase in 480 checked |
| T1 | two on W: kernel, slopes of log P* and log R* ≥ 0.7; P*/R* in [0.3, 1]; k*/n falls | held | P slopes 0.95, 1.01; R slopes 0.91, 0.94; P*/R* = 0.49; k*/n 0.016 (L = 48) to 0.0016 (L = 384), k* about L |
| T2 | two on R6: mean-field jump | held | k*/n 0.091 … 0.086 (advisor 0.085); R*(384)/R*(96) = 2.45 (n^(1/3) gives 2.52); P* 5 → 9.5 |
| T3 | P*(W)/P*(R6) ≥ 5 at L = 384 | held | 27 (256 against 9.5) |
| T4 | P*/D* in [1, 1.5] on W | **failed** | 3.7, 5.5, 6.3: D is measured from all held distinctions, and the kernel grows from one |
| O1 | one: no jump | held | avalanche 0.00006 (W), 0.0005 (R6) |
| O2 | one: flat phases | held | R6 3 → 5; W 4 → 7.5, local slope 0.10 |
| O3 | one on R6: k*/n near 0.222 | held | 0.221, 0.221, 0.222 |
| N1 | nae: no jump | held | avalanche 0.00003 (W), 0.00005 (R6) |
| N2 | nae: P* ≤ 8 | held | 2 to 4 on both |
| N3 | nae planted state: free share near 0.290 | held | 0.292, 0.295, 0.292, 0.293; 300 sweeps change it by 0.0065 |

9 of 10 held. T4 failed because the bound it tested is weaker than the mechanism.

### Medians at k*

| Law, pattern | L = 24 | 48 | 96 | 192 | 384 |
| --- | --- | --- | --- | --- | --- |
| two, W: P* (R*) | 16.5 (45) | 34 (80) | 66 (146) | 127.5 (275) | 256 (528) |
| two, R6: P* (R*) | 5 (27.5) | 6 (40) | 8 (71) | 9 (110) | 9.5 (174) |
| one, W: P* (R*) | 4 (12) | 5 (15) | 6 (18) | 7 (22) | 7.5 (25) |
| one, R6: P* (R*) | 3 (18.5) | 4 (28) | 5 (43) | 5 (46) | 5 (59) |
| nae, W: P* (R*) | 2 (6.5) | 3 (9.5) | 3 (10) | 4 (11) | 4 (14.5) |
| nae, R6: P* (R*) | 2 (8) | 3 (11.5) | 3 (12) | 3 (17) | 3 (20.5) |

**Post hoc, two on W** (rebuilt from the registered seeds): P* against the largest steps apart from the trigger is 254 to 257
against 256 at L = 384, 127 to 136 against 128 at L = 192, and 64 to 77 against 64 at L = 96. The weave's largest steps apart is
2L/3 in each case.

## Limitations

- One weave family (triangular tori) and one shuffle; other two-fold weaves (other cycle pairs) were not tried.
- The planted not-all-equal state is a declared process (30 zero-energy sweeps from the three-class state), checked only by its
  free share; not-all-equal from it cannot grow a kernel, as the advisor computed.
- Phases are one parallel law. Bootstrap-type and planar questions can be in NC by other methods, so P ∝ L is not a claim that these
  patterns are inherently sequential.

## Reproduce

```sh
.venv/bin/python -B experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/gates.py
.venv/bin/python -B scripts/longrun.py launch experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/job.py --out RUN --workers 3 --case-mem 3G
.venv/bin/python -B experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/summarize.py RUN
.venv/bin/python -B research/SPACE-ORDER-20261117-001/posthoc.py
```

## Advisor

Consulted once, before the freeze. It showed the first design could not answer the question: none of its cells would have a
jump. The one-demand twin is smooth, half reached at 0.222 (measured 0.221). Planted not-all-equal is a fixed-choice atom law that
does not percolate. It proposed:

- the two-demand arm, and its predictions (k*/n 0.085 on the twin, measured 0.086; P and R like L on the weave, measured);
- role-preserving twins;
- the free share 0.290 (measured 0.292);
- the lemma and the three regimes, all confirmed: no tangency gives flat phases, a mean-field jump gives log n, a kernel gives one
  phase per step.

Its T4 guess (P ≈ D from the held set) failed for the reason above.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: does space force order | **Status:** Successful (referee pending) | Yes, through steps apart only: a kernel costs one phase per step (256 at L = 384), against 9.5 on the same law's twin; 9 of 10 predictions held |
| Local direction: phases on spatial patterns | Continue, narrowly | The lemma and the kernel regime are clean; other weaves and laws would only repeat it unless a law with longer-range rules is tried |
| Broader exploration: parallel methods on planar patterns | Known alternatives | Planar and bootstrap prediction can be in NC by non-phase methods |
| Long-term goal: G3, with G1 | Capability gained | The sequential resource of untangling is steps apart, which on weaves is the program's own ruler distance |

**Next step:** Research directions. Selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | B184: why layered random circuits need about d^0.4 phases (layering as a built-in order) | 2/3, would explain how order designed into a meeting pattern forces nesting, the counterpart of space here | 3/3, a mean-field recursion for the rank distribution, data in hand | Iterate the infinite-width recursion to d = 10^4 and compare with the measured 4 … 17 → stop when it matches within one, or fails | Selected · next |
| 2 | A law whose two-place rules reach past the rim (rules from knots with no settled member, such as parity's) on weaves | 2/3, would test whether the one-step light cone is special to atoms and not-all-equal | 2/3 | Parity knots on the weave, phases of elimination against steps apart → stop at a clear scaling | Alternative · deferred |

**Corrections:** none.

**Goals:** G3 checkpoint (capability gained), with G1; no goal changed.

**Assumptions:** A96 added (scope: the role-preserving shuffle removes steps apart and nothing else that matters).

**Basket:** read; B185 taken by this epic.
