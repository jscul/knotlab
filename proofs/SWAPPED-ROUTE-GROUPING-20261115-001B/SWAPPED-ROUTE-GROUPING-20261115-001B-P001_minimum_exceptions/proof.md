# Minimum exceptions across all permitted branch orders

Status: Proved

## Standard statement

At each of \(r\) ordered stages, each of two branches contributes its middle, incoming pad and outgoing pad in that order. The two whole branches may be exchanged independently at every stage. Within each of the two roles, a name occurs at most twice. Middle and pad names belong to disjoint sets. A twice-used name retained in an order joins its two physical occurrences. Two retained names alternate if their four positions read \(a,b,a,b\) or \(b,a,b,a\). A reading is nested when no two retained names alternate, which includes disjoint pairs.

There is a deterministic algorithm returning a legal order and a smallest set of repeated names to omit so the rest are nested. It uses \(O((r+1)^2)\) indexed-word operations and working words, including the search for the order. A single-use name never needs to be omitted. The empty layout returns two empty tuples.

## Nearest known result

The predecessor tests one specified order and can search for its smallest exception set by branching on an alternating pair. For a fixed order, retaining the most pairs is also the classical maximum independent set problem on a supplied circle graph, with the paired endpoints giving its chord representation. Valiente's algorithm uses time proportional to the total chord length and linear working space. The present calculation optimizes the omissions and the independent stage exchanges together. [Fixed-order predecessor](../../TWO-RELAY-PADDING-20261115-001D/TWO-RELAY-PADDING-20261115-001D-P001_nested_pair_grouping/proof.md) · [Valiente, maximum-weight independent sets in a supplied chord representation](https://doi.org/10.1007/978-3-540-24587-2_15)

Maximum nonalternating matching by interval decomposition is classical. Nussinov, Pieczenik, Griggs and Kleitman handle a supplied letter sequence with many potential partners by cubic-time dynamic programming. Zhang et al. describe optimizing nested pairings over alternative paths in a finite automaton. Our worst-case quadratic bound follows from this layout's two outgoing choices and the two possible copies of a **specified physical partner**. The argument below derives the bound directly. [Nussinov et al., Algorithms for Loop Matchings](https://doi.org/10.1137/0135006) · [Zhang et al., Methods on finite-automaton parsing](https://doi.org/10.1038/s41586-023-06127-z)

## A path represents a sequence of whole-branch choices

Use boundary vertices \(B_0,\ldots,B_r\). From \(B_i\) to \(B_{i+1}\) put two directed paths of six arcs each, with disjoint interiors. The first spells the physical positions of the stage in supplied branch order. The second spells the other branch first. Every arc has both its physical-position ID and its typed name. Each physical position has two arc copies, exactly one of which a complete path traverses. A middle with input ID \(j\) has typed ID \(2j\), and a pad has typed ID \(2j+1\), matching the predecessor. If a name occurs at positions \(p,q\), record \(q\) as the physical partner of \(p\) and conversely. Single-use positions have no partner.

There are \(11r+1\) vertices and \(12r\) arcs. Complete paths from \(B_0\) to \(B_r\) correspond bijectively to the legal orders. Any path between two vertices can be extended to a complete path, since every vertex can be reached from the first boundary and can reach the last, and topological order prevents revisits. In particular, no such path visits both arc copies of one physical position.

## The interval calculation

Let \(D(u,v)\) be the maximum number of complete nonalternating name pairs on one directed path from \(u\) to \(v\). Only a pair with both physical positions on that path can count. Put \(D(u,u)=0\). Use \(-\infty\) when \(v\) cannot be reached from \(u\). For \(u\ne v\) consider each outgoing arc \(e\) of \(u\). Write \(e^+\) for its end. Try the following terms, discarding any that require an unreachable interval.

1. Skip \(e\)'s position in the matching and take \(D(e^+,v)\).
2. If \(e\)'s position has a physical partner, take either copy \(f\) of that other position. For its start \(f^-\) and end \(f^+\), the score is
   \[
   1+D(e^+,f^-)+D(f^+,v).
   \]

Take the maximum, with the maximum of an empty set equal to \(-\infty\). Skipping an arc still traverses it. In particular, two different private vertices on opposite branches of a stage cannot be treated as the endpoints of an empty path.

To prove the recurrence, fix an optimal path and its selected pairs. If the first arc is unpaired in this selection, skipping it retains every selected pair in the suffix. Otherwise its partner is one of the two candidate arcs \(f\) further along the same path. A pair with one position strictly between \(e,f\) and one after \(f\) would alternate with them. Every other selected pair therefore lies wholly inside or wholly after them, giving the bound in the second term.

Conversely, take paths attaining the two finite interval scores and concatenate \(e\), the inside path, \(f\), and the suffix path. The endpoints agree at the actual vertices, so this is one permitted path even when a split falls inside a stage. Every inside pair lies under the chosen pair, and every suffix pair is disjoint from it. The two interval selections cannot score the same typed name. Each scored name uses both its physical positions, and a permitted path visits each physical position at most once. Adding the selected pair thus attains the displayed sum. The skip case concatenates just \(e\) and its suffix. These two directions prove the formula, including feasibility.

Fill the rows in reverse topological order of \(u\). The skip row starts at \(e^+>u\). A finite inside term requires \(f^-\) to be reachable from \(e^+\), including equality. Therefore \(f^+>u\), and the suffix row is already available. At most two \(e\)'s and two partner copies for each \(e\) are tried per vertex pair. The table has \(O((r+1)^2)\) cells. Each score fits in one indexed word, and a constant-size choice remembers the winning term. The input uses the predecessor's indexed domains, so the physical partner lookup and typed output scan take \(O(r+1)\) work.

Let \(P\) be the set of twice-used names. The exact optimum is
\[
|P|-D(B_0,B_r).
\]
Trace the choices from the full interval. Mark each traversed arc's orientation, record the name of each selected pair, and return the names in \(P\) not recorded. The trace partitions the chosen path into smaller intervals and writes each of its \(6r\) physical occurrences once. This takes linear additional work. The solver returns the ascending typed IDs of omitted names and one 0/1 entry per stage, with 1 exchanging its two intact branches. Multiple optima may exist. [Standalone implementation](solver.py)

## Controls and numerical checks

- For one stage take middles \((0,0)\) and pads \((0,1,0,1)\). Both legal readings spell \(A,B,C,A,B,C\) in typed names. Any two pairs alternate, so exactly one pair can be retained. Number the supplied path's internal vertices \(1,\ldots,5\) and the swapped path's \(6,\ldots,10\), sharing endpoints 0 and 11. After skipping \(A\) and taking the first path's \(B\), its end is 2. The other position of \(B\) has a copy \(6\to7\), and \(7\to11\) contains a complete pair \(C\). Treating the impossible \(2\to6\) as empty falsely retains both \(B\) and \(C\). The checker compares all 529 ordered vertex pairs in a two-stage layout against complete path enumeration, including 303 unreachable pairs and the incompatible copies of all twelve physical positions.
- For middles \((0,1)\) and pads \((1,0,2,3)\), all six typed names occur just once. Erasing the roles yields the word \(0,1,0,1,2,3\) or its three-position rotation, falsely requiring one exception. Inputs containing a third occurrence of the same typed name are rejected.
- Up to renaming within a role, two stages admit 10 middle partitions times 764 pad partitions, since the four middle and eight pad positions may be single or paired. For each of the 7,640 layouts the independent checker enumerates all four literal branch orders and deletion subsets. The counts at minimum \(0,1,2,3,4\) are respectively **2,071, 3,758, 1,614, 194 and 3**. In 3,174 layouts optimizing the order strictly improves on the supplied order. For example, middles \((0,0,2,2)\) and pads \((0,1,0,1,4,5,4,5)\) give two disjoint copies of the first one-stage control. Every order costs four exceptions. The returned order \((0,0)\) with omitted IDs \((0,1,4,9)\) is a direct witness.
- The checker also exhausts orders and deletion sets on 41 selected larger layouts through six stages. A 36-stage example requires exchanging exactly one stage in each of eighteen independently repairable pairs to reach zero exceptions. On 30 stages with the upper middles \(A_1,\ldots,A_{15},A_1,\ldots,A_{15}\), every two of those names alternate under all orders, giving exactly fourteen exceptions. All remaining middles and pads are fresh.

The theorem is a uniform upper bound for finding the optimal grouping on the supplied layout. The numerical replay is V1. Its independent exhaustive oracle uses explicit orders, alternation inequalities and deletion subsets, and the resulting witnesses also pass the predecessor's stack check. A separate AI investigator in the task reviewed the distinction between physical positions, alternative path copies and typed name roles. The exception count measures this particular grouping criterion. SAT decision and total work for unrestricted decision algorithms require their own arguments. [Checker](check.py) · [Retained results](checks.json)
