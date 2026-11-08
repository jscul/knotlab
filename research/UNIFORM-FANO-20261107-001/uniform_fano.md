# The only uniform contradiction

Epic `UNIFORM-FANO-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, let's update the skill, then let's pursue ii, then continue on to i". This is (ii) from
  `UNIFORM-SPHERES-20261107-001`.
- **The question.** Are there uniform knot laws other than the Fano plane whose knot contradicts itself?
- **Why the count is not the issue.** With uniform signs the count never forces a uniform law's lines (UNIFORM-SPHERES-20261107-001A).
  So such a contradiction would have to be of the Fano kind.
- **Rating at the start**, in the new two-scale format: Payoff 1/3 (Incremental), Concreteness 3/3 (Ready).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Non-constant signs are harmless.** With non-constant uniform signs every Cayley law's knot is satisfied by the all-zero assignment. | proved (one line) | A |
| 2 | **The brace lemma.** A simple cubic triple system whose automorphisms are transitive on points and on lines has a brace for its incidence graph. Two translates of a smallest tight shore share at most one point, and counting forces a two-point shore holding a line. | new as far as found; proved | A |
| 3 | **Fano is the only one.** By Seymour's dictionary and McCuaig's theorem, such a system is not 2-colourable only if it is the Fano plane. Among uniform laws with uniform signs, the Fano plane is the only one that contradicts itself. | known-with-delta; proved | A |
| 4 | **Census.** 439 simple Cayley laws (orders 3–720) are all braces, and only the Fano plane fails. | computed | A |

## Answer

There are none. The Fano plane is the only uniform law whose knot contradicts itself. Every other contradiction of the knot needs
non-uniformity: curvature defects that carry the count, or Fano atoms glued without symmetry.

## Reading

**Interpretation, not a theorem.**
- **Coherence.** Uniform worlds are coherent, with one exception, which is a single handle.
- **What the knot needs.** For a contradiction, and so for its hardness, the knot needs a law that tells places apart. That points (i)
  at the right question: how can a law tell places apart by itself?

## Literature and provenance

- **Classical inputs.**
  - Seymour 1974 and Bassett–Maybee–Quirk (the dictionary, via THREEFOLD-SPACES-20261030-001A).
  - McCuaig 2000 (*Even dicycles*: F7 is the only strongly 2-connected digraph without even dicycles).
  - Lovász–Plummer and Robertson–Seymour–Thomas 1999 (braces and strong 2-connectivity).
- **The new part.** The brace lemma for point- and line-transitive systems. Folklore risk is moderate.

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

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — uniform contradictions beyond the Fano plane | **Status:** Successful | None exist among point- and line-transitive laws: the brace lemma plus McCuaig. Checked on 439 Cayley laws. |
| Local direction — contradictions of uniform laws | Practically complete | Open but incremental: laws with one kind of point and no transitive symmetry; non-uniform signs on uniform laws. |
| Broader exploration — question 9 (shape from a uniform local law, nothing drawn) | Known alternatives | Self-built surfaces (UNIFORM-SPHERES), rulers and the number line (LOGIC-AXIS), growth at open ends (OPEN-END-GROWTH), circles (LOGIC-CIRCLE). |
| Long-term goal — question 9 and "hardness at three places" | Capability gained | Uniform laws are coherent, with only the Fano plane as exception. Contradiction and hardness need a law that distinguishes places. |
| Next recommendation — (i), already directed by the owner | **Next step:** Continue to (i): laws that distinguish places by themselves. First a scoping step, then a first discriminator. **Scoping:** (a) laws with two kinds of points that close into large spheres, background (3,3,3) with twelve (2,3,3) defects, are the knot spaces of (4,6)-fullerenes, which is classical; (b) define a local growth rule precisely, and ask whether such a rule can place the six digons itself so that a law grows its own sphere and with it the knot's contradiction. | Answers how a law can tell places apart without being told, which is question 9's open rung, "a law that lays out its own network". |
| Interest — (i) | **Payoff 3/3 — Barrier · Concreteness 1/3 — Stated** | **Payoff:** a law that grows its own sphere would produce space and the knot's hard contradiction from a rule, nothing drawn. **Concreteness:** "local growth rule" is not defined yet, and the expected tension is that a bounded deterministic rule grows one shape, so unbounded families need information or chance. **Uncertainty:** whether any natural rule class gives spheres large in every direction. |
| Execution — that action | Started | Continuing at once under the owner's "then continue on to i". The scoping step comes first. |
