# Persistence needs forgetting

Status: Proved by hand (the theorem and its corollaries). `check.py` verifies them on every substrate of a declared linear family;
check 3 is a computation, not a theorem.

Ticket `INVERT-STEP-20261110-001A`, 2026-11-10.

## Standard statement

- **Networks.** A finite network of rings joined by shared contacts, each contact a cell of two rings, every cell updated by a
  deterministic local law (any law, linear or not). It is read as one space-time law with an open first row (A30): every later value
  is a function of the first row. Its **step** Φ maps a joint state of all cells to the next one; for a second-order law, whose next
  row also reads the row before, the state is a pair of rows and the first two rows are open.
- **Binding.** A contact c **binds** ring X at lag T when every minimally decisive set of c(T), over the first row, meets X's own
  cells, the cells of X other than its contacts (A32, as `PROCESS-CONTACT-20261108-001A` reads it: the contact's own first value c(0)
  belongs to neither ring). It **persists** when it binds both of its rings at every lag T ≥ 1.
- **Open row.** The row at lag t is **open** when every joint value of its cells occurs at lag t from some first row.

**Theorem (persistence needs forgetting).** If the step of a finite network is injective, no contact persists. With p the order of
the step (Φ^p is the identity), every contact's value at every lag kp is its own first value c(0), so at those lags it binds neither
of its rings.

**Corollary 1 (only beginnings are open).** In a finite network with a persistent contact, no row after the first is open: for every
t ≥ 1 some joint value of the cells is never reached at lag t. This extends `REBASE-KNOTS-20261109-001A`, proved there for rule 60 with
law (12, 12) by counting reads, to every rule and contact law.

**Corollary 2 (B39).** No finite substrate has both an invertible step and a persistent contact. On a substrate whose every row is
open, a band inserted while the network runs would meet an open state, but no stage of it, once fixed, keeps any contact bound.

## Proof of the theorem

A finite set's injective self-map is a bijection, a permutation of the joint states, and a permutation of a finite set has finite
order: some p ≥ 1 has Φ^p equal to the identity. Then for every first row the state at lag kp is the first row itself, so the value of
contact c at lag kp, as a function of the first row, is c(0). Its only minimally decisive set is {c(0)}, which meets neither ring's
own cells: c binds neither ring at lag kp, and in the knot language erasing either ring leaves c(kp) unchanged, so loop-erasure contact
loss fails there. For a second-order law the state is a pair of rows and the same argument applies to the pair map; c(kp) is again
c(0). ∎

## Proof of Corollary 1

If the row at lag t ≥ 1 were open, Φ^t would map the finite set of joint states onto itself, so Φ would be onto (Φ^t = Φ ∘ Φ^(t − 1)),
hence a bijection, and by the theorem no contact would persist. ∎

Corollary 2 restates the theorem for a substrate: an invertible step is an injective one. ∎

## Remarks

- **Reconciliation with `DOUBLE-BALANCE-20261109-001A`.** That proof uses an invertible map, and there is no conflict: its invertible
  map is not the step. It is the evolution of a ring X's own cells, read as their X-parts, while every contact is newborn before each
  step and so carries no part of X: in each corner a_1 ← a_1 and a_j ← a_j + a_(j − 1), a unipotent map on own cells alone. The
  network's step there is rule 60 with law (12, 12), which forgets: every cell is read twice, so it loses dimensions at every lag
  (`REBASE-KNOTS-20261109-001A`; check 4 here). Once growth stops, the stage runs that forgetting step, and its contacts persist as the
  static stage's do. While it doubles every lag the network is never fixed, and each contact's first value is discarded by its
  rebirth, itself a way of forgetting. So the transfer lemma needs invertibility inside a ring's own cells, and persistence needs the
  step as a whole to lose information: the two fit.
- **Where the forgetting sits.** In rule 60 with law (12, 12) a contact reads its two left neighbours and not itself, so its first
  value is overwritten at once and returns only through the cells that read it (`SHARED-CONTACT-20261108-001`). Under an invertible
  step nothing is ever lost, so the contact's first value comes back whole.
- **The forgetting can be one cell.** A contact that only listens, read by neither ring (`PROCESS-CONTACT-20261108-001A`), between
  rings whose own rules are invertible, as rule 150 is on rings of 4, 5, 7 and 8 cells, loses only its own first value: the step's rank
  falls short by one, and the contact persists (computed in passing, not a check here). In the shared networks of check 3 the deficit
  is at least 2.
- **Finiteness is used.** On an infinite network, or under growth that never stops, an injective step need not have finite order, and
  the theorem says nothing there.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | First order, 256 substrates (8 ring rules × 32 contact laws reading any subset of the contact and its four ring neighbours) on 3 × 3 and 3 × 4 at g = 2 and 4 × 4 at g = 3, and one size past (5 × 4 at g = 2, 3 × 4 at g = 3): every invertible substrate (45 to 64 per tube) has a finite order, at most 510, and none persists; each fails by lag 25 | pass |
| 2 | Second order, the same 256 on the same five tubes, all invertible by construction: every one has a finite order, at most 7,710, and none persists; each fails by lag 336 | pass |
| 3 | Computed: the first-order substrates that persist (32 to 52 per tube, read through a full cycle) all forget, with rank deficit at least 2; rule 60 with law (12, 12) is among them | pass |
| 4 | Reconciliation: on rule 60 with law (12, 12) the step's rank is below the number of cells on all five tubes, while the own-cell block, with contacts read as zero, is invertible | pass |

## Nonclaims

- **Finite networks only**, read from an open first row (A30) with binding as A32 reads it in the networks. Under A30's alternative,
  the whole space-time law, the contact's history could join the rings as a witness; that reading is not examined.
- **No claim about persistence under growth that never stops** on an invertible substrate, or on infinite networks.
- **The persistent substrates of check 3 are counted, not classified**; 18 per tube have no ring dynamics (rules 0 and 204).
