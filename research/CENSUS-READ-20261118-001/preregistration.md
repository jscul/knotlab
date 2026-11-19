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

- The table is a function of the allowed states. Any presentation with the same allowed states has the same table, so no reader
  can tell them apart: an outside swap (the truth with one junction J replaced by the set L of all loose distinctions), and, where
  the junction graph with the outside vertex is not 3-connected, a Whitney twist at a 2-separation (two junctions change, neither
  becomes L). Outputs with the same allowed states as the truth are classed apart from misreads ("same states", with outside swaps
  counted separately). Only at 3-connected stages does Whitney's theorem leave the outside swap as the only alternative.
- R3 refuses a new clique meeting a known junction in two or more distinctions. Census starts may share two or more distinctions
  between two knots, so R3 can fail there by construction of its filter; R3m drops the filter.
- R3 runs stages to H + 1 = largest + 3, so an outside swap can be found when L has up to largest + 3 distinctions; its L-size is
  recorded, not predicted.
- A smaller least horizon than largest − 1 means some pairs of the largest junction lie in smaller bonds (or its star is not a
  bond, at a cut vertex).

## Definitions

- Stages: for each arrangement, round 0 (the start) and each later round, under the census's growth (`S.gf2(F.fewest)`), up to
  round 8, stopping before a stage of more than 120 junctions, at a stall or at closing. Mixed stages: FRESH-COUNT's
  `reader_mixed` replayed (60 seeds, up to six stages of at most 16 junctions each).
- Table: exact bond distances up to H = largest + 2 over bonds with a side of at most min(junctions, 6) junctions (complete at 14
  or fewer junctions), pooled above.
- Readers: R1 (BOND-NEXT-JOIN's stages run on to H + 1), R3 (RING-READ-20261118-001B's `reader3.r3`, hash-checked, run to H + 1),
  R3m (R3 without the two-shared filter), and on mixed stages FRESH-COUNT's `bonds.read_stars`.
- Verdicts: exact, outside swap, same states (another presentation of the same allowed states: the output junctions span the
  same parity space as the truth's), misread (different allowed states). Each stage is tagged by the vertex connectivity of its
  junction graph with the outside vertex (three, two, one, zero when nothing is loose, small) and by whether its table is complete
  (at most 14 junctions). Horizons: R3's (and R3m's) verdict at every h from H − 1 down to 1 (table pooled above h, stages to
  h + 1); the least horizon is the least h with every larger h exact, and non-monotone stages are counted.
- Rigid stage: 3-connected, and no two junctions share two distinctions (RING-READ's setting).
- "Shares two": some two junctions of the stage share two or more distinctions.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| C0 | Gate: (a) FRESH-COUNT's reader, replayed, misreads exactly 47 of 247 mixed stages; (b) on 300 census stages of 6 to 16 junctions (every 7th such stage in arrangement order), the table equals the brute-force bond table of `RING-READ-20261118-001A`'s check.py; (b′) on 200 stages of 30 to 120 junctions (every 25th such stage), the tables at sides of 6 and 8 junctions agree; (c) R3 here reproduces RING-READ at ring rounds 10 and 15 | any fails |
| C1 | At every rigid census stage, R3 is exact or an outside swap | another verdict at a rigid stage |
| C1b | At every census stage where no two junctions share two distinctions, R3's output has the truth's allowed states (exact, outside swap or same states) | a misread there |
| C2 | Where two junctions share two or more distinctions, R3 misreads at some stage of most such arrangements; R3m has the truth's allowed states at every census stage | R3m misreads a stage, or R3 misreads in at most half of them |
| C3 | At 3-connected stages, R3 never returns same states other than an outside swap | a non-swap same-state output at a 3-connected stage |
| C4 | At every rigid stage R3 reads exactly, its least horizon is exactly largest − 1 ("set by how big the knots are") | some rigid stage needs less or more |
| C5 | R3 has the truth's allowed states on every one of the 247 mixed stages, including the 47 FRESH-COUNT's reader misread | a mixed misread |
| C6 | R1 (the old reader run on) misreads at some stage in at least a tenth of the arrangements that grow past round 3 | fewer |

The least horizon at every exactly read stage, rigid or not, and its relation to the largest junction, is reported as measured.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage` names
claude-fable-5-2). It found my first "settled by construction" incomplete: at stages that are not 3-connected a Whitney twist gives
another presentation with the same table, which no reader can see, so my first C1 ("exact or outside swap everywhere") would fail
for any reader. Taken: the same-states class by rank, connectivity and table-completeness tags, C1 restated at rigid stages, C1b
and C3 added, the horizon recorded at every h (exactness need not be monotone), and the swap's L-size recorded instead of
predicted. It bet against C1 (as first written), C4 and C3.

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 529 census shards of 50 arrangements and 60 mixed seeds; 12 workers, case timeout 900 seconds,
1G per case, MemoryMax 14G; expected about 20 minutes, registered in the long-running index. Readout by `readout.py` into
`artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/summary.json`. The gate C0(b) is run by `gate.py`.
The study stops after one run and the readout; misreads are classified (what they share) and reported, not chased with a new reader
in this study. Advisor before the freeze: below.

## Amendment 1, before the readout (2026-11-19)

Written while the run was under way and before any case was read, after the RING-READ referee found that side-limited tables miss
cuts that wrap a ring (`RING-READ-20261118-001/referee-R1/report.md`). Two additions, no prediction changed:
- **Exact-table sensitivity (C7).** `exact_table.py` builds the table with no limit on either side's size (the referee's method,
  include/exclude growth of connected sides with a max-flow cut, written afresh), validated by `validate_exact.py` against the
  referee's six wrong entries at ring round 25. It is run on (a) every census stage of more than 14 junctions where R3 or R3m is not
  exact, and (b) every 50th census stage of more than 14 junctions where both are exact (in arrangement order), and R3 and R3m are
  rerun on it. **C7: on every such stage the exact table equals the side-limited one at every distance up to the largest junction
  less one, and no verdict of R3 or R3m changes.** Fails when an entry differs inside that range or a verdict changes. Stages of 14 or
  fewer junctions already have complete tables.
- **Timeouts.** A shard that times out three times (900 seconds each) is rerun one arrangement per case with a 3,600-second limit
  (`job_single.py`, same functions), so the census stays complete.
