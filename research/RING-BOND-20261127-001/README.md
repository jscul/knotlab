# The grown ring's bond: chosen or selected, a knot, and does it iterate?


> **Referee R1: refuted, one Block** ([report](referee-R1/report.md); notice in [decision.md](decision.md)). Bonds bind again
> one layer up: eight lower bonds bind three upper agreements on a closed twelve-knot start, and on the grown ring with
> overlapping carriers. The local holder check kept only the first shortest holder (a narrowing under parity).
`RING-BOND-20261127-001`, opened on the coordinator's go-ahead after the not-all-equal layer's referee
(`NAE-LAYER-20261127-001`, report R1) found what the study and the advisor had both predicted would not exist. The census's
three-knot ring (0,1,3), (1,2,4), (2,0,5) grows one birth (3,4,5,6), and three agreement readings on disjoint carriers,
[1=5], [2=3] and [0=4=6], take seven of eight triples and need all four laws. There are three such choices, one for each
pair that receives the fresh distinction 6. The questions:

1. Does anything in the growth single out one of the three choices, or is the choice ours (a scaffold)?
2. Does the bond pass the knot test with the readings as its distinctions? Is any reading read at a single knot?
3. Does it iterate? After further rounds, do such bonds share readings and bind one layer up, and does this happen on
   sampled starts as well as on the ring?
4. The same search under parity, with carriers that take in shared distinctions.

## Definitions (`ringbond.py`)

A **reading** is a function of a **carrier** of two or three distinctions that is unchanged when every place flips, uses
every place, and is not constant on the allowed states. The class used is the agreement [all the carrier's distinctions
equal]. A reading is **read at a knot** when, on the allowed states, it is a function of that knot's values.

A **bond** is three readings on pairwise disjoint carriers, with four conditions: none is read at any knot; every two
take all four pairs of values; the three together miss at least one of the eight triples. Two notions of what holds it:

- **Full search** (`bonds`) runs on the whole stage. A law is *essential* when removing it from the stage lets a missing
  triple occur.
- **Local search** (`local_bonds`) uses a connected set H of at most M knots as the bond's holders, with the carriers in
  H's distinctions. On H's laws alone every law of H is essential and no reading is read at a knot of H. A solver then
  checks the whole stage [R1: only the first shortest holder for each carrier triple; the existential definition needs every candidate]: it gives the same missing triples, every other triple occurs, and no reading is read at any
  knot. Every full-search bond whose essential laws form a connected set of at most M knots, hold the relation alone and
  contain its carriers is found locally. That was checked on rounds 1 to 3 of the ring, and the local search found
  nothing the full search lacks.

**The layer above** (`layer2.py`). Take bonds as laws on their readings, each forbidding its missing triples. A
**cluster** is a connected set of at most three bonds that share readings, with its readings on pairwise disjoint
carriers. A bond of the layer above is a bond on the cluster's own system whose readings are agreements of two or three
of the cluster's readings, with every bond of the cluster essential and no reading read at a single bond. L2 compares the
readings' joint image on the stage (J) with what the cluster's bonds allow (conj).

## Explored before freezing (not evidence for the predictions below)

| What | Seen |
| --- | --- |
| Full search on the ring, rounds 0–3 | 0, 9, 411 and 9,121 bonds; with every law essential, 0, 3, 144 and 234; every bond misses one triple |
| Local search against the full search, rounds 1–3 | agreement as stated above |
| Layer above at round 1, overlap allowed | 70 clusters, no bond of the layer above; J smaller than conj in all (overlapping readings are related on the stage) |
| Layer above at round 2, disjoint carriers | 24 clusters, all of two bonds; tallies not read |
| Census pilot, 10 starts (seed 1, excluded below), holders ≤ 4 | not-all-equal: round-0 bonds on 3 of 10 starts, new round-1 bonds on 5 of 8 funded, every bond missing one triple; parity: many bonds, shapes 222 missing 4, 223 missing 2, 233 missing 1 or 3, 333 missing 1, 2 or 3, all with a six-distinction sum of laws |
| Advisor (hivemind 2026-11-27, committed bda2216350) | its predictions are copied below where they are used |

## Frozen predictions

Predictions marked (A) are the advisor's. Each is checked by the named script, and the scripts are frozen with this
file.

**Q1, chosen or selected** (`symmetry.py`)
- P1.1 At rounds 0 to 5, all six renamings of the start's three knots (identity on every later distinction) map the stage
  onto itself.
- P1.2 At rounds 1 to 3 the image of every bond under each renaming is a bond. The three round-1 bonds with every law
  essential form one orbit of size three, and no bond at rounds 1 to 3 is fixed by all six renamings.
- P1.3 Three seeded relabellings of the start, with a shuffled knot order, grow stages isomorphic to the relabelled
  growth through round 3.
- P1.4 (A) A choice-free reading. Read the three opposite pairs (1,5), (2,3) and (0,4) as three-valued: apart, agree
  with 6, or agree against 6. At round 1 they take 16 of 27 triples, and 19 with the birth's law removed. Mine: removing
  any one of the four laws adds triples, every two of the three readings take all nine pairs (so the three-valued
  relation passes K1 to K3), and the relation is unchanged by every renaming.

**Q2, the knot test** (`ring.py`, `collapse.py`)
- P2.1 The knot checker passes the clause of each round-1 bond with every law essential, with each reading in turn as
  the contact.
- P2.2 The birth's law is essential in every round-1 bond (the start alone has none, as already seen).
- P2.3 (A) The collapse rule agrees with the bond search on every bond. A triple is missing exactly when the system
  stated in `collapse.py` has no state. This covers rounds 1 to 3 of the ring and the round-0 and round-1 bonds of
  census starts 0 to 199, under both laws.

**Q3, iteration** (`ring.py`, `layer2.py`, `census_bonds.py nae`)
- P3.1 (A) On the ring, every one of the 234 round-3 bonds with every law essential has three carriers of three and
  misses 111. At round 4 no bond has every law essential (with every law essential, laws ≥ merged distinctions, after
  Seymour 1974).
- P3.2 Every bond of round t−1 is a bond of round t with the same missing triples, for t = 2, 3 and 4.
- P3.3 Some readings lie in two or more bonds at every round from 1 to 4.
- P3.4 (A) Local search at rounds 4 and 5 (holders ≤ 4) finds bonds with a newest birth among the holders. The
  mechanism is no new layer: a birth whose two fresh distinctions agree writes the other value on its input.
- P3.5 (A) The layer above has no bond on any cluster at round 1 or 2, with disjoint carriers. This holds also at round
  2 with overlapping readings allowed, as far as that run gets in 20 minutes.
- P3.6 L2 is read with no prediction.
- P3.7 Census, a held-out sample of 1,000 starts (seed 20261127, the 10 pilot starts excluded), not-all-equal, holders
  ≤ 4:
  - (a) between 10% and 50% of the starts have a bond at round 0;
  - (b) at least 30% of the funded starts have a round-1 bond with a birth among the holders;
  - (c) every bond meets the count bound in `census_bonds.py`;
  - (d) every bond misses exactly one triple, so not-all-equal's bonds are single clauses ("or" laws), never a
    not-all-equal relation on three readings.

**Q4, parity** (`census_bonds.py parity`, the same sample)
- P4.1 (A) Every bond has a sum of its holders' laws holding exactly two distinctions of each carrier.
- P4.2 (A) 111 (all agree) is never missing.
- P4.3 Missing counts by carrier shape: 222 missing 4, 223 missing 2, 233 missing 1 or 3, 333 missing 1, 2 or 3. The
  advisor's "7 of 8 with two carriers of three, nothing from three" is already contradicted by the pilot.
- P4.4 (A) The ring under parity grows one round and has no bond at rounds 0 and 1.
- Proved (no run needed). Under parity the allowed states form a linear space. Each agreement reading is the indicator
  of a subspace cut out by its carrier's pair sums. So which triples occur is fixed by the linear dependences, on the
  allowed states, among the carriers' pair sums. Those dependences are the sums of the laws. Every parity bond is
  therefore a consequence of sums of laws read through agreements, the class facts' "start's sum of laws" again.

## Scaffolds (each recorded in docs/ASSUMPTIONS.md) and their swaps

| Scaffold | Swap run |
| --- | --- |
| The reading class (agreements) | all readings unchanged by a global flip, rounds 1 and 2 of the ring (`ring.py`) |
| The carrier cap (three) | carriers up to four, round 2 (`ring.py`) |
| The holder notion (whole-stage essential against connected holders ≤ M) | both on the ring; on the census M = 4, with M = 5 on the first 100 sampled starts |
| Bonds as laws of a layer above, disjoint carriers | overlap allowed (`layer2.py --overlap`) |
| The census sample | seeded, held out from the pilot |

## Compute

The census runs at about 3 s a start under not-all-equal and 5 s under parity (pilot), so 1,000 starts each in 6 and 8
chunks takes about 10 to 15 minutes. The ring's round-4 full search, the layer above and the collapse check take
minutes each. Each run has a memory cap (MemoryMax 6G) and a 30-minute stop. Anything that stops is reported as not run.

## Deviations (process only; recorded after the freeze)

- The first launch ran numpy with many threads per process and overloaded the machine. It was stopped after about five
  minutes, before any result was read, and relaunched with one thread per process.
- `symmetry.py` ran the bond search at rounds 4 and 5, which P1.2 does not ask for and the search cannot hold (27
  distinctions). It was changed to read bonds at rounds 1 to 3 only, as frozen, and rerun. P1.3 was compared at round
  5, past the frozen round 3.
- `collapse.py` was changed to save after every start and relaunched. Under parity it was stopped at census start 5 to
  close the study, so starts 6 to 199 are not run.
- The holder-cap swap read every tenth sampled start (100 starts), not the first 100.
- At the 30-minute stop, the parity census had read 179 of 1,000 starts; 821 are not run. The layer above with overlap
  had read round 1; round 2 is not run.

## Results

`decision.md`, with the tallies in `out/tally.json` and post-hoc checks in `post/`.
