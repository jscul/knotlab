# A growing law needs a shared coin

Epic `GROW-COIN-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner's standing mandate of 2026-11-07, to run research on our own and follow what is promising. This is
  `SPHERE-GROWTH-20261107-001`'s selected next step (grow K_m by a local process, Payoff 2/3, Concreteness 2/3), sharpened.
- **The question.** A finished sphere cannot be checked as round without a hidden bit on every incidence. Can a *growing* law do
  without that bit?
- **The standard.** As in the canonical test, no scheduler may supply an input. A growth result belongs to the law only if it holds
  in every growth order, and a history kept with the world is one more witness.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Refinement keeps the shape.** Subdividing every triangle of K_m into j² gives K_{jm} (j = 2, 3). A step is all-or-nothing in every order, since a split edge forces both its triangles to split. It maps a capped tube to a capped tube, so it keeps the seed's shape and never places a corner. | proved | A |
| 2 | **Ring accretion.** Growing annuli around a corner, with each ring vertex completed to degree 6 or a convex turn made a corner, gives K_m exactly when the four turns of one ring become corners. | proved | A |
| 3 | **Turns decided one at a time close lopsided spheres.** Every choice pattern up to 100 triangles closes into 38 distinct spheres, 3 of them round and only from uniform patterns. With an independent coin at every turn, 12 of 400 runs closed non-round, up to 646 triangles. | computed | A |
| 4 | **The coin must be carried.** In single-strip accretion a turn is decided at a radius-w window that is the same in every lap (w ≤ 5). A label-free rule therefore cannot tie the four equator corners together. One bit kept for one lap does, but that bit is history the process supplies: a hidden witness, like the seam bits. | proved, windows computed | A |
| 5 | **A rule read off one order.** The radius-5 window law of the single-strip order, run in random orders, closed only K_1 and K_2 (69 of 200 runs) and was otherwise stuck. | computed | A |

## Answer

Growth does not remove the witness. Refinement keeps a sphere round without one, but only by scaling a seed that is already round:
it never places a corner. Accretion has to place corners, and making the four equator corners agree needs a shared coin. A label-free
local rule cannot share one, so it also closes lopsided spheres. Sharing it takes a bit carried by the process, which is a witness.

## Reading

**Interpretation, not a theorem.**
- **Where the coin lives.** In refinement the edges share the decision: a split edge forces both its triangles to split. In accretion
  nothing in the flat region between two corners links them, so their agreement must be carried.
- **For question 9.** A law can grow space that is already round, by refining it, with nothing hidden. To lay out a new round sphere
  it needs a witness, whether the sphere is checked when finished or grown corner by corner.

## Literature and provenance

- **Classical inputs.**
  - Decorated and undecorated local rules: Levitov (1988), Mozes (1989), Goodman-Strauss (1998), Fernique–Ollinger (2010). In their
    terms `SPHERE-GROWTH-20261107-001`'s round spheres are sofic, with one bit, but not of finite type.
  - Local growth rules that stall without non-local information (Onoda, Steinhardt, DiVincenzo and Socolar 1988; Dworkin and Shieh
    2016), local-rule capsid assembly with conformational states (Berger, Shor, Tucker-Kellogg and King 1994), and tile complexity in
    algorithmic self-assembly (Rothemund–Winfree 2000; Kao–Schweller 2008; Doty 2010).
  - Uniform subdivision is the Goldberg–Coxeter construction with parameters (j, 0).
- **The new part.** The refinement/accretion contrast for the knot spheres, the census of lopsided closures, and the decision-window
  identity. Classified known-with-delta.

## Ratio

Since the epic opened:
- **Substantive.** One proof family.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — can a growing law do without the hidden bit? | **Status:** Successful | Refinement can, by never placing a corner; accretion cannot without a carried bit |
| Local direction — growing round spheres | Unresolved | Ring accretion is settled; a theorem for every accretion law is open |
| Broader exploration — G1, the plane and the line | Known alternatives | The pinwheel atlas; rulers, open-end growth, circles |
| Long-term goal — G1 Space from a law | Obstruction learned | Placing corners consistently needs a witness, checked or grown |

**Corrections:** none. **Goals:** G1 checkpoint, obstruction learned.

The attempt leaves open whether some accretion law with other moves could keep the coin in the shape of its growing edge in every
order. The missing bridge to G1 is a law that lays out a new round sphere without a witness, and the evidence here is against one.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Hardness without roundness (G3) | 2/3 — Substantial | 2/3 — Testable | Extend SPHERE-WIDTH's bound to spheres with far-apart corners → a proof, or a fat sphere that is easy | Selected · started |
| 2 | Growth cannot stand in, for every accretion law (G1) | 2/3 — Substantial | 2/3 — Testable | Formalize accretion laws; an order that splits the equator, then a completion → a theorem, or a law that escapes | Alternative · deferred |
| 3 | Witness economy (G1) | 1/3 — Incremental | 2/3 — Testable | The fewest non-zero hidden bits that single out K_m → a lower bound, or a sparser law | Alternative · deferred |

1. **Hardness without roundness.** Payoff 2 because, if the knot's hard contradiction needs only far-apart corners and not
   roundness, a law that tells places apart by local coins alone grows hard instances with positive probability, while tubes stay
   easy (G3, hardness at three places). Concreteness 2 because SPHERE-WIDTH's lower bound rests on label states and a density
   argument around one vortex, which should survive moved corners. A first data point is in hand: 14 grown lopsided spheres of 64 to
   746 triangles have elimination width 1.0 to 1.9 √n, against 2.1 √n on K_m. These are upper bounds only. The main uncertainty is
   whether the density argument uses symmetry or only corner spread. Bound: one epic.
2. **Every accretion law.** Payoff 2 because it would settle, for spheres, whether growth can stand in for the witness, with a
   theorem rather than a census. Concreteness 2: an adversarial order can split the four turns, and the census shows completions
   exist. The uncertainty is a general completion argument.
3. **Witness economy.** Payoff 1: it refines how much witness roundness costs. Concreteness 2: a lower bound needs a way to repeat a
   band of a marked sphere, which only works for bands without bits.
