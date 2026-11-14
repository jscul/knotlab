# How common certified counting inside is

Epic `CENSUS-FORGET-20261114-001` (`FREE-TARGET-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead.
Pre-registered in 1c416df97 (objects gate passed; advisor consulted). FREE-TARGET's exact forgetting test and audit (Codex's code,
unchanged) run on the shared runner from the thread's `job.py`. The canonical K1–K3 test is unchanged. The gap argument
was confirmed by FREE-TARGET's referee (04e2b87dc). Refereed by the referee thread with Codex (CENSUS-FORGET-R1,
`referee-R1/report.md`, commit 1af7939f1): **confirmed with fixes, two Blocks**. The shares barely move, but "any copy" is restricted
to the targets the certificate covers. All fixes are folded in below and logged.

## Words

As in FREE-TARGET:
- **Certified to grow**: some r with every product of r per-call port relations rectangular. Then at every depth s where a bond
  exists, every bond from a top port to **any** copy at depth s, members **anywhere**, has at least 2 + ⌊s/r⌋ members. A bond exists
  wherever the first ray has one (L_any ≤ L_ray).
- **Chains**: one SELF occurrence in S and in main and no other self-holding call (finite helpers and a wrapper main allowed; the
  literal one-definition class is 4,035 of the 5,190), so there is one copy of S per depth and no side copy. ~~Then L_any = L_ray.~~
  *Corrected after FREE-TARGET's referee:* the free bond may use members below its target, so only
  inf_{d≥s} L_ray(d) ≤ L_any(s) ≤ L_ray(s) holds, which transfers the first-ray growth wherever a bond exists.
- **Weight**: the share of draws (A79).

## The question

Across the census, what share of the families whose first-ray bond provably grows is certified to grow with nothing chosen?

## The question in standard terms

For each of 12,772 iterated hyperedge-replacement NAE families, whether the semigroup of its per-call 8 × 8 port relations becomes
rectangular, weighted by the description weighting.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The test is exact and checked.** All 12,772 first-ray growers finished (3 minutes, 0 errors): 12,706 decided exactly, 66 capped (*separated after the referee*; the sampled capped ones are all non-forgetting). The referee's fresh code reproduces the verdicts on 127 families (all 318 relations, all 103 completed verdicts). The independent audit re-derived every certified family's relations and certifying products: 5,841 families, 0 mismatches. FREE-TARGET's 66 reproduce (43 certified, same r in all 66). No certified family is bounded over paths in EVERY-RAY's 300 sampled growers, a consistency check. No empty relation occurs. | computed | G passed |
| 2 | **Among the non-chains, certified growth is a minority, but not a small one.** Of 7,646 non-chain draws, 1,618 (21.2%) are certified. That is 1,080 of 6,989 with two or more SELF calls (15.5%; Wilson 14.6% to 16.3%) and 538 of 657 with one SELF call and other self-holding calls (81.9%). 5,962 (78.0%) are certified non-forgetting (a recurring non-rectangular product) and 66 capped. Outside EVERY-RAY's sample, the c ≥ 2 share is 15.5% (14.65% to 16.38%). | proved per family (conditional) | P1 held (8% to 25%) |
| 3 | **Together with the chains, half the first-ray growth weight.** *(Shares restricted after the referee; see the end of the cell.)* The chains' first-ray growth transfers to the free bond through inf_{d≥s} L_ray(d) ≤ L_any(s) (*not* by construction, corrected after FREE-TARGET's referee): 5,633 draws (42.4%); 15 chains have depths with no ray bond, 12 of them beyond depth 20. With the 1,618 certified non-chains, 7,251 of the 13,279 first-ray growth draws (54.6%) grow with nothing chosen, at every depth where a bond exists. That is 3.25% of all 223,261 nested draws. *Corrected after the referee (Block):* the certificate covers depth-s targets in copies of S whose ancestry consists of S calls, not "any copy". It does not cover (a) copies of another recursive definition with own distinctions (in 153 of the 538 certified single-call non-chains), or (b) a delayed S, called by another recursive definition after its own self steps (8 certified non-chains, 6 of them among the 153). There the bond can really be bounded: in 5 certified families with main = S a direct search finds a least bond of exactly 3 at every depth 1 to 11, against a claimed 4 at s = 6 (for example f25a8e17968d, where another definition T keeps a main distinction and a local of S together, so a three-member set is a bond at every depth), and the delayed-S family e8ce853eb78a gives 3 at s = 1 to 6 against 4. The covered subtotal is 5,633 + 384 + 1,046 = **7,063 draws: 53.2% [52.3, 54.0] of first-ray growth and 3.16% [3.09, 3.24] of all nested draws**. My interim figure before the referee (209 draws outside the scope, 53.0% covered) used a looser criterion and missed delayed S; the referee's 188 replaces it. The 661 wrapper certificates (main ≠ S) take 2 + ⌊(s − 1)/r⌋. The rest of first-ray growth (45.4%) is undecided here, almost all of it certified non-forgetting. | proved per family; chains by transfer of first-ray growth | reported |
| 4 | **None of the limit-only growers is certified.** *(Reworded after the referee from "never forget".)* None of the 224 one-definition limit-only growers of `PROVED-RATE-20261113-001` is certified (203 non-forgetting, 21 capped). The census's growth there is not counting with nothing chosen by this test. | computed | reported |
| 5 | **r is small.** Certified families have r = 1 (128), 2 (1,431), 3 (2,512), 4 (530), 5 (1,068), 6 (116) or 7 to 12 (56), so the lower bound gains a member every one to six levels in almost all of them. | computed | reported |

## Answer

About half of the census's first-ray growth weight is growth the law makes with nothing chosen: 53.2% (7,063 of 13,279 draws)
counted conservatively over the targets the proof covers, copies of the recursive definition reached through its own calls. In
those, every bond from the top to such a copy at depth s needs a number of members rising with s, wherever they sit. Four fifths of it
is single chains, whose first-ray growth transfers to the free bond (the program's earlier ruler, `LOGIC-AXIS-20261107-001`). The rest
is families with several ways down, every one of which forgets. Among families with two or more self-calls only about one in six
forgets, and none of the limit-only growers that started this line is certified. As a share of all nested patterns under the
description weighting it is 3.16%: a definite, uncommon kind. Where another recursive definition offers its own copies as targets,
the bond can stay at three members at every depth, so the restriction is real. *(Corrected after the referee.)*

## Reading

**Interpretation, not a theorem.**
- **Counting inside, by weight.** The law counts depth inside a nested pattern with nothing chosen in about one draw in thirty of the
  whole population. That is about half of the patterns whose first ray grows. It happens mostly where the pattern is a chain, and
  otherwise where every way down forgets.
- **Where it does not.** The undecided half is mostly certified non-forgetting: some way down keeps a correlation between its ends.
  Such families may still grow (FREE-TARGET's 21 were undecided), or be bounded at every depth along paths that change with the depth
  (EVERY-RAY's counterexample shape).

## Lag cutoffs and census-only claims

The 12,772 census families with a provably growing first ray (13,279 of 223,261 draws), a selected population: the share is over
them, or over all draws where stated. Per depth, at depths where a bond exists. No claim about families whose first ray does not grow,
or about the undecided half.

## Review

**CENSUS-FORGET-R1**: confirmed with fixes, two Blocks (the target scope; the chains' justification, already corrected after FREE-TARGET's referee and confirmed here), three Narrowing and one Not a block, all folded in. The advisor model reviewed the design cold (`advisor_review_answer.md`); its points were adopted.

## Literature and provenance

As in FREE-TARGET (rectangular powers; BRANCH-DEPTH's gap argument generalized). Ours: the census-wide count.

## Workspace assumptions

A79 used.

## Ratio

Substantive: 12,706 exact decisions and 66 capped. Administrative: the freeze, the job wrapper, this note.

## Corrections

Six, from the referee (`docs/CORRECTIONS.md`, 2026-11-14):
- **Block.** "Every bond to any copy at depth s" is restricted to copies of S whose ancestry is S calls. The covered share is 7,063
  draws (53.2%, 3.16% of all nested), with direct bounded counterexamples outside it. My interim 209 / 53.0% is replaced by the
  referee's 188.
- **Block.** The chains' "by construction" is withdrawn. It was already corrected after FREE-TARGET's referee and is confirmed here,
  with the 15 chains with missing depths.
- **Narrowing.** The 66 capped families are separated from the exact decisions.
- **Narrowing.** "Never forget" becomes "none certified".
- **Narrowing.** The 661 wrapper certificates take the shifted bound.
- **Not a block.** The objects gate's missing epic: FORGET-RULE is now named in the prior-work line.

## Data

`experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/`: `job.py`, the run in `full/`
(`results.jsonl`), and `read_census.py`, which writes `reading.json`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the census share | **Status:** Successful (refereed, confirmed with fixes) | P1 held; gates passed; 53.2% of first-ray growth weight certified over covered targets |
| Local direction — counting inside | Continue | The undecided half is mostly non-forgetting; a different argument is needed there |
| Broader exploration — G17 | Searching | Counting inside located by weight; its cause in the calls is open |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The share of patterns in which the law counts depth with nothing chosen |

**Corrections:** six from the referee (two Block, three Narrowing, one Not a block), logged in `docs/CORRECTIONS.md`. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** A79 used.
**Basket:** `FREE-TARGET-20261114-001#2` (2/3 Payoff, 2/3 Concreteness), `FREE-TARGET-20261114-001#3` (2/3, 2/3),
`EVERY-RAY-20261113-001#3` (2/3, 2/3), `TRUE-BOND-20261113-001#2` (2/3, 3/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What makes every way down forget | 2/3 — Substantial | 3/3 — Ready | From the 12,772 verdicts, a rule in the SELF calls' port maps and the knots on the ports (for instance: no port passed down by identity on any cycle of calls) → a syntactic criterion that predicts forgetting on the census, exactly or with stated exceptions | Selected · awaiting go-ahead |
| 2 | The non-forgetting growers | 2/3 — Substantial | 2/3 — Testable | On a sample of the 5,962 certified non-forgetting non-chains, members anywhere and any target with depth-dependent paths (the referee's counterexample shape) → bounded per depth, or growth by another argument | Alternative · deferred |

1. Payoff 2: the cause of counting inside, as a rule a reader can check by eye. Concreteness 3: the verdicts and relations are on
   disk; the search is over simple features.
2. Payoff 2: the undecided half. Concreteness 2: needs a per-depth members-anywhere method.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
