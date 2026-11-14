# Is the bond bounded where the calls remember

Epic `CARRY-BOUND-20261114-001` (`CENSUS-FORGET-20261114-001#2`, backlog B174, with `TIE-CYCLE-20261114-001#2`; G17, with G1),
2026-11-14, at the coordinator's go-ahead. Pre-registered in 99b396c40 (objects gate passed; the advisor consulted twice), with a
clarification after TIE-CYCLE's referee (cc2ece62c) and an addendum answering Codex's eight implementation questions before the
full run (c75547967). Code by Codex in two hand-offs, run by the thread on the shared runner. The canonical K1–K3 test is unchanged.
**Referee pending. Stress test pending:** the direct search's finite readings (step 3) are still running and will be folded in.

## Words

- **L(s)**: the least bond (minimal non-shattered set) containing a port of main and an own distinction of some copy of the ray
  definition S at depth s reached from main through S calls (a covered target), with members anywhere. **Bounded**: L(s) ≤ C at
  every large s. The path to the target may change with the depth.
- **Window**: main's ports together with the block of the target copy. Lemma W (proved in the pre-registration) makes its
  projection exact, so every bond found there is a bond of the whole pattern, and its least size U(s) bounds L(s) at every depth.
- **Carried port**: a port of main handed down unchanged to a copy. **Read** (live) when some knot uses the position that holds it,
  directly or further down; **unread** (dead) otherwise. A distinction held only at unread positions is constrained by nothing below.

## The question

`CENSUS-FORGET-20261114-001` left undecided the families whose first-ray bond provably grows but which do not forget: some long
product of their calls is never a product relation, so the gap argument says nothing. Per depth, with members anywhere and any
covered target, is their bond bounded, or does it grow?

## The question in standard terms

For 5,964 iterated hyperedge-replacement NAE families with a non-rectangular idempotent in their port-relation semigroup, whether the
least minimal non-shattered set containing a root port and a vertex at derivation depth s stays bounded in s. Upper bounds come from
exact projections onto a finite window, eventually periodic in s. Lower bounds come from rectangular powers on the quotient by
unread coordinates.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The method is exact where checked.** All 5,964 families finished (75 minutes, peak 1.8 GB, no failure). The per-call relations equal the census's in every family, and every family is living. A pendant knot at a carried position always gives a bond of at most 3 (22 of 22). No family is both bounded and growing. **Negative control:** on 300 families certified to forget, the window never undercuts the proved lower bound 2 + ⌊s/r⌋, and the trimmed gap certifies all 300. **Brute force:** separate code unfolded 50 identity-cycle families explicitly and matched the window's projection on all 2,686 words of length up to 3; 200 recorded bonds were re-verified there. The four synthetic controls pass. | computed | G passed |
| 2 | **Where the calls carry a value they read, the bond is bounded.** In the identity-cycle stratum the window bounds L at every large depth in 4,967 of 5,687 in-scope families (5,029 of 5,751 draws, **87.4%**; Wilson 86.6% to 88.3%; 88.8% leaving out the 88 undecided). The bound never exceeds 4: at most 2 in 60 families, 3 in 4,901 and 4 in 6. In 86.0% of the bounded weight the bond is the carried port, an own distinction of the target copy and a third member, all in one knot (the advisor's widened reading of Theorem B). The strict Theorem B (two pendant members) explains only 0.4%. | proved per family (finite certificate) | P1 held (≥ 80%) |
| 3 | **An order bounds the bond as well as carrying does.** All 93 in-scope families of the order label are bounded at every large depth: 91 by the window, 2 more by EVERY-RAY's path DP (97.8% by the window alone; Wilson 92.5% to 99.4%). That is 10 points *above* the identity stratum, not 20 below. Their bonds have 3 members (55) or 4 (36). They have no identity cycle, so no port of main is carried to large depths. A one-way order keeps the top readable at every depth without carrying a value. | proved per family | **P2 failed** (gap −10 points, not ≥ +20) |
| 4 | **What stays unbounded carries only values no knot reads.** Of the in-scope identity families the window leaves unbounded at some residue, 89.8% by weight have no carried position in a knot with an own distinction on any such residue (100% of the decided ones). No family is left unbounded because of an opposite tie. | computed | P3 held (≥ 80%) |
| 5 | **Ties act like identity.** All 5 tie families are bounded: 3 through a tie bond, 2 otherwise. | proved per family | P4 held |
| 6 | **Unread carrying hides growth.** In 632 identity-cycle families (634 draws, **10.8%** of the in-scope weight) every value carried down sits at positions no knot ever reads. Deleting those coordinates leaves relations whose r-products are all rectangular (r = 1 in 318, 2 in 163, 3 in 55, 4 in 96). By the gap argument on that quotient (Lemma G), the bond **grows** at least like 2 + ⌊s/r⌋: they forget everything they can read. Their identity cycles made them non-forgetting in name only. | proved per family | **P5 failed** (10.8% > 5%) |
| 7 | **Little is left.** Of the 5,789 in-scope families, 5,074 are proved bounded (5,067 by the window, 7 more by the path DP on the sample of 65), 632 are proved to grow, and **83 (1.4%) are undecided**: 70 capped windows, 11 with no window bound and no growth certificate, and 2 with complete window bounds that the frozen rule counts as undecided because an inherited census cap blocks the growth test. Out of scope, 129 of 175 are bounded (a bound to covered targets bounds L) and 46 undecided. The direct search's finite readings on the 58 sampled families still open after the path DP (28 undecided, 30 growers as a consistency check) are pending. | proved per family; computed | reported |

## Answer

Almost all of the undecided half is decided, and mostly the other way. In nine families out of ten, the bond from the top reaches
every depth with at most four members, wherever they sit. A value carried down from the top, or a one-way order, keeps the top
readable at every depth, and a knot at the target copy reads it. The first ray's growth in these families came from following one
fixed way down. In the remaining tenth, the values carried down are never read by any knot. The family remembers them only in name:
take them away and every way down forgets, so the bond grows. With the earlier census share, the census's first-ray growth now
splits as follows (13,279 draws):
- **grows** with nothing chosen: 58.0% (7,697 = 7,063 from `CENSUS-FORGET-20261114-001` + 634 here);
- **bounded** at every large depth: 39.6% (5,265);
- **undecided**: 2.4% (317, including the 188 draws outside CENSUS-FORGET's covered scope).

## Reading

**Interpretation, not a theorem.**
- **Memory that matters is memory that is read.** TIE-CYCLE sorted what a family keeps of its top by kind: carrying or ordering.
  For the bond, what matters is whether some knot reads the kept value near the target. A read value, or an order, gives a short
  bond at every depth. An unread one leaves the family counting depth as if it had forgotten.
- **The first ray overstates growth.** In 40% of the census's first-ray growth weight, a path that changes with the depth finds a
  bond of at most four at every depth. Counting inside, with nothing chosen, is real in 58% of that weight, and absent in 40%.
- **The owner's nested parts.** A part knows where it sits in the larger pattern when it reads something the top handed down, or is
  held on one side of an order fixed by the top. Without that it is independent of the top after a few levels, and its distance from
  the top is counted by the law.

## Lag cutoffs and census-only claims

Census families only, weighted by draws (A79). Bounded and growing are proved per family; the shares are census facts. "At every
large depth" means after the window's preperiod (at most 36 levels here). The direct search is finite readings only, never growth.

## Review

**Referee pending.** The advisor model was consulted twice before the freeze (`advisor_review_answer.md`,
`advisor_review2_answer.md`). It checked Theorem B, proposed the widened reading, found the missing merges and the living premise
in Lemma W, replaced capped length sets with the deterministic state iteration, proposed the trimmed gap (Lemma G2, which the
thread checked), and flagged P3's first form as settled by construction. The thread replaced P3 before the freeze. All of this was
adopted.

## Literature and provenance

Known: exact projections through tree decompositions (separators), eventual periodicity of finite-state iterations, the gap argument
(BRANCH-DEPTH, FREE-TARGET), deletion of unconstrained variables. Ours: the window certificate for nested NAE families, the
live-quotient growth certificate, and the census split. Classification: known-with-delta.

## Workspace assumptions

A79 used. A81 used: 86% of the bounded weight is a bond through a carried top port. The order families' bonds do not use one.

## Ratio

Substantive: 5,964 exact window decisions, 632 growth proofs, 65 path DP runs. Administrative: the freeze, the clarification, the
addendum, this note.

## Corrections

Two (`docs/CORRECTIONS.md`, 2026-11-14):
- **Narrowing** of TIE-CYCLE's reading. "Where it remembers by carrying, the carried value gives short bonds" holds only for a
  value some knot reads. In 632 families every carried value is unread, and the bond grows.
- **Not a block**, of my own: the pre-registration's Lemma G named the wrong fixed point for unread positions. It was corrected in
  the addendum before the run.

## Data

- `experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/`: Codex's code (`window.py`, `brute.py`,
  `gates.py`, `sample.py`, `summarize.py`, the jobs), `REPORT.md`, the gate runs, the smoke, `sample.json`, the path run
  (`paths_full/`) and the direct run (`direct_full/`, pending).
- The full window results (3.5 GB) stay on the workspace. Their per-family digest is in
  `artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz`, and the summary in
  `summary.json.gz`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the undecided half | **Status:** Successful (referee pending) | P1, P3, P4 held; P2 and P5 failed informatively; 98.6% of the in-scope families decided |
| Local direction — counting inside | Continue | The census's first-ray growth is now 58% grows, 40% bounded, 2% undecided |
| Broader exploration — G17 | Searching | Where the law counts depth, and why: read memory bounds the bond, unread memory does not |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Per-depth reach decided for almost every census family whose first ray grows |

**Corrections:** two (one Narrowing of TIE-CYCLE's reading, one Not a block of my own). **Goals:** a checkpoint for G17 and G1;
no goal change. **Assumptions:** A79 and A81 used; A81's record gains this study.
**Basket:** `B173` (2/3 Payoff, 2/3 Concreteness; next in line by the coordinator's order), `FORGET-RULE-20261114-001#2` (1/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A read carried value bounds the bond, as a theorem | 2/3 — Substantial | 3/3 — Ready | Prove: if a carried position on a residue shares a knot with an own distinction, the bond is at most 3 on that residue (rule out the opposite tie in every living family, or find one) → a whole-stratum theorem covering 86% of the bounded weight, or a counterexample | Selected · awaiting go-ahead |
| 2 | Why an order bounds the bond | 2/3 — Substantial | 2/3 — Testable | From the 93 order families' window bonds, a rule for which one-way orders keep the top readable → a proved sufficient condition | Alternative |
| 3 | Other recursive definitions as targets (B173) | 2/3 — Substantial | 2/3 — Testable | The coordinator's next in line | Alternative · in line |

1. Payoff 2: makes the main bounded mechanism a theorem, which the coordinator ranked above sample counts. Concreteness 3: a short
   proof obligation, and the census gives 0 exceptions to aim at.
2. Payoff 2: the one bounded mechanism without carrying. Concreteness 2: 93 families on disk.
3. Payoff 2: as recorded in B173. Concreteness 2.

**Recommendation.** Research directions, #1, unless the coordinator keeps B173 first.
