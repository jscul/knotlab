# Exact replay of the two sampled witnesses

The five-knot census start at entry 5260 grows to seven knots and 14 distinctions in round one, then to nine knots and 17 distinctions in round two. The first round joins the seven-place knot to the only other knot holding a loose distinction. The seven-place knot has one loose distinction left for an offshoot. The join and offshoot are the two parents of the second round's join, and the offshoot has a loose distinction left for another offshoot. The round-two stage allows **12,912** states.

The independently checked agreements are `A0=(2,8,10)`, `A1=(7,13)`, `B0=(0,1,5)`, `B1=(9,12,14)`, `C0=(3,4,11)` and `C1=(6,15,16)`. A reading is 1 when all the distinctions of its carrier agree. Each carrier member can change its reading in one allowed change. For each of the six readings and each individual knot, some fixing of that knot leaves both reading values possible. The four named lower triples each miss exactly `111`. Their conjunction allows 41 six-reading words. The source allows 39 of those words. There is exactly one pairing with the required four consistently signed triples among the 15 pairings of these six carriers and their two choices of alternating triples.

Each choice of **both** gives the seven upper words `000` through `110`. Each upper pair is free. At each of the four lower bonds, three feasible fixes leave both values possible for the **both** reading and four do so for each **either** reading. None of the other triples of these six readings that determines an upper reading is a bond. The canonical checker forgets the six lower readings and confirms K1–K3 for each designation of the third reading.

Each row counts assignments that restore upper `111` after a single law deletion. The six readings and the remaining round-two laws stay fixed throughout.

| Pair read as both | Start laws 0–4 | Round-one laws 5–6 | Round-two laws 7–8 |
| --- | --- | --- | --- |
| A | 0, 40, 40, 46, 54 | 30, 40 | 40, 46 |
| B | 0, 28, 30, 10, 30 | 10, 28 | 24, 26 |
| C | 0, 34, 40, 18, 40 | 14, 40 | 38, 34 |

The four birth laws and four of the five start laws are necessary and jointly sufficient for the upper exclusion in all three roles. The seven-place law admits 210 further source assignments when deleted and preserves the upper exclusion. All three upper relations also follow from the abstract four-clause conjunction on the six readings. There, each single lower-clause deletion restores one lower word that gives upper `111`.

The final carriers use three distinctions absent in round one, so the literal readings require round two. The final state set projects onto exactly the 2,868 round-one states and the 638 starting states. If one keeps the round-one laws and supplies the later distinctions as free variables for the fixed final readings, all eight upper words occur. There are 98, 72 and 116 assignments with `111` for **both** on A, B and C. This checks the effect of adding the last two laws to the fixed roster. Choosing the readings from the growth rule remains open.

For the four-knot census start at entry 420, the reconstructed support list matches the archived witness. The 17,928 allowed states realize the same 39 six-reading words as its archive. Each of the three roles passes the same tests. All six birth laws are individually essential in all three roles. The archive's role has 20, 0, 42 and 0 restoring assignments on deletion of the four start laws. Its six birth deletions give 10, 36, 36, 36, 36 and 36. [Earlier witness](../../UPPER-GROWN-20261127-001/referee-R1/upper_sample.json)

The replay uses the earlier independent growth rule and new exact finite-state code. The latter cross-checks the first 512 assignments' rule violations using direct bit readings. Its determination checks use the named lower bonds, all triples of the six carriers, and individual source knots. [Growth rule](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py) · [Exact counts](witness_checks.json)

Run from the repository root. The one-role pilot took 0.21 seconds and the full two-witness run took 0.85 seconds. Peak resident memory was below 33 MiB in both runs.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
referee_dir=research/FOUR-CLAUSE-20261127-001/referee-R1
.venv/bin/python -B "$referee_dir/witness_checks.py" --pilot
.venv/bin/python -B "$referee_dir/witness_checks.py" --out "$referee_dir/witness_checks.json"
```
