# Which knot patterns must be worked in order: pre-registration

Epic `SEQUENTIAL-WALL-20261116-001` (the owner's parallelism question, picked up from his Codex session "Clarify P vs NP and
parallelism" of 14 November; goals G3 and G16), 16 November 2026. Frozen before any read-out of the measurements. The code
(`atoms.py`, `gates.py`, `knots_table.py`, `job.py` in
`experiments/SEQUENTIAL-WALL-20261116-001A/SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases/`) was written first and run only on
its gates, on the known classification of three-place knots (Step 1 below), on structured families whose values are settled by
construction, and on smoke cases with unregistered seeds whose values were not read; no registered random pattern or random
circuit was measured before this freeze. Code and long run by this thread with the shared runner. The canonical K1–K3 test is
unchanged.

## The question

The owner asked whether P versus NP is about what can be worked on in parallel. It is not (that is P versus NC), but it raised a
question of its own: do patterns of knots hit the inherently sequential wall, and does the way their knots overlap predict when
they do not? His guidance (16 November): the point is whether the knot picture, his braids and untangling, explains something;
results that restate known mathematics are fine when labelled.

The study works with the atom, A ∧ B → c ("A and B together demand c"), with some distinctions held at 1 by the outside, and asks
which distinctions are forced. Two laws compute the forced set. The **native law** works in **rounds**: an atom whose two demanders
are forced forces what it demands one round later. The **forcing law** works in **phases**: once one demander of an atom is
forced, the atom is no longer a knot but a two-place rule (B → c), and two-place rules can all be followed at once
(reachability, by doubling); a phase follows every such rule, and an atom waits for a later phase only when both its demanders are
first forced in the same phase, an **open use** of the atom as a knot. A distinction's phase is the least Horton–Strahler number of
its derivation trees (Theorem 1 in `proofs/SEQUENTIAL-WALL-20261116-001B/SEQUENTIAL-WALL-20261116-001B-P001_phases_and_rank/proof.md`),
so a family of patterns needing polylogarithmically many phases is decided in polylogarithmic parallel time. The **dual law**, on
patterns without cycles, spreads unforcedness the same way: an atom dies when one demander is unforced, and a distinction demanded
several ways waits until all its atoms are dead. The questions: how do rounds and phases behave on random atom patterns, at and
away from the jump where the forced set leaps; how do phases behave on random monotone circuits, layered (the classical sequential
prototype) and unlayered; and what does the overlap of atoms do to the phase count.

## In standard terms

Horn formulas with clauses ¬a ∨ ¬b ∨ c (the atom is the literature's definite Horn clause with two body atoms; "atom" in Datalog
means something else) and positive unit facts; the least model. Rounds: synchronous unit propagation, the height of the shallowest
derivation. Phases: the Newton iterates of the Boolean fixed-point system (Esparza, Kiefer and Luttenberger 2010), equal to the
least Horton–Strahler number (tree dimension) of a derivation tree. Random model: a random 3-uniform directed hypergraph with
m = 3n hyperedges (two tails, one head) and the first k distinctions of a uniform order as facts; in the mean field
x = α + (1 − α)(1 − e^(−3x²)) the closure jumps from about 0.21n to about 0.93n at the tangency α* = 0.098251, a
bootstrap-percolation-type discontinuous transition (here "the jump"). Circuits: monotone circuits with fan-in two, each gate AND or
OR with chance 1/2 and inputs true with chance 1/2, either layered (width w, depth d, inputs from the layer below) or unlayered
(each gate reads two random earlier nodes), encoded as atom patterns.

## Prior work in the program

`python3 -B scripts/track.py objects "rounds of forced deductions atom pattern untangling phases" --until 2026-11-16 --exclude SEQUENTIAL-WALL-20261116-001`

`python3 -B scripts/track.py objects "Horn unit propagation parallel depth P-complete Strahler Newton" --until 2026-11-16 --exclude SEQUENTIAL-WALL-20261116-001`

`python3 -B scripts/track.py objects "random atom patterns closure threshold held fraction" --until 2026-11-16 --exclude SEQUENTIAL-WALL-20261116-001`

`python3 -B scripts/track.py objects "monotone circuit value alternating layered random circuits" --until 2026-11-16 --exclude SEQUENTIAL-WALL-20261116-001`

`python3 -B scripts/track.py objects "untangle braid strands joint record" --until 2026-11-16 --exclude SEQUENTIAL-WALL-20261116-001`

- `LOOP-LOCK-20261112-001`: unrelated (locks of harmony stitches); matched on "round" only.
- `LEIBNIZ-BOARDS-20261110-001`: unrelated (one-bit laws on boards, the atom among them); no rounds or phases.
- `BASES-WITHIN-20261112-001`: unrelated (ending of outer patterns under lagged stitches).
- `UNSIGNED-ROUTE-JOINS-20261115-001`: a relative. The Codex session's positive-implication route family, decided by
  reachability in linear time; this study takes from it that two-place rules compose by reachability, and asks how many
  reachability phases a pattern of atoms needs.
- `SHARED-REPORT-CANCELLATION-20261115-001`: a relative, the Codex session's parallel result (resolution proofs of Θ(h) nodes with
  dependency chains of Θ(log h) on cycles of parity checks). This study measures phases of a law on atoms, not proofs of parity.
- `SIGNED-KNOT-OVERLAP-20261114-001`: a relative (2^r minimal obstructions decided in Θ(log r) rounds): the warning that counting
  overlaps measures neither work nor parallel time, which is why the measure here is the phase count, not a count of obstructions.
- `COMMON-FOLD-20261112-001`: a relative (the forced fraction of a not-all-equal growth, split into ties, propagation and search);
  a different law and population, and no rounds or phases.
- `LIFE-JUMPS-20261112-001`: a relative (the largest tie class over growing not-all-equal patterns, with a late jump); the jump
  there is in tie classes of a growing pattern, not in a forced set as held distinctions are added.
- `OLD-CORE-20261112-001`: unrelated (cores of growing not-all-equal patterns).
- `FORGET-RULE-20261114-001`: unrelated (forgetting in nested families); matched on general words.
- `NEST-READ-20261112-001`: unrelated (self-nested not-all-equal patterns).
- `BRAID-COUNTS-20261114-001`, `BRAID-READOUT-20261114-001`, `JOINT-BRAID-READS-20261114-001`: relatives, the Codex session's
  braid studies (a reversible ternary crossing; separate strand records lose what the joint record keeps; an advance message for
  b crossed pairs needs about 6^b bits unless the question comes first). This study's forcing law waits for one demander to be
  forced instead of carrying the joint record of an open atom. That is an analogy, not a claim: the atom is not reversible.
- `STRAND-RETURN-20261114-001` (deep search): a relative; its exact two-link hops along closed strands are the doubling inside one
  phase.

## Prior work outside the program

Known, and labelled so in the record. Cook's path systems (1974), the first P-complete problem, are atom patterns; monotone circuit
value is P-complete (Goldschlager 1977); Horn satisfiability and unit resolution are P-complete (Jones and Laaser 1976). With
constants, every Boolean constraint language is complete for AC⁰, L, NL, ⊕L, P or NP (Allender, Bauland, Immerman, Schnoor and
Vollmer 2009). No three-place knot is closed under majority (Baker and Pixley 1975: a majority-closed relation is fixed by its
two-place shadows), so no knot law is NL or L; `knots_table.py` places all 34 three-place knots: 2 in AC⁰ (single-sign clauses), 2
⊕L-complete (parity), 14 P-complete (the atom, its dual, and knots that define one of them with held values), 16 NP-complete
(not-all-equal among them), the same counts as the advisor's hand classification. Being a knot therefore does not decide the
class. Newton iterates and Strahler numbers: Esparza, Kiefer and Luttenberger (2010), Esparza, Luttenberger and Schlund (2014);
Newton converges only linearly at critical systems (Kiefer, Luttenberger and Esparza, STOC 2007). Polynomial fringe gives NC
(Ullman and Van Gelder 1988; LOGCFL, Ruzzo 1980). Formula value is in NC¹ (Buss 1987). Pebbling of pyramids (Cook 1974). Random
Horn satisfiability (Istrate 2002; Moore, Istrate, Demopoulos and Vardi 2007); hypergraph collapse (Darling and Norris 2005);
finite-size scaling of cores (Dembo and Montanari 2008); parallel peeling (Jiang, Mitzenmacher and Thaler 2014); the stripping
number grows like n^(δ/2) at distance n^(−δ) from the core threshold (Gao and Molloy 2018). Few subpowers (Berman, Idziak, Marković,
McKenzie, Valeriote and Willard 2010) is the known form of "open atoms cannot be carried cheaply". Not found: the Newton phase
count of random Horn systems at their closure jump, and the Strahler number of random monotone circuits as they grow.

## Settled by construction (stated, not tested)

- Chain of L atoms with held helpers: R = L, one phase. Ladder of k steps: phase k + 1 at its top. Pyramid of height h: R = h phases
  = h. Balanced tree of height d: R = d phases. The dual law takes no phase on any of them (nothing unforced). (Gates G6.)
- P ≤ R always, the forcing law ends in the native law's forced set, and on patterns without cycles every distinction is forced or
  found unforced by the dual law (Theorems 1 and 6; gates G2, G7).

## Predictions (frozen)

R* and P* are the rounds and phases at k* (the least k whose closure holds half the distinctions, the sample's own jump); medians
are over a size's samples.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: `gates.py`, `check.py` and `knots_table.py` pass; in every random case the Strahler number by relaxation equals the phase at k* and k* − 1; every circuit's forced set equals its evaluation, and every circuit distinction is forced or found unforced. | any fails |
| P1 | Away from the jump the native law is fast: at α = 0.03, 0.06, 0.2 and 0.4, median R(2^20) ≤ 3 × median R(2^12). | any exceeds |
| P2 | The jump slows the native law polynomially: the slopes of log₂ median R against log₂ n, fitted over n = 2^14 … 2^20, are at least 0.15 both at k* and at α* = 0.098251. | either below |
| P2a | (sharp, advisor) at k*, that slope lies in [0.29, 0.37] (n^(1/3), a critical excursion). | outside |
| P2b | (sharp, advisor) at α*, that slope lies in [0.21, 0.29] (n^(1/4), a sample's threshold n^(−1/2) away and ε^(−1/2) passage). | outside |
| P3 | The forcing law slows only logarithmically at the jump: median P*(2^20) ≤ 16, median P*(2^20) − median P*(2^10) between +2 and +8, and the least-squares slope of median P* against log₂ n over 2^10 … 2^20 in [0.2, 0.8] phases per doubling (advisor: about 0.49; Newton is linear, not quadratic, at a tangency). | any fails |
| P3b | Rounds and phases separate: median R*/P* at 2^20 is at least 3 × its value at 2^12. | below |
| P4 | Near the jump, from above, phases fall slowly and rounds like ε^(−1/2): at n = 2^18 and 2^20, median P at k* + 0.001n minus median P at k* + 0.03n is between 1 and 5, and median R at k* + 0.001n ÷ median R at k* + 0.03n is between 2 and 12. | any fails |
| P5 | One phase carries the leap: at n = 2^20, the largest phase at k* holds at least half the distinctions forced at k* that are not held, in at least 7 of the 8 samples. | fewer |
| P6 | Layered random circuits need more phases as they grow: width 1024, median largest output Strahler number (over samples with a true output) at d = 256 ≥ 1.6 × at d = 64 and ≥ 6; at least 7 of the 10 samples at d = 256 have a true output. | any fails |
| P6-linear | (exploratory, either outcome informative) that ratio is ≥ 3, as for growth linear in d. | below |
| P7 | Both laws stay slow on layered circuits: width 1024, median min(P, P_dual) at d = 256 ≥ 1.6 × at d = 64. | below |
| P8 | Unlayered random circuits need few phases: median largest Strahler number over true gates ≤ 8 at every size (1,024 to 65,536 gates on 256 inputs), growing by at most 3 from 1,024 to 65,536 (advisor: about √(2 ln(size/inputs)), at most about 5). | either fails |
| P9 | The fringe bound is loose at the jump: median largest log₂ fringe at k* ≥ 3 × median P* at n = 2^16, 2^18 and 2^20. | fails at any |

A prediction that fails is recorded as failed, with the reading. No prediction is changed after this freeze. P2a, P2b, P3, P6-linear
and P8 carry the advisor's analysis; my own first view, that phases stay O(log log n) at the jump (P3 with "≤ 10 and growth ≤ 3"),
was dropped on the advisor's argument and is kept here as the rejected alternative: if the measured growth from 2^10 to 2^20 is at
most +1, that view was right.

## Runs and stop rule

One shared-runner job (`job.py`): random atom patterns at n = 2^10 (40 samples), 2^12 (40), 2^14 (30), 2^16 (20), 2^18 (12), 2^20
(8), m = 3n, each with k* found exactly by one incremental closure along a random order; rounds, phases, phase sizes at k*,
k* − 1, k* ± {0.001, 0.003, 0.01, 0.03}·n, α* and α ∈ {0.03, 0.06, 0.2, 0.4}; Strahler number by relaxation and log₂ fringe at k*
and k* − 1; structured families; layered circuits w ∈ {64, 256, 1024}, d ∈ {8, 16, 32, 64, 128, 256}, 10 samples each;
unlayered circuits with 256 inputs and 1,024 to 65,536 gates, 10 samples each. Four workers, 3G per case, MemoryMax 16G; expected
about one to two hours; registered in `docs/LONG_RUNNING.md`. The study stops after this run and its summary; then the decision
note, the referee hand-off and the report.

The advisor model (`claude -p --model claude-fable-5-2`) was consulted once before this freeze, on the analysis, the
attributions, the predictions and the words. It corrected four things, all adopted: the class of a knot law is not decided by its
being Horn (two single-sign clauses are knots in AC⁰); the forcing law's phase count grows logarithmically at the jump, not like
log log n; strictly alternating layered circuits make the phase count equal the number of AND layers, so the circuits here mix AND
and OR within each layer and add an unlayered family; and the Strahler number must be the least over derivation trees (relaxation
downward), not the least solution of its equations, which is wrong on unsupported cycles. It proposed the dual law, the sharp
exponents of P2a and P2b, and the words below; it judged the knot reading "mostly a restatement", which the report will test.

Words: **round** (one step of the native law), **phase** (one stage of the forcing or dual law; never "phase transition", which is
"the jump" here), **open use** (an atom whose two demanders are first forced in the same phase), **reused** (a demander in two or
more atoms), **demanded several ways** (demanded by two or more atoms; not the glossary's choice rule, though under the least
reading it plays that part), **rejoining** (one distinction below both demanders of one atom in a derivation tree). "Rank" was
dropped (linear algebra's rank is needed for parity), and so was "nesting" (the record's nested families); the measure is the
phase count, and the trees' measure keeps the literature's name, Strahler number. "Depth" stays reserved: parallel time is called
parallel time. Braid and strand appear only in the owner's words.
