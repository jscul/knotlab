# What one strand can report after repeated crossings

Status: Proved

## Standard statement

Start with any set of ordered pairs of labels from the field of three elements. All 512 sets, including the empty set, are possible. A crossing takes each pair $(x,y)$ to $(y,2y-x)$. The public menu lists possible crossing counts. The reader later chooses one count and one label, then asks whether **some** allowed pair has that first label after that many crossings. With one, two, or three distinct crossing powers offered, the tables fall into **8, 50, or 110** classes of identical answers. A sender who sees the table and knows the menu, and must send one fixed-length binary message before the reader chooses a question, needs exactly **3, 6, or 7 bits**. Of the 110 classes for all powers, 73 determine the full table and one contains 214 different tables.

## Nearest known result

The November 14 learned-crossing experiment counted complete Boolean answer vectors on 13 menus and recorded the class sizes. Its three current single-coordinate tests give the first row below. A second experiment used the crossing studied here, enumerated all 512 tables and measured recovery after undo from the two separate lists of values. Its one-bit and two-bit example used individual states and the one fixed label zero. The increment here is the complete class-size distribution for each menu of powers of this crossing, the first disjoint ambiguities, and the check with five labels. These earlier records are historical comparisons. The derivation below uses the specified permutation and reader directly. [Earlier menu definitions and exact counting](../../../research/BRAID-ACTIONS-20261114-001/independent.py) · [Earlier stop and undo reads](../../../research/STRAND-RETURN-20261114-001/strand_returns.md)

In the literature, the indicator of a label at each chosen position is the binary encoding used in Kautz and Singleton's superimposed codes. Here each codeword is obtained by evaluating a polynomial of degree at most one. The observed table produces the coordinatewise Boolean OR of its codewords. The agreement bound used below is elementary for linear polynomials. The finite class sizes refer to this particular menu. External novelty of these numbers is unassessed. [Kautz and Singleton, 1964](https://doi.org/10.1109/TIT.1964.1053689)

## Counting the classes

Write $d=y-x$. The crossing keeps $d$ and sends the first value $x$ to $x+d$. After $k$ crossings the first value is $x+kd$. Three crossings return every original pair, so repetitions of any offered power modulo three add no test. Write $K$ for the offered subset of $\{0,1,2\}$. Number the Boolean questions by their pair $(k,a)$, with $a$ a possible first label. The report $B(S)$ consists of those questions answered yes by the table $S$. Thus two tables give the same answers precisely when their reports agree.

The following calculation determines **each** class size, including zero for an impossible report. For any proposed set of yes answers $C$, put

$$
D(C)=\{(x,d): (k,x+kd)\in C\text{ for every }k\in K\}.
$$

Exactly the subsets of $D(C)$ give reports contained in $C$, so $2^{|D(C)|}$ tables do. Subtract the tables which miss at least one of the desired yes answers by inclusion–exclusion. For each proposed report $B$, the resulting class size is

$$
n(B)=\sum_{C\subseteq B}(-1)^{|B|-|C|}2^{|D(C)|}.
$$

Indeed, a table with report $A\subseteq B$ contributes the sum of signs over $A\subseteq C\subseteq B$, which is one if $A=B$ and zero otherwise. When $n(B)>0$, the set $D(B)$ itself produces $B$ and is the unique largest table in that class under inclusion.

| Offered powers | Number of classes | Number of classes of each size | Exactly determined tables | Bits |
| --- | ---: | --- | ---: | ---: |
| Any one | 8 | 1 of size 1, 3 of size 7, 3 of size 49, 1 of size 343 | 1 | 3 |
| Any two | 50 | 34 of size 1, 9 of size 7, 6 of size 25, 1 of size 265 | 34 | 6 |
| All three | 110 | 73 of size 1, 27 of size 3, 9 of size 16, 1 of size 214 | 73 | 7 |

For one power, if $r$ labels occur, each of the $r$ disjoint sets of three possible pairs independently supplies a nonempty subset, giving $7^r$ tables per report. For any two powers the two reported first values determine one ordered pair uniquely. The two supports can therefore be any two nonempty subsets of three labels, or both empty. This gives $7^2+1=50$ reports. For three powers the formula above uses only nine cells and nine questions. For example, when all nine questions have answer yes, grouping the sum by $|D(C)|=0,1,2,3,4,6,9$ gives coefficients $-10,36,-36,-9,27,-9,1$. The result is 214. Its tables of sizes three through nine number 3, 18, 72, 75, 36, 9 and 1. The complete array of $n(B)$ for each representative menu is in the census. Bit $3k+a$ indicates a yes answer to question $(k,a)$. [Complete class sizes](census.json)

The program checks all seven nonempty menus individually. Their profiles depend only on the number of offered powers. In particular a relabeling $k\mapsto ak+b$, with $a\ne0$, amounts to replacing $(x,d)$ by $(x+bd,ad)$. It carries any ordered pair of distinct powers to any other such pair. Each class profile accounts for all 512 tables. For example the last row has $73+27\cdot3+9\cdot16+214=512$.

Two distinct classes must send different messages, since one allowed question distinguishes them. A shared enumeration lets the parties encode a class by its index and decode any answer from that index. The minimum fixed length for $c$ classes is therefore $\lceil\log_2 c\rceil$ bits. This is a statement about the bits passed through this interface.

## First ambiguity

Suppose that $m=|K|$ powers are available over a prime field. If a pair $p=(x,d)$ is absent from $T$ yet every read of $p$ occurs in the report of $T$, then $|T|\ge m$. For each $k$, a member of $T$ must match $x+kd$. A different pair agrees with $p$ for at most one $k$, because two linear functions agreeing twice have the same two coefficients. The $m$ required matches therefore use $m$ distinct members. In particular any source table of size less than $m$ is determined among **all** tables. Its report excludes every external pair. A proper subset cannot have the same report either, by the same bound applied to a removed pair.

These disjoint tables attain the lower bound at three labels. The entries here are the original ordered pairs $(x,y)$.

| Powers | First table | Second table | Shared report |
| --- | --- | --- | --- |
| 0 | $\{(0,0)\}$ | $\{(0,1)\}$ | $\{0\}$ |
| 0, 1 | $\{(0,0),(1,1)\}$ | $\{(0,1),(1,0)\}$ | $\{0,1\}$ at both powers |
| 0, 1, 2 | $\{(0,0),(1,1),(2,2)\}$ | $\{(0,1),(1,2),(2,0)\}$ | Every label at all three powers |

Thus over three labels the least size of each table in a disjoint equal-size ambiguity is 1, 2 or 3. The same examples minimize the total size of any two nonidentical indistinguishable tables, at 2, 4 or 6. Under all powers the three sets of size three in the largest class are exactly the sets with fixed $d=0,1,2$. To report all three labels at every power, no two of the three pairs may ever agree at the same power. Two different $d$ values would agree at one power, so all three have the same $d$.

## Controls and five-label check

The middle example tests a reader retaining only the two separate original lists. These are the first-coordinate supports at powers zero and one, since the next first value is the current second value. After two actual crossings, the first table permits first labels $\{0,1\}$ and the second permits only $\{2\}$. Substituting a stop for that second-power read gives the wrong answer on the second table. With all 512 tables equally likely, the optimum decoder of the whole third support from the two lists succeeds for 371 tables. To obtain this count, in each of the 50 marginal classes choose its most frequent third support and sum those frequencies. The two lists determine the third support without guessing for exactly 34 tables. The three-pair example tests the converse limitation. Even an error-free reader of every offered power gives the same answers on two disjoint tables.

The direct calculation enumerates original $(x,y)$ tables, repeatedly performs the crossing, and partitions the tables by all their Boolean answers. The second calculation works with $(x,d)$ and uses inclusion–exclusion over possible reports, without enumerating tables. The two calculations agree separately on each possible report of every ternary menu. This is V1 validation by two algorithms in the same task. The check also compares every displayed class size against the stored census. [Replay and numerical controls](check.py)

For five labels the same crossing returns after five moves. The bounded check covers all $1+25+300+2300+12650+53130=68{,}406$ tables of at most five pairs and all 31 nonempty menus. Every menu of a given size had the same profile within this roster. In order of one through five offered powers, the numbers of distinct reports in the roster are **32, 962, 10,447, 44,372 and 64,527**. The smallest disjoint equal-size confusions have **1, 2, 3, 4 and 5** pairs per table, respectively. The preceding argument excludes smaller examples for every table size. The five counts of distinct reports have only the stated sparse scope. Explicit original pairs for each minimum appear in the census. [Five-label witnesses](census.json)

The evidence class is finite-instance classification. Its inputs are the ordered labels, the crossing and the specified existential reads. Full-table recovery uses 9 fixed bits at three labels. Counting answer classes here supplies no time bound for a satisfiability solver.
