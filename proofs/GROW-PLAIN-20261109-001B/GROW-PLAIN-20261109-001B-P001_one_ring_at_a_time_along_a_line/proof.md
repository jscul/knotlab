# A single fastest way grows one ring at a time, and only along a line

Status: Proved by hand from `RESCUE-MAP-20261109-001A`, `GROWN-DISTANCE-20261109-001A` and `GROW-NET-20261108-001A`; the finite claims
are checked in `check.py`.

Ticket `GROW-PLAIN-20261109-001B`, 2026-11-09.

## Standard statement

- **Networks and readings.** Equally spaced rule-60 rings with law (12, 12) contacts. A network is **on time** when the plain first need
  of every contact on every ring comes at the directed distance (`PLAIN-TIME-20261108-001B`), and a contact **persists** when it binds
  both its rings at every lag (`LOOP-NET-20261108-001A`). Each stage of a growth law is read as a fixed network (A42).
- **The twist torus.** The square torus of ⟨(2, 1), (N, 0)⟩, in tube coordinates: rings at the positions a ∈ Z_N, ring a listing its
  contacts counterclockwise as h(a), v(a), h(a − 1), v(a + 2), where h(a) joins rings a and a + 1 and v(a) joins a and a − 2
  (`RESCUE-MAP-20261109-001A`, proof of Theorem 2).
- **The √3 torus.** The triangular torus of ⟨(1, −1), (N, 0)⟩, in tube coordinates: ring a lists (0, a), (1, a), (2, a), (0, a − 1),
  (1, a − 2), (2, a − 1), where (t, a) joins a to a + 1, a + 2, a + 1 for t = 0, 1, 2.
- **Ring insertion.** Inserting a ring after position j renumbers the rings after j by one and gives the torus of N + 1 rings. On the
  twist torus it cuts the three contacts that span the gap, h(j), v(j + 1) and v(j + 2), and adds five, two h and three v, around the new
  ring; on the √3 torus it cuts four and adds seven. Every other contact, and the cyclic order at every ring more than two positions from
  the gap, stays as it was.

**Theorem 1 (a law that grows a network reading its own distance plainly).** Starting from the twist torus of 4 rings, inserting one ring
at a time, anywhere, gives the twist torus of every size, and every stage has every contact persistent and is on time: every contact needs
every ring first at the directed distance, with nothing frozen. The same holds for the √3 torus from 3 rings, and for the ladder
⟨(0, 2), (n, t)⟩ grown by inserting a rung of two rings.

**Theorem 2 (only a line).** Let M_1, M_2, … be square, triangular or honeycomb tori of unbounded index, each on time. Then all but
finitely many hold a ladder, twist or √3 vector, and none is honeycomb. Each of those is covered by its tube, whose ring balls hold
4r + 1 rings (twist, √3) or 4r rings (ladder) at radius r ≥ 1, so a ball of radius r in M_i holds at most 4r + 1 rings: growth that keeps
the plain first need on time at every stage, through tori, grows a line, not a plane.

## Nearest known result

- **Growth of networks of rings.** The band law (`BAND-SURFACE-20261108-001A`, `GROW-NET-20261108-001A`) grows n × m tori; its first
  stage, the ladder, is the only one read plainly (`GROWN-DISTANCE-20261109-001A`, Theorem 3). `GROW-NET-20261108-001A`, Theorem 2: attaching
  one ring to a balanced network breaks persistence. Insertion here also adds one ring, but rewires three or four contacts as it does.
- **Classification.** New as far as found for the question asked. The ingredients are `RESCUE-MAP-20261109-001A`'s classification and the
  half-turn argument.

## Proof of Theorem 1

**Each stage is a lattice torus.** The map p = (x, y) ↦ x − 2y identifies Z²/⟨(2, 1), (N, 0)⟩ with Z_N and carries the square torus's
rotation (E, N, W, S towards p + e1, p + e2, p − e1, p − e2) to the tube coordinates above: e1 ↦ +1, e2 ↦ −2. Likewise x + y identifies
the √3 torus's rotation with its tube coordinates. Check 1 reads both ways on every size from 3 to 20 and finds the same verdicts.

**Insertion is local.** Writing the torus of N + 1 rings in the same coordinates and sending old ring a to a, or to a + 1 after the gap,
every contact not spanning the gap keeps its rings and slots. Check 2 lists, on tori of 8, 12 and 20 rings and three gaps each, the slots
that change: those of the three cut and five new contacts on the twist torus (six and ten slots), four and seven on the √3 torus (eight and
fourteen), all on the new ring and the four rings beside the gap.

**Persistence.** Every lattice torus has the half-turn about the midpoint of every contact, since −Λ = Λ: an orientation-preserving
automorphism fixing the contact and exchanging its rings, so every contact persists (`GROW-NET-20261108-001A`, Theorem 1, whose proof uses
only that). In tube coordinates the half-turn about a contact joining rings a and b is p ↦ a + b − p with each slot moved half way round
the ring; check 3 confirms it on every stage from 3 to 60.

**On time.** The twist torus of N rings is on time for N ≥ 4 and late at N = 3, and the √3 torus is on time for every N ≥ 3
(`RESCUE-MAP-20261109-001A`, Theorems 2 and 3); every ladder is on time (`GROWN-DISTANCE-20261109-001A`, Theorem 2). Check 3 reads every stage
from 3 to 60 and every ladder to 30 rungs. ∎

## Proof of Theorem 2

By `RESCUE-MAP-20261109-001A`, Theorem 3, an on-time torus holds a family vector or has index at most 17, 21 or 9 (square, triangular,
honeycomb), and no honeycomb torus holds a family vector; so for i large, M_i holds a family vector v and is the quotient of the tube
T/⟨v⟩. The tube's ring graph is the circulant on Z with steps ±1 and ±2 (twist and √3, the √3 one with its ±1 steps doubled), whose ball of
radius r is [−2r, 2r], 4r + 1 rings, or the ladder strip Z × Z_2, whose ball holds 4r rings for r ≥ 1 (`GROWN-DISTANCE-20261109-001A`,
Theorem 4, with n = 2). A ball in a quotient is the image of a ball in the cover, so it holds no more rings. ∎

## Remarks

- **Growth that keeps the reading.** The band law loses the plain reading at its second band, n × 3 (`GROWN-DISTANCE-20261109-001A`,
  Theorem 3). Inserting rings along the twist tube, or rungs along the ladder, keeps it at every stage: growth laws whose every stage
  reads its own distance without freezing.
- **One ring at a time can keep persistence.** `GROW-NET-20261108-001A`, Theorem 2, shows that attaching a ring breaks persistence. Insertion
  is a different step: it adds one ring but cuts the contacts spanning the gap and rejoins them through the new ring, and every stage is a
  lattice torus, so every contact keeps its half-turn.
- **The price is dimension.** By Theorem 2 any such growth through tori makes a tube. A two-dimensional shape that reads its own distance
  plainly at every size, if one exists, is not a torus of these lattices.
- **Growing while running.** Each stage is read as a fixed network. `GROW-RUN-20261109-001A` shows that bands inserted while a network runs
  break the bindings their influence has reached; a ring inserted while running is not read here.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The tube-coordinate tori read as `RESCUE-MAP-20261109-001A`'s lattice tori, sizes 3 to 20, both families | pass |
| 2 | Inserting a ring is local: 6 slots cut and 10 added (twist), 8 and 14 (√3), on the new ring and the four beside the gap | pass |
| 3 | Every stage from 3 to 60 rings: on time from 4 (twist) and 3 (√3), late at twist 3; the half-turn at every contact; every ladder to 30 rungs on time | pass |
| 4 | The tubes' ring balls hold 4r + 1 rings, radius 0 to 12 | pass |

## Nonclaims

- **Tori only.** Growth through networks that are not lattice tori is not classified; Theorem 2 says nothing about them.
- **Stages, not running growth** (A42).
- **Two-time knots only** (A30); equally spaced rings only.
