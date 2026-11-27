# Does growth make the step one layer up typical? Chains of eight knots, round by round

`CHAIN-STEP-20261127-001`. Background, from `FOUR-CLAUSE-20261127-001`'s referee: the four-clause step one layer up
appears exactly on stages that hold a chain of eight three-place knots [R1: in the earlier 600-start sample through round two, for the alternating form]. A chain means each knot shares exactly one
distinction with the next, and no two non-consecutive knots share one. A bare chain of eight carries one pattern, three
steps, with every law needed. The thread replayed this. A chain of seven carries none.

## Method

`chains.py` finds chains of eight. `chain_step.py` grows 1,000 held-out census starts (seed 20261131) for six rounds.
The sample is outside the samples of UPPER-GROWN and FOUR-CLAUSE, their pilots and start 420 [R1: it includes one entry of the three-start pilot]. At every stage it records:
- the number of chains of eight, capped at 1,000;
- for at most three chains, the bare chain's pattern carried onto the chain and checked on the whole stage by a solver;
- on stages of rounds 1 and 2 with at most 19 distinctions, the full four-clause search (the converse test).

The carried pattern counts as a step on the stage when four things hold:
- each lower triple misses exactly its triple;
- no lower reading is read at a knot;
- each of the three upper relations takes seven words with every pair free.

Whether every chain law is needed is recorded beside it. Validated before the freeze: the bare chain, census start
5260 at round 2 (1 chain, a step) and census start 2439 at round 2 (2 chains, both steps).

## Frozen predictions

- C1. Every chain checked carries the step on its whole stage: a chain of eight in a grown stage is enough.
- C2. Chains of eight become common with growth, measured as the share of starts still funded at each round whose stage
  holds one. It is below 5% at round 2 and at least 30% at round 6.
- C3. On the stages read by the full search, every stage with a step holds a chain of eight.

**Scaffolds:**
- the chain definition;
- the bare chain's one pattern, as the reading carried;
- the four-clause form (A309 and the referee's form);
- the 19-distinction cap of the converse;
- the six-round limit.

**Advisor:** not consulted (usage limit).
**Compute:** about 25 seconds a start, in 12 chunks, with a 6G memory cap and a 45-minute stop.
