# What makes a hybrid middle ring work: interpretation

Experiment `PATH-HYBRID-20261108-001C-E001` (exploratory), run 2026-11-08 under the frozen contract on ticket B's 1,120 native
paths, in 95 s. Every measure is exact by the row-sequence reduction. Totals are in `result.json`.

## Control: the canonical check

It passes. The smallest native path:
- **The path.** Rings of 3, 5, 5 and 3 cells running 102, 60, the hybrid (60, 102, 60) and 204, with contacts two apart on both
  middle rings.
- **Its knots.** At every lag from the light-cone lag 5 to lag 10, its last contact has exactly one knot through c3(T), meeting all
  four rings, of 8 to 11 places.
- **knotlab.** `knotlab check` confirms that the parity relation on c3's eventual support (one cell of A, two of B, one of C, two of
  D) is a knot.

## Measures

- **Hybridness is necessary.** For all 1,120 native paths, making the second middle ring uniform under any of the eight linear
  rules destroys nativeness.
- **The ring remembers.** The last contact's eventual support keeps the first rows of two of the hybrid ring's three non-contact
  cells (384 paths), or of all three (736).
- **Transport is partial.**
  - **One more cell in the hybrid ring**, beyond c3 and with a neighbour's rule, keeps some variant native for 704 of the 1,120
    paths.
  - **One more end-ring cell on D** keeps 928 native.
  - **One more cell on ring A** keeps none. The first two rings come from AFFINE-WIRE's carrying chains, which compose only at
    particular sizes.

## Reading

- **Why hybrid rings work.** A ring whose cells differ can keep its own state in its contacts' supports while other cells carry c2's
  past to c3. A uniform ring here did one or the other.
- **Composed topology across time.** It now exists for three contacts in a row, on inhomogeneous middle rings. Whether an
  inhomogeneous ring counts as a native substrate is a reading for the register.
- **Transport.** The far end transports well, and the near end does not, because the near end's composition is size-specific.
- **Addendum, after ticket A.** Ticket A's broad sweep, read after this interpretation was written, found 16 native paths with one
  rule on each ring: shift end rings and rule-150 middle rings. So hybridness is necessary for ticket B's paths, not for native
  paths in general.

## Nonclaims

- **Ticket B's paths only.**
- **Two-time knots only** (A30).
