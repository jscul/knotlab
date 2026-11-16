# Exact rates of the cyclic rulers from marked blocks

Epic `MARK-RATE-20261116-001` (`BLOCK-REACH-20261116-001#1`, at John's go-ahead on 2026-11-16 22:20 UTC, relayed by the coordinator,
as the line's last study; G17, with G1), 2026-11-16. Proof note:
[proof.md](../../proofs/MARK-RATE-20261116-001A/MARK-RATE-20261116-001A-P001_no_skip/proof.md). Code by the thread. The canonical K1–K3
test is unchanged. **Refereed** (MARK-RATE-R1, [report](referee-R1/report.md), commit e60a68d91): **confirmed with fixes**, no
Block; Theorem M and Lemma S's closure hold (3,600 SAT signatures inside the families, an independent recursion agrees on 439
descriptions, 20 newly passing cyclic rulers checked directly), and the pilot is disclosed fairly. Its narrowings concern the line
summary and are folded in there and logged in `docs/CORRECTIONS.md`. The line's closing summary: [line_summary.md](line_summary.md).

## The question

`BLOCK-REACH-20261116-001` proved that every small-orbit ruler of the census grows at every depth. For most of the cyclic ones,
though, it proved only one member per two levels (they forget over two levels, not one), while the census reads one per level
(backlog B180). Can a bond skip a single level once every possible marking of the rest is taken into account?

## Answer

**For 55 more cyclic rulers, no level can be skipped, so they grow by at least one member per level at every depth.** That makes 86
of the 152 small-orbit cyclic rulers with r₀ = 0, up from 31. For the other 66 the test says nothing: it is sound but coarse, and both
frozen predictions failed.

A bond that skips a level splits into two parts. The part above is summarised by the set of values its marks leave possible on the
orbit above the gap (an up signature), the part below by the set on the orbit below the gap (a below signature). The bond's
constraint can only come from a pair of such sets that the step between the two orbits cannot join. Over every possible marking, these
sets form finite families that blocks compute exactly (Lemma S). If every pair in them can be joined at every step, no bond skips a
level (**Theorem M**, proved), and a bond reaching s levels down needs s + 1 members.

| Small-orbit rulers (r₀ = 0) | No level can be skipped | Test fails |
| --- | ---: | ---: |
| cyclic, forgetting over one level | 31 (already by Theorem F) | 0 |
| cyclic, over two levels | 55 | 48 |
| cyclic, over three levels | 0 | 18 |
| acyclic, over one level | 197 | 0 |
| acyclic, over two or three levels | 0 | 48 |

The acyclic rulers with r ≥ 2 grow one per level by the hypertree theorem, yet all 48 fail. So a failure only means that the
families also hold markings no bond uses: the test does not require each part of the split to be free. The advisor's sharper
version, least-mark costs propagated level by level, would give exact values and make failures quantitative. It is not built.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Theorem M: if every up and below signature meets the step, no bond skips a level; L ≥ s + 1 at every depth | proved (with Lemma S, the families computed exactly from Theorem W) |
| 2 | 55 more small-orbit cyclic rulers grow one member per level at every depth (86 of 152) | computed; 360 of 360 real signatures from random markings lie in the families (SAT); every r = 1 description passes, no half-rate one does |
| 3 | The test is coarse: 0 of 48 acyclic rulers with r ≥ 2 pass, though they grow one per level | computed |

## Predictions

Frozen in [predictions.md](predictions.md), committed in f273f812e at 22:33 UTC, before `run_census.py` was run. Seen before: a
held-out pilot of 16 (`exploratory/pilot.json`) and the gate.
- **P1 fails.** 52 of the 115 non-pilot cyclic rulers with r ≥ 2 pass (45%; needed half).
- **P2 fails.** 0 of the 48 acyclic rulers with r ≥ 2 pass (needed all): the test is coarser than the truth.
- The consistency gates hold: all 511 with r = 1 pass, none of the 43 half-rate, and no passing description sits below s + 1 in the
  census.

The first census run was stopped after 10 minutes with no output. One description with many orbit types ran without end, and that run
had no per-description limit. The rerun gives 120 s each and records 6 descriptions as over the limit (LONG_RUNNING `MARK-RATE-A1`,
23 minutes).

## Advisor

Used once, before freezing (`advisor_design_answer.md`). It confirmed the split condition and the cut. It asked for the closure
argument (Lemma S) and for an explicit rule on which group a shared orbit's marks belong to, both written. It labelled two of the
three draft predictions as consistency gates, and it proposed least-mark costs for exact values.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — exact rates of the cyclic rulers | **Status:** Partially successful | 55 more grow one per level; 66 unresolved; exact values not reached |
| Local direction — marked blocks | Practically exhausted | The coarse test is done; exact values need least-mark costs, a new build |
| Broader exploration — G17 nested and addressed lines | Known alternatives | Line wrapped up at the owner's request; the main line is the navigating agent |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Rate one at every depth proved for 86 of 152 cyclic rulers |

**Corrections:** none. **Goals:** a G17 checkpoint (with G1), capability gained. **Assumptions:** A83 used; none added.

**Next step:** Full pivot — No next action selected

The owner asked to wrap this line up after this study (2026-11-16). The program's main line moves to the navigating-agent study. The open
items, graded, are filed as backlog rows in the [line summary](line_summary.md).

## Hand-off to the referee

Folder: this one (note, predictions, advisor Q/A, `marks.py`, `gate_marks.py`, `run_census.py`, `census_marks.json`, `exploratory/`);
the proof family `proofs/MARK-RATE-20261116-001A/` (`proof.md`, `check.py`, `result.json`). Proved: Theorem M and Lemma S. Computed:
Corollary M. Least sure: (a) Lemma S's closure: that the recursion in `marks.py` produces every signature of every finite marking
(the gate samples markings of up to three marks); (b) the cut of the below signatures to the step's image of `_up_free`, a union
over contexts; (c) that the 120 s limit hides no pass among the 6 over it (none is a ruler).
