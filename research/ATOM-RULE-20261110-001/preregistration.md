# Pre-registration: a proof of the atom rule

Epic `ATOM-RULE-20261110-001` (backlog B87, G15), written on 2026-11-10 before any computation, at the coordinator's go-ahead.

## The claim to prove

For an octahedral knot sphere K_k (k ≥ 2) with Fano atoms spliced at lines whose neighbourhoods are disjoint ("separated" atoms: no line
has a corner at a face of two atoms' regions), with the old Kasteleyn law and any completion with no even face:

1. **Role.** Each atom acts as its line (allows on its three outer points exactly the six patterns the replaced line allowed) in exactly one
   of the four classes of its own handle, and is transparent (allows all eight) in the other three, whatever the other atoms' classes.
2. **R-a.** If every atom acts as its line, no state satisfies every line.
3. **R-b.** Otherwise, in every state satisfying every line, every acting atom has a face with three agreeing corners in its region (its
   interior faces and its three junction faces).

## The planned proof

- **O1 (by hand).** The first homology of the grown surface is the direct sum of the atoms' handles (each atom is cut off by a separating
  curve, the three new sides), and an atom's allowed patterns depend only on the signs of its own 21 sides; a change in another atom's
  handle can be made away from them, and a gauge change only relabels patterns.
- **O2 (a finite local check).** An atom's local gadget is its region's faces and every line with a corner at one of them, with all their
  points. For each atom class: if the gadget's lines can all be satisfied with at most one agreeing corner at every region face, a state
  without a unit in the region is not excluded locally; if not, R-b holds for that atom in every sphere containing that gadget. The roles
  are read on the gadget too. Run on every line orbit of K_2 to K_7.
- **O3 (the gadget types).** Classify the gadgets of every line of K_2 to K_8 up to isomorphism, and show that from some k on no new type
  appears, with a structural reason (the sphere is the triangular lattice away from its six corners, and a line meets at most one corner).
- **O4 (assembly).** R-b from O2 for each acting atom of a separated configuration; R-a because all-acting atoms act as their lines, so the
  old points must satisfy the sphere's own law, which no state does (`COUNT-SURFACES-20261107-001A` theorem 3).

## Expectations, frozen

O2 finds, on every gadget, exactly one acting class among the four of the atom's handle, with a local UNSAT for it and local SAT for the
three transparent ones; O3 finds finitely many types, none new beyond K_4. **Against:** a gadget whose acting class is locally satisfiable
(then R-b needs a non-local argument, or is false for larger spheres), or new types appearing at every size.
