# Referee report CYCLE-RULER-R1 (light check, fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**

**What holds.**
- **All three recomputed claims.** Each conclusion is right.
- **The closed fork.** It is verified, minimal, and a true bond in the full pattern.

**What needs fixing.**
- **Claim 1's test.** It is weaker than the advisor's discriminator. Read as stated, the discriminator also fails, so the conclusion
  survives, but on the corrected test.
- **"Six" breaking cases.** Only five are serialised and analysed.

**How the work was split.**
- **The referee.** Fresh code, with LEVEL-REACH-R1's fresh pattern builder and networkx for the blocks.
- **The full pattern for claim 3.** RULER-LEVEL-R1's fresh rebuild of the breaking cases. The study's scripts were read but not run or
  imported.
- **Advisor.** The advisor model was not consulted.

## 1. The discriminator (`referee_chains.py`, `referee_chains.json`)

**Claim 1's test is not the advisor's discriminator.** **Narrowing.**
- **The discriminator.** It concerns the knots of the descending chain: "no cycle of knots passes through two members of one knot of
  the chain".
- **What `discriminator.py` tests.** Whether any cross-level knot anywhere in the pattern (levels 0 to 9) lies on a cycle. A pattern
  can have cycles elsewhere and still a cycle-free chain from level 3 to the target, so this test is much weaker.

**The test as stated.** I recomputed the existence of a descending chain from level 3 to level 3 + s none of whose knots lies on a
cycle.
- **On a cycle.** A knot is on a cycle of knots exactly when its biconnected block of the incidence graph holds another knot, which is
  the study's block test and is correct.
- **Rulers.** None of the 158 cyclic rulers has such a chain, at any s.
- **The others.** No cyclic non-ruler has one either: direct 100, other 73, dead 23, undecided 263 of 264, and no bond 18. The one
  undecided description has one at every s.
- **The study's own figures reproduce.** Every cyclic description except 14 cyclic no-bond ones has a cross-level knot on a cycle.

**So the conclusion survives**, on the corrected test: the discriminator explains none of the cyclic rulers, because none has a
cycle-free chain.

## 2. Girth

**It recomputes.** Every description cyclic at N = 9 (all six outcome groups, 636 descriptions) is already cyclic at N = 7, with Berge
girth 2: two knots share two distinctions.

**Reading at N = 7 is safe.** The depth-7 knots are a subset of the depth-9 knots, and girth is at least 2, so girth 2 at N = 7 means
girth 2 at N = 9.

**Not a block.**

## 3. The closed fork (`referee_fork_check.txt`, `referee_fork_bond.py`, `.json`)

**The core.** The 7-knot core from `cores.log` forbids (0, 1, 1) on {0, 001, 011}, and no 6-knot subset does, so the core is minimal.
Brute force over its 10 distinctions.

**The full pattern.** The breaking case containing this core is log sample 20, profile [3,3,4], which is RULER-LEVEL-R1's fresh case 1
(245 knots, N = 6). There, {0, 001, 011} allows 6 of 8 states, missing (0, 1, 1) and its complement, and all three pairs are full. It
is a bond of size 3 at s = 2, where the ruler gives 4.

**Not a block.** One small wording fix: two pairs of the four within-level knots share two distinctions, not one.

## 4. The other cores and the sample

- **Five cases, not six.** The note speaks of "six small breaking cases", but only five descriptions are serialised (RULER-LEVEL-R1),
  and `cores.log` analyses five, with cores of 7, 16, 18, 153 and 162 knots. The sixth (the second [3,3,4]) has no key. **Narrowing.**
- **The larger cores.** Their minimality was not checked in this light pass.
- **The sample.** All the cases come from one sample of 80 random descriptions, 57 of them decided. So "other shortenings are global"
  is a reading of four cores.

**Narrowing.**

## Fixes for the thread

1. **Replace claim 1's test** with the discriminator as stated: a cycle-free descending chain from level 3. It fails for all 158
   cyclic rulers. **Narrowing.**
2. **"Six" cases.** Say five analysed and one logged only, from one random sample. **Narrowing.**
3. **The fork's wording.** Two pairs of within-level knots share two distinctions. **Not a block.**

## Files

`referee_chains.py` and `.json`; `referee_fork_check.txt`; `referee_fork_bond.py` and `.json`.
