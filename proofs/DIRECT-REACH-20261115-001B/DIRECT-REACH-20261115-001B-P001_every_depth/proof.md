# Direct reach at every depth

`DIRECT-REACH-20261115-001B-P001`, epic `DIRECT-REACH-20261115-001`, 2026-11-16. Written by Claude; the advisor model checked the
three arguments before they were implemented (`research/DIRECT-REACH-20261115-001/advisor/proof_answer.md`) and chose the words
(`words_answer.md`). Referee pending. Checks: `check.py` (result in `result.json`). Words follow the
[Intuitions glossary](../../../publication/knotlab/INTUITIONS.md#glossary); **orbit** is the literature's word, here for the
addresses one address is sent to by the maps.

## Setting

As in `LEVEL-REACH-20261114-001`. A description is an invertible automaton (states q with an output flip and two transitions) and a
set of placements, each three terms (w, e) with w a word of at most two states and e empty, 0 or 1. A word acts on addresses letter by
letter: w(xa) = w(x)·w|_x(a), where the **section** w|_x is again a word of states. The depth-N pattern P_N holds, for every address v
of length n ≤ N and every placement, the not-all-equal knot on the members w(v) (e empty) or w(v)·e (skipped at n = N), when the three
are distinct. L_N(k, s) is the least size of a bond of P_N meeting level k and level k + s.

Three facts are used throughout.

1. P_N is a sub-pattern of P_(N+1) (every knot of P_N is a knot of P_(N+1)).
2. P_N allows the complement of each state it allows, so every single distinction is free whenever P_N is alive.
3. **Lemma 0.** If Q is a sub-pattern of P_N, a set constrained in Q is constrained in P_N, and a pair tied in Q is tied in P_N; when
   P_N is alive that pair is a bond of two members. *Proof.* P_N's states are among Q's, and a set of patterns can only shrink. ∎

## Theorem W (blocks of orbits)

The maps of the placements' words generate a group G acting on each level (each map permutes a level). The **block** of an orbit O
of G at level n < N is O with its children, O ∪ O·{0,1}; at level N it is O.

(a) Every knot placed at an address v lies in the block of v's orbit, since each member is w(v) or w(v)·e with w in G.
(b) The orbit of xa lies in O(x)·{0,1}, since g(xa) = g(x)·g|_x(a). So the orbits of level n + 1 split each O·{0,1} into whole orbits,
    and every block below the root has exactly one parent block.
(c) Two blocks share addresses only when one is the parent block of the other, and then they share the child's orbit. The blocks
    containing a given address are its own orbit's block and that orbit's parent block. So P_N is a system of knots on blocks that
    meet only parent to child, with no ring of blocks (the literature's tree decomposition), and the projection of its states onto a
    block, or onto two orbits, is computed exactly by passing allowed assignments from block to block (dynamic programming over the
    decomposition).
(d) The block's knots, up to renaming, depend only on the orbit's **type**: its addresses in an order fixed from one root address,
    and, for each address and each map, the index of the image and the map's section there. The children's types are functions of the
    type. When the orbits have at most m addresses at every level, there are finitely many types.

**Every depth.** With finitely many types:

- **Life.** Let F_r(t) be the assignments of an orbit of type t that extend to its r levels below. F_(r+1)(t) ⊆ F_r(t), since the block
  holds the orbit's own knots, and F_(r+1) is a function of F_r, so F stops changing at some r₀ and stays fixed. P_N is alive exactly
  when F_N(root) is not empty, which is decided for every N by N ≤ r₀.
- **Pairs.** For a top level k, s ≥ 1 and N = k + s + r, the joint assignments of an orbit at level k and an orbit at level k + s are
  obtained from those at s − 1 by one step that, for r ≥ r₀, does not depend on N. The set of all such joint relations is therefore an
  eventually periodic sequence in s; for r < r₀ the last r₀ − r steps use the earlier F. Whether some address of level k is tied to some
  address of level k + s, and whether a three-member bond lies inside two such orbits (constrained, with each pair free in the joint
  relation, which is exact), is decided for every s and every N by finitely many computations.

**Corollary W** (computed, `exploratory/window_tree.py`, orbits of at most four addresses). Of the 146 descriptions of population D,
85 have orbits of at most four addresses at every level (orbit sizes 1, 2 or 1, 2, 4; 2 to 45 types). All 85 are alive at every depth.

| Profile at N = 9, s = 1..4 | Descriptions | Orbits ≤ 4 | Verdict at every depth N ≥ 3 + s, every s ≥ 1 |
| --- | ---: | ---: | --- |
| constant 2 | 34 | 10 | all 10: a tie meets level 3 and level 3 + s, so L_N(3, s) = 2 |
| constant 3 | 66 | 32 | all 32: no tie, and a three-member bond inside two orbits, so L_N(3, s) = 3 exactly |
| [3, 3, 4, 4] | 46 | 43 | all 43: no tie (L ≥ 3); a three-member bond inside two orbits only at s = 1 |

The same verdicts hold from top level 2, except c99d95ae7866… (constant 3; from level 2 a tie at s = 1, then L = 3) and 39079b659d07…
([3, 3, 4, 4]; from level 2 no two-orbit three-member bond at any s).

*Checks.* The joint relations of 510 random orbit pairs at N = 6, and of 510 more at N = 10, equal the projections of the whole pattern
by SAT, and 595 life verdicts at N = 2..8 and 935 at N = 2..12 equal SAT (`exploratory/gate_window_tree.py`). At N = 9 the every-depth sequences give the certified results of
`DIRECT-REACH-20261115-001A` on all 935 (description, top, s) cells: a tie exactly where the certified tie classes span, and L = 3 in
the certified search wherever a two-orbit three-member bond is found with no tie (436 cells); 86 cells have L = 3 from a bond that uses
a third orbit (`crosscheck_window_tree.py`).

## Theorem D (a block's descent)

When the orbits grow (in the 61 other descriptions they are whole levels up to level 8), a few addresses can still carry the top down. Take S_k₀, a
set of addresses of level k₀, and one letter per address at every level, the letters eventually periodic; set
S_(k+1) = {x·c(x) : x ∈ S_k}. The **block** of S_k is the set of knots placed at level k whose members all lie in S_k ∪ S_k·{0,1}.
This is the **descent** of S_k₀ along those letters (the literature's orbital Schreier graph along a rational point of the boundary).

(a) A knot placed at v with x = w_i(v) in S_k has its term j's member at (w_j · w_i⁻¹)(x), so the type of S_k (for each address x and
    each composite g = w_j · w_i⁻¹: the index of g(x) in S_k or "outside", and g's section at x) fixes the block up to renaming. The next
    type is a function of the type and the letters: g(x_i·c_i) = g(x_i)·g|_(x_i)(c_i) lies in S_(k+1) exactly when g(x_i) = x_j and the
    output letter is c_j. "Outside" stays outside.
(b) The blocks of S_k and S_(k+1) share only S_(k+1), and blocks two levels apart share nothing, so the union of the blocks from k₀ to
    k is a sub-pattern of P_N for every N ≥ k + 1, and its projection onto (S_k₀, S_(k+1)) is computed exactly by passing assignments
    down, carrying the assignment of S_k₀ along (the anchor).
(c) The state (type, allowed (anchor, S_k) assignments, phase of the letters, and the states at S_k of any finite readers carried
    along) is a function of the previous state, so it is eventually periodic, and each per-level verdict below is checked for all k
    by checking the levels before the first repeat.

**Finite-reader states.** A finite machine that reads an address letter by letter and outputs a value gives a **finite-reader state**
(the literature's automatic sequence) when its values satisfy every knot placed at every level; this is a safety check on the product
of the machine with the placements' words (`exploratory/automatic_life.py`). Such a state restricts to a state of P_N for every N, and
so does its complement.

**D1 (ties).** If at every level k ≥ k₀ some address of S_(k+1) is tied to an anchor address in the descent, and the pattern has a
finite-reader state, then one tie class meets level k₀ and every deeper level in every P_N (Lemma 0, fact 2), so L_N(k₀, s) = 2 for every
s ≥ 1 and every N ≥ k₀ + s; for k₀ ≤ 3 the same holds from level 3.

**D2 (three members).** If at every level some address y of S_(k+1) either is tied to an anchor address, or lies in a three-member set
constrained in the descent that is either {x, x′, y} with x, x′ anchors or {x, y, y′} with y′ in S_(k+1), and the pair inside one level
({x, x′} or {y, y′}) is shown free at every depth by two finite-reader states with different parities on it, then L_N(k₀, s) ≤ 3 for
every s ≥ 1 and every N ≥ k₀ + s. *Proof.* The set is constrained in P_N (Lemma 0), so it holds a bond; every subset of it that misses
level k₀ or level k₀ + s is a single distinction or the pair inside one level, all free in P_N; so the bond meets both levels and has at
most three members. ∎

**Corollary D** (computed, `chain_ties.py`, `chain_bounded3.py`; at most four addresses, constant letters or two alternating letter
vectors). With D1, 13 constant-2 descriptions have a tie descent, 8 with orbits ≤ 4 (agreeing with W) and 5 with growing orbits, each
with a finite-reader state. With D2, 28 constant-3 descriptions are bounded by 3 at every depth, 21 with orbits ≤ 4 and 7 with growing
orbits.

| Profile | Every depth, every s, from level 3 | By W | By D (growing orbits) | Together |
| --- | --- | ---: | ---: | ---: |
| constant 2 (34) | L = 2 | 10 | 5 | 15 |
| constant 3 (66) | L ≤ 3 (L = 3 exactly by W) | 32 | 7 | 39 |

*Checks* (`gate_chain.py`, all 41 descents): the blocks from the type evolution equal the blocks computed from explicit addresses (every
v of the level, every placement) at levels k₀ to 8; all 521 ties and constrained triples claimed at levels up to 9 hold in the whole
depth-9 pattern by SAT, and every deep pair claimed free has two finite-reader states with different parities at its explicit
addresses; every finite-reader state used satisfies the depth-12 pattern knot by knot.

## Life at every depth

139 of the 146 descriptions have a finite-reader state with at most 5 machine states (`exploratory/automatic_search.py`), so they are
alive at every depth. For the 85 with orbits ≤ 4, Theorem W gives life independently. The certified search of
`DIRECT-REACH-20261115-001A` found all 146 alive at N = 10, 11 and 12.

## What is not proved

- **Constant 2, growing orbits:** 19 of 34. Most are nearly rigid (their tie classes hold most of each level, and in three one tie class
  holds every address below the root at N = 9). Minimal sets of knots forcing u_k ~ u_(k+1) grow with k or spread across levels (exploratory), and no
  descent of at most four addresses carries the tie.
- **Constant 3 exactly, growing orbits:** D2 gives L ≤ 3, not L = 3. A lower bound at every depth needs every deeper address to be free
  with each top address. Finitely many finite-reader states cannot show this in the cases tried: their joint values at a top address
  recur at deeper addresses, where all of them agree, and in all four constant-3 descriptions tried every top address had such a deeper
  match (`research/DIRECT-REACH-20261115-001/separation.py`). Only Theorem W gives exact lower bounds.
- **Half-rate growth:** W shows no tie at any depth for 43 of 46, so L ≥ 3; that L grows past 4 is read only at N = 9 (s ≤ 6 from top 2).

## Dependencies

`LEVEL-REACH-20261114-001` (the census and its pattern builder `pattern.py`), `DIRECT-REACH-20261115-001A` (certified tie classes,
threshold reach and life to depth 12 at N = 9). Standard: exact dynamic programming over a tree decomposition; sections of automaton
maps (self-similar groups).
