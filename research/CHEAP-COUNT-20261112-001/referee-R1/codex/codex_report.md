Confirmed with fixes

Independent code; no import or execution of `census.py`. All computations used the requested `.venv/bin/python`. Longest synthesis: 27.6 s; peak RSS: 437 MiB. UNSAT results use trusted SAT solvers, without proof-trace replay. No original records were changed.

## 1. S1: minima and enumeration

An independently encoded truth-table synthesis uses helper-assignment witness selectors, odd-extension covering clauses, a totalizer, and justified relabelling symmetry.

| Helpers f | Recomputed m*(f) | Negative check |
| --- | --- | --- |
| 0 | nonexistent | UNSAT with all 0 candidate triples available |
| 1 | nonexistent | UNSAT allowing all 6 candidates |
| 2 | nonexistent | UNSAT allowing all 16 candidates |
| 3 | 12 | UNSAT at ≤11; SAT at 12 |
| 4, 5, 6 | 10 each | UNSAT at ≤9; SAT at 10, separately for each f |

All positive witnesses were independently projected. Exhaustive enumeration gives **168 labelled minima**, **28 classes** under helper permutations alone, and **3 classes** under independent named/helper permutations, with labelled class sizes **24, 72, 72**. Helpers may be unused, as in the study's encoding. No numerical discrepancy; P1 holds.

## 2. Unrestricted helper count

**The ten-knot lower bound holds for every f**, with an argument and additional searches absent from the original study. From a hypothetical gadget with m≤9, repeatedly remove a degree-one helper and its sole triple, then discard unused helpers. This preserves projection: NAE(z,a,b) always admits z for fixed a,b. Remaining helpers have degree ≥2; all four names must occur because parity depends on each. Hence

`4 + 2f ≤ 3m ≤ 27`, so `f ≤ 11`.

Independent reduced searches at m≤9 are UNSAT for **f=7,8,9,10,11**. Together with S1 this closes the unrestricted claim. CaDiCaL 1.9.5 and Glucose 4 agree on selected UNSAT cases (f=3,6,11). The ten-knot/four-helper witness supplies the upper bound.

## 3. S2: growth and collisions

All five exact parity sequences match `s2.json` through 64:

| Rule | Alive depths in 1..64 |
| --- | --- |
| 60 | 1–6, 11–14, 27–30, 59–62 |
| 90 | 1–6, 10, 12–14, 28–30, 60–62 |
| 150 | 1–9, 12, 15, 20, 28, 30–31, 60, 63 |
| 102 | 1–2 |
| hop | 1–7, 9, 11 |

The strict NAE gadget construction, including equality copies at colliding slots, has exactly the same life through 64. Method: exhaustive local gadget/equality projections, disjoint-helper elimination, and enumeration of all 16 initial/reference assignments; additional whole-system SAT controls cover depths 1–8. This is not a claim of whole-system SAT through 64.

At depth 64, rule 60 has **10,116 used variables, 28,353 NAE triples, 128 copies**. Each copy adds eight variables and eight triples. Thus the stated per-position inventory describes the bulk gadget; boundary overhead is additional. G passes. Rule 102's permanent death after depth 2 also follows directly: each update adds one forced trailing relative zero, producing a forbidden terminal triple by depth 3.

## 4. Weight arithmetic and its meaning

For `L=gamma(h)+gamma(m+1)+log2 binom(binom(5(1+h)+1,3),m)`:

| h,m | Recomputed ideal bits |
| --- | --- |
| 3,12 | 105.6192715061 |
| 4,10 | 103.6268977752 |

`log2(504)−L(3,12) = −96.6419915826`, mass **8.08838×10⁻³⁰**. These are ideal self-information values; fixed-width subset ranks give integer lengths 106 and 104 bits.

The formula describes labelled local templates **conditional on the frozen growth decoder**, which already specifies initial width, global R, missing positions, closure and equality-copy repairs. Shared decoder conventions can legitimately cost zero per-template bits; the formula is not a shortest-description theorem across languages or counting constructions.

**504 is exactly the size of the distinct labelled 168-gadget × three-rule family.** With an all-depth counting justification for all three rules, it would be a lower bound on all counting descriptions. Without that justification for 90/150, it counts candidate descriptions. In either case, a small found-subset mass supplies no upper bound on total counting mass. The rarity/probability headline does not follow.

## 5. S3: mutation arithmetic and fragility

There are `binom(7,3)−binom(4,3)=31` admissible triples, hence **12+12(31−12)=240** changes. Independent projection and growth recomputation gives exactly **3 same-parity replacements, 169 constant prefixes, 68 eventually-constant prefixes**; every original mutant sequence matches through 64. There are 36 distinct projected relations. The constant prefixes split into 117 alive and 52 dead.

Using the original zero-based indices, the parity-preserving replacements are `j=6 → (1,3,6)`, `j=7 → (2,3,5)`, `j=8 → (1,2,4)`. Minimality already excludes parity preservation by any deletion and makes a successful replacement another minimum. It does **not** determine these three replacements or the growth classifications. P2's registered share is correctly **3/240=1.25%**; this is local mutation evidence.

## 6. What is known, constructed, or new

| Note conclusion | Classification |
| --- | --- |
| 1. Minimum gadget sizes | Substantive exact synthesis data; unrestricted lower bound completed here. General definability is known. External novelty of the exact minima is not certified. |
| 2. Counter/gadget agreement | Settled by existential composition once local projections and collision repairs are correct; S2 checks implementation. Additive algebra is known; this terminal-closure life predicate needs its own bridge. |
| 3. Astronomical rarity | Formula arithmetic is definitional; rarity and “among the rarest” are unsupported. |
| 4. Fragility | Mutation inventory is arithmetic; deletion obstruction follows from minimality; replacement and finite-life counts are substantive bounded data. |
| 5. Hopping failure | Substantive finite negative result under the registered criterion; no all-depth obstruction established. |

Standard background: Böhler–Reith–Schnoor–Vollmer, *Bases for Boolean co-clones* (2005); the accessible [author dissertation](https://d-nb.info/978707176/34), Figure 3.5, gives NAE₃ and EVEN₄ in the complementive co-clone. [Martin–Odlyzko–Wolfram, *Algebraic Properties of Cellular Automata* (1984)](https://www-users.cse.umn.edu/~odlyzko/doc/arch/cellular.automata.pdf) supplies additive polynomial methods, not a verified theorem here for this exact expanding-width/terminal-NAE condition.

## 7. Honest reporting

**P3's failure is reported honestly and explicitly.** The evidence is death at 12–64, not permanent death. Rules 90/150 are correctly labelled “unexplained” in the data: no tested period ≤16 starting by depth 32. “Count too” needs an explicit all-depth theorem for this closure. Independent extra calculations through 8,192 support further patterns but remain finite evidence, separate from the preregistered run.

## Fixes

- **Block:** Withdraw the rarity, approximately 10⁻²⁹ probability, and “among the rarest” conclusions; found-subset weight has the wrong bound direction for them.
- **Narrowing:** Replace unconditional “count too” and hopping “does not count” by the registered finite verdicts, or supply the missing all-depth arguments. Likewise qualify mutant “settling.”
- **Narrowing:** State the fixed decoder and distinguish ideal template bits, bulk gadget inventory, boundary overhead, and shortest complete descriptions.
- **Not a block:** Add the useful-helper reduction and f=7..11 UNSAT results; the unrestricted ten-knot bound is now supported.
- **Not a block:** Retain P1, P2, G and the explicit P3 failure; add the three isomorphism classes.

## Files written

All are in this directory; `brief_codex.md` pre-existed and was untouched.

- `codex_report.md`
- `s1_recompute.py`
- `s1_summary.json`, `s1_enumeration.json`
- `s1_f*_m*.json`: 20 per-case records, including three Glucose cross-checks; exact filenames are listed in `s1_summary.json`.
- `growth_mutations.py`, `growth_mutations.json`
- `weights_claims.py`, `weights_claims.json`

Reproduction: use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`; run `s1_recompute.py case --f F --m M` for the recorded cases (`--reduced` for reduced cases, `--solver glucose4` for cross-checks), then `enumerate` and `summarize`. Run `growth_mutations.py --phase PHASE --depth 64` for `projections`, `parity`, `mutants`, and `--phase algebra --depth 8192`; run `weights_claims.py`. Wrap synthesis invocations in `timeout 570`.
