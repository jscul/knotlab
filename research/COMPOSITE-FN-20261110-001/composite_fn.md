# Which functions a composite computes

Epic `COMPOSITE-FN-20261110-001` (backlog B109 with B112 folded in, G15; program learning), 2026-11-10, at the coordinator's go-ahead.
Pre-registered in [preregistration.md](preregistration.md), frozen in commit `36d02b296` before any run. Proof families:
`proofs/COMPOSITE-FN-20261110-001A/` (AND for critical hosts), `…B/` (a search outside the proved class), `…C/` (points and a shared
line).

## The answer

AND is the only function a composite computes over any host built from knot spheres and class-forced lattice tori, proved by hand for
the stated class: hosts in which every line is **critical** (some state violates it and no other line).

- **Lemma M (by hand):** a composite's function is f(a) = OR, over the host's minimal unsatisfiable sets of lines, of the AND of the bits
  of the atoms whose lines they contain. So an OR or a projection needs a line whose deletion leaves the host unsatisfiable.
- **Lemma H (by hand):** every set S of lines of a two-coloured sphere touches at least |S| + 2 faces (Euler characteristic and Alexander
  duality), so by Hall's theorem every line of every Kasteleyn knot sphere has a state violating it alone. This settles backlog B110 and
  makes theorem N of `NEST-ATOMS-20261110-001` hold on every knot sphere host.
- **Lemma G (by hand):** growing good atoms whose closed spaces are critical keeps a host critical, at any depth. Class-forced lattice
  tori are critical in their forced class (least states violate one line, `LEARN-HANDLES-20261109-001A`, and translations move it).
- **Checks (computed):** every line of 16 spheres (octahedral to K_8, tubes, grown spheres, branched covers) is critical; the AND held
  exactly over a tube, a grown sphere and a double cover.
- **The search outside the class (ticket B):** the frozen family of branched double covers (six tori and one genus-2 space; the Fano
  torus's cover was undefined under the frozen rule) had no unsatisfiable class at all. So no host there: S1 holds vacuously, and the
  search found neither an OR nor a counterexample.

**Ticket C (B112), its frozen prediction failed.** On fresh composites, 1,199 of 1,200 pairs of disturbances at distance 2 or more
combined, but one did not: one point's repair flipped a point on a line through the other. "Points interact only through a shared line"
is false as stated. The corrected locality is proved by hand (lemma L): two disturbances combine in every order when the lines and faces
touched by each flip and its repair are disjoint. The earlier wording is corrected (Narrowing, `docs/CORRECTIONS.md`).

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Lemma M: the function is the OR of ANDs over minimal unsatisfiable sets | proved by hand |
| Lemma H: every line of every Kasteleyn knot sphere is critical | proved by hand; checked on 16 spheres |
| Lemma G and the theorem: AND only over every host grown from spheres and class-forced lattice tori | proved by hand, with the tori's least states computed to 40 points |
| The AND over three non-octahedral spheres | exact, 16 classes each |
| No unsatisfiable class in seven branched covers | exhaustive per host |
| One distant pair of 1,200 does not combine | computed |
| Lemma L: disjoint supports combine in every order | proved by hand |

## Against the pre-registration

Ticket A's checks held. Ticket B ran on six of the seven named hosts: the frozen rule names no second branch point on the Fano torus
(its graph is K_7), and no substitute was chosen; S1 held only vacuously. Ticket C's L1 failed and its failure line was crossed; L2 held
(94% of pairs sharing a line interact). The proofs were written after the runs.

## What it changes

- **The layered memory computes conjunctions.** Over every host the program can build, each level reads the AND of the bits below. An OR
  would need a host with a non-critical line, which none of the program's spaces has, and no space off the sphere in the search was even
  unsatisfiable. Whether every host is critical is backlog B115.
- **B110 is closed** by lemma H, and theorem N's host hypothesis holds for every knot sphere.
- **Parallel points.** The locality claim of `MANY-POINTS-20261110-001` narrows from "no shared line" to "disjoint supports", which is
  proved. The counts there stand.

## Perspective

In constraint-satisfaction terms a composite's function is the "satisfiability under deletion" of its host, a standard reading of minimal
unsatisfiable sets; lemma H is a Hall-type count of the kind used for matchings in planar bipartite graphs. What the program adds is that
on its spaces every line is necessary, so its layers can only conjoin. No novelty scan was run.

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50, A52. None added or changed.

## Corrections

One, logged in `docs/CORRECTIONS.md` (commit `503f2cc7f`): "points interact only through a shared line" (`MANY-POINTS-20261110-001`),
**Narrowing**, worded beyond its evidence.

## In the owner's words

The layers can only say "all of these". Every pattern the program can grow is held together by every one of its lines, so a level stands
for its line only when every pattern inside it does. Many points can still move at once, as long as what each one and its repair touch
stays apart.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which functions a composite computes (B109) | **Status:** Successful | AND only, proved for every host the program can build; the search found no other host |
| Local direction — the layered memory | Practically complete for this phase | its rule, its units, its parallel moves and its function are all proved |
| Broader exploration — learning program | Known alternatives | a native choice of atom, naming knots as layers, whether every host is critical |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | a layered memory whose logic is proved: conjunctions at every level |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which atom a growth law grows (B106) | 2/3 — Substantial | 1/3 — Exploratory | which uniform local rules can grow the 4-point atom at a dissonance → memory grown natively, or a reason none can | Selected · awaiting go-ahead |
| 2 | Layers through a naming knot (`NEST-ATOMS-20261110-001`#4) | 2/3 — Substantial | 1/3 — Exploratory | parity name against a three-edge cut as the channel between levels → one reading, or a second kind of layer | Alternative · deferred |
| 3 | Is every host critical (B115) | 1/3 — Incremental | 2/3 — Testable | a Hall-type count on the torus and higher genus → AND for every host, or a host with a non-critical line | Alternative · deferred |
| 4 | A writing search that reads roles (B113) | 1/3 — Incremental | 3/3 — Ready | stop on acting leaves and rerun the 96 writes → every write exact and held | Alternative · deferred |
| 5 | Capacity of the learned memory (B98) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |
| 6 | Every torus is free (B105) | 1/3 — Incremental | 2/3 — Testable | as recorded | Alternative · deferred |

- **#1 and #2** tie at the top and stay in the basket; #1 is selected because it asks whether memory can grow without being designed
  (G16), the line's open premise (A52: the experimenter chooses the atom).

**Corrections:** one, Narrowing: "points interact only through a shared line" (`MANY-POINTS-20261110-001`), corrected to disjoint
supports. **Goals:** G15 checkpoint (capability gained); B109 and B112 taken; B110 closed as answered; B115 added. **Assumptions:** none
new or changed.
**Basket:** B106, `NEST-ATOMS-20261110-001`#4; taken: B106 as the selected next step.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (05:47 UTC): the answer (AND only, proved for every host built from knot spheres
and class-forced lattice tori), why (lemma M, the Hall count on spheres closing B110, growth keeping criticality), the empty search (no
unsatisfiable class in seven branched covers; the Fano cover undefined under the frozen rule), ticket C's failed locality and its proved
replacement, the note that another thread's commit `3677826e6` took this epic's files from the shared working tree before `commit_epic`
ran, both tables above with B106 selected, the Corrections, Goals and Assumptions lines, and the Basket line.
