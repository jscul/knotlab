# The two denser rosters at one round

## Standard statement

For ten finite incidence systems, the ideals of an explicit partially ordered set describe every generation produced from the first complete round onward. From generation $t\ge3$, its fixed-size ideals consist of level $t-1$ of $\mathbb N^3\times\{0,1\}^k$ with unit-transfer adjacency, together with three elements of degree one. For $k=2$, the largest number of elements within $r\ge1$ steps attains $12r^2+2$ exactly when $t\ge3r+2$. For $k=4$ and $r\ge2$, its counterpart is $48r^2-48r+24$, attained exactly when $t\ge3r+3$.

## Nearest known result

The earlier result for mutually sharing starts gives one unbounded chain for each knot with two loose distinctions. The fresh-count proof of the grouping rule for down-closed sets supplies the induction below. The two new finite choices for each knot with three loose distinctions, their one-round count, and the sharp range of the best-member formulas are the additions here. [First-knot Proposition 4](../../FIRST-KNOT-20261118-001A/FIRST-KNOT-20261118-001A-P001_two_knots/proof.md) · [Fresh-count Theorems 1 and 4](../../FRESH-COUNT-20261118-001A/FRESH-COUNT-20261118-001A-P001_free_count/proof.md) · [Original probe](../../../research/KNOTS-WITHIN-REACH-20261125-001/checks/roster_probe/README.md)

## The witnessed steps at one round

Consider the ten census starts in Table 1 and the complete-round rule with the ordinary fresh count. A step between two current members requires a knot that shares a distinction with each of them. Let $t$ be the number of completed rounds and let the count within $r$ steps include the member one starts from. Use $k=2$ for the first eight starts and $k=4$ for the last two.

For every $t\ge 3$, write $n=t-1$. The roster consists of

$$
 (x,B),\qquad x\in\mathbb N^3,\quad B\subseteq\{1,\ldots,k\},
 \qquad x_1+x_2+x_3+|B|=n ,
$$

and three further members. Here zero is a natural number. In the displayed set a step transfers one unit between two different entries, reading the membership indicators of $B$ as entries bounded by one. The three further members each reach just one other member in a single step, the member with all $n$ units in the corresponding integer entry.

| Starts | Members at $t\ge3$ | Greatest count within $r$ steps when attained | Exactly when attained |
| --- | ---: | ---: | --- |
| First eight | $2t^2-2t+4$ | $12r^2+2$, $r\ge1$ | $t\ge3r+2$ |
| Last two | $8t^2-24t+27$ | $48r^2-48r+24$, $r\ge2$ | $t\ge3r+3$ |

At smaller $t\ge3$ the respective greatest count is strictly smaller. For the last two starts the greatest count within one step is 23 once $t\ge6$. Both ordinary treatments in the probe preserve these descriptions. All four capped alternatives first split the roster in round two. The proof also describes rounds one and two. It concerns the witnessed steps of these presentations. The companion knot audit addresses the allowed-state test.

## From the given starts to one common description

Number the knots of each input from zero in their listed order. A knot acts in the first round when it holds at least one loose distinction. Every pair of acting knots shares distinctions with a common knot, and no one knot shares a distinction with every acting knot. Thus the set of all acting knots is itself the only group. Call its birth $T$. Each acting knot supplies one distinction to $T$ and makes an offshoot with each of the loose distinctions that remain.

**Table 1.** The middle column gives the complete direct-neighbour lists, before the first round, in the order of the knots. For instance, $123$ denotes the set $\{1,2,3\}$. Shared distinctions between the listed knots are the witnesses used to read these lists. The final column gives offshoots in the first round, in the same order. A dash means the knot had no loose distinction and was absent from the group. A zero means it took part and had nothing left. [Census inputs](../../../research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json)

| Census input | Direct neighbours | Offshoots |
| ---: | --- | --- |
| 178 | $123,02,013,02$ | $1,1,1,2$ |
| 179 | $123,02,013,02$ | $1,1,2,1$ |
| 219 | $123,023,013,012$ | $1,1,1,2$ |
| 1382 | $14,04,34,24,0123$ | $1,1,1,2,0$ |
| 2218 | $14,0234,13,124,013$ | $1,1,1,\text{–},2$ |
| 2231 | $14,0234,13,124,013$ | $1,1,2,0,1$ |
| 2694 | $134,034,34,0124,0123$ | $\text{–},1,2,1,1$ |
| 3077 | $134,024,134,024,0123$ | $0,1,1,1,2$ |
| 1964 | $34,34,34,0124,0123$ | $1,1,1,2,2$ |
| 2236 | $14,0234,13,124,013$ | $1,1,2,1,2$ |

Indeed any two lists for acting knots in a row intersect. An acting knot misses itself. In the two rows with an absent knot, its list misses acting knot 0 in input 2218 and acting knot 2 in input 2694. This proves the claimed first group, including the two cases where an absent knot could still have served as a witness. In round one the births witnessed together by each start knot are exactly $T$ and its own offshoots.

## The induction on rounds

Let $H=\{h_i\}$ have one formal label for each acting start knot, and put $q=|H|$. Use the following order for bookkeeping.

- For each of the three knots making one offshoot, use an infinite chain. Its first element requires all of $H\setminus\{h_i\}$. Every later element also requires the preceding one.
- For each knot making two offshoots, use two incomparable elements. Each requires $H\setminus\{h_i\}$. There are $k$ such elements altogether.
- The labels in $H$ are incomparable. A knot making zero offshoots contributes its $h_i$ alone. These are all the requirements.

A down-closed set contains everything each of its elements requires. In round $t\ge1$ take all such sets of size $q-1+t$. Every set contains either all of $H$ or all but a single $h_i$. Indeed an element outside $H$ requires at least $q-1$ labels, and a set of this size cannot consist of fewer than $q$ labels alone. The sets containing $H$ are exactly the displayed $(x,B)$ with $n=t-1$, by taking initial segments of the three chains. A set missing $h_i$ can take only elements given by start knot $i$. It takes the first $t$ elements of its chain or a size-$t$ subset of its two incomparable elements.

In round one, $H$ names $T$. All other sets name the actual offshoots just listed. A set one element smaller that witnesses two of these is precisely $H\setminus\{h_i\}$, the label for their common start knot. At this initial comparison a start knot that did not act receives no new child and witnesses no new pair.

Suppose current members are the sets of the stated size $s$, and their parents are exactly their down-closed subsets of size $s-1$. Two members are one step apart exactly when their intersection has size $s-1$. The intersection is itself down-closed. It is their common parent, and every distinction shared by an old knot and a current member was taken from a parent. Current members share nothing directly with one another.

The group rule gives one group for each down-closed set $Y$ of size $s+1$ with at least two parents. Two distinct members in a candidate pair are $C\cup\{a\}$ and $C\cup\{b\}$ with $|C|=s-1$. A third member meeting each in $s-1$ elements either contains $C$ or equals $C\setminus\{c\}\cup\{a,b\}$ for some $c\in C$. A third of each kind cannot occur together, since they meet in only $s-2$ elements. A collection containing $C$ has that common witness. A collection of the second kind, together with the pair, is contained in the single set $Y=C\cup\{a,b\}$ and has no common parent. Its maximal extension is all the parents of $Y$. If $Y$ has just two parents, their pair is in no larger group and forms its own. The union of down-closed sets is down-closed, so every such group is accounted for.

It remains to show that the number of loose distinctions actually creates the stipulated sets with only one parent. For a birth with $p$ parents, let $D$ count the groups it owes next. The ordinary fresh count is $\max(D,3-p,1)$ whenever the parity closing exception does not apply. Read $D$ from the just-proved grouping rule.

| Current member | Parents | Groups owed next | Offshoots next |
| --- | ---: | ---: | ---: |
| Contains $H$ | At least 2 | $3+k-\lvert B\rvert$ | 0 |
| Missing $h_i$, uses a chain | 1 | 1 | 1 |
| Missing $h_i$, uses one of its two incomparable elements | 1 | 2 | 0 |
| Missing $h_i$, uses both incomparable elements | 2 | 1 | 0 |

For the first row, a set containing $H$ extends by any one of the three next chain elements or an unchosen incomparable element. Each extension has at least two parents. To see the parent assertion for any set containing $H$, one can remove either of two different maximal elements when it uses entries from at least two start knots. When it uses entries from only one start knot $i$, one can remove a maximal such element or remove $h_i$. The set $H$ itself has $q$ parents. In the second row, adjoining $h_i$ makes a group birth. Extending the chain makes a one-parent birth, supplied by the one surplus distinction. In the third row one can adjoin $h_i$ or the other incomparable element, both group births. In the last row one can only adjoin $h_i$. This accounts for every down-closed set at the next size, with the stipulated parents.

Every start here is connected by shared distinctions, and additions preserve that property. Every used distinction has two holders, and every birth takes only loose distinctions. For parity, a sum of current equations that contains only loose distinctions must use either every current equation or none, since it must cancel at every shared distinction. A birth taking a nonempty proper subset of the loose distinctions therefore never closes by implication. Round one and each induction step make at least the three chain offshoots, with disjoint inputs. The closing exception never applies, and not-all-equal has no such exception. This completes the induction under either knot law. The bookkeeping labels add no distinctions or joining rules to the growth. [Definition of a complete round](../../../research/RING-IN-BALANCE-20261123-001/definitions.md)

For two members containing $H$, having an intersection one element smaller means exactly a unit transfer, since the intersection takes the shorter of two initial segments and the intersection of the two subsets. For $t\ge3$ each of the three other members is a single chain of length $t$ together with $H\setminus\{h_i\}$. It has only one parent. The only other child of that parent is the member containing $H$ and the prefix of length $t-1$ of the same chain. This proves the asserted one-step description. All members belong to one part, since transfers can send all units to the first integer entry.

### The first two rosters and the number of births

Round one has $T$, three single offshoots and $k$ offshoots in pairs. Its size is 6 or 8. Round two has $3+k$ members containing $H$, three further chain members and $k/2$ further members each using both elements of one pair. Each of these last members has exactly two one-step neighbours, the two members containing $H$ and one of that pair. Its two parents each have it and one such member as children. Thus the sizes in round two are 9 and 12. In round one $T$ reaches the entire roster in one step. In round two the $3+k$ members containing $H$ are all witnessed together by $T$, and each is one step from exactly one further member. The best count then is $4+k$ within one step, and the entire roster within two.

For $t\ge3$, the count is

$$
 3+\sum_{h=0}^{\min(k,n)} {k\choose h}{n-h+2\choose2},\qquad n=t-1 .
$$

Choosing $B$ leaves $n-h$ units for three nonnegative integer entries. For $k=2$ the sum gives $2t^2-2t+4$. For $k=4$ it gives $8t^2-24t+27$. In the latter expansion the polynomial values of the missing terms at $n=2,3$ are zero, so it applies already at $t=3$. All births and only births are members after a complete ordinary round here. The two polynomials evaluated at $t=2$ would instead give 8 and 11.

## The greatest number within a given count of steps

First allow all integer values for the three entries of $x$, keeping the sum condition and the bounds on $B$. The least number of transfers between two members is the total increase in their entries. Each move supplies at most one unit of increase toward the target. Repeatedly transferring from an entry in excess of its target to one below its target attains the bound, including for nonnegative endpoints when the three entries are required to be nonnegative.

Fix a source $B$ of size $h$. A target subset may turn $p$ initially absent elements on and $j$ initially present elements off. Write $u=r-p$, $v=r-j$. If either is negative, this target subset is out of reach. Otherwise write $d_i$ for each of the three integer changes. They have sum $u-v$, and their total positive and total negative changes are at most $u$ and $v$, respectively, measuring negative changes by their absolute values.

For three entries, these two bounds are equivalent to $-v\le d_i\le u$ for each $i$ together with the sum condition. For example, if two entries are positive, their sum is bounded by $u$ because the third is at least $-v$. With one or three positive entries the bound is immediate. Changing all signs gives the other bound. Add $v$ to every entry and count triples of sum $u+2v$. At most one entry can exceed $u+v$. Subtracting the triples with such an entry gives

$$
 F(u,v)={u+2v+2\choose2}-3{v+1\choose2}
       ={u^2+4uv+v^2+3u+3v+2\over2}.
$$

Use $F=0$ when either argument is negative. The unrestricted count from type $h$ is exactly

$$
 U_h(r)=\sum_{p=0}^{k-h}\sum_{j=0}^h
  {k-h\choose p}{h\choose j} F(r-p,r-j).
$$

When $r\ge\max(h,k-h)$, expansion gives

$$
 U_h(r)=2^k\left[3r^2+(3-3k/2)r+
  1+{k^2-5k+2h(k-h)\over8}\right].
$$

Indeed summing over subsets gives means $E[p]=(k-h)/2$, $E[j]=h/2$, $E[p^2]=((k-h)^2+k-h)/4$, $E[j^2]=(h^2+h)/4$ and $E[pj]=h(k-h)/4$, with equal weight for each subset. The displayed quadratic in $h$ is maximized uniquely at $h=k/2$.

For completeness, the excluded small $r$ are evaluated directly from the finite sum. Symmetry under exchanging positive and negative changes gives $U_h=U_{k-h}$.

| $k$ | $r$ | $U_0$ | $U_1$ | $U_2$, when $k=4$ |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1 | 13 | 14 | |
| 4 | 1 | 19 | 22 | 23 |
| 4 | 2 | 103 | 115 | 120 |
| 4 | 3 | 293 | 308 | 312 |

Thus over all types the maxima are $12r^2+2$ for $k=2,r\ge1$, and $48r^2-48r+24$ for $k=4,r\ge2$. In both cases exactly type $k/2$ attains the maximum. Each of the $2^k$ possible target subsets contributes leading term $3r^2$ once $r$ is large enough, which accounts for the coefficients 12 and 48. The second expression would give 24 at $r=1$.

Return to the finite roster. Each transfer member keeps the same entries in the unrestricted set. Map each of the three further members to $((n+1)e_i-e_{i+1},\varnothing)$, with the indices taken cyclically and $e_i$ denoting one unit in entry $i$. These are distinct new members, one step from the respective $(ne_i,\varnothing)$. Every finite witnessed step maps to an unrestricted transfer, so every finite count is bounded by the unrestricted count at its image.

A source of type $h=k/2$ whose three integer entries are all at least $r$ realizes its full unrestricted count. A reachable target cannot decrease any entry by more than $r$, and the transfer construction stays between the initial and final values in every entry. Such a source exists exactly when $n-h\ge3r$. Conversely, if $n-h<3r$, some integer entry at every source of this type is less than $r$. Transfer $r$ units from it to another integer entry, keeping $B$ unchanged. This gives a reachable unrestricted member with a negative entry and a nonempty $B$. It has no finite preimage because the three additional images all have empty $B$. Sources of every other type already have strictly smaller unrestricted counts. This proves the stated sharp range, also for the count 23 at $k=4,r=1$. At $r=0$ every count is one.

For example, for the eight starts the last values of $r$ are 6 and 12 at rounds 20 and 40. For the two starts they are 5 and 8 at rounds 20 and 28. At the very next $r$ the best count in each case is strictly below the polynomial. For any fixed positive $r$ in the stated ranges, a sufficiently large finite round attains the unrestricted maximum. A single finite roster has only finitely many members.

## Which of the six laws preserve the result

Every ordinary birth receives at least what it owes. Consequently retiring when short and stalling when short give identical rosters for all rounds. The same argument also preserves the description for any fresh-count cap at least $3+k$, since the table of demands bounds every ordinary fresh count by this value.

At the end of the first round $T$ owes $3+k$ groups, one pair with each offshoot. The two offshoots at a start that made two also owe a group with one another. All these groups are pairs because each larger collection of pairwise candidates is witnessed by its single start knot. With the cap of three or four, $T$ alone falls short. The groups involving $T$ are cancelled. At each of the three starts that made only one offshoot, that offshoot now gives rise to two children forming a part of size two. At each start that made two offshoots, their mutual group survives. Its birth and one child of each of the two parents form a part of size three, with its two witnessed steps given by those parents.

When $T$ retires, these are all the parts. The member totals **still equal 9 and 12** under either retiring cap, although the ordinary roster is one part. With the cap of three and waiting, $T$ is one additional part of size one. With the cap of three and offshoots, its three children are one additional part of size three. A waiting $T$ has direct neighbours only in the start, whereas all other round-two members have direct neighbours only among round-one offshoots. Thus it gives no extra witnessed step across the parts.

The three parts of size two grow independently thereafter. More explicitly, a part consisting of a sequence of $l\ge2$ members, consecutive pairs alone a witnessed step, each holding two, gives $l-1$ pair births and one offshoot at each end. Ordered by successive shared parents, these form a sequence of $l+1$ members again holding two. The end offshoots owe one, and the others owe two. Hence no cap in this comparison shortens their fresh counts. The three parts from single offshoots and the parts from doubled offshoots begin with these holdings. There are no direct sharings between members of different parts at round two, and no knot witnesses a step across them. These facts persist because every later birth takes only from parents in its own part, and any old knot that newly witnesses a step has to be such a parent. If a member waits elsewhere, none of those parents shares a distinction with it. The three growing parts always supply multiple births, so the parity closing exception stays unavailable. In particular none of the four capped laws can recover the one-part description at a later round.

## Evidence boundary

The finite input reduction uses the listed census stars. The proofs of the induction, step count and exact range apply at every indicated integer round. They require the given complete-round growth rule, the choice of one round's current members, and the given common-witness step. The integer and subset names are a bijective description derived from those data. A total alone cannot establish that bijection, as the retiring caps at round two show. The separately frozen experiment and its independent recount are the numerical checks for their declared stages. The original probe was exploratory. No empirical result is used to extend an observed range.
