# The member-free pumping argument, with exact interfaces

This is the referee's reconstruction, not an edit of the frozen proof. It
concerns finite minimal non-shattered sets in the usual-limit solution set,
and only covered own targets in S copies reached through S calls. No
conditional rectangularity is used.

## 1. Assign a member once

Let the target's S word have length n and its copies be c_0,...,c_n.
Absolute depth is d=n+delta, where delta=0 for main=S and delta=1 for
the census wrapper convention. Assign every distinction to the invocation
that first allocates it. For each i<n, collect allocations in c_i's own
block and in all side subtrees of c_i off the chosen word. These collections
are disjoint. A member of W occupies level i only if its allocation belongs
to that collection. Main ports, and allocations in the wrapper outside the
chosen S subtree, belong to an upper remainder.

An identity passed as a port can occur in many blocks but occupies only its
one allocating collection, if any. This qualification is necessary. The
literal occurrence reading of "a member in the block" invalidates the
counting step. `pumping_results.json` contains a living synthetic family with
a 3-bond at depth 20, a carried member appearing at every level, and m=2;
the literal no-long-stretch inference would incorrectly demand more than
five members. The allocation reading repairs that inference.

## 2. Which product is being replaced

Suppose the unoccupied source blocks are c_l,...,c_r, with r<n. Their
top interface is the port tuple of c_l and their bottom interface is the
port tuple of c_{r+1}. The product must include exactly the per-call factors
for c_l -> c_{l+1},...,c_r -> c_{r+1}.

In the original notation, unoccupied levels a+1,...,b therefore require the
product over source blocks c_{a+1},...,c_b, with interfaces c_{a+1} and
c_{b+1}. The product from c_a to c_b instead covers c_a,...,c_{b-1}.
It can eliminate a selected own distinction in c_a and omits c_b. Merely
changing the list of blocks without moving the bottom interface is not
enough. A member of c_a's own block remains in the unchanged upper context
under the corrected cut.

For a per-call factor, impose the source block's constraints and the exact
usual-limit port relation of every side call. Leave the selected continuation
open. This produces a relation on the source and selected child's port
values. Composition existentially quantifies the intermediate port tuples.
At the final bottom interface attach the full usual-limit subtree. This is
an exact factorisation: each invocation interacts with its context solely
through its ports, and hidden side subtrees have exactly the declared
usual-limit extensions. An inherited selected identity that appears in a
side subtree is an interface identity, not an allocation to be forgotten.

More explicitly, divide W into U allocated above/off the replaced interval
and D allocated in the retained lower subtree. There are no selected
allocations in the replaced interval. If A(u,alpha) is the upper context
projection, M(alpha,beta) is this product, and B(beta,v) is the lower
subtree projection, the selected relation is

    {(u,v) : exists alpha,beta,
              A(u,alpha) and M(alpha,beta) and B(beta,v)}.

Here alpha and beta are positional proxy tuples. If a position holds a
selected free identity, its proxy is constrained equal to that free
coordinate; the selected identity itself is never existentially removed.
All interfaces are interpreted with their actual identity identifications.
A selected identity allocated above but used below must be passed through
the top interface. Track the carry map for **every** top port, including
ports containing an ancestor's own identity, rather than only main ports.
An unchanged carry map preserves exactly which lower ports are those upper
identities. A member whose allocation is inside a side subtree of a stretch
copy would occupy that level, so it cannot be silently hidden in this case.

The census has distinct arguments in every raw call, independently checked
on all 5,964 study keys. Consequently each copy's ports are distinct and
the carry map is a partial injection. For a language allowing repeated call
arguments, a full canonical input/output identity partition is a safe
enlargement of the state. Nothing in this audit extends the advertised
constant m to a larger language without counting that enlarged state.

## 3. Pumping preserves a bond, not just non-shattering

The finite state is (R,C). R is the 8-by-8 Boolean truth table on ordered
source/end port tuples. C(j)=i when end port j is literally source port i,
and is undefined when its identity was freshly allocated. With injective
calls, distinct undefined end positions have distinct fresh identities.
The initial state is (identity relation, identity map). Concatenation uses
Boolean relational composition for R and partial-map composition for C:
C_uv(j)=C_u(C_v(j)) when both entries are defined, and is undefined otherwise.
This is a finite associative state algebra whose equality has the contextual
substitutability proved above. There are at most 34 partial injections and
2^32 complement-closed Boolean relations, so enumeration has an explicit
finite universe bound 34*2^32 for these ternary, injective calls.

The empty word counts. Let m be the number of reachable states. Within more
than m consecutive unoccupied source blocks, inspect the first m+1 prefix
states, including the empty prefix. Two agree, after i<j<=m factors. Put
ell=j-i, and write the interval word as t_1 y t_3, where |y|=ell.

Equality of the prefix states says state(t_1 y)=state(t_1). Associativity
and the identity-map composition give state(t_1 y^k)=state(t_1) for every
k>=0. Hence the entire interval state is unchanged. With Pi=m!, add
Pi/ell copies of y: the target's S word length increases by exactly Pi.

Keep upper allocations fixed and rename all allocations of the retained
lower subtree to its corresponding new invocation. This is injective on
selected identities. Carry equality preserves overlap with upper selected
ports, including non-main carried identities. The target remains an own
distinction of a copy of S reached through S calls, at absolute depth d+Pi;
delta stays fixed. Members below the target and in lower side subtrees move
with the same lower subtree. Members of c_{l-1}'s block and its side
subtrees stay fixed.

The displayed factorisation then gives equality of the **entire selected
relation**, under this bijection. Projecting that equality onto each subset
of W gives equal projections on every subset. Non-shattering and
shattering of all proper subsets are therefore both preserved. The moved
set is a bond of the same size. Repeating the same replacement gives
L(d+k Pi)<=|W| for every k>=0.

The finite controls independently compare all subset projections of a
3-member support under a true factorial-period pump and a 4-member support
with a non-main carried identity and an upper side-subtree member. Those
are controls for the factorisation, not replacements for this symbolic
argument.

## 4. Counting and residues

If no empty run has more than m of the n pre-target allocation collections,
and t are occupied, then

    n <= (m+1)t + m.

The root member p and target-own member x are distinct and are outside
these t collections, so t<=|W|-2. Thus

    |W| >= (n-m)/(m+1) + 2.

For delta<=1 this is stronger than the claimed
|W|>=d/(m+1)-1. In particular the wrapper offset does not spoil the stated
weak bound. One can instead keep all estimates in n and explicitly
substitute n=d-delta.

On a fixed residue modulo Pi, the existence of **any** long-gap bond W at
d_0 gives the eventual bound L(d)<=|W| for all later depths in that residue.
If no such bond exists, apply the counting estimate to each least finite
bond, giving the lower bound at every depth in that residue. If no bond
exists at a depth, set L(d)=+infinity and the lower bound is automatic.
The argument does not need a minimum where L is infinite.

This rules out an unbounded sublinear sequence within one residue. A family
with sqrt(d) or logarithmically many members at increasingly sparse allocated
levels eventually contains a long gap. The very first such witness fixes
a constant bound for that residue at all later depths, contradicting
unbounded growth of the minimum. Increasing gaps along different words,
placing members in side subtrees, or hiding ancestor-owned carried members
does not evade the same argument. Finite-state clocks can create large
fixed gaps, but those yield a small positive linear rate, not an unbounded
sublinear asymptotic minimum.

## 5. Explicit thresholds and what is effective

The monoid is effectively enumerable. Thus m, Pi=m!, and 1/(m+1) are
computable, even when impractically large. A certificate consisting of W,
its exact projection, its target depth d_0, and a repeated state in an
empty interval has explicit eventual threshold d_0 and bound C=|W|.

A sufficient numerical trigger is

    |W| < d_0/(m+1)-1,

or d_0>(m+1)(|W|+1). It forces a long gap by the stronger allocation count.
For a desired residue r, the first integer in it above that numerical
threshold is

    r + Pi * ceil(((m+1)(C+1)+1-r)/Pi),

with the obvious nonnegative adjustment. This expression guarantees the
trigger only if a bond of size at most C exists at that depth. It does not
manufacture such a bond or supply an unknown boundedness onset.

For example, the synthetic read-carried family in the controls has m=2,
Pi=2 and L(d)<=3 at every depth. Depths 13 and 14 supply sufficient
numerical seeds for the two residues, each with eventual bound 3. Direct
long-gap seeds are available earlier; these numbers are transparent
sufficient thresholds, not claimed optimal ones.

Given any finite candidate support, its exact solution projection is
decidable by unfolding its finite address tree and replacing untouched
subtrees by their computable usual-limit port relations. Enumerating
candidate long-gap bonds therefore semi-decides boundedness on a residue.
If that residue is eventually bounded, a sufficiently large bounded witness
must have a long gap, so this search eventually succeeds. In contrast,
the proof offers no finite certificate that **no** such witness exists.
It supplies no decision procedure for boundedness and no finite growth test;
this is a limitation of the proof, not an undecidability theorem. It also
does not establish ultimate periodicity of L's values or exact affine
growth. The frozen claim that a finite local state decides the branch is
not recovered by this argument.

## 6. Comparison with remembered standard mathematics

The comparisons here are from memory and unverified: there is no network
use or literature admission. Repeating prefix elements of a finite monoid
is standard pumping. The work specific to this application is the exact
finite-support factorisation with identity sharing and arbitrary side
subtrees, plus the allocation count for minimal non-shattered sets.

The classical cyclicity results for tropical/min-plus powers supply
eventually affine periodic behavior under their respective matrix
hypotheses, especially in the irreducible case. This proof has not encoded
minimal non-shattering, arbitrary support placement, and minimisation over
targets as the entries of a fixed min-plus matrix. Such a theorem cannot
be applied merely because a finite monoid occurs. The conclusion here is
weaker than ultimate affine periodicity.

For a concrete contrast with max-over-words questions in distance automata,
write a word as a^{n_1} b ... b a^{n_k}, with every n_i>=1, and let

    f(word) = min(k, min_i n_i).

A finite automaton with costs 0 and 1 can realise this by choosing either
to count blocks or to count the letters of one chosen complete block.
Among words of length N, the maximum is the greatest t satisfying
t^2+t-1<=N, since f>=t requires at least t blocks each of length at least
t. Balanced words achieve it, giving sqrt(N) growth. This example is
derived here; no bibliographic attribution is asserted. By contrast the
minimum over words is 1 (choose a single block). READ minimises over
covered target words and supports: one pumped cheap witness bounds that
residue of the minimum. A max-over-words assertion could continue to
choose more expensive words and would not follow from this argument.
