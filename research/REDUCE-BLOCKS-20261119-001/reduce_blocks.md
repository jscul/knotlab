# Blocks inside other blocks change nothing

Epic `REDUCE-BLOCKS-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `MERGE-BURST-20261119-001#2`.
Goal G17. **Referee pending.**

**Record.**
- **The proof:** [proof.md](../../proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md), frozen as
  Partial in commit `1ef39c416`, then completed.
- **The machine check:**
  [hublib.py, job.py, job_census.py, merge.py](../../proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/).
  It ran through the shared runner (`runs/reduce-blocks`, and `runs/reduce-blocks-census` for the amended census cases).
- **The advisor** checked the statement before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **The growth reads its start only through which sets of live knots share a common neighbour,** plus the live knots' open counts.
  A block equal to another, or inside another, adds no such set, so it changes nothing. This is proved, for every start, in the
  class or not.
  1. **Round 1.** Which knots can join, and which sets have no common neighbour, are both questions about those sets.
  2. **No knot of the start stays live after round 1.**
  3. **Later rounds read only parents.** From then on the new junctions only see their parents.
  4. **A shortage stops the growth.** A knot that would have to give more than it has is a stall, so there is no tie-break.
- **So any start can be rebuilt with one dead hub per largest block.** That rebuilt start grows exactly like the original from round
  1 on, which gives a direct check: grow both and compare.
  - **The touch census:** all 26,441 arrangements agree round by round, stalls included.
  - **1,000 random starts within seven places:** 998 agree and 2 were stopped by the limits.
  - **Stages of the explosive starts:** 62 agree and 34 were stopped by the limits.
  - **Not one differs.**
- **What this settles.** MERGE-BURST's two readings are now proved, not hypotheses.
  - **The closed case** merges into a block of 9 and ends.
  - **Start-04** merges into a block of 781 and ends after about 2⁷⁸¹ junctions.

  Both read through the rebuilt start, which lies in the proved class.

## Theorem and checks

| Statement | Status | Evidence |
| --- | --- | --- |
| Lemma R: from round 1 on the growth reads a connected start only through its live knots, open counts and the down-closure of its live-neighbour sets | proved | H1–H3 |
| Corollary 1: a start and its hub realization grow identically from round 1 | proved | H1: 26,441 of 26,441; H2: 998 of 998 compared; H3: 62 of 62 compared |
| Corollary 2: a stage whose maximal blocks satisfy the class has its future read exactly | proved | MERGE-BURST's two readings |

3 of 3 checks passed, with one logged amendment: an empty hub realization makes nothing.

## Assumptions

None changed. The reduction was MERGE-BURST's pre-registered hypothesis, never a register entry, and it is now proved.

## Known results, and what this adds

- **Known.** The down-closure of a set family, an abstract simplicial complex.
- **What this adds.**
  - The cheapest growth depends on its start only through that complex and the open counts, which strengthens DOUBLE-IDENT's
    Lemma M.
  - It also gives a canonical rebuilt start for any start or stage.

## Limitations

- **The check** runs to 6 rounds, and 3 for the explosive stages, within the children's limits. The proof covers every round.
- **Corollary 2 needs the reduced stage to lie in the class.** That is checked stage by stage. The 14 unread explosive starts never
  reach such a stage.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze.
- **It found the gap** of shortage tie-breaking. Shortage is a stall in the engine, so there is none.
- **It asked for:**
  - the induction's full invariant;
  - H(X)'s three constraints;
  - connectedness as a hypothesis;
  - class membership stated as a per-stage premise.

  All are folded in.
- **It suggested** a shortage-targeted family. Shortage is a stall, which H1 includes (stalls agree too).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the reduction | **Status:** Successful (proved; 3 of 3 checks) | The growth reads only the down-closure; 26,441 + 998 + 62 comparisons agree, none differ |
| Local direction: the explosive kind (A109) | Research directions | Both merge-and-burst readings proved; the wall stays where maximal blocks share two knots |
| Broader exploration: what the cheapest growth builds | Known alternatives | Any start can be rebuilt with one dead hub per largest block |
| Long-term goal: G17 | Capability gained | A canonical form for every start, and the explosive readings made proofs |

**Next step:** Continue — `MERGE-BURST-20261119-001#1`, a reading past the wall on the smallest unread start (the coordinator's go-ahead, if this lands).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A reading past the wall, where maximal blocks share two knots, on the smallest unread start | 3/3 | 2/3 — the hub form now gives the smallest presentation to study | take the hub form of the smallest unread start at its last stage and find a complex whose clusters give its next round → stop at one, or a proof that none can | Selected (coordinator) |
| 2 | Prove the 2.3830 ceiling within five places | 2/3 | 2/3 | bound every branch system by the theta's → stop at a proof, or a start that beats it | Alternative · in the basket |

## Final report as sent (2026-11-19 19:27 UTC)

**Outcome:** I proved that blocks equal to or inside another block change nothing, so both merge-and-burst readings are now proofs rather than hypotheses: the block of 9 and the block of 781. The growth reads its start only through which sets of live knots share some common neighbour, plus their open counts. So any start can be rebuilt with one dead hub per largest block and grows identically from round 1. All 3 frozen checks passed and none of 27,501 comparisons differs. Closed, referee pending.

- **The proof, in four steps.**
  1. Round 1's joins and groups only ask which sets have a common neighbour.
  2. No knot of the start stays live after round 1.
  3. From then on, new junctions only see their parents.
  4. A knot that would have to give more than it has is a stall, so there's no tie-break.
- **The check: original and rebuilt start, grown side by side.**
  - All 26,441 census arrangements agree round by round, stalls included.
  - Of 1,000 random starts within seven places, 998 agree and 2 hit the limits.
  - Of the explosive starts' stages, 62 agree and 34 hit the limits.
- **One logged amendment.** The census batches first crashed on starts with no live knot, whose rebuilt version is empty. I fixed it to "makes nothing" and reran; no comparison changed.
- **What it strengthens.** DOUBLE-IDENT's Lemma M: the growth's whole dependence on its start is a down-closed family of sets plus counts. The rebuilt "hub form" is a canonical shape for any start or stage.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the reduction | **Status:** Successful (proved; 3 of 3 checks) | The growth reads only the down-closure; 27,501 comparisons agree, none differ |
| Local direction: the explosive kind (A109) | Research directions | Both merge-and-burst readings proved; the wall stays where largest blocks share two knots |
| Broader exploration: what the cheapest growth builds | Known alternatives | Any start can be rebuilt with one dead hub per largest block |
| Long-term goal: G17 | Capability gained | A canonical form for every start, and the explosive readings made proofs |

**Next step:** Continue — a reading past the wall on the smallest unread start (your go-ahead, now that this has landed).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A reading past the wall, where largest blocks share two knots, on the smallest unread start | 3/3 | 2/3 — the hub form now gives its smallest presentation | take the hub form of the smallest unread start at its last stage and find a complex whose clusters give its next round → stop at one, or a proof none can | Selected (coordinator) |
| 2 | Prove the 2.3830 ceiling within five places | 2/3 | 2/3 | bound every branch system by the theta's → stop at a proof, or a start that beats it | Alternative · in the basket |

**Corrections:** one, from the EXPLOSIVE referee fold (bd7357fe8), reported earlier: a Narrowing. "Explosive" means a jump seen before a stop, "none within five places" means none among 2,191 sampled, and the regularity is the smallest case's. **Goals:** G17 checkpoint (capability gained). **Assumptions:** none changed. **Basket:** `MERGE-BURST-20261119-001#2` taken. **Advisor:** Fable 5.2, before the freeze, staying within its text.
- It flagged shortage tie-breaking as a possible gap. In the engine, shortage is a stall, so there is none.
- It asked for the induction's full invariant, the hub form's three constraints, connectedness as a hypothesis, and class membership as a per-stage premise. All are folded in.

**Referee hand-off.** The proof is `proofs/REDUCE-BLOCKS-20261119-001A/REDUCE-BLOCKS-20261119-001A-P001_reduce/proof.md` with `hublib.py`, `job.py`, `job_census.py` and `merge.py`, and the decision note is `research/REDUCE-BLOCKS-20261119-001/reduce_blocks.md`. Please check:
- Lemma R's step 3, that later rounds read only parents;
- that the hub realization's blocks are exactly the maximal blocks;
- the amendment for empty hub realizations.
