# The first three-parent join at width eighteen

**Standard statement.** Consider the binary relations obtained by the serial parity extension rule below. To each pair of coordinates assign the minimum size minus one of an inclusion-minimal nonempty dual support containing them, with infinity when no such support exists. On eighteen coordinates, determine the next legal input sets in the table class of the designated seven-check relation. Also compare the input sets across every same-width table class, including every permutation that preserves a table.

**Nearest known result.** The all-size inverse in the program assumes exactly three fresh coordinates after every join. The earlier variable-output pilot checked all sizes through six junctions and compared the designated seven-junction example only with itself. This proof exhausts one width with either fresh count allowed and gives an exact obstruction to the unrestricted inverse. External novelty is unassessed. [Fixed-count proof](../../BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/proof.md) · [Pilot](../../../research/VARIABLE-OUTPUT-READER-20261118-001/companion.md)

## Claim

1. Among all 3,495 reachable arrangements of width eighteen, the designated table belongs to exactly one incidence type. All 48 permutations preserving it preserve the junctions, the 2,048 allowed states and the legal next input sets. The eighth junction has 9 single, 17 two-parent and 12 three-parent choices. At each choice either fresh count is legal.
2. For this table a triple is legal exactly when its three mutual bond distances, sorted, are `(6,8,8)`. Pooling all scalar distances above four still preserves the entire menu on this class. Pooling above three loses legal triples.
3. At this width the full table distinguishes every incidence type. All of its permutations preserve the three-parent menu on every type. Six types, each with eight existing junctions, nevertheless admit a table-preserving permutation that changes a single or two-parent choice for the ninth junction. In one of these types even two identical full state relations on the same eighteen distinctions have different single and two-parent choices. This refutes the all-finite-stages inverse for the complete menu when two or three fresh distinctions are permitted.

## Rule and completeness of the population

The seed has three loose distinctions and even parity. Each subsequent junction takes one loose distinction from each of one, two or three distinct parents. Every pair of parents must already share an ordinary neighbor. For three parents, none may be a neighbor of all three. The junction also takes two or three fresh distinctions, imposes even parity on its whole support and leaves the fresh distinctions loose. The consumed distinctions retain their identity and now belong to two junctions. A loose distinction belongs to one. All admissible choices at the current stage depend only on these incidences.

If the numbers of two-output and three-output additions are `a,b`, then `2a + 3b = 18 − 3 = 15`. Its solutions `(0,5), (3,3), (6,1)` give six, seven and eight existing junctions. A junction has at most one meeting with any particular earlier one, because a join uses distinct parents. The meetings stay bipartite by induction. For two or three parents, their pairwise common neighbors put all parents on the same side. A new junction can go on the opposite side. Each meeting uses a single distinct shared bit and all other bits are loose.

The forward enumeration stores the current meetings and the number of loose distinctions at each junction. These data specify the entire incidence up to renaming. Loose bits at one parent can be exchanged independently and produce isomorphic successors. Every representative is expanded at every legal parent set and with both output counts. Prefixes are pruned only when additions of two or three can no longer attain eighteen. The equality test on incidences requires a bijection of junctions preserving meetings and loose counts. Distance equality is never used to prune growth. Induction therefore covers every reachable incidence type.

The independent enumeration generates connected bipartite meeting patterns of degree at most six, on all three eligible numbers of junctions. It attaches every possible loose count from zero to three, with width eighteen and junction sizes from three to six, modulo renamings of the meeting pattern. For each candidate it tries every possible last junction. Its earlier neighbors must be legal parents, its support size minus their count must be two or three and returning its used bits to its parents cannot exceed their loose-bit capacity. It then recurses to a three-place seed. Reversing a successful removal order gives an actual construction. Conversely the last junction of any legal construction passes these tests. The two counts agree in every row. [Forward checker](check_width.py) · [Reverse checker](check_reference.py)

| Existing junctions | Reachable meeting patterns before loose counts | Incidence types on eighteen distinctions | Types with an ambiguous next menu |
| ---: | ---: | ---: | ---: |
| 6 | 14 | 89 | 0 |
| 7 | 36 | 1,609 | 0 |
| 8 | 125 | 1,797 | 6 |
| Total | 175 | 3,495 | 6 |

## Reading the seven-junction example

The root has three children introducing 3, 2 and 3 fresh distinctions. Joining the three pairs of children introduces 2, 3 and 2, respectively. For an explicit verification, the supports of the seven parity equations are as follows. The names in the calculation serve only to compare the actual operand sets under permutations.

| Junction | Distinctions |
| --- | --- |
| O | 0, 1, 2 |
| A | 0, 3, 4, 5 |
| B | 1, 6, 7 |
| C | 2, 8, 9, 10 |
| D on A and B | 3, 6, 11, 12 |
| H on A and C | 4, 8, 13, 14, 15 |
| F on B and C | 7, 9, 16, 17 |

D, H and F have a different common neighbor for each pair and none for all three. Reading the incidence rule on all loose distinctions gives exactly the twelve triples taking one from each of `{11,12}`, `{13,14,15}` and `{16,17}`. Between the first and last groups the bond distance is 6. From either of those groups to the middle group it is 8. Of the 816 triples of current distinctions, exactly these twelve have that sorted triple of distances. Independent exchanges within the three groups act transitively on those choices. This describes the full set of choices the observation permits.

For a homogeneous parity system the dual support masks are exactly the sums modulo two of the junction equations. A set of coordinates has a constrained projection precisely when it contains a nonzero dual support. A minimal one therefore gives a bond. Taking the smallest such support through each pair gives the stated scalar distance. The independent calculation enumerated all 262,144 assignments on the target, obtained its 2,048 allowed rows, recovered all even masks by a Walsh transform and checked projections and single-coordinate erasures for every minimal support. There are 69 bonds. The counts of the 153 pair distances at values 2 through 8 respectively are 6, 28, 32, 24, 34, 11 and 18. No other member of the width census has even this full histogram. Comparing all coordinate bijections compatible with the matrix yields 48 isometries. Every one carries the exact named menu, junction supports and allowed rows to themselves. Negative controls include a false histogram match in a coarser observation, an invalid exchange and a fully renamed reference. [Enumeration and maps](width.json) · [Independent projections](reference.json) · [Triple rule](check_triples.py)

The prespecified control pooling values above five gives the same verdict. As a further exploratory check, pooling values above four still gives only the target and its 48 maps. A reader at that cutoff can find three sets of mutually exchangeable distinctions, of sizes 2, 3 and 2. Taking one from each gives the triples. All nine loose bits, the 17 legal pairs and the twelve triples are given by the short decoder. At cutoff three the simultaneous exchanges `(0 6)(2 7)(4 11)(5 12)(8 16)(10 17)` preserve every observed pair yet take the legal triple `{12,13,17}` to the illegal `{5,10,13}`. Four is therefore the least uniform cutoff that suffices for this target. [Decoder and control](triples.json)

## Checking every width-eighteen table

For each scalar matrix, put two distinctions in the same class if their transposition preserves all entries. This is an equivalence relation since the table-preserving permutations form a group. Distances inside a class are constant, as are the entries between any two classes. Color the smaller matrix by each class size and internal distance. Every isometry induces a color-preserving isometry of this smaller matrix. Conversely each such map lifts by arbitrary bijections between corresponding classes. Representatives of all maps on the smaller matrix together with transpositions generating all within-class permutations therefore suffice to test setwise invariance of the legal menu. The checker uses only necessary invariants for rejection and exact backtracking for residual comparisons. It compares sets on the actual distinctions and grades each operand count separately. A four-distinction control checks its group calculation against direct permutation enumeration.

There are 3,495 distinct full matrix classes and 3,495 after pooling values above five. Thus the observed failures at full precision are internal symmetries. Six eight-junction incidence types admit a full-table symmetry that moves a legal single choice outside the menu. Four of those six also lose a two-parent choice. The three-parent choices are preserved in every class at this width. The scope is finite and counts incidence types once, independent of how many histories realize them. [All-class checker](check_classes.py) · [All-class counts and examples](classes.json)

## Two histories with identical states and different ninth joins

Here is an explicit obstruction independent of the census size. Use the seed and three single-parent joins, each with two fresh distinctions. Then join the three pairs of children, again with two fresh distinctions each. In one naming the first seven equations have the following supports.

| Junction | Distinctions |
| --- | --- |
| 0 | 0, 1, 2 |
| 1 | 0, 3, 5 |
| 2 | 1, 4, 7 |
| 3 | 2, 6, 8 |
| 4 | 3, 4, 9, 12 |
| 5 | 5, 6, 10, 13 |
| 6 | 7, 8, 11, 14 |

This common prefix has fifteen distinctions. Junctions 4, 5 and 6 may join. Their loose pairs are `{9,12}`, `{10,13}` and `{11,14}`. One legal eighth junction takes 9, 10 and 11 and creates 15, 16 and 17. Another takes 12, 13 and 14 and creates the very same three fresh distinctions. Both resulting arrangements have width eighteen.

Adding the seven old parity equations modulo two cancels every distinction used twice and leaves exactly `{9,10,11,12,13,14}`. This is precisely the difference modulo two of the two proposed eighth equations. Therefore adjoining either equation gives **the same set of 1,024 allowed rows on the same named distinctions**. Every bond and its scalar distances agree point for point. After the first eighth join, 12 is loose and 9 is shared. After the other, 9 is loose and 12 is shared. The next singleton `{12}` and pair `{12,13}` are legal in the first arrangement and illegal in the second. This rules out a reader for the complete next menu across all finite histories, even if it can see all allowed rows and knows the sequence of fresh counts. The two arrangements are isomorphic under exchanging the members of all three old pairs. The failure concerns which of the current distinctions can be used.

A smaller witness in the first presentation swaps only 9 and 12. That transposition leaves all 153 exact scalar entries fixed and changes the same single and pair choices. It takes 512 of the allowed rows outside the parity relation. The simultaneous exchange of all three pairs gives the stronger identical-states witness above. No three-parent join is available after either of these eighth joins. [Literal witness check](check_witness.py) · [Witness data](witness.json)

The primary comparison and separate width-wide check were recorded before enumeration. The extra cutoff-four and cutoff-three results are exploratory. The positive comparison has separate forward and reverse implementations within the same task. The exact counterexample also has the parity identity above and a separate replay from the literal rows. [Preregistered scope](../../../research/VARIABLE-OUTPUT-READER-20261118-001A/preregistration.md)
