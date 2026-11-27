# Does growth make the step one layer up typical? What stands


> **Referee R1: confirmed with fixes, no Block** ([report](referee-R1/report.md)). The counts reproduce, and the full
> census settles the weighting: **4,213 of the 5,111 growing census starts (82.4%) carry the step on a chain of eight at
> round 6** (59.5% of all 7,075 starts), each with a witness needing all eight chain laws in all three roles and at least
> one birth's law. **Narrowings:** of the 2,808 chains checked, 2,803 pass the frozen test, 2,800 also need every chain
> law, and 2,489 (88.6%) pass the extra test that no stage bond reads an upper reading (all 10,696 chains: 8,941, 83.6%).
> The upper exclusion follows from the four clauses alone, so the chain's eight laws suffice; other stage laws can remove
> a lower word (all 33 such failures: an extra law on the chain's (0, 1, 5)) or make an upper reading visible to one lower
> bond. A larger stage can supply other readings for the same chain (35 of 36 one-distinction extensions qualify). The
> sample includes one entry of a three-start pilot (dropping it: 603 of 731). Credit: the chain construction and the
> eight-law explanation are the earlier referees'. A proof sketch of why eight is in [why_eight.md](why_eight.md).

`CHAIN-STEP-20261127-001`. Frozen in commit 604ddb09f1. Results are in `out/`. Referee pending.

**Answer: yes, under the census weighting.** Of 1,000 held-out census starts, 732 grow, and every one of them is still
growing at round 6. The share of them holding a chain of eight three-place knots, by round:

| Round | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Growing starts with a chain of eight | 0 | 0 | 6 | 27 | 81 | 344 | **604** |
| Share | 0% | 0% | 0.8% | 3.7% | 11.1% | 47.0% | **82.5%** |

- **C2 held:** the share is below 5% at round 2 and well past 30% at round 6.
- **C1 failed narrowly:** 2,803 of the 2,808 chains checked (99.8%) carry the step on their whole stage, and 2,800 need
  every one of their eight laws. The five that fail are on two starts (census 90 and 2030). Their three upper relations
  still take seven words with every pair free, but the stage makes one of the four lower triples miss more than its one
  triple, so the frozen form does not count them.
- **C3 held vacuously:** none of the 1,123 stages the converse read (rounds 1 and 2, at most 19 distinctions) has a step
  or a chain. A chain of eight alone needs 17 distinctions.

| First round with a carried step | 2 | 3 | 4 | 5 | 6 | none by round 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Starts | 6 | 21 | 54 | 263 | 260 | 128 of the growing starts (and the 268 that never grow) |

**Reading.** Growth makes the step one layer up typical. Under the census weighting, ordinary growth builds a chain of
eight three-place knots on 82.5% of growing starts by round 6. [R1: of 2,808 checked chain occurrences, 2,803 pass the frozen test, 2,800 also need every chain law for each role, and 2,489 pass the test against every stage bond as well.] The step's six agreements are fixed by the chain: the bare chain of eight
has exactly one pattern. [R1: the bare chain fixes one pattern on its own 17 distinctions; a larger stage can supply further readings for the same chain.] The
remaining choices are which pair reads "both", and which chain (a stage may hold many).

[R1: ordinary growth frequently builds a sufficient eight-law chain under the stated census weighting; the seven allowed upper words have whole-stage extensions; other stage laws can remove a lower word or make an upper reading visible to a single lower bond.]

## On the owner's rungs

- **Repetition:** met.
- **The tower's next step:** reached, made by ordinary growth on most growing starts (computed, this study; the chain
  mechanism refereed in `FOUR-CLAUSE-20261127-001`).
- **The tower's every step:** open. Does a longer chain carry a step two layers up?
- **Recursion:** not shown.

## Intuition (a link, not evidence)

**A chain is the program's simplest long part, and growth makes long chains because it never closes.** Every birth adds
a fresh distinction, so the born region keeps extending, and chains of single sharings are what extension leaves behind.
A chain of three knots carries clauses on agreements; a chain of eight carries a clause on readings of those. That
suggests a length per layer: 3, then 8, then perhaps 3 × 8 − 1 = 23, or 2 × 8 + 2 = 18 if each layer doubles its
predecessor and adds a link. Cheapest test: on bare chains of 18 to 23 knots, search the step two layers up with a
transfer-matrix count along the chain (exact, since a chain has no ring).

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: chains and the step under growth | **Status:** STOP (C2 held; C1 at 99.8%, failing on 5 of 2,808; C3 vacuous) | 82.5% of growing starts carry the step by round 6 |
| Local direction: the tower's next step under growth | Reached, typical | Chains of eight, built by growth, carry it |
| Long-term goal: G17 with G18 | Advanced | A second-layer fact made by growth and typical under a named weighting |

**Next step:** Continue with direction 1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The tower along chains: does a longer chain carry a step two layers up? | 3/3 | 2/3 | Transfer-matrix search on bare chains of 9 to 24 knots for four clauses among the step's upper readings → a length, or none to 24 | Proposed |
| 2 | Why eight: an exact account of the bare chain's pattern | 2/3 | 3/3 | Read the pattern's carriers along the chain and derive the clause from the not-all-equal laws by hand → a proof, or a counterexample | Proposed |
| 3 | The five failing chains: what the stage adds | 1/3 | 3/3 | Read the extra missing lower word on census 90 and 2030 → a rule | Proposed |

**Corrections:** none.
**Goals:** checkpoint row added (G17, G18).
**Assumptions:** none added (the chain definition, the carried pattern, the four-clause form and the caps are named in
the note; A309 holds the form).
**Scaffolds:**
- The chain definition and the carried pattern: the bare chain's only one, so not a free choice.
- The census weighting of starts.
- The six-round limit, the 1,000-chain cap and three chains checked per stage.

The result is about the model under the four-clause form.
**Advisor:** not consulted (usage limit).
