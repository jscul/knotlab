# Is distance the only form of information: pre-registration

Epic `DISTANCE-INFO-20261117-001` (challenges assumption A97, the owner's reading; goals G1 and G16), 17 November 2026. Frozen
before any read-out. The code (`tables.py`, `census.py` in
`experiments/DISTANCE-INFO-20261117-001A/DISTANCE-INFO-20261117-001A-E001_tables/`) was written first and run only on settled
single-knot cases and on timing and counting checks (relation counts 16, 1,023, 97,248 at n = 4, 5, 6); no bond-distance table of a
registered relation was compared with another. Code and run by this thread. The canonical K1–K3 test is unchanged.

## What is tested, and what "distance" means

The owner (17 November): "Distance is the only form of information. That's the entire basis of the 'this versus that' distinction
in the smallest emergent unit." Recorded as A97, an interpretation.

**Distance** here is the program's **bond distance**, read from the allowed states alone (glossary): a bond is a set of at least two
distinctions on which the allowed states, all others forgotten, form a knot (not every joint state occurs; forgetting any one member
leaves the rest free); the bond distance of two distinctions is the size of the smallest bond holding both, minus one, or infinite.
It is not steps apart. That matters after `SPACE-ORDER-20261117-001`'s referee: there the untangling phases followed the weave's
local overlap structure, not steps apart, and that study's withdrawn headline is no evidence for or against A97. This test does not
use it.

**Bases**: not-all-equal knot patterns on n labelled distinctions that allow some state; every relation is closed under flipping
all values. All relations at n = 4, 5, 6 (16, 1,023, 97,248); at n = 7, relations of 400,000 random knot sets (1 to 12 knots).
For n ≤ 7 distinct satisfiable knot sets give distinct relations (advisor: a state with a = b = c = 0 and every other knot
satisfied breaks only knot abc), so the census asks whether a reading recovers the knots.

**Readings**, each a candidate for "the distance information" of a base:
- (a) the unsigned pairwise bond-distance table, A97's plain reading;
- (b) the signed table: size-two bonds (tied pairs) marked equal or unequal;
- (c) the bond set (every bond, not only the smallest per pair): distance between sets;
- (c-s) the bond set with the sign of each tie;
- (c′) every bond with its missing joint states: signed set-distance;
- (d) the prime implicates (minimal forbidden partial states), a control that determines the relation by theorem.

**What each outcome would mean, stated before running.**
- If (a) determines the relation (no two relations share a table), pairwise distance carries everything the allowed states hold in
  this range, which would support A97 in its plain reading.
- If (a) collides but (b) or (c) does not, A97 survives only if distance includes the sign of a tie ("same versus opposite") or
  distances between sets.
- If only (c′) separates relations, A97 survives only as "signed set-distance", which is close to restating the relation by its
  forbidden states.
- If even (c′) collides, some information lives on sets that already contain a smaller bond, and nothing distance-like in this
  definition sees it, which would challenge A97 itself.

## Prior work in the program

`python3 -B scripts/track.py objects "bond distance table determines allowed states" --until 2026-11-17 --exclude DISTANCE-INFO-20261117-001`

`python3 -B scripts/track.py objects "equal pair counts equal states not-all-equal small patterns" --until 2026-11-17 --exclude DISTANCE-INFO-20261117-001`

`python3 -B scripts/track.py objects "least bond pairs relation census not-all-equal" --until 2026-11-17 --exclude DISTANCE-INFO-20261117-001`

- `JOINT-BRAID-READS-20261114-001`: unrelated (crossing queries; matched on "states").
- `BRANCH-DEPTH-20261112-001`: a relative (least bonds of bounded size on a repeating branch); bond sizes, not whether they determine
  the relation.
- `JOINT-RECORDS-20261116-001`: a relative (seam reports of not-all-equal patterns determined by their two- and three-place
  shadows): the projection hierarchy this census's readings sit in.
- `PARITY-SURVIVE-20261112-001`, `PARITY-MIX-20261112-001`: unrelated (parity placements among stitched copies).
- `RANDOM-FATES-20261112-001`: a relative (least bond d + 2 for patterns without cycles).
- `KNOTS-ALONE-20261111-001`: a relative (bond distance against steps apart on weaves).
- `REACH-CENSUS-20261113-001`: unrelated (first-ray bonds in nested families).
- `OVERLAP-READ-20261111-001` (named in A97): equal pair counts give equal states; the pattern-to-relation direction, where this
  census asks relation-to-distance.

## Prior work outside the program

Bonds are the minimal non-shattered sets, so the bond set is the shattered-set complex sh(R); sh does not determine R in general
(sh(R ⊕ a) = sh(R) for every translate a), and Pajor's lemma |sh(F)| ≥ |F| makes the extremal (lopsided) families those with
equality (Pajor 1985; Lawrence 1983; Bollobás, Leader and Radcliffe 1989; Bollobás and Radcliffe 1995; Anstee, Rónyai and Sali
2002; Bandelt, Chepoi, Dress and Koolen 2006; Moran 2012). A relation is not determined by its binary projections (Montanari 1974,
minimal networks); its prime implicates (Blake; Quine) determine it.

## Predictions (frozen; the advisor's, hand-checked by it)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | (d) has no collision wherever computed; the run completes | any fails |
| D1 | (a) collides already at n = 4: 12 distinct tables for the 16 relations (the four three-knot relations and the four-knot relation share the all-2 table, 8 against 6 allowed states, not isomorphic) | otherwise |
| D2 | (b) collides at n = 4 with the same groups; (b) first separates more than (a) at n = 5 | otherwise |
| D3 | (c) has no collision at n = 4 and collides at n = 5 (three mutually tied distinctions whose odd one is lost; the colliding relations isomorphic) | otherwise |
| D4 | (c-s) has no collision at n = 5 and some at n = 6 or 7 (a guess) | otherwise |
| D5 | (c′) has no collision at n ≤ 6 (moderate confidence) | a collision at n ≤ 6 |

## Runs and stop rule

One script, `census.py`, four processes, expected under ten minutes. The study stops after its read-out; then A97's status (kept
Assumed, narrowed, or challenged), the decision note, the referee hand-off and the report.

The advisor model (`claude -p --model claude-fable-5-2`) was consulted before this freeze. It found, by hand, the collisions behind
D1 and D3, proposed readings (c′) and (d), the isomorphism tag, the remark that relations here are knot sets, the literature above,
and the four readings of the outcome.
