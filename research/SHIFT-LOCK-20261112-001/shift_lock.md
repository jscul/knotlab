# Locks across two shifts

Epic `SHIFT-LOCK-20261112-001` (`LOOP-LOCK-20261112-001` direction 1, why rings lock by arithmetic, taken to copies along two shifts;
G17 with G8; program mathematics, group arithmetic), 2026-11-12, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen in commit `4a511977a`. Proof family: `proofs/SHIFT-LOCK-20261112-001A/`. **Referee
pending.**

## The question

Rings of stitched harmonies lock by the arithmetic of their length; the referee of `LOOP-LOCK-20261112-001` proved it at every length
from the periods of the pair transfer (credited here, not redone). Off one cycle, with copies along two shifts, the coordinator's
question: **is there a pattern family whose influence is unbounded in size and is not a walk around one cycle?** The owner's words
behind it: meeting patterns that "fold in immensely complex ways and can be kind of globally influential".

## The answer

**Two-way states exist, but influence still travels around cycles.** Copies along two shifts tied by straight knots add nothing to the
rings (proved). With the mixed knot, the three-member shape of Ledrappier's law, states that repeat along no step appear in 34 of the
45 harmonies, and in 78 cells they are the only way the arrangement opens. But they tie no copy to any other, and every lock that holds
at all sizes of a family comes from a walk around one cycle.

- **Unmixed knots reduce to rings (proved; 945 of 945).** With knots (x, x + e, x + 2e) along each shift, the n × m arrangement
  locks exactly when the ring of n and the ring of m both lock: rows and columns are rings, and a ring state laid along one shift is a
  state of the whole. No collective lock, and none undone.
- **The mixed knot (exact, n, m = 2 to 9, 2,880 cells).** For the knot (x, x + e₂, x + e₁), 323 cells lock; in 1,303 every non-constant
  state repeats along a short step (at most two copies each way, up to the harmony's own shifts and flip), a walk around one cycle; in
  878 some state repeats along no short step; and in **78 cells, for 10 harmonies, no non-constant state repeats along a short step at
  all**, so the arrangement opens only through two-way states (the frozen "yes", in its weaker form). On squares to 16 × 16 this never
  happens (675 of 675), so the strongest form frozen did not appear.
- **What the two-way states are (after the run).** Each of the 78 satisfies the law by direct evaluation and repeats along no step at
  all; none is a short-step state under any other symmetry of the harmony's states where those could be listed (50 cells). For
  `0011 + 01` they are mixed tilings: on the orbit of 0011 a knot's members are equal or three distinct phases in increasing order,
  which makes each state a height function with three cell types, the literature's height function of a tiling, and a slope rule
  (the windings must give average slopes inside a small polygon, as for the dimer model) decides every lock to 16 × 16 (225 of 225).
  When no whole-number slope fits, every state mixes cell types and repeats along no step.
- **Influence (after the run).** In all 78 cells copy 0 is tied to nothing. Locks that hold at every size of a family come only from
  strips (one count at most 7, a ring of short rows with a finite transfer) and from short-step arithmetic (`0011` locks exactly when
  4 ∤ m and gcd(n, m) ≤ 3, 225 of 225); other locks are sporadic (5 × 5 for `0011 + 01`; 6 × 6, 9 × 9, 9 × 11, 11 × 9 and 11 × 11 for
  `00001111 + 00101101 + 01`). On rings, one copy fixes exactly every L-th copy at every length, L the least common multiple of the
  periods in play (403 of 405 cells as predicted).
- **No linear case, and the method would see one.** No harmony's increments hold a whole line {(a, λa)}, the condition for a
  Ledrappier-type automaton. Ledrappier's own law, run as the control, unlocks exactly at the advisor's sizes (3, 6, 7, 9, 12, 14, 15,
  18, 21, 24, 27, 28, 30, 31 to 32), and at 31 none of its states repeats along a short step.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Unmixed knots on two shifts lock iff both rings lock; stepped states are states | proved by hand (with the advisor model); exact on 945 cells |
| Mixed knot: 78 cells open only through states with no short step; 878 with some; none on squares to 16 | exact on the range (frozen) |
| Ring ties: n, n / L or copy 0 alone | exact on 405 cells (frozen; 2 exceptions at 6) |
| Ledrappier control and the short-step discriminator | exact by rank to 32 (frozen) |
| The 78 states verified, no step at all, tie nothing; no other symmetry gives a short state (50 cells) | after the run, descriptive |
| `0011 + 01`: states are tilings, locks follow the slope polygon (225 of 225); `0011`: 4 ∤ m and gcd ≤ 3 (225 of 225) | after the run, checked to 16 × 16; not proved for every size |

## Against the pre-registration

G1 on every cell and G2 everywhere (theorems). States with no short step widely (predicted 90%: 34 of 45 harmonies). "H0 holds wherever
no orbit's increments hold a line" (mine, 70%): **not met**, no orbit holds one and H0 still failed in 78 cells; "H0 fails somewhere"
(mine, 35%): met. The four harmonies whose rings always lock unlock mixed arrangements (60%: met for all four). The triple-test
prediction was not tested: no single-orbit harmony passes the test. Ledrappier's sizes (90%) and "not every state short at some
unlocking size" (75%): met. Ring ties (80%): met on 403 of 405 cells; the frozen wording did not cover components of period 1 that
avoid the diagonal, scored here as "copy 0 alone". Every search solver call was bounded (20,000 conflicts); 376 cells of the
no-short-step search are not settled and counted for nothing. All five parts finished inside their caps (13 and 27 minutes for the
two large parts). The two after-run checks are labelled; the first attempt at the state check stopped at its one-hour cap and was
rerun with the automorphism search limited to harmonies with at most 20 states.

## Known mathematics

Periodic points of one-dimensional shifts of finite type (Lind and Marcus) for the rings, as the referee showed; matrix subshifts of
rows and columns (Markley and Paul, 1981) for unmixed knots; for the mixed knot, Ledrappier's shift (1978) and periodic points of
algebraic actions of ℤ² (Kitchens and Schmidt, 1988; Lind, Schmidt and Ward), cycle lengths of linear cellular automata on rings
(Martin, Odlyzko and Wolfram, 1984), and periods of two-dimensional shifts of finite type, which can be any NE set (Jeandel and
Vanier); height functions of tilings (Thurston, 1990) and the slope polygon of the dimer model (Kenyon, Okounkov and Sheffield, 2006)
for the two-way states. Novelty is not claimed for any mechanism; the harmonies' data are new.

## What it changes

- **For the owner's "globally influential".** Folding in two directions does make genuinely two-way patterns, ones no walk around a
  single cycle produces, and at some sizes they are the only way the arrangement stays open. But they are the patterns with the least
  influence: in them no copy fixes any other. Influence that reaches across every size, a whole arrangement locked, still runs around
  cycles: thin strips, and the arithmetic of short steps. A pattern whose influence is both unbounded and two-way would need increments
  that hold a whole line, as Ledrappier's law does; none of the 45 harmonies has them.
- **For the knots-alone thread's window bonds** (`COMMON-FOLD-20261112-001`: travelling found on two-shift bases but not certified by
  doubly periodic states up to period 8). Related, not the same object: the states here are doubly periodic (states of a finite
  repeat) with no shorter repeat, while that thread's missing certificates are states of the endless base that no small doubly
  periodic state reproduces. The tiling reading gives one cause for the latter: a height function whose slope is not a whole number
  repeats only on repeats whose sizes fit the slope, so small certificates can miss it. Whether base 16's window bonds are such
  tilings is untested.

## Assumptions

A70 used; A75 (Assumed) used; A76 (the knots-alone thread's reading of global influence) is close to this epic's reading of influence
as locking and ties, and is unchanged. Added: A77, a walk around one cycle read as a state that repeats along a short step.

## Corrections

None. (A progress message in the thread said 11 harmonies for the 78 cells; it is 10, edited in place.)

## In the owner's words

Tie copies of a pattern to each other across two directions with straight ties, and it behaves exactly like two separate rings. Tie
them with a knot that reaches one step each way, and genuinely two-dimensional patterns appear, ones that never repeat along any
step, and sometimes they are the only thing keeping the whole from locking. For one pattern they are tilings, and a slope rule decides
when the whole locks. But these two-dimensional patterns carry no influence: where only they exist, no copy pins any other. The
influence that reaches across every size still runs around cycles.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — locks across two shifts | **Status:** Successful, referee pending | unmixed knots reduced to rings (proved); two-way states found and checked; influence still cyclic |
| Local direction — two-shift arrangements | Continue | the tiling rule is checked, not proved; no linear increments yet |
| Broader exploration — G17's census | Known alternatives | the knots-alone thread's travelling bases; random meeting patterns |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | where two-way influence can and cannot come from, natively |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Influence beyond cycles: a law whose increments hold a whole line | 3/3 — Major | 2/3 — Testable | compute the increments of the odd harmonies (periods 61, 73, 193, whose steps are closed under fourth roots of 1) and of other stitch orders and two-way knot shapes → a line inside, and lock sets of Ledrappier's kind, or none | Selected · awaiting go-ahead |
| 2 | Prove the slope rule | 2/3 — Substantial | 3/3 — Ready | for `0011 + 01`: every non-constant state is a tiling of the 0011 orbit, and every polygon point is realised → the lock set at every size | Alternative · deferred |
| 3 | Window bonds as tilings (with the knots-alone thread) | 2/3 — Substantial | 2/3 — Testable | on base 16 and the travelling bases, find a height function with a slope polygon → window bonds explained, or not | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained, with G8; no goal change). **Assumptions:** A77 added; A70, A75,
A76 unchanged. **Basket:** #1 to #3 recorded. **Advisor:** consulted twice before the freeze (the ring rule and the corner-knot test;
then the design, which it sent back: it widened the explained family to states repeating along a short step, gave the triple test and
the Ledrappier control's sizes, and proposed "line knot / corner knot", which I replaced by unmixed and mixed knots because those are
words for a drawn space).
