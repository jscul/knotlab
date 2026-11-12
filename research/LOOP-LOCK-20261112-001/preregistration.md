# Pre-registration: which loops lock, and overlapping loops

Epic `LOOP-LOCK-20261112-001` (`ENDLESS-BLOCK-20261112-001` direction 1; G17 with G8; program mathematics, group arithmetic), written on
2026-11-12 before any census runs, at the coordinator's go-ahead under the owner's standing mandate. Code frozen with this file in
`proofs/LOOP-LOCK-20261112-001A/LOOP-LOCK-20261112-001A-P001_loop_locking/` (`loop_lib.py`, `check.py`). The canonical K1–K3 test is
unchanged.

## Words

As in `ENDLESS-BLOCK-20261112-001` and the glossary: harmony, one-order stitch, shared and hanging copies, tie class. New, plain: the
**step relation** T of a harmony: T(u, w) when some state v makes (u, v, w) allowed across one knot (the hanging copy quantified away);
T always holds for u = w. Its **girth** g: the length of its shortest round trip that is not standing still (the literature's girth of
the loopless part of a reflexive digraph). A set of copies is **locked** when they are equal, place by place, in every state.

## Settled by hand (before the run; checked with the advisor model)

- **L1 (which loops lock).** A closed chain of k knots, all oriented the same way round with the hanging copy in the middle slot, is
  a closed walk of length k in T; since T stays put at every state, a shorter round trip pads to length k. So **the loop locks exactly
  when k < g**: locking is monotone in k, and "locks at 3 and not at 4" means g = 4.
- **L2 (the open chain is free at every length).** If T has any step u → w with u ≠ w, the walk that stays at u, steps once to w and
  stays there is a state of the open chain of any length with the step at any place: no two shared copies are locked. If T has no such
  step, everything locks, open or closed.
- **L3 (one-orbit harmonies).** If the harmony's states are the shifts of one word, T(w, S^d w) depends only on d, T is the literature's
  Cayley digraph on Z_P with steps D ∪ {0}, and g is the least length of a nonempty sequence from D summing to 0 modulo P. Such a
  harmony never locks at every length: g ≤ P/gcd(d, P) for any d in D. Locking at every length needs T without loops to have no round
  trip at all, which needs several orbits.
- **Overlapping loops (the advisor's, from L1).** A pattern of shared copies not strongly connected never locks. Two loops through one
  shared copy (a figure eight) are independent: each locks as it would alone. Two loops sharing a knot (paths of length 1 from x to y
  and of lengths b₁ ≤ b₂ back) lock together exactly when g > max(1 + b₁, b₂): a loop that fails alone can be locked by a locking loop
  it shares a knot with (the ear rule), but if neither locks alone they do not lock together. Two loops sharing two copies and no knot
  can lock together though each fails alone: the advisor's crossed pair (x → y in 1 knot and back in 3, and x → y in 3 and back in 1)
  creates a round trip of 2 through x and y; and the circulant (n shared copies with steps i → i + 1 and i → i + 2) locks for one
  generator when ⌊n/2⌋ < g, so at n = 2g − 1 each loop fails alone and the union locks, with no round trip shorter than g (a strictly
  collective lock).

## The census (frozen; exact on the range)

- **Rule arm.** The 45 harmonies with P ≤ 16: T and g; closed chains of 2 to 12 knots locked or not, against k < g; open chains of 2
  to 12 knots free or not, against "T has a step".
- **Overlap arm.** The harmonies whose loops lock at some k ≤ 12, and up to 8 others with a finite girth: figure eights (3+3, 3+4,
  3+6, 4+6, 6+6), loops sharing a knot (3+3, 3+4, 4+4, 4+6, 6+6), the crossed pair, circulants of 5, 7 and 9, an open chain of 8 knots
  (the control), the one-shift rings of 4 to 12 knots and the drawn three-copy nestings of levels 1 to 3: locked loops, tie classes,
  copies tied to the root.
- **Cap.** 1 hour and 16 GB per part.

## What counts (frozen)

- **Spread:** a loop that fails alone locked by a pattern it shares knots or copies with. **Collective lock:** two loops that each
  fail alone, whose union is locked (strict if no round trip of the union is shorter than g). These are the answer to "influence that
  depends on how the pattern folds". **Control:** the open chain must have every shared copy in its own class.

## Predictions (frozen; the advisor's, with its confidence)

L1 and L2 on every cell (theorems); figure eights independent (99%); loops sharing a knot follow g > max(1 + b₁, b₂), never
collective (97%); the crossed pair locks on harmonies with g = 4 (95%); strict collective lock in the circulant at n = 2g − 1 for one
generator (90%); some ring locks non-monotonically in n (65%); the nestings' tie share stabilises by level 3 (60%).

## Known mathematics, checked before the freeze

Path consistency and tree-structured networks (Montanari, 1974; Mackworth, 1977; Freuder, 1982; Dechter's *Constraint Processing*):
L2 is the global consistency of a tree network. Homomorphisms into reflexive digraphs and their homotopy (Hell and Nešetřil; Larose,
Tardif and Zádori), circular colourings (Vince; Zhu), tension-continuous maps (DeVos, Nešetřil and Raspaud); voltage graphs and the
cocycle condition on a cycle basis (Gross and Tucker; Zaslavsky); periodic points against higher-block presentations (Lind and Marcus),
tree shifts (Aubrun and Béal), and local consistency that cannot tell a cycle from its cover (Feder and Vardi); zero-sum sequences and
the Davenport constant (Geroldinger and Halter-Koch), and girth of Cayley digraphs (Caccetta and Häggkvist; Hamidoune). So L1 to L3 are
classical in kind; what is tested is their reading for the owner's question.

**Referee.** The background referee thread (referee pending). Assumptions in force: A70, A75 (Assumed). Nothing here bears on P versus
NP.
