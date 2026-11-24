# A structure with a third holder, checked in full: result

Ticket `THIRD-HOLDER-20261123-001A` (direction 1 of `REVIEW-LEADS-20261123-001`; G18 with G17), 2026-11-23. One
argument and exact computations; scientific referee pending. [Pre-registration](preregistration.md) ·
[full tables, the argument and commands](results_draft.md) ·
[deviations](../../experiments/THIRD-HOLDER-20261123-001A/THIRD-HOLDER-20261123-001A-E001_witness/deviations.md)

**With every present word weighted equally and the settings supplied as births, the 18-knot structure gives a
four-correlation score of exactly 20/9 with both complete records hidden, by full enumeration. That is the most any
distribution can give at its weight ratio, by argument: at ratio ρ the ceiling is 4(1 + ρ²)/(1 + ρ)². The family
passes the quantum limit once a setting triggers three births. A setting keyed to an old value changes the other
observer's record, so the structure can also carry a message for anyone able to key a birth to a value, which
ordinary growth cannot do.**

## What happened

- **Full enumeration.** Each of the four finished structures (20 knots, 28 distinctions, 2^28 assignments) has 1,152
  allowed words; the old structure has 512. Full enumeration, the product of side tables and a backtracking search
  give the same record tables. The score is exactly 20/9, the largest change of a complete record is 0, and the four
  totals are equal.
- **Checks of the code, not findings.** The control weighting and parity births in place of not-all-equal births each
  give exactly 2. All 18 knots and the four births pass the canonical test.
- **Several births per setting.**

  | Births per setting | Weight ratio | Score | Hidden | Extra holders |
  | ---: | ---: | --- | --- | ---: |
  | 1 | 2 | 20/9 ≈ 2.22 | yes | 8 |
  | 2 | 4 | 68/25 = 2.72 | yes | 20 |
  | 3 | 8 | 260/81 ≈ 3.21 | yes | 32 |

  The quantum limit is 2√2 ≈ 2.83. Two births stay below it and three pass it. The case of two births was enumerated
  in full (2^36); three births by side tables and backtracking, since 2^44 does not fit the runs.
- **A setting keyed to an old value.** Over all 256 functions of an observer's three old values, the other observer's
  complete record changes by at most 2/9 between two keyings and by 1/9 against a fixed setting. The largest is reached
  by keying Bob's setting to his y2 against keying it to the opposite. The pooled and the normalized readings agree,
  because the four totals are equal.

## The ceiling

**Statement.** Let an old word's weight at settings (a, b) be a common weight times a factor 1 or ρ for each observer,
set by that observer's setting and old values, and let both complete records hide the far setting exactly. Then for
any outcomes the score is at most 2 + 2 T(c) T(c'), where c and c' are the two ratios of the totals of the finished
structures and T(c) = (ρ − c)(ρc − 1)/(c(ρ² − 1)). T is largest at c = 1, where it is (ρ − 1)/(ρ + 1). So the score
is at most 4(1 + ρ²)/(1 + ρ)², with equality only when the four totals are equal.

**Why.** Hiding lets the totals be absorbed into the factors, so that the four distributions are one distribution
times (1 ± δ) for Alice and (1 ± ε) for Bob, with δ averaging to zero given everything Bob holds and ε likewise. Each
of δ and ε can be split into its two extreme values without changing any table, and then the sign of δ is
independent of everything Bob holds. The two settings of an observer change the distribution of its sign by T in
total variation. So with chance T an observer's sign follows its setting and otherwise it does not depend on it. If
neither sign follows its setting, or only one does, a common explanation exists and the score is at most 2; if both
do, it is at most 4. The full argument is in the [draft](results_draft.md#the-argument); the thread read it step by
step and found no gap. The implementer found it; it was not a pre-registered method. It is of the kind the literature
has for relaxed measurement independence (Hall 2011); this exact form was not checked against the literature.

**What it gives.** The 18-knot structure and its copies sit exactly at the ceiling for their ratios. No better
structure exists for this weighting, of any size or with any number of holders. A seeded search of 4,000 starts per
ratio found nothing above the family value.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed | Canonical test on every knot; three computations agree; control weighting and parity births give exactly 2 |
| P1 | Held | 20/9, hidden, by full enumeration |
| P2 | Held | 2/9 between two keyings, 1/9 against a fixed setting |
| P3 | Held | 68/25 and 260/81, hidden |
| P4 | Held, and proved | Ceiling 20/9, 68/25, 260/81; no distribution beats the family |

The thread recomputed the two keyed-setting numbers with separate code from the old table (2/9 and 1/9) and checked
the argument for the ceiling by hand.

## What this is about

About a supplied weighting acting on structures ordinary growth never makes. The excess comes from the weighting: an
old word's weight depends on both settings, the literature's measurement dependence. What the third holder adds is
that the structure can hide it. The settings are births supplied from outside, a choice between starts. The three-birth
case was not enumerated in full.

**Verdict.** Supported. The structure is verified, it is optimal for its weighting, the bound for that weighting is
known at every ratio, and nothing in the family stops at the quantum limit.
