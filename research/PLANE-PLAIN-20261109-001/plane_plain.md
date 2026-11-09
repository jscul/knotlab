# A plane read plainly beyond tori

Epic `PLANE-PLAIN-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `GROW-PLAIN-20261109-001B` proved that a network reading its distance plainly at every stage can be grown one
  ring at a time, but that through tori of the three regular lattices such growth makes only a line: an on-time torus of large index is a
  tube. Backlog B36 asked whether a two-dimensional network of persistent contacts beyond those tori reads its distance plainly at every
  size; the coordinator selected it on 2026-11-09.
- **The question.** The first family beyond the regular lattices: the periodic plane tilings that medial, truncation and duality build
  from them. Do their tori keep every contact persistent, so that they could read distance across time at all, and why or why not?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **A contact persists exactly when it has a flip.** On tori of every shape of 13 periodic tilings, a contact persists exactly when an automorphism fixes it and exchanges its two rings. | exploratory census, exact, frozen hypothesis held | A |
| 2 | **Only the regular lattices keep every contact persistent.** On 4.8.8, 3.12.12 and the tetrakis and triakis tilings only the contacts of the base lattice persist; on kagome, 3.4.6.4, 4.6.12 and the rhombille, deltoidal and kisrhombille tilings none does. A contact between rings of different degree, or between faces of different size, never has a flip. | exploratory census, exact, frozen hypothesis held | A |
| 3 | **No plane read plainly in this family.** A two-dimensional network of persistent contacts among these tilings is a torus of a regular lattice, and those read their distance plainly at large size only as tubes. | conclusion 2 with `GROW-PLAIN-20261109-001B`, Theorem 2 | A |

## Answer

Not among the periodic tilings read. Mixing ring or face sizes takes away the flips that make contacts persist, so the only planes of
persistent contacts are the square, triangular and honeycomb lattices, and their large tori read distance plainly only when they are
thin. A plane read plainly at every size, if one exists, must keep a flip at every contact without being one of these lattices.

## Reading

**Interpretation, not a theorem.**
- **Persistence needs symmetry here.** Every contact that persists on these tilings has a half-turn that exchanges its rings
  (`LOOP-NET-20261108-001A`, Theorem 3 is the sufficient direction); no other mechanism appears.
- **Uniformity is forced.** A network of persistent contacts in this family looks the same from both rings of every contact, which
  rules out mixing ring sizes: the regular lattices are the only flat ones.
- **What is left.** Networks with a flip at every contact are, up to spacing, the orientably regular maps (`GROW-NET-20261108-001A`,
  remark), and their flat ones are the regular tori. So beyond these tilings a plane read plainly would have to be non-periodic or keep
  persistence without flips.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Return parities to length n + 1 (exact) and automorphisms from one dart.
- **Census-only.** Every conclusion: 13 tilings, tori of index 3 to 12 of their base lattices, at most 400 contacts.

## Stress test

The census reads 1,479 tori of every shape, most of which the pilot did not see (it read the n × n ones for n = 4 to 6). No separate
stress test was run.

## Literature and provenance

- **Sources.** Archimedean and Laves tilings (Grünbaum and Shephard, Tilings and Patterns); medial, truncation and dual of maps;
  `LOOP-NET-20261108-001A` for persistence and flips.
- **Classification.** Known-with-delta: the tilings are classical; the delta is which of them carry networks of persistent contacts.

## Workspace assumptions

- **Relied on.** A30, A32, A40, A41.
- **Added.** None.
- **Scope.** Thirteen periodic plane tilings of rule-60 rings with equally spaced law-(12, 12) contacts.

## Ratio

Since the epic opened:
- **Substantive.** One exploratory census (A), pre-registered.
- **Administrative.** The pre-registration, this note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a plane read plainly beyond tori | **Status:** Obstruction learned | The periodic tilings read keep every contact persistent only when regular, and those planes need freezing |
| Local direction — space read plainly | Research directions | Persistence without a flip, or a non-periodic plane, is what remains |
| Broader exploration — G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23, the growth thread); B30, B35 |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | Flat space of persistent contacts is a regular lattice, and it reads its own distance only through freezes, except as a thin tube |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned); B36 taken; backlog B38 and B39 added. **Assumptions:**
none added or changed.

- **What the attempt leaves open.** Whether a contact can persist without a flip in any network; the snub and elongated tilings; whether
  a non-periodic network keeps every contact persistent and reads its distance plainly.
- **The missing bridge to the program's composed topology.** A plane that reads its own distance across time without intervention; none
  exists among the networks read.

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Persistence without a flip (G5) | 2/3 — Substantial | 2/3 — Testable | Search small networks for a contact that persists with no automorphism fixing it and exchanging its rings → one, or a proof that persistence needs a flip in some class | Alternative · deferred |
| 2 | The remaining periodic tilings (G1, with G5) | 1/3 — Minor | 3/3 — Ready | Build the snub and elongated tilings and their duals from coordinates and read their persistence → H2 for all 22 Archimedean and Laves tilings, or an exception | Alternative · deferred |

1. **Without a flip.** Payoff 2: if persistence always needs a flip, persistent networks are regular maps and the whole question reduces to
   them; Concreteness 2: a search over small networks is direct. Main uncertainty: unequal spacing may balance returns another way.
2. **The rest of the tilings.** Payoff 1: completes the census; Concreteness 3: only constructions are missing.

**Recommendation.** Research directions, none selected; directions 1 and 2 go to the backlog as B38 and B39.
