# The sphere's count needs exponential size in bounded-depth Frege

Status: Proved by hand from published lower bounds and the program's reductions. The new reduction step and its composition with
`COUNT-TFNP-20261107-001A` are checked in `check.py`; the sphere step is `FLAT-STATES-20261107-001B`'s, checked there.

Ticket `COUNT-SYSTEMS-20261110-001A`, 2026-11-10.

## Standard statement

- **The count.** NAE(K_k) is the Kasteleyn-signed not-all-equal formula of the octahedral knot sphere K_k: n = 4k² points, one variable
  each, and two 3-clauses per line (`COUNT-NOTE-20261107-001`). Its false-clause search problem, "find a violated line", is the
  sphere's count.
- **Bounded-depth Frege.** Depth-d Frege: Frege proofs whose formulas have depth at most d over ∧, ∨, ¬.
- **LeftPigeon_N.** Pigeons 0, …, N, holes 1, …, N, maps f (pigeons to holes) and g (holes to pigeons) given in binary; a solution is a
  pigeon x with g(f(x)) ≠ x. It is total because f cannot be injective.
- **Bijective PHP.** onto-FPHP_N is the unary CNF in variables p_xh (pigeon x in hole h): every pigeon in a hole, every hole holding a
  pigeon, no pigeon in two holes, no two pigeons in one hole.

**Theorem.** For every d there is ε_d > 0 such that every depth-d Frege refutation of NAE(K_k) has size at least exp(n^{ε_d}) for all
large k.

## Nearest known result

- **Pigeonhole lower bounds.** Depth-d Frege refutations of onto-FPHP_N need size exp(N^{ε_d}) (Ajtai 1988; Pitassi, Beame and
  Impagliazzo, *Computational Complexity* 3, 1993; Krajíček, Pudlák and Woods, *Random Structures & Algorithms* 7, 1995; Håstad improves
  the exponent to Ω(1/d) for graph versions, FOCS 2023 and *TheoretiCS* 2025).
- **Decision-tree reductions and proof systems.** A reduction of search problems by decision trees of depth t turns a refutation of the
  target's formula into one of the source's formula at a cost of 2^{O(t)} per line, in systems closed under such substitutions (the
  framework of Göös, Hollender, Jain, Maystre, Pires, Robere and Tao, *Separations in Proof Complexity and TFNP*, 2022). Bounded-depth
  Frege is closed under them, with the depth raised by 2.
- **Where the count sits.** It is PPADS^dt-complete (`COUNT-TFNP-20261107-001B`), so every PPADS^dt problem, LeftPigeon among them
  (PPADS^dt is unchanged when Sink-of-Line is replaced by LeftPigeon), reduces to it.
- **Sperner's lemma.** Dantchev, "On the complexity of the Sperner lemma" (CiE 2006, LNCS 3988), reduces the pigeonhole principle to
  Sperner's lemma and shows that it has no short constant-depth Frege proofs (only the abstract was read here; its encoding and exponent
  are not known). With `FLAT-STATES-20261107-001B`'s depth-2 reduction of grid Sperner to the sphere, a superpolynomial bound for the
  sphere follows already, for Sperner encodings reducible to one-sided Sperner_m. Buss (*TCS*, 2006) does the same for Hex.
- **Classification.** Known-with-delta. The lower bound is expected and close to Dantchev's; the delta is a self-contained chain for
  this formula through LeftPigeon and SINK, with explicit sizes (N about n^{1/4}) and an exponential bound at every depth.

## Proof

**Step 1: from the unary to the binary pigeon (standard).** Substitute each bit of f(x) by the disjunction of p_xh over the holes h whose
binary expansion has that bit, and each bit of g(h) by the disjunction of p_xh over the pigeons x whose expansion has it. Under
onto-FPHP_N's axioms, "the bits of f(x) spell h" is equivalent to p_xh: for each other hole h′ some bit differs, and p_xh′ with the
functionality axioms falsifies that bit's disjunction. Likewise "the bits of g(h) spell x" is equivalent to p_xh, using the hole axiom
and injectivity. So each clause of LeftPigeon_N, "if f(x) = h and g(h) = z then z = x", becomes, after substitution, a formula derived
from onto-FPHP_N's axioms in depth 3 and size poly(N), and a depth-d refutation of LeftPigeon_N of size s gives a depth-(d + 3)
refutation of onto-FPHP_N of size s·poly(N).

**Step 2: LeftPigeon reduces to SINK.** Put succ(u) = f(u) on the nodes 0, …, N (hole h is node h) and pred(v) = g(v) for v ≥ 1, with
node 0 given no predecessor, and drop a self-loop (a node u with f(u) = u = g(u)), which is neither a sink nor a source. Beame et al.'s
SINK answers are a sink v ≠ 0, or 0 when 0 is not a source. A sink v has an in-edge and no out-edge, so g(f(v)) ≠ v. If 0 is not a source
its out-edge is missing, so g(f(0)) ≠ 0. Each pointer is one value of f or g, read by a decision tree of depth O(log N). Check 1 confirms
it on every instance with N ≤ 3 (5,258 instances, 7,218 answers).

**Step 3: SINK reduces to the count.** `COUNT-TFNP-20261107-001A` reduces SINK on N + 1 nodes to one-sided grid Sperner of side
m = O(N²): each vertex's colour is a function of O(1) pointers, and each counterclockwise full triangle sits at a port whose node, read
from O(1) pointers, is a SINK answer. `FLAT-STATES-20261107-001B` reduces one-sided Sperner_m to the count on K_k, k = 2m + 4: each point
reads at most two colours, and each violated line lies in a counterclockwise full triangle. Composed, every point of K_k is a decision
tree of depth O(log N) over LeftPigeon_N's bits, and every violated line decodes, by a tree of the same depth, to a pigeon x with
g(f(x)) ≠ x. Check 2 composes steps 2 and 3's first half on every instance with N = 2 and 40 with N = 3 (grids of side 228 and 336): all 144
counterclockwise full triangles decode to violations.

**Step 4: the transfer.** Take a depth-d Frege refutation of NAE(K_k) of size s and substitute each variable by its decision tree,
written as a DNF of size 2^{O(log N)} = poly(N): this raises the depth by 2 and gives a refutation of the substituted clauses. Each
substituted clause depends on O(log N) bits of LeftPigeon_N. Wherever it is false, its line is violated, and the decoding tree names a
pigeon x with g(f(x)) ≠ x, a clause of LeftPigeon_N falsified there. So each substituted clause has a tree-like derivation of size
poly(N) from LeftPigeon_N's clauses, by case analysis on those bits. This gives a depth-(d + 2) refutation of LeftPigeon_N of size
s·poly(N).

**Conclusion.** With step 1, onto-FPHP_N has a depth-(d + 5) refutation of size s·poly(N). Since n = 4k² = O(m²) = O(N⁴), the pigeonhole
lower bound gives s ≥ exp(N^{ε_{d+5}})/poly(N) ≥ exp(n^{ε_{d+5}/5}) for large N. ∎

## Remarks

- **Sizes.** The constants are those of the pigeonhole bounds, with N about n^{1/4}. Resolution's 2^{Θ(√n)} (`SPHERE-SIZE-20261107-001`)
  is depth 1; here every fixed depth is exponential, but with a smaller exponent.
- **What does not transfer.** Cutting planes and Res(⊕) are not closed under decision-tree substitution, and cutting planes refute the
  pigeonhole principle in polynomial size, so this route says nothing about them (`COUNT-SYSTEMS-20261110-001B`).
- **The table of `TWO-ROUND-BRIDGE-20261106-001`.** Its row for bounded-depth Frege now reads exponential.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Step 2: every SINK answer of the left-pigeon map is a left-pigeon violation, every f and g with N ≤ 3 | pass: 5,258 instances, 7,218 answers |
| 2 | Steps 2 and 3 composed with `COUNT-TFNP-20261107-001A`'s grid colouring: every counterclockwise full triangle decodes to a violation | pass: 112 instances, 144 triangles |

## Nonclaims

- **The pigeonhole lower bounds and the substitution steps are cited and argued, not formalized.**
- **No lower bound for AC⁰[p]-Frege, cutting planes or Res(⊕)** is claimed.
