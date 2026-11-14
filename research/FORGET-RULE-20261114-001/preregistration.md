# What makes every way down forget: pre-registration

Epic `FORGET-RULE-20261114-001` (`CENSUS-FORGET-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. Frozen
in two stages: the split now, before any verdict is looked at; the rule later, before the held-out half is read. The thread's work,
reusing FREE-TARGET's per-call relations. The canonical K1–K3 test is unchanged.

## The question

`CENSUS-FORGET-20261114-001` decided forgetting exactly for all 12,772 census first-ray growers: some r with every product of r
per-call port relations rectangular. Which syntactic feature of a family's SELF calls and knots makes every way down forget? The aim
is a **proved** implication (rule ⇒ forgetting), with its coverage measured, rather than a fitted description.

## Stage 1: the split (frozen now)

A family is in the **training** half when `int(sha256(key).hexdigest()[:8], 16)` is even, otherwise **held out**. The key is the
canonical JSON of its definitions, as in the census records. The rule is derived from the training half only. The held-out verdicts
are read once, after the rule is frozen in stage 2. One-definition and several-definition families are reported apart, because the
gap argument's several-definition premise is under referee.

## Proved before stage 1 (stated, not tested)

**Necessary condition (N).** *(Narrowed after the referee: for a living family, one with an allowed state; an unsatisfiable family
has empty, hence rectangular, relations.)* Draw the port-passing graph on the three port positions, with an edge j → k for each SELF call whose
k-th argument is the copy's port j. If this graph has a cycle, the family does not forget. Proof: along the cycle's call word a
port value passes unchanged, so the product relation projects onto that pair of ports as equality. Every relation here is
complement-closed, so both values occur, and an equality on two coordinates with both values is not a product. Hence no power of
that word is rectangular. N is therefore a necessary condition for forgetting, and a rule for forgetting must imply N.

## Stage 2 (to be frozen after exploring the training half)

The rule, its proof that it implies forgetting with an explicit r, and its predicted coverage on the held-out half by stratum.

## Stage 2: the rules, frozen before the held-out half is read (2026-11-14)

Derived on the training half (6,388 families) only. The advisor model was consulted on the sufficient side
(`advisor_review_answer.md`). It proved that disconnection in the peeled composite gives a product, showed by an x ≠ y gadget that
the first downward-connectivity rule D is false, and gave the layered automaton. My additions are the free-from-above flag and the
generic start.

**Rule N (necessary, proved in stage 1).** A cycle of identity passing among the ports prevents forgetting.

**Rule A (sufficient, proved here).** `rule_A.py` builds a finite automaton over call words, as follows.
- **State.** A partition σ of a copy's three ports, induced by everything above it in the stretch, together with the set M of its
  blocks connected to the stretch's top and the set F of ports that no constraint above touches.
- **Start.** A generic copy of S: σ discrete, M all, F empty.
- **Step on call i.** Peel the copy's block. Repeatedly remove an NAE knot, or a side relation full on every two coordinates, that
  holds a distinction occurring in no other remaining constraint. ~~That distinction must be an own distinction not among call i's
  arguments, or a port in F.~~ *Corrected after the referee (Block on the sentence):* the distinction must not be among call i's
  arguments, **and** must be an own distinction or a port in F. Read literally, the frozen sentence let a port in F be peeled while it
  is an argument of the call being followed. That is false (the referee's counterexample `[[3,2,[["K",[0,1,2]],["K",[0,2,4]],["SELF",[1,3,4]]]]]`).
  The code (`rule_A.py`) always ran the guarded rule, so every count stands. Join σ with the components of what remains, and carry M and the new F down to the arguments.
- **Verdict.** Rule A holds when the reachable states with M non-empty form no cycle; r is at most the longest such path plus 1.

*Proof.* Each peeling eliminates a distinction that occurs in exactly one constraint of the stretch's composite. For NAE, and for a
relation full on every two coordinates, that elimination is exact: the constraint projects to the full relation on the rest. In
the peeled composite, top-down tracking of the partition of each layer, induced by everything above, sees every path, including
those that climb back. Once M is empty the stretch's top ports lie in components that miss its bottom ports. A disconnected system
has a product solution set, so the stretch's relation R_w is rectangular. Every stretch starts from a generic copy, F empty peels
no more than is valid, and a product composed with anything stays a product. So every word of length r is rectangular, and the
family forgets.

**Training results (seen).**
- N held with no exception: no N-cyclic family forgets.
- Rule A certified 1,107 families, all of which forget. Every exact r lies within A's bound.
- Rule A covers 35.7% of forgetting families: chains one-definition 694/1,659, several-definition 190/468; non-chains
  one-definition 117/439, several-definition 106/414.
- N-acyclic ⇒ forgetting held in 100% of chains (2,596) and 94% of non-chains (853/907).
- Regression control: the x ≠ y gadget (`gadget_control.py`) is alive and non-forgetting, and rule A refuses it.

## Predictions on the held-out half (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| H1 | **N is never violated.** No N-cyclic held-out family forgets (a check of the proof and the code). | any |
| H2 | **A is never violated.** Every rule-A certified held-out family forgets, with its exact r within A's bound. | any |
| H3 | **A's coverage replicates.** A certifies between 30% and 42% of held-out forgetting families, and each of the four strata lies within 8 points of its training share. | outside |
| H4 | **N nearly characterizes forgetting.** Among held-out N-acyclic families, forgetting holds in at least 99% of chains and at least 90% of non-chains. | below |

One- and several-definition families are reported apart. H2 for several-definition families rests on the gap argument's
several-definition premise, which is under referee.

## Prior work in the program

Added after the referee (2026-11-14): stage 1 was frozen after the objects gate took effect, so this section was owed.

`python3 -B scripts/track.py objects "syntactic rule for forgetting port relations rectangular" --until 2026-11-14 --exclude FORGET-RULE-20261114-001`
`python3 -B scripts/track.py objects "port passed down by identity cycle carried top port" --until 2026-11-14 --exclude FORGET-RULE-20261114-001`
`python3 -B scripts/track.py objects "which branches forget their incoming values" --until 2026-11-14 --exclude FORGET-RULE-20261114-001`

- `FREE-TARGET-20261114-001`: forgetting and its gap argument, the object this study explains.
- `BRANCH-DEPTH-20261112-001`: a rectangular power for one fixed call, counted (219 of 664) without a rule; a relative.
- `TRUE-RATE-20261113-001`, `REACH-CENSUS-20261113-001`: carried top ports, the identity mechanism; relatives.
- `TIE-CYCLE-20261114-001`: a later study generalising rule N; named so that the gate finds every top hit.
- `WEAK-APER-20261110-001`, `LEIBNIZ-BOARDS-20261110-001`: unrelated (boards), lexical hits.
