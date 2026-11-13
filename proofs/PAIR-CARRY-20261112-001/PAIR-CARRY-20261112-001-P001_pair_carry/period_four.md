# A bond using one marker per four levels

**Standard statement.** In precisely `sample_0.jsonl.gz`, line 4710, a
finite bond containing a top port and an own distinction at first-child
depth `s` exists at every positive depth. There is a three-member bond at
depth one, and a bond of size `ceil(s/4) + 3` at every `s >= 2`. These are
upper bounds on the unrestricted minimum. All selected distinctions are raw
variables of the given rule; no additional restriction or source is supplied.

**Nearest known result.** The accepted `TWO-LEVEL-BOND-20261112-001`
calculation finds marginal NAE triples but rejects every two-level link
depending on only one selected input bit. The construction here retains two
consecutive `x` values and has an exact finite relation invariant. It makes no
uniform lifting claim from a single input bit. The accepted
`BRANCH-DEPTH-20261112-001A,C` lower bound `1 + ceil(s/6)` remains distinct
from this upper construction. No optimality or finite-flip source claim is
made here.

## 1. The exact rule and its unobserved calls

For a call with ports `(a,b,c)` and own distinctions `(x,y)`, the local rules
are

```text
NAE(y,x,b), NAE(b,x,c), NAE(c,y,b),
```

and the children, in order, receive `(x,a,y)`, `(c,b,y)`, and `(y,c,b)`.
All eight port triples have infinite extensions. For example, setting
`x=y=1-b` satisfies all three local rules for any ports. Repeating this
choice separately in all calls constructs an infinite state; the fresh own
distinctions of separate calls share only their declared ports. Thus every
unopened call has the full port relation. There is no child passing all
three original ports through, so no pass-through correction applies.

Along the first-child branch write

```text
x[-2]=b, x[-1]=a, y[-1]=c,
```

with own distinctions `x[i],y[i]` at level `i >= 0`. The input tuple at
level `i` is `(x[i-1],x[i-2],y[i-1])`. The three local rules are exactly

```text
x[i-2] = NOT majority(x[i],y[i],y[i-1]).                 (1)
```

Indeed, they forbid each pair of the three arguments of `majority` from
both equalling `x[i-2]`. For Boolean values this means at least two of
those arguments equal its complement. This equivalence can also be checked
on all 32 local words, leaving 16 words because `x[i-1]` is free locally.

Consequently, an assignment to any finite first-child prefix extends to
the whole infinite system exactly when it satisfies (1) in that prefix.
Every side call and the final unopened first child can then be extended
from its port tuple. This is the exact projection justification, including
the infinite portions beyond the last selected distinction.

## 2. An exact finite relation invariant

After level `i`, the outgoing tuple is `(x[i],x[i-1],y[i])`. Encode a
tuple `(u,v,w)` by `q=u+2v+4w`, and a set of tuples by the integer mask
`sum(2^q)`. A free step means existentially choosing the next fresh `x,y`
subject to (1). A marked step also prescribes that step's `y` value.
These operations are relational images; they impose no rule beyond (1).

Start either just before level zero (`j=-1`) or just after level zero
(`j=0`). Prescribe the consecutive pair

```text
previous=x[j-1], current=x[j].
```

The exact outgoing tuple set is

```text
{(current,previous,0), (current,previous,1)}.             (2)
```

For `j=-1`, this follows from the free top triple `(a,b,c)`. For `j=0`,
selecting `a,x[0]` leaves `y[0]` free: for each desired `y[0]`, choose
`c` arbitrarily and set the unselected `b` by (1). The unselected root
distinctions are quantified, rather than fixed externally.

Take one free step and then mark `y[j+2]`. The complete table is:

| previous | current | marker 0 | marker 1 |
|---:|---:|---:|---:|
| 0 | 0 | 10 | 240 |
| 0 | 1 | 13 | 64 |
| 1 | 0 | 2 | 176 |
| 1 | 1 | 15 | 80 |

Subsequent markers are four levels apart. Three free steps followed by
one marked step have the following complete table on the eight reachable
sets:

| Incoming mask | Next marker 0 | Next marker 1 |
|---:|---:|---:|
| 2 | 2 | 176 |
| 64 | 13 | 64 |
| 10 | 15 | 240 |
| 13 | 15 | 240 |
| 15 | 15 | 240 |
| 80 | 15 | 240 |
| 176 | 15 | 240 |
| 240 | 15 | 240 |

Both tables follow by listing the allowed `(x,y)` pairs in (1); they
are also exhaustively recomputed by `marked_support.py`. They supply a
finite induction for every marker word, rather than testing some periodic
words and inferring the rest.

Let `C_0=2`, the singleton `(1,0,0)`, and `C_1=64`, the singleton
`(0,1,1)`. Let

```text
D = {10,13,15,80,176,240}.
```

After any nonempty string of these markers, the exact tuple set is `C_v`
if and only if

```text
previous=1-v, current=v, and every marker equals v.     (3)
```

For every other initial pair and marker word, the exact tuple set lies
in `D`. The first table establishes this equivalence at the first marker;
the second table preserves `C_v` exactly for the matching value, sends a
first mismatch to `D`, and keeps every member of `D` inside `D`. No marker
word is omitted from this dichotomy.

## 3. Terminal partial periods

After the final marker, the following table gives the exact indicated
projection. The pair in its final column is ordered `(x,y)` at the terminal
level.

| Mask after final marker | One free step: terminal `x` | Two free steps: terminal `x` | Three free steps: terminal `(x,y)` |
|---|---|---|---|
| `C_0` | `{1}` | `{0}` | `{00,10,01}` |
| `C_1` | `{0}` | `{1}` | `{10,01,11}` |
| Any member of `D` | `{0,1}` | `{0,1}` | `{00,10,01,11}` |

Thus (3) forces terminal `x=1-v` after one step, forces `x=v` after
two steps, and forbids precisely terminal `(x,y)=(1-v,1-v)` after three
steps. Every nonmatching word leaves the indicated terminal observations
entirely free. This checks the partial periods as exact relations, including
all correlations between the two observations in the third column.

## 4. The support at every positive depth

For each `m >= 1` use these raw distinctions:

| Target depth | Ordered support | Size |
|---|---|---:|
| `s=4m-2` | `b,a,y[1],y[5],...,y[4m-3],x[s]` | `m+3` |
| `s=4m-1` | `a,x[0],y[2],y[6],...,y[4m-2],x[s]` | `m+3` |
| `s=4m` | `a,x[0],y[2],y[6],...,y[4m-2],x[s]` | `m+3` |
| `s=4m+1` | `a,x[0],y[2],y[6],...,y[4m-2],x[s],y[s]` | `m+4` |

The first row uses `j=-1` and the one-step terminal observation. The next
three use `j=0` and respectively one, two, and three terminal steps. Every
support has distinct identities, a top port, and an own distinction at the
stated target depth. The two root ports in the first row are both charged.
Depth one is handled separately by `{a,x[1],y[1]}`: its exact projection
is NAE. The local NAE rule at level one gives soundness. Conversely, for
any NAE assignment to `(a,x[1],y[1])`, choose `y[0]` to satisfy
`a = NOT majority(x[1],y[1],y[0])`; NAE is exactly the condition that such
a value exists. Choose `x[0],c` freely and set
`b = NOT majority(x[0],y[0],c)`. Both copies satisfy (1), establishing
completeness without any fixed spectator ports.

For the uniform rows, write the ordered support as `(previous,current,
markers...,terminal observations)`. Its exact projection excludes only
the following assignments, for `v=0,1`:

| Terminal step count | The excluded assignments |
|---:|---|
| 1 | `(1-v,v,v,...,v,v)` |
| 2 | `(1-v,v,v,...,v,1-v)` |
| 3 | `(1-v,v,v,...,v,1-v,1-v)` |

The initial pair and all markers satisfy (3); the terminal values are
precisely those forbidden by the terminal table. Every other support word
is realized by the exact relational images above, and then by an infinite
state by Section 1. The two excluded assignments are complementary.

## 5. Every erasure leaves all remaining distinctions simultaneously free

Let a displayed support have size `n`. Its projection is the full Boolean
relation minus two complementary assignments. Therefore it is constrained
(K1) and nonempty (K3). After deleting any one distinction, prescribe all
`n-1` remaining bits simultaneously. Its two extensions differ only in the
deleted bit. They cannot both be the excluded assignments, which differ
in every bit and have `n >= 3`. At least one extension is allowed and,
by exactness, extends to the whole infinite system. This proves K2 for
each deletion and for arbitrary values of all the remaining bits at once.
The special NAE support at depth one has the same two-complementary-word
description. Thus every displayed support is a finite bond in the required
allowed-state sense.

The uniform sizes equal `ceil(s/4)+3` for `s >= 2`; depth one costs three.
This improves the explicit upper coefficient to `1/4`. It proves neither
the sharpness of that coefficient nor an exact minimum among ray supports
or unrestricted supports.

## 6. Executable discrimination

`marked_support.py` reads only the specified source record and writes no
artifacts. It independently computes the unmarked greatest fixed point,
checks the local majority equivalence on every word, recomputes every entry
of the two finite tables and terminal table, and checks both root bases.
It then uses SAT on the raw positive NAE clauses to compute the complete
projection for every displayed support through the requested depth. It
checks the two excluded assignments, nonemptiness, and every full
single-erasure projection. The default range is depths 1 through 32.

Two matched controls can fail the claimed interface: deleting
`NAE(b,x,y)` from every copy makes the proposed depth-four support entirely
free; adding the unselected top distinction `c` to the valid depth-four support
leaves a constrained proper part and fails K2. The real `knotlab check`
interface accepts the computed depth-four relation and rejects the latter
spectator control. These are finite checks supporting the uniform finite
relation induction; the finite range is not the proof of uniformity.

The default replay passed all 32 depths: 16,312 raw-CNF assignment queries,
the complete simultaneous erasure projections of all supports, all finite
table entries, both matched controls, and both canonical-interface verdicts.

This is a source-zero construction and separate-algorithm validation in the
same task (V1). External novelty is unassessed. No physical structure,
finite-flip source verdict, or claim about other source records follows.
