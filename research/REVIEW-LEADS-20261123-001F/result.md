# A rule that is both parity and not-all-equal: result

Ticket `REVIEW-LEADS-20261123-001F` (B314; G18 with G5), 2026-11-23. Computed; scientific referee pending.
[Pre-registration](preregistration.md) · [full tables and commands](results_draft.md) ·
[deviations](../../experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/deviations.md)

**Requiring both laws at once does not fix the values. It forces the continuation only from the two quiet starts. What
it does give is a count that is carried: on the five-founder clock the number of ones among the loose distinctions
alternates between C and 10 − C for ever.** The rule is a counting constraint and not a knot: it fails K2 at every
arity tested.

## What happened

| Structure (rule arm) | Lawful valued starts | Survive every step | Starts with one history |
| --- | ---: | ---: | ---: |
| Five-founder clock, 30 parent steps | 4,009 | 4,009 | 16 |
| Seven-knot source, 6 steps | 92,312 | 92,312 | 0 |
| Nine-knot drawn source, 4 steps | 449,885,231 | 449,885,231 | 0 |

- **No start is removed.** A newborn on these structures has two paid inputs and two fresh distinctions, or five or
  more places, and then every input word has a lawful completion. The case that would remove a word (three places,
  two equal inputs, one fresh) does not occur on these sources.
- **The signal fraction is not forced.** On the clock, 3,993 of the 4,009 starts reach all seven fractions from 0/6 to
  6/6. The 16 forced starts are those whose loose distinctions hold no ones or ten ones; they stay quiet.
- **The carried count.** Each newborn of the clock holds exactly two ones among two inputs and two fresh, and every
  loose distinction is paid at every step, so the ones among the loose distinctions go from C to 10 − C. A return
  signals exactly when the receiver carries one one among its two loose distinctions. The count is always even. Under
  parity alone or not-all-equal alone nothing of the kind is carried: every value from 0 to 10 occurs.
- **The hand null**, written and hashed before the run, said exactly this: forced only at C = 0 or 10, and all seven
  fractions otherwise. It was right on every start.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed | The rule fails K2 at three to seven places; each law alone reaches all 64 six-return signal patterns from the quiet start; the quiet start stays quiet under the rule |
| P1 | Failed | Every lawful start survives on all three structures |
| P2 | Failed | 3,993 of 4,009 clock starts have all seven fractions |
| P3 | Failed | Across starts all seven fractions occur |

The thread simulated the counting rule on the ring of five directly (2,000 random valued runs): the count alternated
between C and 10 − C in every run.

## What this is about

About the rule, on three recorded sources. Supplied: the rule, the reading that a word with no completion is removed,
the enrolled receiver and its signal. Exact counts of histories reach two steps on the seven-knot source and one on
the nine-knot source; survival and one-or-several histories to the full horizon were decided by a satisfiability
search instead.

**Verdict.** The lead is refuted: two laws at once do not turn a frequency into a prediction. The earlier control saw
a forced continuation only because it started from the quiet word. One thing is kept for the question of what flows
(B263): a counting rule gives ordinary growth a carried count, and neither law alone does.
