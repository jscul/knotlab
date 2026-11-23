# Uniform present words with births as the settings: pre-registration

Ticket `REVIEW-LEADS-20261123-001C` of epic `REVIEW-LEADS-20261123-001` (takes B309; G18, with G17), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Sonnet sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged.

## The question

When every present word has equal weight, an ordinary not-all-equal birth weighs the old words by their number of extensions. A parent that holds two loose distinctions and owes one payment to a newborn is not told by ordinary growth which of the two to pay. Take that as the free setting. Can a lawful structure of parity and not-all-equal knots, with two holders per distinction, then give a four-correlation score above 2 while each observer's complete record has the same distribution for either far setting?

## In standard terms

A CHSH test in which the distribution of the hidden state depends on the settings through a product of local positive factors, the form of a local model with post-selection (the detection loophole: Pearle 1970; Garg and Mermin 1987), with the no-signalling condition imposed on each party's complete local record. The side tables are contractions of read-twice constraint networks (Holant-type) of parity and not-all-equal constraints. Quantities: the CHSH value, exact equality of marginals of complete records, and membership of the full table in the local polytope.

## Prior work in the program

`python3 -B scripts/track.py objects "four-correlation score under uniform present words with births as settings" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "CHSH detection loophole post-selection weighting hidden settings" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "pairs of side tables of parity and not-all-equal knots joined through one or two shared distinctions" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`FOUR-READINGS-20261120-001` — a relative: settings inside the state with complete records; one common weighting.
`ENTANGLEMENT-READ-20261120-001` — a relative: settings select readings on one stage; bound of 2 for any one weighting.
`UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001` — same effect: a not-all-equal birth changes an old pair's weight under uniform present words; it did not make the birth a setting.
`WHOLE-STAGE-SETTINGS-20261120-001` — a relative: settings as edits with old-word weighting; noted the final-structure weighting once (12/689) and set it aside.
`LOCAL-EDIT-POLICIES-20261123-001` — a relative: every edit policy under old-word weighting; its bound is the model for the policy test here.
`NAE-GROWTH-20261119-001` — unrelated object.
`BOND-CLOSURE-20261120-001` — unrelated object.
`CENSUS-READ-20261118-001` — unrelated object.

Seen before this freeze, by the thread's own abstract checks of 2026-11-23 (`docs/prompts/missed_leads_checks/`, private): the four-type distribution (20/9, hidden) and a random sample of about 1.3 million small structures (at most exactly 2 when hidden; 8/3 otherwise). No census and no allocation class has been run.

## Prior work outside the program

Pearle (1970) and Garg and Mermin (1987) for local models with selection; Wharton and Argaman (2020) for models whose weighting is over whole histories. Not found: the selection factor arising as a count of extensions under a constraint law, or the realizability question for read-twice parity and not-all-equal networks.

## Settled by construction (stated, not tested)

Under the control weighting, in which an old word keeps its weight and divides it among its extensions, the old distribution does not depend on the settings and the score is at most 2. A parity birth with a fresh distinction gives every old word the same number of extensions, so the setting births are not-all-equal births. With one shared binary distinction between the sides, hidden settings give at most 2 (argument in the result note; the census checks it).

## What is supplied

The reading of a payment allocation as a free setting; the choice of uniform present words; the observers, their three loose distinctions each and their complete records; the outcome functions; the class of structures searched. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Old structure.** Parity (even or odd) and not-all-equal knots of three or four places, every distinction with one or two holders. Alice holds three loose distinctions x1, x2, x3; Bob y1, y2, y3. A cut is the set of distinctions shared between a knot on Alice's side and a knot on Bob's side; no knot holds distinctions of both observers.
- **Setting.** a in {0, 1}: a newborn three-place not-all-equal knot takes x1, the distinction x2 (a = 0) or x3 (a = 1), and one fresh distinction za. Likewise b, y1, y2 or y3, zb. In the allocation class x2 and x3 are loose distinctions of one knot and x1 of another, so the setting is which of its two loose distinctions that knot pays.
- **Weighting.** Uniform present words: every allowed word of the finished structure has equal weight. Control: every old word has equal weight and divides it among its extensions.
- **Complete record.** Alice: x1, x2, x3, za. Bob: y1, y2, y3, zb.
- **Hidden.** For each of Alice's settings her complete record has exactly the same distribution for both of Bob's settings, and likewise for Bob, in exact arithmetic.
- **Score.** The four-correlation (CHSH) value with each outcome any parity of the observer's own four record bits, maximized over the choices. For hidden pairs that reach 2, also the best value over all two-valued functions of the complete record (alternating optimization from every parity start and 200 random starts) and, for the best ten, a linear-programming test of whether the four complete-record tables have one common local explanation.
- **Side table.** For one side, the number of ways to complete each assignment of its three loose distinctions and its cut distinctions.
- **Census class.** Each side: at most 3 knots (4 if a run stays within bounds), at most 3 internal distinctions, a cut of 1 or of 2 distinctions. Every side table is listed once; every ordered pair of side tables with the same cut size is combined.
- **Reference.** The largest score over arbitrary non-negative side tables with a cut of two under exact hiding, by numerical optimization from 2,000 starts and exact rationalization of the best.
- **Targeted search.** After the census, ten minutes of seeded random search over sides of up to 6 knots in the allocation class, reported as exploratory.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: the four-type distribution gives 20/9 with hidden settings; brute-force enumeration of all words agrees with the side-table product on 200 random pairs; the control weighting never exceeds 2. | any fails |
| P1 | With a cut of one, no hidden pair exceeds 2. | one exceeds 2 |
| P2 | The reference over arbitrary side tables with a cut of two exceeds 2 (at least 20/9). | it does not |
| P3 | In the census class with a cut of two, no hidden pair exceeds 2. | one exceeds 2: that pair is the positive result |
| P4 | Without the hiding requirement the class exceeds 2. | it does not |

## Runs and stop rule

One script lists side tables; one combines pairs; one computes the reference. If a hidden pair exceeds 2, the full structure is written out as a list of knots, every word of the four finished structures is enumerated by brute force, the local-explanation test is run, and a policy keyed to an old value is tested on it. The study stops when the class is exhausted and the reference and targeted search are done. Every run stays under ten minutes and under 12 GB; a longer run is not started, the partial result is reported instead. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the six designs cold before this freeze (`research/REVIEW-LEADS-20261123-001/advisor/`, question and answer kept). Its strongest objection here and the change made: A cut of two is a four-valued hidden variable, the same size as the known 20/9 example, so a null in a small class would reflect the class. Changes: the reference optimum over arbitrary side tables is computed first, locality is tested on the full record tables as well as by parities, and a targeted search beyond the class was added. A second point from the review of design E is used here: the setting is a payment allocation, which ordinary growth leaves open, so the allocation class is the primary class.
