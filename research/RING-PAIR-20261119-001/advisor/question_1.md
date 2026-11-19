# Advisor question 1 (RING-PAIR-20261119-001, before the freeze)

Analysis please, not encouragement; I will check it. Background: your two answers in JOIN-GROWTH (parity growth by the complete-round
joining rule under the fewest counts; bare starts give each knot max(3, shared + round-1 demand) bits; return equations for single
rings; two joined rings non-rational).

## What I found (exploration, before any freeze)

**Model H.** Let X be the candidate complex of a bare start: vertices are the knots; for every knot w, the knots sharing a bit with
w are pairwise candidates through w, and X holds the full simplex on them (one block per knot w with two or more neighbours);
each surplus bit at a knot r adds a new vertex joined to r alone. H: the junctions made in round t are the deck orbits of finite
connected vertex sets of size t + 1 in the universal cover of X that contain a knot. The cover is a tree of blocks, so the orbit
series is computed by the block-tree recursion

U(B, z) = y Π_{B' ∋ z, B' ≠ B} Φ(B', z), Φ(B, z) = Π_{w ∈ B, w ≠ z} (1 + U(B, w)),
C(y) = Σ_x y Π_{B ∋ x} Φ(B, x) − Σ_B Σ_{S ⊆ B, |S| ≥ 2} (|S| − 1) Π_{v ∈ S} U(B, v) = Σ_t c(t) y^(t+1)

(dissymmetry of block trees).

**Evidence.** Exact equality, every grown round:
- the bare 5–5 join by a shared bit, rounds 0–15 (16 terms; round 16 is predicted 822,862, your forecast was ~822,800);
- the six two-ring joins of JOIN-GROWTH's census (5–5 shared knot, path of one, with a surplus bit; 5–7, 5–9, 7–7), 13–17 rounds;
- 36 of 36 census starts inside the scope below (single rings with lone knots and surplus bits);
- a brute-force animal count on the cover, by normal forms of walks, agrees to round 11.

Outside the scope, all 100 census starts miss from round 1. The scope is:
- every knot has shared + demand ≥ 3, so no bit comes from the floor;
- surplus bits only at knots of demand ≥ 2;
- round 1 has no group of three;
- no two knots have two common neighbours.

Floor bits renew and nest, which is your renewing offshoot. Earlier, by hand, an infinite pendant path for the renewing offshoot,
with knot-free sets excluded, reproduced the bare hanging pair exactly.

**Consequence.** The series is algebraic, and rational when X has one independent cycle. λ = 1/ρ, the radius of the positive
system:

| Join | λ |
| --- | --- |
| 5–5 bit | 2.6075 |
| shared knot | 2.8683 |
| path of one | 2.4271 |
| with a surplus bit | 2.6881 |
| 5–7 | 2.3816 |
| 5–9 | 2.2412 |
| 7–7 | 2.1855 |

On the model's series to round 220, λ_t = r_t (t/(t − 1))^(5/2) settles at 1/ρ, and with 3/2 it keeps rising. So c ~ C λ^t
t^(−5/2): your −3/2 was the window's. I have published that as a correction to JOIN-GROWTH.

## The planned frozen test

Fifteen fresh in-scope starts, none grown before:
- 5–5 through a path of two;
- 5–7 by a shared knot, and through a path of one;
- chains of three rings of five, with the middle ring's joints two apart or neighbouring;
- three rings of five through one knot;
- 7–7 joined twice (0–7 and 3–10);
- 5–5 with surplus bits at far knots;
- 9–5 by a shared knot;
- a ring of five with a second cycle through a path of four knots from knot 0 to knot 2;
- a ring of five carrying a lone knot with two surplus bits, joined to a ring of seven;
- 7–7 through a path of one;
- three rings of five each joined to one central knot;
- a single-ring control (a ring of nine with lone knots carrying 2 and 3 surplus bits, and a surplus bit);
- 5–5 joined by two paths of one.

Prediction: the grown counts equal H's at every round grown (80 rounds, 250,000 junctions or 900 s), with three out-of-scope
starts (groups of three in round 1) grown for the record without prediction.

## Questions

1. Is H plausible as a theorem, and what is the proof route? Groups are local, so the growth lifts to the cover. On a tree of
   blocks, the junction sets are the connected sets, the parents are the sets less one non-cut vertex, the groups' validity rule
   is what makes a triangle one junction, and round = size − 1. Which step is weakest?
2. Which in-scope start is most likely to break H? Propose one or two to add as falsifiers.
3. Known mathematics, to cite once: lattice animals or connected subgraphs on trees; the dissymmetry theorem; positive algebraic
   systems (Drmota–Lalley–Woods) and the t^(−3/2) rooted versus t^(−5/2) unrooted laws; growth of free groups. Is anything closer,
   such as animals on Cayley graphs of free groups or graphs of groups?
4. The owner calls this direction "a logic based fractal with emergence as the guiding principle". In two or three plain sentences,
   what does "a rule that refers to itself" mean here, without overclaiming? Is "fractal" defensible in any precise sense
   (self-similar recursive structure of the cover, the generating function's fixed-point equation), or should it stay in quotation?
