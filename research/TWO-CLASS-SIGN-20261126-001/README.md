# The preserved two-class sign: where it is, and whether anything weights the classes oppositely

Epic `TWO-CLASS-SIGN-20261126-001`, under G18, at the coordinator's go-ahead, taking the direction of the
beyond-rejection study's referee: start from the preserved sign that referee found
(`READS-HOLDERS-SOURCES-20261120-001A`, its motion study: after one ordinary growth from the five-knot ring, 32,768
allowed states in two classes of 16,384, labelled by the parity of the old shared distinctions). Map it; then ask whether
any operation of ordinary growth, or any reading a local reader can make, counts the two classes with opposite weight, so
that something adds and can cancel. Computed and argued; the advisor consulted read-only inside the repository
([question](advisor_question.md), [answer](advisor_answer.md)); referee pending.

## The sign, defined

Under parity the allowed assignments S form a linear space. A **move** is, for each distinction, a shortest allowed
change through it, every tie kept (the motion study's choice); H is the space the moves generate; the **classes** are the
cosets of H in S, and every move keeps its class. A class label is a parity of values that every move leaves unchanged and
some allowed change does not. The motion study proved that with every inclusion-minimal change as a move there is always
one class: the classes belong to the choice of move. Here a second choice is read beside it, the shortest allowed changes
overall.

## A. The map ([`classes.py`](classes.py), [`classes2.py`](classes2.py), [`nae_classes.py`](nae_classes.py), [`tally.py`](tally.py))

- **Rings** (each of n knots holds its two ring distinctions and two loose ones): no classes at the start; after one
  round two classes for every n from 4 to 12, which the next stage's moves keep. Odd rings: a class change avoids every
  loose distinction (the change of the whole old ring). Even rings: the class is fixed by the loose values. In no ring can
  the class be read inside one knot: it is the parity of the whole old ring. The archive's counts are reproduced (five
  knots: 2^15 states in two classes; with loose values pinned, 64 in two classes of 32).
- **Every census start of three to five knots** (7,075; [`census_canonical.jsonl.gz`](census_canonical.jsonl.gz)): 794
  have two or more classes at the start (768 two, 24 four, 2 eight), with no symmetry needed (470 of them have no renaming
  but the identity), every one with a cycle of meetings or a double meeting (45 have only a double meeting). After one round, 510 on the engine of
  the 20 November studies, 749 on the recent line's ([`census_fold.jsonl.gz`](census_fold.jsonl.gz)); of the 594 starts
  with classes that grow, the old classes survive the next stage's moves in 359 and merge in 235.
- **But in every census start the class can be read inside one knot** (794 of 794 at the start, 379 of 394 after one
  round; [`census_checks.jsonl.gz`](census_checks.jsonl.gz), [tally](checks_tally.txt)). In the smallest case, a knot
  meeting another twice, every shortest move flips the two shared distinctions together, so their parity, which equals the
  parity of the second knot's two loose distinctions, is a class label: a value a single reader holds. Only on the rings is
  the class the parity of a whole cycle, out of reach of any one knot.
- **Not-all-equal has no such classes** with state-dependent shortest moves: one class in every ring read and in all 200
  sampled starts read at the start (104 after one round; 38 grown stages and 5 ring stages too large, not read). Single
  flips are usually allowed there, which joins everything.
- **The second choice of move** (shortest changes overall) gives far more classes (992 of 994 read starts; 2^24 on the
  twelve-knot grown ring): the count is the move rule's, not the structure's.

## B. Does anything count the classes with opposite weight? (an argument, with checks)

1. **Growth reads no values**, so it builds the same structure whatever the class of the old state.
2. **Equal weight after a round.** Under parity every allowed old state has the same number of completions; a class's
   weight after growth is |ker P| times its meet with the projection P(S′) of the grown space onto the old distinctions,
   which is zero or one common value. Checked ([`weights.py`](weights.py), [output](weights_out.txt)): of the 594 census
   starts with classes that grow, one round under the ordinary count and under both forbidding laws keeps every class, at
   equal weight (200 more do not grow: not run).
3. **Where a class change avoids the loose distinctions** (odd rings, and the 520 census starts where every class pair is
   so exchanged), adding that change to every state exchanges the classes and commutes with everything growth adds, which
   touches only loose distinctions: any law that acts through them treats the classes identically.
4. **Every weighting the laws make is nonnegative** and a value read sums it, so the classes only ever add. (This is the
   motion study's own last line, "the ordinary motion response cannot determine their probabilities because it contains
   no relative sign between distinct allowed assignments"; it is the framing, not a finding.)

**So growth treats the two classes alike, and no recorded operation counts them with opposite weight.** On the census
starts the class is a value one reader holds; on the rings it is the parity of a whole cycle, protected from every move
and from every reader of one knot, and weighted equally by every round.

## Literature (cited once; what this adds)

The rings' classes are the sectors of a classical code (S its words, H the span of its short words): the long change
around the ring is one of its logical operators and the ring's parity read is the conjugate one, the structure of the
literature's toric code (Kitaev, *Annals of Physics* 303, 2, 2003), which has both kinds of check where this has one. The
weighting with opposite sign on the two classes is the −1 state of the long change: exactly what is missing and would have
to be supplied. The even rings, whose class is fixed by the loose values, are the analogue of the literature's code with a
boundary (Bravyi and Kitaev, 1998). What this adds: the growth law's own behaviour on the sectors (kept, weighted alike)
and the finding that on small starts the class is usually a single knot's value.

## What this does not say

- That no rule could weight the classes oppositely: a supplied signed reading does (the motion study's change read).
- More than one round; other moves (inclusion-minimal moves give one class always); not-all-equal beyond the sizes read.
