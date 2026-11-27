# Recount of the three-knot ring and its carriers

## Round-by-round checks

| Round | Full-search bonds | Every stage law essential | Newest birth essential | Readings in at least two bonds | Local bonds with at most four holders |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | | 0 | |
| 1 | 9 | 3 | 9 | 6 | 9 |
| 2 | 411 | 144 | 330 | 91 | 81 |
| 3 | 9,121 | 234 | 5,974 | 330 | 169 |
| 4 | 44,483 | 0 | 17,444 | 1,060 | 473 |
| 5 | | | | | 803 |

The recount matches every non-timing field of the recorded full search, local search and collapse. Each of the 234
every-law bonds at round 3 has three carriers of size three and misses 111. The birth is essential in all nine
round-1 bonds. The canonical checker finds the same seven allowed words and passes all 27 contact-role assignments,
both on the reading clauses and on the actual stage laws with the agreement definitions and underlying distinctions
quantified away. The frozen check covered nine roles across the three every-law bonds. Signed identification followed
by satisfiability testing reproduces all 76,328 words tested for the 9,541 ring bonds through round 3.
[Full counts](ring_full.json) · [Local counts](ring_local.json) · [Collapse and knot checks](ring_checks.json)

All earlier-state projections agree exactly through round 4. Each old state extends by choosing the private fresh
distinctions to satisfy the newest laws. The 14 round-3 bonds lost at round 4 retain their reading images. Each has the
carrier `(9,11)`, and exactly one new knot `(9,11,13,14)` now determines that reading. All nine round-1 bonds and
all 411 round-2 bonds remain bonds in the next round. [Lost bonds](ring_full.json)

There is a direct finite check for the absence of an every-law bond at round 4. The six freshest distinctions must all
be read. An omitted one has a single holder, and changing it can satisfy that holder's law without changing any
reading. A union of at most nine distinctions containing the six fits inside one of 286 nine-distinction sets.
Projecting before and after every law deletion on each of those sets gives at most six laws that change any one
projection. The stage has ten laws. The check covers arbitrary functions of those at most nine distinctions.
[Projection counts](ring_checks.json)

Three three-place knots in a chain give 16 bonds before growth, each with all three laws essential. One example has
readings `[0=3]`, `[1=5]` and `[2=4=6]`, and misses 001. If 2, 4 and 6 agree, the last knot makes 5 disagree
with them. The first two readings being false then make 1 agree and 0 disagree with them. This forces 3 to agree
with 2 and 4, violating the middle law. Both recorded two-knot controls have zero bonds. The three born three-place
knots of the round-3 chain also give 16 in isolation. [Chains](ring_checks.json)

## Corrections and limits

- **Not a block.** Replace “507 bonds, 96 of them with a carrier of four” in [the decision](../decision.md)
  with “636 bonds, 225 of them with a genuine carrier of four.” The original function tested equality of the first
  three distinctions for every carrier of four. All 96 padded results reduce to ordinary bonds already in the
  three-place search. Every corrected result still misses one word. Of the corrected 225, 195 depend on every one of
  the four distinctions of their long carrier on the actual allowed states. The flip-unchanged swap reproduces
  9 and 5,556 bonds at rounds 1 and 2. [Swap recount](ring_swaps.json)
- **Not a block.** Replace “The search would have reported any bond whose readings fail only that test, and none is
  counted” in [the decision](../decision.md) with “The search
  excludes readings determined by a single knot before checking the joint image.” Including them finds 8, 53, 485,
  2,451 and 7,153 additional pair-free constrained tuples at rounds 0 through 4. [Full counts](ring_full.json)
- **Narrowing.** The two holder tests give different claims. At rounds 2 and 3, 54 local bonds at each round have
  valid holder sets beyond those recovered by asking whether the whole-stage essential laws themselves qualify.
  At rounds 2, 3 and 4 there are 174, 6,660 and 38,230 full-search bonds with a carrier outside those essential laws'
  distinctions. The readings in these rounds all depend on every one of their named carrier places on the stage.
  Requiring every carrier to meet every knot in at most one place leaves zero ring bonds in the full and local
  rounds read and zero in the three-knot chain. Qualify “held by the whole” in the [object entry](../../../docs/OBJECTS.md)
  and “recurs: at every round of the ring” in the [decision](../decision.md#on-the-owners-rungs). Specify the
  connected-holder result and its rounds when every law of the chosen holders is essential.
  [Full counts](ring_full.json) · [Local counts](ring_local.json)
- **Narrowing if the explanation is meant to cover all cases.** P3.4's existence test holds. Of 306 and 330
  newest-holder bonds at rounds 4 and 5, respectively 54 and 90 have a valid holder set that uses only joins among
  the newest births. A one-input birth can write the complement of two agreeing fresh distinctions. A join permits
  more than one input pattern under the same condition. Specify the one-input case when repeating the explanation
  in [P3.4](../README.md#frozen-predictions). [Join witnesses](ring_local.json)

The seven frozen digests match commit `8df7206b94`. The closing commit `f027d7d3e9` records changes to the schedule,
partial-save behavior and deviations. The main ring search and reading implementation are identical to their frozen
versions. The published rounds 0–3 totals, every-law totals and single-word exclusions were already known before
freezing. P3.3 can fail at round 1, with 27 reading uses and 34 eligible readings. At rounds 2–4 some reading must
repeat once the full-search totals are known. [Frozen predictions](../README.md#frozen-predictions) · [Counts](ring_full.json)

## Replay

The main recount uses packed integer state masks. A bounded set of allowed states screens for words that occur.
Every unresolved word is decided using the full allowed-state mask. For essentiality, a separate mask is kept for
states violating exactly the law being removed. For local checks, the independent whole-stage comparison solves
clauses defining the readings and checks each knot's feasible value patterns. Stage construction borrows the earlier
[growth rule](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py). The growth check here tries each subset of
live knots to reconstruct the meeting groups and repeats that test on the provisional births to find their demand
for fresh distinctions. It agrees on ordered parents, inputs, demand and fresh distinctions for all 11 births
through round 5. The supports also match the earlier archived ring through round 4 and the recorded knot counts
through round 5. [Growth comparison](ring_growth.json)

From the repository root, run each phase in order. The growth pilot replays its first two rounds. It took 0.07 seconds
and the full growth check took 0.07 seconds with peak resident memory 36,024 KiB. The full-search pilot checks its
first 24 readings at round 4. It took 1.82 seconds. The full recount finished in 7.70 seconds with peak resident
memory 123,608 KiB. Each other full phase finished in at most 2.12 seconds.

```sh
ulimit -v 2621440
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ring_dir=research/RING-BOND-20261127-001/referee-R1
for phase in growth swaps checks local full
do
    .venv/bin/python -B "$ring_dir/ring_verify.py" --part "$phase" --pilot >/dev/null || exit
    .venv/bin/python -B "$ring_dir/ring_verify.py" --part "$phase" --out "$ring_dir/ring_$phase.json" || exit
done
```

## What was not run

This recount stops full enumeration at round 4, growth at round 5 and the collapse check at round 3. It checks the
four-place swap at round 2 and local searches with up to four holders. The symmetry replay follows later growth
separately. The census, parity and layer above also have separate counts.
