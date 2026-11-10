# Renamings, transplants and flips in place

Status: Proved

Ticket `PLACE-FLIP-20261110-001A`, 2026-11-10, the challenge of A59. Pre-registered in commit 75f8e2b79 before any run of ticket B's
census; L1 to L5 were sketched by hand while the registration was written (disclosed there). L6 was found after the census and is
not pre-registered.

## Setting

- **Names and states.** As in `BARE-NAMES-20261110-001A`: a countably infinite set of names with no letters, a symmetric neighbour
  distinction for each pair of names, a value in {0, 1} for each name, and count laws in which every place has exactly four
  neighbours. T is the set of pairs (value, number of neighbours of value 1) that occur in allowed states.
- **Renamings.** A renaming changes x to x ∘ π for a permutation π that moves finitely many names.
- **Flips in place (frozen).** A value s(u) is flipped in place at x by a finite change of values alone, every neighbour distinction
  kept, that is allowed, flips s(u), is not a renaming, and is minimal: no allowed change of a proper subset of its values flips
  s(u). A neighbour distinction is flipped in place likewise, with neighbour distinctions alone changed and every value kept. A
  knot of n(u, v), s(u), s(v) is native in place at x when all three are flipped in place there.
- **Worlds.** A world of finite components (a dust world) is made of infinitely many copies of finitely many finite coloured boards.
  A tree world is an allowed state on four-regular trees, such as the universal cover of a finite coloured board.

## L1. Renamings in a world of finite components

**Statement.** In a world of finite components, a finite change is a renaming exactly when it keeps the multiset of isomorphism
types of the components it touches. So a change of values confined to one copy of (B, c) is a renaming exactly when its new
colouring is an automorphic image of c.

**Proof.**
- **Only if.** Let x′ = x ∘ π, with π moving finitely many names. Every touched component holds a moved name: a changed value sits on a
  moved name, and every changed neighbour distinction has a moved end. π is an isomorphism from x′ to x that is the identity outside
  the finitely many components holding moved names, so it maps those components of x′ isomorphically onto those of x. The untouched
  ones among them are the same in x and x′, so they cancel, and the touched components have the same multiset of types.
- **If.** If the types agree, choose an isomorphism between the touched components of x′ and those of x. Extended by the identity,
  it is a permutation π moving finitely many names, and x′ = x ∘ π.
- **One copy.** A change of values on one copy of (B, c) touches that copy only, so it is a renaming exactly when (B, c′) ≅ (B, c), that
  is, when c′ = c ∘ σ for an automorphism σ of B. ∎

## L2. No renamings on four-regular trees

**Statement.** In a world whose components are four-regular trees, no change of values alone, other than no change, is a renaming.

**Proof.** If x′ = x ∘ π and x′ has the same neighbour distinctions as x, then π is an automorphism of the forest that moves finitely
many places. Take any place v. All four branches at v are infinite and π moves only finitely many places, so two of them hold places
w₁ and w₂ fixed by π. v lies on the unique path from w₁ to w₂, which π maps onto the unique path from π(w₁) = w₁ to π(w₂) = w₂, that
is, onto itself with its ends fixed. So π fixes v. Hence π is the identity and x′ = x. ∎

The degree matters: on a tree with leaves, two leaves of different values at one place can be exchanged.

## L3. The switch flips a neighbour distinction in place

**Statement.** Let {u, v} and {u′, v′} be edges with u, v, u′, v′ distinct, s(u) = s(u′) and s(v) = s(v′), and {u, v′}, {u′, v} not
edges. The switch replaces the first two edges by the second two (`BARE-NAMES-20261110-001A`, T5). It flips n(u, v) in place in
two cases: when the two edges are the copies of an edge that lies on a cycle, in two copies of a finite component; and in a tree
world, when the switch closes a cycle.

**Proof.**
- **Allowed.** Each of the four places trades a neighbour for one of the same value (T5).
- **Minimal.** Every allowed change of a proper subset of the four distinctions that removes {u, v} leaves a place whose number of
  neighbours is not four.
- **Not a renaming.** In the first case the two copies become one connected double cover with twice as many places, so the multiset
  of component types changes (L1). In the second the new state has a cycle and the old one has none, and a renaming would be an
  isomorphism between them.
- **Such a partner exists on trees.** In the universal cover of a connected finite board, a walk that never steps straight back reaches
  every oriented edge of the board. So beyond v, at depth at least 2, lies a copy u′ → v′ of the oriented edge u → v, and switching it
  with {u, v} reconnects the part between v and u′ to itself, which closes a cycle. ∎

## L4. Transplants: why excluding only renamings is not enough

**Statement.** When values and neighbour distinctions change together, a place can be moved from one region to another by a finite
change that is not a renaming. For example, take a law in which no allowed state has an edge between a 0 and a 1, a place u of value
0 whose four neighbours split into two pairs that are not already neighbours, and two disjoint edges of an all-1 component. Join u's
former neighbours in those two pairs, give u the value 1, remove the two edges and join u to their four ends.

**Proof of the example.** u's former neighbours each trade u (value 0) for another former neighbour (value 0); the ends of the two
removed edges each trade a neighbour of value 1 for u, now of value 1; u has four neighbours of value 1. Every place keeps an
allowed pair. In a world of finite components, the all-0 component loses a place (it may also split) and the all-1 component gains
one, so the multiset of component types changes (L1). In a tree world the change closes a cycle on the all-1 side, which no
renaming of a forest does. ∎

So a count that excludes renamings alone still lets values flip cheaply. The frozen definition therefore holds the board fixed while
values change, and the values fixed while neighbour distinctions change.

## L5. Cascades on trees

**Statement.** Suppose no allowed state has an edge between a 0 and a 1 (T ⊆ {(0, 0), (1, 4)}), or the law is law 48 (a 0 has four
neighbours of value 1, a 1 none). Then in any world whose components are infinite, no finite change of values alone flips a value.

**Proof.** In both cases every neighbour of a flipped place must flip too: with no mixed edge, a flipped place's new value must be
shared by each neighbour; in law 48 a 0 needs four neighbours of value 1 and a 1 four of value 0. So the set of flipped places is a
union of whole components, and a component of an infinite world is infinite. ∎

## L6 (after the census, not pre-registered). Flips on trees are decided by least fixed points

**Statement.**
1. **One cover.** In the universal cover of a finite coloured board (B, c), whether s(u) is flipped by a finite change of values alone
   is decided by a least fixed point over B's oriented edges.
2. **Some tree world, one place.** Whether some tree world lets a place of a given value flip that way is decided by a least fixed
   point over the types in T.
3. **Some tree world, an edge.** Whether some tree world has an edge {u, v} such that one finite change of values flips s(u) and
   another flips s(v) is decided by a least fixed point whose states carry both changes at once.

In each case a flip found is a flip in place: on a four-regular tree no change of values is a renaming (L2), and any allowed change
contains a minimal one flipping the same value.

**Proof.**
- **States.** For an oriented edge p → x and flips f_p, f_x in {0, 1}, let G(p → x, f_p, f_x) say that the subtree beyond x can carry a
  finite change of values, with x flipped exactly when f_x = 1, that keeps every place of the subtree allowed when p's flip is f_p.
- **The fixed point.** G holds when f_p = f_x = 0 (no change). It holds for (f_p, f_x) when some flips f_y of x's three children have
  G(x → y, f_x, f_y) and x's new pair (value c(x) ⊕ f_x, number of 1s among its new neighbours) lies in T.
- **Exact.** A finite change gives a finite derivation, since beyond its last flips every state is (1, 0) or (0, 0) and then (0, 0).
  A finite derivation gives a finite change. So the least fixed point is exactly the set of states with finite completions.
- **The root.** s(u) flips iff some flips of u's four neighbours satisfy G(u → y, 1, f_y) and u's new pair lies in T.
- **Part 1.** In the universal cover of a simple board, the subtree beyond an oriented edge p → x, and p's value, depend only on the
  edge of B under it, so G is computed over B's oriented edges.
- **Part 2.** The same recursion runs over abstract states (value of p, f_p, type of x, f_x). The types of x's children are chosen among
  those in T that accept x's value, with their old values adding up, with p's, to x's count. The base case is sound because every
  type of T that accepts its parent's value extends to an allowed infinite tree: T is the set of pairs that occur, and the universal
  cover of a state in which a pair occurs can be copied branch by branch. A tree world is exactly such a choice at every place.
- **Part 3.** The states of part 2 carry two pairs of flips, one for each change, over one choice of old types. The root is an edge
  {u, v} whose first change flips u and whose second flips v, each keeping both stars at the edge allowed. ∎

## Checks

`check.py` (result in `result.json`), all passed:
- **Dust witnesses (L1).** For all 90 laws, the census's 84 witnesses and the six found by hand (`witnesses.json`), a minimal change
  of values flipping each end of the edge is found again by brute force, and its colouring is not isomorphic to the old one as a
  coloured graph, checked with networkx's matcher rather than the census's automorphism code. The six: 2-lifts of the 3 × 3 torus
  (18 places) for laws 36, 44, 144 and 208; a 21-place board with no automorphism, built around an alternating gadget, for laws 40
  and 80 (on the lifts and planted boards first tried, their colourings were unique).
- **The switch (L3)** on every dust witness: allowed, minimal, and joining two copies into one component. In tree worlds the
  neighbour distinction is flipped by L3's argument, not by a computed switch.
- **A transplant (L4)** in law 513, which has no mixed edge: components of 9 and 9 places become 8 and 10, every place stays
  allowed, and the moved place's value flips.
- **Fixed points (L5, L6).**
  - Over all tree worlds, the type-level fixed point finds no flippable value for 58 laws, among them the 31 with no mixed edge and
    law 48.
  - In the covers of the census's frozen colourings (at most 200 per law), the edge-level fixed point makes both ends of an edge flip
    for 26 laws: the 18 the census found within distance 2, and 8 more whose flips reach farther.
  - The joint fixed point of part 3 finds exactly the same 26 laws over all tree worlds. So the six laws whose values can flip but
    not at both ends of an edge (45, 57, 61, 624, 720 and 752) are not native in place in any tree world.
- **The referee's own computations agree:** the depth-2 fixed point matched brute force on 1,326 roots, and the joint recursion found
  none of the six.

## Scope and sources

- **Scope.** Count laws of degree four over abstract names; the 90 knotted one-bit laws of `BARE-NAMES-20261110-001B`; finite
  changes as counted by the frozen definition. No change to the canonical knot test.
- **Sources.** Covering graphs; least fixed points over finite state sets; the 2-switch of graph theory; the rest is elementary.
- **Novelty.** Short consequences of standard facts; folklore risk high. What the epic adds is the reading for the board line.
- **Review.** An independent referee read this proof before publication. It found L1 to L6 sound and asked for the changes made
  here: the four-regular hypothesis in L2, the minimality step and the hypotheses of L3 and its partner edge on trees, the
  hypotheses of the transplant, L5's simpler argument and its hypothesis on T, the missing conditions of L6's part 2, the link from
  "flipped by a finite change" to "flipped in place", and the wording of the Checks. It also proposed the joint recursion of part 3,
  run here in `check.py`.
