# Interpretation of RING-LAW-20261109-001B-E002

Exploratory and exact, pre-registered in 2fbdf69f0. run.py ran 4,875 s and was killed by the out-of-memory killer at its 16 GiB cap
(16 workers) after 3,562 of its 4,002 readings, every one kept in partial.jsonl; resume.py (registered before launch, 71294b4ed, as
RING-LAW-B3) read the other 440 with run.py's own code in 8 workers replaced after every reading, in 8,012 s, and wrote result.json with
run.py's summary. Roster, laws, lags and hypotheses are unchanged.

- **H1 holds.** On none of the nine tori (square, triangular, honeycomb; n = 4, 5, 6) does a law that sees the routing bind both rings
  at every lag read. The only laws that bind on the tori are the 12 blind affine ones.
- **H2 holds.** On the square line networks of n = 4 and 5, exactly 32 laws that see the routing, with both rings passing, bind both
  rings to lag 6, the same 32 at both sizes: one ring's table is the parity of its two neighbours (6 = l + r, or 9 = 1 + l + r) and the
  other's is one of the eight nonlinear tables {1, 2, 4, 7, 8, 11, 13, 14}. On the triangular and honeycomb line networks none does.
- **H3 holds.** Under the eight symmetric nonlinear laws every representative contact of all 18 networks needs both its rings at every
  lag to 64.
- **H4 holds.** Under them every torus and line network read is on time: no (ring, contact) pair is late. The control (12, 12) gives
  its known late pairs on every torus but the triangular 4 × 4 (8 to 36) and none on the line networks.

By the frozen rule: native rings that bind exist on the square lines and not on the tori read, and with H4 a torus read plainly under a
law that sees its rings costs binding.
