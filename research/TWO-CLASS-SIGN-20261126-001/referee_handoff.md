# Referee hand-off: the preserved two-class sign

Epic `TWO-CLASS-SIGN-20261126-001`, closed 26 November 2026, referee pending. [What stands](decision.md) ·
[the note](README.md).

1. **The map** (`classes.py`, `classes2.py`, `census_*.jsonl.gz`, `rings*.jsonl.gz`): with the motion study's moves,
   794 of 7,075 small starts have two or more classes; rings of 4 to 12 knots gain two after one round (odd rings: a class
   change avoids the loose distinctions; even rings: fixed by loose values); on every census start the class can be read
   inside one knot; none under not-all-equal in what was read (`nae_classes.py`).
2. **Equal weight** (`weights.py`): one round under the ordinary count and both forbidding laws keeps every class of 594
   census starts at equal weight.
3. **The argument** that nothing counts the classes with opposite weight (README, part B).
Check the move definition against the motion study (`research/READS-HOLDERS-SOURCES-20261120-001A/motion.md`), the
"read inside one knot" test, and the counts on a seeded sample with your own code.
