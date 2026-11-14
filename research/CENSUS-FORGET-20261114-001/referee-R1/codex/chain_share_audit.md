# R1: chain definition and census shares

**Verdict: the arithmetic reproduces; the broad growth interpretation does not follow from it.** The stated 7,251/13,279 and 7,251/223,261 totals reproduce from recorded verdict labels and the broader 5,190-family chain filter. They are not thereby proved counts of all-copy growth: the lead's separate target-type check has counterexamples. The literal one-definition filter gives 4,035 families / 4,478 draws. Prefix-restricted `L_ray = L_any` is false for the counted class; the weaker lower-bound transfer survives. No new proof of the supplied first-ray or forgetting verdicts is claimed.

This is an offline, independently authored, same-task referee recount (V2), using only permitted data and prior referee material. Producer Python under FREE-TARGET and CENSUS-FORGET was neither opened nor imported. All writes are confined to the three assigned chain-share files. No Git mutations, publication, network calls, or subagents were used.

## Recorded strata

A family here is a distinct description key; draws retain multiplicity from the raw REACH census. The raw keys reconcile exactly: 124,572 family rows, 223,261 nested draws, and 12,772 first-ray-growing families / 13,279 draws. Every current result is present exactly once and has runner status `ok`.

| Stratum | Families | Draws | Forgetting certified, families / draws | Non-forgetting, families / draws | Capped, families / draws |
| --- | ---: | ---: | ---: | ---: | ---: |
| chain | 5,190 | 5,633 | 4,223 / 4,526 | 967 / 1,107 | 0 / 0 |
| c>=2 | 6,925 | 6,989 | 1,080 / 1,080 | 5,779 / 5,843 | 66 / 66 |
| c=1 other | 657 | 657 | 538 / 538 | 119 / 119 | 0 / 0 |
| nonchain | 7,582 | 7,646 | 1,618 / 1,618 | 5,898 / 5,962 | 66 / 66 |
| all | 12,772 | 13,279 | 5,841 / 6,144 | 6,865 / 7,069 | 66 / 66 |
| one-definition limit-only | 224 | 224 | 0 / 0 | 203 / 203 | 21 / 21 |

## Headline arithmetic and nominal Wilson intervals

| Recorded weighted quantity | Exact fraction | Percent | Nominal 95% Wilson interval |
| --- | ---: | ---: | ---: |
| Chains + certified nonchains / first-ray growers | 7,251 / 13,279 | 54.605015% | 53.756996%–55.450372% |
| Certified nonchains / nonchains | 1,618 / 7,646 | 21.161392% | 20.260459%–22.091288% |
| Certified c>=2 / c>=2 | 1,080 / 6,989 | 15.452854% | 14.624441%–16.319224% |
| Certified c=1 nonchains / c=1 nonchains | 538 / 657 | 81.887367% | 78.759873%–84.644139% |
| Chains + certified nonchains / all nested draws | 7,251 / 223,261 | 3.247768% | 3.175039%–3.322107% |

These are exact observed fractions. The intervals are the requested binomial Wilson calculations with z = 1.959963984540054; the audit does not reconstruct or validate the description-weight sampling model. Distinct-key Wilson calculations in the JSON address a different weighting. `reading.json` agrees at its stated four-decimal precision in every tested stratum, share and interval.

The 7,251 combined draws consist of 5,633 chain draws and 1,618 certified nonchain draws. They are not the forgetting-certificate total: that is 5,841 families / 6,144 draws. Some chain families fail the forgetting test and retain their separate inherited chain-growth argument. The complement of this original label aggregation is 6,028 first-ray-growth draws: 5,962 non-forgetting and 66 capped. Their members-anywhere growth is undecided by this test. The target-type scope exclusions below remove another 188 draws from the conditional conservative tally.

## What the chain count means

The reproducing filter expands every earlier numeric call, preserving each occurrence and the definition identity of each `SELF`. Both S and main must then have exactly counter `{S: 1}`. This permits finite helpers, wrappers, and unused definitions. It is broader than the preregistration's literal 'one definition, one SELF call': 1,155 counted families / 1,155 draws have multiple definitions. The claimed 5,190 / 5,633 count needs this actual filter stated.

The 657 `c=1 other` rows are the complement of chains among one-SELF rows. Of them, 489 have `other_holding_calls=true` in the used expansion of S or main. The other 168 have only the S recursive type but multiple entries from main. The JSON records exact occurrence-counter splits. Thus 'one SELF call and other self-holding calls' needs to include additional entries from main and must not be read as 'another recursive type in S'. The independently derived `chain`, c, n_defs, and used-expansion other-type flags match every recorded result.

Among the counted chains, 15 families / 15 draws have at least one absent prefix ray bond in the 30 recorded depths; 12 families / 12 draws still do after depth 20. Literal one-definition chains account for 0 such families / 0 draws. There are 17 chains with a recorded decline, including 2 with a finite-to-finite decline. These are retained in the JSON; absence is not a zero-sized bond.

The prior referee's counterexample is freshly re-enumerated. Its three successive constraints are `NAE(a,b,c), NAE(b,c,d), NAE(c,d,e)`, with c,d,e introduced at depths 1,2,3. No prefix-only bond through depth two contains root a and depth-two d. Yet `{a,b,d,e}` is a four-member bond: exactly `0011` and `1100` are forbidden, and every deletion leaves all eight states. Every allowed prefix extends infinitely. This counted family therefore has `L_any(2)<=4` while `L_ray(2)` is absent. Equality is false for the counted class.

A finite bond reaching depth s also reaches the greatest introduction depth d of any member, and qualifies for prefix-only `L_ray(d)`. Therefore the replacement is

```text
inf_{d>=s} L_ray(d) <= L_any(s) <= L_ray(s).
```

An inherited uniform positive linear lower bound on finite ray minima transfers to every finite members-anywhere minimum. When ray minima are eventually finite at every depth and equal `lambda*s+O(1)`, the same asymptotic rate follows. At-depth existence remains a separate premise. The census conclusions already qualify their lower bound by 'at depths where a bond exists'; keep that qualification and do not use the false equality as its proof.

## The 224 limit-only rows and r

Reconstructing one-definition limit-only growth rows from raw draws (`fate != forever`, `limit_alive=true`, at least two SELF calls) gives exactly 224 keys / 224 draws: zero certified, 203 non-forgetting, 21 capped. The heading 'never forget' overstates this: the 21 capped cases remain undecided for forgetting. A failed forgetting test does not imply bounded members-anywhere bond size, and no claim that the growth is absent follows.

| r | Certified families, all / nonchains | Certified draws, all / nonchains |
| --- | ---: | ---: |
| 1 | 128 / 17 | 128 / 17 |
| 2 | 1,431 / 334 | 1,444 / 334 |
| 3 | 2,512 / 633 | 2,603 / 633 |
| 4 | 530 / 243 | 542 / 243 |
| 5 | 1,068 / 286 | 1,255 / 286 |
| 6 | 116 / 67 | 116 / 67 |
| 7 | 27 / 18 | 27 / 18 |
| 8 | 8 / 7 | 8 / 7 |
| 9 | 5 / 5 | 5 / 5 |
| 10 | 3 / 2 | 3 / 2 |
| 11 | 12 / 5 | 12 / 5 |
| 12 | 1 / 1 | 1 / 1 |

All reported family r distributions reproduce exactly; the JSON additionally gives weighted r distributions and every stratum. No recorded empty relation occurs. All 66 caps report the 250,000-product construction cap, so 'none found up to a tested r' is not their recorded stopping reason.

## Outside EVERY-RAY's selected sample

After replacing the 28 matching phase-two sample rows, G contains 300 keys / 303 raw draws. Excluding all of them from c>=2 leaves 6,625 keys / 6,686 draws. Certified successes are 1,036 keys / 1,036 draws: **15.495064%**, nominal Wilson **14.647534%–16.382222%**. The preregistered 8%–25% band holds. The exclusion removes 44 certified keys / 44 draws, rather than just the 43 certified path growers: one further certified key was unresolved in the path computation.

The refreshed sample has 208 path-bounded, 66 path-growing and 26 unresolved families. Its 208 bounded rows contain no forgetting-certified family; 43 of the 66 growers and one of the 26 unresolved rows are certified. This is a consistency check, as preregistered, and not independent proof of the growth argument.

## Supplemental restricted arithmetic

**Conditional conservative lower tally: 7,063 draws.** The lead's separate `target_inventory.json` identifies 186 certified nonchain draws with own distinctions in another reachable recursive type: 33 among c>=2 and 153 among c=1 nonchains. Another two have a zero-own recursive type that can take arbitrarily many SELF steps before calling S, creating deep S targets without corresponding S transitions. There are eight delayed-S cases in total, six overlapping the first exclusion. Direct checks in the lead's lane found bounded counterexamples from both excluded classes. This lane reconciles the supplied inventory totals with its raw strata but does not independently repeat that structural inventory or its SAT checks.

Excluding all 188 leaves `5633 + 1046 + 384 = 7063` draws. The sufficient scope condition is that every deep own target has S-only recursive ancestry after main's finite expansion: other reachable recursive types neither introduce own distinctions nor delay later S targets. Subject to the corrected chain and gap arguments, this is a conservative lower tally, not an exact incidence of all-copy growth. The 6,216 first-ray-growth draws outside this tally include both undecided cases and counterexamples; they are not all established nongrowers.

Of first-ray-growth draws: **7,063/13,279 = 53.189246%**, nominal Wilson **52.339754%–54.036894%**.

Of all nested draws: **7,063/223,261 = 3.163562%**, nominal Wilson **3.091762%–3.236974%**.

## Provenance and limits

Run: `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/CENSUS-FORGET-20261114-001/referee-R1/codex/chain_share_audit.py`. Inputs and audit code have SHA-256 hashes in `chain_share_audit.json`. The script compares complete raw key sets, independently derives structural strata, streams every draw and result, checks nominal intervals, re-enumerates the finite counterexample with rejection controls, and verifies all reading.json totals requested in this lane. It uses one compute process with a 2 GiB address-space ceiling.

Certificate soundness, exact limit relations, the general gap proof, target-type scope, depth shifts for wrappers, and re-proving the inherited census graph analysis are outside this numerical lane. The combined 54.6% and 3.25% reproduce the original label aggregation; the lead's counterexamples prevent reporting those values as proved all-copy-growth shares. They are observed certificate-label-and-chain yields under recorded description weight, not exact probabilities over all nested patterns or the full share that truly grows.
