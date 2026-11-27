# Comparing growth laws on the step one layer up: what stands

`CHAIN-LAWS-20261127-001`. Frozen in commit fb0b54c376. Results are in `out/`. Referee pending.

**Answer.** On every census start (7,075), grown at most six rounds:

| Law | Grow at least one round | Still growing at round 6 | Of those, carrying the step at round 6 | Carrying it at some round |
| --- | --- | --- | --- | --- |
| Ordinary (CHAIN-STEP's referee) | 5,111 | 5,111 | 4,213 (82.4%) | 59.5% of all starts at round 6 |
| A129, a join takes one fresh distinction fewer | 5,111 | 817 | **816 (99.9%)** | 878 (12.4% of all) |
| A130, only what its arity needs | the same | the same | the same | the same |

- **L1 failed narrowly.** Under each rival law, 12.4% of all census starts carry the step by round 6, against a
  predicted bound of 10%.
- **L2 failed.** Among the starts still growing at round 6, the share is 99.9%, not within 10 points of 82.4%.
- **L3 held.** 3,919 of the 3,932 chains checked (99.7%) carry the step on their stage under the frozen test, and 3,918
  need every chain law. Like CHAIN-STEP's frozen test, this one does not check that no stage bond reads an upper reading.
  CHAIN-STEP's referee found that gate removes about a tenth of the chains, so 99.7% is an upper figure.

**Reading.** The cuts stall most starts: only 817 of the 5,111 that grow are still growing at round 6. Nearly every
survivor carries the step. Under the rival laws, continuing growth and the step one layer up go together almost without
exception. Under ordinary growth, every growing start keeps growing, and 82.4% carry the step by round 6.

So the step is not peculiar to ordinary growth. Whether a law keeps growing appears to be what decides it: the starts
that grow longest build chains of eight. The two rival laws agree on every count here. They differ only in when 48
starts stall.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the step under the rival laws | **Status:** STOP (L3 held; L1 and L2 failed) | 12.4% of all starts; 99.9% of the survivors |
| Local direction: G18, comparing growth laws | Advanced | The step comes with long growth under all three recorded laws |
| Long-term goal: G17 with G18 | Advanced | A second-layer fact typical of long growth, across laws |

**Next step:** Research directions (the coordinator's call). Two layers up along chains needs a careful design.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two layers up along chains, built on the parity reading of the spine (`CHAIN-STEP-20261127-001/why_eight.md`) | 3/3 | 1/3 | Write the level-four form in spine terms with the advisor, then search bare chains of 9 to 24 knots by transfer matrices → a length, or none | Proposed |
| 2 | Why survivors under the cuts carry the step: what stalls a start without a chain | 2/3 | 3/3 | Compare the 817 survivors' growth shapes with the 4,294 that stall → a rule, or none | Proposed |

**Corrections:** none.
**Goals:** checkpoint row added (G17, G18).
**Assumptions:** none added (A129, A130).
**Scaffolds:** those of CHAIN-STEP, with the same gap in the frozen test.
**Advisor:** not consulted (usage limit).
