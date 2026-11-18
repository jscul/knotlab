# Referee report TOUCH-CENSUS-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Two-dimensional growth is typical. That holds under both weightings, in the complete
census, and one size past at six knots. The faster-than-power rings are real exponential growth. The numbers need updating.
- **Distinct arrangements, not descriptions, are counted.**
  - Burnside's lemma over the symmetric group, a method independent of the study's canonical form, gives exactly 3, 22, 154, 1,760
    and 24,502 (26,441).
  - The labelled weights per knot count match the study's: 3, 32, 752 and 35,118, with 2,590,792 at five knots.
  - The referee's own enumeration in the study's key format contains every key the run has read, and nothing else.
- **"Typical" survives the weighting and the unread arrangements, but the rare counts change.**
  - The 200 arrangements unread at the close were not a random sample: shards follow the sorted key list. Since then, the study's run
    has read 100 more and the referee grew the last 100.
  - In the complete census, two-dimensional growth is 81.7% of growing arrangements (the study's 81.8%).
  - But there are **13** faster-than-power rings, not 7, and **40** three-dimensional arrangements, not 36.
  - At six knots, a sample uniform over labelled descriptions gives 84.5% two-dimensional among growing arrangements (labelled
    weight), and 85.1% with distinct weight.
- **The faster-than-power rings are real.**
  - Four per-round count sequences satisfy exact integer linear recurrences over the last rounds computed: Fibonacci, with base
    1.618; x⁶ = x + 1, with base 1.135; and x⁵ = x⁴ − x² + x + 1, with base 1.263.
  - The other rings have ratios that stay flat over the last 12 rounds, at 1.26 and 1.38. A polynomial's ratio would decay like
    1 + d/t.
  - So they are not an artefact of the round horizon (computed, not proved). The base range is 1.13 to 1.62, not "1.25 to 1.4".
- **The dimension read-out is right wherever it reads a polynomial.**
  - 1,686 of 1,686 sampled readings (polynomial or stall) agree at 45 rounds with a 12-round window. These include every three- and
    four-dimensional arrangement and every "plus one" exception.
  - Its "6" is not a dimension: it means two equal fifth differences in a seven-round window, and it fired only on exponential rings.
- **One number is wrong.** "1,713 arrangements force a distinction in their start" should be **1,746** on the 26,241 read, which is
  1,749 on 26,341. The study's own results file says 1,746. Growth never adds one, as claimed. **Narrowing (number).**

## 1. What is counted (question 1)

| Knots | Distinct (Burnside, referee) | Study | Labelled descriptions (referee) | Study's labelled weights |
| --- | --- | --- | --- | --- |
| 1 | 3 | 3 | 3 | 3 |
| 2 | 22 | 22 | 32 | 32 |
| 3 | 154 | 154 | 752 | 752 |
| 4 | 1,760 | 1,760 | 35,118 | 35,118 |
| 5 | 24,502 | 24,502 | 2,590,792 | 2,572,805 read (17,987 unread) |

- **Method.** The number of distinct arrangements is (1/n!) Σ_g (connected descriptions fixed by g), computed by cycle type. Sizes
  are constant on g's cycles and multiplicities constant on its pair orbits (`referee_touch_count.json`).
- **The key format matches.** It is the least relabelling of (sizes, multiplicities), as the referee re-enumerated it. It gives the
  same 26,441, and every one of the 26,341 keys the run had read when this referee ran is among them.
- **So each arrangement is counted once, and the labelled weight n!/|Aut| is right.**

## 2. "Typical", the weighting (A106) and the unread arrangements (question 1)

- **The unread arrangements are not random.** The run shards the sorted key list. The last shards are 5-knot arrangements with the
  largest sizes, which is where the exotic growths live.
  - The shard read after the close added 3 more faster-than-power rings.
  - The referee grew the last 100 itself (`referee_touch_missing.json`): 58 stalls, 7 closes, 5 one-dimensional, 23 two-dimensional,
    **4 three-dimensional** and **3 more exponential rings**.

**The complete census** (26,341 read by the study's run, 100 grown by the referee):

| Outcome | Distinct | Share | Study (26,241) |
| --- | --- | --- | --- |
| cannot start | 11,010 | 41.6% | 10,906 |
| closes | 3,726 | 14.1% | 3,705 |
| one-dimensional | 2,081 | 7.9% | 2,068 |
| two-dimensional | 9,564 | 36.2% | 9,512 |
| three-dimensional | **40** | 0.15% | 36 |
| four-dimensional | 7 | 0.03% | 7 |
| faster than any power | **13** | 0.05% | 7 |

- **Two-dimensional among growing arrangements:** 81.7% distinct (the study's 81.8%). "About four in five" stands.
- **Rare classes:** three-dimensional 40, four-dimensional 7, exponential 13. "Three or more under 2%" still holds.
- **The weighting.** The study's labelled shares (81.4%) agree with its distinct shares, and so does every number of knots. "Typical"
  is said only where both agree, as pre-registered. So A106's choice does not decide it within this population.
- **The cutoffs.** A106's other half is the cutoff at five knots of three to five places. The six-knot sample tests it one size past
  (`referee_touch_six.json`):
  - eight Metropolis chains uniform over labelled six-knot descriptions, 1,200 samples;
  - the distinct weight comes from importance weights |Aut|/6!;
  - stall 56%, closes 7%, one-dimensional 6%, two-dimensional 31%;
  - **two-dimensional among growing: 84.5% (labelled), 85.1% (distinct).**
  - No rare class appeared, as expected for classes near 0.1%.
- **Two is typical one size past.**

## 3. The faster-than-power rings (question 2)

The referee grew all 10 that the study's run had read, as far as 60,000 junctions (`referee_touch_rings.json`). It also found 3 more
in the last 100.

| Ring | Rounds | Ratio, last 12 rounds | Exact recurrence found | Base |
| --- | --- | --- | --- | --- |
| four arrangements, each read "6" by the study | 57 | 1.144 → 1.141 | c_t = c_{t−5} + c_{t−6} | 1.1347 (x⁶ = x + 1) |
| (5,5,5,5,5) ring | 18 | 1.619 → 1.618 | c_t = c_{t−1} + c_{t−2} | 1.618 (Fibonacci) |
| (4,4,4,5,5) ring | 33 | 1.250 → 1.268 | c_t = c_{t−1} − c_{t−3} + c_{t−4} + c_{t−5} | 1.2628 |
| (4,4,4,5,5) second ring | 34 | 1.260 → 1.262 | none of order ≤ 6 | ≈ 1.26 |
| three (4,4,5,5,5) / (5,5,5,5,5) rings | 25 | 1.389 → 1.383 | none of order ≤ 6 | ≈ 1.38 |
| three more in the last 100 | 17 to 27 | 1.26, 1.27, 1.51 | not tested | — |

- **Real, not an artefact.** Polynomial growth of degree d has per-round ratio 1 + d/t, which decays.
  - The ring with ratio 1.26 at round 34 would need d ≈ 9. Its ratio would then have been about 1.4 twelve rounds earlier, not 1.26.
  - Four of the sequences satisfy exact integer linear recurrences with a dominant root above 1, over every term checked.
  - So the growth is exponential over the computed range. This is computed, not proved.
- **The two rings of five four-place knots** grow by exactly 5 junctions a round through 80 rounds: one-dimensional, as stated.
- **Fixes.** The note's "multiply by about 1.25 to 1.4" should read 1.13 to 1.62, and "7 rings" should read 13.

## 4. The dimension read-out (question 3)

- **The method.**
  - Per-round junction counts.
  - The dimension is k + 1 for the least k whose k-th differences are constant and nonzero over the last 7 of 30 rounds.
  - Unsettled cases were rerun.
- **Its error on short horizons.** The referee re-read 1,696 arrangements with its own engine at 45 rounds and a 12-round window
  (`referee_touch_sample.json`): every three- and four-dimensional arrangement, every "6" and every unsettled case, all 145 "plus one"
  exceptions, and 1,500 others at random.
  - **Every polynomial or stall reading agrees:** 0 (222), 1 (123), 2 (694), 3 (36), 4 (7), stall (604).
  - The only differences are the 10 exponential rings. The study read them as "6" or left them unsettled; the referee's reader leaves
    them unsettled.
- **The weak spot is d ≥ 5.**
  - At d = 6 the seven-round window compares only two fifth differences.
  - Two equal values happened by chance on the x⁶ = x + 1 rings.
  - A read of 5 or 6 should be treated as "not settled as a polynomial". The note's "a short-window artefact" says this. P3 is
    correctly scored as failed.
- **The "plus one" exceptions** reproduce under the longer horizon. They are computed, not proved, as the note says.

## 5. Other points

- **The forced distinctions.** Testing each start's distinctions by GF(2) (is the unit word in the junctions' span?):
  - 1,746 of the 26,241 arrangements in the study's results file force a distinction in their start, and 1,749 of the 26,341 now read.
  - Exactly the same arrangements force one at the end of growth, so growth never adds one.
  - The note's 1,713 is wrong. **Narrowing (number).**
- **P1 to P6 scoring** is right as stated. Three of eight held, and the failures are honestly recorded.
- **The lemmas (proof.md)** were not re-derived. They are the predecessors' Lemma 2 and FIRST-KNOT's propositions, which the referee
  checked before.

## Fixes for the thread (listed for the owner, not folded in)

1. **The counts.** Fold in the complete census: 13 faster-than-power rings (not 7) and 40 three-dimensional arrangements (not 36),
   with the other rows as in §2. The two-dimensional share is unchanged at 81.7%. **Narrowing (numbers).**
2. **The forced count.** Change 1,713 to 1,746 (on 26,241), or 1,749 on the complete read. **Narrowing (number).**
3. **The rings' base.** Change "1.25 to 1.4" to 1.13 to 1.62, citing the exact recurrences (Fibonacci; x⁶ = x + 1; x⁵ = x⁴ − x² + x + 1).
   Keep "computed, not proved". **Not a block.**
4. **The six-knot sample.** Add that two-dimensional is 84.5% (labelled) and 85.1% (distinct) of growing arrangements, from a sample.
   **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, `arrlib.py`, `job.py` and `merge.py`;
  - wrote `referee_touch.py`:
    - the Burnside count;
    - an enumeration in the study's key format;
    - growth on its FIRST-KNOT-R1 engine;
    - a longer-window dimension reader;
    - a recurrence finder;
    - the missing 100;
    - Metropolis sampling at six knots.
  - It read the study's per-arrangement results from `runs/touch-census/results.jsonl`, as data.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_touch.py`.**
- **`referee_touch_count.json`, `_rings.json`, `_sample.json`, `_missing.json` and `_six.json`.**

Reproduce, from `research/TOUCH-CENSUS-20261118-001/referee-R1/`. The rings take about 36 minutes; the others take under two minutes
each.

```sh
for p in count sample missing six rings; do ../../../.venv/bin/python -B referee_touch.py $p > referee_touch_$p.json; done
```
