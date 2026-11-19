# Referee report JUNCTION-KINDS-001-R1 (own growth, own shares and kinds, an independent matcher, own interval types)

**Verdict: confirmed. No Block; one wording point. The owner's own narrowing (323c2ccdf) is supported by NATIVE-SPINE-001-R1.**
- **The study's figures reproduce exactly, on all 30 starts.** The referee regrew the ten T, fifteen Q and five C starts with its own
  engine (complete rounds, fewest counts, GF(2) implication). Equal to the study's on every start and round:
  - the counts;
  - the distinct out-shares per round;
  - the distinct sum-equitable kinds of depth 6 per round.
- **`spinelib.out_shares` and `sum_kinds` are right.**
  - The out-share is s(j) = Σ over children c of 1/p(c), with p(c) the number of parents, one distinction from each, so the shares
    of a child add to 1.
  - The kinds refine forward by the share totals into the previous kinds.
  - **The argument holds.** In an exact transfer every junction of a class sends the same totals, hence has the same out-share. So
    finitely many classes give finitely many out-shares, and J1 measures the out-shares rising.
- **The matchings check out with an independent matcher** (networkx's Hopcroft–Karp, on the referee's own ancestry).
  - **T:** at every recurrent round of the ten, every round, not only one, the maximum matching is perfect. Its size equals the
    study's, and so does the single-chain version's.
  - **C:** at every round past the lags of the five, the matching saturates the smaller side.
  - **The recurrent rounds** are the study's.
- **J4 holds, more strictly than searched.** The ten have only 6 or 7 interval types each, so the referee tested every subset of
  them (63 or 127), not only sets of up to three of the top ten. None makes the relation regular, on the first half of the
  recurrent rounds or on all of them.
- **One wording point.** "No finite set of junction kinds carries the count" holds for exact transfers along the parent relation
  with the 1/p shares, as the Limitations say. It should say so where it is stated. Other splittings, such as a choice of one
  ancestor per junction, can give a finite transfer on average. The matchings do exactly that, though NATIVE-SPINE shows that
  shuffled relations do it too.

## The checks (`job_kinds.py` under `scripts/longrun.py`; the starts read from the study's population files)

| | Result |
| --- | --- |
| Counts equal to the study's | 30 of 30 |
| Distinct out-shares per round, equal to the study's | 30 of 30 |
| Distinct sum-equitable kinds (depth 6) per round, equal | 30 of 30 |
| T: recurrent rounds equal; matching perfect at every one (networkx Hopcroft–Karp) | 10 of 10 (21 to 23 rounds each) |
| T and C: matching sizes and single-chain sizes equal to the study's at every round | 15 of 15 |
| C: matching saturates the smaller side at every round past the lags | 5 of 5 |
| T: interval types; subsets tested; regular on the first half / on all rounds | 6–7 (the study's numbers); every subset (63 or 127); **0 / 0** |

## Corrections for the owner (listed, not folded in)

1. **Scope of "no finite set of kinds".** It holds for an exact transfer along parents with 1/p shares. The answer's headline
   should carry the qualifier that the Limitations already state. **Not a block.**

## How the work was split

- **The referee:**
  - read `junction_kinds.md` (with the owner's narrowing), the pre-registration, `spinelib.py`, `kindlib.py`, `job.py` and
    `merge.py`;
  - wrote `job_kinds.py`, on its FIRST-KNOT-R1 and TOUCH-CENSUS-R1 code.
- **Read as data:** the starts and the study's records (`runs/junction-kinds`).
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap, 3 workers (peak 7.0 GB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
