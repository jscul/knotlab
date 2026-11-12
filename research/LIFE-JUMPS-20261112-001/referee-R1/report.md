# Referee report LIFE-JUMPS-R1: jumps over a whole life

**Verdict: Confirmed with fixes.**
- **Every number reproduces.** My own summary code recomputes J1 to J6 from the records, and every figure matches `summary.json`. I
  regenerated 414 growths from the seeds with my own generators, and each matches its record in knots, ending, distinctions and ending
  knot. No deviation changes a verdict.
- **Fix: J6 is forced.** "The class is old" is mostly a consequence of age. Drawing the class's size at random from the distinctions,
  weighted by how many knots each is in, meets J6's criterion in every ending of all four processes. Only in X(0.3), and partly
  X(0.35), is the class older than that.
- **Fix: J4 is narrower than its wording.** Its signal is real, but partly a count: knots per distinction already reach AUC 0.71 to
  0.74. It is weakest for the far ends "long before" suggests: 0.67 at 300 knots for growths that end after 3,000. Censoring at 6,000
  does not inflate it.
- **Rediscovery.** J1 and J3 are the known discontinuous backbone at the 2-colouring threshold. J5 and J6 are the known behaviour of
  giant components in grown random networks.

Referee: the background referee thread, 2026-11-12. The code:
- `ref_records.py` recomputes J1 to J6 and J4's baselines from the records. It does not import `census.py` or `summary_fixed.py`.
- `ref_regen.py` regenerates the growths with RANDOM-FATES-R1's generators (`ref_fates.py`, drawing in the frozen order) and
  Glucose 4, from LIFE-JUMPS's seeds.

Validation: V2 for the regeneration and the null. The summary is a recount of the census's readings: the tie classes at each reading
were not recomputed. The advisor model was not consulted for this job.

## 1. What reproduces

| # | Census | Referee |
| --- | --- | --- |
| J1 | 95 to 100% (share ≤ 0.05 at 40 before), 93 to 95% (≥ 0.5 at the last base) | the same, setting by setting |
| J1b | 0.28 (U100), 0.20 (U300) | the same; 0.234 at U300 with its 30th growth |
| J2 | 61 to 75% | 61.3%, 74.6%, 67.1%, 69.0% |
| J3 | ratios 1.00 in the four processes against 0.015 to 0.034 for U | the same |
| J4 | AUC 0.82 and 0.84 (hazard 0.77 and 0.85) | the same |
| J5 | 96% of 78 | the same; the maximum is 51 |
| J6 | 100% in all four | the same |

**The regeneration.** 414 growths were regenerated: every ending of the four growth processes, and 40 uniform growths. All 414
match their records in knots, whether they ended, distinctions at the end and the ending knot. So the records are what the seeds give.

**The deviations (iii) change nothing.**
- **The side units.** All 500 records of `runs_xo.jsonl` and all 160 of `runs_u.jsonl` are identical to the merged records, the
  seconds aside.
- **The 30th U300 growth** (run 16) finished after the merge, and is in `runs_u300.jsonl`. With it, J1 at U300 reads 96.7% and
  93.3%, and J1b's median rises to 0.234, so the verdicts are unchanged.
- **`summary_fixed.py`** only changes how booleans are written; my independent summary gives the same verdicts.

## 2. (i) What is forced

**J6 is forced by age through degree.** In these processes old distinctions sit in more knots, and a distinction in more knots is
more likely to be tied.
- **The null.** At each ending's last base I drew the largest class's size from the distinctions, with probability proportional to
  each one's number of knots, 400 times.
- **The null passes J6 everywhere.** In all four processes its median arrival index is below (n − 1) / 2 in 100% of draws, for the
  median ending. So J6's criterion is met by degree alone.
- **Is the class older than degree predicts?**

  | Process | Endings | Class's median index / n (record) | Null's | Record below the null's 5th percentile |
  | --- | --- | --- | --- | --- |
  | X(0.3) | 87 | 0.22 | 0.30 | 86% |
  | X(0.35) | 100 | 0.28 | 0.33 | 60% |
  | O global (0.3) | 88 | 0.24 | 0.25 | 8% |
  | O local (0.3) | 99 | 0.24 | 0.25 | 7% |

  In the overlap processes the class's age is what its members' knots predict. In the expanding processes it is older still.

**J4 is not inflated by censoring, but it is narrower than "long before".**
- **Censoring.** It can only blur the contrast. The 13 negatives are growths still bases at 6,000, and any of them that would end
  later count as negatives, which pulls the AUC down. Conditioning on being a base after m knots is the right survivorship.
- **Baselines** (`ref_records.py`): AUC, and censored concordance (Harrell's C on time to the end).

  | Predictor | AUC after 300 | AUC after 1,000 | Concordance after 300 | Concordance after 1,000 |
  | --- | --- | --- | --- | --- |
  | the share | 0.82 | 0.84 | 0.75 | 0.77 |
  | the closing hazard | 0.77 | 0.85 | 0.73 | 0.77 |
  | the largest class's size | 0.81 | 0.83 | 0.75 | 0.76 |
  | knots per distinction (no ties used) | 0.74 | 0.71 | 0.70 | 0.66 |

- **What the ties add.** A plain count of closings gets most of the way. The ties add about 0.08 to 0.13 of AUC, and within terciles
  of knots per distinction the share still separates (AUC 0.74 to 0.97, on small groups).
- **Far ends.** The signal is weak for distant ends. For the 21 growths that end after 3,000 knots, the share separates them from the
  survivors with AUC 0.67 at 300 knots and 0.74 at 1,000, against 0.82 and 0.84 overall.

So "the law signals the end long before" holds for ends within a few times the reading's age, and weakly beyond.

**The rest.**
- **J3 is not forced by the never-shrinking class.** The size cannot fall, but it could still jump at the end, as in uniform knots.
  The ratio of about 1.00 is a real contrast.
- **J2 and J1 are descriptive and conditioned on the end.** J2 reads each growth at half its own life. J1 reads backwards from the
  end. Both are stated as such, and survivors are reported beside J2, which fits.
- **J5's "share falls toward 0"** is partly arithmetic. The size is at most 51 while distinctions grow by about 0.8 per knot.

## 3. (iv) Known mathematics, and what is rediscovery

**J1, J1b and J3 (uniform knots).** The end comes at a median of 2.105 knots per distinction at n = 300, the known 2-colouring
(NAE-3-SAT) threshold of random 3-uniform hypergraphs, about 2.105 (Achlioptas and Moore; Dall'Asta, Ramezanpour and Zecchina). Just
before it, a backbone of pairs forced equal or unequal appears discontinuously (Monasson, Zecchina, Kirkpatrick, Selman and Troyansky
1999; for 2-colouring and frozen variables, Achlioptas and Ricci-Tersenghi; Semerjian). The jump within the last twenty knots is the
finite-size version of that discontinuity, read along one trajectory. **Rediscovery**, with a new reading: along one growth, and
counted in knots before the end.

**The XOR-type analogue** is the core of random XORSAT, which also appears discontinuously (Dubois and Mandler; Mézard,
Ricci-Tersenghi and Zecchina). It is the closest exact model for a tie class that jumps.

**J2, J5 and J6 (growth that adds distinctions).** Grown random networks with occasional closing edges are known to have these
features (Callaway, Hopcroft, Kleinberg, Newman and Strogatz, 2001; Dorogovtsev, Mendes and Samukhin):
- a giant component that appears only above a closing-rate threshold, with an infinite-order transition;
- old vertices with more edges, which sit in the giant component.

So "with rare closings no large class" (J5) and "the class is old" (J6) are rediscovery in kind, for tie classes instead of
components. The mechanism for J6 is degree, as section 2 shows.

**J4.** Early warning of an approaching transition from a rising order parameter is a generic idea; the critical-transition
literature of Scheffer and co-authors is one source. The specific predictive comparison for tie classes, and its baselines, is new
data.

**What is new.** The single-trajectory measurements, J3's contrast, J4's forecast and its size, and J6's excess age in the expanding
processes beyond degree.

## 4. Fixes for the thread

1. **J6.** Say that a degree-weighted random set of the class's size meets J6's criterion in every ending. The class is older than
   degree predicts in X(0.3) (86% of endings) and partly X(0.35) (60%), not in the overlap processes (7 to 8%). "The tie class sits in
   the oldest distinctions" is mostly "in the most knotted ones". **Narrowing** (Settled by definition: a criterion that degree alone
   meets).
2. **J4.**
   - Add the baselines: knots per distinction reaches 0.71 to 0.74, and the ties add about 0.1.
   - Add the far-end AUC: 0.67 and 0.74 for growths that end after 3,000 knots.
   - "Long before" should read "within a few times the reading's age; weakly beyond".
   - Censoring does not inflate the AUC.

   **Narrowing** (Overreading: an AUC dominated by nearer ends).
3. **Literature.** Name the 2-colouring threshold (about 2.105 knots per distinction, matched here) and the discontinuous backbone for
   J1 and J3. Name grown random networks (Callaway and co-authors) for J5 and J6. Classify these as rediscovery in kind. **Not a block.**
4. **U300's 30th growth.** Fold in run 16: J1 96.7% and 93.3%, J1b 0.234, with the same verdicts. **Not a block.**

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_records.py` | `result_records.json` | J1 to J6, J4's baselines, censored concordance, the deviations |
| `ref_regen.py` | `result_regen.jsonl`, `result_regen_summary.json` | the regeneration and J6's null |
