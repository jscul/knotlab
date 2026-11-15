# What three and four open Boolean choices reveal about shared signs

Status: Proved

## Standard statement

In the unpinned prefix below, the only constrained projections on at most three named bits are exactly the displayed clause scopes. Each allows seven of eight states and passes K1–K3. This holds for every finite roster of slots with fresh private bits and arbitrary signs, including repeated slots on the same three original variables.

Two occurrences of the same original variable in different slots reveal their *relative* sign on four private bits alone. The four-bit projection is free if their signs agree. It excludes exactly 1111 if they disagree. Hence three bits reveal the unsigned ternary meeting pattern, and four suffice for relative sign comparisons even after the public variable is forgotten. If the complete truth tables with their Boolean values and public variable names are provided, each displayed gate already reveals its own sign at three.

## Nearest known result

The foundation proved the K1–K3 and majority facts used here under erasure as forgetting. The Intuitions guide uses a signed incidence for an occurrence that reads the opposite of the named bit. The four-negative-literal consequence below is a single classical resolution step on the shared public variable. The additional result here is the extension theorem for **every** scope of at most three bits in this whole prefix, and the exact four-bit projection under shared occurrences. [Foundation proof](../../KNOT-FOUNDATION-20261019-001E/KNOT-FOUNDATION-20261019-001E-P001_forgetting_reading/proof.md) · [Signed-incidence convention](../../../publication/knotlab/INTUITIONS.md) · [Davis and Putnam, 1960](https://doi.org/10.1145/321033.321034)

## The unpinned relation

A slot $s$ lists three distinct original Boolean variables. At place $i$ let $L_{si}$ be the selected variable or its negation. Give that occurrence its own switch $e_{si}$ and choice $w_{si}$. All these private bits are distinct from the public variables and from every other private bit. The prefix is the conjunction, for each slot, of

$$
(w_{s1}\lor w_{s2}\lor w_{s3}),\qquad
(\neg e_{si}\lor\neg w_{si}\lor L_{si})\quad(i=1,2,3).
$$

A projection onto named bits lists the partial assignments to those bits that some joint state of the whole prefix extends. All original and private bits are initially open. A pin below tests extension of a candidate partial assignment. Every assignment of all public variables already extends by setting every switch to zero and choosing one $w$ per slot.

## Extension of every permitted three-pin assignment

Take any consistent partial assignment on at most three distinct bits. If it falsifies all literals of a displayed clause, it has no extension. Suppose it does not. Set every unpinned switch to zero.

1. **Meet demands that are already active.** A pinned $e=w=1$ forces its signed literal true. Each such occurrence consumes two distinct private pins, so there is at most one. Honor that demand in choosing the public value. A prior public pin against it would have falsified its displayed gate. Choose the other public values consistently with their pins.
2. **Fill slots that have an available choice.** A slot with a pinned $w=1$ already satisfies its first clause. Otherwise, if some $w$ is unpinned and its switch was not pinned to one, turn that $w$ on. Its switch is zero, including when it was explicitly pinned to zero. This satisfies the slot independently of its signs. Other unpinned $w$ bits may be zero.
3. **The only remaining kind of slot uses the entire pin budget.** Suppose a slot has no pinned $w=1$ and no available choice from step 2. At each of its three places, $w$ must be pinned zero or $e$ must be pinned one. Three different private pins are required. There are therefore exactly three, one at each place of this single slot. No public value is pinned, there is no previously forced demand, and no other slot has a pin. If all three pins were $w=0$, the displayed first clause was falsified. Otherwise choose a place with $e$ pinned one. Its $w$ is free. Choose the corresponding public value to make its literal true and turn on that $w$. Leave every other free $w$ in the slot zero. Every other slot has its switches zero, so this public choice extends there as well.

Thus the only failures with at most three pins are the single falsifying tuples of the displayed clauses. Every displayed scope is distinct because the private names are fresh. Its seven remaining tuples all extend. All other named triples allow every tuple, as do all pairs and single bits. This statement concerns prefix projections before any completion conditions on the switches are imposed.

## A shared-variable comparison on four private bits

Choose occurrences $i,j$ of one public bit $x$ in different slots, and forget every bit except $(e_i,w_i,e_j,w_j)$. When both switches and both choices are one, the two literals must hold at the same public value. Aligned signs allow it and opposed signs forbid it. For any other assignment to those four bits, at most one of the occurrences demands a value. Choose $x$ accordingly. In each of the two slots there are two other unpinned occurrences. If its pinned $w$ is zero, turn on one of those other choices with its switch zero. Set all other unpinned switches zero and fill every other slot in the same way. This also proves extension of 1111 in the aligned case. For occurrences of different original bits, both values can be chosen independently and the quartet allows all 16 states.

The opposed consequence is

$$
\neg e_i\lor\neg w_i\lor\neg e_j\lor\neg w_j.
$$

The four private bits contain no displayed clause scope. Every subset of three or fewer is free by the extension theorem. Thus the 15-state relation passes K1–K3 and is an additional constrained scope, whereas the aligned 16-state relation fails K1. This proves the exact first arity at which the **list of constrained scopes without their labelled tuples** can distinguish same incidence with opposed versus aligned signs. It does not purport to classify every four-bit projection.

If the incidence and local roles are known, choose an anchor occurrence for each public variable with at least one occurrence. One such quartet per remaining occurrence tells whether to keep or reverse the anchor's sign. For $r_x$ occurrences of $x$, this uses $r_x-1$ Boolean comparisons. Reading all variables needs $\sum_{x:r_x>0}(r_x-1)$ comparisons, linear in the occurrence count. Complementing a public variable and reversing all its occurrences preserves those answers, giving exactly the per-variable sign ambiguity. A free quartet on its own also occurs for unrelated public variables, so incidence identity is part of the input to this reconstruction.

There is a different observation if labelled ternary tables are supplied. In the named order $(e,w,x)$, a positive gate excludes 110 and a negative gate excludes 111. This gives the absolute sign immediately with the public Boolean labels fixed. The unsigned scope list and its seven-state counts omit precisely this information.

## Knot test and the 2-CNF obstruction

A proper relation on at least three bits that excludes only one tuple binds all the named bits, allows a state, and becomes unrestricted on forgetting any one bit. These are K1, K3 and K2, respectively. The displayed seven-state relations and opposed 15-state quartet meet these conditions in the projection of the whole prefix. A full projection fails binding. An implication cycle, a shared name or a syntactic clause-width check would not decide these projection statements.

For any of these single-hole relations, flip one of three different coordinates of the excluded tuple in each of three copies. The three resulting tuples are allowed and their coordinatewise majority is the excluded tuple. Every 2-CNF relation is majority-closed. If the majority of three satisfying assignments falsified a binary clause, at least two of the assignments would falsify each literal, so at least one assignment would falsify both. Unit clauses are preserved as well. Existential witnesses do not change the conclusion, since the majority of three full extensions extends the majority of the three visible tuples. Thus no 2-CNF with existential witnesses defines any of these single-hole projected relations.

These are **relational** knot verdicts on allowed states. The formal loop and contact argument names passed to knotlab specify the roles tested. The static prefix supplies no recurrence law and no two independently witnessed native recurrences. Atomic or composed native topology, contact-distance and SAT solver lower bounds receive no promotion from this proof. [Canonical knot test and native-loop qualification](../../../docs/FOUNDATIONAL_THESIS.md)

## Finite checks

For each small roster, a complete Boolean truth table of the joint CNF was built separately for every signing. Every assignment on every scope of size zero through three was compared with the extension theorem. All private quartets across two slots were also tested. The quartets on different public variables were always free.

| Original public triples per slot | Named bits | Signings | Constrained triple projections | Free triple projections | Opposed, aligned and different-public quartets |
| --- | ---: | ---: | ---: | ---: | --- |
| $(0,1,2)$ | 9 | 8 | 32 | 640 | No two-slot quartet |
| $(0,1,2),(0,1,2)$ | 15 | 64 | 512 | 28,608 | 96, 96, 384 |
| $(0,1,2),(0,2,3)$ | 16 | 64 | 512 | 35,328 | 64, 64, 448 |

An additional 51-bit prefix uses the same original triple in eight slots, one per signing of that triple. A separate algorithm enumerates all eight public assignments and all 64 private states of each slot conditional on each public assignment. For each tested pin set it intersects the compatible public assignments across the slots. Private choices in different slots are independent once the public assignment is fixed, which makes this elimination exact. Among its 20,825 triples, 32 were constrained and 20,793 were free. Among the 252 occurrence-pair quartets, all 48 opposed quartets omitted only 1111, and the 36 aligned and 168 different-public quartets were free. Twenty-one anchor comparisons recovered the relative signs of the 24 occurrences. [Counts and knotlab verdicts](projections.json)

The checker separately submits the complete two-slot CNF to knotlab, with every other variable explicitly forgotten as an existential witness. It compares each entire projected truth table with direct enumeration. It tests the first clause, both gate signs, an undisplayed full triple, an opposed quartet and an aligned quartet. Deleting the opposed gate restores 1111. The local elimination method was also run against the full joint table on every small scope of one signing in each smaller roster. These checks give V1 validation within the task. The uniform conclusion follows from extension for arbitrary finite rosters.

Run the full certificate from the repository root:

~~~sh
python3 -B proofs/SIGNED-KNOT-OVERLAP-20261114-001A/SIGNED-KNOT-OVERLAP-20261114-001A-P001_three_and_four_choices/check.py
~~~

The opposed quartet can also be reproduced directly:

~~~sh
PYTHONPATH=tools python3 -B -m knotlab check \
  --cnf 'w0_0 w0_1 w0_2; ~e0_0 ~w0_0 x0; ~e0_1 ~w0_1 x1; ~e0_2 ~w0_2 x2; w1_0 w1_1 w1_2; ~e1_0 ~w1_0 ~x0; ~e1_1 ~w1_1 x1; ~e1_2 ~w1_2 x2' \
  --loops e0_0 w0_0 e1_0 --contact w1_0 \
  --witnesses x0 x1 x2 w0_1 w0_2 e0_1 e0_2 w1_1 w1_2 e1_1 e1_2 --json
~~~
