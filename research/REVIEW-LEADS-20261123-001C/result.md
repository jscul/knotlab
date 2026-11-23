# Uniform present words with births as the settings: result

Ticket `REVIEW-LEADS-20261123-001C` (B309; G18 with G17), 2026-11-23. Two arguments and an exhaustive census;
scientific referee pending. [Pre-registration](preregistration.md) · [full tables and commands](results_draft.md) ·
[the argument for one shared distinction](one_shared_distinction.md) ·
[deviations](../../experiments/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words/deviations.md)

**With every present word weighted equally and the setting supplied as which not-all-equal birth happens, no structure
of parity and not-all-equal knots with two holders per distinction, in any class searched, gives a four-correlation
score above 2 while both complete records hide the far setting. A distribution that does give 20/9 exists and is the
best found; making it needs a value to be handed to two users, which two holders per distinction do not allow in any
class searched. And the setting the study took as its first choice, which of its two loose distinctions a knot pays,
turns out to be a renaming and not a setting at all.**

## What was searched

| Class of sides | Shared distinctions between the sides | Side tables | Pairs combined | Hidden pairs | Largest score when hidden |
| --- | ---: | ---: | ---: | ---: | --- |
| At most 3 knots, 3 internal distinctions | 1 | 596 | 245,025 | 130,427 | exactly 2 |
| At most 3 knots, 3 internal distinctions | 2 | 3,018 | 6,943,225 | 2,962,619 | exactly 2 |
| At most 4 knots, 5 internal distinctions | 1 | 8,647 | 5.54 million | 2.90 million | exactly 2 |
| At most 4 knots, 5 internal distinctions | 2 | 51,596 | 216.28 million | 79.56 million | exactly 2 |
| Up to 6 knots, seeded draws (exploratory) | 1 and 2 | 1,392,879 structures | 284.4 million | 219.8 million | exactly 2 |

The two smaller classes are exhausted over every ordered pair; the larger over every pair up to the 32 renamings that
leave the score unchanged. Among hidden tables that reach 2 (879 in the smaller class, 14,774 in the larger) the best
score over every two-valued function of the complete record is still 2, and the 50 tested by linear programming all
have one common local explanation. Without the hiding requirement the classes reach 8/3, with a complete record
changing by 1/6. The control weighting, in which an old word keeps its weight, never exceeds 2.

## The two arguments

**One shared distinction.** If the two sides share exactly one two-valued distinction, hidden settings force one
weighting on its two values and local chances that reproduce all four tables. Written before the census
([argument](one_shared_distinction.md)); every pair with one shared distinction agrees.

**Two loose distinctions of one knot are the same up to their names.** Parity and not-all-equal knots do not tell their
places apart, and a loose distinction has no other holder. So exchanging two loose distinctions of one knot carries
the old allowed words onto themselves. If Alice's x2 and x3 are such a pair, the structure finished at her second
setting is the structure finished at her first with those two names exchanged. Her two settings are then two
functions of one record, and with her record hidden from Bob's setting the four tables have a common explanation
(take her record as what is shared, with Bob's average answer given her record as his chance). If both sides are of
this kind no hiding is needed. Found by the study's implementer and checked by the thread; all 152.8 million pairs of
that class score at most 2.

This settles more than the class. A knot that owes one payment and holds two loose distinctions is not told which to
pay, but the two ways give the same structure with two names exchanged. The audit study measured a difference of
5/23 between the two ways on a three-knot example; that number is the size of the renaming on the named distribution
and nothing more. A payment allocation is not a setting.

## The distribution that reaches 20/9

The largest score found over arbitrary side tables with two shared distinctions, under exact hiding, is 20/9: the
four-type distribution of the pre-registration, written as two side tables. Alice's side must force her x2 and x3 to
differ and tie one shared distinction to her x1 or the other to her x2, according to whether x1 and x3 differ. Bob's
side must hand his y1 and y2 into the two shared distinctions and force his y2 and y3 to differ. On that table a
linear program finds no common local explanation (residual 4/27), and a setting keyed to an old value changes the
other observer's complete record by 1/9. A search of about 1.1 million corner points found nothing above 20/9; that is
a lower bound on the largest score, not a proof.

Each of those requirements asks one value to do two jobs while its distinction stays loose for the birth: to be
compared with a neighbour and to be handed across. With two holders per distinction a value can be handed on along a
chain and cannot be handed to two users. That is a reason for the null and not a proof of it.

## After the stop: with more than two holders the distribution can be made

Exploratory, by the thread, after this ticket closed; not frozen and not the engine.
[Script](../REVIEW-LEADS-20261123-001/posthoc/three_holders_check.py). Eighteen three-place knots, thirteen on
Alice's side and five on Bob's, parity and not-all-equal only, make exactly the two side tables of the 20/9
distribution when six internal distinctions may have three or four holders. Brute-force enumeration gives 512 old
words, a score of 20/9 and both complete records hiding the far setting. Each knot passes the canonical test on its
own; what is not ordinary is the distinction with a third holder, which ordinary growth never makes. So in this
reading the two-holder rule is the wall: with it, nothing found in several hundred million pairs; without it, an
explicit structure.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed | The four-type table gives exactly 20/9, hidden; brute-force enumeration of the finished structures matches the product of side tables on 200 pairs; the control weighting never exceeds 2 |
| P1 | Held | One shared distinction: at most exactly 2 when hidden, in every class |
| P2 | Held | Reference 20/9, verified exactly |
| P3 | Held | Two shared distinctions: at most exactly 2 when hidden, in every class |
| P4 | Held | 8/3 without hiding |

The thread re-evaluated the reference pair with its own earlier code: 20/9, hidden.

## What this is about

Supplied: the weighting; the observers and their records; the setting, which here is a choice between two births with
different parents and so a choice between starts, since ordinary growth fixes its parent groups from the holdings; the
classes searched. The classes are finite and the null is a null for those classes. The 4-knot class was read as at
most five internal distinctions, since four knots need at least four. Block files of hidden tables were removed from
the outputs before the commit and can be regenerated (`PRUNED.md` in the output folder).

**Verdict.** The lead reached its stop on the negative side: no lawful structure, the class exhausted, and one bound
proved for a single shared distinction. What is learned is where the wall stands. The weighting does give an excess at
the level of distributions, hidden and all. Knots with two holders per distinction do not make that distribution in
several hundred million tries, and the missing operation is handing one value to two users.
