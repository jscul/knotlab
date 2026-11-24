# What gives a distinction a third holder

Note by the thread for epic `THIRD-HOLDER-20261123-001`, 2026-11-23, written while its two studies ran. One argument,
one small check and a reading of the record. Scientific referee pending.

## What a third holder is for

The 20/9 distribution asks each side to use one of an observer's values twice while the distinction that carries it
stays loose for the birth: once to compare it with a neighbour and once to hand it across. Two parity knots that share
two distinctions tie their third distinctions (even(x, p, q) with even(c, p, q) forces c = x). That hands a value on
once. A third knot on the same pair hands it on twice, and gives p and q a third holder.

## Parity knots with two holders hand a value on once and never twice

Take a connected part made of parity knots in which every distinction has one or two holders, and call an end of the
part a distinction with only one holder inside it: a loose distinction, or one whose other holder is a knot outside
the part. The bond-closure study proved that a rule of the part on loose distinctions alone must contain every one of
them ([criterion](../BOND-CLOSURE-20261120-001/criterion.md)); treating outside holders as loose, the same holds for
ends. So the ends of such a part satisfy exactly one rule, their total parity, and no other.

Two consequences. A part with exactly two ends ties them, which is the copy above. A part with three or more ends
ties no two of them. So no part of parity knots with two holders per distinction presents one value at three of its
ends: it cannot take a loose value and hand it to two users. This is proved for parity parts only. A not-all-equal
knot is not a parity rule and the argument says nothing about parts that contain one; for those the evidence is the
census of the review-leads epic (no hidden excess in 506 million pairs).

## The record already has a copy made of not-all-equal knots, and it has a third holder

The nesting study proved by hand that the Fano pattern less one knot ties that knot's three distinctions
([its note](../SUBST-NEST-20261112-001/subst_nest.md)). A direct check ([script](fano_copy_check.py)): seven
distinctions with the seven not-all-equal knots {i, i + 1, i + 3} allow no word; leave any one knot out and 10 words
remain, in every one of which that knot's three distinctions are equal. In that structure the three tied distinctions have two
holders and the other four have three. So not-all-equal knots can hand one value to three places, and when they do,
some distinction has a third holder. With two holders per distinction every not-all-equal structure allows a word
(recorded in the postulates basket, B265), and no copy made of them has been found.

## Which recorded moves give a third holder

| Move or structure | Third holder? | Why |
| --- | --- | --- |
| Ordinary growth | Never | A birth takes loose distinctions and adds fresh ones; no knot gains a distinction (checked on 403 rounds by the audit of the review-leads epic) |
| The rival fresh-count laws (joins that forbid) | No | They change how many fresh distinctions a birth gets |
| Joins across spent knots | No | The shared distinction between two spent knots permits a birth; the live neighbours pay with loose distinctions |
| A fresh distinction shared by two existing knots (B255, not yet run) | No | The fresh distinction has two holders; two existing knots gain a place each |
| Merging two distinctions the allowed words prove equal | It can, without handing anything on | The merged distinction has the holders of both, so it may have three or four; but the tie it renames was already there |
| Built patterns: the Fano pieces, the bounded-bond pattern, the nesting study's copies | Yes | Three, six and three holders; none is grown by a recorded law |

No recorded growth move gives a third holder to a value that is not already tied. The move that would: a birth that
takes a distinction which already has two holders. Under ordinary growth a value is read once, by the one birth that
takes its loose distinction; that move would let it be read again.

## What the two studies added

Ticket B found the move at work. A structure of seven knots in which no distinction has more than two holders gives a
hidden excess as soon as the setting birth takes distinctions that are already shared; with loose observer
distinctions nothing with at most three holders was found. So the third holder that matters is the one a birth gives
when it takes a shared distinction. [The smallest structure](../THIRD-HOLDER-20261123-001B/result.md)
