# Distributions by stage size and age

A reached stage is one observation. Counts show the least orders zero, two and three. The two size units are ordinary junctions \(J\) and literal distinctions \(n\). All 767 observations have an exact order. Each drawing law contributes 384 initial draws distributed equally over the six initial sizes. [Exact stage assignments](../../artifacts/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/distribution.json)

## Distributions by weighting

The intervals are percentile intervals from 4,000 resamples. Each resample draws 64 independent starting histories with replacement in each original size stratum and keeps all observed ages from each selected history, including zero qualifying observations from a stalled start. For size-band intervals the same resampled starts are used, retaining only observations in that band. Replicates with an empty band are omitted. The final column of each band table gives the number of defined resamples. An interval of 0–0 occurs when the empirical start clusters contain no exception in the band. It gives no population upper bound. [Resampling calculation](../../experiments/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/distribution.py)

| Weighting | Order 0, count and 95% share (%) | Order 2, count and 95% share (%) | Order 3, count and 95% share (%) |
|---|---:|---:|---:|
| Uniform tree | 14 (3.2–8.8) | 227 (91.2–96.8) | 0 (0.0–0.0) |
| Tree + links | 0 (0.0–0.0) | 201 (80.5–94.7) | 27 (5.3–19.5) |
| Recursive tree | 17 (3.4–8.6) | 281 (91.4–96.6) | 0 (0.0–0.0) |

## Ordinary junctions

| Current size | Weighting | Reached stages | Order 0 | Order 2 | Order 3 | Order 3 share, % (95% interval) | Defined resamples |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1–9 | Uniform tree | 78 | 14 | 64 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 1–9 | Tree + links | 32 | 0 | 32 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 1–9 | Recursive tree | 81 | 17 | 64 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 10–19 | Uniform tree | 115 | 0 | 115 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 10–19 | Tree + links | 101 | 0 | 84 | 17 | 16.8 (7.4–27.4) | 4,000 |
| 10–19 | Recursive tree | 117 | 0 | 117 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 20–39 | Uniform tree | 34 | 0 | 34 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 20–39 | Tree + links | 74 | 0 | 64 | 10 | 13.5 (5.9–23.0) | 4,000 |
| 20–39 | Recursive tree | 61 | 0 | 61 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 40–79 | Uniform tree | 12 | 0 | 12 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 40–79 | Tree + links | 19 | 0 | 19 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 40–79 | Recursive tree | 35 | 0 | 35 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 80–150 | Uniform tree | 2 | 0 | 2 | 0 | 0.0 (0.0–0.0) | 3,504 |
| 80–150 | Tree + links | 2 | 0 | 2 | 0 | 0.0 (0.0–0.0) | 3,507 |
| 80–150 | Recursive tree | 4 | 0 | 4 | 0 | 0.0 (0.0–0.0) | 3,941 |

## Literal distinctions

| Current size | Weighting | Reached stages | Order 0 | Order 2 | Order 3 | Order 3 share, % (95% interval) | Defined resamples |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1–19 | Uniform tree | 78 | 14 | 64 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 1–19 | Tree + links | 53 | 0 | 47 | 6 | 11.3 (3.6–21.7) | 4,000 |
| 1–19 | Recursive tree | 81 | 17 | 64 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 20–39 | Uniform tree | 117 | 0 | 117 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 20–39 | Tree + links | 94 | 0 | 83 | 11 | 11.7 (5.0–20.0) | 4,000 |
| 20–39 | Recursive tree | 119 | 0 | 119 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 40–79 | Uniform tree | 32 | 0 | 32 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 40–79 | Tree + links | 62 | 0 | 52 | 10 | 16.1 (7.0–27.1) | 4,000 |
| 40–79 | Recursive tree | 63 | 0 | 63 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 80–149 | Uniform tree | 12 | 0 | 12 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 80–149 | Tree + links | 17 | 0 | 17 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 80–149 | Recursive tree | 31 | 0 | 31 | 0 | 0.0 (0.0–0.0) | 4,000 |
| 150–240 | Uniform tree | 2 | 0 | 2 | 0 | 0.0 (0.0–0.0) | 3,504 |
| 150–240 | Tree + links | 2 | 0 | 2 | 0 | 0.0 (0.0–0.0) | 3,507 |
| 150–240 | Recursive tree | 4 | 0 | 4 | 0 | 0.0 (0.0–0.0) | 3,941 |

## Joint observed sizes

Each entry counts stage observations. Across the three weightings there are 142 distinct exact pairs of current sizes. The table uses the same bands used above. The underlying shape index retains both exact sizes and every observation key. [Joint exact sizes](../../artifacts/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/sample_shape_index.json)

| Junctions | Distinctions | Uniform tree | Tree + links | Recursive tree |
|---:|---:|---:|---:|---:|
| 1–9 | 1–19 | 78 | 32 | 81 |
| 10–19 | 1–19 | 0 | 21 | 0 |
| 10–19 | 20–39 | 115 | 80 | 117 |
| 20–39 | 20–39 | 2 | 14 | 2 |
| 20–39 | 40–79 | 32 | 60 | 59 |
| 40–79 | 40–79 | 0 | 2 | 4 |
| 40–79 | 80–149 | 12 | 17 | 31 |
| 80–150 | 150–240 | 2 | 2 | 4 |

## Age and realized sizes

Each size cell is minimum / median / maximum. Order counts include closed observations.

| Weighting | Age | Stages | Junctions | Distinctions | Orders 0 / 2 / 3 |
|---|---:|---:|---:|---:|---:|
| Uniform tree | 1 | 85 | 7 / 8 / 38 | 12 / 15 / 76 | 0 / 85 / 0 |
| Uniform tree | 2 | 85 | 8 / 12 / 62 | 12 / 21 / 123 | 14 / 71 / 0 |
| Uniform tree | 3 | 71 | 16 / 16 / 93 | 27 / 27 / 184 | 0 / 71 / 0 |
| Tree + links | 1 | 76 | 6 / 10 / 51 | 10 / 19 / 97 | 0 / 67 / 9 |
| Tree + links | 2 | 76 | 8 / 17 / 74 | 14 / 33 / 139 | 0 / 67 / 9 |
| Tree + links | 3 | 76 | 12 / 27 / 103 | 22 / 51 / 193 | 0 / 67 / 9 |
| Recursive tree | 1 | 105 | 7 / 8 / 39 | 12 / 15 / 79 | 0 / 105 / 0 |
| Recursive tree | 2 | 105 | 8 / 12 / 62 | 12 / 21 / 123 | 17 / 88 / 0 |
| Recursive tree | 3 | 88 | 16 / 16 / 91 | 27 / 27 / 180 | 0 / 88 / 0 |

## First-age structural coverage

Each cell gives the count in the broad joined-leaves class followed in parentheses by its degree-two-free subclass. Denominators are all 64 initial draws per cell or, for a conditional rate, the first-age counts in the decision. The tree-plus-links column is zero because its starts already contain ordinary cycles. Counts are a direct application of the two structural predicates to the original support lists of all first-age observations. Every counted observation has exact order two. [Source predicates](structural_features.py) · [Literal starting histories](../../artifacts/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/sample_stages.jsonl.gz)

| Initial junctions | Uniform tree | Tree + links | Recursive tree |
|---:|---:|---:|---:|
| 4 | 14 (14) | 0 | 17 (17) |
| 6 | 5 (5) | 0 | 5 (5) |
| 8 | 1 (1) | 0 | 4 (4) |
| 12 | 1 (0) | 0 | 3 (2) |
| 20 | 0 | 0 | 0 |
| 32 | 0 | 0 | 0 |
| All first-age reached | 21 / 85 (20 / 85) | 0 / 76 | 29 / 105 (28 / 105) |

## Supplementary count of harmful equal-singleton exchanges

For every continuing shape, use its exact singleton minima, physical holder pairs and the binary remainder of each unit vector modulo the junction-row span \(C\). Among the movable literal names count unordered pairs \(x,y\) whose singleton minima agree, whose holders differ, and whose unit remainders differ. The transposition formula proves that these are precisely the singleton-preserving exchanges changing \(C\). For two equal minima, equal unit remainders would instead imply \({\bf e}_x+{\bf e}_y\in C\). Join the count back to every weighted observation by its shape key and apply the overall and initial-size-and-age matched AUC formulas in the distribution calculation. This supplementary extraction leaves the original distribution artifact unchanged. [Remainder and flow routines](../../experiments/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/scale_reader.py) · [AUC calculation](../../experiments/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/distribution.py)

| Continuing stages | Range of harmful counts at order 2 | Range at order 3 | Overall AUC | Matched AUC |
|---|---:|---:|---:|---:|
| Uniform tree | 3–2,430 | No cases | Undefined | Undefined |
| Tree + links | 6–4,110 | 10–326 | .383 | .296 |
| Recursive tree | 3–2,566 | No cases | Undefined | Undefined |

The presence of at least one harmful exchange certifies that singleton readings fail. The number of such exchanges by itself neither defines a pair isometry nor settles order three.
