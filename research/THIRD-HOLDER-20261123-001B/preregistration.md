# The smallest structure with a hidden excess, and whether a third holder is enough: pre-registration

Ticket `THIRD-HOLDER-20261123-001B` of epic `THIRD-HOLDER-20261123-001` (direction 1 of `REVIEW-LEADS-20261123-001`; G18 with G17), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Opus sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged; a distinction with a third holder is something ordinary growth never makes.

## The question

Two holders per distinction gave no hidden excess in the classes searched. The 18-knot structure uses distinctions held three and four times. How small can a structure with a hidden excess be, is a third holder enough, and how much smaller does it get if an observer's own distinction may already be shared when the birth takes it?

## In standard terms

The minimum size of a network of parity and not-all-equal constraints, with variables of bounded degree three, whose weighted solution set gives a CHSH value above 2 under exact no-signalling on complete records; with the observers' variables of degree one (pendant) or two before the setting constraint is added.

## Prior work in the program

`python3 -B scripts/track.py objects "smallest structure with a hidden excess when a distinction may have a third holder" --until 2026-11-23 --exclude THIRD-HOLDER-20261123-001`

`python3 -B scripts/track.py objects "minimal constraint network with fan-out violating CHSH under no-signalling" --until 2026-11-23 --exclude THIRD-HOLDER-20261123-001`

`python3 -B scripts/track.py objects "sides of at most four knots with internal distinctions held three times" --until 2026-11-23 --exclude THIRD-HOLDER-20261123-001`

`REVIEW-LEADS-20261123-001` — the source of this study: its ticket C found no two-holder structure with a hidden excess and, after its stop, the 18-knot structure checked here; its ticket E showed that a value-keyed setting is not an ordinary act.
`TWO-KNOTS-ONE-DECISION-20261121-001` — unrelated object.
`UNIQUE-TABLE-20261119-001` — unrelated object.
`LOCAL-EDIT-POLICIES-20261123-001` — a relative: every edit policy under old-word weighting, and the model for the policy test here.
`ENTANGLEMENT-READ-20261120-001` — a relative: bound of 2 for settings that select readings under any one weighting.
`GUARD-CHOICE-SEPARATION-20261115-001` — unrelated object.
`SUBST-NEST-20261112-001` — a relative: a three-copy gadget used for substitution; not this test.

Seen before this freeze: the same post hoc check of the 18-knot structure. No census with a third holder, no reduction and no search has been run, and the pencil 9-knot structure has not been checked.

## Prior work outside the program

None found.

## Settled by construction (stated, not tested)

With two holders and parity knots alone, the only rule on the loose distinctions of a connected part is their total parity, so a loose value is tied to at most one other loose distinction (the bond-closure study). Any structure found here therefore has a distinction with a third holder or a not-all-equal knot doing the tying.

## What is supplied

The weighting; the settings as births; the two classes; the bound of three holders; the size order; the reduction orders and the seeded samples. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Observers, settings, weighting, records, hidden, score.** As in ticket C of the review-leads epic: Alice holds x1, x2, x3 and Bob y1, y2, y3; setting a adds a three-place not-all-equal knot on x1, x2 (a = 0) or x3 (a = 1) and one fresh distinction, likewise for Bob; every allowed word of the finished structure has equal weight; a record is the observer's three old values and its fresh values; hidden means each complete record has exactly the same distribution for either far setting; the score is the four-correlation (CHSH) value with each outcome any parity of the observer's own record bits, maximized.
- **Knots.** Parity (even or odd) and not-all-equal, of three or four places. Each passes the canonical test on its own.
- **Holders.** Internal distinctions may have one, two or three holders. A shared distinction between the sides has exactly one holder on each side.
- **Class L.** Each observer distinction has exactly one old holder, so the setting birth takes a loose distinction.
- **Class S.** An observer distinction may have one or two old holders; the setting birth gives it one more.
- **Size.** Total knots of the old structure first, then extra holders (holders beyond two, summed over old distinctions). The smallest number of extra holders found at any number of knots is reported beside it.
- **Census.** Every side of at most 4 knots and at most 5 internal distinctions (5 knots if every run stays inside its bounds), in each class; every pair with one or two shared distinctions.
- **Reduction.** From the 18-knot structure of ticket A, and from the pencil structure below: remove one knot at a time (dropping distinctions left with no holder), keep the removal when the structure is still hidden with a score above 2, in 200 seeded orders each (seeds 2026112320 to 2026112519).
- **Pencil structure, class S, 9 knots.** Alice: nae(x1,x2,n2), nae(x1,x3,n1), even(x2,d,e), odd(x3,d,e). Bob: even(y1,p,q), odd(n1,p,q), even(y2,r,t), odd(n2,r,t), odd(y3,r,t). Shared between the sides: n1, n2. Not checked before this freeze.
- **Seeded search.** 2,000,000 drawn sides per class of up to 9 knots (seed 2026112321), pooled and paired as in ticket C of the review-leads epic, with pools capped at 20,000 distinct tables.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Checks of the code: with the holder bound set to two the census reproduces ticket C's maximum of exactly 2 for sides of at most 3 knots; the product of side tables agrees with brute-force enumeration on 100 drawn pairs with a third holder. | any fails |
| P1 | Some structure in class L has a hidden excess with no distinction held more than three times. | none is found by census, reduction or search |
| P2 | Class L has no hidden excess with both sides of at most 4 knots. | one is found: it is the smallest and is reported in full |
| P3 | Class S has a hidden excess with at most 10 knots in all. | none is found |
| P4 | The pencil 9-knot structure gives 20/9 with hidden settings. | it does not |

## Runs and stop rule

One script lists sides, one pairs them, one reduces, one searches. The study stops when the census, both reductions and the seeded search are done. It reports the smallest structure found in each class as a list of knots, verified by full enumeration, with its knots and extra holders, and the lower bound the census gives. Every run stays under ten minutes and under 12 GB; work is split into runs and nothing is stopped by the clock. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed both designs cold before this freeze (`research/THIRD-HOLDER-20261123-001/advisor/question.md`, `answer.json`). Its strongest objections here: the size had two measures with no order, the reduction depends on its order, a time-based stop was used, and the class-L null is conditional on the size searched. Changes: a fixed size order with the other measure reported beside it, 200 seeded reduction orders, a count-based search, and the conditional wording of P2.
