# Two proposed three-parent joins remain distinguishable by bond distance

Let \(r\) be any junction of arity five or six that introduces three fresh
distinctions. Use one of them at each of \(w,B,C\), which each introduce
three fresh distinctions. Let \(w\) be unary. Either of \(B,C\) may use
an additional legal parent from the older block. Next add \(a,b,d\) on
\((w,B),(w,C),(B,C)\), respectively, with either allowed fresh count.
Finally add \(X\) on \((a,b)\) with two fresh distinctions. The first three
parent pairs have \(r\) as a common neighbor and the last has \(w\).

Use \(l_w,l_B,l_C\) for the remaining loose distinctions of \(w,B,C\)
and \(f,g\) for the loose outputs of \(X\). The marks
\(\{f,l_B,l_C\}\) are legal, with pairwise witnesses \(a,b,d\) and no
common neighbor of all three. The marks \(\{l_w,l_B,l_C\}\) are forbidden
because \(r\) is a common neighbor. The bond-distance table capped above
five already distinguishes these unordered triples, even under arbitrary
renaming of its distinctions.

## One entry rules out the named exchange

Write \(K(i,j)=D(i,j)+1\), the minimum bond size through the pair. Use the
auxiliary graph in which a shared distinction joins its two junctions and a
loose distinction joins its junction to a single exterior node. The valid
parity equations are sums of the junction equations, hence their supports
are the cuts of sets of ordinary junctions. A nonempty cut is a bond
exactly when both sides are connected. A disconnected side gives a smaller
cut, and a subcut supported within a cut with connected sides must have
constant membership on each side.

The ordinary meeting graph is simple and bipartite. Its bipartition persists
at a join because parents having a common neighbor have the same color.
The star of a single junction and the sum of the stars of two adjacent
junctions are bonds. Indeed, after removing the one junction or the two
adjacent junctions, the latest junction in each remaining ordinary component
has at least two outputs, at most one of which was consumed at the removed
junctions. Its other output connects the component to the exterior. For an
adjacent pair, the at-most-one claim follows from their opposite colors.

Let \(t=rw\) and \(s=rB\) denote the corresponding shared distinctions.
The star at \(r\) gives \(K(t,s)\le 6\). A cut through \(f,s\) contains
both loose outputs of \(X\), the distinction \(s\), and a crossing on each
of \(X\!\to a\!\to\mathrm{exterior}\) and
\(X\!\to b\!\to\mathrm{exterior}\), via a loose output at \(a,b\).
Exactly one of \(r,B\) is on the ordinary side of the cut. If it is \(r\),
the paths from \(r\) through \(w,C\) to the exterior give two additional
crossings. If it is \(B\), its loose distinction and its path through
\(d\) give two additional crossings. In either case all seven crossings
are distinct. Thus \(K(f,s)\ge 7\), also with \(g\) in place of \(f\).
The proposed exchange fixes \(s\) and sends \(t\) to one of \(f,g\).

## Arbitrary renaming of the marks

For each distinction \(z\), let \(N_k(z)\) be the other distinctions with
\(K(z,\cdot)\le k\). Write \(S_u\) for the star at \(u\) and
\(e_h=1\) if \(h\) has arity four, and \(e_h=0\) otherwise, for
\(h=a,b,d\). The only bonds of size at most six through either \(f\) or
\(g\) are \(S_X\), together with \(S_X\mathbin{\triangle}S_a\) if
\(e_a=1\) and \(S_X\mathbin{\triangle}S_b\) if \(e_b=1\).

To see this, take the ordinary side of a cut through \(f\). It contains
\(X\), so its cut includes both loose outputs of \(X\).

- If both \(a,b\) are outside, also count \(Xa,Xb\). Including \(w\)
  adds its loose distinction and both connections to \(a,b\). Including
  \(B\) or \(C\) adds its loose distinction, its connection to \(a\) or
  \(b\), and a crossing on its path through \(d\) to the exterior. Thus
  any of these inclusions gives at least seven crossings. With all three
  outside, including \(d\) or \(r\) also gives at least seven. For a bond,
  the ordinary side is connected, which leaves just \(X\).
- If just \(a\) is inside, count both loose outputs of \(X\), \(Xb\), a
  loose output of \(a\), and one crossing each from \(a\) through \(w\)
  and \(B\) to the exterior. These are six distinct crossings. A second
  loose output at \(a\) would add one. Including either \(w\) or \(B\)
  would also add one, on \(wb\) or on the path from \(B\) through \(d\),
  respectively. Including \(C\) or \(d\) would add a loose distinction,
  and including \(r\) with \(w\) outside would add \(rw\). For size at
  most six, connectivity therefore leaves just \(X,a\). Interchanging
  \(a,b\) and \(B,C\) covers the case with just \(b\) inside.
- If both \(a,b\) are inside, count the loose distinctions at \(X,a,b\)
  and the three distinct crossings on paths from these junctions through
  \(w,B,C\) to the exterior. There are at least seven crossings.

Consequently \(N_4(f)=S_X\setminus\{f\}\) and \(|N_6(g)|=3+3(e_a+e_b)\).
The same counts hold with \(f,g\) interchanged.

For \(j\in\{w,B,C\}\), the only possible bond of size at most four through
\(l_j\) is \(S_j\). A connected two-junction side through the holder has
size at least six, by the arities of \(j\) and its neighbors. If the side
contains at least three junctions, its latest three supply at least six
fresh distinctions, at most two of which can be used internally, by simple
bipartiteness. If \(j\) is among them, its third output raises the bound
to five. Otherwise \(l_j\) itself is an additional crossing. Thus \(N_4(l_j)\)
is empty at a non-unary \(j\), and equals \(S_j\setminus\{l_j\}\) at a
unary \(j\).

If an isometry sends \(f\) to \(l_j\), then \(j\) must be unary and the
isometry must send \(S_X\) onto \(S_j\). Let \(h_1,h_2\) be the two children
of \(j\) among \(a,b,d\). The image of \(g\) has three possibilities.

- At \(rj\), the stars of \(j,r\) and the adjacent sums with any four-place
  \(h_i\) give at least \(3+(|S_r|-1)+3(e_{h_1}+e_{h_2})\) neighbors in
  \(N_6\). The new contributions are disjoint because \(r,h_1,h_2\) have
  the same color. The bound exceeds \(|N_6(g)|\), since the pair
  \(h_1,h_2\) differs from \(a,b\) in at most one place and \(|S_r|-1\ge4\).
- At a distinction shared with a four-place \(h_i\), the two stars give
  at least six neighbors in \(N_4\), whereas \(|N_4(g)|=3\).
- At a distinction shared with a five-place \(h_i\), the two stars give
  seven neighbors in \(N_6\). This suffices if \(|N_6(g)|\le6\). If
  \(|N_6(g)|=9\), both \(a,b\) have arity four, so \(h_i=d\) and the
  other child has arity four. The adjacent sum with that other child
  gives three more neighbors in \(N_6\), for at least ten.

Each possible image is ruled out by \(D\le3\) or \(D\le5\), establishing the
claim. The argument uses the specified local joins and arbitrary older
blocks. It concerns the two marked triples in this construction.

## Exact replays

The checker starts from the eight-junction closed block and verifies the
actual operand sets. It enumerates all minimal cuts, compares the full
marked tables and their versions capped above five, and checks that every
generator of the full scalar automorphism group preserves the actual legal
triple menu. The two triples have identical internal pair distances on
each replay. Their complete marked tables differ. [Replay checker](square_exchange.py)

| Older second parents at \(B,C\) | Outputs at \(a,b,d\) | Distinctions | \(D(t,s),D(g,s)\) | Entries changed by the named exchange |
|---|---:|---:|---:|---:|
| Neither | 2, 2, 2 | 35 | 5, 7 | 124 |
| \(C\) only | 2, 2, 2 | 36 | 5, 7 | 120 |
| Both | 2, 2, 2 | 37 | 5, 8 | 116 |
| Both | 3, 3, 3 | 40 | 5, 9 | 126 |
