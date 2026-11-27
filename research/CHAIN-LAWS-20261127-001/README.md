# Comparing growth laws on the step one layer up: chains of eight under the forbidding cuts

`CHAIN-LAWS-20261127-001`, for G18. Under ordinary growth, 4,213 of the 5,111 growing census starts (82.4%), or 59.5% of
all 7,075, carry the step one layer up on a chain of eight by round 6 (`CHAIN-STEP-20261127-001`, its referee's full
census count). `laws.py` counts the same on every census start under the two rival laws, A129 (`one_fewer`) and A130
(`arity_floor`). It grows each start for at most six rounds and checks the carried bare-chain pattern on the whole stage
for at most three chains per stage.

## Frozen predictions

- L1. Under each rival law, fewer than 10% of all census starts carry the step by round 6. Most starts stall.
- L2. Among the starts still growing at round 6 under a rival law, the share carrying the step is within 10 points of
  ordinary growth's 82.4%.
- L3. At least 95% of the chains checked carry the step on their stage.

Ordinary growth is not rerun here; its count is the CHAIN-STEP referee's.

**Scaffolds:** those of CHAIN-STEP (the chain, the carried pattern, the four-clause form, three chains per stage, six
rounds).
**Advisor:** not consulted (usage limit).
**Compute:** growth is fast and the checks run only on stages with a chain. The run is 8 chunks per law, with a 6G
memory cap and a 45-minute stop.
