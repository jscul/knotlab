# The role of every torus atom

Status: Proved by hand (lemmas 1 to 4 and the theorem), given two facts about each atom's torus, which ticket D checks by exhaustive SAT.
`check.py` (34 seconds) runs tier T1 of `research/OTHER-ATOMS-20261110-001/preregistration.md` on the 29 named atom types: every line orbit
of K_2 to K_4, every compatible splice, four classes, with the code control on the Fano atom. Its first run (2026-11-10 04:13 UTC) bound
the pre-registration as frozen in commit `1fd95cc5f`; the run committed here is a re-run after the addendum, identical except for that
file's hash. The lemmas were found after the run, by reading it.

## Setting

A **host** is an orientable knot space X (a two-coloured triangulation: points of colour 0, lines of colour 1, faces the vertices) with a
Kasteleyn law s0, one with no even face, whose lines have three distinct points and three distinct faces. A **torus atom** (T, P) is a
knot space T on a torus with such lines and a point P whose triangle has three distinct vertices u_1, u_2, u_3 and whose three sides lie
in three distinct lines l_1, l_2, l_3, with u_i the vertex opposite the side P shares with l_i. The atom is grown at a host line l by a
compatible splice (`GROW-HANDLE-20261110-001A`): P and l are removed and l's side k is glued to P's side with l_{π(k)}, so that l_{π(k)}
now reads the host point p_k on l's side k through a **new side**. The atom's sides keep a Kasteleyn law σ of T, the host's keep s0,
and the new sides take signs τ that leave no even face. The atom's **region** is its interior faces (the faces of T other than the u_i)
and its three **junction faces** (each u_i merged with a vertex of l). T has N points, N lines and N faces (χ = 0), so the region has N
faces.

The **class of the atom** is the class of T read on the atom's sides: complete them with signs on P's three sides that leave no even face
in T. There are two such completions and they differ by flipping P, so the class is well defined. T is **free at P** in a class if, for
each of P's three sides e, the law with e's sign flipped has a satisfying state. (That law has exactly two even faces, the ends of e.)

## Lemmas

**Lemma 1 (completions).** Exactly two signings of the new sides leave no even face, and they differ by a gauge change. Writing σ_i for
T's sign on P's side with l_i and δ_i = σ_i + τ_i, they are δ_{π(k)} = s0_k + c for c = 0 and c = 1, where s0_k is the host's sign on
l's side k.

*Proof.* The junction face J at the vertex of l between its sides a and b is that vertex v merged with the vertex u of P between its sides
with l_{π(a)} and l_{π(b)}. Its line corners are v's other than l's and all of u's, and only the corners of l_{π(a)} and l_{π(b)} at u
change a side: the side P shared with them becomes the new side. A face's parity is its number of corners plus its flip, the sum of the
two side signs at each corner. So d(J) + flip(J) = [d(v) + flip(v)] + [d(u) + flip(u)] − 1 − (s0_a + s0_b) + (δ_{π(a)} + δ_{π(b)}), and since
v and u are odd, J is odd exactly when δ_{π(a)} + δ_{π(b)} = s0_a + s0_b. The three junction faces give three such equations, of rank 2
(their sum is 0 = 0), with the two solutions above. Flipping the three new sides is the gauge change that flips every atom point and
complements every atom line. ∎

**Lemma 2 (the role).** In a grown space let the atom's class be c. Put b_{π(k)} = a_k + s0_k + c for a pattern a on the three outer
points. The atom allows a if and only if T in class c has an assignment of its points other than P satisfying every line when each l_i
reads the value b_i at P. Hence:
1. a lies in the replaced line's forbidden pair (a_k + s0_k constant) exactly when b is constant, and then the atom allows a if and only
   if T is satisfiable in class c;
2. otherwise b_i differs from the other two values for one i, and the atom allows a if and only if T's law with the sign of P's side
   with l_i flipped is satisfiable.

So if T is free at P in class c, the atom **acts as its line** (allows exactly the six patterns the replaced line allowed) when T is
unsatisfiable in c, and is **transparent** (allows all eight) when T is satisfiable in c. The host plays no part.

*Proof.* In the grown space l_{π(k)} reads a_k + τ_{π(k)} on its new side; in T it reads b_{π(k)} + σ_{π(k)} on P's side, and these agree
because b_{π(k)} = a_k + δ_{π(k)} by lemma 1. Every other atom side is the same in both. So the atom's lines with outer points a are T's lines
with P read as b by its three lines. Part 1: complementing every point of T keeps every line's literals' agreement, so T has a state with
P = 0 if and only if it has one with P = 1. Part 2: with b_i alone different, reading b_i at P in l_i is reading the common value with
l_i's sign at P flipped. ∎

**Lemma 3 (holding a unit).** If T is unsatisfiable in the atom's class, then in every state of the grown space satisfying the atom's
lines, some face of the atom's region has at least two agreeing corners, and at least three when the grown space has no even face.

*Proof.* Suppose every region face has at most one agreeing corner. The atom's N lines are satisfied, so each agrees at exactly one corner,
and all their corners are at region faces. There are N region faces, so each has exactly one agreeing corner, an atom line's; in T's
terms every face of T has exactly one agreeing corner, with P read as b (lemma 2). Around u_i the points of T each lie in two consecutive
line corners, except P, which l_j and l_k read as b_j and b_k. So the parity of u_i's agreeing corners is d(u_i) + flip(u_i) + b_j + b_k,
which is 1 + b_j + b_k since T's law has no even face. Every u_i has one agreeing corner, so b_j = b_k for every pair, b is constant, and
T has a satisfying state in class c: a contradiction. ∎

**Lemma 4 (the classes).** The grown surface's first homology over F2 is the host's plus each atom's handle: each atom is cut off by a
separating curve, its three new sides (Mayer–Vietoris, as lemma A of `ATOM-RULE-20261110-001A`). A flat change on an atom's own sides is
a flat change of T avoiding P's sides, and every class of T has a cycle avoiding one triangle, so the classes read on the atom are its
torus's four classes, and they vary independently of the host and of the other atoms.

## The theorem

**Theorem.** Grow torus atoms (T_1, P_1), …, (T_g, P_g) at distinct lines of a host X, in turn, each by a compatible splice with a
completion with no even face. The atoms may be adjacent and their regions may share junction faces. Suppose each T_j has exactly one
unsatisfiable class ω_j and is free at P_j in every class. Then the grown space has no even face, and:
1. atom j acts as its line when its class is ω_j and is transparent otherwise, whatever the other classes: exactly one of its handle's
   four classes;
2. a state of the grown space satisfying every line restricts to a state of the host satisfying every line except the lines of the
   transparent atoms, and every such host state extends; so if every atom acts, the grown space has a state satisfying every line if and
   only if X has one (on a knot sphere, never);
3. in every state satisfying every line, each acting atom has a face with at least three agreeing corners in its region.

*Proof.* No even face: lemma 1 at each growth, since the host at each step is the space grown so far, which has no even face. Part 1:
lemmas 2 and 4; a later growth at another host line does not touch atom j's sides or new sides. Part 2: each atom's points occur only in
its own lines, so the atom's lines constrain the host only through the relation on its outer points, which is the replaced line's or none
(part 1). Part 3: lemma 3 for each acting atom; its region count uses only its own lines, so shared junction faces do not matter. ∎

This contains theorem 1 of `ATOM-RULE-20261110-001A` (the Fano atom, separated atoms, octahedral knot spheres) and removes both of its
restrictions, with a proof that needs neither that record's local check nor its classification of line neighbourhoods: the local system
it checked unsatisfiable in the acting class is lemma 3's, and is unsatisfiable for the reason lemma 3 gives.

## The two facts per torus, and what is computed

The theorem needs, for each atom torus, its unsatisfiable classes and freeness at its point: sixteen SAT calls. Ticket D makes them for
every simple lattice torus to 30 points and every thin torus of even index to 40 (157 types up to isomorphism): every one is free in every
class, and the class-forced types are the Fano torus and the thin tori of even index, each with exactly one unsatisfiable class. So the
theorem applies to the Fano atom and to every thin-torus atom of even index from 4 to 40 points, and every other lattice-torus atom to
30 points is transparent in all four classes on any host (lemma 2).

Two remarks, proved and not used above:
- **Freeness in the unsatisfiable class** is the existence of a state violating only the line at a given side: flipping a side's sign
  toggles that line's two corners at the side's ends, so a state satisfies the flipped law exactly when it violates no other line and the
  side's line agrees at one of those ends or at all three corners, and in an unsatisfiable class only the second is possible. On a lattice
  torus translations move any line to any other, so freeness there is the statement that the least states violate one line
  (`LEARN-HANDLES-20261109-001A` theorem 2 assumes it; its check found it on every class-forced torus to 40 points).
- **Freeness in a class with a uniform matching.** On a lattice torus, matching every line to its corner in one lattice direction d is a
  perfect matching, so (`LEARN-HANDLES-20261109-001A` theorem 4) it is the corner map of a state of one class c_d. For a side e: if e's
  opposite corner is not in direction d, that state satisfies the law with e flipped; if it is, flip the point on e first: of that point's
  three lines, which meet it across edges of three different directions, only e's line agreed at its corner opposite the point, so only
  it becomes violated, and flipping e then satisfies it. So every lattice torus is free in every class c_d.

## The check (T1, computed exhaustively)

- **Check 1.** The 29 named types are the lattice tori grouped by an exact canonical form of maps up to isomorphism and mirror image.
- **Check 2.** The line orbits of K_2 to K_4 meet all four line-neighbourhood types of `ATOM-RULE-20261110-001A`'s lemma C.
- **Check 3 (code control).** The Fano atom through this code reproduces that record's check 1 on K_2 to K_4, splice by splice (60).
- **Check 4.** On each of 60 splices per type (1,740 in all), the eight class-forced atoms act as their line in exactly one class, the
  torus's unsatisfiable class, with an unsatisfiable local system, and are transparent in the other three; the 21 all-satisfiable atoms
  are transparent in all four. Every no-even-face completion existed. Ticket D's check 3 confirms lemma 2 on all 6,960 class readings.

Predictions P1 and P2 held. The theorem's evidence class: proved by hand, with a finite computation per torus (ticket D).
