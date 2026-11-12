# Pre-registration: what does the drawing's work on a base with no drawing

Epic `LAW-RIGIDITY-20261112-001` (sub-goal B158, G15 with G16; program learning), written on 2026-11-12 before any learning run, at the
coordinator's go-ahead. Stage 1 is frozen here with the code in
`proofs/LAW-RIGIDITY-20261112-001A/LAW-RIGIDITY-20261112-001A-P001_the_two_jobs_apart/` (`jobs_lib.py`, `check.py`). Stage 2's
candidates are frozen in an addendum to this file, committed before any stage-2 run; what counts as native is frozen now. Nothing is
tuned after a result is read.

## The question

`UNDRAWN-LEARN-20261111-001` found that the learner learns and holds a count only while it feels the dissonance of a drawing's faces: with
dissonance at violated knots alone it held the count in 0 of 10 runs on one copy of the drawn knot pattern (2, 0, 4) (J1), where with faces
it held 10 of 10. The faces seemed to do two jobs: they restrict where the learner can rest (on J1, 4 of the 512 laws, of which 1 counts),
and they make changing a learned law cost something, so that a repair flips distinctions instead of re-signing knots. Which does learning
need, and what could supply it on a base with no drawing?

## What is known (prior work)

- **The law is a gauge field, and the faces are its plaquettes (the literature's terms; the analogy is mine).** A law gives a sign to each
  place where a distinction sits in a knot, and flipping a distinction or complementing a knot leaves it the same law: that is a field of
  signs on the incidences with a Z2 gauge symmetry at both distinctions and knots. What a law fixes are the sums of its signs around cyclic
  sequences of distinct knots and distinctions, each knot holding the distinction before it and the one after it (the literature's Berge
  cycles of a hypergraph). The faces of a drawing are particular such sequences, and the face term charges for the wrong sum on each: the role of the plaquette term in Wegner's Z2 lattice gauge theory (Wegner 1971), which gives the field its stiffness. On J1 the
  512 laws are the gauge classes, and fixing every face leaves the 4 Kasteleyn classes, the literature's first homology of the drawn torus.
- **Stability against plasticity.** Learned memories are kept stable by making learned parameters slow or costly to change: the
  stability-plasticity dilemma (Grossberg 1980; Carpenter and Grossberg 1987), catastrophic forgetting (McCloskey and Cohen 1989),
  consolidation by penalties on changing important weights (elastic weight consolidation, Kirkpatrick and others 2017) and by synapses with
  several timescales (Benna and Fusi 2016), and in learning materials, slow learning degrees of freedom kept apart from the fast physical
  ones (coupled learning, Stern, Hexner, Rocks and Liu 2021; memory formation in matter, Keim, Paulsen, Zeravcic, Sastry and Nagel 2019).
  So "a learned rule needs a cost to change, or a slower clock" is known. What is not known to me is which of the two jobs a learner of
  this kind needs, and whether a base with no drawing can supply it natively.

## Stage 1: the jobs apart, on J1 (frozen)

All variants use `UNDRAWN-LEARN-20261111-001`'s harness unchanged but for the engine and, where said, the repair.

- **F, with faces (reference):** W = 2 × violated knots + a graded face term. Learned and held in 10 of 10 (`LEARN-PARITY-20261111-001`).
- **K, knots alone (reference):** W = 2 × violated knots. 0 of 10 (`UNDRAWN-LEARN-20261111-001`).
- **R, the rest set without the grade:** W = 2 × violated knots + 2 × [some face lacks exactly one agreeing corner]. The floor is F's: no
  violated knot and every face with one agreeing corner, so the learner rests only at the 4 laws F rests at (check E: 4 laws with no even
  face, 1 counting). Leaving the set costs a flat 2, however many faces a change disturbs; sign changes are proposed where F proposes them.
- **RS:** R, and after each stop the repair flips distinctions only.
- **S (supplied rigidity, no rest set):** K, and the repair flips distinctions only. Not run: it is settled by the earlier runs. Its runs
  with K's seeds would be step for step K's until the first stop, and only 1 of K's 10 runs stopped at the count within 30 minutes, so S
  cannot reach 8 of 10. Rigidity of the repair alone does not let the learner find the count.

**Which variant is settled by its own definition.**

- **RS holds by definition.** A map is read from the law alone, and RS's repair does not touch the law, so whatever RS learns it holds,
  whenever the repair reaches the floor. Its mark therefore counts runs that stop exactly at the count (learned), held or not; holding is
  reported.
- **R is not settled.** Its rest set is F's, but its repair may re-sign knots: a change that mends a violated knot and disturbs faces costs
  −2 + 2 = 0 and is allowed, so a repair can leave the rest set and come back at another law. Whether R finds the count is not settled
  either: R has F's rest set but not F's grade, the face count that tells the learner how far from the rest set it is.
- R and RS use the same seeds (9700 + k), so each pair of runs is step for step the same until its first stop; RS's learned count is at
  least R's.

**The supplied rule.** RS's repair, flipping distinctions only, is a rule we supply, not a property of the base. If it is kept in the line's
learner after this epic, it is registered as an assumption then.

### Marks (decisive, one line each)

- **V:** RestEngine's running dissonance equals a fresh count (computed before freezing: it does).
- **E (exact):** 4 of J1's 512 laws have no even face, and 1 of them counts three (computed before freezing).
- **M1:** R, learned and held at the first target in at least 8 of 10 runs.
- **M2:** RS, learned (stopped exactly at the count) at the first target in at least 8 of 10 runs.

### Frozen readings

- **One job alone suffices:** M1 passes. The rest set, with only a flat cost of leaving it, is enough; the grade is not needed.
- **The rest set finds, holding needs rigidity:** M1 fails and M2 passes.
- **Neither job alone is enough:** M1 and M2 fail. The rest set does not let the learner find the count without the face grade, and
  rigidity alone does not either (S, above). Then what the faces do is the grade itself, a local count of how far each part of the law is
  from where the learner may rest, and stage 2 looks for a native grade.

## What counts as native (frozen for stage 2)

A candidate for the faces' work on a base with no drawing is native when:

1. it is computed from the knot pattern and the law alone: which distinctions each knot holds, and the signs; nothing from a drawing, no
   face, corner, tour or cyclic order, and no set of cyclic sequences chosen by us base by base;
2. it is one rule applied the same way everywhere (at every knot, every distinction, or every cyclic sequence of a kind defined by
   counts);
3. it does not read the target, the examples or the counting law;
4. any rule we supply (a cost on moves, a slower clock for signs) is named as supplied and registered as an assumption.

## Stage 2 (frozen in outline; candidates in an addendum before any run)

On the undrawn base U of `UNDRAWN-LEARN-20261111-001` (6 distinctions, 8 knots; exactly 1 of its 2,048 laws counts three at inputs 0, 1, 3,
read 4), with J1 as a control: at most two native candidates for the job stage 1 names, ten runs each on J1 and on U, seeds 9900 + k, the
same targets and budgets, 30 minutes per run. Before any stage-2 run, the addendum states each candidate, checks it against the four points
above, and states exactly which of U's laws it lets the learner rest at (computed, not run). Mark: learned and held on U in at least 8 of
10, and on J1 in at least 8 of 10. If stage 1's reading names the grade, the first candidate is the grade at the shortest cyclic
sequences of distinct knots and distinctions the base has (the literature's shortest Berge cycles), with the sum each is charged for fixed
by one rule for all. A word for these sequences goes through the language skill's advisor step in the addendum; "circuit", the advisor's
first suggestion, is already used by the record in other senses.

## Predictions

E as computed. M1 fails (no grade, and the repair can drift); M2 fails (the rest set is 4 of 512 laws, and without the grade the learner
has no way to find it). So the reading predicted is "neither job alone is enough", and the first stage-2 candidate is a native grade.

## Caps and long runs

Stage 1: 30 minutes per run, written as each finishes; per part (systemd, MemoryMax 24G, no swap) 40 minutes. Stage 2: the same per run,
40 minutes per part per base. Each learning part is registered in `docs/LONG_RUNNING.md` before it starts.

## Stop

Stage 1's reading and stage 2's candidates settled; or stage 2 stopping at its frozen mark. If B158 stalls at a frozen stop, the next cheap
step is the tie (B157).

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58, A66 (Confirmed).
