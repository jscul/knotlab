# The advisor's review of the draft (claude-fable-5-2, extra-high effort)

No product-form model with no free signalling and CHSH above 2 turned up, and no step of Theorem K fails; the proof has gaps to write out, and H5 looks unnecessary. The larger exposure is in the hypotheses and the inventory, not the theorem. Everything "by hand" below is `unverified` (I have no shell); everything "read" was opened at the cited lines.

## 1. Theorem K

**No counterexample, and no failing step (by hand).** I re-derived the conclusion by a second route and it agrees. The gaps a referee will ask you to close:

- **Step 2.** The exact condition is Y·x = X·y at every record entry, not "Y/y = X/x (or Y = 0)". "The rest" depends on the policy at the other values, so the common profile needs one more line: vary the policy at a second v′ ∈ D and take the difference. The identity μ(v, u) = m_v k(u) holds only on columns where t_2 > 0.
- **Step 3.** The scaling "k = n on D′, k′ = m on D" needs μ not identically zero on D × D′. If it is zero, then either the D rows or the D′ columns carry no weight anywhere that counts, and the model reduces; say so.
- **Step 4.** "𝓜's reader-2 marginal is τ_N ℬ_N" needs the constant to be τ_N. It is, by evaluating Σ_{v∉D} c_v μ(v, u) at a column u ∈ D′. If D′ carries no weight, the scale of k′ off D is free and must be set by the total.
- **Step 5.** Fine.

**H5 is stated correctly but looks unnecessary.** The written proof uses it only to make k one profile for both b. The second route, as a sketch to check:

- Let N, N′ be the values with setting-free positive factor, K(u) = Σ_{v∈N} c_v μ(v, u), K′ likewise, and Z the weight of the N × N′ block.
- If Z > 0: K is nonzero on N′, which lies in both supports, so each D row is m(v)·K on every column that ever counts, each D′ column is n(u)·K′, and K = Z·n on D′, K′ = Z·m on D. The numerator is then Z·𝒜_D⊗ℬ_D + 𝒜_D⊗ℬ_N + 𝒜_N⊗ℬ_D + 𝓜 with total Z(1 + τ_D(a))(1 + σ_D(b)): your coin model.
- If Z = 0: the N rows or the N′ columns carry no weight, and what is left is rank one on each setting pair's rows and columns, a product table with each factor depending on its own setting.

**Checks for H5.**
- `pr_example` (the FORBID-EDITS 4): with the sender's setting equal to its own second value q and the other reader at 1, s = 0 always, against uniform at a fixed setting. Change 1/2.
- The referee's 9/4 variant (three completions for a right guess, one otherwise; H5 holds): same policy, change 3/16 at 1 and 1/16 at 0.
- Rerun `checks.py random` without lines 148–149. First fix `sig`: it returns `None` for the whole model when one policy has zero total (line 138); skip that policy instead. I expect zero quiet models.

**The random check's power is not shown.** It reports 0 quiet among 254 above 2, but not how many quiet models with D, D′ and the N × N′ block all carrying weight were drawn at all. Report that count and their largest CHSH, in exact fractions.

**Scope.**
- K survives A226's challenge: normalising per setting multiplies t_1(1, ·) by a constant, which changes no fixed-setting table, so K applies to the rescaled model.
- K is proved for two readers with two settings. Row 50's "Mermin win 1" (`pr_three`) is not covered.
- K gives no size for the signal, unlike LOCAL-EDIT-POLICIES' "δ forces at least δ".

**Known?** I know no statement of it, and could not search the literature. Closest, from memory:
- Local rejection as factorisable measurement dependence: Pearle 1970; Gisin and Gisin 1999; Hall 2011.
- Fair-sampling conditions: Berry et al. 2010; Orsucci et al. 2020. K reads as "setting-dependent acceptance only on a part uncorrelated with the other side".
- Wood and Spekkens 2015 on fine-tuning. The memory loophole (Barrett et al. 2002) is a different question.

## 2. Rows

| Row | Finding | Source read |
|---|---|---|
| 13, 14, 60 | Patterns with no state of the whole: outside H1 by the README's own "What H1 excludes", yet classed (c) and counted in "none fits none". | `FOUR-READINGS-20261120-001A/results.md` 3, 42, 99–103 |
| missing | NO-WHOLE-STATE part A: CHSH 4 by part counting, three-reader win 1, square 1; part C's 64 of 64. | its `README.md` 40–42, 69–71 |
| missing | Its referee's CHSH 14/5 (a Bell state, Z and X against (4Z ± 3X)/5). | `referee-R1/report.md` 47 |
| missing | EVENTUAL-R part C: three-reader value 4 against 2. | its `README.md` 81–83 |
| 4–6, 11–12 | Settings are distinctions of one state. H1 ("one finished structure per pair of settings") and the free-sender definition do not apply; (c)'s defining sentence does not cover an ordinary counting with supplied settings. | wording only |
| 41, E6 | No birth depends on both settings; the first record simply holds zb. Counterexample to "without separate responses some birth depends on both settings". | `TWO-COUNTINGS-20261125-001/definitions.md` 149 |
| 23 | Three readings, not one (sq) row. The coherent one stays at zero under the adaptive script; uniform and doubled-weight matching are a central rule and signal (1/4 and 1/3 adaptive; 1/2 and 7/12 in sweeps). | `TWO-KNOTS-ONE-DECISION-20261121-001A/results.md` 16–17, 32–36, 43 |
| 37–38 | "Hidden" is for the four-value record. The second observer's setting moves (s1, s2), which the first observer's knots hold, by 1/3 at fixed settings; under FORBID-EDITS' fuller record this row is (a·open). | `SETTING-AS-REREAD-20261123-001A/result.md` 32–34 |
| 51 | Signalling cell is "—"; K applies (3/16 above). | by hand |

Also in the README:
- "Counted from the start every one of them is exactly 2" fails for the FORBID-EDITS 4: counting from the start is undefined under rejection, and renormalised it is the finish (definitions 3.2, 3.4), still 4.
- "Half the sign assignments" is 128 of 512, half of the 256 above 2 (`TWO-COUNTINGS-20261125-001/referee-R1/report.md` 26).
- "59 tables" counts row numbers (there is no row 47), and several rows hold up to six values.
- The 20–22 November squared-weight studies are not classed one by one. I did not open them: NEWBORN-TABLES, CALIBRATIONS-CLOCKS, SPLIT-KNOT-METER, SHARED-DONOR, FOUR-READINGS B, THREE-READERS B, TWO-KNOTS B.

**H2 failure in a kind-(a) row: none found.** Setting knots take x1 with x2 or x3 and records are (x1, x2, x3, za) (definitions 4.1–4.2). Option c is outside the record but forced opposite to x1, so its factor is constant. REREAD-BIRTHS and ONE-PARENT-REREAD were not opened.

## 3. The 9/4

The claim is right for the actual table. Tables (7/8, 0, 0, 1/8) three times and (13/16, 1/16, 1/16, 1/16) give correlators (1, 1, 1, 3/4) with each single value 1 at chance 1/8. The TLM test is necessary for any quantum table whatever the marginals; 3π/2 − arcsin(3/4) ≈ 3.864 > π.

One thing for the surrounding text, by hand: the four-type 20/9, rebuilt from `REVIEW-LEADS-20261123-001C/result.md` 53–56, has correlators −5/9, −5/9, −5/9, +5/9 with fair single values. 4·arcsin(5/9) ≈ 2.36 < π, so at fixed settings that table is inside the quantum set. For kind (a), then, only the free sender tells such a table from a quantum one. Check on the 18-knot tables.

## 4. The A240 consequence

Overstated as worded. It holds under exactly these:

- two readers, two settings;
- H2 for the declared records;
- a keyed setting read by pooling (A226, not cited in the README) or normalised per setting;
- signalling read in the complete declared record;
- a sender that keys a birth to a value.

The last lies outside H0, and the record already says so: "no knot gains a distinction, and no value changes a birth", and the stop rule "was applied to a sender ordinary growth cannot be" (`REVIEW-LEADS-20261123-001E/result.md` 48, 72–75). Write "would signal to anything able to key a birth to a value". The whole-stage 9/4 is the same under both countings (`claim.md` 73–75) and signals to a free sender under both, so the preference for counting from the start holds for kind (a) only.

## 5. Squared-weight rows

None found outside the quantum set or signalling, where the table is the squared-weight chances of one state with each reader's questions on its own distinctions. That is by construction, so say so. Qualifications:

- Row 23, as above.
- Rows 15, 22, 44, 46 have no signalling test recorded, and row 16 says "no sender test". "Signals under no test" should read "none recorded beyond fixed settings".
- Row 59 is conditional on a flag fixed before the settings.
- The counts-of-pairs statement covers the positive uniform preparation with real questions (`FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/results.md` 3, 25). Rows 43–44 use a signed law or a quarter-turned question and are not covered as recorded.

## What a referee would press first

The classification's force comes from A296, a sender outside H0; then H1 against rows 13, 14 and 60 and the missing rows; then what "complete record" means.

I added one consultation entry and one standing fact (the keyed sender and the two meanings of a complete record) to the hivemind. The file had changed on disk since I read it; both edits applied cleanly.
