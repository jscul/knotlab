# Pre-registration: a learned network that computes

Epic `GATES-20261110-001` (sub-goal B118, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead after the owner's
"Yes, let's do that." Exploratory: if the census gives no foothold, the epic stops and reports.

## The question

The layered memory stores bits in handle classes. A three-edge cut reads the AND of the bits inside it (`COMPOSITE-FN-20261110-001`); a
parity name reads correlations of states, single clauses included, and cannot carry a contradiction up (`NAME-LAYERS-20261110-001`). Do
cuts and names together compute every function of the stored bits?

## Words

- **Stored bits.** Two leaves, each the thin-torus atom (2,1,2) (the smallest atom that remembers), each in one of its four classes. The
  stored bit a_j is 1 when leaf j acts (its class is its torus's unsatisfiable one). A class pair has 16 values: one with (1, 1), three
  each with (1, 0) and (0, 1), nine with (0, 0).
- **A network** is a set of components (closed knot spaces with Kasteleyn laws, leaves cut into hosts as in `NEST-ATOMS-20261110-001`),
  three **names** y_0, y_1, y_2, each the parity of a pair of points of a component (a parity naming knot), and one **top** constraint on
  the names: a not-all-equal line with one of 8 sign patterns, or a parity knot y_0 ⊕ y_1 ⊕ y_2 = κ with κ = 0 or 1.
- **The reading** O is 1 when the network has no satisfying state. A network **reads a function** f of (a_1, a_2) when O = f(a_1, a_2) in
  every one of the class pairs (so O may not depend on which non-acting class a leaf is in).

## The families, frozen

- **F1 (cut only).** K_2 with both leaves cut in (at l0 and the first line at the largest distance), no names: one network.
- **F2 (names only).** Two components, the closed tori of leaf 1 and leaf 2. y_0 a pair of the first, y_1 a pair of the second, y_2 a pair
  of either; 6 × 6 × 12 name choices × 10 tops.
- **F3 (a cut and a name).** Component A: K_2 with leaf 1 cut in at l0; component B: the closed torus of leaf 2. Names y_0 and y_1 are pairs
  (unordered, possibly equal) of the six points formed by leaf 1's three points and the three points of the line it replaced, y_2 a pair of
  B; 120 × 6 name choices × 10 tops.
- **F4 (a satisfiable host).** Component A: the all-satisfiable torus (2,0,2) in its first class with leaf 1 cut in at its first line;
  component B as in F3. y_0 and y_1 pairs (unordered, possibly equal) of A's seven points, y_2 a pair of B; 231 × 6 × 10.
- **F4′ (one stored bit).** Component A of F4 alone; three names, a multiset of A's pairs; 1,771 × 10. It reads functions of a_1.

The leaves' classes are set by bringing each leaf with each of its torus's four class laws.

## Predictions and what is proved

- **P1 (proved).** F1 reads AND (theorem N of `NEST-ATOMS-20261110-001`).
- **P2 (proved).** In every network, O = 1 whenever a component has no satisfying state: in F2 when either leaf acts, in F3 when either
  does (K_2 with an acting leaf is unsatisfiable), in F4 when leaf 2 acts. So O(1, 1) = 1 in every family, and XOR, NAND, NOR, equivalence
  and the other functions that are 0 at (1, 1) cannot be read in one network of these families.
- **P3 (predicted).** OR is read in F2 and in F3.
- **P4 (predicted).** NOT a_1 is read in F4′, and so a negation of a stored bit is readable: with AND (F1) and OR (F2) it gives a complete
  basis of gates, each read at the top of its own network.
- **Failure line.** A network contradicting P1 or P2 (a code or proof error).
- **Not tested here, and recorded:** composing gates, which needs a gate's reading to become a stored bit for the next network.

## Stop rule (one epic)

The answer is the set of functions each frozen family reads, with P1 to P4's verdicts. Other families are recorded, not run.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52. The census is expected to take under ten minutes; if a run goes past that it is
registered in `docs/LONG_RUNNING.md` before being relaunched.
