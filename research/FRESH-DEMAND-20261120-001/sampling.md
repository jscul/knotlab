# Fresh demand in the labelled tree sample

Both laws formed the first complete step on 91 of 320 draws. The
220 funded pairs included **107 with an identical marked parent bond-distance
reading observed at two different fresh counts**. Five reading types were
ambiguous. Every one of the 487 births per law agreed with the witnessed
demand count after applying its fresh floor. In the serial sample the same
original pair fired under both schedules on 47 starts. Its fresh count
differed on 20 of those starts. [Frozen design](preregistration.md)

## Funding and complete births

Each stratum draws uniform labelled trees by Prüfer sequence with independent
probability \(1/4\) of one extra loose distinction at each knot. The other
loose distinctions bring the arity up to three when needed. The literal
whole-presentation projection on every written knot passed K1–K3 with
both laws. Each row below gives counts under either law. All 320 formation
records agreed across the two laws.

| Old knots | Draws | Funding stops | Proposed pairs | Funded pairs | Funded unary births |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 64 | 0 | 146 | 146 | 148 |
| 5 | 64 | 52 | 210 | 37 | 30 |
| 6 | 64 | 58 | 254 | 17 | 26 |
| 7 | 64 | 61 | 314 | 8 | 17 |
| 8 | 64 | 58 | 336 | 12 | 46 |
| **Total** | **320** | **229** | **1,260** | **220** | **267** |

There were 1,040 proposed pairs in histories that failed complete funding.
Those histories had 792 loose slots left after deducting each holder's
multi-parent obligations where possible. This is an inventory. The unary
roster is formed only when the multi-parent obligations are funded. There
were no initially closed sources or resource cutoffs. Every funded unary
birth took two fresh distinctions. The funded pair counts for one, two
and three fresh distinctions were 122, 80 and 18 respectively.

Let \(h_U\) be the loose count at \(U\) less one. The other births sharing
parent \(U\) number \(h_U\) because the complete step spends every loose
distinction exactly once. On these trees a candidate pair \(U,V\) is at
two ordinary holder steps, through its unique witness \(S\). Every further
knot pairwise candidate with \(U,V\) is another neighbor of \(S\).
Thus the old candidate cliques of size three or more are all held, and
the funded old multi-parent roster contains only pairs.

Two births in the new roster are candidates when their old parent sets
intersect. With unary and pair parent sets, a pairwise-intersecting family
with no common parent must consist of the three pairs on three old
holders. This creates exactly one successor group replacing two
successor pairs at the marked birth for each third live neighbor of
\(S\). Hence the pair demand is \(h_U+h_V-t\), where \(t\) counts those
third live neighbors. Unary demand is \(h_U\). All 487 raw demands and all
487 clipped fresh counts agree per law. Setting \(t=0\) gives 72 wrong
fresh counts among the 220 pairs. The common floor in this sample is
\(\max(1,3-p)\) for \(p\) inputs, since a first-layer birth here never
consumes the entire loose set or has implied inputs.

## What the current reading distinguishes

Each funded birth contributes one observation. Parent holdings supply
the unordered arity and loose count of each chosen holder. Ordinary
holder steps count shared-distinction meetings; witnessed candidate steps
count relations with a common holder. Those lengths are two and one on
every source pair. The full parent bond-distance reading includes every
pair among all distinctions held by the marked parents. It retains
holdership, looseness and the chosen inputs. Types are matched by verified
isomorphism with all pair readings preserved. The witnessed reading adds
the third-live-holder count \(t\) to the parents' arities and loose counts.

| Reading on a funded pair | Observed types | Types with different fresh counts | Pairs having such a type | Fewest pooled lookup errors |
| --- | ---: | ---: | ---: | ---: |
| Parents | 11 | 5 | 127/220 | 21 |
| Parents and both step lengths | 11 | 5 | 127/220 | 21 |
| Least bond size of the chosen inputs | 4 | 4 | 220/220 | 62 |
| Parents and least bond size of their chosen inputs | 19 | 5 | 107/220 | 20 |
| Parents and all pair bond distances on their holdings | 19 | 5 | 107/220 | 20 |
| Parents and witnessed \(t\) | 16 | 0 | 0/220 | 0 |

The minimum lookup error is obtained by assigning the most frequent
fresh count to each observed type. This is a descriptive restriction on
the recorded sample. Repeated births within a draw are dependent.
All 267 unary births have the same fresh count, leaving these ambiguity
counts unchanged when unary births are included in the denominator.

Even within five old knots, three full parent bond-distance types are
ambiguous, covering 24 of 37 pairs. Draw `5/03` with parents `(1,2)` and
draw `5/36` with parents `(0,1)` both have one parent of arity three and
one of arity four, two loose distinctions per parent, and minimum input
bond size six. Their full marked parent bond-distance matrices match as
type `9`. The respective witnessed \(t\) values are zero and one, giving
two and one fresh distinctions. Within six old knots, one type covers
four of 17 pairs at two different counts. None of the other three size
strata has a full bond-distance type with two counts.

### Computing the bond readings under both laws

For parity, the computation enumerated the distinct boundaries of
connected holder sets by literal distinction incidence and checked them
against the minimal nonzero supports of the row span. Every component
left by deleting a connected holder set reaches an original leaf on its
own side. Such a leaf holds loose distinctions. Wiring loose distinctions
to one auxiliary exterior therefore makes the complement connected, so
each connected holder boundary is support-minimal.

For not-all-equal, fix any input pins. An unpinned shared distinction
passes the possible values of a subtree to its next holder. A message
with one possible value arises only when all the other entries at that
holder are forced to the same value. At a first contradiction all entries
are forced to the same value. Trace the forced messages backward to
their pins. The traced holders form a connected set, and its boundary
is pinned. A pinned shared distinction terminates the trace across that
meeting. Conversely, on any connected holder set, one can pin its
boundary to force a contradiction at a selected holder by alternating the
forced value along its successive meetings. The minimal contradictory
pin supports are therefore the same connected boundaries already checked
for parity. The actual forbidden words generally differ between laws.

Enlarging a connected holder set adds \(a-2\) to the bond size for each
additional holder of arity \(a\). A chosen loose distinction at one parent
of arity \(a_U\) has least bond size \(a_U\). The chosen inputs of a pair
have least bond size \(a_U+a_S+a_V-4\), including the unique witness.
All marked holdings and all pairs were scored by enumeration, and this
formula was checked on each chosen input set. The verifier directly queried
the actual not-all-equal projection on each of 940 distinct measured
minimum supports across draws, using 26,312 pinned words. Each support
excluded exactly two complementary words. An exhaustive all-state scan
recovered all bonds under both laws on two fixed four-knot controls.

## Present-state schedules

The serial weighting is one draw per initially funded source. Within each
such draw, one funded multi-parent set is independently chosen uniformly
and held fixed across laws and schedules. The unrestricted uniform and
joins-first schedules choose from the lists supplied by the archived
present-state rule. The same move ordering and random seed are used for
a given schedule across laws. The immediate control forces the marked
pair as the first legal event. Any different group is another event.
Loose distinctions at a holder are interchangeable; the evaluator uses
one literal allocation. The histories stop at the exact marked group,
a proved loss of that group, lack of a move, or twelve accepted events.

| Schedule | Exact pair made | Pair permanently lost | Still eligible at cap | Fresh differs from complete step among those made |
| --- | ---: | ---: | ---: | ---: |
| Immediate | 91 | 0 | 0 | 49/91 |
| Uniform | 58 | 32 | 1 | 26/58 |
| Joins first | 72 | 19 | 0 | 41/72 |

The outcome counts apply separately under parity and not-all-equal.
Every permanent loss here includes exhaustion of an original parent.
Once a parent loses its last loose distinction, future births cannot
give it another. The single capped uniform draw `6/51` retained the
exact pair on its move list. Among the 47 common firings the raw demand
differed between schedules on 30, with fresh differing on 20. In draw
`4/03`, the exact pair `(2,3)` fires third in both orders under both
laws, taking two fresh distinctions under uniform and one under joins
first. A remaining difference between arbitrary-order and fair infinite
growth is outside this finite panel.

There is one law-specific difference before the marked target stops.
Immediate and uniform traces agree across laws on all 91 starts each.
Joins-first traces agree through stopping on 90 of 91. In draw `4/49`
the exact target is `(0,2)`. Both traces take `(0,3)`, `(2,3)` and `(4,5)`
before the legal ternary `(0,2,6)` supersedes that target. The ternary
consumes inputs `4,6,11`, the entire current loose set, and has zero
provisional demand. Its parity projection permits four even words and
the child closes with zero fresh distinctions. Its actual not-all-equal
input projection permits all eight words, including both constant
words. The same ternary therefore takes one fresh distinction and leaves
a loose distinction. Both original parents are exhausted in both laws,
and the different ternary never counts as the marked pair. The marked
outcome and its fresh count when made agree on all paired law replays.

## Replay and scope

All 182 random parity schedule prefixes were replayed using the archived
serial function itself. The not-all-equal runs used the literal old-stage
implication query and tested the entire actual input projection at every
serial firing. The fixed checks also refused an unlawful two-place
source, a complete-layer shortage and a larger group offered as the
marked pair. Reversing holder and distinction names on a funded control
preserves its birth inventory, bond types and output. The full sample
replay is under a second in the shared runtime and uses below 50 MiB
resident memory. A repeated run matched the saved data byte for byte.
[Replay code](../../experiments/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders/sample_starts.py) · [All draws, schedules and reading types](../../artifacts/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders/sample.json)

```bash
prlimit --as=6442450944 -- .venv/bin/python -B \
  experiments/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders/sample_starts.py
```
