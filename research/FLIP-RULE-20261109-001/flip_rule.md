# Does persistence need a flip?

Epic `FLIP-RULE-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `PLANE-PLAIN-20261109-001` found, on 13 periodic plane tilings, that a contact persists exactly when it has a
  flip, an automorphism fixing it and exchanging its two rings, which `LOOP-NET-20261108-001A`, Theorem 3, shows is sufficient. Backlogs
  B41 (the remaining uniform tilings) and B40 (persistence without a flip) asked whether that holds everywhere; the coordinator selected both
  on 2026-11-09, B41 first.
- **The question.** Does the flip rule hold on every Archimedean and Laves tiling, and is a flip necessary for persistence in general?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The flip rule holds on all 22 uniform tilings and duals.** On tori of the snub square, snub hexagonal and elongated triangular tilings and their pentagonal duals, as on the 13 read before, a contact persists exactly when it has a flip, and none of them keeps every contact persistent. | exploratory census, exact, frozen hypotheses held | A |
| 2 | **In general a flip is not necessary.** Among all maps of up to five contacts a contact persists without a flip from three contacts on; all such contacts there are degenerate (they send or hear nothing, or a ring or face has one or two contacts). | exploratory census, exhaustive, frozen hypothesis refuted; the degeneracy split post hoc | B |
| 3 | **Nor on non-degenerate maps.** On random maps whose rings and faces all have at least three contacts, most persistent contacts have no flip (17,992 of 21,056 at six contacts); the smallest such map has six contacts, three rings on genus 2, and its contact's closed walks are even in number at every length with no symmetry, not even of the contact graph. | exploratory census, sampled, frozen hypothesis refuted | B |

## Answer

The flip rule is a fact about the periodic plane tilings, all 22 of them, not about maps in general. Small maps persist by arithmetic:
their closed walks come out even with no symmetry pairing them. So `PLANE-PLAIN-20261109-001`'s obstruction stands as stated for periodic
tilings, and a non-periodic network could in principle keep persistent contacts without the symmetry the tilings need.

## Reading

**Interpretation, not a theorem.**
- **Symmetry where space is uniform.** On a uniform tiling the only way to cancel every return is the half-turn; on a small, irregular map
  returns can cancel by counting. Persistence is a parity condition, and parity has more solutions than symmetry.
- **What it reopens.** A plane read plainly beyond the regular lattices is not ruled out by the flip rule for non-periodic networks; it is
  ruled out only among the periodic tilings.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Return parities to length E + 1 (exact).
- **Census-only.** Every conclusion; the degeneracy split of conclusion 2 is a post-hoc classification
  (`posthoc_classification.py` beside this note), the contact-graph check of conclusion 3 a post-hoc reading of 14 kept examples.

## Stress test

E002 was the out-of-sample test of the refined hypothesis that E001's post-hoc split suggested, and it refuted it; no further stress test.

## Literature and provenance

- **Sources.** Rotation systems and map automorphisms; `LOOP-NET-20261108-001A` (the parity criterion and the flip); Archimedean and Laves
  tilings (Grünbaum and Shephard); the Conway snub.
- **Classification.** Known-with-delta.

## Workspace assumptions

- **Relied on.** A30, A32.
- **Added.** None.
- **Scope.** Equally spaced rule-60 rings with law-(12, 12) contacts.

## Ratio

Since the epic opened:
- **Substantive.** Three exploratory runs (A's census, B's exhaustive and sampled searches), each pre-registered.
- **Administrative.** The pre-registrations, this note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — does persistence need a flip | **Status:** Partially successful | Yes on all 22 uniform tilings and duals; no on small maps in general |
| Local direction — persistent networks | Research directions | Persistence by arithmetic is common on small maps; whether it survives growth is unknown |
| Broader exploration — G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23, the growth thread); B30, B35 |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | Uniform flat networks persist only by symmetry, and the only symmetric ones are the regular lattices |

**Corrections:** none. **Goals:** a G5 checkpoint (obstruction learned); B40 and B41 taken; backlog B42 and B43 added. **Assumptions:**
none added or changed.

- **What the attempt leaves open.** Whether persistence by arithmetic extends to large networks: a family of growing, non-degenerate,
  non-periodic networks whose every contact persists without flips; why the parity comes out even.
- **The missing bridge to the program's composed topology.** As before.

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Large networks persistent without flips (G1, with G5) | 3/3 — Major | 1/3 — Stated | Search for families of non-degenerate maps whose every contact persists with few or no flips, growing in size → a family, then its plain reading, or the size where it stops | Alternative · deferred |
| 2 | Why the parity comes out even (G5) | 1/3 — Minor | 2/3 — Testable | Read the closed walks of the six-contact example by length and find the pairing they obey, if any → a combinatorial reason, or none | Alternative · deferred |

1. **Large networks.** Payoff 3: a non-periodic two-dimensional network of persistent contacts would reopen the plane read plainly;
   Concreteness 1: no family yet, and fully persistent maps without flips were not counted here.
2. **Parity.** Payoff 1: an explanation of the small exceptions; Concreteness 2: the example is in hand.

**Recommendation.** Research directions, none selected; directions 1 and 2 go to the backlog as B42 and B43.

## Final report as sent

Sent to the owner on 2026-11-09 at 21:55 UTC and copied here verbatim.

B41 and B40 are closed and published together (FLIP-RULE-20261109-001). The flip rule turns out to be a fact about uniform tilings, not about networks in general.
- **B41: all 22 uniform tilings obey it (census, pre-registered).** The snub square, snub hexagonal and elongated triangular tilings and their Cairo, floret and prismatic pentagonal duals behave like the 13 read before: a contact persists exactly when it has a flip, and none keeps every contact persistent. On all 11 Archimedean tilings and their 11 Laves duals, only the square, triangular and honeycomb lattices are fully persistent.
- **B40: persistence doesn't need a flip in general (two pre-registered censuses).** I read every map of up to five contacts exhaustively (258,048 at five). Contacts persist without a flip from three contacts on, but only in degenerate ways: the contact sends or hears nothing, or a ring or face has one or two contacts. I then tested "non-degenerate ⇒ flip" on random maps of 6 to 9 contacts, and it failed too: most persistent contacts there have no flip (17,992 of 21,056 at six). The smallest example has six contacts, three rings on genus 2, and its contact's closed walks are even in number at every length (2, 4, 4, 8, 24, …) with no symmetry, not even of the contact graph. The parity just comes out even.
- **What this means for B36.** The plane obstruction stands for periodic tilings. A non-periodic, irregular network could in principle keep persistent contacts without the symmetry the tilings need, so the plane read plainly isn't ruled out there.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: does persistence need a flip | Partially successful | Yes on all 22 uniform tilings and duals; no on small maps in general |
| Local direction: persistent networks | Research directions | Persistence by arithmetic is common on small maps; whether it survives growth is unknown |
| Broader exploration: G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23, growth thread); B30, B35 |
| Long-term goal: G5 Dynamics | Obstruction learned | Uniform flat networks persist only by symmetry, and only the regular lattices have it everywhere |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Large networks persistent without flips (B42) | 3/3 | 1/3 | Find growing families of non-degenerate maps with every contact persistent and few or no flips → then read them plainly, or find where they stop |
| 2 | Why the parity comes out even (B43) | 1/3 | 2/3 | Read the six-contact example's closed walks by length → a pairing, or none |

**Corrections:** none. **Goals:** a G5 checkpoint (obstruction learned); B40 and B41 marked taken; B42 and B43 added to the backlog. **Assumptions:** none added or changed.

Commits on main: 65843d9d4 (B41 pre-registration), 7581ed1fa and b28d92b98 (B40's two pre-registrations; the second tests a refinement I made after seeing the first run, labelled post hoc), 302e84eec (the epic), aa1f6591a (shared docs). Every run took seconds and nothing is running. No direction is selected; your call.
