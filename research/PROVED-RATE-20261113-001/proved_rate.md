# Proved rates for the law's reach along a ray

Epic `PROVED-RATE-20261113-001` (`BOND-DEPTH-20261112-001` direction 1; G17, with G1), 2026-11-13, at the coordinator's go-ahead;
the first study computed by Codex from a frozen spec. Pre-registered with the spec in commit 43bc81620 before the run. The canonical
K1–K3 test is unchanged. Refereed by the referee thread with Codex (PROVED-RATE-R1, `referee-R1/report.md`, commit 13515112d):
**confirmed with fixes**, folded in below; three corrections logged (two Narrowing, one Not a block).

## Words

As in `BOND-DEPTH-20261112-001`: the ray of copies and the least ray bond L_ray(s). λ is the minimum cycle mean of the ray DP's
reachable graph, trimmed to what can start and still close; **bounded_all** is the sufficient test for boundedness at every depth;
**zero mean** is λ = 0. The record classes (bounded, rising, flat, capped, and unclassified when a record has fewer than eight
depths) are BOND-DEPTH's labels as the spec defined them; its "bounded" includes the 10 families whose ray bond vanishes deeper down.

## The question

Can the long-run behaviour of the law's reach along a ray be proved: a growth rate when it grows, boundedness at every depth when it
does not?

## The question in standard terms

Minimum cycle means of the finite state graphs of a min-plus recurrence, as liminf rates of fixed-length shortest paths, and a
sufficient test for boundedness at every length.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The graphs close and agree.** 655 of 664 graphs are complete (under two million nodes); of the 653 with records, 644 are complete (98.6%), and the least ray bonds recomputed from them equal BOND-DEPTH's at every recorded depth (0 mismatches). | exact | G passed; P1 held |
| 2 | **The ray bond provably grows linearly in 226 families (34%).** On a complete graph L_ray(s) ≥ λ(s − t) at every depth, t the trimmed graph's size (the referee's sharpening), with λ the liminf of L_ray(s)/s: 1/2 (95), 1 (64), 1/3 (40), 1/4 (8), 1/6 (7), 2 (4) and others from 1/7 to 2. A linear lower bound with an additive constant, for ray bonds only; the true least bond may be smaller through side branches. | proved per family | reported |
| 3 | **Of the 240 that rose within depth 30, 214 grow (89%).** The other 26 have λ = 0, the same 26 that were constant between depths 20 and 30; λ = 0 alone does not make them eventually constant (five were proved constant at 4 by BOND-DEPTH's referee). | proved per family | P2 failed (90% registered) |
| 4 | **The reach is bounded in at least 361 families (54%).** 305 pass the every-depth test, which is sufficient only for every large enough depth and not necessary; the referee's exact test (residues modulo the least common multiple of the zero cycles' lengths, proved both ways, by Codex) certifies the 46 disputed flat families bounded at every depth from 1, by at most 4, and 10 more zero-mean families. This transfers to the true least bond. *"Bounded only along a progression" for the 46, first written here, is withdrawn.* 12 families have no ray bond at large depths (2 never have one, 10 lose it). | proved per family | P3 failed as frozen (it tested the predicate) |
| 5 | **What is not reported: rates per length residue.** λ is the liminf over all lengths; the spec did not ask for a rate per residue, so a family could grow at different rates on different residues. | stated | — |

## Answer

The law's reach inside these nested patterns now has proved long-run behaviour along a ray: in about a third of the 664 families
the ray bond grows at least linearly (rates from 1/7 to 2 members per level, as a liminf, with an additive constant), and in at least
361 it is bounded at every depth, which holds for the true bond too. Depth 30 had read the growth right in 214 of 240 rising families; 26 had only risen early.
The growth is a property of ray-shaped bonds; whether side branches make the true bond shorter is open.

## Reading

**Interpretation, not a theorem.**
- **Counting inside, proved along a ray.** In 226 patterns the shortest chain of constraint from the top to depth s along the copies
  lengthens in proportion to s, so the law's reach measures depth there, as on a ruler, though the ends see depth only modulo a
  period (`NEST-COUNT-20261112-001`).

## Lag cutoffs and census-only claims

The 664 one-definition limit-only families; the ray of first SELF calls; graphs to two million nodes. No claim about side branches,
other rays, rates per residue, or the full weighting.

## The hand-off to Codex (for the owner)

- **Quality.** Codex's code was right first time on the part it finished: it reproduced the DP exactly (gate 0 mismatches on 644
  families), checked Karp against an independent cycle enumerator, and flagged two real ambiguities instead of guessing (records with
  fewer than eight depths; empty-W paths leaving a capped graph).
- **Friction.** Its session ended after 11 minutes while its run was going, which killed the run at 508 of 664; the remaining heavy
  families then ran out of memory at seven workers. I finished both with its own runner, unchanged, in two more jobs (three workers,
  50 GB), about 20 minutes, and merged the batches by family (`merge_and_summarize.py`).
- **Saved.** All the algorithmic code (graph building, components, Karp, the every-depth test, the gate) was Codex's; my part was the
  spec, the recovery runs and the reading: roughly two thirds of the work I would otherwise have done.

## Review

**PROVED-RATE-R1** (the referee thread with Codex): the proofs are sound (L_ray(s) ≥ λ(s − t); λ the exact liminf; Karp on the
trimmed graph; capped graphs prove no growth, positive witnesses transfer); a fresh-code recomputation of 95 families agrees on every
field; the rates match the depth-512 sample; the batch history 508 + 92 + 64 is verified. Its fixes are made above. The advisor model reviewed the draft cold (`advisor_review_answer.md`): λ is a liminf and a
lower-bound rate, λ = 0 alone shows boundedness only along a progression, a capped graph's λ is one-sided, and a ray rate says
nothing about the true bond's growth.

## Literature and provenance

Known: minimum cycle means (Karp 1978), min-plus eventual periodicity (Cohen, Dubois, Quadrat and Viot 1983; Heidergott, Olsder and
van der Woude 2006). Ours: their use for least bonds in nested NAE patterns. Classification: known-with-delta.

## Workspace assumptions

A79 used.

## Ratio

Substantive: the proved rates for 655 families. Administrative: the spec, the pre-registration, the recovery runs, this note.

## Corrections

Three, from the referee (`docs/CORRECTIONS.md`, 2026-11-13): **Narrowing**, boundedness (at least 361, not 305; the every-depth test is
sufficient for large depths only); **Narrowing**, growth and absence worded as a ray-only liminf lower bound, rates 1/7 to 2;
**Not a block**, 644 of 653 kept apart from 655 of 664.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — proved rates along a ray | **Status:** Partially successful (refereed, confirmed with fixes) | G, P1 held; P2 (89%) and P3 (as frozen) failed: growth proved in 226, boundedness in at least 361 |
| Local direction — counting inside | Continue | The true bond's growth needs side branches |
| Broader exploration — G17 | Searching | The full census waits on the side-branch method |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The law's reach along a ray has proved long-run behaviour |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** A79 used.
**Basket:** `CHEAP-COUNT-20261112-001#1` (2/3 Payoff, 2/3 Concreteness), `PREFIX-END-20261112-001#2` (2/3, 3/3),
`LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `LIMIT-ONLY-20261112-001#1` (2/3, 2/3), `NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The true bond, with side branches | 3/3 — Breakthrough-scale if growth survives | 2/3 — Testable | The advisor's bottom-up DP over subtree summaries (least cost per summary by Knuth's least fixed point), on the 226 growing families → whether the true least bond still grows | Selected · awaiting go-ahead (a Codex hand-off) |
| 2 | Rates per residue | 1/3 — Minor | 3/3 — Ready | Karp per residue class of length on the same graphs → whether any family grows at different rates on different residues | Alternative · deferred |

1. Payoff 3: growth of the true bond would prove the law counts inside these patterns. Concreteness 2: the method is described, not
   written.
2. Payoff 1: a refinement. Concreteness 3.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
