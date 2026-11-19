# What a pointwise-fixed growing end preserves when junctions meet once

The question concerns a specified renaming on a positive-age stage of complete cheapest-count parity growth. Every distinction of every live junction is fixed individually. We test whether some bijection of the fresh distinctions then preserves the entire next table. Both old stages of a test may be the same arrangement.

## Predictions before running

Take four junctions A,B,C,D. Give them precisely the five shared distinctions AC,BC,AD,BD,CD. The rest meets this part only at A and B. We predict that AC and BC can exchange when two separate connections from A to B run through the rest. After a lawful round leaves just one such connection, AC and AD will read two while BC and AD still read three. This is a hypothesis about all table entries, with no ordinary pair meeting twice.

A seven-junction candidate adjoins three junctions to A, each with two loose distinctions. B has two loose distinctions and the rest have none. Round one should add the three two-parent junctions on the left and two one-parent junctions at B. Round two should gather the left three into one junction with one fresh distinction. An eight-junction variant uses two initial groups with two parents sharing one parent through distinct witnesses. A nine-junction variant keeps starting arities at most four. These are targeted constructions. They do not imply any minimum size.

## Exhaustion and controls

Generate connected simple junction arrangements. In a full tier include every assignment of loose distinctions allowed by its bound, up to renaming. State initial and reached sizes, ages, the number of stage tests, the pointwise stabilizer test, failed or omitted cases and any cap on successors. Start the width diagonal at fourteen distinctions. Extend completed tiers and pursue minimum size even after a hit. A second bound uses total reached junction count. Exhaustion of positive stages may be proved by taking an arbitrary lawful immediate predecessor and checking inheritance of the allowed-start gates. For a finite reached junction bound N and n ordinary junctions immediately before the round, no predecessor junction can spend more than N−n loose distinctions. Witnesses at larger ages or sizes outside a finished tier are samples. Report which comparisons were proved without building the successor, using equation-preserving generators. Test whole generator sets. Permutations which extend form a subgroup.

The positive control is the earlier meet-twice example. Check a legal identity and an illegal input permutation. Check reached examples by two methods for computing bonds and two methods of replaying the complete law. For the earlier example compare full three-distinction readings, mere existence of a common bond, and one fixed third distinction. Distinguish a single query ruling out the marked swap from readings that suffice for all allowed permutations of that table.

## Prior work in the program

`scripts/track.py objects "meet once pair distances pointwise live junction growing end marked symmetry extends complete round" --until 2026-11-19 --limit 6`

The closest indexed records are `EXTEND-ROUND-20261119-001`, `PARENT-RULE-20261119-001`, `CREATED-PAIR-20261119-001`. The earlier meet-once census compared whole arrangements up to renaming. The marked growing-end study tested particular permutations in its census population. The first reached obstruction in GROWN-END-SWAP uses three pairs of repeatedly meeting junctions. The independent referee confirmed it. This continuation restricts every starting pair to a single shared distinction and fixes the entire growing end pointwise. The pre-run Fable 5.2 advisor suggested testing a generating set, screening by equation preservation, and measuring a triple together with a fixed loose distinction. A complete group check and an independent replay will test those suggestions.
