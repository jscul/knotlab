# Referee report MEET-DIST-R1 (fresh code, no Codex)

**Verdict: the numbers are confirmed. One Block, on the reading "the rest is lost, not hidden".**
- **What holds.**
  - Every share recomputes to four digits in the referee's own code, for five to k = 4 and six to k = 3:
    - the grown table's share, the bag-of-knots null and the multiset ablation;
    - in law, the separation of bare bracketings from k = 1;
    - the mirror ties.
  - The study's code is right: the information share, the prior's mirror weights, the null's fill points, the multiset key, and the
    table canonical form against the state canonical form.
- **What changes.**
  - **"The rest is lost, not hidden … the growth does not keep it" is false.** The same grown base, read with its distinctions'
    names (which are the line's, and in what order the new ones came), carries **all** of the information about the bare bracketing
    at five from k = 2. At six it carries 0.83 at k = 2 and 0.91 at k = 3, still rising. The share the study measures is what is
    left when the names are dropped. The missing part sits in the names, mostly in the order of growth. **Block, on this reading.**
  - **"A distance only in part" needs its scope:** one grown table, read without names, under one prior. In law the tables carry all
    of it from k = 1, as the study says. **Narrowing.**
  - **"Then growth blurs it" is the unnamed reading.** Named, the share rises and does not fall. And for eight and nine even the
    unnamed share was still rising at the last k computed. **Narrowing.**
  - **"About two thirds" and "peaks below two thirds" depend on the prior.** Under a prior uniform over bare bracketings the peaks
    are 0.70 (five) and 0.69 (six). **Not a block.**
  - **"No distance holds the nesting before growth"** is the statement that all presentations of a line have the line's states. It
    is true, and not new. **Not a block.**

## What holds

- **The code (the owner's points 1 to 3).**
  - **`identification` and `mutual_information_fraction` (merge.py).**
    - The prior is uniform over labelled presentations: a mirror pair weighs 2 and a self-mirror presentation 1.
    - Masses are exact, and only the logarithms are floats.
    - I / H is computed as defined.
  - **The null (`fills_base`).** It adds, for each chosen knot, the parity of its three distinctions. That is exactly KF3's fill
    point of that knot (MEET-ORDERS Lemma A), with no state added.
  - **The multiset key.** N with the sorted multiset of table entries, labels dropped.
  - **The table canonical form.** It is an exhaustive individualisation–refinement on the counts.
  - **The G2 gate.** It checks that table classes equal state classes (DISTANCE-ORDER 3(a), which covers these signed
    not-all-equal bases) on five and six to n0 + 3.
- **A fresh recomputation (the owner's point 4; `referee_dist.py`).**
  - **The method.** The referee's own KF3 engine, run over every bracketing (so the prior needs no mirror bookkeeping). Table classes
    come from one registry: a WL hash of the edge-weighted complete graph, then VF2.

  | n0, k | Grown table | Null | Multiset | Study |
  | --- | --- | --- | --- | --- |
  | 5, 1 | 0.6306 | 0.6306 | 0.6306 | 0.63 |
  | 5, 2 | 0.6035 | 1.0 | 0.1154 | 0.60 |
  | 5, 3 | 0.3948 | 1.0 | 0.2472 | 0.39 |
  | 5, 4 | 0.2230 | — | 0.1881 | 0.22 |
  | 6, 1 | 0.4478 | 0.4478 | 0.3833 | 0.45 |
  | 6, 2 | 0.6484 | 0.8273 | 0.4239 | 0.65 |
  | 6, 3 | 0.6341 | 1.0 | 0.3388 | 0.63 |

  - Every value equals the study's results.json to four digits.
  - At k = 1 the grown table equals the null by construction: KF3's first step fills one uniform knot.
  - In law, no two bare bracketings have equal table laws at any k ≥ 1. The equal presentation pairs are exactly the mirror pairs at
    k ≥ 2, plus the k = 1 tie at six that the study reports.

## 1. "The rest is lost, not hidden" (the coordinator's question; Block on this reading)

- **The study's argument.** The table up to renaming determines the states up to renaming (3(a)). So what the unnamed table misses
  of the nesting, the unnamed states miss too, and "the growth does not keep it".
- **The gap.** Both readings drop the names: which distinctions are the line's and in what order the new ones were added. The
  referee read the same grown bases with names kept (`referee_dist.py`):

  | n0, k | Unnamed table (the study's) | Line's distinctions named, new ones anonymous | All named (new ones in order of growth) |
  | --- | --- | --- | --- |
  | 5, 1 | 0.63 | 0.63 | 0.63 |
  | 5, 2 | 0.60 | 0.70 | **1.0** |
  | 5, 3 | 0.39 | 0.69 | **1.0** |
  | 5, 4 | 0.22 | 0.51 | **1.0** |
  | 6, 1 | 0.45 | 0.45 | 0.45 |
  | 6, 2 | 0.65 | 0.67 | 0.83 |
  | 6, 3 | 0.63 | 0.71 | 0.91 |

  By 3(a) again, the named table is the named base itself.
- **What follows.**
  - A single grown base keeps all of the nesting at five, and nearly all at six by k = 3.
  - It is "hidden" in the names, mostly in the order of growth. Knowing only which distinctions are the line's adds 0.07 to 0.29.
  - So the share the study reports measures what a reader loses by not knowing which distinction is which. It does not measure what
    the growth loses.
- **The blur goes the same way.** Named, the share rises (1.0 at five from k = 2; 0.45, 0.83, 0.91 at six). The study's "later
  growth blurs it" is the unnamed reading: up to renaming, later fills of re-bracketed triples become confusable. Named, they are
  not.
- **For A97.** "Distance is the only information": the unnamed distances of one grown base carry 0.4 to 0.7 of the nesting. The
  distances together with the distinctions' names carry all of it at five. The names that matter most are the order of growth, and
  that is history, not distance.
- **The fixes.**
  - Replace "the rest is lost, not hidden: in these bases the distances determine the states" (note, A97 line, intuition entry) with
    "the rest is carried by the names: which distinctions are the line's and in what order the new ones came. With them one grown
    base holds all of it at five and 0.91 at six".
  - Restate the reading for A97 accordingly.

## 2. One sample or the law (the coordinator's question; Narrowing)

- **One sample.** The shares are the information in one grown base, a single sample of the random growth, read without names,
  under one prior.
- **The law.** In law, the tables of every two bare bracketings already differ at k = 1, and those of every two non-mirror
  presentations at k = 2. So the law of the distances carries all of the nesting from the first new distinction, confirmed by the
  referee for five and six.
- **A fair sentence.** "The law of the grown distances determines the nesting from the first new distinction. One grown base's
  unnamed distances carry part of it, at most about 0.6 to 0.7, and its named distances carry all of it at five."
- **Where the scope is missing.** The headline's "growth writes part of it into the distances, never all" omits it. So do the
  owner's-terms paragraph and the A97 line.

## 3. "Then growth blurs it" and "about two thirds" (the coordinator's question; Narrowing and wording)

- **Where the unnamed share falls.** It falls after its peak for five, six and seven only. For eight and nine it was still rising at
  k = 3, the last computed: 0.30, 0.51, 0.58 and 0.26, 0.45, 0.53.
- **So the following are not shown for eight and nine:**
  - "peaks near n0 − 4", an extrapolation from three points;
  - "never all";
  - "at most about two thirds".
- **The prior.** Under a prior uniform over bare bracketings, the unnamed peaks are 0.70 (five, k = 1) and 0.69 (six, k = 2). The
  pre-registration's "below two thirds" holds only under the labelled prior.
- **The fix.** Write "about 0.6 to 0.7, depending on the prior, for five to seven; not yet peaked for eight and nine".

## 4. "No distance holds the nesting before growth" (the coordinator's question; Not a block)

- **What it says.** All presentations of a line have the line's states, so every distance read from the states is the same for all
  of them. That is the definition of a presentation (MEET-ORDERS Lemma 0), and the premise STATE-RULES and KNOT-CAP started from.
- **Nothing more.** It is right, but it is a restatement, not a finding of this study.

## 5. Prior work (the owner's point 5)

- **Known.** The tools are standard: mutual information as a share of entropy, and Bayes identification.
- **Specific to the program.** The object is: KF3, presentations of a line, disagreement tables. No outside result applies.
- **An analogue for the named result.** Revealing labelled knots one at a time, as in the null, is close to reconstructing a
  triangulation from a few of its triangles, a standard identifiability count. The referee did not search further.

## Fixes for the thread (listed for the owner, not folded in)

1. **"Lost, not hidden".** It is false. Named, one grown base carries all of the nesting at five (k ≥ 2) and 0.91 at six (k = 3).
   Correct it in the note, the A97 line and the intuition entry, and log it in `docs/CORRECTIONS.md`. **Block** (on the reading;
   every number stands).
2. **Scope.** Say "one grown base, read without names, under the labelled prior". Say that in law the tables carry all of it from
   k = 1. **Narrowing.**
3. **Shape.** "Then blurs it": unnamed only, and for five to seven only. For eight and nine the share has not yet peaked.
   **Narrowing.**
4. **The prior.** About 0.6 to 0.7, with "below two thirds" only under the labelled prior. **Not a block.**
5. **Before growth.** Present "none before growth" as the definition, not a finding. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, `job.py`, `merge.py`, `checks.py` and the results;
  - wrote its own table classes, null, multiset key, named and line-named tables, and shares under two priors
    (`referee_dist.py`), on its MEET-ORDERS-R1 KF3 engine.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_dist.py`.**
- **`referee_dist_5_4.json` and `referee_dist_6_3.json`.**

Reproduce, from `research/MEET-DIST-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_dist.py 5 4 > referee_dist_5_4.json
../../../.venv/bin/python -B referee_dist.py 6 3 > referee_dist_6_3.json
```
