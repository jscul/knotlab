# Counting the states that pass a braid test

November 14, 2026 (Pacific). Goals G3 and G16.

## The question

Which distinctions survive when the same single-strand terminal conditions return parity or the number of allowed input states? Determine exactly which tables these richer readers confuse and whether one additional type of observation recovers an entire table.

## Prior work in the program

`scripts/track.py objects "braid readout" --until 2026-11-14 --exclude BRAID-COUNTS-20261114-001 --limit 3`

`scripts/track.py objects "finite Radon transform" --until 2026-11-14 --exclude BRAID-COUNTS-20261114-001 --limit 3`

`scripts/track.py objects "counting parity allowed tables" --until 2026-11-14 --exclude BRAID-COUNTS-20261114-001 --limit 3`

- `HIDDEN-COPY-20261112-001` studied Additive readouts of small stitched-harmony gadgets against diagonal-preserving random relations. Here the query positions are precisely the affine braid powers and the compared data are integer counts, count parities and existential support.
- `RULER-FLAT-20261111-001` studied Undirected non-orientable six-regular two-fold weaves. Here the query positions are precisely the affine braid powers and the compared data are integer counts, count parities and existential support.
- `PLACE-FLIP-20261110-001` studied Board-value knots read by flips in place in copies of finite boards. Here the query positions are precisely the affine braid powers and the compared data are integer counts, count parities and existential support.
- `LEIBNIZ-BOARDS-20261110-001` studied Boards identified by agreement of every finite view. Here the query positions are precisely the affine braid powers and the compared data are integer counts, count parities and existential support.
- `BRANCH-DEPTH-20261112-001` studied Depths reached by unrestricted bonds of a fixed maximum size k on a repeating branch. Here the query positions are precisely the affine braid powers and the compared data are integer counts, count parities and existential support.
- `WITNESS-COUNT-20261112-001` studied Least all-equal call counts at dead depths of genuine limit-only nested not-all-equal families. Here the query positions are precisely the affine braid powers and the compared data are integer counts, count parities and existential support.
- `KNOTS-ALONE-20261111-001` studied Connected two-fold weaves under the uniform parity knot. Here the query positions are precisely the affine braid powers and the compared data are integer counts, count parities and existential support.

BRAID-READOUT-20261114-001Z supplies the accepted existence-only results. STRAND-RETURN-20261114-001 had already published all 512 source masks. The question here changes which statistic answers each future restriction. INTERFERENCE-20261029-001 studies signed Boolean witness semantics; that study uses different relations and tests.

## Prior work outside the program

Finite Radon transforms sum a function on lines in a discrete affine plane. The incidence identities and finite Fourier inversion are classical; see Matúš and Flusser, Image Representation via a Finite Radon Transform (1993), https://utia.cas.cz/en/people/?pid=74, with exact comparison in the leaf. Class counts for binary tables and the matched comparison with the existential SAT reader are the local targets.

## Evidence and stopping rule

Exhaust all 512 three-label tables, group them separately by existential supports, parity and integer counts, and compare by an algebraic derivation. Seek an example in both directions when two observers disagree. Check a higher prime, including extremal aliases, and separately check characteristic two. Stop when the exact integer/parity ambiguity is characterized or refuted. Distinguish message memory from solver work.
