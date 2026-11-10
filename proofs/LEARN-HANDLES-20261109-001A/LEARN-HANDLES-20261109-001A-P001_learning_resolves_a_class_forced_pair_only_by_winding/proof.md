# Learning resolves a class-forced pair only by winding

Status: Proved by hand (theorems 1–3). The finite claims are checked by `check.py` (checks 1–3); costs and local rules are computed
(checks 4–5); check 6 is a stress test of `RESIGN-STEER-20261107-001B`'s local rule one size past. Pre-registered in
`research/LEARN-HANDLES-20261109-001/preregistration.md`.

## 1. Setting

Knot spaces on closed surfaces as in `COUNT-SURFACES-20261107-001A`: a two-coloured triangulation T, points the triangles of colour 0,
lines those of colour 1, faces the vertices of T. A signing puts a bit on every side; every side of T borders exactly one line, so sides
and edges of T are the same thing. Under a signing s and a state x a line agrees at one corner or at all three (violated); deg(v) is the
number of agreeing corners at the face v; D is the set of faces where deg is even; E = Σ_v ⌊deg(v)/2⌋. Re-signing side k of line i
toggles the agreement of the line's two corners at the ends of that side, so it toggles both ends in or out of D.

A **dissonance** is a violated line, an over-agreeing face (deg ≥ 2) or an even face (A46). A **learning step** (A26) changes one sign,
on a side of a violated line or on a side with an end in D, while the state holds still. A law and a state are **resolved** when there is
no dissonance: no violated line, E = 0 and D = ∅.

The count (theorem 3 there): viol − E = (χ − |D|) / 2 in every state. Theorem 2 there: the signings with a given D form 2^(2 − χ) classes
up to gauge (flipping a point, or complementing a line's three literals), and two signings with the same D differ by a cycle of T (an
even subgraph), whose mod-2 homology class is the difference of their classes. Theorem 4: when χ = |D|, each perfect matching of the
lines with the faces off D is the corner map of exactly two states of exactly one class.

## 2. Theorems

**Theorem 1 (only χ = 0 can resolve).** A law and a state can be resolved only on a surface with χ = 0.
- On the sphere (χ = 2) every law keeps at least two even faces or a violated line in every state: learning moves the forced dissonance
  into the law (`RESIGN-STEER-20261107-001`) but cannot remove it.
- On a surface with χ < 0 every state of every law over-agrees somewhere: E ≥ (|D| − χ) / 2 ≥ 1.
- On a surface with χ = 0 the count forces nothing when D = ∅, and a dissonance that every state of a Kasteleyn law carries is forced
  by its class alone.

*Proof.* Resolved means viol = E = |D| = 0, so the count gives χ = 0. The three cases are the count read with |D| ≥ 0. ∎

**Theorem 2 (the least class-forced dissonance is a pair).** Let χ = 0 and let s be a Kasteleyn law (D = ∅) in a class that no state
satisfies. Then viol = E ≥ 1 in every state. In a state with one violated line l0 exactly one face w0 over-agrees, by one; where every
face has three line corners (the lattice tori) its three corners all agree and every other face has deg 1.

*Proof.* The count gives viol = E, and viol ≥ 1 since no state satisfies s. With viol = 1, E = 1, so one face has ⌊deg/2⌋ = 1 and the
rest 0. With three corners per face and every deg odd (D = ∅), that face has deg 3 and the others deg 1. ∎

**Theorem 3 (learning resolves the pair, and only by winding).** Let χ = 0, let s be a Kasteleyn law in a class ω0 that no state
satisfies, let some other class be satisfiable, and let x be a state with exactly one violated line l0.
1. **Learning resolves it.** With x fixed there is a sequence of learning steps that ends resolved. It has 1 + m steps, where m is the
   least number of lines that a perfect matching of the lines with the faces moves off the corner map after the first step.
2. **Every resolution winds.** Let any process (sign changes anywhere, the state changing too or not) take (s, x) to a resolved
   (s', x'). Then s' − s is a cycle of T whose homology class is s'-class − ω0 ≠ 0. So the process changes at least as many signs as
   the smallest cycle of T in that class has sides, and no process whose sign changes add up to a boundary resolves the pair.

*Proof of 1.*
- **The split.** Re-sign one side k of l0, a learning step since l0 is violated. Now l0 agrees only at its corner k, and the two ends
  u, w of the side each lose one agreeing corner. Every line agrees at exactly one face f(i). Faces of deg 0 are holes; w0 has deg 3, or
  2 if it is u or w.
- **A target.** Some class other than ω0 is satisfiable, so by theorem 4 the lines have a perfect matching with the faces. Let M be one
  that minimises the number m of lines with M(i) ≠ f(i).
- **The arcs.** For each such line draw an arc from M(i) to f(i). Every face has at most one outgoing arc, since M is a matching. At a
  face v, out − in = 1 − deg(v): holes are sources, w0 is the only face with in > out, and every other face has in = out ≤ 1.
- **No cycles.** If the arcs contained a directed cycle, giving its lines back their faces under f would leave a perfect matching (each
  face on the cycle keeps one line) moving fewer lines off f, against the choice of M. So the arcs form directed paths, one from each
  hole, and they can end only at w0.
- **The walk.** Move the hole along its path: at a hole v the next arc is a line i with M(i) = v; re-sign the side of i between v and
  f(i). This is a learning step, since v has deg 0 and is even. Afterwards i agrees at v and no longer at f(i), so the hole moves to
  f(i), or is absorbed if f(i) = w0. Each line keeps exactly one agreeing corner, so no line becomes violated. After both paths every
  line agrees at M(i): every deg is 1, so viol = E = 0 and D = ∅. ∎

*Proof of 2.*
- **A cycle.** Both s and s' have no even face. A face's parity changes by the number of re-signed sides at it, since every side at a
  face lies in exactly one line corner there. So every face meets s' − s an even number of times: it is a cycle of T.
- **Its class is not zero.** x' satisfies s', so the class of s' is satisfiable and differs from ω0. By theorem 2 there, the class of
  s' − s is that difference. A cycle of class zero is a boundary, a sum of triangles' sides, that is, a gauge change: if s' − s were
  one, s' would be a gauge transform of s, and the same gauge applied to x' would give a state satisfying s.
- **Its size.** Each sign change adds one side to s' − s, mod 2, so the process changes at least as many signs as the smallest even
  subgraph of T in that class has sides: the shortest closed walk in the class, or two shortest closed walks in the other two non-zero
  classes, whichever is smaller (`check.py`'s lower bound). ∎

So learning carries what no change of state can: the law's class, 2 − χ bits (two on a torus). On the sphere it moves the forced
dissonance but must leave it in the law as even faces; on a class-forced torus it removes the dissonance completely, leaves no even face
and no other local mark, and the only trace is that the law went around a handle. Part 2 does not rest on A26: whatever the state does,
a class-forced dissonance leaves only through a handle.

## 3. Checks and computations

- **Spaces (check 1).** The two Fano tori and the 57 thin tori of even index 4 to 40 (`COUNT-SURFACES-20261107-001A` theorem 5), each
  with exactly one sign class that no state satisfies; SAT agrees with the criterion. Degenerate tori are left out.
- **E1 (check 2).** Every class-forced law has states with exactly one violated line, and each such state has one face of deg 3 and the
  rest deg 1. Up to 20 points every least state is read: 70 on each Fano torus and n² on each thin torus (computed; the count n² is not
  proved). Beyond 20 points 200 were found by SAT.
- **E2 (check 3).** From every least state read and each of its three splits, the cheapest perfect matching of each of the three other
  classes was reached by the walk of theorem 3.1 with no alternating cycle left over, and replayed as sign changes: 96,732 walks, every
  step a learning step, every end resolved, every change a cycle of the expected non-zero class. Theorem 3.1 proves this for the
  cheapest matching over all classes; that the cheapest matching of each class is reached directly is computed.
- **E4 (check 4, computed).** On every torus, for every class, the cheapest walk found has exactly as many steps as the lower bound of
  theorem 3.2. On a thin torus of n points one class change runs across the short circumference (lower bound 2) and the two others
  around the long one (about n / 2): the mean cost into the short class rises from 2.7 at 4 points to 8.3 at 40, and into the long ones
  it stays within one of n / 2. On the Fano tori every class change costs 3 to 4.
- **E5 (check 5, computed).** The rule that sees only the three lines at a hole, where each agrees and the outside graph distance to w0
  (A26), never stepping straight back, resolved all 9,608 starts (every least state up to 200 per torus, a random split each) within
  20 V steps, and each run replayed as learning steps that wind. It mostly takes the short way around (192 to 199 of 200 runs on each
  40-point torus), and its mean cost rises from 2.3 steps at 4 points to at most 11.8 at 38, 0.2 to 8.7 above the lower bound.
  Unbiased random moves resolved all 2,806 runs; their mean rises from 2.1 steps at 4 points to at most 69 at 40.
- **S (check 6, stress test).** `RESIGN-STEER-20261107-001B`'s no-reversal rule reached 300 of 300 random targets on each of K_14 and
  K_16 (budget 40 m) and on K_2 to K_4 again, and 2,698 of 2,700 on the nine non-octahedral test spheres of `steer_lib` (two tubes,
  three grown spheres of 64 to 128 triangles, four branched double covers; budget 20 ⌈√V⌉): 299 on the tube (2, 5, 1), where the one
  miss is not reached with ten times the budget either (the rule circles), and 299 on one cover, reached with ten times the budget. The
  published line, 2,399 of 2,400 on the octahedral spheres K_2 to K_10 and 300 of 300 on K_12, holds one size past, and the rule
  reaches at least 95% on every other sphere tried.

Against the pre-registration: E1, E2, E3 and E4 held, E2's "every perfect matching is reachable" only in the form above. E5 did not: the
local rule never failed, which the pre-registration listed as the outcome against it. The reason is theorem 3.2: any walk that resolves
the pair winds, so a rule that only heads for w0 needs no plan to go around the handle. The winding is written in the state.

## 4. Scope and novelty

- **Scope.** Kasteleyn laws on lattice tori whose class no state satisfies; the learner of A26 for theorem 3.1 and checks 3–5; dissonance
  read as in A46. Theorem 3.2 holds on every closed surface with χ = 0 for any process. Klein bottles have no class-forced law in the
  tested range (`COUNT-SURFACES-20261107-001A` check 8), so the theorem is exercised only on tori here.
- **Novelty: known-with-delta.** Read as dimers, a resolved configuration is a perfect matching, the classes are winding sectors, the
  holes are the monomers of a worm algorithm, and part 2 is the folklore that local moves keep a torus's winding sector while a worm
  must wrap around to change it (Kasteleyn 1961's four Pfaffians; worm and directed-loop algorithms for dimers). New here are the
  reading as learning against change of state, with the law the worm acts on and the state held fixed; theorem 1's place for χ = 0;
  theorem 2's pair on the class-forced tori, which include the Fano plane; and the costs and the local rule.
