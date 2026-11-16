# Which knot patterns must be worked in order

Epic `SEQUENTIAL-WALL-20261116-001`, 16 November 2026, by Claude, picking up the parallelism question of the owner's Codex session
"Clarify P vs NP and parallelism" (14 November). Goals G3 (and G16, not moved). Refereed: `SEQUENTIAL-WALL-R1`, confirmed with fixes, no Block ([report](referee-R1/report.md), commit `c960effc1`); its four fixes are folded in below (see "Referee"). Pre-registration:
[preregistration.md](preregistration.md), frozen in commit `cb6144f52` before any read-out. Proof:
[Theorems 1–6](../../proofs/SEQUENTIAL-WALL-20261116-001B/SEQUENTIAL-WALL-20261116-001B-P001_phases_and_rank/proof.md).
Experiment: [code and contract](../../experiments/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/),
[summary](../../artifacts/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/summary.json).

## The answer

Patterns of knots do hit the inherently sequential wall: forcing in patterns of the atom A ∧ B → c is P-complete, as monotone
circuit value is (known). In knot terms the wall has a precise place. Once one demander of an atom is settled, the atom is no
longer a knot but a two-place rule, and every two-place rule in a pattern can be followed at once. Order is forced only where an
atom is used **openly**, with both demanders first settled at the same stage. The number of stages, **phases**, is the
Horton–Strahler number of the best derivation (known, Esparza, Kiefer and Luttenberger 2010), and a family needing
polylogarithmically many phases is decided in polylogarithmic parallel time.

Measured against step-by-step propagation (**rounds**), on 150 random atom patterns (each read at about fifteen held counts) and 220 random circuits:

- On random atom patterns at the jump of the forced set, rounds grow like n^0.30 to n^0.36 (312 rounds at n = 2^20; the exponent's
  lower end rests on the eight samples at 2^20), while phases grow only
  logarithmically, 0.57 phases per doubling of n (12 phases at n = 2^20). The slow cascade is almost all two-place work; open uses
  nest only logarithmically deep.
- On random monotone circuits with no layering, a few phases suffice (at most 4 up to 65,536 gates).
- On layered random circuits, where every gate reads only the layer below, phases grow like d^0.41 with the number of layers d (17
  phases at d = 256), and the dual law that spreads unforcedness does no better. Order built into the meeting pattern is what keeps
  the phase count growing.

How the knots overlap decides when the wall can bite: it needs both a distinction **reused** as a demander in several atoms and
one **demanded several ways** by several atoms (Theorem 4: reuse unless P = NC, several-way demand unless P = NL; many phases
alone need only reuse), and more phases than log₂ of the
held count need a **rejoining**, one distinction below both demanders of one atom (Theorem 2). Being a knot does not decide it: of
the 34 three-place knots, 2 make laws that are trivial (AC⁰), 2 parity laws (⊕L), 14 sequential (P-complete) and 16 NP-complete
(Theorem 5, known classification applied).

What the knot picture explained, plainly: it names where order comes from (a knot used as a knot, both its loops still open), and
that naming is exactly the classical Strahler/Newton statement, so as theory it is a restatement, as the advisor judged. It adds
no algorithm. What is new is measured: the separation of rounds and phases on random atom patterns at the jump, the
Newton-at-a-tangency profile of the phases, and the growth of phases with layering in random circuits. The owner's braid reading
is an analogy here, not a result: the forcing law waits for one strand to settle instead of carrying the two together, and the
atom, unlike the braid crossing, is not reversible.

## The knot picture of parallel work

Settling a distinction is the owner's untangling: fix one demander of an atom and what is left is a two-place rule, which is no
knot (every two-place relation is a 2-CNF, the foundation's two/three boundary). Two-place rules compose by reachability, all at
once: following a chain of them is doubling, the "hop" of `STRAND-RETURN-20261114-001`. So one phase untangles everything that can
be untangled from what is already settled. An atom whose two demanders become settled in the same phase is used openly, as a
knot, and must wait. Two open uses of equal standing, nested, make the next standing: that is the Strahler number. A pattern can be
worked in parallel to the extent that its open uses nest shallowly.

What forces nesting is overlap of two kinds. A distinction **reused** in several atoms lets one settled distinction feed several
later knots; one **demanded several ways** offers alternative derivations. Without reuse, a pattern is a formula and needs at most
log₂ |H| phases (Theorem 3). Without several-way demand, the pattern is decided in NL by reasoning from the other side: an atom
dies when one demander is unforced, so unforcedness spreads along single atoms, which is the dual law (Theorems 4(a) and 6). The
ladder (rejoining at every step) and the pyramid need k + 1 and h phases, yet nothing in them is unforced, so the dual law ends them
at once.

## Known part: the wall and where each knot law sits

- Monotone circuits as atom patterns, every piece the atom, which passes K1–K3: AND g = (x, y → g), OR g = (x, t → g) and
  (y, t → g) with one held t (Goldschlager 1977; Cook's path systems, 1974, are atom patterns already). Checked on every input of
  192 small circuits (gate G4).
- Not-all-equal: satisfiability is NP-complete (Schaefer 1978), and propagation is P-complete with two held values, by a gadget
  written and checked here (NAE(x, y, g₀) then NAE(g₀, F, g) for AND; NAE(x, T, g₀), NAE(y, T, g₀) then NAE(g₀, F, g) for OR).
  Since not-all-equal is unchanged by flipping every value, some held value is necessary.
- All 34 three-place knots, each confirmed by `knotlab check` ([table](../../artifacts/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/knots_table.json)):

| Class with held values | Knots | Which |
| --- | --- | --- |
| AC⁰ | 2 | the single-sign clauses a ∨ b ∨ c and ¬a ∨ ¬b ∨ ¬c |
| ⊕L-complete | 2 | parity a ⊕ b ⊕ c = 0 or 1 |
| P-complete | 14 | the atom, its dual, and knots that define one of them with held values (definitions found by search) |
| NP-complete | 16 | not-all-equal and the rest |

  None is NL-complete or L-complete (the two AC⁰ laws are in L, so "never in NL or L", as first written, was wrong), because no
  knot is closed under majority (Baker and Pixley 1975). Counts agree with the advisor's hand
  classification.

## Measurements

### Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gates, checks, Strahler number = phase in every random case, circuit evaluations | held | 386 of 386 cases ok |
| P1 | rounds fast away from the jump | held | at α = 0.03, 0.06, 0.2, 0.4: 5, 11, 17, 10.5 rounds at 2^20 against 2, 4.5, 12, 7 at 2^12 |
| P2 | rounds slow polynomially at the jump | held | slopes 0.30 (k*) and 0.32 (α*) |
| P2a | n^(1/3) at the sample's jump, slope in [0.29, 0.37] | held, only with the last size | 0.302 over 2^14 … 2^20, but 0.258 without the eight samples at 2^20 (bootstrap interval of the fit [0.27, 0.36]; the referee's fresh code gives 0.334 [0.31, 0.35] over 2^10 … 2^18): the exponent is about 0.30 to 0.36 |
| P2b | n^(1/4) at fixed α* = 0.098251, slope in [0.21, 0.29] | **failed** | 0.316: at fixed α* rounds grow like at the sample's own jump, not like n^(1/4) |
| P3 | phases grow logarithmically at the jump | held | 6, 8, 9, 10, 11, 12 phases at 2^10 … 2^20; slope 0.57 per doubling; growth +6. My first view (log log n, growth ≤ +1) was wrong, as the advisor argued |
| P3b | rounds and phases separate | held | R*/P* = 7.0 at 2^12, 25.0 at 2^20 |
| P4 | near the jump, phases fall slowly and rounds like ε^(−1/2) | held | P(+0.001n) − P(+0.03n) = 4 and 3; R ratio 3.4 and 3.5 (2^18, 2^20) |
| P5 | one phase carries the leap | **failed** | 0 of 8: the leap spreads over four or five phases, each about five times the last (below) |
| P6 | layered circuits need more phases as they grow | held | width 1024: 9 at d = 64, 17 at d = 256 (ratio 1.89); 10 of 10 alive |
| P6-linear | linear growth in d | **failed** | ratio 1.89 < 3: growth like d^0.41 |
| P7 | the dual law does no better on layered circuits | held | min(P, P_dual) 8 at d = 64, 16 at d = 256 |
| P8 | unlayered circuits need few phases | held | 2, 3, 4, 4 at 1,024 … 65,536 gates |
| P9 | the fringe bound is loose at the jump | **failed** | log₂ fringe 17.4, 19.0, 21.9 against 10, 11, 12 phases (ratio about 1.8): the fringe is polynomial, about 4n, and the bound is within a factor two |

### Random atom patterns (m = 3n, medians)

| log₂ n | samples | α at the jump | R* | P* | R at k* − 1 | P at k* − 1 | log₂ fringe at k* |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 40 | 0.1021 | 34 | 6 | 11.5 | 3 | 10.8 |
| 12 | 40 | 0.1023 | 55 | 8 | 21 | 4 | 13.2 |
| 14 | 30 | 0.1002 | 86 | 9 | 38.5 | 5 | 15.2 |
| 16 | 20 | 0.0980 | 128 | 10 | 63.5 | 6 | 17.4 |
| 18 | 12 | 0.0984 | 176 | 11 | 107 | 6 | 19.0 |
| 20 | 8 | 0.0984 | 312.5 | 12 | 189.5 | 7 | 21.9 |

At the jump the forced set leaps from 0.21n to 0.93n in one held distinction, as in the mean field.

**How the phases pass the jump** (post hoc, `posthoc.py`). At n = 2^20 the phases at k* add, in sample 0, 55,027, 30,367, 16,195,
8,426, 4,918, 4,234, 8,159, 45,015, 222,960, 378,129, 99,261, 3,189 and 1 distinctions. Before the narrowest phase each phase adds
0.545 times the last (median of 29 ratios), and after it about 5.0 times (16 ratios; 4.5 at 2^18). The advisor's analysis of
Newton's method at a tangency predicted 1/(1 + ρ) = 0.54 and 1/(1 − ρ) = 6.9 with ρ = 1/√3 at c = 3: the shrinking rate matches to
two digits, the growth is somewhat slower, cut off as the forced set fills. This is why P5 failed: the leap is a geometric run of
phases, not one phase, and why the phase count is logarithmic (Kiefer, Luttenberger and Esparza 2007: Newton converges only
linearly at critical systems).

### Circuits

| Family | sizes | largest Strahler number (median) | P | P_dual | R |
| --- | --- | --- | --- | --- | --- |
| layered, width 1024 | d = 8, 16, 32, 64, 128, 256 | 4, 5, 7, 9, 11, 17 | 4 … 17 | 4 … 17 | d |
| unlayered, 256 inputs | 1,024, 4,096, 16,384, 65,536 gates | 2, 3, 4, 4 | 2 … 4 | 3 … 4 | 6 … 16 |

Narrower layered circuits (widths 64, 256) behave alike until their values settle to constants (4 of 10 alive at width 64,
d = 256). Structured families gave their values by construction (chain: R = L, one phase; ladder: k + 1 phases, dual 0; pyramid
and balanced tree: R = phases = height, dual 0).

## Limitations

- Every theorem is labelled in the proof; the new statements are the dual law for atoms, the not-all-equal gadget and the
  rejoining corollary, all known in kind. No claim about P versus NP or P versus NC is made.
- Phases are one parallel law, not every parallel algorithm. Many phases do not mean hardness (the ladder and the pyramid are in
  NL). The layered circuits' growth is measured for two laws only; random monotone circuits may be easy by other means.
- Random patterns are one model (m = 3n, uniform atoms, uniform held order; assumption A86), measured to n = 2^20 with 8 to 40
  samples per size. Exponents are fits over six sizes, not proved.
- P2a's agreement with n^(1/3), and P2b's failure, may change at larger n.

## Reproduce

```sh
.venv/bin/python -B experiments/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/gates.py
.venv/bin/python -B proofs/SEQUENTIAL-WALL-20261116-001B/SEQUENTIAL-WALL-20261116-001B-P001_phases_and_rank/check.py
.venv/bin/python -B scripts/longrun.py launch experiments/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/job.py --out RUN --workers 4 --case-mem 3G
.venv/bin/python -B experiments/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/summarize.py RUN
```

The registered run is `artifacts/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/run`
(long-running row SEQUENTIAL-WALL-L1, 21:55 to 22:18 UTC).

## Advisor

The advisor model (`claude -p --model claude-fable-5-2`) was consulted once, before the freeze, on the analysis, attributions,
predictions and words. It corrected four points, all adopted before any measurement: knot-ness and Horn-ness do not decide the
class; phases grow logarithmically at the jump (it predicted 10 to 13 at 2^20, growth +4 to +6; measured 12 and +6); strictly
alternating layered circuits make the phase count trivial; and the Strahler number is the least over derivation trees. It proposed
the dual law and the sharp exponents (n^(1/3) held, n^(1/4) failed), and judged the knot reading mostly a restatement, which this
note confirms. Its Newton rates (0.54 and 6.9) were checked post hoc above.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the sequential wall in knot patterns | **Status:** Successful (refereed, confirmed with fixes) | The wall located in knot terms (open uses, both kinds of overlap), the knot laws placed, and the rounds/phases separation measured: 9 of 13 frozen predictions held, 4 failed and are read |
| Local direction — phases of the forcing law | Continue, narrowly | The layered √-like growth and carrying open atoms (the owner's braid made exact) are the two open questions it leaves |
| Broader exploration — parallel complexity of knot laws | Known alternatives | Allender et al. classify every knot law; Newton/Strahler theory covers the phases; no new algorithm here |
| Long-term goal — G3 Hardness at three places | Capability gained | A measured, knot-native account of which overlaps force order; no hardness for SAT and no P vs NC claim |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Carry open atoms: a law that keeps the joint record of an open use on up to w distinctions instead of waiting a phase (the owner's braiding of two strands, made exact) | 3/3 — would say how many strands must be carried together to remove a phase, the trade-off the braid studies pointed at | 2/3 — the law is definable on atoms; records may grow, so the measure (record size) must be fixed first | Measure phases against w on the layered circuits and random patterns of this study → stop when phases stop falling with w, or records outgrow a polynomial | Selected · not started |
| 2 | Why layered random circuits need about d^0.4 phases | 2/3 — an explained law of how built-in order forces nesting | 3/3 — a defined max/min recursion on rank distributions, data in hand | Write the recursion for the rank distribution of a random layered circuit and solve it numerically → stop when it predicts the measured 4 … 17 within one, or fails | Alternative · deferred |
| 3 | Phases of not-all-equal propagation on the program's own patterns (weaves, three-regular contradictions) | 2/3 — places the program's main law in this picture | 3/3 — the gadget and code exist | Count phases from one held pair on six-regular weaves and three-regular contradictions → stop at a clear trend over three sizes | Alternative · deferred |
| 4 | Prove the logarithmic phase law at the jump from the tangency analysis | 1/3 — known in kind (Newton at critical systems) | 2/3 | Turn the 0.545 shrink rate into a bound on phases for the mean-field map → stop at a proof or an obstacle | Alternative · deferred |

**Corrections:** none at close; after the referee, four (two Narrowing, two Not a block), logged in `docs/CORRECTIONS.md` and knotlab's
HISTORY.md: Theorem 4's condition restored in three summaries; "never in NL or L" read as never NL- or L-complete; Theorem 4(c)'s
last sentence limited to P-hard families; P2a's verdict rests on the last size. The advisor's four corrections were to this study's
own unpublished design.

**Goals:** G3 checkpoint (capability gained), no goal changed; G16 not moved.

**Assumptions:** two new entries, A85 (measure: what must be worked in order is read by the phases of the forcing law, and on
patterns without cycles by the lesser of it and the dual law) and A86 (scope: a typical atom pattern is uniform atoms at three per
distinction with a uniform held order).

**Basket:** the holes-and-proofs line's basket was read; none of its untaken directions is this question.

## Referee

`SEQUENTIAL-WALL-R1` (background referee thread, fresh code, no Codex; [report](referee-R1/report.md)): **confirmed with fixes, no
Block.** Theorems 1 to 6 hold (Theorem 3's minimal-tree argument is correct); Theorem 5's table recomputes (34 knots, 2 / 2 / 14 / 16,
all 14 definitions valid, and none of them needs a held value: identifying variables and one hidden distinction suffice); the
pre-registration and code hashes are intact; the measurements reproduce within noise in fresh code (median R* 32, 52.5, 86, 142 and
P* 6, 7, 9, 10 at 2^10 … 2^16; 0 failures of Theorem 1 in 115,542 cases). Folded in on 16 November:

1. **Narrowing.** Theorem 4's condition was dropped in `docs/KNOT_INTUITION.md`, the G3 entry of the goals and the public glossary
   entry "Reused; demanded several ways; rejoining"; restored there: the wall needs reuse unless P = NC and several-way demand
   unless P = NL.
2. **Not a block.** "Never in NL or L" (proof, this note, the objects row) is false as written, since the two AC⁰ laws are in L; it
   means never NL-complete or L-complete, which is what Baker–Pixley gives.
3. **Not a block.** Theorem 4(c)'s last sentence tied several-way demand to patterns needing many phases; the pyramid has many phases
   and none. Many phases need only reuse (Theorem 3); a P-hard family needs reuse unless P = NC and several-way demand unless P = NL.
4. **Narrowing.** P2a's "held" rests on the eight samples at 2^20 (table above); the exponent is about 0.30 to 0.36 and n^(1/3)
   stays plausible.

The tally stays 9 of 13 by the frozen rules, with P2a marked as resting on the last size.

## Final report as sent

Posted to the owner's project thread on 2026-11-16 at 22:27:42 UTC (the decision-note link corrected at 22:28:15 UTC):

**Result:** knot patterns do hit the sequential wall, and the knot picture shows exactly where. Once one distinction of an atom (A ∧ B → c) is settled, what's left is a two-place rule, and every two-place rule can be followed at once. Order is forced only where an atom has to be used as a knot, with both its loops still open at the same stage. Counting those stages ("phases") gives the classical Strahler/Newton count, so as theory this restates known results. The measurements are new:

- On random atom patterns at the jump, step-by-step propagation takes about n^0.30 rounds (312 at a million distinctions), while untangling takes only 12 phases, about 0.57 more per doubling.
- Unlayered random circuits need at most 4 phases. Layered ones need about d^0.41.
- Being a knot doesn't decide the outcome. Of the 34 three-place knot laws, 2 are trivial, 2 are parity, 14 hit the wall and 16 are NP-complete.
- The wall needs both kinds of overlap: a distinction reused by several atoms, and one demanded several ways. Braids stay an analogy here.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the sequential wall in knot patterns | **Status:** Successful (referee pending) | Wall located in knot terms, 34 laws placed; 9 of 13 frozen predictions held, and the 4 that failed are explained |
| Local direction: phases of the forcing law | Continue, narrowly | Layered growth and carrying open atoms are still open |
| Broader exploration: parallel complexity of knot laws | Known alternatives | Allender et al. and the Newton/Strahler theory cover it; no new algorithm |
| Long-term goal: G3 Hardness at three places | Capability gained | Which overlaps force an order is now measured; no claim about P vs NC |

**Next step:** Research directions. Selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Carry open atoms (your braid made exact) | 3/3, says how many strands must be carried together to save a phase | 2/3, the record-size measure has to be fixed first | Phases against record width on layered circuits → stop when phases stop falling or records outgrow polynomial size | Selected · not started |
| 2 | Why layered circuits need about d^0.4 phases | 2/3 | 3/3 | Solve the rank recursion → it matches within one, or fails | Deferred |
| 3 | Not-all-equal phases on the program's own patterns | 2/3 | 3/3 | Phases on weaves and three-regular contradictions → a clear trend over three sizes | Deferred |

**Corrections:** none. **Goals:** G3 checkpoint (capability gained); no goal changed. **Assumptions:** two new entries, A85 (measure) and A86 (scope). **Advisor:** consulted before the freeze; I adopted its four corrections, and its predicted Newton rate of 0.54 matched the measured 0.545. [Decision note](https://github.com/jscul/knotlab/blob/main/research/SEQUENTIAL-WALL-20261116-001/sequential_wall.md)
