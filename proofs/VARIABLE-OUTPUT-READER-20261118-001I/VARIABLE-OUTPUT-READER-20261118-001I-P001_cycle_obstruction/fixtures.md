# The four-place cycle and its false six-distinction support

On these six fixtures, the table through \(K=5\) determines every junction
support against every reachable rival. All five fixtures with legal
triples have a reachable opposing witness through \(K=4\), so five is
the smallest sufficient cutoff for their triple verdicts. The particular
false support \(W\) is excluded one cutoff earlier. [Exact certificates](fixtures.json) · [Checker](fixtures.py)

## The named seven-junction fixture

| Junction | Parity support |
|---|---|
| Seed | 0, 1, 2 |
| \(t\) | 0, 3, 4, 5 |
| \(p\) | 3, 6, 7, 8 |
| \(q\) | 4, 9, 10, 11 |
| \(w\) | 6, 9, 12, 13 |
| \(b\) | 7, 10, 14, 15, 16 |
| \(c\) | 5, 12, 17, 18, 19 |

These supports replay in the displayed order. The four-place junctions
\(t,p,w,q\) form the ordinary cycle. The proposed
\(W=\{3,5,7,9,10,12\}\) has four pair entries at \(K=4\), two at
\(K=5\), and nine at \(K=6\). Thus the fifteen pair bounds within \(W\)
admit it as a proposed six-bond. The physical equation space excludes
it. [Original construction](../../VARIABLE-OUTPUT-READER-20261118-001H/VARIABLE-OUTPUT-READER-20261118-001H-P001_high_junctions/high_inverse.md#a-binary-exception-whose-two-parents-started-at-the-same-high-site)

The observed entries through four force the supports \(T,Q\) at \(t,q\).
Adjoining \(W\) would force
\(W\mathbin{\triangle}T\mathbin{\triangle}Q=\{0,7,11,12\}\), a
four-distinction equation. Every four-distinction equation of a reachable
presentation is a bond, since its proper decomposition would need two
nonzero equations of at least three distinctions apiece. It would give
\(K(7,12)\le4\) where the actual value is six. The contradiction uses
the table through four. Adding just the forced support at \(p\) to \(W\)
also gives a six-distinction word through 8 and 10, whose actual minimum
is seven. The complete hypothetical parity extension by \(W\) adds
equations of weight at least four, first changes the table at four, and
changes 61 entries in the full table. This augmentation is a comparison
of linear spaces.

## Reachable alternatives and a live continuation

Each of the 62 legal one-junction extensions of the seven-junction
fixture has an empty triple menu. A two-junction continuation first joins
\(p,c\) at \(u\), then \(u,b\) at \(v\). It has a legal triple at
\(q,c,v\), with \(t\) or \(w\), \(b\), and \(u\) witnessing the three
pairs and no universal witness. This works for either fresh count at
either addition. The mirrored version joins \(q,c\) at \(r\), then
\(r,b\) at \(y\), with three fresh distinctions each. Its legal triple
\(\{8,18,23\}\) has holders \(p,c,y\).

On the width-26 mirrored version the permutation \((5\ 8)(10\ 13)\)
preserves the entire table through \(K=3\). It carries \(W\) to the
genuine bond \(S_p\mathbin{\triangle}S_w\) and sends the legal triple
\(\{8,18,23\}\) to the forbidden \(\{5,18,23\}\), since 5 is shared.
Rebuilding the renamed history confirms these verdicts on the fixed
names. The map moves \(K(0,5)=4\) to \(K(0,8)=6\), so it fails at four.
The four-distinction translation of \(W\) is still forbidden by that
cutoff after the continuation. Thus \(K=4\) is sharp for excluding \(W\)
in both the base and the mirrored live fixture.

The separate permutation \((7\ 8)\) on the mirrored version passes
through \(K=4\) and changes the same legal triple into \(\{7,18,23\}\),
which uses the shared distinction 7. Here \(K(7,10)=5\) moves to
\(K(8,10)=7\). On the four unmirrored continuations, \((10\ 11)\)
preserves every entry through four and moves the loose distinction 11
to shared distinction 10 in the marked triple. On the base fixture
there is also a change of equation space through four. Its physical
triple menu is empty.

## Why the table through five excludes every reachable rival

The deduction uses only the named table at the stated cutoff. A bond of
size \(k\) has all its pair minima at most \(k\). For each observed
pair minimum, list the candidate bonds of exactly its size. Reject a
candidate containing a proper known word, or giving a forbidden short
word when added to a known equation. A sole surviving candidate at a
pair must occur in every rival. Span closure and iteration give the
forced subspace. Through five, every short equation has size at least
three and every such short nonzero equation is minimal. For the separate
six-cutoff check, a six-word can also split into two disjoint ternary
bonds, which are kept as allowable words.

For each fixture the iteration through five forces the whole original
equation space and leaves zero additional possible bonds of size at most
five. Every ordinary rival star that small must be in this pool. The
unique ternary support is the seed, so the five-word
\(\{1,2,3,4,5\}\) cannot be another ordinary star. It shares two
distinctions with the seed. The remaining pool is a basis. These
properties are checked independently of the original history input.

The only possible further rival site has arity six. Before its first
appearance the rival grows using just the recovered pool. The prefix
search starts at the unique seed and adds a support exactly when its old
distinctions are used once, its fresh count is legal, and all parent
conditions hold. The current supports determine the incidence and the
loose distinctions. Thus deduplicating sets of supports retains all
possible next steps. A first six-place junction needs three unused
names and an available legal triple. None of the reached prefix sets
has both. Every rival therefore uses only the recovered pool. It must
use the whole basis to contain the already forced space.

| Fixture | Width | Legal triples | Low-site prefix sets | Prefixes admitting a first six-place site |
|---|---:|---:|---:|---:|
| Base | 20 | 0 | 14 | 0 |
| Two fresh, then two | 24 | 4 | 47 | 0 |
| Two fresh, then three | 25 | 6 | 31 | 0 |
| Three fresh, then two | 25 | 4 | 27 | 0 |
| Three fresh twice | 26 | 6 | 18 | 0 |
| Mirrored three fresh twice | 26 | 6 | 18 | 0 |

The five-cutoff certificate repeats with all larger entries erased and
with a seeded renaming of each fixture. Direct checking of allowed
parity equations and wired cuts agrees on every measured physical pair.
An additional residual-space test through six leaves only the physical
code for each of the six tables. The cutoff-five conclusion concerns
these tables and their renamings. [Short-word inference predecessor](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/check_scalar_span.py)
