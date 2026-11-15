# A linear decision algorithm for nested pairs of middle and padding names

Status: Proved

## Standard statement

In each of $r$ stages, read the six supplied name positions in this order

$$
 A_i,\quad p_{A_i,\rm in},\quad p_{A_i,\rm out},\quad
 B_i,\quad p_{B_i,\rm in},\quad p_{B_i,\rm out}.
$$

The two branches use the positive implications $x_{i-1}\to M\to x_i$, where $M=A_i,B_i$. The boundary variables are distinct. Middle and implication-pad names come from disjoint indexed lists. Each name occurs in at most two of the displayed positions, including positions in the same stage. The two signs of one padded implication occupy a single pad position here. The endpoint pads, per-slot witnesses, and public guards are fresh as in the predecessor.

Suppose no two equal-name pairs have positions $a<b<c<d$ with one name at $a,c$ and another at $b,d$. This condition applies to the union of the middle and pad pairs. For every supplied assignment of all raw guards, ordinary existential SAT and a satisfying assignment on the boundaries, middles and pads can be found in $O(r+1)$ indexed operations and words. The nesting depth can grow linearly with $r$.

More generally, let $k$ be the minimum number of twice-occurring names whose removal from the pairing leaves this condition true. Decision and the same assignment construction take $O(2^k(r+1))$ indexed operations, including finding the names.

## Nearest known result

Alur and Madhusudan give the general finite-state reading model for a word supplied with a properly nested matching. The interval composition below specializes that principle. The contribution here is the precise six-position verifier for guarded implications, the joint condition on the two kinds of names, and its application to this fixed SAT input. The proof uses only the Boolean semantics and the supplied matching. [Alur and Madhusudan, *Adding Nesting Structure to Words*](https://www.cis.upenn.edu/~alur/Jacm09.pdf) · [Guard and padding semantics in the predecessor](../../ONE-RELAY-PADDING-20261115-001B/ONE-RELAY-PADDING-20261115-001B-P001_one_middle_cut/proof.md)

## The state at a position inside a stage

A slot on literals $L_1,L_2,L_3$ has the witness clause $w_1\lor w_2\lor w_3$ and clauses $\neg e_j\lor\neg w_j\lor L_j$. For fixed literals and public switches $e$, the slot enforces its disjunction exactly when all three switches are on. In the remaining cases choose a witness for any off switch. An implication $D$ has two slots $D\lor p$ and $D\lor\neg p$. At pad value $v$, only the slot whose pad literal is false can enforce $D$. This gives two activation bits for each implication, one applicable at $v=0$ and one at $v=1$.

An endpoint unit has four padded slots, one per sign choice on two private pads. The unit is enforced exactly when all four slots are active. If the endpoint literal is false and a slot is inactive, the pad values falsifying that slot satisfy all the others. Thus the initial boundary may be either value unless the positive unit forces $x_0=1$. The final boundary may be either value unless the negative unit forces $x_r=0$. This also treats a length-zero schedule with both units on the same boundary.

Use eight states $(x,y,m)\in\{0,1\}^3$. The known position in the schedule supplies the phase. Between stages the canonical state for boundary $x$ is $(x,0,0)$. For candidate input bit $v$, the transition at position $j$ is a relation $R_j(v)$ on the eight states.

| Position | Action for value $v$ |
| --- | --- |
| Upper middle | From the canonical state for $x$, choose the new boundary $y$ and enter $(x,y,v)$. |
| Upper incoming pad | Keep the state if the implication is inactive at $v$ or $x\le m$. |
| Upper outgoing pad | Keep the state if the implication is inactive at $v$ or $m\le y$. |
| Lower middle | Replace $m$ by $v$, keeping $x,y$. |
| Lower incoming pad | Keep the state if the implication is inactive at $v$ or $x\le m$. |
| Lower outgoing pad | If the implication is inactive at $v$ or $m\le y$, enter the canonical state for $y$. |

For a fixed consistent choice of all name values, a run from an allowed initial state to an allowed final state is exactly a satisfying boundary assignment. Both branches compare against the same guessed $y$. Keeping $x,y,m$ across an interval endpoint matters when that endpoint splits a stage. Giving the two branches independent guesses for $y$, or forgetting $m$ between its incoming and outgoing pads, would describe different formulas.

## Evaluating the nested pairs

For a consecutive piece containing no occurrence paired outside that piece, store the relation between its entry and exit states achievable by assigning its names. Write $UV$ for relational composition in reading order. Construct pieces by the following rules.

* The empty piece gives the identity relation.
* A singleton occurrence at $j$ gives $R_j(0)\cup R_j(1)$.
* Adjoining two pieces with relations $U,V$ gives $UV$.
* Enclosing a piece with relation $I$ by the two occurrences $a,b$ of one name gives

$$
 R_a(0) I R_b(0)\;\cup\; R_a(1) I R_b(1).
$$

The rules are exact by induction. In a concatenation, the two pieces have disjoint names and can choose their assignments independently once the intermediate verifier state is fixed. In an enclosing pair the only joint choice is its common value. Every promised word has this decomposition. Its first position is either a singleton, or its mate divides what follows into a completely enclosed piece and a disjoint remainder. Intersect the resulting relation with the allowed endpoint states to decide SAT.

With indexed names one scan pairs the occurrences and rejects a third occurrence. A stack checks the supplied order and evaluates the decomposition. When a pair opens, save the current prefix relation and start the interior with the identity. When it closes, apply the enclosing-pair rule and adjoin the result to the saved prefix. There are $6r$ positions and a constant number of operations on $8\times8$ Boolean relations per position. Keeping one construction record per operation also permits iterative backward reconstruction. At a composition choose a witnessing intermediate state. At a pair choose its common bit and two intermediate states. The reconstructed run gives every boundary and every occurrence value. The endpoint construction above supplies any needed private pads, and choosing an off switch or a true literal in each slot supplies all private witnesses in another linear scan.

The bound assumes supplied mate indices or names in an indexed universe of size $O(r+1)$. It counts the raw guards, whose number is $24+24r$. Bit-level parsing or interning externally supplied arbitrary strings has its own input cost. The stack can grow with the number of open pairs. This is a linear-work algorithm with indexed storage.

## Conditioning on a few exceptional names

Draw a conflict between any two names whose occurrences alternate in the joint order. Deleting names removes exactly their incident conflicts. For a proposed deletion set skip both occurrences of every deleted name in the stack check. At a failed close, let $a$ be its opening and $b$ the current top opening. The order is $a<b<\operatorname{mate}(a)<\operatorname{mate}(b)$. Any successful further deletion must include the name at $a$ or the one at $b$. Branch on these two possibilities, decreasing the budget each time. With budget $k$, there are fewer than $2^{k+1}$ stack checks of $O(r+1)$ work each. A successful leaf supplies a set $K$ of at most $k$ names. For unknown $k$, try budgets from zero upwards. The sum up to the first successful budget is geometric. This search does not require materializing the possibly quadratic list of conflicts.

Next enumerate the $2^{|K|}$ valuations of that one returned set. In each valuation retain the two positions of each named value in the word, restrict both transitions to its prescribed bit, and treat the positions as singletons for the stack. The other pairs are nested. Every satisfying assignment has one of the enumerated valuations, and restricting two occurrences to the same bit preserves the meaning of their name. Only one deletion set needs this valuation loop. The two work bounds therefore add.

For $t\ge1$, put $B_1,\ldots,B_t,A,B_t,\ldots,B_1,A$ in successive upper-middle slots and use fresh names elsewhere. There are $t$ conflicts and deleting $A$ suffices. At least one deletion is necessary. The word $A,B,C,A,B,C$ in those slots has three mutually alternating pairs and needs two deletions.

## Controls and validation

For a promised family with arbitrarily many open names, take $2d$ stages. Pair the upper middle and upper incoming pad in each of the first $d$ stages separately with the lower middle and upper incoming pad, respectively, of the corresponding stage in reverse order in the second half. Use fresh names elsewhere. Both pairs from one stage close in reverse order and the resulting depth at the midpoint is $2d$. Enforcing the two endpoints, the first upper incoming implication, and the final lower outgoing implication gives a contradiction through their common middle. Disabling one of these implications allows a satisfying assignment.

A one-stage control uses a common middle $J$ at positions 1 and 4 and a common incoming pad $p$ at positions 2 and 5, numbered from one. Each role separately satisfies the nesting promise. Jointly the occurrences alternate. With both endpoints on, select only the positive pad slot of the upper incoming implication, only the negative slot of the lower incoming implication, and both slots of the upper outgoing implication. The upper outgoing implication forces $J=0$, while one of the two incoming implications forces $J=1$ at either value of $p$. Splitting either repeated name restores SAT. On the same layout, disabling every implication gives SAT. A failed stack check reports an inapplicable promise and determines neither outcome on its own.

The checker compares the interval computation with PySAT applied to the predecessor's literal guarded clauses after the stated renaming. For every positive case it pins the returned boundaries, middle values and implication-pad values in the raw formula and verifies extension to all private variables. It covers all one-stage occurrence patterns with at most two uses, every two-stage half-slot mask on a fixed nested layout, mixed raw guards through nine stages, a 1,200-deep layout, and zero-, one-, and two-deletion controls. The formal result is the induction and complexity argument above. The checks are V1, separate algorithms within this task. External work provides mathematical background. [Checker](check.py) · [Replay results](checks.json)
