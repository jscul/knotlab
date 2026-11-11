# Steering the knot sphere's dissonance by re-signing

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern. Results are unchanged;
the earlier text is in git history.

Epic `RESIGN-STEER-20261107-001` (program learning), 2026-11-07.

## The question

- **The approval.** The owner's go-ahead of 2026-11-08 ("Yes, let's do B1, growth as a law and also B2") took up the parked
  direction on steering a dissonance by re-signing. It is the first concrete step toward the owner's learning picture: a point with
  a strength like charge, moving through a learned network of knots, with learning orienting the logic to guide it to a resolution.
- **The setting.** On a Kasteleyn-signed knot sphere no change of state removes the dissonance: some line is always violated
  (`COUNT-SURFACES-20261107-001`). That forced dissonance is the point. Learning is changing signs, which changes the law and not
  the state.
- **The questions.**
  - Does one sign change always move the dissonance out of the states and into the law, as two even faces, wherever they sit?
  - Can sign changes made only where dissonance is seen carry it to any chosen line, and what does a closed learning walk do?
  - Does a rule that sees only an even face's lines and a target signal do so? How does the number of states consistent with the law
    depend on where its two even faces sit?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Bookkeeping.** In every state and law, violated lines minus over-agreement plus half the number of even faces is 1. One sign change moves at most one unit between state and law. With four or more even faces every state over-agrees somewhere. | proved (from the count) | A |
| 2 | **Two even faces suffice, wherever they sit.** On every simplicial knot sphere, every law with exactly two even faces is satisfiable. So one sign change at the violated line always moves the dissonance out of the states, and every line is the violated line of some flat state. | proved (Euler and Hall); known-with-delta | A |
| 3 | **The unlearned law prefers no place.** Every line is the violated line of exactly 2 N(T) flat states, N(T)² = det(B Bᵀ) / (n0 n1 + n1 n2 + n2 n0). Two even faces of different colours never allow fewer matchings than two adjacent ones. | proved (Kasteleyn, the 3-colouring kernel, Cauchy–Binet); no overlap found | A |
| 4 | **Learning alone steers.** With the state fixed, sign changes made only at the violated line or at an even face carry the dissonance from any line to any line, through configurations holding only the forced unit. A closed learning walk equals a block change of state. | proved (alternating paths); known-with-delta (the worm algorithm of dimer models) | A |
| 5 | **A local rule suffices.** A rule that sees only the lines at one even face and the distance to the target, and never steps straight back, reached 2,399 of 2,400 targets within 40 m steps on K_2–K_8 and K_10. Strict descent stalls, a random walk slows with size, and a decoy signal fails. | computed (exploratory) | B |
| 6 | **The halves repel and the corners attract.** The count of consistent states is least when the two even faces touch, where theorem 3 makes it N(T), and grows with their separation like a power near 1/2: fitted slopes 0.46 on K_12, 0.49 on K_16 and 0.51 on K_20, as for two unit holes in lozenge tilings. From every source the maximum sits at a corner, and corners carry more states than other faces at the same distance. | computed (exploratory) | B |
| 7 | **A learner that keeps the most states parks the halves on corners.** Moving one even face at a time to the neighbour with the most consistent states, all 144 runs on K_3–K_8, and six more on K_9 and K_10, stopped with both even faces on corners; 33 of the 144 reached the best pair, antipodal corners. | computed (exploratory) | B |

## Answer

Yes, on every count asked. One sign change at the forced dissonance always moves it out of the states and into the law, as two even faces that can sit anywhere, and the law with nothing learned puts the dissonance on every line equally often. Sign changes made only where dissonance is seen carry it to any line while the state holds still. On the sphere that is everything learning adds to behaviour, since a closed learning walk is a change of state. A rule that sees only one even face's lines and a target signal does it in practice. Left to keep the most states consistent, the two halves repel each other like equal charges and settle on the sphere's corners.

## Reading

**Interpretation, not a theorem.** In the owner's picture, as read in the register of assumptions (A20, A21):
- **The point** is the forced dissonance. In dimer language it is a trimer: the violated line covers all three of its faces. Its
  strength is its index, 2, which no change of state alters.
- **Rationalization** is one sign change at the point. The point leaves the states at once and sits in the law as two half-charges,
  the even faces, each of index 1. This works wherever the halves end up (conclusion 2).
- **Learning** carries the halves. On the sphere this is all that learning can do beyond behaviour: a sign change that keeps the
  even faces where they are is a change of state in disguise (a gauge), and a closed learning walk is a change of state
  (conclusion 4).
- **The unlearned law is neutral.** It puts the point on every line equally often (conclusion 3). Where the point goes is left to
  what is learned.
- **Strength as stability.** The count of consistent states gives the halves a second, entropic notion of strength: positions with
  more consistent states are more stable. The halves are least stable when they touch and settle on corners (conclusions 6, 7),
  where the sphere's curvature, which forced the dissonance, sits.

## Literature and provenance

- **Sources.** The count and the matchings: `COUNT-SURFACES-20261107-001A`. Flat states and vortex steps: `FLAT-STATES-20261107-001A`.
  Test spheres: `SPHERE-GROWTH-20261107-001A`.
- **Classical inputs.** Kasteleyn's theorem; Hall's theorem; Heawood's 3-colouring theorem; complementary Plücker coordinates and
  Cauchy–Binet.
- **Nearest known work.**
  - Monomer–monomer correlations of dimer models (Fisher and Stephenson 1963).
  - Worm and directed-loop algorithms for dimers (Sandvik and Moessner 2006; Alet et al. 2006), which move two monomers along
    alternating paths and close as a loop update.
  - Ciucu's electrostatics of holes in lozenge tilings (Memoirs AMS 178, 2005; later papers): holes interact like two-dimensional
    charges, and correlations of unit holes scale like a power 1/2 of the distance.
  - Triangular Ising antiferromagnet ground states as honeycomb dimers (Blöte and Hilhorst 1982).
- **The new part.** The uniform count over lines with its closed form (no overlap found in a bounded search); the knot's own law as
  the setting, where the dissonance is forced and the even faces are the law's marks; the reading of learning.

## Assumptions taken by default

- **A26, a learner acts only at dissonance while the state holds still.** Theorem 4 and ticket B hold the state fixed and let signs
  change only at the violated line or at an even face, with the target signal supplied from outside.
- **A27, a law is weighed by how many states it allows.** Conclusions 6 and 7 use the uniform count of consistent states as the
  law's weight.
- A20 and A21 gain history lines: the first step of the steering direction ran, and the index predicts every move.

## Stress test

One size past what was checked, before the commit publishes the claims:
- **Ticket A.** The theorems are proved. Check 7 also ran them past their K_2–K_6 range: on K_7 and K_8 every single sign change
  and 300 random pairs of faces are satisfiable, the flat-state count is the same on every line and equals the closed form, and 30
  steering runs each reached their targets.
- **Ticket B** (`stress_test.py`, `stress_test.json`). The local rule reached 300 of 300 targets on K_12. The fitted slope on K_20 is
  0.51 over distances 2–10. Four ascents on K_9 and two on K_10 all stopped with both even faces on corners.
- **Public summaries.** The goals doc, the knot intuition entry and the discovery records state each claim at its checked range.
- **Prior work.** The searches are listed in ticket A's nearest known results. None found the uniform count.

No claim failed, so there is no correction.

## Ratio

Since the epic opened:
- **Substantive.** One proof family and one experiment.
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
| This attempt — steering the forced dissonance by re-signing (B2) | **Status:** Successful | Re-signing always moves it into the law and carries it anywhere |
| Local direction — steering on the knot sphere | Practically exhausted | Every question asked is settled on the sphere; the force is fitted, not proved |
| Broader exploration — G15's open parts | Known alternatives | Handles (B6), many points (B3), layers through naming knots |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | The point, its strength, rationalization and steering have proved forms |

**Corrections:** none. **Goals:** G15 checkpoint, capability gained; backlog B2 marked taken, B6 parked (learning in handles), B3
updated. **Assumptions:** A21 confirmed on the sphere, with its boundary drawn; A20 kept as Assumed with a history line; A26 and
A27 added.

- **What is left on the sphere.** The force between the halves is fitted, not proved, and the layers of B2's third hypothesis were
  not studied.
- **What the steering line keeps.** Theorems 1–4 and the local rule.
- **The missing bridge to G15.** A learned network, not one fixed sphere: whether learning holds information that behaviour cannot,
  and how points cross levels.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Learning in handles (B6) | 2/3 — Substantial | 2/3 — Testable | Winding walks on the Fano and thin even tori → every class-forced dissonance removed, or one no walk removes | Selected · awaiting go-ahead |
| 2 | Many points at once (B3) | 2/3 — Substantial | 2/3 — Testable | Two pairs of even faces under the local rule in every order → order-free, or a scheduler needed | Alternative · deferred |
| 3 | Layers through a naming knot | 2/3 — Substantial | 1/3 — Stated | A two-level network joined by a parity naming knot → a point crosses levels, or cannot | Alternative · deferred |
| 4 | The force as a theorem | 1/3 — Incremental | 2/3 — Testable | Asymptotics of two holes on the octahedral sphere → exponent 1/2 and corner charges, or a gap | Alternative · deferred |
| 5 | A note on the uniform count | 1/3 — Incremental | 3/3 — Ready | Theorem 3 with a replay → a short reviewed note | Alternative · deferred |

1. **Learning in handles.**
   - **Ratings.** Payoff: on the sphere learning adds to behaviour only where the even faces sit; a torus would show whether
     learning can also hold information that no change of state reaches, its homology class, tying G15 to G4 (emergence lives in
     handles). Concreteness: the classes, the tori with class-forced dissonance (`COUNT-SURFACES-20261107-001A` theorem 5) and the
     walks exist. The uncertainty is the walk's passage through over-agreement, since two even faces on a torus force a unit of
     opposite dissonance.
   - **Connection and bound.** It is the selected step: one epic on lattice tori up to 40 points. It awaits a go-ahead under the
     owner's request to wrap up before opening new directions, and is parked as backlog B6.
2. **Many points at once.** The owner's own stretch goal. Several pairs of even faces force over-agreement (theorem 1), so points
   must interact; whether their moves need a scheduler is a sharp question. It is deferred because handles decide first what
   learning can hold.
3. **Layers.** B2's third hypothesis, still only stated: no network built by naming patterns has been set up as a drawn knot pattern with
   dissonance yet.
4. **The force as a theorem.** It would turn conclusion 6 into a statement with proof, a refinement of a known electrostatic
   picture (Ciucu) on a closed polyhedral surface.
5. **A note.** It would make theorem 3, the one result with no overlap found, independently reviewable.

## Final report as sent

Sent to the owner on 2026-11-08 at 06:08 UTC and copied here verbatim.

B2 is done and published as epic RESIGN-STEER-20261107-001, and everything the backlog entry asked is now answered.

- **Rationalizing always works.** One sign change at the knot sphere's forced dissonance moves it out of the state and into the law, as two even faces that can sit anywhere. This is proved for every simplicial sphere.
- **Learning steers it.** With the state held fixed, sign changes made only where the dissonance sits carry it to any line.
- **The untrained law has no favourite line.** Every line carries the dissonance in exactly as many least-dissonance states. I found no prior work for this count or its closed form.

In your terms, the point is the forced dissonance and its strength is an index no change of state can alter. Rationalizing splits it into two half-charges in the law. A local rule steering one half reached 2,399 of 2,400 targets. The two halves push each other away like equal charges, with the state count growing as distance^0.5. A learner that keeps the most states parked both halves on the sphere's corners in all 150 runs.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — steering the forced dissonance by re-signing (B2) | **Status:** Successful | Re-signing always moves it into the law and carries it anywhere |
| Local direction — steering on the knot sphere | Practically exhausted | Everything asked is settled; the force is fitted, not proved |
| Broader exploration — G15's open parts | Known alternatives | Handles (B6), many points (B3), layers |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | Point, strength, rationalizing and steering now have proved forms |

**Corrections:** none. **Goals:** G15 checkpoint, capability gained; B2 marked taken, B3 updated, B6 parked. **Assumptions:** A21 confirmed on the sphere: a sign change that leaves the even faces in place is a change of state in disguise. Two entries added: A26 (the learner acts only at the dissonance while the state holds still) and A27 (a law is weighed by how many states it allows). A20 gets a history line.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Learning in handles (B6) | 2/3 — Substantial | 2/3 — Testable | Winding walks on the Fano and thin even tori → every dissonance forced by the sign class removed, or one that can't be | Selected · awaiting go-ahead |
| 2 | Many points at once (B3) | 2/3 — Substantial | 2/3 — Testable | Two pairs of halves updated in every order → order-free, or a scheduler is needed | Alternative · deferred |
| 3 | Layers through a naming knot | 2/3 — Substantial | 1/3 — Stated | A two-level network joined by a parity knot → a point crosses levels, or can't | Alternative · deferred |
| 4 | The force as a theorem | 1/3 — Incremental | 2/3 — Testable | Two-hole asymptotics → exponent 1/2 proved, or a gap | Alternative · deferred |
| 5 | A note on the uniform count | 1/3 — Incremental | 3/3 — Ready | The count theorem with a replay → a short note | Alternative · deferred |

B6 asks whether learning can hold something no change of state can. On the sphere it can't, but on a torus a walk around a handle changes the sign class. I've parked it under your wrap-up request; say go and I'll start it.
