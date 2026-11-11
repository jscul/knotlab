# A proof of the atom rule

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `ATOM-RULE-20261110-001` (backlog B87, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md). Proof family: `proofs/ATOM-RULE-20261110-001A/ATOM-RULE-20261110-001A-P001_the_atom_rule_for_every_knot_sphere/`
(long-running row ATOM-RULE-A1).

## The answer

Proved, computer-assisted, for every octahedral knot sphere with separated Fano pieces (atoms whose neighbourhoods do not overlap):

1. each atom acts as its line in exactly one of the four classes of its own handle, independently of the others;
2. if every atom acts, no state satisfies every line;
3. otherwise every acting atom holds a unit of the floor dissonance in every state that satisfies every line.

The proof: a homology decomposition (each atom's handle is a direct summand) and a locality lemma by hand; a finite local check on 2,700
splices covering every line of K_5 to K_7 and every line orbit of K_2 to K_4, in which each acting class's local system is unsatisfiable;
and a classification of line neighbourhoods, four types over every line of K_2 to K_8, none new beyond K_3, with a structural reason (the
sphere is the triangular lattice away from six corners, and a neighbourhood meets at most one). So "the acting atoms are the address" is a
theorem on these spheres, not only an observation.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Lemma A: the handles are direct summands | proved by hand (Mayer–Vietoris) |
| Lemma B: an atom's role and local system depend only on its own handle's class and its gadget type | proved by hand |
| Lemma C: four neighbourhood types, none new beyond K_3 | structural argument by hand; classification computed to K_8 |
| The finite local check (one acting class per gadget, locally unsatisfiable; three transparent) | exhaustive computation on 2,700 splices |
| Theorem 1 for every K_k, separated atoms | proved, from the above |
| Free units when fewer atoms act than there are units | not proved (computed in `ADDRESS-STEER-20261110-001`) |

## Against the pre-registration

The expectations held: one acting class per gadget, locally unsatisfiable, and the types stabilized (from K_3, earlier than the K_4
expected). Two runs were stopped and restarted (the long-running row records why); the frozen check itself was unchanged except that every
line of K_5 to K_7 replaced the orbit representatives, which covers more.

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a proof of the atom rule (B87) | **Status:** Successful | proved for every octahedral knot sphere, separated atoms |
| Local direction — the learned memory in atoms | Practically complete for this phase | written, held, rewritten, read, and the rule proved |
| Broader exploration — learning program | Known alternatives | other spheres, stuck states, a write-up |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | a learned memory with a proved rule |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A note on the learning line (B95) | 2/3 — Substantial | 3/3 — Ready | write the arc from learning in handles to the proved atom rule, with evidence classes → a note the owner can read and check | Selected · awaiting go-ahead |
| 2 | The atom rule beyond octahedral spheres (B96) | 1/3 — Incremental | 2/3 — Testable | the local check on other triangulated spheres → same rule, or a new type that breaks it | Alternative · deferred |
| 3 | Learner local minima (B90) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1**: fourteen epics since the owner's question have built one line, from a dissonance that learning removes by winding, through native
  targets, grown handles, layers and a learned register, to a proved rule. A note in plain words, marking what is proved and what is
  computed, would let the owner judge it as a whole.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B87 taken; B95 and B96 added. **Assumptions:** none new.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (03:56 UTC).

**B87 done: the atom rule is now a theorem, not just a small-case observation.** On every octahedral knot sphere, with Fano pieces placed so their neighbourhoods don't overlap:
- each atom acts as its line in exactly one of the four winding classes of its own handle, independently of the others;
- if every atom acts, no state satisfies every line;
- otherwise every acting atom holds a unit of the leftover tension.

The proof is computer-assisted. Two lemmas are by hand: each handle is its own summand, and an atom's behaviour depends only on its own signs. A finite local check covered 2,700 splices on K_2 to K_7. A classification found only four kinds of line neighbourhood from K_2 to K_8, none new after K_3, because the sphere is a flat lattice except at six corners. Not proved: that extra units are free when fewer atoms act. That part is computed only. This didn't need max effort.

**Your two asks on B88.** (1) Its failure criteria were frozen in commit 1be11cd69 at 02:32 UTC, before the run started at 02:33, so B88 is not post hoc. (2) The atom rule says nothing about the 10 runs stuck one unit above the floor, since it only covers floor states. They're recorded as an open observation, B90.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: proof of the atom rule (B87) | **Status:** Successful | proved for every octahedral knot sphere, separated atoms |
| Local direction: the learned memory | Practically complete for this phase | written, held, rewritten, read, rule proved |
| Broader exploration: learning program | Known alternatives | other spheres, stuck states, a write-up |
| Long-term goal: G15 | Capability gained | a learned memory with a proved rule |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A note on the learning line (B95) | 2/3 — Substantial | 3/3 — Ready | write the arc from B6 to B87 in plain words, proved vs computed → a note you can check | Selected · awaiting go-ahead |
| 2 | The rule beyond octahedral spheres (B96) | 1/3 — Incremental | 2/3 — Testable | local check on other spheres → same rule, or a breaking type | Alternative · deferred |
| 3 | Learner local minima (B90) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G15 checkpoint; B87 taken; B95, B96 added. **Assumptions:** none new.
