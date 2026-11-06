# Access is local: plane pieces keep it

Status: Proved (items 1–4; item 5 is a computation)

Ticket `HANDLE-LOCALITY-20261103-001A`, 2026-11-03.

## Question

- **Background (PLANAR-THEOREM C).** Every pinning on a plane knot space has access.
- **The scout.** In 16-point spaces made by splicing the Fano plane into a plane space, access depended on where the gluing line sat, not
  on where the removed line was.
- **The question.** Is access decided by the planar piece around the gluing line alone?

## Dependencies

- **`PLANAR-THEOREM-20261102-001A` and `C`.**
  - Heights of line–face matchings.
  - The staircase and the midpoint argument.
  - Re-centring at any point.
- **`PLANAR-COMPOSE-20261102-001A`.** The pinning classifier.
- **`HANDLE-EMERGENCE-20261102-001C`.** The skip model: a line skips the corner opposite its odd point.
- **Classical.**
  - Heights of plane bipartite perfect matchings (Thurston, Propp).
  - L-convex sets and their sections (Murota).

## Setting

- **A plane signed system.** Lines of three points with signs, whose incidence graph is embedded in the plane. Points may have any degree.
- **Face parity.** For a face f, let π(f) be the parity of the number of corners of f plus the number of corners where the line's two signs
  differ.
- **A splice.** S joins H1 minus a line li to H2 split at a point z. Each point of li goes to one line through z.
  - Lines and points belong to the piece they came from.
  - li's points (the ports) belong to H1, and they also stand for z in H2's piece.
- **Closures.** H1 is the closure of H1's piece, and H2 is the closure of H2's piece.
- **A removal.** M is any line of S.

## 1. Plane matching systems (proved)

**Call a plane signed system a matching system if it is satisfiable and has as many lines as odd faces. Then its solutions, up to
complement, are exactly the perfect matchings of lines to odd faces (each line to the odd face of one of its corners).**

*Proof.*
- **Skips.** In a solution, each line skips the corner between its two agreeing points (the skip model).
- **Parity.** Around a face, the values of consecutive points telescope. So the number of skipped corners of f has parity π(f).
- **Counting.** Every odd face receives at least one skip. There are exactly as many skips (one per line) as odd faces. So every odd face
  receives exactly one skip, and every even face none.
- **The converse.** A perfect matching satisfies every face's parity. In the plane, the face conditions generate every cycle condition.
  So it is a solution, unique up to complement. ∎

**The access lemma holds on every matching system:** every pinning (p, a) of a line L with six patterns has access relative to p.

*Proof.* PLANAR-THEOREM A and C use only the following:
- the solutions are the perfect matchings of a plane bipartite graph B (here lines against odd faces);
- the regions of B are points, or holes made of even faces with their boundary points;
- heights are integrated across B's edges, and re-centred at p;
- the parity reading (alternating cycles flip exactly the points they enclose);
- the staircase at a line whose three corners lie in odd faces.

A line with six patterns has its three corners in odd faces: otherwise one of its points could never be odd. So the proofs apply
verbatim. ∎

## 2. Point splits are matching systems (proved)

**Split a point z of a plane knot space H with Kasteleyn signs into three ports, one on each line through z. The result is a matching
system.**

*Proof.*
- **The faces.** The three faces at z merge into one face F₀, which holds all three ports as pendant points. So there are n faces for n
  lines.
- **The parity.** The corners are unchanged, so π(F₀) is the sum of the three merged parities: 1 + 1 + 1, which is odd.
- **A port's sign.** Changing it flips both corners of its line at the port. Both lie in F₀, so no parity changes. ∎

## 3. The interface lemma (proved)

- **H1 minus li acts as the point.** H1 is unsatisfiable. So every solution of H1 minus li violates li: its three points are all equal
  after signs. This is a pair {σ, σ̄} of port patterns, and the ports read as one point.
- **H2 split acts as li.** H2 is unsatisfiable. So the split excludes exactly the two port patterns that read z consistently. S fails,
  so that pair is {σ, σ̄}, and the split allows exactly li's patterns.
- **The restrictions.** The solutions of S minus M, restricted to a piece, are that piece's own solutions met with the other side's
  port relation.

| Piece | Removal inside the piece | Removal outside the piece |
| --- | --- | --- |
| H1's | H1 minus M (the other side restores li) | H1 minus li (its own all-equal pair already lies in the other side's relation) |
| H2's | H2 minus M (the ports read as z, with H2's signs) | the point split met with the other side's relation: the split itself (6 port patterns), the split with two ports merged (4 patterns), or H2 with z re-signed (2 patterns) |

**Each restriction is a matching system when the closure is plane.**
- **A closure minus a line.** This is the skip model (HANDLE-EMERGENCE C).
- **The point split.** Item 2.
- **Two ports merged.** The merged point splits F₀ into two faces whose parities add to π(F₀) = 1. So one is odd and one is even, leaving n
  odd faces for n lines. A sign on the merged incidence flips one corner in each of the two faces and leaves the sum unchanged.
- **z re-signed.** Changing the sign of line Lᵢ at z flips the two faces at z beside Lᵢ. A re-signing that changes the solutions leaves
  exactly two of the three faces at z even, so n faces are odd for n lines. If no face became even, the system would be H2 and
  unsatisfiable. ∎

## 4. Locality (proved, from 1–3)

- **The theorem.** Let a piece of a splice have a plane closure with Kasteleyn signs, and let L be a line of that piece with six patterns
  after a removal M (anywhere). Then every pinning of L's pattern by two points of that piece has access.
- **Why.** Its restriction is a matching system (item 3), and access holds there (item 1). Pinnings, ties and exclusions among the piece's
  points are read off that restriction.
- **With the route lemma** (PLANAR-COMPOSE A, for any pinning pair; PLANAR-THEOREM C). Every three-point crossing knot at L, pinned by two
  points of L's piece and separated by one far point, is generated in any further splice at L.

## 5. Pinnings from outside the piece (computation)

On the splices of check 3:
- **One pinning point outside the piece.** All 9,028 such pinnings have access. This is not proved.
- **Both pinning points outside.**
  - **Removal inside the piece.** All 260 have access.
  - **Removal outside the piece.** 528 of 620 fail: 192 tied to the odd port, 336 free of the non-odd ports.
- **So** a handle can pin a plane line's pattern without access only when the removal opens the handle itself.

## Checks

`check.py` (`result.json`, about two minutes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Point splits of 26 plane spaces (census, grown, prisms; to 14 points; all 28 tested spaces Kasteleyn) | all 301 splits have n faces for n lines, all odd; all 260,892 pinnings (ports included) of type (i) or (ii) |
| 2 | Interface lemma on 14 splices (Fano plane and census 58 against three grown plane spaces both ways; census 6 against a grown space both ways) | the predicted restriction at all 266 (piece, removal) pairs: H1 minus M 72, H1 minus li 61, H2 minus M 80, point split 35, two ports merged 18 |
| 3 | Access by piece, same splices | 31,596 pinnings by points of a plane piece, all of type (i) or (ii); outside pinnings as in item 5 |

## What this does not establish

- **Pinnings from outside the piece.** Their behaviour is only computed (item 5).
- **Creation.** That a gluing line in a plane piece never creates. That would also need the residual knots of PLANAR-THEOREM C, and the
  pinnings from outside a piece; ticket B tests it.
- **Pieces with several cuts.** The same argument applies cut by cut: a side the removal misses is intact and acts as its closing point
  or line. Here it is checked only on single splices; ticket B's two-atom spaces exercise it.

## Novelty

- **New here.** Plane matching systems as the common setting, the point-split and gadget parities, the interface lemma, and the locality
  theorem.
- **Classical.** Plane matching heights, Kasteleyn's face condition, L-convexity.
