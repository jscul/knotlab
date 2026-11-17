# Does space force order

Epic `SPACE-ORDER-20261117-001`, 17 November 2026, by Claude; takes B185. Goals G3, with G1. Referee pending. Pre-registration:
[preregistration.md](preregistration.md), frozen in commit `6995ef26a` at 17:09:44 UTC; the run was created at 17:09:52 UTC and
ended at 17:14:24 UTC. Experiment: [code and contract](../../experiments/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/),
[summary](../../artifacts/SPACE-ORDER-20261117-001A/SPACE-ORDER-20261117-001A-E001_weave_phases/summary.json).

## The answer (corrected after the referee, 17 November)

*The first version of this answer said "space forces order, and only through steps apart; the price is exactly steps apart". The
referee (`SPACE-ORDER-R1`) ran assumption A96's own challenge and overturned it: that sentence is withdrawn (Block, logged in
`docs/CORRECTIONS.md`). The corrected reading follows.*

Phases are at least the steps apart from what is held (proved, below): a two-place rule exists only where a knot already has a
settled member, so a phase's long chains run only next to what is already settled, and each phase moves the settled set at most
one step. This is the light cone of a local rule (the locality bound of Linial 1992).

On the weave the law that can grow a set region from one place (each knot demanding two members) grows a kernel that needs one
phase per step of its growth through the weave's local structure, in which every co-knotted pair lies in two knots: 256 phases at
L = 384, where its growth distance equals the weave's largest steps apart, 2L/3 (the diameter of the triangular torus when 3
divides L). Phases rise about one per step from the trigger (post hoc: correlation 0.99, slope 0.99 at L = 384, but a few phases
above the steps apart, equal for only 4 to 18% of distinctions). Phases and rounds both grow like L; rounds like L after
nucleation are the known time of bootstrap percolation (Balister, Bollobás and Smith 2016; Bollobás, Holmgren, Smith and Uzzell
2014).

What the phases follow is that local structure, not steps apart. Rewiring 0.2% of the weave's knots keeps 99% of the pairs that
lie in two knots and cuts the largest steps apart from 256 to 52, yet the phases stay at 252 (referee's run). They fall only as the
local structure goes: 134 at 95% of it, 48 at 35%, and about 10 on the fully shuffled twin, which keeps every distinction's role
counts and has no such structure. The 27-fold ratio between weave and twin is the loss of that local structure. Laws that cannot
grow a kernel (one demand per knot; not-all-equal from a planted state) need 2 to 7.5 phases on both.

So in the knot picture, order on a weave comes from a kernel that can grow only through knots that overlap two at a time on each
pair. Long-range shortcuts that bring everything close do not speed it, because a lone shortcut knot cannot carry the growth.
Random atom patterns were easy for untangling not because everything there is within log n steps (the first version said so,
also withdrawn) but because they have no such local structure for a kernel: their jump is the mean-field one.

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
  free share; it keeps part of the three-class order of its start (order parameter 0.32 to 0.36, still 0.23 to 0.35 after 3,000
  sweeps; referee), though the readings are unchanged with 100 times the mixing. Not-all-equal from it cannot grow a kernel.
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
| This attempt: does space force order | **Status:** Successful (refereed: confirmed numbers, Block on the reading) | Phases are at least the steps apart (proved); a kernel costs one phase per step of growth through the weave's local structure (256 at L = 384), against 9.5 on the twin; the first reading, "only through steps apart", is withdrawn |
| Local direction: phases on spatial patterns | Continue, narrowly | The lemma and the kernel regime are clean; other weaves and laws would only repeat it unless a law with longer-range rules is tried |
| Broader exploration: parallel methods on planar patterns | Known alternatives | Planar and bootstrap prediction can be in NC by non-phase methods |
| Long-term goal: G3, with G1 | Capability gained (narrowed) | Local overlap structure that lets a kernel grow is what forces nesting; steps apart is only a lower bound |

**Next step:** Research directions. Selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | B184: why layered random circuits need about d^0.4 phases (layering as a built-in order) | 2/3, would explain how order designed into a meeting pattern forces nesting, the counterpart of space here | 3/3, a mean-field recursion for the rank distribution, data in hand | Iterate the infinite-width recursion to d = 10^4 and compare with the measured 4 … 17 → stop when it matches within one, or fails | Selected · next |
| 2 | A law whose two-place rules reach past the rim (rules from knots with no settled member, such as parity's) on weaves | 2/3, would test whether the one-step light cone is special to atoms and not-all-equal | 2/3 | Parity knots on the weave, phases of elimination against steps apart → stop at a clear scaling | Alternative · deferred |

**Corrections:** none at close; after the referee, a Block on the reading "only through steps apart" (and on the explanation of the
random patterns by log n steps), a Narrowing on the post hoc "phase = steps apart from the trigger", and three Not a block notes
(the lemma named as a light cone, the planted state's residual order, the known bootstrap time); A96 overturned. All in
`docs/CORRECTIONS.md` and knotlab's HISTORY.md.

**Goals:** G3 checkpoint (capability gained), with G1; no goal changed.

**Assumptions:** A96 added (scope: the role-preserving shuffle removes steps apart and nothing else that matters), overturned by its
own challenge after the referee: the shuffle also removes the local structure, and that is what the phases follow.

**Basket:** read; B185 taken by this epic.

## Referee

`SPACE-ORDER-R1` ([report](referee-R1/report.md), commit `2739fc6d7`): the lemma and every frozen number confirmed (all 426 cases
recompute with 0 mismatches; phases recomputed as least labels of g(i, j) = max(i, j) if i ≠ j, else i + 1, so "Strahler number =
phase" is a theorem); **Block** on the reading "space forces order, and only through steps apart" and on the explanation of the
random patterns by log n steps; A96 overturned by its own challenge (table below, the referee's run at L = 384); **Narrowing** on
the post hoc relation; Not a block on the lemma's naming, the planted state and the known bootstrap time.

| Rewired share of knots | Pairs in two knots | Largest steps apart | P* | R* |
| --- | --- | --- | --- | --- |
| 0 (weave) | 1.000 | 256 | 260 | 543 |
| 0.002 | 0.989 | 52 | 252 | 530 |
| 0.01 | 0.949 | 27 | 134 | 303 |
| 0.05 | 0.778 | 15 | 115 | 295 |
| 0.25 | 0.345 | 9 | 48 | 212 |
| twin | 0.000 | 7 | 10 | 244 |

The final report below is kept as sent; its headline was withdrawn here.

## Final report as sent

Posted to the owner's project thread on 2026-11-17 at about 17:20 UTC:

**Result: space does force order, and only through distance.** An untangling stage can follow two-place rules only where a knot already has a settled member. So its long chains run along the edge of what's settled and never out into the open. Each stage therefore moves the settled region at most one step (proved).

On the program's six-regular weaves, a law that can grow a settled region from one place needs one stage per step from where that region began. That's 256 stages at L = 384, exactly the weave's widest distance. The same law on a shuffled copy of the weave, with identical counts per distinction, needs only 9.5 stages. Laws that can't grow a region see no space at all: 2 to 7.5 stages on both. So distance (steps apart, which the program's ruler made the law's own distance) is exactly what untangling can't shortcut. The classical counterpart is a light cone, so there's no complexity claim.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: does space force order | **Status:** Successful (referee pending) | One stage per step (256 at L = 384) against 9.5 on the twin; 9 of 10 predictions held |
| Local direction: stages on spatial patterns | Continue, narrowly | The lemma and the growth regime are clean |
| Broader exploration | Known alternatives | Planar problems can be fast by other methods |
| G3, with G1 | Capability gained | Untangling's sequential cost is steps apart, the program's own distance |

**Next step:** Research directions. Selected: #1, B184 (why layered circuits need about d^0.4 stages), payoff 2/3, concreteness 3/3. Starting now.

**Corrections:** none at close; after the referee, a Block on the reading "only through steps apart" (and on the explanation of the
random patterns by log n steps), a Narrowing on the post hoc "phase = steps apart from the trigger", and three Not a block notes
(the lemma named as a light cone, the planted state's residual order, the known bootstrap time); A96 overturned. All in
`docs/CORRECTIONS.md` and knotlab's HISTORY.md. **Goals:** G3 checkpoint. **Assumptions:** A96 (the shuffled twin removes distance and nothing else that matters). [Decision note](https://github.com/jscul/knotlab/blob/main/research/SPACE-ORDER-20261117-001/space_order.md)
