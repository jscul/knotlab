# Native paths in the knot's spaces

Epic `NATIVE-PATHS-20261101-001` (program topology), 2026-11-01.

## The question

- **Approval.** The owner approved this direction ("Yes continue.") as recommended after the composition epic and the note.
- **The recommendation.** "Test whether network hubs can carry native paths and separation (the next gate after first emergence) on the
  knot's spaces."
- **The first check.** Is a path defined through hubs fixed by the law, or chosen by an observer?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | The parts of a knot's space meet in two ways. Across every nontrivial 2-edge cut, one side is exactly equality and the other exactly disequality (complementary two-place parity, no hub). Across every nontrivial 3-edge cut, the point side is exactly an antipodal pair {v, v̄} and the line side its complement: a knot against a hub, up to signs. | proof (general); 40 + 48 cuts checked | A |
| 2 | Correction. KNOT-COMPOSE's "compose only through hubs" fails at 2-edge cuts (odd cycles of Fano blocks, the twisted cube, splices containing them), and its "exactly" holds only up to signs. Its "hub-free failure is parity" stands. | proof and documentation | A, R |
| 3 | Every nontrivial 3-edge cut is either a proper splice cut or the shift of a 2-edge cut. A shift is twisted exactly when the absorbing shore is a disequality. | proof | B |
| 4 | Routes are fixed by the space, not chosen. In ten spaces, proper splice cuts never cross each other or a 2-edge cut, and the decomposition is unchanged under relabelling. | computation (ten spaces) | B |
| 5 | A route through atoms carries its length mod 2. Two units of an odd cycle are joined by two routes of opposite parity, whose disagreement is the failure. A route through a hub carries nothing about what lies beyond. | proof | B |
| 6 | Cutting junctions separates two units exactly when both routes are met. | proof; 2998 cases | B |
| 7 | Counting witnesses gives 5 per Fano unit and 5^m per arc of m units: a count of what K1–K3 quantifies away, not a relation. | proof and enumeration | B |
| 8 | The twist criterion: a knot's space stays non-colourable under a twist pattern iff the pattern is a cocycle (an edge cut). | proof (from SNS and the uniqueness of Pfaffian signings); 1568 + 1200 checks | C |
| 9 | Knot meets knot only pairwise. If both sides of a nontrivial cut accept knots, the cut has exactly two edges. | proof | C |
| 10 | Every statement of "compose only through hubs" is recorded, with the note's erratum. D001's status is left to the owner. | documentation | R |

## Answer

- **Fixed, not chosen.**
  - The parts of a knot's space, the cycles of units between them, and the tree of splice cuts are all determined by the incidence
    graph, which is the declared substrate.
  - The law fixes what each route carries.
  - No observer chooses a route.
- **Hubs carry routes, but not native paths.**
  - A route through a hub collapses everything beyond it into one point or one line.
  - A hub is an equality fan-out, which the program never counts as contact.
  - So hubs carry routes of the declared substrate, which separate when cut.
- **Hub-free routes exist, but they are pairwise.**
  - Across 2-edge cuts the parts meet as two-place parity, with no hub. That relation has no contact variable.
  - Ticket C shows this is the only hub-free meeting of knots: across three or more channels, a knot never meets a knot.
- **Native paths of knots between the parts of a knot's space do not exist.** The rung of the ladder after first emergence is not reached
  in these spaces. The obstruction is proved, not merely unobserved.

## Reading

- **The 2-versus-3 boundary, again.**
  - The atom lemma projects each part's knots to a negation, and an odd cycle of negations fails pairwise.
  - In splice trees, a knot is fed one hub on all three places.
  - Three-place emergence stays inside the parts, and everything joining the parts is pairwise or a hub. This is the owner's thesis seen
    from composition: the boundary between two places and three is where emergence lives, and it does not pass between parts.
- **Everything is relational, and the joins carry one bit at most.** A route's relation is its length mod 2, or nothing. A length exists
  only as a count of hidden witnesses.
- **Failure lives on cuts.**
  - A knot's space keeps failing under a twist exactly when the twist is a coboundary, so the knot reads one bit of each twist pattern:
    whether its holonomy vanishes.
  - Atoms are signs: a Fano unit inserted on an incidence acts as one twist. This is why the twisted cube's proper cuts can be twisted.
- **Hubs are where the knot selects.**
  - A system in which every distinction lies in at most two knots has fewer knots than distinctions. By Seymour's bound it never fails.
  - So the knot's failure, which is its selection of its spaces, needs distinctions shared three ways, which are hubs.
  - Native (fan-out two) composition and selection do not meet in one system.
  - This is elementary, and it is recorded here as interpretation.

## Literature

- **Classical.**
  - Seymour's bound (1974) and sign-nonsingularity (Brualdi–Shader).
  - Pfaffian signings and their uniqueness up to switching (Little; Lovász–Plummer).
  - The cactus of 2-edge cuts and tight cut decompositions (Lovász; Lovász–Plummer).
  - Frustration of signed cycles (Harary).
- **Ours.** The atom lemma (KNOT-COUPLING), the point lemma and Lemma 1 (THREEFOLD-AMPLITUDE), the dictionary (THREEFOLD-SPACES), the cycles
  of Fano blocks (THREEFOLD-SPACES C) and complementarity (KNOT-COMPOSE).
- **New here.**
  - The two-interface theorem with signs.
  - The shift lemma and twist rule.
  - Knot meets knot only pairwise.
  - The reading against the program's definitions.
  No source checked states them.
- **Folklore risk.** Moderate for A and C(2); high for B's graph facts and for C(1) as a matching-theory fact.

## Pending the owner

- **The note.** `SELECTION-NOTE-20261101-001` needs an erratum to item (5), Section 6 and Theorem 12 before it is shared. Nothing has
  been sent.
- **The old record.** `KNOT-COMPOSE-20261101-001-D001` should be marked superseded by `NATIVE-PATHS-20261101-001-D001`, text preserved.
  The one earlier cross-epic supersession was made at the owner's request, so it awaits the owner.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — native paths and separation through hubs on the knot's spaces | **Status:** Successful | The first check is answered: routes are fixed by the space. Native paths of knots between parts are obstructed: the parts meet pairwise or through hubs, and knot meets knot only pairwise. Cuts of four or more channels with other kinds of side remain unclassified. |
| Local direction — paths in the knot's own spaces | Practically exhausted | A–C classify every interface that could carry a hub-free knot. Retain the two-interface theorem, the twist criterion and the pairwise-only theorem. Reopen only if a hub-free knot-to-knot interface is found outside cuts, which C excludes for cuts. |
| Broader exploration — composed topology (topology program) | Known alternatives | Laws that compose like cycles have native routes and a bond distance (NATIVE-NETWORK, 2026-10-21). The knot selects its spaces but does not compose that way; parity composes but selects nothing. Not assessed: four-place laws. |
| Long-term goal — the ladder from first emergence to composed topology and distance | Obstruction learned | Through the knot's own spaces the ladder stops at hubs. The missing bridge is a law that both selects its spaces and composes natively. |
| Next recommendation — selection versus composition | **Next step:** Full pivot, from paths in the knot's spaces to whether any law both selects and composes natively. First discriminator: test the five weak four-place classes (13–17 of FOUR-PREFER, the only candidates for selection besides the knot) for cycle-like composition (KNOT-CIRCUITS and CYCLE-TOPS criteria). | If none composes like cycles, then up to four places selection and native composition exclude each other: a dichotomy linking the selection and composition arcs. If one does and also fails, it is the first law to do both. Alternatives: the note's erratum and reissue, a conversion if the owner wants it shared (1/3); counted length as a measure, which needs a doctrine decision (1/3). |
| Interest — selection versus composition | **2/3 — Promising** | It is the one question that joins the two arcs, and its first test is finite. Main uncertainty: the likely answer is negative, and part of it may follow from known clone theory. |
| Execution — that action | Deferred to the owner | No new epic opened. Bound: five relations, existing criteria. Stop if the criteria cannot be applied to four-place relations without new theory; then record the obstruction and return to the alternatives. |
