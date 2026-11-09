# Which contact laws see how rings continue

Status: Theorems 1 to 3 proved by hand, their finite claims checked in `check.py`.

Ticket `RING-LAW-20261109-001A`, 2026-11-09.

## Standard statement

- **Networks.** Rule-60 rings (every own cell reads its left neighbour and itself) joined by contacts, each contact a cell of both its
  rings, laid out as in `REROUTE-20261109-001B` (`ring_law_lib.py`). A **self-blind law** sets c ← u(l_a, r_a) xor v(l_b, r_b), where
  l and r are the contact's left (arriving) and right (leaving) neighbours on its two rings and u, v are any of the 16 two-input
  tables: 256 laws, among them law (12, 12), u = v = l, of every network epic since `LOOP-NET-20261108-001` (A31's self-blind family).
  Write u = u₀ + u₁l + u₂r + u₃lr over GF(2), and v likewise.
- **Seeing the routing.** A law **sees the routing** at a contact when re-routing there (exchanging which arriving corner continues on
  which leaving corner, `REROUTE-20261109-001B`) changes the automaton. A ring **passes** a contact when the contact's value depends on
  the ring's arriving cell, so that the ring's chain of reads runs through it.
- **Binding and needing.** c **needs** ring X at lag T when c(T) depends on X's own cells; c **binds** X at lag T (A32) when every
  minimally decisive set of c(T) meets X's own cells, that is, when no assignment of the other cells makes c(T) constant in X's.

**Theorem 1 (which laws see the routing).** Re-routing at a contact changes only that contact's update, from u(l_a, r_a) + v(l_b, r_b)
to u(l_b, r_a) + v(l_a, r_b). The two agree for every input exactly when u₃ = v₃ = 0 and u₁ = v₁. So a law is blind to the routing
exactly when it is affine and reads both arriving cells alike (32 laws), and it sees the routing otherwise (224 laws).

**Theorem 2 (an affine law sees only by cutting).** If the law is affine and sees the routing, the contact reads exactly one of its two
arriving cells, so the other ring does not pass it: its chain of left-neighbour reads stops at the contact. Hence a law under which
both rings pass every contact and the routing is seen is nonlinear: u₃ = 1 or v₃ = 1 (128 laws).

**Theorem 3 (affine binding is needing).** Under an affine law the automaton is affine, and c binds X at a lag exactly when it needs X
there. Under a nonlinear law binding is stronger than needing.

## Nearest known result

- **Sources.** Algebraic normal forms of Boolean functions; `REROUTE-20261109-001B` and `same_automaton.py` beside its decision note,
  which found law (12, 12) blind; A31 and A32 for the self-blind family and binding.
- **Classification.** New as far as found, as a reading of these networks; the algebra is elementary.

## Proof of Theorem 1

The re-routed network has the same cells, and every cell other than the contact reads the same cells: a leaving corner's first cell
reads the contact whichever corner arrived. At the contact the left neighbours exchange their rings. The difference of the two
updates is u₁(l_a + l_b) + u₃r_a(l_a + l_b) + v₁(l_b + l_a) + v₃r_b(l_b + l_a) = (l_a + l_b)(u₁ + v₁ + u₃r_a + v₃r_b), which vanishes
for every input exactly when u₁ = v₁ and u₃ = v₃ = 0. Check 1 compares the two truth tables for all 256 laws; check 2 builds the 4 × 4
square torus and its line network cell by cell under every law and finds them the same automaton exactly for the 32 blind laws. ∎

## Proof of Theorem 2

An affine u depends on l exactly when u₁ = 1, so an affine law that sees the routing (u₁ ≠ v₁) reads one arriving cell and not the
other. The unread ring's arriving cell is then read by itself only along the ring, since the next cell along it is the contact. Check 3
confirms it at all 1,024 contacts of the 4 × 4 torus under the 32 affine laws that see. ∎

## Proof of Theorem 3

Under affine laws every update is affine, so c(T) = ℓ(first row) + constant with ℓ linear. Fixing the cells outside X leaves the
restriction of ℓ to X's cells, constant exactly when it is zero, which is exactly when c(T) does not need X. Under the law u = v = AND,
by contrast, c(3) needs both rings at the 4 × 4 torus's contacts while some assignment of the other cells makes it constant in either
ring's cells (`ring_law_lib.binds_exactly`; the census of `RING-LAW-20261109-001B` reads this for every law). Check 4
confirms the equivalence on every affine law at contacts 0 and 1 of the 4 × 4 torus, both rings, lags 1 to 4 (512 cases). ∎

## Remarks

- **A45 is forced for the program's networks.** Law (12, 12) is affine and reads both arriving cells, so by Theorem 1 its rings are a
  declaration, and by Theorem 2 no affine law can make them native without cutting a ring. Native rings that every ring passes need a
  nonlinear contact.
- **The cost moves to binding.** Under affine laws binding is needing (Theorem 3), which `LOOP-NET-20261108-001A` reads through the
  contact graph. Under nonlinear laws the two part, and `RING-LAW-20261109-001B` reads both.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Theorem 1: the ANF condition agrees with the truth tables of all 256 laws; 32 blind | pass |
| 2 | Theorem 1 on a network: the 4 × 4 torus and its line network are the same automaton exactly for the blind laws | pass: 256 of 256 |
| 3 | Theorem 2: every contact under an affine law that sees reads exactly one arriving cell | pass: 1,024 contacts |
| 4 | Theorem 3: binding equals needing under affine laws | pass: 512 cases |

## Nonclaims

- **Self-blind laws and rule-60 rings only;** contacts that read themselves, other ring rules and laws beyond A31's family are not read.
- **Two-time knots only** (A30).
