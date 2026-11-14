# Does the law's reach grow to every copy at depth with members anywhere

Epic `FREE-TARGET-20261114-001` (`EVERY-RAY-20261113-001#1`, backlog B172; G17, with G1), 2026-11-14, at the coordinator's
go-ahead. Code by Codex from a frozen spec. The thread ran it on the shared runner. Pre-registered in a89dc18f5 (objects gate passed),
with one clarification in 5660af585 before the full run. The canonical K1–K3 test is unchanged. Refereed by the referee thread with
Codex (FREE-TARGET-R1, `referee-R1/report.md`, commit 04e2b87dc), the proof as the main object: **confirmed with fixes**. The gap
argument is sound and the headline stands; six corrections are folded in below (one Block, four Narrowing, one Not a block).

## Words

**L_any(s)**: the least bond (minimal non-shattered set) containing a port of main and an own distinction of **some** copy at depth
s, with members **anywhere** in the infinite usual-limit pattern, side copies included. It is the most generous reading of the
law's reach to depth s: no ray, no target and no support is chosen. **Forgetting**: every product of r per-call port relations is
rectangular. The **66**: the sampled families whose least bond over paths, with members on the path, grows per depth
(`EVERY-RAY-20261113-001`).

## The question

Freeing the bond's members and its target can only shorten it. Does the least bond from the top to depth s still grow?

## The question in standard terms

In an infinite iterated hyperedge-replacement NAE instance (a tree of copies), the least minimal non-shattered set containing a root
port and some vertex at derivation depth s, over the whole instance. Lower bounds come from rectangular powers of port relations;
upper bounds from a fixed-size tree-automaton saturation along an eventually periodic path.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The method is exact where checked.** Codex's independent code re-derived every per-call relation and every certifying product on all 66 families (161 SELF calls, 0 mismatches). Synthetic controls pass for the semigroup, rectangularity and the bounded search, including a carried top port that needs a side member. No family is certified both ways. A mutant that drops one call's side relation changes a relation. All 66 cases finished (2 minutes, 2 workers, peak 172 MB per case). | computed | G passed |
| 2 | **Two thirds of the 66 count depth with nothing chosen.** In 43 of 66 (65.2%; Wilson 53.1% to 75.5%) every product of r per-call relations is rectangular, for r = 2 (9), 3 (14), 4 (6), 5 (9) or 6 (5). By the gap argument (BRANCH-DEPTH's, generalized to every call; confirmed by the referee), every bond from a top port to any copy of S at depth s, members anywhere, has at least 2 + ⌊s/r⌋ members in the 36 whose main is S, and at least 2 + ⌊(s − 1)/r⌋ in the 7 whose main is a wrapper (*narrowed after the referee*: the unshifted form fails in general). Copies of S are every eligible target here: of the 9 several-definition families, the 4 with another self-holding definition give it no own distinctions. Bonds exist at every large depth, since L_any ≤ L_path. So L_any grows at least linearly, at a rate between 1/r and λ_path (1, 1/2, 1/3 or 2). | proved per family (finite certificate) | P1 held (22 needed) |
| 3 | **No bounded certificate.** *Narrowed after the referee:* the eventually-periodic search ran on 57 families (the 9 with main ≠ S were skipped: the 7 certified wrappers and 2 unresolved), and produced no bond of at most 5 members, anywhere, along an eventually periodic path at every depth. The search certifies one infinite path; boundedness per depth along paths that change with the depth is not tested. | computed, sufficient test only | P2 failed |
| 4 | **23 unresolved.** In 21 a non-rectangular product recurs, so forgetting fails, and no bounded certificate exists at k ≤ 5. In 2 (main is not the ray definition) the bounded search was not run. | computed | reported |

## Settled by construction (added at the close)

**A chain's first-ray growth transfers.** *Corrected after the referee (Block on the justification).* A family whose S and main
each make one SELF occurrence and no other self-holding call is a single chain of copies, with finite helper definitions and a
wrapper main allowed: 5,190 distinct families, 5,633 draws (the literal one-definition, one-call class is 4,035 and 4,478). ~~It has
one copy at each depth and no side copies, so L_any = L_ray.~~ The free bond may use members **below** its target, so L_any = L_ray
is false; the referee's counted family has a bond {a, b, d, e} to depth 2 through e below the target with no prefix bond there. What
holds is inf_{d≥s} L_ray(d) ≤ L_any(s) ≤ L_ray(s), because a bond's deepest member makes it a prefix bond at that depth. So the
census's proved first-ray growth (Karp's uniform lower bound) transfers, and a chain's free bond grows at least linearly wherever a
bond exists; 15 counted chains have depths with no ray bond, 12 of them beyond depth 20. A single chain as a ruler is the program's
earlier result (`LOGIC-AXIS-20261107-001`, and the chains of `RANDOM-FATES-20261112-001`); this transfers it to the free bond.

## Answer

Yes, often. In two thirds of the sampled families whose bond grows along every path, it still grows when its members may lie
anywhere and its target may be any copy at that depth. Every bond from the top to depth s needs at least one member every few levels.
The reason is that every way down forgets: any r consecutive levels, by any choice of calls, pass on no correlation between their two
ends unless a member sits inside them. The other third are undecided here. No bounded certificate was found (the search ran on 57). Together
with the chains, whose first-ray growth transfers to the free bond wherever a bond exists, the law does count depth inside a nested
pattern with nothing chosen, in a definite part of the population. *(Confirmed by the referee, with the fixes above.)*

## Reading

**Interpretation, not a theorem.**
- **Counting inside, with nothing chosen.** For these families depth is a bond distance in the strictest sense the program has. The
  tie between the top and any copy at depth s needs a number of distinctions growing with s, wherever those distinctions sit. The
  mechanism is forgetting: each stretch of levels, by whatever calls, decouples its ends. This is the owner's "larger patterns hold
  smaller ones" read as a count: the deeper the copy, the more of the pattern a constraint must pass through.
- **How common.** The 43 are 43 of 66 every-path growers and 43 of the 300 sampled first-ray growers with a choice of calls
  (14.3%; Wilson 10.8% to 18.8%, *rounding corrected after the referee*). ~~With the chains, an estimate of the weight that counts
  depth with nothing chosen is about 3% of all nested weight.~~ *Removed after the referee:* it combined a census count with a sample
  share against the frozen no-extrapolation rule; the census-wide count is `CENSUS-FORGET-20261114-001`'s.

## Lag cutoffs and census-only claims

The 66 per-depth growers over paths of EVERY-RAY's frozen G sample. Budgets k ≤ 5 for the bounded search; the semigroup decided
exactly. No claim on the 21 non-forgetting families, on the strata EVERY-RAY did not sample, or on boundedness with depth-dependent
paths.

## The hand-off to Codex (for the owner)

- **Quality.** Codex built it in 23 minutes:
  - the per-call relations and the exact semigroup decision;
  - a generalized fixed-size saturation with a subset construction over calls;
  - an independent re-derivation, SAT witness checks, synthetic controls and a mutant;
  - the shared-runner job.

  It flagged two small ambiguities and froze its source digests. Those digests stopped the first launch when my clarification
  changed the pre-registration, which is the right behaviour.
- **Friction.** One re-freeze, and the bounded search skips the two families whose main is not the ray definition (the convention I
  decided was not implemented).
- **Saved.** All algorithmic and validation code was Codex's. My part was the design, the clarification, the launch, the chain count
  and the reading.

## Review

**FREE-TARGET-R1**: confirmed with fixes. The referee checked the gap argument and its premises independently. Codex reproduced all 161
relations and 66 decisions from fresh code, and found 70 exact minima on the 10 smallest certified families with no relation code, all
within the bounds. The advisor model reviewed the design cold (`advisor_review_answer.md`). It confirmed the gap argument for a
free target with members anywhere and sharpened the bound to 2 + ⌊s/r⌋. It also asked for the exact semigroup decision, for
minimality and every-step acceptance in the bounded test, and for no extrapolation from the sample. All were adopted.

## Literature and provenance

Known: rectangular relations and powers of finite relations; tree automata and finite saturation (Rabin); BRANCH-DEPTH's gap argument
and fixed-size test for a fixed branch. Ours: the generalization to every call and a free target, the exact semigroup decision, and
the verdicts on the 66. Classification: known-with-delta.

## Workspace assumptions

A79 used; A80 overturned (the target is free here); A81 (carried ports) caught by the bounded test's controls.

## Ratio

Substantive: the 66 verdicts and the chain count. Administrative: the spec, the clarification, the re-freeze, this note.

## Corrections

Six, from the referee (`docs/CORRECTIONS.md`, 2026-11-14):
- **Block.** The chains' "L_any = L_ray by construction" is false. It is replaced by the inequality, the counting filter, the
  absent-depth caveat and the citation, and it carries over to `CENSUS-FORGET-20261114-001`.
- **Narrowing.** The bound for the 7 wrapper families is shifted.
- **Narrowing.** The target is a copy of S, and the argument does not cover another recursive definition with own distinctions; this
  carries over to CENSUS-FORGET and to rule A's reading in `FORGET-RULE-20261114-001`.
- **Narrowing.** The bounded search was tested on 57 families, not 66.
- **Narrowing.** "About 3%" is removed.
- **Not a block.** Wilson's upper end is 18.8%.

## Data

`experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/`, with the full run in `full/`
(`summary.json`), the gates in `gates.json` and `gate_relations.jsonl`, and the smoke in `smoke/`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the free-target bond | **Status:** Successful (refereed, confirmed with fixes) | P1 held (43 of 66 certified to grow with nothing chosen); P2 failed (no bounded certificate) |
| Local direction — counting inside | Continue | Genuine counting exists; its share and its cause can now be read |
| Broader exploration — G17 | Searching | The 21 non-forgetting families and the unsampled strata are open |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The law counts depth inside nested patterns with nothing chosen, proved per family |

**Corrections:** six (one Block, four Narrowing, one Not a block; above). **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** A79, A81 used.
**Basket:** `EVERY-RAY-20261113-001#2` (2/3 Payoff, 2/3 Concreteness), `EVERY-RAY-20261113-001#3` (2/3, 2/3),
`TRUE-BOND-20261113-001#2` (2/3, 3/3), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | How common counting with nothing chosen is | 2/3 — Substantial | 3/3 — Ready | Run the forgetting test (exact and cheap, all calls) on every census family with two or more SELF calls whose first ray grows, and on the 224 and the 657, with no sample → the census share of certified counters | Selected · awaiting go-ahead |
| 2 | The 21 that do not forget | 2/3 — Substantial | 2/3 — Testable | Per-depth boundedness with changing paths and members anywhere (the referee's counterexample shape), or a growth argument other than forgetting → each decided, or not | Alternative · after #1 |
| 3 | What makes every call forget | 2/3 — Substantial | 2/3 — Testable | From the 43 and the 21, a rule in the calls' port maps → stated and checked on #1's census | Alternative · deferred |

1. Payoff 2: a census-wide count of genuine counting. Concreteness 3: the test takes milliseconds per family. But forgetting alone
   certifies growth only with existence, which L_path gives here and the census's first-ray growth gives where the ray grows with no
   choice; for others, existence must come from the first ray.
2. Payoff 2: the open third. Concreteness 2.
3. Payoff 2: the cause. Concreteness 2.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
