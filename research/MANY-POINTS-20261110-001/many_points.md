# Many points at once

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern. Results are unchanged;
the earlier text is in git history.

Epic `MANY-POINTS-20261110-001` (backlog B3, G15 stretch goal; program learning), 2026-11-10, at the coordinator's go-ahead, which lifted
the hold on B3. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `880f19375` before any run. Proof families:
`proofs/MANY-POINTS-20261110-001A/` (where units sit together), `…B/` (two points at once), `…C/` (writing with more addresses).

## The answer

Several points of dissonance in the layered memory move independently unless they share a line; where they do, they mostly cancel.

- **Where units sit together (proved, then exact).** In the two-level space (two composites, floor 3 units) no region holds three units,
  the two composites never act together, an acting composite holds exactly two units, one in each of its leaves, and the other composite
  holds exactly one. Every distribution the theorem allows is realized in every class (all 256, both leaf types); a composite that does
  not act can also hold two, with the placements recorded.
- **Two points at once (computed).** Of 1,280 sampled pairs of disturbances, all 320 in different composites were independent: each
  learned away as if alone, in every order of the two learners' moves, with the address kept. Pairs within one composite were 83%
  independent, pairs on the outer host 70%, mixed pairs 98%. The rest interacted, mostly by cancelling (I < 0). After two disturbances
  the address held 93% to 100% of the time, against 100% after one.
- **Post hoc:** every pair at distance 2 or more was independent (1,104 of 1,104), and 154 of the 176 pairs sharing a line interacted.
  Points interact only through a shared line, on these samples.
  *Corrected on 2026-11-10 (`COMPOSITE-FN-20261110-001C`).* As a general statement this is false: on fresh composites one of 1,200
  distant pairs interacted, because the repair of one point flipped a point on a line through the other. Two disturbances combine in
  every order when the lines and faces touched by each flip and its repair are disjoint (proved there); `docs/CORRECTIONS.md`.
- **Writing, re-tested (computed).** With 96 addresses: thin leaves held 48 of 48. With Fano leaves the result is not a pass: it landed
  between the marks twice (5 of 6 in `NEST-ATOMS-20261110-001`, 43 of 48 here), all misses inexact searches. Every exact write, 91 of
  91, held after the disturbance.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| A1: no region holds three units; composites never act together; distributions by acting composite | proved by hand (lemma U and the floor count); exact check |
| A3: an acting composite's two units sit one per leaf | proved by hand; exact check |
| A2: every allowed distribution realized in every class | exact (SAT over every state, 512 classes) |
| Two points: independence by category, cancel and bind | computed on 1,280 sampled pairs, the order test exhaustive per pair |
| Interaction only through a shared line | computed, post hoc |
| Writing: thin leaves 48 of 48 held; Fano leaves between the marks twice (5 of 6, 43 of 48), all misses inexact searches | computed |

## Against the pre-registration

A1, A2 and A3 held. B1, B2 and B3 held, and the failure line was not crossed; the stop condition was not met, so the answer is "independent
when apart, interacting when they share a line", not "always independent". Ticket C landed between its marks for Fano leaves (89.6%), as
the six-write run did; its secondary measure locates the misses in the writes, not the returns. The distance table is post hoc.

## What it changes

- **For the owner's parallel picture (B3).** Points can be updated with no scheduler wherever they are at least two apart: the order does
  not matter, and the memory keeps its address. Points that share a line meet, and most cancel.
- **For the memory.** Disturbances in different composites never interfere, which is what a layered memory needs to be read and written
  in parallel; returns after a disturbance held whenever the write was exact (91 of 91 here, 18 of 18 before).
- **For the tools.** The frozen writing search accepts a unit in a leaf that does not act; a search that checks roles (backlog B113)
  would remove the only misses seen.

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50, A52. None added or changed.

## Corrections

None.

## In the owner's words

Many points can move at once. Wherever two are not on a common line, each finds its way back as if the other were not there, in any
order, and the memory keeps what it was told. Two points on one line meet, and usually cancel each other out.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — many points at once (B3) | **Status:** Successful | points apart move independently in every order; on a shared line they meet, mostly cancelling |
| Local direction — the layered memory | Capability gained | unit placements proved and realized; parallel disturbances keep the address |
| Broader exploration — learning program | Known alternatives | an OR from a host, a native atom, naming knots as layers |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | many points in a learned network, with a locality observed |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which functions a composite computes (B109) | 2/3 — Substantial | 1/3 — Exploratory | look for a host whose contradiction survives deleting either of two lines → an OR, or only AND | Selected · awaiting go-ahead |
| 2 | Which atom a growth law grows (B106) | 2/3 — Substantial | 1/3 — Exploratory | which uniform local rules can grow the 4-point atom → memory grown natively, or none | Alternative · deferred |
| 3 | Layers through a naming knot (`RESIGN-STEER-20261107-001`#3) | 2/3 — Substantial | 1/3 — Exploratory | parity name against a three-edge cut as the channel between levels → one reading, or two kinds of layer | Alternative · deferred |
| 4 | Points interact only through a shared line (B112) | 1/3 — Incremental | 2/3 — Testable | prove that two flips at distance 2 or more add their rises and that D's moves commute → a locality theorem, or a far pair that interacts | Alternative · deferred |
| 5 | A writing search that reads roles (B113) | 1/3 — Incremental | 3/3 — Ready | stop the search on the acting leaves instead of units → every write exact, and held | Alternative · deferred |
| 6 | Capacity of the learned memory (B98) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1 to #3** tie at the top rating and are independent; #1 continues the layered memory directly, and the coordinator may run the
  others in parallel.
- **#4** would turn the post hoc locality into a theorem.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B3 taken; B112 and B113 added. **Assumptions:** none new or changed.
**Basket:** B106, B109, `NEST-ATOMS-20261110-001`#4 (layers through a naming knot); taken: B109 as the selected next step.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (05:28 UTC): the answer (points apart move independently in every order; on a
shared line they meet and mostly cancel), where floor units sit (proved, exact on 512 classes), the two-point results by category with
the post hoc locality, the writing re-test (91 of 96, every exact write held), the plain statement added to the B104 record, both tables
of the position and next directions above with B109 selected and B106 and layers through a naming knot tied, the Corrections, Goals and
Assumptions lines, and the Basket line.
