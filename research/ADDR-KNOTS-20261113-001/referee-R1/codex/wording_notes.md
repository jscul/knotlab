# Wording audit: ADDR-KNOTS-20261113-001

One assertion about tail-independent internal knots is false. That blocks the asserted interpretation, not the numeric census. The sample findings remain reportable with explicit units, conditioning, and the level-12 boundary. No producer source or forbidden recheck script was accessed.

## Independently recomputed quantities

| Quantity | W | E |
| --- | ---: | ---: |
| Accepted draws | 28,770 | 19,416 |
| Distinct pattern hashes | 3,990 | 8,937 |
| Nonempty distinct hashes | 3,989 | 8,936 |
| All (hash, relative class) units | 3,997 | 8,952 |
| Nonempty (hash, relative class) units | 3,993 | 8,948 |
| Nonempty class units: finitary / bounded / polynomial / exponential | 27 / 146 / 152 / 3,668 | 18 / 292 / 195 / 8,443 |
| Nonempty draws: finitary / bounded / polynomial / exponential | 82 / 453 / 158 / 5,066 | 126 / 860 / 206 / 10,720 |

Bounded activity is 453/5,759 = 7.87% of nonempty W draw weight, versus 146/3,993 = 3.66% of nonempty W class units. In E it is 292/8,948 = 3.26% of nonempty class units. “A minority” is calibrated; “rare” has no registered threshold and should not hide the difference in denominators. Activity supplies an upper bound on joining and does not identify every description with actually bounded joining.

The raw W composition in conclusion 3 is correct: 17,768 actual one-state draws (61.76% of accepted draws), plus 5,243 empty draws with at least two states (18.22%). All 23,011 empty draws merge into one hash, whose least s is 1. Reading that merged summary count as the actual count of one-state descriptions would be a mistake.

The settlement figures use different rules. Each draw’s own description flags give 4,307 settled and 1,452 unsettled nonempty W draws; 314/1,452 = 21.63% of the latter are F2. The addendum inherits settlement from any description of the pattern, giving 4,604 settled and 1,155 unsettled draws; 314/1,155 = 27.19%. Either can be shown if labeled; the main frozen summary uses the second rule.

All 48 returning keys are F2. Of them, 25 are alive at level 12, 19 dead, and 4 undecided. The “1,812 that die” denominator counts keys; there are 1,808 distinct hashes with an observed death. The supplied Glucose vectors contain a decided dead-then-alive pair for every return, while leaving 26 level verdicts undecided in 12 records.

## False internal-tail assertion

The claim occurs at addr_knots.md:23 and proof.md:110. A two-state example from permitted raw key 26892553d70dde64fd0f6df06341a9b09b64775b66b5500709cc72af9778cfd7 has sw=[1,0], d0=[1,0], d1=[1,1]. The single placement consists of words (1,), (0,0), (1,0), composed right to left. At level 4, project each wholly internal knot by dropping its last two letters. Suffixes 00 and 01 have no internal knots; suffixes 10 and 11 each have projected triples {(0,1,2),(0,1,3)}. The original raw key includes two additional placements that contribute no level-4 triples; its recorded total of 14 agrees. Full finite fixture is in wording_audit.json.

## Fixes and exact proposed wording

### W01 — Block

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 23, 24.
- `proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces/proof.md` lines 109, 110, 111.

False for suffix length 2, already at level 4. Prefix action does not imply that the same triples remain internal to every tail class. The explicit fixture is in tail_counterexample.

Replacement:

> A map's action on a prefix is independent of the suffix, while its section determines the output suffix. Consequently both the subset of knots internal to a tail class and the knots joining it to the rest may depend on its tail.

### W02 — Narrowing

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 44.
- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 44.

3997 and 8952 are (pattern hash, relative class) memberships, not 3990 and 8937 distinct hashes. Relative activity is a property of a producing description and need not be unique for a hash. Bounded accounts for 7.87% of nonempty W draw weight, versus 3.66% of nonempty W class units; rare has no frozen threshold. These are minority frequencies, not an estimate of every pattern with actually bounded joining.

Replacement:

> Exponential relative activity is most frequent in this sample; bounded activity is a minority. Among the 5,759 W draws with a knot within levels 1–12, 5,066 (88.0%) are exponential, 453 (7.9%) bounded, 158 (2.7%) polynomial, and 82 (1.4%) finitary. Class-split counts use (pattern hash, relative class), allowing one pattern to occur in several classes: after excluding F0, exponential has 3,668/3,993 units in W (91.9%) and 8,443/8,948 in E (94.4%); bounded has 146/3,993 (3.7%) and 292/8,948 (3.3%).

### W03 — Narrowing

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 41.

The original numbers are correct when each draw is classified by its OWN description flags. Under the addendum and frozen unsplit pattern summary, any description can settle its pattern; this gives 4604 settled and 1155 unsettled draws, with 314/1155=27.19% F2. Do not call the raw description arithmetic wrong; disclose its different unit or use the frozen pattern rule. The 61.8% actual one-state and 18.2% other-empty components are independently confirmed.

Replacement:

> Among the 28,770 accepted W draws, 17,768 (61.8%) have one state map and place no knot; 5,243 more (18.2%) place no knot within levels 1–12. Among the 5,759 draws with a knot, 5,430 (94.3%) are alive at every level read, 314 (5.5%) have an observed death after an alive knotted level, and 15 (0.3%) are FU. Using the addendum rule that any description can settle its pattern, 4,604/5,759 (79.9%) are settled; among the remaining 1,155 draws, 314 (27.2%) are F2.

Alternative preserving the raw-description measure:

> Here settled is evaluated on each sampled description itself, rather than inherited from any description of the same pattern as in the frozen summary:4,307/5,759 (74.8%) are settled and 314/1,452 (21.6%) of the rest are F2.

### W04 — Narrowing

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 52, 53, 54.
- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 147, 148.

Exact activity provides an upper bound, not a lower bound on actual joining. Class averages at levels 10–12 do not establish every-level growth for individual patterns. Nonempty W exponential key cb20b8fe2c4262bab1f0cf6a4b0124c0f082e6e72267baf75842775b08776d97 has J = [0,4,4,4,4,4,4,4,4,4,4,4]. Eleven exponential nonempty W draws satisfy J10 = J11 = J12. State the sample, conditioning, and finite-level boundary.

Replacement:

> Among accepted W draws with a knot within levels 1–12, exponential relative activity is most frequent (88.0%); bounded activity accounts for 7.9%. In the exponential class the mean measured joining count nearly doubled from level 10 to 11 and from 11 to 12. Activity bounds joining from above, so these data do not show that every exponential description has growing joining, or that the observed growth continues beyond level 12.

### W05 — Narrowing

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 17, 18.
- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 45.
- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 55, 56.

F1/F2 record an observed dead level; neither means permanent extinction. All 48 returning keys remain F2,25 are alive at level 12,19 dead,4 undecided. Late first deaths were observed only in exponential-class descriptions, which is a finite-sample association, not necessity of actual exponential joining.

Replacement:

> Within levels 1–12, F1 means dead at the first level with knots; F2 means alive at a knotted level and dead at a later knotted level; a return is a separate flag. Neither F1 nor F2 asserts permanent extinction. All observed first deaths at levels 9–12 were in descriptions of exponential relative activity; no all-level necessity is claimed.

### W06 — Narrowing

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 47.
- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 47.
- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 57, 58.

The sole eligible E cell has 8 observed exponential deaths,0 bounded deaths, and 16 FU exponential units. The exponential arm denominator for assigned shares is 1108, not 1092 decided units. The frozen same verdict means the interval lies within the 10-percentage-point equivalence margin; it does not mean zero deaths or identical effects.

Replacement:

> The primary matched comparison is eligible only in a bin with few observed deaths. At rho_max in [1.5, 2.1), the bounded arm has 36 units and no observed deaths; the exponential arm has 1,108 units, including 8 F2 and 16 FU (1,092 decided). Delta is −8/1,108 = −0.00722 with FU read as alive and −24/1,108 = −0.02166 with FU read as dead. Both meet the frozen same criterion (within the 10 percentage point margin). No bounded or polynomial comparison is eligible in the bins rho_max >= 2.1, where observed death shares are larger.

### W07 — Narrowing

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 43.
- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 56.

The displayed bins show an association with ever-observed death through level 12. They do not identify a causal effect, determinacy, or a fraction of variation explained. FU remains unresolved.

Replacement:

> Observed death share increases across the displayed density bins in this finite sample. The census does not establish that density alone determines fate or causally explains the association.

### W08 — Narrowing

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 46.
- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 161, 162.

1812 is a count of keys/descriptions with an observed death; the distinct-pattern denominator is 1808. The Glucose record independently contains a decided dead-then-alive pair for all 48, but has 26 null level verdicts in 12 records and only 38 wholly equal vectors; confirm each return is justified, confirm every level verdict would not be. Neither solver refutations nor class labels were independently certified in this wording lane.

Replacement:

> 48 descriptions, representing 48 distinct patterns and all classified exponential, have a decided dead level followed by a decided alive level. They are 48/1,812 (2.65%) of descriptions with an observed death, or 48/1,808 (2.65%) of distinct patterns with an observed death. The supplied Glucose recheck confirms a dead-then-alive pair in all 48; it leaves some other levels undecided.

### W09 — Narrowing

- `proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces/proof.md` lines 54, 55, 56, 57.

Lemma A supplies a finite profile for the three declared uniform list forms. This wording sounds like a general decidability characterization, which the stated argument does not supply. This lane does not audit the proof of Lemma A or its fixed-point prerequisites.

Replacement:

> For the three uniform list forms above, unboundedly many seen distinctions coexist with finite-state behavior because a fixed finite profile suffices. This refutes interface size alone as the proposed separator in that language; it does not give a general characterization of decidable nesting.

### W10 — Narrowing

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 48.

The permitted frozen summary says required core checks passed, but its master status is passed_with_skipped_ambiguous_assertions and explicitly all assertions passed:false (summary.md:14–15). This audit did not access the forbidden validation source.

Replacement:

> The frozen summary reports all required core gate checks passed, with skipped ambiguous assertions; it explicitly does not claim that every assertion passed.

### W11 — Not a block

- `research/ADDR-KNOTS-20261113-001/addr_knots.md` lines 79, 80, 81.
- `research/ADDR-KNOTS-20261113-001/preregistration.md` lines 115, 116, 117.

These are the correct empirical scope boundaries. B0 and first-letter settlement have separately stated mathematical all-level claims; their theorem scope is not limited by the finite census. Preserve this distinction.

Replacement:

> All empirical fate and joining-frequency claims concern the registered samples and levels 1–12 under the stated sampling and solver budgets. The separately proved B0 and first-letter-settled results retain their explicitly stated mathematical scope.

## Reproduction

All totals above were streamed from the two permitted gzipped JSONL files with the workspace `.venv/bin/python -B`; keys were joined to draws by key_id. A nonempty key has any(knots_n). Raw class totals sum draw multiplicities by rel_class. Unsplit pattern counts deduplicate pattern_hash; class counts deduplicate (pattern_hash, rel_class). Raw settlement tests each key’s two flags. Inherited settlement ORs those flags over all keys of one hash within the population, then sums the associated draw multiplicities. Source SHA-256 values and exact source lines are preserved in wording_audit.json.

Focused checks: direct W/E fate counts and pattern counts agree with the frozen summary; the JSON parses; the fresh level-4 fixture matches the raw knot count; all 48 Glucose vectors have a decided return pair. Resource use stayed below 2 GB with one live computation. No SAT solver, producer code, network, Git mutation, publication, or source-document edit was used.

This lane does not certify the SAT verdicts, activity classification implementation, general proof correctness, or novelty. The supplied source labels and theorem/empirical boundaries are retained.
