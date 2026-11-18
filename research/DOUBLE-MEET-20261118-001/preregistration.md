# Which double meetings are harmless: pre-registration

Epic `DOUBLE-MEET-20261118-001` (the coordinator's go-ahead on `NAE-METRIC-20261118-001`'s direction 2; G1 and G16; tests A97 and
A39; B200), 18 November 2026. Frozen before the run. Code by the thread (Claude); the run through the shared runner. The canonical
K1–K3 test is unchanged.

## The question, and what was found while designing it

Under not-all-equal, two knots sharing two distinctions alone break bond distance (no bond holds their two other distinctions), yet
the weave, the base the owner's premise is most tested on, is made of such double meetings and its bond distance is steps apart + 1
(`RULER-20261111-001`). Which double meetings are harmless?

While designing it: in patches of the weave the double meeting is never the cause. On every patch without holes tried, every pair
held by some bond has bond distance exactly steps apart + 1, and the only pairs no bond holds are pairs of **lone distinctions**
(each in a single knot of the patch) whose knots are of **opposite classes** and that **face each other**. The lone double meeting is
the smallest such patch: its two other distinctions are lone and face each other. Hexagonal patches (no lone distinction), triangular
ones (all lone distinctions of one class) and cylinders, in the literature's words for their shapes, are true distances; every parallelogram fails at exactly its two acute lone
distinctions.

## Terms

The weave's distinctions are (i, j); its knots are u(i, j) = {(i, j), (i+1, j), (i, j+1)} and d(i, j) = {(i+1, j), (i, j+1),
(i+1, j+1)}, every one not-all-equal. Two knots meeting twice are of different **classes** (u or d). A **patch** is a set of knots;
it is a **disc** when it has no hole and no pinch. A **lone** distinction lies in one knot of the patch. A lone x in knot {x, u, v}
**faces** z when z = x + p(u − x) + q(v − x) for integers p, q ≥ 1 (z lies in the parallelogram, in the literature's word, that x's
knot opens onto); two lone distinctions face **each other** when each faces the other.

## In standard terms

Not-all-equal on the weave is the triangular Ising antiferromagnet at zero temperature; its states are height functions
(Blöte and Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984), equivalently dimer coverings of the honeycomb (lozenge tilings), with
the pairs of the patch's rim usable alone. Heights as difference constraints are Thurston's (1990). Up and down holes in lozenge
tilings interact like opposite charges (Ciucu). Patches without holes are systolic (bridged) complexes (Chepoi; Januszkiewicz and
Świątkowski).

## Prior work in the program

`python3 -B scripts/track.py objects "weave patches bond distance steps apart not-all-equal" --until 2026-11-18 --exclude DOUBLE-MEET-20261118-001`
`python3 -B scripts/track.py objects "double meeting two knots sharing two distinctions lone" --until 2026-11-18 --exclude DOUBLE-MEET-20261118-001`
`python3 -B scripts/track.py objects "height function triangular antiferromagnet dimers ruler" --until 2026-11-18 --exclude DOUBLE-MEET-20261118-001`

- `NAE-METRIC-20261118-001` — same question one level up: bond distance is a true distance exactly when it is one on every block;
  this study looks inside the weave's blocks.
- `BOND-METRIC-20261118-001` — the lone double meeting (T2).
- `RULER-20261111-001`, `RULER-FLAT-20261111-001`, `LONG-LOOP-20261111-001` — relatives: the endless weave (b = steps + 1, proved by
  height functions and difference constraints), closed weaves below a cutoff.
- `KNOTS-ALONE-20261111-001`, `OVERLAP-READ-20261111-001` — relatives: not-all-equal weaves read faithfully; pairs in no bond.
- `FREE-READ-20261118-001` — relative: bond distance on knot trees and rings (steps apart + 1).
- `WEAVE-LAWS-20261117-001` — relative: three-place laws on the six-regular weave (only the not-all-equal class is pairwise).
- `CUMULANT-DIST-20261118-001`, `MEET-ORDERS-20261118-001`, `ADDR-KNOTS-20261113-001` — unrelated (matched on words).

## Settled by construction, and sketched (ticket A)

- **Smallest case** (proved, `BOND-METRIC-20261118-001A`, T2): two knots sharing two distinctions, their other two distinctions lone,
  of opposite classes, facing each other: no bond holds them.
- **Heights** (the advisor's sketch, checked computationally in P0). On a disc, the states (up to switching every value) are height
  functions h with h(v) ≡ i + 2j (mod 3) and steps of +1 or −2 along each forward pair. With D(s, t) the least weight of a route in
  the patch (a forward step costing 1, a backward step 2), a set is constrained exactly when it holds m ≥ 3 distinctions with a cyclic
  order whose D-sum is at most 3(m − 2).
- **D(x, y) + D(y, x) = 3·steps apart** on every disc (the advisor's sketch, using that discs are systolic; checked in P0).
- **Hence b ≥ steps apart + 1 on every disc** (the advisor's sketch): a bond of m members has a cyclic order of D-sum 3(m − 2), which
  is at least D(x, y) + D(y, x) = 3·steps for any two of its members.
- Not proved: b ≤ steps + 1 when a bond exists; that only facing pairs of opposite classes can be unbonded; an exact rule for which
  facing pairs are.

## Exploration disclosed

Before the freeze: hexagonal patches of radius 1 and 2, parallelograms 2 × 2 to 4 × 4 and 2 × 5, triangles of side 3 to 5, two
trapezoids, an L-shaped patch, three cylinders; 355 and then about 800 random disc patches (to 15 and 14 distinctions); every disc
patch to nine knots (2,912) for D + D = 3·steps and for facing; whether the parallelogram spanned by a facing pair lies in the patch.
Seen: unbonded pairs always lone, of opposite classes and facing each other (1,512 of 1,656 such pairs at nine knots unbonded); every
bonded such pair had knots outside its parallelogram. The frozen job's case kinds were smoke-tested reading only their keys.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): the disc test on known shapes and the count of discs to four knots; the parallelogram builder; facing; the two-knot exhibit and D + D = 3·steps on it; the constrained-set criterion on it | any fails |
| P0 | (advisor) On every disc to seven knots, the cyclic D-sum criterion gives exactly the constrained sets; on every disc patch of the census D(x, y) + D(y, x) = 3·steps apart | any set or pair differs |
| P1 | On every disc to eleven knots (fixed up to translation) and on 480 random discs of 10 to 16 distinctions, every pair held by a bond has b = steps apart + 1 | any pair differs |
| P2 | Every pair held by no bond is two lone distinctions of opposite classes facing each other | any other unbonded pair |
| P3 | Every facing pair of a patch with no knot outside their parallelogram is unbonded | such a pair bonded |
| P4 | Every parallelogram a × b with at most 16 distinctions has exactly one unbonded pair, its two lone distinctions, and b = steps + 1 on every other pair | any differs |
| P5 | A disc is a true distance (no failure of the triangle inequality) exactly when it has no unbonded pair | any disc differs |

Recorded without prediction: how many facing pairs are bonded, by number of knots.

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 102 cases (disc census in 44 cases, 7 criterion cases, 40 random cases, 11 parallelograms); `merge.py`
scores. Registered as DOUBLE-MEET-B1. One run; no change after seeing results; later looks labelled post hoc. Stop at the read-out,
the proofs, the referee hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` was asked before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2). It gave the height description, the cyclic criterion for
constrained sets, the identity D + D = 3·steps and with it b ≥ steps + 1 on discs (sketches, not machine-checked; P0 checks the first
two), a structure statement for bonds through opposite-class lone distinctions, and the literature; it could not prove the upper
bound or give an exact rule for facing pairs, and guessed that bonded facing pairs need knots alongside the parallelogram (P3 tests the
converse direction).
