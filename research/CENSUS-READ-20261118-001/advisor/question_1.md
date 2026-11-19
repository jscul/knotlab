Colleague check before I freeze a census study. Under 450 words. Which of C1-C6 would you bet against, and why? Anything I must add
to classify misreads well (one or two concrete splits)? Anything wrong in "settled by construction"?

Background: RING-READ-20261118-001 read one cheapest-count parity ring back from its bond-distance table alone with an incremental
reader R3 (keep read junctions; at stage s set aside short pairs lying in supports of connected sums of read junctions, up to s of
them, running support <= s + 2, unless one read junction holds both; new junctions = maximal cliques of <= s distinctions not in
the GF(2) span of the read ones and meeting each read one in at most one distinction). Exact at rounds 10-25; least horizon =
largest junction - 1; the junction graph with the outside vertex 3-connected; R3 stays exact when stages run three past the largest
junction. The census: 26,441 connected arrangements of up to five parity knots of 3-5 places (pairs may share several
distinctions), grown under the cheapest counts; 41.6% stall in round 1, 14.1% close, most of the rest grow two-dimensionally.

The frozen design follows.

# Does the new distance reader read every growing census arrangement? Pre-registration

Epic `CENSUS-READ-20261118-001` (`RING-READ-20261118-001#1`, the coordinator's go-ahead; goals G1 and G17; assumption A97),
2026-11-18. Code by the thread (`job.py` for the shared runner), launched by the thread. Frozen before any case is run. The
canonical K1–K3 test is unchanged.

## The question

`RING-READ-20261118-001` read one ring back from its bond distances alone, to round 25, with the incremental reader R3, which
needed distances exactly as far as the largest junction less one. Is that the ring or the law? Run R3, unchanged, on every stage of
every arrangement of the cheapest-count census (`TOUCH-CENSUS-20261118-001`, 26,441 arrangements of up to five touching parity knots
of three to five places, all regrown here, including the last 100 the census itself never read), and on the 247 mixed-count stages
of `FRESH-COUNT-20261118-001` on which its threshold reader misread 47. Ask what is typical: how many stages read exactly, what the
misreads share, and whether "how far you must look is set by how big the knots are" holds across the census, where Codex's
`VARIABLE-OUTPUT-READER-20261118-001H` family has a fixed cutoff of five under its own law.

## In standard terms

For each grown presentation, the junction graph with an outside vertex; the input is the matrix of smallest-bond sizes through
pairs of edges, truncated at H; the readers output a set of vertex stars. The quantities: the fraction of presentations read
exactly, the classes of failure, and the least truncation h at which reading still succeeds, against the largest star size.

## Prior work in the program

`python3 -B scripts/track.py objects "distance reader every census arrangement junctions read back from bond distances" --until 2026-11-18 --exclude CENSUS-READ-20261118-001`

- `RING-READ-20261118-001`: the reader under test (same object, one ring); this study changes only the population.
- `FRESH-COUNT-20261118-001`: a relative and one population here: its threshold reader on stages of at most 21 junctions,
  exact on one count, one round early on the 2^a pattern, 47 misreads of 247 mixed stages. Those 247 stages are replayed from their
  seeds and read by both readers.
- `TOUCH-CENSUS-20261118-001`: the same population (its arrangements and growth rule); it measured dimension, never distances.

`python3 -B scripts/track.py objects "graph reconstruction from smallest bonds through pairs of edges horizon" --until 2026-11-18 --exclude CENSUS-READ-20261118-001`

- `RING-READ-20261118-001`: as above.
- `RANDOM-FATES-20261112-001`: unrelated (endings of not-all-equal growth).
- `MISSING-KNOTS-20261112-001`: a distant relative (least bond through two distinctions against missing knots, not-all-equal
  weaves); nothing read back.

`python3 -B scripts/track.py objects "touching parity knots arrangements up to five knots cheapest counts census" --until 2026-11-18 --exclude CENSUS-READ-20261118-001`

- `TOUCH-CENSUS-20261118-001`: the same population.
- `PLUS-ONE-20261118-001`: same population, another measure (when chains born apart combine).
- `FIRST-KNOT-20261118-001`: a relative (the rule reads open distinctions; the same relation grows differently by presentation).

Also read for scope: `BOND-NEXT-JOIN-20261117-001` (the reader to six) and Codex's `VARIABLE-OUTPUT-READER-20261118-001A` to
`-001H` (the other law; `-001H`: distance five enough and sharp on a three-dimensional family, and a cycle of four-place junctions
whose six distinctions look like one equation that is not there).

## Prior work outside the program

Whitney's 2-isomorphism theorem (1933); cited once in `RING-READ-20261118-001`. Nothing further searched.

## Disclosed before the freeze

- After `RING-READ-20261118-001` closed, I checked on the ring (rounds 10, 15, 20) whether R3 needs to be told the largest
  junction size: with tables exact one, two and three past it and stages run that far, R3 stayed exact. So here the table is cut at
  H = largest + 2 and R3 runs every stage the table allows.
- Timing only, on 12 arrangements and one mixed seed (no verdict read): 0.54 seconds per arrangement on average.

## Settled by construction (stated, not tested)

- An outside swap (the truth with one junction J replaced by the set L of all loose distinctions) has the same allowed states and
  so the same table (`RING-READ-20261118-001`); no table can tell it from the truth, and it is classed separately, not as a misread.
- R3 refuses a new clique meeting a known junction in two or more distinctions. Census starts may share two or more distinctions
  between two knots, so R3 can fail there by construction of its filter; R3m drops the filter.
- A stage whose largest junction has all its pairs at their own size less one cannot be read below horizon (largest − 1) by these
  readers; a smaller least horizon means some pairs of the largest junction lie in smaller bonds.

## Definitions

- Stages: for each arrangement, round 0 (the start) and each later round, under the census's growth (`S.gf2(F.fewest)`), up to
  round 8, stopping before a stage of more than 120 junctions, at a stall or at closing. Mixed stages: FRESH-COUNT's
  `reader_mixed` replayed (60 seeds, up to six stages of at most 16 junctions each).
- Table: exact bond distances up to H = largest + 2 over bonds with a side of at most min(junctions, 6) junctions (complete at 14
  or fewer junctions), pooled above.
- Readers: R1 (BOND-NEXT-JOIN's stages run on to H + 1), R3 (RING-READ-20261118-001B's `reader3.r3`, hash-checked, run to H + 1),
  R3m (R3 without the two-shared filter), and on mixed stages FRESH-COUNT's `bonds.read_stars`.
- Verdicts: exact, outside swap, misread. Least horizon: the least h with R3 (or R3m) exact on the table pooled above h, stages to
  h + 1, scanning down from H − 1.
- "Shares two": some two junctions of the stage share two or more distinctions.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| C0 | Gate: (a) FRESH-COUNT's reader, replayed, misreads exactly 47 of 247 mixed stages; (b) on 300 census stages of at most 18 junctions (every 20th stage in case order), the table equals the brute-force bond table of `RING-READ-20261118-001A`'s check.py; (c) R3 here reproduces RING-READ at ring rounds 10 and 15 | any fails |
| C1 | R3's output is exact or an outside swap at every census stage where no two junctions share two distinctions | one misread there |
| C2 | Where two junctions share two or more distinctions, R3 misreads at some stage of most such arrangements, and R3m is exact or an outside swap at every census stage | R3m misreads a stage |
| C3 | Outside swaps occur only at stages whose loose set L has at most as many distinctions as the largest junction | a swap with a larger L |
| C4 | At every stage R3 reads exactly, its least horizon is exactly largest − 1 ("set by how big the knots are") | some stage needs less or more |
| C5 | R3 reads every one of the 247 mixed stages exactly or as an outside swap, including the 47 that FRESH-COUNT's reader misread | a mixed misread |
| C6 | R1 (the old reader run on) misreads at some stage in at least a tenth of the arrangements that grow past round 3 | fewer |

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 529 census shards of 50 arrangements and 60 mixed seeds; 12 workers, case timeout 900 seconds,
1G per case, MemoryMax 14G; expected about 20 minutes, registered in the long-running index. Readout by `readout.py` into
`artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/summary.json`. The gate C0(b) is run by `gate.py`.
The study stops after one run and the readout; misreads are classified (what they share) and reported, not chased with a new reader
in this study. Advisor before the freeze: below.
