# Pre-registration: which functions a composite computes

Epic `COMPOSITE-FN-20261110-001` (backlog B109, with B112 folded in as ticket C; G15), written on 2026-11-10 before any run, at the
coordinator's go-ahead.

## The question, frozen

`NEST-ATOMS-20261110-001` proved that a composite acts where its closed space has no satisfying state, so a level reads only a monotone
function of the bits below, and on the knot spheres used there exactly their AND. **Either exhibit a host giving a monotone function
other than AND (an OR, a projection, a constant), or prove that AND is the only one for a stated class of hosts.**

## Words

A **host** is a closed orientable knot space with a Kasteleyn law (no even face), whose lines have three distinct points and three
distinct faces, taken in a class with no satisfying state. A line l of a host is **critical** if some state violates l and no other line;
the host is critical if every line is. Atoms are good (free, one unsatisfiable class), grown at lines l_1, …, l_m; a composite is the host
with its atoms, less a point where it is free.

## Ticket A: AND for critical hosts (by hand, with checks)

To prove:
- **Lemma M.** The composite acts exactly where H with the lines of its transparent atoms deleted has no satisfying state. So its function
  is f(a) = OR over the minimal unsatisfiable sets M of H's lines of AND of a_j over the l_j in M.
- **AND-only.** If every l_j is critical, f is the AND of all a_j.
- **Lemma H.** Every line of every Kasteleyn knot sphere is critical. Planned proof: every set S of lines touches at least |S| + 2 faces
  (Euler characteristic of the union of S's triangles and Alexander duality on the sphere), so Hall's theorem gives a perfect matching of
  the lines into the faces other than the two ends of any side of l, which is a state violating l alone.
- **Lemma G.** A host grown from a critical host by good atoms whose closed spaces are critical in their unsatisfiable class is critical
  in its own; so every host built from Kasteleyn spheres and class-forced lattice tori by growth, at any depth, gives only AND.

Checks (computed): a state violating each line alone on every line of every sphere of `steer_lib.test_spheres(random.Random(109))` and of
K_5 to K_8; and the AND, exactly in all 16 classes, for a composite with two Fano leaves (at the first line-orbit representative and the
first line at the largest distance) over three hosts from that set, a tube, a grown sphere and a double cover, at the standard point.
**Failure:** a sphere line with no such state, or a composite over a critical host computing anything but AND.

## Ticket B: a search outside the proved class (computed, exhaustive per host)

The family, frozen: (i) double covers of K_2 and K_3 branched at four vertices, tori, with three branch sets each: the first four corners
(degree-4 vertices, by index); the first two corners and the first two regular vertices (three line corners); the first four regular
vertices; (ii) double covers of the Fano torus (7,2,1) and the thin torus (4,3,2) branched at vertex 0 and the lowest-index vertex not
adjacent to it, genus 2. For each host: a Kasteleyn law by solving the face parities, every class, its satisfiability, and in each
unsatisfiable class whether each line is critical (SAT).

- **Prediction S1.** Every line of every unsatisfiable class of every host in the family is critical, so no host here gives other than AND.
- **If a non-critical line is found:** for each pair of lines {l1, l2} with l1 non-critical in that class, the function is read by lemma M
  (four SAT calls on H less subsets of {l1, l2}); report which monotone functions occur, and confirm one on a grown composite exactly.
  That would answer B109 positively for that host.
- **Stop rule (one epic).** Only this family is searched in this epic; whatever it shows, the epic closes.

## Ticket C: points interact only through a shared line (B112, frozen re-test)

The observation of `MANY-POINTS-20261110-001`, made after its run, frozen here as a prediction and re-tested on fresh composites: the
outer host K_2 with two composites C(3, leaf) (K_3 with two leaves at its l0 and its farthest line), for the Fano and thin (2,1,2) leaves;
floors written by the frozen search toward the four addresses from the class where every leaf is transparent; at each floor 150 pairs of
flipped points at distance 2 or more and 50 at distance 1 (distance in lines: two points are at distance 1 when they share a line), with
random.Random(112). Classes and the rule D as in `MANY-POINTS-20261110-001B`. Pairs at distance 2 or more that share a face are reported
apart.

- **L1.** Every pair at distance 2 or more is independent. **L2.** At least half of the pairs at distance 1 interact.
- **Failure.** Any pair at distance 2 or more that is not independent: the locality is then false as stated.
- **Then** try to prove L1: at least that I = 0 for pairs sharing no line and no face, and what more can be shown.

## Runs

Each check is expected to take under ten minutes; one expected to take longer is registered in `docs/LONG_RUNNING.md` before launch.
Assumptions in force: A20, A21, A46, A47, A49, A50, A52.
