# The question to the advisor (26 November 2026), on the scoping of weights that cancel

Short, skeptical answers please. After the forbidding study (forbidding that splits is local rejection) and a linear
program showing that the whole-round response gives no excess that survives a free sender, the coordinator asked me to
scope the second route: list every place the recorded model already produces something that cancels, say for each
whether it arises from growth or from a choice of ours and whether it could weight whole configurations, and stop at
one candidate with a frozen runnable test or at a short note saying why none exists. My draft table and candidate are
below.

1. Is anything missing from the table, or misjudged (especially rows 3, 4 and 5)?
2. Is the candidate the right single one? With value reads only, is my parity argument right, and does it make the
   test pointless for parity? Should the test instead allow the phase-sensitive reading (then it reproduces GHZ with a
   supplied reading, as already shown)? Or is the honest outcome the note "none exists in the recorded laws": every
   native cancellation either weights nothing, or is a local phase, or is a supplied sign?
3. If a test: its exact frozen form and your prediction.

## B. Where the recorded model makes something cancel (scoping; draft for the advisor)

The question (the coordinator's): list every place the recorded model already produces something that cancels; for
each, does it arise from growth or from a choice of ours, and could it weight whole configurations (a signed weight on
each allowed state, which is what a table beyond the classical bound needs once responses split)?

| # | Where | What cancels | Growth or our choice | Weights whole configurations? |
|---|---|---|---|---|
| 1 | The parity knot rule (mod-2 sums) | Adding parity equations cancels shared distinctions in pairs; growth uses it (an implied birth gets no fresh distinction where its inputs already imply the law; GROWTH-SIGN-LAW, the three-copy circuit) | Growth (the knot law) | No: it decides which states are allowed; it weights none |
| 2 | Two passes of a shared distinction | A distinction held twice contributes x + x = 0 to a sum of characters; a character (−1)^(sum of a knot's places) is +1 on every allowed state | The knot law | Trivially: the character is constant on allowed states, so it weights nothing |
| 3 | The signed knot law +--- on 000, 011, 101, 110 (INTERFERENCE-20261029-001; equal to i^(weight) on even words) | Under the signed witness reading, the two fillings of the three-copy circuit cancel (1 − 1 = 0); every three-bit knot is a signed sum of pair functions over one hidden bit; with phase-sensitive reads it gives every GHZ probability (WEIGHTED-KNOT-FOUR-SETTINGS) | A choice: the reading is the owner's working reading, the sign law is chosen; growth does not select it (GROWTH-SIGN-LAW: neither operation forced) | Yes: the product over knots is a signed weight on every allowed state, (−1)^(shared distinctions holding 1) · i^(loose distinctions holding 1) |
| 4 | The reversal sign (−1)^C(k,2) (REORDER-CONFIRM) | The round's own order (every parent before any child) gives each word of weight k the sign (−1)^C(k,2) under the swap rule | The order is growth's own (the round), but the swap rule is added (A275), and the sign is a local adjustment (diag(1, i) at each reader) | Yes, but as a product of per-reader phases: it cannot change any table of value reads, and with phase reads it is absorbed into the reader |
| 5 | The exchange sign of crossing lifetimes (Wick sign; REORDER-SIGN, REORDER-CONFIRM) | Two occupied parents whose lifetimes cross cost −1; carries the contradiction only for schedules whose crossings are the pairs across a split | The schedule is supplied (A279 weights them equally); the line stopped | Yes (a sign per schedule and word), but no rule of the model selects a carrying schedule |
| 6 | Not-all-equal's completion matrix K = [[3,2],[2,3]] | Its antisymmetric mode (1, −1), eigenvalue 1 against 5, is what carries correlation along a chain | The knot law | No: K is positive; the mode is a signed direction of a nonnegative weighting |
| 7 | Complement symmetry and antiperiods (odd harmonies; LINE-LOCK) | Not-all-equal states come in complementary pairs; an antiperiod returns a pattern flipped | The knot law | A Z2 character on configurations, but complement-symmetric weightings give it weight zero |
| 8 | Basis changes (holographic transforms, the y-basis of the native scan; x² = −1/3) | Signatures with signs appear after a change of basis | Our choice of basis | Only in the transformed frame; the physical weighting is unchanged |
| 9 | Counting identities (point splitting #col(H0) = 2#col(H1) − #col(H2); inclusion–exclusion over knots) | Signed sums of counts of different structures | Arithmetic over structures | They weight structures, not the states of one structure |
| 10 | A knot's co-information (three-place parity: −1 bit on every allowed word; not-all-equal: log2(8/9)) | The interaction term of a knot is negative | The knot law | It is a logarithm of ratios of a nonnegative weighting, not a weight |

**The one candidate with a test (draft).** Row 3 under growth: give every allowed state of a grown structure the signed
weight of the signed law (row 3), read values only (the program's readers), settings as free local edits (the
forbidding study's census), one round; per setting pair, normalize the signed sum. Ask: are all four context tables
nonnegative (a valid table), with every complete record unchanged by far settings, and CHSH above 2? Runnable on
`forbid.py`'s census with a signed counter. A parity argument suggests the answer is no for value reads (the signed
weight is a product of one phase per distinction, so summing hidden distinctions gives tables that are either
nonnegative and classical or not tables at all), so the test would decide whether not-all-equal's signed law escapes it.
