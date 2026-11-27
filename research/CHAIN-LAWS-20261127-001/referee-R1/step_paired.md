# Stage bonds containing an upper pair

For each chain the search takes the three named pairs of agreement carriers in A, B, C order. With the two carriers of a pair fixed, the remaining choices are all pairs and triples of raw distinctions disjoint from both. When a third carrier completes a lower bond, that bond determines both the conjunction and the disjunction of the fixed pair. Every choice of which upper pair reads “both” therefore loses the test against a single lower bond on that chain.

## Census

The two rival laws share 1,325 stages with checked chains. Across all 26,373 chains on those stages, 6,588 chains on 1,164 stages have a determining lower bond containing an upper pair.

| Upper pair | Third-carrier choices | Third carrier contained in one source knot | Determining bonds | Bonds with a third named carrier |
| --- | ---: | ---: | ---: | ---: |
| A | 75,399,995 | 2,061,014 | 30,865 | 4,538 |
| B | 75,399,995 | 1,893,738 | 0 | 0 |
| C | 84,027,847 | 2,163,214 | 0 | 0 |
| Total | 234,827,837 | 6,117,966 | 30,865 | 4,538 |

Each bond has the seven words 000 through 110. A separate read aligned all 26,373 rows with the original chain order, reproduced all 228 pilot rows and all 622 wide-pilot rows, and checked the raw witness states in the full summary. [Per-chain counts](step_paired_rows.jsonl.gz) · [Summary and source-law variation witnesses](step_paired.json)

## Exact test

A carrier contained in a source knot is already read at that knot. The remaining triples pass only if their whole-stage relation is nonempty and proper, all three pairs have four words, and each agreement varies at fixed raw values of every individual source knot.

The search starts with 512 validated allowed raw states per stage. For each word of the two fixed agreements, up to 64 matching states certify present words of the triple. For each word still undecided, the solver uses the whole stage's not-all-equal laws. All three agreement readings are invariant under complementing every raw value. To test whether the third carrier can agree, the solver fixes all its distinctions to zero. To test disagreement, it fixes the first distinction to zero and asks whether any other member can be one. A separate test uses two full copies of the stage to require the same raw values on one source knot and different agreement values on the carrier. This is repeated for each source knot and each carrier of a surviving triple. The choice of allowed sample states affects running time.

## Direct witness

In round four of the three-knot census entry 2, the third chain has fixed carriers X on `(3,4,8)` and Y on `(11,13,15)`. The third carrier Z on `(0,9,12)` completes a lower bond. Of the 13,110 allowed raw states, the eight words in order 000 through 111 have counts `8586, 1968, 942, 186, 1206, 90, 132, 0`. The direct truth table finds five qualifying third carriers for this fixed pair. Applied to all three named pairs of the bare eight-law chain, it finds zero determining bonds on 13,122 allowed raw states. [Direct controls](step_paired_controls.json)

When X, Y and Z agree internally, write their respective common values as x, y and z. The knots on `(0,3,4)` and `(12,13,15)` force x and y both opposite z. The knot on `(8,10,11)` then forces distinction 10 to take z, while the knot on `(9,10,12)` forces it opposite z. Deleting each of those four laws individually restores 111, with 42, 18, 18 and 18 raw states in source order. They form the unique minimal set excluding that word. The knot on `(8,10,11)` is outside this chain. The canonical forgetting test confirms the seven-word relation is a knot.

## Replay

Run from the repository root. The 13-stage pilot took about one second. The eight widest stages took 27 seconds, testing 23.6 million choices and peaking below 58 MiB. Projecting the wider pilot's rate to the entire census gave 4.5 minutes. The full search took 203 seconds and peaked below 64 MiB. The controls used direct raw-state enumeration to check the complete third-carrier results for the tested pairs.

The separate bare-chain control pilot took 0.092 seconds and peaked at 34.2 MiB. Both direct controls then ran in 0.248 seconds and peaked below 35 MiB. [Direct-control pilot](step_paired_controls_pilot.json)

```sh
ulimit -v 1572864
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
ref=research/CHAIN-LAWS-20261127-001/referee-R1
.venv/bin/python -B "$ref/step_paired.py" --pilot
.venv/bin/python -B "$ref/step_paired.py" --widest 8
.venv/bin/python -B "$ref/step_paired.py" --controls --pilot
.venv/bin/python -B "$ref/step_paired.py" --controls
.venv/bin/python -B "$ref/step_paired.py"
PYTHONPATH=tools .venv/bin/python -B -m knotlab check --cnf '~X ~Y ~Z' --loops X Y --contact Z --json
```
