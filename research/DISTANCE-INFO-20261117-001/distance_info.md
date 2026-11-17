# Is distance the only form of information

Epic `DISTANCE-INFO-20261117-001`, 17 November 2026, by Claude; challenges assumption A97, the owner's reading. Goals G1 and G16.
Referee pending. Pre-registration: [preregistration.md](preregistration.md), frozen in commit `d8e3b518c` at 17:41:21 UTC; the
census ran 17:41:27 to 17:46:38 UTC. Code: [tables.py and census.py](../../experiments/DISTANCE-INFO-20261117-001A/DISTANCE-INFO-20261117-001A-E001_tables/);
results: [census.json](../../artifacts/DISTANCE-INFO-20261117-001A/DISTANCE-INFO-20261117-001A-E001_tables/census.json).

## The answer

Read as the program's bond distance between pairs of distinctions, **distance is not the only form of information**. It fails
already at four distinctions, and at six it leaves 96% of all not-all-equal bases sharing their distances with another base that
allows different states. Distance between sets (which sets of distinctions are knots in the allowed states) is not enough either.
What carries everything, through six distinctions and in every sampled base at seven, is each knot of the allowed states together
with **which joint states it excludes**: how far, and which way.

| Reading of a base's "distance information" | Distinct readings / relations, n = 4 | n = 5 | n = 6 | n = 7 (sampled) |
| --- | --- | --- | --- | --- |
| (a) bond distance of every pair | 12 / 16 | 293 / 1,023 | 10,012 / 97,248 | 88,428 / 258,384 |
| (b) the same, ties signed equal or unequal | 12 / 16 | 362 / 1,023 | 11,560 / 97,248 | 94,987 / 258,384 |
| (c) which sets are bonds (distance between sets) | 16 / 16 | 593 / 1,023 | 54,229 / 97,248 | 217,969 / 258,384 |
| (c-s) the same, ties signed | 16 / 16 | 662 / 1,023 | 56,722 / 97,248 | 227,282 / 258,384 |
| (c′) every bond with the joint states it excludes | 16 / 16 | 1,023 / 1,023 | 97,248 / 97,248 | 258,384 / 258,384 |
| (d) prime implicates (control) | 16 / 16 | 1,023 / 1,023 | 5,000 / 5,000 checked | 5,000 / 5,000 checked |

A distinct reading for every relation means the reading determines the allowed states.

**The smallest failures.**
- **Four distinctions, pairwise distance.** Three of the four knots on four distinctions allow 8 states; all four allow only the 6
  states of weight two. In both, every pair lies in a knot of three, so every pair is at bond distance 2. The tables agree and the
  allowed states differ, and the two are not the same up to renaming (8 against 6 states). Pairwise distance does not say which
  triples are knots.
- **Five distinctions, distance between sets.** A base whose states are a single state and its flip has every pair tied, at
  distance 1, and its bonds are all the pairs; which state it is cannot be read from distances, only from the signs of the ties.
- **Five distinctions, sets with signed ties.** Two bases with the same bonds (two unequal pairs, four bonds of three) and the same
  tie signs differ in which antipodal pair each three-place bond excludes, 000/111 in one, 001/110 in the other. A knot has an
  orientation too.

**What it means for A97**, by the outcomes stated before the run. The plain reading, that a base's information is carried by how
far its distinctions are from one another, is false at the smallest size where it could fail (n = 4). Neither the sign of ties nor
distances between sets repairs it. The owner's reading survives only if "distance" includes orientation, which knots exclude which
joint states. Taken that way, it is close to restating the relation by its forbidden states, and I cannot say whether the owner
means it so. Status: A97 is under challenge, its plain reading overturned; the question for the owner is whether his "distance"
includes "which way".

**What the knot picture explained.** "This versus that" has two parts here: how far (the size of the least knot that ties two
distinctions) and which way (which joint states that knot rules out). The census shows the second part is not redundant: it is
most of the information. In the literature's terms bonds are the minimal non-shattered sets, so (c) is the shattered-set complex,
which does not determine a set system in general (Pajor 1985 and the lopsided-family literature), and a relation is not determined
by its binary projections (Montanari 1974). That (c′) determines every not-all-equal relation through n = 6 is the local finding.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | (d) collides nowhere | held | none at n ≤ 5, nor in 5,000 checked at n = 6 and 7 |
| D1 | (a) collides at n = 4, 12 tables for 16 relations, not isomorphic | held | 12 / 16; one group of 5 (four of 8 states, one of 6) |
| D2 | (b) same at n = 4, finer than (a) at n = 5 | held | 12 at n = 4; 362 against 293 at n = 5 |
| D3 | (c) clean at n = 4, collides at n = 5 (isomorphic) | held | 16 / 16; 593 / 1,023, smallest collisions isomorphic |
| D4 | (c-s) clean at n = 5 | **failed** | 662 / 1,023: three-place bonds carry an orientation that signed ties do not |
| D5 | (c′) clean at n ≤ 6 | held | 97,248 / 97,248, and 258,384 / 258,384 sampled at n = 7 |

4 of 5 held, and the control; D4 failed.

## Limitations

- Bases of not-all-equal knots only, n ≤ 6 exhaustively and n = 7 sampled (400,000 random knot sets of 1 to 12 knots); the
  control (d) is checked on all relations only at n ≤ 5.
- (c′) determining every relation through n = 6 is a census, not a theorem; the advisor could not build a collision by hand and
  could not rule one out at larger n.
- "Distance" is taken as the glossary's bond distance; another reading of the owner's word would need its own test.

## Reproduce

```sh
.venv/bin/python -B experiments/DISTANCE-INFO-20261117-001A/DISTANCE-INFO-20261117-001A-E001_tables/census.py
```

## Advisor

Consulted before the freeze. It found by hand the collisions behind D1 and D3, proposed readings (c′) and (d), the isomorphism tag
and the literature (shattered sets, Pajor's lemma, lopsided families; binary projections, Montanari), and gave the four readings of
the outcome. Its guess D4 failed.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is distance the only form of information | **Status:** Successful (referee pending) | A clean answer: pairwise distance fails at n = 4; distance with orientation (bonds with their excluded states) determines every base through n = 6 |
| Local direction: distance as information | Unresolved | Turns on whether the owner's "distance" includes orientation; then a proof or a counterexample for (c′) at larger n |
| Broader exploration: what determines a relation | Known alternatives | Prime implicates; shattered sets do not suffice in general |
| Long-term goal: G1 and G16 | Obstruction learned | Space-like distance alone cannot be the whole of what a base holds; orientation is needed |

**Next step:** Research directions. No next action selected; the first depends on the owner's answer.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove or refute that every not-all-equal relation is determined by its bonds with their excluded states (c′) | 2/3, would make "distance with orientation" an exact statement | 2/3, a theorem attempt with a census to n = 7 or 8 as a check | Try a proof via prime implicates of complement-closed relations → stop at a proof, or at a counterexample | Alternative · awaiting the owner |
| 2 | Ask the owner whether his "distance" includes orientation, and record the answer in A97 | 2/3 | 3/3 | One question in the thread → stop at his answer | Asked in the report |

**Corrections:** none.

**Goals:** G1 and G16 checkpoint (obstruction learned); no goal changed.

**Assumptions:** A97 set Under challenge (its plain reading overturned); no new entry.

**Basket:** read; nothing in it is this question.

## Final report as sent

Posted to the owner's project thread on 2026-11-17 at about 17:50 UTC:

**Result of testing "distance is the only form of information": read as the program's distance between pairs, it fails.** It fails at the smallest possible size. On four distinctions, three of the four knots give the same pairwise distances as all four knots, yet they allow different states (8 against 6). At six distinctions, 10,012 distance tables cover 97,248 different not-all-equal bases.

Knowing which whole sets are knots, or whether tied pairs are equal or opposite, still isn't enough. What does carry everything (every base up to six distinctions, and every sampled one at seven) is each knot together with which joint states it rules out. In other words: how far, and which way.

So your reading holds only if "distance" includes that orientation. **Does your "distance" include which way, or only how far?** I've marked A97 "under challenge" until you say. 4 of 5 frozen predictions held.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is distance the only information | **Status:** Successful (referee pending) | Pairwise distance fails at n = 4; distance with orientation determines every base tested |
| Local direction | Unresolved | Turns on your answer; then a proof for larger n |
| Broader exploration | Known alternatives | Shattered sets and binary projections are known not to suffice |
| G1, G16 | Obstruction learned | How-far alone can't be all a base holds |

**Next step:** no next action until you answer; then a proof attempt that orientation always suffices (payoff 2/3, concreteness 2/3).

**Corrections:** none here. **Goals:** G1/G16 checkpoint. **Assumptions:** A97 now under challenge. [Decision note](https://github.com/jscul/knotlab/blob/main/research/DISTANCE-INFO-20261117-001/distance_info.md)
