# Pre-registration: reading the address natively, and a stress case for writing it

Epic `READ-ADDRESS-20261110-001` (backlog B85, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## Background

`ADDRESS-20261110-001` wrote the two leftover units of three Fano atoms into every chosen pair of atoms on K_3 (9 of 9, computed), and
`LAW-HOLDS-20261110-001` showed the holders are the atoms that act as their lines. "Memory" rests so far on those small cases.

## Tests

- **S (stress, one size past).** The frozen targeted search of `ADDRESS-20261110-001` (same moves, bound, target rule and cap of 300,000) on
  K_4 with three atoms (at l0 and at distances 2 and 3, every line orbit of K_4), toward every pair of atoms.
- **N1 (a native read from the law alone).** For every configuration written (K_3 and K_4), compute each atom's role from its own signs
  only (whether its lines allow all eight patterns on its three outer points or only the line's six: `LAW-HOLDS-20261110-001`'s atom role).
  This uses no state and no census: it is local to the atom (A47).
- **N2 (the state alone does not show it).** For each written law, draw 1,000 random states (seeded) and read where over-agreement sits
  (faces with three or more agreeing corners, inside atoms).

## Expectations, frozen

- **S.** Every pair of atoms is reached as the holders on every K_4 line orbit.
- **N1.** In every written configuration the holders are exactly the atoms whose local role is "line": the address is read off each
  atom's own signs.
- **N2.** In fewer than half of the random states do the atoms holding over-agreement coincide with the holder pair: the law shows the
  address, a random state does not.

## What would count against them

A K_4 pair not reached within the cap (against S); a written configuration whose holders differ from its line-acting atoms (against N1);
random states that show the address in half or more (against N2).
