# Deviations and readings, REVIEW-LEADS-20261123-001F-E001

The pre-registration (`research/REVIEW-LEADS-20261123-001F/preregistration.md`,
sha256 `59cb60d8f25af312545849616b7a7928e60bb9ab1879089effe9350d2e62ba3f`) was
not edited and no definition in it was changed. Below: one deviation from the
requested enumeration, and each place where the text left a reading open, with
the reading taken. Nothing was tuned after values were seen; the additions
listed under D9 only add reporting.

## D1. Deviation: exact history counts do not reach the horizon on the seven-knot and nine-knot sources

Requested: enumerate every whole history over the horizon. Over the full
horizon (6 parent steps on the seven-knot source, 4 on the nine-knot source) the
number of whole histories per start is far beyond enumeration, and the exact
count by elimination over the payments of the growth does not fit either: its state space
passes the 3,000,000-state allowance at parent step 3 on the seven-knot source
(0 of the 345, 482 and 582 distinct carried-count vectors of the three arms
finished) and at parent step 2 on the nine-knot source (1 of 966 finished in the
rule arm, 0 of 1,004 and 0 of 990 in the others; `counting_stopped_at_depth`,
`distinct_carried_vectors_finished_at_stop_depth` in `seven.json` and
`nine.json`). Horizons shortened as little as the engine allows, structure by
structure:

| structure | pre-registered horizon (as read, D2) | exact whole-history counts through | what decides survival and uniqueness to the full horizon instead |
| --- | --- | --- | --- |
| five-founder clock | 30 parent steps (six returns) | 30 (full) | the same exact count |
| seven-knot source | 6 parent steps (235 knots) | 2 | SAT |
| nine-knot source | 4 parent steps (259 knots) | 1 | SAT |

The SAT instance has one variable for each payment, that is each (child, parent)
pair of the growth (the value of the distinction the parent pays that child) and one exact
counter for each knot's number of ones; a start enters by assumptions on its
founders' counters. It decides, for every start and every number t of parent
steps up to the horizon, whether at least one whole lawful history of t parent
steps exists, and (with one blocking clause and a check of the number of ones
among the horizon newborns' still-loose fresh distinctions) whether there is
exactly one. It was checked against the exact counts at depths 1 and 2 on all
drawn carried-count vectors of both sources (an assertion in the run), on the
clock at depths 1 to 5 and on the seven-knot source (gate.json), and it detects
removal where there is some (negative controls with two stricter rules, gate.json).
It was run on every carried-count vector that any lawful start has, so its
statements cover every lawful start, not only the drawn ones. The single-law arms
were handled the same way.

## D2. Reading: "8 parent steps or 300 knots", "6 parent steps or 300 knots"

Read as: the last parent step at which the whole structure (founders and all
births) has at most 300 knots, and at most the stated number of parent steps.
Seven-knot source: knots by step 7, 15, 27, 46, 78, 134, 235, 420, so 6 parent
steps. Nine-knot source: 9, 24, 54, 117, 259, 597, so 4 parent steps. The
five-founder clock to six returns needs 30 parent steps and has 155 knots. No
step stalls inside any horizon. (Outside the horizon the archived literal engine
refuses the nine-knot source at step 7, where the births exceed its cap of 1,024;
this was never needed.)

## D3. Reading: what makes two histories the same

The text: two valued continuations are the same history when a renaming of fresh
distinctions that preserves every later holding carries one to the other. The
founders' own loose distinctions are not fresh, and a renaming of fresh
distinctions only does not identify two allocations that differ by swapping two
equal-valued loose distinctions of a founder. Two counts are therefore kept:

* value-flow count (the main one): continuations related by renaming every
  distinction that is not shared by two founders, which is the number of
  assignments of one value to each payment (each (child, parent) pair), together with the number
  of ones among the still-loose fresh distinctions of the newborns at the horizon;
* labelled-founder count: renaming of fresh distinctions only; it is the
  value-flow count times the product over founders of c!(h-c)!, c the ones among
  a founder's h loose distinctions.

Both were checked against explicit enumeration with named distinctions
(every lawful completion, every bijection of loose distinctions to children),
five-founder clock, depths 1 and 2 (gate.json). Uniqueness ("exactly one
history") is judged on the value-flow count; on the labelled-founder count no
start is unique because every founder has two or more loose distinctions to
allocate. The number of ones among still-loose fresh distinctions at the horizon
is part of a history; which of two equal-sized fresh sets carries them is not.

## D4. Reading: "1,024 drawn by seed 2026112306"

Read as: 1,024 distinct lawful valuations, drawn from `random.Random(2026112306)`
by rejection: draw a uniform bit string over the structure's distinctions, accept
it when every founder's word is lawful under the arm's rule, skip repeats, stop at
1,024. Each accepted string is uniform over the lawful valuations. Each arm draws
from its own copy of the stream (same seed). The number of lawful valuations is
counted exactly first (a sum over the shared distinctions of independent founder
factors), and all of them are used if there are at most 4,096. Five-founder clock:
rule 4,009 (all used); parity alone 8,192 and not-all-equal alone 179,878
(1,024 drawn). Seven-knot: 92,312, 262,144, 16,316,976 (1,024 drawn each). Nine-knot:
449,885,231, 1,073,741,824, 267,940,964,814 (1,024 drawn each). Digests of the
drawn lists are in the result files. What a continuation depends on is only the
vector of ones among each live founder's loose distinctions (carried counts);
survival and history counts are computed per carried-count vector and weighted by
the starts that have it.

## D5. Reading: survivors and removal

"Survivors counted at every step" is read as the number of valued starts that
have at least one whole lawful history of t parent steps, t = 0, 1, ...; a start
with no such history is removed at the first step where there is none, and stays
in the denominators. The 1,024 drawn starts and, separately, every lawful start
(by carried-count vector, with its exact number of starts) are counted.
No stall occurs in any horizon, and no start is removed in any arm, so there
are no removed starts or stalls to carry in the denominators. On the clock the
number of carried-count vectors from which no lawful next step exists is also
zero (so no old word is removed at any step, reachable or not); on the
seven-knot source the same is checked for every vector of ones that the eight
newborns of parent step 1 could carry (space 4^7 x 5 = 81,920, whether reachable
or not). Prefix-level removal beyond that was not enumerated.

## D6. Reading: P2 and P3

P2 is judged over the whole histories of each start: the start passes when every
whole history of it has the same signal fraction. P3 is judged on the union of
the signal fractions of all whole histories of all surviving starts (at most two
distinct values); the variant that uses only starts with a single fraction is
also given. The result is the same under both readings.

## D7. Reading: gate G

G1: K1, K2, K3 of `knotlab.knots.check_knot` and of the command-line checker
(`knotlab check`, same verdict) on the relation of the allowed words, with the
first n-1 places as loops and the last as contact; the rule fails K2 at 3 and 4
places (and also at 5, 6, 7); parity alone and not-all-equal alone pass K1-K3 at
the same places (controls). G2: "the recorded range of fractions from 0 to 1" is
read as: from the quiet start under each single law, all 64 six-bit patterns of
signals and all signal counts 0/6 through 6/6 occur. G3: from the quiet start
under the rule there is exactly one whole history, silent at every return, and
the carried count alternates 0, 10, 0, ...; the receiver returns at cuts 5, 10,
..., 30 (checked from the actual births and the founders' physical word order).

## D8. Note: the hand null's carried counts 1 and 9 are not realised by any lawful start

`counting_null.md` (sha256 recorded in the artifacts folder before any run)
derives a case C0 = 1 or 9. The five founders' weights sum to twice the number of
ones on shared distinctions plus C0, and each founder's weight is even under the
rule, so C0 is even in every lawful start (only 0, 2, 4, 6, 8, 10 occur). The
derivation of the hand null is unchanged and checked on the vectors with C0 = 1
and 9 as pure counting (gate.json, 2^30 histories each, signal counts as derived);
no lawful start has them. The null file was not edited.

## D9. Additions made after the first runs (reporting only)

After the first full run of each script, these were added; they change no
definition and no prediction: for the clock, the pooled and per-start-share
distributions of signal counts by carried count and the count of carried-count
vectors with no lawful next step; for the structures, the check of prefix removal
at parent step 2 over all vectors of newborn ones (seven-knot only; the nine-knot
space, about 4 x 10^10, is too large) and the check that SAT and exact counts
agree; in the gate, the negative controls and the check of the hand null on
carried counts 1 and 9. All outputs in the artifacts folder come from the final
scripts, run again after these additions.

## D10. Sources imported (read-only)

`experiments/GENERATORS-20261120-001A/.../fixtures.py` (ordinary growth engine
with its built-in agreement test against the archived end operator at every
step; `source_from`); `experiments/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/.../phase_clocks.py`
(the five-founder clock source and its physical phase order). Their sha256 are
in every result file. The seven-knot source is built as in
`research/GENERATORS-20261120-001/source.md` (meetings 01 twice, 04, 14, 24, 26,
34, 35, 56; loose 3, 0, 3, 3, 3, 2, 2; 25 distinctions); the nine-knot source as
in `research/READS-HOLDERS-SOURCES-20261120-001C/proof.md` (ten pairs, loose 5, 2,
4, 3, 3, 4, 3, 3, 2; 39 distinctions). Both laws give the same births on every
step of every structure used here, so the rule's structure is the ordinary growth
of either law.

## D11. Wording note on `counting_null.md`

`counting_null.md` was written and its sha256 recorded before any run, and is
not edited. It uses the word "edge" once (H6, "(child, parent) edge"), which the
program's glossary does not allow for its own objects; it means a payment of a
loose distinction from a parent to a child. All other notes use "payment".
