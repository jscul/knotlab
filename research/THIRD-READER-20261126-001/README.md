# The middle as a third reader: a game of certainty for separated readers with no sorting?

Epic `THIRD-READER-20261126-001`, under G18, at the coordinator's go-ahead after `VALUE-CHANGE-20261126-001`, whose
square of certainty for two readers whom no knot joins needed three supplied pieces: the coherent counting state, combined
questions (a change of one set read with a value of another), and a middle reader who reads changes and whose record's
signs are applied to the score. Here the middle becomes a third reader with two settings, to remove the sorting. Computed,
with arguments; the advisor consulted read-only in the repository ([question](advisor_question.md),
[answer](advisor_answer.md)); referee pending. Every prediction frozen was entailed by the advisor's hand values, and all
held ([preregistration](preregistration.md)).

## A. Readers whom no knot joins share nothing a list cannot give (an argument, checked)

For any readers no two of which share a knot, everything else unread, the coherent counting state on their distinctions
is diagonal in a product of local bases: an allowed change supported on the readers splits into one allowed change per
reader (each knot meets at most one reader), so every certainty's change part is local, and each reader's parts of the
certainties commute among themselves. So their joint table has a list of values, whatever they read, and they may still
share value information. The advisor's shorter proof (from the change-read study's referee) widens it: fix the unread
values and each knot constrains at most one reader, so the completions factor; it needs no linearity (not-all-equal too)
and holds for any amplitude that is a product of one factor per knot. Three ways out exist: a reader joined to the others
takes part, its record sorts the table, or the state carries a factor no knot holds (the side-sign study's supplied
signed weighting). In the literature's terms this is the conditional independence of a factor graph given a separating
set (Hein, Eisert and Briegel, 2004, for graph states).

## B. Three readers on the joined-ring starts ([`tripartite.py`](tripartite.py), [output](tripartite_out.jsonl.gz))

The ring readers hold their rings' regions; the middle holds everything else, so the three hold the whole pure state.
The count of shared triples g (the literature's GHZ count of a stabiliser state, Bravyi, Fattal and Gottesman, 2006),
computed four ways that agree on every row, is exactly the advisor's table: g = 1 for every pair of rings joined by a dead
chain (the two-ring family included), 0 for the chain holding a loose distinction, 2 for one reader holding two rings
(1 on the loose family), at every round read. As the advisor showed, g is the ring readers' value correlation, the same
number the change-read study counted: not a new count. No birth has parents in two regions through round 2.

**The game, at round 0.** Each reader's two settings: the change read of its part of a change running through the link
(a loose distinction of a ring knot, its attachment, the link, the other attachment, a loose distinction there), and a
quarter-turn read of that part with its part of a connecting knot's law. On the three three-ring families with dead
chains (chains of knots and direct links) the readers win the literature's three-reader game (Mermin, 1990) with
certainty, where a list of values wins at most 3/4; on the loose-chain family exactly 3/4. Every probability is
nonnegative and no reader or pair of readers sees another's setting.

## C. But the third reader shares knots with both

**A list in which the middle hears both ring settings gives the same table**, exactly, on all four families: the ring
readers answer fair coins, and the middle answers the product's certain sign times their answers where the three reads'
product is a certainty, a fair coin otherwise. The game's bound of 3/4 holds only if no reader's answer depends on
another's setting, and the middle touches both rings through the connecting knots. So the second middle setting does not
make the test fairer than the sorted square: the sorted square too is won by a middle that hears the row and the column.
By part A this is forced: three readers whom no knot joins share nothing a list cannot give, so any excess needs a joined
reader taking part or sorting.

## D. Which reads it needs ([`real_paradox.py`](real_paradox.py), [output](real_paradox_out.txt))

With positive amplitudes and real reads (no quarter-turn), no three-reader game of certainty exists on one or two copies
of the shared triple, with two settings per reader (0 of 46,656 choices on two copies) or three (0 of 592,704). The
advisor's lemma explains it and was checked on every certainty: draw an allowed word and an independent sum of laws, and
each real read i^|x∧z| X^x Z^z is answered by the parity |x∧z|/2 + (word · z) + (sum · x), which reproduces every
table for one read per reader, any number of settings. A positive control with signed amplitudes (the literature's graph
state of three) gives a real game of certainty, so the claim is "for positive amplitudes". So without sorting, the game
needs a **quarter-turn read**, a fourth supplied piece, or a reader reading together two reads whose change and value parts
cross oddly (as the square's rows do).

## E. Scoping: does any birth's law depend on two allowed states of its parents?

**No** (read in the engines: `freelib.py` 140–170 and 230–249 of the fresh-count study, `rival_growth.py`). A birth's law
is even parity. Its fresh count is the demand (how many next-round groups hold it), floored at three places and one
fresh distinction, unless its parity is implied. "Implied" is decided from the holders alone: the birth takes every loose
distinction of its component (checked by GF(2) elimination as a second route). Implied means the inputs' parity is the
same on every allowed state, a statement true of each allowed state separately, not a comparison of two. Equivalently no
allowed change flips the inputs' parity, so the closing rule is the one place growth's law is fixed by the allowed changes
collectively, but it reads no change: it reads a law.

## So

Removing the sorting is not possible while keeping all readers separated: three readers whom no knot joins share nothing
a list cannot give. Making the middle a reader with two settings gives a game of certainty, but at the cost of a
quarter-turn read (a fourth supplied piece), and with a third reader who shares knots with both others, so a list that
lets it hear their settings wins too. The event-ready square of the change-read study, with the middle's record applied,
remains the fairest table the line has, and it rests on three supplied pieces: the coherent counting state, combined
questions and the middle reader.

## What this does not say

- Anything about sampled starts or rounds of growth for the game (round 0 of built starts; growth plays no part).
- That no growth law could read a change; only that the recorded ones do not.
- The three-reader value 4 is not new: the rule-R study's part C had it on the four-knot closure.

## Scaffolds

The middle as one reader holding every distinction outside the two rings; its two settings; the quarter-turn read; the
coherent counting state and combined questions (from the change-read study); the 'places' regions; the built families at
round 0 for the game. The separability argument is about the model's reads in any state whose amplitude is a product of
one factor per knot; the game is about these scaffolds.
