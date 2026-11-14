# Pinning and whole-main-block referee lane

Verdict: **Confirmed with fixes** for Theorem P′ and the two-block bound. The
claim that all 65 residual families require members allocated strictly
between main and the target is **refuted**. This lane does not audit the
localisation proof or recompute the overall census denominators.

## Theorem P′ and the residue quantifier

**Not a block.** The proof at
`proofs/TOP-INFO-20261114-001B/TOP-INFO-20261114-001B-P001_top_info/proof.md:11–16`
is correct. A minimal non-full subset of T ∪ D cannot be contained in either
shattered side, so it holds both a main port and a target-own distinction.
The finite-relation argument itself does not require a covered target; the
declared L(s) and census restrict the conclusion to covered S copies.

The exact census flag is existential over the reachable word states **at
each eventual Q phase**. Since the entire Q set at that phase recurs, a
witness gives the same uniform bound at every sufficiently large depth in
that phase. Neither plain pinning nor P′ requires all words to work. Merely
finding a pinned word at infinitely many depths in a coarser residue would
be weaker: every refined eventual phase must be covered to conclude a bound
at every large depth of that coarse residue. Both interpretations are
retained in `coarse_residue_quantifiers`; they agree in the audited sample.
P′ at every Q phase gives boundedness directly, without the dichotomy.

Fresh independent pinning reconstruction checked all **632 growers**, all
**93 order-label families**, and **32 identity families**: **757 families,
26,431 unique repeating word states, 1,045 eventual phases**. All preperiods,
periods, phase flags and numbers of pinned states match the producer data.
No grower has even one pinned or bond-pinned repeating state. Among the 93
order-label families, 78 are bond-pinned on every phase and 15 are not, so
T1 holds and T2 fails. The 15 identifiers are explicitly listed in
`pinning_window_results_summary.json` and their complete keys and phase
records are in `pinning_window_results_orders.jsonl`.

The advisor's 26-state hiding relation is independently enumerated and has
correlation but no bond containing x. A separate exhaustive check of all
255 nonempty complement-closed relations on four distinctions confirms the
shattered-side/cross-bond equivalence. These finite checks supplement the
short symbolic proof; they do not replace it.

## A hidden word state actually occurs

**Narrowing.** `research/TOP-INFO-20261114-001/top_info.md:31` infers that the
advisor's hiding phenomenon does not occur from agreement of the
existential residue flags. Those flags do agree in the audited population,
but individual word states can differ.

Order-label family **aab77be157e5** has preperiod 7 and period 1. Its 28-state
eventual Q set has 24 plainly pinned states but only 22 bond-pinned states.
The two exceptional words are `[0,1,2,0,2,1,1]` and
`[1,1,0,0,2,1,1]`, both at depth 7 with no wrapper. Their J values are
`0xfffeffffffff7fff` and `0xff7ffffffffffeff`, respectively, with identity
partition `[0,1,2,3,4,5]`.

For each word, the projection on three main ports and five target-own
distinctions has **220 states**, versus **8 × 28 = 224** for its two
marginals. Its sole minimal non-full support uses four target-own
distinctions, labels `[6,7,8,10]`, with 14 allowed states. There is no cross
bond. Explicit all-S-copy CNF unfolds **3,280 copies / 16,403 variables**
for each word, reproduces the complete window relation, and exhaustively
checks all 256 support projections of its eight-distinction joint relation.
The complete rows, actual IDs, words, transfer states and all minimal
supports are in `pinning_window_results_hiding.json`.

This is the **generic hiding phenomenon**, not a claim that the advisor's
particular four-top-port/one-target relation occurs up to a role-preserving
permutation: this example has three top ports and five target-own
distinctions. Its family/residue flags remain true because other words at
the same depth are bond-pinned.

## Two-block exactness and the nine new bounds

**Not a block.** Retain every distinction of main in the transfer row, carry
its identity through the partition, and merge equal occurrences before
testing a support. Eliminating the intermediate blocks then gives the exact
projection. An own distinction of main passed as an argument remains the
same retained distinction. The fresh implementation uses only permitted
older referee helpers; the independent CNF computation never uses a
port-to-port generator or relational composition.

**Narrowing.** The formula and context sentence at `proof.md:32–35` need an
explicit main = S convention. At s = 0 the retained blocks are the same
copy. For w = i₁…iₛ with s ≥ 1, use main's call-specific whole-block
Start′ᵢ₁ followed by Rᵢ₂…Rᵢₛ. A wrapper instead has a direct-entry Start′
followed by s transfer factors, and absolute depth s + 1. The producer
REPORT explicitly states that it handles this special case; this is a
proof-notation qualification, not a demonstrated numerical error.

All nine newly bounded, formerly undecided families independently reproduce
the complete finite Q iteration and a maximum U₂ of **4**:

| Family | Word preperiod | Period | Absolute threshold |
| --- | ---: | ---: | ---: |
| b6ebb4241032 | 7 | 1 | 8 |
| d418f587a3d6 | 3 | 1 | 4 |
| 714cdee7811a | 7 | 1 | 8 |
| 2c048723bc85 | 4 | 1 | 5 |
| 6962298bed11 | 3 | 1 | 4 |
| 76b8d752905a | 3 | 1 | 4 |
| 89d5e870c85e | 5 | 2 | 6 |
| a4b93391c243 | 3 | 2 | 4 |
| b1cce7c5f270 | 4 | 1 | 5 |

All nine have a wrapper. Threshold means the start of the complete periodic
Q certificate, not necessarily the earliest depth where a bound holds.
Raw CNF checks **45 selected-word bonds**, covering two full eventual
periods and early depths, plus **18 all-branching explicit unfoldings** at
word depths 1 and 2. Their whole-window comparisons check **778,752
assignments**. Every bond is non-full, nonempty and full after each single
deletion; actual distinction IDs and source allocations are recorded.
These are upper bounds for the infinite pattern, not global lower bounds
from a finite member universe.

Twelve additional full explicit projections exercise main = S, wrappers
with multiple direct entries, repeated main-own arguments and wrapper
constraints. A wrong-identity control rejects the spurious two-occurrence
support of one distinction. A wrong-start control erases a wrapper knot and
is rejected by comparison with the correct raw CNF.

## The residual 65 do not imply strict-middle members

**Block for the mechanism claim**, not for P′ or the numerical bounded
split. The assertions at `top_info.md:31–32,44,53–56` do not follow from the
two failed sufficient conditions. An additional member can be allocated in
main's own block. Fresh finite-Q searches deliberately exclude every target
port unless it is identical to a retained main distinction; the remaining
permitted support universe consists only of main allocations and the
target's own allocations.

Three of the residual 65 have such bounds on every eventual phase:

| Family | Word preperiod | Period | Absolute threshold | Phase bounds |
| --- | ---: | ---: | ---: | --- |
| fea4933ecaf1 | 3 | 2 | 4 | 3, 3 |
| fd60333c5872 | 8 | 3 | 9 | 3, 3, 3 |
| 5ceea39607cb | 11 | 2 | 12 | 4, 4 |

For example, **fea4933ecaf1** at word `[1,1,1]` has a size-three bond on
actual IDs `[1,8,22]`, allocated at absolute depths **[0,0,4]**. Its six
allowed rows exclude assignments 3 and 4; all three one-deleted projections
have four rows. At word `[1,1,1,1]`, IDs `[1,8,26]` give the other eventual
phase, also allocated at [0,0,5]. No strict-middle allocation appears.
The all-order pinning audit excludes a size-two root/target-own bond at
every sufficiently large depth, so these eventual size-three bounds are
globally least for this family. The other entries are certified upper
bounds only. All seven phase certificates are independently checked in raw
CNF, with complete whole-window projection comparisons.

This refutes the claimed necessity of strict-middle allocations. It does
not classify all 65, assert that every least bond has only main/target
allocations, or refute localisation. Use "not explained by the two tested
sufficient conditions" for the residual class until its mechanisms are
directly established.

## The two R rescues

**Not a block.** Earlier independent READ referee logic independently
reconstructs effective readings for **432127c418b0** (word preperiod 19,
period 12) and **981fdc202826** (word preperiod 14, period 4). Both have
wrappers. Every refined Q phase has a surviving reading, with 2,340
eligible checks, zero exceptions and 395 complete-window triple
crosschecks. Sixteen independent raw-CNF size-three bonds cover all 16
phases. The exact records are in `pinning_window_results_Rrescues.json`.
Reconciling whether these change a strict or full-admission historical
denominator belongs to the lead's independent count audit.

## Evidence and limits

All code and results are confined to this directory. The new scripts are
`pinning_window_core.py` and `pinning_window_audit.py`; output names begin
`pinning_window_results`. The JSON records retain exact source and code
hashes, phases, identity partitions, concrete words, SAT-tested supports,
resource measurements and the explicit no-forbidden-TOP-Python flag.

Validation is **V2**, independently authored same-task AI referee work,
with explicitly permitted older referee algorithms reused. This is not
external replication. The audit uses one single-thread process at a time,
no network, no Git mutation and no publication. The proof conclusions remain
separate from finite computational checks. Localisation, full-population
pinning beyond the 757 audited families, the official 30-family gate, and
new general SAT algorithms are outside this lane.
