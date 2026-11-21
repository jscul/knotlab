# Bare ring clocks and a one-member receiver

With a physically marked bare cycle and the full present holdings
supplied, two one-member clocks can draw apart, hold their witnessed
separation, or draw closer by one witnessed step per cut. A receiver
with one current member and two actual parents can take a returning
knot directly from another clock on every turn. In this class its
own child prices and clock period stay the same. The anonymous
witnessed end erases the markers.
[Frozen design](preregistration.md) · [Exact receipt](../../artifacts/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B-E001_receivers/phase_clocks.json)

## What the holdings identify

Let the original live knots have one candidate cycle with $L\ge4$
phases and two loose distinctions at each live knot. The physical
marks distinguish an original knot and the first witnessed step of
an order around this cycle. Use $p$ for the first phase of the
oriented interval recovered at age $t$. Its size is $t+1$ and its
opposite endpoint has phase $p+t$ modulo $L$. Identifying a phase
uses the order of recovered originals. The integers used to display
it are names for the proof and replay.

All original groups are the neighbouring pairs of the candidate
cycle. Every live knot belongs to two such pairs. Each pair gives
one birth, with its two old knots as true parents. At the new end
these births witness one another precisely when their parent sets
share one old knot. They give the same cycle again. Each new knot
belongs to two next groups and therefore receives two fresh
distinctions. This proves the claim at every age. Every cut has
at least four births, and the sole parity closing condition never
occurs. At positive age the birth at phase $p$ has the two true
parents of phases $p$ and $p+1$ at the preceding cut. They are
its two end deletions. This also follows from the identified
cluster rule.
[Actual parent identification](../../proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/proof.md) · [Law-specific continuing rule](../NAE-GROWTH-20261119-001/nae_growth.md#why-it-holds)

The full reader peels each complete loose cohort and checks its
actual input and fresh rosters on the preceding holdings. The
original all-live five and mixed six have shared distinctions
between two original live knots. In the four-spent-witness case,
peeling the live originals would leave four disconnected spent
knots. These physical tests locate the supplied original cut.
Read its marked direction, then assemble each new word from
its two actual parent words with their common shorter word
identified. Independent renaming of knots and distinctions
preserves the whole calculation.

| Preparation | Physical way to read the original order | Original knots | Original distinctions | Witnessed period |
| --- | --- | ---: | ---: | ---: |
| All-live ring of five | Common holder of a tripled sharing and a doubled sharing. Follow the ordinary neighbour of the doubled sharing for the first of the two original steps to the next live phase. | 5 | 18 | 5 |
| Same five with one added sharing | Add a second shared distinction to original pair 2,3, away from the mark. Retain all original distinction identities. | 5 | 19 | 5 |
| Four live knots and two spent witnesses | Live holdings form an ordinary path. Start at the doubled end of the unique spent witness whose doubled end has just one live neighbour. | 6 | 17 | 4 |
| Four live knots and four spent witnesses | Each spent witness relates two consecutive live phases. Start at the tripled end of the only spent witness with four distinctions. | 8 | 21 | 4 |

In the anonymous witnessed end from age zero onward, every phase
has two loose distinctions and every nontrivial witness set is an
adjacent pair. The witnessed ends of any two cuts of the same
period are isomorphic. Their phase rotations exchange the exact
one-member roles. This reading alone leaves the roles and the
elapsed count unresolved. The full-holdings calculation uses the
physical mark and recovers current age by actual parents. Its
tick detector tests the two endpoint roles of the current member.

## Turns and witnessed separation

Fix the first endpoint at mark $a$, or the last at mark $b$.
Either rule gives one current member at every cut and keeps a
true parent from the preceding member. A turn means that the
opposite endpoint is again the chosen mark. The cut of origin
starts the count at zero. Each positive return is one event.
The first turn has age $L$ and future turns are $L$ cuts apart.
A rival reading tests the opposite endpoint against a different
original mark. Its first positive age is $r\in\{1,\ldots,L\}$.
For first anchoring, $r$ is the positive residue of target minus
anchor. For last anchoring, it is the residue of anchor minus
target. The count at age $t$ is

$$
C_r(t)=\max\!\left(0,1+\left\lfloor\frac{t-r}{L}\right\rfloor\right).
$$

After both have started, two readings of the same period with
different first phases differ by at most one tick. Changing the
target shifts the phase. The physical edit on the five-ring
preserves the entire recovered role, the actual phase rosters and
every count. Both laws give identical positive cohorts. This is
a count relative to a recovered original and a chosen event.

Write $\rho_L(x)=\min(r,L-r)$ for the least number of witnessed
steps with residue $x$, where $r=x\bmod L$ lies in $\{0,\ldots,L-1\}$.
Two age-$t$ members share an old witness precisely when their
first phases differ by one, in either direction. Their exact
witnessed separation is therefore $\rho_L$ of the difference.
The first-anchored member at $a$ has first phase $a$. The
last-anchored member at $b$ has first phase $b-t$. For the
two current members this gives

$$
d_t=\rho_L(b-a-t).
$$

Two members anchored at the same kind of endpoint have constant
separation $\rho_L(b-a)$. The opposite-end choices attain
increases and decreases of one. On the odd cycle the farthest
value holds at two successive ages. On the even cycle the
opposite-end separation reverses directly at the farthest
value. The same-end comparison supplies a constant positive
separation on both. For equal opposite anchors the complete
patterns, including the next zero, are $0,1,2,2,1,0$ for five
phases and $0,1,2,1,0$ for four. Other choices of $a,b$ shift the
patterns. When the exact members coincide, the measured
separation is zero.

## What arrives in a selected member

Take a sender at first phase $q$ and a receiver at first phase
$p$ on the same launch cut. After $h$ cuts the sender's inclusive
descendants occupy the phases $q-h,\ldots,q$. The analogous
list from the receiver ends at $p$. These claims follow by
listing both actual children of each knot at a step. The two
inclusive sets have separation $\max(\rho_L(q-p)-h,0)$.
For distinct launches, their first common birth has one actual
parent exclusive to each branch at the preceding cut. There is
one such first birth, or two when the original phases have even
period and are separated by $L/2$. Co-membership at launch is
recorded as zero separation and no outside receipt.
[Inherited inclusive-arrival criterion](../FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/clock_proof.md#what-arrives-where-and-at-which-count)

The first-anchored receiver's later selected member always starts
at $p$. Its launch-age ancestors at delay $h$ start at
$p,\ldots,p+h$. The last-anchored receiver's selected member
instead starts at $p-h$ and has launch-age ancestors beginning at
$p-h,\ldots,p$. Consequently a distinct send first enters
receiver ancestry after $(q-p)\bmod L$ cuts for first anchoring
and $(p-q)\bmod L$ for last anchoring. The continuing receiver's
own parent at that first receipt has yet to inherit the send.
The second true parent carries it. An immediate admission of the
sent knot into the next selected member occurs exactly at delay
one. Both adjacent launches give a direct input to one of the
receiver's own two children. The chosen endpoint determines
which child becomes the next member.

| Physical sender of first-phase receiver at 0 | Five phases, first inclusive ages | Five phases, first ancestry ages inside receiver | Four phases, inclusive / inside delays |
| --- | --- | --- | --- |
| First endpoint at 1, turn returns to 1 | 6, 11, 16 | 6, 11, 16 | 1 / 1 |
| First endpoint at the phase preceding 0, turn returns there | 6, 11, 16 | 9, 14, 19 | 1 / 3 |

The pairs of receiver outputs that admit the two adjacent senders
each have the unlabelled price roster $[2,2]$. The immediate
inside receipt can therefore be read through actual inputs but
leaves no difference in that roster in this class. A further
control compares two first-anchored receivers at phases 0 and 3
with one sender anchored at phase 1. Both receivers count their
own returns with the same period and the same first age. At
each sender turn the first receiver directly takes that sender
as its outside parent. None of the second receiver's immediate
children takes that same sender. The second can inherit the send
later. Both receivers have the same count at all common ages
and the same two child prices on each cut. The inputs are
distinct returning knots. The earlier continuing pure packets
impose an additional all-parent requirement.

For a send at age $a$ with launch separation $d_a$, inclusive
arrival is at $a+d_a$ while the ordinary cuts keep forming.
Consecutive send ages $a,a+P$ therefore have arrival gap
$P+d_{a+P}-d_a$. For these current ring clocks, $d$ changes
by at most one in a cut, and returns to its same value if
$P=L$. Their regular inclusive gap equals their send spacing,
and the selected ancestry delay also repeats. The preceding
16-step sender and its 24-step receiver have a launch separation
that increases by 16 between those sends, so the same formula
gives 32. Their first three inclusive arrivals are 50, 82 and
114. Sending every 16 and arriving every 32 is a property of
that specified comparison.
[Prior exact send schedule](../FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/clock_proof.md#what-arrives-where-and-at-which-count)

## Minimum and limits

A nonempty receiver needs at least one member. For direct entry
into a next member, the continuing receiver parent and the
distinct outside parent require at least two actual parents.
The first-anchored example attains both lower bounds at
unbounded cuts. Its next member always retains the internal
parent and one outside parent. The bare cycle funds two children
from every current knot, so at any positive cut each member's
two inputs and two fresh distinctions give arity four. The
unrestricted floor with two parents only yields arity at least
three. The stronger arity bound here uses the bare cycle.

For a complete persistent bare pair cycle, $L$ must be at least
four. Fewer than three live knots cannot give two distinct pair
groups per member. With three live knots a common witness for
all three can give the three original pair births. The three
new pair births then witness one another through three different
parents, so the next step forms a group of three and leaves
the bare class. For a four-phase cycle, each candidate pair
requires its own original witness. A witness with three live
neighbours would create a witnessed triangle. Four live knots
and at most one spent knot would need at least three of the
four live knots to have two live neighbours. In the ordinary
sharing relation restricted to these four, degree is at most two.
The sum of degrees forces the last live degree to be zero or
two. The possibilities are a three-cycle and an isolated live
knot, or a four-cycle. The former creates a witnessed triple and
the latter duplicates opposite candidate pairs. Thus four phases
require at least six original knots, and the mixed arrangement
attains this bound. With the five-phase fixture the overall
minimum is five original knots. These are bounds for the
specified bare class, with no minimum claimed over all ordinary
growth preparations.

If an indefinitely continuing family requires all its parents
inside, then on this ring it contains the whole live cohort
at every cut from its launch. A member $L-1$ cuts later already
has every earlier phase as an ancestor. The one-member current
clock is possible because it keeps one continuation parent and
admits the other. In every matched preparation preserving the
same phase cycle, marker and ordinary supply, the two child
prices and next phase rosters are forced. A change of the sender
phase changes which branch supplies an input and when the
selected receiver inherits it. It cannot change the paid roster
or either period within that class. The study supplies no later
choice between different actual sends on fixed past holdings.

## Validation

Four deterministic preparations under both laws furnished 296
complete cuts, 1,296 actual positive births, and 25,752 exact
physical star projections, counting the repeated checks on older
stars. The canonical forgetting command passed for all ten
law/arity combinations, from arity three through seven. The
full reader recovered the phase orders and every actual parent
after independent renaming at every complete cut. All 5,412
ordered launch-member comparisons, including equal members, were
checked through launch age 32. Actual future cuts through age 36
certified each inclusive and selected ancestry delay. All fixed
endpoints and rival targets were tested. A different Python hash
seed reproduced the exact receipt. Independent referee pending.
[Code](../../experiments/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B-E001_receivers/phase_clocks.py)

The physical mark, original preparation, chosen turn, receiver
membership and observed meaning of receipt are scaffolds. The
witnessed parent identities, bounds, count increments and receipt
delays follow from ordinary growth once those choices are supplied.
The readings concern order in that growth.

The receipt digest is `72be0d16ea0a0276954b8ae049808f6a5b8c3e91097b9c997a8cd6716255c435`.
The measured replay ran in 6.31 seconds, with 62,088 KiB peak memory.
