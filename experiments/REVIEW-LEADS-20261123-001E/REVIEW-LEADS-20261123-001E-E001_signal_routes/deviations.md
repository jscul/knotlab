# Deviations and readings for REVIEW-LEADS-20261123-001E-E001

No definition of the frozen note (`research/REVIEW-LEADS-20261123-001E/preregistration.md`) was changed. Each
item below is an ambiguity in the note, the reading taken, or an addition. Nothing was tuned after values
were seen; the only changes made after the first (development) runs were repairs of code that failed or
ran too slowly, listed at the end.

## Readings of the note

1. **Sources of the starts** (all read only). Seven-knot source: rebuilt from `research/GENERATORS-20261120-001/
   source.md` (meetings 01 twice, 04, 14, 24, 26, 34, 35, 56; loose supply 3,0,3,3,3,2,2; 25 distinctions);
   checked by its birth counts 8, 12, 19, 32, 56 and fresh totals 25, 42, 75, 140, 269 per round, which match
   that note, under both laws. Five-founder clock: `source_cases()["five_odd"]` of
   `experiments/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/.../phase_clocks.py`, rebuilt with the same
   arithmetic (18 distinctions). Archived explosive starts 00, 04, 13 (six-knot starts of the explosive-growth
   archive): the literal supports of `artifacts/HEAVY-GROWTH-20261119-001/.../sources_audit.json`. Smallest
   two-sided stall and smallest parity closing: `S_cycle_five` and `C_binary` of
   `WHOLE-STAGE-SETTINGS-20261120-001B/.../edits.py`. Concealed-shortage preparation: `physical()` of
   `LOCAL-EDIT-POLICIES-20261123-001C/.../physical.py`, names mapped to integers. Every plan of every history
   was also checked against the compact reference operator (`ORDINARY-DYNAMICS-20261120-001A/.../end_operator.py`)
   except rounds of over 400 births (12 rounds in all).
2. **The smallest two-sided stall has no funded step.** R3 needs a funded step, so the structure used is the
   five-knot, 13-distinction start with both optional additions (setting 11, the only funded setting; 15
   distinctions). The three unfunded settings (00, 01, 10) stall, so they have no allocation to enumerate.
   They are histories of R1 and R2.
3. **"The first two funded steps."** Funded step 2 starts from the structure that funded step 1 produces
   under the canonical allocation (smallest names first). The allocations of step 1 are not crossed with
   those of step 2.
4. **"Cap about 24 distinctions."** Read as at most 26 old distinctions for an exhaustive enumeration of
   every old word (the seven-knot source has 25 at funded step 1, and the note names it). Consequences:
   the stall is enumerated at both funded steps (15 and 25 old distinctions); the seven-knot source (50 old
   distinctions at step 2) and the five-founder clock (28) only at funded step 1. For those two, step 2 is
   not enumerated; instead 200 random allocations are checked for R3 (i) and (ii) only (births of the
   later rounds up to the horizon and the exact count of allowed words of the grown structure by variable
   elimination), and the clock's step 2 is also run as a labelled supplementary row beyond the cap
   (28 old distinctions, still exact because only the loose marginal is enumerated).
5. **Allocation classes.** Several unary births at one knot are exchangeable copies, so allocations that
   differ only by which copy receives which loose distinction are identified ("up to renaming"). The raw
   number of bijections is reported next to the number of classes. In every structure and step enumerated
   the two numbers coincide, because no knot there has a spare that becomes a unary birth.
6. **"To six steps", "to three returns", horizons.** The seven-knot source is grown six rounds in total
   (the allocation at funded step 1 and five later rounds are compared). The clock's returns of the
   marked turn are at ages 6, 11, 16, ... (`research/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/
   phase_clocks.md`), so three returns is 16 rounds and six returns is 31. The stall is compared over six
   rounds. R1's "12 parent steps" is read as 12 complete rounds. Histories with no stated horizon (the stall
   and closing settings, the concealed preparation) run 12 rounds or to 2,000 knots.
7. **"To 2,000 knots."** Rounds are atomic. A history stops before any round that would take the number of
   knots above 2,000, or when growth ends. The knots actually reached are reported (archived explosive 04:
   1,300 after 7 rounds; 13: 1,368 after 6 rounds; 00 under parity closes at 1,084 after 22 rounds, under
   not-all-equal 1,987 after 64 rounds).
8. **"Interchangeable" per knot.** The loose distinctions of a knot are interchangeable under a law and a
   weighting when the distribution of all old distinctions is unchanged by every reordering of that knot's
   payments with all other knots at their canonical allocation. The reported largest difference per knot is
   over those reorderings. The overall largest difference is over all allocation classes against the
   canonical one; because permuting the loose distinctions of a knot is an automorphism of the old
   structure, the largest difference over all pairs equals this (checked on all 496 pairs where there are 32
   classes; on 300 random pairs of the seven-knot row it never exceeded it).
9. **The joint distribution of all old distinctions.** The weight of an old word depends on the allocation
   only through the values of the loose distinctions, so the total variation on all old distinctions equals
   that on the loose ones. The script computes the loose marginal and verifies the equality against the full
   joint on every allocation where there are at most 64 classes and the old structure is within the cap (the
   clock's step 1 and the stall's two steps), and on 12 random classes of the seven-knot source. Totals of
   allowed words of the grown structure are cross-checked against an independent variable-elimination count
   (every class of the 32-class rows; the first 64, 12 random and every 97th of the seven-knot row).
10. **Valued versions (R2).** Parity: uniform on the allowed words by linear algebra over GF(2).
    Not-all-equal: uniform by rejection where the acceptance rate allows (400,000 draws), otherwise
    Moser-Tardos resampling (each version lawful, distribution not exactly uniform): the 8 concealed-preparation
    rows. Each row of the R2 output states which. Horizons were fixed from run time, not from values: the
    seven-knot source six rounds, the clock sixteen, the explosive starts up to 1,000 knots (18, 6 and 5
    rounds), all others eight rounds or 300 knots. A valued run hands each fresh distinction a lawful value
    drawn uniformly given its paid inputs.
11. **The injected join veto (R2).** The all-parent veto of `WRITTEN-BIT-AND-JOIN-VETO-20261122-001A`:
    a proposed group is dropped unless every distinction on every parent equals a reference word (zero under
    parity, the lexicographically first allowed word under not-all-equal; fresh reference values are the
    lexicographically first lawful completion of the reference inputs). On the closing start 00 under parity
    only 55 of 64 valued versions differ from the reference: the start has 8 allowed words under parity, the veto
    reads all six distinctions, and nine of the 64 sampled versions are the zero reference word itself. The fault
    is flagged there with 55 of 64.
12. **The injected holdings fault (R1)** is applied after the third round; a history with fewer than three
    rounds receives it after its last round (the closing start 00 under parity, one round), and a history with
    no funded round (a stalled start) cannot receive it (14 of 42 rows).
13. **Concealed-shortage preparation.** The four types (u, v) are histories with the funded free settings
    (x, y) = (u, v); the unedited preparations (stalled) are also replayed.
14. **R4 reading.** The reading is an abstract-syntax-tree listing of the parameters and names read by the
    functions that form the groups and by the reference operator. It shows what is read, not what is
    ignored; the replays carry the claim. The law argument of `plan_round` is checked to be used only after
    the groups are formed (plus an assertion that it is a known law).
15. **R5.** The replay rebuilds every birth and recomputes the eligible births from the holdings after every
    birth. The reference ancestry of the marked turn and the ancestry-isomorphism test are imported
    read-only from `research/LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001/audit_last_spend.py`. The
    contrast with the complete-round rule on the same prefix is a diagnostic: that prefix was made by
    serial births and need not be reachable by complete rounds.

## Additions (not part of the frozen definitions, reported separately)

- R1: audits that every funded round pays every loose distinction and that each old distinction gains a
  second holder only from a new knot; agreement of every round (up to 400 births) with the compact reference
  operator.
- R3: the smallest lawful start on which an allocation changes the distribution of the old distinctions
  (searched over connected starts of three knots; `minimal_start.py`), with its full tables, and a
  supplementary report of the total variation of the loose distinctions of each other knot, alone and
  jointly with the allocating knot's.
- R4: a replay of an extra loose distinction added at a live knot (an edit): the groups do not change.
- `routes_evidence.py` (replays for the table of routes: whether the two detector sides of the concealed
  preparation ever meet, whether the four types differ in any round's birth statistics, stall persistence, the
  smallest parity closing with the R3 comparison). It was run once, after the five checks, outside the
  recorded `run_all.sh` pass; its line was added to `run_all.sh` afterwards.

## Development runs and repairs

Development runs preceded the recorded pass (gate, R1, R3, R4, R5 each run once or more while the code was
written; their outputs are kept in `artifacts/.../dev_runs/`). Changes after them, none of which touches a
definition: an early stop for rounds that would exceed the knot cap (before the costly look-ahead);
sampling of lawful completions without enumerating 2^f words (an enumeration ran out of memory on a round
with many fresh distinctions); the fallback sampler for not-all-equal (rejection failed on the 62-knot
preparation); the R2 horizons in item 10 (the first horizons made the veto run grow without bound); the
gate's own shorter horizon (6 rounds, 300 knots); skipping the reference-operator cross-check for rounds of
over 400 births; the `--history` option of R1 (one explosive history per run); and the additions above.
After the recorded pass `summarize.py` was repaired (the repository root, and the rows of the sampled step 2),
so `logs/code_sha256.txt` (taken at the start of the pass) differs from the final `summarize.py`, and
`routes_evidence.py` is not in it. Before the recorded pass the development outputs were moved into `dev_runs/`; nothing was deleted.
