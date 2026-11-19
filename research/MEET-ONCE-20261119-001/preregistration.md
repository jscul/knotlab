# Do reached arrangements whose junctions meet once ever share a table with other states? Pre-registration

Epic `MEET-ONCE-20261119-001` (B205, `GROWN-PAIR-20261119-001#2` via `THREE-WAY-20261119-001#1`, the coordinator's go-ahead; A97,
G1), 2026-11-19. Frozen before the run. The canonical K1–K3 test is unchanged.

## The question

GROWN-PAIR's 152 reached collisions with other states all came from starts whose knots share two distinctions; where junctions meet
at most once its 80 reached collisions (up to 14 junctions) kept the states. Is that a size effect? Every grown census stage of 15 to
24 junctions in which no two junctions share two distinctions, and as declared now 25 to 40 (cheapest counts, complete rounds,
rounds 1 to 8; 1,196 and 1,502 stages): is there a pair of non-isomorphic such stages with isomorphic full tables and other states?

## Prior work in the program

`python3 -B scripts/track.py objects "reached collisions where junctions meet once same table other states" --until 2026-11-19 --exclude MEET-ONCE-20261119-001`

- `GROWN-PAIR-20261119-001`: the same object up to 14 junctions.
- `UNIQUE-TABLE-20261119-001`: static rivals on the same named distinctions (a relative).
- `CENSUS-READ-20261118-001`: the census stages and exact tables (the same population).
Also `THREE-WAY-20261119-001` (three-way readings separate GROWN-PAIR's 152).

## Method

`job.py`: each stage's table exact up to distance 8 and pooled above (H = 8 for every stage, a function of the full table, so equal
full tables share the key), a Weisfeiler–Leman hash of it and of the arrangement. `pairs_meet.py`: arrangement classes by exact
isomorphism; candidate groups by exact isomorphism of the pooled tables; each regrouped at H = 12, 16, … and at the full table (each
step only splits groups, the advisor's check); states by enumerating isomorphisms of the full tables (up to 5,000) and testing by
rank whether one carries the equation space: same, other (all enumerated and none), or undecided.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| M1 | No pair of non-isomorphic meet-once grown stages with isomorphic full tables and other states (the advisor: about 70%) | one exists |
| M2 | At least one pair of non-isomorphic meet-once grown stages with isomorphic full tables and the same states | none |

Undecided groups (cap or time) are reported, not scored against M1.

## Advisor

Fable 5.2 before the freeze ([answer](advisor/answer_1_fable.md)): the escalation is sound if the key is invariant (it is: WL hashes
and isomorphism); a capped search must be called undecided, not a violation (taken); it expects M1 to hold at about 70%, and, if it
fails, from three junctions meeting pairwise in three distinctions. Its generator-orbit method to avoid the cap is not used; capped
groups are reported.

## Runs and stop rule

`job.py` on the shared runner (265 shards, 8 workers, 16G cap), then `pairs_meet.py`. One run; then stop.

## Amendment 1 (2026-11-19, after the frozen pairing ran an hour without a result, before any pair was read)

- **Why.** The frozen pairing escalates every candidate group to the full table, and a full table at 50 to 90 distinctions takes
  hours (at 52 distinctions: 1.6 s pooled at 12, 238 s at 20). Its time limit was checked only between steps, so it never fired.
  It was stopped after an hour with no output. Also fixed before any pairing ran: its incidence matcher read an edge label the
  incidence graphs do not have.
- **What changes: the order, not the verdicts** (`pairs_meet2.py`). Every bijection carrying one equation space onto the other keeps
  the full table, hence the pooled one. So states are decided first, on the tables pooled at 8: same when a junction-graph
  isomorphism carries them (the outside vertex a plain vertex), else by enumerating pooled-table isomorphisms on twin classes
  (distinctions held by the same junctions; any carrier maps these classes onto each other, and permutations inside one keep the
  equation space), up to 5,000, by rank. Classes with the same states have isomorphic full tables: same-states collisions, with no
  full table needed. Only classes of one candidate group with other states are escalated, as frozen (H = 12, 16, … and the full
  table), under a hard limit per group (an alarm, 1,800 s): isomorphic at the full table is an other-states collision, a split is
  none, the limit is undecided.
- **Unchanged.** M1, M2, the population, the candidate groups, and the reading of undecided groups.
