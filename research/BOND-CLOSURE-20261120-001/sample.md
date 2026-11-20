# Ternary closure under two named weightings

In the uniform labelled tree sample, **127 of 247** funded ternary
proposals had a full marked growing-end component recorded with both
closing and continuing outcomes. Their three pair bond readings all
answered correctly. The shared type consists of three live
parents with one loose distinction each and three
distinct pair witness sets. Every choice of a root among the three
parents preserves its shape. The other ten observed component types
can certify continuation by an additional loose distinction in their
own component. [Frozen weightings and scope](preregistration.md)

| Ordinary labelled tree proposals | Closing | Continuing |
| --- | ---: | ---: |
| Funded proposals | 22 | 225 |
| Full step type observed with both outcomes | 22/22 | 105/225 |
| Correct under the component-exhaustion rule | 22/22 | 120/225 |
| Correct for each of the three possible pair queries | 22/22 | 225/225 |
| Individual pair queries correct | 66/66 | 675/675 |

The component-exhaustion rule predicts closure when the marked inputs
are the only loose distinctions displayed in the connected component.
The best rule fitted to the observed step types would instead predict
continuation on the shared type. It must miss **22 of 247** proposals,
even with the entire component supplied. This is an empirical
incompatibility in the recorded sample. It is also the exact
structural ambiguity case for this ternary reader: the extra loose
distinctions in all other component types exclude closure, whereas
one can realize the single shared type in lawful cases with both
outputs. An occurrence's source size, age, or full number of
live components is not supplied as another feature.

## Uniform labelled trees

The first weighting draws 128 independent uniform labelled Prüfer
trees at each source size from four through eight. At a holder of
ordinary degree \(g\) it assigns \(\max(0,3-g)\) loose distinctions
plus one with independent probability \(1/4\). Every generated
source passed the literal parity projection gate. This also follows
from its form: each component after deleting one knot contains an
original leaf with loose distinctions, so every surviving component
still reaches the auxiliary exterior. The exact row-space check
verifies the projection on each written knot individually.

| Original knots | Draws | True funding stops | Draws with a funded ternary | Closing proposals | Continuing proposals |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 128 | 0 | 73 | 22 | 113 |
| 5 | 128 | 93 | 23 | 0 | 40 |
| 6 | 128 | 115 | 6 | 0 | 17 |
| 7 | 128 | 112 | 13 | 0 | 26 |
| 8 | 128 | 109 | 16 | 0 | 29 |
| Total | 640 | 429 | 131 | 22 | 225 |

The 640 draw outcomes include 22 closures and 189 histories ending
at the scheduled replay horizon. There were no physical resource
caps and no two-input closing exceptions. A last observed continuation
does not certify an infinite fate. A proposal contributes one vote
at the age it is read, up to age three inclusive. The 247 proposals
are drawn from 131 histories and their repeated occurrences do not
supply independent binomial trials. In the four-knot stratum alone,
the shared step type occurs with 22 closers and 47 continuers.
The larger size strata include more instances of that type, with no
closer in any of those strata. The condition of observing both
outputs therefore uses the stated pooled sample. Continuing
proposals use one, two or three fresh distinctions, with respective
counts 211, 13 and 1.

## Random physical elaborations

The second weighting uses 128 independently generated common cores.
Each uses three routes between two old ends, with separate lengths
uniform in four through eight. The first and last meetings of a
route have one or two physical distinctions chosen independently.
Its interior meetings have two or three. With independent probability
\(1/2\), two admissible interior holders on distinct routes get an
additional path of length two through four with all its meetings
doubled. The three holders near the first common end each have two
loose distinctions. In each draw the two arms differ by one
loose distinction at the far common holder. All 128 physical cores
differ in their labelled meeting descriptions. There are 61 with
the additional path. Every arm is lawful and funds the tested
ternary.

**All 128 paired draws** give the same marked step type in both arms
and opposite outcomes. In the closing arm every pair and the whole
triple has least bond size three. In the continuing arm those same
minima are all four. The two arms together give 128 closing and
128 continuing proposals, with one recorded step type and zero
failures on 768 individual pair queries. These are 128 pairs of
histories. The arm count does not weight them as 256 independent draws.

The separate fair-arm weight selects just one history per core by
a fair bit independent of the shape. It gives **59 closing and
69 continuing** proposals, all in the same exact step type. Even
fitted to these observations, a rule of that type alone makes at
least 59 mistakes. The bond criterion succeeds on 59/59 closing
and 69/69 continuing proposals. In the weighting itself the single
step type gives equal probabilities for the two outcomes, because
every base sends the two fair choices into opposite outcomes. That
is an exact statement on this construction's support. It supplies
no prevalence for the random trees or for all lawful starts.

## Physical checks

For each funded ternary, the receipt records the actual allocated
inputs, the fresh count, the whole stage closing verdict, whether
it takes every loose distinction, and a parity row-span test of
whether its support is already implied. The two independent
bond readings use the full-loose tightness criterion and
literal size-three cuts. All five quantities agree on the binary
closing decision on every scored proposal. Extra positive fresh
counts are retained as separate measurements.

In a connected written presentation, a size-three bond through
two loose inputs either takes the sole full loose support or
crosses one ordinary shared distinction. In the second case that
single physical distinction must separate the ordinary holder
presentation when removed. The calculation enumerates all such
single bridges and checks the exact two-loose side. A multiply
shared meeting cannot supply that single crossing. This audit
of every pair uses the current physical holdings independently
of the proposal outcome. There are at least three loose inputs
for every scored ternary. Therefore its two queried inputs
cannot exhaust the whole loose support or form a cut by
themselves. A size-three minimum is exactly bond distance two.
In the continuing three-route arm the
three marked loose distinctions and the remote unary's single
old input form a connected-shore cut of size four. Its two sides
were also verified for every draw.

Among reached frames with at most sixteen knots, a separate solver
enumerated all connected cuts for a deterministic prefix of
qualifying literal frames. It checked 32 frames from the trees
and 19 from the three-route samples, including the exact minima
through all subsets of the selected ternary inputs. The bridges,
tightness tests and complete minima all agree on those checks.
Renaming the knots and physical distinctions independently
preserves each instrument and the exact marked step type on
a control from both weightings. Equal step types were checked
by isomorphisms of the typed witnessed incidence. One vote is
given to each unordered parent-set proposal. Alternative loose
positions at the same holder are physically permutable, and the
receipt records their multiplicities alongside the representative
allocated decision.

The 2,048-knot and 8,192-distinction stage limits and the six-GiB
process limit were in force. None of the 429 stalled stages
offered a prospective ternary, so no ternary label was dropped
from an underfunded history. Both panels retain each original
draw and all termination states. The independent arm bit in the
second weighting selects which physical start to score. The
ordinary growth law sees only that start's physical incidence.

~~~sh
.venv/bin/python -B experiments/BOND-CLOSURE-20261120-001A/BOND-CLOSURE-20261120-001A-E001_proposals/sample_starts.py
~~~

[Per-draw receipts, bridges and shape classes](../../artifacts/BOND-CLOSURE-20261120-001A/BOND-CLOSURE-20261120-001A-E001_proposals/sample.json)
