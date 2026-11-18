# Omitting the planted six-distinction junction changes bond distance

The two histories below use the same 27 distinctions. The second skips
\(v\). In each row, the displayed distinctions support one even-parity
equation. The scalar comparison uses the displayed identities.

| Junction | Support |
|---|---|
| Seed | 0, 1, 2 |
| \(A\) | 0, 3, 4, 5 |
| \(B\) | 1, 6, 7, 8 |
| \(C\) | 2, 9, 10, 11 |
| \(P_{AB}\) | 3, 6, 12, 13 |
| \(P_{AC}\) | 4, 9, 14, 15 |
| \(P_{BC}\) | 7, 10, 16, 17 |
| \(v\) | 12, 14, 16, 18, 19, 20 |
| \(G_A\) | 5, 18, 21, 22 |
| \(G_B\) | 8, 19, 23, 24 |
| \(G_C\) | 11, 20, 25, 26 |

The first three joins each take a distinction from the seed. The next
three use two parents with the seed as their common neighbor. The three
parents of \(v\) have \(A,B,C\) as their three pairwise witnesses and have
no common neighbor. Each \(G_i\) in the history with \(v\) uses \(i\) and
\(v\), with an already present \(P_{ij}\) as their common neighbor. In
the history without \(v\), each \(G_i\) uses one parent and introduces
its distinction from \(\{18,19,20\}\) as a third fresh distinction.

Initially \(\{12,15,17\}\) is a legal triple without \(v\). Its three
parents are the \(P_{ij}\). With \(v\), distinction 12 is shared, and
the three \(P_{ij}\) have \(v\) as a common neighbor. This gives opposite
verdicts on the proposed triple.

## The bond distance through 18 and 19

Take any finite legal continuation of the history without \(v\) that keeps
all of \(S=\{12,14,16,18,19,20\}\) loose. The bond distance through 18
and 19 is at least 6. Inserting the equation on \(S\) into that same
presentation gives bond distance at most 5 through 18 and 19.

Use an auxiliary graph with one node per junction and an additional node
\(o\). A shared distinction connects its two holders. A loose distinction
connects its holder to \(o\). The sum over \(\mathbb F_2\) of the equations
at any set \(U\) of junctions has support \(\partial U\), the distinctions
with exactly one holder in \(U\) in this graph. All valid parity equations
are linear combinations of the junction equations, so every bond is such
a support.

If \(\partial U\) contains 18 and 19 without \(v\), the loose distinctions
18 and 19 put both \(G_A\) and \(G_B\) in \(U\). Four paths to \(o\) then
give four distinct crossings of \(\partial U\). Their distinction lists are
\((18)\), \((19)\), \((5,4,14)\), and \((8,7,16)\). These paths persist
throughout the continuation because their shared distinctions remain shared
and their final distinctions belong to \(S\).

- If \(U\) contains at least two later junctions, consider the last two in
  growth order. Their at least four fresh distinctions cannot be shared with
  any earlier junction. At most one can be shared between the two, because a
  join takes at most one distinction per parent. At least three of their fresh
  distinctions therefore cross \(\partial U\), in addition to the four
  crossings from the listed paths.
- If \(U\) contains exactly one later junction, it can consume at most one
  of \(21,22\) and at most one of \(23,24\). Hence at least two of those
  four old distinctions cross \(\partial U\). Both or all three of the
  later junction's fresh distinctions also cross. If \(U\) contains no later
  junctions, all four old distinctions cross. In both cases the extra
  crossings are distinct from the four contributed by the listed paths.

Thus every bond through 18 and 19 has size at least seven. With the equation
on \(S\) inserted, \(S\) is the support of the equation at \(v\). Removing
\(v\) from the auxiliary graph leaves a connected graph. The remaining
junctions are connected by their parent joins, and \(o\) still attaches
through a loose distinction outside \(S\). Such a distinction exists in the
displayed prefix, or among the fresh distinctions of the last continuation
join if there is one. A cut supported inside \(S\) must assign the same
membership in \(U\) to every node of this connected graph. Since \(o\) lies
outside \(U\), the only nonempty such support is the whole of \(S\). It
is therefore a bond of size six.

The two initial histories replay legally. Enumerating their parity equation
sums gives exact bond distances \(10\) without \(v\) and \(5\) with \(v\)
for the pair \(\{18,19\}\). The replay and enumeration use the
[predecessor's checker](../../VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/check_gluing.py).

The argument above rules out equality under the displayed correspondence
even after an arbitrary legal continuation that keeps \(S\) loose on the
side without \(v\). Arbitrary renamings of the completed scalar tables are
outside this comparison.
