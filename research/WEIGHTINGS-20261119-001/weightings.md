# Two dimensions: typical of the weighting, not of the growth

Epic `WEIGHTINGS-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead to challenge `A106` (and `A107`).
Goal G17. **Referee pending.**

**Record.**
- **Pre-registration:** [preregistration.md](preregistration.md), frozen in commit `61b0ec72a` at 15:07 UTC, before any sample
  was classified (smoke tests disclosed).
- **The run:** the shared runner (`runs/weightings`, 56 cases, all ok by 15:09 UTC). There are 112,000 samples: seven weightings ×
  eight sizes × 2,000.
- **Code:** [weightlib.py, job.py, merge.py](../../experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/). The
  reader is SCALE-THEOREM's, which is DOUBLE-IDENT's class and rule, unchanged.
- **Results:** [results.json](../../artifacts/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/results.json).
- **Post hoc, after the run was read:** [posthoc.py](posthoc/posthoc.py), output in [posthoc.json](posthoc/posthoc.json). It
  checks the five-place lemma below on every tree of 3 to 14 knots, and the dead-hub start.

## The answer

**In the owner's terms.**
- **Two is typical because of the weighting, not because of the growth.** The test kept the proved theorem as the reader and
  changed only how starts are drawn.
  - **Uniform random trees.** Every knot gets the places its joins need, so nothing stalls and every start is in the proved class.
    Under this weighting, three or more dimensions grows with size: 5% of growers at seven knots, 12% at twelve, 24% at sixteen
    and 37% at twenty. Up to six dimensions occur.
  - **Adding random extra lines** (Poisson, mean one) makes exponential growth common in the class: 11% of its growers at six
    knots, rising to 41% at twenty. Three or more dimensions reaches 23%.
  - **The crowded weightings keep two.** These are the configuration model, which joins places at random, and growth by
    attaching knots one at a time.
    - Most of their starts stall: 50% to 88% under the configuration model, and 64% to 99.7% under attachment.
    - Among their in-class growers, two dimensions are 80% to 100%.
    - Three never occurs, and exponential growth appears in 8 samples in all.

    The configuration model follows SCALE-SHARE's pattern: two rises from 80% to 100% of in-class growers, against 85% to 98%. So
    that weighting's result is not an artefact of counting each description once.
- **So what I'm about to tell John needs narrowing.** "Two is typical" holds for starts whose knots are crowded and have three to
  five places: the census, SCALE-SHARE, random pairing of places, and growth by attachment. It is not a law of the growth. By the
  stated threshold (10% of in-class growers, with at least 20 of them), three or more is common:
  - under random trees from twelve knots;
  - with surplus at 25% or 50% from sixteen knots.

  Exponential growth is common with extra lines from six knots.
- **Why, in the theorem's terms.**
  - A growth's dimension is the most chains in one piece of its map, with a finished piece counting two.
  - A chain hangs from a knot that keeps open places after its joins. In a bare tree that is a leaf beside a knot of two touches.
  - A uniform random tree has (n−1)(1−2/n)^(n−3) such leaves on average, about n/e² for large n (W2 held within 1.6% at every
    size). They split
    between the tree's two parity classes, so the dimension grows with the number of knots.
  - Crowded weightings leave almost no knot with open places, so chains are scarce and pieces finish, which relays them to two.
- **The five-place cap is what keeps trees at two. Proved here, post hoc.**
  - **The lemma.** A bare tree whose knots all have at most five places grows in at most two dimensions.
  - **Why.** Each knot's places count its touches plus the pairs it joins. With at most five places, no knot touches three
    non-leaves, so the non-leaves form one line of knots: the tree is a caterpillar, in the literature's word.
  - **So** only the line's two ends can carry a chain.
  - **Checked** on every tree of 3 to 14 knots (posthoc.py), and the run agrees. Every three-or-more-dimensional tree sample has a
    knot of six or more places. Across all 112,000 samples, no in-class start whose knots all have at most five places is
    three-or-more dimensional (0 of about 25,000 such growers).
  - **The cap is not a law, though.** A hand-built start (post hoc) of ten knots of at most five places is in the class and grows
    three-dimensionally. It is three arms joined through a dead hub, a knot all of whose places are shared. It agrees with the
    relayed cover round by round to round 6. The program's engine grows it 12, 19, 27, 36, … to round 20, a growth with steadily
    increasing differences.
- **The theorem held where the census never reached.** I regrew 1,226 samples, including 622 predicted three-to-six-dimensional or
  exponential. Every one agrees with the relayed cover round by round to round 6, in every junction's parents and fresh count.
- **One prediction failed (W7).** The advisor expected attachment growth's in-class starts to be dominated by cycles, and so to grow
  exponentially. Instead its cycles almost all stall or leave the class. Exponential growth is 1.5% of its in-class growers at five
  knots and absent after. Its in-class starts are few: 457 growers at five knots, 4 at twenty.
- **Where "two" comes from changes too.**
  - In random trees, two chains in one piece give 67% of two-dimensional growers at twenty knots, against 10% at eight. A relay
    alone falls from 51% to 13%.
  - In the configuration model, two chains give 73% at five knots. A relay together with two chains gives 61% at twenty.

**The table.** Shares are of all samples for the class mix, and of the class's growers for the dimensions. Counts are of samples
(2,000 per row).

| Weighting | Knots | Stall | Out (S3) / (S4) | In the class | Its growers | Dim 1 | Dim 2 | Dim 3+ | Exponential |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| tree | 5 | 0.0% | 0.0% / 0.0% | 100.0% | 1,924 | 0.0% | 100.0% | 0.0% | 0.0% |
| tree | 6 | 0.0% | 0.0% / 0.0% | 100.0% | 1,992 | 27.4% | 72.6% | 0.0% | 0.0% |
| tree | 7 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 30.1% | 64.8% | 5.1% | 0.0% |
| tree | 8 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 24.1% | 73.0% | 2.9% | 0.0% |
| tree | 10 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 22.5% | 69.6% | 7.9% | 0.0% |
| tree | 12 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 20.2% | 67.8% | 12.0% | 0.0% |
| tree | 16 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 14.4% | 61.8% | 23.8% | 0.0% |
| tree | 20 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 10.9% | 52.0% | 37.0% | 0.0% |
| tree-s25 | 5 | 0.0% | 0.0% / 0.0% | 100.0% | 1,938 | 6.6% | 93.4% | 0.0% | 0.0% |
| tree-s25 | 6 | 0.0% | 0.0% / 0.0% | 100.0% | 1,992 | 19.3% | 80.7% | 0.0% | 0.0% |
| tree-s25 | 7 | 0.0% | 0.0% / 0.0% | 100.0% | 1,999 | 19.9% | 78.3% | 1.8% | 0.0% |
| tree-s25 | 8 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 19.7% | 79.0% | 1.4% | 0.0% |
| tree-s25 | 10 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 21.1% | 74.9% | 4.0% | 0.0% |
| tree-s25 | 12 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 19.2% | 73.4% | 7.4% | 0.0% |
| tree-s25 | 16 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 16.0% | 67.0% | 17.0% | 0.0% |
| tree-s25 | 20 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 15.1% | 58.9% | 26.1% | 0.0% |
| tree-s50 | 5 | 0.0% | 0.0% / 0.0% | 100.0% | 1,969 | 12.0% | 88.0% | 0.0% | 0.0% |
| tree-s50 | 6 | 0.0% | 0.0% / 0.0% | 100.0% | 1,995 | 14.9% | 85.1% | 0.0% | 0.0% |
| tree-s50 | 7 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 16.7% | 82.4% | 0.9% | 0.0% |
| tree-s50 | 8 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 17.4% | 81.3% | 1.2% | 0.0% |
| tree-s50 | 10 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 18.8% | 78.1% | 3.0% | 0.0% |
| tree-s50 | 12 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 19.2% | 76.3% | 4.5% | 0.0% |
| tree-s50 | 16 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 17.1% | 72.5% | 10.4% | 0.0% |
| tree-s50 | 20 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 16.3% | 65.5% | 18.2% | 0.0% |
| tree-s100 | 5 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 0.0% | 100.0% | 0.0% | 0.0% |
| tree-s100 | 6 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 28.1% | 71.9% | 0.0% | 0.0% |
| tree-s100 | 7 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 13.8% | 86.2% | 0.0% | 0.0% |
| tree-s100 | 8 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 12.9% | 87.1% | 0.0% | 0.0% |
| tree-s100 | 10 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 15.2% | 84.2% | 0.7% | 0.0% |
| tree-s100 | 12 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 14.1% | 84.9% | 1.1% | 0.0% |
| tree-s100 | 16 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 16.7% | 80.2% | 3.2% | 0.0% |
| tree-s100 | 20 | 0.0% | 0.0% / 0.0% | 100.0% | 2,000 | 18.0% | 77.8% | 4.2% | 0.0% |
| tree+ | 5 | 0.0% | 48.6% / 13.0% | 38.4% | 739 | 8.3% | 91.7% | 0.0% | 0.0% |
| tree+ | 6 | 0.0% | 43.4% / 15.2% | 41.5% | 826 | 24.9% | 63.7% | 0.0% | 11.4% |
| tree+ | 7 | 0.0% | 41.9% / 16.6% | 41.5% | 830 | 26.0% | 55.4% | 3.4% | 15.2% |
| tree+ | 8 | 0.0% | 37.0% / 16.2% | 46.9% | 937 | 20.9% | 58.4% | 1.9% | 18.8% |
| tree+ | 10 | 0.0% | 36.1% / 15.6% | 48.3% | 966 | 17.1% | 51.6% | 6.8% | 24.5% |
| tree+ | 12 | 0.0% | 36.3% / 13.6% | 50.1% | 1,002 | 15.9% | 50.4% | 7.0% | 26.7% |
| tree+ | 16 | 0.0% | 30.1% / 13.8% | 56.1% | 1,122 | 10.2% | 41.1% | 14.3% | 34.3% |
| tree+ | 20 | 0.0% | 29.0% / 11.7% | 59.2% | 1,185 | 5.2% | 30.9% | 23.4% | 40.5% |
| grow | 5 | 64.3% | 5.9% / 5.7% | 24.1% | 457 | 14.2% | 84.2% | 0.0% | 1.5% |
| grow | 6 | 87.2% | 1.5% / 2.0% | 9.3% | 178 | 13.5% | 86.5% | 0.0% | 0.0% |
| grow | 7 | 93.0% | 1.8% / 0.6% | 4.5% | 88 | 10.2% | 89.8% | 0.0% | 0.0% |
| grow | 8 | 94.3% | 1.3% / 0.5% | 3.9% | 76 | 7.9% | 92.1% | 0.0% | 0.0% |
| grow | 10 | 96.1% | 0.5% / 0.4% | 3.0% | 60 | 3.3% | 96.7% | 0.0% | 0.0% |
| grow | 12 | 97.8% | 0.2% / 0.4% | 1.6% | 32 | 0.0% | 100.0% | 0.0% | 0.0% |
| grow | 16 | 99.1% | 0.1% / 0.1% | 0.7% | 14 | 0.0% | 100.0% | 0.0% | 0.0% |
| grow | 20 | 99.7% | 0.1% / 0.1% | 0.2% | 4 | 0.0% | 100.0% | 0.0% | 0.0% |
| config | 5 | 49.6% | 4.8% / 9.8% | 29.6% | 460 | 20.0% | 79.8% | 0.0% | 0.2% |
| config | 6 | 55.9% | 4.9% / 8.2% | 26.4% | 406 | 19.5% | 80.5% | 0.0% | 0.0% |
| config | 7 | 62.5% | 4.7% / 6.5% | 23.4% | 387 | 16.8% | 83.2% | 0.0% | 0.0% |
| config | 8 | 66.0% | 4.7% / 4.5% | 21.9% | 368 | 12.0% | 88.0% | 0.0% | 0.0% |
| config | 10 | 75.1% | 2.7% / 4.0% | 16.8% | 306 | 5.9% | 94.1% | 0.0% | 0.0% |
| config | 12 | 77.7% | 2.3% / 3.5% | 16.0% | 294 | 2.7% | 97.3% | 0.0% | 0.0% |
| config | 16 | 83.2% | 1.6% / 1.7% | 13.2% | 256 | 2.0% | 98.0% | 0.0% | 0.0% |
| config | 20 | 87.5% | 0.8% / 1.6% | 10.0% | 197 | 0.0% | 100.0% | 0.0% | 0.0% |

The weightings:
- **tree:** a uniform labelled tree at bare sizes.
- **tree-sP:** the same tree, with one surplus distinction per knot with probability P%.
- **tree+:** a bare tree plus Poisson(1) extra lines.
- **grow:** knots of 3 to 5 places attached one at a time.
- **config:** knots of 3 to 5 places, with places joined by a uniform random partial matching.

The full figures, by fine class, with mechanisms, the five-place restriction and tree+ split by extra lines, are in results.json.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| W1 | tree: three-plus count 0 at n = 5, 6; 70–130 at 7; 31–73 at 8; more at 7 than 8 | **held** | 0, 0, 103, 58 (expected 100 and 51) |
| W2 | tree: mean ray-leaf count within 5% of (n−1)(1−2/n)^(n−3) | **held** | within 1.6% at every size |
| W3 | tree and tree-sP: every sample in the class | **held** | 64,000 of 64,000 |
| W4 | tree and tree-sP: no exponential growth | **held** | 0 |
| W5 | (risky) tree: three-plus above 10% of all at 16 and 20% at 20 | **held** | 23.8% and 37.0% |
| W6 | tree+: exponential at least 10% of in-class growers at n ≥ 8; no extra line means all in class, no exponential | **held** | 18.8% to 40.5%; the zero stratum all in class, none exponential |
| W7 | grow: exponential above half of in-class growers at n ≥ 10 (where at least 20); three-plus under 2% | **failed** | exponential 0 of 60 and 0 of 32 at 10 and 12; three-plus 0 everywhere |
| W8 | n = 20: three-plus share falls with surplus, tree ≥ s25 ≥ s50 ≥ s100 | **held** | 37.0% ≥ 26.1% ≥ 18.2% ≥ 4.3% |
| W9 | config like SCALE-SHARE: stall above 40%; dimension 2 at least 70% and three-plus under 2% of in-class growers | **held** | stall 50–88%; dimension 2 79.8–100%; three-plus 0 |
| W10 | (the stop rule) every regrown sample agrees to round 6 | **held** | 1,226 of 1,226 (622 three-plus or exponential) |
| W11 | grow: cycle-free share at least (2/3)^(n−1) less three standard errors | **held** | above the floor at every size |

10 of 11 held.

## Assumptions

- **A106** (arrangements weighted uniformly up to five knots of three to five places): **Overturned** as a reading of what the
  growth makes typical. Assumed → Under challenge → Overturned.
  - Its challenge named random pairing of places and growth that adds knots one at a time. Under both, two stays typical and three
    absent.
  - It also named more than five places. Under random trees, where knots take the places their joins need, three or more is common
    from twelve knots.
  - So "two typical, three and four rare" is a fact about crowded knots of at most five places, not about the growth. The census's
    figures stand as figures under its weighting (A71); the claims that read them as the growth's are narrowed (Corrections).
- **A107** (ring joins weighted over one bare census): history line. Under random trees with one random extra line, every in-class
  start whose one cycle has knots attached grows exponentially (94 of 94 at six knots, 391 of 391 at twenty). Only a cycle through
  every knot stays one-dimensional, as the theorem says. "Every join speeds the ring" holds beyond the bare census.
- **A71** (each random process is one weighting) is the frame used here.

## Known results, and what this adds

- **Known, cited once.**
  - Leaves and degrees in uniform random labelled trees: Rényi (1959); Moon, *Counting Labelled Trees* (1970). The ray-leaf mean
    follows from Prüfer codes.
  - Caterpillars, the trees whose non-leaves form a path: Harary and Schwenk (1973).
  - Configuration models: Bollobás (1980).
- **What this adds.** The cheapest growth's dimension under each weighting, read from proved statements, with a mechanism:
  - typical dimension grows with size under random trees;
  - cycles make it exponential;
  - crowded weightings and the five-place cap keep it at two.

## Limitations

- **Sizes.** Every sample has 5 to 20 knots, and the regrowth is checked to round 6.
- **The out-of-class starts** are not read. They are 41–62% of tree+ (mostly first-round groups of three from short cycles), 2–15% of
  config and 0–12% of grow.
- **Attachment growth** leaves very few in-class starts above ten knots (14 at sixteen, 4 at twenty).
- **The five-place lemma** is proved for bare trees only. The dead-hub start shows that it fails once a knot is dead, and the
  general case is open.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze, staying within its text.
- **It judged none of the original three weightings clean,** and added the surplus knob and the configuration model.
- **It gave the exact tree counts,** 840/16,807 and 6,720/262,144, and the ray-leaf mean. Both held.
- **Its traps were adopted:** shares of all samples beside in-class shares, the two sources of two, and the stratified regrowth.
- **Its expectations.** Its cycle expectation for tree+ held (W6). For attachment growth it failed (W7).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: two dimensions under other weightings | **Status:** Successful (10 of 11 held; W7 failed) | Three or more is common under random trees from twelve knots, and exponential with extra lines from six; crowded weightings keep two; 1,226 of 1,226 regrown agree |
| Local direction: what the cheapest growth makes typical | Research directions | The typical dimension follows the open places a weighting leaves, by the theorem's own mechanism |
| Broader exploration: what the cheapest growth builds | Known alternatives | Dimension is chains per piece; any number of chains occurs in the proved class; cycles make it exponential |
| Long-term goal: G17 | Capability gained | Typical and rare growth read per weighting from proved statements, with the five-place cap named as what keeps trees at two |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Dimension grows linearly under random trees: prove that the typical dimension is about n/(2e²) for large n | 2/3 — what is typical, proved at every size under one weighting | 3/3 — the ray-leaf mean is exact; it needs concentration and the split between the two parity classes | prove concentration of each parity class's ray-leaves → stop at a proof, or at a size where the measured dimension departs from it | Alternative · proposed |
| 2 | What the five-place cap forbids beyond trees: without dead knots, can knots of at most five places grow in three dimensions in the class? | 2/3 — it says whether the census's two comes from the cap itself | 2/3 — the caterpillar argument and the dead-hub start bound it | extend the caterpillar argument to the relayed map with multiplicities → stop at a proof, or a start without dead knots that has three chains | Alternative · proposed |
| 3 | Mutually touching knots (`SCALE-THEOREM-20261119-001#1`): the unproved part, now also 41–62% of the random trees with extra lines | 2/3 — re-rated from 3/3: the rare dimensions no longer live only there | 1/3 — a different complex is needed | find the complex on the census's 2,958 out-of-class starts → stop at one, or a start where none exists | Alternative · in the basket |

## Final report as sent (2026-11-19 15:22 UTC)

**Outcome:** Two dimensions are typical because of the weighting, not because of the growth, so "two is typical" needs narrowing before it goes to John. I kept the proved theorem as the reader and changed only how starts are drawn: seven weightings, frozen before I looked, 2,000 samples per size from 5 to 20 knots. Three or more dimensions does become common in the class, and so does exponential growth. 10 of 11 predictions held. Closed, referee pending.

- **Uniform random trees.** Nothing stalls and every start is in the proved class. Three or more dimensions is 5% of growers at seven knots, 12% at twelve, 24% at sixteen and 37% at twenty, with up to six dimensions.
- **Random extra lines** (Poisson, mean one) make exponential growth common in the class: 11% of growers at six knots and 41% at twenty.
- **The crowded weightings keep two.** These are random pairing of places (a configuration model) and growth that attaches knots one at a time. Their in-class growers are 80% to 100% two-dimensional, and three never occurs. Most of their starts stall.
- **Why, in the theorem's terms.** Dimension is the most chains in one piece of the map, and a chain needs a knot with open places left after its joins. A random tree has about n/e² leaves beside a knot of two touches, and each carries a chain. Crowded weightings leave almost none.
- **The five-place cap is what keeps trees at two.** I proved this after the run. A bare tree whose knots all have at most five places is a caterpillar: its non-leaves form one line, so it carries at most two chains. Every three-dimensional tree in the run has a knot of six or more places, and no in-class start in all 112,000 with knots of at most five places reached three. The cap isn't a law, though: a hand-built ten-knot start with a dead hub grows three-dimensionally within five places.
- **The theorem held on new ground.** All 1,226 regrown samples agree round by round to round 6. 622 of them are three- to six-dimensional or exponential, which the census never reached.
- **The miss.** The advisor expected cycles to make attachment growth exponential (W7). Instead its cycles stall or leave the class.

| Weighting | Knots | In the class | Dim 2 of in-class growers | Dim 3+ | Exponential |
| --- | ---: | ---: | ---: | ---: | ---: |
| random tree | 8 | 100% | 73% | 2.9% | 0 |
| random tree | 20 | 100% | 52% | 37% | 0 |
| tree + extra lines | 8 | 47% | 58% | 1.9% | 19% |
| tree + extra lines | 20 | 59% | 31% | 23% | 41% |
| configuration model | 20 | 10% | 100% | 0 | 0 |
| growth by attachment | 8 | 4% | 92% | 0 | 0 |

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: two dimensions under other weightings | **Status:** Successful (10 of 11 held; W7 failed) | Three or more is common under random trees from twelve knots, and exponential with extra lines from six; crowded weightings keep two; 1,226 of 1,226 regrown agree |
| Local direction: what the cheapest growth makes typical | Research directions | The typical dimension follows the open places a weighting leaves, by the theorem's own mechanism |
| Broader exploration: what the cheapest growth builds | Known alternatives | Dimension is chains per piece; any number of chains occurs in the proved class; cycles make it exponential |
| Long-term goal: G17 | Capability gained | Typical and rare growth read per weighting from proved statements, with the five-place cap named as what keeps trees at two |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the dimension grows linearly under random trees, about n/(2e²) | 2/3 | 3/3 | prove each parity class's chain-carrying leaves concentrate → stop at a proof, or a size where the measured dimension departs | Alternative · proposed |
| 2 | What the five-place cap forbids beyond trees: without dead knots, can knots of at most five places reach three dimensions in the class? | 2/3 | 2/3 | extend the caterpillar argument to the relayed map with multiplicities → stop at a proof, or a start without dead knots that has three chains | Alternative · proposed |
| 3 | Mutually touching knots: the unproved part, now also 41–62% of trees with extra lines | 2/3 (re-rated from 3/3: the rare dimensions no longer live only there) | 1/3 | find the complex on the census's out-of-class starts → stop at one, or a start where none exists | Alternative · in the basket |

**Corrections:** two.
- **Narrowing.** "Three or more lives only among mutually touching knots" (SCALE-THEOREM) and "every start that grows in three or four dimensions has knots that touch each other all round" (the working doc) hold only under crowded weightings of knots with three to five places, and so does the line summary's "that is why two is typical". Logged and published (bafaa96ff).
- **Not a block.** SCALE-THEOREM's referee wording points: the class now names "no stall", and open places per knot are quoted as measured (9dbf5d048).

**Goals:** G17 checkpoint (capability gained). **Assumptions:** A106 overturned as a reading of what the growth makes typical (Assumed → Under challenge → Overturned). Its named alternatives, random pairing and attachment, keep two, but more than five places doesn't; the census's figures stand as figures under its weighting. A107 gets a history line: every in-class ring with knots attached grows exponentially under random extra lines too. **Basket:** a new direction from you; nothing taken. **Advisor:** Fable 5.2, before the freeze, staying within its text. It judged none of my first three weightings clean, so I added the surplus knob and the configuration model. Its exact tree counts (840/16,807 at seven knots) and leaf mean held, and its prediction for attachment growth failed.

**Referee hand-off.** The decision note is `research/WEIGHTINGS-20261119-001/weightings.md`, the code is `experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/`, and the post-hoc checks are `research/WEIGHTINGS-20261119-001/posthoc/posthoc.py`. Please check:
- that the weightings sample what the pre-registration says, especially the configuration model's weighting by matching counts;
- the caterpillar lemma's step that no knot touches three non-leaves;
- the dead-hub start.
