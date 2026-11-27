# Which bonds the growth distinguishes

**The original three stay equivalent.** Each of the three source knots spends its one loose distinction in the first birth. Every source distinction then has two holders. Later births use loose distinctions only. Each of the six permutations of the source knots therefore extends by fixing every later distinction and every later knot. These maps exchange the three bonds that need all four laws, so a rule respecting renaming cannot designate one member. The three fixed definitions of the readings give one missing word apiece, and deleting any law gives all eight words in each case.

| Ring round | Bonds | Symmetries of that stage | Bonds fixed by the six source maps | Bonds fixed by all stage symmetries |
| --- | ---: | ---: | ---: | ---: |
| 1 | 9 | 6 | 0 | 0 |
| 2 | 411 | 12 | 0 | 0 |
| 3 | 9,121 | 48 | 16 | 0 |

All 16 fixed by the source maps use only the seven born distinctions. Only 12 of the 48 round-3 maps extend across the recorded round-4 births. Their action has eight orbits of two, one of three, 313 of six and 602 of twelve. The same 12 extend through rounds 5 and 6. A join spends distinctions 9 and 11. They were one of four equivalent pairs at round 3. The join makes a reading available at one knot, removing 6 of 24 bonds in one former orbit, 6 of 24 in another and 2 of 8 in a third. All fourteen missing-word relations persist. A different assignment of the exchangeable loose inputs can change which named pair the join takes. [Orbit and loss counts](sym_orbits.json)

The frozen script's three seeded trials each compared only the last stage, with the start distinctions pinned and the birth rounds unmarked. Its six source-map checks compared supports. In a new replay, all six preserve the supports and the parent, input, fresh-distinction and demand records at every round through round 6. The three shuffled starts each match at every round through 6 with their specified renaming. The earlier independent growth rule reproduced the supports recorded by the first ring witness at rounds 0–4. It also reproduced the funded status and both stage sizes wherever available on all 1,000 held-out starts. An incidence symmetry preserves the defining tests for a bond. Closure of the bonds under these maps checks the implementation. [Growth replay](sym_growth.json) · [Frozen-sample coverage](sym_survey.json)

**The three-valued reading.** The 44 states at round 1 give 16 of 27 triples and nine of nine pairs on every two readings. Dropping each law gives 20, 20, 20 and 19 triples. Giving the grown stage an independent free reference yields the same 19 triples as deleting the birth law. The three gained triples are 001, 010 and 100, where 0 means apart and 1 means agreement with the reference. Removing every law gives 27 triples. Reading just agreement of the opposite pairs gives all eight binary triples. The three ternary readings share the reference, so their supports overlap.

Within the specified reading scheme, the stage determines both the reference and the unordered pairing. Distinction 6 is the only loose distinction. Over seven possible references and fifteen perfect pairings of the six remaining distinctions, exactly one of 105 proposals has a proper, nonempty image with all three pair projections full. It is the unique pairing and reference fixed by all six symmetries. The choice to use this scheme remains. [Ternary enumeration and controls](sym_ternary.json)

**Selection away from the ring.** The held-out sample has 1,000 starts. Exactly one has no nonidentity permutation of its knots and distinctions, and it stalls. Across the full census only five of 7,075 have that property, and one grows. This five-knot start lies outside the held-out sample. Its single birth takes four old inputs. The birth makes six of 281 old bonds readable at a knot, preserving the images of all 281 and leaving 275 as bonds. Of 362 bonds on the grown stage, 25 need all six laws. [All five starts](sym_all_rigid.json) · [Grown-stage controls](sym_controls.json)

Of 683 held-out starts on which every symmetry fixes every knot, 500 grow. Their symmetries may still exchange distinctions held by the same knots. The full search found old bonds on 341 of these starts. The next birth round removes 18 of 24,684 bonds on four starts and retains 24,666. Two starts have losses and retentions within a single source orbit. The other two distinguish entire source orbits. No start in this set loses exactly one bond. An old reading becomes a function of a birth precisely when it is a function of the birth's old inputs. For fixed input values, each admissible old state allows the same nonempty set of fresh completions there, and the other births have separate fresh distinctions. Directly testing all four grown stages retains the images of all 1,203 source bonds and confirms the four loss counts of 8, 2, 2 and 6. The outcome distinguishes subsets while leaving the original ring result intact. [Per-start counts](sym_selected.json) · [Grown-stage controls](sym_controls.json)

## Exact wording changes

- **Not a block.** In the first answer in [the decision](../decision.md), replace “Relabelled starts grow isomorphic stages through round 5 (P1.3, held).” with “The three frozen trials matched the final, round-5 stage with its start distinctions pinned. A replay matched supports at every round from 0 through 6 and matched parents, inputs and fresh distinctions at every birth.”
- **Narrowing.** Replace “So every bond read here is one of several equivalent choices.” with “At rounds 1–3 each bond has equivalent choices under that stage's symmetries. The following round can distinguish some of these choices. The round-4 join removes 14 bonds from three earlier orbits and retains others in each orbit. The original three remain exchanged at every funded round.”
- **Not a block.** Replace “the reference distinction (here 6) is still a choice” with “the three-valued reading scheme is supplied. Within it, the first grown stage determines the reference, its only loose distinction, and the pairing.” The same qualification applies to “a three-valued relation needs no choice” in the goals checkpoint for the grown ring.

## Replay

The calculations reuse the [earlier independent ordinary growth](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py) and the [independent exact bond enumeration](ring_recount.py) in this review. Each command runs one process. The first command in each loop times the same method on a subset.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
r=research/RING-BOND-20261127-001/referee-R1
for part in growth ternary orbits; do
  .venv/bin/python -B "$r/sym_ring.py" --part "$part" --pilot --out "$r/sym_${part}_pilot.json"
  if [ "$part" = orbits ]; then
    .venv/bin/python -B "$r/sym_ring.py" --part orbit-cost --out "$r/sym_orbit_cost.json"
  fi
  .venv/bin/python -B "$r/sym_ring.py" --part "$part" --out "$r/sym_${part}.json"
done
for part in survey universe selection controls; do
  case "$part" in
    universe) output=all_rigid ;;
    selection) output=selected ;;
    *) output=$part ;;
  esac
  .venv/bin/python -B "$r/sym_selection.py" --part "$part" --pilot
  .venv/bin/python -B "$r/sym_selection.py" --part "$part" --out "$r/sym_${output}.json"
done
```

The ternary pilot checked 15 pairings in 0.003 seconds. One relabelling took 0.002 seconds with the source-map checks. The round-3 size check scanned 24 first readings and tested six history extensions in 0.16 seconds including setup, giving an estimate under ten seconds for the orbit run. It took 0.63 seconds. The sample survey took 0.03 seconds for 40 starts. The full-census pilot took 0.09 seconds for 284. Their estimates were under one and three seconds. Four complete selection cases took 0.18 seconds, giving an estimate of 23 seconds for 500. The run took 15.31 seconds. Controls on two bonds at each of five starts and a prefix of new bonds took 0.28 seconds. The complete controls took 0.96 seconds, within a one-minute estimate.

The old-bond selection calculation on the 230 funded sampled starts with nontrivial knot permutations, full-stage bond orbits at rounds 4 and later, and later-history extension beyond round 6 were not run. The 105 proposals cover the specified perfect-pairing scheme. Other three-valued reading schemes were not enumerated.
