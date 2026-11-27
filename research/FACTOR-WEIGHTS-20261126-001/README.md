# Do the record's weightings factor over knots? The one way out of the separability argument

Epic `FACTOR-WEIGHTS-20261126-001`, under G18, at the coordinator's pick after `THIRD-READER-20261126-001`, whose part A
showed that readers whom no knot joins share nothing a list of values cannot give in any state whose weighting is a
product of one factor per knot. The one way out left is a weighting that does not factor. Here the record's own
weightings are tested: the two countings (`TWO-COUNTINGS-20261125-001`) and a restriction to one value of a bound
whole-held fact (the third-layer referee's three rings of four). Computed; the advisor consulted read-only in the
repository ([question](advisor_question.md), [answer](advisor_answer.md)); referee pending.
[Preregistration](preregistration.md), frozen before the runs, with one deviation recorded.

## A. Both countings factor ([`countings.py`](countings.py), [output](countings_out.txt))

The test (the advisor's): for every pair of distinctions no knot holds together and every assignment of the rest, the
two-by-two table of weights has rank at most one, as a weighting that is a product of one factor per knot must. On 300
census starts (uniform over the census, seed 20261129; 69 to 70 parity and 17 to 21 not-all-equal growths per arm kept
at 14 distinctions or fewer), up to two rounds, parity and not-all-equal, the three arms of the canonical engine:

| Weighting | Tables tested | Tables that do not factor |
|---|---:|---:|
| Counting from the finish (every allowed word once) | 4,303,444 | **0** |
| Counting from the start (rounds as stages; the record's definition) | 4,303,444 | **0** |
| Control: each start word divided among all its finished completions at once (not the record's) | 4,303,444 | 1,476, on 7 not-all-equal growths; none under parity |

So both recorded countings factor over knots on every growth read, under every arm: the start counting gives one factor
per birth (its law divided by the number of fresh assignments its own inputs allow), because the births of a round have
disjoint fresh distinctions (`TWO-COUNTINGS` definitions, 1.5). The control shows the test can fail: dividing over the
whole growth at once ties together births that no knot joins. Two corollaries the advisor drew: factoring does not part
the two countings (the finish's 20/9 excess of the setting-as-reread study arose under a factoring weighting, because its
four setting pairs are four structures, outside one state's argument); and what keeps the start counting at 2 there is
the division at each birth, not factoring.

## B. Restricting to a bound fact leaves ring readers separated ([`bound_facts.py`](bound_facts.py), [output](bound_facts_out.jsonl.gz))

On the referee's three rings of four at rounds 1, 4, 5 and 6, with ring readers by lineage: no change local to a ring
flips R, S or T; changes local to the first ring flip P and Q together (16 of the 31 sums). Restricted to any of the 31
sums of the five facts, **e = 0 for every pair of ring readers with the middle unread or read for values**: each fact has a
representative on one ring, so the restriction is one more knot missing a reader, and the separability argument applies
unchanged (the advisor's shorter proof). With the middle read for changes (the event-ready arrangement), fixing the third
ring's whole fact raises e from 1 to 2 for the other two rings at every round, so the square of certainty becomes
available to two single-ring readers, still sorted by the middle's record.

**Controls** (three rings joined by nothing): fixing the joint parity of one loose distinction of each of two rings gives
e = 1 under every treatment (a restriction no knot holds that does join the readers); adding a third ring's distinction
to it gives 1 only with the middle read for values; one ring's own fact gives 0. One frozen control failed: readers
holding only a and b, with a + b + m fixed and the middle read for changes, give 0, not 1 (the advisor's value; the
value law partner includes m, in the middle).

**Does the model restrict to a fact's value?** Not under ordinary growth: a birth with no fresh distinction is implied
(`freelib.py` 163–164), so it fixes nothing. The record's restrictions are the forbidding arms' cut births (each a knot's
law, so a factor: part A's start counting factors on those arms too), the side-sign study's supplied weightings, and
tables sorted on a combined read.

## C. The event-ready square on sampled starts ([`square_sample.py`](square_sample.py), [tally](square_tally.txt))

On 300 census starts (uniform, seed 20261129), grown two rounds, regions by start-knot lineage: 82 starts have a pair
of regions no knot joins (154 such pairs); 13 have a pair with one shared pair once the middle is read for changes; **none
has a pair with two**, so the square is never available, under any of the three arms. With the middle unread, e = 0 on
every separated pair, as the separability argument says (a bug that repeated names in unions showed otherwise in the
frozen run; recorded as a deviation).

## So

**Every weighting the model makes factors over knots** (counting from the finish, counting from the start with rounds as
stages, under both laws and all three arms; start values, a product over distinctions), so readers whom no knot joins
share nothing a list cannot give unless something is supplied: a middle reader whose record sorts, combined questions,
the coherent counting state, or a weighting that does not factor (the side-sign study's, supplied). Restricting to a
bound fact does not change that for ring readers. By the coordinator's criterion this line stops.

## What this does not say

- Anything about structures over 14 distinctions in part A, or more than two rounds (part A) or six (part B).
- That no growth law could make a non-factoring weighting; only that the recorded ones do not.

## Scaffolds

The census sample and its cap (part A keeps 69 or 70 of 300 starts per arm under parity, 17 to 21 under not-all-equal); the canonical engine and its arms;
ring readers by lineage; the coherent counting state and the middle's treatments (from the change-read study); the
third-layer referee's construction. Part A is about the model's countings; part B's restriction is a test, not a
scaffold the model uses.
