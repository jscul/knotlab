# AND for critical hosts

Status: Proved by hand (lemmas M, H, G and the theorem); checked by `check.py` (4 seconds) as frozen in
`research/COMPOSITE-FN-20261110-001/preregistration.md` (commit `36d02b296`). The proofs were written after the run.

## Words

A **host** is a closed orientable knot space with a Kasteleyn law whose lines have three distinct points and three distinct faces, in a
class with no satisfying state. A line l is **critical** if some state violates l and no other line; a host is critical if every line is.
Atoms are good (free, exactly one unsatisfiable class), grown at lines l_1, …, l_m; the composite is the host with its atoms, less a point
where it is free (`NEST-ATOMS-20261110-001A`).

## Lemma M (the function)

The composite acts exactly where H with the lines of its transparent atoms deleted has no satisfying state. So, writing a_j = 1 when atom j
acts, its function is f(a) = OR, over the minimal unsatisfiable sets M of H's lines, of AND of the a_j with l_j in M.

*Proof.* The composite acts exactly where its closed space T has no satisfying state (lemma 2 of `OTHER-ATOMS-20261110-001A`, with
freeness). Each atom's points occur only in its own lines, so T is satisfiable exactly when H is with each acting atom read as its line
(it allows exactly that line's patterns) and each transparent one as nothing (it allows all eight). A set of lines is unsatisfiable
exactly when it contains a minimal unsatisfiable set. ∎

**AND-only.** If every l_j is critical, f = AND: if atom j is transparent, H less l_j has the state violating l_j alone, which satisfies
every other line, so f = 0; if every atom acts, f = 1 because H has no satisfying state. ∎

## Lemma H (every line of a knot sphere is critical)

Let T be a two-coloured triangulation of the sphere (multiple edges allowed), with N lines (black triangles), N points and N + 2 faces
(vertices). **Every nonempty set S of lines touches at least |S| + 2 faces.**

*Proof.* Let X be the union of the closed triangles of S. Each edge of T borders one black and one white triangle, so the triangles of S
have 3|S| distinct edges, and X has Euler characteristic χ(X) = |V(S)| − 3|S| + |S|. X is not the whole sphere, so H_2(X; F2) = 0 and
χ(X) = b_0 − b_1, and by Alexander duality b_1 = C − 1, where C is the number of components of the sphere less X. In a component K, let
w_K be its white triangles and b_K its black triangles not in S. A white triangle's edge borders either a triangle of S (an edge of X
facing K) or a black triangle not in S, which then lies in K; a black triangle not in S has all three edges on white triangles of K. So
the edges of X facing K number e(K) = 3w_K − 3b_K: a multiple of three, and positive, since otherwise K would contain every triangle.
Every edge of X faces exactly one component through its white side, so 3C ≤ Σ e(K) = 3|S|. Hence
|V(S)| = 2|S| + b_0 − C + 1 ≥ 2|S| + 1 − |S| + 1 = |S| + 2. ∎

So by Hall's theorem, for any two faces u and w the lines have a perfect matching into the other N faces. Take a line l and a side e of
l with ends u ≠ w. The law with e's sign flipped has even faces exactly u and w, and on the sphere (χ = 2 = |D|) the matching is the
corner map of a state of it (theorem 4 of `COUNT-SURFACES-20261107-001A`, as used in `LEARN-HANDLES-20261109-001A`), in which l agrees
at its third face. Flipping e back toggles l's corners at u and w, so l agrees at all three and is violated, and nothing else changes: a
state violating l alone. **Every line of every Kasteleyn knot sphere is critical.** This also settles backlog B110 (a flat state at every
line), so theorem N of `NEST-ATOMS-20261110-001A` holds on every Kasteleyn knot sphere host.

## Lemma G (growth keeps criticality)

Let H be a critical host and grow good atoms whose closed spaces T_j are critical in their unsatisfiable classes. Then the grown closed
space is critical in its unsatisfiable class (H's, with every atom acting).

*Proof.* A line i of H: H's state violating i alone satisfies every replaced line, so every acting atom completes it. A line λ of atom j:
T_j has a state y violating λ alone; it reads the removed point at one value b, so the atom (with λ violated and its other lines
satisfied) shows on its outer points the replaced line's forbidden pair; H's state violating l_j alone shows that pair too (its three
literals on l_j are equal), complemented if need be (complementing every point keeps every line's status), so y joins it, and the other
atoms complete as before. ∎

## The theorem

For every host built from Kasteleyn knot spheres and class-forced lattice tori by growing good atoms, at any depth, every line is
critical, so every composite over it computes the AND of its atoms' bits. The spheres are critical by lemma H; the class-forced lattice
tori are critical in their forced class because a least state violates exactly one line (`LEARN-HANDLES-20261109-001A`, check E1, on every
class-forced torus to 40 points) and translations carry it to every line; lemma G carries criticality through growth.

A host where a composite computes something other than AND (beyond the constant 0 of a space with no unsatisfiable class) needs a
non-critical line: an unsatisfiable class that stays unsatisfiable when that line is deleted. None is known.

## The check (computed)

- **Check 1.** On all 16 spheres of the frozen set (K_2 to K_8, two tubes, three grown spheres, four branched double covers), every line
  has three distinct faces and a state violating it alone (SAT, every line).
- **Check 2.** A composite with two Fano leaves over a tube, a grown sphere and a double cover, at the standard point: in all 16 classes
  it acts exactly where both leaves act, with the replaced line's own patterns, and is transparent otherwise.

Both held, as frozen.
