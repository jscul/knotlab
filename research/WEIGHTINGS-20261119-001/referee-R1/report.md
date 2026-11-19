# Referee report WEIGHTINGS-001-R1 (samplers against their exact laws; own reading and regrowth of all 112,000 samples; the lemma to 18 knots)

**Verdict: confirmed. The Narrowing stands. No Block. One wording point, Not a block.**
- **The weightings sample what the pre-registration says.**
  - **config, by matching counts.** The referee derived the sampler's exact law of labelled descriptions. Sizes are uniform in
    {3, 4, 5}ⁿ, and the matching is uniform on all partial matchings of the N places. A description is realised by
    ∏ᵢ (sᵢ)₍degᵢ₎ / ∏ᵢ<ⱼ mᵢⱼ! matchings. The draw is conditioned on no self-line and on connection. The referee enumerated every
    such description and compared 200,000 draws of `weightlib.sample`:
    - at three knots, 752 descriptions: χ² = 760 on 751 degrees of freedom, with every line count matching;
    - at four knots, 35,118 descriptions: χ² = 34,705 on 35,117 (z = −1.6).

    No draw falls outside the support. The line count is weighted by its number of matchings, as stated.
  - **tree.** Uniform on labelled trees: χ² = 108 on 124 degrees of freedom at five knots, and 1,233 on 1,295 at six.
  - **The bare sizes.** In tree, tree-sP and tree+, the referee recomputed the bare sizes with its own engine: every knot given
    one open distinction, its round-1 groups counted, then max(3, shared + demand). Tree and tree+ match on every sample, and
    tree-sP adds 0 or 1 on every sample: 80,000 of 80,000.
  - **grow and tree+, read line by line.** Each matches the pre-registration:
    - grow: a new knot touches a first existing knot drawn in proportion to its open places; with probability 1/3 a second,
      distinct one is drawn the same way if both still have an open place; the start is redrawn when no existing knot has one;
    - tree+: Poisson(1) distinct non-adjacent pairs, at bare sizes.
- **The caterpillar lemma is correct, including the step asked about.**
  - **The step.** In the bare convention a knot's places are max(3, deg + d), where d counts the knots two apart: every pair is a
    group, since a tree has no valid three. A knot v touching three non-leaves u₁, u₂, u₃ has deg ≥ 3 and
    d ≥ Σ(deg uᵢ − 1) ≥ 3, so it has at least six places.
  - **The rest follows.** With at most five places the non-leaves induce a subtree of degree at most two, a path, so the tree is
    a caterpillar. A leaf carries a ray only beside a knot of degree 2, which on the spine is an end, so there are at most two
    rays. A tree's map has no cycle, so the dimension is at most 2.
  - **Checked one size past, on every tree of 3 to 18 knots** (the study: to 14; 205,002 trees, 368 within five places), by the
    referee's own bare sizes and reading:
    - every knot touching three non-leaves has six or more places;
    - every five-place tree is a caterpillar with at most two ray-leaves and dimension at most 2.
- **The dead-hub start, regrown.** It is in the class and the referee's reading gives three dimensions. The referee's growth
  agrees with its relayed model to round 6, and the counts to round 20 equal the program engine's (12, 19, 27, 36, … 316).
  - **The rate is exactly quadratic.** The minimal recurrence is (x − 1)³, and the second differences are 1 from round 2 on. That
    is a sharp form of "steadily increasing differences".
  - **Its bare sizes give the hub six places,** so the start is the bare spider of three arms with the hub cut to three.
- **The referee's own reading agrees on every sample, and every hard start regrows as read.** The 112,000 samples were regenerated
  with the study's seeds and read with DOUBLE-IDENT-R1's classification and X⁺ reading.
  - **The records.** The fine class, the growth class and the largest knot match the study's on all 112,000.
  - **The regrowth sample**, which is the referee's own:
    - **every** in-class start read as three or more dimensional or exponential, **6,271** in all: 3,926 at dimension 3, 512 at
      4, 56 at 5, 3 at 6, and 1,774 exponential;
    - one in sixteen other in-class growers, 4,318 more.

    The referee's growth was compared with its relayed model, keys per round to 6: **all 10,589 agree.** The study regrew 622
    hard ones; this is the theorem's first test at three to six dimensions and on exponential pieces in bulk.

## The checks (`job_weight.py` under `scripts/longrun.py`; 77 cases, all ok)

| Check | Result |
| --- | --- |
| config sampler against its exact law, 3 and 4 knots (200,000 draws each) | χ² 760 / 751 and 34,705 / 35,117 degrees of freedom; line counts match |
| tree sampler against the uniform law, 5 and 6 knots | χ² 108 / 124 and 1,233 / 1,295 |
| Bare sizes (own engine), tree, tree-sP, tree+ | 80,000 of 80,000 as stated |
| Fine class, growth class, largest knot against the records | 112,000 of 112,000 |
| Regrown, every hard in-class start / a sixteenth of the rest | **6,271 / 6,271** and 4,318 / 4,318 agree to round 6 |
| In-class growers with knots of at most five places | 25,133: none three or more dimensional; 127 exponential (tree+ 119, grow 7, config 1) |
| Five-place lemma, every tree of 3 to 18 knots | 368 five-place trees: all caterpillars, at most two ray-leaves, dimension at most 2 |
| Dead hub | in the class, three dimensions, agrees to round 6, minimal recurrence (x − 1)³ |

## Point for the owner (listed, not folded in)

1. **"Two is typical" holds for knots of at most five places, crowded or not.** The note says it holds "for starts whose knots are
   crowded and have three to five places", and explains the crowded weightings by scarce open places. The data put the cause in
   the cap, not in crowding:
   - Across all seven weightings, the uncrowded trees included, none of the 25,133 in-class growers whose knots have at most five
     places is three or more dimensional.
   - The note's own lemma, and the five-place cap study after it, prove the cap is enough without dead knots.

   Crowding explains the stalls, not the two. Within five places, cycles still make growth exponential: 127 such growers, mostly
   in tree+. **Not a block:** the Narrowing is right, and only its stated cause should be the cap.

## Remarks (no correction)

- **"Typical of the weighting."** Under A71 a place cap is part of the weighting, so the headline is consistent. Of A106's named
  alternatives, the two that keep five places (random pairing and attachment) keep two, and the one that lifts the cap does not.
- **Not recomputed by the referee:** the dimension-two mechanism shares (two chains against relay), which come from the study's
  reader. Its growth classes, which the mechanism refines, agree on every sample.

## How the work was split

- **The referee:**
  - read `weightings.md`, the pre-registration, `weightlib.py`, `job.py`, `merge.py`, `results.json` and `posthoc.py` with its
    output;
  - derived the configuration sampler's exact law;
  - wrote `job_weight.py` and `weight_readout.py`. They use its own DOUBLE-IDENT-R1 classification and X⁺ reading, its
    RELAY-IDENT-R1 growth and relayed model, its FIRST-KNOT-R1 engine with the program's rule, and its BREAK-EDDIES-R1 exact
    recurrence.
- **Run as the object under test, and to regenerate the study's samples:** `weightlib.sample` only.
- **Read as data:** the per-sample records in `runs/weightings`.
- **No study reader or growth code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 2.7 GB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
