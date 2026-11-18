# Identical mixed states with different next joins

## Standard statement

Fix the finite betweenness attachment and the parity growth rule in the [eight-distinction construction](../../CUBIC-FROM-A-KNOT-20261117-001/CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/cube_interface.md). There are two reachable presentations on the same 36 binary distinctions with exactly the same allowed assignments. One admits a full next round under the existing simultaneous policy. The other lacks enough loose distinctions for two of its required parents. Therefore even the complete binary relation fails to determine whether the next round is available. Its table of scalar bond distances also fails. The eight original distinctions occupy exactly the same places in both presentations.

## Nearest known result

The [pure parity theorem](../../BOND-NEXT-JOIN-20261117-001/BOND-NEXT-JOIN-20261117-001-P001_distance_reader/proof.md) reconstructs every legal next join from bond distances up to five on every finite pure parity history. Its proof assumes that all solutions of the designated parity equations occur. Here the original eight-place betweenness condition restricts those solutions. The [design and prior-work searches](../../../research/MIXED-NEXT-JOIN-20261117-001/preregistration.md) give the scope. The argument uses the two accepted constructions and elementary arithmetic modulo two. External novelty is unassessed.

## The starting system and the observable

For checking the construction, use the classical coordinates of the two-by-two-by-two cube. Name its eight ordinary junctions as follows.

| Name | O | X | Y | Z | P | Q | R | T |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Coordinate | 000 | 100 | 010 | 001 | 110 | 101 | 011 | 111 |

Each junction v has three outgoing distinctions x_v, y_v and k_v. Each occurs at the junction one step farther in its direction if that junction is present. The last direction is z. Each junction requires an even sum of its outgoing and incoming distinctions. The original eight distinctions are the actual outgoing k_v. On them the allowed tuples are exactly the two constants and each of the three coordinates or its complement. Call these eight tuples S. All later presentations keep S as a conjunct. Given a tuple in S, choose all eight y-values arbitrarily, then solve each junction for its outgoing x-value in order of increasing first coordinate. This gives 256 complete assignments per old tuple, hence 2,048 assignments on the 24 present distinctions. It also proves every old tuple survives.

The source growth rule permits one loose distinction from each of one, two or three distinct parent junctions. *Loose* means occurring in exactly one designated parity junction, even if the bit also occurs in an old betweenness. Each pair of parents must already have an ordinary common neighbor. A group of three is allowed only if no ordinary neighbor is common to all three. The new parity equation joins the selected distinctions to three fresh ones. It gives four extensions of every old state. The simultaneous policy requires all qualifying triples, every qualifying pair outside those triples, and a singleton for each remaining loose distinction. Each participating parent must supply a separate loose distinction to each required group. Both policies read the present junctions. Names and coordinates above serve only to verify which choices the rules allow.

For a pair of observed distinctions the scalar bond distance is the least size minus one of a support containing them whose projected relation passes K1–K3, with infinity if there is none. The tests are on the projected allowed states. Equal complete relations have identical projections on *every* support. Thus their entire distance tables coincide under the same identification, including infinite entries. Likewise any permutation preserving a complete relation preserves its table, without any change to bit values. This implication holds for nonlinear relations.

## A failure already at 24 distinctions

Write v=(i,j,z). At each junction with z=1 the sum of the incident x- and y-distinctions equals k_(i,j,0) ⊕ k_(i,j,1). For a fixed old tuple this quantity is the same at every i,j. It is one on the two z-cuts and zero on the six remaining tuples. Therefore interchanging i with j and x with y on the upper horizontal distinctions preserves every parity equation there as a system. The permutation fixes every lower distinction and every k_v, so it preserves the full mixed relation. More explicitly, its four transpositions are (x_Z,y_Z), (x_Q,y_R), (y_Q,x_R), (x_T,y_T). It preserves the entire set of loose distinctions too.

The pair k_Q,x_Q belongs to one junction Q, so those two bits cannot be selected together. Its image k_Q,y_R has parents Q,R with common neighbors Z and T. Both bits are loose, so the image is a permitted next pair. Every state-based reader receives the same input after the permutation. Even identifying the eight originals and all loose distinctions leaves this symmetry. A direct scan of the projected 2,048 states gives scalar bond distance four for each of these pairs, with seven shortest five-place supports for each. The canonical knot test accepts one shortest projection for each pair and rejects its free four-place restriction. This argument concerns exact serial choices on the observed bits. The whole simultaneous round is unavailable at this initial snapshot.

## Two reachable presentations on 27 distinctions

Call the upper marked distinctions a=k_Z, b=k_Q, c=k_R and d=k_T. In each old tuple there are either zero, two or four ones among them. Thus

    a ⊕ d = b ⊕ c

on every joint state. Name three fresh bits u, v, w. In presentation A make a new junction J using a,d. In presentation B use b,c. Each selected pair has distinct parents with a common ordinary neighbor. These four old bits are loose at this snapshot. Each new junction therefore obeys the very same serial law.

The new parity equation is u ⊕ v ⊕ w = a ⊕ d in A, and u ⊕ v ⊕ w = b ⊕ c in B. They impose the same condition at each old row, so the extensions coincide **as sets of assignments on the same 27 bits**. There are 8,192 assignments. In the pure parity control, a tuple with just a=1 among the eight marked bits has 256 completions. Its two input sums disagree, and the original restriction S excludes this tuple. Each of the two five-place local relations has the full even-parity projection because its two old inputs jointly take all four possible values. The distinguished incidence differs. J is the only junction sharing distinctions with just two ordinary neighbors. Its neighbors in A have total arities four and six, and those in B both have arity five. No renaming of the full presentations identifies them.

In B one can now make a singleton attachment using a. In A that distinction is shared. Even allowing a different legal group to supply the same output relation cannot reproduce this attachment on the same old bits. To see this, take an A-state whose old tuple is the first coordinate i. Flip the six shared distinctions along the closed sequence of junctions O–X–P–T–J–Z–O. They are x_O, y_X, k_P, k_T, k_Z and k_O. Each affected junction sees two flips. On the old eight this switches exactly the positions i=j and takes the tuple i to 1⊕j, another permitted original tuple. This yields two A-states agreeing on every loose distinction and differing at a. Any legal A-join uses only loose distinctions, so it prescribes the same parity for its three fresh outputs on both states. B's singleton through a prescribes opposite parities. This is a difference in possible next relations on the same observed distinctions. Exact enumeration gives both presentations 13 one-parent and 35 two-parent choices. Only B permits a three-parent choice, with three in total. The 48 and 51 choices respectively give that many distinct fresh-parity functions on the fixed old states. These counts precede any quotient by automorphisms.

## Two identical state sets, one feasible full round

Start with A and B above. Append exactly the same three parity junctions, using identical fresh names on both sides.

1. Junction W uses x_X and y_Y. The two parents X,Y have common neighbors O and P.
2. Junction L uses the loose x_P.
3. Junction M uses the other loose distinction y_P.

Each step is legal in each presentation. These are identical new equations on identical complete relations, so the two presentations still have the same full states and the same original eight-place marginal. There are 12 junctions and 36 distinctions. Four serial additions since the initial attachment give 2,048 × 4⁴ = **524,288 allowed states** on each side. The equality holds row by row.

Here is the simultaneous rule evaluated afresh. A juxtaposition such as QRW means a group with those three parents. The table includes all required groups of size at least two. Junctions in opposite parts of the ordinary bipartition cannot share a neighbor, so the groups can be checked within each listed part.

| Presentation | Required groups in the part containing Q,R,W | Required groups in the other part | Loose distinctions and allocation |
| --- | --- | --- | --- |
| A, after joining Z,T | QRW, QJ, RJ | TL, TM, LM | Q and R can each supply two, T two, J three, W three, L and M three apiece. After meeting every obligation, five singleton groups use the remainder. |
| B, after joining Q,R | QRW | ZT, ZJ, TJ, TL, TM, LM | Z has one loose distinction for two required pairs. T has three for four required pairs. |

For completeness, the original ordinary neighbor pairs are OX, OY, OZ, XP, XQ, YP, YR, ZQ, ZR, PT, QT, RT. Both histories add WX,WY,LP,MP. The executable record denotes J,L,M by U,A,B respectively. A adds JZ,JT, while B adds JQ,JR. In both, QRW has pairwise common neighbors and no one neighbor common to all three. In A, Q,R,J all have Z or T in common, and T,L,M have P in common. In B, Z,T,J have Q or R in common, and T,L,M have P in common. These latter triples are excluded by the same rule. The lists exhaust the live parents from the displayed incidences. In A one can allocate each required group and then run the five singletons, five pairs and one triple. B has no such allocation.

A further common singleton using an outgoing distinction of W gives equal relations on 39 distinctions with 2,097,152 allowed states. A then has seven singleton, five pair and one triple joins in its full round. B again has too few loose distinctions at Z and T. The checker compares every extension of every previous row.

Whether *any* full round can run is invariant under renaming. Consequently these different outcomes persist even when the next joins are considered only up to renaming, when the old eight are disclosed, or when one supplies the entire current truth table. No observer need pick a point of comparison in either presentation.

## Scope and checks

This is a constructive counterexample on finite, legally reachable mixed presentations. The prescribed growth law still has access to its designated junctions. The stronger universal reading under test would recover its next choices from the distances or states alone. The construction refutes that reading for this law. The original three-dimensional growth theorem concerns a chosen continuation that fills to the aligned stage I₄ and then follows complete rounds. The predecessor guarantees feasibility along that sequence. Recovery of the exact next joins on its anonymous distinctions remains open. Both counterexample histories leave the prescribed alignment when a single junction consumes two of its upper marked outputs.

The [state check](check_witness.py), [direct scalar and knot tests](check_distances.py), and [round check](round_probe.py) exercise the concrete witnesses. The [validation record](result.json) identifies the scope, check outputs, controls, and level of independence. All arguments and checks here were made within this task.
