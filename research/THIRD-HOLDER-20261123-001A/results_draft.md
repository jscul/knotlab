# A structure with a third holder: the hidden excess checked in full: results (draft)

Ticket `THIRD-HOLDER-20261123-001A` of epic `THIRD-HOLDER-20261123-001`, 2026-11-23. Exact finite combinatorics,
optimisation and one argument. Code by a Claude Opus sub-agent from the frozen
[pre-registration](preregistration.md); scientific referee pending. Readings taken where the note was open:
[deviations](../../experiments/THIRD-HOLDER-20261123-001A/THIRD-HOLDER-20261123-001A-E001_witness/deviations.md).
Outputs: `artifacts/THIRD-HOLDER-20261123-001A/THIRD-HOLDER-20261123-001A-E001_witness/` (JSON summaries, `logs/`).

**In short.** Every check of the code passes. The full enumeration of the 18-knot structure, every knot on every
assignment of its 28 distinctions, gives exactly 20/9 with both complete records hidden; the four finished structures
have 1,152 allowed words each. A setting keyed to the observer's own old values changes the other observer's complete
record by up to 2/9 between two keyings (1/9 against a fixed setting) in both readings, which agree here because the four
totals are equal. Two and three births per setting, made with further holders on the copying pairs, give 68/25 and
260/81, hidden; 260/81 is above Tsirelson's bound 2√2. The ceiling at each ratio equals the family's value, and this is
proved, not only found: under exact hiding of both complete records the score is at most 2 + 2 T(c) T(c') ≤
4(1 + ρ²)/(1 + ρ)², for any distribution on the old values and any outcomes.

## Row G: checks of the code

| Check | Result |
| --- | --- |
| Canonical K1–K3 test (`tools/knotlab`, forgetting reading) of each of the 18 knots, each of the three choices of contact place | 18 of 18 pass every choice; the four births pass too |
| Engine self-test: bit-operation enumeration vs backtracking vs plain itertools, 200 seeded random structures | 0 mismatches |
| Full enumeration of each finished structure (28 distinctions, 20 knots, 2^28 assignments) vs side tables (each side alone, combined over s1 s2) vs exhaustive backtracking over the whole structure | equal in all 4 × 256 entries of the four 16 × 16 tables of complete records |
| Old structure (26 distinctions, 2^26 assignments) | 512 allowed old words; each finished table equals the old table times the lawful fresh counts; the starter's `evaluate` on it: 2.222222222, hidden, change 0 |
| Control weighting (old words equal, divided among extensions) | score exactly 2 |
| Even births in place of not-all-equal births | score exactly 2 (four totals 512) |
| Odd births in place of not-all-equal births | score exactly 2 (four totals 512) |

Row G passed; the predictions were then evaluated.

Distinctions held more than twice in the 18-knot structure: a, b, r, t (three holders each) and d, e (four each):
8 extra holders.

## P1: the full enumeration

| Settings (a, b) | Distinctions | Knots | Assignments | Allowed words |
| --- | ---: | ---: | ---: | ---: |
| (0, 0) | 28 | 20 | 2^28 | 1,152 |
| (0, 1) | 28 | 20 | 2^28 | 1,152 |
| (1, 0) | 28 | 20 | 2^28 | 1,152 |
| (1, 1) | 28 | 20 | 2^28 | 1,152 |

Score over parity outcomes of each observer's four record bits (15 per setting), the four sign patterns, exact:
**20/9**. Attained with Alice's outcome the parity of x3 at a = 0 and of x1 at a = 1, Bob's the parity of y2 at b = 0
and of y1 at b = 1, the minus sign on (0, 0). Both complete records hide the far setting exactly; the largest change of a
complete record is 0.

## P2: a setting keyed to the observer's own old values

256 functions of the keyed observer's three old values; the other observer's setting fixed; each case below covers all
256 × 256 ordered pairs. Exact fractions.

| Keyed observer | Other fixed at | Pooled: largest change between two functions | Normalized per setting | Largest change against a fixed setting | Keyed to one old value, against a fixed setting |
| --- | --- | --- | --- | --- | --- |
| Bob | 0 | 2/9 | 2/9 | 1/9 | y2 or y3: 1/9; y1: 1/18 |
| Bob | 1 | 2/9 | 2/9 | 1/9 | y1: 1/9; y2 or y3: 1/18 |
| Alice | 0 | 2/9 | 2/9 | 1/9 | x1: 1/9; x2 or x3: 1/18 |
| Alice | 1 | 2/9 | 2/9 | 1/9 | x2 or x3: 1/9; x1: 1/18 |

The two readings give the same values because the four finished structures have equal totals (1,152), so weighting
each by 1/Z_ab changes nothing. The pair maximum 2/9 is attained by "Bob's setting is y2" against "Bob's setting is
1 − y2" when Alice is fixed at 0 (truth tables over y1y2y3 = 000…111: 00100010 and 01000100), and by y1 against 1 − y1
when Alice is fixed at 1 (00000110 and 01100000); Alice keyed is the mirror. 512 ordered pairs attain it in each case:
every allowed old word has y3 = 1 − y2, so the 16 functions that differ only on the other four old values act alike.
The pencil value 1/9 is the change against a fixed setting; the two fixed settings give the same distribution (change
0), as hiding requires.

## P3: two and three births per setting

Each birth takes its own loose copy of x1 and of x2 (a = 0) or x3 (a = 1), and one fresh distinction; Bob likewise.
Copies: even(x1_i, a, b), even(x2_i, d, e), odd(x3_i, d, e), even(y1_i, p, q), even(y2_i, r, t), odd(y3_i, r, t). The
structures are written out in `structure_k2.json` and `structure_k3.json`.

| Births per setting k | Old distinctions | Old knots (Alice, Bob) | Finished: distinctions, knots | Extra holders | Holders per distinction above two | Allowed words, each of the four finished structures | Score | Hidden (both records) | Verified by |
| ---: | ---: | --- | --- | ---: | --- | ---: | --- | --- | --- |
| 1 | 26 | 18 (13, 5) | 28, 20 | 8 | a b r t: 3; d e: 4 | 1,152 | 20/9 = 2.2222 | yes | full enumeration, side tables, backtracking |
| 2 | 32 | 24 (16, 8) | 36, 28 | 20 | p q: 3; a b: 4; r t: 5; d e: 6 | 3,200 | 68/25 = 2.72 | yes | full enumeration (2^36 each), side tables, backtracking |
| 3 | 38 | 30 (19, 11) | 44, 36 | 32 | p q: 4; a b: 5; r t: 7; d e: 8 | 10,368 | 260/81 = 3.2099 | yes | side tables and backtracking; full enumeration (2^44 each) not run |

Every knot of each structure passes the canonical test (32 of 32 for k = 2, 42 of 42 for k = 3). In every allowed word
every copy equals its original. The old structure for k = 2 has 512 allowed old words (2^32 assignments). The largest
change of a complete record is 0 for k = 2 and 3; the control weighting gives exactly 2 for both. The outcomes attaining
the score are the same old-value parities as for one birth. Extra holders grow as 12k − 4.

Against the quantum limit: 20/9 and 68/25 are below 2√2 ≈ 2.8284; 260/81 ≈ 3.2099 is above it.

## P4: the ceiling

The largest score under exact hiding of both complete records over all distributions on the six old values and all
parity outcomes of the record (three old values and k fresh ones, ρ = 2^k), no structure.

| Ratio ρ | Family value 4(1 + ρ²)/(1 + ρ)² | Ceiling | Status | Seeded optimisation, 4,000 starts: best | Starts within 1e-6 of the family value | Exact re-verification of the best |
| ---: | --- | --- | --- | --- | ---: | --- |
| 2 | 20/9 | 20/9 | proved | 2.222222222169 | 27 | 20/9 at c = c' = 1, hidden, 8 old words of equal weight (the four-type table) |
| 4 | 68/25 | 68/25 | proved | 2.719999999900 | 125 | 68/25 at c = c' = 1, hidden, 8 old words of equal weight |
| 8 | 260/81 | 260/81 | proved | 3.209876543210 | 131 | 260/81 at c = c' = 1, hidden, 8 old words of equal weight |

No distribution with hidden settings scores higher than the family at any ratio. The seeded runs end at 2 in 10,466 of the
12,000 starts (within 1e-6); none ends above the family value by more than 1e-9, and none above the proved bound 2 + 2 T(c) T(c') for
its own ratios by more than 3.0e-8 (values at 2 with a ratio at the end of its range, where both sides equal 2 up to the
solver's tolerance). A relaxation used in the proof was also solved as a linear program on 39 × 39 values of (c, c') per
ratio: its value equals 2 + 2 T(c) T(c') to 1.5e-14 everywhere, with the maximum at c = c' = 1.

### The argument

Write c = Z_00/Z_01 and c' = Z_00/Z_10 for the ratios of the totals, and

T(c) = (ρ − c)(ρc − 1) / (c(ρ² − 1)).

**Claim.** Let each observer hold hidden values of any finite kind, with a joint weight q, and let an old word's weight
at settings (a, b) be q times a factor 1 or ρ for each observer chosen by that observer's setting and hidden values
(here: ρ when the chosen inputs differ). Let each outcome be any ±1 function of the observer's record, and let each
observer's hidden values hide the far setting exactly (for the structures here this is the hiding of the complete
records, which contain the old values and whose fresh values are drawn given the old ones). Then the score is at most 2 + 2 T(c) T(c') ≤ 2 + 2((ρ − 1)/(ρ + 1))² =
4(1 + ρ²)/(1 + ρ)², with the second equality only when c = c' = 1, that is when the four totals are equal.

*Fresh values.* Given the old values the lawful fresh values are equally weighted, so each outcome enters through its
average over them, a number in [−1, 1]. The score is a sum of products of one of Alice's averages and one of Bob's, so
for fixed q its largest value over averages in [−1, 1] is reached with every average ±1. It is enough to bound ±1
outcome functions of the old values.

*Step 1: one distribution.* Hiding of Alice's complete record says that the weights of her old values summed against
Bob's factor at b = 0 and at b = 1 are proportional, with ratio c; Bob's likewise with ratio c'. Absorb c' into Alice's
factor at a = 1 and c into Bob's at b = 1 (F_a = f_a c'^a, G_b = g_b c^b), set δ = (F_0 − F_1)/(F_0 + F_1),
ε = (G_0 − G_1)/(G_0 + G_1) and ν proportional to q (F_0 + F_1)(G_0 + G_1). Then the distribution at (a, b) is
ν (1 + (−1)^a δ)(1 + (−1)^b ε), ν is a probability distribution, and hiding says exactly: the average of ε under ν given
Alice's hidden values is 0, and the average of δ given Bob's is 0.

*Step 2: two values of δ.* δ lies between δ− = (1 − ρc')/(1 + ρc') and δ+ = (ρ − c')/(ρ + c'). (If c' is not between
1/ρ and ρ these have one sign, hiding forces δ = 0 wherever ν has weight, and Alice's part below has T_A = 0.) Split each hidden value
of Alice into a + copy and a − copy, chosen with chances that average δ+ and δ− to δ, independently of Bob; give the
copies δ+ and δ−. The four distributions, the outcomes and both hiding conditions are unchanged. Do the same for Bob.
Now the average of δ given Bob's values being 0 means that Alice's sign i_A is independent of everything Bob holds;
likewise Bob's sign i_B. So at (a, b) the two signs are drawn independently, Alice's from a distribution π_a and Bob's
from σ_b, and given the two signs the hidden values follow a law that does not depend on the settings, whose Alice part
depends only on i_A and whose Bob part only on i_B.

*Step 3: flags.* π_0 and π_1 differ by T_A = 2δ+|δ−|/(δ+ + |δ−|) = T(c') in total variation, so
π_a = (1 − T_A) R + T_A [i_A = + if a = 0, − if a = 1], with R not depending on a; likewise for Bob with T_B = T(c).
Draw an independent flag for each observer, raised with chance T_A and T_B. With neither raised, nothing depends on the
settings: one distribution and fixed outcome functions, score at most 2. With only Alice's raised, her sign is her
setting and Bob's is drawn from his R; for each value of his sign the two laws given (+, i_B) and (−, i_B) have the same
Bob part and can be joined into one law, from which Alice reads the part labelled by her setting: again one distribution,
score at most 2. The same holds with only Bob's raised. With both raised the score is at most 4. So the score is at most
2(1 − T_A T_B) + 4 T_A T_B = 2 + 2 T(c) T(c').

*Step 4.* T(c) = (ρ² + 1 − ρ(c + 1/c))/(ρ² − 1) ≤ (ρ − 1)²/(ρ² − 1) = (ρ − 1)/(ρ + 1), with equality only at c = 1.
The four-type family has c = c' = 1 and reaches 2 + 2((ρ − 1)/(ρ + 1))². ∎

The argument uses neither parity outcomes nor the six-value form; it holds for any outcomes and any finite hidden
values, so the ceiling at ratio ρ is the family's value for every ρ > 1, not only for 2, 4 and 8. Its value passes 2√2
from ρ ≈ 4.61 on. The decomposition by flags is of the kind used for relaxed measurement independence (Hall 2011); this
exact product form, with hiding of both complete records, was not checked against the literature. What it adds here:
within this weighting the 18-knot structure and its copies are already at the ceiling for their ratios, and the ceiling
can be reached only with the four totals equal.

## Predictions

| # | Prediction | Verdict | Evidence |
| --- | --- | --- | --- |
| G | Checks of the code | Passed | table above |
| P1 | The full enumeration gives 20/9 with both complete records hidden exactly | Held | 20/9 exactly, both hidden, change 0; four totals 1,152 |
| P2 | Some value-keyed setting changes the other observer's complete record under the pooled reading (pencil 1/9) | Held | 1/9 against a fixed setting, as pencilled; 2/9 between two keyings; the same in the normalized reading |
| P3 | Two births give 68/25 and three give 260/81, both hidden | Held | 68/25 and 260/81 exactly, both hidden; k = 2 by full enumeration, k = 3 by side tables and backtracking |
| P4 | The ceiling at each ratio equals the family's value | Held, proved | upper bound proved for every ratio; the family reaches it; seeded search finds nothing higher |

## Commands

From the repository root (`D=experiments/THIRD-HOLDER-20261123-001A/THIRD-HOLDER-20261123-001A-E001_witness`,
`R="timeout 600 prlimit --as=12884901888 .venv/bin/python -B"`):

```bash
$R $D/selftest.py
$R $D/item_g.py
$R $D/item_p1.py
$R $D/item_p2.py
$R $D/item_p3.py build 2
$R $D/item_p3.py build 3
$R $D/item_p3.py full 2 0 0                       # and full 2 SA SB PART 4 for (0,1), (1,0), (1,1), PART = 0..3
$R $D/item_p3.py summary
$R $D/item_p4.py relax
$R $D/item_p4.py seeded RHO START END             # RHO = 2, 4, 8; START, END = 0, 500, ..., 4000
$R $D/item_p4.py summary
$R $D/item_p4.py exact
```

Each run took under ten minutes and under 12 GB; several single-process runs ran at the same time on the shared machine.

## What this is about

Supplied, each a scaffold to be recorded at close: the weighting (every present word equal); the settings as births; the
18-knot structure with distinctions held three and four times; the copies made by further holders on the copying pairs;
the pooled and normalized readings of a value-keyed setting; for P4, the reading of ratio 2^k as k births with their
fresh values in the record. Everything here is about these scaffolds and the structures built from them, except the
argument of P4, which is about the weighting alone: any distribution, any outcomes. Ordinary growth never makes a
distinction with a third holder, and a value-keyed setting is not an ordinary act (ticket E of the review-leads epic).
The excess is produced by the supplied weighting; hiding is what the third holders make possible.
