# Bond distances at the attachments

The attached starts have smaller bond balls around the original path distinctions next to a seam. The effect is weaker far from the seam. J0, J1, J2 and the funded cut control C1 have the same individual ball cardinalities at all 16 original path distinctions, at radii one through five, across their common rounds zero through six. P3 and the near–far part of P4 hold in the measured panel. The larger effect predicted for J2 is absent at these radii.

## Matched original path distinctions

At the source, each singly attached start and C1 lengthens 62 of the 120 unordered original path pairs compared with B. The increases are 2 for 14 pairs, 4 for one, 6 for 14, and 8 for 33. The other 58 pairs agree with B. T4 and T8 lengthen 95 and 99 pairs, respectively, with increases up to 16. The first complete round gives the same 62 changed pairs for J0, J1, J2 and C1, now with increases of 2 for 14 pairs, 4 for one, and 6 for 47. These four starts have identical pair tables at both rounds. All 840 source pair values agree with the independent source calculation. [Source formula and check](source_bonds.md)

The table gives mean changes from B in ball cardinality at the same radius and cluster size. Every mark has equal weight. Single-seam starts have two near and ten far marks, T4 has four near and six far, and T8 has four near and four far. Every planned value is exact. At radii one and two all matched changes are zero.

| Starts and rounds | Full near, radii 3, 4, 5 | Full far, radii 3, 4, 5 | Restricted near, radii 3, 4, 5 | Restricted far, radii 3, 4, 5 |
| --- | --- | --- | --- | --- |
| All attachments and C1, source | −6, −6, −7 | 0, 0, 0 | −2, −2, −3 | 0, 0, 0 |
| J0, J1, J2, C1, positive rounds | −6, −6, −17 | 0, 0, −3/5 | −2, −2, −3 | 0, 0, 0 |
| T4, positive rounds | −6, −6, −17 | 0, 0, −1 | −2, −2, −3 | 0, 0, 0 |
| T8, positive rounds | −6, −6, −17 | 0, 0, −3 | −2, −2, −3 | 0, 0, 0 |

For a single seam, the full radius-five loss by offset at positive rounds is 17, 8, 8 and 3 at offsets zero through three, then zero. The restricted radius-five losses are 3, 1 and 1 at offsets zero through two, then zero. At offset one in T4, two full radius-five losses are 14 and two are 8. The corresponding restricted losses are 2 and 1, respectively. T8 has full losses of 8 and restricted losses of 1 at each offset-one mark. These are differences between the tested placements.

The changes relative to B are identical at every individual mark from the first round through each case's measured cap. Absolute ball cardinalities can still change. For example, at the round from one to two the full radius-five ball at each of the two outermost path marks gains six distinctions in every case. The restricted effects establish a change among the matched historical distinctions. The common result with J0 and C1 shows that neither decoration nor a ring return is needed for the measured path effect. The funding convention changes loose counts locally when attaching the added part.

The two doubles reach the time cap for unrestricted exact rows at round one. The cutoff still decides 19 of their 120 matched pair comparisons at every positive measured round, including four increases of 2. For J0, J1, J2 and C1 from round two, 24 of the 120 pair comparisons are exact, including two increases of 2. The retained cutoff certifies ball membership for all marks even where an individual distance exceeds five. For the longer distances, the record gives lower bounds and the source and round-one values where available.

## Original ring distinctions

Both original ring marks have smaller full radius-five balls after attachment than at the corresponding isolated ring. Each entry gives the isolated and attached counts in that order. The positive-round values hold through the common measured cap of the corresponding pair.

| Mark | Source, R0 and J0 | Positive rounds, R0 and J0 | Source, R1 and J1 | Positive rounds, R1 and J1 | Source, R2 and J2 | Positive rounds, R2 and J2 |
| --- | --- | --- | --- | --- | --- | --- |
| c1–c2 | 13, 12 | 23, 12 | 11, 10 | 19, 12 | 11, 10 | 16, 12 |
| c3–c4 | 13, 12 | 23, 12 | 10, 9 | 18, 9 | 11, 10 | 16, 12 |

The restricted radius-five balls around the same marks reach four of the five original ring distinctions in J0 compared with five in R0. They reach three in J1 and J2 compared with four in R1 and R2. Both marked positions have the same respective restricted counts at every common round. The full table includes each of the five radii and the exact longer pair distances where available. [Ball profiles](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/bond_profiles.json)

## Two ring landmarks

A second calculation with connected cuts gives exact longer distances at cluster sizes 1, 2 and 3. For the two fixed c1–c2 marks the distances are 31, 27, 27 in T4 and 39, 35, 35 in T8. Allowing all original exclusive distinctions gives 31, 19, 19 and 39, 27, 27, respectively. These strengthen the radius-five bounds below. [Exact supplemental calculation](ring_distance_dp.md)

At the source the bond distance between the two original c1–c2 marks is 31 in T4 and 39 in T8. These also give the minima across the two sets of originals whose holders all lie on the respective ring outside the seam, whether counting only shared distinctions or including loose ones. The radius-five panel gives a lower bound of six for all three readings in each positive measured round. The old minimum remains an upper bound because the old allowed-state relation is the projection of each later relation onto the old distinctions. Each new equation in each of the 150 measured extensions has a fresh distinction that occurs only in that new equation at its addition. The validator checks those witnesses and the literal retention of all older equations. Every old assignment extends by choosing the fresh witnesses. Therefore every old coordinate projection is preserved, including the inclusion-minimal nonfree supports that supply the upper bound.

The shortest co-support step count across original ring-exclusive shared distinctions stays at seven in T4 and eleven in T8 through round five. If the original loose distinctions are included among the possible marks, these counts fall from seven and eleven at the source to five and nine in rounds one through five. Some of those original loose distinctions acquire another holder. A co-support step crosses one literal junction holding two distinctions. The new step readings concern the same set of eligible original marks and can select a different pair from the set. [Bond profiles and distinguished pairs](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/bond_profiles.json)

## Exact calculation and scope

Over the binary allowed-state relation, projection onto a set of distinctions is nonfree exactly when the span of the parity equations contains a nonzero word supported on that set. Thus inclusion-minimal nonfree sets are exactly the inclusion-minimal nonempty supports of this span. In the calculation each junction is a vertex, each shared distinction joins its two holders, and each loose distinction joins its holder to a bookkeeping exterior. A sum of junction rows crosses the cut determined by the chosen junctions. The omitted exterior row is the sum of all other rows in its component. A support is minimal precisely when it lies in one wired component and both sides of the cut in that component are connected. A disconnected side supplies a smaller nonempty cut. When both sides are connected, any smaller cut would have to preserve both connected sides and so would cut the same links. This is the connected-cut description of a graph bond.

Every such bond lies within a single biconnected block of the wired graph. A bond found inside a block extends to the full graph by putting each attached part on the side of its point of attachment. Parallel distinctions cross together during enumeration, with weight equal to their number. Every individual distinction contributes to the ball count. Adding a part at a single wired vertex preserves old pair distances because the two connected sides force the added part to take the side of its attachment whenever the bond crosses an old holder pair. A connection through two wired vertices can change which sides are connected. In the actual attached starts the seam and the exterior both matter to the calculation. The exterior is excluded from co-support step counts.

The first two rounds use the archived exact connected-cut solver on at most 128 wired vertices, with 60 seconds for an attempted piece. For larger or timed-out pieces the search first tries exhaustive short bonds through size six, with caps of 2,000 holder bundles, 1.5 million half-subsets and 16 million joined bucket pairs. Its fallback branches on a surviving path between the marked link's endpoints. A bond through the mark has to remove one of the surviving path's links. Assigning the first removed link on that path partitions the search, with branches exceeding the remaining weight discarded. At separation, both connected parts and every cut link are checked. After the first panel, the later panel gave priority to completing all marks at each radius before advancing, using unrestricted native reads only for stages with at most 18 ordinary junctions. The fallback caps work at 50,000 branch states per wired piece and stage. Its maximum observed usage was 27,371.

All 160 admitted stages returned 15,180 exact ball counts and no unresolved ball count. The last rounds are 32 for B and R0, 29 for R1, 17 for R2, seven for J0, six for J1 and J2, five for T4 and T8, and eleven for C1. Twenty wired pieces used unrestricted exact cuts, 36 used the exhaustive short-bond bank, and 104 used the anchored search. A reported bound such as `>5` certifies that the target is outside each requested ball. Saturation marks full coverage of the specified roster and applies only to some restricted ring balls at radius five here. The finite radii give no estimate of an exponent.

Six finite controls exhaust their allowed states and then their coordinate projections to check all minimal nonfree sets. All agree with the unrestricted cut solver, the short-bond bank and the anchored method at the radii each reads. A literal one-vertex attachment leaves the marked control distance at six. A literal two-vertex attachment lowers it to three. The exact source pair replay and the projection-witness checks cover independent aspects of the measured panel. [Reader](../../experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/world_bonds.py) · [Control receipt](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/bond_controls.json) · [Validation receipt](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/bond_validation.json)

The first panel finished 20 cases with four workers in about 108 seconds and peak memory of 114 MiB. The later panel finished 140 cases with six workers in about seven seconds and peak memory of 503 MiB. Replay from the repository root with the existing literal stage and independent source-pair artifacts.

```bash
eddy_ticket=EDDY-WORLD-20261119-001
eddy_family=${eddy_ticket}-E001_world
eddy_reader=experiments/$eddy_ticket/$eddy_family/world_bonds.py
eddy_scratch=$(mktemp -d /var/tmp/eddy-bonds.XXXXXXXX)
.venv/bin/python -B "$eddy_reader" compile "$eddy_scratch"
.venv/bin/python -B "$eddy_reader" controls "$eddy_scratch/order_reader"
.venv/bin/python -B scripts/longrun.py launch "$eddy_reader" \
  --out "$eddy_scratch/first" --unit eddy-bonds-first --workers 4 \
  --case-timeout 120 --case-mem 2G --mem-max 10G --prepare-only \
  --param panel=first --param binary="$eddy_scratch/order_reader"
.venv/bin/python -B scripts/longrun.py run --out "$eddy_scratch/first" --foreground
.venv/bin/python -B scripts/longrun.py launch "$eddy_reader" \
  --out "$eddy_scratch/later" --unit eddy-bonds-later --workers 6 \
  --case-timeout 120 --case-mem 2G --mem-max 14G --prepare-only \
  --param panel=later --param binary="$eddy_scratch/order_reader"
.venv/bin/python -B scripts/longrun.py run --out "$eddy_scratch/later" --foreground
.venv/bin/python -B "$eddy_reader" collect "$eddy_scratch/first" "$eddy_scratch/later" \
  > "$eddy_scratch/bond_profiles.json"
.venv/bin/python -B "$eddy_reader" validate "$eddy_scratch/bond_profiles.json"
```
