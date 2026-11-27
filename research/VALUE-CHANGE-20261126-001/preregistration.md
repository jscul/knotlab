# Preregistration: values and changes on the joined-ring starts (part C)

Frozen before `rings.py 2` is run. Written 26 November 2026, after the advisor's attack ([question](advisor_question.md),
[answer](advisor_answer.md)): it found my drafted predictions entailed by hand, one of them wrong after round 0 (the
control), and pointed to the cases that are not entailed by my reader choice (one reader holding two rings; the family
with a loose distinction in a chain; a middle of one distinction). Its by-hand values are now the predictions; a run
that differs overturns its argument there. Part A (the advisor's three checks) was run before this freeze.

## Seen before freezing

Code checks on the ring of three, the four-knot closure and a lone knot (`css.py` against hand values), and a smoke
test of `css.square` on the three-rings-of-four start with two single distinctions as readers (no square, as e < 2).

## Predictions (frozen)

1. Every separated pair of rings, under both reader choices ('places' and 'own'), in every family, rounds 0 to 2:
   e = 0 with the middle unread and with the middle read for values (entailed by the separability argument), e = 1
   with the middle read for changes; the advisor's rank identities agree with `css.ebits` on every row.
2. With only the distinction the pair's two connecting knots share read for its change, the rest unread: e = 1.
3. The control, two adjacent knots of ring 0: e = 1, 1, 1 (unread, changes, values) at round 0; 0, 1, 0 at rounds 1 and 2.
4. One reader holding rings 0 and 2 against ring 1, the three-ring families, round 0: e = 2 with the middle read for
   changes, 0 unread and 0 read for values; the square has 9 of 9 cells certain in the sorted state and its rows and
   columns commute on the first reader's side.
5. The family with a loose distinction at the first chain's middle knot, round 0: e(changes) = 0 for rings 0 and 1, 1
   for the other two pairs.

## Argued, not computed

With values and changes each read alone (no combined question), every table has a list of values: draw an allowed word
and, independently, a sum of knot laws; a value read answers the word, a change read answers the sum (the literature's
rebit result, Delfosse, Allard Guerin, Bian and Raussendorf, 2015). So an excess needs combined questions. With e = 1,
Pauli reads keep CHSH at most 2 (a rotated read reaches 2√2); with e ≥ 2 the square gives certainty where a list of
values wins at most 8 of 9.

## Scaffolds named

The reader choice ('places', 'own', and the union of two rings), the middle's treatment (unread, read for changes, read
for values, one distinction read), the families (BUILT-BINDING's builder; not sampled), the engine (canonical), the
coherent counting state (supplied).

## Deviation after the run

`css.square` first chose its two pairs greedily from basis vectors and found none on two rows (the direct-link family,
round 2) where e = 2. It now clears the remaining vectors against each chosen pair (symplectic Gram-Schmidt over GF(2)).
Rerun: every other field of `rings_out.jsonl` is identical; the frozen run is kept as `rings_out_frozen.jsonl.gz`.
`frozen.sha256` keeps the hashes of the files as frozen.
