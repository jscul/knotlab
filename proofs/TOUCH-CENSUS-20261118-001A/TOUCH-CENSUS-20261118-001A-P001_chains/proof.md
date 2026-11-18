# Why chains of offshoots decide the cheapest growth's dimension

## Standard statement

Under the least count rule of the complete-round joining policy on even-parity constraints, started from any finite set of
constraints: a round can be unavailable only in the first round; extra variables are added only at one-parent constraints of demand
at most one and, through a single forced relay, at unimplied constraints of demand zero; each such one-parent constraint of demand
one starts a chain that never ends. The conjectured rule (tested by ticket B) is that the dimension is the largest set of chains
started together with one common partner, and one when the growth regrows without starting any.

## Nearest known result

`FRESH-COUNT-20261118-001A` (Theorems 1 and 4), `FIRST-KNOT-20261118-001A` (Lemma 1, Theorem 3, Proposition 4).
[Design](../../../research/TOUCH-CENSUS-20261118-001/preregistration.md).

## 1. Stalls only in round 1

**Lemma 1.** Under the fewest rule no round after the first stalls. *Proof.* A round stalls only when some live junction is in more
groups than it has loose distinctions. A junction of round t ≥ 1 received max(d, 3 − p, 1) ≥ d fresh distinctions, d being the
number of groups of round t + 1 containing it, computed on the snapshot after round t with every new junction counted live; the
junctions that received 0 have demand 0 and no candidates, so removing them from the live set changes no other group. So in round
t + 1 every live junction has at least as many loose distinctions as groups. Only the start knots, whose sizes are given, can fall
short, in round 1. ∎

## 2. Where surplus comes from

**Lemma 2.** Under the fewest rule a new junction gets more fresh distinctions than its demand d only (a) when it is an offshoot
(p = 1) with d ≤ 1, or (b) when d = 0 and its parity is not implied (one fresh distinction, the relay). *Proof.* max(d, 3 − p, 1) > d
only if 3 − p > d or 1 > d; with p ≥ 2 the first means d = 0. At d = 0 with implied parity the rule gives 0. ∎

**Consequences** (from `FRESH-COUNT-20261118-001A` Theorem 4(b) and `FIRST-KNOT-20261118-001A` Theorem 3):
- an offshoot of demand 1 gets one surplus distinction, its own offshoot again has demand 1, and the chain never ends;
- an offshoot of demand 0 whose parity is not implied gets two, and their two offshoots have demand 1 each (a sibling pair);
- a junction of demand 0 with two or more parents and unimplied parity gets one fresh distinction, whose lone offshoot is the case
  above.

So every unbounded growth contains chains of offshoots of demand 1, except growth that regrows its multi-parent junctions without
ever making an offshoot of demand at most 1 (the advisor's ring of five four-place knots, each in two pair-groups: five junctions per
round forever, with no chain).

## 3. The rule, and what is proved of it

Call a **birth** an offshoot of demand 1 whose parent is not itself an offshoot of demand 1, and its **partner** its unique
candidate (the other live child of its parent). Births of one round with a common partner form a class; two sibling births, each
the other's partner, form one class of two.

- *Proved instances.* A sibling class of two grows a copy of ℕ² (`FIRST-KNOT-20261118-001A` Theorem 3). A class of m births whose
  partner is the group of m mutually touching knots of m + 1 places grows m-dimensionally (`FIRST-KNOT-20261118-001A` Proposition 4).
  A single birth grows one chain beside its partner.
- *Conjectured (the frozen rule).* For every finite start, the dimension of the fewest growth is the largest class ever formed if
  there is a birth; 1 if the growth runs forever without a birth; 0 if it closes.
- *Not proved.* That classes born in different rounds, or classes whose partners are themselves candidates of each other, never
  combine into a higher dimension (the advisor's open case).

## 4. The largest dimension within the census

Four mutually touching knots of five places grow four-dimensionally (Proposition 4 of `FIRST-KNOT-20261118-001A` with m = 4). A
class of five births with one partner would need, in round 1, five knots each with exactly two open distinctions, each in one group,
pairwise having common neighbours among the start knots and with none common to all; within five knots of at most five places the
advisor could construct none. The census tests whether any arrangement there exceeds four.

## Verification and evidence

Ticket B grows every distinct connected arrangement of up to five knots of three to five places (26,441) and scores the rule. The
lemmas were written by the thread before the census; the advisor (Fable 5.2) proposed the split rule and the birthless exception.
No independent referee verdict yet.
