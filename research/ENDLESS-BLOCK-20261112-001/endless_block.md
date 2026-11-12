# Endless blocks

Epic `ENDLESS-BLOCK-20261112-001` (`TWIST-PIN-20261112-001` #1, from `SUBST-NEST-20261112-001` #3; G17 with G8; program mathematics,
group arithmetic), 2026-11-12, at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit
`b602c411a`. Proof family: `proofs/ENDLESS-BLOCK-20261112-001A/`. **Referee pending.**

## The question

Make each distinction an endless series, a harmony, bound to the other copies by the harmony's own knots. What does that add to what
the theorems already give, and does any reach arise that is not plain connectivity, the owner's "globally influential"?

## The answer

**Bound in every order, endless blocks lock completely (by the theorems); bound in one order, a loop shorter than the harmony's girth
locks every copy on it into one state, longer loops do not lock at all, and no open chain ever ties.** *Narrowed by referee R1 (logged):
every one of the seven locks only loops shorter than its girth, 4 to 16 knots and at most its period; the frozen range (3, 4, 6) could
not see the bound. The mechanism is known: closed walks of a reflexive transfer relation, see below.*

- **Every order (proved; exact).** A harmony has no distinction it can spare, so the pinning theorem ties every copy to every other:
  the nested base has exactly the harmony's states, all copies sharing one. With lags, the loops' net lags fold it to the states of
  matching period (502 of 502 cells as predicted), and, by the referee's rule of the twisted-pins epic, with no effect of loop length.
- **One order: loop-born locking (exact; robust).** Bind each knot's three copies by the harmony's kinds in one order only, a stitch of
  three harmonies (the reading of the bases-within-bases epic, with the harmony's own kinds as its lags). Then for 7 of 45 harmonies a
  closed loop of knots shorter than the harmony's girth locks all the copies on it into one shared state, place by place, while the
  same knots in an open chain, unrolled three times (frozen) or nine times (after the run), leave the copies free. That is a tie born of
  the whole loop: the frozen criterion for reach that is not plain connectivity is met, for short loops. No open chain of any length
  ties copies (proved by referee R1: the transfer contains the diagonal, so a tie at any distance would already be one at distance 1).
- **Only short loops lock.** All seven lock exactly the loops shorter than their girth: 4 knots (0010011011, 00101101 + 0011), 7
  (00100101101101 + 01), 8 (00101101, a four-orbit harmony of period 16), 12 (001010110101), 16 (0010101011010101); at the girth and beyond
  nothing is tied (referee R1; `LOOP-LOCK-20261112-001` proves the rule).

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Every order: complete locking; lagged: folding by net lags | proved by hand (from the pinning theorem and the twisted-pin lemmas); exact on every cell |
| Lagged harmonies show no loop-length effect | proved by hand after the freeze (no moves without a spare distinction) |
| One order: loop-born locking in 7 of 45 harmonies; length-dependent in 2 | exact on the frozen range; robust to a nine-fold unrolling (after the run) |

## Against the pre-registration

P1 and P2 (E1, E2) held on every cell. P3 (one order always lives, no new tie inside a copy) held. P4 (some single knot ties copies;
some cycle-born tie; rings of 6 and 7 differ) held: the alternation's single knot, 7 harmonies' loops, many harmonies' rings. Seen
before the freeze: the alternation's rows, as disclosed. All parts inside their caps (the one-order arm in 23 minutes).

## Referee R1 (folded in 2026-11-12)

Confirmed with fixes ([report](referee-R1/report.md)), with its own transfer matrices and direct SAT: E1 on every harmony, E2 on every
lag cell, the post-freeze lemma correct; the same seven harmonies, 17 cells and 1,376 ties at k = 3, 4, 6. With A the one-knot transfer
between consecutive loop copies (the hanging copy quantified away), a loop of k knots is a closed walk of length k in A, and since A
contains the diagonal the loop locks exactly when k is below the girth (computed to 48 knots; direct SAT on 28 cells: ties at g − 1, none
at g; for 00101101 at k = 8, 52,496 = 8 · 3^8 + 8 states, the eight extra winding once). Every girth among the 45 harmonies is finite and
at most P. **Real or built in:** the lock is real and needs the whole loop; it is built in to the extent that the stitch uses the
harmony's own kinds, so the transfer commutes with the shift, steps are phase offsets, and a loop must wind a whole turn to unlock,
hence girth ≤ P. **Known:** closed walks of a transfer digraph are periodic points of a shift of finite type (the trace of A^k; Lind and
Marcus), or homomorphisms of a directed cycle into a reflexive digraph (Hell and Nešetřil; Larose and Tardif's reflexive homotopy);
arc consistency never sees the lock and path consistency does (Montanari; Feder and Vardi's tree duality and the universal cover); for
shift-equivariant steps it is a winding (voltage-graph) condition. The advisor model, asked cold by the referee, calls the exact
statement folklore; only the harmonies' girths are new data. Four corrections logged (one Narrowing, three Not a block).

## What it changes

- **For the owner's "globally influential".** A native case where a whole loop, and not a chain of local links, decides a value:
  endless patterns stitched by their own rules, closed into a loop shorter than their girth, fall into step, while the same stitches
  in a line never do. Long loops do not lock. The mechanism is known (closed walks of a reflexive transfer). A sceptic would note what is built in: the stitch is the harmony's own kinds, so the loop's
  lock is a consistency condition on offsets around the loop (like phase locking, or a Tseitin parity), and its reach is still within
  the loop's own component; what is not built in is that an open chain of the same stitches stays free.
- **Next.** Which harmonies lock their loops, and why some only on short ones.

## Assumptions

A70 used; A75 (Assumed) — the one-order arm is the stitch reading, the every-order arms the substitution reading.

## Corrections

None.

## In the owner's words

If every yes-or-no is itself an endless repeating pattern, and the patterns are tied to each other by their own rules taken one way
round, then a short enough closed loop of ties makes every pattern on the loop fall into step, while the same ties in a straight line
leave each free to drift. That is influence that comes from the loop as a whole, and it stops once the loop is as long as the
pattern's own repeat or less: long loops can wind round and stay free. *(Narrowed after the referee.)*

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — endless blocks | **Status:** Successful, referee R1 confirmed with fixes | the theorems' predictions held; loop-born locking of short loops found, a known mechanism |
| Local direction — nesting | Continue | which harmonies lock their loops, and the length effect, are open |
| Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random bases (knots alone) |
| Long-term goal — G17 Typical and rare meeting patterns | Capability gained | a native case of influence born of a whole loop |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which loops lock | 2/3 — Substantial | 2/3 — Testable | for the 7 harmonies, read the relation between two stitched copies' offsets and the loop condition it imposes, and test loops of 2 to 12 knots → a rule for which harmonies and lengths lock, or a counterexample | Selected · awaiting go-ahead |
| 2 | Locking along two shifts | 2/3 — Substantial | 2/3 — Testable | the ring arm: classify the two-shift states of rings of 5 to 12 under one order → sheared copies, walls, or new states | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained, with G8; no goal change). **Assumptions:** A70 used, A75 unchanged.
**Basket:** #1, #2 recorded. **Advisor:** consulted once before the freeze (E1, E2's corrections, the one-order frame and the
universal-cover criterion).

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 09:38 UTC, verbatim:

> Done: endless blocks. Influence born of a whole loop exists. The write-up is research/ENDLESS-BLOCK-20261112-001/endless_block.md, and the referee is pending.
>
> • **Bound in every order, they lock completely (proved).** A harmony can't spare any position, so substituting one for every distinction puts all the copies in one shared state. With lags, the loops' net lags fold that down to the states whose period divides them. Here loop length plays no part.
> • **Bound in one order, a loop locks (exact).** Tie the copies by the harmony's own rules taken one way round, which is the stitch reading. Then in 7 of 45 harmonies, a closed loop of knots puts every copy on it into one shared state, in step at every position. The same knots in an open line leave each copy free to drift, even unrolled nine times. So the value is decided by the loop as a whole, not passed along a chain.
> • **Sometimes only a short loop locks.** For two harmonies, a loop of 3 knots locks and loops of 4 or 6 don't.
> • **What's built in, plainly.** The stitch is the harmony's own rules, so the lock is a consistency condition around the loop, much like phase locking. It still only reaches the loop's own component. What isn't built in is that an open line of the same stitches stays free.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — endless blocks | **Status:** Successful, referee pending | the theorems' predictions held; loop-born locking found |
> | Local direction — nesting | Continue | which harmonies lock, and why some only on short loops, is open |
> | Broader exploration — G17's census | Known alternatives | random patterns' jumps; folding among random bases |
> | Long-term goal — G17 Typical and rare meeting patterns | Capability gained | a native case of influence born of a whole loop |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Which loops lock | 2/3 — Substantial | 2/3 — Testable | for the 7 harmonies, read how two stitched copies' offsets combine around a loop; test loops of 2 to 12 knots → a rule for which harmonies and lengths lock | Selected · awaiting go-ahead |
> | 2 | Locking along two shifts | 2/3 — Substantial | 2/3 — Testable | classify one-order states on rings of 5 to 12 → sheared copies, walls, or something new | Alternative · deferred |
>
> **Corrections:** none this epic. **Goals:** G17 checkpoint (capability gained), no goal change. **Assumptions:** A75 unchanged; the one-order arm is the stitch reading. **Basket:** #1, #2 recorded. **Advisor:** consulted once before the freeze.
