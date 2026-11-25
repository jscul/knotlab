# Changes from the first version, item by item (the advisor's `reach_advisor/answer.md`)

One line per item. "Applied" = applied as worded; "applied with a change" says the change; "not applied" says why. KD =
`definitions_v2.md`, PR = `preregistration_v2.md`, claim = `claim_v2.md`.

## Section 16, required, in order

1. History count, roster count, M removed — **applied**: claim §1 says "The count is of the growth's history, not of what exists at one round" and "1 from the rounds"; KD 2.1, 2.2 (H and P under two names, never added); M and member-class final readings withdrawn (KD 2.2, 2.3).
2. One gate — **applied**: KD 4.1 (two-sided bound on one common range, every knot examined, k of K, 3/k), KD 4.2 (scaling condition), made knots near s_min/2 (KD 2.3); with a change: 8 per class in run 1 and 64 per class in run 2, where the gate is read, to fit the hour.
3. Exact reading primary, 0.3 as swap, OUTGROWS replaced, precedence — **applied**: KD 3.2 (also on b(t)), 3.3 (LINREC), 3.4, 3.5 (RATIO), 3.6 (precedence with a final-segment rule), 3.7 (swap, disclosed as the reading first used, the trimming rule stated).
4. Growing end — **applied**: |γ| beside |κ| and the headline rule (KD 5.8), strata (5.7), concordant/discordant/tied with Kendall's S and its exact permutation reference (5.6), integers (5.2), fixed directions (5.6); with a finding against the advisor's guess (section 8 below).
5. Knot test — **applied with a change**: every start knot; every knot of every stage in run 5; in run 4 every knot of the structure after round 25 only (testing rounds 50 and 100 too does not fit an hour; PR run 4); a seeded sample of 200 knots per run with the cited argument for runs 1 and 2; the advisor's wording exactly (KD 6.3).
6. C6 and "past its start" — **applied**: C6 dropped (claim §3, with the reason); δ = ∞ needs past its start (KD 5.5).
7. C3 and P11 — **applied**: 100 rounds, readings at 25, 50, 100, the base law at the same round, the four steps, "held by hubs" with the doubling-knots condition, "ALL WITHIN r" as the stage verdict (claim 3, KD 2.6, 1.7). The rescaled scratch run already contradicts the first version's P11 (PR, disclosure).
8. Definitions and symbols — **applied**: checks E, F, R, N, P, I defined (KD 7.4, named by letters, not C1–C6); L9 cut (claim §2, KD 7.1); uniform CARRY not defined, so CARRY runs under OLDEST only (T9, T10); IMPLIED closing stated (KD 6.1); name-free stage cap (KD 7.3); symbols renamed (KD 0).
9. P9, P8, C1, denominators, run 5 family — **applied**: P6 (old P9) with the closed form for odd n; P5 (old P8) needs a decided share; claim 1 no longer says "every start of the census"; denominators 3,344 / 3,376 (PR, files); run 5 on every census start, rounds 1 to 3, with the five-knot cost measured (0.35 s per start and law).
10. Controls and the table — **applied**: the comb as the gate's negative control (KD 8.5, counts checked), the branching structure under not-all-equal as the order test's positive control (8.6), a known tie (8.7); the start-by-start table registered (claim 1, PR run 1) and computed now (PR, disclosure).
11. Words of section 14 — **applied** (section 14 below).

## Optional

- Betweenness test — **applied**: it needs no new contraction (the pair readings already computed), so it adds no run time; computed now on the saved data (PR disclosure).
- Parity rules on loose distinctions per stage — **applied**: KD 5.4 (Λ_t's dimension and least weight), claim 4, PR run 4; computed now on 64 runs.
- Exact numbering check — **registered** as run 4b; **not run and not timed** by the drafter, so its wall time is not stated; it runs only if run 0 shows a case finishing in under 10 s. This is the one registered run whose cost is unmeasured.
- With and without the 64 scratch starts — **applied**: `five_knot_order_v2.json` marks them (23 of the first 1,000 five-knot starts are among them); every share is reported both ways.
- Exception (i) — **not registered**, listed in PR with the advisor's reason; also (ii) and (iii).

## Sections 1 to 15, other points

- §1 the two critics — **applied** in claim §6 ("no limit object"; "the count depends on the knot counted from"; "the birth order read in both directions gives the roster's exponent plus one"; the step convention under hubs). Reading by chains and intervals is named as a later study, not registered.
- §1 "M is empty", "member centres have ℓ ≤ 0" — **agreed and applied**; my scratch M was computed only from members as a stage reading, never as a final reading, but the first version's text registered it wrongly.
- §2 "uniform doubling alone does not fix D" — **applied**; the doubling reading is now a swap only.
- §3 Ring(33, 2) blur, C(r+3,3) at 13, the trimming of a run that starts before 4 — **applied**; the disclosure corrects "14" to "13".
- §4 hub swaps for run 4 — **applied** (KD 1.7).
- §5 R: s = round with FILLERS, joins of three, closings — **applied**; sandwich as the triangle inequality with a connected start — **applied**; "verdicts follow the record's kinds" only where proved — **applied**; L8 qualifies for R — **applied**; F covers N and HOLD, not M — **applied**, and the 325 checks are said to have covered H only; N "E under the stage weighting", K depends on λ, (1 − K)/2 not a share — **applied** (the share ρ_K is dropped); P "connected holder graph, barred counted as loose" — **applied**.
- §6 bare ring: odd n ≥ 5, two-apart order, N = n(2r + 1) for r ≥ n, step 3n − 1, r ≤ round and ≤ ℓ — **applied**; checked against my saved counts (26 then 18 for n = 9; 44, 30 for n = 15; 62, 42 for n = 21: the advisor is right and my first version was wrong). The even-n remarks are **taken on the advisor's word, not checked**; only odd n are registered. The advisor's honest sentence is used in claim 2.
- §7 the table — **applied and computed** (PR disclosure).
- §8 "the smallest case compares offshoots with a four-parent join, so loose counts are the likely driver" — **applied as a rule, but the guess is not borne out**: all three members of census start 157 after round 1 hold two loose distinctions each, so the disagreement there is among pairs with equal loose counts, and it survives |γ| (PR disclosure, exact counts). In the pooled data, though, most discordance under |κ| is removed by |γ| or by equal loose counts (17,448 → 5,438 and 201 under ORDINARY), so the advisor's caution is right in aggregate.
- §8 "ρ is always a pseudo-distance" — **applied** in claim §1.
- §8 "use no 'random'" — **applied** in the drafts' own words; `random.Random` remains as the name of the generator in seeds.
- §9 knot test — **applied** (item 5 above).
- §10 ±2.6 points and 8 or more — **applied** in PR; golden eddy k = 5 — **agreed**, disclosed as a correction; effective sample size for the labelled reweighting — **applied** (to be stated with each labelled share).
- §11 names still entering — **applied** (KD 2.3, 7.2, 5.9); "four seeds cannot check" the uniform-takes statement — **applied**: run 4b checks it exactly; run 4 keeps 2 seeds as a sample of runs, not as a check.
- §12 every point — **applied**: m when growth has ended (KD 2.4); δ under HOLD in an "ancestor" stratum and undecided at the knot bound (KD 5.5); SATURATED replaced by ENDED and, for stages, ALL WITHIN r; "commonest verdict" and "growing" removed; P4 replaced by Lemma E's identity; "common range of at least 32" is now z ≥ 32 as the endpoint with z ≥ 8a; L-W's non-vacuous stages; T1–T10 as ten labels; symbol collisions removed (KD 0).
- §13 predictions — **applied**: engine checks separated; replication marked; P5 needs a decided share; P9 (now P9) and C3 rescaled; old P19 and P20 turned into registered questions; P6, P7 fixed; old P18 limited to the laws run; the missing predictions added (P2, P3, P8, the controls). **Against the record of my own data**: the old P16 (no disagreement under COPY-LAW(RETIRE)) was vacuous, since every comparison in stratum (i) is tied in δ; the new P13 says so.
- §14 words — **applied**: "steps from the start", "the count within r holder steps", POWER(j) kept (never for a test's strength); OUTGROWS replaced by RATIO(x) on [a, z] (the advisor kept the word with a range and suggested the ratio form; I took the ratio form); "kept range", "the knot counted from", "counted from", "greatest steps within the start", "the between-knots reading γ", "the same power from every knot examined"; "dimension" only for the target; literature's names once and marked; "to depth d", "draws", "grows above every power", "how far apart", "rate" in three senses, "spaces of one dimension" removed; "counterexample" kept (an ordinary word, not "counter" as a thing that counts); the weave control marked drawn and hand-built.
- §15 sentences for the owner — **applied** at the end of the report, adjusted to what is registered; the blurs listed are removed from the drafts ("CAP-3 laws grow by powers", "nears 3", "for most small starts" without a weighting, "as the record already showed", "no graded reading at all" now limited to pairs, the owner sentence no longer states results before the runs).

## What changed in the files

`claim_v2.md`, `definitions_v2.md`, `preregistration_v2.md` rewritten; `survey_v2.md` with small changes (a quoted word, the parity statement's standing, the cap's chains, the denominators); new data files `named_starts_v2.json` (controls added, odd bare rings), `five_knot_order_v2.json`, `data_table7_v2.jsonl`, `data_c3_v2.json`. The first versions are left in place.
