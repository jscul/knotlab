# A structure with a third holder: the hidden excess checked in full: pre-registration

Ticket `THIRD-HOLDER-20261123-001A` of epic `THIRD-HOLDER-20261123-001` (direction 1 of `REVIEW-LEADS-20261123-001`; G18 with G17), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Opus sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged; a distinction with a third holder is something ordinary growth never makes.

## The question

After its stop, ticket C of the review-leads epic found that 18 ordinary three-place knots give a four-correlation score of 20/9 with hidden settings once six internal distinctions have three or four holders. That check used the product of two side tables. This study checks the structure with no such shortcut, asks what any setting keyed to an old value does, tests the same family with two and three births per setting against the quantum limit, and computes the ceiling: the largest hidden score any distribution on the six old values can give at each weight ratio.

## In standard terms

A local model with measurement dependence of product form (post-selection): the hidden state's weight is multiplied by a local factor for each setting. The no-signalling condition is imposed on complete local records. Quantities: the CHSH value against the classical bound 2 and Tsirelson's bound 2√2 (Tsirelson 1980); the maximum of CHSH over such models at a given ratio of the local factors.

## Prior work in the program

`python3 -B scripts/track.py objects "structure with distinctions held three or four times giving a hidden four-correlation excess" --until 2026-11-23 --exclude THIRD-HOLDER-20261123-001`

`python3 -B scripts/track.py objects "CHSH above the quantum limit with no-signalling complete records under post-selection weighting" --until 2026-11-23 --exclude THIRD-HOLDER-20261123-001`

`python3 -B scripts/track.py objects "eighteen parity and not-all-equal knots with copies made by knots sharing a pair of distinctions" --until 2026-11-23 --exclude THIRD-HOLDER-20261123-001`

`REVIEW-LEADS-20261123-001` — the source of this study: its ticket C found no two-holder structure with a hidden excess and, after its stop, the 18-knot structure checked here; its ticket E showed that a value-keyed setting is not an ordinary act.
`FOUR-READINGS-20261120-001` — a relative: settings inside the state under one weighting; bound of 2 through one shared distinction.
`KNOT-RATION-GAME-20261121-001` — unrelated object.
`LOCAL-EDIT-POLICIES-20261123-001` — a relative: every edit policy under old-word weighting, and the model for the policy test here.
`WHOLE-STAGE-SETTINGS-20261120-001` — a relative: an excess of 9/4 from stalling with old-word weighting; signals under policies.
`NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001` — unrelated object.
`COPIES-AND-MEETINGS-20261120-001` — unrelated object (copies there are released families).
`UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001` — a relative: the weighting used here differs from the old-word weighting exactly under not-all-equal.

Seen before this freeze: the post hoc check of 2026-11-23 (`research/REVIEW-LEADS-20261123-001/posthoc/three_holders_check.py`): the 18-knot structure's two side tables and their product, 20/9, hidden. No full enumeration, no policy, no several births and no ceiling has been run.

## Prior work outside the program

Pearle (1970), Garg and Mermin (1987) for local models with selection; Popescu and Rohrlich (1994) for non-signalling tables above the quantum limit; Tsirelson (1980). Not found: these tables realized by a network of parity and not-all-equal constraints, or the ceiling at a fixed ratio with hiding on complete records.

## Settled by construction (stated, not tested)

The excess comes from the weighting: with every present word equal, an old word's weight is a product of one factor per setting. Under the control weighting (old words equal, divided among extensions) and with parity births in place of not-all-equal births, the old distribution does not depend on the settings and the score is at most 2. These two are run as checks of the code and are not predictions. Wherever the score exceeds 2 no common local explanation exists. Hiding does not depend on the weight ratio, so the scores at two and three births per setting follow from the single-birth case and the known formula if the copies copy.

## What is supplied

The weighting; the settings as births; the 18-knot structure with more than two holders on six distinctions; the copies for further births; the reading of a value-keyed setting. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Observers, settings, weighting, records, hidden, score.** As in ticket C of the review-leads epic: Alice holds x1, x2, x3 and Bob y1, y2, y3; setting a adds a three-place not-all-equal knot on x1, x2 (a = 0) or x3 (a = 1) and one fresh distinction, likewise for Bob; every allowed word of the finished structure has equal weight; a record is the observer's three old values and its fresh values; hidden means each complete record has exactly the same distribution for either far setting; the score is the four-correlation (CHSH) value with each outcome any parity of the observer's own record bits, maximized.
- **Knots.** Parity (even or odd) and not-all-equal, of three or four places. Each passes the canonical test on its own.
- **The structure.** Alice's side, 13 knots: even(x1,a,b), even(c1,a,b), even(k1,a,b); even(x2,d,e), odd(x3,d,e), even(c2,d,e), odd(c3,d,e); nae(c1,c2,n2), nae(k1,c3,n1); even(n2,g,h), odd(s2,g,h); even(n1,u,v), odd(s1,u,v). Bob's side, 5 knots: even(y1,p,q), even(s1,p,q); even(y2,r,t), even(s2,r,t), odd(y3,r,t). The shared distinctions between the sides are s1 and s2. Held three times: a, b, r, t. Held four times: d, e.
- **Full enumeration.** Every assignment of the 26 old distinctions and the fresh ones is tested against every knot of each of the four finished structures, with no factorization by side. A second computation by side tables must agree.
- **Totals.** The number of allowed words of each of the four finished structures is reported; equal totals are not assumed.
- **Value-keyed setting.** One observer's setting is a function of its three old values (256 functions), the other's is fixed. The weighting pools, unnormalized, every old word together with its lawful fresh completions under the birth its own values select, each such finished word with equal weight. The change is the total-variation distance between the other observer's complete-record distributions under two such functions, maximized over pairs of functions and over the fixed setting. The normalized-per-setting reading is reported beside it.
- **Several births per setting.** For k = 2 and 3, setting a adds k not-all-equal births, each on its own loose copy of x1 and of x2 (a = 0) or x3 (a = 1) and one fresh distinction; copies are made by further holders on the copying pairs. The record is the three old values and the k fresh ones. The number of extra holders (holders beyond two, summed over distinctions) is reported.
- **Ceiling.** For weight ratio 2, 4 and 8: the largest score, under exact hiding, over all distributions on the six old values and all parity outcomes, with no structure. Solved exactly where the problem is linear and by seeded optimization with exact re-verification otherwise (4,000 starts).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Checks of the code, not predictions: each of the 18 knots passes the canonical test; the side-table computation agrees with the full enumeration; the control weighting and parity births give at most 2. | any fails |
| P1 | The full enumeration gives 20/9 with both complete records hidden exactly. | either differs |
| P2 | Some value-keyed setting changes the other observer's complete record under the pooled reading (pencil: 1/9). | no function changes it |
| P3 | Two births per setting give 68/25 and three give 260/81, both hidden. | either differs |
| P4 | The ceiling at each ratio equals the family's value: 20/9, 68/25 and 260/81. | a distribution with hidden settings scores higher: it is reported in full |

## Runs and stop rule

One script per item. The study stops when the five items are done. Every run stays under ten minutes and under 12 GB; work is split into runs and nothing is stopped by the clock. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed both designs cold before this freeze (`research/THIRD-HOLDER-20261123-001/advisor/question.md`, `answer.json`). Its strongest objections here: the excess comes from the weighting and the third holder only lets the structure hide it, so several arms could not fail; the value-keyed setting was underdefined; and a ceiling over all distributions was missing. Changes: the arms that cannot fail are run as code checks and named as such, the pooled reading of a value-keyed setting is defined with the normalized one beside it, the totals of the four finished structures are reported, extra holders are counted for several births, and the ceiling is computed as P4.
