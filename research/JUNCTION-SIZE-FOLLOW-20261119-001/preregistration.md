# Largest junction under complete parity growth

Does one finite start keep the size of every exhausted junction bounded at every complete round?

Each of the 26,441 distinct touch-census starts receives equal weight in the census. Use separately a uniform labelled Prüfer tree, a uniform recursive tree with random final naming, and a uniform labelled tree with ceil((m−1)/4) different extra meetings sampled without replacement. Give each site max(0,3−degree) loose distinctions. Each weighting is sampled independently within each size. Count draws that cannot begin, close, continue or hit a cap. Probe all 26,441 and the 960 independently generated starts to as many full rounds as the controls permit, first targeting ten and extending to sixteen or twenty-four as feasible. Repeated rosters with identical open counts and blocks may be cached if relabeling is checked. Predict that the sparse earlier ceiling of eight is family-specific and that the partnered recurrence has unbounded birth support. A single-block burst should instead have a finite bound even when its round population is enormous. Report the number of observations as well as the depth, and any symbolic continuation separately. Theorem M yields a fixed order along every start whose largest junction is bounded, and at a given observed stage the current finite size suffices for its entire future.

**Decision.** A proof of a size bound for a named class or an explicit finite start with unbounded junction sizes, then distinguish the WALL-READ partnered start and MERGE-BURST cases.

## Prior work in the program

`python3 -B scripts/track.py objects "largest exhausted junction partnered growth places open count" --until 2026-11-19 --exclude JUNCTION-SIZE-FOLLOW-20261119-001 --limit 3`

`python3 -B scripts/track.py objects "maximum vertex arity iterated clique graph" --until 2026-11-19 --exclude JUNCTION-SIZE-FOLLOW-20261119-001 --limit 3`

`python3 -B scripts/track.py objects "touch census reached stages complete rounds" --until 2026-11-19 --exclude JUNCTION-SIZE-FOLLOW-20261119-001 --limit 3`

THREE-RIGID contains Theorem M and the sparse census probe. WALL-READ Theorem 1 supplies the partnered recurrence. MERGE-BURST distinguishes finite binomial bursts from unresolved sampled starts. Other records use degree, contact or reached stages with different observables.

Other retrieved records, included with their scope given by the objects index, are `ADDR-KNOTS-20261113-001`, `GROWN-PAIR-20261119-001`, `MEET-ONCE-20261119-001`, `PARENT-RULE-20261119-001`, `RING-READ-20261118-001`, `TRUE-BOND-20261113-001`, `WALL-READ-20261119-001`.
