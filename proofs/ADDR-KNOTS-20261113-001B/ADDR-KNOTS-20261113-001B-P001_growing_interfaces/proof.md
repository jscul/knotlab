# Growing interfaces: shared lists, one placement, finite types

Proof note of `ADDR-KNOTS-20261113-001B` (epic `ADDR-KNOTS-20261113-001`; G17, with G1), 2026-11-13, written by Claude at the
coordinator's go-ahead before the census of `ADDR-KNOTS-20261113-001A` ran, and revised after the advisor model's review of the
frozen design (`research/ADDR-KNOTS-20261113-001/advisor_review_answer.md`). The canonical K1–K3 test is unchanged; every knot below
is a three-place not-all-equal knot on three distinct distinctions. **Referee pending.**

## Why

`NEST-COUNT-20261112-001` proved that every nested pattern of the A79 language is finite-state, because each nested copy meets the
rest through three distinctions, and read the contrast with the plane as "the interface size is what separates decidable nesting
from undecidable" (an interpretation). The owner's recursion picture asks for nested parts that depend on the larger pattern. This
note settles, before any census, what two natural ways of letting a copy meet a growing number of its container's distinctions do
by construction.

## 1. Shared lists stay finite-state (Lemma A)

**The language.** A description of the A79 language (`SHORT-DESC-20261112-001`'s `dlang.py`: definitions with ports, own
distinctions, calls of K, of earlier definitions and of SELF, each call on distinct distinctions, to a depth t), with h **lists**
added. A self-holding definition may also make three new kinds of call:

- **enlist (p, c):** its own distinction p goes on list c for every copy nested inside this copy (its descendants);
- **list knots**, read against the members of the lists this copy sees: (c; p, q), a knot (u, p, q) for every member u of list c;
  (c, c′; p), a knot (u, u′, p) for every two distinct members u of c and u′ of c′; (c, c′, c″), a knot on every three distinct
  members, one from each list. The lists named may coincide (c = c′ is allowed). A knot whose three distinctions are not distinct
  (a member that is also one of p, q) is skipped.

A copy **sees** the members enlisted by the copies that contain it (its ancestors), never its own or a sibling's. So the number of
the container's distinctions that a copy's knots touch grows with depth, without bound.

**Lemma A.** For every definition D and depth t, whether a copy of D at depth t, with everything nested inside it, allows a state,
given the values on its ports and on every list member it sees, depends on the members only through its **profile**: for each
nonempty set S of lists and each value b, the number of seen members other than its ports lying on exactly the lists S with value
b, capped at 3, together with the set of lists each port lies on (a port can be a member, enlisted by an ancestor and passed down).
So what a definition allows at depth t is a set R_t(D) of pairs (port values, profile), a subset of a fixed finite set, and
R_t = Φ(R_{t−1}) for a fixed map Φ built from the description. Hence, as in `NEST-COUNT-20261112-001` T1: life at depth t is
eventually periodic in t, with preperiod plus period at most the number of possible tuples (R(D))_D; the bottomless pattern is
decided by a greatest fixed point; and the top reads depth only modulo the period. *Proved.*

*Proof.* (i) A list knot placed by the copy holds or fails according to the values of the members it names and of the copy's own
distinctions. Each form names at most three distinct members, and the forms quantify over all members of the named lists, so
whether every knot of the form holds depends only on which (lists held, value) combinations occur, and with what multiplicity up
to 3 (three distinct members of one combination are needed only by the third form with c = c′ = c″), with the ports' own values and
lists known separately because a knot skips a member that coincides with one of its own places. That is the profile. (ii) A child
copy's profile is computed from the parent's profile, the parent's values, the parent's newly enlisted distinctions, and the call's
binding (which of the parent's distinctions become the child's ports, since a child's profile leaves its own ports out and records
their lists): a function of finite data of the parent. *(Clarified after the referee: a seen member that is not a port lies outside
the copy's distinctions, so no call can bind it to a port or an own distinction of the copy; only ports can coincide with members.)*
(iii) Given the parent's values, two children's subpatterns share nothing
through the lists (each sees only its ancestors' members), so they are independent, exactly as SELF copies are in the A79 language.
(iv) So the set of (port values, profile) under which a depth-t copy of D lives is computed from the same sets for the definitions
it calls at depth t − 1 (and the knot at depth 1) by a fixed map. The domain is finite, so the sequence R_t is eventually periodic;
the fixed-point statements are `NEST-COUNT-20261112-001`'s T1(b) word for word, with the profile carried alongside the port values.
∎

**What follows.** A copy can meet an unbounded number of its container's distinctions and the pattern is still finite-state. What
keeps it finite is that the copy treats all members of a list alike: it can tell apart only a bounded number of different ways of
being met. So the size of the interface is not what separates decidable from undecidable nesting; the number of different ways a
copy can be met is. *This narrows NEST-COUNT's reading (logged in `docs/CORRECTIONS.md`, Narrowing, for the list forms above only).*
The classical form of this is the literature's clique-width and rank-width (Courcelle, Makowsky and Rotics 2000; Courcelle and Oum
2007): bounded rank keeps monadic second-order questions decidable; Lemma A is the plain not-all-equal case of it, known in kind.

**Direct influence by construction.** If the top enlists a distinction u₀ on list c and every self-holding copy places a knot form
on c, then at every depth a knot holds u₀ together with that copy's own distinctions: influence across depth at one knot, put in by
the list, as a carried top port is (A81).

## 2. Knots placed by address maps

**The object.** An **address** is a word over the letters {0, 1}; **level n** is the set of addresses of length n. An **address
map** is the map on addresses defined by a state of an invertible finite automaton (the literature's states of a Mealy automaton,
which define automorphisms of the tree of words), or a product of such maps: it reads an address from its first letter, keeps or
swaps that letter, and hands the rest of the address to a next map chosen by the letter read. A **placement** is a triple
(g₁, g₂, g₃) of address maps; at level n it places the knot {g₁(x), g₂(x), g₃(x)} for every address x of length n whose three
images are distinct. Address maps keep length and act on first letters before later ones, so dropping the last letter of every
address sends level n + 1's knots onto triples of level n.

**Proposition B0 (one placement on two letters always lives).** For any three automorphisms g₁, g₂, g₃ of the binary tree of words,
the level-n pattern of the single placement (g₁, g₂, g₃) allows a state at every level n. *Proved.*

*Proof,* by induction on n. Each gᵢ either swaps the first letter of every address or of none (its root letter permutation σᵢ). If
the σᵢ are not all equal, the three images of every address do not all have the same first letter; give every address its first
letter as its value, and every knot holds both values. If they are all equal, every knot lies inside the addresses with one first
letter h, and those knots are the level-(n − 1) pattern of the single placement (g₁|_a, g₂|_a, g₃|_a) on the remaining letters,
where a = h ⊕ σ is the first letter read and gᵢ|_a is the map handed the rest; the two halves share no knot. Level 1 has two
addresses and no knot. ∎

A second proof (the advisor model's): with y = g₁(x) the knots are {y, g y, g′ y}; every cycle of a permutation of a level of the
binary tree has length a power of two, so the cycles of length at least 2 are even, an alternating value along a cycle extends along
shortest paths to it, and the cycles of length 1 (fixed addresses) give triples with a repeat, which are not knots.

**Remarks.** (a) *First-letter settled.* The first case of the proof needs no induction and no single placement: if in every
placement of a description the three root permutations are not all equal, the first letter is a state at every level, whatever the
number of placements and the knot density. *Proved.* More generally a state of level k lifts to every later level (each address
takes the value of its first k letters) whenever no placement maps a length-k prefix to a triple with a repeat on which that state is
constant. (b) The proposition needs one placement or remark (a): with several placements the root letters can disagree from one
placement to another, and patterns die: the exploratory run in `research/ADDR-KNOTS-20261113-001/exploratory/` found 336 of the
5,832 three-state automata with all four triples of {identity, three state maps} dying within level 10 (*computed, exploratory, not
registered*). (c) It needs two letters. On seven letters the single placement (e, a, a³), with a adding 1 modulo 7 to the first
letter and leaving the rest, places on every seven addresses that differ only in their first letter the knots {x, x + 1, x + 3},
which is the Fano pattern (the difference set {0, 1, 3} modulo 7), so it is dead at every level. *Proved; checked.* (d) In general a
smallest dead pattern needs at least as many knots as distinctions (Seymour 1974), and one placement places at most one knot per
address, so with one placement only an exactly balanced dead part can occur; whether one occurs on three to six letters is open (on
three letters with two state maps none to level 6, exploratory).

**Where a tail class meets the rest.** The addresses sharing their last k letters v form a **tail class** (the literature's tile):
g(uv) = g(u) · g|_u(v), so each map acts on the free first letters as at level n − k whatever the tail, and a knot **joins** the
class to the rest when its three addresses do not all share the tail. *(Corrected after the referee: the map's section at u decides
the output tail, so which knots stay inside the class, as well as which join it, can depend on the tail.)* That happens only where some relative map gⱼgᵢ⁻¹ changes the
tail, so the number of joining knots is bounded above by how many addresses of each length hand a relative map a non-identity one
(the literature's activity, Sidki 2000): bounded activity of the relative maps gives classes joined by a bounded number of knots at
every level (the literature's finitely ramified case), polynomial activity a number growing at most as a power of the level,
exponential activity at most exponentially. These are upper bounds only: maps can cancel, and a description whose state maps are
exponentially active can have no joining knot at all. ~~A class's inner knots are the same for every tail; how it is joined to the
rest depends on its tail.~~ *Withdrawn 2026-11-13 after the referee (Block for the sentence; logged in `docs/CORRECTIONS.md`): with
sw = [1, 0], d0 = [1, 0], d1 = [1, 1] and the one placement of (1,), (0, 0), (1, 0), level 4 has 14 knots; the tail classes 00 and
01 hold no inner knot, while 10 and 11 each hold two. A map's prefix action is independent of the tail; its section decides the
output tail, so both a class's inner knots and its joining knots can depend on the tail.* Bartholdi 2022 (Groups Geom. Dyn.) proved the domino problem decidable in the bounded case and undecidable
on a linear-activity example, and conjectured, for contracting groups, decidable exactly when finitely ramified. *Known.* Whether
the not-all-equal law in the bounded case is finite-state by Bartholdi's construction, applied to knots instead of edges, is expected
but not proved here.

## 3. Finite types (a remark, unchecked)

Let definitions take definitions as arguments (the literature's higher-order recursion schemes), every definition with a bounded
number of ports. A ground definition denotes a relation on its ports; a definition of higher type denotes a function between finite
sets of such denotations, again a finite set. If depth t is the number of unfoldings, each depth replacing every recursive call by
the definition at depth t − 1, then the denotations at depth t are a fixed function of those at depth t − 1 on a finite set, so life
is eventually periodic in t. *My argument, by hand; the referee found it sound for depth counted in unfoldings (narrowed: the
statement is about that depth measure only).* The advisor model held the opposite view (decidable
but not periodic in depth). It may be right if depth is measured instead as the longest chain of nested copies in the expanded
pattern, which higher-order schemes can make grow like 2^t, so that a fate read along that measure need not repeat.

## Prior work

Treewidth and hyperedge replacement, clique-width and vertex replacement (Courcelle and Engelfriet, *Graph Structure and Monadic
Second-Order Logic*, 2012); Courcelle, Makowsky and Rotics 2000; Courcelle and Oum 2007; Seymour 1974 (on minimal non-two-colourable
hypergraphs); Sidki 2000 (activity); Bartholdi 2022 (*Monadic second-order logic and the domino problem on self-similar graphs*);
Barbieri and Sablik 2016; Bondarenko et al. 2008 (groups of three-state two-letter automata). **Ours:** the not-all-equal law on these
patterns, Lemma A's profile argument in this language, B0's first-letter induction and remark (a), and the narrowing of NEST-COUNT's
reading. Classification: known in kind (Lemma A, the remark on finite types), known-with-delta (B0 and its limits).

## Checks

`check.py` (run `.venv/bin/python -B check.py`): B0 on every automaton with at most two states and every triple of words of length
at most 2 in its state maps, and on 2,000 random (three-state automaton, triple) pairs, levels 1 to 10, by SAT; the Fano placement
dead at levels 1 to 4 on seven letters. Lemma A, remark (a) and §3 are by hand only.
