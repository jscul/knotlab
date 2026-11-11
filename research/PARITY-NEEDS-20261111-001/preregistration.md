# Pre-registration: what a knot space needs to compute parity

Epic `PARITY-NEEDS-20261111-001` (backlog B147, G15 with G16), written on 2026-11-11 before the search runs, at the coordinator's
go-ahead. Code frozen with this file in `proofs/PARITY-NEEDS-20261111-001A/PARITY-NEEDS-20261111-001A-P001_the_parity_gadget_refereed/`
(`referee.py`, `gadget.json`, `needs_lib.py`, `check.py`).

## First: an independent check of the parity gadget (done before this freeze, logged here)

`UNATE-20261111-001`'s 8-point gadget was checked by fresh code (`referee.py`) that reads only the gadget's rotation system and signs
(`gadget.json`) and uses no library of the learning line. It found: every line on three distinct points and every point on three lines;
two faces, Euler characteristic −6, genus 4, traced from the rotation system; every face odd, so the law is Kasteleyn; 8 states satisfying
every line, on which point 5 is the parity of points 0, 3 and 4. Under the canonical K1–K3 test (`tools/knotlab`, forgetting reading)
every line's relation is a knot, and the relation on the four interface points with the other four as witnesses is a knot (binding,
loss on erasure, coexistence all hold). **Referee passed.** It is independent code, not an independent reviewer: this session does not
start other agents.

## Is the least genus forced by known results?

- **Genus 0 is excluded for disk gadgets, conditionally.** Planar NAE-3SAT is polynomial (Moret 1988). Parity of four points (EVEN⁴) is
  symmetric in its four terminals, and three such gates sharing one local reference point r make a crossover: c = a ⊕ b ⊕ r,
  a′ = c ⊕ b ⊕ r = a, b′ = c ⊕ a ⊕ r = b (the XOR crossover of Lichtenstein 1982 with r cancelling in pairs). So a planar gadget with its
  four terminals on one face would let planar NAE-3SAT simulate any NAE-3SAT instance, which is NP-complete; unless P = NP, no such gadget
  exists. (On a sphere the floor states also violate a line, so this program's reading of maps uses genus at least 1 in any case.)
- **Whether genus 1 suffices is not settled by any construction I know.** A torus lets two families of wires cross as often as needed,
  so nothing above rules parity out at genus 1; the knot-space conditions (every point on three lines, a 2-coloured triangulation, a
  Kasteleyn law) may. The search below decides it within its range.

## The search (frozen; exact)

- **Tori (genus 1):** every simple, non-degenerate triangular-lattice torus with up to 20 points (281 tori), every class, every interface
  of three held points and one output, all floor states enumerated.
- **Steered random spaces (genus 1, 2, 3):** `UNATE-20261111-001`'s random incidence with n = 8, 10, 12, 14 points, its rotation changed by a
  seeded random walk until the genus is the target; seeds 0 to 99 for each (n, genus); spaces that never reach the genus in 4,000 steps,
  or come out disconnected or not simple, are counted and skipped.
- **Caps, set now:** each space 300 seconds; the tori part 30 minutes and the steered part 60 minutes of wall-clock time, enforced by the
  systemd unit. A space or a part over its cap is dropped by rule and reported as dropped.

## Predictions and failure criteria

- No non-unate map on any torus of the range (lattice or steered): the least genus is at least 2 here.
- A non-unate map (parity) appears by genus 3 in the steered spaces; I expect genus 3 to be the least found.
- **Answer by rule:** the least genus at which any non-unate map occurs in the range, with the smallest such space and its faces; or, if
  none occurs below genus 4, that the range is exhausted with the least genus known to be at most 4 (the referee-checked gadget).
- Stop there; report and hold.

Assumptions in force: A20, A46, A47, A58. The runs are expected to take more than ten minutes and are registered in
`docs/LONG_RUNNING.md` with the caps above.
