# A lower bond containing the two carriers of an upper reading

On **316 of the 2,808 checked chains**, the two agreements of an upper reading belong to a lower bond together. That bond determines both “either” and “both” for this pair. The 316 chains occur on 193 stages of 138 sampled starts. Of the 2,803 chains passing the frozen step criteria, 314 have such a bond. Of the 2,800 also needing all eight chain laws, 311 have one. This leaves **2,489** after the fixed-pair test. The search over triples that omit either fixed carrier is recorded separately. [Counts by stage and round](other_bonds_paired_all.json)

| Weighting | Count |
| --- | ---: |
| Choice of checked chain, upper pair and disjoint third carrier of two or three distinctions | 373,457,816 |
| Such choices in which a single source knot visibly contains the third carrier | 1,467,964 |
| Qualifying lower bonds, counted once per choice of checked chain, upper pair and third carrier | 1,459 |
| Qualifying bonds where the third carrier is among the chain's four other named carriers | 201 |
| Qualifying bonds where the third carrier is another agreement | 1,258 |

Each of the 1,459 bonds has exactly the seven words other than 111. Every one of its three agreements can change at fixed raw values of each individual source knot. The separate six-agreement projection recovered all 201 with a named third carrier. Counting each distinct fixed pair once in its stage gives 8,422 pairs and 1,457 qualifying triples. [Per-stage results](other_bonds_paired_all.jsonl.gz) · [Six-agreement cross-check](other_bonds_paired_witness.json)

## Why every eligible third carrier is covered

For each checked chain the search takes each of its three designated pairs of agreements, X and Y. It enumerates every pair and triple of raw distinctions disjoint from their carriers as Z. If a source knot contains Z, its raw values determine that agreement. For other Z the test needs the exact set of possible values of (X,Y,Z).

The initial test uses 2,048 allowed source states. Starting from one allowed assignment, a raw distinction can be redrawn freely wherever every law holding it already has two different values among its other members. Otherwise the distinction takes the value required by those laws. The code validates all 2,048 resulting states against every law. For each of the four values of (X,Y), up to 64 states first give a fast check on every Z. Any word still missing is checked against all 2,048 states. The remaining queries use the full source constraints, so coverage is independent of the choice of sampled witnesses.

For a proposed word with Z agreeing, global complementation allows all its raw distinctions to be fixed at zero. For a proposed word with Z disagreeing, fix its first raw distinction at zero and test a 1 at each other member in turn. Each agreement requirement on X and Y is invariant under that complement. The resulting truth table decides whether all pair projections are free and at least one triple word is absent.

For each surviving carrier and source knot, a final two-state test requires identical raw values on the knot, agreement on the carrier in the first state, and disagreement in the second. All knots must admit such a pair of allowed states for each of X, Y and Z. The bare eight-knot chain supplied four full truth-table controls. Each of its three upper pairs has zero eligible third carriers, while two members of a defining lower clause recover its unique third agreement and missing 111. [Implementation](other_bonds_paired.py) · [Controls and pilot](other_bonds_paired_pilot.json)

## An extra source law explains one witness

The second checked chain in the second grown round of four-knot census entry 87 has X on (1,3,7), Y on (6,11,16) and a qualifying Z on (2,4,5). The 12 source laws allow 70,038 of the 2,097,152 raw assignments. Each of the three agreements changes at fixed values of each of the 12 knots. The data records all 36 pairs of assignments.

| Lower word XYZ | Allowed raw assignments | Both X and Y | Either X or Y |
| --- | ---: | ---: | ---: |
| 000 | 50,022 | 0 | 0 |
| 001 | 6,552 | 0 | 0 |
| 010 | 5,634 | 0 | 1 |
| 011 | 414 | 0 | 1 |
| 100 | 6,282 | 0 | 1 |
| 101 | 450 | 0 | 1 |
| 110 | 684 | 1 | 1 |
| 111 | 0 | — | — |

Suppose X, Y and Z each agree internally, with common raw values a, b and c respectively. The laws on (0,1,3) and (0,2,4) force distinction 0 opposite to both a and c, so a=c. The laws on (4,5,10) and (10,11,16) force distinction 10 opposite to both c and b, so b=c. The source law on (1,5,6) would then have all three values equal. This fifth law is outside the chain. Checking all 4,096 subsets of source laws finds exactly this one inclusion-minimal set excluding 111.

Direct enumeration also recovers all five qualifying third carriers for this fixed pair among its 560 possible choices. The others are (0,4,10), (0,4,12), (4,9,10) and (4,9,12). The canonical checker accepts their shared seven-word relation under forgetting. [Raw truth table, matching state pairs and law deletions](other_bonds_paired_witness.json) · [Independent enumeration](other_bonds_paired_witness.py)

## Replay

The paired search reads the reconstructed stages archive. The direct witness compares its result with the full fixed-pair search and the separately reconstructed projections of the six named carriers. Run from the repository root after creating those inputs.

```sh
ulimit -v 1835008
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ref=research/CHAIN-STEP-20261127-001/referee-R1
.venv/bin/python -B "$ref/other_bonds_paired.py" --pilot
.venv/bin/python -B "$ref/other_bonds_paired.py"
.venv/bin/python -B "$ref/other_bonds_paired_witness.py" --pilot
.venv/bin/python -B "$ref/other_bonds_paired_witness.py"
PYTHONPATH=tools .venv/bin/python -B -m knotlab check --cnf '~X ~Y ~Z' --loops X Y --contact Z --json
```

The fixed-pair pilot examined nine chains on three stages, including the largest stage of 162 distinctions, in 0.36 seconds. The full run took 17.00 seconds and peaked at 66,340 KiB. The direct witness pilot examined the first eighth of the raw assignments and 24 third carriers. The complete direct check took 0.28 seconds. [Witness pilot](other_bonds_paired_witness_pilot.json)
