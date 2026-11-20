# What advances when the next layer is made?

On the 17-knot background a directed pattern of newly made junctions advances for eight steps toward the opposite end. Its distances to the two fixed source ends run from $(0,16)$ through $(8,8)$ and then become $(9,9),(10,10),\ldots$. The rule follows one marked meeting and reads the nearby parents and children. The opposite end only scores the result. Both reflected patterns occur in the anonymous background. A closed four-distinction parity pattern can follow the same sequence with one additional layer of lookahead. The old parity assignment by itself has no such transition.

## A0. What the old assignment retains

Restricting an allowed extension to the earlier distinctions returns that same earlier assignment, coordinate by coordinate. The round attaches its own fresh variables to each new parity equation. These open sources admit extensions for every old allowed row. Even when an equation requires some new bits to be nonzero, it leaves the values of the previously assigned bits intact. In particular the all-zero state has an all-zero extension at every age. The growth rule supplies no choice of occupied pattern or state update.

There is also an exact zero-extension test for the previously demonstrated pulse. Its four occupied distinctions already have two ordinary holders each. They form a cycle with two occupied distinctions at each of its four junctions. Later junctions consume loose distinctions only. Assigning zero to all fresh bits therefore leaves exactly the original four occupied at every later stage. All 485 first-round ordinary squares across the 14 sources satisfy this test. For J1 the three specified predecessor supports were also checked directly against every equation at all six available positive ages. Choosing a neighboring four-distinction support changes old bits and requires an additional update. [Predecessor pulse](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/adjacent_changes.json)

## A1. The marked meeting

The mark is one actual shared distinction between a parent $P$ and its current child $C$. Age distinguishes its holders. Among the children $D$ of $C$, retain all satisfying

$$\operatorname{Parents}(D)\ \cap\ \bigl(\operatorname{Children}(P)\setminus\{C\}\bigr)=\varnothing.$$

Thus a child of $C$ is excluded if it is **also a child of any sibling sharing $P$**. Advance the directed mark to $C,D$ only for a unique answer. A zero and a tie both end the strict trace. The full set at a tie is recoverable. This rule uses the holder incidence and a completed next layer. With $P$ and $C$ marked, the sibling incidences and the parent sets of $C$'s children suffice. At most two ordinary meeting steps from the marked holders expose them. The chosen holder advances exactly one meeting per larger-size event.

The layers themselves are recognizable in this family. A junction is in the current growing end exactly when it carries a loose distinction. Every earlier junction has a child in the next age and can continue to the current age. A physical meeting changes age by at most one. Minimum holder steps to the end therefore equal the junction's age deficit. Its older and younger neighbors can be read from full anonymous current incidence. Occupying a single shared distinction in an allowed binary state would generally violate parity. The A1 mark is an identified meeting used by a reader.

**Exact continuation theorem.** Lift $P$ to a connected cluster $A$ containing an original knot in the identified cover. Lift $C$ as $A\cup\{x\}$. Its child adds one further point $y$. If $y$ was already adjacent to $A$, then $A\cup\{y\}$ is another child of $P$ and is a parent of $D$. Conversely, suppose such a sibling exists. Using its parent link, the same lift of $D$ contains a copy of $A$ inside that sibling. It cannot contain two different translates of $A$, since the union lemma requires at least four extra points and $D$ has only two extra points. Thus the sibling is $A\cup\{y\}$ in these lifts, so $y$ was adjacent to $A$.

There is a unique incidence block $B$ through which $x$ joins $A$. Two would create a cycle in the covering tree. The eligible points are precisely the other points of every block at $x$ except $B$. Their number is

$$\sum_{B'\ni x,\ B'\ne B}(|B'|-1).$$

All are distinct physical child orbits by the identification theorem. The directed rule follows a path through incidence blocks with no immediate reversal. A finite spare has zero exits. An endless chain has one forward exit. A bare cycle has one at every arrival, and a decorated ring has additional choices. In particular arriving *through* a held block excludes every other point in that incoming block, including any third or fourth point. At the next block all its other points are available. [Identification and union lemma](../../proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/proof.md) · [Chains and admissible parents](../../proofs/CHAIN-IDENT-20261119-001A/CHAIN-IDENT-20261119-001A-P001_chains/proof.md)

## The path, its two landmarks and its reflected launch

Write $b_0,\ldots,b_{2L}$ for the ordinary source path, with the four registered leftovers. Each of its two map pieces is a line. On the even line index $b_{2i}$ by $i=0,\ldots,L$ and continue the two ends through their endless chains. The unique binary child of $b_0$ is the interval $[0,1]$. The unary child is $[-1,0]$. If $P=[i,j-1]$ and $C=[i,j]$, the backward-side extension $[i-1,j]$ is also a child of $[i-1,j-1]$. The only eligible continuation is $[i,j+1]$. Thus the inward trace is $C_t=[0,t]$ for all $t$, including its continuation past the last physical source on the line.

For an age-$t$ junction $C$ and any fixed source knot $v$, ordinary holder distance is

$$d(C,v)=t+\min_{u\text{ a source ancestor of }C} d_{\rm source}(u,v).$$

A route can replace a peak through a child by a route through its parents' common older witness of equal length. Reducing the sum of ages on shortest routes gives monotone descent to an ancestral source followed by original meetings. The source ancestors of a cluster are precisely its contained original labels. For the inward trace these are $b_0,b_2,\ldots,b_{2\min(t,L)}$. Hence the two readings ordered by launch and opposite end are $(t,2L-t)$ through $t=L$ and $(t,t)$ afterwards. Starting with the unary child and following its unique continuation gives $(t,2L+t)$ at every age. Its sole original ancestor stays $b_0$. This control moves one physical holder step each time as well. [Ordinary meeting steps](../EDDY-WORLD-20261119-001/steps.md) · [Source ancestry and the two lines](../EDDY-WORLD-20261119-001/theory_fate.md)

No source endpoint can be picked singly on anonymous B or B81 by an equivariant deterministic rule. Reflection exchanges them. Taking both gives an intrinsic unordered pair of traces. Their inward traces reach the **same current junction** at $t=L$ and continue through different children because their entering meetings differ. Supplying one endpoint as the launch distinguishes the two landmarks for grading. At J1 or J81 the single seam also distinguishes the two ends by its unequal source distances. A symmetric double, such as T8 or T81, again exchanges the two copies and the ends. No landmark enters the local continuation test.

At every positive age the inward junction on B has two parents and two forward opportunities, and its marked incoming meeting has the same local directed role on successive layers. The original interval from the endpoint accumulates all earlier source ancestors. The bounded travelling shape is the marked meeting, or the square below. The whole growing interval has size $t+1$.

There is a general limit to an indefinitely opposed two-landmark reading. Along **any** parent–child sequence $j_t$, for a fixed junction $v$ of age $h$, the integer $d(j_t,v)-t$ is nonincreasing. An additional holder step suffices to reach the new child. This integer is bounded below by $-h$, since each step changes age by at most one. It stabilizes. For every finite set of fixed landmarks, all their distances eventually increase by one at every subsequent advance. Within this class, a longer initial path provides an arbitrarily long finite approach interval. For B81 that interval has 40 steps. This argument places no fixed duration on all starts.

## The commuting square

In the unbranched inward trace let $S$ be the other child of $P$ and $M$ the common child of $C$ and $S$. The four shared distinctions of $P,C,M,S,P$ form a closed parity change. For the next marked meeting the corresponding square shares exactly the distinction joining $C$ to $M$. The two supports differ on six real distinctions. Each state exists in any accumulated stage that contains its four junctions. Their minimum holder distances to the two fixed ends are $(t-1,2L-t)$ for $1\le t\le L$ and $(t-1,t-1)$ afterwards, where $C$ has age $t$ and the square is available at age $t+1$. Its vertices have ages $t-1,t,t,t+1$. Substituting their intervals $[0,t-1],[0,t],[-1,t-1],[-1,t]$ into the source-distance formula gives these readings. The launch square at $(0,15)$ has two three-place and two four-place holders. From $t=2$ all four holders have two parents and two fresh distinctions. Three successive copies with this same decoration score $(1,14),(2,13),(3,12)$ on B.

This gives a fixed-size allowed difference supported by the advancing structural mark. Turning one occupied square into the next requires a change of assignment on their six differing old distinctions once both exist. Appending the next layer alone leaves all previously occupied bits in place.

## First forks, returns and source fates

The binary launch from $b_0$ in the short joined cases reaches the first seam at age 2. Entering its point copy along the background offers three children, the forward path point and two ring points. The cut control gives the same three-way fork. From $b_{16}$ the first fork occurs at age 6 in J0, J1, J2 and C1, at age 4 in T4 and at age 2 in T8. On J81 the two inward first forks are at ages 15 and 25. On T81 both are at 15. The outward unary launch at every one of these path ends continues uniquely forever. The assigned rule halts at a tie even if an evaluator can distinguish a ring exit from a path exit.

On R0 and R31 every directed first meeting continues uniquely. The newly added point's projected source phase advances around the two-step ring walk and repeats with period five or 31. Each physical birth and its entering distinction are new. Once all original ring knots belong to a cluster, at $t\ge4$ or $t\ge30$, its distance to each original landmark is $t$. Returning a phase on larger and larger clusters does not bring the occupied pattern back to the same physical four distinctions. The bare ring also gives a sharp current-junction-only obstruction. Reflection $k\mapsto i+j-k$ in the unrolled ring fixes the current interval $[i,j]$ and swaps its two parents and its two children. It descends to an automorphism of the complete accumulated incidence. A single marked current junction cannot select a unique one of these children equivariantly. Its marked incoming meeting distinguishes the continuations.

On R1 its one finite spare gives one immediately terminal source launch. The ten directed core launches reach a two-way tie, two each at ages 1 through 5. On R2 the two offshoot launches stop immediately and the ten directed core launches reach ties, respectively four, four and two at ages 1, 2 and 3. Retaining both choices at a decorated point would include the continuing ring route and a finite spare that stops. That branching relation is recorded separately from the strict rule.

| Source | Last literal age | Source meetings launched | Endless chain | Periodic source phase | Strict stop on zero | Strict stop on tie | Literal marked meetings with next layer available |
|---|---:|---:|---:|---:|---:|---:|---:|
| B | 32 | 34 | 34 | 0 | 0 | 0 | 2,914 |
| R0 | 32 | 10 | 0 | 10 | 0 | 0 | 310 |
| R1 | 29 | 11 | 0 | 0 | 1 | 10 | 5,549 |
| R2 | 17 | 12 | 0 | 0 | 2 | 10 | 3,882 |
| J0 | 7 | 52 | 24 | 0 | 0 | 28 | 1,968 |
| J1 | 6 | 53 | 24 | 0 | 1 | 28 | 1,217 |
| J2 | 6 | 54 | 24 | 0 | 2 | 28 | 1,430 |
| T4 | 5 | 72 | 20 | 0 | 2 | 50 | 1,116 |
| T8 | 5 | 72 | 16 | 0 | 2 | 54 | 1,048 |
| C1 | 11 | 53 | 26 | 0 | 10 | 17 | 4,647 |
| B81 | 1 | 162 | 162 | 0 | 0 | 0 | 0 |
| J81 | 1 | 181 | 88 | 0 | 1 | 92 | 0 |
| T81 | 1 | 200 | 68 | 0 | 2 | 130 | 0 |
| R31 | 1 | 62 | 0 | 62 | 0 | 0 | 0 |

The fate columns classify all 1,028 source launches at arbitrary later sizes by the proved forward choices in the finite map, with endless chains represented by their repeated incidence type. A branch with two exits of the same kind still has two choices. The last column concerns physically materialized comparisons. There were 160 archived stages and 150 adjacent-layer comparisons, plus source and first layer for the four new starts. Testing a marked incoming meeting against its next candidates needs three consecutive layers, so 140 archived adjacent-transition pairs supply the 24,081 literal meeting tests. Their outcomes are 6,244 empty, 15,301 unique, 1,651 two-way and 885 three-way. A final physical layer with unknown successors has no scored verdict. The archive includes all concrete alternative IDs at the observed ties, every directed launch, and the reachable map types with all exits. [Replay](../../experiments/MOTION-AT-EDDY-20261119-001/MOTION-AT-EDDY-20261119-001-E001_motion/layers.py) · [Per-case results and alternatives](../../artifacts/MOTION-AT-EDDY-20261119-001/MOTION-AT-EDDY-20261119-001-E001_motion/layers.json)

The replay infers ages and holders from anonymous incidence, checks them against every archived layer, and transports the candidate sets under a simultaneous permutation of junction and distinction names. To check the map prediction on every observed directed meeting, a first binary link adds the other parent through the unique source witness. A unary link adds a pendant or its next ray point. At larger joins the opposite sides of any commuting square add the same point through the same block. Peeling such squares reduces an incoming link to its earlier type. Every available choice of older square gave the same type. The predicted multiset of outward types agreed with the complete physically admitted set on every comparison.

## The passive background and the ring's own growth

The four additional sources passed K1–K3, funding and the unique-witness and held-triple checks. They have one distinction per ordinary meeting and each source knot has a loose distinction. Removing it from the wired ordinary graph leaves all the other knots connected to the exterior, so its star is a genuine even-parity bond. In B81 both parity pieces have two endless chains, giving $81+2t$ births and cumulative dimension two. R31 has 31 births per round. J81 has the same five-knot cycle, one finite spare and four independent endless arms as J1, with exponential size factor 1.940108222202. T81 has three independent cycles and four endless arms. Applying the predecessor’s exact positive-series inequalities to the new separation 20 gives its total size factor in $[2.051,2.052]$. This is $\lim N_t^{1/t}$ for births by size. Both confined ring counts remain R1's with factor 1.134724138402. The short fixtures retain their previously proven fates, including C1's cumulative dimension three. None of A0 or A1 changes the growth equations or selects a different number of births. [Source qualifications, rate proof and predecessor fates](../EDDY-WORLD-20261119-001/theory_fate.md)

The A1 directed pattern is read on completed incidence. On the identified family the same relations can be considered after the required parents and children have been made in a dependency ordering. A partially built snapshot can still be missing a sibling or an additional exit, so a premature claim of uniqueness does not follow. The continuing pattern, its new closed square and the original stationary ring are three separate physical supports. No comparison here moves the older ring's self-feeding activity to another attachment or defines elapsed physical time. [Prior order-free scope](../ROUND-FREE-20261119-001/round_free.md)
