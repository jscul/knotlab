# Which upper readings can one stage bond determine?

**316 of the 2,808 checked chains have a determining stage bond.** In every case that bond contains both agreement carriers of one upper reading. It then determines both “either” and “both” on that pair, and every choice of which upper pair reads “both” uses one of these two functions. Of the 2,803 chains passing the study's frozen tests, 314 have a determining bond. Of the 2,800 also needing every chain law, 311 have one. **2,489 checked chains pass every test.** [Joined counts](other_bonds_summary.json)

There are 1,459 ways to choose a checked chain, one of its three upper pairs and a determining lower bond. In 201 the third carrier belongs to the six named carriers. In 1,258 it is another stage agreement. The second grown round of four-knot census entry 87 supplies a direct example with a five-law explanation. One of those five lies outside its checked chain. [Witness and hand derivation](other_bonds_paired.md)

## Why this covers every stage bond

Fix a checked chain. Let X and Y be the two designated, disjoint raw carriers of one upper reading U. Each lower value is 1 exactly when all members of its carrier agree. U reads either “both” or “either” of those two values. Let D be the five or six raw distinctions in X and Y together. An eligible lower bond uses three disjoint carriers, each on two or three raw distinctions. Its lower word set is nonempty and proper, every pair is free, and each individual agreement can vary at fixed raw values of each individual source knot. The argument admits lower bonds missing any number of words.

1. **All of D is necessary.** For each d in D the program finds two allowed states differing only at d and with different U. To find such states, each source law containing d must already see both raw values among its other members. The rest of d's named carrier must agree, so flipping d changes its agreement. The opposite named carrier must agree for “both” and disagree for “either”. These conditions are also sufficient. All five or six tests succeeded for each of the 16,848 choices of checked chain and upper function. A triple of lower carriers omitting even one of these distinctions gives the same three readings on its witnessing states.
2. **Many individual carriers cannot occur.** Consider e outside D. Suppose an allowed state admits all four combinations of d and e with every other raw value fixed and flipping d changes U. A carrier on d and e has the same agreement when both bits are reversed. For a carrier on d, e and f, choose e opposite f and change d. That carrier reads 0 both times. Either construction supplies two different values of U while preserving this carrier and every disjoint carrier. To find the four combinations exactly, use the preceding flip conditions on d and require both values among the remaining members of each law holding e after removing e and, if present, d. The program also uses a single allowed quartet to certify multiple exclusions when other raw distinctions are freely changeable. Every carrier still possible goes forward.
3. **Test each remaining individual carrier.** For three-member carriers, a d-flip witness with the two other members unequal already preserves its agreement. For the others, two complete copies of the stage are constrained to agree outside this one candidate carrier, give it the same agreement value and give U opposite values. A solution excludes that carrier from any determining triple. A full named carrier always survives this individual test, because its own value and the complete raw assignment on the other named carrier together determine U.
4. **List the disjoint ways to cover D.** A single carrier has at most three raw distinctions. Thus either two or all three of the candidate bond's carriers contain members of D. In every case the only possible two-carrier cover was X and Y themselves. The accompanying search exhausts all disjoint third carriers, using allowed states to certify present words and exact source constraints for every unresolved word. It also checks each carrier's variation at every source knot. [All fixed-pair cases](other_bonds_paired_all.jsonl.gz)
5. **Decide the remaining triples.** Across the 16,848 upper-function occurrences, 90,385 disjoint triples survived with each of the three carriers containing members of D. For each such triple, two complete stage copies must give identical agreement values on all three carriers while giving U opposite values. If such a pair is impossible, the program tests whether the triple is an eligible stage bond. Zero of the 90,385 are determining eligible bonds. This exhausts every way a three-carrier agreement bond could determine a designated upper reading on these checked chains. [Per-function coverage](other_bonds_determination_counts.jsonl.gz) · [Run counts](other_bonds_determination_counts.json)

## Weighting by starts and rounds

| Round | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Starts with a complete step on a checked chain at that round | 6 | 24 | 75 | 343 | 604 |
| First such round for a start | 6 | 18 | 52 | 267 | 261 |
| Starts with such a round by then | 6 | 24 | 76 | 343 | 604 |

At round four the checked chain selections on five-knot census entry 1603 lose the complete step seen at round three. The table counts just the original prefix of up to three chains per stage. At round six every one of the 604 sampled starts with a chain has a complete step on at least one printed chain. Their share is 604/732 weighting each growing sampled start once, and 604/1,000 weighting each sampled start once. [Counts by round and overlap of tests](other_bonds_summary.json)

## Independent controls and replay

Direct enumeration of every allowed raw assignment and every disjoint nonlocal carrier triple on four small two-holder systems gave 16, 56, 100 and 285 genuine lower bonds. It tested 4,209 possible upper queries with every named raw distinction necessary. For representatives of each observed type in each system, the direct scan and the reduction agreed on the full set of surviving individual carriers and on every determining bond with three carriers containing named distinctions. Two systems have positive examples of that latter case. Two systems admit a determining bond in which just two carriers contain named distinctions and differ from the named pair. These alternatives were therefore detectable by the method. [Direct controls](other_bonds_controls_all.json)

Run from the repository root after constructing `stages.jsonl.gz` and `stage_readings.jsonl.gz`. The direct-witness and fixed-pair commands are in the companion record. The largest whole-stage pilot had 162 raw distinctions. The four timing stages took about one second and the 1,062-stage replay took under three minutes using one process. [Pilot measurements](other_bonds_determination_pilot.json) · [Fixed-pair replay and controls](other_bonds_paired.md)

```sh
ulimit -v 1792000
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ref=research/CHAIN-STEP-20261127-001/referee-R1
.venv/bin/python -B "$ref/other_bonds_controls.py" --pilot
.venv/bin/python -B "$ref/other_bonds_controls.py"
.venv/bin/python -B "$ref/other_bonds_determination.py" --pilot
.venv/bin/python -B "$ref/other_bonds_determination.py"
.venv/bin/python -B "$ref/other_bonds_summary.py" --pilot
.venv/bin/python -B "$ref/other_bonds_summary.py"
```
