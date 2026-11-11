# Are maps of held points unate

Epic `UNATE-20261111-001` (backlog B136, G15 with G16; program learning), 2026-11-11, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen with the code in commit `ca98cab51` before the searches ran; one job dropped as
infeasible before any result was read (deviation, commit `771a8f5bf`). Proof family: `proofs/UNATE-20261111-001A/`.

## The answer

*Refereed on 2026-11-11 (`PARITY-NEEDS-20261111-001`).* An independent check by fresh code passed: the gadget is a valid knot
space of genus 4 with a Kasteleyn law, every line and its four-point parity relation are knots under the canonical K1–K3 test, and the
parity is exact. One handle is in fact enough: an 8-point lattice torus also computes parity.

**No. Unateness is not a theorem of knot spaces: an 8-point knot space of genus 4 computes the parity of three held points exactly.**
Hold points 0, 3 and 4 at any values, and every floor state gives point 5 their sum mod 2. Small knot spaces compute majority often.
The learned memories' interfaces stay unate: the limit `THREE-IN-20261110-001` found belongs to them, not to knot spaces (a correction).

- **Not forced by the definition (by hand, before any run).** A map of held points is only required to be self-dual (theorem D), and
  self-dual non-unate maps such as parity exist. In general NAE logic they are definable: NAE-3SAT is NP-complete, so NAE's polymorphisms
  are the projections and their negations, and by Post's lattice every relation closed under complement is definable from NAE with hidden
  points. Any limit must come from a knot space's shape.
- **Prior work.** Planar NAE-3SAT is polynomial (Moret 1988, through planar max-cut), so planar knot spaces are limited; but a handle lets
  two wires cross, and the gadget found uses every handle its surface can hold (two faces, genus 4 on eight points).
- **The gadget (exact).** Its eight floor states, found by brute force over all 256 states, by the dissonance engine (W = |χ| = 6 exactly
  there) and by SAT, are on points 0, 3, 4, 5 exactly the eight patterns of even weight.
- **The searches (exact).** In 799 random knot spaces of 6 to 12 points, every class and every interface of three held points: total
  parity 20 times (16 at 8 points, 4 at 12), total majority 307,451 times, no other non-unate map. On the deeper memories' interfaces (T1 and
  T3, every class): no non-unate map, no majority.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Unateness is not forced by the definition; parity is definable in general NAE logic | proved by hand (Post's lattice, Schaefer) |
| An 8-point knot space of genus 4 computes three-input parity of held points | exhaustive computation, three independent readings |
| Parity and majority in random small knot spaces; none at the deeper memories' interfaces | exhaustive computation |

## Against the pre-registration

Both predictions held: the censuses found no non-unate map, and the random search found one (parity), so mark N holds. Census 2 (S1 at
radius 2) was dropped as infeasible before any result was read; the stop condition (a parity gadget) was reached without it, and no proof
was attempted, as the pre-registration said.

## What it changes

- **What limits the learned memory is its shape, not knot logic.** Its handles sit inside separate atoms, and every interface read so far
  is unate. A knot space that packs many handles near its interface counts three held points; whether a learned memory can grow or write
  such a place is now the question for G15 (sub-goal B146).
- **Knot spaces as such are not limited to unate computation.** Majority with negated inputs (a frame) generates every self-dual
  function by Post's lattice, and a self-dual function of the inputs and one reference point gives any function of the inputs; so
  gadgets of these kinds, if they could be wired together, would compute anything. Whether a memory can wire them is not addressed here.

## Assumptions

None added or changed. Relied on: A20, A46, A47, A58.

## Corrections

One, logged in `docs/CORRECTIONS.md`: `THREE-IN-20261110-001`'s "the limit belongs to the knot space" (**Narrowing**, worded beyond its
evidence); it belongs to the learned memories' interfaces. Dated lines in its note, intuition entry, the goals doc and the learning note.

## In the owner's words

The memories never counted because of how their knots are placed, not because knots cannot count. Eight points tied by eight knots on a
surface with four handles count three of them exactly: hold any three, and the fourth is forced to their parity.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: are maps of held points unate (B136) | **Status:** Successful | a definite answer: no; an exact 8-point parity gadget |
| Local direction: what held points can compute | Continue | parity exists in knot spaces; what it needs, and whether memories can have it, is open |
| Broader exploration: learning program | Known alternatives | a learned memory that computes parity, what parity needs, the probe as a theorem |
| Long-term goal: G15 Learning: a point in a learned knot space | Capability gained | knot spaces compute non-unate maps; the memories' limit is their shape |

**Next step:** Research directions — selected: #2

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A learned memory that computes parity (sub-goal B146) | 3/3 — Major | 1/3 — Exploratory | splice the 8-point gadget, less a point, into a memory host and ask whether the learner can turn its parity on and off from examples → a learned non-unate map, or what stops it | Alternative · recorded as a sub-goal |
| 2 | What a knot space needs to compute parity (B147) | 2/3 — Substantial | 2/3 — Testable | the same exact search over knot spaces of genus 1 and 2 and over more faces per point → the least genus and the local structure parity needs, or parity at low genus too | Selected · awaiting go-ahead |
| 3 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |
| 4 | How learning cost grows with atoms (B143) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

Direction 2 comes first because it is the cheapest discriminator for direction 1: it says what structure a memory would need to grow.

**Corrections:** one, Narrowing (`THREE-IN-20261110-001`'s scope). **Goals:** G15 checkpoint (capability gained); B136 taken; sub-goal
B146 and B147 added. **Assumptions:** none new or changed.
**Basket:** B147 (what a knot space needs to compute parity), B130 (a probe that is a theorem); taken: B147 as the selected next step;
B146 recorded as a sub-goal.

## Final report as sent

Posted in the thread on 2026-11-11:

**B136 is closed. Unateness is not a theorem: knot spaces can count, and only the learned memories can't.** An 8-point knot space of genus 4 computes the parity of three held points exactly: hold points 0, 3 and 4 at any values, and point 5 is forced to their sum mod 2.

- **Definition (by hand, before anything ran):** a map of held points is only required to be self-dual, and general NAE logic can define parity (Post's lattice). So any limit has to come from the knot space's shape.
- **Prior work:** planar NAE-3SAT is polynomial (Moret 1988). A handle lets two wires cross, though, and the gadget uses every handle its surface can hold (8 points, 2 faces).
- **The gadget (exact, three independent readings):** brute force over all 256 states, the dissonance engine (W = |χ| exactly on its 8 floor states), and SAT all agree. Parity recurs at 12 points.
- **The search (exact):** across 799 random knot spaces of 6 to 12 points, every class and every interface, majority appears at every size and parity 20 times. No other non-unate map appears. The deeper memories' interfaces have no non-unate map and no majority.
- **Deviation:** the radius-2 census proved infeasible (unfinished after two hours), so I dropped it before any result was read; it's logged. The stop condition was met by the gadget, so no proof attempt was needed; three independent readings stand in for the referee pass.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: are maps of held points unate (B136) | **Status:** Successful | a definite answer: no; an exact 8-point parity gadget |
| Local direction: what held points can compute | Continue | knot spaces count; what that needs, and whether memories can, is open |
| Broader exploration: learning program | Known alternatives | a learned memory that computes parity, what parity needs, the probe as a theorem |
| Long-term goal: G15, a point in a learned knot space | Capability gained | knot spaces compute non-unate maps; the memories' limit is their shape |

**Next step:** Research directions, selected #2.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A learned memory that computes parity (sub-goal B146) | 3/3 Major | 1/3 Exploratory | splice the gadget, less a point, into a memory host and ask whether the learner turns its parity on and off from examples → a learned non-unate map, or what stops it | Recorded as a sub-goal |
| 2 | What a knot space needs to compute parity (B147) | 2/3 Substantial | 2/3 Testable | the same exact search over genus 1 and 2 and more faces per point → the least genus and local structure parity needs | Selected, awaiting go-ahead |
| 3 | A probe that is a theorem (B130) | 2/3 Substantial | 1/3 Exploratory | as recorded | Deferred |
| 4 | How learning cost grows with atoms (B143) | 1/3 Incremental | 3/3 Ready | as recorded | Deferred |

I put #2 first because it's the cheaper discriminator for #1: it says what structure a memory would have to grow.

**Corrections:** one, Narrowing: B133's "the limit belongs to the knot space" was too broad; it belongs to the memories' interfaces.
**Goals:** G15 checkpoint (capability gained, with G16); B136 taken; sub-goal B146 and B147 added.
**Assumptions:** none new or changed.
**Basket:** B147 (what a knot space needs to compute parity), B130; taken: B147 as the selected next step; B146 recorded as a sub-goal.

The long run is registered in docs/LONG_RUNNING.md and folded in. B147 waits for a go-ahead.
