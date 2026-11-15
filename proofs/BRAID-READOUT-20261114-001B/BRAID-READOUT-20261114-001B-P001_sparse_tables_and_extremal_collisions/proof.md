# Sparse recovery and the first collisions under one-strand tests

Status: Proved

## Standard statement

Let \(p\) be prime. An unknown table \(T\subseteq\mathbb F_p^2\) lists possible input pairs \((x,y)\). After any word in the crossing \(\sigma(x,y)=(y,2y-x)\) and its inverse, a test asks whether some pair in \(T\) gives a specified value on one specified strand. Each test starts from the same table. Answers record existence. Two tables *tie* when all these Boolean answers agree.

1. Every table with fewer than \(p\) states is uniquely determined, even among competitors of unrestricted size. Some tables of size \(p\) tie and others remain uniquely determined.
2. The minimum size on each side of a disjoint equal-size tie is \(p\). Each such minimum pair consists of two different complete families \(L_d=\{(x,x+d):x\in\mathbb F_p\}\). Precisely \(\binom p2\) unordered pairs attain this bound.
3. At size \(p\), every tie sharing \(p-1\) states is specified by two affine functions with different slopes and a derangement of their \(p-1\) columns of disagreement. There are \(\binom p2 p^2 D_{p-1}\) unordered pairs of this form, where \(D_m\) is the number of derangements of \(m\) objects. This gives a different sharp equality case for each \(p\ge3\).

## Nearest known result

The p-coordinate evaluation words of the affine functions form the dimension-two Reed–Solomon evaluation code on the full field. Recording one yes/no answer for each column and value is the classical Kautz–Singleton construction applied to this code. Each binary word has weight \(p\), and two different words have at most one common 1. The sparse recovery argument below is the classical cover-free bound for these parameters. Coordinatewise sets of possible symbols also give exactly the data defining the descendant of a subcode in the literature on separable codes. [Kautz and Singleton, *Nonrandom Binary Superimposed Codes*, Theorem 2 and pp. 370–371](https://doi.org/10.1109/TIT.1964.1053689) · [Cheng et al., *Bounds and Constructions for Separable Codes*, definitions in the abstract](https://arxiv.org/abs/1507.00954)

Fernández and Urroz also state the frameproof criterion for extended Reed–Solomon codes in section 3. At dimension two it gives the same small-table threshold. The equality cases below distinguish which tables collide at the threshold. [Their paper](https://doi.org/10.1007/s10623-021-00988-z)

In classical finite geometry the graphs \(k\mapsto x+kd\) are the nonvertical lines of the affine plane of order \(p\). A complete family of parallel lines partitions that plane. The two equality statements below use only agreement of affine functions and interpolation at two columns. The local contribution is to identify the exact crossing tests with this code and describe both equality cases for those tests. External priority for the equality cases remains unassessed.

Füredi and Ruszinkó use the same tight-cover argument for disjoint equal unions in linear uniform hypergraphs, and identify the three-member overlap configurations (Corollary 1.9 and Lemma 3.4). Thus the disjoint classification also specializes known reasoning. The all-prime enumeration for a single replacement is the narrower local comparison. [Uniform hypergraphs containing no grids](https://real.mtak.hu/7997/1/Uniform%20hypergraphs%20containing%20no%20grids.pdf)

The earlier three-label studies tested a single crossing and its inverse, and a learned reader that could inspect any individual cell of a joint table. Here every crossing power is available, and the later test sees one strand. [Earlier fixed crossing](../../../research/STRAND-RETURN-20261114-001/braid_design.md) · [Earlier learned reader and its cell queries](../../../research/BRAID-ACTIONS-20261114-001/braid_actions.md)

## Proof

Write \(d=y-x\). The crossing keeps \(d\) and adds \(d\) to the first value. Its inverse subtracts \(d\). A word with exponent sum \(k\) takes the input to

\[
(x+kd,\;x+(k+1)d).
\]

The field is prime, so the integer exponent sums cover every element \(k\) of the field. A possible pair names one function \(f(k)=x+kd\). Thus we know exactly the sets \(U_T(k)=\{f(k):f\in T\}\), one per column \(k\). We identify a state with its function from here on. An affine function of nonzero slope difference has exactly one agreement with its competitor. Distinct functions of equal slope have none.

**Sparse recovery.** If \(h\notin T\), each \(f\in T\) can account for \(h(k)\) at most once. Hence at least \(p-|T|\) columns witness \(h(k)\notin U_T(k)\) whenever \(|T|<p\). All members of \(T\) pass every test on their own values. Therefore keeping precisely the candidate functions whose values always appear reconstructs \(T\). Further, suppose \(S\) has the same readout. The witness argument gives \(S\subseteq T\), so \(|S|<p\) and applying it to \(S\) gives \(T\subseteq S\). The empty table is included.

**Equality for disjoint tables.** Suppose \(A\) and \(B\) are disjoint, have \(p\) members each, and tie. Each \(f\in A\) must meet some \(g\in B\) in each of the \(p\) columns. There are only \(p\) choices for \(g\), each usable at most once. Thus exactly one member of \(B\) agrees with \(f\) at each column. The reverse conclusion also holds. If two members of \(A\) gave the same value at one column, the member of \(B\) giving that value would agree there with two members of \(A\). This contradicts reverse uniqueness. Every two distinct members of \(A\) consequently have equal slopes. All \(p\) intercepts occur. The same holds for \(B\), with a different slope by disjointness.

Conversely, each complete \(L_d\) realizes all values in every column, so any two different such families tie. These are also the only size-\(p\) tables with this full readout, since each of their \(p\) entries must take a different value in every column. The preceding sparse bound gives minimality.

**Equality for one changed state.** Write \(A=C\cup\{f\}\) and \(B=C\cup\{g\}\) with \(|C|=p-1\) and \(f\ne g\) outside \(C\). If \(f\) and \(g\) never agree, covering the \(p\) values of \(f\) would require \(p\) members of \(C\). Thus \(f,g\) meet in one column \(k_0\). Write \(K=\mathbb F_p\setminus\{k_0\}\). At every \(a\in K\), \(f(a)\) must occur in \(C\) and so must \(g(a)\). Each common function agrees with each of \(f,g\) at most once. All \(p-1\) functions are therefore used exactly once to cover \(f\) on \(K\), and exactly once to cover \(g\) there.

For each \(a\in K\), take the unique member \(h_a\) agreeing with \(f\) there and let \(\pi(a)\) be its column of agreement with \(g\). The two uniqueness statements make \(\pi\) a permutation of \(K\). Since \(f(a)\ne g(a)\), \(\pi(a)\ne a\).

Conversely, given any fixed-point-free permutation \(\pi\) of \(K\), define \(h_a\) by interpolation through the two values \(f(a)\) and \(g(\pi(a))\) in their respective distinct columns. This function differs from \(f\) at \(\pi(a)\) and from \(g\) at \(a\). If \(a\ne b\) and \(h_a=h_b\), that function agrees twice with \(f\), forcing it to equal \(f\). Thus the \(h_a\) are \(p-1\) distinct functions, each with just its prescribed single agreement with \(f\) and with \(g\). At each column in \(K\), their joint support already includes both differing values. At \(k_0\), \(f\) and \(g\) agree. Adding either function therefore gives exactly the same sets of values. This construction inverts the extraction of \(\pi\).

For unordered ties fix any ordering of the function labels and take the earlier differing function first. There are \(\binom p2\) choices for their distinct slopes and \(p^2\) ways to assign their intercepts in slope order. Each pair has \(D_{p-1}\) possible common sets. An unordered tie recovers its two differing functions from its symmetric difference, and the fixed ordering recovers its permutation, so every tie is counted exactly once.

## Controls and scope

- For \(p\ge3\), take every nonzero constant function as \(C\). The two completions \(C\cup\{k\mapsto k\}\) and \(C\cup\{k\mapsto 2k\}\) tie. Only column 0 has all \(p\) values. This shows why disjointness matters in the complete-slope-family classification. When \(p=2\), one column of disagreement remains and has no derangement. The disjoint tie still exists.
- A size-\(p\) table can be uniquely determined. Take \(f_d(k)=dk\) for all \(d\). Column 0 forces every candidate to have intercept 0. Column 1 requires every slope. In contrast, adjoining any new function to a complete \(L_d\) gives a size-\((p+1)\) table with exactly the same readout.
- All one-strand tests together detect whether \(T\) itself is nonempty. For two distinct complete \(L_d,L_e\), a later joint requirement \(y-x=d\) admits every state of the first table and none of the second. This distinguishes compatibility with a later joint constraint from the observations available here. A solver with the two original tables can compare their entries directly. The information lost under this observation rule supplies no lower bound on the time for formula-only SAT decision.
- The assertions concern sets of states with no multiplicities, and a stated prime alphabet. Intermediate overlap sizes between 1 and \(p-2\) are outside the two equality classifications.

## Validation

[The checker](check.py) executes the crossing on every original pair, groups tables by their actual observations, and compares the tied pairs with the algebraic classifications. All tables of size at most \(p\) were enumerated at \(p=2,3,5\). The numbers of disjoint size-\(p\) ties were respectively 1, 3 and 10. The numbers sharing \(p-1\) states were 0, 27 and 2,250. For each smaller table the checker looks for an outside compatible state and for a redundant member. At \(p=7\) it checks all 265 replacements for one fixed pair of differing functions, plus the unique and ambiguous controls at sizes 7 and 8. The argument above proves the assertions uniformly. These computations check finite cases by a separate method within the task.

Three deliberate changes each made the checker exit with failure. Replacing the crossing by a plain swap failed the strand-value check. Selecting pairs with one common state instead of disjoint pairs failed the complete-family comparison. Omitting a class of derangements failed the comparison against the independently enumerated common-state ties.
