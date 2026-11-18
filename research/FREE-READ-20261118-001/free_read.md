# The distance that reads freedom

Epic `FREE-READ-20261118-001`, 18 November 2026, by Claude. The coordinator's go-ahead after `TREE-STEPS-20261118-001`'s referee:
on the mixed cycle the referee found, look for a distance that reads freedom (the knot test's K2) rather than zero correlation,
agreeing with bond distance there and keeping what the irreducible-set distance δ_K gained on trees (hub-free, steps apart), or prove
none exists. Goals G1 and G16; tests A97; sub-goal B200. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `8cec5373d` at 08:19:50 UTC. The frozen run
  (`FREE-READ-B1`, `runs/free-read`, 08:19 to 08:20 UTC) finished its 232 tree cases but its cycles case failed when writing its
  output: a parity pair has no correlation, τ is infinite, and JSON has no infinity. The writer was fixed before any read-out
  (recorded in the contract's `amendments`) and the whole job rerun (`runs/free-read-r2`, 08:21 to 08:22 UTC, 233 cases, none
  failed); its tree results are identical to the first run's.
- Proofs: [proof.md](../../proofs/FREE-READ-20261118-001A/FREE-READ-20261118-001A-P001_trees/proof.md).
- Code: [freelib.py, job.py, merge.py, checks.py, posthoc.py](../../experiments/FREE-READ-20261118-001B/FREE-READ-20261118-001B-E001_bonds/).
- Results: [results.json](../../artifacts/FREE-READ-20261118-001B/FREE-READ-20261118-001B-E001_bonds/results.json); post hoc
  [posthoc.json](../../artifacts/FREE-READ-20261118-001B/FREE-READ-20261118-001B-E001_bonds/posthoc.json).

## The answer

**In the owner's terms.**
- **The distance asked for is bond distance, the knot test itself applied to sets of distinctions.** Take the least set holding
  both distinctions on which the allowed states, everything else forgotten, form a knot (some joint value never occurs, and
  forgetting any one member leaves the rest free), and count its size minus one. On every tree of knots, parity, not-all-equal or
  betweenness in any mixture, this is exactly steps apart plus one (proved). It cannot be fooled by hubs, since the statement covers
  trees of any size. On the mixed cycle it reads the parity knot as one knot, and on every pair of the four mixed cycles checked it
  is steps apart plus one (computed). It reads freedom by definition, it is read from the allowed states alone, and it ignores
  which value is called 1.
- **Why it works, in one line each.** The two distinctions, with the third distinction of every knot on the path between them, form
  a knot: fix them and every value along the path is forced, forget any one and the path goes slack. And no smaller set can be a
  knot: if it skipped the branch at some path knot, that knot would leave its two sides free of each other, so the set would split
  into two independent parts and one part would already be bound, which a knot forbids.
- **It needs knots that pass a value on.** Under the clause "not all ones" (also a knot by K1 to K3) no set is a knot holding the two
  ends of a chain of two or more clauses: setting the middle distinctions to 0 satisfies everything. The lower half of the theorem
  holds for every three-place knot; the upper half holds for knots that pass a value on, as parity, not-all-equal and betweenness do.
- **Where freedom and correlation part.** Bond distance and the correlation readings (τ, the cumulant distance δ, δ_K) agree on trees.
  On cycles of knots they part in two ways. On a ring of not-all-equal knots bond distance is still steps apart plus one, while τ
  shifts by fractions with the ring's length (the correlation feels the ring close; freedom does not) and τ fails the triangle
  inequality there, while bond distance satisfies it on every ring and cycle checked (post hoc). On a ring of three or four parity
  knots the ring's own distinctions together form a parity knot, so bond distance falls below steps apart plus one, and the
  correlation readings agree with it. And on a split line or split grid (cuts and their complements) every three distinctions form
  a knot, so bond distance is two for every pair, flat, while τ grades them (known from `COUNT-BALLS-20261118-001`; checked again post
  hoc). So bond distance answers the go-ahead, but not the whole of B200: it does not read split grids.

**Post hoc (after the read-out; no prediction):** two hybrids were tried, and each fails one side, on the record.
- **Freedom-gated cumulant distance δ_F**: δ's minimum over sets whose proper subsets are all free. It equals δ on every small base
  checked (all 16,766 pairs of every knot tree to five knots under every law assignment, all rings and mixed cycles, the split line,
  two split grids, a weave patch), and so reads the mixed cycle right. But it keeps δ's hub shortcut: the hub set with one child of
  each of 32 not-all-equal knots on x is free, so freedom gating cannot exclude it (argument from `TREE-STEPS-20261118-001A`, H1 and
  H2). The hub's binding is a correlation among free distinctions, invisible to any reading of which values occur.
- **Bonds or irreducible sets, δ_KB** = the lesser of δ_K and the cumulant reading over bonds: it fixes the mixed cycle's own pair
  (1.011), but on the same cycles it still reads pairs across the parity knot by their weak correlation the long way round (for
  example 5 where steps apart is 2), as δ_K does.

So on the bases checked, the plain cumulant distance δ reads everything (trees, mixed cycles within 0.11 of steps apart on every
pair, rings, split grids as τ) except hubs of at least 32 copies of one spin; δ_K mends hubs and breaks mixed cycles; freedom gating
cannot mend hubs; bond distance mends both but is flat on split grids.

| Base | Bond distance − 1 | δ | δ_K | τ |
| --- | --- | --- | --- | --- |
| Knot trees, any mixture | steps apart (proved) | steps apart to 7 knots (computed); below it at hubs of ≥ 32 copies (proved) | steps apart (proved except one mixed case, computed) | steps apart where C ≠ 0 |
| Trees of "not all ones" clauses | undefined past one knot (proved) | not computed | not computed | not computed |
| Mixed cycles (k = 2 to 5) | steps apart on all 154 pairs | within 0.11 of steps apart | misreads 52 of 154 pairs (x, y as k) | the long way round |
| Not-all-equal rings (3 to 6) | steps apart | = τ, fractional, no triangle inequality | = τ | fractional |
| Parity rings (3 to 6) | below steps apart on rings of 3 and 4 (the ring's own knot) | = bond distance − 1 | = bond distance − 1 | infinite (C = 0) |
| Split line, split grids | 1 for every pair (flat) | = τ on the grids | = τ | graded |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 4 gates | held | all pass |
| P1 | every six-knot tree, every law assignment: bond distance = steps apart + 1 | held | 0 of 94,848 pairs differ (1,216 bases) |
| P2 | 80 random seven-knot trees: the same | held | 0 of 8,400 |
| P3 | mixed cycles k = 2 to 5: bond distance − 1 = 1 for x, y; δ_K = k; δ ≤ 1.1 | held | 1; k; δ = 1.0113, 1.0012, 1.0001, 1.00002 |
| P4 | rings: parity bond − 1 = δ; not-all-equal bond − 1 = steps; alternating ≤ steps | held | every pair |
| P4b | alternating rings: bond − 1 = steps | held | every pair |
| P5 | not-all-equal rings: τ differs from bond − 1 by more than 0.01 somewhere | held | on every ring |
| P6 | "not all ones" chains of 2 to 4: no bond holds the ends | held | none |

7 of 7 held.

## What it means for A97 and B200

B200 asked for one distance read from the states for parity and not-all-equal bases alike. On trees the answer is the program's own
bond distance, proved: one step per knot under either law and any mixture, hub-free, with the cumulant distances adding nothing
there. On cycles freedom and correlation part, and the split grid is where they part most: every triple there is a knot, so freedom
alone is flat, while correlation grades the grid. A97 (distance is the only form of information) gains a proved distance on knot
trees that needs no measure at all, and a located gap: the split grid's grading lives in correlation, not in which values occur.

## Known results, and what this adds

Known, cited once: bonds are the minimal non-shattered sets of the family of allowed states (Sauer–Shelah, Pajor; shattering-extremal
families); the splitting lemma is the acyclic join-tree decomposition (Beeri, Fagin, Maier and Yannakakis 1983; Freuder 1982); on
parity bases bonds are matroid circuits. What this adds: the statement that the least non-shattered set holding two variables of a
tree of three-place constraints passing K2 has size at least steps apart plus two, with equality for parity, not-all-equal and
betweenness in any mixture and not for the clause "not all ones"; the advisor knows no published statement of it (no literature
search was run). In the
program it closes the bond-distance comparison that `CUMULANT-DIST-20261118-001` and `TREE-STEPS-20261118-001` got wrong (corrected
in `01941028d`).

## Limitations

- The theorem is for trees. On cycles everything is computed, on rings of up to six knots and four mixed cycles.
- The triangle inequality for bond distance is checked post hoc on 16 small bases, not proved.
- The hybrids δ_F and δ_KB were tried after the read-out; their failures are an argument (δ_F's hub) and a computation (δ_KB).
- Bond distance's search is exponential in the set size.

## Reproduce

```sh
d=experiments/FREE-READ-20261118-001B/FREE-READ-20261118-001B-E001_bonds
.venv/bin/python -B $d/checks.py
.venv/bin/python -B scripts/longrun.py launch $d/job.py --out runs/free-read-r2 --workers 8 --case-mem 1500M
.venv/bin/python -B $d/merge.py runs/free-read-r2
.venv/bin/python -B $d/posthoc.py      # post hoc: delta_F, delta_KB, split grids, weave patch
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage`
names claude-fable-5-2), asked before the freeze. It confirmed both halves of the proof with three lemmas made explicit, showed the
theorem is not law-independent (the clause counterexample, P6), confirmed P3 and P4, strengthened P4 to equality on alternating rings
(P4b), asked for a tolerance in P5, and named the literature. The post hoc hybrids were not put to it.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the distance that reads freedom | **Status:** Successful (referee pending) | Bond distance = steps apart + 1 on every knot tree of the three laws (proved), hub-free, right on the mixed cycle; 7 of 7 held |
| Local direction: one distance for both laws (B200) | Promising | Answered on trees; on split grids freedom is flat and only correlation grades, and the correlation readings either shortcut at hubs (δ, δ_F) or misread mixed cycles (δ_K, δ_KB) |
| Broader exploration: state-read distances | Known alternatives | Shattering and acyclic joins are classical; the tree statement is the program's |
| Long-term goal: G1 and G16 | G1 capability gained; G16 capability gained | G1: a proved distance on knot trees from which values occur alone. G16: freedom and correlation located as two readings that agree on trees and part on cycles |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One distance for split grids, mixed cycles and hubs: mend δ's hub shortcut without losing the mixed cycle (normalise a set's cumulant by its parts', tree cumulants, or charge each distinction its own binding), or prove no cumulant-of-sets reading can | 3/3 | 2/3 | the hub family by H1 in closed form against each candidate, then the frozen rings, cycles and split grids → stop at a candidate passing all or an obstruction | Alternative |
| 2 | Is bond distance a metric on every base? | 2/3 | 3/3 | every base of up to seven distinctions from parity, not-all-equal and betweenness knots, and a proof for parity bases by circuit elimination → stop at a proof or a counterexample | Alternative |
| 3 | Which three-place knots pass a value on (equality in the tree theorem)? | 1/3 | 3/3 | classify the three-place laws passing K2 up to switching and renaming by whether a chain of them is constrained → stop at the list | Alternative |

**Corrections:** none for this study (the correction it prompted, `01941028d`, is logged under `CUMULANT-DIST-20261118-001` and
`TREE-STEPS-20261118-001`).

**Goals:** G1 checkpoint (capability gained: bond distance, the knot test applied to sets, is steps apart plus one on every knot tree
of parity, not-all-equal and betweenness knots, proved, hub-free; flat on split grids) and G16 checkpoint (capability gained: freedom
and correlation located as the two state readings, agreeing on trees, parting on cycles); no goal changed.

**Assumptions:** A97 gains this study; no new entry.

## The final report as sent (18 November 2026)

**Outcome:** the distance that reads freedom is bond distance itself, the knot test applied to sets of distinctions. On every tree of
knots, parity, not-all-equal or betweenness in any mixture, it is exactly steps apart plus one (proved), so hubs cannot fool it, and
it reads the mixed cycle's parity knot as one knot. 7 of 7 frozen predictions held, with no exception among 103,248 tree pairs. The
catch is on cycles: on split grids every three distinctions form a knot, so bond distance is flat there and only correlation grades
the grid; and, post hoc, gating the cumulant distance by freedom does not remove its hub shortcut, because the hub's set is free.
Closed, referee pending.

The position table, the next-step line and the three directions as in Position above.

**Corrections:** none. **Goals:** G1 and G16 checkpoints (capability gained). **Assumptions:** A97 gains this study. **Advisor:**
before the freeze (proof check, the clause counterexample, P4b); not on the post hoc hybrids.
