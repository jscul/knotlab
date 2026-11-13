# Shared helpers for the additive counting rule

**Standard statement.** Start with an arbitrary generation of $m\ge2$
binary main distinctions and one open reference distinction $R$. Each new
generation has one more position. The required relation is

\[
 y_i=x_{i-1}\mathbin\oplus x_i\mathbin\oplus R,
 \qquad x_{-1}=x_m=R.
\]

Can a uniform positive, strict, three-place not-all-equal (NAE) rule express
this relation, with two further distinctions per position available to nearby
positions, including iteration and both ends?

**Nearest known result.** The terminal CHEAP-COUNT referee verifies the exact
private-helper parity gadgets: three helpers require twelve NAE constraints;
four helpers allow ten, and fewer than three helpers cannot define the
four-place even-parity relation. Its observation that this does not exclude
shared helpers is the present target. ROW-NEST and TWO-BIT-ROWS do not supply
an exact additive transition. Their finite null results concern their own
rule classes, end protocols, and tested depths.

**Attained result and status: Partial.** Three distinctions per position
**suffice if a second broadcast reference identity is allowed**. That identity
can be an already counted initial helper, so the complete inventory is
exactly three distinctions per position plus $R$. The construction has an
exact projected relation at every width and depth and reproduces the actual
CHEAP-COUNT rule-60 closing protocol. Its depth predicate is not eventually
periodic; an exact description is proved below.

The extra access matters: a rule at every position reads that particular
initial helper. This is not a solution in the original slot alphabet if only
$R$ may be read globally. For that stricter question, the checker gives
direct countermodels for all 784 deterministic adjacent-pair encodings and
all 256 encodings with one local complementary-reference helper and one
arbitrary three-main helper, in the precisely stated local class below.
Period-dependent, longer-support, and nondeterministic encodings remain open.

## 1. Supplied system and the two access contracts

There is a linear order of positions in each generation and a supplied
successor-generation arrangement. These are the same external indexing
conventions as CHEAP-COUNT; this result does not derive native paths or
composed topology from them. NAE is read as a constraint on joint states,
without an executor choosing an input. All initial main values and $R$ are
free before the terminal closing constraints are imposed.

The positive construction uses main $x_i$ and helpers $h_i,k_i$. In
reference-relative notation, its intended meaning is

\[
 \bar x_i=x_i\oplus R,\qquad
 h_i=R\oplus\operatorname{NOR}(\bar x_{i-1},\bar x_i),\qquad
 k_i=R\oplus\operatorname{NAND}(\bar x_{i-1},\bar x_i),
 \quad \bar x_{-1}=0.
\]

Here NOR and NAND are the ordinary Boolean functions. Write $S$ for the
first initial position's $k_0$, **the same variable identity**, rather than
a fresh copy. The initial constraints force $S=1-R$. Both $R$ and $S$
are read in the fixed templates throughout the construction.

Thus the distinction budget and the permitted access are different claims:

| Contract | Inventory | Extra access |
| --- | --- | --- |
| Constructed here | Three distinctions per position, plus $R$ | Both $R$ and the initial helper $S$ are broadcast |
| Original stricter target | Three distinctions per position, plus $R$ | Only $R$ is broadcast; helpers have bounded neighbouring access |

The second row is not established. No count of variables turns the first
row's long access into neighbouring access.

For comparison, a separately allocated $S$ can be forced opposite to $R$
with three further distinctions $a,b,c$ and

\[
 \operatorname{NAE}(R,S,a),\quad \operatorname{NAE}(R,S,b),\quad
 \operatorname{NAE}(R,S,c),\quad \operatorname{NAE}(a,b,c).
\]

If $R=S$, the first three force $a=b=c=1-R$, contradicting the last.
If $R\ne S$, any not-all-equal values of $a,b,c$ extend it. This alternative
costs four extra distinctions and still has two broadcast references.

## 2. A five-constraint relation for two helpers

For distinct identities $p,x,h,k,R,S$, allowing $p=R$ by identity at the
left end where no individual triple then repeats an identity, define

\[
\begin{split}
 I(p,x;h,k)={}&\operatorname{NAE}(p,x,h)\ \wedge
 \operatorname{NAE}(p,x,k)\ \wedge
 \operatorname{NAE}(p,h,k)\\
 &\wedge\operatorname{NAE}(x,h,S)\ \wedge
 \operatorname{NAE}(x,k,R).
\end{split}
\]

**Lemma 1.** Assuming $S=1-R$, this defines exactly the intended NOR/NAND
helpers of $p,x$, with a unique extension.

Complementing every value preserves all the constraints, so take $R=0$,
$S=1$. The four cases are

| $p,x$ | $h,k$ |
| --- | --- |
| 00 | 11 |
| 01 | 01 |
| 10 | 01 |
| 11 | 00 |

For 00 and 11, the first two constraints force the two helper values. For
01, the fourth forces $h=0$, then the third forces $k=1$. For 10, the
fifth forces $k=1$, then the third forces $h=0$. These values satisfy all
five constraints. This proves the lemma for both reference values.

## 3. Initial generation: obtaining the second reference without a new variable

Let the first two initial positions be $(a,h_0,S)$ and $(b,h_1,k_1)$.
Impose these nine strict NAE constraints:

\[
\begin{array}{lll}
 (a,h_0,S), &(a,h_0,R), &(a,S,h_1),\\
 (a,b,h_1), &(a,b,k_1), &(a,k_1,R),\\
 (S,b,R), &(S,h_1,R), &(b,h_1,k_1).
\end{array}
\]

Each parenthesized triple means NAE, as below.

**Lemma 2.** These constraints define precisely $S=1-R$,
$h_0=1-a$, and the intended pair of helpers at the second position. Every
assignment of $R,a,b$ has exactly one extension.

Suppose $S=R=0$. The seventh and eighth triples force $b=h_1=1$;
the ninth then forces $k_1=0$; the sixth forces $a=1$. The fourth is now
111, a contradiction. Complementation also excludes $S=R=1$.

For $R=0,S=1$, the first two triples force $h_0=1-a$. The remaining
triples give $(h_1,k_1)=(1,1),(0,1),(0,1),(0,0)$ for
$(a,b)=00,01,10,11$, respectively. Conversely all these assignments satisfy
the nine triples. Complementation completes the proof.

For every later initial position impose $I(x_{i-1},x_i;h_i,k_i)$. Thus the
initial generation is defined for arbitrary width $m\ge2$, with a unique
helper extension and no restriction on its $m$ main values or on $R$.
For $m=3$ there are fourteen initial NAE constraints.

## 4. Uniform interior transition

At new position $i<m$, denote the old main values by
$b=x_{i-1},c=x_i$, the old helpers at $i$ by $f,g$, the preceding new
main by $v=y_{i-1}$, and the new position by $(w,h,k)$. At $i=0$,
substitute $b=v=R$. Use $I(v,w;h,k)$ and these five constraints:

\[
 (b,f,w),\quad(c,f,w),\quad(f,w,S),\quad(g,v,h),\quad(g,k,R).
\]

This is a single ten-constraint template. It reads old positions $i-1,i$,
new positions $i-1,i$, and the two broadcast identities. All its triples
have three distinct identities, including at $i=0$.

**Lemma 3.** If the old helpers have their intended meaning and $S=1-R$,
the template permits exactly

\[
 w=b\oplus c\oplus R,\qquad (w,h,k)
  =\text{the intended encoding of the pair }(v,w).
\]

Again take $R=0,S=1$. Lemma 1 supplies the new helper meaning. For old
$bc=00$, $f=g=1$, and $(f,w,S)$ forces $w=0$. For 01, $f=0$, and
$(b,f,w)$ forces $w=1$. For 10, $(c,f,w)$ does so.

For 11, $f=g=0$. If $w=1,v=0$, the new NOR helper is $h=0$, so
$(g,v,h)$ is 000. If $w=v=1$, the new NAND helper is $k=0$, so
$(g,k,R)$ is 000. Hence $w=0$. In all four correct cases the five update
triples hold for both possible $v$. This proves soundness and completeness.

In particular the proof does not require a guessed life sequence, a special
initial seed, or the previous new helper values. The old helper meaning is
the invariant carried by the whole construction.

## 5. The right end without extra distinctions

There is no old position $m$. Its missing main value is $R$, so the
required last update is $w=x_{m-1}=b$. Let $v=y_{m-1}$, and use

\[
 I(v,w;h,k)\quad\wedge\quad I(v,b;h,k).
\]

The two relations share the triple $(v,h,k)$, giving **nine** distinct NAE
constraints on existing variables. They introduce no copy or witness.
All triples are strict.

**Lemma 4.** This defines exactly $w=b$ and the correct helpers of $v,w$.

For either fixed $v$, the two different values of the second argument in
Lemma 1 give different helper pairs. Therefore its common pair $h,k$
forces $w=b$. Conversely $w=b$ and its intended helpers satisfy both
relations. This includes every possible value of $v,b,R$.

## 6. Exact projection, composition, and complete inventory

**Theorem 1 (two broadcast references, one counted initial helper).** For
every $m\ge2$ and every finite depth $t\ge0$, the unclosed NAE system
projects exactly onto the reference-relative rule-60 histories. Every
assignment of the initial $m$ main distinctions and $R$ extends uniquely
to the entire history and every helper.

Lemma 2 starts the induction with arbitrary initial main values. At each new
generation, proceed through its positions. Lemma 3 forces each nonfinal
main to its required value and provides its uniquely correct helpers; the
preceding new main is already present, with $R$ used at the left end.
Lemma 4 supplies the last position. Conversely these values satisfy all the
constraints. Induction over the generations proves both directions for all
widths and depths. No finite-width test is used as the uniform proof.

Now put NAE on every three consecutive **main** distinctions of the last
generation, exactly as in CHEAP-COUNT. This merely selects those uniquely
determined histories satisfying its terminal condition. It does not close
triples of helper variables or leave out end triples. Its projected initial
relation is therefore exactly the predecessor's relation, for every depth.

For the predecessor's initial width three, the complete distinction count is

\[
 M_t=\sum_{r=0}^{t}(3+r)=\frac{(t+1)(t+6)}2,\qquad
 D_t=3M_t+1.
\]

The $+1$ is the supplied $R$. The broadcast $S$ is already one of the
$2M_t$ helpers. There are no extra reference copies, missing-position
variables, equality gadgets, end witnesses, or uncounted distinctions.

An old generation of width $k$ contributes $10k+8$ **distinct** NAE
constraints: nine at the left position (two of the ten occurrences coincide),
ten at each of the remaining $k-1$ nonfinal new positions, and nine at the
right end. With fourteen initial constraints and $t+1$ terminal triples,
the exact total is

\[
 N_t=5t^2+34t+15.
\]

At depth 64 this is **6,826 distinctions and 22,671 NAE constraints**.
The private-gadget minima do not contradict this count: one output consumes
helpers already constrained by earlier generations and helpers also serving
the next generation. It is not an isolated parity definition with only two
private witnesses.

## 7. The actual closing protocol counts in binary at all depths

This section concerns initial width three. Normalize $R=0$, which is a
complementation argument, not an input supplied by an executor. Write the
initial three main values as the coefficients of
$P(X)=a+bX+cX^2$ over the two-element field. Theorem 1 gives the exact
terminal polynomial

\[
 P_t(X)=(1+X)^tP(X),
\]

read with exactly $t+3$ coefficients, including any zero coefficients at
the ends. The terminal NAE condition means no three consecutive coefficients
are all zero or all one.

**Theorem 2.** For every positive depth $t$, the closed system lives exactly
when $t=1,2$ or

\[
 2^h-5\le t\le2^h-2\quad\text{for some }h\ge3.
\]

Let $n=2^h\ge8$, $V=1+X$. For $t=n-5+r$, $r=0,1,2,3$, take seed
polynomials $1+X^2,1+X,1,1$, respectively. Since

\[
 V^{n-8}=1+X^8+X^{16}+\cdots+X^{n-8},
\]

the terminal polynomial is a succession of identical eight-coefficient
blocks: $V^5=1+X+X^4+X^5$, written 11001100 in increasing coefficient
order, for the first three cases; $V^6=1+X^2+X^4+X^6$, written 10101010,
for the fourth. The first two cases truncate one or two final zero
coefficients; the third uses all $n$ coefficients; the fourth appends one
further zero, ending 100. No case has three equal consecutive coefficients,
including across consecutive blocks or at either end. Hence all four depths
live. Depths 1 and 2 also live, directly, with seed 001 in increasing
coefficient order.

At $t=n-1$, $V^t=1+X+\cdots+X^{n-1}$. For every seed, coefficients
2 through $n-1$ of $P_t$ are all $a+b+c$, so there is a forbidden
constant triple.

For $t=n+s$ with $0\le s\le n-6$, set $Q=V^sP$, of degree at most
$s+2$. Then

\[
 P_t=Q+X^nQ.
\]

Between the two terms are at least $n-s-3\ge3$ consecutive zero
coefficients. Thus every seed fails. The live interval $n-5$ through
$n-2$ and dead interval $n-1$ through $2n-6$, for successive powers
of two, cover every depth from 3 onward. This proves the exact criterion.

The dead intervals have unbounded lengths, while live depths occur
arbitrarily late. An eventually periodic binary sequence with any later one
has a one in every sufficiently late interval of its period's length. Hence
this life sequence is **not eventually periodic**. The statement concerns
the supplied generation index and closing condition, not physical time.

## 8. What simple sharing cannot do

### 8.1 The 168 minimum private gadgets

The checker independently projects every listed minimum gadget, including
all sixteen raw named assignments. Every even assignment has exactly one
three-helper extension, and every odd assignment has none. For each of the
504 helper occurrences, its value fails to be a function of **any two** of
the four named distinctions.

Adjacent rule-60 parity occurrences share only $R$ and one old main
distinction. Given those shared values, the two outer inputs remain
independent. Identifying a uniquely determined helper from each occurrence
would require both helper functions to depend only on the shared pair.
The checked dependence property excludes this, including different labelled
minimum gadgets and permutations of the helper roles. This is an obstruction
to direct sharing of those private optimal gadgets, not to every NAE
construction. The replay retains concrete correct inputs rejected by one
incorrect overlap.

### 8.2 All deterministic adjacent-pair encodings in a stronger local window

Fix one helper at each position to be any Boolean function of either the
previous and current normalized mains or the current and next normalized
mains. There are $16+16-4=28$ distinct functions. Fix both helper channels
this way, with the same two functions at every position and generation:
there are 784 ordered encodings. Raw helper values are $R$ XOR the chosen
normalized function. Missing old or helper-input main positions are $R$.

For each encoding and each of widths five and six, construct the **maximum**
set of strict NAE constraints that hold on every correctly encoded rule-60
row pair. Allow every triple drawn from both generations and $R$, subject
only to its nonreference positions spanning at most two index increments.
This includes every triple on three consecutive positions in both
generations, so it is more permissive than the original old-$i-1,i,i+1$,
new-$i-1,i$ slot shape. Give each end every valid width-specific constraint
too. Fix the old generation to a completely correct encoding for free.

The replay supplies a directly verified wrong-main countermodel for every
encoding:

| Countermodel | Encodings |
| --- | ---: |
| Wrong main after one transition, initial width five | 724 |
| First-transition main values pass; wrong main after two transitions | 60 |
| Iterable exact encoding surviving both tests | 0 |

For the two-step case the maximum width-five and width-six systems are
composed by the identities of their shared generation. Every countermodel
satisfies every clause of this strengthened system and starts with the
correct supplied initial helpers. The result file retains the input and
full joint state for each case.

**Why these countermodels prove a bounded obstruction.** Any candidate NAE
rule admitting every correct encoded transition can contain only triples in
the corresponding maximum relation. The countermodel satisfies them all,
and therefore satisfies every candidate subset. A rule must also admit all
canonical correct transitions at its ends; strengthening those ends cannot
remove the exhibited countermodel. This excludes the declared encoding and
window class. It does not exclude a different representation of helpers.

The one-step/two-step distinction is necessary: a helper can hold an advance
copy of a future main value, making the next main correct while leaving the
following helper unconstrained. Such a one-generation agreement is not
composability.

### 8.3 A local complementary-reference helper is insufficient with one
three-main function

A second check pins the first helper to $1-R$ at **every old and new
position for free**, and lets the second helper be any of the 256 functions
of the three normalized mains at previous, current, and next positions.
In the same stronger span-two class, every function admits a wrong main
after one step at width five. All 256 countermodels retain the correctly
pinned complementary-reference channel. Thus the defect is not merely an
unproved method for transporting that channel.

### 8.4 An isolated two-output overlapping block

For raw named distinctions $R,a,b,c,u,v$, require
$u=a\oplus b\oplus R$, $v=b\oplus c\oplus R$. A separate complete
selector encoding tests every strict positive NAE definition using four
additional **private** helpers. All three-named projections of the target
are full, so no all-named NAE triple is permitted. Every other strict triple
is available. Positive named assignments receive arbitrary existential
helpers; every helper assignment on a wrong named state must violate a
chosen triple. Complementation permits $R=0$ representatives.

CaDiCaL returns UNSAT for this complete finite encoding (132 Boolean SAT
variables, 976 clauses). This is a solver-backed obstruction to that
isolated block; no proof trace was replayed. It does not cover helpers
inherited from the old generation. A three-output/six-private-helper search
was left inconclusive; it supplies no impossibility verdict.

## 9. Controls, validation, and the remaining obligation

`check.py --write-result` passed with the repository `.venv` Python. Its
decisive positive checks are:

- All 128 raw assignments of the nine-constraint initial relation; the local
  helper, transition, and right-end truth tables, for both values of $R$.
- Every main input at widths two through seven, both reference values, with
  an exact one-transition SAT projection including every output helper.
- All eight normalized initial seeds through depth 64 for the actual closed
  system; at depths one through eight, all sixteen raw seed/reference
  assignments against the original CHEAP-COUNT `growth` implementation.
- A separate integer-polynomial calculation through depth 8,192 against
  the all-depth criterion, and the symbolic uniform argument above.
- Strictness and exact inventory at every tested depth. Depth 64 gives
  6,826 distinctions and 22,671 distinct NAE triples.

Matched controls include an incorrect overlap of private gadgets, an
incorrect reference in the uniform update (which allows 00 to update to 1),
and an insufficient initial relation that leaves $S=R$ possible. The code
actually accepts each malformed control and rejects it under the claimed
relation. The 1,040 local-class countermodels are additionally checked by
direct evaluation, rather than trusting a solver's satisfiable answer.

Validation is **V1, separate algorithms in the same task**: NAE/SAT
construction, direct local truth tables, and the integer-polynomial
calculation share authorship. Original-code calls are marked as predecessor
comparison, not independent derivation. There is no formal-kernel
verification or external replication. The finite replays support the stated
claim surface; Lemmas 1–4 and the induction, not a depth cutoff, prove the
uniform construction. The exact band proof separately supplies the
all-depth counting conclusion.

The primary epistemic class is an exact construction, with a bounded
countermodel exhaustion as a secondary result. Source contribution is zero:
the theorem concerns chosen positive NAE constraints on the declared binary
variables. Broadcast access to the already counted seed helper is an
explicit supplied access convention, not a consequence of its low inventory.
External novelty remains **candidate local delta**, unassessed beyond the
existing terminal nearest-known comparison.

The strict single-broadcast-reference objective remains open. The strongest
surviving positive statement is the exact three-per-position counter under
two-reference access; the strongest obstruction excludes the specified
adjacent-function classes even with strengthened ends. The blocker is a
**substantive near-miss**, not a failed validation envelope.

The next natural gap is to realize the second reference by genuinely bounded
access **without adding a third helper per position**, using a
period-dependent or nondeterministic block encoding outside the excluded
classes, or to prove a broader obstruction. A further attempt must state
its complete allowed input relation, access pattern, boundary variables,
soundness, and simultaneous extension gate before comparing life sequences.
No rarity, global minimality, or general impossibility claim is made here.
