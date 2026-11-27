# What the finite two-holder lemmas prove

Every knot here requires both values among at least three distinct places. Each distinction has one holder or two different holders. A **part** retains just its selected knots. Its loose distinctions are those held once **in that part**. These assumptions permit repeated meetings, coincident supports and knots of different arities.

For these finite systems, forcing decides extension, arbitrary allowed states can be joined by single-distinction changes, and every pair of distinctions is free. In a connected part, a ring makes every pattern of its loose distinctions possible. A ring can still impose a relation when a shared distinction is also read.

## A ring with a joint restriction

Take the three knots $(q,p,x)$, $(p,r,y)$, $(r,q,z)$. Their loose distinctions $x,y,z$ take all eight words. On $(q,x,y,z)$ the missing words are exactly **0010 and 1101**. If $q=x=z=v$, the first and last knots require $p=r=1-v$, so the middle knot requires $y=v$. If either $x$ or $z$ differs from $q$, the corresponding outer knot leaves its shared value free, so $p,r$ can be chosen to differ. Each single knot deletion gives all 16 words. Forgetting any of the four distinctions gives all eight words on the others.

The canonical check uses the six original clauses and forgets $p,r$. It reports a knot of width four. Its output orders the variables $x,y,z,q$. The four values in this example are individually readable source distinctions. The example demonstrates exactly what is lost by insisting that every chosen distinction be loose. [Literal images and deletions](lemma_counts.json) · [Canonical check](lemma_ring_check.json)

## Gluing and the loose distinctions of a connected part

**G.** Write two knots sharing just $x$ as $(A,x)$ and $(x,B)$. A mixed word on either group leaves $x$ free there. If $A$ is all $v$, its knot demands $x=1-v$. The two demands conflict precisely when $A$ and $B$ are constant with opposite values. After forgetting $x$ the relation is therefore one not-all-equal law on the remaining places, with every value in $B$ reversed. For two three-place knots, 18 states project to 14 of 16 words.

**R for a tree of knots.** Choose any first holder, and mark each holder by the parity of the number of holder steps from it in the tree. Gluing along each shared distinction gives one not-all-equal relation on the loose distinctions, each value reversed exactly at the holders marked odd. To see the signs under repeated gluing, complement all the signed inputs to one relation whenever necessary so that the two occurrences of their common distinction have opposite signs. A constant signed word on each side then conflicts precisely when their signed values agree. This lets the two boundary lists be joined with their existing signs. On the tree, adjacent holders have opposite marks, so the rule applies at every join.

The two missing words prescribe the holder's mark at every loose place, or the opposite at every loose place. A tree of $h$ knots has at least $3h-2(h-1)=h+2$ loose distinctions. Deleting any one knot leaves tree parts, each with its own newly loose distinction to the deleted holder. All the other loose places of each part were already loose. With those old values fixed, at most one of the two complementary forbidden words matches them, and the newly loose value can avoid it. The parts can be completed separately. This proves that deleting any one of the tree's laws releases the entire original loose set.

**R for a ring, including a double meeting.** Keep enough shared distinctions to connect all the holders as a tree. Temporarily split each of the $r$ other shared distinctions into two loose copies, one at each of its holders. Here $r ≥ 1$. The tree calculation gives exactly two complementary forbidden words on the original loose distinctions and all the copies. Restoring the original pattern requires equal values on each copy pair. For any prescription on a nonempty original loose set, at most one forbidden word matches that prescription, while the pairs offer $2^r$ distinct choices consistent with equality. If there were no original loose distinctions, the shared count $e$ would satisfy $2e ≥ 3h$, giving $r=e-h+1 ≥ 2$. Again an allowed choice exists. Thus every original loose word occurs. Other knots retained outside a selected part can impose further restrictions on its readings.

## Moving a value through knots that block a change

At a given word, a mixed knot **blocks** the change of $b$ precisely when $b$ alone has its value there. A knot blocks at most one distinction. If it blocks $b$, any one of its other places can change while the knot stays mixed, because at least two places have the other value.

Both arguments below use the following operation. Start at $b_0$, which has a holder where its change is already safe or repairs that holder. If its other holder blocks its change, go through that blocking knot to one of the permitted other places $b_1$. At $b_1$, the knot just traversed already permits its change. Continue until reaching an unblocked $b_j$. Each blocked distinction reached has a unique blocking knot, and at most one way to be reached from a predecessor. Indeed, only its other holder could have supplied that predecessor, and that holder blocks at most one distinction. The starting distinction has no predecessor when its starting holder never supplies a step.

Choose a shortest sequence to the selected unblocked end. Its blocking knots are distinct, since each one blocks only its initial distinction. Every internal distinction has spent both holdings on consecutive knots. The last distinction cannot also occur in an earlier blocking knot, since that occurrence would shorten the sequence. Change the distinctions in reverse order. At each traversed knot, just its successor changes first, joining its initially lone value. At least one of the original opposite values remains. The initially lone value then changes, leaving the successor to carry the opposite value. Thus each traversed knot stays mixed throughout. The two applications below check the starting holder and the end's possible other holder.

## F for arbitrary fixed values

Whenever a knot has one free place and all its other places agree, set the free place to the opposite value. Repeat until no such knot remains. Each such step is necessary. A fully fixed all-equal knot certifies a contradiction.

Suppose the process has stopped without a conflict. Fill the remaining distinctions arbitrarily. If some knot $K$ is now all equal, at least two of its places were free when forcing stopped. Pick one as $b_0$. Its change repairs $K$. Whenever a mixed knot blocks the change of a free distinction, it contains at least one other free distinction. Otherwise the sole free value would already have been forced. Use every such other free distinction as a possible next choice. The starting holder $K$ supplies no predecessor, since it is all equal.

If every reachable distinction were blocked, each would have at least one successor, each would have at most one predecessor, and the start would have none. Counting the same steps by departures and arrivals contradicts finiteness. A shortest sequence to an unblocked end therefore exists. Make its changes in reverse. The last distinction can also lie in $K$. In that case at most the start and end change there, and a third place keeps its original value. Otherwise only the start changes at $K$. The end's other holder permits its first change, and every traversed knot stays mixed. This reduces the number of all-equal knots. Repetition yields an allowed extension.

This proves the forcing criterion for arbitrary pins without a local-fullness or individual-essentiality assumption. The earlier classification completed the residual assignment by an alternating traversal. [Earlier proof in its reconstruction setting](../../THREE-READERS-AND-GROWTH-20261120-001B/classification.md#two-observations-on-the-states)

## Single changes connect every finite system of this kind

**Counting disagreements.** Suppose two allowed states $s,t$ in different classes minimize the number of distinctions on which they disagree. Write $D$ for this nonempty set. Every $d ∈ D$ must be blocked in $s$, because otherwise changing $d$ there brings the two classes closer. At least $|D|$ different knots block such a distinction. Each of these knots must contain at least two disagreements, since $t$ also satisfies it. But all the disagreements together have at most $2|D|$ holdings. Equality follows throughout. Each $d$ has two holders, exactly one of which blocks it in $s$. Every knot meeting $D$ has exactly two disagreements of opposite values and at least one common place. Its other places agree with its majority value. In $t$ the two disagreements exchange values.

**Choosing a common change.** Pick a disagreement $d$, its blocking knot $K$ at $s$, and its other holder $L$. Pick any common distinction $x$ in $K$. Changing a common place leaves each knot meeting $D$ mixed in both states as long as the disagreements keep their values. The common distinctions in $K$ have value $1-s_d$. Those in $L$ have value $s_d$, since $L$ blocks its other disagreement in $s$. Hence $x$ cannot also belong to $L$.

If $x$ can change in both states, change it in both. Otherwise its single blocking holder contains only common distinctions. Use the preceding sequence argument starting at $x$, allowing steps only through these all-common blocking knots. Every blocked distinction now has **at least two** successors, because arity is at least three. The initial holder $K$ supplies no steps. If $B$ is the set of reachable blocked distinctions, at most $|B|-1$ steps lead to $B$. At least $2|B|$ steps leave $B$. There are therefore at least $|B|+1$ steps to unblocked ends.

If $L$ has just one common distinction $z$, reserve it. This distinction can receive at most one of those steps, since its holder $L$ takes no part in the sequences. Choose an unblocked end other than $z$. If $L$ has more than one common place, any unblocked end will do. Change the shortest sequence to the chosen end in reverse, in both states. The optional other holder of that end permits its first change, and every knot meeting $D$ keeps its opposite pair. All changes are legal and preserve the classes of $s,t$.

**Reducing a disagreement.** At $K$ the changed value of $x$ now permits $d$ to change in $s$. At $L$ the only possible change to its common distinctions occurred at the final end, because the root $x$ lies elsewhere and every internal distinction has both holdings among the all-common knots. If $L$ had a single common distinction it was reserved. Otherwise at least one common distinction still has its original value $s_d$. Thus $L$ also permits the change of $d$. Making it gives a closer pair from the same two classes, a contradiction. The proof also constructs the changes between any two states. Use a change toward the target whenever one is available. Otherwise apply the common changes at both states, reduce one disagreement, recurse on the closer pair, and undo the common changes at the target end.

There is an allowed state by F with no pins. The single-change class is therefore unique. Complementing every value preserves the entire relation. If two distinct distinctions lacked any of their four joint words, their projection would be only $00,11$ or only $01,10$. Changing either distinction individually would then be impossible, although the complement of a state changes both. Connectivity rules this out. **Every pair is free.**

Choosing the last common distinction requires care. On $(a,b,x),(a,b,z),(x,z,u)$, take $s=(1,0,0,1,1)$ and $t=(0,1,0,1,1)$ in the order $a,b,x,z,u$. To unblock $a$ in $s$, changing $z,x$ in both states is legal, but leaves $a$ blocked at the second knot. Changing $u,x$ instead frees $a$. The reserved-place step covers exactly this possibility. [Control and executed changes](lemma_counts.json)

## Literal checks and scope

A separate enumeration covered every connected system of one to four knots, with three or four places per knot and at most eight distinctions, once up to renaming. The 107 systems have 9,160 allowed states. Of 433,161 partial words, 357,339 extend and 75,822 fail. Forcing agreed with direct enumeration throughout. Each of 2,403 pairs was free. The eight trees gave exactly the two prescribed missing words, and deleting any one of their laws freed the original loose set. The other 99 systems gave the full loose projection.

Of 498,188 unordered pairs of allowed states, 998 initially permitted no disagreement-reducing single change from either end. The sequence construction was run on every choice of target disagreement and starting common distinction for those pairs, totaling 3,014 successful reductions. In a separate 33-knot example, the executed sequence made six common changes per state for the designated target and starting place. A two-place odd ring and a seven-knot pattern with three holders per distinction both have no states although the empty prescription triggers no forcing. The seven-knot pattern also ties three distinctions after one knot is removed. [Counts and controls](lemma_counts.json) · [Independent check](lemma_checks.py)

The three-system timing pilot took 0.043 seconds under the same memory cap. The longer 33-knot example checked its designated two states and their changes. Its full state relation was not enumerated. No unrestricted family of carrier functions was examined here.

From the repository root, the following reruns the checks.

```sh
r=research/NAE-LAYER-20261127-001/referee-R1
ulimit -v 1572864
.venv/bin/python -B "$r/lemma_checks.py" --pilot
.venv/bin/python -B "$r/lemma_checks.py" --output "$r/lemma_counts.json"
PYTHONPATH=tools .venv/bin/python -B -m knotlab check \
  --cnf 'q p x; ~q ~p ~x; p r y; ~p ~r ~y; r q z; ~r ~q ~z' \
  --loops x y z --contact q --witnesses p r --json
```
