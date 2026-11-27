# Preregistration: do the record's weightings factor over knots?

Frozen before `countings.py 300 14`, `bound_facts.py` and `square_sample.py 300` are run. Written 26 November 2026,
after the advisor's attack ([question](advisor_question.md), [answer](advisor_answer.md)): it found my first check an
identity (the record's code already computes the start counting as a product) and replaced it with a test on readers no
knot joins, added two controls that should fail, gave the three treatments of the middle for restrictions, and named the
restrictions already in the record. Its values are frozen here; most are entailed, and the ones that could fail are
marked.

## Seen before freezing

A 40-start timing pilot of `countings.py` (output not read); a 10-start timing pilot of an earlier `square_sample.py`
(output not read); the third-layer referee's certificate (the five facts' carriers and their relations).

## Predictions (frozen)

**A. Countings** (300 census starts, seed 20261129, kept at 14 distinctions or fewer; parity and not-all-equal; three arms;
up to two rounds). For every pair of distinctions no knot holds together and every assignment of the rest:
1. Counting from the finish and counting from the start (stages = rounds) factor: 0 tables that do not, every law and
   arm (entailed: law indicators; one factor per birth, a function of its inputs).
2. The one-stage control (each start word's weight divided among all its finished completions at once) fails on at
   least one not-all-equal growth of two rounds (**could fail**), and never under parity (every start word then has the
   same number of completions).

**B. Bound facts** (the third-layer referee's three rings of four, rounds 1, 4, 5, 6; ring readers by lineage):
3. No change local to one ring's region flips R, S or T; changes local to ring 0 flip P and Q (together).
4. Restricted to any of the five facts or their 31 sums: e = 0 for every pair of ring readers with the middle unread or
   read for values (entailed: each fact has a representative on one ring, so the restriction is a knot missing a reader).
5. With the middle read for changes: unrestricted e = 1; fixing the third ring's whole fact gives e = 2 for the other
   two rings (the advisor's: T fixed, rings 0 and 1, from 1 to 2) (**could fail**).

**Controls** (three rings joined by nothing): 6. a + b fixed: e = 1, 1, 1 (unread, values, changes); a + b + m fixed: 0,
1, 0; ring 0's own fact fixed: 0, 0, 0; readers holding only a and b with a + b + m fixed: changes 1, values 0.

**C. The event-ready square on sampled starts** (300 census starts, seed 20261129, two rounds, three arms):
7. Fewer than half of the starts have a separated pair with e ≥ 1 with the middle read for changes, and fewer than one in
   twenty a pair with e ≥ 2, under every arm (my guess).

## What would change the reading

- A failure of prediction 1 is a non-factoring weighting the model makes: the line goes on, to a frozen test of
  separated readers on it.
- Otherwise every recorded weighting the model makes factors over knots, and the line stops.

## Scaffolds named

The census sample and its size cap; the canonical engine and its arms; the ring readers by lineage; the coherent
counting state and the middle's treatments (from the change-read study); the third-layer referee's construction.

## Deviation after the run

`square_sample.py` built a union of two regions by concatenating their lists, so a distinction held by knots of both
lineages appeared twice and `css.ebits`, which adds bits, corrupted the set (it showed e ≥ 1 with the middle unread on 18
starts, which the separability argument forbids). The union now lists each distinction once; rerun. The frozen run is
kept as `square_sample_frozen.jsonl.gz`. `countings.py` and `bound_facts.py` build no unions and are unchanged.
