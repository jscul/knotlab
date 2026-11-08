# CRYSTAL-UP-20261108-001A-E001: interpretation

**Stopped after 12 of 203 seeds (11:36 UTC, 2026-11-08); superseded by E002.** The control passed: for the constant decoration
00000 / 11111 the rhombus seed's two patches gave 2 strict periods spanning exactly the rhombus lattice, and its torus of 4 tiles
completed and passed the check (126.5 seconds into the run).

**Why it was stopped.** On all 12 seeds, every one of the 1,440 torus attempts (120 lattices each) was invalid: the seed collar
could not be placed on the torus without overlapping its own translates or meeting them with other labels. Two facts the contract
did not use make that expected. Tiles of one orbit share their shape and label, so a crystal containing a seed collar has at least
as many tiles per period as the collar has (shape, label) classes, 8 to 17 for these seeds; the 120 smallest lattices sat mostly
below that. And a period must map the seed collar's tiles to tiles, which most patch periods fail. Running the other 191 seeds would
have tested only lattices the seed cannot fit, so the run was stopped and E002 was frozen with both conditions as exact filters.

**What it shows.** Nothing about crystals: the attempted lattices could not carry the seeds. The patches themselves rarely repeat:
on 10 of the 12 seeds no two complete tiles share shape, label and labelled collar (strict periods 0; the other two give 3 and 5),
as in the pre-freeze probe at distance 3.

**Process note.** The ticket's activation command failed on a flag and was rerun 9 seconds after this run started, while it was
still in setup; no result had been read.
