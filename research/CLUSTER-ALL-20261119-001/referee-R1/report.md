# Referee report CLUSTER-ALL-001-R1 (the referee's own growth against the rule)

**Verdict: confirmed, with two wording points. No Block.**
- **The rule reproduces against the referee's own growth** (its full engine, with the GF(2) implied-parity test), on samples of
  the study's five- and six-knot tests and on all twelve falsifiers.
  - **One size past the study, on 3,000 random seven-knot arrangements:** 2,985 of the 2,986 in scope equal the rule at every
    round.
  - **The one miss has the study's mechanism:** a block of four knots with one pair unlinked, carrying two round-3 junctions.
- **The break reproduces.** In both overlapping-sunflower falsifiers, the referee's growth puts two round-3 junctions, each with
  three parents, on the same four start knots.
- **The three clauses checked** (pendants, relay, hyperedges) agree with the policy and are exercised by the sample.
- **The pilot history has six versions.** The last one drew the scope around the pilot's 38 remaining misses. The pre-registration
  reports the 38 as out of scope, but does not say the scope was drawn after they missed. **Wording; not a block.** The frozen
  tests are unaffected.
- **The post hoc dimension reading holds, graded as post hoc.** The rule's class equals the census's dimension on all 15,261
  arrangements; the referee's own measured dimension equals the chain count on 300 of 300. But "the chain count reproduces all
  15,261" needs two conventions that the note states in words and `dimension.py` leaves unset (237 arrangements). **Wording; not a
  block.**

## 1. The rule against the referee's own growth

`referee_cluster.py sample` and `seven`. Each sampled start was grown 20 rounds (20,000 junctions) by the referee's own engine,
`FIRST-KNOT-R1`'s, which has the fewest rule and an exact GF(2) implied-parity test. The referee's lean engine is not exact on these
small closing starts, so it was not used. The rule's `clusters.series` (the object under test) was run read-only for the prediction.

| Sample | Cases | Equal at every round | Out of scope | Misses |
| --- | --- | --- | --- | --- |
| Five-knot census, random 600 of 24,502 (seed 19) | 600 | 599 | 1 | 0 |
| Six-knot samples, the study's sampler re-implemented (seeds 70000 + 7k) | 300 | 297 | 2 | 1: seed 71946, the study's own miss |
| The study's two six-knot misses | 2 | 0 | 0 | 2: both differ from round 3, as recorded |
| T4, the twelve falsifiers | 12 | 9 | 1 | 2: both overlapping sunflowers |
| **Seven knots, one size past** (the referee's sampler: sizes 3 to 5, 6 to 14 touches, connected; seeds 90000 + k) | **3,000** | **2,985** | 14 | **1:** seed 91758, from round 3 |

- **Seven knots.** 1,988 stall, 70 close and 928 are alive at round 20 in the referee's growth. The rule's scope holds 99.5% of
  them, as at five knots.
- **The seven-knot miss** (`referee_cluster_seven_miss.json`) is the study's mechanism.
  - The rule has a block of four knots {2, 4, 5, 6} with the pair 4–5 unlinked.
  - The referee's round 3 has two junctions on those four start knots, each with three parents.
  - So the counts read 12 against the rule's 11 at round 3.

**What the sample exercises** (`referee_cluster_coverage.json`, the rule's own analysis of each sampled start). Of the 322
five-knot starts that grow or close:
- 176 have a leaf pendant, 177 an endless chain and 80 a point with two chains;
- 8 have a hyperedge.

Among the six-knot ones, 4 have a hyperedge. **The hyperedge clause is therefore lightly sampled here.** The study's T1 covers its
748 five-knot starts.

## 2. The break (the mechanism)

`referee_cluster_sample.json`, "overlapping sunflowers, my growth":
- **In both falsifiers** (b with no surplus and with one), the referee's growth has two round-3 junctions whose start-knot ancestors
  are the same four knots {2, 3, 4, 5}, each with three parents.
- **The rule counts one.** This is the study's account: two maximal valid sets with one union.

## 3. The clauses against the policy (the owner's first point)

`clusters.py` was read against the complete-round policy (A104) and its fewest rule, k = max(d, 3 − p, 1):
- **The pendants.** A surplus offshoot takes one parent, so it gets at least two fresh distinctions.
  - **Open ≥ 3:** its demand is met and nothing joins it again, so it is a leaf.
  - **Open = 2:** the floor gives it one distinction beyond its demand every round, so it is an endless chain.
  - **Open = 1:** a point with two chains.
  - **The exception** (the start's only loose distinction) takes every loose bit. That is the implied parity, which closes; it is
    coded as `len(live) == 1`, which is the same condition.
- **The relay.** A finished piece with other live pieces gets y^(m + 1)/(1 − y)², two chains from its top. The top's parity is not
  implied while other loose distinctions exist.
- **The hyperedge.** A round-1 group of three or more, with its earlier top (`m` less one round per extra knot).
- **Empirically,** each clause agrees with the referee's growth wherever the sample exercises it (Section 1).

## 4. The pilot history (the owner's second point)

`pilot/history.json` has six versions:

| Version | Change | Pilot result (1,939 arrangements) |
| --- | --- | --- |
| v1 | pendants, relay, the implied single loose distinction; two common neighbours and round-1 triples out of scope | 1,212 match, 727 out of scope |
| v1b | merged blocks | 1,737 match, 202 out of scope |
| v2 | hyperedges (no margin) | 1,842 match, **97 miss** |
| v3 | the series' margin | 1,901 match, **38 miss** |
| v4-tried | hyperedges merged with overlapping blocks | no gain, reverted |
| v5 | **hyperedges overlapping another block in two knots out of scope** | 1,901 match, 38 out of scope |

- **"Revised four times" is right** for the rule: v1b, v2, v3 and the implied-closure change inside v1. The tried-and-reverted v4 is
  recorded too.
- **The scope cut that turned the 38 misses into "out of scope" came last, after they had missed.** The pre-registration says "38
  are out of scope", and that the advisor explained them. It does not say that the scope boundary was drawn after those 38 missed.
  - **What stays valid.** The frozen tests are unaffected: the predicate was fixed by hash before T1, and the five-knot scope
    fraction (99.5%) was computed from the starts alone.
  - **The wording should say it.** For example: "the scope excludes the 38 pilot arrangements the rule missed; it was drawn after
    they missed".
  - **Not a block.**

## 5. The post hoc dimension reading (the owner's third point, graded separately)

`referee_cluster_posthoc.json` (`dimension.py` run read-only as the object under test, on every census arrangement):
- **The rule's own long-horizon class equals the census's measured dimension on all 15,261 polynomial arrangements in scope.** That
  is what the note compares, and it reproduces.
- **The chain-count reading as coded** (the largest number of chains feeding one cycle-free piece) equals the class on 15,024.
  - **234** close with no live knot. There the chain count is undefined (None) and the class is 0: they are the note's "it closes"
    case.
  - **3** are bare rings with a cycle and class 1: the note's "a bare ring is itself one chain once unrolled".
  - **With those two stated conventions, all 15,261 agree.** But "reproduces the census's measured dimension in all 15,261" should
    name them, since the code does not apply them.
- **Against the referee's own growth:** on 300 growing arrangements grown 45 rounds, the referee's measured dimension equals the
  chain count in **300 of 300**.
- **Grade.** The reading holds as a post hoc description of the census. It was not a frozen prediction, as the note says.

## Addendum (2026-11-19, found while refereeing SCALE-SHARE-20261119-001): a second break, from six knots

**A second shape on which the rule fails inside its scope.** A block of two knots and two first-round groups of three
(hyperedges) form a cycle of blocks, each pair of blocks sharing one knot.
- **Where it occurs.** The rule declares these in scope; its scope excludes only a hyperedge sharing two or more knots with
  another block.
- **The rule fails from round 2,** and its growth class can be wrong. Both outcomes below are confirmed by the referee's engine and
  by the study's own grower (joinlib's `grow`, run read-only as a cross-check):
  - **Six knots, seed 6028024** (sizes 5, 3, 5, 5, 5, 5; blocks {0, 3}, {0, 2, 4}, {3, 4, 5}). The growth is 6, 5, 5, 6, 7, 8, …,
    two-dimensional. The rule gives 6, 5, 7, 11, 18, 30, … and classifies it **a ring (exponential)**.
  - **Six knots, seed 6029462** (blocks {2, 5}, {1, 2, 4}, {3, 4, 5}). The growth closes: 6, 3, 1. The rule gives 6, 3, 3, 3, …,
    **dimension 1**.
  - **The same two outcomes at 16 and 12 knots** on the referee's SCALE-SHARE chains (a false ring at 16, a closing start read as
    dimension 1 at 12).
- **How often.** In random arrangements with the referee's sampler (40,000 per knot count, `hyper_cycle_search.py`), the shape was
  found in scope 2, 10, 7, 5 and 1 times at 6, 7, 8, 9 and 10 knots. The rule missed 23 of the 25.
  - It never occurs in the five-knot census (0 of 24,502), so T1 stands.
  - The study's 2,000 six-knot samples would hold about 0.1 such starts, which is why T3 did not meet it.
- **What it changes.** The note's "where it breaks" (the overlapping sunflowers, a block with a missing pair) is not the only
  break. Its reading that "the break is understood" is narrowed, and the second mechanism is not yet explained.
- **Files:** `research/SCALE-SHARE-20261119-001/referee-R1/` (`scan_cycles.py`, `hyper_cycle_search.py`, `hyper_cycle_small.py`,
  `new_shape.py` and their JSON files).
- **Correction 3 for the owner:** **Narrowing; not a block.** The rule is computed, not proved, and every five-knot result stands.

## Corrections for the owner (listed, not folded in)

1. **The pilot's scope.** Say that the scope exclusion (hyperedges sharing two knots with another block) was drawn after the 38
   pilot arrangements it excludes had missed. **Not a block (disclosure).**
2. **The post hoc figure.** "All 15,261" needs the two conventions (234 closing arrangements with no live knot count as "closes";
   3 bare rings count as one chain), which `dimension.py` leaves unset. **Not a block (wording).**

## How the work was split

- **The referee:**
  - read `cluster_all.md`, the pre-registration, `clusters.py`, `job.py`, `dimension.py` and `pilot/history.json`;
  - wrote `referee_cluster.py` (sample, posthoc, seven), `coverage.py` and `seven_miss.py`, on its FIRST-KNOT-R1 growth engine and
    TOUCH-CENSUS-R1 helpers.
- **Read-only, as the objects under test:** `clusters.py` (the rule) and `dimension.py` (the post hoc reading). The study's
  falsifier list (`job.falsifiers`) and six-knot misses (`results.json`) were read as data.
- **No growth or scoring code of the study was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
