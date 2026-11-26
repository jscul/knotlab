# The question to the advisor (26 November 2026): look for a counterexample

You are running inside the repository with read-only access. Please look for counterexamples and check the code rather
than give a verdict; short answers.

The study (`research/TWO-CLASS-SIGN-20261126-001/`, programs `classes.py`, `nae_classes.py`, `weights.py`, outputs
`census_*.jsonl`, `rings_*.jsonl`, `nae_*.jsonl`, `weights_out.txt`) maps the preserved two-class sign of
`research/READS-HOLDERS-SOURCES-20261120-001A/motion.md` (under parity, the allowed space S; moves = for each
distinction the shortest allowed changes through it; H their span; classes = cosets of H in S) and asks whether any
operation of ordinary growth, or any reading a local reader can make, makes the classes count with opposite weight.

Found so far: under parity, 794 of the 7,075 census starts have two or more classes at the start (530 where some class
change avoids every loose distinction, 264 where the class is fixed by loose values); after one round, 510 (canonical
engine) or 749 (the recent line's engine); rings reproduce the archive (five knots, two loose each: 32,768 states in two
classes after one round); odd rings keep two classes with a class change avoiding the loose distinctions, even rings'
classes are fixed by loose values. Under not-all-equal with state-dependent shortest moves: one class in every ring and
in all 200 sampled starts read. And one round of growth under the ordinary count and both forbidding laws keeps every
class of every census start with two or more, at equal weight.

My argument that nothing makes them count with opposite weight: (1) growth reads no values; (2) under parity every
allowed old state has the same number of completions, and a class's weight after growth is |ker P| times its meet with
the projection P(S') onto the old distinctions, which is 0 or a common value; (3) where a class change avoids the loose
distinctions, adding it to every state exchanges the classes and commutes with every constraint growth adds (growth
only touches loose distinctions), so the classes are treated identically by any law acting through loose distinctions,
and a reader of loose values cannot tell them apart; (4) every weighting the laws make is nonnegative, and a value read
sums weights; so the classes only ever add.

1. Find a counterexample to (2), (3) or (4) in the recorded laws, or a bug in the programs (especially the move
   definition and the "avoids the loose distinctions" test).
2. Is there any recorded operation (a reading, a count, a rule in any study) that does weight the classes with opposite
   sign? Name it with its file.
3. Is the literature link right: the classes as a code's logical sectors (local moves keep them; the long ring change, an
   allowed change outside H, exchanges them), as in the toric code?
