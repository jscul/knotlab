# Which three-place holdings admit a common explanation?

With the supplied right to read a change and the supplied squared-weight probabilities, **four exact probability comparisons decide every lawful three-place not-all-equal holder**, including a holder in a structure of arbitrary finite size. A knot with at least two loose distinctions always defeats a common explanation. A knot with one or zero loose distinctions can give either result. Which outside holders use its marks, and which outside assignments they have in common, determine the answer.

## Four comparisons from the physical holdings

With one reader on each mark, let $p_i$ be the probability that mark $i$ is the minority in the three ordinary reads, and write $X_i=+$ for a positive change answer. There is a common explanation for all eight complete question tables exactly when all four comparisons hold:

\[
  \Pr(X_i=X_j=+)\ \le\ (1+p_k)/2
       \qquad(\{i,j,k\}=\{1,2,3\}),\qquad
  \Pr(X_1=X_2=X_3=+)\ \le\ 1/2.
\]

To compute these quantities directly, let $G(x,y)$ count assignments on all outside distinctions compatible with **both** central words $x,y$. The squared-weight rule gives reduced entries $G(x,y)/\operatorname{tr}G$. In particular $p_i$ uses the diagonal, and $\langle X_D\rangle=\sum_x G(x,x+D)/\operatorname{tr}G$. Expanding $\prod_{i\in I}(1+X_i)/2$ then gives each all-plus probability. This uses the outside completions with their physical multiplicities. Knowing which six words occur on the central knot gives only its support.

**Proof.** Complementing the whole assignment preserves the positive weighting, exchanges the two signs of each ordinary read and preserves every change answer. Moments with an odd number of $Z$ reads therefore vanish. A common explanation, if it exists, can have this same symmetry by giving both ordinary orientations equal weight. Its $Z$ list has exactly one minority position $i$. A table of nonnegative masses on the eight complete $X$ lists and three minority positions specifies the entire model after giving the $Z$ list its two orientations. The $XXX$ table fixes the eight available masses.

To see what the mixed questions require, write $T_i=\langle X_iZ_jZ_k\rangle$. Both central words related by flipping $i$ are allowed only when $j$ and $k$ have opposite ordinary values. Thus $T_i=-\langle X_i\rangle$, even if there are further restrictions outside. In a predetermined list, $Z_jZ_k=+1$ exactly when $i$ is the minority. The mixed expectation requires $\mathbb E[X_i\,1_{\text{minority }i}]=(T_i+\langle X_i\rangle)/2=0$. Consequently the two bins at minority $i$, one for each sign of $X_i$, each require mass $p_i/2$. Meeting these demands gives all remaining moments: every all-change moment is obtained from the $XXX$ list, every ordinary pair from the minority position, and the only other moments with an even number of ordinary reads are the three just checked. Binary moments determine the complete outcome probabilities in every question.

Each supplied $X$ list $s$ can contribute to precisely three bins $(i,s_i)$. The elementary allocation condition requires the demand of each collection of bins to be at most the total mass of the lists eligible for at least one of them. This condition is sufficient by the finite maximum-flow theorem. Taking both signs for any one minority permits all lists and gives an automatic bound. Taking one sign $\sigma_i$ for each $i$ in a nonempty set $I$ gives the remaining 26 bounds
\[
 \frac12\sum_{i\in I}p_i+\Pr[X_i=-\sigma_i\text{ for every }i\in I]\ \le\ 1 .
\]
All change products have nonnegative expectations because the physical amplitudes are nonnegative. Expanding the probability of any fixed answer word therefore bounds it by the all-plus probability for those same readers. Finally $\langle X_i\rangle\le 1-p_i$: pair each contribution with its flipped word and apply $2ab\le a^2+b^2$ on the ordinary slice $Z_j\ne Z_k$. The three single-reader bounds hold automatically. The three pair comparisons and the one triple comparison remain. The classical allocation result enters at the sufficiency step. The reduction to these four counts follows from this knot and measurement rule. [Ford and Fulkerson, 1956](https://doi.org/10.4153/CJM-1956-045-5)

## What the loose distinctions tell us

With two loose central marks, the outside rules see only the third. The two values of that mark have equally many outside completions, paired by complement. The central minority probabilities are all $1/3$. The two loose marks individually, and their joint change, each have expectation $2/3$, independently of how the outside uses the third mark. Thus their two-plus chance is $3/4$, exceeding the bound $2/3$. Equivalently, each loose mark has $\Pr(X_i=-)=p_i/2$. In a common explanation every such minus would have to come from its own minority bin. Two loose marks both give minus with probability $1/12$, although they cannot both be the minority.

With independent outside parts, each touching just one central mark, let $\lambda_i$ be the number of common completions when that mark is changed, divided by the number for one fixed value. Complement symmetry gives the same denominator for either value, and a loose mark gives $\lambda_i=1$. Between central words $x,y$, the common-completion factor is $\prod_{i:x_i\ne y_i}\lambda_i$ relative to the diagonal. In particular $p_i=1/3$ and
\[
 M=\lambda_1\lambda_2\lambda_3+\frac23(\lambda_1+\lambda_2+\lambda_3).
\]
If the immediate outer holder has $q$ places and all its other distinctions are private, then $\lambda=(2^{q-1}-2)/(2^{q-1}-1)$. The same formula holds inside any tree of holders meeting once per pair: after removing the immediate holder, the separate parts at its other marks each have equal completion counts for their two values. Thus on a tree with three-place neighbors, a ternary with at least one loose mark defeats a common explanation. A ternary with no loose mark has the same complete local table as the three separate outer ternaries in the table below.

| Supplied central reading, all outside distinctions unread | Loose marks | $M$ | Common explanation |
|---|---:|---:|---|
| Isolated three-place knot | 3 | 3 | No |
| One mark in one other ternary | 2 | 22/9 | No |
| Two marks in two separate ternaries | 1 | 2 | No |
| Two marks together in one other ternary | 1 | 12/5 | No |
| Two marks in one ternary and the third in another | 0 | 28/15 | No |
| All marks in the same duplicate ternary | 0 | 3 | No |
| Three separate outer ternaries | 0 | 44/27 | Yes |
| Three separate four-place outer knots | 0 | 804/343 | No |
| Three separate five-place outer knots | 0 | 9044/3375 | No |

The all-shared result already differs among three-place outside holders. Repeated meetings give the $28/15$ example without requiring a duplicate. Even with three distinct neighbors and just one shared distinction per pair of holders, changing the widths of those neighbors can reverse the answer. A one-loose counterexample to a rule based on loose count alone is given by the smallest funded four-ternary source below. Each row has a direct physical completion count and a separate, exact test on all 64 lists. Every corresponding parity table admits a common explanation. [Complete tables and certificates](../../artifacts/THREE-READERS-AND-GROWTH-20261120-001A/THREE-READERS-AND-GROWTH-20261120-001A-E001_three_readers/holders.json)

## Enlarging the readers or telling them other answers

With three separate outer ternaries, enlarging reader $i$ to hold its central mark and its own two outside marks restores the complete isolated table. For not-all-equal, use the ordinary central read and the change of all three marks in that branch. Complementing the branch exchanges its two equally sized conditional preparations. For parity the change of the central and one private mark does this. These local changes act as the original single change on the encoded central word. All mixed product expectations reproduced the isolated table. The enlarged not-all-equal score is 3. The parity score is 0 and its explanation remains common.

With the outside marks measured as changes before the free reader settings, each reader needs one communicated bit. On its branch, take the parity of the private minus answers under not-all-equal. Reverse the central change answer if that parity is odd. For a branch with $p$ private marks and outside answer word $h$, the unnormalized factor on its central value $x$ is $2^p-1$ for the all-plus answer, and $-(-1)^{x|h|}$ otherwise. Its magnitude is independent of $x$. The communicated correction removes the relative sign. Under parity only the two answer words all-plus and all-minus have nonzero probability, and the sign of the first private answer gives the correction. It is fixed before any reader setting.

| Supplied reading on the six outside marks | Not-all-equal outcome on the three readers | Parity outcome |
|---|---|---|
| All changes, every outcome kept and corrected | Every one of 64 heralds gives the isolated table after correction, $M=3$. Ignoring the messages gives $44/27$. | Eight nonzero heralds out of 64, each corrected to the isolated table, $M=0$. |
| All changes, accept only an all-plus outside report | $M=3$ at acceptance probability $27/64$ | $M=0$ at acceptance probability $1/8$ |
| All ordinary reads, heralds ignored | $M=44/27$, with a common explanation | $M=0$, with a common explanation |
| All ordinary reads, accept only differing marks within every private pair | $M=3$ at acceptance probability $8/27$ | The accepted event has probability zero. |

With all ordinary outcomes publicly retained under not-all-equal, two are impossible. Of the other 62, eight have $M=3$ and total probability $8/27$. Another 24 have $M=4/3$ and no common explanation, with total probability $4/9$. The other 30 are local. A common model including the public herald would have to explain each positive-probability conditional table. Forgetting the herald does admit a common explanation here. In these positive ordinary-read preparations each $XZZ$ correlation is already nonpositive and the $XXX$ correlation nonnegative. Local answer-sign changes cannot improve their average signed score. This distinguishes information retained on every trial from accepting just the $8/27$ subensemble. [All herald probabilities, complete tables and certificates](../../artifacts/THREE-READERS-AND-GROWTH-20261120-001A/THREE-READERS-AND-GROWTH-20261120-001A-E001_three_readers/holders.json)

## Smallest funded and reached examples

With three one-mark readers on any holder, **one four-place not-all-equal knot is the smallest funded source on which every three-mark table has a common explanation**. Three names allow only an isolated or duplicated ternary. The former violates and the latter is closed. Every choice of three from a four-place source scores $12/7$. An explicit common explanation uses 56 units of mass before giving both orientations of the $Z$ signs equal weight. Give the all-plus $X$ list 49 units, and each of the other seven one unit. Put each list with at least two minuses in the all-equal $Z$ bin, and each one-minus list in the bin where that reader is the minority. Divide the all-plus mass as 4 in the all-equal bin and 15 in each minority bin. These lists reproduce every entry. For any wider isolated knot the hidden marks are either all equal, giving the same four-place mixture after summing over their two possible values, or contain both values, giving independent positive single-mark weightings. Thus every three-mark subset is local at every width at least four. The four-place source also gives four unary four-place children, and every triple on the resulting five holders is local. The fresh assignments in the separate branches only reduce the corresponding change expectations by independent local sign noise.

With **at least one eligible ternary** required, the minimum for a funded source is seven physical distinctions. One witness consists of four ternaries
\[
 \{0,1,2\},\quad \{0,3,4\},\quad \{1,3,5\},\quad \{2,4,6\}.
\]
The last two holders each have one loose mark. The first two score $32/19$ and the last two $34/19$, all with common explanations. An exhaustive census of connected all-ternary holdings through four holders, allowing repeated meetings, gave respectively 1, 3, 4 and 12 lawful types. The corresponding numbers funding a step were 1, 2, 4 and 9. Only the displayed four-holder type was funded and lacked a violation on every holder. A separate census permitted wider holders and exhausted every connected open source on at most eight physical distinctions. Its counts of lawful sources at widths three through eight were 1, 2, 5, 13, 40 and 125. All cases through six with an eligible ternary and a funded step had a violation. This proves the minimum by physical distinctions. The following argument also proves a minimum of four holders at unrestricted widths.

With at most three holders, **every eligible ternary violates**, even if its neighbors are arbitrarily wide. The two-loose proof covers at most one shared mark. If exactly two marks are shared with the same outside holder and the remaining outside holder sees none, fix all the unmarked outside values. Mixed values on that first holder restore the isolated central table. Its two complementary constant assignments give the same reduced table as the two ternaries sharing two marks, once their equally numerous completions are added. The score is consequently a mixture of $3$ and $12/5$. A holder sharing all three marks must duplicate the central knot, since a strict superset fails its own projected law.

It remains to take two outside holders, $K,L$, each seeing a nonempty disjoint subset of the central marks. The subset sizes are either $(1,1)$ or $(2,1)$. Let $u,v$ count their respective unmarked distinctions held by just one of $K,L$, and $w$ those held by both. Put $N=2^{u+v+w}$, $A=2^v$, $B=2^u$. For a pair of allowed central words $x,y$, form $J_K$ from the values taken uniformly by all of $K$'s marked distinctions in either word, and likewise $J_L$. For each such value the outside holder forbids the one constant word of that value on its unmarked distinctions. Inclusion and exclusion give
\[
  G(x,y)=N-|J_K|A-|J_L|B+
  \begin{cases}|J_K||J_L|&w=0,\\ |J_K\cap J_L|&w>0.\end{cases}
\]
On the $(2,1)$ shape, summing these entries for the two-plus test at the two marks in $K$ gives excess, multiplied by $8\operatorname{tr}G$, equal to $4N-4A-4B+4\,1_{w=0}$. This is strictly positive because $A/N\le1/2$ and $B/N\le1/4$. On the $(1,1)$ shape the three-plus test gives $12N-30A-30B+58$ for $w=0$ and $12N-30A-30B+30$ otherwise. Each outer holder has at least two unmarked places. If at least one has three or more, $(A+B)/N\le3/8$, which is sufficient. If both have exactly two, their common unmarked count can be 0, 1 or 2; the three numerators are respectively 10, 6 and 18. This exhausts the holdings with at most three holders. The code derives the coefficients by summing over the six central words and checks them against independently enumerated physical assignments. [Coefficient and physical receipts](../../artifacts/THREE-READERS-AND-GROWTH-20261120-001A/THREE-READERS-AND-GROWTH-20261120-001A-E001_three_readers/holders.json)

With **a completed ordinary growth step** required, start with $\{0,1,3\},\{0,2,4\},\{1,2,5\}$. Each pair of holders has the third as its witness, with no joint witness. The sole funded birth takes $3,4,5$ and, under not-all-equal, receives one fresh distinction $6$. The resulting four holders have seven physical distinctions and give seven reader placements: three old ternaries and four triples in the new four-place knot. Every table admits a common explanation. The largest signed score is $19/11$. The resulting stage also funds its next step.

For minimality, one starting holder makes at least three children, and two connected open lawful holders each need an exclusive distinction. Otherwise one support is properly contained in the other, making the larger projection stricter than its written law; identical supports are closed. Two holders have no third witness for a pair birth and therefore form at least two children. Any greater starting holder count plus a genuine birth also gives at least four total. Each not-all-equal birth supplies a fresh distinction. At least 12 places and at least one loose distinction require at least seven physical distinctions. Both lower bounds are attained by the displayed example, which retains eligible ternaries. Demanding an *empty* eligible-ternary denominator instead gives nine physical distinctions at the first reached example. Four old holders all meeting pairwise, each with one extra loose distinction, supply a separate wider-only preparation: they make a single new five-place holder.

With one vote per unlabelled physical holding type, the width census generated the multiplicity of each pair's meetings and each holder's loose count, factored out holder permutations, enforced at least three places, connectedness and the full projected local law, and passed each lawful source to the archived complete-round operator. Every NAE target of width at most nine has a predecessor of width at most eight, since its birth brings a fresh distinction. The search includes any last predecessor of a longer history. The built cases have no population weighting. These are properties of the supplied reader on actual ordinary holdings; the rule assigning the three-reader probabilities remains supplied. [Reproduction script](../../experiments/THREE-READERS-AND-GROWTH-20261120-001A/THREE-READERS-AND-GROWTH-20261120-001A-E001_three_readers/holders.py)
